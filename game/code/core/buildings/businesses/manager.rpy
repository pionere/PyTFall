# Manager stuff goes here, will prolly be only one function but it doesn't fit anywhere else.
init -5 python:
    class Manager(Job):
        pass # obsolete
    class ManagerJob(Job):
        id = "Manager"
        type = "Management"

        # Traits/Job-types associated with this job:
        occupations = ["Specialist"] # General Strings likes SIW, Combatant, Server...
        occupation_traits = ["Manager"] # Corresponding trait, later replaced by the corresponding instance
        aeq_purpose = 'Manager'
        desc = "Manages your business, helping workers in various ways and improving their performance."

        base_skills = {"management": 80, "refinement": 20}
        base_stats = {"character": 40, "intelligence": 60}

        allowed_status = ["free"]

    def manager_pre_nd(building):
        if not building.needs_manager:
            return

        workers = building.available_workers

        mj = ManagerJob
        managers = [w for w in workers if w.action == mj]

        effectiveness = 0
        if managers:
            for m in managers:
                log = NDEvent(job=mj, char=m, loc=building)
                m._dnd_effectiveness = mj.effectiveness(m, building.tier, log)
                m._dnd_mlog = log
                m._dnd_pp = m.PP

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
        mp_init_jp_bonus(manager, building, effectiveness)

        cheered_up_workers = set()

        while (1):
            yield env.timeout(5)
            simpy_debug("Entering manager_process at %s", env.now)
            # select a new manager if the current one is exhausted
            if manager.PP <= 10:
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
            if building.cheering_up and manager.PP > 10 and dice(effectiveness-50):
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
                    temp = "%s noticed that %s looks a bit %s." % (manager.nickname, worker.nickname, handle)

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

                    temp += " Your manager cheered %s up. %s" % (worker.op, set_font_color(bonus_str, "lawngreen"))
                    manager._dnd_mlog.append(temp)

                    building.log("Your manager cheered up %s." % worker.name)

                    manager.PP -= 10

            simpy_debug("Exiting manager_process at %s", env.now)


    def mp_init_jp_bonus(manager, building, effectiveness):
        if not building.init_pep_talk:
            return

        # Special bonus to JobPoints (aka pep talk) :D
        init_jp_bonus = effectiveness-95
        if init_jp_bonus <= 0:
            return

        if init_jp_bonus > 30: # Too much power otherwise...
            init_jp_bonus = 30
        elif init_jp_bonus < 5: # Less than 5% is absurd...
            init_jp_bonus = 5

        # Bonus to the maximum amount of workers:
        max_workers = manager.PP / 20 # pp / (2 * PER_WORKER)
        if max_workers == 0:
            return

        workers = building.available_workers
        if not workers:
            return

        if len(workers) > max_workers:
            workers = random.sample(workers, max_workers)

        temp = manager.name
        temp += " gave a nice motivational speech and approached some of the workers individually! "
        temp += ", ".join([w.name for w in workers])
        temp += " responded positively! "
        temp += set_font_color("(+%d%% Job Points)" % init_jp_bonus, "lawngreen")
        manager._dnd_mlog.append(temp)
        building.log("%s gave a motivational speech!" % manager.name)

        init_jp_bonus = 1.0 + init_jp_bonus/100.0
        for w in workers:
            w.PP = round_int(w.PP*init_jp_bonus)
        manager.PP -= len(workers)*10 # PER_WORKER

    def manager_post_nd(building):
        managers = getattr(building, "_dnd_managers", None)
        if managers is None:
            return

        del building._dnd_managers
        del building._dnd_manager
        building.manager_effectiveness = 0

        for m in managers:
            points_used = m._dnd_pp - m.PP
            log = m._dnd_mlog
            if points_used != 0:
                if dice(points_used):
                    log.logws("management", randint(1, 2))
                    log.logws("intelligence", randrange(2))
                    log.logws("refinement", 1)
                    log.logws("character", 1)

                ap_used = (points_used)/100.0
                log.logws("exp", exp_reward(m, building.tier, exp_mod=ap_used))

                if points_used > m._dnd_pp*3/4:
                    log.append("%s had a long working day." % m.name)
                elif points_used > m._dnd_pp/2:
                    log.append("%s's day was quite busy on the job." % m.name)
                else:
                    log.append("%s had only a few things to accomplish during the day." % m.name)
            else:
                log.append("%s had nothing to do on the job." % m.name)

            # finalize the log:
            log.img = m.show("profile", add_mood=True)
            log.type = "manager_report"
            log.after_job()

            NextDayEvents.append(log)

            del m._dnd_effectiveness
            del m._dnd_mlog
            del m._dnd_pp
