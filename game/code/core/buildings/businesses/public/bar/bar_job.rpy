init -5 python:
    class BarJob(Job):
        def __init__(self):
            super(BarJob, self).__init__()
            self.id = "Bartending"
            self.type = "Service"

            self.per_client_payout = 6

            # Traits/Job-types associated with this job:
            self.occupations = ["Server"] # General Strings likes SIW, Combatant, Server...
            self.occupation_traits = [traits["Maid"], traits["Barmaid"]] # Corresponding traits...
            self.aeq_purpose = 'Bartender'

            # Relevant skills and stats:
            self.base_skills = {"service": 50, "bartending": 100}
            self.base_stats = {"intelligence": 50, "character": 50}

            self.desc = "Barmaids serve drinks from the bar and occasionally chat with customers"

        def traits_and_effects_effectiveness_mod(self, worker, log):
            effectiveness = 0

            if 'Food Poisoning' in worker.effects:
                log.append("%s suffers from Food Poisoning, and is very far from %s top shape." % (worker.name, worker.pp))
                effectiveness -= 50
            elif 'Down with Cold' in worker.effects:
                log.append("%s is not feeling well due to colds..." % worker.name)
                effectiveness -= 15
            elif 'Exhausted' in worker.effects:
                log.append("%s is exhausted and is in need of some rest." % worker.name)
                effectiveness -= 75
            elif 'Drunk' in worker.effects:
                log.append("Being drunk, %s perfectly understands %s customers who also are far from sobriety." % (worker.name, worker.pp))
                effectiveness += 20

            # traits don't always work, even with high amount of traits
            # there are normal days when performance is not affected
            if locked_dice(65):
                traits = ["Great Arse", "Bad Eyesight", "Curious", "Indifferent", "Nerd",
                        "Heavy Drinker", "Ill-mannered", "Psychic", "Shy", "Neat", "Messy",
                        "Natural Follower", "Virtuous", "Natural Leader", "Clumsy", "Manly",
                        "Stupid", "Abnormally Large Boobs", "Big Boobs", "Scars", "Vicious"]
                traits = list(i.id for i in worker.traits if i.id in traits)

                if worker.height == "short" and "Lolita" in worker.traits:
                    traits.append("Lolita")

                if traits:
                    trait = choice(traits)
                else:
                    return effectiveness

                if trait == "Great Arse":
                    log.append("The customers kept ordering drinks from the bottom shelf just to watch %s bend over. What a view!" % worker.name)
                    effectiveness += 25
                elif trait == "Lolita":
                    log.append("Poor %s has a hard time with the top shelves of the bar due to %s height." % (worker.name, worker.pp))
                    effectiveness -= 20
                elif trait == "Bad Eyesight":
                    log.append("Occasionally %s serves the wrong drinks, making customers unhappy." % worker.name)
                    effectiveness -= 15
                elif trait == "Curious":
                    log.append("Curious %s can listen to customers complaints about their lives for hours, making a great barmaid." % worker.name)
                    effectiveness += 10
                elif trait == "Indifferent":
                    log.append("%s provides some really bland service. The customers aren't even sure %s is paying attention." % (worker.name, worker.p))
                    effectiveness -= 10
                elif trait == "Neat":
                    log.append("%s keeps the bar and all the glasses perfect clean, making a good impression on customers." % worker.name)
                    effectiveness += 20
                elif trait == "Messy":
                    log.append("It's not unusual for %s to serve drinks without cleaning glasses first. That does not add to %s popularity as a barmaid." % (worker.name, worker.pp))
                    effectiveness -= 20
                elif trait == "Heavy Drinker":
                    if dice(50):
                        log.append("%s's deep knowledge of alcohol helps to serve the best possible drink." % worker.name)
                        effectiveness += 10
                    else:
                        log.append("The customers all passed out in no time. %s has no idea why - drinks don't seem that strong to %s." % (worker.name, worker.op))
                        effectiveness -= 10
                elif trait == "Ill-mannered":
                    log.append("Unfortunately %s's rudeness scares away customers, affecting the business." % worker.name)
                    effectiveness -= 20
                elif trait == "Psychic":
                    log.append("People marvel at how %s usually already has the drink ready before the customer comes up to the bar." % worker.name)
                    effectiveness += 25
                elif trait == "Shy":
                    log.append("It's difficult for %s to serve drinks and maintain a conversation at the same time. %s's too afraid of making mistakes." % (worker.name, worker.pC))
                    effectiveness -= 25
                elif trait == "Nerd":
                    log.append("%s is a bit awkward as a bartender, always more interested in %s little hobby than on tending to the customers." % (worker.name, worker.pp))
                    effectiveness -= 10
                elif trait == "Natural Follower" or trait == "Virtuous":
                    log.append("Customers keep asking %s for a discount and %s keeps accepting. Maybe it's not the best job for %s." % (worker.name, worker.p, worker.op))
                    effectiveness -= 15
                elif trait == "Natural Leader":
                    log.append("%s has a real way with words. Customers like to talk to %s about anything just to hear %s voice." % (worker.name, worker.op, worker.pp))
                    effectiveness += 15
                elif trait == "Clumsy":
                    log.append("The sound of breaking glass filled the building once %s began %s shift. Sigh..." % (worker.name, worker.pp))
                    effectiveness -= 15
                elif trait == "Stupid":
                    log.append("%s has to ask for help all the time because %s can't remember how to make anything." % (worker.name, worker.p))
                    effectiveness -= 20
                elif trait == "Abnormally Large Boobs" or trait == "Big Boobs":
                    log.append("People keep asking her to make cocktails just to watch her boobs quake.")
                    effectiveness += 15
                elif trait == "Scars":
                    log.append("%s scars give %s a tough look that makes %s cool as a bartender." % (worker.ppC, worker.op, worker.op))
                    effectiveness += 10
                elif trait == "Manly":
                    log.append("A tough looking bartender helps to keep some of the rowdy customers in line.")
                    effectiveness += 10
                elif trait == "Vicious":
                    log.append("It's nice to have %s working as a bartender. %s doesn't let the customers build up a tab no matter how pitiable they are." % (worker.name, worker.pC))
                    effectiveness += 10

            return effectiveness

        def calculate_disposition_level(self, worker):
            """
            calculating the needed level of disposition;
            since it's whoring we talking about, values are really close to max,
            or even higher than max in some cases, making it impossible
            """
            sub = check_submissivity(worker)
            if "Shy" in worker.traits:
                disposition = 400 + 50 * sub
                if "Psychic" in worker.traits:
                    disposition += 200
            else:
                disposition = 200 + 50 * sub
                if "Psychic" in worker.traits:
                    disposition -= 50
            if check_lovers(hero, worker):
                disposition -= 200
            elif check_friends(hero, worker):
                disposition -= 100
            if "Natural Follower" in worker.traits:
                disposition -= 50
            elif "Natural Leader" in worker.traits:
                disposition += 50
            if "Heavy Drinker" in worker.traits:
                disposition -= 150
            if "Indifferent" in worker.traits:
                disposition += 100
            return disposition

        def settle_workers_disposition(self, worker, log=None):
            """
            handles penalties in case of wrong job
            """
            if log is None:
                log = []

            if not("Server" in worker.gen_occs):
                sub = check_submissivity(worker)
                if worker.status != 'slave':
                    if sub < 0:
                        if dice(15):
                            worker.logws('character', 1)
                        log.append("%s is not very happy with %s current job as a barmaid, but %s will get the job done." % (worker.name, worker.pp, worker.p))
                    elif sub == 0:
                        if dice(25):
                            worker.logws('character', 1)
                        log.append("%s serves customers as a barmaid, but, truth be told, %s would prefer to do something else." % (worker.nickname, worker.p))
                    else:
                        if dice(35):
                            worker.logws('character', 1)
                        log.append("%s makes it clear that %s wants another job before getting busy with clients." % (worker.name, worker.p))
                    worker.logws("joy", -randint(3, 5))
                    worker.logws("disposition", -randint(5, 10))
                    worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
                else:
                    if sub < 0:
                        if worker.get_stat("disposition") < self.calculate_disposition_level(worker):
                            log.append("%s is a slave so no one really cares, but being forced to work as a barmaid, %s's quite upset." % (worker.name, worker.p))
                        else:
                            log.append("%s will do as %s is told, but doesn't mean that %s'll be happy about %s bar duties." % (worker.name, worker.p, worker.p, worker.pp))
                        if dice(25):
                            worker.logws('character', 1)
                    elif sub == 0:
                        if worker.get_stat("disposition") < self.calculate_disposition_level(worker):
                            log.append("%s will do as you command, but %s will hate every second of %s barmaid shift..." % (worker.name, worker.p, worker.pp))
                        else:
                            log.append("%s was very displeased by %s order to work as a barmaid, but didn't dare to refuse." % (worker.name, worker.pp))
                        if dice(35):
                            worker.logws('character', 1)
                    else:
                        if worker.get_stat("disposition") < self.calculate_disposition_level(worker):
                            log.append("%s was very displeased by %s order to work as a barmaid, and makes it clear for everyone before getting busy with clients." % (worker.name, worker.pp))
                        else:
                            log.append("%s will do as you command and work as a barmaid, but not without a lot of grumbling and complaining." % worker.name)
                        if dice(45):
                            worker.logws('character', 1)
                    if worker.get_stat("disposition") < self.calculate_disposition_level(worker):
                        worker.logws("joy", -randint(5, 10))
                        worker.logws("disposition", -randint(5, 15))
                        worker.logws('vitality', -randint(5, 10))
                    else:
                        worker.logws("joy", -randint(2, 4))
                        worker.logws('vitality', -randint(1, 4))
            else:
                log.append(choice(["%s is doing %s shift as a barmaid." % (worker.name, worker.pp),
                                   "%s gets busy with clients." % worker.fullname,
                                   "%s serves customers in the bar." % worker.nickname]))
            return True

        def work_bar(self, worker, clients, effectiveness, log):

            len_clients = len(clients)
            building = log.loc

            bartending = self.normalize_required_skill(worker, "bartending", effectiveness, building.tier)
            charisma = self.normalize_required_stat(worker, "charisma", effectiveness, building.tier)

            if bartending > 150:
                if dice(70):
                    log.logloc('reputation', 1)
                log.append("%s was an excellent bartender, customers kept spending their money just for the pleasure of %s company." % (worker.pC, worker.pp))
            elif bartending >= 100:
                if dice(50):
                    log.logloc('reputation', 1)
                log.append("Customers were pleased with %s company and kept asking for more booze." % worker.pp)
            elif bartending >= 75:
                if dice(10):
                    log.logloc('reputation', 1)
                log.append("%s was skillful enough not to mess anything up during %s job." % (worker.pC, worker.pp))
            elif bartending >= 50:
                if dice(70):
                    log.logloc('reputation', -1)
                log.append("%s performance was rather poor and it most definitely has cost you income." % worker.ppC)
            else:
                log.logloc('reputation', -2)
                log.append("%s is a very unskilled bartender, %s definitely needs training." % (worker.name, worker.p))

            if charisma > 150:
                if dice(70):
                    log.logloc('fame', 1)
                log.append("Your worker was stunningly charming, customers couldn't keep their eyes off %s." % worker.op)
            elif charisma > 100:
                if dice(50):
                    log.logloc('fame', 1)
                log.append("Your worker looked beautiful, this will bring more customers.")
            elif charisma > 75:
                if dice(20):
                    log.logloc('fame', 1)
                log.append("Your worker was easy on the eyes, not bad for a bartender.")
            elif charisma > 50:
                log.append("Your may consider buying some items for your worker. %s's not exactly pleasant to look at." % worker.pC)
            else:
                log.logloc('fame', -2)
                log.append("Customers did not appreciate a hag serving them. Consider sending this worker to a beauty school.")

            log.append("\n")

            #Stat Mods
            # Award EXP:
            if effectiveness >= 90:
                log.logws("exp", exp_reward(worker, log.loc.tier))
            else:
                log.logws("exp", exp_reward(worker, log.loc.tier, exp_mod=.5))

            log.logws('bartending', choice([1, 2]))
            log.logws('refinement', choice([0, 0, 0, 1]))
            log.logws('vitality', round_int(len_clients*-.5))

            if worker.has_image("waitress", exclude=["sex"]):
                log.img = worker.show("waitress", exclude=["sex"])
            elif worker.has_image("maid", exclude=["sex"]):
                log.img = worker.show("maid", exclude=["sex"])
            else:
                log.img = worker.show("profile", exclude=["sex", "nude"])
