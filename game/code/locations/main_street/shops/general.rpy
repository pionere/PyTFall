label general_store:
    scene bg general_store
    with dissolve

    show expression npcs["Yukiko_shop"].get_vnsprite() as npc
    with dissolve

    $ y = npcs["Yukiko_shop"].say
    if pytfall.enter_location("general_store", music=True, env="shops"):
        y "Welcome to PyTFall's General Store!"
        y "Here you can buy all sorts of items!"
        y "Please take a look at our selection:"
    else:
        y "Welcome back!"
    $ del y

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

label general_store_shopping:
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["General Store"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_3

    hide screen shopping
    with dissolve
    hide npc
    $ del shop, focus, item_price, amount, purchasing_dir
    jump main_street
