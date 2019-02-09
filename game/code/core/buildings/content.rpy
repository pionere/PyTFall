init -9 python:
    #################################################################
    # UNIQUE BUILDING/LOCATION CLASSES
    # The classes for actual buildings with the customizations they require.
    #
    class SlaveMarket(HabitableLocation):
        """
        Class for populating and running of the slave market.

        TODO sm/lt: (Refactor)
        Use actors container from Location class and
        """
        def __init__(self, type=None):
            """
            Creates a new SlaveMarket.
            type = type girls predominantly present in the market. Not used.
            """
            super(SlaveMarket, self).__init__(id="PyTFall Slavemarket")
            self.type = [] if type is None else type

            self.chars_list = None

            self.girl = None

            self.blue_girls = dict() # Girls (SE captured) blue is training for you.
            self.restock_day = 0

        def populate_chars_list(self):
            """
            Populates the list of girls that are available.
            """
            if day >= self.restock_day:
                self.restock_day += locked_random("randint", 2, 3)

                # Search for chars to add to the slavemarket.
                uniques = []
                randoms = []
                total = randint(9, 12)
                for c in chars.values():
                    if c in hero.chars:
                        continue
                    if c.home == self:
                        if c.__class__ == Char:
                            uniques.append(c)
                        elif c.__class__ == rChar:
                            randoms.append(c)

                # Prioritize unique chars:
                slaves = random.sample(uniques, min(len(uniques), 7))
                slaves.extend(random.sample(randoms, min(len(randoms), total-len(slaves))))
                shuffle(slaves)
                self.chars_list = slaves

                # Gazette:
                temp = "Stan of the PyTFall's Slave Market was seen by our reporters "
                temp += "complaining about the poor quality of the new slave lot. We however didn't find any prove of such a claim!"
                temp1 = "Blue of the Slave Market sent out a bulletin about new slave arrivals!"
                gazette.other.append(choice([temp, temp1]))

        def get_price(self, girl):
            return girl.fin.get_price()

        def buy_girl(self, girl):
            if hero.take_ap(1):
                if hero.take_money(self.get_price(girl), reason="Slave Purchase"):
                    renpy.play("content/sfx/sound/world/purchase_1.ogg")
                    hero.add_char(girl)
                    girl.set_workplace(None, None)
                    girl.home = pytfall.streets
                    set_location(girl, None)
                    girl.set_workplace(None, None)
                    self.chars_list.remove(girl)

                    if self.chars_list:
                        self.girl = choice(self.chars_list)
                    else:
                        self.girl = None
                else:
                    renpy.call_screen('message_screen', "You don't have enough money for this purchase!")
            else:
                renpy.call_screen('message_screen', "You don't have enough AP left for this action!")

        def next_index(self):
            """
            Sets the focus to the next girl.
            """
            if self.chars_list:
                index = self.chars_list.index(self.girl)
                index = (index + 1) % len(self.chars_list)
                self.girl = self.chars_list[index]

        def previous_index(self):
            """
            Sets the focus to the previous girl.
            """
            if self.chars_list:
                index = self.chars_list.index(self.girl)
                index = (index - 1) % len(self.chars_list)
                self.girl = self.chars_list[index]

        def set_girl(self, girl):
            self.girl = girl

        def set_index(self):
            """
            Sets the focus to a random girl.
            """
            if self.chars_list:
                self.girl = choice(self.chars_list)

        def next_day(self):
            """
            Solves the next day logic.
            """
            self.populate_chars_list()

            for g in self.blue_girls.keys():
                self.blue_girls[g] += 1
                if self.blue_girls[g] == 30:
                    hero.add_char(g)
                    del self.blue_girls[g]
                    # pytfall.temp_text.append("Blue has finished training %s! The girl has been delivered to you!" % chars[g].name)

    class CityJail(BaseBuilding):
        """
        The jail where escaped slaves can turn up. May do other things later.
        """

        # TODO lt: Needs recoding!

        def __init__(self):
            super(CityJail, self).__init__()
            self.girl = None
            self.chars_list = []
            self.auto_sell_captured = False # Do we auto-sell SE captured slaves?

        def __contains__(self, char):
            return char in self.chars_list

        def add_prisoner(self, char, flag=None):
            """Adds a char to the jail.

            char: Character to throw into Jail
            flag: Sentence type (reason to put in Jail)
            """
            if char not in self:
                if char in hero.team:
                    hero.team.remove(char)
                self.chars_list.append(char)

                # Flag to determine how the girl is handled in the jail:
                if flag:
                    char.set_flag("sentence_type", flag)
                    if flag == "SE_capture":
                        char.set_flag("days_in_jail", 0)

        def get_price(self):
            """
            Returns the price to retrieve the girl.
            """
            # In case of non-slave girl, use 3000 as base price
            return (self.girl.fin.get_price() or 3000) / 2

        def buy_girl(self):
            """Buys an escaped girl from the jail.
            """
            if hero.take_ap(1):
                if hero.take_money(self.get_price(), reason="Slave Repurchase"):
                    renpy.play("content/sfx/sound/world/purchase_1.ogg")
                    self.remove_prisoner(self.girl, True)
                    self.girl.set_workplace(None, None)
                else:
                    renpy.call_screen('message_screen', "You don't have enough money for this purchase!")
            else:
                renpy.call_screen('message_screen', "You don't have enough AP left for this action!")

        def next_index(self):
            """
            Sets the focus to the next girl.
            """
            if self.chars_list:
                index = self.chars_list.index(self.girl)
                index = (index + 1) % len(self.chars_list)
                self.girl = self.chars_list[index]

        def previous_index(self):
            """
            Sets the focus to the previous girl.
            """
            if self.chars_list:
                index = self.chars_list.index(self.girl)
                index = (index - 1) % len(self.chars_list)
                self.girl = self.chars_list[index]

        def remove_prisoner(self, girl, update_location=True):
            """
            Returns an actor to the player.
            girl = The girl to return.
            """
            if girl in self:
                girl.del_flag("sentence_type")
                girl.del_flag("days_in_jail")
                self.chars_list.remove(girl)

                if self.chars_list:
                    self.index %= len(self.chars_list)
                    self.worker = self.chars_list[self.index]
                else:
                    self.index = 0
                    self.worker = None

                if update_location:
                    girl.home = pytfall.city if girl.status == "free" else pytfall.streets
                    set_location(girl, None)

        # Deals with girls captured during SE:
        def sell_captured(self, girl, auto=False):
            # Flat price of 1500 Gold - the fees:
            """
            Sells off captured girl from the jail.
            auto: Auto Selloff during next day.
            """
            if not auto:
                if not hero.take_ap(1):
                    renpy.call_screen('message_screen', "You don't have enough AP left for this action!")
                    return
                renpy.play("content/sfx/sound/world/purchase_1.ogg")
                hero.add_money(1500 - self.get_fees4captured(girl), "SlaveTrade")

            self.remove_prisoner(girl, False)
            girl.home = pytfall.sm
            set_location(girl, None)

        def next_day(self):
            for i in self.chars_list:
                if i.flag("sentence_type") == "SE_capture":
                    i.mod_flag("days_in_jail")
                    if self.auto_sell_captured:
                        # Auto-selloff through flag set in SE module
                        # TODO se: Implement the button in SE!
                        self.sell_captured(i, True)
                        # pytfall.temp_text.append("Jail keepers sold off: {color=[red]}%s{/color}!" % i.name)
                    if i.flag("days_in_jail") > 20:
                        # Auto-Selloff in case of 20+ days:
                        self.sell_captured(i, True)
                        # pytfall.temp_text.append("Jail keepers sold off: {color=[red]}%s{/color}!" % i.name)

        def get_fees4captured(self, girl):
            # 200 for registration with city hall + 30 per day for "rent"
            return 200 + girl.flag("days_in_jail") * 30

        def retrieve_captured(self, girl, direction):
            """
            Retrieve a captured character (during SE).
            We handle simple sell-off in a different method (self.sell_captured)
            """
            if hero.take_ap(1):
                base_price = self.get_fees4captured(girl)
                if hero.take_money(base_price, reason="Jail Fees"):
                    renpy.play("content/sfx/sound/world/purchase_1.ogg")
                    if direction == "STinTD":
                        self.remove_prisoner(girl, True)
                    elif direction == "Blue":
                        if hero.take_money(2000, reason="Blue's Fees"):
                            pytfall.sm.blue_girls[girl] = 0
                            self.remove_prisoner(girl, False)
                        else:
                            hero.add_money(base_price, reason="Jail Fees")
                            renpy.call_screen('message_screen', "You don't have enough money for upfront payment for Blue's services!")
                else:
                    renpy.call_screen('message_screen', "You don't have enough money!")
            else:
                renpy.call_screen('message_screen', "You don't have enough AP left for this action!")

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
            self.jail_cache = dict()
            self.look_cache = dict()

            self.retrieve_jail = False

            # Slavemarket stuff
            self.girl = None
            self.index = 0

        def __contains__(self, girl):
            """
            Checks whether a girl has runaway.
            """
            return girl in self.girls

        def add(self, girl, jail=False):
            """
            Adds a girl that has runaway.
            girl = The girl to add.
            jail = Whether to add straight to jail.
            """
            if girl not in self:
                self.girls[girl] = 0
                for team in hero.teams:
                    if girl in team:
                        team.remove(girl)
                girl_disobeys(girl, 10)

                if jail:
                    set_location(girl, pytfall.jail)

                    self.jail_cache[girl] = [4, False]
                    if self.girl is None:
                        self.girl = girl
                        self.index = 0
                else:
                    set_location(girl, pytfall.ra)

        def buy_girl(self):
            """
            Buys an escaped girl from the jail.
            """
            if hero.take_ap(1):
                if hero.take_money(self.get_price(), reason="Slave Repurchase"):
                    renpy.play("content/sfx/sound/world/purchase_1.ogg")
                    self.retrieve(self.girl)

                else:
                    renpy.call_screen('message_screen', "You don't have enough money for this purchase!")

            else:
                renpy.call_screen('message_screen', "You don't have enough AP left for this action!!")

            if not self.chars_list:
                renpy.hide_screen("slave_shopping")

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
                elif girl.health < girl.get_max("health")*.25 or girl.vitality < girl.get_max("vitality")*.25 :
                    # Girl was caight without fighting
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
                                guards = [g for g in location.get_girls("Guard") if g.AP > 0 and g.health > 40 and g.vitality > 40]

                            # Get warriors
                            else:
                                guards = [g for g in location.get_girls(occupation="Combatant") if g.AP > 0 and g.health > 40 and g.vitality > 40]

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
                                girlmod["joy"] -= choice([0,2,2,4,6])

                            else:
                                girl.health = max(1, girl.health - randint(20, 30))
                                girl.vitality -= randint(20, 30)
                                girl.joy -= choice([0,2,2,4,6])

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
                                girlmod["joy"] -= choice([0,1,1,2,3])

                            else:
                                girl.health = max(1, girl.health - randint(10, 20))
                                girl.vitality -= randint(10, 20)
                                girl.joy -= choice([0,1,2,2,3])

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
                                girl.health = max(1, girl.health - randint(10, 20))
                                girl.vitality -= randint(10, 20)
                                girl.exp += exp

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
                                girlmod["joy"] += choice([0,1,1,2,3])

                            else:
                                girl.health = max(1, girl.health - randint(10, 20))
                                girl.vitality -= randint(10, 20)
                                girl.exp += exp
                                girl.joy += choice([0,1,1,2,3])

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
                                girlmod["joy"] += choice([0,2,2,4,6])

                            else:
                                girl.exp += exp
                                girl.joy += choice([0,2,2,4,6])

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
                                girlmod["joy"] -= choice([0,1,1,2,3])

                            else:
                                girl.health = max(1, girl.health - randint(10, 20))
                                girl.joy -= choice([0,1,1,2,3])

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
                                girlmod["joy"] += choice([0,1,1,2,3])

                            else:
                                girlmod.vitality -= randint(10, 20)
                                girlmod.exp += exp
                                girl.joy += choice([0,1,1,2,3])

                            return False, self.FOUGHT

            else:
                return False

        def get_look_around_girl(self, event):
            """
            Gets the girl for the event.
            event = The event to return the girl for.
            """
            return self.look_cache.pop(event.name, None)

        def get_price(self):
            """
            Returns the price to retieve the girl.
            """
            # In case non-slaves escape, use 3000 as base price
            base = self.girl.fin.get_price() or 3000
            time = float(self.jail_cache[self.girl][0])
            return int(base * (.75 - (.125 * time)))

        def get_upkeep(self):
            """
            Return the upkeep cost for the girl.
            """
            return self.girl.fin.get_upkeep()

        @property
        def chars_list(self):
            """
            The list to use for the slavemarket interface.
            """
            if self.jail_cache: return self.jail_cache.keys()
            else: return []

        def location_runaway(self, location, sutree=None):
            """
            Returns a runaway chance for the location.
            location = The location to calculate the chance for.
            sutree = The name of the security upgrade tree to use if not default.

            Calculates the chance using:
            - The mod_runaway function if it exists.
            - The sutree current / total, if it exists.
            - The amount of guards in the location, if the action exists.
            - The amount of warriors in the location

            Returns:
            0 = high chance.
            1 = low chance
            """
            # Get runaway modifier
            mod = 0

            # If location has own function, use it # TODO check upgrades
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
            type = "schoolndreport"
            txt = ["Escaped girls:"]

            # Replace with better code to prevent mass-creation/destruction of events?
            # Clean look_cache
            for i in self.look_cache.keys():
                pytfall.world_events.kill_event(i, cached=True)
                del self.look_cache[i]

            # Clean jail_cache
            for i in self.jail_cache.keys():
                if self.jail_cache[i][0] == 0:
                    del self.jail_cache[i]

                else:
                    self.jail_cache[i][0] -= 1

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
                if cdb: txt.append("{color=[blue]}        status: %s{/color}"%status)

                # If girl is free
                if girl not in self.jail_cache:
                    # Chance to escape for good
                    if girl_away_days > 20:
                        if dice(status) and dice(girl_away_days):
                            del self.girls[girl]
                            hero.remove_char(girl)

                            if cdb: txt.append("{color=[blue]}        escaped for good{/color}")
                            continue

                    # Chance to go to jail
                    if girl_away_days > 10:
                        if dice(status) and len(self.jail_cache) < 10:
                            self.jail_cache[girl] = [4, False]

                            if cdb: txt.append("{color=[blue]}        sent to jail for 4 days (%s days till escape){/color}"%(20-girl_away_days))
                            continue

                    # Chance to find in look_around
                    if dice(status) and len(self.look_cache) < 5:
                        ev = "runaway_look_around_%s"%str(girl)
                        self.look_cache[ev] = girl
                        # Add event for girl (do we want high priority?)
                        register_event_in_label(ev, label=girl.runaway_look_event, trigger_type="look_around", locations=["all"], dice=status, max_runs=1, start_day=day+1, priority=999)

                        if cdb: txt.append("{color=[blue]}        in look around (%s days till escape){/color}"%(20-girl_away_days))
                        continue

                    if cdb: txt.append("{color=[blue]}        %s days till escape{/color}"%(20-girl_away_days))

                # Else if girl is jailed
                else:
                    # If we know they're in jail
                    if self.jail_cache[girl][1]:
                        txt.append("    %s, in jail for %s days"%(girl.fullname, self.jail_cache[girl][0]))
                        if cdb: txt.append("{color=[blue]}    (%s days till escape){/color}"%(20-girl_away_days))

                    # Else
                    else:
                        txt.append("    %s"%girl.fullname)
                        if cdb: txt.append("{color=[blue]}        in jail for %s days (%s days till escape){/color}"%(self.jail_cache[girl], (20-girl_away_days)))

            # Slavemarket update
            self.index = 0
            if self.jail_cache:
                self.girl = self.chars_list[0]

            # If we have escaped girls, post the event
            if self.girls:
                ev = NDEvent()
                ev.type = type
                ev.char = None
                ev.img = im.Scale("content/gfx/bg/locations/dungeoncell.webp", int(config.screen_width*.6), int(config.screen_height*.8))
                ev.txt = "\n".join(txt)
                NextDayEvents.append(ev)

        def next_index(self):
            """
            Sets the next index for the slavemarket.
            """
            self.index = (self.index+1) % len(self.chars_list)
            self.girl = self.chars_list[self.index]

        def previous_index(self):
            """
            Sets the previous index for the slavemarket.
            """
            self.index = (self.index-1) % len(self.chars_list)
            self.girl = self.chars_list[self.index]

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

                if girl in self.jail_cache:
                    del self.jail_cache[girl]

                    if self.jail_cache:
                        self.index %= len(self.jail_cache)
                        self.girl = self.chars_list[self.index]

                    else:
                        self.index = 0
                        self.girl = None

                if girl.status == "slave":
                    girl.home = pytfall.streets 
                else:
                    girl.home = pytfall.city
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
