label workshop:

    # Music related:
    if not "shops" in ilists.world_music:
        $ ilists.world_music["shops"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("shops")]
    if not global_flags.has_flag("keep_playing_music"):
        play world choice(ilists.world_music["shops"]) fadein 1.5

    hide screen main_street

    scene bg workshop
    with dissolve
    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show expression npcs["Katia_workshop"].get_vnsprite() as katia
    with dissolve
    $ k = npcs["Katia_workshop"].say

    if global_flags.flag('visited_workshop'):
        "Welcome back!"
    else:
        $ global_flags.set_flag('visited_workshop')
        k "Welcome to PyTFall's Workshop!"
        k "The best place to go for Weapons and Armor!"
        k "Please take a look at our selection: "

label workshop_shopping:

    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.workshop
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control

    $ global_flags.del_flag("keep_playing_music")
    hide screen shopping
    with dissolve
    hide katia
    $ del shop, focus, item_price, amount, purchasing_dir
    jump main_street
