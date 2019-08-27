label interactions_invite_ice:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end

    $ n = iam.flag_days_checker(char, "interactions_invite", 2)
    if n >= 2:
        $ del n
        if char.status == "free":
            $ iam.refuse_invite_too_many(char)

            $ char.gfx_mod_stat("disposition", -randint(3, 6))
            $ char.gfx_mod_stat("affection", -randint(0, 3))
        else:
            $ iam.slave_refuse(char)

            $ char.gfx_mod_stat("disposition", -randint(1, 2))
        jump girl_interactions

    if not iam.want_ice(char):
        $ del n
        $ char.gfx_mod_stat("disposition", -randint(1, 2))
        $ iam.int_reward_exp(char, .1)
        $ iam.refuse_invite_any(char)
        jump girl_interactions

    $ iam.accept_invite(char)

    scene bg icestand
    with dissolve

    if iam.label_cache != "city_beach_cafe_main":
        $ iam.img = iam.select_beach_img_tags(char, "beach_cafe")

    if not hero.take_money(randint(10, 25), reason="Icecream"):
        if n == 0 and (check_friends(char) or check_lovers(char)) and char.gold > 500:
            $ char.take_money(randint(10, 25), reason="Icecream")

            $ iam.invite_pay(char)
            # no penalty, it is the thought what counts
        else:
            $ del n
            $ iam.invite_not_pay(char)

            $ char.gfx_mod_stat("disposition", -randint(3, 6))
            $ char.gfx_mod_stat("affection", -randint(0, 3))
            if char.get_stat("joy") > 60:
                $ char.gfx_mod_stat("joy", -randint(1, 2))
            if hero.get_stat("joy") > 60:
                $ hero.gfx_mod_stat("joy", -randint(1, 2))
            jump girl_interactions_end

    $ iam.ice_reward((hero, char), 6 / (n+1))
    $ iam.int_reward_exp(char)

    $ iam.icecream_line(char)

    $ iam.restore_img()
    $ del n
    jump girl_interactions

label interactions_invite_cafe:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end

    $ n = iam.flag_days_checker(char, "interactions_invite", 2)
    if n >= 2:
        $ del n
        if char.status == "free":
            $ iam.refuse_invite_too_many(char)

            $ char.gfx_mod_stat("disposition", -randint(3, 6))
            $ char.gfx_mod_stat("affection", -randint(0, 3))
        else:
            $ iam.slave_refuse(char)

            $ char.gfx_mod_stat("disposition", -randint(1, 2))
        jump girl_interactions

    if not iam.want_cafe(char):
        $ del n
        $ char.gfx_mod_stat("disposition", -randint(1, 2))
        $ iam.int_reward_exp(char, .1)
        $ iam.refuse_invite_any(char)
        jump girl_interactions

    $ iam.accept_invite(char)

    scene bg cafe
    with dissolve

    if iam.label_cache != "main_street":
        $ iam.set_img("girlmeets", "happy", "outdoors", "urban", exclude=["swimsuit", "indoor", "wildness", "suburb", "beach", "pool", "onsen", "nature"], type="reduce", gm_mode=True, add_mood=False)

    if not hero.take_money(randint(10, 25), reason="Cafe"):
        if n == 0 and (check_friends(char) or check_lovers(char)) and char.gold > 500:
            $ char.take_money(randint(10, 25), reason="Cafe")

            $ iam.invite_pay(char)
            # no penalty, it is the thought what counts
        else:
            $ del n
            $ iam.invite_not_pay(char)

            $ char.gfx_mod_stat("disposition", -randint(3, 6))
            $ char.gfx_mod_stat("affection", -randint(0, 3))
            if char.get_stat("joy") > 60:
                $ char.gfx_mod_stat("joy", -randint(1, 2))
            if hero.get_stat("joy") > 60:
                $ hero.gfx_mod_stat("joy", -randint(1, 2))
            jump girl_interactions_end

    $ iam.cafe_reward((hero, char), 6 / (n+1))
    $ iam.int_reward_exp(char)

    $ iam.cafe_line(char)

    $ iam.restore_img()
    $ del n
    jump girl_interactions

label interactions_invite_eat:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end

    $ n = iam.flag_days_checker(char, "interactions_invite", 7)
    if n >= 7:
        $ del n
        if char.status == "free":
            $ iam.refuse_invite_too_many(char)

            $ char.gfx_mod_stat("disposition", -randint(3, 6))
            $ char.gfx_mod_stat("affection", -randint(0, 3))
        else:
            $ iam.slave_refuse(char)

            $ char.gfx_mod_stat("disposition", -randint(1, 2))
        jump girl_interactions

    if not iam.want_eat(char):
        $ char.gfx_mod_stat("disposition", -randint(1, 3))
        $ iam.int_reward_exp(char, .1)
        $ iam.refuse_invite_any(char)
        jump girl_interactions

    $ iam.accept_invite(char)

    scene bg cafe
    with dissolve

    if iam.label_cache != "main_street":
        $ iam.set_img("girlmeets", ("urban", "outdoors", None), ("eating", None), ("happy", None), exclude=["swimsuit", "wildness", "suburb", "beach", "pool", "onsen", "nature"], type="ptls", gm_mode=True, add_mood=False)

    if not hero.take_money(randint(250, 400), reason="Cafe"):
        if n == 0 and check_lovers(char) and char.gold > 5000:
            $ char.take_money(randint(250, 400), reason="Cafe")
            # add penalty, but continue
            $ iam.dispo_reward(char, -randint(12, 16))
            $ char.gfx_mod_stat("affection", -randint(3, 6))

            $ iam.invite_pay(char)
        else:
            $ del n
            $ iam.dispo_reward(char, -randint(12, 16))
            $ char.gfx_mod_stat("affection", -randint(10, 20))
            if char.get_stat("joy") > 60:
                $ char.gfx_mod_stat("joy", -randint(1, 2))
            if hero.get_stat("joy") > 60:
                $ hero.gfx_mod_stat("joy", -randint(1, 2))

            $ iam.invite_not_pay(char)
            jump girl_interactions_end

    $ iam.eat_reward((hero, char), 25 / (n+1))
    $ iam.int_reward_exp(char)

    $ iam.eating_line((char, ))

    $ iam.restore_img()
    $ del n
    jump girl_interactions

label interactions_invite_study:
    if hero.PP < 100 - iam.PP_COST: # PP_PER_AP
        $ hero.PP += iam.PP_COST
        $ PyTGFX.message("You don't have time (Action Point) for that!")
        jump girl_interactions

    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end

    $ n = iam.flag_days_checker(char, "interactions_study")
    if n >= 2:
        $ del n
        if char.status == "free":
            $ iam.refuse_invite_too_many(char)

            $ char.gfx_mod_stat("disposition", -randint(3, 6))
            $ char.gfx_mod_stat("affection", -randint(0, 3))
        else:
            $ iam.slave_refuse(char)

            $ char.gfx_mod_stat("disposition", -randint(1, 2))
        jump girl_interactions

    if not iam.want_study(char, None):
        $ del n
        $ char.gfx_mod_stat("disposition", -randint(1, 2))
        $ iam.int_reward_exp(char, .1)
        $ iam.refuse_invite_any(char)
        jump girl_interactions

    $ iam.accept_invite(char)

    scene bg academy_town
    with dissolve

    hide screen girl_interactions
    call screen library_study
    $ topic = _return
    if not topic:
        char.say "Well..."
        $ del topic, n
        jump girl_interactions
    $ topic = topic[2]

    show screen girl_interactions

    if not iam.want_study(char, topic):
        $ iam.refuse_invite_any(char)
        $ iam.int_reward_exp(char, .05)
        $ iam.flag_days_checker(char, "interactions_study")
        $ del topic, n
        jump girl_interactions

    if not hero.take_money(500, reason="Library Fee"):
        if dice((hero.tier - char.tier)*50) and char.gold > 5000:
            $ char.take_money(500, reason="Library Fee")
            # no penalty, since the char is going to learn
            $ iam.invite_pay(char)
        else:
            $ iam.dispo_reward(char, -randint(3, 6))
            $ char.gfx_mod_stat("affection", -randint(0, 3))

            $ iam.invite_not_pay(char)
            $ del topic, n
            jump girl_interactions_end
    
    if iam.label_cache != "main_street":
        $ iam.set_img("girlmeets", ("indoors", None), ("schoolgirl", None), ("studying", None), exclude=["swimsuit", "wildness", "beach", "pool", "urban", "stage", "onsen"], type="ptls", gm_mode=True, add_mood=False)

    # restore interaction-cost before take_ap below...
    $ hero.PP += iam.PP_COST
    $ char.PP += iam.PP_COST

    $ study_pp = int(hero.PP / 100) # PP_PER_AP
    $ study_ap = "You have %d AP. How much time do you want to spend studying?" % study_pp
    $ study_ap = renpy.call_screen("digital_keyboard", line=study_ap)
    if not study_ap:
        "You wanted to leave, but since you already paid for the entry you decided to stay for a bit."
        $ study_ap = 1
    else:
        if study_ap > study_pp:
            $ study_ap = study_pp
        $ study_pp = int(char.PP / 100) # PP_PER_AP
        if study_ap > study_pp:
            # char does not have enough time
            $ study_ap = study_pp
            $ study_pp = None

    $ iam.study_reward(Team(implicit=(hero, char)), topic, study_ap, 7 / (n+1))
    $ iam.int_reward_exp(char)

    $ gain = hero.tier - char.tier 
    if gain >= 0:
        $ iam.study_line_learn(char)
    else:
        $ iam.study_line_teach(char)

    $ hero.take_ap(study_ap)
    $ char.take_ap(study_ap)
    if study_pp is None:
        "You wanted to study longer, but [char.name] had to leave."
    # prevent repetition based on the char's gain
    if gain >= 0:
        # char learned more
        $ study_ap /= 1 + min(2, gain)
    else:
        # hero learned more
        $ study_ap *= 1 - gain
    $ study_ap -= 1
    if study_ap > 0:
        $ iam.flag_days_checker(char, "interactions_study", study_ap)
    # cleanup
    $ del topic, n, study_ap, study_pp, gain
    $ iam.restore_img()
    jump girl_interactions
