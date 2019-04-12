label forest_entrance:
    $ gm.enter_location(goodtraits=["Furry", "Monster", "Scars", "Adventurous"], badtraits=["Homebody", "Coward", "Exhibitionist", "Human"],
                        curious_priority=True, coords=[[.1, .7], [.39, .84], [.88, .71]])
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("forest_entrance")
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("forest_entrance"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    scene bg forest_entrance at truecenter
    show screen forest_entrance
    with dissolve

    if not global_flags.flag('visited_dark_forest'):
        $ global_flags.set_flag('visited_dark_forest')
        $ block_say = True
        "A dark, thick forest surrounds the city from the west. Only a few people live here, and even fewer are brave enough to step away far from city walls without a platoon of guards."
        $ block_say = False

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:

        $ result = ui.interact()

        if result[0] == 'jump':
            $ gm.start_gm(result[1], img=result[1].show("girlmeets", "nature", "wildness", type="first_default", label_cache=True, resize=(300, 400), gm_mode=True,
                            exclude=["urban", "winter", "night", "beach", "onsen", "dungeon", "stage", "swimsuit", "indoor", "formal"]))
        if result[0] == 'control':
            if result[1] == 'return':
                hide screen forest_entrance
                jump city
        elif result[0] == 'location':
            $ renpy.music.stop(channel="world")
            $ jump(result[1])

label mc_action_wood_cutting:
    if not has_items("Woodcutting Axe", hero, equipped=True):
        "You need an equipped Woodcutting Axe before doing anything."
    elif hero.AP <= 0:
        "You don't have Action Points left. Try again tomorrow."
    elif hero.get_stat("vitality") < 50:
        "You are too tired for that."
    else:
        "You grab your axe and start working."
        $ wood = (hero.get_stat("constitution")+hero.get_stat("attack")) // 10 + randint(1, 2)
        $ hero.AP -= 1
        $ hero.mod_stat("vitality", -50)
        if dice(50):
            $ hero.gfx_mod_stat("attack", randint(0, 2))
        if dice(50):
            $ hero.gfx_mod_stat("constitution", 1)
        $ hero.gfx_mod_stat("joy", -randint(0, 2))
        $ hero.add_item("Wood", wood)
        $ gfx_overlay.random_find(items["Wood"], 'items', wood)
        $ del wood

    $ global_flags.set_flag("keep_playing_music")
    jump forest_entrance

screen forest_entrance():
    use top_stripe(True)

    use location_actions("forest_entrance")

    if gm.show_girls:
        key "mousedown_3" action ToggleField(gm, "show_girls")

        add "content/gfx/images/bg_gradient.webp" yalign .45
        for entry, pos in zip(gm.display_girls(), gm.coords):
            hbox:
                align pos
                use rg_lightbutton(return_value=['jump', entry])

    if not gm.show_girls:
        $ img_witch_shop = ProportionalScale("content/gfx/interface/icons/witch.png", 90, 90)
        imagebutton:
            pos(670, 490)
            idle (img_witch_shop)
            hover (im.MatrixColor(img_witch_shop, im.matrix.brightness(.15)))
            action [Jump("witches_hut"), With(dissolve)]
            tooltip "Abby's Shop"

        $ img_deep_forest= ProportionalScale("content/gfx/interface/icons/deep_forest.png", 75, 75)
        imagebutton:
            pos(350, 450)
            idle (img_deep_forest)
            hover (im.MatrixColor(img_deep_forest, im.matrix.brightness(.15)))
            action [Hide("forest_entrance"),
                    Function(global_flags.set_flag, "keep_playing_music"),
                    Jump("forest_dark"), With(dissolve)]
            tooltip "Dark Forest\nBeware all who enter here"

        if global_flags.has_flag("met_peevish"):
            $ img_peev_shop= ProportionalScale("content/gfx/interface/icons/peevish.png", 75, 75)
            imagebutton:
                pos(100, 100)
                idle (img_peev_shop)
                hover (im.MatrixColor(img_peev_shop, im.matrix.brightness(.15)))
                action [Hide("forest_entrance"), Jump("peevish_menu"), With(dissolve)]
                tooltip "Peevishes Shop"

        $ img_forest_wood = ProportionalScale("content/gfx/interface/icons/wood_cut.png", 90, 90)
        imagebutton:
            pos(1120, 460)
            idle (img_forest_wood)
            hover (im.MatrixColor(img_forest_wood, im.matrix.brightness(.15)))
            action [Hide("forest_entrance"), Jump("mc_action_wood_cutting"), With(dissolve)]
            tooltip "Trees Cutting"
