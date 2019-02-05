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
                if hero.take_money(self.get_price(), reason="Slave Purchase"):
                    renpy.play("content/sfx/sound/world/purchase_1.ogg")
                    hero.add_char(girl)
                    girl.action = girl.workplace = None
                    girl.home = pytfall.streets
                    girl.set_location(girl, None)
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
                    girl.home = pytfall.streets
                    set_location(girl, None)
                    girl.action = None
                    girl.workplace = None

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
            set_location(girl, pytfall.sm)
            girl.action = None
            girl.workplace = None

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

    class Building(BaseBuilding):
        """
        The building that represents Business Buildings.
        """
        WORKER_RULES = ["strict", "normal", "loose"]
        WORKER_RULES_DESC = {
            "strict": "Workers will only preform jobs that are the exact match to the action you're assigned them!",
            "normal": "Workers may choose to do a job that directly matches to their class if they are not busy otherwise!",
            "loose": "Workers may choose to do a job that is at least loosely matches to their class if they are not busy otherwise! (for example a Stripper doing a Whore Job)"
        }

        DIRT_STATES = ("Immaculate", "Sterile", "Spotless", "Clean", "Tidy",
                       "Messy", "Dirty", "Grimy", "Filthy", "Disgusting")

        def __init__(self):
            """
            Creates a new Building.
            # maxrank = The maximum rank this brothel can achieve.
            """
            super(Building, self).__init__()

            self.tier = 0
            self.rooms = 0

            self._upgrades = list()
            self.allowed_upgrades = []
            self._businesses = list()
            self.allowed_businesses = []

            # We add allowed BUs here, for businesses that have not been built yet.
            # { business: ["u1", "u2", ...]}
            self.allowed_business_upgrades = {}

            self.fin = Finances(self)

            # And new style upgrades:
            self.in_slots = 0 # Interior Slots
            self.in_slots_max = 0
            self.ex_slots = 0 # Exterior Slots
            self.ex_slots_max = 0

            # Optional inventory - initialized later
            #self.given_items = dict()
            #self.inventory = Inventory(15)

            # Clients:
            self.all_clients = list() # All clients of this building are maintained here.
            self.regular_clients = set() # Subset of self.all_clients.
            self.clients = list() # temp clients, this is used during SimPy cals and reset on when that ends.
            # This is the amount of clients that will visit the Building:
            self.clients_regen_day = 0

            # Management:
            # Note: We also use .inhabitants set inherited from all the way over location.
            self.manager = None
            self.manager_effectiveness = 0 # Calculated once at start of each working day (performance)
            self.workers_rule = "normal"
            self.init_pep_talk = True
            self.cheering_up = True
            self.asks_clients_to_wait = True
            self.help_ineffective_workers = True # Bad performance still may get a payout.
            self.works_other_jobs = False
            # TODO Before some major release that breaks saves, move manager and effectiveness fields here.
            self.mlog = None # Manager job log

            # Workers:
            # Bit of an issue could be that we're using all_workers in SimPy as well? :D
            # TODO (bb) Look into the above.
            self.all_workers = list() # All workers presently assigned to work in this building.
            self.available_workers = list() # This is built and used during the next day (SimPy).

            # Upgrades:
            self.nd_ups = list() # Upgrades active during the next day...

            # SimPy and etc follows:
            self.env = None

            self.adverts = []

            # Dirt/Threat
            self.maxdirt = 1000
            self.dirt = 0
            self.maxthreat = 1000
            self.threat = 0
            #self.threat_mod = 5 initialized later
            self.auto_clean = 100

            # Fame/Reputation
            self.minfame = 0 # The minimum amount of fame the building can have.
            self.maxfame = 0 # The maximum amount of fame the building can have.
            self.fame = 0    # The current fame of the building

            self.minrep = 0 # The minimum amount of reputation the building can have.
            self.maxrep = 0 # The maximum amount of reputation the building can have.
            self.rep = 0    # The current reputation of the building

            # Logging stat changes during the day:
            self.stats_log = OrderedDict()

            # ND Report
            self.nd_events_report = list()

        def init(self):
            self.normalize_jobs()

            if not hasattr(self, "threat_mod"):
                if self.location == "Flee Bottom":
                    self.threat_mod = 5
                elif self.location == "Midtown":
                    self.threat_mod = 2
                elif self.location == "Richford":
                    self.threat_mod = -1
                else:
                    devlog.warn("{} Building with an unknown location detected!".format(self.name))

            if hasattr(self, "inventory"):
                if bool(self.inventory):
                    self.inventory = Inventory(15)
                    self.given_items = dict()
                    # Once again, for the Items transfer:
                    self.status = "slave"
                else:
                    del self.inventory

        def normalize_jobs(self):
            jobs = set()
            for up in self._businesses:
                jobs.update(up.jobs)
            self.jobs = jobs

        def get_valid_jobs(self, char):
            """Returns a list of jobs available for the building that the character might be willing to do.

            Returns an empty list if no jobs is available for the character.
            """
            jobs = []

            for job in self.jobs:
                # We need to check if there are any slots for a worker are left (atm only the Manager job):
                if job.id == "Manager":
                    # we get a list of all workers that are assigned for this job:
                    temp = [w for w in self.all_workers if w.action == job or w.previousaction == job]
                    # This isn't bulletproof... we prolly want to access building.manager here...
                    if temp:
                        continue
                if job.is_valid_for(char):
                    jobs.append(job)

            return jobs

        def get_extension_cost(self, extension, **ec_kwargs):
            # We figure out what it would take to add this extension (building or business)
            # using it's class attributes to figure out the cost and the materials required.
            tier = self.tier or 1

            if isclass(extension):
                ext = extension(**ec_kwargs)
            else:
                ext = extension
            if ext.building is None:
                ext.building = self

            cap = ext.capacity

            cost = ext.get_price()

            materials = ext.materials.copy()
            for k, v in materials.items():
                materials[k] = round_int(v*min(tier, 4))

            in_slots = ext.in_slots + cap*ext.exp_cap_in_slots
            ex_slots = ext.ex_slots + cap*ext.exp_cap_ex_slots

            return cost, materials, in_slots, ex_slots

        def eval_extension_build(self, extension_class, price=None):
            # If price is not None, we expect a tuple with requirements to build
            # Check if we can build an upgrade:
            if price is None:
                cost, materials, in_slots, ex_slots = self.get_extension_cost(extension_class)
            else:
                cost, materials, in_slots, ex_slots = price

            if (self.in_slots_max - self.in_slots) < in_slots or (self.ex_slots_max - self.ex_slots) < ex_slots:
                return False

            if self.has_extension(extension_class):
                return False

            if hero.gold < cost:
                return False

            for i, a in materials.iteritems():
                if hero.inventory[i] < a:
                    return False

            return True

        def pay_for_extension(self, cost, materials):
            # This does assume that we checked and know that MC has the resources.
            if cost:
                hero.take_money(cost, "Building Upgrades")
                self.fin.log_logical_expense(cost, "Upgrade")

            if materials:
                for item, amount in materials.items():
                    hero.remove_item(item, amount)

        def add_business(self, business, normalize_jobs=False, pay=False):
            """Add business to the building.
            """
            cost, materials, in_slots, ex_slots = self.get_extension_cost(business)
            self.in_slots += in_slots
            self.ex_slots += ex_slots

            if pay:
                self.pay_for_extension(cost, materials)

            business.building = self
            business.in_slots = in_slots
            business.ex_slots = ex_slots

            self._businesses.append(business)
            self._businesses.sort(key=attrgetter("SORTING_ORDER"), reverse=True)

            # Add possible upgrades:
            cls_name = business.__class__.__name__
            upgrades = self.allowed_business_upgrades.get(cls_name, None)
            if upgrades is not None:
                for u in upgrades:
                    u = getattr(store, u)
                    if u not in business.allowed_upgrades:
                        business.allowed_upgrades.append(u)

            if normalize_jobs:
                self.normalize_jobs()

        def close_business(self, business, normalize_jobs=False, pay=False):
            """Remove a business from the building.
            """
            self._businesses.remove(business)
            self.in_slots -= business.in_slots
            self.ex_slots -= business.ex_slots

            if pay:
                self.pay_for_extension(business.get_price(), None)

            if normalize_jobs:
                self.normalize_jobs()

        def add_upgrade(self, upgrade, pay=False):
            cost, materials, in_slots, ex_slots = self.get_extension_cost(upgrade)
            self.in_slots += in_slots
            self.ex_slots += ex_slots

            if pay:
                self.pay_for_extension(cost, materials)

            upgrade.building = self
            self._upgrades.append(upgrade)
            self._upgrades.sort(key=attrgetter("SORTING_ORDER"), reverse=True)

        def all_possible_extensions(self):
            # Returns a list of all possible extensions (businesses and upgrades)
            return self.allowed_businesses + self.allowed_upgrades

        def all_extensions(self):
            return self._businesses + self._upgrades

        def has_extension(self, extension, include_business_upgrades=False):
            if not isclass(extension):
                extension = extension.__class__

            for ex in self.all_extensions():
                if isinstance(ex, extension):
                    return True

            if include_business_upgrades:
                for ex in self.all_extensions():
                    if ex.has_extension(extension):
                        return True

            return False

        def get_business(self, up):
            # Takes a string as an argument
            if up == "fg":
                temp = [u for u in building._businesses if u.__class__ == ExplorationGuild]
                if temp:
                    return temp[0]
                else:
                    return False

        # Describing building purposes:
        def is_business(self):
            return len(self.allowed_businesses) != 0

        @property
        def habitable(self):
            # Overloads property of Location core class to serve the building.
            return self.rooms != 0 or any(i.habitable for i in self._businesses)

        @property
        def workable(self):
            """Returns True if this building has upgrades that are businesses.
            """
            return any(i.workable for i in self._businesses)

        @property
        def vacancies(self):
            return self.habitable_capacity - len(self.inhabitants)

        @property
        def workable_capacity(self):
            capacity = 0
            for i in self._businesses:
                if i.workable:
                    capacity += i.capacity
            return capacity

        @property
        def habitable_capacity(self):
            capacity = self.rooms
            for i in self._businesses:
                if i.habitable:
                    capacity += i.capacity
            return capacity

        @property
        def capacity(self):
            # Full capacity, habitable and workable:
            return self.workable_capacity + self.habitable_capacity

        # Gui/Controls:
        # Mimicking the show method expected from character classes for items transfer:
        def show(self, *tags, **kwargs):
            size = kwargs.get("resize", (205, 205))
            return ProportionalScale(self.img, size[0], size[1])

        def toggle_workers_rule(self):
            index = self.WORKER_RULES.index(self.workers_rule)
            index = (index + 1) % len(self.WORKER_RULES)

            self.workers_rule = self.WORKER_RULES[index]

        def get_cleaning_price(self):
            """
            How much it costs to clean this building.
            """
            return 10 + 2*self.dirt

        def get_threat_percentage(self):
            """
            Returns percentage of dirt in the building as (percent, description).
            """
            return self.threat * 100 / self.maxthreat

        def get_dirt_percentage(self):
            """
            Returns percentage of dirt in the building as (percent, description).
            """
            dirt = self.dirt * 100 / self.maxdirt
            dirt_string = self.DIRT_STATES[min(9, dirt/10)]

            return dirt, dirt_string

        @property
        def fame_percentage(self):
            return self.fame*100/max(1, self.maxfame)

        @property
        def rep_percentage(self):
            return self.rep*100/max(1, self.maxrep)

        def moddirt(self, value):
            # Ignore dirt for small buildings!
            cap = getattr(self, "workable_capacity", 0)

            if self.manager_effectiveness >= 100 and cap <= 15:
                value = 0
            elif cap <= 10:
                value = 0
            else:
                value += self.dirt
                if value > self.maxdirt:
                    value = self.maxdirt
                elif value < 0:
                    value = 0
            self.dirt = value

        def modthreat(self, value):
            # Ignore threat for small buildings!
            cap = getattr(self, "workable_capacity", 0)

            if self.manager_effectiveness >= 100 and cap <= 20:
                value = 0
            elif cap <= 15:
                value = 0
            else:
                value += self.threat
                if value > self.maxthreat:
                    value = self.maxthreat
                elif value < 0:
                    value = 0

            self.threat = value

        def modfame(self, value):
            """
            Changes how famous this building is.
            value = The amount to change.
            """
            value += self.fame
            if value > self.maxfame:
                value = self.maxfame
            elif value < self.minfame:
                value = self.minfame
            self.fame = value

        def modrep(self, value):
            """
            Changes how reputable this building is.
            value = The amount to change.
            """
            value += self.rep
            if value > self.maxrep:
                value = self.maxrep
            elif value < self.minrep:
                value = self.minrep
            self.rep = value

        @property
        def mjp(self):
            if self.manager:
                return self.manager.jobpoints
            else:
                return 0
        @mjp.setter
        def mjp(self, value):
            if self.manager:
                self.manager.jobpoints = value

        # Clients related:
        def get_client_count(self, write_to_nd=False):
            """Get the amount of clients that will visit the building the next day.

            Weakness of this method atm is this:
                We only get 70% of total possible clients from businesses,
                    to make extensions meaningful.
                We do not make any distinctions between businesses we generate clients for.
                    This makes having businesses that attract loads of clients
                    hugely favorable to have when running a business that does not.
            """

            min_clients = 0
            for a in self.adverts:
                if a['active']:
                    min_clients += a.get('client', 0)

            clients = 0
            # Generated by upgrades:
            for u in [u for u in self._businesses if u.expects_clients]:
                clients += u.get_client_count()
                if DSNBR:
                    devlog.info("{} pure clients for {}".format(u.get_client_count(), u.name))

            # Fame percentage mod (linear scale):
            mod = self.fame_percentage / 100.0

            # Special check for larger buildings:
            if mod > 80 and self.maxfame > 400:
                if write_to_nd:
                    self.log("Extra clients are coming in! You business is getting very popular with the people")
                mod *= 1.1

            # Upgrades:
            temp = False
            for u in self._upgrades:
                um = getattr(u, "client_flow_mod", 0)
                if um != 0:
                    temp = True
                    mod *= um
            if temp and write_to_nd:
                self.log("Your building upgrades are attracting extra clients!")

            # Normalize everything:
            clients = min(min_clients + round_int(clients * mod), clients)

            if write_to_nd:
                if clients != 0:
                    self.log("Total of {} clients are expected to visit this establishment!".format(set_font_color(clients, "lawngreen")))
                else:
                    self.log("{}".format(set_font_color("You may want to put up a sign!\n", "red")))
                    self.flag_red =  True

            return clients

        def get_max_client_capacity(self):
            """Returns the very maximum amount of clients this building can host
                at any given time. This is used in a number of ND-calculations.
            """
            capacity = 0
            for u in self._businesses:
                if u.expects_clients:
                    capacity += u.capacity
            return capacity

        @property
        def expects_clients(self):
            return any(i.expects_clients for i in self._businesses)

        def create_customer(self, name="", likes=None):
            """
            Returns a customer for this Building.
            If name is an empty string, a random customer is returned.
            If name is given, the returning customer with that name is returned
            by this method. A NameError will be raised if the given name is not
            associated with a returning customer.
            """
            if name:
                raise NotImplementedError("Returning customers are not implemented yet")

            # determine gender of random customer
            gender = "male" if dice(75) else "female"

            # determine caste of random customer
            caste = randint(0, 2)
            if self.rep < 50: caste = max(caste, 1)
            elif self.rep <= 150: caste += 1
            elif self.rep <= 400: caste += 2
            elif self.rep <= 600: caste += 3
            elif self.rep <= 800: caste += 4
            else:                 caste += 5
            caste = CLIENT_CASTES[caste]

            # create random customer
            min_tier = float(max(self.tier-2, .1))
            max_tier = float(self.tier + 1)
            customer = build_client(gender=gender, caste=caste,
                                    tier=uniform(min_tier, max_tier),
                                    likes=likes)
            return customer

        # SimPy/Working the building related:
        def run_nd(self):
            """This method is ran for buildings during next day
            - Gets list of workable businesses and available workers
            - Creates SimPy Environment
            """
            tl.start("{}.run_nd (SimPy/Clients, etc.)".format(self.name))
            # Setup and start the simulation
            self.flag_red = False

            temp = "{} General Report:".format(self.name)
            self.log("{}".format(set_font_color(temp, "lawngreen")))
            self.log("")

            # Get businesses we wish SimPy to manage! business_manager method is expected here.
            self.nd_ups = list(up for up in self._businesses if up.workable)

            client_businesses = list(up for up in self._businesses if up.expects_clients)
            if client_businesses:
                self.all_workers = self.get_workers()

                # All workers and workable businesses:
                # This basically roots out Resting/None chars!
                self.available_workers = list(c for c in self.all_workers if
                                              c.action in self.jobs)
                for w in self.all_workers:
                    convert_ap_to_jp(w)
                    # And AEQ
                    if isinstance(w.action, Job):
                        w.action.auto_equip(w)

                # Clients:
                tl.start("Generating clients in {}".format(self.name))
                total_clients = self.get_client_count(write_to_nd=True)

                # Note (Beta): currently all clients are regulars
                # remove maximum of 100 clients at a time (better perfomance, closer to RL)
                if self.clients_regen_day <= day:
                    clients = self.all_clients
                    num = len(clients)
                    to_remove = min(num/2, 100)
                    idx = randint(0, num-to_remove)
                    self.all_clients = clients[0:idx]+clients[idx+to_remove:num]
                    # TODO make the remaining clients regulars?!
                    self.clients_regen_day = day + randint(2, 4)

                # update all_clients (and clients) based on the new expectations
                clnts = total_clients - len(self.all_clients)
                if clnts > 0:
                    for i in xrange(clnts):
                        client = self.create_customer(likes=[choice(client_businesses)])
                        self.all_clients.append(client)
                elif clnts < 0:
                    # something happened to the building(downsized/reputation-hit/etc...) -> it it time that the clients react to it
                    clients = self.all_clients
                    num = len(clients)
                    to_remove = -clnts/2
                    idx = randint(0, num-to_remove)
                    self.all_clients = clients[0:idx]+clients[idx+to_remove:num]

                self.clients = self.all_clients[:]

                tl.end("Generating clients in {}".format(self.name))

            if self.nd_ups or client_businesses:
                # Building Stats:
                self.log("")
                self.log("Reputation: {}%".format(self.rep_percentage))
                self.log("Fame: {}%".format(self.fame_percentage))
                self.log("Dirt: {}%".format(self.get_dirt_percentage()[0]))
                self.log("Threat: {}%".format(self.get_threat_percentage()))

                self.log("")
                # We can calculate manager effectiveness once, so we don't have to do
                # expensive calculations 10 000 000 times:
                if self.manager:
                    job = simple_jobs["Manager"]
                    self.manager_effectiveness = job.effectiveness(self.manager,
                                                    self.tier, None, False)
                    self.log("This building is managed by {} at {}% effectiveness!".format(
                                self.manager.name, self.manager_effectiveness
                    ))
                else:
                    self.log("This building has no manager assigned to it.")
                    self.manager_effectiveness = 0
                self.log("")

                self.log("{}".format(set_font_color("Starting the workday:", "lawngreen")))
                # Create an environment and start the setup process:
                self.env = simpy.Environment()
                for up in self._businesses:
                    up.pre_nd()

                # We run till 110 DU and should attempt to stop all businesses at 100.
                proc = self.env.process(self.building_manager(end=111))

                self.env.run(until=proc)
                self.log("{}".format(set_font_color("Ending the workday.", "green")))

                # Building Stats:
                self.log("Reputation: {}%".format(self.rep_percentage))
                self.log("Fame: {}%".format(self.fame_percentage))
                self.log("Dirt: {}%".format(self.get_dirt_percentage()[0]))
                self.log("Threat: {}%".format(self.get_threat_percentage()))

                income = self.fin.get_logical_income()
                if income > 0:
                    self.log("\nA total of {} Gold was earned here today!".format(set_font_color(str(income), "lawngreen")))
                elif income < 0:
                    self.log("\nYou are losing money with this business! After the night your pockets are lighter with {} Gold".format(set_font_color(str(-income), "red")))
                self.log("{}".format(set_font_color("===================", "lawngreen")))

                # finish the business by resetting the variables
                for c in self.all_clients:
                    for f in c.flags.keys():
                        if f.startswith("jobs"):
                            c.del_flag(f)

                # Uncomment when we allow inter-building actions...
                #self.manager_effectiveness = 0

                for up in self._businesses:
                    up.post_nd()

                self.nd_ups = list()
                self.env = None
            else:
                self.log(set_font_color("===================", "lawngreen"))
                self.log("This is a residential building. Nothing much happened here today.")

            tl.end("{}.run_nd (SimPy/Clients, etc.)".format(self.name))

        def building_manager(self, end):
            """This is the main process that manages everything that is happening in the building!
            """
            env = self.env

            # Run the manager process:
            if self.manager:
                init_jp = self.manager.jobpoints
                self.mlog = NDEvent(job=simple_jobs["Manager"], char=self.manager, loc=self)
                env.process(manager_process(env, self))

            for u in self.nd_ups:
                # Trigger all public businesses:
                if u.active:  # Business as usual:
                    env.process(u.business_control())
                else: # inactive business
                    env.process(self.inactive_process())

                if u.has_workers():
                    u.is_running = True

            if self.clients:
                env.process(self.clients_dispatcher(end=end-10))

            for u in self._upgrades:
                if isinstance(u, Garden):
                    has_garden = True
                    break
            else:
                has_garden = False

            while (1):
                temp = "\n{color=[green]}%d =========>>>{/color}" % (env.now)
                self.log(temp)
                yield env.timeout(1)
                simpy_debug("%s DU Executing =====================>>>", env.now)

                # Delete the line if nothing happened on this turn:
                if self.nd_events_report[-1] == temp:
                    del self.nd_events_report[-1]

                if env.now >= end:
                    break
                if not env.now % 25:
                    self.moddirt(5) # 5 dirt each 25 turns even if nothing is happening.
                    self.modthreat(self.threat_mod)

                    if has_garden and dice(25):
                        for w in self.all_workers:
                            w.joy += 1

            # post-process of the manager
            if self.manager:
                log = self.mlog
                manager = self.manager
                points_used = init_jp - manager.jobpoints

                # Handle stats:
                if points_used > 0:
                    if points_used > 100:
                        log.logws("management", randint(1, 2))
                        log.logws("intelligence", randrange(2))
                        log.logws("refinement", 1)
                        log.logws("character", 1)
 
                    ap_used = (points_used)/100.0
                    log.logws("exp", exp_reward(manager, self.tier, ap_used=ap_used))

                # finalize the log:
                log.img = manager.show("profile", resize=ND_IMAGE_SIZE, add_mood=True)
                log.type = "manager_report"
                log.after_job()

                NextDayEvents.append(log)
                self.mlog = None

        def clients_dispatcher(self, end):
            """This method provides stream of clients to the building following it's own algorithm.

            We want 50% of all clients to come in the 'rush hour' (turn 50 - 80).
            """
            expected = len(self.clients)
            running = 0

            for u in self._upgrades:
                if isinstance(u, Garden):
                    has_garden = True
                    break
            else:
                has_garden = False

            # We do not want to add clients at the last 5 - 10 turns...
            # So we use 90 as base.
            normal_step = expected*.5/60
            rush_hour_step = expected*.5/30

            while (1):
                simpy_debug("Entering PublicBusiness(%s).client_dispatcher iteration at %s", self.name, self.env.now)

                if self.env.now >= end:
                    break
                if 50 <= self.env.now <= 80:
                    running += rush_hour_step
                else:
                    running += normal_step

                if running >= 1:
                    add_clients = round_int(running)
                    running -= add_clients

                    for i in range(add_clients):
                        if not self.clients:
                            break
                        client = self.clients.pop()
                        self.env.process(self.client_manager(client, has_garden=has_garden))
                    if not self.clients:
                        break

                if DSNBR:
                    devlog.info("Client Distribution running: {}".format(running))
                simpy_debug("Exiting PublicBusiness(%s).client_dispatcher iteration at %s", self.name, self.env.now)
                yield self.env.timeout(1)

        def client_manager(self, client, has_garden=False):
            """Manages a client using SimPy.

            - Picks a business
            - Tries other businesses if the original choice fails
            - Kicks the client if all fails

            So this basically sends the client into the businesses within this building or keeps them waiting/rotating.
            Once in, client is handled and managed by the Business itself until control is returned here!
            Once this method is terminated, client has completely left the building!
            """
            # Register the fact that client arrived at the building:
            temp = '{} arrives at the {}.'.format(
                        set_font_color(client.name, "beige"), self.name)
            self.log(temp, True)

            if self.dirt >= 800:
                yield self.env.timeout(1)
                temp = "Your building is as clean a pig stall. {} storms right out.".format(client.name)
                self.log(temp)
                self.env.exit()
            if self.threat >= 800:
                yield self.env.timeout(1)
                temp = "Your building is as safe as a warzone. {} ran away.".format(client.name)
                self.log(temp)
                self.env.exit()

            # Client threat mod:
            if "Aggressive" in client.traits:
                self.modthreat(2 if has_garden else 3)

            # Visit counter:
            client.up_counter("visited_building" + str(self.id))

            # Prepare data:
            businesses = [b for b in self.nd_ups if b.expects_clients]
            shuffle(businesses)

            fav_business = client.likes.intersection(self._businesses)

            # Case where clients fav business was removed from the building, client to react appropriately.
            if not fav_business:
                self.all_clients.remove(client)
                temp = "{}: {} storms out of the building pissed off as his favorite business was removed!".format(
                                        self.env.now, set_font_color(client.name, "beige"))
                self.log(temp)
                self.env.exit()
            else:
                fav_business = fav_business.pop()

            visited = 0 # Amount of businesses client has successfully visited.
            while businesses:
                # Here we pick an upgrade if a client has one in preferences:
                if not visited and fav_business in businesses:
                    # On the first run we'd want to pick the clients fav.
                    business = fav_business
                    businesses.remove(business)
                else:
                    business = businesses.pop()

                # Manager active effect:
                # Wait for the business to open in case of a favorite:
                if self.manager and self.asks_clients_to_wait and all([
                        self.manager.jobpoints >= 1,
                        (business == fav_business),
                        (business.res.count >= business.capacity),
                        self.env.now < 85]):
                    wait_till = min(self.env.now + 7, 85)
                    temp = "Your manager convinced {} to wait till {} for a slot in {} favorite {} to open up!".format(
                                    set_font_color(client.name, "beige"), wait_till, client.op, fav_business.name)
                    self.log(temp)

                    self.mlog.append("\nAsked a client to wait for a spot in {} to open up!".format(fav_business.name))

                    self.manager.jobpoints -= 1
                    while (wait_till < self.env.now) and (business.res.count < business.capacity):
                        yield self.env.timeout(1)

                if business.type == "personal_service" and business.res.count < business.capacity:
                    # Personal Service (Brothel-like):
                    job = business.job
                    workers = business.get_workers(job, amount=1, match_to_client=client)

                    if not workers:
                        continue # Send to the next update.
                    else:
                        # We presently work just with the one char only, so:
                        worker = workers.pop()
                        if worker in self.available_workers:
                            self.available_workers.remove(worker)

                        # We bind the process to a flag and wait until it is interrupted:
                        visited += 1
                        self.env.process(business.request_resource(client, worker))
                        client.set_flag("jobs_busy")
                        while client.flag("jobs_busy"):
                            yield self.env.timeout(1)
                # Jobs like the Club:
                elif business.type == "public_service" and business.res.count < business.capacity:
                    self.env.process(business.client_control(client))
                    visited += 1
                    client.set_flag("jobs_busy")
                    while client.flag("jobs_busy"):
                        yield self.env.timeout(1)

            if not visited:
                temp = "There is not much for the {} to do...".format(set_font_color(client.name, "beige"))
                self.log(temp)
                temp = "So {} leaves your establishment cursing...".format(set_font_color(client.name, "beige"))
                self.log(temp)
                self.env.exit()
            else:
                temp = '{} is leaving after visiting {} business(es).'.format(set_font_color(client.name, "beige"), visited)
                self.log(temp)

        def nd_log_stats(self):
            # Get a list of stats, usually all 4.
            new_stats = OrderedDict()
            stats = []
            if self.maxdirt != 0:
                stats.append("dirt")
            if self.maxthreat != 0:
                stats.append("threat")
            if self.maxfame != 0:
                stats.append("fame")
            if self.maxrep != 0:
                stats.append("rep")
            stats_log = self.stats_log
            for stat in stats:
                val = getattr(self, stat)
                new_stats[stat] = val
                # Do not run the very first time:
                if stats_log:
                    stats_log[stat] = val - stats_log[stat]

            self.stats_log = new_stats
            return stats_log

        def next_day(self):
            """
            Solves the next day logic for the Building.
            """
            self.run_nd() # simulate the business

            # Local vars
            txt = self.nd_events_report

            tmodrep = 0 # Total of rep changed on next day, girl's mod are not included here.
            tmodfame = 0 # Total of fame, same rules.
            spentcash = 0

            # Applies effects of advertisements:
            for advert in self.adverts:
                if advert['active']:
                    if 'fame' in advert:
                        modf = randint(*advert['fame'])
                        self.modfame(modf)
                        tmodfame += modf
                    if 'reputation' in advert:
                        modr = randint(*advert['reputation'])
                        self.modrep(modr)
                        tmodrep += modr

                    spentcash += advert['upkeep']
                    if advert.get('unique', False):
                        advert['active'] = False

            if spentcash or tmodfame or tmodrep:
                txt.append("In total you got a bill of %d Gold in advertising fees, reputation was increased through advertising by %d, fame by %d." % (spentcash, tmodrep, tmodfame))

                if spentcash and not hero.take_money(spentcash, reason="Building Ads"):
                    rep_hit = max(10, spentcash/10)
                    self.modrep(-rep_hit)
                    txt.append("{color=[red]}And yet, you did not have enough money to pay your advertisers! They took it out on you by promoting %s as a shitty dump...{/color}" % self.name)
                    self.flag_red = True

                self.fin.log_logical_expense(spentcash, "Ads")

            locmod = self.nd_log_stats()

            evt = NDEvent(type='buildingreport',
                          img=self.img,
                          txt = txt,
                          loc = self,
                          locmod = locmod,
                          red_flag = self.flag_red)
            NextDayEvents.append(evt)

            self.nd_events_report = list()

        def log(self, item, add_time=False):
            # Logs the item (text) to the Building log...
            # if add_time and self.env:
            #     item = "{}: ".format(self.env.now) + item
            self.nd_events_report.append(item)
            if DSNBR:
                devlog.info(item)

        def nd_log_income(self):
            """
            Log the next day income for this building.
            """
            self.fin.next_day()
