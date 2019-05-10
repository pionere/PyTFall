init python:
    class MyTimer(renpy.display.layout.Null):
        """
        To Be Moved to appropriate file and vastly improved later!
        Ren'Py's original timer failed completely for chaining sounds in BE, this seems to be working fine.
        """
        def __init__(self, delay, action=None, repeat=False, args=(), kwargs={}, replaces=None, **properties):
            super(MyTimer, self).__init__(**properties)

            if action is None:
                raise Exception("A timer must have an action supplied.")

            if delay <= 0:
                raise Exception("A timer's delay must be > .")

            self.started = None

            # The delay.
            self.delay = delay

            # Should we repeat the event?
            self.repeat = repeat

            # The time the next event should occur.
            self.next_event = None

            # The function and its arguments.
            self.function = action
            self.args = args
            self.kwargs = kwargs

            # Did we start the timer?
            self.started = False

            # if replaces is not None:
                # self.state = replaces.state
            # else:
                # self.state = TimerState()


        def render(self, width, height, st, at):
            if self.started is None:
                self.started = st
                renpy.redraw(self, self.delay)
                return renpy.Render(0, 0)

            self.function()
            return renpy.Render(0, 0)


    class ChainedAttack(renpy.Displayable):
        """
        Going to try and chain gfx/sfx for simple BE attacks using a UDD.
        """
        def __init__(self, gfx, sfx, chain_sfx=True, times=2, delay=.35,
                     sd_duration=.5, alpha_fade=.0, webm_size=(), **properties):
            """
            chain_sfx: Do we play the sound and do we chain it?
                True = Play and Chain.
                False = Play once and don't play again.
                None = Do not play SFX at all.
            times = how many times we run the animation in a sequence.
            delay = time between showing displayables.
            sd_duration = single frame (displayable) duration.
            alpha_fade = Do we want alpha fade for each frame or not. 1.0 means not,
                .0 means yes and everything in between is partial fade.
            """
            super(ChainedAttack, self).__init__(**properties)

            self.gfx = gfx
            self.sfx = sfx
            self.chain_sfx = chain_sfx
            self.times = times
            self.delay = delay
            self.count = 0
            if webm_size:
                self.size = webm_size
            else:
                self.size = get_size(self.gfx)
            # raise Exception(self.size)
            self.last_flip = None # This is meant to make sure that we don't get two exactly same flips in the row!

            # Timing controls:
            self.next = 0
            self.displayable = [] # List of dict bindings if (D, st) to kill.
            self.single_displayable_duration = sd_duration
            self.alpha_fade = alpha_fade

        def render(self, width, height, st, at):
            # if self.count > self.times:
                # return renpy.Render(0, 0)

            if self.count < self.times and st >= self.next:
                # Prep the data:

                # get the "flip":
                flips = [{"zoom": 1}, {"xzoom": -1}, {"yzoom": -1}, {"zoom": -1}]

                if self.last_flip is None:
                    flip = choice(flips)
                    self.last_flip = flip
                else:
                    flips.remove(self.last_flip)
                    flip = choice(flips)
                    self.last_flip = flip

                # Offset:
                # Adjusting to UDD feature that I do not completely understand...
                offx, offy = choice(range(0, 15) + range(30, 60)), choice(range(0, 15) + range(30, 60))

                # GFX:
                gfx = Transform(self.gfx, **flip)
                gfx = multi_strike(gfx, (offx, offy), st,
                                   self.single_displayable_duration, self.alpha_fade)

                # Calc when we add the next gfx and remove the old one from the list.
                # Right now it's a steady stream of ds but I'll prolly change it in the future.
                next_disp = uniform(self.delay*.85, self.delay)
                self.next = st + next_disp
                self.count += 1
                self.displayable.append((gfx, st + self.single_displayable_duration))

                # We can just play the sound here:
                if self.chain_sfx is None:
                    pass
                elif self.chain_sfx or self.count == 1:
                    renpy.play(self.sfx, channel="audio")

            # Render everything else:
            render = renpy.Render(self.size[0] + 60, self.size[1] + 60)
            for d, t in self.displayable[:]:
                if st <= t:
                    render.place(d)
                else: # Remove if we're done with this displayable:
                    self.displayable.remove((d, t))

            renpy.redraw(self, .1)
            return render


    # Plain Events:
    class RunQuotes(BE_Event):
        def __init__(self, team):
            self.team = team

        def check_conditions(self):
            return True

        def kill(self):
            return True

        def apply_effects(self):
            interactions_prebattle_line([member.char for member in self.team])


    class BESkip(_object):
        """
        Simplest possible class that just skips the turn for the player and logs that fact.
        This can/should be a function but heck :D

        This will now also restore 3 - 6% of Vitality and Mana!
        """
        def __init__(self):
            pass

        def execute(self, source):
            if source.status == "free" and source.take_pp():
                msg = "%s skips a turn." % source.nickname

                # Restoring Vitality:
                temp = round_int(source.maxvit * uniform(.03, .06))
                temp = min(temp, source.maxvit - source.vitality)
                if temp != 0:
                    source.vitality += temp
                    msg += " {color=lawngreen}+%d VP{/color}" % temp

                # Restoring mp:
                temp = round_int(source.maxmp * uniform(.03, .06))
                temp = min(temp, source.maxmp - source.mp)
                if temp != 0:
                    source.mp += temp
                    msg += " {color=dodgerblue}+%d MP{/color}" % temp
                battle.log(msg)
            else: # Slaves or inactive character:
                msg = "%s stands still." % source.nickname
                battle.log(msg)

            return "break"


    class BELeave(BESkip):
        """Try to leave from the battle field"""
        def __init__(self, mode=None):
            self.mode = mode

        def execute(self, source):
            if self.mode == "escape":
                # Try to escape:
                if renpy.call_screen("yesno_prompt", message="Are you sure that you want to escape?", yes_action=Return(True), no_action=Return(False)):
                    battle.combat_status = "escape"
                    return "break"
            elif self.mode == "surrender":
                # Surrender:
                if renpy.call_screen("yesno_prompt", message="Are you sure that you want to surrender?", yes_action=Return(True), no_action=Return(False)):
                    battle.combat_status = "surrender"
                    return "break"
            else: # self.mode == "leave"
                # just leave
                battle.combat_status = "leave"
                return "break"

    class RPG_Death(BE_Event):
        """
        Used to instantiate death and kill off a player at the end of any turn...
        """
        def __init__(self, target, death_effect=None, msg=None):
            self.target = target
            self.death_effect = death_effect
            if not msg:
                self.msg = "{color=red}%s was (heroically?!?) knocked out!{/color}" % self.target.name
            else:
                self.msg = msg

        def check_conditions(self):
            # We want to run this no matter the f*ck what or we'll have fighting corpses on our hands :)
            return True

        def kill(self):
            return True

        def apply_effects(self):
            target = self.target
            battle.corpses.add(target)

            if not battle.logical:
                if self.death_effect == "dissolve":
                    renpy.hide(target.betag)
                    renpy.with_statement(dissolve)

            # Remove poor sod from the queue:
            battle.queue = [t for t in battle.queue if t != target]

            battle.log(self.msg, delayed=True)


    class PoisonEvent(BE_Event):
        def __init__(self, source, target, effect, duration, group):
            self.target = target
            self.source = source
            self.counter = duration
            self.effect = effect
            self.group = group # Or we collide with Buffs
            self.icon = "content/gfx/be/poison1.webp"
            # We also add the icon to targets status overlay:
            target.status_overlay.append(self.icon)

        def check_conditions(self):
            if battle.controller == self.target:
                return True

        def kill(self):
            if not self.counter:
                t = self.target

                t.status_overlay.remove(self.icon)
                msg = "{color=forestgreen}Poison effect on %s has ran its course...{/color}" % (t.name)
                battle.log(msg)
                return True

        def apply_effects(self):
            t = self.target

            # Damage Calculations:
            damage = t.maxhp * self.effect
            damage = max(8, int(damage)) + randint(-2, 2)

            # Take care of modifiers:
            damage = round_int(BE_Core.damage_modifier(self.source, t, damage, "poison")) 

            # GFX:
            if not battle.logical:
                gfx = Transform("poison_2", zoom=1.5)
                renpy.show("poison", what=gfx, at_list=[Transform(pos=battle.get_cp(t, type="center"), anchor=(.5, .5))], zorder=t.besk["zorder"]+1)
                renpy.play("content/sfx/sound/be/poisoned.mp3", channel="audio")
                txt = Text("%d"%damage, style="content_label", color="red", size=15)
                renpy.show("bb", what=txt, at_list=[battle_bounce(store.battle.get_cp(t, type="tc", yo=-10))], zorder=t.besk["zorder"]+2)
                renpy.pause(1.5*persistent.battle_speed)
                renpy.hide("poison")
                renpy.pause(.2*persistent.battle_speed)
                renpy.hide("bb")

            if t.health > damage:
                t.health -= damage
                msg = "%s is poisoned! {color=forestgreen}☠: %d{/color}" % (t.name, damage)
                battle.log(msg)
            else:
                t.health = 1
                death = RPG_Death(t,
                                  msg="{color=red}Poison took out %s!\n{/color}" % t.name,
                                  death_effect="dissolve")
                death.apply_effects()

            if not battle.logical:
                t.update_delayed()

            self.counter -= 1

    class DefenceBuff(BE_Event):
        def __init__(self, source, target, duration, bonus, multi, icon, group, gfx_effect):
            # bonus and multi both expect dicts if mods are desirable.
            self.target = target
            self.source = source
            #self.buff = True # We may need this for debuffing later on?

            self.counter = duration

            self.icon = icon
            self.gfx_effect = gfx_effect
            self.activated_this_turn = False # Flag used to pass to gfx methods that this buff was triggered.
            self.group = group # No two buffs from the same group can be applied twice.
            # We also add the icon to targets status overlay:
            target.status_overlay.append(self.icon)

            if bonus:
                self.defence_bonus = bonus

            if multi:
                self.defence_multiplier = multi

        def check_conditions(self):
            if battle.controller == self.target:
                return True

        def kill(self):
            if not self.counter:
                t = self.target

                t.status_overlay.remove(self.icon)
                msg = "{color=skyblue}Defence Buff on %s has worn out!{/color}" % (t.name)
                battle.log(msg)
                return True

        def apply_effects(self):
            self.counter -= 1

    # Actions:
    class MultiAttack(BE_Action):
        """
        Base class for multi attack skills, which basically show the same displayable and play sounds (conditioned),
        """
        def __init__(self):
            super(MultiAttack, self).__init__()

        def show_main_gfx(self, battle, attacker, targets):
            # Shows the MAIN part of the attack and handles appropriate sfx.
            main_effect = self.main_effect

            gfx = main_effect["gfx"]
            sfx = main_effect["sfx"]

            times = main_effect.get("times", 2)
            interval = main_effect.get("interval", .2)
            sd_duration = main_effect.get("sd_duration", .3)*persistent.battle_speed
            alpha_fade = main_effect.get("alpha_fade", .3)
            webm_size  = main_effect.get("webm_size", ())

            # GFX:
            if gfx:
                what = self.get_main_gfx()

                # Flip the attack image if required:
                if main_effect.get("hflip", None) and battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0]:
                    what = Transform(what, xzoom=-1)

                # Posional properties:
                aim = main_effect["aim"]
                point = aim.get("point", "center")
                anchor = aim.get("anchor", (.5, .5))
                xo = aim.get("xo", 0)
                yo = aim.get("yo", 0)

                # Create a UDD:
                what = ChainedAttack(what, sfx, chain_sfx=True, times=times, delay=interval, sd_duration=sd_duration, alpha_fade=alpha_fade, webm_size=webm_size)

                for index, target in enumerate(targets):
                    gfxtag = "attack" + str(index)
                    renpy.show(gfxtag, what=what, at_list=[Transform(pos=battle.get_cp(target, type=point, xo=xo, yo=yo), anchor=anchor)], zorder=target.besk["zorder"]+1)


    class ArealSkill(BE_Action):
        """
        Simplest attack, usually simple magic.
        """
        def __init__(self):
            super(ArealSkill, self).__init__()

        def show_main_gfx(self, battle, attacker, targets):
            # Shows the MAIN part of the attack and handles appropriate sfx.
            main_effect = self.main_effect

            gfx = main_effect["gfx"]
            sfx = main_effect["sfx"]

            # SFX:
            if sfx:
                if isinstance(sfx, (list, tuple)) and not main_effect.get("loop_sfx", False):
                    sfx = choice(sfx)
    
                renpy.music.play(sfx, channel='audio')

            # GFX:
            if gfx:
                what = self.get_main_gfx()
                # Flip the attack image if required:
                if main_effect.get("hflip", False) and battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0]:
                    what = Transform(what, xzoom=-1)

                target = targets[0]
                teampos = target.beteampos
                aim = main_effect["aim"]
                point = aim.get("point", "center")
                anchor = aim.get("anchor", (.5, .5))
                xo = aim.get("xo", 0)
                yo = aim.get("yo", 0)

                gfxtag = "areal"
                if teampos == "l":
                    teampos = battle.BDP["perfect_middle_right"]
                else:
                    teampos = battle.BDP["perfect_middle_left"]
                renpy.show(gfxtag, what=what, at_list=[Transform(pos=battle.get_cp(target, type=point, xo=xo, yo=yo, override=teampos), anchor=anchor)], zorder=1000)

        def hide_main_gfx(self, targets):
            renpy.hide("areal")


    class P2P_Skill(BE_Action):
        """ ==> @Review: There may not be a good reason for this to be a magical attack instead of any attack at all!
        Point to Point magical strikes without any added effects. This is one step simpler than the ArrowsSkill attack.
        Used to attacks like FireBall.
        """
        def __init__(self):
            super(P2P_Skill, self).__init__()

            self.projectile_effects = { "gfx" : None, "sfx" : None, "duration": 1.0 }

        def show_main_gfx(self, battle, attacker, targets):
            # We simply want to add projectile effect here:
            pro_gfx = self.projectile_effects["gfx"]
            pro_sfx = self.projectile_effects["sfx"]
            pause = self.projectile_effects["duration"]*persistent.battle_speed

            missle = Transform(pro_gfx, xzoom=-1, xanchor=1.0) if battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0] else pro_gfx

            initpos = battle.get_cp(attacker, type="fc", xo=60)

            if pro_sfx:
                if isinstance(pro_sfx, (list, tuple)):
                    pro_sfx = choice(pro_sfx)
                renpy.sound.play(pro_sfx)

            for index, target in enumerate(targets):
                aimpos = battle.get_cp(target, type="center")
                renpy.show("launch" + str(index), what=missle,
                        at_list=[move_from_to_pos_with_easeout(start_pos=initpos, end_pos=aimpos, t=pause),
                        Transform(anchor=(.5, .5))], zorder=target.besk["zorder"]+50)

            renpy.pause(pause)

            for index, target in enumerate(targets):
                renpy.hide("launch" + str(index))

            # Shows the MAIN part of the attack and handles appropriate sfx.
            gfx = self.main_effect["gfx"]
            sfx = self.main_effect["sfx"]

            # SFX:
            if sfx:
                if isinstance(sfx, (list, tuple)):
                    sfx = choice(sfx)
                renpy.sound.play(sfx)

            # GFX:
            if gfx:
                what = self.get_main_gfx()

                aim = self.main_effect["aim"]
                point = aim.get("point", "center")
                anchor = aim.get("anchor", (.5, .5))
                xo = aim.get("xo", 0)
                yo = aim.get("yo", 0)

                c0 = self.main_effect.get("hflip", False)
                c1 = battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0]
                if c0 and c1:
                    what = Transform(what, xzoom=-1)

                for index, target in enumerate(targets):
                    gfxtag = "attack" + str(index)
                    renpy.show(gfxtag, what=what,
                        at_list=[Transform(pos=battle.get_cp(target, type=point, xo=xo, yo=yo), anchor=anchor)],
                        zorder=target.besk["zorder"]+51)

        def hide_main_gfx(self, targets):
            for i in xrange(len(targets)):
                gfxtag = "attack" + str(i)
                renpy.hide(gfxtag)


    class P2P_ArealSkill(P2P_Skill):
        """
        Used to attacks like FireBall.
        """
        def __init__(self):
            super(P2P_ArealSkill, self).__init__()

        def show_main_gfx(self, battle, attacker, targets):
            # We simply want to add projectile effect here:
            pro_gfx = self.projectile_effects["gfx"]
            pro_sfx = self.projectile_effects["sfx"]
            pause = self.projectile_effects["duration"]*persistent.battle_speed

            target = targets[0]

            missle = Transform(pro_gfx, zoom=-1, xanchor=1.0) if battle.get_cp(attacker)[0] > battle.get_cp(target)[0] else pro_gfx

            initpos = battle.get_cp(attacker, type="fc", xo=60)

            if pro_sfx:
                if isinstance(pro_sfx, (list, tuple)):
                    pro_sfx = choice(pro_sfx)
                renpy.sound.play(pro_sfx)

            aimpos = battle.BDP["perfect_middle_right"] if target.beteampos == "l" else battle.BDP["perfect_middle_left"]

            renpy.show("launch", what=missle, at_list=[move_from_to_pos_with_easeout(start_pos=initpos, end_pos=aimpos, t=pause), Transform(anchor=(.5, .5))], zorder=target.besk["zorder"]+1000)
            renpy.pause(pause)
            renpy.hide("launch")

            # Shows the MAIN part of the attack and handles appropriate sfx.
            gfx = self.main_effect["gfx"]
            sfx = self.main_effect["sfx"]

            # SFX:
            if sfx:
                if isinstance(sfx, (list, tuple)):
                    sfx = choice(sfx)
                renpy.sound.play(sfx)

            # GFX:
            if gfx:
                what = self.get_main_gfx()

                aim = self.main_effect["aim"]
                point = aim.get("point", "center")
                anchor = aim.get("anchor", (.5, .5))
                xo = aim.get("xo", 0)
                yo = aim.get("yo", 0)

                renpy.show("projectile", what=what, at_list=[Transform(pos=aimpos, anchor=anchor)], zorder=target.besk["zorder"]+1001)

        def hide_main_gfx(self, targets):
            renpy.hide("projectile")


    class ArrowsSkill(P2P_Skill):
        """This is the class I am going to comment out really well because this spell was not originally created by me
        and yet I had to rewrite it completely for new BE.
        """
        def __init__(self):
            super(ArrowsSkill, self).__init__()

            self.firing_effects = { "gfx" : None, "sfx" : None, "duration": .6 }

        def show_main_gfx(self, battle, attacker, targets):
            firing_gfx = self.firing_effects["gfx"]
            firing_sfx = self.firing_effects["sfx"]
            pause = self.firing_effects["duration"]*persistent.battle_speed

            bow = Transform(firing_gfx, zoom=-1, xanchor=1.0) if battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0] else firing_gfx

            if firing_sfx:
                if isinstance(firing_sfx, (list, tuple)):
                    firing_sfx = choice(firing_sfx)
                renpy.sound.play(firing_sfx)

            castpos = battle.get_cp(attacker, type="fc", xo=30)

            renpy.show("casting", what=bow, at_list=[Transform(pos=castpos, yanchor=.5)], zorder=attacker.besk["zorder"]+50)
            renpy.pause(pause)

            # We simply want to add projectile effect here:
            pro_gfx = self.projectile_effects["gfx"]
            pro_sfx = self.projectile_effects["sfx"]
            pause = self.projectile_effects["duration"]*persistent.battle_speed

            missle = Transform(pro_gfx, zoom=-1, xanchor=1.0) if battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0] else pro_gfx

            if pro_sfx:
                if isinstance(pro_sfx, (list, tuple)):
                    pro_sfx = choice(pro_sfx)
                renpy.sound.play(pro_sfx)

            castpos = battle.get_cp(attacker, type="fc", xo=75)

            for index, target in enumerate(targets):
                aimpos = battle.get_cp(target, type="center", yo=-20)
                renpy.show("launch" + str(index), what=missle, at_list=[
                           move_from_to_pos_with_easeout(start_pos=castpos, end_pos=aimpos, t=pause),
                           Transform(anchor=(.5, .5))],
                           zorder=target.besk["zorder"]+51)

            renpy.pause(pause)

            for index, target in enumerate(targets):
                renpy.hide("launch" + str(index))

            # Shows the MAIN part of the attack and handles appropriate sfx.
            gfx = self.main_effect["gfx"]
            sfx = self.main_effect["sfx"]

            # SFX:
            if sfx:
                if isinstance(sfx, (list, tuple)):
                    sfx = choice(sfx)
                renpy.sound.play(sfx)

            # GFX:
            if gfx:
                what = self.get_main_gfx()

                # pause = self.main_effect["duration"]
                aim = self.main_effect["aim"]
                point = aim.get("point", "center")
                anchor = aim.get("anchor", (.5, .5))
                xo = aim.get("xo", 0)
                yo = aim.get("yo", 0)

                for index, target in enumerate(targets):
                    gfxtag = "attack" + str(index)
                    renpy.show(gfxtag, what=what, at_list=[Transform(pos=battle.get_cp(target, type=point, xo=xo, yo=yo), anchor=anchor)], zorder=target.besk["zorder"]+52)

        def hide_main_gfx(self, targets):
            renpy.hide("casting")
            renpy.with_statement(Dissolve(.5))
            for i in xrange(len(targets)):
                gfxtag = "attack" + str(i)
                renpy.hide(gfxtag)


    class ATL_ArealSkill(ArealSkill):
        """This one used ATL function for the attack, ignoring all usual targeting options.

        As a rule, it expects to recieve left and right targeting option we normally get from team positions for Areal Attacks.
        """
        def __init__(self):
            super(ATL_ArealSkill, self).__init__()

        def show_main_gfx(self, battle, attacker, targets):
            # Shows the MAIN part of the attack and handles appropriate sfx.
            sfx = self.main_effect["sfx"]
            gfx = self.main_effect["atl"]

            # SFX:
            if sfx:
                if isinstance(sfx, (list, tuple)) and not self.main_effect.get("loop_sfx", False):
                    sfx = choice(sfx)
                renpy.music.play(sfx, channel='audio')

            # GFX:
            gfx = getattr(store, gfx)
            gfx = gfx(*self.main_effect["left_args"]) if battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0] else gfx(*self.main_effect["right_args"])
            gfxtag = "areal"
            renpy.show(gfxtag, what=gfx, zorder=1000)


    class FullScreenCenteredArealSkill(ArealSkill):
        """Simple overwrite, negates offsets and shows the attack over the whole screen aligning it to truecenter.
        """
        def __init__(self):
            super(FullScreenCenteredArealSkill, self).__init__()

        def show_main_gfx(self, battle, attacker, targets):
            # Shows the MAIN part of the attack and handles appropriate sfx.
            gfx = self.main_effect["gfx"]
            sfx = self.main_effect["sfx"]

            # SFX:
            if sfx:
                if isinstance(sfx, (list, tuple)) and not self.main_effect.get("loop_sfx", False):
                    sfx = choice(sfx)
                renpy.music.play(sfx, channel='audio')

            # GFX:
            if gfx:
                gfxtag = "areal"
                renpy.show(gfxtag, what=gfx, at_list=[Transform(align=(.5, .5))], zorder=1000)


    class BasicHealingSpell(BE_Action):
        def __init__(self):
            super(BasicHealingSpell, self).__init__()

        def effects_resolver(self, targets):
            source = self.source
            base_restore = self.get_attack()

            for t in targets:
                base_restore = t.maxhp * self.effect
                effects = []

                # We get the multi and any effects that those may bring:
                restore = round_int(BE_Core.damage_modifier(source, t, base_restore, "healing"))
                effects.append(("healing", restore))

                t.dmg_font = "lightgreen" # Color the battle bounce green!

                # String for the log:
                temp = "{color=teal}%s{/color} used %s to heal %s!" % (source.nickname, self.name, t.name)
                self.log_to_battle(effects, restore, source, t, message=temp)

        def apply_effects(self, targets):
            for t in targets:
                t.health += t.beeffects[0]
                if t.health > t.maxhp:
                    t.health = t.maxhp

            self.settle_cost()

    class BasicPoisonSpell(BE_Action):
        def __init__(self):
            super(BasicPoisonSpell, self).__init__()
            self.event_class = PoisonEvent
            self.buff_group = self.__class__
            self.event_duration = (3, 5)  # Active for 3-5 turns

    class ReviveSpell(BE_Action):
        def __init__(self):
            super(ReviveSpell, self).__init__()

        def effects_resolver(self, targets):
            char = self.source

            for t in targets:
                revive = int(t.maxhp * (0.1 + 0.2*random.random()))

                t.beeffects = [revive]

                # String for the log:
                s = ("{color=palegreen}%s revives %s!{/color}" % (char.nickname, t.name))
                t.dmg_font = "lightgreen" # Color the battle bounce green!

                battle.log(s)

        def apply_effects(self, targets):
            for t in targets:
                battle.corpses.remove(t)
                t.health = t.beeffects[0]

            self.settle_cost()

            return []

        def show_main_gfx(self, battle, attacker, targets):
            for target in targets:
                renpy.show(target.betag, what=target.besprite, at_list=[Transform(pos=target.cpos), fade_from_to(start_val=0, end_val=1.0, t=1.0, wait=.5)], zorder=target.besk["zorder"])
            super(ReviveSpell, self).show_main_gfx(battle, attacker, targets)


    class DefenceBuffSpell(BE_Action):
        def __init__(self):
            super(DefenceBuffSpell, self).__init__()
            self.event_class = DefenceBuff

            self.defence_bonus = None      # direct def bonus
            self.defence_multiplier = None # def multiplier
            self.event_duration = (5, 8)   # Active for 5-8 turns
            self.buff_icon = "content/gfx/be/fists.webp"
            self.buff_group = self.__class__
            self.defence_gfx = "default"

        def effects_resolver(self, targets):
            source = self.source
            type = self.damage[0] # FIXME what about multi type buffs? Partial resist?
            group = self.buff_group

            for t in targets:
                effects = []

                # We get the multi and any effects that those may bring:
                effect = round_int(BE_Core.damage_modifier(source, t, 100, type)) # BASE_EFFECT == 100
                if effect:
                    # Check if event is in play already:
                    for event in store.battle.mid_turn_events:
                        if t == event.target and event.group == group:
                            battle.log("{color=skyblue}%s is already buffed by %ss spell!{/color}" % (t.nickname, event.source.name))
                            break
                    else:
                        temp = self.event_class(source, t, randint(*self.event_duration),
                                                self.defence_bonus, self.defence_multiplier,
                                                self.buff_icon, group, self.defence_gfx)
                        battle.mid_turn_events.append(temp)
                        temp = "{color=skyblue}%s buffs %ss defence!{/color}" % (source.nickname, t.name)
                        self.log_to_battle(effects, effect, source, t, message=temp)
                else:
                    temp = "{color=skyblue}%s resisted the defence buff!{/color}" % (t.name)
                    self.log_to_battle(effects, effect, source, t, message=temp)

        def apply_effects(self, targets):
            self.settle_cost()


    class ConsumeItem(BE_Action):
        def __init__(self, item):
            super(ConsumeItem, self).__init__()
            self.item = item # item to use...

            self.type = "sa"
            self.attributes = ["item"]
            self.delivery = "status"
            self.kind = "item"
            self.desc = "Use an item!"

            self.target_damage_effect["gfx"] = None
            self.target_sprite_damage_effect["gfx"] = "being_healed"
            self.main_effect["gfx"] = None
            self.main_effect["sfx"] = "content/sfx/sound/be/heal2.mp3"

            super(ConsumeItem, self).init()

        def execute(self, source, t=None):
            self.source = source
            self.effects_resolver(t)
            return self.apply_effects(t)

        def effects_resolver(self, targets):
            source = self.source
            # assert(len(targets) == 1)
            target = targets[0]
            if target == source:
                temp = "%sself" % source.char.op
            else:
                temp = target.name
            battle.log("{color=teal}%s{/color} uses a %s on %s!" % (source.nickname, self.item.id, temp))

        def apply_effects(self, targets):
            global equipment_safe_mode
            item = self.item
            # assert(len(targets) == 1)
            source = self.source
            target = targets[0]
            tc = target.char
            if target != source:
                if not can_transfer(source.char, tc, item):
                    return False # can not give to the target
                esm = equipment_safe_mode
                equipment_safe_mode = True
                if not can_equip(item, tc, silent=False):
                    equipment_safe_mode = esm
                    return False # can not equip
                equipment_safe_mode = esm
                transfer_items(source.char, tc, item)
            else:
                esm = equipment_safe_mode
                equipment_safe_mode = True
                if not can_equip(item, tc, silent=False):
                    equipment_safe_mode = esm
                    return False # can not equip
                equipment_safe_mode = esm
            target.restore_char()
            tc.equip(item)
            target.load_char(tc)
            source.take_pp()
            return True
