label interactions_sparring: # sparring with MC, for Combatant occupations only
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if char.get_stat("health") < char.get_max("health")/2:
        $ iam.refuse_because_tired(char)
        jump girl_interactions
    elif hero.get_stat("health") < hero.get_max("health")/2:
        "Unfortunately, you are not in shape for sparring."
        jump girl_interactions

    $ m = iam.flag_count_checker(char, "flag_interactions_sparring")
    if m > 1:
        $ del m
        $ iam.refuse_because_tired(char)
        jump girl_interactions
    $ del m

    $ iam.sparring_start(char)
    hide screen girl_interactions

    $ last_track = renpy.music.get_playing("world")
    python hide:
        pre_aps = char.PP
        back = iam.select_background_for_fight(iam.label_cache)

        enemy_team = Team(name="Enemy Team")
        enemy_team.add(char)

        your_team = Team(name="Your Team")
        your_team.add(hero)
        result = run_default_be(enemy_team, your_team=your_team, background=back, give_up="surrender")

        if result is True:
            char.gfx_mod_stat("disposition", randint(15, 30))
        elif result is False:
            ap_used = (pre_aps - char.PP)/100.0 # PP_PER_AP = 100
            char.gfx_mod_exp(exp_reward(char, hero, exp_mod=ap_used))
            char.gfx_mod_stat("disposition", randint(2, 5))

    if char.get_stat("health") < char.get_max("health")/2:
        $ char.set_stat("health", char.get_max("health")/2)
    if hero.get_stat("health") < hero.get_max("health")/2:
        $ hero.set_stat("health", hero.get_max("health")/2)
    if last_track:
        play world last_track
    $ del last_track

    $ iam.restore_img()

    show screen girl_interactions

    if iam.mode == "girl_interactions":
        scene expression iam.select_girl_room(char)
    else:
        show expression iam.bg_cache

    $ iam.sparring_end(char)
    jump girl_interactions

label interactions_girlfriend:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if check_lovers(char): # you never know
        "But you already are!"
        jump girl_interactions
    $ m = iam.flag_count_checker(char, "flag_interactions_girlfriend")
    if m > 1:
        $ del m
        $ iam.refuse_too_many(char)
        $ char.gfx_mod_stat("disposition", -randint(1, 5))
        $ char.gfx_mod_stat("affection", -randint(8, 12))
        if char.get_stat("joy") > 50:
            $ char.gfx_mod_stat("joy", -randint(0, 1))
        if hero.get_stat("joy") > 60:
            $ hero.gfx_mod_stat("joy", -randint(1, 2))
        jump girl_interactions
    $ del m
    if iam.gender_mismatch(char, just_sex=False):
        $ iam.refuse_because_of_gender(char)
        jump girl_interactions
    if iam.incest(char):
        $ iam.refuse_because_of_incest(char)
        jump girl_interactions

    if (char.flag("quest_cannot_be_lover") != True) and iam.become_lover(char):
        $ set_lovers(char)
        $ iam.int_reward_exp(char)
        $ char.gfx_mod_stat("affection", affection_reward(char))
        $ char.gfx_mod_stat("joy", 25)
        if hero.get_stat("joy") < 80:
            $ hero.gfx_mod_stat("joy", randint(1, 2))
        $ iam.accept_relationship(char)
    else:
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(1, 2))
        $ iam.refuse_relationship(char)
    jump girl_interactions

label interactions_movein:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if not check_lovers(char):
        $ iam.refuse_movein_disp(char)
        jump girl_interactions
    if hero.home is None or hero.home.get_daily_modifier() <= char.home.get_daily_modifier():
        $ iam.refuse_movein_home(char)
        jump girl_interactions
    if hero.home.get_dirt_percentage() > 50 and "Messy" not in char.traits:
        $ iam.refuse_movein_dirt(char)
        if hero.get_stat("joy") > 60:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        jump girl_interactions
    if hero.home.vacancies <= 0:
        $ iam.refuse_movein_space(char)
        jump girl_interactions

    $ char.home = hero.home

    $ iam.int_reward_exp(char)

    $ char.gfx_mod_stat("joy", 15)
    if hero.get_stat("joy") < 80:
        $ hero.gfx_mod_stat("joy", randint(0, 1))

    $ iam.accept_movein(char)

    jump girl_interactions

label interactions_moveout:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if char.home != hero.home: # you never know
        "But we aren't!"
        jump girl_interactions

    $ char.home = pytfall.city

    $ iam.int_reward_exp(char)

    $ char.gfx_mod_stat("joy", -15)
    $ char.gfx_mod_stat("disposition", -150)
    $ char.gfx_mod_stat("affection", -15)

    $ iam.accept_moveout(char)

    jump girl_interactions 

label interactions_breakup:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if not check_lovers(char): # you never know
        "But we aren't!"
        jump girl_interactions

    $ end_lovers(char)

    $ iam.int_reward_exp(char)

    $ iam.accept_lover_end_mc(char)

    $ char.gfx_mod_stat("joy", -25)
    if hero.get_stat("joy") > 70:
        $ hero.gfx_mod_stat("joy", -randint(0, 1))

    jump girl_interactions 

##### j3
init python:
    def char_value(c):
        n = 0
        value = 0
        for i in c.traits.basetraits:
            for s in i.base_stats:
                value += c.get_stat(s)
                n += 1
        return (value / n) if n else 0

label interactions_hire:
    if char.flag("quest_cannot_be_hired") or char.arena_active:
        $ iam.refuse_hire(char)
        jump girl_interactions

    python:
        herovalue = max(1, char_value(hero))
        charvalue = char_value(char)

        if DEBUG_LOG:
            devlog.info("Hero|Char: {}|{}".format(herovalue, charvalue))

        if hero.tier > char.tier:
            target_val = 50
        else:
            target_val = 150 + (char.tier-hero.tier)*400

    # Solve chance
    if char.get_stat("disposition") > ((target_val * charvalue) / herovalue):
        $ del herovalue, charvalue, target_val
        $ iam.accept_hire(char)
        menu:
            "Hire her? Her average wage will be [char.expected_wage]":
                $ iam.remove_girl(char)
                $ hero.add_char(char)
                hide screen girl_interactions

                $ iam.see_greeting = True

                jump expression iam.label_cache

            "Maybe later." :
                jump girl_interactions
    else:
        $ del herovalue, charvalue, target_val
        $ iam.refuse_hire(char)
        jump girl_interactions
