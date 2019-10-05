init -6 python: # WorkshopGuild and its Events
    # ======================= (Simulated) Arena code =====================>>>
    class WorkshopEvent(_object):
        def __init__(self, proc, team):
            self.name = proc["id"]   # name of the event
            self.type = proc["type"] # type of the event (to filter)
            self.repeat = False      # restart the event when done TODO timed restart?
            self.report = False      # add green flag when done
            self.warn = True         # add red flag when fails  
            self.sell = False        # sell the products when done
            self.team = team         # the team working on the project

            self.materials = proc.get("materials", {})# dict of required materials
            self.upgrades = proc.get("upgrades", [])  # list of required upgrades
            self.tasks = proc["tasks"]                # the difficulty of the sub-tasks
            self.PP = int(proc["ap_cost"] * 100)      # 'time'-cost PP_PER_AP
            self.dirt_mod = proc.get("dirt_mod", 0)   # created dirt per 5 DU
            self.tools = proc.get("tools", {})        # dict of required tools while crafting
            self.capacity = proc.get("capacity", 0)   # required space while crafting
            self.wait_days = proc.get("wait_days", 0)  # time necessary to finalize the products
            #self.wait_tools                          # dict of required tools while waiting
            self.wait_cap = proc.get("wait_cap", 0)   # required space while waiting

            products = proc["products"]
            self.products = products  # result of the event
            products = [[i, None] for i in products if i not in items]
            self.pro_teams = products # the teams working on the products of this project

            self.ready = None     # the day the products are ready    

    class WorkshopGuild(TaskBusiness):
        def __init__(self):
            super(WorkshopGuild, self).__init__()

            # Global Values that have effects on the whole business.
            self.teams = list() # List to hold all the teams formed in this guild.
            self.events = list() # List to hold all (active) events.
            self.warn_on_cancel = True # whether to warn the player of lost material when a event is cancelled

            self.teams.append(Team(name="Hephaestie")) # sample team

            # gui
            self.view_mode = "work"   # the selected tab
            #  team screen
            #self.selected_team initialized later 
            #self.workers initialized later
            #self.guild_teams initialized later
            #  work screen
            self.event_type = None

            # ND
            #self.reset_nd_fields() 

        #def reset_nd_fields(self):
        #    pass #self.earned = 0

        def can_close(self):
            return not any((p.ready is not None for p in self.events))

        def idle_teams(self):
            active_teams = [p.team for p in self.events]
            return [t for t in self.teams if t not in active_teams]

        def load_gui(self):
            # Looks pretty ugly... this might be worth improving upon just for the sake of esthetics.
            _teams = self.teams
            _chars = [w for w in self.building.all_workers if w != hero and WorkshopTask.willing_work(w) and w.is_available]

            # filter chars
            idle_chars = list(f for t in _teams for f in t)
            _chars = [w for w in _chars if w not in idle_chars]

            # filter teams
            _teams = self.idle_teams()

            # load gui elements
            self.workers = CharsSortingForGui(_chars, 18, occ_filters={"Combatant", "Server"})
            self.guild_teams = PagerGui(_teams, page_size=9)
            self.gui_events = PagerGui(self.events[:], page_size=6)

            recipes = [i for i in crafting_recipes if i["tier"] <= self.building.tier]
            self.gui_recipes = recipes

            options = [i["type"] for i in recipes]
            options = [(i, i.capitalize()) for i in options]
            options.sort(key=itemgetter(1))
            options.append((None, "-"))
            self.gui_options = OrderedDict(options)

            self.selected_team = None

        def clear_gui(self):
            """Clear GUI-object to free memory and eliminate dead references
                @TODO merge with EG.clear_gui?
            """
            self.workers = None
            self.guild_teams = None
            self.gui_events = None
            self.gui_recipes = None
            self.gui_options = None

        # FIXME begin: copy-paste from the gladiators-guild
        def update_teams(self):
            gt = self.guild_teams
            gt.pager_content = self.idle_teams()
            gt.page = min(gt.page, gt.max_page())

        @staticmethod
        def assign_workers(chars):
            """
            Assign the list/set/tuple of chars to the task if available, 
            otherwise report an error.
            :param chars: the characters to assign
            """
            msg = None
            for c in chars:
                if not c.is_available:
                    if msg is None:
                        msg = "%s is currently unavailable!" % c.name
                    else:
                        msg = "Some of your workers are currently unavailable!"
                    continue
                c.set_task(WorkshopTask)
            return msg

        def unassign_workers(self, chars):
            """
            Unassign workers (chars) in case an task is removed.
            :param chars: the characters to consider
            """
            all_chars = [c for p in self.events if p.ready is None for c in p.team]

            for c in chars:
                if c not in all_chars and c.task == WorkshopTask:
                    c.set_task(None)

        @staticmethod
        def battle_ready(char):
            """
            Return whether the character is available in the guild.
            """
            return char.employer is hero and char.is_available

        # Teams control/sorting/grouping methods:
        def new_team(self, name):
            t = Team(name=name)
            self.add_team(t)
            self.guild_teams.pager_content.append(t)

        def add_team(self, t):
            self.teams.append(t)

        def remove_team(self, t):
            self.teams.remove(t)
            self.guild_teams.pager_content.remove(t)

        def teams_to_fight(self):
            # Returns a list of teams that can be launched on an exploration run.
            # Must have at least one member and NOT already running exploration!
            return [t for t in self.teams if t and all((self.battle_ready(f) for f in t))]

        def filter(self):
            events = self.events
            type = self.event_type
            if type is None:
                events = events[:]
            else:
                events = [p for p in events if p.type == type]
            ge = self.gui_events
            ge.pager_content = events
            ge.page = min(ge.page, ge.max_page())
        # FIXME end: copy-paste from the gladiators-guild

        def toggle_repeat(self, p):
            p.repeat = not p.repeat

        def toggle_sell(self, p):
            p.sell = not p.sell

        def toggle_report(self, p):
            p.report = not p.report

        def toggle_warn(self, p):
            p.warn = not p.warn

        # Event-Scheduling
        def schedule(self, rel_evt):
            team = self.selected_team

            event = renpy.call_screen("crafting_tasks", team=team, type=self.event_type)
            if not event:
                return

            event = WorkshopEvent(event, team)
            events = self.events
            ge = self.gui_events
            if rel_evt is None:
                events.append(event)
                ge.pager_content.append(event)
                ge.page = ge.max_page()
            else:
                idx = events.index(rel_evt) 
                events.insert(idx, event)
                
                events = ge.pager_content
                idx = events.index(rel_evt)
                events.insert(idx, event)

            self.reschedule_event(event)
            self.update_teams()

        def reschedule_event(self, proc):
            msg = self.assign_workers(proc.team)
            if msg is not None:
                PyTGFX.message(msg) # continue anyway, this is just a warning for the moment

        def remove_event(self, e):
            if e.ready is not None and self.warn_on_cancel:
                # the process is started -> ask for confirmation
                if not renpy.call_screen("yesno_prompt",
                                 message="The crafting process (%s) is started. Are you sure you want to discard the related materials?" % e.name,
                                 yes_action=Return(True), no_action=Return(False)):
                    return

            self.events.remove(e)
            ge = self.gui_events
            ge.pager_content.remove(e)
            ge.page = min(ge.page, ge.max_page())

            self.unassign_workers(e.team)
            self.update_teams()

        def change_prio(self, proc, delta):
            events = self.gui_events.pager_content
            idx = events.index(proc)
            rel_evt = events[idx+delta]
            events[idx+delta] = proc
            events[idx] = rel_evt

            events = self.events
            idx = events.index(proc)
            rel_idx = events.index(rel_evt)
            events[idx] = rel_evt
            events[rel_idx] = proc

        # SimPy methods:
        def get_team_ability(self, team, pp, tasks, mod, txt, me):
            # Effectiveness (Ability):
            du, pps = 0, []
            for char, difficulty in zip(team, tasks):
                if char.task != WorkshopTask:
                    return 0, "%s is not assigned to work on %s task." % (char.name, char.pd)

                effectiveness = WorkshopTask.effectiveness(char, difficulty, txt, me)

                # Upgrade mods:
                effectiveness += self.job_effectiveness_mod

                # convert to fraction
                effectiveness *= mod / 100.0

                if effectiveness == 0:
                    return 0, "%s did not feel %s is up to the assigned task. Maybe you should find an easier job for %s." % (char.nickname, char.p, char.op)

                cdu = round_int(pp / effectiveness)
                if char.PP < cdu:
                    return 0, "%s was too tired to start working on %s assigned task." % (char.nickname, char.pd)

                pps.append(cdu)
                cdu = cdu * 100 / char.setPP # MAX_DU
                if cdu == 0:
                    cdu = 1
                if cdu <= du:
                    continue

                if du > 100: # MAX_DU
                    # should not happen too often. only if setPP is lower than PP
                    return 0, "The task of %s would have taken more than a day to finish. %s decided to postpone it." % (char.nickname, char.pC)

                du = cdu

            return du, pps

        @staticmethod
        def schedule_nd_job(proc, length, req_tools, capacities, workers, av_tools):
            """
            @TODO implement a more efficient algorithm? cache the space 'matrix'?

            :param proc: the task to add
            :param length: the length of the task in blocks
            :param req_tools: the required tools from the buildings inventory
            :param capacities: the available capacities of the business (per block) 
            :param workers: the scheduled workers (per block)
            :param av_tools: the available tools in the buildings inventory (per block)
            """
            pcap = proc.capacity
            team = proc.team
            workspace = [(1 if pcap > cap else 0) for cap in capacities]
            for idx, ws in enumerate(workers):
                if any(w in ws for w in team):
                    workspace[idx] = 2
            for idx, tools in enumerate(av_tools):
                if any(tools[tool] < num for tool, num in req_tools.iteritems()):
                    workspace[idx] = 3
            workspace.pop()

            wcap = proc.wait_cap
            if wcap == 0:
                # no waiting for the product -> do the job as soon as possible
                for idx in xrange(len(workspace) - length + 1):
                    for j in xrange(idx, idx + length):
                        if workspace[j] != 0:
                            break
                    else:
                        # reserve the resources
                        for j in xrange(idx, idx + length):
                            capacities[j] -= pcap
                            tools = av_tools[j]
                            for tool, num in req_tools.iteritems():
                                tools[tool] -= num
                            workers[j].update(team)

                        # create the job 
                        nd_job = object()
                        nd_job.proc = proc
                        nd_job.start = idx
                        nd_job.end = idx + length
                        nd_job.running = False
                        return nd_job
            else:
                # wait is necesaary after the task -> do the job as late as possible
                for idx in xrange(len(workspace), length - 1, -1):
                    if capacities[idx] < wcap:
                        return "The product of %s could not have been stored properly, so %s decided to postpone the task." % (proc.name, itemize([w.nickname for w in team]))
                    # TODO wait_tools?
                    for j in xrange(idx - length, idx):
                        if workspace[j] != 0:
                            break
                    else:
                        # reserve the resources
                        for j in xrange(idx - length, idx):
                            capacities[j] -= pcap
                            tools = av_tools[j]
                            for tool, num in req_tools.iteritems():
                                tools[tool] -= num
                            workers[j].update(team)

                        for j in xrange(idx, len(capacities)):
                            capacities[j] -= wcap
                            # TODO wait_tools?

                        # create the job 
                        nd_job = object()
                        nd_job.proc = proc
                        nd_job.start = idx - length
                        nd_job.end = idx
                        nd_job.running = False
                        return nd_job

            if all(w == 3 for w in workspace):
                msg = "There was not enough tools in the inventory of the building to proceed with the %s, so %s decided to postpone the task." % (proc.name, itemize([w.nickname for w in team]))
            elif any(w == 2 for w in workspace):
                if len(team) == 1:
                    w = team[0]
                    msg = "%s could not fit the task of %s in %s schedule, so %s decided to postpone it." % (w.nickname, proc.name, w.pd, w.p)
                else:
                    msg = "%s could not fit the task of %s in their schedule, so they decided to postpone it." % (itemize([w.nickname for w in team]), proc.name)                
            else:
                msg = "The capacity of the business was enough to proceed with the %s, so %s decided to postpone the task." % (proc.name, itemize([w.nickname for w in team]))
            return msg

        def business_control(self):
            """SimPy business controller.
            """
            building = self.building

            workers = set()
            log = NDEvent(type="workshopndreport", job=WorkshopTask, loc=building, team=workers, business=self)
            #self.nd_log = log

            temp = "Report of %s in %s!\n" % (self.name, building.name)
            log.append(temp)

            cap = self.capacity
            events = self.events
            # check reserved capacity of the waiting projects
            for p in events:
                if p.ready is None:
                    continue
                # the process is started
                if cap < p.wait_cap:
                    log.red_flag = True
                    msg = "There was not enough space to store the materials of %s. They ended up in a landfill." % p.name
                    log.append(set_font_color(msg, "red"))
                    p.ready = -1
                # TODO check wait_tools?
                else:
                    cap -= p.wait_cap

            # create the work-matrix
            # PRECISION = 5
            # NUM_BLOCKS = 21 # (MAX_DU / precision) + 1
            cap = [cap] * 21 # NUM_BLOCKS
            tools = [dict() for i in xrange(21)] # the available tools from the building's inventory NUM_BLOCKS
            bws = [set() for i in xrange(21)] # workers per block NUM_BLOCKS

            # calculate mod
            mod = building.get_dirt_percentage()
            if mod < 25:
                mod = 1
            else:
                mod = get_linear_value_of(mod, 25, 1.0, 100, .2)

            # schedule the events
            jobs = []
            for p in events:
                if p.ready is not None:
                    continue
                # the process is not started
                # - check required materials
                inv = building.inventory
                team = p.team
                for m, num in p.materials.iteritems():
                    if inv[m] < num:
                        # FIXME use materials from non-waiting processes?
                        temp = "%s could not start to work on task %s due to the missing %s (Required: %d, Found: %d)." % (itemize([w.nickname for w in team]), p.name, m, num, inv[m])
                        if p.warn:
                            log.red_flag = True
                            temp = set_font_color(temp, "red")
                        log.append(temp)
                        inv = None
                        break
                if inv is None:
                    continue
                # - check required extensions
                for u in p.upgrades:
                    if not self.has_extension(u):
                        temp = "%s could not start to work on task %s due to the missing %s." % (itemize([w.nickname for w in team]), p.name, u.name)
                        if p.warn:
                            log.red_flag = True
                            temp = set_font_color(temp, "red")
                        log.append(temp)
                        inv = None
                        break
                if inv is None:
                    continue
                # - check workers
                du, pps = self.get_team_ability(team, p.PP, p.tasks, mod, log, building.manager_effectiveness)
                if du == 0:
                    if p.warn:
                        log.red_flag = True
                        pps = set_font_color(pps, "red")
                    log.append(pps)
                    continue
                # - check required tools
                b_tools = {}
                for t, num in p.tools.iteritems():
                    t = items[t]
                    for c in team:
                        num -= count_owned_items(t, c)
                        if num <= 0:
                            break
                    else:
                        b_tools[t] = num
                        # lazy init the tools-dicts
                        if t not in tools[0]:
                            num = inv[t]
                            for tt in tools:
                                tt[t] = num
                # add entry to the work-matrix
                du = int(math.ceil(du/5.0)) # PRECISION
                job = self.schedule_nd_job(p, du, b_tools, cap, bws, tools)
                if isinstance(job, basestring):
                    if p.warn:
                        log.red_flag = True
                        job = set_font_color(job, "red")
                    log.append(job)
                    continue

                # convert blocks to DU
                job.start *= 5 # PRECISION
                job.end *= 5   # PRECISION

                jobs.append(job)

                # remove materials
                for m, num in p.materials.iteritems():
                    inv.remove(m, num)

                # adjust PPs, register jobpoints
                key = "jp_crafting:%s" % max(p.tasks)
                for w, pp in zip(team, pps):
                    w.PP -= pp
                    w.up_counter(key, pp)
                    workers.add(w)

            jobs.sort(key=attrgetter("start"))
            #if True: #DEBUG_ND:
            #    for job in jobs:
            #        temp = "%s is scheduled from block %s to block %s for %s." % (job.proc.name, job.start, job.end, ", ".join([w.nickname for w in job.proc.team]))
            #        devlog.warn(temp)
            #        #nd_debug(temp)
                
            wlen = len(workers)
            temp = "%s %s are scheduled to work in the workshop.\n" % (set_font_color(wlen, "lightgreen"), plural("Employee", wlen))
            log.append(temp)

            # run the scheduled events
            while 1:
                now = self.env.now
                simpy_debug("Entering Workshop.business_control at %s", now)

                dirt = 0
                for job in jobs:
                    s = job.running
                    if s is None:
                        continue # the job is done
                    if job.start > now:
                        continue # the job is scheduled for later

                    p = job.proc
                    if s is False:
                        temp = "%s started to work on %s." % (itemize([w.nickname for w in p.team]), p.name)
                        self.log(log, temp, now)
                        job.running = True

                    # create dirt
                    dirt += p.dirt_mod

                    if job.end > now:
                        continue # the job is still running

                    temp = "%s finished the work on %s." % (itemize([w.nickname for w in p.team]), p.name)
                    self.log(log, temp, now)
                    job.running = None # job is done

                    w = p.wait_days
                    if w != 0:
                        msg = choice(["It takes %d %s till the process is finished.",
                                      "The process takes another %d %s till it is finished.",
                                      "It needs %d %s until the job can be called done.",
                                      "You need to wait %s %s for the final product.",
                                      "You have to wait %s %s for the finished product."])
                        log.append(msg % (w, plural("day", w)))
                    p.ready = day + w

                building.moddirt(dirt)
                        
                if now >= 100: # MAX_DU
                    break

                simpy_debug("Exiting Workshop.business_control at %s", now)
                yield self.env.timeout(5)

            # filter the events
            discard, create = [], []
            for p in events:
                ready = p.ready
                if ready is None or ready > day:
                    continue
                if ready != -1:
                    # the products are ready
                    if p.report:
                        log.green_flag = True
                        msg = "The process %s is finished." % p.name
                        log.append(set_font_color(msg, "green"))
                    inv = getattr(building, "inventory", hero.inventory)
                    for product, num in p.products.iteritems():
                        temp = items.get(product, None)
                        if temp is not None:
                            if p.sell:
                                temp = int(temp.price*pytfall.shops_stores["General Store"].sell_margin)
                                temp *= num
                                log.earned += temp
                                hero.add_money(temp, "Workshop")
                            else:
                                inv.append(temp, num)
                    if p.pro_teams:
                        create.append(p)

                discard.append(p)

            # add new events
            for proc in create:
                idx = events.index(proc) + 1
                new_procs = [WorkshopEvent(crafting_recipes[p], team) for p, team in proc.pro_teams]
                events[idx:idx] = new_procs

                for p in new_procs:
                    msg = self.assign_workers(p.team)
                    if msg is not None:
                        log.red_flag = True
                        msg = "Failed to completely schedule new task %s of %s. " % (p.name, itemize([w.nickname for w in p.team])) + msg
                        log.append(msg)

            # remove obsolete events
            for p in discard:
                events.remove(p)

            # Rewards:
            for w in workers:
                ap_used = exp_rew = 0
                jp_flags = [] 
                for flag, val in w.flags.iteritems():
                    if flag.startswith("jp_crafting"):
                        jp_flags.append(flag)
                        flag = float(flag.split(":")[1])
                        val /= 100.0
                        exp_rew += exp_reward(w, flag, exp_mod=val)
                        ap_used += val

                log.logws("vitality", round_int(ap_used*-5), w)
                log.logws("crafting", randfloat(ap_used), w)
                log.logws("refinement", randfloat(ap_used/4), w)
                log.logws("attack", randfloat(ap_used/2), w)
                log.logws("agility", randfloat(ap_used/2), w)
                log.logws("intelligence", randfloat(ap_used/4), w)
                log.logws("exp", exp_rew, w)
                for flag in jp_flags:
                    w.del_flag(flag)

            # release chars FIXME ND of the chars might complain about missing assignment, etc..?
            self.unassign_workers(workers)

            # Next Day Report:

            # Build an image combo for the report:
            img = choice(["content/gfx/bg/locations/workshop.webp",
                          "content/gfx/bg/buildings/workshop.webp"])
            log.img = nd_report_image(img, workers, "cleaning", exclude=["nude", "sex"]) # FIXME proper tag?

            log.after_job()
            NextDayEvents.append(log)
            #del self.nd_log

            #self.reset_nd_fields()

        def log(self, log, text, time):
            # Logs the text for next day event... # FIXME similar to log of Building, log of Clinic
            # try to create a timestamp between 9:00 and 19:00 assuming env.now is between 0 and 100 MAX_DU
            text = "%02d:%02d - %s" % (9+time/10,(time*6)%60, text)
            log.append(text)
