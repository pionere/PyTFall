label general_store:
    # Music related:
    if not "shops" in ilists.world_music:
        $ ilists.world_music["shops"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("shops")]
    if not global_flags.has_flag("keep_playing_music"):
        play world choice(ilists.world_music["shops"]) fadein 1.5

    hide screen main_street

    scene bg general_store
    with dissolve
    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show expression npcs["Yukiko_shop"].get_vnsprite() as npc
    with dissolve
    $ y = npcs["Yukiko_shop"].say

    if global_flags.flag('visited_general_store'):
        y "Welcome back!"
    else:
        $ global_flags.set_flag('visited_general_store')
        y "Welcome to PyTFall's General Store!"
        y "Here you can buy all sorts of items!"
        y "Please take a look at our selection: "

label general_store_shopping:

    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.general_store
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_3

    $ global_flags.del_flag("keep_playing_music")
    hide screen shopping
    with dissolve
    hide npc
    $ del shop, focus, item_price, amount, purchasing_dir
    jump main_street
