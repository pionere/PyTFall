#Angelica

label mages_tower:
    $ iam.enter_location(goodtraits=["Psychic", "Curious"], badtraits=["Indifferent"], goodoccupations=["Caster"], badoccupations=["SIW"],
                        coords=[[.07, .8], [.57, .64], [.93, .61]])
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("mages_tower")
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("mages_tower"):
            pytfall.world_actions.add("angelica", "Find Angelica", Jump("angelica_meet"), condition=Iff(global_flag_complex("met_angelica")))
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    scene bg mages_tower
    with dissolve

    if not global_flags.has_flag('visited_mages_tower'):
        $ global_flags.set_flag('visited_mages_tower')
        "Real mages, other practitioners of Arcane Arts and some plain weirdos hang around here."
        "Try not to get yourself blown up :)"

    show screen mages_tower

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_int(result[1], img=result[1].show("girlmeets", "magic", exclude=["swimsuit", "beach", "pool", "urban", "stage", "onsen", "indoors", "indoor"], type="reduce", label_cache=True, gm_mode=True))

        elif result == ['control', 'return']:
            hide screen mages_tower
            jump city


screen mages_tower():
    use top_stripe(True)
    use location_actions("mages_tower")

    if iam.show_girls:
        use interactions_meet