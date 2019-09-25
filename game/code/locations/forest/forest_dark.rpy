label forest_dark:
    python:
        background_number = -1
        forest_bg_change = True
        forest_location = None

    if not hero.team.take_pp(80):
        if len(hero.team) > 1:
            "Unfortunately, your team is too tired at the moment. Maybe another time."
        else:
            "Unfortunately, you are too tired at the moment. Maybe another time."

        "Each member of your party must have at least 80 PP (and 2 AP is recommended)."
        jump dark_forest_exit

label forest_dark_continue:
    if forest_bg_change:
        $ background_number = choice(list(i for i in range(1, 7) if i != background_number))
        $ forest_location = "content/gfx/bg/locations/forest_" + str(background_number) + ".webp"
    scene expression forest_location

    if pytfall.enter_location("deep_forest", music=False, env="forest_entrance"):
        "You step away from the city walls and go deep into the forest. It's not safe here, better to be on guard."

    show screen city_dark_forest
    with dissolve # dissolve the whole scene, not just the bg
    while 1:
        $ result = ui.interact()

        if result in hero.team:
            $ came_to_equip_from = "forest_dark_continue"
            $ eqtarget = result
            $ equip_girls = [result]
            $ equipment_safe_mode = True
            $ forest_bg_change = False

            hide screen city_dark_forest
            jump char_equip

screen city_dark_forest():
    use top_stripe(False, show_lead_away_buttons=False)
    use team_status(interactive=True)

    frame:
        xalign .95
        ypos 50
        background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
        padding 10, 10
        vbox:
            style_group "wood"
            align (.5, .5)
            spacing 10
            button:
                xysize (120, 40)
                yalign .5
                action [Hide("city_dark_forest"), Jump("city_dark_forest_explore"), With(dissolve)]
                text "Explore" size 15
            button:
                xysize (120, 40)
                yalign .5
                action [Hide("city_dark_forest"), Jump("mc_action_city_dark_forest_rest"), With(dissolve), SensitiveIf(not hero.has_flag("dnd_dark_forest_rested"))]
                text "Rest" size 15
            if global_flags.has_flag("found_old_ruins"):
                button:
                    xysize (120, 40)
                    yalign .5
                    action [Hide("city_dark_forest"), Jump("city_dark_forest_ruines_part"), With(dissolve)]
                    text "Ruins" size 15
            button:
                xysize (120, 40)
                yalign .5
                action [Hide("city_dark_forest"), Jump("dark_forest_exit"), With(dissolve)]
                text "Leave" size 15
                keysym "mousedown_3"

label city_dark_forest_explore:
    if not(hero.team.take_pp(20)):
        if len(hero.team) > 1:
            "Unfortunately, your team is too tired at the moment. Maybe another time."
        else:
            "Unfortunately, you are too tired at the moment. Maybe another time."

        "Each member of your party should have at least 20 PP (and 1 AP is recommended)."
        $ forest_bg_change = False
        jump forest_dark_continue
    else:
        if (not hero.has_flag("dnd_dark_forest_river")) and hero.get_stat("vitality") < hero.get_max("vitality") and dice(10):
            jump mc_action_city_dark_forest_river
        elif not global_flags.has_flag("found_old_ruins") and dice(5):
            $ global_flags.set_flag("found_old_ruins")
            jump storyi_start
        elif dice(20) and not hero.has_flag("dnd_dark_forest_girl"):
            jump dark_forest_girl_meet
        elif dice(70) or hero.has_flag("dnd_dark_forest_bandits"):
            jump city_dark_forest_fight
        else:
            $ hero.set_flag("dnd_dark_forest_bandits")
            jump city_dark_forest_hideout

label city_dark_forest_ruines_part:
    if not(hero.team.take_pp(20)):
        if len(hero.team) > 1:
            "Unfortunately, your team is too tired to explore dungeons. Maybe another time."
        else:
            "Unfortunately, you are too tired to explore dungeons. Maybe another time."

        "Each member of your party should have at least 20 PP (and 2 AP is recommended)."
        $ forest_bg_change = False
        jump forest_dark_continue
    else:
        jump storyi_start

label mc_action_city_dark_forest_rest:
    $ hero.set_flag("dnd_dark_forest_rested")
    scene bg camp
    with dissolve

    "You take a short rest before moving on, restoring mp and vitality."

    python hide:
        for i in hero.team:
            i.gfx_mod_stat("vitality", i.get_max("vitality")/4)
            i.gfx_mod_stat("health", i.get_max("health")/20)
            i.gfx_mod_stat("mp", i.get_max("mp")/5)
    $ forest_bg_change = False
    jump forest_dark_continue

label city_dark_forest_hideout:
    $ group_counter = total = randint(2, 4)
    while group_counter > 0:
        scene bg forest_hideout
        with dissolve

        if group_counter == total:
            menu:
                "You found bandits hideout inside an old abandoned castle."
                "Attack them":
                    "You carefully approach the hideout when a group of bandits attacks you."
                "Leave them be":
                    $ group_counter = total = 0
        else:
            "Another group is approaching you!"

        if group_counter > 0:
            $ enemy_team = Team(name="Enemy Team")
            python hide:
                for i in range(3):
                    mob = choice(["Samurai", "Warrior", "Archer", "Soldier", "Barbarian", "Orc", "Infantryman", "Thug", "Mercenary", "Dark Elf Archer"])
                    min_lvl = mobs[mob]["min_lvl"]
                    mob = build_mob(id=mob, level=randint(min_lvl, min_lvl+20))
                    enemy_team.add(mob)

            $ result = iam.select_background_for_fight("forest")
            $ result = run_default_be(enemy_team, background=result, end_background=forest_location, give_up="escape")
            if result is True:
                $ group_counter -= 1
            elif result == "escape":
                scene black
                pause 1.0
                $ group_counter = total = 0
            else:
                jump game_over
            $ del result, enemy_team

    if total != 0:
        "After killing all bandits, you found stash with loot."

        python hide:
            for type, price in (("treasure", 300), ("restore", 100), ("armor", 300), ("weapon", 300)):
                if locked_dice(50):
                    give_to_mc_item_reward(type, tier=2, price=price)
        $ forest_bg_change = False
    else:
        $ forest_bg_change = True
    $ del total, group_counter
    jump forest_dark_continue

label city_dark_forest_fight:
    $ enemy_team = Team(name="Enemy Team")
    python hide:
        mob = choice(["slime", "were", "harpy", "goblin", "wolf", "bear",
                      "druid", "rat", "undead", "butterfly"])
        et_len = 3
        if mob == "slime":
            msg = "You encountered a small group of predatory slimes."
            mob_ids = ["Alkaline Slime", "Slime", "Acid Slime"]
        elif mob == "were":
            msg = "Hungry shapeshifters want a piece of you."
            mob_ids = ["Werecat", "Werewolf", "Weregirl"]
        elif mob == "harpy":
            msg = "A flock of wild harpies attempts to protect their territory."
            mob_ids = ["Harpy", "Vixen"]
        elif mob == "goblin":
            msg = "You find yourself surrounded by a group of goblins."
            mob_ids = ["Goblin", "Goblin Archer", "Goblin Warrior", "Goblin Shaman"]
        elif mob == "wolf":
            msg = "A pack of wolves picks you for dinner."
            mob_ids = ["Wolf", "Black Wolf"]
        elif mob == "bear":
            msg = "You disturbed an angry bear."
            mob_ids = ["Bear", "Beargirl"]
            et_len -= 1
        elif mob == "druid":
            msg = "Forest fanatics attempt to sacrifice you in the name of «mother nature» or something like that."
            mob_ids = ["Druid", "Wild Dryad"]
        elif mob == "rat":
            msg = "A pack of foul-smelling rats picks you for dinner."
            mob_ids = ["Undead Rat"]
        elif mob == "undead":
            msg = "A group of decayed skeletons rise from the ground."
            mob_ids = ["Skeleton", "Skeleton Warrior"]
        else:
            msg = "You encountered a small group of aggressive giant butterflies."
            mob_ids = ["Black Butterfly"]

        for i in range(et_len):
            mob_id = choice(mob_ids)
            min_lvl = mobs[mob_id]["min_lvl"]
            mob = build_mob(id=mob_id, level=randint(min_lvl, min_lvl+20))
            enemy_team.add(mob)

        narrator(msg)

    $ result = iam.select_background_for_fight("forest")
    $ result = run_default_be(enemy_team, background=result, end_background=forest_location, give_up="escape")

    if result is True:
        $ give_to_mc_item_reward(["treasure", "restore"], tier=2)
        $ forest_bg_change = False
    elif result == "escape":
        scene black
        pause 1.0
        $ forest_bg_change = True
    else:
        jump game_over
    $ del result, enemy_team
    jump forest_dark_continue

label dark_forest_girl_meet:
    $ hero.set_flag("dnd_dark_forest_girl")
    python:
        temp = set(iam.get_all_girls()) | set(hero.chars)
        choices = list(i for i in chars.values() if
                       i not in temp and i.location != pytfall.jail and
                       not i.arena_active)
        temp = ["Homebody", "Indifferent", "Coward"]
        choices = list(i for i in choices if not any(trait in temp for trait in i.traits))
    if choices:
        $ char = random.choice(choices)
        $ spr = char.get_vnsprite()
        show expression spr with dissolve
        $ char.override_portrait("portrait", "happy")
        $ char.show_portrait_overlay("love", "reset")
        if char.gender == "female":
            "You found a girl lost in the woods and escorted her to the city."
            char.say "She happily kisses you on the cheek as a thanks."
        else:
            "You found a guy lost in the woods and escorted him to the city."
            char.say "He wholeheartedly thanks you for your help."
        extend " Maybe you should try to find [char.op] in the city later."
        $ char.restore_portrait()
        $ char.hide_portrait_overlay()
        $ char.gfx_mod_stat("disposition", get_linear_value_of(char.get_stat("disposition"), 0, 100, char.get_max("disposition"), 0))
        $ char.gfx_mod_stat("affection", affection_reward(char))
        hide expression spr with dissolve
        $ del char, spr, temp, choices
        $ forest_bg_change = True
        jump forest_dark_continue
    $ del temp, choices

label mc_action_city_dark_forest_river:
    scene bg forest_lake
    with dissolve
    $ pytfall.enter_location("deep_forest", music=False, env="forest_lake")
    $ hero.set_flag("dnd_dark_forest_river")
    "You found a river. Fresh, clean water restores some of your vitality."
    python hide:
        for i in hero.team:
            i.gfx_mod_stat("vitality", i.get_max("vitality")/2)
    $ forest_bg_change = False
    jump forest_dark_continue

label dark_forest_exit:
    $ del background_number, forest_location, forest_bg_change
    jump forest_entrance
