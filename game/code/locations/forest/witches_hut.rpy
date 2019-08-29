label witches_hut:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("shops", fadein=1.5)
    $ global_flags.del_flag("keep_playing_music")

    scene bg witches_hut
    with dissolve

    show expression npcs["Abby_the_witch"].get_vnsprite() as npc
    with dissolve

    if global_flags.has_flag('visited_witches_hut'):
        $ w = npcs["Abby_the_witch"].say
        w "Welcome back!"
    else:
        $ w = npcs["Abby_the_witch"]
        $ w = Character("???", color=w.say_style["color"], what_color=w.say_style["what_color"], show_two_window=True)
        $ global_flags.set_flag('visited_witches_hut')
        w "New Customer!"
        extend " Welcome to my Potion Shop!"
        w "I am Abby, the Witch, both Cool and Wicked. You'll never know what you run into here!"
        $ w = npcs["Abby_the_witch"].say
        $ temp = BE_Core.TYPE_TO_COLOR_MAP
        $ temp = "%s and %s" % (set_font_color("Fire", temp["fire"]), set_font_color("Air", temp["air"])) 
        w "Oh, and I also know a few decent [temp] spells if you're interested."
        w "Check out the best home brew in the realm and some other great items in stock!"
        $ del temp

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

label witch_menu:
    show screen witch_shop
    with dissolve
    while 1:
        $ result = ui.interact()

        hide screen witch_shop
        if result == "shop":
            jump witches_hut_shopping
        elif result == "spells":
            jump witches_hut_shopping_spells
        elif result == "train":
            jump witch_training
        elif result == "talk":
            jump witch_talking_menu
        else:
            $ del result
            jump witches_hut_exit

label witches_hut_shopping:
    $ gfx_overlay.notify(msg="Sweet!", tkwargs={"style": "interactions_text"})
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Witches Hut"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_8

    hide screen shopping
    with dissolve
    $ gfx_overlay.notify("Let me know if you need anything else.", tkwargs={"style": "interactions_text"}, duration=1.5)
    $ del shop, focus, item_price, amount, purchasing_dir, char
    jump witch_menu

label witches_hut_shopping_spells:
    $ gfx_overlay.notify(msg="Sweet!", tkwargs={"style": "interactions_text"})
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Witch Spells Shop"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_9

    hide screen shopping
    with dissolve
    $ gfx_overlay.notify("Let me know if you need anything else.", tkwargs={"style": "interactions_text"}, duration=1.5)
    $ del shop, focus, item_price, amount, purchasing_dir, char
    jump witch_menu

label witch_training:
    if not global_flags.has_flag("witches_training_explained"):
        call about_abby_personal_training from _call_about_abby_personal_training
        $ global_flags.set_flag("witches_training_explained")
    else:
        w "You know the deal!"

    if len(hero.team) > 1:
        call screen character_pick_screen
        $ char = _return
    else:
        $ char = hero

    if not char:
        $ del char
        jump witch_menu

    while 1:
        menu:
            "About training sessions":
                call about_personal_training(w) from _call_about_personal_training_1
            "About Abby training":
                call about_abby_personal_training from _call_about_abby_personal_training_1
            "{color=green}Setup sessions for [char.name]{/color}" if "Abby Training" not in char.traits:
                $ char.apply_trait(traits["Abby Training"])
                w "I will take [char.npc_training_price] gold per day. Be sure to use my training only on wicked stuff!"
            "{color=red}Cancel sessions for [char.name]{/color}" if "Abby Training" in char.traits:
                $ char.remove_trait(traits["Abby Training"])
                w "Maybe next time then?"
            "Pick another character" if len(hero.team) > 1:
                call screen character_pick_screen
                if _return:
                    $ char = _return
            "Do Nothing":
                $ del char
                jump witch_menu

label about_abby_personal_training:
    w "With me you can learn about magic."
    w "I can also guarantee that your character will go up if you pay attention in class!"
    extend " That, however, doesn't happen very often."
    w "But your agility might increase naturally while you are handling the ingredients."
    w "Since the training room is full of magic clouds, it is inevitable that part of your MP will be restored as well."
    "The training will cost you 250 gold per tier of the trained character every day."
    return

label witch_talking_menu:
    while 1:
        menu:
            w "What do you want?"
            "Abby The Witch Main":
                $ pass
            "Nevermind":
                jump witch_menu
            "Leave the shop":
                jump witches_hut_exit

screen witch_shop():
    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Shop":
            action Return("shop")
        textbutton "Spells":
            action Return("spells")
        textbutton "Train":
            action Return("train")
        textbutton "Talk":
            action Return("talk")
        textbutton "Leave":
            action Return("leave")
            keysym "mousedown_3"

label witches_hut_exit:
    $ del w
    jump forest_entrance
