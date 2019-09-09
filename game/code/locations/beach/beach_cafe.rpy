label city_beach_cafe:
    scene bg city_beach_cafe
    with dissolve

    $ pytfall.enter_location("beach_cafe", music=True, env="beach_cafe", coords=[(.2, .75), (.5, .65), (.87, .6)],
                             goodtraits=["Athletic", "Dawdler", "Always Hungry"], badtraits=["Scars", "Undead", "Furry", "Monster"])

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen city_beach_cafe
    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            python hide:
                char = result[1]
                iam.start_int(char, img=iam.select_beach_img_tags(char, "beach_cafe"))

        elif result == ['control', 'return']:
            hide screen city_beach_cafe
            jump city_beach_cafe_main


screen city_beach_cafe:
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
        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80)
        imagebutton:
            align (.99, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "return"])