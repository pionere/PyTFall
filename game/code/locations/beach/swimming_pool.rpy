label swimming_pool:
    $ iam.enter_location(has_tags=["girlmeets", "swimsuit"], has_no_tags=["beach", "sleeping"],
                        coords=[[.2, .45], [.42, .6], [.7, .5]])
    # Music
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("swimming_pool")
    $ global_flags.del_flag("keep_playing_music")

    scene bg swimming_pool
    with dissolve

    if not global_flags.has_flag('visited_swimming_pool'):
        $ global_flags.set_flag('visited_swimming_pool')
        $ block_say = True
        show expression npcs["Henry_beach"].get_vnsprite() as henry
        $ h = npcs["Henry_beach"].say
        h "Welcome to the swimming pool!"
        h "It's not free, but we don't have sea monsters and big waves here, so it's perfect for a novice swimmer!"
        h "We also provide swimming lessons at a reasonable price. Feel free to ask anytime!"
        $ block_say = False
        hide henry
        $ del h

    show screen swimming_pool
    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:
        $ result = ui.interact()

        if result == "swim":
            hide screen swimming_pool
            show screen swimmong_pool_swim
            with dissolve
        elif result == "leave":
            hide screen swimming_pool
            jump city_beach
        elif result[0] == "pool":
            hide screen swimmong_pool_swim
            $ result = result[1]
            if result == "swim":
                jump single_swim_pool
            elif result == "hire":
                jump instructor_swim_pool
            elif result == "work":
                jump mc_action_work_swim_pool
            else:
                show screen swimming_pool
                with dissolve
        elif result[0] == "jump":
            python hide:
                char = result[1]
                iam.start_int(char, img=iam.select_beach_img_tags(char, "pool"))


screen swimming_pool():
    use top_stripe(True, return_button_action=Return("leave"))

    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Look Around":
            action Function(pytfall.look_around)
        textbutton "Meet Girls":
            action ToggleField(iam, "show_girls")

    if iam.show_girls:
        use interactions_meet
    else:
        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
        imagebutton:
            align (.01, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return("leave")

        $ img = im.Scale("content/gfx/interface/icons/sp_swimming.png", 90, 90)
        imagebutton:
            pos (290, 510)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return("swim")

screen swimmong_pool_swim():
    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Swim (10 G)":
            action Return(["pool", "swim"])
        textbutton "Hire an instructor (50 G)":
            action Return(["pool", "hire"])
        textbutton "Work as instructor":
            action Return(["pool", "work"])
        textbutton "Leave":
            action Return(["pool", "leave"])
            keysym "mousedown_3"

label single_swim_pool:
    if hero.get_stat("vitality") < 40 or not hero.has_ap():
        "You are too tired at the moment."
    elif hero.get_stat("health") < hero.get_max("health")/2:
        "You are too wounded at the moment."
    elif hero.take_money(10, reason="Swimming Pool"):
        play world "underwater.mp3"
        scene bg pool_swim
        with dissolve

        $ hero.take_ap(1)
        $ temp = hero.get_skill("swimming")
        if temp < 20:
            if locked_dice(60):
                "You barely stay afloat. Clearly, more practice is needed."
                $ swim_act = randint(1, 2)
            else:
                "You can barely stay afloat. After a while, you lose your cool and start drowning, but the swimming instructor immediately comes to your aid."
                $ swim_act = 1
                $ hero.gfx_mod_stat("health", -5)
            $ swim_vit = randint(25, 35)
        elif temp < 50:
            "You can swim well enough to not drown in a swimming pool, but more practice is needed."
            $ swim_act = randint(2, 3)
            $ swim_vit = randint(20, 30)
        elif temp < 100:
            "You are somewhat confident about your swimming skills."
            $ swim_act = randint(2, 4)
            $ swim_vit = randint(15, 20)
        else:
            "It feels nice swimming in the pool, but the sea is more suitable to learn something new."
            $ swim_act = randint(0, 1)
            $ swim_vit = randint(10, 15)
        if locked_dice(75) and temp >= 50 and hero.get_stat("constitution") < hero.get_max("constitution"):
            "Swimming did you good."
            $ hero.gfx_mod_stat("constitution", 1)
        $ hero.gfx_mod_skill("swimming", 0, swim_act)
        $ hero.mod_stat("vitality", -swim_vit)
        $ del temp, swim_act, swim_vit

        jump swimming_pool
    else:
        "You don't have enough gold."
    $ global_flags.set_flag("keep_playing_music")
    jump swimming_pool

label instructor_swim_pool:
    if hero.get_stat("vitality") < 40 or not hero.has_ap():
        "You are too tired at the moment."
    elif hero.get_stat("health") < hero.get_max("health")/2:
        "You are too wounded at the moment."
    elif hero.take_money(50, reason="Swimming Pool"):
        play world "underwater.mp3"
        scene bg pool_swim
        with dissolve

        $ hero.take_ap(1)
        $ temp = hero.get_skill("swimming")
        if temp < 20:
            "The instructor teaches you water safety to prevent mouth-to-mouth accidents once and for all."
            $ swim_act = randint(2, 4)
            $ swim_tra = randint(2, 4)
            $ swim_vit = randint(20, 30)
        elif temp < 50:
            "The instructor shows you the most basic swimming styles."
            $ swim_act = randint(4, 6)
            $ swim_tra = randint(4, 6)
            $ swim_vit = randint(15, 25)
        elif temp < 100:
            "The instructor shows you common swimming styles and the very basics of underwater swimming."
            $ swim_act = randint(4, 8)
            $ swim_tra = randint(4, 8)
            $ swim_vit = randint(10, 15)
        elif temp < 250:
            "The instructor shows you advanced swimming styles, including underwater ones."
            $ swim_act = randint(1, 3)
            $ swim_tra = randint(5, 10)
            $ swim_vit = randint(10, 15)
        else:
            "There is nothing else he can show you now, but his knowledge about behavior on the water is second to none nevertheless."
            $ swim_act = randint(0, 1)
            $ swim_tra = randint(5, 10)
            $ swim_vit = randint(5, 10)
        if locked_dice(65) and temp >= 50:
            "Swimming did you good."
            $ hero.gfx_mod_stat("constitution", 1)
        $ hero.gfx_mod_skill("swimming", 0, swim_act)
        $ hero.gfx_mod_skill("swimming", 1, swim_tra)
        $ hero.mod_stat("vitality", -swim_vit)
        $ del temp, swim_act, swim_tra, swim_vit

        jump swimming_pool
    else:
        "You don't have enough Gold."
    $ global_flags.set_flag("keep_playing_music")
    jump swimming_pool

label mc_action_work_swim_pool: # here we could use an option to meet characters with a certain probability
    if hero.get_skill("swimming") < 100:
        $ h = npcs["Henry_beach"].say
        h "Haha! What? You can't even swim properly!"
        h "Come back if you don't drown in the ocean! HAHAha..."
        $ del h
    elif not global_flags.has_flag("sw_pool_group"):
        show expression npcs["Henry_beach"].get_vnsprite() as henry
        $ h = npcs["Henry_beach"].say
        h "Ok. I see you are capable to teach our kinds."
        extend "Here is how this works."
        h "We provide the place to train your group and a base salary to teach the kids."
        h "Our payment might be low, but I think this is a great opportunity to meet people and make some friends in the city."
        h "You also get additional payment from the members of your group, but that is not our business."
        h "You can have the trainings daily or every other day or even just weekly, but I can tell you from experience that they prefer to come every day."
        extend " And you better not skip a day without a notice! Some might drop out even if you come every day."
        h "I'm not going to tell you how to teach your group, you'll have to learn the ins and outs yourself. Just keep in mind that they are almost human."
        extend " Or at least they pretend."
        h "One thing: We can not allow you to have girls in your group who are working for you. There is an obvious conflict of interest there!"
        h "Good luck!"
        hide henry
        $ global_flags.set_flag("sw_pool_group", object())
        $ del h
        jump mc_action_work_swim_pool
    elif not hero.has_ap():
        "You don't have enough Action Points. Try again tomorrow."
    elif hero.get_stat("vitality") < 40 or hero.get_stat("health") < hero.get_max("health")/2:
        if hero.get_stat("vitality") < 40:
            "You are too tired for work."
        else:
            "You are too wounded at the moment."
        $ temp = global_flags.get_flag("sw_pool_group")
        if getattr(temp, "members", None) and temp.last_training < day:
            menu:
                "Do you want to inform your group?"
                "Yes":
                    $ hero.take_ap(1)
                    $ temp.last_training = day
                "No":
                    $ pass
        $ del temp
    elif getattr(global_flags.flag("sw_pool_group"), "last_training", day-1) >= day:
        "Your group is not here to train."
        menu:
            "Do you want to teach the kids?"
            "Yes":
                $ picture = "content/gfx/images/swim_kids/sk_" + str(randint(1, 4)) + ".webp"
                show expression picture at truecenter with dissolve

                "You teach local kids to swim. The payment is low, but at least you can use the pool for free."

                python hide:
                    # Rewards:
                    result = randint(5, round(hero.get_skill("swimming")*.1))
                    if result > 200:
                        result = randint(190, 220)
                    hero.gfx_mod_skill("swimming", 0, randint(0, 2))
                    hero.gfx_mod_skill("swimming", 1, randint(1, 2))
                    hero.mod_stat("vitality", -randint(10, 20))
                    hero.add_money(result, reason="Job")
                    gfx_overlay.random_find(result, 'work')
                    hero.gfx_mod_exp(exp_reward(hero, hero))

                hide expression picture with dissolve
                $ del picture
            "No":
                $ pass
    else:
        $ picture = "content/gfx/images/swim_kids/sk_" + str(randint(1, 4)) + ".webp"
        show expression picture at truecenter with dissolve

        python:
            # remove AP so the hero can not spend it on interactions
            hero.take_ap(1)
            max_gain = 10
            # handle expiration
            spool_group = global_flags.flag("sw_pool_group")
            if not hasattr(spool_group, "members"):
                spool_group.last_training = None
                spool_group.members = []
            else:
                last_training = spool_group.last_training
                mod = day - last_training
                for trainee in spool_group.members[:]:
                    char, last_session, last_gain, last_incentive, last_perf = trainee 
                    if char not in chars.values() or char.employer is hero or not char.is_available:
                        # char is 'gone'
                        spool_group.members.remove(trainee)
                        continue
                    # Dispo penalty for missed session(s):
                    if mod != 1:
                        iam.dispo_reward(char, -min(10*mod, char.get_stat("disposition")/10))
                    # Check if the char wants to go on with the trainings:
                    if last_session is None:
                        temp = 50
                    else:
                        temp = (day - last_session)*10
                        temp *= 1 + get_linear_value_of(char.get_stat("disposition"), 0, 0, char.get_max("disposition"), -.5)
                        #temp *= 1 + get_linear_value_of(last_gain, 0, .5, max_gain, -.5)
                        temp *= 1 + get_linear_value_of(last_incentive, 0, .5, 2, -.5)
                    if dice(temp*mod):
                        spool_group.members.remove(trainee)
                        continue
                    # Next_day effects
                    temp = trainee[3]
                    if temp > 1:
                        temp = .9
                    elif temp < 1:
                        temp = 1.1
                    trainee[3] *= math.pow(temp, mod)

            # add newcomers TODO filter arena_active?
            candidates = [char for char in chars.values() if char.employer is not hero and char.status == "free" and char.get_skill("swimming") < hero.get_skill("swimming")/2]

            temp = 4 * 100 * hero.get_stat("fame") * max(0, hero.get_stat("reputation"))
            temp /= float(hero.get_max("fame") * hero.get_max("reputation"))

            tmp = 2
            if dice(temp):
                tmp += 1
            elif dice(100-temp):
                tmp -= 1
                if dice(50) and spool_group.last_training is not None:
                    tmp -= 1
            tmp = min(tmp, 9 - len(spool_group.members))
            candidates = random.sample(candidates, min(len(candidates), tmp))
            candidates = [[char, None, 0, 1 + .002 * temp, None] for char in candidates]

            while len(spool_group.members) > 6:
                tmp = spool_group.members.pop()
                candidates.append(tmp) 

        # Build the group:
        #  train/interact/dismiss/send home
        $ backup = []
        call swimming_pool_build_group from _swimming_pool_build_group

        "You teach local kids and your group to swim."

        # train
        python:
            for trainee in spool_group.members:
                char = trainee[0]
                if char.get_stat("health") < char.get_max("health")/2 or char.get_stat("vitality") < 40 or not char.has_ap():
                    # char is not able to swim, but the hero did not send her/him home -> dispo penalty
                    iam.dispo_reward(char, -randint(16, 20))
                    continue

                trainee[1] = day

                # base gain
                temp = max_gain

                # hero's incentive
                temp *= trainee[3]

                # traits
                tmp = char.traits
                if "Artificial Body" in tmp:
                    temp *= 1.5
                if "Athletic" in tmp:
                    temp *= 1.4
                if "Manly" in tmp:
                    temp *= 1.3
                if "Energetic" in tmp:
                    temp *= 1.2
                if "Dawdler" in tmp:
                    temp *= .6
                if "Chubby" in tmp:
                    temp *= .8
                tmp = char.gents
                if tmp.id == "Abnormally Large Boobs":
                    temp *= .6
                elif tmp.id == "Big Boobs":
                    temp *= .8
                elif tmp.id == "Small Boobs":
                    temp *= 1.2
                # effects
                tmp = char.effects
                if "Exhausted" in tmp:
                    temp *= .2
                if "Injured" in tmp:
                    temp *= .1
                if "Food Poisoning" in tmp:
                    temp *= .75
                if "Down with Cold" in tmp:
                    temp *= .3
                if "Horny" in tmp:
                    temp *= .9
                # mood
                temp *= 1 + get_linear_value_of(char.get_stat("joy"), 0, -.3, 100, .3) # 100: max joy...

                # today's performance
                trainee[4] = random.betavariate(2, 1)
                temp *= trainee[4]

                # Rewards:
                tmp = char.get_skill("swimming")
                char.stats.mod_full_skill("swimming", temp)
                trainee[2] = char.get_skill("swimming") - tmp
                char.mod_exp(exp_reward(char, hero))

                iam.dispo_reward(char, randint(8, 12))

                # action cost
                char.take_ap(1)
                char.mod_stat("vitality", -randint(10, 20))

        # evaluate results
        #  punish/ok/praise
        call swimming_pool_eval_group from _swimming_pool_eval_group

        # finish (get paid, stat rewards, cleanup)
        python hide:
            # Rewards:
            result = randint(5, round(hero.get_skill("swimming")*.1))
            if result > 200:
                result = randint(190, 220)
            temp = Team(implicit=[trainee[0] for trainee in spool_group.members])
            for char in temp:
                tmp = .5 + char.get_skill("swimming") / float(char.get_max_skill("swimming"))
                result += int(char.expected_wage * tmp)
            hero.gfx_mod_skill("swimming", 0, randint(0, 2+len(temp)/2))
            hero.gfx_mod_skill("swimming", 1, randint(1, 2+len(temp)/2))
            hero.mod_stat("vitality", -(randint(10, 20) + 2*len(temp)))
            hero.mod_stat("fame", randint(0, sum((char.tier+1) for char in temp)))
            hero.add_money(result, reason="Job")
            gfx_overlay.random_find(result, 'work')
            temp.add(hero)
            hero.gfx_mod_exp(exp_reward(hero, temp))

            # Update the group:
            spool_group.members.extend(backup)

            # Cleanup:
            cleanup = ["char", "temp", "tmp", "mod", "trainee",
                      "max_gain", "backup", "candidates"]
            for i in cleanup:
                if hasattr(store, i):
                    delattr(store, i)

        menu:
            "Next Training?"
            "Tomorrow":
                $ spool_group.last_training = day
            "Day after tomorrow":
                $ spool_group.last_training = day+1
            "In three days":
                $ spool_group.last_training = day+2
            "Next week":
                $ spool_group.last_training = day+6
            "Dismiss the group":
                $ spool_group.last_training = day
                $ spool_group.members = []

        hide expression picture with dissolve
        $ del picture, spool_group

    $ global_flags.set_flag("keep_playing_music")
    jump swimming_pool

label swimming_pool_build_group:
    # just in case we are returning from an interaction
    show expression picture at truecenter with dissolve

    # Group building screen before training:
    show screen swimming_pool_build_group
    with dissolve

    while 1:
        $ result = ui.interact()

        if result == "train":
            hide screen swimming_pool_build_group
            with dissolve

            return
        else:
            $ trainee = result[1]
            if result[0] == "interact":
                $ iam.start_int(trainee[0], img=iam.select_beach_img_tags(char, "pool"), exit="swimming_pool_build_group", bg="swimming_pool")
            elif result[0] == "dismiss":
                $ spool_group.members.remove(trainee)
                $ iam.dispo_reward(trainee[0], -randint(8, 12))
            elif result[0] == "take":
                $ spool_group.members.append(trainee)
                $ candidates[candidates.index(trainee)] = None
            elif result[0] == "home":
                python hide:
                    spool_group.members.remove(trainee)
                    backup.append(trainee)
                    # char sent home:
                    char = trainee[0]
                    if any((char.get_stat("health") < char.get_max("health")/2,
                           char.get_stat("vitality") < 40,
                           not char.has_ap(),
                           "Exhausted" in char.effects,
                           "Injured" in char.effects,
                           "Food Poisoning" in char.effects,
                           "Down with Cold" in char.effects,
                           char.get_stat("joy") < 30)):
                        # char not able to swim or has a negative effect
                        iam.dispo_reward(char, randint(8, 12))
                    else:
                        # char is able to swim
                        iam.dispo_reward(char, -randint(4, 8))
            $ del trainee

screen swimming_pool_build_group:
    frame:
        background Frame("content/gfx/images/bg_gradient.webp")
        yalign .4
        xsize config.screen_width
        padding 20, 20
        hbox:
            style_prefix "proper_stats"
            align .5, .5
            spacing 100
            vbox:
                xsize 300
                yalign .5
                label "Candidates:" xalign .5 text_size 24
                for i, trainee in izip_longest(xrange(3), candidates):
                    $ char = None if trainee is None else trainee[0]
                    hbox:
                        xalign .5
                        xysize 300, 160
                        if char is None:
                            frame:
                                padding(2, 2)
                                background Frame("content/gfx/frame/MC_bg3.png")
                                xysize (94, 94)
                                yalign .5
                                imagebutton:
                                    align .5, .5
                                    idle im.Scale("content/gfx/interface/icons/checkbox_inactive.png", 90, 90)
                                    action NullAction()
                        else:
                            fixed:
                                xysize 94, 160
                                frame:
                                    padding(2, 2)
                                    background Frame("content/gfx/frame/MC_bg3.png")
                                    xysize (94, 94)
                                    yalign .5
                                    imagebutton:
                                        align .5, .5
                                        idle char.show("portrait", label_cache=True, resize=(90, 90), type="reduce")
                                        action NullAction()
                                    python:
                                        effects = set([i for i in char.effects if i in ("Exhausted", "Injured", "Food Poisoning", "Down with Cold")])
                                        if char.get_stat("health") < char.get_max("health")/2:
                                            effects.add("Injured")
                                        if char.get_stat("vitality") < 40 or not char.has_ap():
                                            effects.add("Tired")
                                    for i in effects:
                                        imagebutton:
                                            align .9, .9
                                            idle "red_dot_gm"
                                            action NullAction()
                                            tooltip i
                                label char.name align .5, .1 text_color "#DAA520":
                                    if len(char.name) > 9:
                                        text_size 12
                                hbox:
                                    align .5, .98
                                    use stars(char.get_skill("swimming"), char.get_max_skill("swimming"))
                                label "Tier %s" % char.tier align .5, .9 text_color "#DAA520"

                        frame:
                            style_group "main_screen_3"
                            yalign .5
                            has vbox
                            textbutton "Interact":
                                xsize 200
                                action Return(["interact", trainee])
                                sensitive trainee is not None
                            textbutton "Take":
                                xsize 200
                                action Return(["take", trainee])
                                sensitive trainee is not None

            vbox:
                xsize 600
                yalign .5
                label "Group members:" xalign .5 text_size 24
                grid 2 3:
                    for i, trainee in izip_longest(xrange(6), spool_group.members):
                        $ char = None if trainee is None else trainee[0]
                        hbox:
                            xalign .5
                            xysize 300, 160
                            if char is None:
                                frame:
                                    padding (2, 2)
                                    background Frame("content/gfx/frame/MC_bg3.png")
                                    xysize (94, 94)
                                    yalign .5
                                    imagebutton:
                                        align .5, .5
                                        idle im.Scale("content/gfx/interface/icons/checkbox_inactive.png", 90, 90)
                                        action NullAction()
                            else:
                                fixed:
                                    xysize 94, 160
                                    frame:
                                        padding (2, 2)
                                        background Frame("content/gfx/frame/MC_bg3.png")
                                        xysize (94, 94)
                                        yalign .5
                                        imagebutton:
                                            align .5, .5
                                            idle char.show("portrait", label_cache=True, resize=(90, 90), type="reduce")
                                            action NullAction()
                                        python:
                                            effects = set([i for i in char.effects if i in ("Exhausted", "Injured", "Food Poisoning", "Down with Cold")])
                                            if char.get_stat("health") < char.get_max("health")/2:
                                                effects.add("Injured")
                                            if char.get_stat("vitality") < 40 or not char.has_ap():
                                                effects.add("Tired")
                                        for i in effects:
                                            imagebutton:
                                                align .9, .9
                                                idle "red_dot_gm"
                                                action NullAction()
                                                tooltip i
                                    label char.name align .5, .1 text_color "#DAA520":
                                        if len(char.name) > 9:
                                            text_size 12
                                    hbox:
                                        align .5, .98
                                        use stars(char.get_skill("swimming"), char.get_max_skill("swimming"))
                                    label "Tier %s" % char.tier align .5, .9 text_color "#DAA520"

                            frame:
                                style_group "main_screen_3"
                                yalign .5
                                has vbox
                                textbutton "Interact":
                                    xsize 200
                                    action Return(["interact", trainee])
                                    sensitive trainee is not None
                                textbutton "Send home":
                                    xsize 200
                                    action Return(["home", trainee])
                                    sensitive trainee is not None
                                textbutton "Dismiss":
                                    xsize 200
                                    action Return(["dismiss", trainee])
                                    sensitive trainee is not None

    textbutton "Begin training":
        align .5, .94
        style "basic_button"
        action Return("train")
        keysym "mousedown_3"

label swimming_pool_eval_group:
    # Evalutaion screen after the training
    python hide:
        global base_incentive
        for tmp in spool_group.members:
            tmp[3] = [tmp[3], None]
        temp = 4 * 100 * hero.get_stat("fame") * max(0, hero.get_stat("reputation"))
        temp /= float(hero.get_max("fame") * hero.get_max("reputation"))
        base_incentive = 1 + .002 * temp

    show screen swimming_pool_eval_group
    with dissolve

    while 1:
        $ result = ui.interact()

        python hide:
            if result == "done":
                # "ok" the non-evaluated chars
                group_members = [["ok", trainee] for trainee in spool_group.members if isinstance(trainee[3], list)] 
            else:
                group_members = [result]

            for decision, trainee in group_members:
                char = trainee[0]
                performance = trainee[4]
                incentive = trainee[3][0]
                if decision == "praise":
                    if performance > .9:
                        # exceptional performance -> praise expected
                        char.gfx_mod_stat("affection", affection_reward(char))
                        char.gfx_mod_stat("joy", randint(4, 6))

                        iam.dispo_reward(char, randint(4, 6))
                        incentive *= 1.1
                        if dice(20 - incentive * 10):
                            incentive *= 1.1 # a bit of chance to increase the incentive
                        elif dice((incentive - base_incentive) * 20):
                            incentive *= .9 # a bit of chance to slack off
                    elif performance > .7:
                        # good performance -> ok expected
                        if dice(50 + check_submissivity(char) * 25):
                            # a char without character might believe the praise is justified
                            char.gfx_mod_stat("affection", affection_reward(char))
                            char.gfx_mod_stat("joy", randint(2, 4))

                            incentive *= 1.1
                            if dice(50 + check_submissivity(char) * 25):
                                incentive *= 1.1 # might even want to push more
                        else:
                            iam.dispo_reward(char, -randint(1, 2))
                    elif performance > .5:
                        # bad perforamnce -> insult expected
                        iam.dispo_reward(char, -randint(8, 10))
                        if dice(50 - check_submissivity(char) * 25):
                            incentive *= .8 # a char with character might slack off even more
                    else:
                        # awful perforamnce -> punishment expected
                        iam.dispo_reward(char, -randint(16, 20))
                        incentive *= .8
                elif decision == "ok":
                    if performance > .9:
                        # exceptional performance -> praise expected
                        if dice(50 - check_submissivity(char)* 25):
                            incentive *= 1.1 # a char with character can live without praise
                        else:
                            iam.dispo_reward(char, -randint(1, 2))
                            char.gfx_mod_stat("joy", -randint(1, 2))
                    elif performance > .7:
                        # good performance -> ok expected
                        iam.dispo_reward(char, randint(4, 6))
                        incentive *= 1.1
                        if dice(20 - incentive * 10):
                            incentive *= 1.1 # a bit of chance to increase the incentive
                        elif dice((incentive - base_incentive) * 20):
                            incentive *= .9 # a bit of chance to slack off
                    elif performance > .5:
                        # bad perforamnce -> insult expected
                        if dice(50 - check_submissivity(char) * 25):
                            incentive *= 1.1 # a char with character might proceed without change
                        else:
                            iam.dispo_reward(char, -randint(4, 6))
                            if dice(50 + check_submissivity(char) * 25):
                                incentive *= .9 # a char without character might slack off even more
                    else:
                        # awful perforamnce -> punishment expected
                        iam.dispo_reward(char, -randint(8, 10))
                        if dice(50 - check_submissivity(char) * 25):
                            incentive *= .8 # a char with character might slack off even more
                elif decision == "insult":
                    char.gfx_mod_stat("character", stat_reward(char, hero, "character", -1))
                    char.gfx_mod_stat("joy", -randint(2, 4))
                    if performance > .9:
                        # exceptional performance -> praise expected
                        if dice(30 + check_submissivity(char) * 15):
                            incentive *= 1.1 # a char without character might believe the insult is justified
                        else:
                            iam.dispo_reward(char, -randint(8, 10))
                    elif performance > .7:
                        # good performance -> ok expected
                        if dice(50 + check_submissivity(char) * 25):
                            incentive *= 1.1 # a char without character might believe the insult is justified
                            if dice(50 + check_submissivity(char) * 25):
                                incentive *= 1.1 # might even want to push more
                        else:
                            iam.dispo_reward(char, -randint(4, 6))
                    elif performance > .5:
                        # bad perforamnce -> insult expected
                        iam.dispo_reward(char, randint(4, 6))
                        incentive *= 1.1
                        if dice(20 - incentive * 10):
                            incentive *= 1.1 # a bit of chance to increase the incentive
                        elif dice((incentive - base_incentive) * 20):
                            incentive *= .9 # a bit of chance to slack off
                    else:
                        # awful perforamnce -> punishment expected
                        if dice(50 - check_submissivity(char) * 25):
                            incentive *= 1.1 # to a char with character an insult is enough
                            if dice(50 - check_submissivity(char) * 25):
                                incentive *= 1.1 # might even want to push more
                        else:
                            iam.dispo_reward(char, -randint(1, 2))
                            if dice(50 + check_submissivity(char) * 25):
                                incentive *= .9 # a char without character might slack off even more
                elif decision == "punish":
                    char.gfx_mod_stat("character", -1)
                    char.gfx_mod_stat("joy", -randint(4, 6))
                    if performance > .95:
                        # exceptional performance -> praise expected
                        iam.dispo_reward(char, -randint(16, 20))
                        incentive *= .8
                    elif performance > .7:
                        # good performance -> ok expected
                        if dice(30 + check_submissivity(char) * 15):
                            incentive *= 1.1 # a char without character might believe the punishment is justified
                        else:
                            iam.dispo_reward(char, -randint(8, 10))
                    elif performance > .5:
                        # bad perforamnce -> insult expected
                        if dice(50 + check_submissivity(char) * 25):
                            incentive *= 1.1 # a char without character might believe the punishment is justified
                            if dice(50 + check_submissivity(char) * 25):
                                incentive *= 1.1 # might even want to push more
                        else:
                            iam.dispo_reward(char, -randint(4, 6))
                    else:
                        # awful perforamnce -> punishment expected
                        iam.dispo_reward(char, randint(4, 6))
                        incentive *= 1.1
                        if dice(20 - incentive * 10):
                            incentive *= 1.1 # a bit of chance to increase the incentive
                        elif dice((incentive - base_incentive) * 20):
                            incentive *= .9 # a bit of chance to slack off
                trainee[3] = incentive

        if result == "done":
            hide screen swimming_pool_eval_group
            with dissolve
            $ del base_incentive
            return

screen swimming_pool_eval_group:
    frame:
        background Frame("content/gfx/images/bg_gradient.webp")
        yalign .1
        xsize config.screen_width
        padding 20, 20
        vbox:
            style_prefix "proper_stats"
            align .5, .5
            xsize 600
            label "Group members:" xalign .5 text_size 24
            grid 2 3:
                for i, trainee in izip_longest(xrange(6), spool_group.members):
                    $ char = None if trainee is None else trainee[0]
                    hbox:
                        xalign .5
                        xysize 300, 200
                        fixed:
                            xysize 130, 200
                            if char is None:
                                frame:
                                    padding (2, 2)
                                    background Frame("content/gfx/frame/MC_bg3.png")
                                    xysize (94, 94)
                                    align .5, .35
                                    imagebutton:
                                        align .5, .5
                                        idle im.Scale("content/gfx/interface/icons/checkbox_inactive.png", 90, 90)
                                        action NullAction()
                            else:
                                frame:
                                    padding (2, 2)
                                    background Frame("content/gfx/frame/MC_bg3.png")
                                    xysize (94, 94)
                                    align .5, .35
                                    imagebutton:
                                        align .5, .5
                                        idle char.show("portrait", label_cache=True, resize=(90, 90), type="reduce")
                                        action NullAction()
                                    python:
                                        effects = set([i for i in char.effects if i in ("Exhausted", "Injured", "Food Poisoning", "Down with Cold")])
                                        if char.get_stat("health") < char.get_max("health")/2:
                                            effects.add("Injured")
                                        if char.get_stat("vitality") < 40 or not char.has_ap():
                                            effects.add("Tired")
                                    for i in effects:
                                        imagebutton:
                                            align .9, .9
                                            idle "red_dot_gm"
                                            action NullAction()
                                            tooltip i
                                label char.name align .5, .1 text_color "#DAA520":
                                    if len(char.name) > 9:
                                        text_size 12
                                hbox:
                                    align .5, .8
                                    use stars(char.get_skill("swimming"), char.get_max_skill("swimming"))
                                label "Tier %s" % char.tier align .5, .7 text_color "#DAA520"
                                $ value = int(trainee[2])
                                frame:
                                    align .5, .94
                                    xysize 130, 25
                                    text ("Swimming:") align .02, .5
                                    label "[value]" text_color ("lawngreen" if value > 0 else "red") align .98, .5

                        frame:
                            style_group "main_screen_3"
                            yalign .5
                            has vbox
                            textbutton "Praise":
                                xsize 200
                                action Return(["praise", trainee])
                                sensitive trainee is not None and isinstance(trainee[3], list)
                            textbutton "Ok":
                                xsize 200
                                action Return(["ok", trainee])
                                sensitive trainee is not None and isinstance(trainee[3], list)
                            textbutton "Insult":
                                xsize 200
                                action Return(["insult", trainee])
                                sensitive trainee is not None and isinstance(trainee[3], list)
                            textbutton "Punish":
                                xsize 200
                                action Return(["punish", trainee])
                                sensitive trainee is not None and isinstance(trainee[3], list)

    textbutton "Done":
        align .98, .98
        style "basic_button"
        action Return("done")
        keysym "mousedown_3"
