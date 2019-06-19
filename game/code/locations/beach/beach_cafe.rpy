label city_beach_cafe:
    $ iam.enter_location(goodtraits=["Athletic", "Dawdler", "Always Hungry"], badtraits=["Scars", "Undead", "Furry", "Monster"],
                        coords=[[.2, .75], [.5, .65], [.87, .6]])
    $ global_flags.set_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("city_beach_cafe"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    scene bg city_beach_cafe
    with dissolve
    show screen city_beach_cafe

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
                hide screen city_beach_cafe
                jump city_beach_cafe_main


screen city_beach_cafe:
    use top_stripe(True)

    if not iam.show_girls:
        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80)
        imagebutton:
            align (.99, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach_cafe"), Jump("city_beach_cafe_main")]

    use location_actions("city_beach_cafe")

    if iam.show_girls:
        key "mousedown_3" action ToggleField(iam, "show_girls")

        add "content/gfx/images/bg_gradient.webp" yalign .45

        for entry, pos in zip(iam.display_girls(), iam.coords):
            hbox:
                align pos
                use rg_lightbutton(return_value=['jump', entry])