init python:
    register_event("peevish_meeting", locations=["forest_entrance"], simple_conditions=["hero.get_stat('magic') >= 50"],  priority=500, start_day=1, jump=True, dice=100, max_runs=1)
    register_gossip("peevish_forest", "gossip_peevish_in_forest", dice=100)

label peevish_meeting:
    $ pytfall.enter_location("peevish", music=False, env=None)

    $ p = Character("???", color="lawngreen", what_color="lawngreen", show_two_window=True)

    hide screen forest_entrance
    with dissolve

    show bg forest_entrance:
        size (config.screen_width, config.screen_height)
        crop (0, 0, config.screen_width, config.screen_height)
        easein 4.0 crop (100, 100, config.screen_width/4, 200)

    play sound "content/sfx/sound/events/get.mp3" fadein 1.0

    $ renpy.pause(5.0, hard=True)

    show expression npcs["Peevish"].get_vnsprite() as peevish
    with dissolve

    play music "content/sfx/music/events/irish.mp3" fadein 2.0
    # with vpunch
    p "Hello dumbass!"
    p "Wow. Can you see me? There aren't many who can!"
    extend " Like that old crone living up that damn hobbit hole..."

    p "I am the great and powerful Peevish McSpud!"

    $ p = npcs["Peevish"].say

    menu:
        "Old crone? That witch looks young and kinda hot?":
            p "Haha! Shows how much you know!"
            p "Let me get down from here."
        "Hey! Are you the midget who lives up in a tree?":
            p "Amn't!"
            p "I am a genuine leprechaun!"
            extend " Well... almost. I wish that I had that damn pile of gold under the rainbow..."
            p "But the rest of me is 100%% you mother-frecker! Just wait till I come down there!" #not swearing on purpose?

    hide peevish
    hide bg forest_entrance

    stop music fadeout 1.0

    show bg forest_entrance
    with dissolve

    show expression npcs["Peevish"].get_vnsprite() as peevish:
        pos (.4, .2)
        linear 1.0 pos (.4, .25)
        linear 1.0 pos (.4, .2)
        repeat
    with dissolve

    $ temp = BE_Core.TYPE_TO_COLOR_MAP
    $ temp = "%s and %s" % (set_font_color("Earth", temp["earth"]), set_font_color("Water", temp["water"])) 

    p "Haha, you're a lot uglier from this angle!"
    p "But you're in luck today! Since you can see me, you aren't entirely hopeless..."
    extend " and I just happen to teach [temp] magic!"
    p "Normally I wouldn't bother with a shitty pipsqueak like you, but my greatness requires a good pile of {color=gold}gold{/color} to become a real genuine and authentic leprechaun."
    p "I could use a rainbow too..."
    p "Well, don't expect it to be cheap!"
    extend " Talk to me when you have some G's on you!"

    $ pytfall.shops_stores["Peevish Shop"].visible = True 
    $ del p, temp
    $ stop_gossip("peevish_forest")
    jump forest_entrance

label peevish_menu:
    $ p = npcs["Peevish"].say

    #hide screen forest_entrance
    show expression npcs["Peevish"].get_vnsprite() as peevish:
        pos (.4, .2)
        linear 1.0 pos (.4, .25)
        linear 1.0 pos (.4, .2)
        repeat
    with dissolve

    p "Haha, look who's back!"
    p "Got some gold on ya?"

    p "Well? What do you want?"
    python:
        focus = False
        item_price = 0
        amount = 1
        purchasing_dir = None
        shop = pytfall.shops_stores["Peevish Shop"]
        char = hero
        char.inventory.set_page_size(18)

    show screen shopping(left_ref=hero, right_ref=shop)
    with dissolve

    call shop_control from _call_shop_control_7

    hide screen shopping
    with dissolve
    $ del shop, focus, item_price, amount, purchasing_dir, char
    p "Come back when you have more {color=gold}gold{/color}!"
    if not (global_flags.has_flag("revealed_aine_location") or global_flags.has_flag("visited_aine")):
        p "Oh! Before I forget!"
        p "I have a goodie, goodie sis that usually hangs around the park area. She is magical too so you might not be able to see her until you train up a bit..."
        p "Sure wish you weren't such a wuss..."
        extend " Now you can get the hell out of here!"
        $ global_flags.set_flag("revealed_aine_location")
    hide peevish with dissolve
    $ del p
    jump forest_entrance
