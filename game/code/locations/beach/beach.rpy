label city_beach:
    $ iam.enter_location(goodtraits=["Energetic", "Exhibitionist"], badtraits=["Scars", "Undead", "Furry", "Monster", "Not Human"],
                        coords=[[.14, .65], [.42, .6], [.85, .45]])

    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("beach_main")
    $ global_flags.del_flag("keep_playing_music")

    scene bg city_beach
    with dissolve

    if not global_flags.flag('visited_city_beach'):
        $ global_flags.set_flag('visited_city_beach')
        "Welcome to the beach!"
        "Sand, sun, and girls in bikinis, what else did you expect?"
        "Oh, we might have a Kraken hiding somewhere as well :)"

    show screen city_beach

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            python hide:
                char = result[1]
                iam.start_int(char, img=iam.select_beach_img_tags(char))

        elif result == ['control', 'return']:
            hide screen city_beach
            with dissolve
            jump city

screen city_beach():
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
        # Jump buttons:
        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80)
        imagebutton:
            align (.99, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach"), Jump("city_beach_right")]

        $ img = im.Flip(img, horizontal=True)
        imagebutton:
            align (.01, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach"), Function(global_flags.set_flag, "keep_playing_music"), Jump("city_beach_left")]

        $ img = im.Scale("content/gfx/interface/icons/swimming_pool.png", 60, 60)
        imagebutton:
            pos (1040, 80)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach"), Jump("swimming_pool")]
            tooltip "Swimming Pool"

        $ img = im.Scale("content/gfx/interface/icons/sp_swimming.png", 90, 90)
        imagebutton:
            pos (280, 240)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("city_beach"), Show("city_beach_swim"), With(dissolve)]
            tooltip "Swim"

screen city_beach_swim():
    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Swim":
            action Hide("city_beach_swim"), Jump("city_beach_swimming_checks")
        if hero.get_skill("swimming") >= 150:
            textbutton "Diving":
                action Hide("city_beach_swim"), Jump("mc_action_city_beach_diving_checks")
        if global_flags.has_flag('constitution_bonus_from_swimming_at_beach'):
            textbutton "About swimming":
                action Hide("city_beach_swim"), Jump("city_beach_about_swimming")
        textbutton "Leave":
            action Hide("city_beach_swim"), Show("city_beach"), With(dissolve)
            keysym "mousedown_3"

label city_beach_about_swimming:
    "By swimming here you can increase max constitution and, if you manage to avoid sea monsters, agility."
    "But you need high enough swimming skill. Consider practicing in the swimming pool first."
    "With high enough swimming skill you can try diving, where you can obtain some valuable items."
    $ global_flags.set_flag("keep_playing_music")
    jump city_beach

label city_beach_swimming_checks:
    if not global_flags.has_flag('constitution_bonus_from_swimming_at_beach'):
        $ global_flags.set_flag("constitution_bonus_from_swimming_at_beach", value=0)
        "The water is quite warm all year round, but it can be pretty dangerous for novice swimmers due to big waves and sea monsters."
        "Those who are not confident in their abilities prefer the local swimming pool, although it's not free, unlike the sea."
        "In general, the swimming skill will increase faster in the ocean, unless you drown immediately due to low skill."
        scene bg open_sea
        with dissolve
        "You stay in shallow water not too far from land to get used to the water. It feels nice, but the real swimming will require some skills next time."
    elif hero.get_stat("vitality") < 30:
        "You are too tired at the moment."
    elif not hero.has_ap():
        "You don't have Action Points at the moment. Try again tomorrow."
    elif hero.get_stat("health") < hero.get_max("health")/4:
        "You are too wounded at the moment."
    else:
        scene bg open_sea with dissolve

        $ hero.take_ap(1)
        if locked_dice(20):
            "A group of sea monsters surrounded you!"
            if hero.get_skill("swimming") < 50:
                if hero.get_stat("health") > 100 and locked_dice(75):
                    "They managed to attack you a few times before you got a chance to react."
                    $ hero.mod_stat("health", -randint(15, 30))
                jump city_beach_monsters_fight
            elif hero.get_skill("swimming") < 200:
                jump city_beach_monsters_fight
            else:
                menu:
                    "You are fast enough to avoid the fight."
                    "Swim away":
                        "You quickly increase the distance between you and the monsters {color=green}(max agility +1){/color}."
                        $ hero.gfx_mod_skill("swimming", 0, randint(2, 4))
                        $ hero.stats.mod_raw_max("agility", 1)
                        $ hero.gfx_mod_stat("agility", 1)
                    "Fight":
                        jump city_beach_monsters_fight
        $ temp = hero.get_skill("swimming")
        if temp < 50:
            if locked_dice(40):
                "You try to swim, but strong tide keeps you away {color=red}(no bonus to swimming skill this time){/color}."
                "You need higher swimming skill to prevent it. Consider training in the swimming pool."
                $ swim_act = 0
            else:
                scene bg ocean_underwater with dissolve
                "Waves are pretty big today. You try fighting them, but quickly lose, pulling you under the water."
                "Nearly drowned, you get out of the ocean."
                "You need higher swimming skill to prevent it. Consider training in the swimming pool."
                $ hero.gfx_mod_stat("health", -50)
                $ swim_act = randint(1, 2)
            $ swim_vit = randint (40, 50)
        elif temp < 100:
            "You try to swim, but rapid underwater currents make it very difficult for a novice swimmer."
            if locked_dice(10):
                scene bg ocean_underwater with dissolve
                "Waves are pretty big today. You try to fight them, but they win, sending you under the water."
                "You need higher swimming skill to prevent it. Consider training in the swimming pool."
                "Nearly drowned, you get out of the ocean."
                $ hero.gfx_mod_stat("health", -50)
            $ swim_act = randint(4, 8)
            $ swim_vit = randint (30, 40)
        elif temp < 200:
            "You cautiously swim in the ocean, trying to stay close to the shore just in case."
            $ swim_act = randint(6, 12)
            $ swim_vit = randint (20, 30)
        else:
            "You take your time enjoying the water. Even big ocean waves are no match for your swimming skill."
            $ swim_act = randint(10, 15)
            $ swim_vit = randint (15, 25)
        $ hero.gfx_mod_skill("swimming", 0, swim_act)
        $ hero.mod_stat("vitality", -swim_vit)

        if locked_dice(min(600, temp) - global_flags.flag("constitution_bonus_from_swimming_at_beach")*20): # MAX 30
            $ hero.stats.mod_raw_max("constitution", 1)
            $ hero.gfx_mod_stat("constitution", 1)
            $ global_flags.up_counter("constitution_bonus_from_swimming_at_beach")
            "You feel more endurant than before {color=green}(max constitution +1){/color}."

        $ del swim_act, swim_vit, temp

    $ global_flags.set_flag("keep_playing_music")
    jump city_beach

label city_beach_monsters_fight:
    $ enemy_team = Team(name="Enemy Team")
    python hide:
        min_lvl = mobs["Skyfish"]["min_lvl"]
        for i in range(randint(2, 3)):
            mob = build_mob(id="Skyfish", level=randint(min_lvl, min_lvl+10))
            #mob.front_row = 1
            enemy_team.add(mob)

    $ result = iam.select_background_for_fight("beach")
    $ result = run_default_be(enemy_team, background=result, end_background="city_beach", give_up="escape")

    if result is True:
        $ pass
    elif result is False:
        "The guards managed to drive away monsters, but your wounds are deep..."
    else:
        scene black
        pause 1.0
    $ del result, enemy_team
    jump city_beach

transform alpha_dissolve:
    alpha .0
    linear .5 alpha 1.0
    on hide:
        linear .5 alpha 0

screen diving_progress_bar(o2, max_o2): # oxygen bar for diving
    default oxigen = o2
    default max_oxigen = max_o2

    timer .1 repeat True action If(oxigen > 0, true=SetScreenVariable('oxigen', oxigen-1), false=(Hide("diving_progress_bar"), Return("All out of Air!")))
    key "mousedown_3" action (Hide("diving_progress_bar"), Return("Swim Out"))
    key "K_ESCAPE" action (Hide("diving_progress_bar"), Return("Swim Out"))
    if DEBUG:
        vbox:
            xalign .5
            text str(oxigen)
            text str(max_oxigen)
    vbox:
        xsize 300
        bar:
            right_bar im.Scale("content/gfx/interface/bars/oxigen_bar_empty.png", 300, 50)
            left_bar im.Scale("content/gfx/interface/bars/oxigen_bar_full.png", 300, 50)
            value oxigen
            range max_oxigen
            thumb None
            xysize (300, 50)
            at alpha_dissolve
        label "Find hidden items!" text_color "gold" text_size 18 xalign .5 yalign .5
        label "Right click or Esc to exit" text_color "gold" text_size 18 xalign .5 yalign .5

screen diving_hidden_area(items, size):
    on "hide":
        action SetField(config, "mouse", None)

    # randomly places a "hidden" rectangular area(s) on the screen.
    # Areas are actually plain buttons with super low alpha...
    # Expects a list/tuple, like: (["hidden_cache_1", (100, 100), (.1, .5)], ["hidden_cache_2", (50, 50), (.54, .10)])
    # If cache is found, screen (which should be called) will return: "hidden_cache_1" string. Tuple is the size in pixels.
    # Data is randomized outside of this screen!
    for item, align in items:
        button:
            align align
            background Null()
            xysize size
            action Return(item)
            hovered SetField(config, "mouse", {"default": [("content/gfx/interface/icons/net.png", 0, 0)]})
            unhovered SetField(config, "mouse", None)

label mc_action_city_beach_diving_checks:
    if not global_flags.flag('diving_city_beach'):
        $ global_flags.set_flag('diving_city_beach')
        "With high enough swimming skill you can try diving. The amount of oxygen is based on your swimming skill."
        "You need vitality to pick up items. Vitality is not consumed, but the more vitality you have in general, the more items you can pick up."
        "The goal is to find invisible items hidden on the seabed."
        "You can leave the sea anytime by clicking the right mouse button, and you will lose some health if you don't leave before the oxygen is over."
    if hero.get_stat("vitality") < 60:
        "You're too tired at the moment."
        jump city_beach
    elif hero.get_stat("health") < hero.get_max("health")/2:
        "You are too wounded at the moment."
        jump city_beach
    elif not hero.take_ap(1):
        "You don't have Action Points at the moment. Try again tomorrow."
        jump city_beach

    play world "underwater.mp3"
    scene bg ocean_underwater_1 with dissolve

    python:
        i = round_int(hero.get_skill("swimming")/2)
        loots = [[j, j.chance] for j in items.values() if "Diving" in j.locations and j.price <= i]
        if has_items("Snorkel Mask", hero, equipped=True):
            i += 100
        if has_items("Lantern", hero, equipped=True):
            j = (90, 90)
        else:
            j = (50, 50)
            renpy.show("shadow", what=Solid("#000000a0", xysize=(config.screen_width, config.screen_height)))
        vitality = hero.get_stat("vitality")
        result = hero.get_max("vitality")

    $ renpy.start_predict("content/gfx/images/fishy.png", "content/gfx/interface/icons/net.png")
    show screen diving_progress_bar((i * vitality) / result, i)
    while vitality > 10:
        if not renpy.get_screen("diving_progress_bar"):
            "You've run out of air!"
            $ hero.gfx_mod_stat("health", -40)
            jump mc_action_city_beach_diving_exit

        $ result = tuple(["Item", (random.random(), random.random())] for i in range(4))
        show screen diving_hidden_area(result, j)

        $ result = ui.interact()

        hide screen diving_hidden_area
        if result == "All out of Air!":
            "You've run out of air!"
            $ hero.gfx_mod_stat("health", -40)
            jump mc_action_city_beach_diving_exit
        if result == "Swim Out":
            "You return to the surface before you run out of air."
            jump mc_action_city_beach_diving_exit

        python hide:
            if result == "Item":
                item = weighted_choice(loots)
            else:
                item = None
            tkwargs = {"color": "dodgerblue", "outlines": [(1, "black", 0, 0)]}
            if item is not None:
                gfx_overlay.notify("You caught %s!" % item.id, tkwargs=tkwargs)

                hero.add_item(item)
                gfx_overlay.random_find(item, 'fishy')
            else:
                gfx_overlay.notify("There is nothing there...", tkwargs=tkwargs)

        $ vitality -= randint(20, 30)

    hide screen diving_progress_bar
    "You're too tired to continue!"
    $ hero.mod_stat("vitality", -randint(15, 25))
    $ hero.gfx_mod_skill("swimming", 0, randrange(1))
    if locked_dice(min(100, hero.get_skill("swimming")) - global_flags.get_flag("vitality_bonus_from_diving_at_beach", 0)*2): # MAX 50
        $ hero.stats.mod_raw_max("vitality", 1)
        $ hero.mod_stat("vitality", 1)
        $ global_flags.up_counter("vitality_bonus_from_diving_at_beach")
        "You feel more endurant than before {color=green}(max vitality +1){/color}."

label mc_action_city_beach_diving_exit:
    $ renpy.stop_predict("content/gfx/images/fishy.png", "content/gfx/interface/icons/net.png")
    $ del i, j, loots, vitality, result
    jump city_beach
