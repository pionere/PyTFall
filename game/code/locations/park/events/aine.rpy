init python:
    register_event("aine_menu", locations=["city_park"],
        simple_conditions=["hero.get_stat('magic') >= 100"],
        priority=100, start_day=1, jump=True, dice=100, max_runs=1)
    register_gossip("aine_park", "gossip_aine_in_park", dice=80)

label aine_menu:

    $ a = npcs["Aine"].say

    hide screen city_park
    show expression npcs["Aine"].get_vnsprite() as aine:
        pos (.4, .2)
        linear 1.0 pos (.4, .25)
        linear 1.0 pos (.4, .2)
        repeat
    with dissolve

    if not global_flags.flag("met_aine"):
        $ global_flags.set_flag("met_aine")

        a "Well now, a magic practitioner... "
        extend " Hello dear, I am Aine!"

        menu:
            "What are you doing here?":
                a "How Rude! I go wherever I please, and I can take care of myself!"
                a "Not mentioning that this is a really nice place and very few people can see me!"
            "A leprechaun? Here in the park?" if not global_flags.has_flag("met_peevish"):
                a "Yes, why not? This place is as good as anywhere else!"
                a "Or maybe even better. It is not so crowded and a pleasant location for someone like me."
            "I've met someone called Peevish..." if global_flags.has_flag("met_peevish"):
                a "That rude, good for nothing, useless excuse for a brother... well, you don't get to choose family..."

        a "I can teach you {color=lightblue}Ice{/color} and {color=yellow}Electricity{/color} spells if you're interested,"
        extend " it will cost you, but you'll never have to hear a word about no pile of gold from me."

        $ pytfall.shops_stores["Aine Shop"].visible = True
        $ stop_gossip("aine_park")
    else:
        a "Hello again. How are you today?"

label aine_menu_return:
    show screen aine_screen
    with dissolve
    while 1:
        $ result = ui.interact()

        hide screen aine_screen
        if result == "shop":
            jump aine_shop
        elif result == "training":
            jump aine_training
        else:
            a "Good luck!"
            hide aine with dissolve
            $ del a
            jump city_park

label aine_shop:
    a "Of course!"
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Aine Shop"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_10

    hide screen shopping
    with dissolve
    a " Come back with more gold!"
    $ del shop, focus, item_price, amount, purchasing_dir, char
    jump aine_menu_return

label aine_training:
    if not global_flags.has_flag("aine_training_explained"):
        call about_aine_personal_training from _call_about_aine_personal_training
        $ global_flags.set_flag("aine_training_explained")
    else:
        a "Let's see what I can do, dear."

    if len(hero.team) > 1:
        call screen character_pick_screen
        $ char = _return
    else:
        $ char = hero

    if not char:
        $ del char
        jump aine_menu_return

    while 1:
        menu:
            "About training sessions":
                call about_personal_training(a) from _call_about_personal_training_2
            "About Aine training":
                call about_aine_personal_training from _call_about_aine_personal_training_1
            "{color=green}Setup sessions for [char.name]{/color}" if "Aine Training" not in char.traits:
                $ char.apply_trait(traits["Aine Training"])
                a "It will require [char.npc_training_price] gold per day. Don't you dare misuse skills you've learned here!"
            "{color=red}Cancel sessions for [char.name]{/color}" if "Aine Training" in char.traits:
                $ char.remove_trait(traits["Aine Training"])
                a "Fair enough."
            "Pick another character" if len(hero.team) > 1:
                call screen character_pick_screen
                if _return:
                    $ char = _return
            "Do Nothing":
                $ del char
                jump aine_menu_return

label about_personal_training(speaker):
    speaker "You can arrange for daily training sessions!"
    speaker "It will cost you One AP and {color=gold}[char.npc_training_price] Gold{/color}."
    speaker "Price will increase as you level up. Feel free to ask me about this any time!"
    speaker "Training will be automatically terminated if you lack the gold to continue."
    speaker "Sessions can be arranged with multiple trainers on the same day. But you'll be running a risk of not leaving Action Points to do anything else."
    return

label about_aine_personal_training:
    a "Well dear, I can teach you manners and proper care so as to increase your charisma."
    a "Being taught by a leprechaun Princess has its perks!"
    a "Your vitality will be boosted, plus your fame and reputation may also increase."
    extend " Due to my magical nature, there is a tiny chance that you will get luckier in your life endeavors!!!"
    a "That I dare say is a truly rare feat!"
    "The training will cost you 250 gold per tier of the trained character every day."
    return

screen aine_screen():
    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Spells":
            action Return("shop")
        textbutton "Training":
            action Return("training")
        textbutton "Leave":
            action Return("leave")
            keysym "mousedown_3"
