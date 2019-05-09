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
            return char.get_price()

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

                slaves = random.sample(slaves, min(min(len(slaves), randrange(3)), max(0, 12 - len(self.slaves))))

                for c in slaves:
                    if c.location == pytfall.ra:
                        del pytfall.ra.chars[c]
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
                    if c.status != "free" or c.location == self or c.action == ExplorationTask or c.home == pytfall.afterlife:
                        continue
                    traits = list(i.id for i in c.traits if i.id in PUNISHABLE_TRAITS)
                    for t in traits:
                        cells.append((c, t))

                cells = random.sample(cells, min(min(len(cells), randrange(3)), max(0, 12 - len(self.cells))))
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
            if char != hero and char.take_money(self.get_bail(char), "Bail:%s" % sentence):
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
                return int(slave.get_price() * .8)
            else: # self.chars_list == self.captures
                return self.get_fees4captured(slave) + 2000

        def sell_price(self, slave):
            return max(50, slave.get_price()/4 - self.get_fees4captured(slave))

        def prison_time(self, char):
            """
            Returns the remaining time the prisoner must spend in the jail.
            """
            return char.flag("release_day") - day + 1

        def get_bail(self, char):
            """
            Returns the price to bail the prisoner.
            """
            return self.prison_time(char) * 500

        def buy_slave(self, char):
            """Buys an escaped slave from the jail.
            """
            if not hero.take_ap(1):
                return "You don't have enough AP left for this action!"
            if not hero.take_money(self.get_price(char), reason="Slave (Re)Purchase"):
                return "You don't have enough money for this purchase!"

            renpy.play("content/sfx/sound/world/purchase_1.ogg")
            self.slaves.remove(char)
            self.slave_index[0] = 0
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
            self.capt_index[0] = 0

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
            self.capt_index[0] = 0

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
            self.cell_index[0] = 0

            char.del_flag("sentence_type")
            char.del_flag("release_day")
            set_location(char, char.get_flag("last_location"))
            char.del_flag("last_location")

            if char != hero:
                if char in hero.chars:
                    char.gfx_mod_stat("disposition", randint(10, 40))
                else:
                    char.gfx_mod_stat("disposition", 50 + randint(0, price/100))
                char.del_flag("cnd_interactions_blowoff")
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
                    if char in hero.chars:
                        hero.remove_char(char)
                        # FIXME notify the player
                    else:
                        char.home = pytfall.sm
                        set_location(char, None)
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
                    #if char in hero.chars:
                    #    pass # FIXME notify the player!
                    # If we know they're in jail
                    #    txt.append("    %s, in jail for %s days"%(char.fullname, days))
                    #    if cdb: txt.append("{color=blue}    (%s days till escape){/color}"%(20-girl_away_days))
                    #    txt.append("    %s"%char.fullname)
                    #    if cdb: txt.append("{color=blue}        in jail for %s days (%s days till escape){/color}"%(days, days)))

                self.cells = prisoners

            self.populate_chars_list()


    class RunawayManager(_object):
        """
        The class that handles runaway logic.
        """

        STATUS_STATS = ["vitality", "intelligence", "agility"]

        CAUGHT = "caught"
        FOUGHT = "fought"

        def __init__(self):
            """
            Creates a new RunawayManager.
            """
            self.chars = dict()
            self.look_cache = dict()

        def add(self, char):
            """
            Adds a char that has run away.
            char = The char to add.
            """
            for team in hero.teams:
                if char in team:
                    team.remove(char)

            self.chars[char] = day
            set_location(char, pytfall.ra)

        def try_escape(self, char, location=None, guards=None):
            """
            Calculates whether a character can escape the location.
            char = The char check.
            location = The location to check, or None to ignore security
            guards = The list of explicit guards
            """

            # Get security
            if location is not None:
                sec = self.location_security(location)
                if guards is None:
                    guards = [hero] + hero.chars
                    guards = [w for w in guards if w.workplace == location and w.action == GuardJob and w.is_available]
                else:
                    sec += len(guards)
            else:
                if guards is None:
                    sec = 0
                else:
                    sec = len(guards) 

            # get the char capability
            status = self.status(char)
            if guards is not None and char in guards:
                # Trojan horse
                guards.remove(char)
                sec /= 2

            # check for weak security
            if sec == 0 or dice(status/sec):
                self.add(char)
                return True

            # check for smart 'char' -> capable, but the security is tight at the moment
            if dice(status):
                return False

            # check if the only protection is the building -> noone to fight
            if not guards:
                return False

            # check for 'damaged' char -> pointless to fight
            if any("Injured" in char.effects,
                   char.get_stat("health") < char.get_max("health")/4,
                   char.get_stat("vitality") < char.get_max("vitality")/4,
                   char.PP <= 200): # PP_PER_AP
                if dice(max(status, 50)):
                    return False
                return False, self.CAUGHT

            # escalate to fight
            guards = random.sample(guards, min(len(guards), 3))
            member_aps = []
            def_team = Team(name="Guards", maxsize=3)
            for g in guards:
                def_team.add(g)
                member_aps.append(g.PP)
            off_team = Team(name="Runner", maxsize=1)
            off_team.add(char)

            battle = run_auto_be(off_team, def_team)
            if battle.winner == off_team:
                char.mod_exp(exp_reward(char, def_team, exp_mod=10))
                char.mod_stat("joy", randint(2, 6))

                self.add(char)
                return True, self.FOUGHT
            else:
                for member, aps in zip(def_team, member_aps):
                    # Awards:
                    if member not in battle.corpses:
                        aps = (aps - member.PP)/100.0 # PP_PER_AP = 100
                        member.mod_exp(exp_reward(member, char, exp_mod=aps*.1))
                char.mod_stat("joy", -randint(1, 5))
                return False, self.FOUGHT

        def get_look_around_char(self, event):
            """
            Gets the char for the event.
            event = The event to return the char for.
            """
            return self.look_cache[event.name]

        def location_security(self, location, modifier=1):
            """
            Returns the security modifier for the location.
            location = The location to get the modifier for.
            modifier = A multiplier for the final modifier.

            Returns:
            1 = low security
            2 = high security
            """
            # Get runaway modifier
            mod = 1

            # If location has own function, use it
            if hasattr(location, "mod_runaway"):
                mod += location.mod_runaway()

            # Add workers effect
            workers = [hero] + hero.chars
            workers = [w for w in workers if w.workplace == location and w.is_available]
            if workers:
                guards = [g for g in workers if g.action == GuardJob]
                guards = len(guards)
                workers = len(workers) - guards
                if workers == 0:
                    mod *= guards
                else:
                    mod *= float(guards) / float(workers)

            return mod

        def next_day(self):
            """
            Solves the next day logic for the chars.
            """
            rachars = self.chars
            if not rachars:
                return

            txt = ["Escaped characters:"]

            # Loop through chars in a random order
            rachars = list(rachars.keys())
            shuffle(rachars)

            for char in rachars:
                txt.append("    %s"%char.fullname)

                # get the chars escape time
                char_away_days = day - self.chars[char]+1

                # Get status
                status = self.status(char)

                # Chance to escape for good
                if char_away_days > 20 and dice(status) and dice(char_away_days):
                    self.remove_char(char)
                    char.status = "free"
                    hero.remove_char(char)
                    continue

                status = 100-status
                # Chance to go to jail
                if char_away_days > 10 and dice(status):
                    self.remove_char(char)
                    pytfall.jail.add_slave(char)
                    continue

                # Chance to find in look_around
                if dice(status):
                    ev = "runaway_look_around_%s"%str(char)
                    if ev not in self.look_cache:
                        self.look_cache[ev] = char
                        # Add event for the char (do we want high priority?)
                        register_event(ev, label=getattr(char, "runaway_look_event", "runaway_char_recapture"), trigger_type="look_around", locations=["all"], dice=status, times_per_days=(1,0), start_day=day+1, priority=999)

            # If we have escaped chars, post the event
            ev = NDEvent(type = "runawayndreport",
                         char = None,
                         img = "content/gfx/bg/locations/dungeoncell.webp",
                         txt = "\n".join(txt))
            NextDayEvents.append(ev)


        def remove_char(self, char):
            """
            Removes the character from the Manager.
            char = The char to remove.
            """
            del self.chars[char]

            ev = "runaway_look_around_%s"%str(char)
            ev = self.look_cache.pop(ev, None)
            if ev is not None:
                kill_event(ev)

        def retrieve(self, char):
            """
            Returns a character to the player.
            char = The char to return.
            """
            self.remove(char)

            char.home = pytfall.streets 
            set_location(char, None)

        def status(self, char):
            """
            Returns the "runaway status" of the character.
            char = The character to get the status for.
            """
            a = 0
            b = 0
            for i in self.STATUS_STATS:
                a += char.get_stat(i)
                b += char.get_max_stat(i)

            status = float(100*a)/float(b)
            #status *= girl_training_trait_mult(girl, "Restrained")
            status *= .75 # if char.status == "slave" - only slaves can run away at the moment
            return status
