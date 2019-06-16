label city_beach_cafe_main:
    $ iam.enter_location(goodtraits=["Athletic", "Dawdler", "Always Hungry"], badtraits=["Scars", "Undead", "Furry", "Monster"],
                        coords=[[.15, .75], [.5, .6], [.9, .8]])
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("beach_cafe")
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("city_beach_cafe_main"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    scene bg city_beach_cafe_main
    with dissolve
    show screen city_beach_cafe_main

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            python hide:
                char = result[1]
                tags = char.get_tags_from_cache(last_label)
                if not tags:
                    img_tags = (["girlmeets", "beach"], ["girlmeets", "swimsuit", "simple bg"], ["girlmeets", "swimsuit", "no bg"], ["girlmeets", "swimsuit", "outdoors"])
                    tags = get_simple_act(char, img_tags)
                    if not tags:
                        img_tags = (["girlmeets", "simple bg"], ["girlmeets", "no bg"])
                        tags = get_simple_act(char, img_tags)
                        if not tags:
                            # giveup
                            tags = ["girlmeets", "swimsuit"]
                iam.start_gm(char, img=char.show(*tags, type="reduce", label_cache=True, gm_mode=True))

        elif result[0] == 'control':
            if result[1] == 'return':
                hide screen city_beach_cafe_main
                jump city_beach_left


screen city_beach_cafe_main:
    use top_stripe(True)

    if not iam.show_girls:
        # Jump buttons:
        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
        imagebutton:
            align (.01, .5)
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(.15))
            action [Hide("city_beach_cafe_main"), Function(global_flags.del_flag, "keep_playing_music"), Jump("city_beach_cafe")]

        $ img = im.Scale(im.Flip("content/gfx/interface/buttons/blue_arrow_up.png", vertical=True), 80, 70)
        imagebutton:
            align (.5, .99)
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(.15))
            action [Hide("city_beach_cafe_main"), Jump("city_beach_left")]

    use location_actions("city_beach_cafe_main")

    if iam.show_girls:
        key "mousedown_3" action ToggleField(iam, "show_girls")

        add "content/gfx/images/bg_gradient.webp" yalign .45

        for entry, pos in zip(iam.display_girls(), iam.coords):
            hbox:
                align pos
                use rg_lightbutton(return_value=['jump', entry])