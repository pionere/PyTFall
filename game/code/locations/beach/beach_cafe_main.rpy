label city_beach_cafe_main:
    scene bg city_beach_cafe_main

    $ pytfall.enter_location("beach_cafe", music=True, env="beach_cafe", coords=[(.15, .75), (.65, .62), (.9, .8)],
                             goodtraits=["Athletic", "Dawdler", "Always Hungry"], badtraits=["Scars", "Undead", "Furry", "Monster"])

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
    with dissolve # dissolve the whole scene, not just the bg
    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            python hide:
                char = result[1]
                iam.start_int(char, img=iam.select_beach_img_tags(char, "beach_cafe"))

        elif result[0] == "control":
            hide screen city_beach_cafe_main
            if result[1] == "return":
                jump city_beach_left
            elif result[1] == "left":
                jump city_beach_cafe
            elif result[1] == "return":
                jump mc_action_city_beach_ice


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
            action Return(["control", "ice"])
            tooltip "Ice Cream"

        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80), horizontal=True)
        imagebutton:
            align (.01, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "left"])

        $ img = im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow_up.png", 90, 60), vertical=True)
        imagebutton:
            align (.5, .99)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "return"])

label mc_action_city_beach_ice:
    if hero.has_flag("dnd_ice_in_cafe"):
        "You already had an icecream today. Too much of it, and a cold is guaranteed."
        jump city_beach_cafe_main

    scene bg icestand
    show expression pytfall.shops_stores["Cafe"].server.get_vnsprite() as npc at truecenter
    show screen city_beach_ice_stand

    if global_flags.flag('visited_ice'):
        pytfall.shops_stores["Cafe"].server.say "Welcome back! What can I have you today?"
    else:
        $ global_flags.set_flag('visited_ice')
        pytfall.shops_stores["Cafe"].server.say "Welcome to the finest Ice Cream stand in the city!"

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
    jump city_beach_cafe_main
