label city_beach_cafe_main:
    $ iam.enter_location(goodtraits=["Athletic", "Dawdler", "Always Hungry"], badtraits=["Scars", "Undead", "Furry", "Monster"],
                        coords=[[.15, .75], [.65, .62], [.9, .8]])
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("beach_cafe")
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("city_beach_cafe_main"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    scene bg city_beach_cafe_main
    with dissolve
    show screen city_beach_cafe_main

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    if global_flags.get_flag("waitress_ice", [-1])[0] != day:
        python hide:
            who = global_flags.get_flag("waitress_cafe", [0, None])
            who = getattr(who[1], "id", None)
            who = [w for w in ["Mel_cafe", "Monica_cafe", "Chloe_cafe"] if w != who]
            who = npcs[(choice(who))]
            global_flags.set_flag("waitress_ice", value=[day, who])

    if not hero.has_flag("dnd_ice_in_cafe"):
        $ inviting_character = iam.would_invite(locked_random("randint", 100, 200))
        if inviting_character != hero:
            $ iam.icecream_propose(inviting_character)
            menu:
                "Do you want to accept [inviting_character.pd] invitation (free of charge)?"
                "Yes":
                    jump mc_action_ice_invitation
                "No":
                    $ pass
        $ del inviting_character

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            python hide:
                char = result[1]
                tags = char.get_tags_from_cache(last_label)
                if not tags:
                    img_tags = (["girlmeets", "beach"], ["girlmeets", "swimsuit", "simple bg"], ["girlmeets", "swimsuit", "no bg"], ["girlmeets", "swimsuit", "outdoors"])
                    tags = get_simple_act(char, img_tags)
                    if not tags:
                        img_tags = (["girlmeets", "simple bg"], ["girlmeets", "no bg"])
                        tags = get_simple_act(char, img_tags)
                        if not tags:
                            # giveup
                            tags = ["girlmeets", "swimsuit"]
                iam.start_gm(char, img=char.show(*tags, type="reduce", label_cache=True, gm_mode=True))

        elif result[0] == 'control':
            if result[1] == 'return':
                hide screen city_beach_cafe_main
                jump city_beach_left


screen city_beach_cafe_main:
    use top_stripe(True)
    use location_actions("city_beach_cafe_main")

    if iam.show_girls:
        key "mousedown_3" action ToggleField(iam, "show_girls")

        add "content/gfx/images/bg_gradient.webp" yalign .45

        for entry, pos in zip(iam.display_girls(), iam.coords):
            hbox:
                align pos
                use rg_lightbutton(return_value=['jump', entry])

    else:
        $ img = im.Scale("content/gfx/interface/icons/beach_ice.png", 80, 80)
        imagebutton:
            pos (642, 390)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach_cafe"), Jump("mc_action_city_beach_ice")]
            tooltip "Ice Cream"

        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
        imagebutton:
            align (.01, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach_cafe_main"), Function(global_flags.del_flag, "keep_playing_music"), Jump("city_beach_cafe")]

        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow_up.png", 90, 60), vertical=True)
        imagebutton:
            align (.5, .99)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach_cafe_main"), Jump("city_beach_left")]

label mc_action_city_beach_ice:
    if hero.has_flag("dnd_ice_in_cafe"):
        "You already had an icecream today. Too much of it, and a cold is guaranteed."
        jump city_beach_cafe_main

    $ waitress = global_flags.flag("waitress_ice")[1]

    hide screen city_beach_cafe_main

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
        jump city_beach_cafe_main

screen city_beach_ice_stand:
    style_prefix "dropdown_gm"

    add im.Scale("content/gfx/images/ice_stand.webp", config.screen_width, config.screen_height) # align .5, .5

    frame:
        pos (.98, .98) anchor (1.0, 1.0)
        has vbox

        textbutton "Eat an icecream alone":
            action Return("ice_alone")

        textbutton "Icecream for the team":
            sensitive len(hero.team) > 1
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
            $ hero.gfx_mod_stat("joy", randint(2, 4))
            if dice(20):
                $ hero.disable_effect("Depression")
            if dice(5):
                $ hero.enable_effect("Down with Cold", duration=randint(1, 2))
        else:
            $ narrator("You do not even have the means to buy yourself an icecream. Maybe it is time to make yourself useful?")
    else:
        # icecream for the team by the inviting_character
        if inviting_character.take_money(randint(10, 25), reason="Icecream"):
            $ hero.set_flag("dnd_ice_in_cafe")
            $ members = list(member for member in hero.team if (member != hero))
            if len(members) == 1:
                show expression members[0].get_vnsprite() at center as temp1
                with dissolve
            else:
                show expression members[0].get_vnsprite() at center_left as temp1
                show expression members[1].get_vnsprite() at center_right as temp2
                with dissolve
            "You ordered the icecreams and spent some time together."
            python:
                for member in hero.team:
                    member.gfx_mod_stat("joy", randint(3, 5))
                    if dice(20):
                        member.disable_effect("Depression")
                    if dice(5):
                        member.enable_effect("Down with Cold", duration=randint(1, 2))
                    if member != hero:
                        member.gfx_mod_stat("disposition", randint(3, 5))
                        member.gfx_mod_stat("affection", affection_reward(member))
                del member, members
            hide temp1
            hide temp2
            with dissolve
            $ del inviting_character
            jump city_beach_cafe
        else:
            "You could spend time with your team, but sadly you are too poor to afford it at the moment."

    $ del inviting_character
    jump city_beach_cafe_main
