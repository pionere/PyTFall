label city_park:
    $ iam.enter_location(goodtraits=["Elf", "Furry"], badtraits=["Aggressive", "Adventurous"],
                        coords=[[.1, .7], [.4, .45], [.74, .73]])
    python:
        # Build the actions
        if pytfall.world_actions.location("city_park"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    scene bg city_park
    with dissolve

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen city_park

    while 1:

        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_gm(result[1], img=result[1].show("girlmeets", "outdoors", "nature", "urban", exclude=["swimsuit", "wildness", "indoors", "stage", "beach", "pool", "onsen", "indoor"], type="reduce", label_cache=True, gm_mode=True))

        if result[0] == 'control':
            #if result[1] in ['jumpgates', 'return'):
                $ global_flags.set_flag("keep_playing_music")
                hide screen city_park
                jump city_parkgates

screen city_park():
    use top_stripe(True)

    if not iam.show_girls:
        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
        imagebutton:
            align (.01, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(['control', 'jumpgates'])

    use location_actions("city_park")

    if iam.show_girls:
        key "mousedown_3" action ToggleField(iam, "show_girls")
        add "content/gfx/images/bg_gradient.webp" yalign .45
        for entry, pos in zip(iam.display_girls(), iam.coords):
            hbox:
                align pos
                use rg_lightbutton(return_value=['jump', entry])

    if not iam.show_girls:
        if global_flags.has_flag("met_aine"):
            $ img = im.Scale("content/gfx/interface/icons/aine.png", 75, 75)
            imagebutton:
                pos (1090, 340)
                idle img
                hover PyTGFX.bright_img(img, .15)
                action [Hide("city_park"), Jump("aine_menu"), With(dissolve)]
