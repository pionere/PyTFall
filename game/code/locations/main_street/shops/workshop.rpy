label workshop:
    scene bg workshop
    with dissolve

    show expression npcs["Katia_workshop"].get_vnsprite() as katia
    with dissolve

    if pytfall.enter_location("workshop", music=True, env="workshop"):
        $ k = npcs["Katia_workshop"].say
        k "Welcome to PyTFall's Workshop!"
        k "The best place to go for Weapons and Armor!"
        k "Please take a look at our selection:"
        $ del k
    else:
        $ iam.comment_line(npcs["Katia_workshop"], "Welcome back!")

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

label workshop_shopping:
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Work Shop"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control

    hide screen shopping
    with dissolve
    hide katia
    $ del shop, focus, item_price, amount, purchasing_dir
    jump main_street
