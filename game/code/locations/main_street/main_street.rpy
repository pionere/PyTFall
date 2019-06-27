label main_street:
    $ iam.enter_location(goodtraits=["Human", "Kleptomaniac"], badtraits=["Not Human", "Alien", "Strange Eyes"],
                        coords=[[.1, .7], [.57, .54], [.93, .61]])
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("main_street")
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("main_street"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    #$ global_flags.set_flag("visited_mainstreet", True)

    hide screen city_screen
    scene bg main_street at truecenter
    with dissolve

    show screen main_street
    with dissolve

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_int(result[1], img=result[1].show("girlmeets", "outdoors", "urban", exclude=["swimsuit", "indoor", "wildness", "suburb", "beach", "pool", "onsen", "nature"], type="reduce", label_cache=True, gm_mode=True))

        elif result == ['control', 'return']:
            hide screen main_street
            jump city


screen main_street():

    use top_stripe(True)

    use location_actions("main_street")

    if not iam.show_girls:
        $ img = im.Scale("content/gfx/interface/icons/tailor_shop.png", 50, 50)
        imagebutton:
            pos (245, 374)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("main_street"), Jump("tailor_store")]
            tooltip "Tailor Shop"
        $ img = im.Scale("content/gfx/interface/icons/cafe_shop.png", 60, 60)
        imagebutton:
            pos (31, 540)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("main_street"), Jump("cafe")]
            tooltip "Cafe"
        $ img = im.Scale("content/gfx/interface/icons/general_shop.png", 65, 65)
        imagebutton:
            pos (640, 360)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("main_street"), Jump("general_store")]
            tooltip "General Store"
        $ img = im.Scale("content/gfx/interface/icons/work_shop.png", 50, 50)
        imagebutton:
            pos (90, 390)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("main_street"), Jump("workshop")]
            tooltip "Workshop"
        $ img = im.Scale("content/gfx/interface/icons/realtor_shop.png", 50, 50)
        imagebutton:
            pos 245, 203
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("main_street"), Jump("realtor_agency")]
            tooltip "Real Estate Agency"
        $ img = im.Scale("content/gfx/interface/icons/employment_agency.png", 50, 50)
        imagebutton:
            pos 245, 256
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Jump("employment_agency")
            tooltip "Employment Agency"

    # Girlsmeets screen
    if iam.show_girls:
        key "mousedown_3" action ToggleField(iam, "show_girls")

        add "content/gfx/images/bg_gradient.webp" yalign .45

        for entry, pos in zip(iam.display_girls(), iam.coords):
            hbox:
                align pos
                use rg_lightbutton(return_value=['jump', entry])