init:
    transform blueprint_position:
        align (0.5, 0.6)
init python:
    def eyewarp(x):
        return x**1.33

label storyi_start: # beginning point of the dungeon;
    python:
        sflash = Fade(.25, 0, .25, color="darkred")
        q_dissolve = Dissolve(.2) # fast dissolve to quickly show backgrounds

        eye_open = ImageDissolve("content/gfx/masks/eye_blink.webp", 0.5, ramplen=128, reverse=False, time_warp=eyewarp) # transitions for backgrounds, try to emulate effect of opening or closing eyes
        eye_shut = ImageDissolve("content/gfx/masks/eye_blink.webp", 0.5, ramplen=128, reverse=True, time_warp=eyewarp)

        map_scroll = PyTGFX.scale_img("content/events/StoryI/scroll.webp", 900, 900)
        blueprint = PyTGFX.scale_img("content/events/StoryI/blueprint.webp", 660, 540)
        point = "content/gfx/interface/icons/move15.png" # the point which shows location on the map; it's actually a part of the main gui

        #enemy_soldier = Character("Guard", color="white", what_color="white", show_two_window=True, show_side_image=PyTGFX.scale_img("content/mobs/ct1.png", 120, 120))
        #enemy_soldier2 = Character("Guard", color="white", what_color="white", show_two_window=True, show_side_image=PyTGFX.scale_img("content/mobs/h1.png", 120, 120))

        fight_chance = 100

        storyi_data = "code/story/prison_break/coordinates_1.json"
        with open(renpy.loader.transfn(storyi_data)) as f:
            storyi_data = json.load(f)
        storyi_loc_map = dict([(i["id"], i) for i in storyi_data])

        # create/update a map of id-day pairs to store the last search day at the given location
        storyi_treasures = global_flags.get_flag("storyi_treasures", {})
        for i in storyi_data:
            if i.get("items", False):
                i = i["id"]
                if i not in storyi_treasures:
                    storyi_treasures[i] = -1
            else:
                storyi_treasures.pop(i["id"], None)
        global_flags.set_flag("storyi_treasures", storyi_treasures)
        del i, f

        storyi_prison_location = "Dung"
        controlled_exit = False

    stop music
    stop world fadeout 2.0
    scene black with dissolve
    # show expression Text("Some time later", style="TisaOTM", align=(0.5, 0.33), size=40) as txt1:
        # alpha 0
        # linear 3.5 alpha 1.0
    # pause 2.5
    # hide txt1
    play world "Theme2.ogg" fadein 2.0 loop
    show bg story d_entrance with eye_open
    if not global_flags.has_flag("been_in_old_ruins"):
        $ global_flags.set_flag("been_in_old_ruins")
        hero.say "I've found the ruins of a tower near the city."
        hero.say "It may be not safe here, but I bet there is something valuable deep inside!"
        "You can enter and exit the ruins at any point, but it will consume your AP."

label storyi_gui_loop: # the gui loop; we jump here every time we need to show controlling gui
    show screen prison_break_controls
    while 1:
        $ result = ui.interact()
        if result in hero.team:
            $ came_to_equip_from = "storyi_continue"
            $ eqtarget = result
            $ equip_girls = [eqtarget]
            $ equipment_safe_mode = True
            hide screen prison_break_controls
            jump char_equip

label storyi_continue: # the label where we return after visiting characters equipment screens
    call storyi_show_bg from _call_storyi_show_bg_4
    $ equipment_safe_mode = False
    jump storyi_gui_loop

label storyi_exit:
    $ last_label = "forest_dark" if controlled_exit else "forest_entrance"
    $ del sflash, q_dissolve, eye_open, eye_shut, map_scroll, blueprint, point, fight_chance #, enemy_soldier, enemy_soldier2 
    $ del storyi_data, storyi_loc_map, storyi_prison_location, storyi_treasures, controlled_exit
    jump expression last_label

screen prison_break_controls(): # control buttons screen
    use top_stripe(False, show_lead_away_buttons=False, show_team_status=True)
    frame:
        xalign 0.95
        ypos 50
        background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
        xpadding 10
        ypadding 10
        vbox:
            style_prefix "wood"
            align (0.5, 0.5)
            spacing 10
            button:
                xysize (120, 40)
                yalign 0.5
                action [Hide("prison_break_controls"), Play("events2", "events/letter.mp3"), Jump("storyi_map")]
                text "Show map" size 15
            if not hero.has_flag("dnd_storyi_rest"):
                button:
                    xysize (120, 40)
                    yalign 0.5
                    action [Hide("prison_break_controls"), Jump("mc_action_storyi_rest")]
                    text "Rest" size 15
            if not hero.has_flag("dnd_storyi_heal"):
                if storyi_prison_location == "Infirmary":
                    button:
                        xysize (120, 40)
                        yalign 0.5
                        action [Hide("prison_break_controls"), Jump("storyi_treat_wounds")]
                        text "Heal" size 15
            if storyi_prison_location == "MHall" and not global_flags.has_flag("defeated_boss_1"):
                button:
                    xysize (120, 40)
                    yalign 0.5
                    action [Hide("prison_break_controls"), Jump("storyi_bossroom")]
                    text "Go Up" size 15
            if storyi_prison_location in storyi_treasures:
                button:
                    xysize (120, 40)
                    yalign 0.5
                    action [Hide("prison_break_controls"), Jump("storyi_search_items")]
                    text "Search" size 15
            button:
                xysize (120, 40)
                yalign 0.5
                action [Hide("prison_break_controls"), SetVariable("controlled_exit", True), Jump("storyi_exit")]
                text "Exit" size 15
                keysym "mousedown_3"

            if DEBUG:
                button:
                    xysize (120, 40)
                    yalign 0.5
                    action [Hide("prison_break_controls"), Jump("storyi_bossroom")]
                    text "Test Boss" size 15

label storyi_bossroom:
    stop music
    stop world fadeout 2.0
    play world "events/6.ogg" fadein 2.0 loop
    play events2 "events/wind1.mp3" fadein 2.0 loop
    show bg story p2 with dissolve
    show sinister_star:
        pos (704, 91)
        anchor (0.5, 0.5)
        subpixel True
        zoom 0.1
        alpha 0
        linear 1.5 alpha 1.0
    "Finally, you reach the throne room on top of the building. Some windows are broken, and the wind blows through."
    menu:
        "If you continue, there won't be way back."
        "Continue":
            $ pass
        "Return to the ground floor":
            call storyi_show_bg from _call_storyi_show_bg
            play world "Theme2.ogg" fadein 2.0 loop
            stop events2
            hide sinister_star
            jump storyi_gui_loop
    show sinister_star:
        linear 2.5 zoom 0.2
    "You take a step forward, and something changes."
    show bg story p3 with dissolve
    show sinister_star:
        linear 1.5 zoom 0.3
    extend " Daylight fades, being replaced by red glow from above."
    show sinister_star:
        linear 2.0 zoom 0.4
    "There is a tiny red star in the gem on the ceiling."
    show sinister_star:
        linear 2.0 zoom 0.5
    extend " It wakes up, disturbed by your presence."
    show sinister_star:
        linear 8 ypos 375 zoom 1.5
    "The air temperature rises rapidly."
    show bg story p3 with sflash
    show sinister_star:
        linear 4 zoom 2.5
    extend " You prepare for a fight!"
    python:
        enemy_team = Team(name="Enemy Team", max_size=3)
        mob = build_mob(id="Blazing Star", level=25)
        mob.stats.mod_raw_max("health", 500)
        mob.mod_stat("health", 500)
        mob.stats.mod_raw_max("mp", 100)
        mob.mod_stat("mp", 100)
        enemy_team.add(mob)
        del mob
        result = "content/gfx/bg/story/p_b.webp"
        result = run_default_be(enemy_team, background="content/gfx/bg/story/p_b.webp", end_background=result,
                                track="content/sfx/music/be/battle (5)b.ogg", death=True)

    if result is True:
        show bg story p4 with sflash
        show sinister_star at Position(xpos = 704, xanchor=.5, ypos=375, yanchor=.5):
            anchor (0.5, 0.5)
            zoom 1.0
            alpha 1.0
        $ global_flags.set_flag("defeated_boss_1")
        "The star loses its strength, and the air temperature drops."
        hide sinister_star with dissolve
        extend " You pick it up and put in your pocket."
        $ hero.add_item("Red Star")
        stop events2
        call storyi_show_bg from _call_storyi_show_bg_1
        play world "Theme2.ogg" fadein 2.0 loop
        "You return to the ground floor."
        $ del result, enemy_team
        jump storyi_gui_loop
    else:
        jump game_over

label mc_action_storyi_rest: # resting inside the dungeon; team may be attacked during the rest
    $ hero.set_flag("dnd_storyi_rest")
    show bg tent with q_dissolve
    python hide:
        for i in hero.team:
            i.gfx_mod_stat("vitality", i.get_max("vitality")/3)
            i.gfx_mod_stat("mp", i.get_max("mp")/10)
    "You set up a small camp and rest for a bit."
    $ fight_chance += 10
    call storyi_show_bg from _call_storyi_show_bg_2
    if dice(fight_chance):
        hide screen prison_break_controls
        "You have been ambushed by enemies!"
        jump storyi_randomfight
    jump storyi_gui_loop

label storyi_randomfight:  # initiates fight with random enemy team
    $ fight_chance = 10

    python:
        enemy_team = Team(name="Enemy Team", max_size=3)
        mobs = storyi_loc_map[storyi_prison_location]["mobs"]
        for j in range(randint(1, 3)):
            mob = build_mob(id=random.choice(mobs), level=15)
            mob.controller = Complex_BE_AI(mob)
            enemy_team.add(mob)
        del mobs, mob, j
        result = storyi_loc_map[storyi_prison_location]["img"]
        result = run_default_be(enemy_team, background="content/gfx/bg/be/b_dungeon_1.webp",
                                end_background=result, skill_lvl=4, give_up="escape")

    if result is True:
        play world "Theme2.ogg" fadein 2.0 loop

        if storyi_prison_location not in storyi_treasures and dice(hero.get_stat("luck")+30):
            python hide:
                money = randint(10, 30)
                hero.add_money(money, reason="Loot")
                gfx_overlay.random_find(money, 'gold')

        $ del result, enemy_team
        call storyi_show_bg from _call_storyi_show_bg_3
        jump storyi_gui_loop
    elif result == "escape":
        $ del result, enemy_team
        scene black
        pause 1.0
        jump storyi_exit
    else:
        jump game_over

label storyi_treat_wounds:
    $ j = False
    python:
        for i in hero.team:
            if i.get_stat("health") < i.get_max("health"):
                j = True
                break
    if j:
        python:
            for i in hero.team:
                i.gfx_mod_stat("health", i.get_max("health") - i.get_stat("health"))
        $ hero.set_flag("dnd_storyi_heal")
        "Health is restored!"
    else:
        "Everyone is healthy already."
    $ del j, i
    jump storyi_gui_loop

label storyi_show_bg: # shows bg depending on matrix location; due to use of BE it must be a call, and not a part of matrix logic itself
    $ bg = storyi_loc_map[storyi_prison_location]["img"]
    show expression bg with q_dissolve
    $ del bg
    if storyi_treasures.get(storyi_prison_location, 0) == -1:
        $ renpy.notify("It might be worth to search this room...")
        $ storyi_treasures[storyi_prison_location] = max(0, day-10)
    return

label storyi_search_items:
    "You look around the room in search of something useful."
    $ search_day = storyi_treasures[storyi_prison_location]
    if search_day == day:
        "... This is pointless."
        $ del search_day
        jump storyi_gui_loop
    if not dice((day - search_day) * 8 * (100 + hero.get_stat("luck")) / 100):
        "There is only trash on the floor."
        $ storyi_treasures[storyi_prison_location] += 1 
        $ del search_day
        jump storyi_gui_loop

    $ storyi_treasures[storyi_prison_location] = day
    $ del search_day

    python hide:
        items = storyi_loc_map[storyi_prison_location]["items"]
        luck = hero.get_stat("luck")
        found = False
        for i in items:
            if i == "loot":
                if not dice(luck / 3):
                    continue
                msg = "There is something shiny in the corner of the room..."
                prices = [100, 200, 300]
            elif i == "restore":
                msg = "Surveying the room, you found a few portable restoration items. Sadly, others are too heavy and big to carry around."
                prices = [100, 200, 400]
            elif i == "armor":
                msg = "You see some old armor on the shelves."
                prices = [500, 700, 1000]
            elif i == "weapon":
                msg = "Among a heap of rusty blades, you see some good weapons."
                prices = [500, 700, 1000]
            elif i == "food":
                msg = "Most of the food is spoiled, but some of it is still edible."
                prices = [500, 500, 500]
            elif i == "alcohol":
                msg = "The food is spoiled, but alcohol is still good..."
                prices = [500, 500, 500]
            elif i == "dress":
                msg = "There is a pile of clothes in the corner, probably remained from the former prisoners."
                prices = [500, 500, 500]
            else:
                continue
            narrator(msg)
            found |= give_to_mc_item_reward(i, tier=2, price=prices[0])
            found |= give_to_mc_item_reward(i, tier=2, price=prices[1])
            if dice(luck):
                found |= give_to_mc_item_reward(i, tier=2, price=prices[2])

        if not found:
            narrator("There is only trash on the floor.")

    jump storyi_gui_loop

label storyi_move_map_point: # moves green point to show team location on the map
    show expression point at Transform(pos=storyi_loc_map[storyi_prison_location]["pos"]) with move
    return

label storyi_map: # shows dungeon map and calls matrix to control it
    show expression map_scroll at truecenter
    show expression blueprint at blueprint_position
    call storyi_move_map_point from _call_storyi_move_map_point
    call screen poly_matrix(storyi_data, cursor="content/gfx/interface/icons/zoom_pen.png", xoff=0, yoff=0, show_exit_button=(1.0, 1.0))
    $ setattr(config, "mouse", None)
    $ fight_chance += randint(10, 20)

    if _return in storyi_loc_map:
        if storyi_prison_location == _return:
            # already at the selected location
            $ msg = storyi_loc_map[_return]["desc"]
            "[msg]"
            $ del msg
            jump storyi_map
        if storyi_prison_location not in storyi_loc_map[_return]["entries"]:
            "You are too far to go there."
            jump storyi_map
        # enter the new location
        $ storyi_prison_location = _return
        $ sfx = storyi_loc_map[storyi_prison_location].get("sfx", None)
        if sfx:
            play events2 sfx
        $ del sfx
        
        call storyi_move_map_point from _call_storyi_move_map_point_1
        call storyi_show_bg from _call_storyi_show_bg_5

        # special comment before boss
        if storyi_prison_location == "MHall" and not global_flags.has_flag("defeated_boss_1"):
            hero.say "I see old stairs. I wonder where they lead."

        # chance encounter
        if storyi_loc_map[storyi_prison_location].get("mobs", None) and dice(fight_chance):
            jump storyi_randomfight

        jump storyi_map
    else:
        play events2 "events/letter.mp3"
        hide expression map_scroll
        hide expression blueprint
        hide expression point
        with dissolve
        jump storyi_gui_loop
