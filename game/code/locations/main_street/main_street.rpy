label main_street:
    scene bg main_street

    $ pytfall.enter_location("main_street", music=True, env="main_street", coords=[(.1, .7), (.57, .54), (.93, .61)],
                             goodtraits=["Human", "Kleptomaniac"], badtraits=["Not Human", "Alien", "Strange Eyes"])

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen main_street
    with dissolve # dissolve the whole scene, not just the bg
    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_int(result[1], img=result[1].show("girlmeets", "outdoors", "urban", exclude=["swimsuit", "indoor", "wildness", "suburb", "beach", "pool", "onsen", "nature"], type="reduce", label_cache=True, gm_mode=True))

        elif result == ['control', 'return']:
            hide screen main_street
            jump city


screen main_street():
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
            action [Hide("main_street"), Jump("employment_agency")]
            tooltip "Employment Agency"
        if global_flags.flag("know_swinger_club"):
            $ img = im.Scale("content/gfx/interface/icons/swinger_club.png", 50, 50)
            imagebutton:
                pos 800, 220
                idle img
                hover PyTGFX.bright_img(img, .15)
                action [Hide("main_street"), Jump("swinger_club")]
                tooltip "Club"
