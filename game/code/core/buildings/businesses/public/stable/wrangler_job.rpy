init -5 python:
    class WranglerJob(Job):
        id = "Wrangler"
        desc = "Wranglers tend the horses and handing over the horses to the customers"
        type = "Service"

        per_client_payout = 6

        aeq_purpose = 'Wrangler'

        # Relevant skills and stats:
        base_skills = {"service": 50, "riding": 100}
        base_stats = {"agility": 50, "constitution": 50}

        traits = {"Abnormally Large Boobs", "Aggressive", "Coward", "Neat", "Clumsy",
                  "Natural Leader", "Scars", "Courageous", "Manly", "Sadist", "Peaceful", "Psychic"}

        @staticmethod
        def want_work(worker):
            return any(t.id in ["Knight", "Maid"] for t in worker.basetraits)

        @staticmethod
        def willing_work(worker):
            return True

        @staticmethod
        def traits_and_effects_effectiveness_mod(worker, log):
            """Affects worker's effectiveness during one turn. Should be added to effectiveness calculated by the function below.
               Calculates only once per turn, in the very beginning.
            """
            effectiveness = 0
            name = worker.name
            effects = worker.effects
            if 'Exhausted' in effects:
                log.append("%s is exhausted and is in need of some rest." % name)
                effectiveness -= 75
            elif 'Injured' in effects:
                log.append("%s is injured and is in need of some rest." % name)
                effectiveness -= 70
            elif 'Food Poisoning' in effects:
                log.append("%s suffers from Food Poisoning, and is very far from %s top shape." % (name, worker.pd))
                effectiveness -= 50
            elif 'Drunk' in effects:
                log.append("%s is drunk, which affects %s coordination. Not the best thing when you need to tend to the horses." % (name, worker.pd))
                effectiveness -= 20
            elif 'Down with Cold' in effects:
                log.append("%s is not feeling well due to colds..." % name)
                effectiveness -= 15

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                traits = WranglerJob.traits
                traits = list(i for i in worker.traits if i.id in traits)

                if worker.height == "short":
                    traits.append(store.traits["Lolita"])

                if not traits:
                    return effectiveness
                trait = choice(traits)
                trait = trait.id

                if trait == "Psychic":
                    log.append("%s knows how to control the horses." % name)
                    effectiveness += 30
                elif trait == "Lolita":
                    log.append("The small frame of %s enables %s to ride a horse without encumbering it." % (name, worker.op))
                    effectiveness += 25
                elif trait == "Natural Leader":
                    log.append("%s sits firmly in the saddle." % name)
                    effectiveness += 20
                elif trait == "Courageous":
                    log.append("%s refuses to back down no matter the odds, making a great guard." % name)
                    effectiveness += 15
                elif trait == "Manly":
                    log.append("%s can easily keep the horses in line." % name)
                    effectiveness += 15
                elif trait == "Peaceful":
                    log.append("The calmness of %s helps %s to tend to the horses." % (name, worker.op))
                    effectiveness += 10
                elif trait == "Scars":
                    log.append("Even some of the animals are startled by the scars of %s." % name)
                    effectiveness -= 10
                elif trait == "Abnormally Large Boobs":
                    log.append("Her massive tits get in the way and keep her off balance as %s tries to ride a horse." % name)
                    effectiveness -= 10
                elif trait == "Neat":
                    log.append("%s refuses to dirty %s hands on some of the muddier animals." % (name, worker.pd))
                    effectiveness -= 15
                elif trait == "Coward":
                    log.append("%s is too afraid to get close to the animals. Maybe it's not the best job for %s." % (name, worker.op))
                    effectiveness -= 20
                elif trait == "Aggressive":
                    log.append("%s keeps disturbing the horses who aren't doing anything wrong." % name)
                    effectiveness -= 25
                elif trait == "Sadist":
                    log.append("%s gladly beats the horses just out of spite. Obviously the horses do not tolerate %s long." % (name, worker.op))
                    effectiveness -= 35
            return effectiveness

        @staticmethod
        def settle_workers_disposition(worker, log):
            """
            handles penalties in case of wrong job
            """
            name = set_font_color(choice([worker.fullname, worker.name, worker.nickname]), "pink")
            if WranglerJob.want_work(worker):
                log.append(choice(["%s is working as a wrangler." % name,
                                   "%s gets busy with horses." % name,
                                   "%s is working in the stable!" % name, 
                                   "%s serves customers in the stable." % name]))
            else:
                sub = check_submissivity(worker)
                if worker.status != 'slave':
                    if sub < 0:
                        log.append("%s is not very happy with %s current job as a wrangler, but %s will get the job done." % (name, worker.pd, worker.p))
                        sub = 15
                    elif sub == 0:
                        log.append("%s serves customers in the stable, but, truth be told, %s would prefer to do something else." % (name, worker.p))
                        sub = 25
                    else:
                        log.append("%s makes it clear that %s wants another job before getting busy with the horses." % (name, worker.p))
                        sub = 35
                    if dice(sub):
                        worker.logws('character', 1)
                    worker.logws("joy", -randint(3, 5))
                    worker.logws("disposition", -randint(5, 10))
                    worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
                else:
                    dispo = worker.get_stat("disposition")
                    dispo_req = WranglerJob.calculate_disposition_level(worker)
                    if sub < 0:
                        if dispo < dispo_req:
                            log.append("%s is a slave so no one really cares, but being forced to work as a wrangler, %s's quite upset." % (name, worker.p))
                        else:
                            log.append("%s will do as %s is told, but doesn't mean that %s'll be happy about %s stable duties." % (name, worker.p, worker.p, worker.pd))
                        sub = 25
                    elif sub == 0:
                        if dispo < dispo_req:
                            log.append("%s will do as you command, but %s will hate every second of %s stable job..." % (name, worker.p, worker.pd))
                        else:
                            log.append("%s was very displeased by %s order to work as a wrangler, but didn't dare to refuse." % (name, worker.pd))
                        sub = 35
                    else:
                        if dispo < dispo_req:
                            log.append("%s was very displeased by %s order to work as a wrangler, and makes it clear for everyone before getting busy with the horses." % (name, worker.pd))
                        else:
                            log.append("%s will do as you command and work as a wrangler, but not without a lot of grumbling and complaining." % name)
                        sub = 45
                    if dice(sub):
                        worker.logws('character', 1)
                    if dispo < dispo_req:
                        worker.logws("joy", -randint(5, 10))
                        worker.logws("disposition", -randint(5, 15))
                        worker.logws('vitality', -randint(5, 10))
                    else:
                        worker.logws("joy", -randint(2, 4))
                        worker.logws('vitality', -randint(1, 4))

        @staticmethod
        def log_work(worker, clients, ap_used, effectiveness, log):
            len_clients = len(clients)
            tier = log.loc.tier

            riding = WranglerJob.normalize_required_skill(worker, "riding", effectiveness, tier)
            service = WranglerJob.normalize_required_skill(worker, "service", effectiveness, tier)

            if riding > 150:
                if dice(70):
                    log.logloc('reputation', 1)
                log.append("%s was an excellent wrangler, customers kept spending their money just for the pleasure of %s company." % (worker.pC, worker.pd))
            elif riding >= 100:
                if dice(50):
                    log.logloc('reputation', 1)
                log.append("Customers were pleased with %s company and kept spending more time in the stable." % worker.pd)
            elif riding >= 75:
                if dice(10):
                    log.logloc('reputation', 1)
                log.append("%s was skillful enough not to mess anything up during %s job." % (worker.pC, worker.pd))
            elif riding >= 50:
                if dice(70):
                    log.logloc('reputation', -1)
                log.append("%s performance was rather poor and it most definitely has cost you income." % worker.pdC)
            else:
                log.logloc('reputation', -2)
                log.append("%s is a very unskilled wrangler, %s definitely needs training." % (worker.name, worker.p))

            if service > 150:
                if dice(70):
                    log.logloc('fame', 1)
                log.append("Your worker provided excellent service to the customer.")
            elif service > 100:
                if dice(50):
                    log.logloc('fame', 1)
                log.append("The customers were very pleased by the service of your worker.")
            elif service > 75:
                if dice(20):
                    log.logloc('fame', 1)
                log.append("Your worker handled the customers the right way.")
            elif service > 50:
                log.append("Your worker definitely needs more training to handle the customers.")
            else:
                log.logloc('fame', -2)
                log.append("The rude service of your worker really hurt your business.")

            log.append("\n")

            #Stat Mods
            # Award EXP:
            if effectiveness < 90:
                ap_used *= .5
            log.logws("exp", exp_reward(worker, tier, exp_mod=ap_used))

            log.logws('vitality', -(len_clients+1)/2)

            log.logws('riding', randint(1, 2))
            if dice(25):
                log.logws('service', 1)
            if dice(25):
                log.logws('agility', 1)
            if dice(10):
                log.logws('constitution', 1)

            excluded = ["nude", "sex"]
            if worker.has_image("nature", "outdoors", exclude=excluded):
                log.img = worker.show("nature", "outdoors", exclude=excluded)
            elif worker.has_image("maid", exclude=excluded):
                log.img = worker.show("maid", exclude=excluded)
            else:
                log.img = worker.show("profile", exclude=excluded)
