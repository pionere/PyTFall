label city_park:
    $ iam.enter_location(goodtraits=["Elf", "Furry"], badtraits=["Aggressive", "Adventurous"],
                        coords=[[.1, .7], [.4, .45], [.74, .73]])

    scene bg city_park
    with dissolve

    show screen city_park

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_int(result[1], img=result[1].show("girlmeets", "outdoors", "nature", "urban", exclude=["swimsuit", "wildness", "indoors", "stage", "beach", "pool", "onsen", "indoor"], type="reduce", label_cache=True, gm_mode=True), keep_music=False)

        elif result[0] == 'control':
            #if result[1] in ['jumpgates', 'return'):
                $ global_flags.set_flag("keep_playing_music")
                hide screen city_park
                jump city_parkgates

screen city_park():
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
        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
        imagebutton:
            align (.01, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(['control', 'jumpgates'])

        $ img = im.Scale("content/gfx/interface/icons/park_swing.png", 80, 80)
        imagebutton:
            pos (670, 310)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_park"), Jump("mc_action_park_rest")]
            tooltip "Rest"

        if global_flags.has_flag("met_aine"):
            $ img = im.Scale("content/gfx/interface/icons/aine.png", 75, 75)
            imagebutton:
                pos (1090, 340)
                idle img
                hover PyTGFX.bright_img(img, .15)
                action [Hide("city_park"), Jump("aine_menu"), With(dissolve)]

label mc_action_park_rest:
    if hero.has_flag("dnd_rest_at_park"):
        "You already relaxed at the park today."
        jump city_park
    $ hero.set_flag("dnd_rest_at_park")

    if len(hero.team) > 1:
        $ members = list(member for member in hero.team if (member != hero))
        if len(members) == 1:
            show expression members[0].get_vnsprite() at center as temp1
            with dissolve
        else:
            show expression members[0].get_vnsprite() at left as temp1
            show expression members[1].get_vnsprite() at right as temp2
            with dissolve
        $ del members
        "You're relaxing in the park with your team."
    else:
        "You're relaxing in the park."

    python hide:
        for member in hero.team:
            member.gfx_mod_stat("vitality", randint(4, 8))
            if ("Clumsy" in member.traits or "Homebody" in member.traits) and dice(5):
                member.enable_effect("Injured", duration=randint(1, 2))
                member.gfx_mod_stat("joy", -randint(1, 2))
                iam.got_injured(member)
            elif member.get_stat("joy") < 50:
                member.gfx_mod_stat("joy", randint(1, 2))
            if member != hero:
                member.gfx_mod_stat("disposition", randint(1, 2))
                member.gfx_mod_stat("affection", affection_reward(member, .1))

    jump city_park
