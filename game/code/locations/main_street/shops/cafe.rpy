label cafe:
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("shops", fadein=1.5)

    hide screen main_street

    scene bg cafe
    with dissolve
    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    if global_flags.flag("waitress_chosen_today") != day:
        $ cafe_waitress_who = npcs[(choice(["Mel_cafe", "Monica_cafe", "Chloe_cafe"]))]
        $ global_flags.set_flag("waitress_chosen_today", value=day)

    $ w = cafe_waitress_who.say

    show expression cafe_waitress_who.get_vnsprite() as npc
    with dissolve

    if global_flags.flag('visited_cafe'):
        w "Welcome back! Do you want a table?"
    else:
        $ global_flags.set_flag('visited_cafe')
        $ hero.set_flag("health_bonus_from_eating_in_cafe", value=0)
        w "Welcome to the Cafe!"
        "Here you can find delicious food and tasty beverages!"
    $ del w
    $ inviting_character = hero

    if len(hero.team) > 1 and not hero.has_flag("dnd_ate_in_cafe"):
        python hide:
            global inviting_character
            members = [] # all chars willing to invite will be in this list
            for member in hero.team:
                if member != hero:
                    if member.status == "free" and member.gold >= locked_random("randint", 500, 1000) and (member.get_stat("disposition") >= 200 or member.get_stat("affection") >= 200) and member.get_stat("joy") >= 30:
                        # the chance for a member of MC team to invite team
                        if "Imouto" in member.traits:
                            chance = 60
                        elif "Kamidere" in member.traits:
                            chance = 55
                        elif "Yandere" in member.traits:
                            chance = 50
                        elif "Ane" in member.traits:
                            chance = 45
                        elif "Bokukko" in member.traits:
                            chance = 40
                        elif "Tsundere" in member.traits:
                            chance = 30
                        elif "Kuudere" in member.traits:
                            chance = 20
                        elif "Dandere" in member.traits:
                            chance = 10
                        elif "Impersonal" in member.traits:
                            chance = 5
                        else:
                            chance = 35
                        if dice(chance):
                            members.append(member)
            if members:
                inviting_character = random.choice(members)
                interactions_eating_propose(inviting_character)

    if inviting_character != hero:
        menu:
            "Do you want to accept [inviting_character.pp] invitation (free of charge)?"
            "Yes":
                jump mc_action_cafe_invitation
            "No":
                $ pass
    $ del inviting_character

label cafe_menu: # after she said her lines but before we show menu controls, to return here when needed
    scene bg cafe
    show expression cafe_waitress_who.get_vnsprite() as npc
    show screen cafe_eating
    while 1:
        $ result = ui.interact()

label cafe_shopping:
    python:
        focus = None
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.cafe
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_2

    $ global_flags.del_flag("keep_playing_music")
    hide screen shopping
    with dissolve
    $ del shop, focus, item_price, amount, purchasing_dir
    jump cafe_menu

screen cafe_eating():
    #use top_stripe(False)

    style_prefix "dropdown_gm"
    
    frame:
        pos (.98, .98) anchor (1.0, 1.0)
        has vbox
        textbutton "Shop":
            action [Hide("cafe_eating"), Jump("cafe_shopping")]

        textbutton "Eat alone":
            sensitive not hero.has_flag("dnd_ate_in_cafe")
            action [Hide("cafe_eating"), Jump("mc_action_cafe_eat_alone_cafe_invitation")]

        textbutton "Eat with group":
            sensitive len(hero.team)>1 and not hero.has_flag("dnd_ate_in_cafe")
            action [Hide("cafe_eating"), Jump("cafe_eat_group")]

        textbutton "Leave":
            action [Hide("cafe_eating"), Jump("main_street")]
            keysym "mousedown_3"

label mc_action_cafe_eat_alone_cafe_invitation:
    menu:
        "What will it be?"

        "Light Snack (10 G)":
            if hero.take_money(10, reason="Cafe"):
                $ name = "small_food_" + str(renpy.random.randint(1, 3))
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

        "Ordinary Meal (25 G)":
            if hero.take_money(25, reason="Cafe"):
                $ name = "medium_food_" + str(renpy.random.randint(1, 3))
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
        "Extra Large Meal (50 G)":   # by eating big meals hero can increase max health by 2 with 75% chance; after increasing it by 50 the chance drops to 10% with smaller bonus
            if hero.take_money(50, reason="Cafe"):
                $ name = "big_food_" + str(renpy.random.randint(1, 3))
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
                if hero.flag("health_bonus_from_eating_in_cafe") <= 25 and locked_dice(75):
                    $ hero.stats.mod_raw_max("health", 2)
                    $ hero.gfx_mod_stat("health", 2)
                    $ hero.up_counter("health_bonus_from_eating_in_cafe", 2)
                    extend "{color=goldenrod} +2 Max Health{/color}"
                elif hero.flag("health_bonus_from_eating_in_cafe") <= 50 and locked_dice(10): # after 50 successful attempts bonus no longer applies
                    $ hero.stats.mod_raw_max("health", 1)
                    $ hero.gfx_mod_stat("health", 1)
                    $ hero.up_counter("health_bonus_from_eating_in_cafe", 1)
                    extend "{color=goldenrod} +1 Max Health{/color}"
                hide image name with dissolve
                $ del name, result_v
            else:
                "You don't have that amount of gold."
    jump cafe_menu

label cafe_eat_group:
    # MC always pays for everyone; an algorithm where we check if every character can and wants to pay and then pays separately is too complex without a good reason
    # instead there will be another event when a character with enough money and disposition invites the group and pays for everything
    if hero.gold < 200:
        "Sadly, you don't have enough money to reserve a table." # MC doesn't even have 200 gold, it's not a good idea to spend money here so we just stop it immediately
        jump cafe_menu
    else:
        $ inviting_character = hero
        jump mc_action_cafe_invitation

label mc_action_cafe_invitation: # we jump here when the group was invited by one of chars
    $ result = randint (30, 40) # base price MC pays for himself and the table
    python:
        for member in hero.team:
            if member != hero:
                if member.status != "free":
                    if member.get_stat("disposition") < -50:
                        result += randint(5, 10) # slaves with negative disposition will afraid to order too much, and also will have low bonuses
                    else:
                        result += randint(20, 45)
                    if "Always Hungry" in member.traits:
                        result += randint(5, 10)
                else:
                    result += randint(25, 50)
                    if "Always Hungry" in member.traits:
                        result += randint(10, 20)
        del member

    if inviting_character.take_money(result, reason="Cafe"):
        $ img = renpy.random.randint(1, 9)
        $ img = "content/gfx/images/food/cafe_mass_%d.webp" % img
        show expression img at truecenter with dissolve
        $ interactions_eating_line(hero.team)
        "You enjoy your meals together. Overall health and mood were improved."
        $ hero.set_flag("dnd_ate_in_cafe")
        python hide:
            for member in hero.team:
                if member.status != "free" and member.get_stat("disposition") < -50:
                    d = .5
                else:
                    d = 1
                stat = int(randint(5, 10)*d)
                if "Effective Metabolism" in member.traits:
                    stat *= 2
                member.gfx_mod_stat("vitality", stat)
                stat = int(randint(5, 10)*d)
                member.gfx_mod_stat("health", stat)
                stat = int(randint(5, 10)*d)
                member.gfx_mod_stat("mp", stat)
                stat = int(randint(4, 8)*d)
                member.gfx_mod_stat("joy", stat)
                if member != hero:
                    stat = int(randint(10, 20)*d)
                    if len(hero.team)<3: # when there is only one char, disposition bonus is higher
                        stat += randint(5, 10)
                    member.gfx_mod_stat("disposition", stat)
                    member.gfx_mod_stat("affection", affection_reward(member))

        hide expression img with dissolve
        $ del img
    $ del result, inviting_character
    jump cafe_menu
