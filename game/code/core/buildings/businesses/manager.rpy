# Manager stuff goes here, will prolly be only one function but it doesn't fit anywhere else.
init -5 python:
    class Manager(_object):
        pass # obsolete
    class ManagerJob(Job):
        """This is the manager Job, so far it just creates the instance we can use to assign the job.

        - Later we may use this to do mod stats and level up Managers somehow...
        """
        def __init__(self):
            super(ManagerJob, self).__init__()
            self.id = "Manager"
            self.type = "Management"

            # Traits/Job-types associated with this job:
            self.occupations = ["Specialist"] # General Strings likes SIW, Combatant, Server...
            self.occupation_traits = [traits["Manager"]] # Corresponding traits...
            self.aeq_purpose = 'Manager'
            self.desc = "Manages your business, helping workers in various ways and improving their performance."

            self.base_skills = {"management": 80, "refinement": 20}
            self.base_stats = {"character": 40, "intelligence": 60}

            self.allowed_status = ["free"]

    def manager_pre_nd(building):
        if not building.needs_manager:
            return

        workers = building.available_workers

        mj = simple_jobs["Manager"]
        managers = [w for w in workers if w.action == mj]

        effectiveness = 0
        if managers:
            for m in managers:
                m._dnd_effectiveness = mj.effectiveness(m, building.tier, None, False)
                m._dnd_mlog = NDEvent(job=mj, char=m, loc=building)
                m._dnd_jobpoints = m.jobpoints

                workers.remove(m)

            managers.sort(key=attrgetter("_dnd_effectiveness"))
            effectiveness = managers[-1]._dnd_effectiveness
            building.log("This building is managed by {} at {}% effectiveness!".format(
                    managers[-1].name, effectiveness))
        else:
            building.log("This building has no manager assigned to it.")

        building.manager_effectiveness = effectiveness
        building.available_managers = managers

    def manager_process(env, building):
        managers = getattr(building, "available_managers", None)
        if not managers:
            return

        building._dnd_managers = managers[:]
        manager = managers.pop()
        effectiveness = manager._dnd_effectiveness
        #building.manager_effectiveness = effectiveness
        building._dnd_manager = manager
        manager._dnd_mlog.append("%s is overseeing %s!" % (manager.name, building.name))
        #building.log("%s is overseeing the building!" % manager.name)

        # Special bonus to JobPoints (aka pep talk) :D
        if building.init_pep_talk and manager.jobpoints >= 10:
            mp_init_jp_bonus(manager, building, effectiveness)

        cheered_up_workers = set()

        while (1):
            yield env.timeout(5)
            simpy_debug("Entering manager_process at %s", env.now)
            # select a new manager if the current one is exhausted
            if manager.jobpoints <= 10:
                if managers:
                    manager = managers.pop()
                    effectiveness = manager._dnd_effectiveness
                    building.manager_effectiveness = effectiveness
                    building._dnd_manager = manager
                    manager._dnd_mlog.append("%s is overseeing %s!" % (manager.name, building.name))
                    building.log("From now on %s is overseeing the building!" % manager.name)
                else:
                    building._dnd_manager = None
                    building.manager_effectiveness = 0
                    break

            # Special direct bonus to tired/sad characters
            #c1 = not env.now % 5
            if building.cheering_up and manager.jobpoints > 10 and dice(effectiveness-50):
                workers = [w for w in building.available_workers if
                           w != manager and
                           w not in cheered_up_workers and
                           (check_stat_perc(w, "joy", .5) or
                           check_stat_perc(w, "vitality", .3))]

                if workers:
                    worker = choice(workers)
                    cheered_up_workers.add(worker)

                    give_joy = check_stat_perc(worker, "joy", .5)
                    give_vit = check_stat_perc(worker, "vitality", .3)
                    if give_joy:
                        handle = "sad"
                    else:
                        handle = "tired"
                    temp0 = "%s noticed that %s looks a bit %s." % (manager.nickname, worker.nickname, handle)

                    if give_joy and give_vit:
                        bonus_str = "(+10% Joy, +15% Vitality)"
                        mod_by_max(worker, "joy", .1)
                        mod_by_max(worker, "vitality", .15)
                    elif give_joy:
                        bonus_str = "(+20% Joy)"
                        mod_by_max(worker, "joy", .2)
                    elif give_vit:
                        bonus_str = "(+30% Vitality)"
                        mod_by_max(worker, "vitality", .3)

                    temp1 = " Your manager cheered %s up. %s" % (worker.op, set_font_color(bonus_str, "lawngreen"))
                    manager._dnd_mlog.append(temp0+temp1)

                    building.log("Your manager cheered up %s." % worker.name)

                    manager.jobpoints -= 10

            simpy_debug("Exiting manager_process at %s", env.now)


    def mp_init_jp_bonus(manager, building, effectiveness):
        # Special bonus to JobPoints (aka pep talk) :D
        init_jp_bonus = effectiveness-95
        if init_jp_bonus <= 0:
            return

        init_jp_bonus /= 100.0
        if init_jp_bonus > .3: # Too much power otherwise...
            init_jp_bonus = .3
        elif init_jp_bonus < .05: # Less than 5% is absurd...
            init_jp_bonus = .05

        workers = building.available_workers
        if workers:
            # Bonus to the maximum amount of workers:
            max_job_points = manager.jobpoints*.5
            per_worker = 10
            max_workers = round_int(max_job_points/per_worker)

            if len(workers) > max_workers:
                workers = random.sample(workers, max_workers)

            temp = "{} gave a nice motivational speech and approached some of the workers individually! ".format(manager.name)
            temp += ", ".join([w.name for w in workers])
            temp += " responded positively! "
            temp_p = "(+{}% Job Points)".format(round_int(init_jp_bonus*100))
            temp += set_font_color(temp_p, "lawngreen")
            manager._dnd_mlog.append(temp)
            building.log("{} gave a motivational speech!".format(manager.name))

            init_jp_bonus += 1.0
            for w in workers:
                w.jobpoints = round_int(w.jobpoints*init_jp_bonus)
            manager.jobpoints -= len(workers)*per_worker
            
    def manager_post_nd(building):
        managers = getattr(building, "_dnd_managers", None)
        if managers is None:
            return

        del building._dnd_managers
        del building._dnd_manager
        building.manager_effectiveness = 0

        for m in managers:
            points_used = m._dnd_jobpoints - m.jobpoints
            log = m._dnd_mlog
            if points_used != 0:
                if points_used > 100:
                    log.logws("management", randint(1, 2))
                    log.logws("intelligence", randrange(2))
                    log.logws("refinement", 1)
                    log.logws("character", 1)

                ap_used = (points_used)/100.0
                log.logws("exp", exp_reward(m, building.tier, exp_mod=ap_used))

                if points_used > m._dnd_jobpoints*3/4:
                    log.append("%s had a long working day." % m.name)
                elif points_used > m._dnd_jobpoints/2:
                    log.append("%s's day was quite busy on the job." % m.name)
                else:
                    log.append("%s had only a few things to accomplish during the day." % m.name)
            else:
                log.append("%s had nothing to do on the job." % m.name)

            # finalize the log:
            log.img = m.show("profile", resize=ND_IMAGE_SIZE, add_mood=True)
            log.type = "manager_report"
            log.after_job()

            NextDayEvents.append(log)

            del m._dnd_effectiveness
            del m._dnd_mlog
            del m._dnd_jobpoints
