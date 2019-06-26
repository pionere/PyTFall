label tailor_store:

    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("shops", fadein=1.5)
    $ global_flags.del_flag("keep_playing_music")

    hide screen main_street

    scene bg tailor_store
    with dissolve

    $ t = npcs["Kayo_Sudou"].say

    if global_flags.flag('visited_tailor_store'):
        show expression npcs["Kayo_Sudou"].get_vnsprite() as npc
        with dissolve
        t "Welcome back, take a look at our latest arrivals!"
    else:
        $ global_flags.set_flag('visited_tailor_store')

        "You entered the shop. The shelves are filled with colorful silks, and some exquisite dresses are displayed on the mannequins. Noticing your arrival, a tailor lady comes in from the back room and approaches you."

        show expression npcs["Kayo_Sudou"].get_vnsprite() as npc
        with dissolve

        t "Oh, a new customer! Welcome to my store."
        t "I'm honored to present you our wares. All pieces you see were acquired from the most renowned merchants. "
        t "But If you have any special requests, just tell me. I'm sure I will be able to help you."

label tailor_menu: # after she said her lines but before we show menu controls, to return here when needed
    scene bg tailor_store
    show expression npcs["Kayo_Sudou"].get_vnsprite() as npc
    show screen tailor_shop
    with dissolve
    while 1:
        $ result = ui.interact()


label tailor_store_shopping:
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.tailor_store
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_4

    hide screen shopping
    with dissolve
    hide npc

    $ del shop, focus, item_price, amount, purchasing_dir
    jump tailor_menu

screen shopkeeper_items_upgrades(upgrades_list):
    modal True
    fixed:
        xysize(config.screen_width, 43)
        hbox:
            style_group "content"
            align .023, .5
            null width 10
            add "coin_top" yalign .5
            null width 5
            fixed:
                xsize 70
                $ g = gold_text(hero.gold)
                text g size 20 color "gold" yalign .5
 
    frame:
        align (.5, .5)
        background Frame("content/gfx/frame/frame_dec_1.png", 75, 75)
        xpadding 25
        ypadding 25
        xysize (670, 600)

        #button:
        #    xysize (180, 50)
        #    style_prefix "wood"
        #    text "Cancel" size 16 color "goldenrod"
        #    xalign .3
        #    yoffset -40
        #    action Return(-1)
        #    keysym "mouseup_3"
        #hbox:
        #    xalign .7
        #    add "content/gfx/animations/coin_top 0.13 1/1.webp" yalign .6
        #    null width 15
        #    yoffset -40
        #    text "%d" % hero.gold style "proper_stats_value_text" outlines [(1, "#181818", 0, 0)] color "#DAA520" size 30

        viewport id "tailor_orders":
            mousewheel True
            #scrollbars "vertical"
            draggable True
            xysize (650, 540)
            has vbox
            for i in upgrades_list:
                frame:
                    style_prefix "wood"
                    background Frame("content/gfx/frame/cry_box.png", 5, 5)
                    xpadding 10
                    ypadding 10
                    hbox:
                        spacing 0
                        xsize 600
                        xalign .5
                        imagebutton:
                            xsize 100
                            align (.5, .5)
                            action NullAction()
                            idle PyTGFX.scale_content(items[i["first_item"]].icon, 80, 80)
                            tooltip i["first_item"] 
                        hbox:
                            yalign .5
                            style_prefix "proper_stats_value"
                            text "+" color "goldenrod" size 25 
                            hbox:
                                xsize 80
                                $ price = i["price"]
                                text "[price]" color "goldenrod" size 25 xalign 1.0 
                            add "content/gfx/animations/coin_top 0.13 1/1.webp" yalign 1.0 
                            text "  =" color "goldenrod" size 25 
                        imagebutton:
                            xsize 100
                            align (.5, .5)
                            action NullAction()
                            idle PyTGFX.scale_content(items[i["second_item"]].icon, 80, 80)
                            tooltip i["second_item"]
                        button:
                            xysize (100, 50)
                            align (.5, .5)
                            text "Order" size 16 color "goldenrod"
                            action Show("yesno_prompt", message="Are you sure you wish to order a %s for %s Gold?" % (i["second_item"], price), yes_action=[Hide("yesno_prompt"), Return(i)], no_action=Hide("yesno_prompt")) 
                        null height 1
        vbar value YScrollValue("tailor_orders")

        null height 5
        use exit_button(action=Return(None), align=(.5, 1.05))

label tailor_special_order:
    if npcs["Kayo_Sudou"].has_flag("tailor_special_order"):
        if day - npcs["Kayo_Sudou"].flag("tailor_special_order")[0] < 3:
            t "I'm very sorry. Your order is not ready yet. Please come back later."
        else:
            $ item = npcs["Kayo_Sudou"].flag("tailor_special_order")[1]
            t "Yes, your order is ready. *she gives you [item]*"
            $ hero.add_item(item)
            $ del item
            t "Ask anytime if you need anything else!"
            $ npcs["Kayo_Sudou"].del_flag("tailor_special_order")
    else:
        t "For a small price, I can upgrade your clothes to better versions. What would you like to order?"
        $ items_upgrades = load_db_json("items", "upgrades.json")
        $ upgrade_list = list(i for i in items_upgrades if i["location"] == "Tailor")

        $ result = renpy.call_screen("shopkeeper_items_upgrades", upgrade_list)
        $ del upgrade_list, items_upgrades
        if result is None:
            t "If you want anything, please don't hesitate to tell me."
        else:
            if not has_items(result["first_item"], hero, equipped=False):
                t "I'm sorry, you don't have the required base item. Please make sure to unequip it if it's equipped."
            elif hero.take_money(result["price"], reason="Tailor Upgrade"):
                $ hero.remove_item(result["first_item"])
                t "Of course, dear customer, it will be ready in three days. You can retrieve your order in our shop after the time passes."
                $ npcs["Kayo_Sudou"].set_flag("tailor_special_order", value=[day, result["second_item"]])
            else:
                t "I'm sorry, but you don't have that much gold."
    jump tailor_menu

screen tailor_shop():
    #use top_stripe(False)
    style_prefix "dropdown_gm"
    frame:
        pos (.98, .98) anchor (1.0, 1.0)
        has vbox
        textbutton "Shop":
            action Hide("tailor_shop"), Jump("tailor_store_shopping")
        textbutton "Special Order":
            action Hide("tailor_shop"), Jump("tailor_special_order")
        textbutton "Leave":
            action Hide("tailor_shop"), Jump("main_street")
            keysym "mousedown_3"
