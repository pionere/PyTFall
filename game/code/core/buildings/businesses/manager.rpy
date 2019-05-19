# Manager stuff goes here, will prolly be only one function but it doesn't fit anywhere else.
init -5 python:
    class Manager(Job):
        pass # obsolete
    class ManagerJob(Job):
        id = "Manager"
        desc = "Manages your business, helping workers in various ways and improving their performance."
        type = "Management"

        aeq_purpose = 'Manager'

        base_skills = {"management": 80, "refinement": 20}
        base_stats = {"character": 40, "intelligence": 60}

        @staticmethod
        def want_work(worker):
            return any(t.id == "Manager" for t in worker.basetraits)

        @staticmethod
        def willing_work(worker):
            return any(t.id == "Manager" for t in worker.basetraits)

        @staticmethod
        def traits_and_effects_effectiveness_mod(worker, log):
            effectiveness = 0

            name = worker.name
            effects = worker.effects
            if 'Exhausted' in effects:
                log.append("%s is exhausted and is in need of some rest." % name)
                effectiveness -= 75
            elif 'Drunk' in effects:
                log.append("Being drunk, %s is totally incapable to fulfill %s job." % (name, worker.pp))
                effectiveness -= 70
            elif 'Food Poisoning' in effects:
                log.append("%s suffers from Food Poisoning, and is very far from %s top shape." % (name, worker.pp))
                effectiveness -= 50
            elif 'Down with Cold' in effects:
                log.append("%s is not feeling well due to colds..." % name)
                effectiveness -= 15

            # traits don't always work, even with high amount of traits
            # there are normal days when performance is not affected
            if locked_dice(65):
                traits = {"Exhibitionist", "Frigid", "Serious", "Peaceful", "Clumsy", "Shy",
                          "Nerd", "Elegant", "Natural Leader", "Natural Follower", "Aggressive", 
                          "Psychic", "Always Hungry", "Well-mannered", "Ill-mannered"}
                traits = list(i.id for i in worker.traits if i.id in traits)

                if traits:
                    trait = choice(traits)
                else:
                    return effectiveness

                if trait == "Natural Leader":
                    log.append("Every guesture of %s calls for action. %s was born for this job." % (name, worker.pC))
                    effectiveness += 25
                elif trait == "Psychic":
                    log.append("%s knows how to convince the workers to do their job." % name)
                    effectiveness += 20
                elif trait == "Well-mannered":
                    log.append("%s expresses %s wishes in a perfect way. The workers are happy to comply." % (name, worker.pp))
                    effectiveness += 10
                elif trait == "Frigid":
                    log.append("%s focus is always on the job, which makes %s a great manager." % (name, worker.pp))
                    effectiveness += 10
                elif trait == "Serious":
                    log.append("%s means business. The workers follow %s orders promptly." % (name, worker.pp))
                    effectiveness += 10
                elif trait == "Peaceful":
                    log.append("%s does not let arguments spiral out of control. Makes it easy to handle the difficulties on the job." % name)
                    effectiveness += 10
                elif trait == "Elegant":
                    log.append("The perfect dress of %s indicates professionalism." % name)
                    effectiveness += 10
                elif trait == "Clumsy":
                    log.append("The footsteps of %s are marked with mistakes. %s subordinates wish for a better lead." % (name, worker.ppC))
                    effectiveness -= 10
                elif trait == "Nerd":
                    log.append("The workers find it hard to communicate with %s." % name)
                    effectiveness -= 10
                elif trait == "Always Hungry":
                    log.append("It is hard to give orders while your stomach is empty and your mouth is full. %s should find a more appropriate job." % name)
                    effectiveness -= 10
                elif trait == "Ill-mannered" or trait == "Aggressive":
                    log.append("The rude behaviour of %s makes %s co-worker unwilling to follow %s orders." % (name, worker.pp, worker.pp))
                    effectiveness -= 10
                elif trait == "Exhibitionist":
                    log.append("The way %s dresses distracts the worker around %s." % (name, worker.pp))
                    effectiveness -= 20
                elif trait == "Natural Follower":
                    log.append("%s would rather take than give orders. This is really not a job for %s." % (name, worker.pp))
                    effectiveness -= 25
                elif trait == "Shy":
                    log.append("The commands of %s are easily suppressed by the workers wishes. %s feels out of place at %s job." % (name, worker.pC, worker.pp))
                    effectiveness -= 30

            return effectiveness

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
                workers = [wjv for wjv in ((w, w.get_stat("joy") < w.get_max("joy")/2, w.get_stat("vitality") < w.get_max("vitality")/3)
                                      for w in building.available_workers if w != manager and w not in cheered_up_workers)
                            if wjv[1] or wjv[2]]

                if workers:
                    worker, give_joy, give_vit = choice(workers)
                    cheered_up_workers.add(worker)

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
