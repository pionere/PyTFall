label witches_hut:
    if not "shops" in ilists.world_music:
        $ ilists.world_music["shops"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("shops")]
    if not global_flags.has_flag("keep_playing_music"):
        play world choice(ilists.world_music["shops"]) fadein 1.5

    hide screen forest_entrance

    scene bg witches_hut
    with dissolve

    show expression npcs["Abby_the_witch"].get_vnsprite() as npc
    with dissolve

    $ w = npcs["Abby_the_witch"].say

    if global_flags.flag('visited_witches_hut'):
        w "Welcome back!"
    else:
        $ w = Character("???", color=orange, what_color=yellow, show_two_window=True)
        $ global_flags.set_flag('visited_witches_hut')
        w "New Customer!"
        extend " Welcome to my Potion Shop!"
        w "I am Abby, the Witch, both Cool and Wicked. You'll never know what you run into here!"
        $ w = npcs["Abby_the_witch"].say
        w "Oh, and I also know a few decent {color=[orangered]}Fire{/color} and {color=[lime]}Air{/color} spells if you're interested."
        w "Check out the best home brew in the realm and some other great items in stock!"

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

label witch_menu:
    show screen witch_shop
    with dissolve
    while 1:
        $ result = ui.interact()

label witches_hut_shopping:
    $ gfx_overlay.notify(msg="Sweet!", tkwargs={"style": "interactions_text"})
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.witches_hut
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_8

    $ global_flags.del_flag("keep_playing_music")
    hide screen shopping
    with dissolve
    $ gfx_overlay.notify("Let me know if you need anything else.", tkwargs={"style": "interactions_text"}, duration=1.5)
    $ del shop, focus, item_price, amount, purchasing_dir
    jump witch_menu

label witches_hut_shopping_spells:
    $ gfx_overlay.notify(msg="Sweet!", tkwargs={"style": "interactions_text"})
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.witch_spells_shop
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_9

    $ global_flags.del_flag("keep_playing_music")
    hide screen shopping
    with dissolve
    $ gfx_overlay.notify("Let me know if you need anything else.", tkwargs={"style": "interactions_text"}, duration=1.5)
    $ del shop, focus, item_price, amount, purchasing_dir
    jump witch_menu

label witch_training:
    if not global_flags.has_flag("witches_training_explained"):
        w "I train magic and intelligence."
        w "I can also guarantee that your agility will go up if you pay attention in class!"
        extend " That, however, doesn't happen very often."
        w "And to make me even more awesome, half of your MP will be restored each time you train here!"
        w "Yeap! I am That good!"
        "The training will cost you 250 gold per tier of the trained character every day."
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
                w "I will train magic, intelligence and restore some MP."
                w "I can also guarantee your character will go up if you pay attention in class!"
                extend " That, however, does not often happen for reasons unknown..."
                w "Yeap! I am That good!"
                "The training will cost you 250 gold per tier of the trained character every day."
            "{color=[green]}Setup sessions for [char.name]{/color}" if "Abby Training" not in char.traits:
                $ char.apply_trait(traits["Abby Training"])
                w "I will take [char.npc_training_price] gold per day. Be sure to use my training only on wicked stuff!"
            "{color=[red]}Cancel sessions for [char.name]{/color}" if "Abby Training" in char.traits:
                $ char.remove_trait(traits["Abby Training"])
                w "Maybe next time then?"
            "Pick another character" if len(hero.team) > 1:
                call screen character_pick_screen
                if _return:
                    $ char = _return
            "Do Nothing":
                $ del char
                jump witch_menu

label witch_talking_menu:
    while 1:
        menu:
            w "What do you want?"
            "Abby The Witch Main":
                $ pass
            "Nevermind":
                jump witch_menu
            "Leave the shop":
                jump forest_entrance

screen witch_shop():
    style_prefix "dropdown_gm"
    frame:
        pos (.98, .98) anchor (1.0, 1.0)
        has vbox
        textbutton "Shop":
            action Hide("witch_shop"), Jump("witches_hut_shopping")
        textbutton "Spells":
            action Hide("witch_shop"), Jump("witches_hut_shopping_spells")
        textbutton "Train":
            action Hide("witch_shop"), Jump("witch_training")
        textbutton "Talk":
            action Hide("witch_shop"), Jump("witch_talking_menu")
        textbutton "Leave":
            action Hide("witch_shop"), Jump("forest_entrance")
            keysym "mousedown_3"
