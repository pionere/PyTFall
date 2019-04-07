init -1 python: # Core classes:
    """
    This is our version of turn based BattleEngine.
    I think that we can use zorders on master layer instead of messing with multiple layers.
    """
    class BE_Combatant(_object):
        def __init__(self, char):
            self.char = char

            # most commonly used variables during the battle
            self.name = char.name
            self.nickname = char.nickname
            self.status = char.status
            self.attack_skills = char.attack_skills
            self.magic_skills = char.magic_skills

            self.AP = char.AP
            self.PP = char.PP

            self.health = char.get_stat("health")
            self.delayedhp = self.health
            self.maxhp = char.get_max("health")
            self.mp = char.get_stat("mp")
            self.delayedmp = self.mp
            self.maxmp = char.get_max("mp")
            self.vitality = char.get_stat("vitality")
            self.delayedvit = self.vitality
            self.maxvit = char.get_max("vitality")

            self.grimreaper = "Grim Reaper" in char.traits
            self.is_mob = isinstance(char, Mob)

            self.controller = char.controller
            self.attack = char.get_stat("attack")
            self.agility = char.get_stat("agility")
            self.luck = char.get_stat("luck")
            self.defence = char.get_stat("defence")
            self.constitution = char.get_stat("constitution")
            self.magic = char.get_stat("magic")
            self.intelligence = char.get_stat("intelligence")

            self.resist = char.resist

            # cached item bonuses
            items = char.eq_items()

            critical_hit_chance = 0

            self.item_damage_multiplier = 0
            self.item_delivery_bonus = {}
            self.item_delivery_multiplier = {}
            self.item_evasion_bonus = 0
            self.item_defence_bonus = {}
            self.item_defence_multiplier = {}
            for i in items:
                self.item_damage_multiplier += getattr(i, "damage_multiplier", 0)
                critical_hit_chance += getattr(i, "ch_multiplier", 0)

                if hasattr(i, "delivery_bonus"):
                    for delivery, bonus in i.delivery_bonus.iteritems():
                        bonus += self.item_delivery_bonus.get(delivery, 0)
                        self.item_delivery_bonus[delivery] = bonus

                if hasattr(i, "delivery_multiplier"):
                    for delivery, mpl in i.delivery_multiplier.iteritems():
                        mpl += self.item_delivery_multiplier.get(delivery, 0)
                        self.item_delivery_multiplier[delivery] = mpl

                self.item_evasion_bonus += getattr(i, "evasion_bonus", 0)

                if hasattr(i, "defence_bonus"):
                    for delivery, bonus in i.defence_bonus.iteritems():
                        bonus += self.item_defence_bonus.get(delivery, 0)
                        self.item_defence_bonus[delivery] = bonus

                if hasattr(i, "defence_multiplier"):
                    for delivery, mpl in i.defence_multiplier.iteritems():
                        mpl += self.item_defence_multiplier.get(delivery, 0)
                        self.item_defence_multiplier[delivery] = mpl

            # cached trait bonuses
            self.damage_multiplier = 0
            self.delivery_bonus = {}
            self.delivery_multiplier = {}
            self.el_dmg = {}
            self.el_def = {}
            self.evasion_bonus = 0
            self.absorbs = {}
            self.defence_bonus = {}
            self.defence_multiplier = {}
            for trait in char.traits:
                self.damage_multiplier += getattr(trait, "damage_multiplier", 0)
                critical_hit_chance += getattr(trait, "ch_multiplier", 0)

                if hasattr(trait, "delivery_bonus"):
                    for delivery, bonus in trait.delivery_bonus.iteritems():
                        # Reference: (minv, maxv, lvl)
                        minv, maxv, lvl = bonus
                        if lvl <= 0:
                            lvl = 1
                        if lvl > char.level:
                            maxv = max(minv, float(char.level)*maxv/lvl)
                        maxv += self.delivery_bonus.get(delivery, 0)
                        self.delivery_bonus[delivery] = maxv

                if hasattr(trait, "delivery_multiplier"):
                    for delivery, mpl in trait.delivery_multiplier.iteritems():
                        mpl += self.delivery_multiplier.get(delivery, 0)
                        self.delivery_multiplier[delivery] = mpl

                for type, val in trait.el_damage.iteritems():
                    val += self.el_dmg.get(type, 0)
                    self.el_dmg[type] = val

                for type, val in trait.el_defence.iteritems():
                    val += self.el_def.get(type, 0)
                    self.el_def[type] = val

                if hasattr(trait, "evasion_bonus"):
                    # Reference: (minv, maxv, lvl)
                    minv, maxv, lvl = trait.evasion_bonus
                    if lvl <= 0:
                        lvl = 1
                    if lvl <= char.level:
                        self.evasion_bonus += maxv
                    else:
                        self.evasion_bonus += max(minv, float(char.level)*maxv/lvl)

                # Get all absorption capable traits:
                if trait.el_absorbs:
                    for type, val in trait.el_absorbs.iteritems():
                        absorbs = self.absorbs.get(type, [])
                        absorbs.append(val)
                        self.absorbs[type] = absorbs

                if hasattr(trait, "defence_bonus"):
                    for delivery, bonus in trait.defence_bonus.iteritems():
                        # Reference: (minv, maxv, lvl)
                        minv, maxv, lvl = bonus
                        if lvl <= 0:
                            lvl = 1
                        if lvl > char.level:
                            maxv = max(minv, float(char.level)*maxv/lvl)
                        maxv += self.defence_bonus.get(delivery, 0)
                        self.defence_bonus[delivery] = maxv

                if hasattr(trait, "defence_multiplier"):
                    base_mpl = 1
                    if trait in char.traits.basetraits and len(char.traits.basetraits)==1:
                        base_mpl = 2
                    
                    for delivery, mpl in trait.defence_multiplier.iteritems():
                        mpl *= base_mpl
                        mpl += self.defence_multiplier.get(delivery, 0)
                        self.defence_multiplier[delivery] = mpl

            # prepare base critical hit chance: (Items bonuses + Traits bonuses)
            self.base_ch = 100.0*critical_hit_chance

            # Convert absorptions to ratios:
            for type, val in self.absorbs.iteritems():
                val = sum(val) / len(val)
                self.absorbs[type] = val

            self.front_row = char.front_row

            # BE assets:
            self.besprite = None # Used to keep track of sprite displayable in the BE.
            self.besprite_size = None # Sprite size in pixels.
            self.beinx = 0 # Passes index from logical execution to SFX setup.
            self.beteampos = None # This manages team position bound to target (left or right on the screen).
            self.row = 1 # row on the battlefield, used to calculate range of weapons.
            self.betag = None # Tag to keep track of the sprite.
            self.dpos = None # Default position based on row + team.
            self.sopos = () # Status underlay position, which should be fixed.
            self.cpos = None # Current position of a sprite.
            self.besk = None # BE Show **Kwargs!
            self.allegiance = None # BE will default this to the team name.
            self.beeffects = []
            self.dmg_font = "red"
            self.status_overlay = [] # Status icons over the sprites.

        def set_besprite(self, besprite):
            self.besprite = besprite
            if self.is_mob:
                webm_spites = mobs[self.char.id].get("be_webm_sprites", None)
                if webm_spites:
                    self.besprite_size =  webm_spites["idle"][1]
                    return
            self.besprite_size = get_size(besprite)

        # Delayed stats to use it in BE so we can delay updating stats on the GUI.
        def update_delayed(self):
            self.delayedhp = self.health
            self.delayedmp = self.mp
            self.delayedvit = self.vitality

        def get_be_items(self):
            # be_items only for non-logical battles (for the moment? Mobs do not have inventory anyway)
            if not hasattr(self.char, "inventory"):
                return None
            be_items = OrderedDict()
            for item, amount in self.char.inventory.items.iteritems():
                if item.be:
                    be_items[item] = amount
            return be_items

        def take_pp(self):
            if self.PP < 10:
                if self.AP <= 0:
                    return False
                self.PP += 100 # PP_PER_AP = 100
                self.AP -= 1
            self.PP -= 10
            return True

        def has_pp(self):
            return self.AP > 0 or self.PP >= 10

        def restore_char(self):
            self.char.AP = self.AP
            self.char.PP = self.PP

            self.char.set_stat("health", self.health)
            self.char.set_stat("mp", self.mp)
            self.char.set_stat("vitality", self.vitality)

    class BE_Core(_object):
        BDP = dict()               # BE DEFAULT POSITIONS
        TYPE_TO_COLOR_MAP = dict() # DAMAGE TYPE TO COLOR MAP
        """Main BE attrs, data and the loop!
        """
        def __init__(self, bg=None, music=None, row_pos=None, start_sfx=None,
                     end_bg=None, end_sfx=None, logical=False, quotes=False,
                     max_skill_lvl=float("inf"), max_turns=1000, give_up=None,
                     use_items=False):
            """Creates an instance of BE scenario.

            logical: Just the calculations, without pause/gfx/sfx.
            """
            self.teams = list() # Each team represents a faction on the battlefield. 0 index for left team and 1 index for right team.
            self.queue = list() # List of events in BE..
            self.give_up = give_up # allows to avoid battle in one way or another
            self.use_items = use_items # allows use of items during combat.
            self.combat_status = None # general status of the battle, used to run away from BF atm.

            self.max_turn = max_turns

            if not logical:
                # Background we'll use.
                if bg:
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

                self.quotes = quotes # Decide if we run quotes at the start of the battle.

            self.corpses = set() # Anyone died in the BE.

            self.row_pos = row_pos if row_pos else self.BDP

            # Whatever controls the current queue of the loop is the controller.
            self.controller = None # The current character (player or AI combatant)
            self.winner = None
            self.win = None # We set this to True if left team wins and to False if right.
            self.combat_log = list()
            # We may want to delay logging something to the end of turn.
            self.delayed_log = list()

            # Events:
            self.start_turn_events = list() # Events we execute on start of the turn.
            self.mid_turn_events = list() # Events we execute on the end of the turn.
            self.end_turn_events = list() # Events to execute after controller was set.
            self.terminate = False

            self.logical = logical
            self.logical_counter = 0

            self.max_skill_lvl = max_skill_lvl

        @staticmethod
        def init():
            # BE DEFAULT POSITIONS *positions are tuples in lists that go from top to bottom.
            BDP = {"l0": [(230, 540), (190, 590), (150, 640)], # Left (Usually player) teams backrow default positions.
                   "l1": [(360, 540), (320, 590), (280, 640)]} # Left (Usually player) teams frontrow default positions.
            BDP["r0"] = list((config.screen_width-t[0], t[1]) for t in BDP["l0"]) # BackRow, Right (Usually enemy).
            BDP["r1"] = list((config.screen_width-t[0], t[1]) for t in BDP["l1"]) # FrontRow, Right (Usually enemy).

            # We need to get perfect middle positioning:
            # Get the perfect middle x:
            perfect_middle_xl = BDP["l0"][1][0] + round_int((BDP["l1"][1][0] - BDP["l0"][1][0])*.5)
            perfect_middle_yl = perfect_middle_yr = BDP["l1"][1][1] - 100
            perfect_middle_xr = BDP["r0"][1][0] + round_int((BDP["r1"][1][0] - BDP["r0"][1][0])*.5)
            BDP["perfect_middle_right"] = (perfect_middle_xl, perfect_middle_yl)
            BDP["perfect_middle_left"] = (perfect_middle_xr, perfect_middle_yr)
            BE_Core.BDP.clear()
            BE_Core.BDP.update(BDP)

            # DAMAGE TYPE TO COLOR MAP
            type_to_color_map = {e.id.lower(): e.font_color for e in tgs.elemental}
            type_to_color_map["poison"] = "green"
            type_to_color_map["healing"] = "lightgreen"

            BE_Core.TYPE_TO_COLOR_MAP.clear()
            BE_Core.TYPE_TO_COLOR_MAP.update(type_to_color_map)

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
                for event in self.start_turn_events[:]:
                    if event():
                        self.start_turn_events.remove(event)

                fighter = self.controller = self.next_turn()

                for event in self.mid_turn_events[:]:
                    if event():
                        self.mid_turn_events.remove(event)

                # If the controller was killed off during the mid_turn_events:
                if fighter not in self.corpses:
                    if fighter.controller is not None:
                        # This character is not controlled by the player so we call the (AI) controller:
                        fighter.controller()
                    else: # Controller is the player:
                        # making known whose turn it is:
                        w, h = fighter.besprite_size
                        renpy.show("its_my_turn", at_list=[Transform(additive=.6, alpha=.7, size=(int(w*1.5), h/3),
                                                           pos=battle.get_cp(fighter, type="bc", yo=20),
                                                           anchor=(.5, 1.0))],
                                                           zorder=fighter.besk["zorder"]+1)

                        while 1:
                            skill = None
                            targets = None

                            rv = renpy.call_screen("pick_skill", fighter)

                            # Unique check for Skip/Escape Events:
                            if isinstance(rv, BESkip):
                                if rv() == "break":
                                    break
                            else: # Normal Skills:
                                if isinstance(rv, Item):
                                    skill = ConsumeItem()
                                    skill.item = rv
                                else:
                                    skill = rv

                                skill.source = fighter
                                targets = skill.get_targets()
                                targets = renpy.call_screen("target_practice", skill, fighter, targets)
                                if targets:
                                    break

                        # We don't need to see status icons during skill executions!
                        if not self.logical:
                            renpy.hide_screen("be_status_overlay")
                            renpy.hide("its_my_turn")

                        # This actually executes the skill!
                        if skill is not None:
                            skill(t=targets)

                        if not self.logical:
                            renpy.show_screen("be_status_overlay")

                if not self.logical:
                    renpy.hide_screen("pick_skill")
                    renpy.hide_screen("target_practice")

                # End turn events, Death (Usually) is added here for example.
                for event in self.end_turn_events[:]:
                    if event():
                        self.end_turn_events.remove(event)

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
                        member.portrait = member.char.show('portrait', resize=(118, 118), cache=True)
                        member.angry_portrait = member.char.show("portrait", "angry", resize=(65, 65), type='reduce', cache=True)
                        self.show_char(member, at_list=[Transform(pos=self.get_icp(team, member))])

                renpy.show("bg", what=self.bg)
                renpy.show_screen("battle_overlay", self)
                renpy.show_screen("be_status_overlay")
                if self.start_sfx: # Special Effects:
                    renpy.with_statement(self.start_sfx)

                if self.quotes:
                    self.start_turn_events.append(RunQuotes(self.teams[0]))

                # After we've set the whole thing up, we've launch the main loop:
                gfx_overlay.notify(type="fight")
                renpy.pause(.6)
                # renpy.pause(.35)

            self.main_loop()

        def prepare_teams(self):
            # Plainly sets allegiance of chars to their teams.
            # Allegiance may change during the fight (confusion skill for example once we have one).
            # I've also included part of team/char positioning logic here.
            pos = "l"
            for team in self.teams:
                team.position = pos
                size = len(team)
                for idx in range(len(team)):
                    char = BE_Combatant(team._members[idx])
                    team._members[idx] = char
                    if char.controller is not None:
                        char.controller.source = char

                    # Position:
                    char.beteampos = pos
                    if size == 3 and idx < 2:
                        char.beinx = 1 - idx
                    else:
                        char.beinx = idx
                    if pos == "l":
                        char.row = char.front_row
                    else: # Case "r"
                        char.row = 3 - char.front_row

                    # Allegiance:
                    char.allegiance = team

                pos = "r"

        def end_battle(self):
            """Ends the battle, trying to normalize any variables that may have been used during the battle.
            """
            if not self.logical:
                if self.win is True:
                    gfx_overlay.notify("You Win!")
                elif self.win is False:
                    tkwargs = {"color": "blue",
                               "outlines": [(1, "cyan", 0, 0)]}
                    gfx_overlay.notify("You Lose!", tkwargs=tkwargs)

                renpy.pause(1.0) # Small pause before terminating the engine.

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
                for idx in range(len(team)):
                    f = team._members[idx]
                    c = f.char
                    if f in self.corpses:
                        self.corpses.remove(f)
                        self.corpses.add(c)
                    team._members[idx] = c

                    if c.controller is not None:
                        c.controller.source = c
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

        def get_icp(self, team, member):
            """Get Initial Character Position

            Basically this is what sets the characters up at the start of the battle-round.
            Returns initial position of the character based on row/team!
            Positions should always be retrieved using this method or errors may occur.
            """
            # We want different behavior for 3 member teams putting the leader in the middle:
            member.besk = dict()
            # Supplied to the show method.
            member.betag = str(random.random())
            # First, lets get correct sprites:
            if member.grimreaper:
                sprite = Image("content/gfx/images/reaper.png")
            else:
                char = member.char
                sprite = char.show("battle_sprite", resize=char.get_sprite_size("battle_sprite"))

            # We'll assign "indexes" from 0 to 3 from left to right [0, 1, 3, 4] to help calculating attack ranges.
            team_index = team.position
            char_index = member.beinx
            # Sprite Flips:
            if team_index == "r":
                if not member.is_mob:
                    if isinstance(sprite, ProportionalScale):
                        sprite = im.Flip(sprite, horizontal=True)
                    else:
                        sprite = Transform(sprite, xzoom=-1)
            else:
                if member.is_mob:
                    if isinstance(sprite, ProportionalScale):
                        sprite = im.Flip(sprite, horizontal=True)
                    else:
                        sprite = Transform(sprite, xzoom=-1)

            member.set_besprite(sprite)

            # We're going to land the character at the default position from now on,
            # with centered bottom of the image landing directly on the position!
            # This makes more sense for all purposes:
            x, y = self.row_pos[team_index + str(member.front_row)][char_index]
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
            if not override:
                if not member.cpos or not member.besprite_size:
                    raise Exception([member.cpos, member.besprite_size])

                if type == "sopos":
                    xpos = member.dpos[0] + member.besprite_size[0] / 2
                    ypos = member.dpos[1] + yo
                elif type == "pos":
                    xpos = member.cpos[0]
                    ypos = member.cpos[1] + yo
                elif type == "center":
                    xpos = member.cpos[0] + member.besprite_size[0] / 2
                    ypos = member.cpos[1] + member.besprite_size[1] / 2 + yo
                elif type == "tc":
                    xpos = member.cpos[0] + member.besprite_size[0] / 2
                    ypos = member.cpos[1] + yo
                elif type == "bc":
                    xpos = member.cpos[0] + member.besprite_size[0] / 2
                    ypos = member.cpos[1] + member.besprite_size[1] + yo
                elif type == "fc":
                    if member.row in [0, 1]:
                        xpos = member.cpos[0] + member.besprite_size[0]
                        ypos = member.cpos[1] + member.besprite_size[1] / 2 + yo
                    else:
                        xpos = member.cpos[0]
                        ypos = member.cpos[1] + member.besprite_size[1] / 2 + yo

            # in case we do not care about position of a target/caster and just provide "overwrite" we should use instead:
            else:
                xpos, ypos = override
                ypos += yo # Same as for comment below (Maybe I just forgot how offsets work and why...)

            # While yoffset is the same, x offset depends on the team position: @REVIEW: AM I TOO WASTED OR DOES THIS NOT MAKE ANY SENSE???
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
            if self.combat_status in ("escape", "surrender"):
                self.win = False
                self.winner = self.teams[1]
                return True
            if self.logical and self.logical_counter >= self.max_turn:
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
                self.log("%s is victorious!" % self.winner.name)
                return True
            if team1 == 0:
                self.winner = self.teams[0]
                self.win = True
                self.log("%s is victorious!" % self.winner.name)
                return True

        def get_all_events(self):
            return itertools.chain(self.start_turn_events, self.mid_turn_events, self.end_turn_events)


    class BE_Event(_object):
        """
        Anything that happens in the BE.
        Can be executed in RT or added to queues where it will be called.
        This is just to show off the structure...
        """
        def __init__(self, **kwargs):
            pass

        def __call__(self, *args, **kwargs):
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

        # ported from Action class as we need this for Events as well:
        def damage_modifier(self, t, damage, type):
            """
            This calculates the multiplier to use with effect of the skill.
            t: target
            damage: Damage (number per type)
            type: Damage Type
            """
            if type in t.resist:
                return 0

            a = self.source
            m = 1.0

            # Get multiplier from traits:
            # We decided that any trait could influence this:
            # damage = 0
            # defence = 0

            # Damage first:
            m += a.el_dmg.get(type, 0)

            # Defence next:
            m -= t.el_def.get(type, 0)

            damage *= m

            return damage


    class BE_Action(BE_Event):
        """Basic action class that assumes that there will be targeting of some kind and followup logical and graphical effects.
        """
        DELIVERY = set(["magic", "ranged", "melee", "status"]) # Damage/Effects Delivery Methods!
        DAMAGE = {"physical": "{image=physical_be_viewport}", "fire": "{image=fire_element_be_viewport}", "water": "{image=water_element_be_viewport}",
                  "ice": "{image=ice_element_be_viewport}", "earth": "{image=earth_element_be_viewport}", "air": "{image=air_element_be_viewport}",
                  "electricity": "{image=ele_element_be_viewport}", "light": "{image=light_element_be_viewport}", "darkness": "{image=darkness_element_be_viewport}",
                  "healing": "{image=healing_be_viewport}", "poison": "{image=poison_be_viewport}"} # Damage (Effect) types...
        DAMAGE_20 = {"physical": "{image=physical_be_size20}", "fire": "{image=fire_element_be_size20}", "water": "{image=water_element_be_size20}",
                     "ice": "{image=ice_element_be_size20}", "earth": "{image=earth_element_be_size20}", "air": "{image=air_element_be_size20}",
                     "electricity": "{image=ele_element_be_size20}", "light": "{image=light_element_be_size20}", "darkness": "{image=darkness_element_be_size20}",
                     "healing": "{image=healing_be_size20}", "poison": "{image=poison_be_size20}"}


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

            if self.delivery not in self.DELIVERY:
                raise Exception("Skill %s does not have a valid delivery type[melee, ranged, magic or status]!" % self.name)

            self.damage = [d for d in self.attributes if d in self.DAMAGE]

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

        def __call__(self, ai=False, t=None):
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
        def get_targets(self, source=None):
            """
            Gets tagets that can be hit with this action.
            Rows go [0, 1, 2, 3] from left to right of the battle-field.
            """
            char = source if source else self.source

            # First figure out all targets within the range:
            # We calculate this by assigning.
            all_targets = battle.get_fighters(self.target_state)
            left_front_row_empty = all(f.row != 1 for f in all_targets)
            right_front_row_empty = all(f.row != 2 for f in all_targets)
            range = self.range
            if left_front_row_empty:
                # 'move' closer because of an empty row
                range += 1
            elif char.row == 0 and self.range == 1:
                # allow to reach over a teammate
                range += 1
            if right_front_row_empty:
                # 'move' closer because of an empty row
                range += 1
            elif char.row == 3 and self.range == 1:
                # allow to reach over a teammate
                range += 1

            rows_from, rows_to = char.row - range, char.row + range
            in_range = [f for f in all_targets if rows_from <= f.row <= rows_to]

            #if DEBUG_BE:
            #    if any(t for t in in_range if isinstance(t, basestring)):
            #        raise Exception(in_range)

            # Lets handle the piercing (Or not piercing since piercing attacks include everyone in range already):
            if not self.piercing:
                if char.row < 2:
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
                in_range = [f for f in in_range if char.allegiance != f.allegiance]
            elif self.type in ("all_allies", "sa"):
                in_range = [f for f in in_range if char.allegiance == f.allegiance]

            # @Review: Prevent AI from casting the same Buffs endlessly:
            # Note that we do not have a concrete setup for buffs yet so this
            # is coded to be safe.
            if char.controller is not None:
                # a character controller by an AI
                buff_group = getattr(self, "buff_group", None)
                if buff_group is not None:
                    for target in in_range[:]:
                        for ev in store.battle.get_all_events():
                            if target == ev.target and getattr(ev, "group", "no_group") == buff_group:
                                in_range.remove(target)
                                break

            return in_range # List: So we can support indexing...

        def check_conditions(self, source=None):
            """Checks if the source can manage the attack."""
            member = source if source else self.source

            # Indoor check:
            if self.menu_pos >= battle.max_skill_lvl:
                return False

            # Check if attacker has enough resources for the attack:
            cost = self.mp_cost
            if not isinstance(cost, int):
                cost = int(member.maxmp*cost)
            if member.mp < cost:
                return False

            cost = self.vitality_cost
            if not isinstance(cost, int):
                cost = int(member.maxvit*cost)
            if member.vitality < cost:
                return False

            cost = self.health_cost
            if not isinstance(cost, int):
                cost = int(member.maxhp*cost)
            if member.health <= cost:
                return False

            # Check if there is a target in sight
            return self.get_targets(member)

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
                attack = self.get_attack()
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
                    ch = a.base_ch + max(0, min((a.luck - t.luck), 20)) # No more than 20% chance based on luck

                    if dice(ch):
                        multiplier += 1.1 + self.critpower
                        effects.append("critical_hit")
                    elif not inevitable:
                        ev = max(0, min(t.agility*.05-a.agility*.05, 15) + min(t.luck-a.luck, 15)) # Max 15 for agility and luck each...

                        # Items bonuses:
                        ev += t.item_evasion_bonus

                        # Traits Bonuses:
                        ev += t.evasion_bonus

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
                        result = self.damage_modifier(t, attack, type)

                        # Resisted:
                        if result == 0:
                            effects.append((type, "resisted"))
                            continue

                        # We also check for absorbtion:
                        absorb_ratio = self.check_absorbtion(t, type)
                        if absorb_ratio:
                            result = absorb_ratio*result
                            # We also set defence to 0, no point in defending against absorption:
                            temp_def = 0
                            absorbed = True
                        else:
                            temp_def = defense
                            absorbed = False

                        # Get the damage:
                        result = self.damage_calculator(result, temp_def, multiplier, a, absorbed)

                        effects.append((type, result))
                        total_damage += result

                if self.event_class:
                    # First check resistance, then check if event is already in play:
                    type = self.buff_group
                    if type in t.resist or self.check_absorbtion(t, type):
                        pass
                    else:
                        for event in store.battle.mid_turn_events:
                            if t == event.target and event.type == type:
                                battle.log("%s is already affected by %s!" % (t.nickname, type))
                                break
                        else:
                            duration = getattr(self, "event_duration", 3)
                            temp = self.event_class(a, t, self.effect, duration=duration)
                            battle.mid_turn_events.append(temp)
                            # We also add the icon to targets status overlay:
                            t.status_overlay.append(temp.icon)

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

        def check_absorbtion(self, t, type):
            # Get ratio:
            return t.absorbs.get(type, None)

        def get_attack(self):
            """
            Very simple method to get to attack power.
            """
            a = self.source

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

            # Items bonuses:
            attack += a.item_delivery_bonus.get(delivery, 0)
            m = 1.0 + a.item_delivery_multiplier.get(delivery, 0)
            attack *= m

            # Trait Bonuses:
            attack += a.delivery_bonus.get(delivery, 0)
            m = 1.0 + a.delivery_multiplier.get(delivery, 0)
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

            # Items bonuses:
            defense += target.item_defence_bonus.get(delivery, 0)
            m = 1.0 + target.item_defence_multiplier.get(delivery, 0)
            defense *= m

            # Trait Bonuses:
            defense += target.defence_bonus.get(delivery, 0)
            m = 1.0 + target.defence_multiplier.get(delivery, 0)
            defense *= m

            # Testing status mods through be skillz:
            m = 0
            d = 0
            for event in battle.get_all_events():
                if event.target == target:
                    if hasattr(event, "defence_bonus"):
                        d += event.defence_bonus.get(delivery, 0)
                        event.activated_this_turn = True
                    if hasattr(event, "defence_multiplier"):
                        m += event.defence_multiplier.get(delivery, 0)
                        event.activated_this_turn = True

            if d or m:
                target.beeffects.append("magic_shield")
                defense += d
                defense *= (1.0 + m)

            return defense

        def damage_calculator(self, damage, defense, multiplier, attacker, absorbed=False):
            """Used to calc damage of the attack.
            Before multipliers and effects are applied.
            """
            if absorbed:
                damage = -damage

            damage *= multiplier * (75.0/(75 + defense)) * uniform(.9, 1.1)

            # Items Bonus:
            damage *= 1.0 + attacker.item_damage_multiplier

            # Traits Bonus:
            damage *= 1.0 + attacker.damage_multiplier

            return round_int(damage)

        # To String methods:
        def log_to_battle(self, effects, total_damage, a, t, message=None):
            # Logs effects to battle, target...
            effects.insert(0, total_damage)

            # Log the effects:
            t.beeffects = effects

            # String for the log:
            s = list()
            if not message:
                if total_damage >= 0:
                    s.append("{color=teal}%s{/color} attacks %s with %s" % (a.nickname, t.nickname, self.name))
                else:
                    s.append("{color=teal}%s{/color} attacks %s with %s, but %s absorbs it" % (a.nickname, t.nickname, self.name, t.nickname))
            else:
                s.append(message)

            s = s + self.effects_to_string(t)

            battle.log(" ".join(s), delayed=True)

        def color_string_by_DAMAGE_type(self, effect, return_for="log"):
            # Takes a string "s" and colors it based of damage "type".
            # If type is not an element, color will be red or some preset (in this method) default.
            type, value = effect

            if value < 0:
                value = -value
                color = battle.TYPE_TO_COLOR_MAP["healing"]
            else:
                color = battle.TYPE_TO_COLOR_MAP.get(type, "red")

            if return_for == "log":
                s = "%s: %s" % (self.DAMAGE.get(type, type), value)
                return "{color=%s}%s{/color}" % (color, s)
            elif return_for == "bb": # battle bounce
                return value, color
            else:
                return "Unknown Return For DAMAGE type!"

        def effects_to_string(self, t, default_color="red"):
            """Adds information about target to the list and returns it to be written to the log later.

            - We assume that all tuples in effects are damages by type!
            """
            # String for the log:
            effects = t.beeffects
            s = list()

            str_effects = list()
            type_effects = list()

            for effect in effects:
                if isinstance(effect, tuple):
                    type_effects.append(effect)
                else:
                    str_effects.append(effect)

            # First add the str effects:
            for effect in str_effects:
                if effect == "backrow_penalty":
                    # Damage halved due to the target being in the back row!
                    s.append("{color=red}1/2 DMG (Back-Row){/color}")
                elif effect == "critical_hit":
                    s.append("{color=lawngreen}Critical Hit{/color}")
                elif effect == "magic_shield":
                    s.append("{color=lawngreen}☗+{/color}")
                elif effect == "missed_hit":
                    gfx = self.dodge_effect.get("gfx", "dodge")
                    if gfx == "dodge":
                        s.append("{color=lawngreen}Attack Missed{/color}")

            # Next type effects:
            for effect in type_effects:
                temp = self.color_string_by_DAMAGE_type(effect)
                s.append(temp)

            # And finally, combined damage for multi-type attacks:
            if len(type_effects) > 1:
                value = effects[0]
                if value < 0:
                    value = -value
                    color = battle.TYPE_TO_COLOR_MAP["healing"]
                else:
                    color = "red"
                temp = "{color=%s}DGM: %d{/color}" % (color, value)
                s.append(temp)

            return s

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
            if not(isinstance(cost, int)):
                cost = int(self.source.maxmp*cost)
            source.mp -= cost

            cost = self.health_cost
            if not(isinstance(cost, int)):
                cost = int(self.source.maxhp*cost)
            source.health -= cost

            cost = self.vitality_cost
            if not(isinstance(cost, int)):
                cost = int(self.source.maxvit*cost)
            source.vitality -= cost

            if not battle.logical:
                source.update_delayed()

        # Game/Gui Assists:
        def get_element(self):
            # This may have to be expanded if we permit multi-elemental attacks in the future.
            # Returns first (if any) an element bound to spell or attack:
            elem = None
            for a in self.attributes:
                if a in tgs.el_names:
                    if elem is None:
                        elem = a
                    else:
                        return "me"

            for t in tgs.elemental:
                if t.id.lower() == elem:
                    return t

        # GFX/SFX:
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
            # Try to predict the images:
            if self.attacker_effects["gfx"]:
                renpy.start_predict(self.get_attackers_first_effect_gfx())
            if self.main_effect["gfx"]:
                renpy.start_predict(self.get_main_gfx())

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
            gfx_overlay.be_taunt(attacker, self)

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
            # Try to predict the images:
            if self.attacker_effects["gfx"]:
                renpy.stop_predict(self.get_attackers_first_effect_gfx())
            if self.main_effect["gfx"]:
                renpy.stop_predict(self.get_main_gfx())

        def time_attackers_first_action(self, battle, attacker):
            # Lets start with the very first part (attacker_action):
            self.timestamps[0] = renpy.curry(self.show_attackers_first_action)(battle, attacker)
            delay = self.get_show_attackers_first_action_initial_pause() + self.attacker_effects.get("duration", 0)
            hide_first_action = delay + self.attacker_action.get("keep_alive_delay", 0)
            self.timestamps[hide_first_action] = renpy.curry(self.hide_attackers_first_action)(battle, attacker)
            return delay

        def show_attackers_first_action(self, battle, attacker):
            if self.attacker_action["gfx"] == "step_forward":
                battle.move(attacker, battle.get_cp(attacker, xo=50), .5, pause=False)

            sfx = self.attacker_action.get("sfx", None)
            if sfx:
                renpy.sound.play(sfx)

        def get_show_attackers_first_action_initial_pause(self):
            if self.attacker_action["gfx"] == "step_forward":
                return .5
            else:
                return 0

        def hide_attackers_first_action(self, battle, attacker):
            if self.attacker_action["gfx"] == "step_forward":
                battle.move(attacker, attacker.dpos, .5, pause=False)

        def time_attackers_first_effect(self, battle, attacker, targets):
            start = self.get_show_attackers_first_action_initial_pause()
            if start in self.timestamps:
                start = start + uniform(.001, .002)
            self.timestamps[start] = renpy.curry(self.show_attackers_first_effect)(battle, attacker, targets)

            if self.attacker_effects["gfx"]:
                effects_delay = start + self.attacker_effects.get("duration", 0)
                if effects_delay in self.timestamps:
                    effects_delay = effects_delay + uniform(.001, .002)
                self.timestamps[effects_delay] = renpy.curry(self.hide_attackers_first_effect)(battle, attacker)
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
                if self.attacker_effects.get("hflip", None) and battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0]:
                    what = Transform(what, xzoom=-1)
                    align = (1.0 - align[0], align[1])

                renpy.show("casting", what=what,  at_list=[Transform(pos=battle.get_cp(attacker, type=point, xo=xo, yo=yo), align=align)], zorder=attacker.besk["zorder"]+zorder)

            sfx = self.attacker_effects["sfx"]
            if sfx:
                if sfx == "default":
                    sfx="content/sfx/sound/be/casting_1.mp3"
                renpy.sound.play(sfx)

        def hide_attackers_first_effect(self, battle, attacker):
            # For now we just hide the tagged image here:
            renpy.hide("casting")

        def time_main_gfx(self, battle, attacker, targets, start):
            if start in self.timestamps:
                start = start + uniform(.001, .002)
            self.timestamps[start] = renpy.curry(self.show_main_gfx)(battle, attacker, targets)

            pause = start + self.main_effect["duration"]
            # Kind of a shitty way of trying to handle attacks that come.
            # With their own pauses in time_main_gfx method.
            pause += getattr(self, "firing_effects", {}).get("duration", 0)
            pause += getattr(self, "projectile_effects", {}).get("duration", 0)
            if pause in self.timestamps:
                pause = pause + uniform(.001, .002)

            self.timestamps[pause] = renpy.curry(self.hide_main_gfx)(targets)

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
                gfx = ProportionalScale(gfx, *scale)

            return gfx

        def show_main_gfx(self, battle, attacker, targets):
            # Shows the MAIN part of the attack and handles appropriate sfx.
            gfx = self.main_effect["gfx"]
            sfx = self.main_effect["sfx"]
            loop_sfx = self.main_effect.get("loop_sfx", False)

            # SFX:
            if isinstance(sfx, (list, tuple)):
                if not loop_sfx:
                    sfx = choice(sfx)

            if sfx:
                renpy.music.play(sfx, channel='audio')

            # GFX:
            if gfx:
                what = self.get_main_gfx()

                aim = self.main_effect["aim"]
                point = aim.get("point", "center")
                anchor = aim.get("anchor", (.5, .5))
                xo = aim.get("xo", 0)
                yo = aim.get("yo", 0)

                # Flip the attack image if required:
                if self.main_effect.get("hflip", None) and battle.get_cp(attacker)[0] > battle.get_cp(targets[0])[0]:
                    what = Transform(what, xzoom=-1)

                for index, target in enumerate(targets):
                    gfxtag = "attack" + str(index)
                    renpy.show(gfxtag, what=what, at_list=[Transform(pos=battle.get_cp(target, type=point, xo=xo, yo=yo), anchor=anchor)], zorder=target.besk["zorder"]+1)

        def hide_main_gfx(self, targets):
            for i in xrange(len(targets)):
                gfxtag = "attack" + str(i)
                renpy.hide(gfxtag)

        def time_target_sprite_damage_effect(self, targets, died, start):
            # We take previous start as basepoint for execution:
            damage_effect_start = start + self.target_sprite_damage_effect["initial_pause"]

            if damage_effect_start in self.timestamps:
                damage_effect_start = damage_effect_start + uniform(.001, .002)
            self.timestamps[damage_effect_start] = renpy.curry(self.show_target_sprite_damage_effect)(targets)

            delay = damage_effect_start + self.target_sprite_damage_effect["duration"]
            if delay in self.timestamps:
                delay = delay + uniform(.001, .002)

            self.timestamps[delay] = renpy.curry(self.hide_target_sprite_damage_effect)(targets, died)

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
            damage_effect_start = start + self.target_damage_effect["initial_pause"]

            if damage_effect_start in self.timestamps:
                damage_effect_start = damage_effect_start + uniform(.001, .002)
            self.timestamps[damage_effect_start] = renpy.curry(self.show_target_damage_effect)(targets, died)

            delay = damage_effect_start + self.get_target_damage_effect_duration()
            if delay in self.timestamps:
                delay = delay + uniform(.001, .002)

            self.timestamps[delay] = renpy.curry(self.hide_target_damage_effect)(targets, died)

        def show_target_damage_effect(self, targets, died):
            """Easy way to show damage like the bouncing damage effect.
            """
            type = self.target_damage_effect.get("gfx", "battle_bounce")
            force = self.target_damage_effect.get("force", False)
            if type == "battle_bounce":
                for index, target in enumerate(targets):
                    if target not in died or force:
                        tag = "bb" + str(index)
                        value = target.beeffects[0]

                        if "missed_hit" in target.beeffects:
                            gfx = self.dodge_effect.get("gfx", "dodge")
                            if gfx == "dodge":
                                s = "Missed"
                            else:
                                s = "▼ "+"%s" % value
                            color = target.dmg_font
                        else:
                            effects = []
                            for effect in target.beeffects:
                                if isinstance(effect, tuple):
                                    effects.append(effect)

                            if len(effects) == 1:
                                value, color = self.color_string_by_DAMAGE_type(effect, return_for="bb")
                                s = "%s" % value
                            else:
                                if value < 0:
                                    s = "%s" % -value
                                    color = "lightgreen"
                                else:
                                    s = "%s" % value
                                    color = target.dmg_font

                        if "critical_hit" in target.beeffects:
                            s = "\n".join([s, "Critical hit!"])
                        txt = Text(s, style="TisaOTM", min_width=200,
                                   text_align=.5, color=color, size=18)
                        renpy.show(tag, what=txt,
                                   at_list=[battle_bounce(battle.get_cp(target,
                                                                        type="tc",
                                                                        yo=-30))],
                                   zorder=target.besk["zorder"]+2)

                        target.dmg_font = "red"

        def get_target_damage_effect_duration(self):
            type = self.target_damage_effect.get("gfx", "battle_bounce")
            if type == "battle_bounce":
                duration = 1.5
            else:
                duration = 0

            # Kind of a shitty way of trying to handle attacks that come
            # With their own pauses in time_main_gfx method.
            firing = hasattr(self, "firing_effects")
            if hasattr(self, "firing_effects"):
                duration += getattr(self, "firing_effects", {}).get("duration", 0)
                duration += self.main_effect.get("duration")
            duration += getattr(self, "projectile_effects", {}).get("duration", 0)

            return duration

        def hide_target_damage_effect(self, targets, died):
            for index, target in enumerate(targets):
                if target not in died:
                    tag = "bb" + str(index)
                    renpy.hide(tag)

        def time_target_death_effect(self, died, start):
            death_effect_start = start + self.target_death_effect["initial_pause"]

            if death_effect_start in self.timestamps:
                death_effect_start = death_effect_start + uniform(.001, .002)
            self.timestamps[death_effect_start] = renpy.curry(self.show_target_death_effect)(died)

            delay = death_effect_start + self.target_death_effect["duration"]
            if delay in self.timestamps:
                delay = delay + uniform(.001, .002)

            self.timestamps[delay] = renpy.curry(self.hide_target_death_effect)(died)

        def show_target_death_effect(self, died):
            gfx = self.target_death_effect["gfx"]
            sfx = self.target_death_effect["sfx"]
            duration = self.target_death_effect["duration"]

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
            effect_start = start + self.bg_main_effect["initial_pause"]

            if effect_start in self.timestamps:
                effect_start = effect_start + uniform(.001, .002)
            self.timestamps[effect_start] = self.show_bg_main_effect

            delay = effect_start + self.bg_main_effect["duration"]
            if delay in self.timestamps:
                delay = delay + uniform(.001, .002)

            self.timestamps[delay] = self.hide_bg_main_effect

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
                renpy.with_statement(dissolve)
                # renpy.pause(.5)

        def hide_bg_main_effect(self):
            gfx = self.bg_main_effect["gfx"]
            if gfx == "mirage":
                battle.bg.change("default")
            elif gfx == "black":
                renpy.with_statement(None)
                renpy.show("bg", what=battle.bg)
                renpy.with_statement(dissolve)

        def time_dodge_effect(self, targets, attacker, start):
            # effect_start = start - .3
            # if effect_start < 0:
                # effect_start = 0

            # Ok, so since we'll be using it for all kinds of attacks now, we need better timing controls:
            effect_start = self.dodge_effect.get("initial_pause", None)
            if effect_start is None:
                effect_start = start - .3
                if effect_start < 0:
                    effect_start = 0
            else:
                effect_start = effect_start + start

            if effect_start in self.timestamps:
                effect_start = effect_start + uniform(.001, .002)
            self.timestamps[effect_start] = renpy.curry(self.show_dodge_effect)(attacker, targets)

            # Hiding timing as well in our new version:
            delay = effect_start + self.main_effect["duration"]
            if delay in self.timestamps:
                delay = delay + uniform(.001, .002)

            self.timestamps[delay] = renpy.curry(self.hide_dodge_effect)(targets)

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
                        pause = self.main_effect["duration"]
                        if pause < .5:
                            pause = 0
                        else:
                            pause = pause - .5

                        renpy.show(target.betag, what=target.besprite, at_list=[be_dodge(xoffset, pause)], zorder=target.besk["zorder"])

                # We need to find out if it's reasonable to show shields at all based on damage effects!
                # This should ensure that we do not show the shield for major damage effects, it will not look proper.
                elif "magic_shield" in target.beeffects and self.target_sprite_damage_effect["gfx"] != "fly_away":
                    # Get GFX:
                    what = None
                    for event in battle.get_all_events():
                        if event.target == target and isinstance(event, DefenceBuff) and event.activated_this_turn:
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
                    tag = "dodge" + str(index)
                    renpy.show(tag, what=what, at_list=[Transform(size=size, pos=battle.get_cp(target, type="center"), anchor=(.5, .5))], zorder=target.besk["zorder"]+1)

        def hide_dodge_effect(self, targets):
            # gfx = self.dodge_effect.get("gfx", "dodge")
            for index, target in enumerate(targets):
                if "magic_shield" in target.beeffects:
                    tag = "dodge" + str(index)
                    renpy.hide(tag)


    class BE_AI(_object):
        # Not sure this even needs to be a class...
        def __init__(self, source):
            self.source = source

        def __call__(self):
            skip = BESkip(source=self.source)

            skills = self.get_available_skills()
            if skills:
                skill = choice(skills)
                # So we have a skill... now lets pick a target(s):
                skill.source = self.source
                targets = skill.get_targets() # Get all targets in range.
                targets = targets if "all" in skill.type else [choice(targets)] # We get a correct amount of targets here.

                skill(ai=True, t=targets)
            else:
                skip()

        def get_available_skills(self):
            # slaves should not battle
            if self.source.status == "slave":
                return

            allskills = list(self.source.attack_skills) + list(self.source.magic_skills)
            return [s for s in allskills if s.check_conditions(self.source)]

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
        def __init__(self, source):
            super(Complex_BE_AI, self).__init__(source=source)

        def __call__(self):
            skip = BESkip(source=self.source)

            temp = self.get_available_skills()
            if not temp:
                skip()
                return

            # Split skills in containers:
            skills = {}
            for s in temp:
                skills.setdefault(s.kind, []).append(s)

            # Reviving first:
            revival_skills = skills.get("revival", None)
            if revival_skills and dice(50):
                for skill in revival_skills:
                    targets = skill.get_targets(source=self.source)
                    if targets:
                        skill.source = self.source
                        targets = targets if "all" in skill.type else [choice(targets)]
                        skill(ai=True, t=targets)
                        return

            healing_skills = skills.get("healing", None)
            if healing_skills and dice(70):
                for skill in healing_skills:
                    targets = skill.get_targets(source=self.source)
                    for t in targets:
                        if t.health < t.maxhp*.5:
                            skill.source = self.source
                            targets = targets if "all" in skill.type else [t]
                            skill(ai=True, t=targets)
                            return

            buffs = skills.get("buffs", None)
            if buffs and dice(10):
                for skill in buffs:
                    targets = skill.get_targets(source=self.source)
                    if targets:
                        skill.source = self.source
                        targets = targets if "all" in skill.type else [choice(targets)]
                        skill(ai=True, t=targets)
                        return

            attack_skills = skills.get("assault", None)
            if attack_skills:
                # Sort skills by menu_pos:
                attack_skills.sort(key=attrgetter("menu_pos"))
                while attack_skills:
                    # Most powerful skill has 70% chance to trigger.
                    # Last skill in the list will execute!
                    skill = attack_skills.pop()
                    if not attack_skills or dice(70):
                        skill.source = self.source
                        targets = skill.get_targets()
                        targets = targets if "all" in skill.type else [choice(targets)]
                        skill(ai=True, t=targets)
                        return

            # In case we did not pick any specific skill:
            skip()

    #def get_char_with_lowest_attr(chars, attr="hp"):
    #    chars.sort(key=attrgetter(attr))
    #    return chars[0]
