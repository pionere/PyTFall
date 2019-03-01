label forest_dark:
    python:
        background_number = -1
        forest_bg_change = True
        # Build the actions
        if pytfall.world_actions.location("forest_entrance"):
            pytfall.world_actions.finish()

label forest_dark_continue:
    if forest_bg_change:
        $ background_number = choice(list(i for i in range(1, 7) if i != background_number))
        $ forest_location = "content/gfx/bg/locations/forest_" + str(background_number) + ".webp"
    else:
        $ forest_bg_change = True
    scene expression forest_location
    with dissolve

    # Music related:
    if not "forest_entrance" in ilists.world_music:
        $ ilists.world_music["forest_entrance"] = [track for track in os.listdir(content_path("sfx/music/world")) if track.startswith("forest_entrance")]
    if not global_flags.has_flag("keep_playing_music"):
        play world choice(ilists.world_music["forest_entrance"])
    $ global_flags.del_flag("keep_playing_music")

    if not global_flags.has_flag('visited_deep_forest'):
        $ global_flags.set_flag('visited_deep_forest')
        $ block_say = True
        "You step away from the city walls and go deep into the forest. It's not safe here, better to be on guard."
        $ block_say = False

    show screen city_dark_forest

    while 1:
        $ result = ui.interact()

        if result in hero.team:
            $ came_to_equip_from = "forest_dark_continue"
            $ eqtarget = result
            $ equip_girls = [result]
            $ global_flags.set_flag("keep_playing_music")
            $ equipment_safe_mode = True
            $ forest_bg_change = False

            hide screen city_dark_forest
            jump char_equip

screen city_dark_forest():
    use top_stripe(False, None, False, True)

    frame:
        xalign .95
        ypos 50
        background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
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
                action [Hide("city_dark_forest"), Jump("forest_entrance"), With(dissolve)]
                text "Leave" size 15

    key "mousedown_3" action [Hide("city_dark_forest"), Jump("forest_entrance"), With(dissolve)]

label city_dark_forest_explore:
    if not(take_team_ap(1)):
        if len(hero.team) > 1:
            "Unfortunately, your team is too tired at the moment. Maybe another time."
        else:
            "Unfortunately, you are too tired at the moment. Maybe another time."

        "Each member of your party should have at least 1 AP."

        $ global_flags.set_flag("keep_playing_music")
        $ forest_bg_change = False
        jump forest_dark_continue
    else:
        if (not hero.has_flag("dnd_dark_forest_river")) and hero.get_stat("vitality") < hero.get_max("vitality") and dice(35):
            jump mc_action_city_dark_forest_river
        elif not global_flags.has_flag("found_old_ruins") and day >= 10 and dice(50):
            $ global_flags.set_flag("found_old_ruins")
            hide screen city_dark_forest
            jump storyi_start
        elif dice(20) and not hero.has_flag("dnd_dark_forest_girl"):
            jump dark_forest_girl_meet
        elif dice(70) or hero.has_flag("dnd_dark_forest_bandits"):
            jump city_dark_forest_fight
        else:
            $ hero.set_flag("dnd_dark_forest_bandits")
            jump city_dark_forest_hideout

label city_dark_forest_ruines_part:
    if not(take_team_ap(2)):
        if len(hero.team) > 1:
            "Unfortunately, your team is too tired to explore dungeons. Maybe another time."
        else:
            "Unfortunately, you are too tired to explore dungeons. Maybe another time."

        "Each member of your party should have at least 2 AP."

        $ global_flags.set_flag("keep_playing_music")
        jump forest_dark_continue
    else:
        hide screen city_dark_forest
        jump storyi_start

label mc_action_city_dark_forest_rest:
    $ hero.set_flag("dnd_dark_forest_rested")
    $ forest_bg_change = False
    scene bg camp
    with dissolve

    "You take a short rest before moving on, restoring mp and vitality."
    $ forest_bg_change = False
    $ global_flags.set_flag("keep_playing_music")

    python:
        for i in hero.team:
            i.gfx_mod_stat("vitality", i.get_max("vitality")/4)
            i.gfx_mod_stat("health", i.get_max("health")/20)
            i.gfx_mod_stat("mp", i.get_max("mp")/5)
    jump forest_dark_continue

label city_dark_forest_hideout:
    hide screen city_dark_forest
    scene bg forest_hideout
    with dissolve

    $ forest_bg_change = False

    menu:
        "You found bandits hideout inside an old abandoned castle."

        "Attack them":
            "You carefully approach the hideout when a group of bandits attacks you."
        "Leave them be":
            show screen city_dark_forest
            $ global_flags.set_flag("keep_playing_music")
            jump forest_dark_continue

    call city_dark_forest_hideout_fight from _call_city_dark_forest_hideout_fight

    $ N = randint(1, 3)
    $ j = 0
    while j < N:
        scene bg forest_hideout
        with dissolve

        "Another group is approaching you!"

        call city_dark_forest_hideout_fight from _call_city_dark_forest_hideout_fight_1

        $ j += 1

    # Could be wrong... but this looks like double :(
    # if persistent.battle_results:
    #     call screen give_exp_after_battle(hero.team, exp)

    show screen city_dark_forest
    scene bg forest_hideout
    with dissolve

    "After killing all bandits, you found stash with loot."

    $ give_to_mc_item_reward("treasure", price=300)
    if locked_dice(50):
        $ give_to_mc_item_reward("treasure", price=300)
    $ give_to_mc_item_reward("restore", price=100)
    if locked_dice(50):
        $ give_to_mc_item_reward("restore", price=200)
    if locked_dice(50):
        $ give_to_mc_item_reward("armor", price=300)
    if locked_dice(50):
        $ give_to_mc_item_reward("weapon", price=300)
    jump forest_dark_continue

label city_dark_forest_hideout_fight:
    python:
        enemy_team = Team(name="Enemy Team", max_size=3)
        for i in range(3):
            mob_id = choice(["Samurai", "Warrior", "Archer", "Soldier", "Barbarian", "Orc", "Infantryman", "Thug", "Mercenary", "Dark Elf Archer"])
            min_lvl = mobs[mob_id]["min_lvl"]
            mob = build_mob(id=mob_id, level=randint(min_lvl, min_lvl+20))
            enemy_team.add(mob)

    $ result = interactions_pick_background_for_fight("forest")
    $ result = run_default_be(enemy_team, background=result,
                              slaves=True, prebattle=False,
                              death=False, give_up="escape",
                              use_items=True)
    if result is True:
        scene expression forest_location
        if persistent.battle_results:
            call screen give_exp_after_battle(hero.team, enemy_team)
        $ del result, enemy_team

    elif result == "escaoe":
        $ be_hero_escaped(hero.team)
        $ del result, enemy_team
        scene black
        pause 1.0
        jump forest_dark_continue
    else:
        jump game_over
    return

label city_dark_forest_fight:
    $ forest_bg_change = False

    $ enemy_team = Team(name="Enemy Team", max_size=3)
    python hide:
        mob = choice(["slime", "were", "harpy", "goblin", "wolf", "bear",
                      "druid", "rat", "undead", "butterfly"])
        et_len = min(len(hero.team) + 1, 3)

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
            et_len = 3
        elif mob == "wolf":
            msg = "A pack of wolves picks you for dinner."
            mob_ids = ["Wolf", "Black Wolf"]
            et_len = 3
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
            et_len = 3
        else:
            msg = "You encountered a small group of aggressive giant butterflies."
            mob_ids = ["Black Butterfly"]

        for i in range(et_len):
            mob_id = choice(mob_ids)
            min_lvl = mobs[mob_id]["min_lvl"]
            mob = build_mob(id=mob_id, level=randint(min_lvl, min_lvl+20))
            enemy_team.add(mob)

        narrator(msg)

    $ result = interactions_pick_background_for_fight("forest")
    $ result = run_default_be(enemy_team, background=result,
                              slaves=True, prebattle=False,
                              death=False, give_up="escape",
                              use_items=True)

    if result is True:
        scene expression forest_location

        if persistent.battle_results:
            call screen give_exp_after_battle(hero.team, enemy_team)
        $ give_to_mc_item_reward(["treasure", "scrolls", "consumables",
                                 "potions", "restore"])
        $ del result, enemy_team
        jump forest_dark_continue
    elif result == "escape":
        $ be_hero_escaped(hero.team)
        $ del result, enemy_team
        scene black
        pause 1.0
        jump forest_dark_continue
    else:
        jump game_over

label dark_forest_girl_meet:
    $ hero.set_flag("dnd_dark_forest_girl")
    python:
        temp = set(gm.get_all_girls()) | set(hero.chars)
        choices = list(i for i in chars.values() if
                       i not in temp and i.location != pytfall.jail and
                       not i.arena_active)
        temp = ["Homebody", "Indifferent", "Coward"]
        choices = list(i for i in choices if not any(trait in temp for trait in i.traits))
    if choices:
        $ char = random.choice(choices)
        $ spr = char.get_vnsprite()
        show expression spr at center with dissolve
        "You found a girl lost in the woods and escorted her to the city."
        $ char.override_portrait("portrait", "happy")
        $ char.show_portrait_overlay("love", "reset")
        $ char.say("She happily kisses you in the chick as a thanks. Maybe you should try to find her in the city later.")
        if char.get_stat("disposition") < 450:
            $ char.gfx_mod_stat("disposition", 100)
        else:
            $ char.gfx_mod_stat("disposition", 50)
        $ char.gfx_mod_stat("affection", affection_reward(char))
        hide expression spr with dissolve
        $ char.restore_portrait()
        $ char.hide_portrait_overlay()
        $ del spr, temp, choices # FIXME del char if possible
        $ global_flags.set_flag("keep_playing_music")
        jump forest_dark_continue
    $ del temp, choices

label mc_action_city_dark_forest_river:
    play world "forest_lake.ogg"
    $ global_flags.set_flag("keep_playing_music")
    $ hero.set_flag("dnd_dark_forest_river")
    $ forest_bg_change = False
    scene bg forest_lake
    with dissolve
    "You found a river. Fresh, clean water restores some of your vitality."
    python:
        for i in hero.team:
            i.gfx_mod_stat("vitality", i.get_max("vitality")/2)
    jump forest_dark_continue
