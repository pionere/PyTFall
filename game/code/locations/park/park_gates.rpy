label city_parkgates:
    $ iam.enter_location(goodtraits=["Elf", "Furry", "Human"], badtraits=["Aggressive", "Adventurous"],
                        coords=[[.1, .75], [.4, .67], [.9, .7]])
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("park", fadein=.5)
    $ global_flags.del_flag("keep_playing_music")

    scene bg city_parkgates
    with dissolve

    if not global_flags.has_flag('visited_park_gates'):
        $ global_flags.set_flag('visited_park_gates')
        "Gates to the park on city outskirts. Great place to hit on girls or take a walk after lunch on a sunny day."

    show screen city_parkgates

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

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
