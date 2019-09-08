label cafe:
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("shops", fadein=1.5)
    $ global_flags.del_flag("keep_playing_music")

    if global_flags.get_flag("waitress_cafe", [-1])[0] != day:
        python hide:
            who = global_flags.get_flag("waitress_ice", [0, None])
            who = getattr(who[1], "id", None)
            who = [w for w in ["Mel_cafe", "Monica_cafe", "Chloe_cafe"] if w != who]
            who = npcs[(choice(who))]
            global_flags.set_flag("waitress_cafe", value=[day, who])

    scene bg cafe
    with dissolve

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    $ waitress = global_flags.flag("waitress_cafe")[1]

    show expression waitress.get_vnsprite() as npc
    with dissolve

    if global_flags.has_flag('visited_cafe'):
        $ iam.greeting_cafe(waitress)
    else:
        $ global_flags.set_flag('visited_cafe')
        waitress.say "Welcome to the Cafe!"
        "Here you can find delicious food and tasty beverages!"

    if not hero.has_flag("dnd_ate_in_cafe"):
        $ inviting_character = iam.would_invite(locked_random("randint", 500, 1000))
        if inviting_character:
            $ iam.eating_propose(inviting_character)
            menu:
                "Do you want to accept [inviting_character.pd] invitation (free of charge)?"
            "Yes":
                jump mc_action_cafe_invitation
            "No":
                $ pass
        $ del inviting_character

label cafe_menu: # after she said her lines but before we show menu controls, to return here when needed
    show expression waitress.get_vnsprite() as npc
    show screen cafe_eating
    while 1:
        $ result = ui.interact()

        hide screen cafe_eating
        if result == "shop":
            jump cafe_shopping
        if result == "eat_alone":
            jump mc_action_cafe_eat_alone_cafe_invitation
        if result == "eat_group":
            jump cafe_eat_group
        $ del waitress, result
        jump main_street

label cafe_shopping:
    python:
        focus = None
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Cafe"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_2

    hide screen shopping
    with dissolve
    $ del shop, focus, item_price, amount, purchasing_dir
    jump cafe_menu

screen cafe_eating():
    #use top_stripe(False)

    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Shop":
            action Return("shop")
        textbutton "Eat alone":
            action Return("eat_alone")
            sensitive not hero.has_flag('dnd_ate_in_cafe')
        textbutton "Eat with group":
            action Return("eat_group")
            sensitive len(hero.team) > 1 and not hero.has_flag('dnd_ate_in_cafe')
        textbutton "Leave":
            action Return("leave")
            keysym "mousedown_3"

label mc_action_cafe_eat_alone_cafe_invitation:
    menu:
        "What will it be?"

        "Light Snack (25 G)":
            if hero.take_money(25, reason="Cafe"):
                $ name = "small_food_%d" % randint(1, 3)
                show image name at truecenter with dissolve
                $ hero.set_flag("dnd_ate_in_cafe")
                "You feel a bit better!"
                $ result_v = randint(4, 10)
                if "Effective Metabolism" in hero.traits:
                    $ result_v *= 2
                $ hero.gfx_mod_stat("vitality", result_v)
                $ hero.gfx_mod_stat("mp", randint(4, 10))
                $ hero.gfx_mod_stat("joy", randint(1, 2))
                $ hero.gfx_mod_exp(exp_reward(hero, hero))
                hide image name with dissolve
                $ del name, result_v
            else:
                "You don't have that amount of gold."

        "Ordinary Meal (50 G)":
            if hero.take_money(50, reason="Cafe"):
                $ name = "medium_food_%d" % randint(1, 3)
                show image name at truecenter with dissolve
                $ hero.set_flag("dnd_ate_in_cafe")
                "You feel quite satisfied."
                $ result_v = randint(8, 15)
                if "Effective Metabolism" in hero.traits:
                    $ result_v *= 2
                $ hero.gfx_mod_stat("vitality", result_v)
                $ hero.gfx_mod_stat("mp", randint(8, 15))
                $ hero.gfx_mod_stat("health", randint(8, 15))
                $ hero.gfx_mod_stat("joy", randint(2, 4))
                $ hero.gfx_mod_exp(exp_reward(hero, hero))
                hide image name with dissolve
                $ del name, result_v
            else:
                "You don't have that amount of gold."
        "Extra Large Meal (200 G)":   # by eating big meals hero can increase max health by 2 with 75% chance; after increasing it by 50 the chance drops to 10% with smaller bonus
            if hero.take_money(200, reason="Cafe"):
                $ name = "big_food_%d" % randint(1, 3)
                show image name at truecenter with dissolve
                $ hero.set_flag("dnd_ate_in_cafe")
                "You feel extremely full and satisfied."
                $ result_v = randint(10, 20)
                if "Effective Metabolism" in hero.traits:
                    $ result_v *= 2
                $ hero.gfx_mod_stat("vitality", result_v)
                $ hero.gfx_mod_stat("mp", randint(10, 20))
                $ hero.gfx_mod_stat("health", randint(10, 20))
                $ hero.gfx_mod_stat("joy", randint(3, 6))
                $ hero.gfx_mod_exp(exp_reward(hero, hero))
                if global_flags.get_flag("health_bonus_from_eating_in_cafe", 0) <= 25 and locked_dice(75):
                    $ hero.stats.mod_raw_max("health", 2)
                    $ hero.gfx_mod_stat("health", 2)
                    $ global_flags.up_counter("health_bonus_from_eating_in_cafe", 2)
                    extend "{color=goldenrod} +2 Max Health{/color}"
                elif global_flags.get_flag("health_bonus_from_eating_in_cafe", 0) < 50 and locked_dice(10): # after 50 successful attempts bonus no longer applies
                    $ hero.stats.mod_raw_max("health", 1)
                    $ hero.gfx_mod_stat("health", 1)
                    $ global_flags.up_counter("health_bonus_from_eating_in_cafe", 1)
                    extend "{color=goldenrod} +1 Max Health{/color}"
                hide image name with dissolve
                $ del name, result_v
            else:
                "You don't have that amount of gold."
        "Nevermind":
            $ pass
    jump cafe_menu

label cafe_eat_group:
    # MC always pays for everyone; an algorithm where we check if every character can and wants to pay and then pays separately is too complex without a good reason
    # instead there will be another event when a character with enough money and disposition invites the group and pays for everything
    if hero.gold < 400:
        "Sadly, you don't have enough money to reserve a table." # MC doesn't even have 400 gold, it's not a good idea to spend money here so we just stop it immediately
        jump cafe_menu
    else:
        $ inviting_character = hero
        jump mc_action_cafe_invitation

label mc_action_cafe_invitation: # we jump here when the group was invited by one of chars
    $ result = randint (60, 80) # base price MC pays for himself and the table
    python:
        for member in hero.team:
            if member != hero:
                if member.status != "free":
                    if member.get_stat("disposition") < -50:
                        result += randint(10, 20) # slaves with negative disposition will afraid to order too much, and also will have low bonuses
                    else:
                        result += randint(40, 90)
                    if "Always Hungry" in member.traits:
                        result += randint(10, 20)
                else:
                    result += randint(50, 100)
                    if "Always Hungry" in member.traits:
                        result += randint(20, 40)
        del member

    if inviting_character.take_money(result, reason="Cafe"):
        $ img = renpy.random.randint(1, 9)
        $ img = "content/gfx/images/food/cafe_mass_%d.webp" % img
        show expression img at truecenter with dissolve
        $ iam.eating_line(hero.team)
        "You enjoy your meals together. Overall health and mood were improved."
        $ hero.set_flag("dnd_ate_in_cafe")
        $ iam.eat_reward(hero.team, 20 if len(hero.team) == 2 else 13)

        hide expression img with dissolve
        $ del img
    $ del result, inviting_character
    jump cafe_menu
