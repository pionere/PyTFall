label forest_entrance:
    scene bg forest_entrance
    with dissolve

    if pytfall.enter_location("dark_forest", music=True, env="forest_entrance", coords=[(.1, .7), (.39, .84), (.88, .71)],
                             goodtraits=["Furry", "Monster", "Scars", "Adventurous", "Curious"], badtraits=["Homebody", "Coward", "Exhibitionist", "Human"]):
        "A dark, thick forest surrounds the city from the west. Only a few people live here, and even fewer are brave enough to step away far from city walls without a platoon of guards."

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen forest_entrance
    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_int(result[1], img=result[1].show("girlmeets", "nature", "wildness", type="first_default", label_cache=True, gm_mode=True,
                            exclude=["urban", "beach", "onsen", "dungeon", "stage", "swimsuit", "indoor", "formal"]))
        elif result[0] == "control":
            hide screen forest_entrance
            if result[1] == "return":
                jump city
            elif result[1] == "hut":
                jump witches_hut
            elif result[1] == "forest":
                jump forest_dark
            elif result[1] == "peevish":
                jump peevish_menu
            elif result[1] == "wood":
                jump mc_action_wood_cutting

label mc_action_wood_cutting:
    if not has_items("Woodcutting Axe", hero, equipped=True):
        "You need an equipped Woodcutting Axe before doing anything."
    elif not hero.has_ap():
        "You don't have Action Points left. Try again tomorrow."
    elif hero.get_stat("vitality") < 50:
        "You are too tired for that."
    else:
        "You grab your axe and start working."
        $ wood = (hero.get_stat("constitution")+hero.get_stat("attack")) // 10 + randint(1, 2)
        $ hero.take_ap(1)
        $ hero.mod_stat("vitality", -50)
        if dice(50):
            $ hero.gfx_mod_stat("attack", randint(0, 2))
        if dice(50):
            $ hero.gfx_mod_stat("constitution", 1)
        $ hero.gfx_mod_stat("joy", -randint(0, 2))
        $ hero.add_item("Wood", wood)
        $ gfx_overlay.random_find(items["Wood"], 'items', wood)
        $ del wood

    jump forest_entrance

screen forest_entrance():
    use top_stripe(True)

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
        $ img = im.Scale("content/gfx/interface/icons/witch.png", 90, 90)
        imagebutton:
            pos (670, 490)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "hut"])
            tooltip "Abby's Shop"

        $ img = im.Scale("content/gfx/interface/icons/deep_forest.png", 75, 75)
        imagebutton:
            pos (350, 450)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "forest"])
            tooltip "Dark Forest\nBeware all who enter here"

        if global_flags.has_flag("visited_peevish"):
            $ img = im.Scale("content/gfx/interface/icons/peevish.png", 75, 75)
            imagebutton:
                pos (100, 100)
                idle img
                hover PyTGFX.bright_img(img, .15)
                action Return(["control", "peevish"])
                tooltip "Peevishes Shop"

        $ img = im.Scale("content/gfx/interface/icons/wood_cut.png", 90, 90)
        imagebutton:
            pos (1120, 460)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "wood"])
            tooltip "Trees Cutting"
