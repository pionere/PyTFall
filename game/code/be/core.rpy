init -1 python: # Core classes:
    """
    This is our version of turn based BattleEngine.
    I think that we can use zorders on master layer instead of messing with multiple layers.
    """
    class BE_Modifiers(_object):
        FIELDS = ["ch_multiplier", "damage_multiplier", "delivery_bonus", "delivery_multiplier", "el_damage", "el_defence", "el_absorbs", "defence_bonus", "defence_multiplier", "evasion_bonus"]
        def __init__(self, source):
            self.ch_multiplier = 0
            self.damage_multiplier = 0
            self.delivery_bonus = {}
            self.delivery_multiplier = {}
            self.el_damage = {}
            self.el_defence = {}
            self.el_absorbs = {}
            self.defence_bonus = {}
            self.defence_multiplier = {}
            self.evasion_bonus = 0

            for field in self.FIELDS:
                value = getattr(source, field, None)
                if value is not None:
                    setattr(self, field, value)
                    delattr(source, field)

        def __eq__(self, other):
            """
            Checks for equality with the given argument.
            other = The object to check against.
            """
            if not isinstance(other, BE_Modifiers): return False
            for field in self.FIELDS:
                if getattr(self, field) != getattr(other, field):
                    return False
            return True

        def __ne__(self, other):
            """
            Checks for inequality with the given argument.
            other = The object to check against.
            """
            return not self.__eq__(other)

        def merge(self, other):
            """Merge two flat(!) BE_Modifiers into one.
            """
            self.ch_multiplier += other.ch_multiplier
            self.damage_multiplier += other.damage_multiplier
            merge_dicts(self.delivery_bonus, other.delivery_bonus) 
            merge_dicts(self.delivery_multiplier, other.delivery_multiplier)
            merge_dicts(self.el_damage, other.el_damage)
            merge_dicts(self.el_defence, other.el_defence)
            merge_dicts(self.el_absorbs, other.el_absorbs)
            merge_dicts(self.defence_bonus, other.defence_bonus)
            merge_dicts(self.defence_multiplier, other.defence_multiplier)
            self.evasion_bonus += other.evasion_bonus

        def get_flat_modifier(self, level):
            """Get a flat version of a non-flat BE_Modifiers
            """
            result = deepcopy(self)
            delivery_bonus = {}
            for delivery, bonus in self.delivery_bonus.iteritems():
                # Reference: (minv, maxv, lvl)
                minv, maxv, lvl = bonus
                if lvl > level:
                    maxv = minv + (maxv-minv)*level/float(lvl)
                maxv += delivery_bonus.get(delivery, 0)
                delivery_bonus[delivery] = maxv
            result.delivery_bonus = delivery_bonus

            # Reference: (minv, maxv, lvl)
            if self.evasion_bonus:
                minv, maxv, lvl = self.evasion_bonus
                if lvl > level:
                    maxv = minv + (maxv-minv)*level/float(lvl)
                result.evasion_bonus = maxv

            defence_bonus = {}
            for delivery, bonus in self.defence_bonus.iteritems():
                # Reference: (minv, maxv, lvl)
                minv, maxv, lvl = bonus
                if lvl > level:
                    maxv = minv + (maxv-minv)*level/float(lvl)
                maxv += defence_bonus.get(delivery, 0)
                defence_bonus[delivery] = maxv
            result.defence_bonus = defence_bonus
            return result

    class BE_Combatant(_object):
        def __init__(self, team, idx, pos):
            char = team._members[idx]

            # Allegiance:
            self.allegiance = team

            # BE assets:
            #self.besprite = None # Used to keep track of sprite displayable in the BE.
            #self.besprite_size = None # Sprite size in pixels.
            #self.betag = None # Tag to keep track of the sprite.
            #self.besk = None # BE Show **Kwargs!
            #self.dpos = None # Default position based on row + team.
            #self.cpos = None # Current position of a sprite.

            # TODO obsolete attributes -> remove
            #self.sopos = () # Status underlay position, which should be fixed.
            #self.dmg_font = "red"

            #self.beinx = 0 # Passes index from logical execution to SFX setup.
            #self.beteampos = pos # This manages team position bound to target (left or right on the screen).
            #self.row = 1 # row on the battlefield, used to calculate range of weapons.
            #self.allegiance = None # BE will default this to the team name.
            self.beeffects = []
            self.status_overlay = [] # Status icons over the sprites.

            # Position:
            self.beteampos = pos
            if len(team) == 3 and idx < 2:
                self.beinx = 1 - idx
            else:
                self.beinx = idx
            front_row = char.front_row
            if pos == "l":
                self.row = front_row
            else: # Case "r"
                self.row = 3 - front_row

            self.load_char(char)

        def load_char(self, char):
            self.char = char

            # most commonly used variables during the battle
            self.name = char.name
            self.nickname = char.nickname
            temp = char.status
            if temp == "slave":
                # slaves should not battle
                self.attack_skills = self.magic_skills = []
            else:
                self.attack_skills = char.attack_skills
                self.magic_skills = char.magic_skills
            self.status = temp
            self.PP = char.PP

            temp = char.stats
            self.health = self.delayedhp = temp._get_stat("health")
            self.maxhp = temp.get_max("health")
            #self.minhp = temp.get_min("health")
            self.mp = self.delayedmp = temp._get_stat("mp")
            self.maxmp = temp.get_max("mp")
            self.minmp = temp.get_min("mp")
            self.vitality = self.delayedvit = temp._get_stat("vitality")
            self.maxvit = temp.get_max("vitality")
            self.minvit = temp.get_min("vitality")

            self.attack = temp._get_stat("attack")
            self.agility = temp._get_stat("agility")
            self.luck = temp._get_stat("luck")
            self.defence = temp._get_stat("defence")
            self.constitution = temp._get_stat("constitution")
            self.magic = temp._get_stat("magic")
            self.intelligence = temp._get_stat("intelligence")

            self.resist = char.resist

            # cached item bonuses
            temp = getattr(char, "eqslots", None)
            if temp is not None:
                temp = temp.itervalues()
            item_modifiers = BE_Core.get_item_modifiers(temp)
            # cached trait bonuses
            trait_modifiers = BE_Core.get_trait_modifiers(char.traits, char.level)

            # prepare modifiers
            BE_Core.merge_modifiers(trait_modifiers, item_modifiers)

            #  base critical hit chance:
            trait_modifiers[0] *= 100.0 

            self.modifiers = trait_modifiers

            # Controller:
            temp = char.controller
            if temp is not None:
                temp.init(self)
            self.controller = temp

        def set_besprite(self, besprite):
            self.besprite = besprite

            char = self.char
            if isinstance(char, Mob):
                webm_spites = mobs[char.id].get("be_webm_sprites", None)
                if webm_spites:
                    self.besprite_size =  webm_spites["idle"][1]
                    return
            self.besprite_size = get_size(besprite)

        # Delayed stats to use it in BE so we can delay updating stats on the GUI.
        def update_delayed(self):
            self.delayedhp = self.health
            self.delayedmp = self.mp
            self.delayedvit = self.vitality

        def get_be_items(self, use_items=1):
            # be_items only for non-logical battles (for the moment? Mobs do not have inventory anyway)
            if not hasattr(self.char, "inventory"):
                return None
            be_items = OrderedDict()
            for item, amount in self.char.inventory.items.iteritems():
                if use_items is 2 or item.be:
                    be_items[item] = amount
            return be_items

        def get_default_attack(self):
            return getattr(self, "last_skill", False) or self.char.default_attack_skill

        def take_pp(self):
            if self.PP < 10:
                return False
            self.PP -= 10
            return True

        def has_pp(self):
            return self.PP >= 10

        def restore_char(self):
            self.char.PP = self.PP

            self.char.set_stat("health", self.health)
            self.char.set_stat("mp", self.mp)
            self.char.set_stat("vitality", self.vitality)

    class BE_Core(_object):
        BDP = dict()               # BE DEFAULT POSITIONS
        TYPE_TO_COLOR_MAP = dict() # DAMAGE TYPE TO COLOR MAP
        DELIVERY = set(["magic", "ranged", "melee", "status"]) # Damage/Effects Delivery Methods!
        DAMAGE = {"physical": "{image=physical_be_viewport}", "fire": "{image=fire_element_be_viewport}", "water": "{image=water_element_be_viewport}",
                  "ice": "{image=ice_element_be_viewport}", "earth": "{image=earth_element_be_viewport}", "air": "{image=air_element_be_viewport}",
                  "electricity": "{image=ele_element_be_viewport}", "light": "{image=light_element_be_viewport}", "darkness": "{image=darkness_element_be_viewport}",
                  "healing": "{image=healing_be_viewport}", "poison": "{image=poison_be_viewport}"} # Damage (Effect) types...
        DAMAGE_20 = {"physical": "{image=physical_be_size20}", "fire": "{image=fire_element_be_size20}", "water": "{image=water_element_be_size20}",
                     "ice": "{image=ice_element_be_size20}", "earth": "{image=earth_element_be_size20}", "air": "{image=air_element_be_size20}",
                     "electricity": "{image=ele_element_be_size20}", "light": "{image=light_element_be_size20}", "darkness": "{image=darkness_element_be_size20}",
                     "healing": "{image=healing_be_size20}", "poison": "{image=poison_be_size20}"}

        """Main BE attrs, data and the loop!
        """
        def __init__(self, logical=False,
                     max_skill_lvl=float("inf"), max_turns=1000,
                     use_items=False, give_up=None,
                     bg=None, start_sfx=None, end_bg=None, end_sfx=None,
                     music=None, quotes=False):
            """Creates an instance of BE scenario.
            :param logical: Just the calculations, without pause/gfx/sfx.
            :param max_skill_lvl: limit the allowed skills (for e.g. indoor battles)
            :param max_turns: limit the number of turns to prevent too long battles (due to resistances/immunities/lowPP)
            :param give_up: allows to avoid battle in one way or another
            :param use_items: allows use of items during combat.
            --- non-logical parameters ---
            :param bg: the background of the battle
            :param start_sfx: the transition from the current-bg to the battle-bg
            :param end_bg: the background after the battle
            :param end_sfx: the transition from the battle-bg to the end_bg
            :param music: the track to play, or "random" to choose a random battle track
            :param quotes: Decide if we run quotes at the start of the battle.
            """
            self.max_skill_lvl = max_skill_lvl
            self.max_turns = max_turns
            self.give_up = give_up
            self.use_items = use_items
            self.logical = logical
            self.logical_counter = 0

            if not logical:
                self.predict = []
                # Background we'll use.
                if bg:
                    self.predict.append(bg)
                    renpy.start_predict(bg)

                    if isinstance(bg, basestring):
                        if check_image_extension(bg):
                            bg = Image(bg)
                        else:
                            bg = ImageReference("bg " + bg)
                else:
                    bg = Null()
                self.bg = ConsitionSwitcher("default", {"default": bg,
                                                        "black": Solid("#000000"),
                                                        "mirage": Mirage(bg, resize=get_size(bg),
                                                        amplitude=.04, wavelength=10, ycrop=10)})

                self.start_sfx = start_sfx
                self.end_bg = end_bg
                self.end_sfx = end_sfx
                self.music = get_random_battle_track() if music == "random" else music

                self.quotes = quotes

            self.teams = list() # Each team represents a faction on the battlefield. 0 index for left team and 1 index for right team.
            self.queue = list() # List of events in BE..
            self.combat_status = None # general status of the battle, used to run away from BF atm.
            self.corpses = set() # Anyone died in the BE.

            # Whatever controls the current queue of the loop is the controller.
            self.controller = None # The current character (player or AI combatant)
            self.winner = None
            self.win = None # We set this to True if left team wins and to False if right.
            self.combat_log = list()
            # We may want to delay logging something to the end of turn.
            self.delayed_log = list()

            # Events:
            self.start_turn_events = list() # Events we execute on start of the turn.
            self.mid_turn_events = list() # Events to execute after controller was set.
            self.end_turn_events = list() # Events we execute on the end of the turn.
            self.terminate = False

        @staticmethod
        def init():
            # BE DEFAULT POSITIONS *positions are tuples in lists that go from top to bottom.
            BDP = {0: [(230, 540), (190, 590), (150, 640)], # Left (Usually player) teams backrow default positions.
                   1: [(360, 540), (320, 590), (280, 640)]} # Left (Usually player) teams frontrow default positions.
            BDP[3] = list((config.screen_width-t[0], t[1]) for t in BDP[0]) # BackRow, Right (Usually enemy).
            BDP[2] = list((config.screen_width-t[0], t[1]) for t in BDP[1]) # FrontRow, Right (Usually enemy).

            # Perfect middle positioning:
            y = BDP[1][1][1] - 100
            BDP["perfect_middle_left"] = ((BDP[0][1][0] + BDP[1][1][0])/2, y)
            BDP["perfect_middle_right"] = ((BDP[3][1][0] + BDP[2][1][0])/2, y)
            BE_Core.BDP.clear()
            BE_Core.BDP.update(BDP)

            # DAMAGE TYPE TO COLOR MAP
            type_to_color_map = {e.id.lower(): e.font_color for e in tgs.elemental}
            type_to_color_map["poison"] = "forestgreen"
            type_to_color_map["healing"] = "lightgreen"

            BE_Core.TYPE_TO_COLOR_MAP.clear()
            BE_Core.TYPE_TO_COLOR_MAP.update(type_to_color_map)

        @property
        def battle_speed(self):
            value = 1.0/persistent.battle_speed
            return math.log(value, 2)

        @battle_speed.setter
        def battle_speed(self, value):
            persistent.battle_speed = 1.0/2**value

        @staticmethod
        def color_string_by_DAMAGE_type(effect, logstr):
            # Takes a string "s" and colors it based of damage "type".
            # If type is not an element, color will be red or some preset (in this method) default.
            type, value = effect

            if value < 0:
                value = -value
                color = BE_Core.TYPE_TO_COLOR_MAP["healing"]
            else:
                color = BE_Core.TYPE_TO_COLOR_MAP.get(type, "red")

            if logstr is True:
                return "{color=%s}%s: %s{/color}" % (color, BE_Core.DAMAGE.get(type, type), value)
            else:
                return "{color=%s}%s{/color}" % (color, value)

        @staticmethod
        def get_item_modifiers(items):
            critical_hit_chance = 0
            damage_multiplier = 0
            delivery_bonus = {}
            delivery_multiplier = {}
            el_dmg = {} # FIXME unused?
            el_def = {} # FIXME unused?
            absorbs = {}# FIXME unused?
            defence_bonus = {}
            defence_multiplier = {}
            evasion_bonus = 0
            if items is not None:
                for i in items:
                    if i is None:
                        continue
                    bem = i.be_modifiers
                    if bem is None:
                        continue

                    damage_multiplier += bem.damage_multiplier
                    critical_hit_chance += bem.ch_multiplier

                    for delivery, bonus in bem.delivery_bonus.iteritems():
                        bonus += delivery_bonus.get(delivery, 0)
                        delivery_bonus[delivery] = bonus

                    for delivery, mpl in bem.delivery_multiplier.iteritems():
                        mpl += delivery_multiplier.get(delivery, 0)
                        delivery_multiplier[delivery] = mpl

                    evasion_bonus += bem.evasion_bonus

                    for delivery, bonus in bem.defence_bonus.iteritems():
                        bonus += defence_bonus.get(delivery, 0)
                        defence_bonus[delivery] = bonus

                    for delivery, mpl in bem.defence_multiplier.iteritems():
                        mpl += defence_multiplier.get(delivery, 0)
                        defence_multiplier[delivery] = mpl

            return [critical_hit_chance, damage_multiplier, delivery_bonus, delivery_multiplier, el_dmg, el_def, absorbs, defence_bonus, defence_multiplier, evasion_bonus]

        @staticmethod
        def get_trait_modifiers(traits, level):
            critical_hit_chance = 0
            damage_multiplier = 0
            delivery_bonus = {}
            delivery_multiplier = {}
            el_dmg = {}
            el_def = {}
            absorbs = {}
            defence_bonus = {}
            defence_multiplier = {}
            evasion_bonus = 0
            for trait in traits:
                bem = trait.be_modifiers
                if bem is None:
                    continue

                damage_multiplier += bem.damage_multiplier
                critical_hit_chance += bem.ch_multiplier

                for delivery, bonus in bem.delivery_bonus.iteritems():
                    # Reference: (minv, maxv, lvl)
                    minv, maxv, lvl = bonus
                    if lvl > level:
                        maxv = minv + (maxv-minv)*level/float(lvl)
                    maxv += delivery_bonus.get(delivery, 0)
                    delivery_bonus[delivery] = maxv

                for delivery, mpl in bem.delivery_multiplier.iteritems():
                    mpl += delivery_multiplier.get(delivery, 0)
                    delivery_multiplier[delivery] = mpl

                for type, val in bem.el_damage.iteritems():
                    val += el_dmg.get(type, 0)
                    el_dmg[type] = val

                for type, val in bem.el_defence.iteritems():
                    val += el_def.get(type, 0)
                    el_def[type] = val

                # Reference: (minv, maxv, lvl)
                if bem.evasion_bonus:
                    minv, maxv, lvl = bem.evasion_bonus
                    if lvl > level:
                        maxv = minv + (maxv-minv)*level/float(lvl)
                    evasion_bonus += maxv

                # Get all absorption capable traits:
                for type, val in bem.el_absorbs.iteritems():
                    val += absorbs.get(type, 0)
                    absorbs[type] = val

                for delivery, bonus in bem.defence_bonus.iteritems():
                    # Reference: (minv, maxv, lvl)
                    minv, maxv, lvl = bonus
                    if lvl > level:
                        maxv = minv + (maxv-minv)*level/float(lvl)
                    maxv += defence_bonus.get(delivery, 0)
                    defence_bonus[delivery] = maxv

                for delivery, mpl in bem.defence_multiplier.iteritems():
                    mpl += defence_multiplier.get(delivery, 0)
                    defence_multiplier[delivery] = mpl

            return [critical_hit_chance, damage_multiplier, delivery_bonus, delivery_multiplier, el_dmg, el_def, absorbs, defence_bonus, defence_multiplier, evasion_bonus]

        @staticmethod
        def merge_modifiers(target_modifiers, other_modifiers):
            target_modifiers[0] += other_modifiers[0]           # critical_hit_chance
            target_modifiers[1] += other_modifiers[1]           # damage_multiplier
            merge_dicts(target_modifiers[2], other_modifiers[2])# delivery_bonus
            merge_dicts(target_modifiers[3], other_modifiers[3])# delivery_multiplier
            merge_dicts(target_modifiers[4], other_modifiers[4])# el_dmg
            merge_dicts(target_modifiers[5], other_modifiers[5])# el_def
            merge_dicts(target_modifiers[6], other_modifiers[6])# absorbs
            merge_dicts(target_modifiers[7], other_modifiers[7])# defence_bonus
            merge_dicts(target_modifiers[8], other_modifiers[8])# defence_multiplier
            target_modifiers[9] += other_modifiers[9]           # evasion_bonus

        @staticmethod
        def damage_modifier(a, t, damage, type):
            """
            This calculates the multiplier to use with effect of the skill.
            t: target
            damage: Damage (number per type)
            type: Damage Type
            """
            if type in t.resist:
                return 0

            m = 1.0

            # Get multiplier from traits:
            # We decided that any trait could influence this:
            # damage = 0
            # defence = 0

            # Damage first:
            # item_el_dmg + trait_el_dmg
            m += a.modifiers[4].get(type, 0)

            # Defence next:
            # item_el_def + trait_el_def
            m -= t.modifiers[5].get(type, 0)

            damage *= m

            return damage

        @staticmethod
        def check_absorbtion(t, type):
            # Get ratio:
            #         absorbs
            return t.modifiers[6].get(type, None)

        @staticmethod
        def damage_calculator(damage, defense, multiplier, attacker):
            """Used to calc damage of the attack.
            Before multipliers and effects are applied.
            """
            damage *= multiplier * (75.0/(75 + defense)) * uniform(.9, 1.1)

            # Items/Traits Bonus:
            # 1 + item_damage_multiplier + trait_damage_multiplier
            damage *= 1.0 + attacker.modifiers[1]

            return round_int(damage)

        def log(self, report, delayed=False):
            be_debug(report)
            if delayed:
                self.delayed_log.append(report)
            else:
                self.combat_log.append(report)

        def get_faction(self, char):
            # Since factions are simply teams:
            for team in self.teams:
                if char in team:
                    return team

        def main_loop(self):
            """
            Handles events on the battlefield until something that can break the loop is found.
            """
            s = None # Clear this on first BE review.

            while 1:
                # We run events queued at the start of the turn first:
                self.start_turn_events = [event for event in self.start_turn_events if not event.execute()]

                fighter = self.controller = self.next_turn()

                self.mid_turn_events = [event for event in self.mid_turn_events if not event.execute()]

                # If the controller was killed off during the mid_turn_events:
                if fighter not in self.corpses:
                    if fighter.controller is not None:
                        # This character is not controlled by the player so we call the (AI) controller:
                        fighter.controller.execute()
                    else: # Controller is the player:
                        # making known whose turn it is:
                        w, h = fighter.besprite_size
                        renpy.show("its_my_turn", at_list=[Transform(additive=.6, alpha=.7, size=(int(w*1.5), h/3),
                                                           pos=battle.get_cp(fighter, type="bc", yo=20),
                                                           anchor=(.5, 1.0))],
                                                           zorder=fighter.besk["zorder"]+1)

                        skill = None
                        targets = None
                        while 1:
                            rv = renpy.call_screen("pick_skill", fighter)

                            # Skip/Escape Events:
                            if isinstance(rv, BESkip):
                                if rv.execute(source=fighter) == "break":
                                    break
                            # Using an item:
                            elif isinstance(rv, Item):
                                rv = ConsumeItem(rv)
                                targets = rv.get_targets(fighter)
                                targets = renpy.call_screen("target_practice", rv, fighter, targets)
                                if rv.execute(source=fighter, t=targets):
                                    break
                            # Normal Skills:
                            else:
                                targets = rv.get_targets(fighter)
                                targets = renpy.call_screen("target_practice", rv, fighter, targets)
                                if targets:
                                    skill = rv
                                    break

                        # We don't need to see status icons during skill executions!
                        renpy.hide_screen("be_status_overlay")
                        renpy.hide("its_my_turn")

                        # Execute the skill:
                        if skill is not None:
                            skill.execute(source=fighter, t=targets)
                            fighter.last_skill = skill

                        renpy.show_screen("be_status_overlay")

                # End turn events, Death (Usually) is added here for example.
                self.end_turn_events = [event for event in self.end_turn_events if not event.execute()]

                self.logical_counter += 1

                if not self.logical:
                    for c in self.get_fighters("all"):
                        c.update_delayed()

                self.combat_log.extend(self.delayed_log)
                self.delayed_log = list()

                # We check the conditions for terminating the BE scenario, this should prolly be end turn event as well, but I've added this before I've added events :)
                if self.check_break_conditions():
                    break

            self.end_battle()

        def start_battle(self):
            self.prepare_teams()

            if not self.logical:
                self.predict_battle_skills()

                renpy.maximum_framerate(60)

                if self.music:
                    renpy.music.stop()
                    renpy.music.stop(channel="world")
                    renpy.music.play(self.music)

                # Show the BG:
                renpy.scene()

                # Lets render the teammembers:
                for team in self.teams:
                    for member in team:
                        member.portrait = member.char.show('portrait', resize=(112, 112), cache=True)
                        member.angry_portrait = member.char.show("portrait", "angry", resize=(65, 65), type='reduce', cache=True, add_mood=False)
                        self.show_char(member, at_list=[Transform(pos=self.set_icp(team, member))])

                renpy.show("bg", what=self.bg)
                renpy.show_screen("battle_overlay", self)
                renpy.show_screen("be_status_overlay")
                if self.start_sfx: # Special Effects:
                    renpy.with_statement(self.start_sfx)

                if self.quotes:
                    self.start_turn_events.append(RunQuotes(self.teams[0]))

                # After we've set the whole thing up, we've launch the main loop:
                gfx_overlay.notify(type="fight")
                renpy.pause(.6*persistent.battle_speed)
                # renpy.pause(.35)

            self.main_loop()

        def prepare_teams(self):
            # Plainly sets allegiance of chars to their teams.
            # Allegiance may change during the fight (confusion skill for example once we have one).
            # I've also included part of team/char positioning logic here.
            pos = "l"
            for team in self.teams:
                team.position = pos
                for idx in range(len(team)):
                    team._members[idx] = BE_Combatant(team, idx, pos)

                pos = "r"

        def end_battle(self):
            """Ends the battle, trying to normalize any variables that may have been used during the battle.
            """
            if not self.logical:
                if self.combat_status:
                    if self.combat_status == "escape":
                        renpy.show("escape_gates", what="portal_webm",  at_list=[Transform(align=(.5, .5))], zorder=100)
                        renpy.sound.play("content/sfx/sound/be/escape_portal.ogg")
                        tkwargs = {"color": "gray",
                                   "outlines": [(1, "black", 0, 0)]}
                        gfx_overlay.notify("Escaped...", tkwargs=tkwargs)
                    elif self.combat_status == "surrender":
                        tkwargs = {"color": "gray",
                                   "outlines": [(1, "black", 0, 0)]}
                        gfx_overlay.notify("Surrendered...", tkwargs=tkwargs)
                    else:
                        pass # just leaving
                elif self.win is True:
                    gfx_overlay.notify("You Win!")
                elif self.win is False:
                    tkwargs = {"color": "blue",
                               "outlines": [(1, "cyan", 0, 0)]}
                    gfx_overlay.notify("You Lose!", tkwargs=tkwargs)

                renpy.stop_predict(*self.predict)

                renpy.pause(1.0*persistent.battle_speed) # Small pause before terminating the engine.

                renpy.scene(layer='screens')
                renpy.scene()
                bg = self.end_bg
                if bg:
                    if isinstance(bg, basestring):
                        if check_image_extension(bg):
                            bg = Image(bg)
                        else:
                            bg = ImageReference("bg " + bg)
                    renpy.show("bg", what=bg)

                if self.end_sfx:
                    renpy.with_statement(self.end_sfx)

                if self.music:
                    renpy.music.stop()

            for team in self.teams:
                del team.position
                for idx in range(len(team)):
                    f = team._members[idx]
                    c = f.char
                    if f in self.corpses:
                        self.corpses.remove(f)
                        self.corpses.add(c)
                    team._members[idx] = c

                    if c.controller is not None:
                        c.controller.source = None
                    for s in chain(f.magic_skills, f.attack_skills):
                        s.source = None

                    f.restore_char()

        def next_turn(self):
            """
            Returns the next battle events to the game.
            (Re)Calculates the queue of events.
            Currently we're calculating one turn where everyone gets to go once.
            Last index is the next in line.
            """
            if not self.queue:
                l = self.get_fighters()
                l.sort(key=attrgetter("agility"))
                self.queue = l
            return self.queue.pop()

        def set_icp(self, team, member):
            """Set Initial Character Position

            Basically this is what sets the characters up at the start of the battle-round.
            Returns initial position of the character based on row/team!
            Positions should always be retrieved using this method or errors may occur.
            """
            # We want different behavior for 3 member teams putting the leader in the middle:
            member.besk = dict()
            # Supplied to the show method.
            member.betag = str(random.random())
            # First, lets get correct sprites:
            char = member.char
            if "Grim Reaper" in char.traits:
                sprite = Image("content/gfx/images/reaper.png")
            else:
                sprite = char.show("battle_sprite", resize=char.get_sprite_size("battle_sprite"))

            # We'll assign "indexes" from 0 to 3 from left to right [0, 1, 3, 4] to help calculating attack ranges.
            team_index = team.position
            char_index = member.beinx
            # Sprite Flips:
            is_mob = isinstance(char, Mob)
            if team_index == "r":
                if not is_mob:
                    if isinstance(sprite, im.Scale):
                        sprite = im.Flip(sprite, horizontal=True)
                    else:
                        sprite = Transform(sprite, xzoom=-1)
            else:
                if is_mob:
                    if isinstance(sprite, im.Scale):
                        sprite = im.Flip(sprite, horizontal=True)
                    else:
                        sprite = Transform(sprite, xzoom=-1)

            renpy.start_predict(sprite)
            self.predict.append(sprite)

            member.set_besprite(sprite)

            # We're going to land the character at the default position from now on,
            # with centered bottom of the image landing directly on the position!
            # This makes more sense for all purposes:
            x, y = self.BDP[member.row][char_index]
            w, h = member.besprite_size
            xpos = round_int(x-w*.5)
            ypos = round_int(y-h)
            member.dpos = member.cpos = (xpos, ypos)

            member.besk["what"] = member.besprite
            # Zorder defaults to characters (index + 1) * 100
            member.besk["zorder"] = (char_index + 1) * 100

            # ---------------------------------------------------->>>
            return member.dpos

        def show_char(self, member, *args, **kwargs):
            for key in member.besk:
                if key not in kwargs: # We do not want to overwrite!
                    kwargs[key] = member.besk[key]
            renpy.show(member.betag, *args, **kwargs)

        def move(self, member, pos, t, pause=True):
            """
            Move character to new position...
            """
            renpy.hide(member.betag)
            renpy.show(member.betag, what=member.besprite, at_list=[move_from_to_pos_with_ease(start_pos=member.cpos, end_pos=pos, t=t)], zorder=member.besk["zorder"])
            member.cpos = pos
            if pause:
                renpy.pause(t)

        def get_cp(self, member, type="pos", xo=0, yo=0, override=False,
                   use_absolute=False):
            """I am not sure how this is supposed to work yet in the grand scheme of things.

            Old Comment: For now it will report initial position + types:
            **Updated to using Current Position + Types.
            pos: Character position (pos)
            sopos: This is tc of default character position. Used to place status overlay icons.
            center: center of the characters image
            tc: top center of the characters image
            bc: bottom center of the characters image
            fc: front center (Special per row instruction (for offset) applies)

            xo = offset for x
            yo = offset for y

            absolute: convert to absolute for subpixel positioning.
            """
            # in case we do not care about position of a target/caster and just provide "overwrite" we should use instead:
            if override:
                xpos, ypos = override
            else:
                if type == "sopos":
                    xpos = member.dpos[0] + member.besprite_size[0] / 2
                    ypos = member.dpos[1]
                elif type == "pos":
                    xpos = member.cpos[0]
                    ypos = member.cpos[1]
                elif type == "center":
                    xpos = member.cpos[0] + member.besprite_size[0] / 2
                    ypos = member.cpos[1] + member.besprite_size[1] / 2
                elif type == "tc":
                    xpos = member.cpos[0] + member.besprite_size[0] / 2
                    ypos = member.cpos[1]
                elif type == "bc":
                    xpos = member.cpos[0] + member.besprite_size[0] / 2
                    ypos = member.cpos[1] + member.besprite_size[1]
                elif type == "fc":
                    if member.row in [0, 1]:
                        xpos = member.cpos[0] + member.besprite_size[0]
                        ypos = member.cpos[1] + member.besprite_size[1] / 2
                    else:
                        xpos = member.cpos[0]
                        ypos = member.cpos[1] + member.besprite_size[1] / 2

            # Add offsets:
            ypos += yo

            # While yoffset is the same, x offset depends on the team position:
            if member.row in [0, 1]:
                xpos += xo
            else:
                xpos -= xo # Is this a reasonable approach instead of providing correct (negative/positive) offsets? Something to consider during the code review...

            if use_absolute:
                return absolute(xpos), absolute(ypos)
            else:
                return xpos, ypos

        def get_fighters(self, state="alive", row=None):
            """
            Returns a list of all fighters from the team.
            states:
            - alive: All active member on the battlefield.
            - all: Everyone dead or alive.
            - dead: Everyone dead in the battlefield.
            row: If provided, should be number in range of 0 - 3. Only fighters in the row will be returned.
            """
            if state == "all":
                l = list(i for i in itertools.chain.from_iterable(self.teams))
            elif state == "alive":
                l =  list(i for i in itertools.chain.from_iterable(self.teams) if i not in self.corpses)
            elif state == "dead":
                l = list(self.corpses)

            if row:
                l = list(i for i in l if i.row == row)

            return l

        def check_break_conditions(self):
            # Checks if any specific condition is reached.
            # Should prolly be turned into a function when this gets complicated, for now it's just fighting until one of the party are "corpses".
            # For now this assumes that team indexed 0 is player team.
            if self.terminate:
                return True
            if self.combat_status is not None: #in ("escape", "surrender", "leave"):
                self.win = False
                self.winner = self.teams[1]
                return True
            if self.logical and self.logical_counter >= self.max_turns:
                self.win = False
                self.winner = self.teams[1]
                self.log("Battle went on for far too long! %s is considered the winner!" % self.winner.name)
                return True
            team0 = len(self.teams[0])
            team1 = len(self.teams[1])
            for c in self.corpses:
                if c.row < 2:
                    team0 -= 1
                else:
                    team1 -= 1
            if team0 == 0:
                self.winner = self.teams[1]
                self.win = False
                self.log("{color=green}%s{/color} is victorious!" % self.winner.name)
                return True
            if team1 == 0:
                self.winner = self.teams[0]
                self.win = True
                self.log("{color=green}%s{/color} is victorious!" % self.winner.name)
                return True

        def get_all_events(self):
            return itertools.chain(self.start_turn_events, self.mid_turn_events, self.end_turn_events)

        def predict_battle_skills(self):
            # Auto-Prediction:
            skills = set()
            for team in self.teams:
                for fighter in team:
                    for skill in chain(fighter.attack_skills, fighter.magic_skills):
                        skills.add(skill)


            force_predict = set()
            for skill in skills:
                gfx = skill.main_effect.get("gfx", None)
                force_predict.add(gfx)
                gfx = skill.main_effect.get("predict", [])
                for i in gfx:
                    force_predict.add(i)
                gfx = skill.target_sprite_damage_effect.get("gfx", None)
                force_predict.add(gfx)
                gfx = skill.attacker_effects.get("gfx", None)
                force_predict.add(gfx)
                gfx = getattr(skill, "projectile_effects", {}).get("gfx", None)
                force_predict.add(gfx)
                gfx = getattr(skill, "firing_effects", {}).get("gfx", None)
                force_predict.add(gfx)
                #gfx = skill.attacker_action.get("gfx", None)
                #gfx = skill.dodge_effect.get("gfx", None)
                #gfx = skill.target_damage_effect.get("gfx", None)
                #gfx = skill.target_death_effect.get("gfx", None)
                #gfx = skill.bg_main_effect.get("gfx", None)
                # PoisonEvent."poison_2", "content/gfx/be/poison1.webp"
                # DefenceBuffSpell.defence_gfx, buff_icon
            force_predict.discard(None)
            force_predict.discard("")
            force_predict = list(force_predict)

            renpy.start_predict(*force_predict)
            self.predict.extend(force_predict)

    class BE_Event(_object):
        """
        Anything that happens in the BE.
        Can be executed in RT or added to queues where it will be called.
        This is just to show off the structure...
        """
        def __init__(self, **kwargs):
            pass

        def execute(self):
            """
            Sets the pause and logic to allow event to be executed.
            """
            if self.check_conditions():
                self.apply_effects()
                return self.kill()

        def __str__(self):
            return str(self.name)

        def check_conditions(self):
            """Should return True/False to allow event execution.
            """
            pass

        def kill(self):
            """
            Decides if event should be killed or not (should return True for yes and False for keeping it alive)
            """
            pass

        def apply_effects(self, targets=None):
            pass

    class BE_Action(BE_Event):
        """Basic action class that assumes that there will be targeting of some kind and followup logical and graphical effects.
        """
        def __init__(self):
            # Naming/Sorting:
            self.name = self.mn = None
            self.kind = "assault"
            self.menu_pos = 0 # Skill level might be a better name.
            self.tier = None

            # Logic:
            self.range = 1
            self.source = None
            self.type = "se"
            self.critpower = 0
            self.piercing = False
            self.true_pierce = False # Does full damage to back rows.
            self.attributes = []
            self.delivery = None
            self.effect = 0
            self.multiplier = 1
            self.desc = ""
            self.target_state = "alive"

            self.event_class = None # If a class, instance of this even will be created and placed in the queue. This invokes special checks in the effects method.):

            # GFX/SFX:
            self.attacker_action = { "gfx" : "step_forward", "sfx" : None }
            self.attacker_effects = { "gfx" : None, "sfx" : None }
            self.main_effect = { "gfx" : None, "sfx" : None, "start_at" : 0, "aim": {}, "duration": None }
            self.dodge_effect = { "gfx": "dodge" }
            self.target_sprite_damage_effect = { "gfx" : "shake", "sfx" : None, "duration": None, "initial_pause": None }
            self.target_damage_effect = { "gfx" : "battle_bounce", "sfx" : None, "initial_pause": None }
            self.target_death_effect = { "gfx" : "dissolve", "sfx" : None, "duration": .5, "initial_pause": None }
            self.bg_main_effect = { "gfx" : None, "initial_pause" : None, "duration": None }

            # Cost of the attack:
            self.mp_cost = 0
            self.health_cost = 0
            self.vitality_cost = 0

        def init(self):
            # set default values
            if not self.mn:
                self.mn = self.name

            if self.delivery not in BE_Core.DELIVERY:
                raise Exception("Skill %s does not have a valid delivery type[melee, ranged, magic or status]!" % self.name)

            self.damage = [d for d in self.attributes if d in BE_Core.DAMAGE]

            if self.type=="all_allies":
                self.piercing = True

            # Dicts:
            self.tags_to_hide = list() # BE effects tags of all kinds, will be hidden when the show gfx method runs it's course and cleared for the next use.
            self.timestamps = {} # Container for the timed gfx effects

            if self.main_effect["duration"] is None:
                self.main_effect["duration"] = (.1 if self.delivery in ["melee", "ranged"] else .5)

            if self.target_sprite_damage_effect["duration"] is None:
                self.target_sprite_damage_effect["duration"] = self.main_effect["duration"]

            if self.target_sprite_damage_effect["initial_pause"] is None:
                self.target_sprite_damage_effect["initial_pause"] = .1 if self.delivery in ["melee", "ranged"] else .2

            if self.target_damage_effect["initial_pause"] is None:
                self.target_damage_effect["initial_pause"] = (self.main_effect["duration"] * .75) if self.delivery in ["melee", "ranged"] else .21

            if self.target_death_effect["initial_pause"] is None:
                self.target_death_effect["initial_pause"] = (.2 if self.delivery in ["melee", "ranged"] else (self.target_sprite_damage_effect["initial_pause"] + .1))

            if self.bg_main_effect["initial_pause"] is None:
                self.bg_main_effect["initial_pause"] = self.main_effect["start_at"]

            if self.bg_main_effect["duration"] is None:
                self.bg_main_effect["duration"] = self.main_effect["duration"]

        def execute(self, source, t=None):
            self.source = source
            self.effects_resolver(t)
            died = self.apply_effects(t)

            if not battle.logical:
                self.time_gfx(t, died)

                for tag in self.tags_to_hide:
                    renpy.hide(tag)
                self.tags_to_hide = list()

            # Clear (maybe move to separate method if this ever gets complicated), should be moved to core???
            for f in battle.get_fighters(state="all"):
                f.beeffects = []

        # Targeting/Conditioning.
        def get_targets(self, source):
            """
            Gets targets that can be hit with this action.
            Rows go [0, 1, 2, 3] from left to right of the battle-field.
            """
            # First figure out all targets within the range:
            # We calculate this by assigning.
            all_targets = battle.get_fighters(self.target_state)
            left_front_row_empty = all(f.row != 1 for f in all_targets)
            right_front_row_empty = all(f.row != 2 for f in all_targets)
            range = self.range
            if left_front_row_empty:
                # 'move' closer because of an empty row
                range += 1
            #elif source.row == 0 and self.range == 1:
            #    # allow to reach over a teammate
            #    range += 1
            if right_front_row_empty:
                # 'move' closer because of an empty row
                range += 1
            #elif source.row == 3 and self.range == 1:
            #    # allow to reach over a teammate
            #    range += 1

            rows_from, rows_to = source.row - range, source.row + range
            in_range = [f for f in all_targets if rows_from <= f.row <= rows_to]

            #if DEBUG_BE:
            #    if any(t for t in in_range if isinstance(t, basestring)):
            #        raise Exception(in_range)

            # Lets handle the piercing (Or not piercing since piercing attacks include everyone in range already):
            if not self.piercing:
                if source.row < 2:
                    # Source is on left team:
                    # We need to check if there is at least one member on the opposing front row and if true, remove everyone in the back.
                    if not right_front_row_empty:
                        # opfor has a defender:
                        # we need to remove everyone from the back row:
                        in_range = [f for f in in_range if f.row != 3]
                else:
                    if not left_front_row_empty:
                        in_range = [f for f in in_range if f.row != 0]

            # Now the type, we just care about friends and enemies:
            if self.type in ("all_enemies", "se"):
                in_range = [f for f in in_range if source.allegiance != f.allegiance]
            elif self.type in ("all_allies", "sa"):
                in_range = [f for f in in_range if source.allegiance == f.allegiance]

            # @Review: Prevent AI from casting the same Buffs endlessly:
            # Note that we do not have a concrete setup for buffs yet so this
            # is coded to be safe.
            if source.controller is not None:
                # a character controller by an AI
                buff_group = getattr(self, "buff_group", None)
                if buff_group is not None:
                    for target in in_range[:]:
                        for ev in store.battle.get_all_events():
                            if target == ev.target and getattr(ev, "group", "no_group") == buff_group:
                                in_range.remove(target)
                                break

            return in_range # List: So we can support indexing...

        def check_conditions(self, source):
            """Checks if the source can manage the attack."""
            # Check if attacker has enough resources for the attack:
            cost = self.mp_cost
            if not isinstance(cost, int):
                cost = int(source.maxmp*cost)
            if source.mp < cost:
                return False

            cost = self.vitality_cost
            if not isinstance(cost, int):
                cost = int(source.maxvit*cost)
            if source.vitality < cost:
                return False

            cost = self.health_cost
            if not isinstance(cost, int):
                cost = int(source.maxhp*cost)
            if source.health <= cost:
                return False

            # Check if there is a target in sight
            if not self.get_targets(source):
                return False

            # Indoor check:
            return self.menu_pos < battle.max_skill_lvl # TODO strange limit. Sure not equal?

        # Logical Effects:
        def effects_resolver(self, targets):
            """Logical effect of the action.

            - For normal attacks, it calculates the damage.
            Expects a list or tuple with targets.
            This should return it's results through PytCharacters property called damage so the show_gfx method can be adjusted accordingly.
            But it is this method that writes to the log to be displayed later... (But you can change even this :D)
            """
            # prepare the variables:
            a = self.source

            # DAMAGE Mods:
            num_dmg = len(self.damage)
            if num_dmg != 0:
                # Get the attack power:
                attack = self.get_attack(a)
                attack /= num_dmg

            if self.delivery in ["melee", "ranged"]:
                melee_ranged_delivery = True
                inevitable = "inevitable" in self.attributes # inevitable attribute makes skill/spell undodgeable/unresistable
            else:
                melee_ranged_delivery = False

            for t in targets:
                # effect list must be cleared here first thing... preferably in the future, at the end of each skill execution...
                effects = t.beeffects

                # We get the multiplier and any effects that those may bring.
                multiplier = 1.0
                # Critical Strike and Evasion checks:
                if melee_ranged_delivery is True:
                    # Critical Hit Chance:
                    # No more than 20% chance based on luck
                    ch = a.modifiers[0] + max(0, min((a.luck - t.luck), 20)) # base_ch + luck modifiers 

                    if dice(ch):
                        multiplier += 1.1 + self.critpower
                        effects.append("critical_hit")
                    elif not inevitable:
                        ev = max(0, min(t.agility*.05-a.agility*.05, 15) + min(t.luck-a.luck, 15)) # Max 15 for agility and luck each...

                        # Items/Traits bonuses:
                        # item_evasion_bonus + trait_evasion_bonus
                        ev += t.modifiers[9]

                        if t.health <= t.maxhp/4:
                            if ev < 0:
                                ev = 0 # Even when weighed down adrenaline takes over and allows for temporary superhuman movements
                            ev += randint(1,5) # very low health provides additional random evasion, 1-5%

                        if dice(ev):
                            effects.append("missed_hit")
                            self.log_to_battle(effects, 0, a, t, message=None)
                            continue

                total_damage = 0
                if num_dmg != 0:
                    defense = self.get_defense(t)
                    defense /= num_dmg

                    # Rows Damage:
                    if self.row_penalty(t):
                        multiplier *= .5
                        effects.append("backrow_penalty")

                    for type in self.damage:
                        result = BE_Core.damage_modifier(a, t, attack, type)

                        # Resisted:
                        if result == 0:
                            effects.append((type, "resisted"))
                            continue

                        # We also check for absorbtion:
                        absorb_ratio = BE_Core.check_absorbtion(t, type)
                        if absorb_ratio:
                            result *= -absorb_ratio
                            # We also set defence to 0, no point in defending against absorption:
                            temp_def = 0
                        else:
                            temp_def = defense

                        # Get the damage:
                        result = BE_Core.damage_calculator(result, temp_def, multiplier, a)

                        effects.append((type, result))
                        total_damage += result

                if self.event_class:
                    # First check resistance, then check if event is already in play:
                    type = self.damage[0] # FIXME what about multi type events? Partial resist?
                    if type in t.resist or BE_Core.check_absorbtion(t, type):
                        pass
                    else:
                        group = self.buff_group
                        for event in store.battle.mid_turn_events:
                            if t == event.target and event.group == group:
                                battle.log("%s is already affected by %s!" % (t.nickname, type))
                                break
                        else:
                            temp = self.event_class(a, t, self.effect, randint(*self.event_duration), group)
                            battle.mid_turn_events.append(temp)

                # Finally, log to battle:
                self.log_to_battle(effects, total_damage, a, t, message=None)

        def row_penalty(self, t):
            # It's always the normal damage except for rows 0 and 3 (unless everyone in the front row are dead :) ).
            # Adding true_piece there as well:
            if t.row == 3:
                if battle.get_fighters(row=2) and not self.true_pierce:
                    return True
            elif t.row == 0:
                if battle.get_fighters(row=1) and not self.true_pierce:
                    return True

        def get_attack(self, a):
            """
            Very simple method to get to attack power.
            """
            delivery = self.delivery
            if delivery == "melee":
                attack = a.attack*.7 + a.agility*.3
            elif delivery == "ranged":
                attack = a.agility*.7 + a.attack*.3
            elif delivery == "magic":
                attack = a.magic*.7 + a.intelligence*.3
            else: #if delivery == "status":
                attack = a.intelligence*.7 + a.agility*.3

            attack += self.effect
            attack *= self.multiplier

            # Items/Traits bonuses:
            # item_delivery_bonus + trait_delivery_bonus
            attack += a.modifiers[2].get(delivery, 0)
            # item_delivery_multiplier + trait_delivery_multiplier
            m = 1.0 + a.modifiers[3].get(delivery, 0)
            attack *= m

            # Simple randomization factor?:
            # attack *= uniform(.90, 1.10) # every time attack is random from 90 to 110% Alex: Why do we do this? Dark: we make damage calculations unpredictable (within reasonable limits); many games use much more harsh ways to add randomness to BE.

            # Decreasing based of current health:
            # healthlevel=(1.0*a.health)/(1.0*a.maxhp)*.5 # low health decreases attack power, down to 50% at close to 0 health.
            # attack *= (.5+healthlevel)

            return attack

        def get_defense(self, target):
            """
            A method to get defence value vs current attack.
            """
            delivery = self.delivery

            if delivery == "melee":
                defense = target.defence*.7 + target.constitution*.3
            elif delivery == "ranged":
                defense = target.defence*.7 + target.agility*.3
            elif delivery == "magic":
                defense = target.defence*.4 + target.magic*.2 + target.intelligence*.4
            else: # if delivery == "status":
                defense = target.defence*.4 + target.intelligence*.3 + target.constitution*.3

            # Items/Traits bonuses:
            # item_defence_bonus + trait_defence_bonus
            defense += target.modifiers[7].get(delivery, 0)
            # 1 + item_defence_multiplier + trait_defence_multiplier
            m = 1.0 + target.modifiers[8].get(delivery, 0)
            defense *= m

            # Testing status mods through be skillz:
            m = 0
            d = 0
            for event in battle.get_all_events():
                if event.target == target and event.__class__ == DefenceBuff:
                    ed = event.defence_bonus.get(delivery, 0)
                    em = event.defence_multiplier.get(delivery, 0)
                    if ed or em:
                        e = event.effect
                        d += ed * e
                        m += em * e
                        event.activated_this_turn = True

            if d or m:
                target.beeffects.append("magic_shield")
                defense += d
                defense *= (1.0 + m)

            return defense

        # To String methods:
        def log_to_battle(self, effects, total_damage, a, t, message=None):
            # String for the log:
            if message is None:
                if total_damage >= 0:
                    message = "{color=teal}%s{/color} attacks %s with %s" % (a.nickname, t.nickname, self.name)
                else:
                    message = "{color=teal}%s{/color} attacks %s with %s, but %s absorbs it" % (a.nickname, t.nickname, self.name, t.nickname)
            s = [message]

            # add effects as string
            #  First add the str effects and collect the type effects:
            type_effects = list()
            for effect in effects:
                if isinstance(effect, tuple):
                    type_effects.append(effect)
                elif effect == "backrow_penalty":
                    s.append("{color=red}1/2 DMG (Back-Row){/color}")
                elif effect == "critical_hit":
                    s.append("{color=lawngreen}Critical Hit{/color}")
                elif effect == "magic_shield":
                    s.append("{color=lawngreen}☗+{/color}")
                elif effect == "missed_hit":
                    s.append("{color=lawngreen}Attack Missed{/color}")
                else:
                    debug_be("Unrecognized effect '%s' when converting to string." % effect)

            #  Next type effects:
            if len(type_effects) > 1:
                # add entry for a combined damage in case of multi-type attacks:
                type_effects.append(("DMG", total_damage))
            s += [BE_Core.color_string_by_DAMAGE_type(effect, True) for effect in type_effects]

            # Log the effects to battle
            battle.log(" ".join(s), delayed=True)

            # Log the effects to target:
            effects.insert(0, total_damage)
            t.beeffects = effects

        def apply_effects(self, targets):
            """This is a  final method where all effects of the attacks are being dished out on the objects.
            """

            # Not 100% for that this will be required...
            # Here it is simple since we are only focusing on damaging health:
            # prepare the variables:
            died = list()
            for t in targets:
                t.health -= t.beeffects[0]
                if t.health <= 0:
                    t.health = 1
                    battle.end_turn_events.append(RPG_Death(t))
                    died.append(t)

            self.settle_cost()
            return died

        def settle_cost(self):
            # Here we need to take of cost:
            source = self.source
            source.take_pp()

            cost = self.mp_cost
            if cost:
                if not(isinstance(cost, int)):
                    cost = int(source.maxmp*cost)
                source.mp -= cost
                if source.mp < source.minmp:
                    source.mp = source.minmp

            cost = self.health_cost
            if cost:
                if not(isinstance(cost, int)):
                    cost = int(source.maxhp*cost)
                source.health -= cost
                #if source.health < source.minhp:
                #    source.health = source.minhp

            cost = self.vitality_cost
            if cost:
                if not(isinstance(cost, int)):
                    cost = int(source.maxvit*cost)
                source.vitality -= cost
                if source.vitality < source.minvit:
                    source.vitality = source.minvit

            if not battle.logical:
                source.update_delayed()

        # Game/Gui Assists:
        def get_element(self):
            # This may have to be expanded if we permit multi-elemental attacks in the future.
            # Returns first (if any) an element bound to spell or attack:
            result = []
            for a in self.attributes:
                if a in tgs.el_names:
                    result.append(traits[a.capitalize()])

            return result

        # GFX/SFX:
        def queue_call(self, at, func, *args):
            if at in self.timestamps:
                at += uniform(.001, .002)

            self.timestamps[at] = renpy.curry(func)(*args)
            return at

        def time_gfx(self, targets, died):
            """Executes GFX part of an attack. Disregarded during logical combat.

            Usually, this has the following order:
                - Intro (attacker sprite manipulation) + Effect (attacker_effects)
                - Attack itself. (main_effects) = which is usually impact effect!
                - Visual damage effect to the target(s) (sprites shaking for example). (target_sprite_gamage_effects)
                - Some form of visual representation of damage amount (like battle bounce). (target_damage_effects)
                - Events such as death (GFX Part, event itself can be handled later). (death_effect)

            Through complex system currently in design we handle showing gfx/hiding gfx and managing sfx (also here).
            """
            # Simple effects for the magic attack:
            attacker = self.source
            battle = store.battle

            # We need to build a dict of pause timespamp: func to call.
            self.timestamps = {}

            if self.attacker_action["gfx"] or self.attacker_action["sfx"]:
                delay = self.time_attackers_first_action(battle, attacker)

            # Next is the "casting effect":
            # Here we need to start checking for overlapping time_stamps so we don't overwrite:
            # calculate start time in any case, because we'll need it later
            start = self.main_effect["start_at"]
            if self.attacker_effects["gfx"] or self.attacker_effects["sfx"]:
                # We start as effects gfx is finished.
                start += self.time_attackers_first_effect(battle, attacker, targets)

            #  We start after attackers first action is finished.
            elif "delay" in locals():
                start += delay
            #else: # We plainly start at timestamp...

            # Next is the main GFX/SFX effect!:
            if self.main_effect["gfx"] or self.main_effect["sfx"]:
                self.time_main_gfx(battle, attacker, targets, start)

            # Dodging:
            if self.dodge_effect["gfx"]: # <== Presently always True...
                self.time_dodge_effect(targets, attacker, start)

            # Now the damage effects to targets (like shaking):
            if self.target_sprite_damage_effect["gfx"] or self.target_sprite_damage_effect["sfx"]:
                self.time_target_sprite_damage_effect(targets, died, start)

            # Damage effect (battle bounce type):
            if self.target_damage_effect["gfx"] or self.target_damage_effect["sfx"]:
                self.time_target_damage_effect(targets, died, start)

            # And Death Effect:
            if died and (self.target_death_effect["gfx"] or self.target_death_effect["sfx"]):
                self.time_target_death_effect(died, start)

            # And possible BG effects:
            if self.bg_main_effect["gfx"]:
                self.time_bg_main_effect(start)

            # Doesn't feel conceptually correct to put this here,
            # but it's likely the safest solution atm.
            gfx_overlay.be_taunt(attacker, self, 1.5*persistent.battle_speed)

            time_stamps = sorted(self.timestamps.keys())
            st = time.time()
            for stamp in time_stamps:
                func = self.timestamps[stamp]
                # devlog.info("Func: {}".format(func.__dict__["callable"]))

                real_passed_time = time.time()-st
                # devlog.info("New iteration at: {}".format(round(real_passed_time, 2)))

                if real_passed_time < stamp:
                    pause = stamp-real_passed_time
                    if pause > .05:
                        # devlog.info("Paused for: {}".format(round(pause, 2)))
                        # ui.pausebehavior(pause, False)
                        # ui.interact(mouse='pause', type='pause', roll_forward=None)
                        renpy.pause(pause)

                # devlog.info("Function called at: {} (perfect time to call: {})".format(round(time.time()-st, 2), round(stamp, 2)))
                func()
                # devlog.info("Leaving iteration at: {}".format(round(time.time()-st, 2)))

            self.timestamps = {}

        def time_attackers_first_action(self, battle, attacker):
            # Lets start with the very first part (attacker_action):
            self.timestamps[0] = renpy.curry(self.show_attackers_first_action)(battle, attacker)
            delay = self.get_show_attackers_first_action_initial_pause() + self.attacker_effects.get("duration", 0)*persistent.battle_speed
            hide_first_action = delay + self.attacker_action.get("keep_alive_delay", 0)*persistent.battle_speed

            self.queue_call(hide_first_action, self.hide_attackers_first_action, battle, attacker)
            return delay

        def show_attackers_first_action(self, battle, attacker):
            if self.attacker_action["gfx"] == "step_forward":
                battle.move(attacker, battle.get_cp(attacker, xo=50), .5*persistent.battle_speed, pause=False)

            sfx = self.attacker_action.get("sfx", None)
            if sfx:
                renpy.sound.play(sfx)

        def get_show_attackers_first_action_initial_pause(self):
            if self.attacker_action["gfx"] == "step_forward":
                return .5*persistent.battle_speed
            else:
                return 0

        def hide_attackers_first_action(self, battle, attacker):
            if self.attacker_action["gfx"] == "step_forward":
                battle.move(attacker, attacker.dpos, .5*persistent.battle_speed, pause=False)

        def time_attackers_first_effect(self, battle, attacker, targets):
            start = self.get_show_attackers_first_action_initial_pause()
            start = self.queue_call(start, self.show_attackers_first_effect, battle, attacker, targets)

            if self.attacker_effects["gfx"]:
                effects_delay = start + self.attacker_effects.get("duration", 0)*persistent.battle_speed

                effects_delay = self.queue_call(effects_delay, self.hide_attackers_first_effect, battle, attacker)
                return effects_delay

            return 0

        def get_attackers_first_effect_gfx(self):
            gfx = self.attacker_effects["gfx"]
            zoom = self.attacker_effects.get("zoom", None)

            if zoom is not None:
                gfx = Transform(gfx, zoom=zoom)

            return gfx

        def show_attackers_first_effect(self, battle, attacker, targets):
            gfx = self.attacker_effects["gfx"]
            if gfx:
                what = self.get_attackers_first_effect_gfx()

                cast = self.attacker_effects.get("cast", {})
                point = cast.get("point", "center")
                align = cast.get("align", (.5, .5))
                xo = cast.get("xo", 0)
                yo = cast.get("yo", 0)
                zorder = 1 if cast.get("ontop", True) else -1

                # Flip the attack image if required:
                if self.attacker_effects.get("hflip", False) and battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0]:
                    what = Transform(what, xzoom=-1)
                    align = (1.0 - align[0], align[1])

                renpy.show("casting", what=what, at_list=[Transform(pos=battle.get_cp(attacker, type=point, xo=xo, yo=yo), align=align)], zorder=attacker.besk["zorder"]+zorder)

            sfx = self.attacker_effects["sfx"]
            if sfx:
                if sfx == "default":
                    sfx="content/sfx/sound/be/casting_1.mp3"
                renpy.sound.play(sfx)

        def hide_attackers_first_effect(self, battle, attacker):
            # For now we just hide the tagged image here:
            renpy.hide("casting")

        def time_main_gfx(self, battle, attacker, targets, start):
            start = self.queue_call(start, self.show_main_gfx, battle, attacker, targets)

            pause = self.main_effect["duration"]
            # Kind of a shitty way of trying to handle attacks that come.
            # With their own pauses in time_main_gfx method.
            pause += getattr(self, "firing_effects", {}).get("duration", 0)
            pause += getattr(self, "projectile_effects", {}).get("duration", 0)
            pause *= persistent.battle_speed
            pause += start
            self.queue_call(pause, self.hide_main_gfx, targets)

        def get_main_gfx(self):
            gfx = self.main_effect["gfx"]

            # use AlphaBlend
            blend = self.main_effect.get("blend", None)
            if blend is not None:
                alpha = blend.get("alpha", None)
                if alpha is not None:
                    gfx = Transform(gfx, alpha=alpha)
                effect = getattr(store, blend.get("effect", None), None)
                if effect is not None:
                    size = blend["size"]
                    gfx = AlphaBlend(gfx, gfx, effect(*size), alpha=True)

            # Zoom if requested
            xzoom = self.main_effect.get("xzoom", 1.0)
            yzoom = self.main_effect.get("yzoom", 1.0)
            zoom = self.main_effect.get("zoom", None)
            if zoom is not None:
                xzoom *= zoom
                yzoom *= zoom
            if xzoom != 1.0 or yzoom != 1.0:
                gfx = Transform(gfx, xzoom=xzoom, yzoom=yzoom)

            # Scale if requested
            scale = self.main_effect.get("scale", None)
            if scale is not None:
                gfx = PyTGFX.scale_content(gfx, *scale)

            return gfx

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
                what = self.get_main_gfx()

                # Flip the attack image if required:
                if self.main_effect.get("hflip", False) and battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0]:
                    what = Transform(what, xzoom=-1)

                aim = self.main_effect["aim"]
                point = aim.get("point", "center")
                anchor = aim.get("anchor", (.5, .5))
                xo = aim.get("xo", 0)
                yo = aim.get("yo", 0)

                for index, target in enumerate(targets):
                    renpy.show("attack" + str(index), what=what,
                               at_list=[Transform(pos=battle.get_cp(target, type=point, xo=xo, yo=yo), anchor=anchor)],
                               zorder=target.besk["zorder"]+1)

        def hide_main_gfx(self, targets):
            for i in xrange(len(targets)):
                renpy.hide("attack" + str(i))

        def time_target_sprite_damage_effect(self, targets, died, start):
            # We take previous start as basepoint for execution:
            damage_effect_start = start + self.target_sprite_damage_effect["initial_pause"]*persistent.battle_speed

            damage_effect_start = self.queue_call(damage_effect_start, self.show_target_sprite_damage_effect, targets)

            delay = damage_effect_start + self.target_sprite_damage_effect["duration"]*persistent.battle_speed

            self.queue_call(delay, self.hide_target_sprite_damage_effect, targets, died)

        def show_target_sprite_damage_effect(self, targets):
            """Target damage graphical effects.
            """
            gfx = self.target_sprite_damage_effect["gfx"]

            if gfx:
                for target in [t for t in targets if not "missed_hit" in t.beeffects]:
                    at_list = []

                    what = target.besprite
                    if gfx == "shake":
                        at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx == "true_dark": # not used atm! will need decent high level spells for this one!
                        what = AlphaBlend(Transform(what, alpha=.8), what, Transform("fire_logo", size=target.besprite_size), alpha=True)
                    elif gfx == "true_water":
                        what = AlphaBlend(Transform(what, alpha=.6), what, Transform("water_overlay_test", size=target.besprite_size), alpha=True)
                    elif gfx == "vertical_shake":
                        at_list = [vertical_damage_shake(.1, (-5, 5))]
                    elif gfx == "fly_away":
                        at_list = [fly_away]
                    elif gfx == "on_air":
                        at_list = [blowing_wind()]
                    elif gfx.startswith("iced"):
                        child = Transform("content/gfx/be/frozen.webp", size=target.besprite_size)
                        what = AlphaMask(child, what)
                        if gfx.endswith("shake"):
                            at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx.startswith("on_darkness"):
                        size = int(target.besprite_size[0]*1.5), 60
                        what = Fixed(what, Transform("be_dark_mask", size=size, anchor=(.5, .3), align=(.5, 1.0), alpha=.8), xysize=(target.besprite_size))
                        if gfx.endswith("shake"):
                            at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx.startswith("on_light"):
                        size = int(target.besprite_size[0]*2.5), int(target.besprite_size[1]*2.5)
                        what = Fixed(what, Transform("be_light_mask", size=size, align=(.5, 1.0), alpha=.6), xysize=(target.besprite_size))
                        if gfx.endswith("shake"):
                            at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx == "on_death":
                        what = AlphaBlend(Transform(what, alpha=.5), what, dark_death_color(*target.besprite_size), alpha=True)
                    elif gfx.startswith("on_dark"):
                        child = Transform("content/gfx/be/darken.webp", size=target.besprite_size)
                        what = AlphaMask(child, what)
                        if gfx.endswith("shake"):
                            at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx.startswith("frozen"): # shows a big block of ice around the target sprite
                        size = (int(target.besprite_size[0]*1.5), int(target.besprite_size[1]*1.5))
                        what = Fixed(what, Transform("content/gfx/be/frozen_2.webp", size=size, offset=(-30, -50)))
                        t = self.target_sprite_damage_effect.get("duration", 1)
                        at_list=[fade_from_to_with_easeout(start_val=1.0, end_val=.2, t=t)]
                        if gfx.endswith("shake"):
                            at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx.startswith("burning"): # looks like more dangerous flame, should be used for high level spells
                        child = Transform("fire_mask", size=target.besprite_size)
                        what = AlphaMask(child, what)
                        if gfx.endswith("shake"):
                            at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx.startswith("on_fire"):
                        what = AlphaBlend(Transform(what, alpha=.8), what, fire_effect_color(*target.besprite_size), alpha=True)
                        if gfx.endswith("shake"):
                            at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx.startswith("on_water"):
                        sprite_size = target.besprite_size
                        child = Transform("be_water_mask", size=sprite_size)
                        what = Fixed(what, AlphaMask(child, what), xysize=sprite_size)
                        if gfx.endswith("shake"):
                            at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx.startswith("on_ele"):
                        sprite_size = target.besprite_size
                        child = Transform("be_electro_mask", size=sprite_size)
                        what = Fixed(what, AlphaMask(child, what), xysize=sprite_size)
                        if gfx.endswith("shake"):
                            at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx.startswith("poisoned"): # ideally we could use animated texture of green liquid, but it's hard to find for free...
                            what = AlphaBlend(Transform(what, alpha=.8), what, poison_effect_color(*target.besprite_size), alpha=True)
                            if gfx.endswith("shake"):
                                at_list = [damage_shake(.05, (-10, 10))]
                    elif gfx == "being_healed":
                            what = AlphaBlend(Transform(what, alpha=.9, additive=.4),
                                              what, healing_effect_color(*target.besprite_size),
                                              alpha=True)
                    else:
                        be_debug("Unknown target_sprite_damage_effect-gfx '%s' defined in %s" % (gfx, self.name))
                        continue

                    renpy.show(target.betag, what=what, at_list=at_list, zorder=target.besk["zorder"])

            if self.target_sprite_damage_effect.get("master_shake", False):
                renpy.layer_at_list([damage_shake(.05, (-5, 5))], layer='master')

        def hide_target_sprite_damage_effect(self, targets, died):
            # Hides damage effects applied to targets:
            if self.target_sprite_damage_effect.get("master_shake", False):
                renpy.layer_at_list([], layer='master')

            type = self.target_sprite_damage_effect.get("gfx", "shake")
            if type == "frozen":
                for target in targets:
                    if target not in died:
                        renpy.hide(target.betag)
                        renpy.show(target.betag, what=target.besprite, at_list=[Transform(pos=target.cpos), fade_from_to(.3, 1, .3)], zorder=target.besk["zorder"])
            elif type == "shake" and self.target_death_effect["gfx"] == "shatter":
                for target in targets:
                    renpy.hide(target.betag)
                    renpy.show(target.betag, what=target.besprite, at_list=[Transform(pos=target.cpos)], zorder=target.besk["zorder"])
            else:
                for target in targets:
                    if target not in died:
                        renpy.hide(target.betag)
                        renpy.show(target.betag, what=target.besprite, at_list=[Transform(pos=target.cpos)], zorder=target.besk["zorder"])

        def time_target_damage_effect(self, targets, died, start):
            # Used to be .2 but it is a better idea to show
            # it after the attack gfx effects are finished
            # if no value was specified directly.
            damage_effect_start = start + self.target_damage_effect["initial_pause"]*persistent.battle_speed

            damage_effect_start = self.queue_call(damage_effect_start, self.show_target_damage_effect, targets, died)

            delay = damage_effect_start + self.get_target_damage_effect_duration()

            self.queue_call(delay, self.hide_target_damage_effect, targets, died)

        def show_target_damage_effect(self, targets, died):
            """Easy way to show damage like the bouncing damage effect.
            """
            type = self.target_damage_effect.get("gfx", "battle_bounce")
            force = self.target_damage_effect.get("force", False)
            if type == "battle_bounce":
                for index, target in enumerate(targets):
                    if target not in died or force:
                        effects = target.beeffects
                        value = effects[0]
                        #color = "red"

                        if "missed_hit" in effects:
                            gfx = self.dodge_effect.get("gfx", "dodge")
                            if gfx == "dodge":
                                s = "{color=lawngreen}Missed{/color}"
                            else:
                                s = "▼ %s" % value
                        else:
                            dmg = [effect for effect in effects if isinstance(effect, tuple)]
                            if len(dmg) == 1:
                                dmg = dmg[0]
                            else:
                                dmg = ("DMG", value)
                            s = BE_Core.color_string_by_DAMAGE_type(dmg, False)

                        if "critical_hit" in effects:
                            s += "\n{color=lawngreen}Critical hit!{/color}"
                        txt = Text(s, style="TisaOTM", min_width=200,
                                   text_align=.5, size=18)
                        renpy.show("bb" + str(index), what=txt,
                                   at_list=[battle_bounce(battle.get_cp(target, type="tc", yo=-30))],
                                   zorder=target.besk["zorder"]+2)

        def get_target_damage_effect_duration(self):
            type = self.target_damage_effect.get("gfx", "battle_bounce")
            if type == "battle_bounce":
                duration = 1.5
            else:
                duration = 0

            # Kind of a shitty way of trying to handle attacks that come
            # With their own pauses in time_main_gfx method.
            if hasattr(self, "firing_effects"):
                duration += self.firing_effects.get("duration", 0)
                duration += self.main_effect.get("duration")
            duration += getattr(self, "projectile_effects", {}).get("duration", 0)

            return duration*persistent.battle_speed

        def hide_target_damage_effect(self, targets, died):
            for index, target in enumerate(targets):
                if target not in died:
                    renpy.hide("bb" + str(index))

        def time_target_death_effect(self, died, start):
            death_effect_start = start + self.target_death_effect["initial_pause"]*persistent.battle_speed

            death_effect_start = self.queue_call(death_effect_start, self.show_target_death_effect, died)

            delay = death_effect_start + self.target_death_effect["duration"]*persistent.battle_speed

            self.queue_call(delay, self.hide_target_death_effect, died)

        def show_target_death_effect(self, died):
            gfx = self.target_death_effect["gfx"]
            sfx = self.target_death_effect["sfx"]
            duration = self.target_death_effect["duration"]*persistent.battle_speed

            if sfx:
                renpy.sound.play(sfx)

            if gfx == "dissolve":
                for t in died:
                    renpy.show(t.betag, what=t.besprite, at_list=[fade_from_to(start_val=1.0, end_val=.0, t=duration)], zorder=t.besk["zorder"])
            elif gfx == "shatter":
                for t in died:
                    renpy.show(t.betag, what=HitlerKaputt(t.besprite, 20), zorder=t.besk["zorder"])

        def hide_target_death_effect(self, died):
            for target in died:
                renpy.hide(target.betag)

        def time_bg_main_effect(self, start):
            effect_start = start + self.bg_main_effect["initial_pause"]*persistent.battle_speed

            effect_start = self.queue_call(effect_start, self.show_bg_main_effect)

            delay = effect_start + self.bg_main_effect["duration"]*persistent.battle_speed

            self.queue_call(delay, self.hide_bg_main_effect)

        def show_bg_main_effect(self):
            gfx = self.bg_main_effect["gfx"]
            sfx = self.bg_main_effect.get("sfx", None)

            if sfx:
                renpy.sound.play(sfx)

            if gfx == "mirage":
                battle.bg.change(gfx)
            elif gfx == "black":
                renpy.with_statement(None)
                renpy.show("bg", what=Solid("#000000"))
                renpy.with_statement(Dissolve(.5*persistent.battle_speed))
                # renpy.pause(.5)

        def hide_bg_main_effect(self):
            gfx = self.bg_main_effect["gfx"]
            if gfx == "mirage":
                battle.bg.change("default")
            elif gfx == "black":
                renpy.with_statement(None)
                renpy.show("bg", what=battle.bg)
                renpy.with_statement(Dissolve(.5*persistent.battle_speed))

        def time_dodge_effect(self, targets, attacker, start):
            # effect_start = start - .3
            # if effect_start < 0:
                # effect_start = 0

            # Ok, so since we'll be using it for all kinds of attacks now, we need better timing controls:
            effect_start = self.dodge_effect.get("initial_pause", -.3)*persistent.battle_speed
            effect_start += start
            if effect_start < 0:
                effect_start = 0

            effect_start = self.queue_call(effect_start, self.show_dodge_effect, attacker, targets)

            # Hiding timing as well in our new version:
            delay = effect_start + self.main_effect["duration"]*persistent.battle_speed

            self.queue_call(delay, self.hide_dodge_effect, targets)

        def show_dodge_effect(self, attacker, targets):
            # This also handles shielding... which might not be appropriate and future safe...

            gfx = self.dodge_effect.get("gfx", "dodge")
            # gfx = self.dodge_effect["gfx"]
            # sfx = self.dodge_effect.get("sfx", None)

            # if sfx:
                # renpy.sound.play(sfx)

            for index, target in enumerate(targets):
                if "missed_hit" in target.beeffects:
                    if gfx == "dodge":
                        xoffset = -100 if battle.get_cp(attacker)[0] > battle.get_cp(target)[0] else 100

                        # Figure out the pause:
                        pause = self.main_effect["duration"]-.5
                        if pause < 0:
                            pause = 0
                        else:
                            pause *= persistent.battle_speed

                        renpy.show(target.betag, what=target.besprite, at_list=[be_dodge(xoffset, pause)], zorder=target.besk["zorder"])

                # We need to find out if it's reasonable to show shields at all based on damage effects!
                # This should ensure that we do not show the shield for major damage effects, it will not look proper.
                elif "magic_shield" in target.beeffects and self.target_sprite_damage_effect["gfx"] != "fly_away":
                    # Get GFX:
                    what = None
                    for event in battle.get_all_events():
                        if event.target == target and event.__class__ == DefenceBuff and event.activated_this_turn:
                            what = event
                            event.activated_this_turn = False # reset the flag

                    if what is None:
                        be_debug("No Effect GFX detected for magic_shield dodge_effect!")
                        continue

                    what = what.gfx_effect
                    # we just show the shield:
                    if what == "default":
                        what, size = "resist", (300, 300)
                    elif what == "gray_shield":
                        what = AlphaBlend("resist", "resist", gray_shield(300, 300), alpha=True)
                        size = (300, 300)
                    elif what == "air_shield":
                        what = AlphaBlend("ranged_shield_webm", "ranged_shield_webm", green_shield(350, 300), alpha=True)
                        size = (350, 300)
                    elif what == "solid_shield":
                        what, size = "shield_2", (400, 400)
                    else:
                        be_debug("The defence_gfx '%s' is not recognized. Should be one of ('default', 'gray_shield', 'air_shield', 'solid_shield')" % what)
                        continue
                    renpy.show("dodge" + str(index), what=what,
                               at_list=[Transform(size=size, pos=battle.get_cp(target, type="center"), anchor=(.5, .5))],
                               zorder=target.besk["zorder"]+1)

        def hide_dodge_effect(self, targets):
            # gfx = self.dodge_effect.get("gfx", "dodge")
            for index, target in enumerate(targets):
                if "magic_shield" in target.beeffects:
                    renpy.hide("dodge" + str(index))


    class BE_AI(_object):
        # Not sure this even needs to be a class...
        def init(self, source):
            self.source = source

        def execute(self):
            source = self.source
            skills = self.get_available_skills()
            while skills:
                skill = choice(skills)
                # So we have a skill... now lets pick a target(s):
                targets = skill.get_targets(source) # Get all targets in range.
                if targets:
                    targets = targets if "all" in skill.type else [choice(targets)] # We get a correct amount of targets here.
                    skill.execute(source, t=targets)
                    return
                skills.remove(skill)

            # skip
            BESkip().execute(source=source)

        def get_available_skills(self):
            source = self.source
            return [s for s in chain(source.attack_skills, source.magic_skills) if s.check_conditions(source)]

    class Complex_BE_AI(BE_AI):
        """This one does a lot more "thinking".

        Possible options (Copied from GitHub Issue):
            Elemental affinities.
            Personalities (of AI).
            Intelligence (How smart it actually should be).
            Healing/Reviving.
            Favorite attacks/spells?
            Test multiple scenarios to see if we get infinite loops anywhere.
        """
        def init(self, source):
            super(Complex_BE_AI, self).init(source=source)

        def execute(self):
            source = self.source

            # Split skills in containers:
            map = {"revival": 1, "healing": 2, "buff": 3}
            skills = [[], [], [], []]
            for s in self.get_available_skills():
                skills[map.get(s.kind, 0)].append(s)

            # Reviving first:
            revivals = skills[1]
            if revivals_skills and dice(50):
                for skill in revivals:
                    targets = skill.get_targets(source)
                    if targets:
                        targets = targets if "all" in skill.type else [choice(targets)]
                        skill.execute(source=source, t=targets)
                        return

            healings = skills[2]
            if healings and dice(70):
                for skill in healings:
                    targets = skill.get_targets(source)
                    for t in targets:
                        if t.health < t.maxhp/2:
                            targets = targets if "all" in skill.type else [t]
                            skill.execute(source=source, t=targets)
                            return

            buffs = skills[3]
            if buffs and dice(10):
                for skill in buffs:
                    targets = skill.get_targets(source)
                    if targets:
                        targets = targets if "all" in skill.type else [choice(targets)]
                        skill.execute(source=source, t=targets)
                        return

            attacks = skills[0]
            if attacks:
                # Sort skills by menu_pos:
                attacks.sort(key=attrgetter("menu_pos"))
                while attacks:
                    # Most powerful skill has 70% chance to trigger.
                    # Last skill in the list will execute!
                    skill = attacks.pop()
                    if not attacks or dice(70):
                        targets = skill.get_targets(source)
                        targets = targets if "all" in skill.type else [choice(targets)]
                        skill.execute(source=source, t=targets)
                        return

            # Skip in case we did not pick any specific skill:
            BESkip().execute(source=source)

    #def get_char_with_lowest_attr(chars, attr="hp"):
    #    chars.sort(key=attrgetter(attr))
    #    return chars[0]
