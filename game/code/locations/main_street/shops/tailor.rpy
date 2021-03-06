label tailor_store:
    scene bg tailor_store
    with dissolve

    $ t = npcs["Kayo_Sudou"].say
    if pytfall.enter_location("tailor_store", music=True, env="shops"):
        "You enter the shop. The shelves are filled with colorful silks, and some exquisite dresses are displayed on the mannequins. Noticing your arrival, a tailor lady comes in from the back room and approaches you."

        show expression npcs["Kayo_Sudou"].get_vnsprite() as npc
        with dissolve

        t "Oh, a new customer! Welcome to my store."
        t "I'm honored to present you our wares. All pieces you see were acquired from the most renowned merchants. "
        t "But If you have any special requests, just tell me. I'm sure I will be able to help you."
    else:
        show expression npcs["Kayo_Sudou"].get_vnsprite() as npc
        with dissolve
        $ iam.comment_line(npcs["Kayo_Sudou"], "Welcome back, take a look at our latest arrivals!")

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

label tailor_menu: # after she said her lines but before we show menu controls, to return here when needed
    show screen tailor_shop
    with dissolve
    while 1:
        $ result = ui.interact()

        hide screen tailor_shop
        if result == "shop":
            jump tailor_store_shopping
        elif result == "order":
            jump tailor_special_order
        elif result == "show":
            jump fashion_show
        else:
            hide npc
            $ del t, result
            jump main_street

label tailor_store_shopping:
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Tailor Store"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_4

    hide screen shopping
    with dissolve

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
        use exit_button(action=Return(False), align=(.5, 1.05))

label tailor_special_order:
    if global_flags.has_flag("tailor_special_order"):
        if day - global_flags.flag("tailor_special_order")[0] < 3:
            t "I'm very sorry. Your order is not ready yet. Please come back later."
        else:
            $ item = global_flags.flag("tailor_special_order")[1]
            t "Yes, your order is ready. *she gives you [item]*"
            t "Ask anytime if you need anything else!"
            $ hero.add_item(item)
            $ del item
            $ global_flags.del_flag("tailor_special_order")
    else:
        t "For a small price, I can upgrade your clothes to better versions. What would you like to order?"
        $ items_upgrades = load_db_json("items", "data", "upgrades.json")
        $ upgrade_list = list(i for i in items_upgrades if i["location"] == "Tailor")

        $ result = renpy.call_screen("shopkeeper_items_upgrades", upgrade_list)
        $ del upgrade_list, items_upgrades
        if result is False:
            t "If you want anything, please don't hesitate to tell me."
        else:
            if not has_items(result["first_item"], hero, equipped=False):
                t "I'm sorry, you don't have the required base item. Please make sure to unequip it if it's equipped."
            elif hero.take_money(result["price"], reason="Tailor Upgrade"):
                $ hero.remove_item(result["first_item"])
                t "Of course, dear customer, it will be ready in three days. You can retrieve your order in our shop after the time passes."
                $ global_flags.set_flag("tailor_special_order", value=[day, result["second_item"]])
            else:
                t "I'm sorry, but you don't have that much gold."
    jump tailor_menu

screen tailor_shop():
    #use top_stripe(False)

    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Shop":
            action Return("shop")
        textbutton "Special Order":
            action Return("order")
        textbutton "Leave":
            action Return("leave")
            keysym "mousedown_3"

    if global_flags.flag("know_fashion_show"):
        $ img = im.Scale("content/gfx/interface/icons/fashion_show.png", 50, 50)
        imagebutton:
            pos 910, 110
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return("show")
            tooltip "Fashion Show"