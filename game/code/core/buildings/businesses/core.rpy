init -12 python:
    #################################################################
    # BUILDING UPGRADE CLASSES:
    class CoreExtension(_object):
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
            self.duration = getattr(self, "duration", None)

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

            # If False, no clients are expected.
            # If all businesses in the building have this set to false, no client stream will be generated at all.
            self.expects_clients = False
            self.habitable = False # habitable/workable flags are exclusive (can not be True at the same time)
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
                self.exp_cap_duration = getattr(self, "exp_cap_duration", None)

                cap = self.capacity
                self.in_slots += cap*self.exp_cap_in_slots
                self.ex_slots += cap*self.exp_cap_ex_slots
                self.base_capacity = cap

            self.allowed_upgrades = getattr(self, "allowed_upgrades", [])
            self.in_construction_upgrades = list() # work (capacity expansion/upgrade) in progress. [("capacity"/upgrade), remaining days, job_effectiveness_mod]
            self.upgrades = list()
            self.job_effectiveness_mod = 0

        def can_close(self):
            # test if the business can be closed
            return True

        # Business MainUpgrade related:
        def build_upgrade(self, upgrade):
            building = self.building

            cost, materials, in_slots, ex_slots = upgrade.get_cost()
            self.in_slots += in_slots
            building.in_slots += in_slots
            self.ex_slots += ex_slots
            building.ex_slots += ex_slots

            building.pay_for_extension(cost, materials)

            duration = upgrade.duration
            if duration is None or duration[0] < 1:
                self.add_upgrade(upgrade)
            else:
                self.job_effectiveness_mod -= duration[1]
                self.in_construction_upgrades.append([upgrade, duration[0], duration[1]])

        def add_upgrade(self, upgrade):
            upgrade.building = self.building
            upgrade.business = self
            self.upgrades.append(upgrade)
            self.upgrades.sort(key=attrgetter("ID"), reverse=True)
            self.job_effectiveness_mod += getattr(upgrade, "job_effectiveness_mod", 0)

        def all_possible_extensions(self):
            # Named this was to conform to GUI (same as for Buildings)
            return self.allowed_upgrades

        def has_extension(self, upgrade):
            # Named this was to conform to GUI (same as for Buildings)
            return any(u.__class__ == upgrade for u in self.upgrades)

        def expand_capacity(self):
            cost, materials, in_slots, ex_slots = self.get_expansion_cost()
            building = self.building

            self.in_slots += in_slots
            building.in_slots += in_slots
            self.ex_slots += ex_slots
            building.ex_slots += ex_slots

            building.pay_for_extension(cost, materials)

            duration = self.exp_cap_duration
            if duration is None or duration[0] < 1:
                self.capacity += 1
            else:
                self.job_effectiveness_mod -= duration[1]
                self.in_construction_upgrades.append(["capacity", duration[0], duration[1]])

        def can_reduce_capacity(self):
            if not self.expands_capacity:
                return False
            if self.capacity <= 1: # simpy.Resource can not handle capacity == 0...
                return False
            if hero.gold < self.get_expansion_cost()[0]:
                return False
            if self.in_construction_upgrades:
                return False
            # these two should never happen, but check anyways...
            if self.in_slots < self.exp_cap_in_slots:
                return False  
            if self.ex_slots < self.exp_cap_ex_slots:
                return False
            return True

        def reduce_capacity(self):
            renpy.play("content/sfx/sound/world/purchase_1.ogg")

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
                char = next(iter(building.inhabitants))
                char.home = pytfall.streets

        def cancel_construction(self, icu):
            self.in_construction_upgrades.remove(icu)

            u, d, m = icu
            self.job_effectiveness_mod += m

            if u == "capacity":
                cost, materials, in_slots, ex_slots = self.get_expansion_cost()
            else:
                cost, materials, in_slots, ex_slots = u.get_cost()
            self.in_slots -= in_slots
            building.in_slots -= in_slots
            self.ex_slots -= ex_slots
            building.ex_slots -= ex_slots

        def get_client_count(self):
            """Returns amount of clients we expect to come here.

            Right now we base our best guess on time and cap.
            """
            # .7 is just 70% of absolute max (to make upgrades meaningful).
            # self.time is amount of time we expect to spend per client.
            if not self.time:
                raise Exception("Zero Modulo Division Detected #02")
            return 70*self.capacity/self.time # MAX_DU * 70%

        @property
        def env(self):
            return self.building.env

        def log(self, item, add_time=False):
            # Logs the text for next day event...
            self.building.log(item, add_time=add_time)

        @property
        def all_workers(self):
            # This may be a poor way of doing it because different upgrades could have workers with the same job assigned to them.
            # Basically what is needed is to allow setting a business to a worker as well as the general building if required...
            # And this doesn't work? workers are never populated???
            job = self.jobs[0] # FIXME one job per business
            return [i for i in self.building.available_workers if job.willing_work(i)]

        def get_workers(self, job, amount=None, rule="normal", client=None):
            """Tries to find workers for the given job.

            @param job: the job to find the workers for
            @param amount: the limit on the number of workers to be returned. Must not be 0.
            @param rule: Will use given rule and check it vs building rule, using only
                workers permitted.
            @param: client: try to find a good match to client,
                    expects a client (or any PytC instance with .likes set) object.
            """
            building = self.building

            rules = building.WORKER_RULES
            # Select the stricter rule:
            if rules.index(rule) > rules.index(building.workers_rule):
                rule = building.workers_rule
            if amount is None:
                # no limit -> use the most relaxed rule only
                rules = [rule]
                amount = -1

            rv = list()
            checked_workers = list()
            for r in rules:
                workers = building.available_workers
                if r == "strict":
                    workers = [i for i in workers if i.action == job] 
                elif r == "normal":
                    workers = [i for i in workers if job.want_work(i)]
                else: # r == loose
                    workers = [i for i in workers if job.willing_work(i)]
                workers = [w for w in workers if w not in checked_workers]
                checked_workers.extend(workers)

                shuffle(workers)
                while workers:
                    if client is not None:
                        # Attempts to match a client to a worker.
                        for w in workers[:]:
                            likes = client.likes.intersection(w.traits)
                            if not likes:
                                continue
                            if not self.check_worker_for_job(w, job):
                                workers.remove(w)
                                continue
                            slikes = ", ".join([str(l) for l in likes])
                            if dice(50):
                                temp = '%s liked %s for %s %s.' % (
                                    set_font_color(client.name, "beige"),
                                    set_font_color(w.nickname, "pink"),
                                    slikes, plural("trait", len(likes)))
                            else:
                                temp = '%s found %s %s in %s very appealing.' % (
                                    set_font_color(client.name, "beige"),
                                    slikes, plural("trait", len(likes)),
                                    set_font_color(w.nickname, "pink"))
                            self.log(temp)
                            client.set_flag("jobs_matched_traits", likes)
                            workers.remove(w)
                            break
                        else:
                            if not workers:
                                break
                            w = None
                    else:
                        w = None
                    if w is None:
                        w = workers.pop()
                        if not self.check_worker_for_job(w, job):
                            continue

                    rv.append(w)
                    amount -= 1
                    if amount == 0:
                        return rv

                if r == rule:
                    break

            return rv

        def check_worker_for_job(self, worker, job):
            """Checks if the worker is capable and willing to do the job.

            Removes worker from instances master list.
            Returns True is yes, False otherwise.
            """
            if worker.can_do_work(True) is not True:
                self.building.available_workers.remove(worker)

                temp = "%s is done working for the day." % worker.name
                self.log(set_font_color(temp, "cadetblue"))
                return False

            if not job.willing_work(worker):
                if DSNBR:
                    temp = 'Debug: {} worker (Occupations: {}) with action: {} refuses to do {}.'.format(
                            worker.nickname, ", ".join(list(str(t) for t in worker.occupations)),
                            action_str(worker), job.id)
                else:
                    temp = '%s refuses to do %s!' % (worker.name, job.id)
                self.log(set_font_color(temp, "red"))
                return False

            if DSNBR:
                temp = "Debug: {} worker (Occupations: {}) with action: {} is doing {}.".format(
                            worker.nickname, ", ".join(list(str(t) for t in worker.occupations)), action_str(worker), job.id)
                self.log(set_font_color(temp, "lawngreen"), True)
            return True

        # Runs before ND calcs stats for this building.
        def pre_nd(self):
            # Runs at the very start of execution of SimPy loop during the next day.
            return

        def post_nd(self):
            # Resets all flags and variables after next day calculations are finished.
            return

        def log_income(self, amount, reason=None):
            # Plainly logs income to the main building finances.
            if not reason:
                reason = self.name
            self.building.fin.log_logical_income(amount, reason)

        def inactive_process(self):
            temp = "%s is currently inactive, no actions will be conducted here!" % self.name
            self.log(temp)
            self.building.nd_ups.remove(self)

            yield self.env.exit()

        # SimPy:
        def business_control(self):
            """SimPy business controller.
            """
            raise Exception("The business_control method is not implemented for %s!" % self.name)

    class PrivateBusiness(Business):
        def __init__(self):
            super(PrivateBusiness, self).__init__()

            self.type = "personal_service"
            self.workable = True
            self.expects_clients = True

            # SimPy and etc follows:
            self.res = None # Restored before every job...
            self.time = 10 # Same

        def has_workers(self):
            job = self.jobs[0] # FIXME one job per business
            return any(job.willing_work(i) for i in self.building.available_workers)

        def business_control(self):
            while 1:
                yield self.env.timeout(self.time)

                if self.res.count == 0 and not self.has_workers():
                    break

            # We remove the business from nd if there are no more strippers to entertain:
            temp = "There are no workers available in the %s so it is shutting down!" % self.name
            self.log(temp)
            self.building.nd_ups.remove(self)

        def client_control(self, client):
            """Handles the client after a room is reserved...
            """
            raise Exception("client_control method/process must be implemented")

        def pre_nd(self):
            self.res = simpy.Resource(self.env, self.capacity)

        def post_nd(self):
            self.res = None


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
            self.has_tap_beer = False # cached result of check for TapBeer upgrade

        def client_control(self, client):
            """Handles the client after a spot is reserved...
            We add dirt here.
            """
            temp = "%s enters the %s." % (set_font_color(client.name, "beige"), self.name)
            self.log(temp, True)

            self.clients_waiting.add(client)

            tier = self.building.tier or 1
            du_to_spend_here = self.time
            dirt = du_spent_here = du_without_service = 0

            while 1:
                simpy_debug("Entering PublicBusiness(%s).client_control iteration at %s", self.name, self.env.now)

                yield self.env.timeout(1) # wait to be served
                if client in self.clients_waiting:
                    simpy_debug("Client %s is waiting to be served.", client.name)
                    du_spent_here += 1
                    du_without_service += 1
                else:
                    simpy_debug("Client %s is about to be served.", client.name)
                    yield self.env.timeout(3)

                    du_spent_here += 3
                    dirt += 3
                    du_without_service = 0

                    # Tips:
                    (worker, effectiveness), client.served_by = client.served_by, None
                    if effectiveness >= 100:
                        tips = tier*randint(1, 2)
                        if effectiveness >= 150:
                            tips += tier
                        if self.has_tap_beer and dice(75):
                            tips += tier
                        worker.up_counter("_jobs_tips", tips)

                    # And remove client from actively served clients by the worker:
                    worker.serving_clients.discard(client)
                    self.clients_waiting.add(client)

                if du_spent_here >= du_to_spend_here:
                    break

                if du_without_service >= 2:
                    if du_without_service >= 5:
                        temp = "%s spent too long waiting for service!" % set_font_color(client.name, "beige")
                        self.log(temp, True)
                        break

                    # We need a worker ASAP:
                    self.send_in_worker = True

            dirt = randint(0, dirt)
            self.building.moddirt(dirt) # Move to business_control?)

            temp = "%s exits the %s leaving %s dirt behind." % (
                                    set_font_color(client.name, "beige"), self.name, dirt)
            self.log(temp, True)

            #self.clients_being_served.discard(client)
            self.clients_waiting.discard(client)

            simpy_debug("Exiting PublicBusiness(%s).client_control iteration at %s", self.name, self.env.now)

        def add_worker(self, job):
            simpy_debug("Entering PublicBusiness(%s).add_worker at %s", self.name, self.env.now)
            # Get all candidates:
            ws = self.get_workers(job, amount=1)
            if ws:
                w = ws.pop()
                self.active_workers.add(w)
                self.building.available_workers.remove(w)
                self.env.process(self.worker_control(w))
            else:
                temp = "Could not find an available %s." % job.id
                self.log(set_font_color(temp, "red"))
            simpy_debug("Exiting PublicBusiness(%s).add_worker at %s", self.name, self.env.now)

        def business_control(self):
            """This runs the club as a SimPy process from start to the end.
            """
            #counter = 0
            building = self.building
            job = self.jobs[0] # FIXME one job per business, is should be client specific anyway

            while 1:
                simpy_debug("Entering PublicBusiness(%s).business_control iteration at %s", self.name, self.env.now)

                if self.send_in_worker: # Sends in workers when needed!
                    new_workers_required = (4+len(self.clients_waiting))/5
                    if DSNBR:
                        temp = "Adding {} workers to {}!".format(
                                set_font_color(new_workers_required, "green"),
                                self.name)
                        temp += " ~ self.send_in_worker == {}".format(
                                    set_font_color(self.send_in_worker, "red"))
                        self.log(temp, True)
                    for i in range(new_workers_required):
                        self.add_worker(job)
                    self.send_in_worker = False

                # Every 5 DU
                if not self.env.now % 5:
                    if DSNBR:
                        temp = "Debug: {} capacity is currently in use.".format(
                                set_font_color(self.res.count, "red"))
                        temp += " {} Workers are currently on duty in {}!".format(
                                set_font_color(len(self.active_workers), "blue"),
                                self.name)
                        siw_workers = len([w for w in building.available_workers if job.willing_work(w)])
                        temp += " {} (gen_occ) workers are available in the Building for the job!".format(
                                set_font_color(siw_workers, "green"))
                        self.log(temp, True)

                    if not self.active_workers and not self.all_workers:
                        break

                simpy_debug("Exiting PublicBusiness(%s).business_control iteration at %s", self.name, self.env.now)
                yield self.env.timeout(1)

            # We remove the business from nd if there are no more strippers to entertain:
            temp = "There are no workers available in the %s so it is shutting down!" % self.name
            self.log(temp)
            building.nd_ups.remove(self)

        def worker_control(self, worker):
            self.log(self.intro_string % (worker.name), True)

            du_working = min(35, 100 - self.env.now) # FIXME MAX_DU ?

            # We create the log object here! And start logging to it directly!
            job, building = self.jobs[0], self.building # a single job per business at the moment
            log = NDEvent(job=job, char=worker, loc=building, business=self)

            job.settle_workers_disposition(worker, log)

            difficulty = building.tier
            effectiveness = job.effectiveness(worker, difficulty, log, building.manager_effectiveness)

            # Upgrade mods:
            effectiveness += self.job_effectiveness_mod

            if DSNBR:
                log.append("Debug: Her effectiveness: {}! (difficulty: {}, Tier: {})".format(
                                effectiveness, difficulty, worker.tier))

            # Actively serving these clients:
            can_serve = 5 # We consider max of 5
            worker.serving_clients = set() # actively serving these clients
            clients_served = [] # client served during the shift (all of them, for the report)

            while worker.PP > 0 and du_working > 0:
                simpy_debug("Entering PublicBusiness(%s).worker_control iteration at %s", self.name, self.env.now)

                # Add clients to serve:
                for c in self.clients_waiting.copy():
                    if len(worker.serving_clients) < can_serve:
                        self.clients_waiting.remove(c)
                        worker.serving_clients.add(c)
                        clients_served.append(c)

                        c.served_by = (worker, effectiveness)
                    else:
                        break

                simpy_debug("Exiting PublicBusiness(%s).worker_control iteration at %s", self.name, self.env.now)
                yield self.env.timeout(1)
                du_working -= 1

                worker.PP -= len(worker.serving_clients)*2 # 2 partial AP per client?

            if clients_served:
                # wait for the clients to finish
                while worker.serving_clients:
                    yield self.env.timeout(1)

                if DSNBR:
                    temp = "Logging {} for {}!".format(self.name, worker.name)
                    self.log(temp, True)
                # Weird way to call job method but it may help with debugging somehow.
                job.log_work(worker, clients_served, effectiveness, log)

                earned = payout(job, effectiveness, difficulty, building,
                                self, worker, clients_served, log)
                temp = len(clients_served)
                temp = "%s earns %s by serving %d %s!" % (set_font_color(worker.name, "pink"),
                                                               set_font_color("%d Gold" % earned, "gold"), temp, plural("client", temp))
                self.log(temp, True)

                # Create the job report and settle!
                log.after_job()
                NextDayEvents.append(log)
            else:
                temp = "There were no clients for %s to serve" % worker.name
                self.log(temp, True)

            self.active_workers.remove(worker)
            building.available_workers.append(worker) # Put the worker back in the pool.
            temp = "%s is finished with %s shift in %s!" % (worker.name, worker.pp, self.name)
            temp = set_font_color(temp, "cadetblue")
            self.log(temp, True)

            simpy_debug("Leaving PublicBusiness(%s).worker_control at %s", self.name, self.env.now)

        def pre_nd(self):
            # Whatever we need to do at start of Next Day calculations.
            self.res = simpy.Resource(self.env, self.capacity)
            self.has_tap_beer = self.has_extension(TapBeer)

        def post_nd(self):
            self.res = None
            self.send_in_worker = False
            self.active_workers = set()

    class OnDemandBusiness(Business):
        def __init__(self):
            super(OnDemandBusiness, self).__init__()

            self.type = "on_demand_service"
            self.workable = True

            # SimPy and etc follows:
            self.expands_capacity = False

        def get_strict_workers(self, job, power_flag_name, log):
            workers = set(self.get_workers(job, rule="strict"))

            if workers:
                # Do Disposition checks:
                job.settle_workers_disposition(workers, self)
                # Do Effectiveness calculations:
                self.calc_job_power(workers, job, power_flag_name, log)

            return workers

        def all_on_deck(self, workers, job, power_flag_name, log):
            # calls everyone in the building to clean it
            new_workers = self.get_workers(job, rule="loose")

            if new_workers:
                # Do Disposition checks:
                job.settle_workers_disposition(new_workers, self, all_on_deck=True)
                # Do Effectiveness calculations:
                self.calc_job_power(new_workers, job, power_flag_name, log)
            workers = workers.union(new_workers)

            # Throw in the manager:
            if self.building.works_other_jobs:
                workers.update(self.building.available_managers)

            return workers

        def calc_job_power(self, workers, job, power_flag_name, log):
            building = self.building
            difficulty = building.tier

            for w in workers:
                if not w.flag(power_flag_name):
                    effectiveness = job.effectiveness(w, difficulty, log, building.manager_effectiveness)

                    # Upgrade mods:
                    effectiveness += self.job_effectiveness_mod

                    if DEBUG_SIMPY:
                        devlog.info("{} Effectiveness: {}: {}".format(job.id,
                                            w.nickname, effectiveness))

                    value = -round_int(effectiveness / 20.0)
                    w.set_flag(power_flag_name, value)

                    # Remove from active workers:
                    building.available_workers.remove(w)


    class TaskBusiness(Business):
        """Base class upgrade for businesses that just need to complete a task, like FG, crafting and etc.
        """
        # For lack of a better term... can't come up with a better name atm.
        def __init__(self):
            super(TaskBusiness, self).__init__()
            self.workable = True
            self.res = None #*Throws an error?
