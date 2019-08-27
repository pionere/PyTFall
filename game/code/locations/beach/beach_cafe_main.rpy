label city_beach_cafe_main:
    $ iam.enter_location(goodtraits=["Athletic", "Dawdler", "Always Hungry"], badtraits=["Scars", "Undead", "Furry", "Monster"],
                        coords=[[.15, .75], [.65, .62], [.9, .8]])
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("beach_cafe")
    $ global_flags.del_flag("keep_playing_music")

    if global_flags.get_flag("waitress_ice", [-1])[0] != day:
        python hide:
            who = global_flags.get_flag("waitress_cafe", [0, None])
            who = getattr(who[1], "id", None)
            who = [w for w in ["Mel_cafe", "Monica_cafe", "Chloe_cafe"] if w != who]
            who = npcs[(choice(who))]
            global_flags.set_flag("waitress_ice", value=[day, who])

    scene bg city_beach_cafe_main
    with dissolve

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    if not hero.has_flag("dnd_ice_in_cafe_inv"):
        $ hero.set_flag("dnd_ice_in_cafe_inv")
        $ inviting_character = iam.would_invite(locked_random("randint", 100, 200))
        if inviting_character:
            $ iam.icecream_propose(inviting_character)
            menu:
                "Do you want to accept [inviting_character.pd] invitation (free of charge)?"
                "Yes":
                    scene bg icestand
                    jump mc_action_ice_invitation
                "No":
                    $ pass
        $ del inviting_character

    show screen city_beach_cafe_main

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            python hide:
                char = result[1]
                iam.start_int(char, img=iam.select_beach_img_tags(char, "beach_cafe"))

        elif result == ['control', 'return']:
            hide screen city_beach_cafe_main
            jump city_beach_left


screen city_beach_cafe_main:
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
        $ img = im.Scale("content/gfx/interface/icons/beach_ice.png", 80, 80)
        imagebutton:
            pos (642, 390)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach_cafe_main"), Jump("mc_action_city_beach_ice")]
            tooltip "Ice Cream"

        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
        imagebutton:
            align (.01, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach_cafe_main"), Jump("city_beach_cafe")]

        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow_up.png", 90, 60), vertical=True)
        imagebutton:
            align (.5, .99)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "return"])

label mc_action_city_beach_ice:
    if hero.has_flag("dnd_ice_in_cafe"):
        "You already had an icecream today. Too much of it, and a cold is guaranteed."
        $ global_flags.set_flag("keep_playing_music")
        jump city_beach_cafe_main

    $ waitress = global_flags.flag("waitress_ice")[1]

    scene bg icestand
    show expression waitress.get_vnsprite() as npc at truecenter
    show screen city_beach_ice_stand

    if global_flags.flag('visited_ice'):
        waitress.say "Welcome back! What can I have you today?"
    else:
        $ global_flags.set_flag('visited_ice')
        waitress.say "Welcome to the finest Ice Cream stand in the city!"
    $ del waitress

    while 1:
        $ result = ui.interact()

        hide screen city_beach_ice_stand
        if result == "ice_alone":
            $ inviting_character = None
            jump mc_action_ice_invitation
        if result == "ice_group":
            $ inviting_character = hero
            jump mc_action_ice_invitation
        $ global_flags.set_flag("keep_playing_music")
        jump city_beach_cafe_main

screen city_beach_ice_stand:
    add im.Scale("content/gfx/images/ice_stand.webp", config.screen_width, config.screen_height) # align .5, .5

    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Eat an icecream alone":
            action Return("ice_alone")
        textbutton "Icecream for the team":
            action Return("ice_group")
        textbutton "Leave":
            action Return("leave")
            keysym "mousedown_3"

label mc_action_ice_invitation:
    hide npc
    if inviting_character is None:
        # icecream alone
        if hero.take_money(randint(5, 10), reason="Icecream"):
            $ hero.set_flag("dnd_ice_in_cafe")
            "You ordered an icecream for yourself. It is very tasty, but it would be more fun if you weren't alone."
            $ hero.gfx_mod_stat("joy", randint(1, 3))
            if dice(20):
                $ hero.disable_effect("Depression")
            if dice(5):
                $ hero.enable_effect("Down with Cold", duration=randint(1, 2))
        else:
            "You do not even have the means to buy yourself an icecream. Maybe it is time to make yourself useful?"
    else:
        # icecream for the team by the inviting_character
        if inviting_character.take_money(randint(10, 25), reason="Icecream"):
            $ hero.set_flag("dnd_ice_in_cafe")
            $ members = hero.team
            if len(members) == 2:
                show expression members[1].get_vnsprite() at center as temp1
                with dissolve
            else:
                show expression members[1].get_vnsprite() at left as temp1
                show expression members[2].get_vnsprite() at right as temp2
                with dissolve
            "You ordered the icecreams and spent some time together."
            $ iam.ice_reward(members, 4 if len(members) == 2 else 3)
            $ del members, inviting_character

            hide temp1
            hide temp2
            with dissolve
            jump city_beach_cafe
        else:
            "You could spend time with your team, but sadly you are too poor to afford it at the moment."

    $ del inviting_character
    $ global_flags.set_flag("keep_playing_music")
    jump city_beach_cafe_main
