label city_parkgates:
    scene bg city_parkgates
    with dissolve

    if pytfall.enter_location("park_gates", music=True, env="city_park", coords=[(.1, .75), (.4, .67), (.9, .7)],
                             goodtraits=["Elf", "Furry", "Human"], badtraits=["Aggressive", "Adventurous"]):
        "Gates to the park on city outskirts. Great place to hit on girls or take a walk after lunch on a sunny day."

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen city_parkgates
    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_int(result[1], img=result[1].show("girlmeets", "outdoors", "nature", "urban", exclude=["swimsuit", "wildness", "indoors", "stage", "beach", "pool", "onsen", "indoor"], type="reduce", label_cache=True, gm_mode=True))

        elif result[0] == 'control':
            hide screen city_parkgates
            if result[1] == 'jumppark':
                jump city_park

            if result[1] == 'return':
                jump city

screen city_parkgates():
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
            action Return(['control', 'jumppark'])
