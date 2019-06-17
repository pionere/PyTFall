init -5 python:
    class WhoreJob(Job):
        id = "Whore"
        desc = "Oldest profession known to men, exchanging sex services for money"
        type = "SIW"

        per_client_payout = 30

        aeq_purpose = "Sex"

        base_skills = {"sex": 60, "vaginal": 40, "anal": 40, "oral": 40}
        base_stats = {"charisma": 100}

        traits = {"Ill-mannered", "Always Hungry", "Heavy Drinker", "Neat", "Messy",
                  "Indifferent", "Open Minded", "Dawdler", "Energetic", "Lactation",
                  "Frigid", "Nymphomaniac", "Psychic", "Flexible", "Sexy Air", "Homebody"}

        @staticmethod
        def want_work(worker):
            return any(t.id == "Prostitute" for t in worker.basetraits)

        @staticmethod
        def willing_work(worker):
            return any("SIW" in t.occupations for t in worker.basetraits)

        @staticmethod
        def traits_and_effects_effectiveness_mod(worker, log):
            """Affects worker's effectiveness during one turn. Should be added to effectiveness calculated by the function below.
               Calculates only once per turn, in the very beginning.
            """
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
                log.append("%s suffers from Food Poisoning and doesn't feel like whoring." % name)
                effectiveness -= 50
            elif 'Down with Cold' in effects:
                log.append("%s is not feeling well (down with cold)..." % name)
                effectiveness -= 15
            elif 'Horny' in effects:
                log.append("%s is horny. It's perfect mindset for %s job!" % (name, worker.pd))
                effectiveness += 20
            elif 'Revealing Clothes' in effects:
                log.append("%s revealing clothes appeal to customers and make them really horny." % worker.pdC)
                effectiveness += 15

            if locked_dice(65): # traits don't always work, even with high amount of traits there are normal days when performance is not affected
                traits = WhoreJob.traits
                traits = list(i for i in worker.traits if i.id in traits)

                if not traits:
                    return effectiveness
                trait = choice(traits)
                trait = trait.id

                if trait == "Always Hungry":
                    if locked_dice(50):
                        log.append("Sperm is a good source of protein, and today %s intends to get all protein available!" % name)
                        effectiveness += 25
                    else:
                        log.append("Hungry %s eats %s snacks all the day, making customers feel like they are less important for %s than food... Which may be true." % (name, worker.pd, worker.pd))
                        effectiveness -= 25
                        log.logloc("dirt", 1)
                elif trait == "Heavy Drinker":
                    if locked_dice(50):
                        log.append("Unfortunately %s drank too much yesterday, and now suffers from a hangover." % name)
                        effectiveness -= 20
                    else:
                        log.append("Slightly drunk %s sexually assaults customers all the day, they don't complain." % name)
                        effectiveness += 20
                elif trait == "Nymphomaniac":
                    log.append("%s is always glad to engage in sex, and this job is just perfect for %s." % (name, worker.op))
                    effectiveness += 40
                elif trait == "Psychic":
                    log.append("Knowing what %s partners really want is a trivial matter for a psychic like %s, making %s customers happier." % (worker.pd, name, worker.pd))
                    effectiveness += 35
                elif trait == "Lactation":
                    log.append("%s is lactating! Sometimes customers crave whitish liquids as much as working girls." % name)
                    effectiveness += 25
                elif trait == "Open Minded":
                    log.append("%s has no problems trying different things sexually, making a perfect partner for customers with unusual tastes." % name)
                    effectiveness += 25
                elif trait == "Dawdler":
                    log.append("%s's slow movements find favor among oversensitive customers who'd came too soon otherwise." % name)
                    effectiveness += 20
                elif trait == "Messy":
                    log.append("Today %s wants it really sloppy and messy, attracting customers with similar tastes." % name)
                    log.logloc("dirt", randint(1, 2))
                    effectiveness += 20
                elif trait == "Ill-mannered":
                    log.append("%s is pretty rude today, but fortunately in bed %s bad manners makes customers harder." % (name, worker.pd))
                    effectiveness += 15
                elif trait == "Homebody":
                    log.append("%s really enjoys %s job, having warm food and soft bed nearby all the time. Nice to see someone dedicated to their work." % (name, worker.pd))
                    effectiveness += 15
                elif trait == "Sexy Air":
                    log.append("%s's sexiness gives customers more fuel, resulting in better satisfaction." % name)
                    effectiveness += 15
                elif trait == "Indifferent":
                    log.append("Somehow %s doesn't care much about being fucked today, and most customers don't appreciate it." % name)
                    effectiveness -= 15
                elif trait == "Neat":
                    log.append("Unfortunately %s is too focused on keeping %s freshly laundered clothes clean instead of satisfying %s partners..." % (name, worker.pd, worker.pd))
                    effectiveness -= 20
                elif trait == "Energetic":
                    log.append("%s's moves too fast for %s own good today, rushing too much to the displeasure of %s partners." % (name, worker.pd, worker.pd))
                    effectiveness -= 20
                elif trait == "Frigid":
                    log.append("For %s sex is just a boring job, and many customers don't appreciate it." % name)
                    effectiveness -= 40
            return effectiveness

        @staticmethod
        def calculate_disposition_level(worker, sub):
            """calculating the needed level of disposition;
            since it's whoring we talking about, values are really close to max,
            or even higher than max in some cases, making it impossible.
            """
            disposition = 800 + 50 * sub

            traits = worker.traits
            if "Shy" in traits:
                disposition += 100
            if "Open Minded" in traits: # really powerful trait
                disposition = disposition // 2
            if WhoreJob.willing_work(worker, "SIW") or "Nymphomaniac" in traits:
                disposition -= 200
            elif "Frigid" in traits:
                disposition += 200
            if "Natural Follower" in traits:
                disposition -= 50
            elif "Natural Leader" in traits:
                disposition += 50

            # Virgin trait makes whoring problematic, unless Chastity effect is
            # active which should protect Virgin trait all the time no matter what
            virgin = "Virgin" in traits
            if check_lovers(worker):
                if virgin:
                    if "Dedicated" in traits:
                        disposition += 2000 # not a typo; they never agree, even with Chastity effect
                        return disposition
                    if "Chastity" not in worker.effects:
                        disposition += 300
                else:
                    disposition -= 100
            elif check_friends(worker):
                if virgin:
                    if worker.get_stat("disposition") >= 900 and "Chastity" not in worker.effects:
                        disposition += 100
                else:
                    disposition -= 50
            elif virgin and "Chastity" not in worker.effects:
                disposition += 50
            return disposition

        @staticmethod
        def settle_workers_disposition(worker, log):
            # handles penalties in case of wrong job
            name = set_font_color(choice([worker.fullname, worker.name, worker.nickname]), "pink")
            if WhoreJob.want_work(worker):
                log.append(choice(["%s is doing %s shift as a harlot." % (name, worker.p),
                                   "%s gets busy with clients." % name,
                                   "%s serves customers as a whore." % name]))
            else:
                sub = check_submissivity(worker)
                if worker.status != 'slave':
                    if sub < 0:
                        log.append("%s is not very happy with %s current job as a harlot, but %s'll get the job done." % (name, worker.pd, worker.p))
                        sub = 15
                    elif sub == 0:
                        log.append("%s serves customers as a whore, but %s would prefer to do something else." % (name, worker.p))
                        sub = 25
                    else:
                        log.append("%s makes it clear that %s wants another job before getting busy with clients." % (name, worker.p))
                        sub = 35
                    if dice(sub):
                        worker.logws('character', 1)
                    worker.logws("joy", -randint(3, 6))
                    worker.logws("disposition", -randint(10, 15))
                    worker.logws('vitality', -randint(2, 8)) # a small vitality penalty for wrong job
                else:
                    dispo = worker.get_stat("disposition")
                    dispo_req = WhoreJob.calculate_disposition_level(worker, sub)
                    if sub < 0:
                        if dispo < dispo_req:
                            log.append("%s is a slave so no one really cares, but being forced to work as a whore, %s's quite upset." % (name, worker.p))
                        else:
                            log.append("%s will do as %s is told, but doesn't mean that %s'll be happy about doing 'it' with strangers." % (name, worker.p, worker.p))
                        sub = 25
                    elif sub == 0:
                        if dispo < dispo_req:
                            log.append("%s will do as you command, but %s will hate every second of %s working as a harlot..." % (name, worker.p, worker.pd))
                        else:
                            log.append("%s was very displeased by %s order to work as a whore, but didn't dare to refuse." % (name, worker.pd))
                        sub = 35
                    else:
                        if dispo < dispo_req:
                            log.append("%s was very displeased by %s order to work as a whore, and makes it clear for everyone before getting busy with clients." % (name, worker.pd))
                        else:
                            log.append("%s will do as you command and work as a harlot, but not without a lot of grumbling and complaining." % name)
                        sub = 45
                    if dice(sub):
                        worker.logws('character', 1)
                    if dispo < dispo_req:
                        worker.logws("joy", -randint(8, 15))
                        worker.logws("disposition", -randint(25, 50))
                        worker.logws('vitality', -randint(10, 15))
                    else:
                        worker.logws("joy", -randint(2, 4))
                        worker.logws('vitality', -randint(2, 6))

        @staticmethod
        def log_work(worker, client, ap_used, effectiveness, log):
            # Pass the flags from occupation_checks:
            # log.append(worker.flag("jobs_whoreintro"))
            log.append("\n")

            always_exclude = ["sexwithmc", "angry", "in pain", "dungeon", "sad", "rape", "restrained"]

            clientname = set_font_color(client.name, "beige")
            nickname = set_font_color(choice([worker.fullname, worker.name, worker.nickname]), "pink")

            sexmod = vaginalmod = analmod = oralmod = 0

            # determine act
            if client.gender == 'male':
                act = choice(["sex", "anal", "blowjob"])
            else: #if client.gender == 'female':
                act = "lesbian"

            # Acts, Images, Tags and things Related:
            # Straight Sex Act
            if act == 'sex':
                kwargs = dict(exclude=["gay"]+always_exclude, type="reduce", add_mood=False)
                log.append(choice(["%s hired %s for some good old straight sex. " % (clientname, worker.op),
                                   "%s is willing to pay for %s." % (clientname, "her pussy" if worker.gender == "female" else "his dick")]))
                if "Lesbian" in worker.traits: # lesbians will have only a part of skill level compared to others during normal sex
                    effectiveness -= 25
                    vaginalmod = 20
                    sexmod = 8
                else:
                    vaginalmod = 25
                    sexmod = 10
                # Temporarily done here, should be moved to game init and after_load to improve performance
                # probably not everything though, since now we don't form huge lists of pictures for some acts, using get_image_tags to figure out poses
                if worker.has_image("2c vaginal", **kwargs):
                    image_tags = worker.show("2c vaginal", **kwargs)
                else:
                    kwargs["exclude"] = always_exclude
                    image_tags = worker.show("after sex", **kwargs)

                log.img = image_tags
                image_tags = tagdb.get_image_tags(image_tags)
                if "ontop" in image_tags:
                    log.append("He invited her to 'sit' on his lap as he unsheathed his cock. They've continued along the same lines in 'girl-on-top' position. \n")
                elif "doggy" in image_tags:
                    log.append("He ordered %s to bend over and took her from behind. \n" % nickname)
                elif "missionary" in image_tags:
                    log.append("He pushed %s on her back, shoved his cock in, screaming: 'Oh, Your pussy is wrapping around me so tight!' \n" % nickname)
                elif "onside" in image_tags:
                    log.append("%s lay on her side inviting the customer to fuck her. He was more than happy to oblige.\n" % nickname)
                elif "standing" in image_tags:
                    log.append("Not even bothering getting into a position, he took her standing up. \n")
                elif "spooning" in image_tags:
                    log.append("Customer felt cuddly so he spooned the girl until they both cummed. \n")
                else:
                    log.append(choice(['He wanted some old-fashioned straight fucking. \n',
                                       'He was in the mood for some pussy pounding. \n',
                                       'He asked for some playtime with her vagina.\n']))
                # Virgin trait check:
                WhoreJob.take_virginity(worker, log)
            # Anal Sex Act
            elif act == 'anal':
                kwargs = dict(exclude=["gay"]+always_exclude, type="reduce", add_mood=False)
                log.append(choice(["%s hired her for some anal fun. ", "%s is willing to pay her for backdoor action. "]) % clientname)
                if "Lesbian" in worker.traits:
                    effectiveness -= 25
                    analmod = 20
                    sexmod = 8
                else:
                    analmod = 25
                    sexmod = 10
                log.append(choice(["Anal sex is the best, customer thought... ",
                                   "I am in the mood for a good anal fuck, customer said. ",
                                   "Customer's dick got harder and harder just from the thought of %s's asshole! " % nickname]))

                if worker.has_image("2c anal", **kwargs):
                    image_tags = worker.show("2c anal", **kwargs)
                else:
                    kwargs["exclude"] = always_exclude
                    image_tags = worker.show("after sex", **kwargs)

                log.img = image_tags
                image_tags = tagdb.get_image_tags(image_tags)
                if "ontop" in image_tags:
                    log.append("He invited her to 'sit' on his lap as he unsheathed his cock. They've continued along the same lines in 'girl on top' position. \n")
                elif "doggy" in image_tags:
                    log.append("He ordered %s to bend over and took her from behind. \n" % nickname)
                elif "missionary" in image_tags:
                    log.append("He pushed %s on her back, shoved his cock in, screaming: 'Oh, Your anus is wrapping around me so tight!' \n" % nickname)
                elif "onside" in image_tags:
                    log.append("%s lays on her side inviting the customer to fuck her. He was more than happy to oblige.\n" % nickname)
                elif "standing" in image_tags:
                    log.append("Not even bothering getting into a position, he took her standing up. \n")
                elif "spooning" in image_tags:
                    log.append("Customer felt cuddly so he spooned the girl until they both cummed. \n")
                else:
                    log.append(choice(['He took her in the ass right there and then. \n',
                                       'He got his dose of it. \n',
                                       'And so he took her in her butt. \n']))
            # Various job acts
            elif act == 'blowjob':
                kwargs = dict(exclude=always_exclude, type="reduce", add_mood=False)
                log.append(choice(["%s hired %s for some side job on his thing. ", "%s is paying %s today for naughty service. "]) % (clientname, worker.op))
                # here we will have to choose skills depending on selected act
                tags = ({"tags": ["bc deepthroat"], "exclude": always_exclude},
                        {"tags": ["bc handjob"], "exclude": always_exclude},
                        {"tags": ["bc footjob"], "exclude": always_exclude},
                        {"tags": ["bc titsjob"], "exclude": always_exclude},
                        {"tags": ["bc blowjob"], "exclude": always_exclude},
                        {"tags": ["after sex"], "exclude": always_exclude, "dice": 20})
                act = WhoreJob.get_act_idx(worker, tags)
                if act == 0:
                    log.append(choice(["He shoved his cock all the way into her throat! \n",
                                       "Deepthroat is definitely my style, thought the customer... \n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness -= 25
                        oralmod = 20
                        sexmod = 8
                    else:
                        oralmod = 25
                        sexmod = 10
                    log.img = worker.show("bc deepthroat", **kwargs)
                elif act == 1:
                    log.append("He told %s to give him a good handjob.\n"%nickname)
                    if "Lesbian" in worker.traits:
                        effectiveness -= 25
                        oralmod = 20
                        sexmod = 8
                    else:
                        oralmod = 25
                        sexmod = 10
                    log.img = worker.show("bc handjob", **kwargs)
                elif act == 2:
                    log.append(choice(["He asked her for a footjob.\n",
                                       "Footjob might be a weird fetish but that's what the customer wanted...\n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness -= 25
                        oralmod = 20
                        sexmod = 8
                    else:
                        skill = round(worker.get_skill("oral")*.25 + worker.get_skill("sex")*.75)
                        oralmod = 25
                        sexmod = 10
                    log.img = worker.show("bc footjob", **kwargs)
                elif act == 3:
                    if "Lesbian" in worker.traits:
                        effectiveness -= 25
                        sexmod = 20
                        oralmod = 8
                    else:
                        sexmod = 25
                        oralmod = 10
                    if "Big Boobs" in worker.traits or "Abnormally Large Boobs" in worker.traits:
                        log.append(choice(["He went straight for her big boobs. \n",
                                           "Seeing her knockers, customer wanted nothing else then to park his dick between them. \n",
                                           "Lustfully gazing on your girl's breasts, he asked for a titsjob. \n",
                                           "He put his manhood between her big tits. \n" ,
                                           "He showed his cock between %s's enormous breasts. \n"%nickname]))
                    elif "Small Boobs" in worker.traits:
                        if dice(15):
                            log.append("With a smirk on his face, customer asked for a titsjob. He was having fun from her vain efforts. \n")
                        else:
                            log.append(choice(["He placed his cock between her breasts, clearly enjoining her flat chest. \n",
                                               "Even knowing that her breasts are small, he wanted to be caressed by them. \n"]))
                    else:
                        log.append(choice(["He asked for a titsjob. \n",
                                           "He let %s to caress him with her breasts. \n" % nickname,
                                           "He showed his cock between %s's tits. \n" % nickname]))
                    log.img = worker.show("bc titsjob", **kwargs)
                elif act == 4:
                    log.append(choice(['Client was in mood for some oral sex. \n',
                                       'Client was in the mood for a blowjob. \n',
                                       'He asked her to lick his dick. \n']))
                    if "Lesbian" in worker.traits:
                        effectiveness -= 25
                        sexmod = 20
                        oralmod = 8
                    else:
                        sexmod = 25
                        oralmod = 10
                    log.img = worker.show("bc blowjob", **kwargs)
                elif act == 5:
                    if "Lesbian" in worker.traits:
                        effectiveness -= 25
                        sexmod = 20
                    else:
                        sexmod = 25
                        oralmod = 5
                    log.append(choice(["Customer wanted nothing else then to jerk himself in from of her and ejaculate on her face. \n",
                                       "He wanked himself hard in effort to cover her with his cum. \n"]))
                    log.img = worker.show("after sex", **kwargs)
                else: # could not find a matching image
                    log.append(choice(['Client was in mood for some oral sex. \n',
                                       'Client was in the mood for a blowjob. \n',
                                       'He asked her to lick his dick. \n']))
                    if "Lesbian" in worker.traits:
                        effectiveness -= 25
                        sexmod = 20
                        oralmod = 8
                    else:
                        sexmod = 25
                        oralmod = 10
                    log.img = worker.show("bc blowjob", **kwargs)
            # Lesbian Act
            elif act == 'lesbian':
                log.append("%s hired her for some hot girl on girl action. " % clientname)
                skill = worker.get_skill("vaginal")
                kwargs = dict(exclude=always_exclude, type="reduce", add_mood=False)

                tags = ({"tags": ["gay", "2c lickpussy"], "exclude": always_exclude},
                        {"tags": ["gay", "bc lickpussy"], "exclude": always_exclude},
                        {"tags": ["gay", "2c lickanus"], "exclude": always_exclude},
                        {"tags": ["gay", "bc lickanus"], "exclude": always_exclude},
                        {"tags": ["gay", "2c vaginalfingering"], "exclude": always_exclude},
                        {"tags": ["gay", "bc vaginalhandjob"], "exclude": always_exclude},
                        {"tags": ["gay", "2c analfingering"], "exclude": always_exclude},
                        {"tags": ["gay", "bc analhandjob"], "exclude": always_exclude},
                        {"tags": ["gay", "2c caresstits"], "exclude": always_exclude},
                        {"tags": ["gay", "bc caresstits"], "exclude": always_exclude},
                        {"tags": ["gay", "bc hug", "2c hug"], "exclude": always_exclude},
                        {"tags": ["gay", "2c vaginal"], "exclude": always_exclude},
                        {"tags": ["gay", "bc vaginal"], "exclude": always_exclude},
                        {"tags": ["gay", "2c anal"], "exclude": always_exclude},
                        {"tags": ["gay", "bc anal"], "exclude": always_exclude},
                        {"tags": ["gay", "2c vaginaltoy"], "exclude": always_exclude},
                        {"tags": ["gay", "bc toypussy"], "exclude": always_exclude},
                        {"tags": ["gay", "2c analtoy"], "exclude": always_exclude},
                        {"tags": ["gay", "bc toyanal"], "exclude": always_exclude},
                        {"tags": ["gay", "scissors"], "exclude": always_exclude})
                act = WhoreJob.get_act_idx(worker, tags)

                # We'll be adding "les" here as Many lesbian pics do not fall in any of the categories and will never be called...
                if act == 0:
                    log.append(choice(["Clearly in the mood for some cunt, she licked %ss pussy clean.\n" % nickname,
                                       "Hungry for a cunt, she told %s to be still and started licking her soft pussy with her hot tongue. \n" % nickname]))
                    if "Lesbian" in worker.traits: # bisexuals will have normal value during lesbian action, lesbians will get +15 effectiveness, and straight ones -25
                        effectiveness += 15
                        sexmod = 25
                        oralmod = 10
                        vaginalmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        oralmod = 9
                        vaginalmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        oralmod = 8
                        vaginalmod = 8
                    log.img = worker.show("gay", "2c lickpussy", **kwargs)
                elif act == 1:
                    log.append(choice(["All hot and bothered, she ordered %s to lick her cunt. \n" % nickname,
                                       "As if she had an itch, she quickly told %s to tongue her pussy. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 10
                        oralmod = 25
                        vaginalmod = 10
                    elif "Bisexual" in worker.traits:
                        skill = round(worker.get_skill("oral")*.7 + worker.get_skill("vaginal")*.15 + worker.get_skill("sex")*.15)
                        sexmod = 9
                        oralmod = 22
                        vaginalmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 8
                        oralmod = 20
                        vaginalmod = 8
                    log.img = worker.show("gay", "bc lickpussy", **kwargs)
                elif act == 2:
                    log.append(choice(["She licked %ss anus clean.\n" % nickname,
                                       "She told %s to be still and started licking her asshole with her hot tongue. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        oralmod = 10
                        analmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        oralmod = 9
                        analmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        oralmod = 8
                        analmod = 8
                    log.img = worker.show("gay", "2c lickanus", **kwargs)
                elif act == 3:
                    log.append(choice(["All hot and bothered, she ordered %s to lick her asshole. \n" % nickname,
                                       "As if she had an itch, she quickly told %s to tongue her anus. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 10
                        oralmod = 25
                        analmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 8
                        oralmod = 22
                        analmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 8
                        oralmod = 20
                        analmod = 8
                    log.img = worker.show("gay", "bc lickanus", **kwargs)
                elif act == 4:
                    log.append(choice(["In mood for a hot lesbo action, she stuck her fingers in your girls pussy. \n",
                                       "She watched %s moan as she stuck fingers in her pussy. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        vaginalmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        vaginalmod = 9
                    else:
                        effectiveness -= 25 # TODO Check if it is ok to mess with effectiveness this far into the calculations...
                        sexmod = 20
                        vaginalmod = 8
                    log.img = worker.show("gay", "2c vaginalfingering", **kwargs)
                elif act == 5:
                    log.append(choice(["Quite horny, she ordered your girl to finger her cunt. \n",
                                       "Clearly in the mood, she told %s to finger her until she cums. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        vaginalmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        vaginalmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        vaginalmod = 8
                    log.img = worker.show("gay", "bc vaginalhandjob", **kwargs)
                elif act == 6:
                    log.append(choice(["In mood for a hot lesbo action, she stuck her fingers in your girls anus. \n",
                                       "She watched %s moan as she stuck fingers in her asshole. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        analmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        analmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        analmod = 8
                    log.img = worker.show("gay", "2c analfingering", **kwargs)
                elif act == 7:
                    log.append(choice(["Quite horny, she ordered your girl to finger her anus. \n",
                                       "Clearly in the mood, she told %s to finger her asshole until she cums. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        analmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        analmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        analmod = 8
                    log.img = worker.show("gay", "bc analhandjob", **kwargs)
                elif act == 8:
                    log.append(choice(["Liking your girls breasts, she had some good time caressing them. \n",
                                       "She enjoyed herself by caressing your girls breasts. \n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                    else:
                        effectiveness -= 25
                        sexmod = 20
                    log.img = worker.show("gay", "2c caresstits", **kwargs)
                elif act == 9:
                    log.append(choice(["She asked your girl to caress her tits. \n",
                                       "She told your girl to put a squeeze on her breasts. \n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                    else:
                        effectiveness -= 25
                        sexmod = 20
                    log.img = worker.show("gay", "bc caresstits", **kwargs)
                elif act == 10:
                    log.append(choice(["Girls lost themselves in each others embrace.\n",
                                       "Any good lesbo action should start with a hug, don't you think??? \n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                    else:
                        effectiveness -= 25
                        sexmod = 20
                    log.img = worker.show("gay", "bc hug", "2c hug", **kwargs)
                elif act == 11:
                    log.append(choice(["She put on a strapon and fucked your girl in her cunt. \n",
                                       "Equipping herself with a strap-on, she lustfully shoved it in %ss pussy. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        vaginalmod = 25
                        sexmod = 10
                    elif "Bisexual" in worker.traits:
                        vaginalmod = 22
                        sexmod = 9
                    else:
                        effectiveness -= 25
                        vaginalmod = 20
                        sexmod = 8
                    log.img = worker.show("gay", "2c vaginal", **kwargs)
                    WhoreJob.take_virginity(worker, log)
                elif act == 12:
                    log.append(choice(["She ordered %s to put on a strapon and fuck her silly with it. \n" % nickname,
                                       "She equipped %s with a strapon and told her that she was 'up' for a good fuck! \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        vaginalmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        vaginalmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        vaginalmod = 8
                    log.img = worker.show("gay", "bc vaginal", **kwargs)
                elif act == 13:
                    log.append(choice(["She put on a strapon and fucked your girl in her butt. \n",
                                       "Equipping herself with a strapon, she lustfully shoved it in %s's asshole. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        analmod = 25
                        sexmod = 10
                    elif "Bisexual" in worker.traits:
                        analmod = 22
                        sexmod = 9
                    else:
                        effectiveness -= 25
                        analmod = 20
                        sexmod = 8
                    log.img = worker.show("gay", "2c anal", **kwargs)
                elif act == 14:
                    log.append(choice(["She ordered %s to put on a strapon and butt-fuck her silly with it. \n" % nickname,
                                       "She equipped %s with a strapon and told her that she was 'up' for a good anal fuck! \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        analmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        analmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        analmod = 8
                    log.img = worker.show("gay", "bc anal", **kwargs)
                elif act == 15:
                    log.append(choice(["She played with a toy and %ss pussy. \n" % nickname,
                                       "She stuck a toy up %s cunt. \n" % nickname]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        vaginalmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        vaginalmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        vaginalmod = 8
                    log.img = worker.show("gay", "2c vaginaltoy", **kwargs)
                    WhoreJob.take_virginity(worker, log)
                elif act == 16:
                    log.append(choice(["Without further ado, %s fucked her with a toy. \n" % nickname,
                                       "She asked your girl to fuck her pussy with a toy. \n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        vaginalmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        vaginalmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        vaginalmod = 8
                    log.img = worker.show("gay", "bc toypussy", **kwargs)
                elif act == 17:
                    log.append(choice(["After some foreplay, she stuck a toy up your girls butt. \n",
                                       "For her money, she had some fun playing with a toy and your girls asshole. \n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        analmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        analmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        analmod = 8
                    log.img = worker.show("gay", "2c analtoy", **kwargs)
                elif act == 18:
                    log.append(choice(["After some foreplay, she asked %s to shove a toy up her ass. \n" % nickname,
                                       "This female customer of your brothel clearly believed that there is no greater pleasure than a toy up her butt. \n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        analmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        analmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        analmod = 8
                    log.img = worker.show("gay", "bc toyanal", **kwargs)
                elif act == 19:
                    log.append(choice(["She was hoping to get some clit to clit action, and she got it. \n",
                                       "The female customer asked for a session of hot, sweaty tribadism. \n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                        analmod = 10
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                        analmod = 9
                    else:
                        effectiveness -= 25
                        sexmod = 20
                        analmod = 8
                    log.img = worker.show("gay", "scissors", **kwargs)
                else:
                    log.append(choice(["She was in the mood for some girl on girl action. \n",
                                       "She asked for a good lesbian sex. \n"]))
                    if "Lesbian" in worker.traits:
                        effectiveness += 15
                        sexmod = 25
                    elif "Bisexual" in worker.traits:
                        sexmod = 22
                    else:
                        effectiveness -= 25
                        sexmod = 20
                    log.img = worker.show("gay", **kwargs)
                    # Last fallback!
            else:
                log.append("Whore Job\n\nMissed All acts!\n\n")
                log.img = worker.show("sex", **kwargs)

            tier = log.loc.tier
            # Charisma mods:
            charisma = WhoreJob.normalize_required_stat(worker, "charisma", effectiveness, tier)
            if charisma >= 170:
                log.append("Her supernal loveliness made the customer to shed tears of happiness, comparing %s to ancient goddess of love. Be wary of possible cults dedicated to her..." % nickname)
                log.logws("joy", 1)
                if dice(75):
                    log.logloc("fame", 1)
                if dice(50):
                    log.logloc("reputation", 1)
            elif charisma >= 160:
                log.append("%s made the customer fall in love with her unearthly beauty. Careful now girl, we don't need crowds of admires around our businesses..." % nickname)
                log.logws("joy", 1)
                if dice(50):
                    log.logloc("fame", 1)
                if dice(30): 
                    log.logloc("reputation", 1)
            elif charisma >= 145:
                log.append("%s completely enchanted the customer with her stunning beauty." % nickname)
                if dice(30):
                    log.logloc("fame", 1)
                if dice(25):
                    log.logloc("reputation", 1)
            elif charisma >= 120:
                log.append("The client was happy to be alone with such a breathtakingly beautiful girl as %s." % nickname)
                if dice(25):
                    log.logloc("fame", 1)
            elif charisma >= 100:
                log.append("%s good looks clearly was pleasing to the customer." % nickname)
            elif charisma >= 50:
                log.append("%s did her best to make the customer like her, but her beauty could definitely be enhanced." % nickname)
            else:
                log.logws("joy", -2)
                if dice(50):
                    log.logloc("fame", -1)
                log.append("The customer was unimpressed by %s looks, to say at least. Still, %s preferred fucking her over a harpy. Hearing that from %s however, was not encouraging for the poor girl at all..." % (nickname, client.p, client.op))

            refinement = WhoreJob.normalize_required_skill(worker, "refinement", effectiveness, tier)
            if charisma >= 100 and refinement >= 100 and dice(75):
                log.append("Her impeccable manners also made a very good impression.")
                log.logloc("reputation", 1)

            # Award EXP:
            if effectiveness < 90:
                ap_used *= .5
            log.logws("exp", exp_reward(worker, tier, exp_mod=ap_used))

            if effectiveness >= 190:
                log.append("The client was at the girls mercy. She brought him to the heavens and %s remained there, unconscious from sensory overload." % client.p)
                if dice(50):
                    log.logloc("reputation", 1)
                log.logws("joy", 3)
            elif effectiveness >= 150:
                log.append("She playfully took the customer into embrace and made him forget about the rest of the world until they were finished." % client.op)
                if dice(30):
                    log.logloc("reputation", 1)
                log.logws("joy", 2)
            elif effectiveness >= 130:
                log.append("She performed wonderfully with her unmatched carnal skills, making the customer exhausted and completely satisfied.")
                log.logws("joy", 2)
            elif effectiveness >= 100:
                log.append("Her well honed sexual tricks and techniques were very pleasing to the customer, and she was quite pleased in return by client's praises.")
                log.logws("joy", 1)
            elif effectiveness >= 65:
                log.append("%s did the job to the best of her ability, making a good impression, but her skills could definitely be improved." % nickname)
            elif effectiveness >= 35:
                log.append("The girl performed quite poorly. Still, %s somewhat managed to provide required service, following impatient instructions of the client." % nickname)
            else:
                if charisma >= 100:
                    log.append("Even though %s failed to satisfy the client, her performance was however somewhat saved by her looks." % nickname)
                else:
                    log.append("Unfortunately, %s failed to satisfy the client. Her looks were not likely to be of any help to her either." % nickname)
            if effectiveness < 100 and "Open Minded" not in worker.traits and "Bisexual" not in worker.traits:
                # with low effectiveness wrong orientation will take some vitality
                if ("Lesbian" in worker.traits or "Gay" in worker.traits) != (client.gender == worker.gender):
                    log.append(" It was a bit difficult for %s to do it with %s due to %s sexual orientation..." % (nickname, clientname, worker.pd))
                    log.logws("vitality", -randint(1, 5))

            log.append("")

            # Take care of stats mods
            worker.logws("vitality", -randint(2, 5))
            if dice(12):
                worker.logws("constitution", 1)
                learned = True
            if dice(sexmod):
                worker.logws("sex", 1)
                learned = True
            if dice(vaginalmod):
                worker.logws("vaginal", 1)
                learned = True
            if dice(analmod):
                worker.logws("anal", 1)
                learned = True
            if dice(oralmod):
                worker.logws("oral", 1)
                learned = True
            if 'learned' in locals():
                log.append("%s feels like %s learned something!\n" % (nickname, worker.p))
                worker.logws("joy", 1)

            return effectiveness

        @staticmethod
        def get_act_idx(worker, tags):
            acts = list()
            for idx, t in enumerate(tags):
                if isinstance(t, tuple):
                    if worker.has_image(*t):
                        acts.append((idx, 100))
                elif isinstance(t, dict):
                    if worker.has_image(*t.get("tags", []), exclude=t.get("exclude", [])):
                        acts.append((idx, t.get("dice", 100)))

            if acts:
                act = weighted_sample(acts)
            else:
                act = None

            return act

        @staticmethod
        def take_virginity(worker, log):
            # let's just assume (for now) that dildos are too small to take virginity, otherwise it becomes too complicated in terms of girls control :)
            if "Virgin" in worker.traits and "Chastity" not in worker.effects:
                tips = 100 + worker.get_stat("charisma") * 3
                log.append("\n{color=pink}%s lost her virginity!{/color} Customer thought that was super hot and left a tip of {color=gold}%d Gold{/color} for the girl.\n\n" % (worker.nickname, tips))
                worker.remove_trait(traits["Virgin"])
                if tips:
                    worker.up_counter("_jobs_tips", tips)
