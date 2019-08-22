init -5 python:
    class StripJob(Job):
        id = "Stripper"
        desc = "Strippers dance half-naked on the stage, keeping customers hard and ready to hire more whores"
        type = "SIW"

        per_client_payout = 8

        aeq_purpose = "Striptease"

        base_skills = {"strip": 100, "dancing": 40, "sex": 5}
        base_stats = {"charisma": 70, "agility": 30}

        traits = {"Abnormally Large Boobs", "Small Boobs", "Scars", "Not Human", "Flat Ass", "Exhibitionist",
                  "Sexy Air", "Clumsy", "Flexible", "Psychic", "Manly", "Artificial Body", "Strange Eyes",
                  "Lesbian", "Shy", "Aggressive", "Big Boobs", "Great Arse", "Long Legs", "Natural Follower"}

        @staticmethod
        def want_work(worker):
            return any(t.id == "Stripper" for t in worker.basetraits) 

        @staticmethod
        def willing_work(worker):
            return any("SIW" in t.occupations for t in worker.basetraits)

        @staticmethod
        def traits_and_effects_effectiveness_mod(worker, log):
            """Affects worker's effectiveness during one turn. Should be added to effectiveness calculated by the function below.
               Calculates only once per turn, in the very beginning.
            """
            # Special check to prevent crashing
            effectiveness = 0
            name = worker.name
            effects = worker.effects
            # effects always work
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
                log.append("%s is drunk, which affects %s coordination. Not the best thing when you need to dance around pole." % (name, worker.pd))
                effectiveness -= 20
            elif 'Down with Cold' in effects:
                log.append("%s is not feeling well due to colds..." % name)
                effectiveness -= 15
            elif 'Revealing Clothes' in effects:
                log.append("%s revealing clothes are perfect for %s job!" % (worker.pdC, worker.pd))
                effectiveness += 40
            elif 'Horny' in effects:
                log.append("%s is horny. A positive mindset for %s job!" % (name, worker.pd))
                effectiveness += 10

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                # This cannot work comparing strings to trait objects:
                traits = StripJob.traits
                traits = list(i for i in worker.traits if i.id in traits)

                if not traits:
                    return effectiveness
                trait = choice(traits)
                trait = trait.id

                if trait == "Abnormally Large Boobs":
                    if dice(65):
                        log.append("%s makes a big splash today playing with her massive boobs to customers delight." % name)
                        effectiveness += 50
                    else:
                        log.append("Handling massive boobs on daily basis is a tiresome job, even more so when %s has to dance at the stage." % name)
                        worker.logws('vitality', -randint(5, 10))
                elif trait == "Small Boobs":
                    if not "Lolita" in worker.traits:
                        log.append("%s tries her best, but most customers are not very impressed by her modest forms." % name)
                        effectiveness -= 25
                    else:
                        log.append("%s may not have many fans due to her forms, but there are always lolicons among customers." % name)
                        effectiveness += 20
                elif trait == "Exhibitionist":
                    log.append("%s is at least as aroused as the customers and isn't afraid to show it." % name)
                    effectiveness += 50
                elif trait == "Flexible":
                    log.append("%s makes a good use of %s flexibility, bending around the pole in impossible ways." % (name, worker.pd))
                    effectiveness += 20
                elif trait == "Natural Follower":
                    log.append("%s is quick to figure out how a crowd likes %s to move, making a great show." % (name, worker.op))
                    effectiveness += 20
                elif trait == "Not Human":
                    log.append("%s's inhuman features attract more attention than usual, and that is never a bad thing in striptease." % name)
                    effectiveness += 15
                elif trait == "Big Boobs":
                    log.append("The customers' eyes are glued to her tits all the time.")
                    effectiveness += 15
                elif trait == "Great Arse":
                    log.append("%s shakes %s sexy ass to great effect. It's like %s curves were made for stripping." % (name, worker.pd, worker.pd))
                    effectiveness += 15
                elif trait == "Long Legs":
                    log.append("Today the customers went nuts for those sexy legs of %s." % name)
                    effectiveness += 15
                elif trait == "Sexy Air":
                    log.append("%s's sexiness attracts the views all day. %s has an air about %s that makes %s a natural at stripping." % (name, worker.pC, worker.op, worker.op))
                    effectiveness += 10
                elif trait == "Strange Eyes":
                    log.append("%s exotic eyes hold the customers in a trance." % worker.pdC)
                    effectiveness += 10
                elif trait == "Flat Ass":
                    log.append("%s tries %s best, but skill alone cannot replace a fine ass." % (name, worker.pd))
                    effectiveness -= 15
                elif trait == "Psychic":
                    log.append("Every customer wants different things, which is quite confusing for psychics like %s when so many people watching %s." % (name, worker.op))
                    effectiveness -= 20
                elif trait == "Aggressive":
                    log.append("%s slaps customers who get too close, ruining the mood." % name)
                    effectiveness -= 20
                elif trait == "Manly":
                    log.append("It looks like %s is a bit too muscular for this job, intimidating some customers." % name)
                    effectiveness -= 25
                elif trait == "Clumsy":
                    log.append("Sadly, %s ruins the show when %s trips and falls from the stage. At least customers had a good laugh." % (name, worker.p))
                    effectiveness -= 25
                elif trait == "Lesbian":
                    log.append("%s is somewhat disgusted by the idea of letting so many MEN see her naked." % name)
                    effectiveness -= 30
                elif trait == "Shy":
                    log.append("%s is too nervous and stiff, making customers bored." % name)
                    effectiveness -= 30
                elif trait == "Scars":
                    log.append("Poor %s does %s best, but many customers turn away when they see %s scars..." % (name, worker.pd, worker.pd))
                    effectiveness -= 35
                elif trait == "Artificial Body":
                    log.append("Sadly, customers figured out that %s body is a construct and booed %s off the stage." % (worker.pd, name))
                    effectiveness -= 50
            return effectiveness

        @staticmethod
        def calculate_disposition_level(worker, sub):
            """
            calculating the needed level of disposition;
            """
            disposition = 600 - 50 * sub

            if check_lovers(worker):
                disposition -= 50
            elif check_friends(worker):
                disposition -= 25

            if StripJob.willing_work(worker, "SIW"):
                disposition -= 500

            traits = worker.traits
            if "Shy" in traits:
                disposition += 100
            if "Exhibitionist" in traits:
                disposition -= 200
            if "Nymphomaniac" in traits:
                disposition -= 50
            elif "Frigid" in traits:
                disposition += 50
            if "Natural Follower" in traits:
                disposition -= 50
            elif "Natural Leader" in traits:
                disposition += 50
            return disposition

        @staticmethod
        def settle_workers_disposition(worker, log):
            """
            Handles penalties in case of wrong job
            """
            # Formerly check_occupation
            name = set_font_color(choice([worker.fullname, worker.name, worker.nickname]), "pink")
            if StripJob.want_work(worker):
                log.append(choice(["%s is doing %s shift as a stripper.",
                                   "%s entertains customers with %s body on the stage.",
                                   "%s begins %s striptease performance!",
                                   "%s shows %s goods to clients."]) % (name, worker.pd))
            else:
                sub = check_submissivity(worker)
                if worker.status != 'slave':
                    if sub > 0:
                        log.append("%s is not very happy with %s current job as a stripper, but %s will get the job done." % (name, worker.pd, worker.p))
                        sub = 15
                    elif sub == 0:
                        log.append("%s shows %s goods to customers, but %s would prefer to do something else." % (name, worker.pd, worker.p))
                        sub = 25
                    else:
                        log.append("%s makes it clear that %s wants another job before going to the stage." % (name, worker.p))
                        sub = 35
                    if dice(sub):
                        log.logws('character', 1)
                    worker.logws("joy", -randint(1, 10))
                    worker.logws("disposition", -randint(10, 15))
                    worker.logws('vitality', -randint(5, 10))
                else:
                    dispo = worker.get_stat("disposition")
                    dispo_req = StripJob.calculate_disposition_level(worker, sub)
                    if sub > 0:
                        if dispo < dispo_req:
                            log.append("%s is a slave so no one really cares, but being forced to work as a stripper, %s's quite upset." % (name, worker.p))
                        else:
                            log.append("%s will do as %s is told, but doesn't mean that %s'll be happy about showing %s body to strangers." % (name, worker.p, worker.p, worker.pd))
                        sub = 25
                    elif sub == 0:
                        if dispo < dispo_req:
                            log.append("%s will do as you command, but %s will hate every second of %s stripper shift..." % (name, worker.p, worker.pd))
                        else:
                            log.append("%s was very displeased by %s order to work as a stripper, but didn't dare to refuse." % (name, worker.pd))
                        sub = 35
                    else:
                        if dispo < dispo_req:
                            log.append("%s was very displeased by %s order to work as a stripper, and makes it clear for everyone before going to the stage." % (name, worker.pd))
                        else:
                            log.append("%s will do as you command and work as a stripper, but not without a lot of grumbling and complaining." % name)
                        sub = 45
                    if dice(sub):
                        log.logws('character', 1)
                    if dispo < dispo_req:
                        worker.logws("joy", -randint(5, 10))
                        worker.logws("disposition", -randint(15, 30))
                        worker.logws('vitality', -randint(10, 15))
                    else:
                        worker.logws("joy", -randint(2, 4))
                        worker.logws('vitality', -randint(2, 6))

        @staticmethod
        def log_work(worker, ap_used, effectiveness, log):
            tier = log.loc.tier

            strip = StripJob.normalize_required_skill(worker, "strip", effectiveness, tier)
            dancing = StripJob.normalize_required_skill(worker, "dancing", effectiveness, tier)
            skill = (strip*1.3 + dancing)/2
            charisma = StripJob.normalize_required_stat(worker, "charisma", effectiveness, tier)

            name = worker.name
            if charisma >= 170:
                log.append("%s supernal loveliness instantly captivated audiences." % name)
                log.logws("joy", 2)
            elif charisma >= 150:
                log.append("The attention of customers was entirely focused on %s thanks to %s prettiness." % (name, worker.pd))
                log.logws("joy", 1)
            elif charisma >= 120:
                log.append("%s enchanted customers with %s stunning beauty." % (name, worker.pd))
            elif charisma >= 100:
                log.append("Customers were delighted with %s beauty." % name)
            elif charisma >= 75:
                log.append("%s good looks was pleasing to audiences." % name)
            elif charisma >= 50:
                log.append("%s did %s best to make customers like %s, but %s charm could definitely be enhanced." % (name, worker.pd, worker.op, worker.pd))
                log.logws("joy", -1)
            else:
                log.append("Customers clearly were unimpressed by %s looks, to say the least. Such a cold reception was not encouraging for the poor %s at all..." % (name, "girl" if worker.gender == "female" else "guy"))
                log.logws("joy", -2)

            log.append("\n")
            if skill >= 170:
                log.append("%s gave an amazing performance, %s sexy and elegant moves forced a few customers to come right away to their own embarrassment." % (worker.pC, worker.pd))
                if dice(50):
                    log.logloc("reputation", 1)
                log.logws("joy", 2)
            elif skill >= 150:
                log.append("%s gave a performance worthy of kings and queens as the whole hall was cheering for %s." % (worker.pC, worker.op))
                if dice(30):
                    log.logloc("reputation", 1)
                log.logws("joy", 1)
            elif skill >= 130:
                log.append("%s lost all of %s clothing piece by piece as %s gracefully danced on the floor, the whole hall was cheering for %s." % (worker.pC, worker.pd, worker.p, worker.op))
            elif skill >= 100:
                log.append("%s lost all of %s clothing piece by piece as %s danced on the floor, some mildly drunk clients cheered for %s." % (worker.pC, worker.pd, worker.p, worker.op))
            elif skill >= 75:
                log.append("%s danced to the best of %s ability but %s skills could definitely be improved." % (worker.pC, worker.pd, worker.pd))
            elif skill >= 50:
                log.append("%s barely knew what %s was doing. %s performance can hardly be called a striptease, but at least %s showed enough skin to arouse some customers in the club." % (worker.pC, worker.p, worker.pdC, worker.p))
                log.logws("joy", -1)
                if dice(10):
                    log.logloc("reputation", -1)
            else:
                log.logws("joy", -2)
                if charisma >= 100:
                    if dice(50):
                        log.append("%s performance made some of the customers fall asleep. Apparently not even %s looks could keep their attention alive..." % (worker.pdC, worker.pd))
                        log.logloc("reputation", -2)
                    else:
                        log.append("%s tripped several times while trying to undress %sself as %s 'stripdanced' on the floor. Still, %s was pretty enough to arouse some men and women in the club." % (worker.pC, worker.op, worker.p, worker.p))
                        log.logloc("reputation", -1)
                else:
                    log.append("%s certainly did not shine as %s clumsily 'danced' on the floor. Neither %s looks nor %s skill could save the performance..." % (worker.pC, worker.p, worker.pd, worker.pd))
                    log.logloc("reputation", -2)

            # Stats Mods
            log.logws('vitality', round_int(ap_used*-10))
            # Award EXP:
            if effectiveness < 90:
                ap_used *= .5
            log.logws("exp", exp_reward(worker, tier, exp_mod=ap_used))
            log.logws("strip", randfloat(ap_used))
            log.logws("dancing", randfloat(ap_used/2))
            log.logws("agility", randfloat(ap_used/4))
            log.logws("charisma", randfloat(ap_used/2))

            log.img = worker.show("stripping", ("stage", "no bg", "simple bg", "indoors", None), exclude=["sex", "sad", "angry", "in pain"], type="ptls")
