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
            - Finds best client match using business.get_workers()
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
        pass # FIXME obsolete

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

        def add_inhabitant(self, char):
            self.inhabitants.add(char)
        def remove_inhabitant(self, char):
            self.inhabitants.remove(char)

        def __str__(self):
            return str(getattr(self, "name", self.id))

    class AfterLife(HabitableLocation):
        """
        """
        def __init__(self):
            super(AfterLife, self).__init__(id="After Life", daily_modifier=.0, desc="No one knows where is this place and what's going on there")
            self.inhabitants = OrderedDict()

        def add_inhabitant(self, char):
            self.inhabitants[char] = calendar.string()

    class InvLocation(HabitableLocation):
        """Location with an inventory:

        Basically, a habitable location where one can store 'stuff'
        Also has a number of extra properties.
        """
        pass # FIXME obsolete

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
            "strict": "Workers will only perform jobs that are the exact match to the action you're assigned them!",
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

            self.upgrades = []
            self.allowed_upgrades = []
            self.businesses = []
            self.allowed_businesses = []

            self.in_construction_upgrades = [] # work (business/upgrade) in progress. [(business/upgrade), remaining days, job_effectiveness_mod]

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
            self.auto_clean = 100 # percentage at the cleaners should be called
            self.maxthreat = 1000
            self.threat = 0
            self.auto_guard = 0   # amount of money spent on guards (per day)
            #self.threat_mod = 5 initialized later

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
            if self.needs_manager:
                # Management:
                self.manager_effectiveness = 0 # Calculated once at start of each working day (performance)
                self.workers_rule = "normal"
                self.init_pep_talk = True
                self.cheering_up = True
                self.asks_clients_to_wait = True
                self.help_ineffective_workers = True # Bad performance still may get a payout.
                self.works_other_jobs = False
                # TODO Before some major release that breaks saves, move manager and effectiveness fields here.

                # Workers:
                self.all_workers = list() # All workers presently assigned to work in this building.
                self.available_workers = list() # This is built and used during the next day (SimPy).
                self.available_managers = list() # This is built and used during the next day (SimPy).

                # Clients:
                self.all_clients = list() # All clients of this building are maintained here.
                self.regular_clients = set() # Subset of self.all_clients.
                self.clients = list() # temp clients, this is used during SimPy cals and reset on when that ends.
                self.clients_regen_day = 0 # The day when the clients are regenerated
                
            self.normalize_jobs()

            if not hasattr(self, "threat_mod"):
                if self.location == "Flee Bottom":
                    mod = 5
                elif self.location == "Midtown":
                    mod = 2
                else: # if self.location == "Richford":
                    mod = 0
                self.threat_mod = mod

            if hasattr(self, "inventory"):
                if bool(self.inventory):
                    self.inventory = Inventory(15)
                    self.given_items = dict()
                    # Once again, for the Items transfer:
                    self.status = "slave"
                else:
                    del self.inventory

        @property
        def needs_manager(self):
            return any(b.workable for b in self.allowed_businesses)

        def can_sell(self):
            return all(u.can_close() for u in self.businesses)

        def get_daily_modifier(self):
            daily_modifier = self.daily_modifier
            for b in self.businesses:
                for u in b.upgrades:
                    if hasattr(u, "daily_modifier_mod"):
                        daily_modifier *= u.daily_modifier_mod
            for u in self.upgrades:
                if hasattr(u, "daily_modifier_mod"):
                    daily_modifier *= u.daily_modifier_mod
            daily_modifier *= 1.0 - max(0, (self.get_dirt_percentage() - 40)/100.0)
            return daily_modifier

        def normalize_jobs(self):
            jobs = set()
            if self.needs_manager:
                jobs.add(simple_jobs["Manager"])
            for up in self.businesses:
                jobs.update(up.jobs)
            self.jobs = jobs

        def get_valid_jobs(self, char):
            """Returns a list of jobs available for the building that the character might be willing to do.

            Returns an empty list if no jobs is available for the character.
            """
            return [job for job in self.jobs if char.can_work(job)]

        def get_price(self):
            # Returns our best guess for price of the Building
            # Needed for buying, selling the building or for taxation.
            # **We may want to take reputation and fame into account as well.
            price = self.price - self.get_cleaning_price()

            for u in self.upgrades:
                price += u.get_price()
            for b in self.businesses:
                price += b.get_price()

            price *= (1.0 - self.get_threat_percentage()/200.0)
            return price

        def pay_for_extension(self, cost, materials):
            # This does assume that we checked and know that MC has the resources.
            if cost:
                hero.take_money(cost, "Building Upgrades")
                self.fin.log_logical_expense(cost, "Upgrade")

            if materials:
                for item, amount in materials.items():
                    hero.remove_item(item, amount)

        def build_business(self, business, in_game=False):
            """Add business to the building.
            """
            cost, materials, in_slots, ex_slots = business.get_cost()
            self.in_slots += in_slots
            self.ex_slots += ex_slots

            if in_game:
                self.pay_for_extension(cost, materials)

            duration = business.duration
            if duration is None or duration[0] < 1 or not in_game:
                self.add_business(business, in_game)
                for icu in self.in_construction_upgrades:
                    business.job_effectiveness_mod -= icu[2]
            else:
                mod = duration[1]
                for b in self.businesses:
                    b.job_effectiveness_mod -= mod
                self.in_construction_upgrades.append([business, duration[0], mod])

        def add_business(self, business, in_game):
            self.businesses.append(business)
            self.businesses.sort(key=attrgetter("ID"), reverse=True)
            if in_game:
                self.normalize_jobs()

        def close_business(self, business):
            """Remove a business from the building.
            """
            self.businesses.remove(business)

            cost, materials, in_slots, ex_slots = business.get_cost()

            self.in_slots -= in_slots
            self.ex_slots -= ex_slots

            self.pay_for_extension(cost, None)

            # reset the business
            business.upgrades = list()
            if business.expands_capacity:
                cap = business.capacity - business.base_capacity
                business.in_slots -= cap * business.exp_cap_in_slots
                business.ex_slots -= cap * business.exp_cap_ex_slots
                business.capacity -= cap

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
                    if worker.job not in self.jobs:
                        worker.set_job(None)

        def build_upgrade(self, upgrade):
            cost, materials, in_slots, ex_slots = upgrade.get_cost()
            self.in_slots += in_slots
            self.ex_slots += ex_slots

            self.pay_for_extension(cost, materials)

            duration = upgrade.duration
            if duration is None or duration[0] < 1:
                self.add_upgrade(upgrade)
            else:
                mod = duration[1]
                for b in self.businesses:
                    b.job_effectiveness_mod -= mod
                self.in_construction_upgrades.append([upgrade, duration[0], mod])

        def add_upgrade(self, upgrade):
            self.upgrades.append(upgrade)
            self.upgrades.sort(key=attrgetter("ID"), reverse=True)

        def cancel_construction(self, icu):
            self.in_construction_upgrades.remove(icu)

            u, d, m = icu

            cost, materials, in_slots, ex_slots = u.get_cost()

            self.in_slots -= in_slots
            self.ex_slots -= ex_slots

            for b in self.businesses:
                b.job_effectiveness_mod += m

        def all_possible_extensions(self):
            # Returns a list of all possible extensions (businesses and upgrades)
            return self.allowed_businesses + self.allowed_upgrades

        def has_extension(self, extension):
            return any(u.__class__ == extension for u in chain(self.upgrades, self.businesses))

        # Describing building purposes:
        def is_business(self):
            return len(self.allowed_businesses) != 0

        @property
        def habitable(self):
            # Overloads property of Location core class to serve the building.
            return self.rooms != 0 or any(i.habitable for i in self.businesses)

        @property
        def workable(self):
            """Returns True if this building has upgrades that are businesses.
            """
            return any(i.workable for i in self.businesses)

        @property
        def vacancies(self):
            return self.habitable_capacity - len(self.inhabitants)

        @property
        def workable_capacity(self):
            capacity = 0
            for i in self.businesses:
                if i.workable:
                    capacity += i.capacity
            return capacity

        @property
        def habitable_capacity(self):
            capacity = self.rooms
            for i in self.businesses:
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
            return (10+self.dirt)*(self.tier+2) 

        def get_threat_percentage(self):
            """
            Returns percentage of dirt in the building as (percent, description).
            """
            return 0 if self.maxthreat == 0 else self.threat*100/self.maxthreat

        def get_dirt_percentage(self):
            """
            Returns percentage of dirt in the building as (percent, description).
            """
            return 0 if self.maxdirt == 0 else self.dirt*100/self.maxdirt

        def get_fame_percentage(self):
            return 0 if self.maxfame == 0 else self.fame*100/self.maxfame

        def get_rep_percentage(self):
            return 0 if self.maxrep == 0 else self.rep*100/self.maxrep

        def moddirt(self, value):
            value += self.dirt
            if value > self.maxdirt:
                value = self.maxdirt
            elif value < 0:
                value = 0
            self.dirt = value

        def modthreat(self, value):
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
            # Capacity of the businesses:
            for u in self.businesses:
                if u.expects_clients:
                    clients += u.get_client_count()
                    if DSNBR:
                        devlog.info("{} pure clients for {}".format(u.get_client_count(), u.name))

            # Fame percentage mod (linear scale):
            mod = self.get_fame_percentage() / 100.0

            # Upgrades:
            temp = False
            for u in self.upgrades:
                um = getattr(u, "client_flow_mod", 0)
                if um != 0:
                    temp = True
                    mod *= um
            if temp:
                txt.append("Your building upgrades are attracting extra clients!")

            # Normalize everything:
            clients = max(min_clients, round_int(clients * mod))

            return clients

        def get_max_client_capacity(self):
            """Returns the very maximum amount of clients this building can host
                at any given time. This is used in a number of ND-calculations.
            """
            capacity = 0
            for u in self.businesses:
                if u.expects_clients:
                    capacity += u.capacity
            return capacity

        @property
        def expects_clients(self):
            return any(i.expects_clients for i in self.businesses)

        def create_customer(self, likes=None):
            """
            Returns a customer for this Building.
            """
            # determine gender of the customer
            gender = "male" if dice(75) else "female"

            # determine rank(caste) of the customer
            rank = randrange(3)
            rep = self.rep
            if rep < 50: rank = max(rank, 1)
            elif rep <= 150: rank += 1
            elif rep <= 400: rank += 2
            elif rep <= 600: rank += 3
            elif rep <= 800: rank += 4
            else:            rank += 5

            # determine tier of the customer
            tier = self.tier
            tier = uniform(float(max(tier-2, .1)), float(tier + 1))

            # create random customer
            customer = build_client(gender=gender, rank=rank,
                                    tier=tier,
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
            self.nd_ups = list(up for up in self.businesses if up.workable)

            client_businesses = list(up for up in self.businesses if up.expects_clients)
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
                clients = self.all_clients
                curr_clients = len(clients)
                if self.clients_regen_day <= day:
                    to_remove = min(curr_clients/2, 100)
                    idx = randint(0, curr_clients-to_remove)
                    clients = clients[0:idx]+clients[idx+to_remove:curr_clients]
                    curr_clients -= to_remove
                    self.all_clients = clients
                    # TODO make the remaining clients regulars?!
                    self.clients_regen_day = day + randint(2, 4)

                # update all_clients (and clients) based on the new expectations
                new_clients = total_clients - curr_clients
                if new_clients > 0:
                    if len(client_businesses) == 1:
                        # single business -> all customer wants the same
                        cb = client_businesses[0]
                        for i in xrange(new_clients):
                            clients.append(self.create_customer(likes=[cb]))
                    else:
                        # multiple businesses -> generate 'likes' based on the expected client count
                        businesses = client_businesses[:]
                        shuffle(businesses)
                        likes = []
                        counter = 0.0
                        for up in businesses:
                            cc = up.get_client_count()
                            cc = float(cc*new_clients)/total_clients
                            likes.extend([up] * (int(cc+counter)-int(counter)))
                            counter += cc
                        shuffle(likes)
                        for like in likes:
                            clients.append(self.create_customer(likes=[like]))
                elif new_clients < 0:
                    # something happened to the building(downsized/reputation-hit/etc...) -> it it time that the clients react to it
                    to_remove = -new_clients/2
                    idx = randint(0, curr_clients-to_remove)
                    clients = clients[0:idx]+clients[idx+to_remove:curr_clients]
                    self.all_clients = clients

                self.clients = clients[:]

                tl.end("Generating clients in {}".format(self.name))

            if self.nd_ups or client_businesses:
                # Building Stats:
                txt.append("")
                txt.append("Reputation: {}%".format(self.get_rep_percentage()))
                txt.append("Fame: {}%".format(self.get_fame_percentage()))
                txt.append("Dirt: {}%".format(self.get_dirt_percentage()))
                txt.append("Threat: {}%".format(self.get_threat_percentage()))
                txt.append("")
                
                # All workers and workable businesses:
                # This basically roots out Resting/None chars!
                workers = [w for w in self.all_workers if w.is_available and w.task is None]
                for w in workers:
                    if w != hero:
                        w.action.auto_equip(w)
                self.available_workers = workers

                # Do the expensive manager preparation out of the loop once
                manager_pre_nd(self)

                txt.append(set_font_color("Starting the workday:", "lawngreen"))
                # Create an environment and start the setup process:
                self.env = simpy.Environment()
                for up in self.businesses:
                    up.pre_nd()

                # We run till 110 DU and should attempt to stop all businesses at 100.
                proc = self.env.process(self.building_manager(end=111))

                self.env.run(until=proc)
                txt.append(set_font_color("Ending the workday.", "green"))

                # Building Stats:
                txt.append("Reputation: {}%".format(self.get_rep_percentage()))
                txt.append("Fame: {}%".format(self.get_fame_percentage()))
                txt.append("Dirt: {}%".format(self.get_dirt_percentage()))
                txt.append("Threat: {}%".format(self.get_threat_percentage()))

                income = self.fin.get_logical_income()
                if income > 0:
                    txt.append("\nA total of {} Gold was earned here today!".format(set_font_color(str(income), "lawngreen")))
                elif income < 0:
                    txt.append("\nYou are losing money with this business! After the night your pockets are lighter with {} Gold".format(set_font_color(str(-income), "red")))
                txt.append(set_font_color("===================", "lawngreen"))

                # finish the business by resetting the variables
                for c in self.all_clients:
                    for f in c.flags.keys():
                        if f.startswith("jobs"):
                            c.del_flag(f)

                # Clear manager attributes which are used only during the nd run
                manager_post_nd(self)

                for up in self.businesses:
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
                        for c in self.inhabitants:
                            if c != hero:
                                c.mod_stat("joy", (dirt-50)/2)

                        txt.append("The place is quite dirty. You might want to call the cleaners.")

                    # accumulate dirt based on the number of inhabitants
                    self.moddirt(len(self.inhabitants) * 10)

                    # handle auto cleaning
                    if self.get_dirt_percentage() > self.auto_clean:
                        price = self.get_cleaning_price()
                        if hero.take_money(price, "Hired Cleaners"):
                            self.dirt = 0
                            txt.append("Cleaners arrived to tidy up the place. You had to pay {color=gold}%d Gold{/color}." % price)
                        else:
                            txt.append("You wanted to hire cleaners, but could not afford it.")

                    # 'auto cleaning' by the inhabitants 
                    for c in self.inhabitants:
                        if self.dirt <= 200:
                            break
                        if c == hero or "Messy" in c.traits:
                            continue
                        if "Neat" in c.traits:
                            if c.get_stat("disposition") < 650 or c.get_stat("joy") < 60:
                                continue
                        else:
                            if c.get_stat("disposition") < 800 or c.get_stat("joy") > 80:
                                continue
                        effectiveness = simple_jobs["Cleaning"].effectiveness(c, self.tier, txt)

                        self.moddirt(-effectiveness / 5.0)

                        c.mod_stat("disposition", -50)
                        c.mod_stat("affection", -10)
                        c.mod_stat("joy", -10)
                        txt.append("%s cleaned up a bit." % c.nickname)

                # in-house fighting between the inhabitants
                for c in self.inhabitants:
                    if c == hero or c.get_stat("vitality") < 25:
                        continue
                    traits = [t for t in c.traits if t.id in ("Aggressive", "Vicious", "Sadist", "Extremely Jealous")]
                    if not traits:
                        continue
                    traits.append(None)
                    trait = choice(traits)
                    if trait is None:
                        continue
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
                        self.moddirt(50)
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
            env.process(manager_process(env, self))

            for u in self.nd_ups:
                # Trigger all public businesses:
                if u.active:  # Business as usual:
                    env.process(u.business_control())
                else: # inactive business
                    env.process(self.inactive_process())

            if self.clients:
                env.process(self.clients_dispatcher(end=end-10))

            has_garden = self.has_extension(Garden)
            auto_guard = self.auto_guard
            if auto_guard != 0:
                if hero.take_money(auto_guard, "Hired Guards"):
                    self.fin.log_logical_expense(auto_guard, "Hired Guards")
                    self.log("Hired guards are protecting the building.")
                    auto_guard /= 2
                else:
                    self.log("You could not pay the hired guards so they left the building.")
                    auto_guard = 0
            threatmod = self.threat_mod * max(1, min(self.fame - self.rep - self.threat, 50))

            while (1):
                if not env.now % 20:
                    temp = "{color=green} =========>>>{/color}\n"
                    self.log(temp, True)
                yield env.timeout(1)
                simpy_debug("%s DU Executing =====================>>>", env.now)

                # handle auto-clean
                if self.get_dirt_percentage() > self.auto_clean:
                    price = self.get_cleaning_price()
                    if hero.take_money(price, "Hired Cleaners"):
                        self.fin.log_logical_expense(price, "Hired Cleaners")
                        self.log("The building was cleaned by hired professionals!", True)
                        self.dirt = 0

                # handle auto-guard
                if auto_guard > 0 and self.threat > 200:
                    temp = min(auto_guard, 200)
                    self.threat -= temp
                    auto_guard -= temp
                    self.log("The hired guards eliminated %d threat." % temp, True)

                # check the need for police intervention
                if self.threat >= 900:
                    temp = "{color=red}Police{/color} arrived at %s!" % self.name
                    price = 500*self.get_max_client_capacity()*(self.tier or 1)
                    if hero.take_money(price, "Police"):
                        temp += " You paid %d in penalty fees for allowing things to get this out of hand." % price
                    else:
                        price = int(price*1.25)
                        temp += " You could not settle the due penalty fees. Now you have to pay %d as a property tax with interest." % price
                        hero.fin.property_tax_debt += price
                    temp += " The building's reputation also took a very serious hit!"
                    self.log(temp, True)

                    self.flag_red = True
                    self.modrep(-(20*max(1, self.tier)))
                    self.threat = 0

                # add default mods of the building
                if not env.now % 25:
                    self.moddirt(5) # 5 dirt each 25 turns even if nothing is happening.
                    self.modthreat(threatmod)

                    if has_garden and dice(25):
                        for w in self.all_workers:
                            w.mod_stat("joy", 1)

                if env.now >= end:
                    break

        def clients_dispatcher(self, end):
            """This method provides stream of clients to the building following it's own algorithm.

            We want 50% of all clients to come in the 'rush hour' (turn 50 - 80).
            """
            expected = len(self.clients)
            running = 0

            has_garden = self.has_extension(Garden)

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
            client_name = set_font_color(client.name, "beige")

            # Register the fact that client arrived at the building:
            temp = "%s arrives at the %s." % (client_name, self.name)
            self.log(temp, True)

            if self.dirt >= 800:
                yield self.env.timeout(1)
                temp = "Your building is as clean as a pig stall. %s storms right out." % client_name
                self.log(temp)
                self.env.exit()
            if self.threat >= 800:
                yield self.env.timeout(1)
                temp = "Your building is as safe as a warzone. %s ran away." % client_name
                self.log(temp)
                self.env.exit()

            # Client threat mod:
            if "Aggressive" in client.traits:
                self.modthreat(2 if has_garden else 3)

            # Visit counter:
            #client.up_counter("visited_building" + str(self.id))

            # Prepare data:
            businesses = [b for b in self.nd_ups if b.expects_clients]
            shuffle(businesses)

            fav_business = client.likes.intersection(self.businesses)

            # Case where clients fav business was removed from the building, client to react appropriately.
            if not fav_business:
                self.all_clients.remove(client)
                temp = "%s storms out of the building pissed off as %s favorite business was removed!" % (client_name, client.pp)
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

                if business.res.count >= business.capacity:
                    # not enough capacity to handle the client 
                    # Wait for the business to open in case of a favorite:
                    if any((not self.asks_clients_to_wait,
                            self.manager_effectiveness == 0 or self._dnd_manager.PP == 0,
                            business != fav_business,
                            self.env.now > 85)):
                        continue # no one can help -> skip
                    
                    # Manager active effect:
                    temp = "Your manager convinced %s to wait a bit for a slot in %s favorite %s to open up!" % (
                                    client_name, client.pp, fav_business.name)
                    self.log(temp)

                    self._dnd_manager._dnd_mlog.append("\nAsked a client to wait for a spot in %s to open up!" % (fav_business.name))
                    self._dnd_manager.PP -= 1

                    # the actual waiting
                    for i in range(5):
                        yield self.env.timeout(1)
                        if business.res.count < business.capacity:
                            break # a free spot -> jump
                    else:
                        continue # timeout -> skip

                if business.type == "personal_service":
                    # Personal Service (Brothel-like):
                    job = business.jobs[0] # FIXME one job per business, is should be client specific anyway
                    workers = business.get_workers(job, amount=1, client=client)

                    if workers:
                        # We presently work just with the one char only, so:
                        worker = workers.pop()
                        self.available_workers.remove(worker)

                        # We bind the process to a flag and wait until it is interrupted:
                        visited += 1
                        with business.res.request() as request:
                            yield request
                            yield self.env.process(business.request_resource(client, worker))
                elif business.type == "public_service":
                    # Jobs like the Club:
                    visited += 1
                    with business.res.request() as request:
                        yield request
                        yield self.env.process(business.client_control(client))

            if not visited:
                temp = "There is not much for %s to do, so %s leaves your establishment cursing..." % (client_name, client.p)
            else:
                temp = "%s is leaving after visiting %d %s." % (client_name, visited, plural("business", visited))
            self.log(temp, True)
            self.env.exit()

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
                    mod = advert.get('fame', None)
                    if mod is not None:
                        mod = randint(*mod)
                        self.modfame(mod)
                        tmodfame += mod
                    mod = advert.get('reputation', None)
                    if mod is not None:
                        mod = randint(*mod)
                        self.modrep(mod)
                        tmodrep += mod

                    spentcash += advert['upkeep']
                    if advert.get('unique', False):
                        advert['active'] = False

            if spentcash or tmodfame or tmodrep:
                txt.append("In total you got a bill of %d Gold in advertising fees, reputation was increased through advertising by %d, fame by %d." % (spentcash, tmodrep, tmodfame))

                if spentcash and not hero.take_money(spentcash, reason="Building Ads"):
                    rep_hit = max(10, spentcash/10)
                    self.modrep(-rep_hit)
                    txt.append("{color=red}And yet, you did not have enough money to pay your advertisers! They took it out on you by promoting %s as a shitty dump...{/color}" % self.name)
                    self.flag_red = True

                self.fin.log_logical_expense(spentcash, "Ads")

            # do the construction work 
            for b in self.businesses:
                if not b.in_construction_upgrades:
                    continue
                for icu in b.in_construction_upgrades[:]:
                    u, d, m = icu
                    d -= 1
                    if d > 0:
                        icu[1] = d
                        continue
                    if u == "capacity":
                        b.capacity += 1
                        txt.append("After the construction work, %s expanded its capacity!" % b.name)
                    else:
                        b.add_upgrade(u)
                        txt.append("The construction work is finished on %s in %s!" % (u.name, b.name))
                    b.in_construction_upgrades.remove(icu)
                    b.job_effectiveness_mod += m

            if self.in_construction_upgrades:
                for icu in self.in_construction_upgrades[:]:
                    u, d, m = icu
                    d -= 1
                    if d > 0:
                        icu[1] = d
                        continue
                    self.in_construction_upgrades.remove(icu)
                    for b in self.businesses:
                        b.job_effectiveness_mod += m

                    if isinstance(u, Business):
                        self.add_business(u, True)
                        txt.append("After the construction work, %s is ready to open!" % u.name)
                    else:
                        self.add_upgrade(u)
                        txt.append("The construction work is finished on %s!" % u.name)

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
            if add_time:
                # try to create a timestamp between 18:00 and 23:00 assuming env.now is between 0 and 100
                now = self.env.now
                item = "%02d:%02d - %s" % (18+now/20,(now*3)%60, item)
            self.nd_events_report.append(item)
            if DSNBR:
                devlog.info(item)

        def nd_log_income(self):
            """
            Log the next day income for this building.
            """
            self.fin.next_day()
