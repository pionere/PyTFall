init -11 python:
    def mod_to_tooltip(mod):
        t = ""
        for i in mod:
            t += i + ": +" + str(mod[i]) + " "
        return t

    def show_all_targeting_closshairs(targets):
        for index, t in enumerate(targets):
            temp = dict(what=crosshair_red,
                        at_list=[Transform(pos=battle.get_cp(t, "center",
                                           use_absolute=True),
                        anchor=(.5, .5))], zorder=t.besk["zorder"]+1)
            renpy.show("enemy__"+str(index), **temp)

    def hide_all_targeting_closshairs(targets):
        for index, t in enumerate(targets):
            renpy.hide("enemy__"+str(index))

    def new_style_conflict_resolver(off_team, def_team, simple_ai=True):
        for fighter in chain(off_team, def_team):
            # dress for fight - not needed at the moment
            #if fighter.last_known_aeq_purpose not in FIGHTING_AEQ_PURPOSES and fighter.autoequip and fighter != hero:
            #    fighter.equip_for("Fighting")
            # create AI-controller
            fighter.controller = BE_AI(fighter) if simple_ai else Complex_BE_AI(fighter)

        max_turns=15*(len(off_team)+len(def_team))

        global battle
        battle = BE_Core(logical=True, max_turns=max_turns)
        battle.teams = [off_team, def_team]

        if DEBUG_BE:
            msg = "\n    Custom Logical Combat Scenario ===================================================>>>>"
            msg += "\n{} VS {}".format(str([c.name for c in off_team.members]), str([c.name for c in def_team.members]))
            msg += "\nUsing simple ai: {}.".format(simple_ai)
            be_debug(msg)

        tl.start("logical combat: BATTLE")
        battle.start_battle()
        tl.end("logical combat: BATTLE")
        be_debug("\n\n")

        # Reset the controllers:
        off_team.reset_controller()
        def_team.reset_controller()

        return battle

    def get_random_battle_track():
        # get a list of all battle tracks:
        battle_tracks = []
        folder = os.path.join("content", "sfx", "music", "be")
        path = os.path.join(gamedir, folder, '.')
        for fn in os.walk(path).next()[2]:
            if fn.endswith(MUSIC_EXTENSIONS):
                battle_tracks.append(os.path.join(folder, fn))
        return choice(battle_tracks)

    def be_hero_escaped(team):
        '''Punish team for escaping'''
        for i in team:
            i.AP = 0
            mod_by_max(i, "vitality", -.3)
            mod_by_max(i, "mp", -.3)

    def run_default_be(enemy_team, slaves=False, your_team=None,
                       background="battle_arena_1",
                       end_background=None,
                       track="random", prebattle=True, death=False,
                       skill_lvl=float("inf"), give_up=None, use_items=False):
        """
        Launches BE with MC team vs provided enemy team, returns True if MC won and vice versa
        - if slaves == True, slaves in MC team will be inside BE with passive AI, otherwise they won't be there
        - background by default is arena, otherwise could be anything,
            like interactions_pick_background_for_fight(gm.label_cache) for GMs
            or interactions_pick_background_for_fight(pytfall.world_events.event_instance("event name").label_cache) for events
        - track by default is random, otherwise it could be a path to some track
        - if prebattle is true, there will be prebattle quotes inside BE from characters before battle starts
        - if death == True, characters in MC team will die if defeated, otherwise they will have 1 hp left
        """
        if your_team is None:
            your_team = Team(name="Your Team")
            for member in hero.team:
                if member.status == "free":
                    member.controller = None # no AI -> controlled by the player
                    your_team.add(member)
                elif slaves: # and member.status == "slave"
                    member.controller = BE_AI(member)
                    your_team.add(member)

        # Controllers:
        for member in enemy_team:
            member.controller = Complex_BE_AI(member)

        pre_aps = [(member.AP, member.PP) for member in your_team]

        global battle
        battle = BE_Core(background, start_sfx=get_random_image_dissolve(1.5),
                    end_bg=end_background, end_sfx=dissolve,
                    music=track, quotes=prebattle,
                    max_skill_lvl=skill_lvl, give_up=give_up,
                    use_items=use_items)
        battle.teams = [your_team, enemy_team]
        battle.start_battle()

        your_team.reset_controller()
        enemy_team.reset_controller()

        for member in your_team:
            if member in battle.corpses:
                if death:
                    kill_char(member)
                else:
                    member.set_stat("health", 1)
                    if member != hero:
                        member.mod_stat("joy", -randint(5, 15))

        rv = battle.combat_status
        if rv == "escape":
            be_hero_escaped(your_team)
        elif rv != "surrender":
            rv = battle.win
            if rv is True:
                for mob in enemy_team:
                    if mob.__class__ == Mob:
                        defeated_mobs.add(mob.id)

                ap_used = {}
                for member, aps in zip(hero.team, pre_aps):
                    ap_used[member] = aps[0] - member.AP + (aps[1] - member.PP)/100.0 # PP_PER_AP = 100

                if persistent.battle_results:
                    renpy.call_screen("give_exp_after_battle", your_team, enemy_team, ap_used)
                else:
                    for member in hero.team:
                        member.gfx_mod_exp(exp_reward(member, enemy_team, exp_mod=ap_used[member]))

        return rv
