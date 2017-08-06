init -5 python:
    class BarJob(Job):
        def __init__(self):
            super(BarJob, self).__init__()
            self.id = "Bartending"
            self.type = "Service"

            # Traits/Job-types associated with this job:
            self.occupations = ["Server"] # General Strings likes SIW, Warrior, Server...
            self.occupation_traits = [traits["Maid"]] # Corresponding traits...

            # Relevant skills and stats:
            self.base_skills = {"bartending": 100}
            self.base_stats = {"intelligence": 25, "constitution": 25, "character": 25}

            self.desc = "Barmaids serve drinks from the bar and occasionally chat with customers."

        def traits_and_effects_effectiveness_mod(self, worker, log):
            effectiveness = 0
            if worker.effects['Food Poisoning']['active']:
                log.append("%s suffers from Food Poisoning, and is very far from her top shape." % worker.name)
                effectiveness -= 50
            elif worker.effects['Down with Cold']['active']:
                log.append("%s is not feeling well due to colds..." % worker.name)
                effectiveness -= 15
            elif worker.effects['Drunk']['active']:
                log.append("Being drunk, %s perfectly understands her customers who also are far from sobriety." % worker.name)
                effectiveness += 20

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected

                traits = list(i.id for i in worker.traits if i in ["Great Arse", "Bad Eyesight",
                                "Curious", "Indifferent", "Neat", "Messy", "Heavy Drinker",
                                "Ill-mannered", "Psychic", "Shy"])
                if "Lolita" in worker.traits and worker.height == "short":
                    traits.append("Lolita")
                if traits:
                    trait = random.choice(traits)
                else:
                    return effectiveness

                if trait == "Great Arse":
                    log.append("Customers keep ordering drinks from lower shelves to see %s bending over. What a view!" % worker.name)
                    effectiveness += 25
                elif trait == "Lolita":
                    log.append("Poor %s has a hard time with the top shelves of the bar due to her height." % worker.name)
                    effectiveness -= 20
                elif trait == "Bad Eyesight":
                    log.append("Occasionally %s serves the wrong drinks due to her bad eyesight, making customers unhappy." % worker.name)
                    effectiveness -= 15
                elif trait == "Curious":
                    log.append("Curious %s can listen to customers complaints about their lives for hours, making a great barmaid." % worker.name)
                    effectiveness += 10
                elif trait == "Indifferent":
                    log.append("%s shows no interest in conversations with drunk customers, upsetting them a little." % worker.name)
                    effectiveness -= 10
                elif trait == "Neat":
                    log.append("%s keeps the bar and all the glasses perfect clean, making a good impression on customers." % worker.name)
                    effectiveness += 30
                elif trait == "Messy":
                    log.append("It's not unusual for %s to serve drinks without cleaning glasses first. That does not add to her popularity as a barmaid." % worker.name)
                    effectiveness -= 30
                elif trait == "Heavy Drinker":
                    log.append("%s's deep knowledge of alcohol helps to serve the best possible drink." % worker.name)
                    effectiveness += 10
                elif trait == "Ill-mannered":
                    log.append("Unfortunately %s's rudeness scares away customers, affecting the business." % worker.name)
                    effectiveness -= 20
                elif trait == "Psychic":
                    log.append("As a psychic, %s always has the best advice for her customers, knowing what they want to hear." % worker.name)
                    effectiveness += 25
                elif trait == "Shy":
                    log.append("%s is too shy for a proper conversation with her customers today, something that drunk people don't really appreciate." % worker.name)
                    effectiveness -= 25
            return effectiveness

        def effectiveness(self, worker, difficulty, log):
            """
            difficulty is used to counter worker tier.
            100 is considered a score where worker does the task with acceptable performance.
            """
            base_effectiveness = super(BarJob, self).effectiveness(worker, difficulty, log)

            # Do whatever has to be done for the job:
            effectiveness = base_effectiveness + 0

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

        def settle_workers_disposition(self, worker, log):
            """
            handles penalties in case of wrong job
            """
            if not("Maid" in worker.traits):
                sub = check_submissivity(worker)
                if worker.status != 'slave':
                    if sub < 0:
                        if dice(15):
                            worker.logws('character', 1)
                        log.append("%s is not very happy with her current job as a barmaid, but she will get the job done." % worker.name)
                    elif sub == 0:
                        if dice(25):
                            worker.logws('character', 1)
                        log.append("%s serves customers as a barmaid, but, truth be told, she would prefer to do something else." % worker.nickname)
                    else:
                        if dice(35):
                            worker.logws('character', 1)
                        log.append("%s makes it clear that she wants another job before getting busy with clients." % worker.name)
                    worker.logws("joy", -randint(3, 5))
                    worker.logws("disposition", -randint(5, 10))
                    worker.logws('vitality', -randint(2, 5)) # a small vitality penalty for wrong job
                else:
                    if sub < 0:
                        if worker.disposition < self.calculate_disposition_level(worker):
                            log.append("%s is a slave so no one really cares but, being forced to work as a barmaid, she's quite upset." % worker.name)
                        else:
                            log.append("%s will do as she is told, but doesn't mean that she'll be happy about her bar duties." % worker.name)
                        if dice(25):
                            worker.logws('character', 1)
                    elif sub == 0:
                        if worker.disposition < self.calculate_disposition_level(worker):
                            log.append("%s will do as you command, but she will hate every second of her barmaid shift..." % worker.name)
                        else:
                            log.append("%s was very displeased by her order to work as a barmaid, but didn't dare to refuse." % worker.name)
                        if dice(35):
                            worker.logws('character', 1)
                    else:
                        if worker.disposition < self.calculate_disposition_level(worker):
                            log.append("%s was very displeased by her order to work as a barmaid, and makes it clear for everyone before getting busy with clients." % worker.name)
                        else:
                            log.append("%s will do as you command and work as a barmaid, but not without a lot of grumbling and complaining." % worker.name)
                        if dice(45):
                            worker.logws('character', 1)
                    if worker.disposition < self.calculate_disposition_level(worker):
                        worker.logws("joy", -randint(5, 10))
                        worker.logws("disposition", -randint(5, 15))
                        worker.logws('vitality', -randint(5, 10))
                    else:
                        worker.logws("joy", -randint(2, 4))
                        worker.logws('vitality', -randint(1, 4))
            else:
                log.append(choice(["%s is doing her shift as a barmaid." % worker.name, "%s gets busy with clients." % worker.fullname, "%s serves customers in the bar." % worker.nickname]))
            return True

        def bar_task(self, worker, clients, loc, log):

            len_clients = len(clients)

            serviceskill = worker.get_skill("bartending")
            charisma = worker.charisma

            # Skill checks, TODO: This should prolly die or be moved to another place?
            if serviceskill > 2000:
                log.logloc('reputation', choice([0, 1, 2]))
                log.append("She was an excellent bartender, customers kept spending their money just for the pleasure of her company. \n")

            elif serviceskill >= 1000:
                log.logloc('reputation', choice([0, 1]))
                log.append("Customers were pleased with her company and kept asking for more booze. \n")

            elif serviceskill >= 500:
                log.logloc('reputation', choice([0, 0, 0, 0, 0, 1]))
                log.append("She was skillful enough not to mess anything up during her job. \n")

            elif serviceskill >= 100:
                log.logloc('reputation', -1)
                log.append("Her performance was rather poor and it most definitely has cost you income. \n")

            else:
                log.logloc('reputation', -2)
                log.append("She is a very unskilled bartender, this girl definitely needs training \n")

            if charisma > 300:
                log.logloc('fame', choice([0,1,1]))
                log.append("Your girl was stunningly pretty, customers couldn't keep their eyes off her. \n")

            elif charisma > 150:
                log.logloc('fame', choice([0,0,1]))
                log.append("Your girl looked beautiful, this will not go unnoticed. \n")

            elif charisma > 45:
                log.logloc('fame', choice([0, 0, 0, 1]))
                log.append("Your girl was easy on the eyes, not bad for a bartender. \n")

            else:
                log.logloc('fame', -2)
                log.append("Customers did not appreciate a hag serving them. Consider sending this girl to a beauty school. \n")

            log.append("\n")

            #Stat Mods
            log.logws('exp', randint(15, 25))
            log.logws('bartending', choice([1, 2]))
            log.logws('refinement', choice([0, 0, 0, 1]))
            log.logws('vitality', len_clients * -3)

            # Integers:
            # barfees = int(round(worker.earned_cash))
            # tips = int(round(worker.flag("jobs_" + self.id + "_tips")))
            #
            # if tips:
            #     log.append("She got %d in tips! " % tips)

            if worker.has_image("waitress", exclude=["sex"]):
                log.img = worker.show("waitress", exclude=["sex"], resize=(740, 685))
            elif worker.has_image("maid", exclude=["sex"]):
                log.img = worker.show("maid", exclude=["sex"], resize=(740, 685))
            else:
                log.img = worker.show("profile", exclude=["sex", "nude"], resize=(740, 685))

            # Finances:
            # worker.fin.log_logical_income(barfees, "Barmaid")
            # if tips:
            #     worker.mod_flag("jobs_tips", tips)

            # self.loc.fin.log_logical_income(tips, "Barmaid")
            #
            # self.apply_stats()
            # self.finish_job()
