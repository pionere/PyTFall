init -5 python:
    ####################### Whore Job  ############################
    class WhoreJob(Job):
        def __init__(self):
            super(WhoreJob, self).__init__()
            self.id = "Whore Job"
            self.type = "SIW"

            # Traits/Job-types associated with this job:
            self.occupations = ["SIW"] # General Strings likes SIW, Warrior, Server...
            self.occupation_traits = [traits["Prostitute"]] # Corresponding traits...

            self.disposition_threshold = 950 # Any worker with disposition this high will be willing to do the job even without matched traits.

            self.base_skills = {"sex": 60, "vaginal": 40, "anal": 40, "oral": 40}
            self.base_stats = {"charisma": 100}

        def traits_and_effects_effectiveness_mod(self, worker, log):
            """Affects worker's effectiveness during one turn. Should be added to effectiveness calculated by the function below.
               Calculates only once per turn, in the very beginning.
            """
            effectiveness = 0
             # effects always work
            if worker.effects['Food Poisoning']['active']:
                log.append("%s suffers from Food Poisoning, and is very far from her top shape." % worker.name)
                effectiveness -= 50
            elif worker.effects['Down with Cold']['active']:
                log.append("%s is not feeling well due to colds..." % worker.name)
                effectiveness -= 10
            elif worker.effects['Horny']['active']:
                log.append("%s is horny. A perfect mindset for her job!" % worker.name)
                effectiveness += 10

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected

                traits = list(i for i in worker.traits if i in ["Ill-mannered", "Always Hungry", "Heavy Drinker", "Neat", "Messy", "Homebody", "Indifferent", "Open Minded", "Dawdler", "Energetic", "Sexy Air", "Frigid", "Nymphomaniac", "Psychic", "Flexible", "Lactation"])
                if traits:
                    trait = random.choice(traits)
                else:
                    return effectiveness

                if trait == "Ill-mannered":
                    log.append("%s is pretty rude today, but fortunately in bed her unciviliness makes customers harder." % worker.name)
                    effectiveness += 20
                elif trait == "Always Hungry":
                    if locked_dice(50):
                        log.append("Sperm is a good source of protein, and today %s intends to get all protein available!" % worker.name)
                        effectiveness += 15
                    else:
                        log.append("Hungry %s eats her snacks all the day, making customers feel like they are less important for her than food... Which may be true." % worker.name)
                        effectiveness -= 15
                        log.logloc("dirt", 1)
                elif trait == "Heavy Drinker":
                    if locked_dice(50):
                        log.append("Unfortunately %s drank too much yesterday evening, and currently suffers from a headache." % worker.name)
                        effectiveness -= 15
                    else:
                        log.append("Slightly drunk %s sexually assaults customers all the day, making them happy to oblige." % worker.name)
                        effectiveness += 15
                elif trait == "Neat":
                    log.append("Unfortunately %s is too focused on keeping her freshly laundered clothes clean instead of satisfying her partners..." % worker.name)
                    effectiveness -= 25
                elif trait == "Messy":
                    log.append("Today %s wants it really sloppy and messy, attracting customers with similar tastes." % worker.name)
                    log.logloc("dirt", randint(1, 2))
                    effectiveness += 25
                elif trait == "Homebody":
                    log.append("%s really enjoys her job, having warm food and soft bed nearby all the time. Nice to see someone who enjoys work." % worker.name)
                    effectiveness += 10
                elif trait == "Indifferent":
                    log.append("Somehow %s doesn't care much about being fucked today, and most customers don't appreciate it." % worker.name)
                    effectiveness -= 15
                elif trait == "Open Minded":
                    log.append("%s has no problems trying different things sexually, making a perfect partner for customers with unusual tastes." % worker.name)
                    effectiveness += 20
                elif trait == "Dawdler":
                    log.append("%s's slow movements find favor among oversensitive customers who'd came too soon otherwise." % worker.name)
                    effectiveness += 15
                elif trait == "Energetic":
                    log.append("%s's moves too fast for her own good today, rushing too much to the displeasure of her partners." % worker.name)
                    effectiveness -= 15
                elif trait == "Sexy Air":
                    log.append("%s's sexiness gives customers more fuel, resulting in better satisfaction." % worker.name)
                    effectiveness += 10
                elif trait == "Frigid":
                    log.append("For %s sex is just a boring job, and many customers don't appreciate it." % worker.name)
                    effectiveness -= 35
                elif trait == "Nymphomaniac":
                    log.append("%s is always glad to engage in sex, and this job is just perfect for her." % worker.name)
                    effectiveness += 35
                elif trait == "Psychic":
                    log.append("Knowing what her partners really want is a trivial matter for a psychic like %s, making her customers happier." % worker.name)
                    effectiveness += 25
                elif trait == "Lactation":
                    log.append("Sometimes customers are happy to swallow liquids too. As in the case of %s's milk which is produced more than usual today." % worker.name)
                    effectiveness += 15
            return effectiveness

        def effectiveness(self, worker, difficulty, log):
            """Checking effectiveness specifically for whore job.

            difficulty is used to counter worker's tier.
            100 is considered a score where worker does the task with acceptable performance.
            """
            if worker.occupations.intersection(self.occupations):
                effectiveness = 50
            else:
                effectiveness = 0
            # 25 points for difference between difficulty/tier:
            diff = difficulty - worker.tier
            effectiveness += diff*25
            return effectiveness

        def calculate_disposition_level(self, worker): # calculating the needed level of disposition; since it's whoring we talking about, values are really close to max, or even higher than max in some cases, making it impossible
            sub = check_submissivity(worker)
            if "Shy" in worker.traits:
                disposition = 900 + 50 * sub
            else:
                disposition = 800 + 50 * sub
            if "Open Minded" in worker.traits:  # really powerful trait
                disposition = disposition // 2
            if cgochar(worker, "SIW") or "Nymphomaniac" in worker.traits:
                disposition -= 200
            elif "Frigid" in worker.traits:
                disposition += 200
            if "Natural Follower" in worker.traits:
                disposition -= 50
            elif "Natural Leader" in worker.traits:
                disposition += 50


            if check_lovers(worker, hero): # Virgin trait makes whoring problematic, unless Chastity effect is active which should protect Virgin trait all the time no matter what
                if "Virgin" in worker.traits and "Dedicated" in worker.traits:
                    disposition += 2000 # not a typo; they never agree, even with Chastity effect
                    return disposition

                if "Virgin" in worker.traits and not(worker.effects['Chastity']['active']):
                    disposition += 300
                else:
                    disposition -= 100
            elif check_friends(hero, worker):
                if "Virgin" in worker.traits and worker.disposition >= 900 and not(worker.effects['Chastity']['active']):
                    disposition += 100
                else:
                    disposition -= 50
            elif "Virgin" in worker.traits and not(worker.effects['Chastity']['active']):
                disposition += 50
            return disposition

        def settle_workers_disposition(self, worker, log): # handles penalties in case of wrong job
            if not("Prostitute" in worker.traits):
                sub = check_submissivity(worker)
                if worker.status != 'slave':
                    if sub < 0:
                        if dice(15):
                            worker.logws('character', 1)
                        log.append("%s is not very happy with her current job as a harlot, but she will get the job done." % worker.name)
                    elif sub == 0:
                        if dice(25):
                            worker.logws('character', 1)
                        log.append("%s serves customers as a whore, but, truth be told, she would prefer to do something else." % worker.nickname)
                    else:
                        if dice(35):
                            worker.logws('character', 1)
                        log.append("%s makes it clear that she wants another job before getting busy with clients." % worker.name)
                    worker.logws("joy", -randint(3, 6))
                    worker.logws("disposition", -randint(20, 40))
                    worker.logws('vitality', -randint(2, 8)) # a small vitality penalty for wrong job
                else:
                    if sub < 0:
                        if worker.disposition < self.calculate_disposition_level(worker):
                            log.append("%s is a slave so no one really cares but, being forced to work as a whore, she's quite upset." % worker.name)
                        else:
                            log.append("%s will do as she is told, but doesn't mean that she'll be happy about doing 'it' with strangers." % worker.name)
                        if dice(25):
                            worker.logws('character', 1)
                    elif sub == 0:
                        if worker.disposition < self.calculate_disposition_level(worker):
                            log.append("%s will do as you command, but she will hate every second of her harlot shift..." % worker.name)
                        else:
                            log.append("%s was very displeased by her order to work as a whore, but didn't dare to refuse." % worker.name)
                        if dice(35):
                            worker.logws('character', 1)
                    else:
                        if worker.disposition < self.calculate_disposition_level(worker):
                            log.append("%s was very displeased by her order to work as a whore, and makes it clear for everyone before getting busy with clients." % worker.name)
                        else:
                            log.append("%s will do as you command and work as a harlot, but not without a lot of grumbling and complaining." % worker.name)
                        if dice(45):
                            worker.logws('character', 1)
                    if worker.disposition < self.calculate_disposition_level(worker):
                        worker.logws("joy", -randint(5, 10))
                        worker.logws("disposition", -randint(25, 50))
                        worker.logws('vitality', -randint(10, 15))
                    else:
                        worker.logws("joy", -randint(3, 6))
                        worker.logws("disposition", -randint(20, 40))
                        worker.logws('vitality', -randint(2, 8))
            else:
                log.append(choice(["%s is doing her shift as a harlot." % worker.name, "%s gets busy with clients." % worker.fullname, "%s serves customers as a whore." % worker.nickname]))
            return True

        def acts(self, worker, client, loc, log):
            skill = 0
            # Pass the flags from occupation_checks:
            # log.append(worker.flag("jobs_whoreintro"))
            log.append("\n\n")

            width = 820
            height = 705

            size = (width, height)
            # Acts, Images, Tags and things Related:
            # Straight Sex Act
            if client.act == 'sex':
                kwargs = dict(exclude=["rape", "angry", "in pain", "dungeon", "sad", "gay", "restrained"], resize=size, type="reduce", add_mood=False)
                log.append(choice(["%s hired her for some good old straight sex. " % client.name, "%s is willing to pay for her pussy. " % client.name]))
                if "Lesbian" in worker.traits: # lesbians will have only a part of skill level compared to others during normal sex
                    skill = round(worker.get_skill("vaginal")*0.6 + worker.get_skill("sex")*0.15)
                    vaginalmod = 1 if dice(20) else 0
                    sexmod = 1 if dice(8) else 0
                else:
                    skill = round(worker.get_skill("vaginal")*0.75 + worker.get_skill("sex")*0.25)
                    vaginalmod = 1 if dice(25) else 0
                    sexmod = 1 if dice(10) else 0
                # Temporarily done here, should be moved to game init and after_load to improve performance
                # probably not everything though, since now we don't form huge lists of pictures for some acts, using get_image_tags to figure out poses
                if worker.has_image("2c vaginal", **kwargs):
                    log.img = worker.show("2c vaginal", **kwargs)
                else:
                    log.img = worker.show("after sex", exclude=["angry", "in pain", "dungeon", "sad"], **kwargs)
                image_tags = log.img.get_image_tags()
                if "ontop" in image_tags:
                    log.append("He invited her to 'sit' on his lap as he unsheathed his cock. They've continued along the same lines in 'girl ontop' position. \n")
                elif "doggy" in image_tags:
                    log.append("He ordered %s to bend over and took her from behind. \n"%worker.nickname)
                elif "missionary" in image_tags:
                    log.append("He pushed %s on her back, shoved his cock in, screaming: 'Oh, Your pussy is wrapping around me so tight!' \n"%worker.nickname)
                elif "onside" in image_tags:
                    log.append("%s lay on her side inviting the customer to fuck her. He was more than happy to oblige.\n"%worker.nickname)
                elif "standing" in image_tags:
                    log.append("Not even bothering getting into a position, he took her standing up. \n")
                elif "spooning" in image_tags:
                    log.append("Customer felt cuddly so he spooned the girl until they both cummed. \n")
                else:
                    log.append(choice(['He wanted some old-fashioned straight fucking. \n',
                                                         'He was in the mood for some pussy pounding. \n',
                                                         'He asked for some playtime with her vagina.\n']))
                # Virgin trait check:
                self.take_virginity(worker, loc, log)


            # Anal Sex Act
            elif client.act == 'anal':
                kwargs = dict(exclude=["rape", "angry", "in pain", "dungeon", "sad", "gay", "restrained"], resize=size, type="reduce", add_mood=False)
                log.append(choice(["%s hired her for some anal fun. " % client.name, "%s is willing to pay her for backdoor action. " % client.name]))
                if "Lesbian" in worker.traits:
                    skill = round(worker.get_skill("anal")*0.6 + worker.get_skill("sex")*0.15)
                    analmod = 1 if dice(20) else 0
                    sexmod = 1 if dice(8) else 0
                else:
                    skill = round(worker.get_skill("anal")*0.75 + worker.get_skill("sex")*0.25)
                    analmod = 1 if dice(25) else 0
                    sexmod = 1 if dice(10) else 0
                log.append(choice(["Anal sex is the best, customer thought... ",
                                                      "I am in the mood for a good anal fuck, customer said. ",
                                                      "Customer's dick got harder and harder just from the thought of %s's asshole! "%worker.nickname]))

                if worker.has_image("2c anal", **kwargs):
                    log.img = worker.show("2c anal", **kwargs)
                else:
                    log.img = worker.show("after sex", exclude=["angry", "in pain", "dungeon", "sad"], **kwargs)
                image_tags = log.img.get_image_tags()
                if "ontop" in image_tags:
                    log.append("He invited her to 'sit' on his lap as he unsheathed his cock. They've continued along the same lines in 'girl on top' position. \n")
                elif "doggy" in image_tags:
                    log.append("He ordered %s to bend over and took her from behind. \n"%worker.nickname)
                elif "missionary" in image_tags:
                    log.append("He pushed %s on her back, shoved his cock in, screaming: 'Oh, Your anus is wrapping around me so tight!' \n"%worker.nickname)
                elif "onside" in image_tags:
                    log.append("%s lays on her side inviting the customer to fuck her. He was more than happy to oblige.\n"%worker.nickname)
                elif "standing" in image_tags:
                    log.append("Not even bothering getting into a position, he took her standing up. \n")
                elif "spooning" in image_tags:
                    log.append("Customer felt cuddly so he spooned the girl until they both cummed. \n")
                else:
                    log.append(choice(['He took her in the ass right there and then. \n',
                                                          'He got his dose of it. \n',
                                                          'And so he took her in her butt. \n']))

            # Various job acts
            elif client.act == 'blowjob':
                kwargs = dict(exclude=["rape", "angry", "in pain", "dungeon", "sad", "gay", "restrained"], resize=size, type="reduce", add_mood=False)
                log.append(choice(["%s hired her for some side job on his thing. " % client.name, "%s is paying her today for naughty service. " % client.name]))
                # here we will have to choose skills depending on selected act
                tags = ({"tags": ["bc deepthroat"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["bc handjob"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["bc footjob"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["bc titsjob"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["bc blowjob"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["after sex"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"], "dice":20})
                act = self.get_act(worker, tags)
                if act == tags[0]:
                    log.append(choice(["He shoved his cock all the way into her throat! \n", "Deepthroat is definitely my style, thought the customer... \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.65 + worker.get_skill("sex")*0.1)
                        oralmod = 1 if dice(20) else 0
                        sexmod = 1 if dice(8) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.8 + worker.get_skill("sex")*0.2)
                        oralmod = 1 if dice(25) else 0
                        sexmod = 1 if dice(10) else 0
                    log.img = worker.show("bc deepthroat", **kwargs)
                elif act == tags[1]:
                    log.append("He told %s to give him a good handjob.\n"%worker.nickname)
                    if "Lesbian" in worker.traits: # lesbians will have 0.7 of skill level compared to others during normal sex
                        skill = round(worker.get_skill("oral")*0.1 + worker.get_skill("sex")*0.6)
                        oralmod = 1 if dice(20) else 0
                        sexmod = 1 if dice(8) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.25 + worker.get_skill("sex")*0.75)
                        oralmod = 1 if dice(25) else 0
                        sexmod = 1 if dice(10) else 0
                    log.img = worker.show("bc handjob", **kwargs)
                elif act == tags[2]:
                    log.append(choice(["He asked her for a footjob.\n", "Footjob might be a weird fetish but that's what the customer wanted...\n"]))
                    if "Lesbian" in worker.traits: # lesbians will have 0.7 of skill level compared to others during normal sex
                        skill = round(worker.get_skill("oral")*0.1 + worker.get_skill("sex")*0.6)
                        oralmod = 1 if dice(20) else 0
                        sexmod = 1 if dice(8) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.25 + worker.get_skill("sex")*0.75)
                        oralmod = 1 if dice(25) else 0
                        sexmod = 1 if dice(10) else 0
                    log.img = worker.show("bc footjob", **kwargs)
                elif act == tags[3]:
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.1 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        oralmod = 1 if dice(8) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        oralmod = 1 if dice(10) else 0
                    if traits["Big Boobs"] in worker.traits or traits["Abnormally Large Boobs"] in worker.traits:
                        log.append(choice(["He went straight for her big boobs. \n", "Seeing her knockers, customer wanted nothing else then to park his dick between them. \n", "Lustfully gazing on your girl's burst, he asked for a titsjob. \n", "He put his manhood between her big tits. \n" , "He showed his cock between %s's enormous breasts. \n"%worker.nickname]))
                    elif traits["Small Boobs"] in worker.traits:
                        if dice(15):
                            log.append("With a smirk on his face, customer asked for a titsjob. He was having fun from her vain efforts. \n")
                        else:
                            log.append(choice(["He placed his cock between her breasts, clearly enjoining her flat chest. \n", "Even when knowing that her breasts are small, he wanted to be caressed by them. \n"]))
                    else:
                        log.append(choice(["He asked for a titsjob. \n", "He let %s to caress him with her breasts. \n", "He showed his cock between %s's tits. \n"%worker.nickname]))
                    log.img = worker.show("bc titsjob", **kwargs)
                elif act == tags[4]:
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("sex")*0.75)
                        sexmod = 1 if dice(20) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.1 + worker.get_skill("sex")*0.9)
                        sexmod = 1 if dice(25) else 0
                        oralmod = 1 if dice(5) else 0
                    log.append(choice(["Customer wanted nothing else then to jerk himself in from of her and ejaculate on her face. \n", "He wanked himself hard in effort to cover her with his cum. \n"]))
                    log.img = worker.show("after sex", **kwargs)
                elif act == tags[5]:
                    log.append(choice(['Client was in mood for some oral sex. \n', 'Client was in the mood for a blowjob. \n', 'He asked her to lick his dick. \n']))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.65 + worker.get_skill("sex")*0.1)
                        sexmod = 1 if dice(20) else 0
                        oralmod = 1 if dice(8) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.8 + worker.get_skill("sex")*0.2)
                        sexmod = 1 if dice(25) else 0
                        oralmod = 1 if dice(10) else 0
                    log.img = worker.show("bc blowjob", **kwargs)
                else: # I do not thing that this will ever be reached...
                    log.append(choice(['Client was in mood for some oral sex. \n', 'Client was in the mood for a blowjob. \n', 'He asked her to lick his dick. \n']))
                    skill = worker.get_skill("oral")
                    oralmod = 1 if dice(20) else 0
                    log.img = worker.show("bc blowjob", **kwargs)

            # Lesbian Act
            elif client.act == 'lesbian':
                log.append("%s hired her for some hot girl on girl action. " % client.name)
                skill = worker.get_skill("vaginal")
                kwargs = dict(exclude=["rape", "angry", "in pain", "dungeon", "sad", "restrained"], resize=size, type="reduce", add_mood=False)
                tags = ({"tags": ["gay", "2c lickpussy"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc lickpussy"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "2c lickanus"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc lickanus"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "2c vaginalfingering"], "exclude": ["rape", "angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc vagnalhandjob"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "2c analfingering"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc analhandjob"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "2c caresstits"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc caresstits"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc hug", "2c hug"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "2c vaginal"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc vaginal"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "2c anal"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc anal"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "2c vaginaltoy"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc toypussy"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "2c analtoy"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "bc toyanal"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]}, {"tags": ["gay", "scissors"], "exclude": ["angry", "in pain", "dungeon", "sad", "restrained"]})
                act = self.get_act(worker, tags)
                # We'll be adding "les" here as Many lesbian pics do not fall in any of the categories and will never be called...
                if act == tags[0]:
                    log.append(choice(["Clearly in the mood for some cunt, she licked %ss pussy clean.\n"%worker.nickname,
                                                         "Hungry for a cunt, she told %s to be still and started licking her soft pussy with her hot tong. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits: # bisexuals will have normal value during lesbian action, lesbians will get ~1.2 of skill, and straight ones ~0.8
                        skill = round(worker.get_skill("oral")*0.2 + worker.get_skill("vaginal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        oralmod = 1 if dice(10) else 0
                        vaginalmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.15 + worker.get_skill("vaginal")*0.15 + worker.get_skill("sex")*0.7)
                        sexmod = 1 if dice(22) else 0
                        oralmod = 1 if dice(9) else 0
                        vaginalmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.1 + worker.get_skill("vaginal")*0.1 + worker.get_skill("sex")*0.6)
                        sexmod = 1 if dice(20) else 0
                        oralmod = 1 if dice(8) else 0
                        vaginalmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "2c lickpussy", **kwargs)
                elif act == tags[1]:
                    log.append(choice(["All hot and bothered, she ordered %s to lick her cunt. \n"%worker.nickname,
                                                         "As if she had an itch, she quickly told %s to tong her pussy. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.8 + worker.get_skill("vaginal")*0.2 + worker.get_skill("sex")*0.2)
                        sexmod = 1 if dice(10) else 0
                        oralmod = 1 if dice(25) else 0
                        vaginalmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.7 + worker.get_skill("vaginal")*0.15 + worker.get_skill("sex")*0.15)
                        sexmod = 1 if dice(9) else 0
                        oralmod = 1 if dice(22) else 0
                        vaginalmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.6 + worker.get_skill("vaginal")*0.1 + worker.get_skill("sex")*0.1)
                        sexmod = 1 if dice(8) else 0
                        oralmod = 1 if dice(20) else 0
                        vaginalmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "bc lickpussy", **kwargs)
                elif act == tags[2]:
                    log.append(choice(["She licked %ss anus clean.\n"%worker.nickname,
                                                                                    "She told %s to be still and started licking her asshole with her hot tong. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.2 + worker.get_skill("anal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        oralmod = 1 if dice(10) else 0
                        analmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.15 + worker.get_skill("anal")*0.15 + worker.get_skill("sex")*0.7)
                        sexmod = 1 if dice(22) else 0
                        oralmod = 1 if dice(9) else 0
                        analmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.1 + worker.get_skill("anal")*0.1 + worker.get_skill("sex")*0.6)
                        sexmod = 1 if dice(20) else 0
                        oralmod = 1 if dice(8) else 0
                        analmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "2c lickanus", **kwargs)
                elif act == tags[3]:
                    log.append(choice(["All hot and bothered, she ordered %s to lick her asshole. \n"%worker.nickname,
                                                         "As if she had an itch, she quickly told %s to tong her anus. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.8 + worker.get_skill("anal")*0.2 + worker.get_skill("sex")*0.2)
                        sexmod = 1 if dice(10) else 0
                        oralmod = 1 if dice(25) else 0
                        analmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("oral")*0.7 + worker.get_skill("anal")*0.15 + worker.get_skill("sex")*0.15)
                        sexmod = 1 if dice(8) else 0
                        oralmod = 1 if dice(22) else 0
                        analmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("oral")*0.6 + worker.get_skill("anal")*0.1 + worker.get_skill("sex")*0.1)
                        sexmod = 1 if dice(8) else 0
                        oralmod = 1 if dice(20) else 0
                        analmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "bc lickanus", **kwargs)
                elif act == tags[4]:
                    log.append(choice(["In mood for a hot lesbo action, she stuck her fingers in your girls pussy. \n",
                                                         "She watched %s moan as she stuck fingers in her pussy. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.4 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        vaginalmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(22) else 0
                        vaginalmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("vaginal")*0.15 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        vaginalmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "2c vaginalfingering", **kwargs)
                elif act == tags[5]:
                    log.append(choice(["Quite horny, she ordered your girl to finger her cunt. \n",
                                                         "Clearly in the mood, she told %s to finger her until she cums. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.4 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        vaginalmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(22) else 0
                        vaginalmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("vaginal")*0.15 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        vaginalmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "bc vagnalhandjob", **kwargs)
                elif act == tags[6]:
                    log.append(choice(["In mood for a hot lesbo action, she stuck her fingers in your girls anus. \n",
                                                         "She watched %s moan as she stuck fingers in her asshole. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.4 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        analmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(22) else 0
                        analmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("anal")*0.15 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        analmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "2c analfingering", **kwargs)
                elif act == tags[7]:
                    log.append(choice(["Quite horny, she ordered your girl to finger her anus. \n",
                                                         "Clearly in the mood, she told %s to finger her asshole until she cums. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.4 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        analmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(22) else 0
                        analmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("anal")*0.15 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        analmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "bc analhandjob", **kwargs)
                elif act == tags[8]:
                    log.append(choice(["Liking your girls breasts, she had some good time caressing them. \n",
                                                         "She enjoyed herself by caressing your girls breasts. \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("sex")*1.1)
                        sexmod = 1 if dice(25) else 0
                    elif "Bisexual" in worker.traits:
                        skill = worker.get_skill("sex")
                        sexmod = 1 if dice(22) else 0
                    else:
                        skill = round(worker.get_skill("sex")*0.9)
                        sexmod = 1 if dice(20) else 0
                    log.img = worker.show("gay", "2c caresstits", **kwargs)
                elif act == tags[9]:
                    log.append(choice(["She asked your girl to caress her tits. \n",
                                                         "She told your girl to put a squeeze on her breasts. \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("sex")*1.1)
                        sexmod = 1 if dice(25) else 0
                    elif "Bisexual" in worker.traits:
                        skill = worker.get_skill("sex")
                        sexmod = 1 if dice(22) else 0
                    else:
                        skill = round(worker.get_skill("sex")*0.9)
                        sexmod = 1 if dice(20) else 0
                    log.img = worker.show("gay", "bc caresstits", **kwargs)
                elif act == tags[10]:
                    log.append(choice(["Girls lost themselves in eachothers embrace.\n",
                                                         "Any good lesbo action should start with a hug, don't you think??? \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("sex")*1.1)
                        sexmod = 1 if dice(25) else 0
                    elif "Bisexual" in worker.traits:
                        skill = worker.get_skill("sex")
                        sexmod = 1 if dice(22) else 0
                    else:
                        skill = round(worker.get_skill("sex")*0.9)
                        sexmod = 1 if dice(20) else 0
                    log.img = worker.show("gay", "bc hug", "2c hug", **kwargs)
                elif act == tags[11]:
                    log.append(choice(["She put on a strapon and fucked your girl in her cunt. \n",
                                                          "Equipping herself with a strap-on, she lustfully shoved it in %ss pussy. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.9 + worker.get_skill("sex")*0.3)
                        vaginalmod = 1 if dice(25) else 0
                        sexmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.75 + worker.get_skill("sex")*0.25)
                        vaginalmod = 1 if dice(22) else 0
                        sexmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("vaginal")*0.7 + worker.get_skill("sex")*0.2)
                        vaginalmod = 1 if dice(20) else 0
                        sexmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "2c vaginal", **kwargs)
                    self.take_virginity(worker, loc, log)
                elif act == tags[12]:
                    log.append(choice(["She ordered %s to put on a strapon and fuck her silly with it. \n"%worker.nickname,
                                                          "She equipped %s with a strapon and told her that she was 'up' for a good fuck! \n" %worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("sex")*0.9 + worker.get_skill("vaginal")*0.3)
                        sexmod = 1 if dice(25) else 0
                        vaginalmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("sex")*0.8 + worker.get_skill("vaginal")*0.2)
                        sexmod = 1 if dice(22) else 0
                        vaginalmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("sex")*0.6 + worker.get_skill("vaginal")*0.15)
                        sexmod = 1 if dice(20) else 0
                        vaginalmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "bc vaginal", **kwargs)
                elif act == tags[13]:
                    log.append(choice(["She put on a strapon and fucked your girl in her butt. \n",
                                                          "Equipping herself with a strapon, she lustfully shoved it in %s's asshole. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.9 + worker.get_skill("sex")*0.3)
                        analmod = 1 if dice(25) else 0
                        sexmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.75 + worker.get_skill("sex")*0.25)
                        analmod = 1 if dice(22) else 0
                        sexmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("anal")*0.6 + worker.get_skill("sex")*0.2)
                        analmod = 1 if dice(20) else 0
                        sexmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "2c anal", **kwargs)
                elif act == tags[14]:
                    log.append(choice(["She ordered %s to put on a strapon and butt-fuck her silly with it. \n"%worker.nickname,
                                                         "She equipped %s with a strapon and told her that she was 'up' for a good anal fuck! \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("sex")*0.9 + worker.get_skill("anal")*0.3)
                        sexmod = 1 if dice(25) else 0
                        analmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("sex")*0.8 + worker.get_skill("anal")*0.2)
                        sexmod = 1 if dice(22) else 0
                        analmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("sex")*0.6 + worker.get_skill("anal")*0.15)
                        sexmod = 1 if dice(20) else 0
                        analmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "bc anal", **kwargs)
                elif act == tags[15]:
                    log.append(choice(["She played with a toy and %ss pussy. \n"%worker.nickname,
                                                         "She stuck a toy up %s cunt. \n"%worker.nickname]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.4 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        vaginalmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(22) else 0
                        vaginalmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("vaginal")*0.15 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        vaginalmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "2c vaginaltoy", **kwargs)
                    self.take_virginity(worker, loc, log)
                elif act == tags[16]:
                    log.append(choice(["Without further ado, %s fucked her with a toy. \n"%worker.nickname,
                                                         "She asked your girl to fuck her pussy with a toy. \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.4 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        vaginalmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("vaginal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(22) else 0
                        vaginalmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("vaginal")*0.15 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        vaginalmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "bc toypussy", **kwargs)
                elif act == tags[17]:
                    log.append(choice(["After some foreplay, she stuck a toy up your girls butt. \n",
                                                                                   "For her money, she had some fun playing with a toy and your girls asshole. \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.4 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        analmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(22) else 0
                        analmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("anal")*0.15 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        analmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "2c analtoy", **kwargs)
                elif act == tags[18]:
                    log.append(choice(["After some foreplay, she asked %s to shove a toy up her ass. \n"%worker.nickname,
                                                         "This female customer of your brothel clearly believed that there is no greater pleasure than a toy up her butt. \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.4 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        analmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(22) else 0
                        analmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("anal")*0.15 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        analmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "bc toyanal", **kwargs)
                elif act == tags[19]:
                    log.append(choice(["She was hoping to get some clit to clit action, and she got it. \n",
                                                         "The female customer asked for a session of hot, sweaty tribadism. \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.4 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(25) else 0
                        analmod = 1 if dice(10) else 0
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("anal")*0.2 + worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(22) else 0
                        analmod = 1 if dice(9) else 0
                    else:
                        skill = round(worker.get_skill("anal")*0.15 + worker.get_skill("sex")*0.65)
                        sexmod = 1 if dice(20) else 0
                        analmod = 1 if dice(8) else 0
                    log.img = worker.show("gay", "scissors", **kwargs)
                else:
                    log.append(choice(["She was in the mood for some girl on girl action. \n", "She asked for a good lesbian sex. \n"]))
                    if "Lesbian" in worker.traits:
                        skill = round(worker.get_skill("sex")*1.1)
                        sexmod = 1 if dice(25) else 0
                    elif "Bisexual" in worker.traits:
                        skill = worker.get_skill("sex")
                        sexmod = 1 if dice(22) else 0
                    else:
                        skill = round(worker.get_skill("sex")*0.8)
                        sexmod = 1 if dice(20) else 0
                    log.img = worker.show("gay", **kwargs)
                    # Last fallback!

            else:
                log.append("Whore Job\n\nMissed All acts!\n\n")

                skill = worker.get_skill("sex")
                log.img = worker.show("sex", **kwargs)

            self.check_skills(skill, worker, client, log)

            # Take care of stats mods
            constmod = 1 if dice(12) else 0
            worker.logws("constitution", constmod)
            worker.logws("vitality", -randint(14, 28))
            sexskill = 0
            if 'sexmod' in locals():
                worker.logws("sex", sexmod)
                sexskill += 1
            if 'vaginalmod' in locals():
                worker.logws("vaginal", vaginalmod)
                sexskill += 1
            if 'analmod' in locals():
                worker.logws("anal", analmod)
                sexskill += 1
            if 'oralmod' in locals():
                worker.logws("oral", oralmod)
                sexskill += 1
            if sexskill + constmod > 0:
                log.append("\n%s feels like she learned something! \n"%worker.name)
                worker.logws("joy", 1)


            # Dirt:
            log.logloc("dirt", randint(2, 5))

            log.loc.fin.log_logical_income(1000000, "!!!!!!")

        @staticmethod
        def get_act(worker, tags):
            acts = list()
            for t in tags:
                if isinstance(t, tuple):
                    if worker.has_image(*t):
                        acts.append(t)
                elif isinstance(t, dict):
                    if worker.has_image(*t.get("tags", []), exclude=t.get("exclude", [])) and dice(t.get("dice", 100)):
                        acts.append(t)

            if acts:
                act = choice(acts)
            else:
                act = None

            return act

        @staticmethod
        def take_virginity(worker, loc, log): # let's just assume that dildos are too small to take virginity, otherwise it becomes too complicated in terms of girls control :)
            if traits["Virgin"] in worker.traits and not (worker.effects['Chastity']['active']):
                tips = 100 + worker.charisma * 3 # TODO Slave/Free payouts
                log.append("\n{color=[pink]}%s lost her virginity!{/color} Customer thought that was super hot and left a tip of {color=[gold]}%d Gold{/color} for the girl.\n\n"%(worker.nickname, tips))
                worker.remove_trait(traits["Virgin"])
                worker.mod_flag("jobs_tips", tips)
                loc.fin.log_logical_income(tips, "WhoreJob")

        def check_skills(self, skill, worker, client, log):
            # I'm making checks for stats and skills separately, otherwise it will be a nightmare even with an army of writers
            # first is charisma, as initial impression
            if worker.charisma >= 1500:
                log.append("Her supernal loveliness made the customer to shed tears of happiness, comparing %s to ancient goddess of love. Be wary of possible cults dedicated to her..." %worker.name)
                log.logws("joy", 1)
                log.logloc("fame", choice([0, 1, 1, 1]))
                log.logloc("reputation", choice([0, 1]))
            elif worker.charisma >= 800:
                log.append("%s made the customer fall in love with her unearthly beauty. Careful now girl, we don't need crowds of admires around our businesses..." %worker.name)
                log.logws("joy", 1)
                log.logloc("fame", choice([0, 1]))
                log.logloc("reputation", choice([0, 0, 1]))
            elif worker.charisma >= 500:
                log.append("%s completely enchanted the customer with her stunning beauty." %worker.name)
                log.logloc("fame", choice([0, 0, 1]))
                log.logloc("reputation", choice([0, 0, 0, 1]))
            elif worker.charisma >= 200:
                log.append("The client was happy to be alone with such a breathtakingly beautiful girl as %s." %worker.name)
                log.logloc("fame", choice([0, 0, 0, 1]))
            elif worker.charisma >= 100:
                log.append("%s good looks clearly was pleasing to the customer." %worker.name)
            elif worker.charisma >= 50:
                log.append("%s did her best to make the customer like her, but her beauty could definitely be enhanced." %worker.name)
                log.logloc("fame", choice([-1, 0, 0, 1]))
            else:
                log.logws("joy", -2)
                log.logloc("fame", choice([-1, 0]))
                if client.gender == "male":
                    log.append("The customer was unimpressed by %s looks, to say at least. Still, he preferred fucking her over a harpy. Hearing that from him however, was not encouraging for the poor girl at all..." %worker.name)
                else:
                    log.append("The customer was unimpressed by %s looks, to say at least. Still, she preferred fucking her over a harpy. Hearing that from her however, was not encouraging for the poor girl at all..." %worker.name)
            # then a small refinement check, useless with low charisma
            if dice(worker.get_skill("refinement")*0.1) and worker.charisma >= 150:
                log.append(" Her impeccable manners also made a very good impression." %worker.name)
                log.logloc("reputation", choice([0, 0, 1]))
            # then we check for skill level
            log.append("\n")
            if skill >= 4000:
                if client.gender == "male":
                    log.append("The client was at the girls mercy. She brought him to the heavens and left there, unconscious due to sensory overload.")
                else:
                    log.append("The client was at the girls mercy. She brought her to the heavens and left there, unconscious due to sensory overload.")
                log.logws("exp", randint(250, 500))
                log.logloc("reputation", choice([0, 1]))
                log.logws("joy", 3)
            elif skill >= 2000:
                if client.gender == "male":
                    log.append("She playfully took the customer into embrace and made him forget about the rest of the world until they were finished.")
                else:
                    log.append("She playfully took the customer into embrace and made her forget about the rest of the world until they were finished.")
                log.logws("exp", randint(100, 200))
                log.logloc("reputation", choice([0, 0, 1]))
                log.logws("joy", 2)
            elif skill >= 1000:
                log.append("She performed wonderfully with her unmatched carnal skill, making the customer exhausted and completely satisfied.")
                log.logws("exp", randint(50, 120))
                log.logws("joy", 2)
            elif skill >= 500:
                log.append("Her well honed sexual tricks and techniques were very pleasing to the customer, and she was quite pleased in return by client's praises.")
                log.logws("exp", randint(40, 75))
                log.logws("joy", 1)
            elif skill >= 200:
                log.append("$s did the job to the best of her ability but her skills could definitely be improved." %worker.name)
                log.logws("exp", randint(35, 45))
            elif skill >= 50:
                log.append("The girl barely knew what she was doing. Still, %s somewhat managed to provide basic service, following impatient instructions of the client." %worker.name)
                log.logws("exp", randint(20, 35))
            else:
                log.logws("exp", randint(15, 25))
                if worker.charisma >= 200:
                    log.append("A cold turkey sandwich would have made a better sex partner than %s. Her performance was however somewhat saved by her looks." %worker.name)
                else:
                    log.append("Unfortunately, %s barely knew what she was doing. Her looks were not likely to be of any help to her either." %worker.name)
            if skill < 500: # with low skill wrong orientation will take some vitality
                if ("Lesbian" in worker.traits) and (client.gender == "male"):
                    log.append(" It was a bit difficult for %s to do it with a man due to her sexual orientation..." %worker.name)
                    log.logws("vitality", randint(-25, -5))
                elif (client.gender == "female") and not("Lesbian" in worker.traits) and not("Bisexual" in worker.traits):
                    log.append(" It was a bit difficult for %s to do it with a woman due to her sexual orientation..." %worker.name)
                    log.logws("vitality", randint(-25, -5))
            log.append("\n")
