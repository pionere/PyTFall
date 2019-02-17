init -10 python:
    #################################################################
    # CORE BUILDING CLASSES
    # BaseBuilding = Base class, needed if no other.
    #
    # Examples:
    # class CityJail(Building): <-- Just a building
    #
    """Core order for SimPy jobs loop:
    ***Needs update after restructuring/renaming.

    BUILDING:
        # Holds Businesses and data/properties required for operation.
        run_nd():
            # Setups and starts the simulation.
            *Generates Clients if required.
            *Builds worker lists.
            *Logs the init data to the building report.
            *Runs pre_day for all businesses.
            *Creates SimPy Environment and runs it (run_jobs being the main controlling process)
            *Runs the post_nd.
        building_manager():
            SimPy process that manages the building as a whole.
            # Main controller for all businesses.
            *Builds a list of all workable businesses.
            *Starts business_manager for each building.
        clients_manager():
            SimPy Process that supplies clients to the businesses within the building as required.
            *Adds a steady/conditioned stream of clients to the appropriate businesses and manages that stream:
            *Kicks clients if nothing could be arranged for them.

    BUSINESS:
        # Hold all data/methods required for business to operate.
        *Personal Service:
            - Finds best client match using update.get_workers()
            - Runs the job.
        *Public Service:
            - Simply sends client to business.
            - Sends in Workers to serve/entertain the clients.
        *OnDemand Service:
            - Includes some form of "on demand" service, like cleaning or guarding (defending).
            - May also have a continued, "automatic" service like Guard-patrol.

        *workers = On duty characters.
        *habitable/workable = self-explanotory.
        *clients = clients used locally (maybe useful only for the public service?)
        *capacity = cap of the building such as amount of rooms/workspace.
        *jobs = only for businesses
        *get_workers:
            - Checks if a char is capable.
            - Checks if a char is willing.
            - Can also try to match find the best client for the job.

        # This may be obsolete after refactoring... to be rewritten or deleted after a steady system is in place.
        SimPy Land:
            *res = Resource
            *time = cycle
            *is_running = May be useless

        *Personal Service:
            *find_best_match = finds a best client/worker combination.
            *request_resource:
                - requests a room for worker/client.
                - adds a run_job process to Env
                - logs it all to building log
            *run_job:
                - Waits for self.time delay
                - Calls the job so it can form an NDEvent

        *Public Service:
            *active_workers = Does this not simply double the normal workers?
            *request = plainly adds a client and keeps it in the business based on "ready_to_leave" flag set directly to the client.
            *add_worker:
                # Adds workers to business to serve clients.
                - Checks willingness to do the job.
                - Adds workers as required.
                - self.env.process(self.worker_control(worker)) Possible the most important part, this adds a process to Env.
                - Removes worker from building in order to reserve her for this business
            *run_job:
                # main method/SimPy event that manages the job from start to end.
                - Runs for as long there are active workers
                - Waits for self.time delay
                - Manages clients in the business
            *worker_control:
                # Env Process, manages each individual worker.
                - Runs while there are clients and worker has AP in self.time delays.
                - Logs all active clients as flags to a worker.
                - Logs tips to the worker.
                - Runs the Job once AP had been exhausted or there are no more clients availible.
                - Removes the worker from active workers

    Job:
        Has been completely restructured to server as an object to keep track
        of what character is doing what by direct binding and hosting loose
        functions.
    """

    # Core Logic:
    def set_location(actor, loc):
        """This plainly forces a location on an actor.
        """
        actor.location = loc
    class Location(_object):
        """
        Usually a place or a building.
        This simply holds references to actors that are present @ the location.
        If a location is not a member of this class, it is desirable for it to have a similar setup or to be added to change_location() function manually.
        """
        pass # obsolete

    class HabitableLocation(_object):
        """Location where actors can live and modifier for health and items recovery.
        Other Habitable locations can be buildings which mimic this functionality or may inherit from it in the future.
        """
        def __init__(self, id, daily_modifier=.1, desc=""):
            super(HabitableLocation, self).__init__()

            self.id = id
            self.inhabitants = set()
            self.daily_modifier = daily_modifier
            self.desc = desc

        def get_daily_modifier(self):
            return self.daily_modifier

        def __str__(self):
            if hasattr(self, "name"):
                return str(self.name)
            else:
                return str(self.id)

    class InvLocation(HabitableLocation):
        """Location with an inventory:

        Basically, a habitable location where one can store 'stuff'
        Also has a number of extra properties.
        """
        pass # obsolete

    class BaseBuilding(HabitableLocation, Flags):
        """The super class for all Building logic.
        """
        def __init__(self, id=None, name=None, desc=None):
            """Creates a new building.

            id = The id of the building.
            name = The name of the building.
            desc = The description of the building.
            mod = The modifier for the building.
            """
            super(BaseBuilding, self).__init__(id=id)
            Flags.__init__(self)

            self.name = name
            self.desc = desc

            # Flagging:
            self.flag_red = False
            self.flag_green = False

            # Security:

            self.tier = 0

            # Location Default:
            self.location = "Flee Bottom"

            # ND Report
            self.txt = ""

        def __str__(self):
            if self.name:
                return str(self.name)
            return super(BaseBuilding, self).__str__()

        def get_girls(self, action=undefined, occupation=undefined, nott=False):
            """
            The girls that are in this location.
            action = The type of action the girls are doing.
            occupation = The occupation of the girls.
            nott = Whether to negate the selection.

            Note: undefined is used as an alternative to None, as a girl can have no action.
            Used by School, should be refactored out of all modern code now.
            """
            # Get all girls
            if action is undefined:
                g = [girl for girl in hero.chars if girl.workplace is self]

            # Only get girls that (don't) match action list
            elif isinstance(action, (list,tuple)):
                g = [girl for girl in hero.chars if girl.workplace is self and (girl.action in action) != nott]

            # Only get girls that are training
            elif action == "Course":
                g = [girl for girl in hero.chars if girl.workplace is self and isinstance(girl.action, basestring) and girl.action.endswith("Course") != nott]

            # Only get girls with specific action
            else:
                g = [girl for girl in hero.chars if girl.workplace is self and (girl.action == action) != nott]

            # Get all girls
            if occupation is undefined:
                return g

            # Only get girls that (don't) match occupation list
            elif isinstance(occupation, (list,tuple)):
                return [girl for girl in g if [tr for tr in girl.occupations if tr in occupation] != nott]

            # Only get girls with specific occupation
            else:
                return [girl for girl in g if (occupation in girl.occupations) != nott]

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

        def __init__(self):
            """
            Creates a new Building.
            # maxrank = The maximum rank this brothel can achieve.
            """
            super(Building, self).__init__()

            self.tier = 0
            #self.price = 0
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

            # Jobs - initialized later
            #self.jobs = set()

            # Note: We also use .inhabitants set inherited from all the way over location.

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
            if any(b.workable for b in self.allowed_businesses):
                # Management:
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
                self.all_workers = list() # All workers presently assigned to work in this building.
                self.available_workers = list() # This is built and used during the next day (SimPy).

                # Clients:
                self.all_clients = list() # All clients of this building are maintained here.
                self.regular_clients = set() # Subset of self.all_clients.
                self.clients = list() # temp clients, this is used during SimPy cals and reset on when that ends.
                self.clients_regen_day = 0 # The day when the clients are regenerated
                
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

        def get_daily_modifier(self):
            daily_modifier = self.daily_modifier
            for b in self._businesses:
                for u in b.upgrades:
                    if hasattr(u, "daily_modifier_mod"):
                        daily_modifier *= u.daily_modifier_mod
            for u in self._upgrades:
                if hasattr(u, "daily_modifier_mod"):
                    daily_modifier *= u.daily_modifier_mod
            return daily_modifier

        def normalize_jobs(self):
            jobs = set()
            if hasattr(self, "manager"):
                jobs.add(simple_jobs["Manager"])
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
                    if self.manager and char != self.manager:
                        continue
                if job.is_valid_for(char):
                    jobs.append(job)

            return jobs

        def get_price(self):
            # Returns our best guess for price of the Building
            # Needed for buying, selling the building or for taxation.
            # **We may want to take reputation and fame into account as well.
            price = self.price

            for u in self._upgrades:
                price += u.get_price()
            for b in self._businesses:
                price += b.get_price()
            return price

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
            cost, materials, in_slots, ex_slots = business.get_cost()
            self.in_slots += in_slots
            self.ex_slots += ex_slots

            if pay:
                self.pay_for_extension(cost, materials)

            business.in_slots = in_slots
            business.ex_slots = ex_slots

            self._businesses.append(business)
            self._businesses.sort(key=attrgetter("ID"), reverse=True)

            if normalize_jobs:
                self.normalize_jobs()

        def close_business(self, business):
            """Remove a business from the building.
            """
            self._businesses.remove(business)

            self.in_slots -= business.in_slots
            self.ex_slots -= business.ex_slots

            self.pay_for_extension(business.get_cost()[0], None)

            # reset the business
            business.upgrades = list()
            if business.expands_capacity:
                business.in_slots -= business.capacity * business.exp_cap_in_slots
                business.ex_slots -= business.capacity * business.exp_cap_ex_slots
                business.capacity = 0

            # update affected characters
            if business.habitable:
                vacs = self.vacancies
                if vacs < 0:
                    # move out the extra inhabitants
                    for i in range(-vacs):
                        for char in self.inhabitants: break
                        char.home = pytfall.streets

            # inactivate jobless workers
            if hasattr(self, "all_workers"):
                self.normalize_jobs()
                
                for worker in self.all_workers:
                    if worker.get_job() not in self.jobs:
                        worker.set_job(None)

        def add_upgrade(self, upgrade, pay=False):
            cost, materials, in_slots, ex_slots = upgrade.get_cost()
            self.in_slots += in_slots
            self.ex_slots += ex_slots

            if pay:
                self.pay_for_extension(cost, materials)

            self._upgrades.append(upgrade)
            self._upgrades.sort(key=attrgetter("ID"), reverse=True)

        def all_possible_extensions(self):
            # Returns a list of all possible extensions (businesses and upgrades)
            return self.allowed_businesses + self.allowed_upgrades

        def all_extensions(self):
            return self._businesses + self._upgrades

        def has_extension(self, extension):
            return extension in self.all_extensions()

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
            return self.dirt*100/self.maxdirt

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
        def get_client_count(self, txt):
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
                txt.append("Extra clients are coming in! You business is getting very popular with the people")
                mod *= 1.1

            # Upgrades:
            temp = False
            for u in self._upgrades:
                um = getattr(u, "client_flow_mod", 0)
                if um != 0:
                    temp = True
                    mod *= um
            if temp:
                txt.append("Your building upgrades are attracting extra clients!")

            # Normalize everything:
            clients = min(min_clients + round_int(clients * mod), clients)

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
            txt = self.nd_events_report

            self.flag_red = False

            temp = "{} General Report:".format(self.name)
            txt.append("{}".format(set_font_color(temp, "lawngreen")))
            txt.append("")

            # Get businesses we wish SimPy to manage! business_manager method is expected here.
            self.nd_ups = list(up for up in self._businesses if up.workable)

            client_businesses = list(up for up in self._businesses if up.expects_clients)
            if client_businesses:
                # Clients:
                tl.start("Generating clients in {}".format(self.name))
                total_clients = self.get_client_count(txt)

                if total_clients != 0:
                    txt.append("Total of {} clients are expected to visit this establishment!".format(set_font_color(total_clients, "lawngreen")))
                else:
                    txt.append("{}".format(set_font_color("You may want to put up a sign!\n", "red")))
                    self.flag_red =  True

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
                txt.append("")
                txt.append("Reputation: {}%".format(self.rep_percentage))
                txt.append("Fame: {}%".format(self.fame_percentage))
                txt.append("Dirt: {}%".format(self.get_dirt_percentage()))
                txt.append("Threat: {}%".format(self.get_threat_percentage()))
                txt.append("")
                
                # All workers and workable businesses:
                # This basically roots out Resting/None chars!
                self.available_workers = [w for w in self.all_workers if w.is_available]
                for w in self.available_workers:
                    convert_ap_to_jp(w)
                    # And AEQ
                    if isinstance(w.action, Job):
                        w.action.auto_equip(w)

                # We can calculate manager effectiveness once, so we don't have to do
                # expensive calculations 10 000 000 times:
                if hasattr(self, "manager"):
                    if self.manager:
                        job = simple_jobs["Manager"]
                        self.manager_effectiveness = job.effectiveness(self.manager,
                                                    self.tier, None, False)
                        txt.append("This building is managed by {} at {}% effectiveness!".format(
                                self.manager.name, self.manager_effectiveness))
                    else:
                        txt.append("This building has no manager assigned to it.")
                        self.manager_effectiveness = 0
                    txt.append("")

                txt.append("{}".format(set_font_color("Starting the workday:", "lawngreen")))
                # Create an environment and start the setup process:
                self.env = simpy.Environment()
                for up in self._businesses:
                    up.pre_nd()

                # We run till 110 DU and should attempt to stop all businesses at 100.
                proc = self.env.process(self.building_manager(end=111))

                self.env.run(until=proc)
                txt.append("{}".format(set_font_color("Ending the workday.", "green")))

                # Building Stats:
                txt.append("Reputation: {}%".format(self.rep_percentage))
                txt.append("Fame: {}%".format(self.fame_percentage))
                txt.append("Dirt: {}%".format(self.get_dirt_percentage()))
                txt.append("Threat: {}%".format(self.get_threat_percentage()))

                income = self.fin.get_logical_income()
                if income > 0:
                    txt.append("\nA total of {} Gold was earned here today!".format(set_font_color(str(income), "lawngreen")))
                elif income < 0:
                    txt.append("\nYou are losing money with this business! After the night your pockets are lighter with {} Gold".format(set_font_color(str(-income), "red")))
                txt.append("{}".format(set_font_color("===================", "lawngreen")))

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
                if self.maxdirt != 0:
                    # check current status of the building and update its inhabitants
                    dirt = self.get_dirt_percentage()
                    if dirt < 30:
                        # the place is clean
                        for c in self.inhabitants:
                            if c != hero:
                                c.mod_stat("joy", 5)
                    elif dirt > 50:
                        # the place is dirty
                        for c in self.habitants:
                            if c != hero:
                                c.mod_stat("joy", (dirt-50)/2)
                            
                        txt.append("The place is quite dirty. You might want to call the cleaners.")

                    # accumulate dirt based on the number of inhabitants
                    self.dirt += len(self.inhabitants) * 10

                    # handle auto cleaning
                    if self.get_dirt_percentage() > self.auto_clean and self.auto_clean != 100:
                        price = self.get_cleaning_price()
                        if hero.take_money(price, "Hired Cleaners"):
                            self.dirt = 0
                            txt.append("Cleaners arrived to tidy up the place. You had to pay {color=[gold]}%d Gold{/color}." % price)
                        else:
                            txt.append("You wanted to hire cleaners, but could not afford it.")

                    # 'auto cleaning' by the inhabitants 
                    for c in self.inhabitants:
                        if self.dirt <= 200:
                            break
                        if c != hero and c.get_stat("disposition") > 800 and c.get_stat("joy") > 80:
                            effectiveness_ratio = simple_jobs["Cleaning"].effectiveness(c, self.tier)

                            self.dirt -= (5 * effectiveness_ratio)
                            
                            c.mod_stat("disposition", -50)
                            c.mod_stat("joy", -10)
                            txt.append("%s cleaned up a bit." % c.nickname)
                
                # in-house fighting between the inhabitants
                for c in self.inhabitants:
                    if c == hero or c.get_stat("vitality") < 25:
                        continue
                    traits = [t for t in c.traits if t.id in ("Aggressive", "Vicious", "Sadist", "Extremely Jealous")]
                    if not traits:
                        continue
                    trait = choice(traits)
                    others = [o for o in self.inhabitants if o != c and o != hero]
                    if trait == "Extremely Jealous":
                        if not check_lovers(c, hero):
                            continue
                        others = [o for o in others if check_lovers(o, hero)]
                    if not others:
                        continue
                    o = choice(others)
                    if self.maxdirt != 0:
                        txt.append("%s and %s started to fight over a minor issue. The building suffered the most." % (c.nickname, o.nickname))
                        self.dirt += 50
                    else:
                        txt.append("%s and %s started to fight over a minor issue. They became very tense." % (c.nickname, o.nickname))
                    o.mod_stat("joy", -20)
                    c.mod_stat("joy", -20)
                    o.mod_stat("vitality", -10)
                    c.mod_stat("vitality", -10)
                    self.flag_red =  True

                txt.append(set_font_color("===================", "lawngreen"))
                txt.append("This is a residential building. Nothing much happened here today.")

            tl.end("{}.run_nd (SimPy/Clients, etc.)".format(self.name))

        def building_manager(self, end):
            """This is the main process that manages everything that is happening in the building!
            """
            env = self.env

            # Run the manager process:
            if getattr(self, "manager", None):
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
                            w.mod_stat("joy", 1)

            # post-process of the manager
            if getattr(self, "manager", None):
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
