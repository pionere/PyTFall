label city_beach_cafe:
    $ iam.enter_location(goodtraits=["Athletic", "Dawdler", "Always Hungry"], badtraits=["Scars", "Undead", "Furry", "Monster"],
                        coords=[[.2, .75], [.5, .65], [.87, .6]])

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
                iam.start_int(char, img=iam.select_beach_img_tags(char, "beach_cafe"), keep_music=False)

        elif result == ['control', 'return']:
            $ global_flags.set_flag("keep_playing_music")
            hide screen city_beach_cafe
            jump city_beach_cafe_main


screen city_beach_cafe:
    use top_stripe(True)
    use location_actions("city_beach_cafe")

    if iam.show_girls:
        use interactions_meet
    else:
        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80)
        imagebutton:
            align (.99, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach_cafe"), Jump("city_beach_cafe_main")]