label hiddenvillage_entrance:
    scene bg hiddenvillage_entrance

    $ pytfall.enter_location("village", music=True, env="village", coords=[(.2, .25), (55, .2), (.8, .18)],
                             limited_location=True, goodtraits=["Curious"])

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen hiddenvillage_entrance
    with dissolve # dissolve the whole scene, not just the bg
    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_int(result[1], img=result[1].show("girlmeets", "suburb", exclude=["beach", "winter", "night", "formal", "indoors", "swimsuit"], type="first_default", label_cache=True, gm_mode=True))

        elif result == ['control', 'return']:
            hide screen hiddenvillage_entrance
            jump city


screen hiddenvillage_entrance:
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
        $ img = im.Scale("content/gfx/interface/icons/ninja_shop.png", 70, 70)
        imagebutton:
            pos (300, 315)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("hiddenvillage_entrance"), Jump("hidden_village_shop")]
            tooltip "Ninja Shop"

label hidden_village_shop: # ninja shop logic
    scene bg workshop
    with dissolve

    show expression npcs["Ren_hidden_village"].get_vnsprite() as ren
    with dissolve

    if pytfall.enter_location("ninja_shop", music=True, env="shops"):
        $ r = npcs["Ren_hidden_village"]
        $ tmp = Character("???", color=r.say_style["color"], what_color=r.say_style["what_color"], show_two_window=True)
        tmp "Hm? Ah, I've heard about you."
        extend " Welcome to my Tools Shop."
        $ r = r.say
        r "I'm Ren. We sell ninja stuff here."
        r "If we are interested, I can sell you some leftovers. Of course, it won't be cheap for an outsider like you."
        r "But you won't find these things anywhere else, so it is worth it."
        r "Wanna take a look?"
        $ del r, tmp
    else:
        npcs["Ren_hidden_village"].say "Hey, [hero.name]. Need something?"

    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Ninja Tools Shop"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_5

    hide screen shopping
    with dissolve
    hide ren

    $ del shop, focus, item_price, amount, purchasing_dir
    jump hiddenvillage_entrance
