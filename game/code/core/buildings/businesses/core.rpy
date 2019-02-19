init -12 python:
    #################################################################
    # BUILDING UPGRADE CLASSES:
    class CoreExtension(_object) :
        """BaseClass for any building expansion! (aka Business)
        """
        # Class attributes serve as default, they are fed to a method of Building,
        # adjusted and displayed to the player. In most of the cases, Extension will be created
        # using these (alt is from JSON/Custom data):


        def __init__(self):
            # This means that we can add capacity to this business.
            # Slots/Cost are the cost of a single expansion!
            self.cost = getattr(self, "cost", 0)
            self.in_slots = getattr(self, "in_slots", 0)
            self.ex_slots = getattr(self, "ex_slots", 0)
            self.materials = getattr(self, "materials", {})

            self.expands_capacity = False

        def get_price(self):
            # Returns our best guess for price of the business
            # Needed for buying, selling the building or for taxation.
            price = self.cost
            if self.expands_capacity:
                price += self.capacity*self.exp_cap_cost
            price *= self.building.tier + 1
            return price

        def get_cost(self):
            # We figure out what it would take to add this extension (building or business)
            # using it's class attributes to figure out the cost and the materials required.
            cost = self.get_price()

            mpl = self.building.tier + 1

            in_slots = self.in_slots
            ex_slots = self.ex_slots
            if self.expands_capacity:
                cap = self.capacity
                in_slots += cap*self.exp_cap_in_slots
                ex_slots += cap*self.exp_cap_ex_slots

            materials = self.materials.copy()
            for k, v in materials.items():
                materials[k] = v * mpl

            return cost, materials, in_slots, ex_slots

        def get_expansion_cost(self):
            # Assume self.expands_capacity is true
            mpl = self.building.tier + 1

            cost = self.exp_cap_cost * mpl

            in_slots = self.exp_cap_in_slots
            ex_slots = self.exp_cap_ex_slots

            materials = self.exp_cap_materials.copy()
            for k, v in materials.items():
                materials[k] = v * mpl

            return cost, materials, in_slots, ex_slots

    class Business(CoreExtension):
        """BaseClass for any building expansion! (aka Business)
        """
        def __init__(self):
            super(Business, self).__init__()

            # Jobs this upgrade can add. *We add job instances here!
            # It may be a good idea to turn this into a direct job assignment instead of a set...
            self.jobs = list()
            self.workers = set() # List of on duty characters.
            self.clients = set() # Local clients, this is used during next day and reset on when that ends.

            # If False, no clients are expected.
            # If all businesses in the building have this set to false, no client stream will be generated at all.
            self.expects_clients = False
            self.habitable = False
            self.workable = False
            # If not active, business is not executed and is considered "dead",
            # we run "inactive" method with a corresponding simpy process in this case.
            self.active = True

            self.capacity = getattr(self, "capacity", 0)
            if hasattr(self, "exp_cap_cost"):
                self.expands_capacity = True
                self.exp_cap_in_slots = getattr(self, "exp_cap_in_slots", 0)
                self.exp_cap_ex_slots = getattr(self, "exp_cap_ex_slots", 0)
                self.exp_cap_materials = getattr(self, "exp_cap_materials", {})

            self.allowed_upgrades = getattr(self, "allowed_upgrades", [])
            self.in_construction_upgrades = list() # Not used yet!
            self.upgrades = list()

        def expand_capacity(self):
            cost, materials, in_slots, ex_slots = self.get_expansion_cost()
            building = self.building

            self.in_slots += in_slots
            building.in_slots += in_slots
            self.ex_slots += ex_slots
            building.ex_slots += ex_slots

            building.pay_for_extension(cost, materials)

            self.capacity += 1

        def can_reduce_capacity(self):
            if not self.expands_capacity:
                return False
            if self.capacity == 0:
                return False
            if hero.gold < self.get_expansion_cost()[0]:
                return False
            # these two should never happen, but check anyways...
            if self.in_slots < self.exp_cap_in_slots:
                return False  
            if self.ex_slots < self.exp_cap_ex_slots:
                return False
            return True

        def reduce_capacity(self):
            cost, materials, in_slots, ex_slots = self.get_expansion_cost()
            building = self.building

            self.in_slots -= in_slots
            building.in_slots -= in_slots
            self.ex_slots -= ex_slots
            building.ex_slots -= ex_slots

            building.pay_for_extension(cost, None)

            self.capacity -= 1

            # relocate the possible extra inhabitant
            if self.habitable and building.vacancies < 0:
                for char in building.inhabitants: break
                char.home = pytfall.streets

        def get_client_count(self):
            """Returns amount of clients we expect to come here.

            Right now we base our best guess on time and cap.
            """
            # .7 is just 70% of absolute max (to make upgrades meaningful).
            # 101.0 is self.env duration.
            # self.time is amount of time we expect to spend per client.
            if not self.time:
                raise Exception("Zero Modulo Division Detected #02")
            amount = round_int(((101.0/self.time)*self.capacity)*.7)

            return amount

        @property
        def env(self):
            return self.building.env

        def log(self, item, add_time=False):
            # Logs the text for next day event...
            self.building.log(item, add_time=add_time)

        # Worker methods:
        def has_workers(self, amount=1):
            # Checks if there is a worker(s) available.
            return False

        @property
        def all_workers(self):
            # This may be a poor way of doing it because different upgrades could have workers with the same job assigned to them.
            # Basically what is needed is to allow setting a business to a worker as well as the general building if required...
            # And this doesn't work? workers are never populated???
            return list(i for i in self.building.available_workers if self.all_occs & i.occupations)

        def strict_rule_workers(self, job):
            return list(i for i in self.building.available_workers if i.action == job)

        def normal_rule_workers(self, job):
            return list(i for i in self.building.available_workers if i.traits.basetraits.intersection(job.occupation_traits))

        def loose_rule_workers(self, job):
            return list(i for i in self.building.available_workers if i.occupations.intersection(job.occupations))

        def get_workers(self, job, amount=1, match_to_client=None,
                        rule="normal", use_slaves=True):
            """Tries to find workers for any given job.

            Will use given rule and check it vs building rule, using only
                workers permitted.

            @param: match_to_client: Will try to find the a good match to client,
                    expects a client (or any PytC instance with .likes set) object.
            """
            building = self.building
            rv = list()
            workers = list()

            # Get the allowed rules:
            rules = building.WORKER_RULES
            local_index = rules.index(rule)
            building_rule_index = rules.index(building.workers_rule)
            slice_by = min(local_index, building_rule_index) + 1
            rules = rules[:slice_by]

            for r in rules:
                func = getattr(self, r + "_rule_workers")
                workers = list(i for i in func(job) if i not in workers)
                if not use_slaves:
                    workers = [w for w in workers if w.status != "slave"]

                shuffle(workers)
                while len(rv) < amount and workers:
                    if match_to_client:
                        w = self.find_best_match(match_to_client, workers) # This is not ideal as we may end up checking a worker who will soon be removed...
                    else:
                        w = workers.pop()
                    if self.check_worker_capable(w) and self.check_worker_willing(w, job):
                        rv.append(w)

                if len(rv) >= amount:
                    break

            return rv

        def find_best_match(self, client, workers):
            """Attempts to match a client to a worker.

            This intersects worker traits with clients likes and acts accordingly.
            Right now it will not try to find the very best match and instead will break on the first match found.
            Returns a worker at random if that fails.
            """
            for w in workers:
                likes = client.likes.intersection(w.traits)
                if likes:
                    slikes = ", ".join([str(l) for l in likes])
                    temp0 = '{} liked {} for {} {}.'.format(
                        set_font_color(client.name, "beige"),
                        set_font_color(w.nickname, "pink"),
                        slikes, plural("trait", len(likes)))
                    temp1 = '{} found {} {} in {} very appealing.'.format(
                        set_font_color(client.name, "beige"),
                        slikes, plural("trait", len(likes)),
                        set_font_color(w.nickname, "pink"))
                    self.log(choice([temp0, temp1]))
                    client.set_flag("jobs_matched_traits", likes)
                    workers.remove(w)
                    return w
            return workers.pop()

        def check_worker_willing(self, worker, job):
            """Checks if the worker is willing to do the job.

            Removes worker from instances master list.
            Returns True is yes, False otherwise.
            """
            if worker.can_work(job):
                if DSNBR:
                    temp = set_font_color("Debug: {} worker (Occupations: {}) with action: {} is doing {}.".format(
                                          worker.nickname, ", ".join(list(str(t) for t in worker.occupations)), worker.action, job.id), "lawngreen")
                    self.log(temp, True)
                return True
            else:
                building = self.building
                if worker in building.available_workers:
                    building.available_workers.remove(worker)

                if DSNBR:
                    temp = set_font_color('Debug: {} worker (Occupations: {}) with action: {} refuses to do {}.'.format(
                            worker.nickname, ", ".join(list(str(t) for t in worker.occupations)),
                            worker.action, job.id), "red")
                    self.log(temp)
                else:
                    temp = set_font_color('{} is refuses to do {}!'.format(worker.name, job.id), "red")
                    self.log(temp)

                return False

        def check_worker_capable(self, worker):
            """Checks if the worker is capable of doing the job.

            Removes worker from instances master list.
            Returns True is yes, False otherwise.
            """
            if can_do_work(worker):
                return True
            else:
                building = self.building
                if worker in building.available_workers:
                    building.available_workers.remove(worker)
                temp = set_font_color('{} is done working for the day.'.format(worker.name), "cadetblue")
                self.log(temp)
                return False

        # Runs before ND calcs stats for this building.
        def pre_nd(self):
            # Runs at the very start of execution of SimPy loop during the next day.
            return

        def post_nd(self):
            # Resets all flags and variables after next day calculations are finished.
            return

        @property
        def all_occs(self):
            s = set()
            for j in self.jobs:
                s = s | j.all_occs
            return s

        def log_income(self, amount, reason=None):
            # Plainly logs income to the main building finances.
            if not reason:
                reason = self.name
            self.building.fin.log_logical_income(amount, reason)

        def inactive_process(self):
            temp = "{} is currently inactive, no actions will be conducted here!".format(self.name)
            self.log(temp)
            #yield self.env.timeout(100)

        # SimPy:
        def business_control(self):
            """SimPy business controller.
            """
            while (1):
                break #yield self.env.timeout(100)

        # Business MainUpgrade related:
        def add_upgrade(self, upgrade, pay=False):
            building = self.building

            cost, materials, in_slots, ex_slots = upgrade.get_cost()
            building.in_slots += in_slots
            building.ex_slots += ex_slots

            if pay:
                building.pay_for_extension(cost, materials)

            upgrade.building = building
            upgrade.business = self
            self.upgrades.append(upgrade)
            self.upgrades.sort(key=attrgetter("ID"), reverse=True)

        def all_possible_extensions(self):
            # Named this was to conform to GUI (same as for Buildings)
            return self.allowed_upgrades

        def has_extension(self, upgrade):
            # Named this was to conform to GUI (same as for Buildings)
            return upgrade in self.upgrades

    class PrivateBusiness(Business):
        def __init__(self):
            super(PrivateBusiness, self).__init__()

            self.type = "personal_service"
            self.workable = True
            self.expects_clients = True

            # SimPy and etc follows:
            self.res = None # Restored before every job...
            self.time = 10 # Same
            self.is_running = False

        def has_workers(self):
            return any((self.all_occs & i.occupations) for i in self.building.available_workers)

        def business_control(self):
            while 1:
                yield self.env.timeout(self.time)

                if self.res.count == 0 and not self.has_workers():
                    break

            # We remove the business from nd if there are no more strippers to entertain:
            temp = "There are no workers available in the {} so it is shutting down!".format(self.name)
            self.log(temp)
            self.building.nd_ups.remove(self)

        def request_resource(self, client, char):
            """Requests a room from Sim'Py, under the current code, this will not be called if there are no rooms available...
            """
            raise Exception("request_resource method/process must be implemented")

        def run_job(self, client, char):
            """Waits for self.time delay and calls the job...
            """
            raise Exception("Run Job method/process must be implemented")

        def pre_nd(self):
            self.res = simpy.Resource(self.env, self.capacity)

        def post_nd(self):
            self.res = None
            self.is_running = False


    class PublicBusiness(Business):
        """Public Business Upgrade.

        This usually assumes the following:
        - Clients are handled in one general pool.
        - Workers randomly serve them.
        """
        def __init__(self):
            super(PublicBusiness, self).__init__()
            self.workable = True
            self.expects_clients = True
            self.type = "public_service"

            # If this is set to self.env.now in client manager, we send in workers (bc).
            self.send_in_worker = False

            self.active_workers = set() # On duty Workers.
            self.clients_waiting = set() # Clients waiting to be served.
            #self.clients_being_served = set() # Clients that we serve.

            # SimPy and etc follows (L33t stuff :) ):
            self.res = None # Restored before every job... Resource Instance that may not be useful here...
            self.time = 10 # Time for a single shift.
            self.is_running = False # Active/Inactive.

        def client_control(self, client):
            """Request for a spot for a client...
            We add dirt here.
            """
            building = self.building
            tier = building.tier or 1

            with self.res.request() as request:
                yield request

                self.clients_waiting.add(client)
                temp = "{color=[beige]}%s{/color} enters the %s." % (client.name, self.name)
                self.log(temp, True)

                dirt = 0
                #flag_name = "jobs_spent_in_{}".format(self.name)
                du_to_spend_here = self.time
                du_spent_here = 0
                client.du_without_service = 0

                while 1:
                    simpy_debug("Entering PublicBusiness(%s).client_control iteration at %s", self.name, self.env.now)

                    if client in self.clients_waiting:
                        simpy_debug("Client %s will wait to be served.", client.name)
                        yield self.env.timeout(1)
                        du_spent_here += 1
                        client.du_without_service += 1
                    else:
                        client.du_without_service = 0

                        simpy_debug("Client %s is about to be served.", client.name)
                        yield self.env.timeout(3)
                        du_spent_here += 3
                        #self.clients_being_served.remove(client)
                        self.clients_waiting.add(client)
                        dirt += randint(2, 3) # Move to business_control?

                        # Tips:
                        worker, effectiveness = client.served_by
                        client.served_by = ()
                        if effectiveness >= 150:
                            tips = tier*randint(2, 3)
                        elif effectiveness >= 100:
                            tips = tier*randint(1, 2)
                        else:
                            tips = 0
                        if tips:
                            for u in self.upgrades:
                                if isinstance(u, TapBeer) and dice(75):
                                    tips += tier
                            worker.up_counter("_jobs_tips", tips)

                        # And remove client from actively served clients by the worker:
                        worker.serving_clients.discard(client)

                    if client.du_without_service >= 2:
                        # We need a worker ASAP:
                        self.send_in_worker = True

                    if du_spent_here >= du_to_spend_here:
                        break

                    if client.du_without_service >= 5:
                        temp = "{color=[beige]}%s{/color} spent too long waiting for service!" % client.name
                        self.log(temp, True)
                        break

                building.moddirt(dirt)

                temp = "{} exits the {} leaving {} dirt behind.".format(
                                        set_font_color(client.name, "beige"), self.name, dirt)
                self.log(temp, True)

                #self.clients_being_served.discard(client)
                self.clients_waiting.discard(client)
                client.del_flag("jobs_busy")

                simpy_debug("Exiting PublicBusiness(%s).client_control iteration at %s", self.name, self.env.now)

        def add_worker(self, job):
            simpy_debug("Entering PublicBusiness(%s).add_worker at %s", self.name, self.env.now)
            # Get all candidates:
            ws = self.get_workers(job)
            if ws:
                w = ws.pop()
                self.active_workers.add(w)
                self.building.available_workers.remove(w)
                self.env.process(self.worker_control(w))
            else:
                temp = "{color=[red]}"
                temp += "Could not find an available {} worker".format(job)
                self.log(temp)
            simpy_debug("Exiting PublicBusiness(%s).add_worker at %s", self.name, self.env.now)

        def business_control(self):
            """This runs the club as a SimPy process from start to the end.
            """
            #counter = 0
            building = self.building
            #tier = building.tier
            job = self.jobs[0] # there is a single job per business at the moment -> the client should now what kind of worker is expected anyway

            while 1:
                simpy_debug("Entering PublicBusiness(%s).business_control iteration at %s", self.name, self.env.now)

                if self.send_in_worker: # Sends in workers when needed!
                    new_workers_required = max(1, len(self.clients_waiting)/5)
                    if DSNBR:
                        temp = "Adding {} workers to {}!".format(
                                set_font_color(new_workers_required, "green"),
                                self.name)
                        temp = temp + " ~ self.send_in_worker == {}".format(
                                    set_font_color(self.send_in_worker, "red"))
                        self.log(temp, True)
                    for i in range(new_workers_required):
                        self.add_worker(job)
                    self.send_in_worker = False

                # Could be flipped to a job Brawl event?:
                # if False:
                #     if counter < 1 and self.env.now > 20:
                #         counter += 1
                #         for u in building._businesses:
                #             if u.__class__ == WarriorQuarters:
                #                 process = u.request_action(building=building, start_job=True, priority=True, any=False, action="patrol")[1]
                #                 u.interrupt = process # New field to which we can bind a process that can be interrupted.
                #                 break
                #
                #     # testing interruption:
                #     if "process" in locals() and (counter == 1 and self.env.now > 40):
                #         counter += 1
                #         process.interrupt("fight")
                #         self.env.process(u.intercept(interrupted=True))
                # =====================================>>>

                # Every 5 DU
                if not self.env.now % 5:
                    if DSNBR:
                        temp = "Debug: {} capacity is currently in use.".format(
                                set_font_color(self.res.count, "red"))
                        temp = temp + " {} Workers are currently on duty in {}!".format(
                                set_font_color(len(self.active_workers), "blue"),
                                self.name)
                        siw_workers = len([w for w in building.available_workers if set(w.gen_occs).intersection(self.all_occs)])
                        temp = temp + " {} (gen_occ) workers are available in the Building for the job!".format(
                                set_font_color(siw_workers, "green"))
                        self.log(temp, True)

                    if not self.active_workers and not self.all_workers:
                        break

                simpy_debug("Exiting PublicBusiness(%s).business_control iteration at %s", self.name, self.env.now)
                yield self.env.timeout(1)

            # We remove the business from nd if there are no more strippers to entertain:
            temp = "There are no workers available in the {} so it is shutting down!".format(self.name)
            self.log(temp)
            building.nd_ups.remove(self)

        def worker_control(self, worker):
            self.log(self.intro_string % (worker.name), True)

            du_working = 35

            # We create the log object here! And start logging to it directly!
            job, building = self.jobs[0], self.building # a single job per business at the moment
            log = NDEvent(job=job, char=worker, loc=building, business=self)

            log.append(self.log_intro_string % (worker.name))
            log.append("\n")

            difficulty = building.tier
            effectiveness = job.effectiveness(worker, difficulty, log, False,
                                manager_effectiveness=building.manager_effectiveness)

            # Upgrade mods:
            # Move to Job method?
            eff_mod = 0
            for u in self.upgrades:
                eff_mod += getattr(u, "job_effectiveness_mod", 0)
            effectiveness += eff_mod

            if DSNBR:
                log.append("Debug: Her effectiveness: {}! (difficulty: {}, Tier: {})".format(
                                effectiveness, difficulty, worker.tier))

            # Actively serving these clients:
            can_serve = 5 # We consider max of 5
            worker.serving_clients = set() # actively serving these clients
            clients_served = [] # client served during the shift (all of them, for the report)

            while worker.jobpoints > 0 and du_working > 0:
                simpy_debug("Entering PublicBusiness(%s).worker_control iteration at %s", self.name, self.env.now)

                # Add clients to serve:
                for c in self.clients_waiting.copy():
                    if len(worker.serving_clients) < can_serve:
                        self.clients_waiting.remove(c)
                        #self.clients_being_served.add(c)
                        c.du_without_service = 0 # Prevent more worker from being called on duty.
                        c.served_by = (worker, effectiveness)
                        worker.serving_clients.add(c)
                        clients_served.append(c)
                    else:
                        break

                yield self.env.timeout(1)
                du_working -= 1

                worker.jobpoints -= len(worker.serving_clients)*2 # 2 jobpoints per client?

                simpy_debug("Exiting PublicBusiness(%s).worker_control iteration at %s", self.name, self.env.now)

            if clients_served:
                # wait for the clients to finish
                while worker.serving_clients:
                    yield self.env.timeout(1)

                if DSNBR:
                    temp = "Logging {} for {}!".format(self.name, worker.name)
                    self.log(temp, True)
                # Weird way to call job method but it may help with debugging somehow.
                work_method = getattr(job, self.job_method)
                work_method(worker, clients_served, effectiveness, log)

                earned = payout(job, effectiveness, difficulty, building,
                                self, worker, clients_served, log)
                temp = "{} earns {} by serving {} clients!".format(
                                worker.name, earned, self.res.count)
                self.log(temp, True)

                # Create the job report and settle!
                log.after_job()
                NextDayEvents.append(log)
            else:
                temp = "There were no clients for {} to serve".format(worker.name)
                self.log(temp, True)

            self.active_workers.remove(worker)
            building.available_workers.append(worker) # Put the worker back in the pool.
            temp = "{} is done with the job in {} for the day!".format(
                                worker.name,
                                self.name)
            temp = set_font_color(temp, "cadetblue")
            self.log(temp, True)

            simpy_debug("Leaving PublicBusiness(%s).worker_control at %s", self.name, self.env.now)

        def pre_nd(self):
            # Whatever we need to do at start of Next Day calculations.
            self.res = simpy.Resource(self.env, self.capacity)

        def post_nd(self):
            self.res = None
            self.is_running = False
            self.send_in_worker = False
            self.active_workers = set()
            self.clients = set()


    class OnDemandBusiness(Business):
        def __init__(self):
            super(OnDemandBusiness, self).__init__()

            self.type = "on_demand_service"
            self.workable = True
            self.active_workers = list()
            self.action = None # Action that is currently running! For example guard that are presently on patrol should still respond to act
                               # of violence by the customers, even thought it may appear that they're busy (in code).

            # SimPy and etc follows:
            self.time = 1 # Same.
            # We can bind an active process here if
            # it can be interrupted. I'ma an idiot... This needs to be reset.
            self.interrupt = None
            self.expands_capacity = False

        def get_strict_workers(self, job, power_flag_name, use_slaves=True):
            workers = set(self.get_workers(job, amount=float("inf"),
                           rule="strict",
                           use_slaves=use_slaves))

            if workers:
                # Do Disposition checks:
                job.settle_workers_disposition(workers, self)
                # Do Effectiveness calculations:
                self.calc_job_power(workers, job, power_flag_name)

            return workers

        def all_on_deck(self, workers, job, power_flag_name, use_slaves=True):
            # calls everyone in the building to clean it
            new_workers = self.get_workers(job, amount=float("inf"),
                            rule="loose", use_slaves=use_slaves)

            if new_workers:
                # Do Disposition checks:
                job.settle_workers_disposition(new_workers, self, all_on_deck=True)
                # Do Effectiveness calculations:
                self.calc_job_power(new_workers, job, power_flag_name)
            workers = workers.union(new_workers)

            # Throw in the manager:
            if self.building.works_other_jobs:
                manager = self.building.manager
                if manager:
                    workers.add(manager)

            return workers

        def calc_job_power(self, workers, job, power_flag_name,
                                remove_from_available_workers=True):
            building = self.building
            difficulty = building.tier

            for w in workers:
                if not w.flag(power_flag_name):
                    effectiveness_ratio = job.effectiveness(w, difficulty,
                            manager_effectiveness=building.manager_effectiveness)

                    if DEBUG_SIMPY:
                        devlog.info("{} Effectiveness: {}: {}".format(job.id,
                                            w.nickname, effectiveness_ratio))
                    value = -(5 * effectiveness_ratio)

                    for u in self.upgrades:
                        value += getattr(u, "job_power_mod", 0)

                    w.set_flag(power_flag_name, value)

                    # Remove from active workers:
                    if remove_from_available_workers:
                        building.available_workers.remove(w)

        def post_nd(self):
            # Resets all flags and variables after next day calculations are finished.
            self.interrupt = None


    class TaskBusiness(Business):
        """Base class upgrade for businesses that just need to complete a task, like FG, crafting and etc.
        """
        # For lack of a better term... can't come up with a better name atm.
        def __init__(self):
            super(TaskBusiness, self).__init__()
            self.workable = True
            self.res = None #*Throws an error?
