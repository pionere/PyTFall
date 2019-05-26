label swimming_pool:
    $ gm.enter_location(has_tags=["girlmeets", "swimsuit"], has_no_tags=["beach", "sleeping"],
                        curious_priority=False, coords=[[.2, .45], [.42, .6], [.7, .5]])
    # Music
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("swimming_pool")
    $ global_flags.del_flag("keep_playing_music")

    python:
        if pytfall.world_actions.location("swimming_pool"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()
    scene bg swimming_pool
    with dissolve

    if not global_flags.flag('visited_swimming_pool'):
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

        if result[0] == 'jump':
            python hide:
                char = result[1]
                tags = char.get_tags_from_cache(last_label)
                if not tags:
                    img_tags = (["girlmeets", "pool"], ["girlmeets", "swimsuit", "simple bg"], ["girlmeets", "swimsuit", "no bg"])
                    tags = get_simple_act(char, img_tags)
                    if not tags:
                        img_tags = (["girlmeets", "simple bg"], ["girlmeets", "no bg"])
                        tags = get_simple_act(char, img_tags)
                        if not tags:
                            # giveup
                            tags = ["girlmeets", "swimsuit"]
                gm.start_gm(char, img=char.show(*tags, type="reduce", label_cache=True, gm_mode=True))

        elif result[0] == 'control':
            if result[1] == 'return':
                hide screen swimming_pool
                jump city_beach


screen swimming_pool():
    use top_stripe(True)

    $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
    imagebutton:
        align (.01, .5)
        idle (img)
        hover (im.MatrixColor(img, im.matrix.brightness(.15)))
        action [Hide("swimming_pool"), Jump("city_beach")]

    use location_actions("swimming_pool")
    $ img_swim_pool = ProportionalScale("content/gfx/interface/icons/sp_swimming.png", 90, 90)
    imagebutton:
        pos(290, 510)
        idle (img_swim_pool)
        hover (im.MatrixColor(img_swim_pool, im.matrix.brightness(.15)))
        action [Hide("swimming_pool"), Show("swimmong_pool_swim"), With(dissolve)]

    if gm.show_girls:
        key "mousedown_3" action ToggleField(gm, "show_girls")

        add "content/gfx/images/bg_gradient.webp" yalign .45

        for entry, pos in zip(gm.display_girls(), gm.coords):
            hbox:
                align pos
                use rg_lightbutton(return_value=['jump', entry])

screen swimmong_pool_swim():
    style_prefix "dropdown_gm"
    frame:
        pos (.98, .98) anchor (1.0, 1.0)
        has vbox
        textbutton "Swim (10 G)":
            action Hide("swimmong_pool_swim"), Jump("single_swim_pool")
        textbutton "Hire an instructor (50 G)":
            action Hide("swimmong_pool_swim"), Jump("instructor_swim_pool")
        if hero.get_skill("swimming") >= 100:
            textbutton "Work as instructor":
                action Hide("swimmong_pool_swim"), Jump("mc_action_work_swim_pool")
        textbutton "Leave":
            action Hide("swimmong_pool_swim"), Show("swimming_pool"), With(dissolve)
            keysym "mousedown_3"


label single_swim_pool:
    if hero.get_stat("vitality") < 20 or not hero.has_ap():
        "You are too tired at the moment."
    elif hero.get_stat("health") < hero.get_max("health")/2:
        "You are too wounded at the moment."
    elif hero.take_money(10, reason="Swimming Pool"):
        play world "underwater.mp3"
        scene bg pool_swim
        with dissolve
        call mc_action_swimming_pool_skill_checks from _call_mc_action_swimming_pool_skill_checks
    else:
        "You don't have enough gold."
    jump swimming_pool

label instructor_swim_pool:
    if hero.get_stat("vitality") < 20 or not hero.has_ap():
        "You are too tired at the moment."
    elif hero.get_stat("health") < hero.get_max("health")/2:
        "You are too wounded at the moment."
    elif hero.take_money(50, reason="Swimming Pool"):
        play world "underwater.mp3"
        scene bg pool_swim
        with dissolve
        call mc_action_instructor_swimming_pool_skill_checks from _call_mc_action_instructor_swimming_pool_skill_checks
    else:
        "You don't have enough Gold."
    jump swimming_pool

label mc_action_swimming_pool_skill_checks:
    $ hero.take_ap(1)
    $ temp = hero.get_skill("swimming")
    if temp < 20:
        if locked_dice(60):
            "You barely stay afloat. Clearly, more practice is needed."
            $ swim_act = randint(1,2)
        else:
            "You can barely stay afloat. After a while, you lose your cool and start drowning, but the swimming instructor immediately comes to your aid."
            $ swim_act = 1
            $ hero.gfx_mod_stat("health", -5)
        $ swim_vit = randint (25, 35)
    elif temp < 50:
        "You can swim well enough to not drown in a swimming pool, but more practice is needed."
        $ swim_act = randint(2,3)
        $ swim_vit = randint (20, 30)
    elif temp < 100:
        "You are somewhat confident about your swimming skills."
        $ swim_act = randint(2,4)
        $ swim_vit = randint (15, 20)
    else:
        "It feels nice swimming in the pool, but the sea is more suitable to learn something new."
        $ swim_act = randint(0,1)
        $ swim_vit = randint (10, 15)
    if locked_dice(75) and hero.get_skill("swimming") >= 50 and hero.get_stat("constitution") < hero.get_max("constitution"):
        "Swimming did you good."
        $ hero.gfx_mod_stat("constitution", 1)
    $ hero.gfx_mod_skill("swimming", 0, swim_act)
    $ hero.mod_stat("vitality", -swim_vit)
    $ del swim_act, swim_vit
    return

label mc_action_instructor_swimming_pool_skill_checks:
    $ hero.take_ap(1)
    $ temp = hero.get_skill("swimming")
    if temp < 20:
        "The instructor teaches you water safety to prevent mouth-to-mouth accidents once and for all."
        $ swim_act = randint(2,4)
        $ swim_tra = randint(2,4)
        $ swim_vit = randint (20, 30)
    elif temp < 50:
        "The instructor shows you the most basic swimming styles."
        $ swim_act = randint(4,6)
        $ swim_tra = randint(4,6)
        $ swim_vit = randint (15, 25)
    elif temp < 100:
        "The instructor shows you common swimming styles and the very basics of underwater swimming."
        $ swim_act = randint(4,8)
        $ swim_tra = randint(4,8)
        $ swim_vit = randint (10, 15)
    elif temp < 250:
        "The instructor shows you advanced swimming styles, including underwater ones."
        $ swim_act = randint(1,3)
        $ swim_tra = randint(5,10)
        $ swim_vit = randint (10, 15)
    else:
        "There is nothing else he can show you now, but his knowledge about behavior on the water is second to none nevertheless."
        $ swim_act = randint(0,1)
        $ swim_tra = randint(5,10)
        $ swim_vit = randint (5, 10)
    if locked_dice(65) and hero.get_skill("swimming") >= 50:
        "Swimming did you good."
        $ hero.gfx_mod_stat("constitution", 1)
    $ hero.gfx_mod_skill("swimming", 0, swim_act)
    $ hero.gfx_mod_skill("swimming", 1, swim_tra)
    $ hero.mod_stat("vitality", -swim_vit)
    $ del swim_act, swim_tra, swim_vit
    return

label mc_action_work_swim_pool: # here we could use an option to meet characters with a certain probability
    if hero.get_stat("vitality") < 20:
        "You are too tired for work."
        jump swimming_pool
    elif not hero.has_ap():
        "You don't have enough Action Points. Try again tomorrow."
        jump swimming_pool
    elif hero.get_stat("health") < hero.get_max("health")/2:
        "You are too wounded at the moment."
        jump swimming_pool

    $ picture = "content/gfx/images/swim_kids/sk_" + str(renpy.random.randint(1, 4)) + ".webp"
    show expression picture at truecenter with dissolve
    $ narrator ("You teach local kids to swim. The payment is low, but at least you can use the pool for free.")

label mc_action_work_swim_pool_reward:
    python:
        result = randint(5, round(hero.get_skill("swimming")*.1))
        if result > 200:
            result = randint (190, 220)
        result = gold_reward(hero, result)
        hero.take_ap(1)
        hero.gfx_mod_skill("swimming", 0, randint(0,2))
        hero.gfx_mod_skill("swimming", 1, randint(1,2))
        hero.mod_stat("vitality", -randint (20, 35))
        hero.add_money(result, reason="Job")
        gfx_overlay.random_find(result, 'work')
        hero.gfx_mod_exp(exp_reward(hero, hero))
        del result

    hide expression picture with dissolve
    jump swimming_pool
