init -9 python:
    #################################################################
    # UNIQUE BUILDING/LOCATION CLASSES
    # The classes for actual buildings with the customizations they require.
    #
    class SlaveMarket(HabitableLocation):
        """
        Class for populating and running of the slave market.
        """
        def __init__(self):
            """
            Creates a new SlaveMarket.
            """
            super(SlaveMarket, self).__init__(id="PyTFall Slavemarket")

            self.chars_list = None # slaves currently for sale
            self.index = 0         # the selected slave

            self.blue_slaves = list() # slaves under Blue training

            self.restock_day = 0

        def populate_chars_list(self):
            """
            Populates the list of characters that are available.
            """
            if day >= self.restock_day:
                self.restock_day += locked_random("randint", 2, 3)

                # Search for chars to add to the slavemarket.
                uniques = []
                randoms = []
                total = randint(9, 12)
                for c in self.inhabitants:
                    if c.location == pytfall.jail:
                        continue
                    if c.__class__ == Char:
                        uniques.append(c)
                    elif c.__class__ == rChar:
                        randoms.append(c)

                # Prioritize unique chars:
                slaves = random.sample(uniques, min(len(uniques), 7))
                slaves.extend(random.sample(randoms, min(len(randoms), total-len(slaves))))
                shuffle(slaves)
                self.chars_list = slaves
                self.index = 0

                # Gazette:
                temp = "Stan of the PyTFall's Slave Market was seen by our reporters "
                temp += "complaining about the poor quality of the new slave lot. We however didn't find any prove of such a claim!"
                temp1 = "Blue of the Slave Market sent out a bulletin about new slave arrivals!"
                gazette.other.append(choice([temp, temp1]))

        def remove_char(self, char):
            if char in self.chars_list:
                self.chars_list.remove(char)
                self.index = 0
            if char in self.blue_slaves:
                self.blue_slaves.remove(char)

        def get_price(self, char):
            return char.fin.get_price()

        def buy_slave(self, char):
            if not hero.take_ap(1):
                return "You don't have enough AP left for this action!"

            if not hero.take_money(self.get_price(char), reason="Slave Purchase"):
                return "You don't have enough money for this purchase!"

            renpy.play("content/sfx/sound/world/purchase_1.ogg")
            hero.add_char(char)
            char.reset_workplace_action()
            char.home = pytfall.streets
            set_location(char, None)
            self.chars_list.remove(char)
            self.index = 0

        def next_index(self):
            """
            Sets the focus to the next char.
            """
            self.index += 1
            if self.index == len(self.chars_list):
                self.index = 0

        def previous_index(self):
            """
            Sets the focus to the previous char.
            """
            self.index -= 1
            if self.index < 0:
                self.index = len(self.chars_list) - 1

        def get_char(self):
            return self.chars_list[self.index]

        def set_char(self, index):
            self.index = index

        def next_day(self):
            """
            Solves the next day logic.
            """
            self.populate_chars_list()

            # Blue training:
            trained, trainee = [], []
            for slave in self.blue_slaves:
                if slave.flag("release_day" == day):
                    trained.append(slave)
                else:
                    trainee.append(slave)
            for slave in trained:
                hero.add_char(slave)
                slave.reset_workplace_action()
                slave.home = pytfall.streets
                set_location(slave, None)
                # pytfall.temp_text.append("Blue has finished training %s! The slave has been delivered to you!" % chars[g].name)
            self.blue_slaves = trainee

    class CityJail(BaseBuilding):
        """
        The jail where escaped slaves can turn up, captured characters of SE are listed
         and misbehaving citizens are held as prisoners.
        """
        def __init__(self):
            super(CityJail, self).__init__()

            self.chars_list = None          # the list of chars for the current activity in the jail
            self.index = None               # the selected char

            self.slaves = list()            # caught runaway slaves currently for sale
            self.slave_index = [0,]         # the selected slave
            self.slave_restock_day = 0

            self.captures = list()          # captured characters from SE
            self.capt_index = [0,]          # the selected captured char
            self.auto_sell_captured = False # Do we auto-sell SE captured slaves?

            self.cells = list()             # civilian prisoners
            self.cell_index = [0,]          # the selected prisoner
            self.cell_restock_day = 0

        def switch_mode(self, mode):
            if mode == "slaves":
                self.chars_list = self.slaves
                self.index = self.slave_index
            elif mode == "cells":
                self.chars_list = self.cells
                self.index = self.cell_index
            else: # captures
                self.chars_list = self.captures
                self.index = self.capt_index

        def populate_chars_list(self):
            """
            Populates the list of characters that are present.
            """
            if day >= self.slave_restock_day:
                # populate the list of runaway slaves
                self.slave_restock_day += locked_random("randint", 2, 3)

                # Search for slaves to add to the jail.
                slaves = [c for c in chars.values() if c.status == "slave" and c not in pytfall.sm.chars_list and c not in hero.chars and c.location != pytfall.jail]

                slaves = random.sample(slaves, min(randint(0, 2), max(0, 12 - len(self.slaves))))

                for c in slaves:
                    if c.location == pytfall.ra:
                        del pytfall.ra.girls[c]
                    self.add_slave(c)

            if day >= self.cell_restock_day:
                # populate the list of free prisoners
                self.cell_restock_day += locked_random("randint", 2, 3)

                # Search for citizens to add to the jail.
                PUNISHABLE_TRAITS = {"Aggressive": ("Fight", (4, 10)),
                                     "Vicious": ("Bodily harm", (2, 10)),
                                     "Sadist": ("Assault", (4, 10)),
                                     "Exhibitionist": ("Indecent behavior", (1, 3)),
                                     "Kleptomaniac": ("Theft", (1, 4)),
                                     "Heavy Drinker": ("Brawl", (3, 6))}
                cells = []
                for c in chars.values():
                    if c.status != "free" or c.location == self or c.action.__class__ == ExplorationJob or c.home == pytfall.afterlife:
                        continue
                    traits = list(i.id for i in c.traits if i.id in PUNISHABLE_TRAITS)
                    for t in traits:
                        cells.append((c, t))

                cells = random.sample(cells, min(randint(0, 2), max(0, 12 - len(self.cells))))
                temp = set()
                for c in cells:
                    char = c[0]
                    if char in temp:
                        continue
                    temp.add(char)
                    sentence = PUNISHABLE_TRAITS[c[1]]
                    self.add_prisoner(char, sentence[0], randint(*sentence[1]))
                    # FIXME notify the player about the event

        def remove_char(self, char):
            if char in self.slaves:
                self.slaves.remove(char)
                self.slave_index = [0,]

            if char in self.captures:
                self.captures = list()
                self.capt_index = [0,]

            if char in self.cells:
                self.cells = list()
                self.cell_index = [0,]

        def add_slave(self, char):
            set_location(char, self)
            char.set_flag("release_day", day + 10)
            self.slaves.append(char)
            #self.slave_index = [0,]

        def add_capture(self, char):
            set_location(char, self)
            # Auto-selloff through flag set in SE module
            # TODO se: Implement the button in SE!
            char.set_flag("release_day", day + (0 if self.auto_sell_captured else 20))
            self.captures.append(char)

        def add_prisoner(self, char, sentence, days):
            """Sends a char to the jail, but bails them out if they can afford it.

            char: Character to throw into Jail
            sentence: Sentence type (reason to put in Jail)
            days: the length of the sentence
            """
            char.set_flag("release_day", day + days)
            if char.take_money(self.get_bail(char), "Bail:%s" % sentence):
                char.del_flag("release_day")
                return False

            char.set_flag("sentence_type", sentence)
            char.set_flag("last_location", char.location)
            set_location(char, self)
            self.cells.append(char)
            #self.cell_index = [0,]

            if char in hero.chars:
                char.set_task(None)
                for team in hero.teams:
                    if char in team:
                        team.remove(char)
                return True
            return False

        def get_fees4captured(self, char):
            # 200 for registration with city hall + 30 per day for "rent"
            return 200 + (20 + day - char.flag("release_day")) * 30

        def get_price(self, slave):
            """
            Returns the price to retrieve the slave.
            """
            if self.chars_list == self.slaves:
                return int(slave.fin.get_price() * .8)
            else: # self.chars_list == self.captures
                return self.get_fees4captured(slave) + 2000

        def sell_price(self, slave):
            return max(50, slave.fin.get_price()/4 - self.get_fees4captured(slave))

        def get_bail(self, char):
            """
            Returns the price to bail the prisoner.
            """
            return (char.flag("release_day") - day) * 500

        def buy_slave(self, char):
            """Buys an escaped slave from the jail.
            """
            if not hero.take_ap(1):
                return "You don't have enough AP left for this action!"
            if not hero.take_money(self.get_price(char), reason="Slave (Re)Purchase"):
                return "You don't have enough money for this purchase!"

            renpy.play("content/sfx/sound/world/purchase_1.ogg")
            self.slaves.remove(char)
            self.index[0] = 0
            if char not in hero.chars:
                hero.add_char(char)
                char.home = pytfall.streets
                char.reset_workplace_action()
            set_location(char, None)

        def sell_captured(self, char):
            """
            Sells off captured char from the jail for a flat price of 1500 Gold - the fees:
            """
            if not hero.take_ap(1):
                return "You don't have enough AP left for this action!"

            renpy.play("content/sfx/sound/world/purchase_1.ogg")
            hero.add_money(self.sell_price(char), "SlaveTrade")

            self.captures.remove(char)
            self.index[0] = 0

            char.del_flag("release_day")
            char.home = pytfall.sm
            set_location(char, None)

        def retrieve_captured(self, char, direction):
            """
            Retrieve a captured character (during SE).
            We handle simple sell-off in a different method (self.sell_captured)
            """
            if not hero.take_ap(1):
                return "You don't have enough AP left for this action!"

            blue_train = direction == "Blue"
            base_price = self.get_fees4captured(char)
            blue_price = 2000
            if hero.gold < base_price:
                return "You don't have enough money!"
            if blue_train and hero.gold < base_price + blue_price:
                return "You don't have enough money for upfront payment for Blue's services!"

            renpy.play("content/sfx/sound/world/purchase_1.ogg")
            hero.take_money(base_price, reason="Jail Fees")
            if blue_train:
                hero.take_money(blue_price, reason="Blue's Fees")
                char.set_flag("release_day", day+30)
                pytfall.sm.blue_slaves.append(char)
            else:
                char.del_flag("release_day")
                set_location(char, None)

            self.captures.remove(char)
            self.index[0] = 0

        def bail_char(self, char):
            """Bails a prisoner from the jail.
            """
            if not hero.take_ap(1):
                return "You don't have enough AP left for this action!"
            price = self.get_bail(char)
            if not hero.take_money(price, reason="Prisoner Bail"):
                return "You don't have enough money to do this!"

            renpy.play("content/sfx/sound/world/purchase_1.ogg")

            self.cells.remove(char)
            self.index[0] = 0

            char.del_flag("sentence_type")
            char.del_flag("release_day")
            set_location(char, char.get_flag("last_location"))
            char.del_flag("last_location")

            if char in hero.chars:
                char.gfx_mod_stat("disposition", randint(10, 40))
            else:
                char.gfx_mod_stat("disposition", 50 + randint(price/10))
            char.gfx_mod_stat("affection", affection_reward(char, stat="gold"))

        def next_index(self):
            """
            Sets the focus to the next char.
            """
            self.index[0] += 1
            if self.index[0] == len(self.chars_list):
                self.index[0] = 0

        def previous_index(self):
            """
            Sets the focus to the previous char.
            """
            self.index[0] -= 1
            if self.index[0] < 0:
                self.index[0] = len(self.chars_list) - 1

        def get_char(self):
            return self.chars_list[self.index[0]]

        def set_char(self, index):
            self.index[0] = index

        def next_day(self):
            # auto-sell slaves if their time is expired
            prisoners, frees = [], []
            for char in self.slaves:
                if char.flag("release_day") == day:
                    frees.append(char)
                else:
                    prisoners.append(char)
            if frees:
                self.slaves = [0,]
                for char in frees:
                    char.del_flag("release_day")
                    char.home = pytfall.sm
                    set_location(char, None)
                    if char in hero.chars:
                        hero.remove_char(char)
                        char.reset_workplace_action()
                        # FIXME notify the player
                    # pytfall.temp_text.append("Jail keepers sold off: {color=red}%s{/color}!" % char.name)
                self.slaves = prisoners

            # auto-sell the captured chars
            prisoners, frees = [], []
            for char in self.captures:
                if char.flag("release_day") == day:
                    frees.append(char)
                else:
                    prisoners.append(char)
            if frees:
                self.capt_index = [0,]
                for char in frees:
                    char.del_flag("release_day")
                    char.home = pytfall.sm
                    set_location(char, None)
                    # pytfall.temp_text.append("Jail keepers sold off: {color=red}%s{/color}!" % char.name)
                self.captures = prisoners

            # release chars whose sentence is over
            prisoners, frees = [], []
            for char in self.cells:
                char.mod_stat("joy", -randint(5, 10))
                if char.flag("release_day") == day:
                    frees.append(char)
                else:
                    prisoners.append(char)
            if frees:
                self.cell_index = [0,]
                for char in frees:
                    char.del_flag("sentence_type")
                    char.del_flag("release_day")
                    set_location(char, char.get_flag("last_location"))
                    char.del_flag("last_location")
                    if char in hero.chars:
                        pass # FIXME notify the player!
                    # If we know they're in jail
                    #    txt.append("    %s, in jail for %s days"%(char.fullname, days))
                    #    if cdb: txt.append("{color=blue}    (%s days till escape){/color}"%(20-girl_away_days))
                    #    txt.append("    %s"%char.fullname)
                    #    if cdb: txt.append("{color=blue}        in jail for %s days (%s days till escape){/color}"%(days, days)))

                self.cells = prisoners

            self.populate_chars_list()


    class RunawayManager(_object):
        """
        The class that handles runawawy logic.
        """

        STATUS_STATS = ["vitality", "intelligence", "agility"]

        ACTION = "Hiding"
        LOCATION = "Unknown"

        CAUGHT = "caught"
        DEFEATED = "defeated"
        FOUGHT = "fought"
        ESCAPED = "escaped"

        def __init__(self):
            """
            Creates a new RunawwayManager.
            """
            self.girls = dict()
            self.look_cache = dict()


        def add(self, girl, jail=False):
            """
            Adds a girl that has runaway.
            girl = The girl to add.
            jail = Whether to add straight to jail.
            """
            if girl not in self:
                for team in hero.teams:
                    if girl in team:
                        team.remove(girl)

                if jail:
                    pytfall.jail.add_slave(girl)

                else:
                    self.girls[girl] = 0
                    #girl_disobeys(girl, 10)
                    set_location(girl, pytfall.ra)

        def can_escape(self, girl, location, guards=None, girlmod=None, pos_traits=None,
                       neg_traits=["Restrained"], use_be=True, simulate=True, be_kwargs=None):
            """
            Calculates whether a girl can the location.
            girl = The girl check.
            location = The location to check, or None to ignore security and go straight to combat.
            guards = A list of guards to use in combat. If None guards/warriors are pulled from the locaiton.
            girlmod = A dict to use to record the girls stats.
            pos_traits = A list of trait names that increase the girls chance.
            neg_trats = A list of trait names that decrease the girls chance.
            use_be = Whether to require a BE simulation at high security levels.
            simulate = Whether to simulate the battle or use the BE.
            be_kwargs = Keyword arguments to pass to the BE.
            """
            # This requires revision to be used in the future!

            # Ensure stats in girlmod
            if girlmod:
                girlmod.setdefault("health", 0)
                girlmod.setdefault("vitality", 0)
                girlmod.setdefault("joy", 0)
                girlmod.setdefault("disposition", 0)
                girlmod.setdefault("exp", 0)

            be_kwargs = dict() if be_kwargs is None else be_kwargs
            # Get traits
            p = 0
            if pos_traits:
                for i in pos_traits:
                    p += girl_training_trait_mult(girl, i)

            n = 0
            if neg_traits:
                for i in neg_traits:
                    n += girl_training_trait_mult(girl, i)

            # Get security
            if location:
                sec = self.location_security(location)
                runaway = (self.location_runaway(location) + p) < (sec - n)

            else:
                sec = 1
                runaway = True

            if runaway:
                # If no BE or low security
                if not use_be or sec < .5:
                    # Girl escaped without fighting
                    return True, self.ESCAPED

                # If girl is too injured to fight
                elif girl.get_stat("health") < girl.get_max("health")/4 or girl.get_stat("vitality") < girl.get_max("vitality")/4:
                    # Girl was caught without fighting
                    return False, self.CAUGHT

                # BE simultaion
                else:
                    # If we need guards
                    if not guards:

                        # If we have no location, girl walks out
                        if not location:
                            return True, self.ESCAPED

                        else:
                            # Get guards if available action
                            if hasattr(location, "actions") and "Guard" in location.actions:
                                guards = [g for g in location.get_girls("Guard") if g.AP > 0 and g.get_stat("health") > 40 and g.get_stat("vitality") > 40]

                            # Get warriors
                            else:
                                guards = [g for g in location.get_girls(occupation="Combatant") if g.AP > 0 and g.get_stat("health") > 40 and g.get_stat("vitality") > 40]

                            if girl in guards: guards.remove(girl)

                            # Force simulation if hero not available
                            if not simulate: simulate = hero.workplace is not location

                            # If we are simulating
                            if simulate:
                                # Get amount according to location
                                gam = max(int(len(guards) * ((sec-0.5) * 2)), 1)
                                while len(guards) > gam: guards.remove(choice(guards))

                                # Add hero
                                if hero.workplace is location: guards.append(hero)

                            # Else we are BE
                            else:
                                # If we have more then 2, get the player and 2 random guards
                                if len(guards) > 2:
                                    g = randint(0, len(guards)-1)
                                    guards = [hero, guards[g], guards[g+1]]
                                    pt_ai = [False, True, True]

                                else:
                                    guards.insert(0, hero)
                                    pt_ai = [True for i in guards]
                                    pt_ai[0] = False

                    # If we want to simulate
                    if simulate:

                        # If we end up with no guards
                        if not guards:
                            return True, self.ESCAPED

                        result, exp = s_conflict_resolver(guards, [girl], new_results=True)

                        # Remove hero from guards to avoid event
                        if hero in guards: guards.remove(hero)

                        # Overwhelming victory
                        # Girl was caught without fighting
                        if result == "OV":
                            for g in guards:
                                guard_escape_event.count(g, 1)
                                guard_escape_event.against(g, [girl])
                                guard_escape_event.stats(g, dict(exp=randint(15, 25)))
                                guard_escape_event.win(g, 1)

                            return False, self.CAUGHT

                        # Desisive victory
                        # Girl was caught easily while fighting
                        elif result == "DV":
                            for g in guards:
                                guard_escape_event.count(g, 1)
                                guard_escape_event.against(g, [girl])
                                guard_escape_event.stats(g, dict(health=randint(-10, -20),
                                                                 vitality=randint(-10, -20),
                                                                 exp=exp
                                                                 ))
                                guard_escape_event.win(g, 1)

                            if girlmod:
                                girlmod["health"] -= randint(20, 30)
                                girlmod["vitality"] -= randint(20, 30)
                                girlmod["joy"] -= randint(0, 6)

                            else:
                                girl.mod_stat("health", -randint(20, 30))
                                girl.mod_stat("vitality", -randint(20, 30))
                                girl.mod_stat("joy", -randint(0, 6))

                            return False, self.DEFEATED

                        # Victory
                        # Girl was caught while fighting
                        elif result == "V":
                            for g in guards:
                                guard_escape_event.count(g, 1)
                                guard_escape_event.against(g, [girl])
                                guard_escape_event.stats(g, dict(health=randint(-10, -20),
                                                                 vitality=randint(-10, -20),
                                                                 exp=exp
                                                                 ))
                                guard_escape_event.win(g, 1)

                            if girlmod:
                                girlmod["health"] -= randint(10, 20)
                                girlmod["vitality"] -= randint(10, 20)
                                girlmod["joy"] -= randint(0, 3)

                            else:
                                girl.mod_stat("health", -randint(10, 20))
                                girl.mod_stat("vitality", -randint(10, 20))
                                girl.mod_stat("joy", -randint(0, 3))

                            return False, self.DEFEATED

                        # Lucky victory
                        # Girl was bearly caught while fighting
                        elif result == "LV":
                            for g in guards:
                                guard_escape_event.count(g, 1)
                                guard_escape_event.against(g, [girl])
                                guard_escape_event.stats(g, dict(health=randint(-20, -30),
                                                                 vitality=randint(-20, -30),
                                                                 ))
                                guard_escape_event.win(g, 1)

                            if girlmod:
                                girlmod["health"] -= randint(10, 20)
                                girlmod["vitality"] -= randint(10, 20)
                                girlmod["exp"] += exp

                            else:
                                girl.mod_stat("health", -randint(10, 20))
                                girl.mod_stat("vitality", -randint(10, 20))
                                girl.mod_exp(exp)

                            return False, self.DEFEATED

                        # Defeat
                        # Girl was able to escape while fighting
                        elif result == "D":
                            for g in guards:
                                guard_escape_event.count(g, 1)
                                guard_escape_event.against(g, [girl])
                                guard_escape_event.stats(g, dict(health=randint(-20, -30),
                                                                 vitality=randint(-20, -30),
                                                                 ))
                                guard_escape_event.loss(g, 1)

                            if girlmod:
                                girlmod["health"] -= randint(10, 20)
                                girlmod["vitality"] -= randint(10, 20)
                                girlmod["exp"] += exp
                                girlmod["joy"] += randint(0, 3)

                            else:
                                girl.mod_stat("health", -randint(10, 20))
                                girl.mod_stat("vitality", -randint(10, 20))
                                girl.mod_exp(exp)
                                girl.mod_stat("joy", randint(0, 3))

                            return True, self.FOUGHT

                        # Overwhelming defeat
                        # Girl was able to escape without fighting
                        elif result == "OD":
                            for g in guards:
                                guard_escape_event.count(g, 1)
                                guard_escape_event.against(g, [girl])
                                guard_escape_event.loss(g, 1)

                            if girlmod:
                                girlmod["exp"] += exp
                                girlmod["joy"] += randint(0, 6)

                            else:
                                girl.mod_exp(exp)
                                girl.mod_stat("joy", randint(0, 6))

                            return True, self.ESCAPED

                    else:
                        # Fight!
                        # TODO lt training (Alex) Check out what this is/does:
                        result, dead = start_battle(guards, [girl], pt_ai=pt_ai, **be_kwargs)

                        exp = (girl.attack + girl.defence + girl.agility + girl.magic) / 10

                        # Remove hero from guards to avoid event
                        if hero in guards: guards.remove(hero)

                        # If the guards won
                        if result:
                            for g in guards:
                                guard_escape_event.count(g, 1)
                                guard_escape_event.against(g, [girl])
                                guard_escape_event.stats(g, dict(vitality=-randint(-10, -20),
                                                                 exp=exp
                                                                 ))
                                guard_escape_event.win(g, 1)

                            if girlmod:
                                girlmod["vitality"] -= randint(10, 20)
                                girlmod["joy"] -= randint(0, 3)

                            else:
                                girl.mod_stat("health", -randint(10, 20))
                                girl.mod_stat("joy", -randint(0, 3))

                            return True, self.DEFEATED

                        # Else the girl won
                        else:
                            for g in guards:
                                guard_escape_event.count(g, 1)
                                guard_escape_event.against(g, [girl])
                                guard_escape_event.stats(g, dict(vitality=-randint(-10, -20),
                                                                 exp=exp
                                                                 ))
                                guard_escape_event.loss(g, 1)

                            if girlmod:
                                girlmod["vitality"] -= randint(10, 20)
                                girlmod["exp"] += exp
                                girlmod["joy"] += randint(0, 3)
                            else:
                                girl.mod_stat("vitality", -randint(10, 20))
                                girl.mod_exp(exp)
                                girl.mod_stat("joy", randint(0, 3))

                            return False, self.FOUGHT

            else:
                return False

        def get_look_around_girl(self, event):
            """
            Gets the girl for the event.
            event = The event to return the girl for.
            """
            return self.look_cache.pop(event.name, None)

        def location_runaway(self, location, sutree=None):
            """
            Returns a runaway chance for the location.
            location = The location to calculate the chance for.
            sutree = The name of the security upgrade tree to use if not default.

            Calculates the chance using:
            - The mod_runaway function if it exists.
            - The amount of guards in the location, if the action exists.
            - The amount of warriors in the location

            Returns:
            0 = high chance.
            1 = low chance
            """
            # Get runaway modifier
            mod = 0

            # If location has own function, use it # FIXME check upgrades and business!
            if hasattr(location, "mod_runaway"):
                mod = location.mod_runaway()

            # Else if has guard action, use amount over total
            elif hasattr(location, "actions") and "Guard" in location.actions:
                girls = [g for g in hero.chars if g.workplace == location]
                if girls:
                    mod = float(len(location.get_girls("Guard"))) / float(len(girls))
                else:
                    mod = 0

            # Else use warriors over total
            else:
                girls = [g for g in hero.chars if g.workplace == location]
                if girls:
                    mod = float(len(location.get_girls(occupation="Combatant"))) / float(len(girls))
                else:
                    mod = 0

            return mod

        def location_security(self, location, modifier=1):
            """
            Returns the security modifier for the location.
            location = The location to get the modifier for.
            modifier = A multiplier for the final modifier.

            Returns:
            1 = low chance
            2 = high chance
            """
            # Handled differently now.
            return 1 # (random.random() * (2 - location.security_mult())) * modifier

        def next_day(self):
            """
            Solves the next day logic for the girls.
            """
            type = "runawayndreport"
            txt = ["Escaped girls:"]

            # Replace with better code to prevent mass-creation/destruction of events?
            # Clean look_cache
            for i in self.look_cache.keys():
                pytfall.world_events.kill_event(i, cached=True)
                del self.look_cache[i]

            # Loop through girls in a random order
            girls = list(self.girls.keys())
            shuffle(girls)
            for girl in girls:
                cdb = config.developer
                txt.append("    %s"%girl.fullname)

                # Increase girls escape time
                girl_away_days = self.girls[girl] + 1
                self.girls[girl] = girl_away_days

                # Get status
                status = self.status(girl)
                if cdb: txt.append("{color=blue}        status: %s{/color}"%status)

                # Chance to escape for good
                if girl_away_days > 20:
                    if dice(status) and dice(girl_away_days):
                        del self.girls[girl]
                        hero.remove_char(girl)
                        char.home = pytfall.city
                        set_location(char, None)
                        char.reset_workplace_action()
                        char.status = "free"
                        if cdb: txt.append("{color=blue}        escaped for good{/color}")
                        continue

                # Chance to go to jail
                if girl_away_days > 10:
                    if dice(status):
                        del self.girls[girl]
                        pytfall.jail.add_slave(char)


                        if cdb: txt.append("{color=blue}        sent to jail.{/color}")
                        continue

                # Chance to find in look_around
                if dice(status) and len(self.look_cache) < 5:
                    ev = "runaway_look_around_%s"%str(girl)
                    self.look_cache[ev] = girl
                    # Add event for girl (do we want high priority?)
                    register_event_in_label(ev, label=girl.runaway_look_event, trigger_type="look_around", locations=["all"], dice=status, max_runs=1, start_day=day+1, priority=999)

                    if cdb: txt.append("{color=blue}        in look around (%s days till escape){/color}"%(20-girl_away_days))
                    continue

                if cdb: txt.append("{color=blue}        %s days till escape{/color}"%(20-girl_away_days))


            # If we have escaped girls, post the event
            if self.girls:
                ev = NDEvent()
                ev.type = type
                ev.char = None
                ev.img = im.Scale("content/gfx/bg/locations/dungeoncell.webp", int(config.screen_width*.6), int(config.screen_height*.8))
                ev.txt = "\n".join(txt)
                NextDayEvents.append(ev)


        def retrieve(self, girl):
            """
            Returns a girl to the player.
            girl = The girl to return.
            """
            if girl in self:
                del self.girls[girl]

                ev = "runaway_look_around_%s"%str(girl)
                if ev in self.look_cache:
                    del self.look_cache[ev]
                    pytfall.world_events.kill_event(ev)


                girl.home = pytfall.streets 
                set_location(girl, None)

        def status(self, girl):
            """
            Returns the "runaway status" of the girl.
            girl = The girl to get the status for.
            """
            a = 0
            b = 0
            for i in self.STATUS_STATS:
                a += girl.stats[i]
                b += girl.stats.max[i]

            status = (float(a) / float(b)) * 100
            status *= girl_training_trait_mult(girl, "Restrained")
            if girl.status == "slave": status *= .75

            return 100-status
