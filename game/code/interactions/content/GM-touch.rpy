label interactions_hug:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_hug")
    $ n = 2 + iam.repeating_lines_limit(char)
    if check_lovers(char):
        $ n += 2
    elif check_friends(char) or "Half-Sister" in char.traits:
        $ n += 1

    $ temp = iam.want_hug(char)
    if temp is True:
        if m > n:
            $ char.gfx_mod_stat("disposition", -randint(8, 12))
            $ char.gfx_mod_stat("affection", -randint(1, 3))
            if char.get_stat("joy") > 40:
                $ char.gfx_mod_stat("joy", -randint(1, 3))
            if hero.get_stat("joy") > 70:
                $ hero.gfx_mod_stat("joy", -randint(0, 1))

            $ iam.refuse_sex_too_many(char)
        else:
            $ char.gfx_mod_stat("disposition", randint(16, 20))
            $ char.gfx_mod_stat("affection", affection_reward(char, 1.4))
            if char.get_stat("joy") < 70:
                $ char.gfx_mod_stat("joy", randint(0, 1))
            $ iam.int_reward_exp(char)

            $ iam.accept_hug(char)

            if 2*m <= n and dice(50) and dice(char.get_stat("joy")-20):
                $ narrator(choice(["You feel especially close.", "It felt like it could go on forever."]))
                $ char.gfx_mod_stat("joy", randint(0, 1))
                if hero.get_stat("joy") < 80:
                    $ hero.gfx_mod_stat("joy", randint(0, 1))
                $ char.gfx_mod_stat("disposition", randint(8, 10))
                $ iam.int_reward_exp(char)
                $ char.gfx_mod_stat("affection", affection_reward(char, .1))
    else:
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status == "free":
            $ char.gfx_mod_stat("disposition", -randint(16, 20))
            $ char.gfx_mod_stat("affection", -randint(4,6))
            if char.get_stat("joy") > 80:
                $ char.gfx_mod_stat("joy", -randint(0, 1))

            $ iam.refuse_hug(char)

            if m > 1 or temp == "blowoff":
                $ char.set_flag("cnd_interactions_blowoff", day+1)
            $ del temp, m, n
            jump girl_interactions_end
        else:
            if m > n:
                $ char.gfx_mod_stat("disposition", -randint(8, 12))
                $ char.gfx_mod_stat("affection", -randint(1, 3))
                if char.get_stat("joy") > 40:
                    $ char.gfx_mod_stat("joy", -randint(1, 3))

                $ iam.refuse_sex_too_many(char)
            else:
                $ iam.slave_refuse(char)
    $ del temp, m, n
    jump girl_interactions

label interactions_touchcheek:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_cheek")
    $ n = 1 + iam.repeating_lines_limit(char)
    if check_lovers(char):
        $ n += 1
    elif char.get_stat("affection") < 400:
        $ n -= 1

    $ temp = iam.want_cheektouch(char)
    if temp is True:
        if m > n or (iam.gender_mismatch(char) and char.status == "free"):
            if hero.get_stat("joy") > 70:
                $ hero.gfx_mod_stat("joy", -randint(0, 1))
            if m > 1 or not iam.gender_mismatch(char):
                $ char.gfx_mod_stat("disposition", -randint(8, 12))
                $ char.gfx_mod_stat("affection", -randint(1,3))
                if char.get_stat("joy") > 30:
                    $ char.gfx_mod_stat("joy", -randint(0, 1))

                $ iam.refuse_sex_too_many(char)
            else:
                $ iam.refuse_because_of_gender(char)
        else:
            $ iam.int_reward_exp(char)
            $ char.gfx_mod_stat("affection", affection_reward(char, 1.6))
            $ char.gfx_mod_stat("disposition", randint(30, 36))
            if char.get_stat("joy") < 70:
                $ char.gfx_mod_stat("joy", randint(0, 1))

            $ char.override_portrait("portrait", "shy")
            $ char_dispo = char.get_stat("affection")
            if check_lovers(char):
                char.say "While one of your hand is on [char.pd] cheek, the other slides down [char.pd] body."
            elif char_dispo >= 600:
                char.say "[char.pC] buries [char.pd] head in your palm."
            elif char_dispo >= 400:
                char.say "You put your palm on [char.pd] cheek passionately."
            else:
                char.say "You gently stroke her cheek with your hand."
            $ char.restore_portrait()

            if iam.incest(char) and not(check_lovers(char)) and char_dispo < 400:
                "[char.pC] looks a bit uncomfortable."
                $ iam.incest_touch_cheek(char)
            else:
                $ iam.accept_touch_cheek(char)

            if 2*m <= n and dice(50) and dice(char.get_stat("joy")-40) and dice(hero.get_stat("joy")-40):
                $ narrator(choice(["You feel especially close.", "It felt like it could go on forever."]))
                $ char.gfx_mod_stat("joy", randint(0, 1))
                if hero.get_stat("joy") < 80:
                    $ hero.gfx_mod_stat("joy", randint(0, 1))
                $ char.gfx_mod_stat("disposition", randint(1, 2))
                $ char.gfx_mod_stat("affection", affection_reward(char, .8))
                $ iam.int_reward_exp(char)

            $ del char_dispo
    else:
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status == "free":
            $ char.gfx_mod_stat("disposition", -randint(20, 25))
            $ char.gfx_mod_stat("affection", -randint(3,5))
            if char.get_stat("joy") > 80:
                $ char.gfx_mod_stat("joy", -randint(0, 1))

            $ iam.refuse_touch_cheek(char)

            if m > 1 or temp == "blowoff":
                $ char.set_flag("cnd_interactions_blowoff", day+1)
            $ del temp, m, n
            jump girl_interactions_end
        else:
            if m > n:
                $ char.gfx_mod_stat("disposition", -randint(16, 20))
                $ char.gfx_mod_stat("affection", -randint(3,5))
                if char.get_stat("joy") > 30:
                    $ char.gfx_mod_stat("joy", -randint(2, 4))

                $ iam.refuse_sex_too_many(char)
            else:
                $ iam.slave_refuse(char)
    $ del temp, m, n
    jump girl_interactions

label interactions_grabbutt:
    $ narrator(choice(["You reach out and brush your hands across her ass.", "You put your hand against her firm rear and grind against it.", "You reach into her gap and she gasps as you slide your hand across and stroke her puckered hole.", "She gasps as you reach under her and lightly stroke her ass.", "You slide a hand up her inner thigh, she moans a little as it slides between her cheeks."]))
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_slapbutt")
    $ n = 2 + iam.repeating_lines_limit(char)
    if check_lovers(char) or "Nymphomaniac" in char.traits:
        $ n += 1
    elif (iam.incest(char) and char.get_stat("affection") < 500) or "Frigid" in char.traits:
        $ n -= 1

    $ temp = iam.want_buttgrab(char)
    if temp is True:
        if m > n or (iam.gender_mismatch(char) and char.status == "free"):
            if hero.get_stat("joy") > 70:
                $ hero.gfx_mod_stat("joy", -randint(0, 1))
            if m > 1 or not iam.gender_mismatch(char):
                $ char.gfx_mod_stat("disposition", -randint(8, 12))
                $ char.gfx_mod_stat("affection", -randint(4,6))
                if char.get_stat("joy") > 30:
                    $ char.gfx_mod_stat("joy", -randint(1, 3))

                $ iam.refuse_sex_too_many(char)
            else:
                $ iam.refuse_because_of_gender(char)
        else:
            $ char.gfx_mod_stat("disposition", randint(8, 12))
            $ char.gfx_mod_stat("affection", affection_reward(char, 1.2))
            $ iam.int_reward_exp(char)

            $ iam.accept_grab_butt(char)

            if 2*m <= n and dice(50) and dice(char.get_stat("joy")-20):
                $ narrator(choice(["[char.name] looks at you with a mischievous smile.", "[char.name] looks at you with glowing eyes."]))
                $ char.gfx_mod_stat("joy", randint(1, 2))
                if hero.get_stat("joy") < 80:
                    $ hero.gfx_mod_stat("joy", randint(0, 1))
                $ char.gfx_mod_stat("disposition", randint(1, 2))
                $ iam.int_reward_exp(char)
                $ char.gfx_mod_stat("affection", affection_reward(char, .4))
    else:
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status == "free":
            $ char.gfx_mod_stat("disposition", -randint(24, 30))
            $ char.gfx_mod_stat("affection", -randint(5,7))
            if char.get_stat("joy") > 80:
                $ char.gfx_mod_stat("joy", -randint(0, 1))

            $ iam.refuse_grab_butt(char)

            if m > 1 or temp == "blowoff":
                if iam.silent_check_for_escalation(char, 10*m):
                    $ del temp, m, n
                    jump interactions_escalation
                $ char.set_flag("cnd_interactions_blowoff", day+2)

            $ del temp, m, n
            jump girl_interactions_end
        else:
            if m > n:
                $ char.gfx_mod_stat("disposition", -randint(8, 12))
                $ char.gfx_mod_stat("affection", -randint(4,6))
                if char.get_stat("joy") > 30:
                    $ char.gfx_mod_stat("joy", -randint(1, 3))

                $ iam.refuse_sex_too_many(char)
            else:
                $ iam.slave_refuse(char)
    $ del temp, m, n
    jump girl_interactions


###### j4
label interactions_grabbreasts:
    $ narrator(choice(["You reach out and massage her glorious breasts.", "You pass your hands gently over her warm breasts.", "Her nipples catch lightly on your fingers as you grasp her warm flesh, you can feel them stiffen.", "She gasps as you lightly thumb her rigid nipples."]))
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_grabbreasts")

    $ n = 2 + iam.repeating_lines_limit(char)
    if check_lovers(char) or "Nymphomaniac" in char.traits:
        $ n += 1
    elif (iam.incest(char) and char.get_stat("affection") < 500) or "Frigid" in char.traits:
        $ n -= 1

    $ temp = iam.want_breastgrab(char)
    if temp is True:
        if m > n or (iam.gender_mismatch(char) and char.status == "free"):
            if hero.get_stat("joy") > 70:
                $ hero.gfx_mod_stat("joy", -randint(0, 1))
            if m > 1 or not iam.gender_mismatch(char):
                $ char.gfx_mod_stat("disposition", -randint(8, 12))
                $ char.gfx_mod_stat("affection", -randint(5,7))
                if char.get_stat("joy") > 30:
                    $ char.gfx_mod_stat("joy", -randint(1, 3))

                $ iam.refuse_sex_too_many(char)
            else:
                $ iam.refuse_because_of_gender(char)
        else:
            $ iam.int_reward_exp(char)
            $ char.gfx_mod_stat("disposition", randint(8, 12))
            $ char.gfx_mod_stat("affection", affection_reward(char, 1.3))

            $ iam.accept_grab_breast(char)

            if 2*m <= n and dice(50) and dice(char.get_stat("joy")-40):
                $ narrator(choice(["[char.pC] looks at you with a mischievous smile.", "[char.name] looks at you with glowing eyes."]))
                $ char.gfx_mod_stat("joy", randint(1, 2))
                if hero.get_stat("joy") < 80:
                    $ hero.gfx_mod_stat("joy", randint(0, 1))
                $ char.gfx_mod_stat("disposition", randint(1, 2))
                $ char.gfx_mod_stat("affection", affection_reward(char, .6))
                $ iam.int_reward_exp(char)
    else:
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status == "free":
            $ char.gfx_mod_stat("disposition", -randint(32, 40))
            $ char.gfx_mod_stat("affection", -randint(7,9))
            if char.get_stat("joy") > 80:
                $ char.gfx_mod_stat("joy", -randint(0, 1))

            $ iam.refuse_grab_breast(char)

            if m > 1 or temp == "blowoff":
                if iam.silent_check_for_escalation(char, 20*m):
                    $ del temp, m, n
                    jump interactions_escalation
                $ char.set_flag("cnd_interactions_blowoff", day+2)

            $ del temp, m, n
            jump girl_interactions_end
        else:
            if m > n:
                $ char.gfx_mod_stat("disposition", -randint(8, 12))
                $ char.gfx_mod_stat("affection", -randint(5,7))
                if char.get_stat("joy") > 30:
                    $ char.gfx_mod_stat("joy", -randint(1, 3))

                $ iam.refuse_sex_too_many(char)
            else:
                $ iam.slave_refuse(char)
    $ del temp, m, n
    jump girl_interactions

label interactions_kiss:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if iam.check_for_minor_bad_stuff(char):
        jump girl_interactions
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_kiss")

    $ n = 2 + iam.repeating_lines_limit(char)
    if "Nymphomaniac" in char.traits or check_lovers(char):
        $ n += 1
    elif (iam.incest(char) and char.get_stat("affection") < 500) or "Frigid" in char.traits:
        $ n -= 1

    $ temp = iam.want_kiss(char)
    if temp is True:
        if m > n or (iam.gender_mismatch(char) and char.status == "free"):
            if hero.get_stat("joy") > 70:
                $ hero.gfx_mod_stat("joy", -randint(0, 1))
            if m > 1 or not iam.gender_mismatch(char):
                $ char.gfx_mod_stat("disposition", -randint(8, 12))
                $ char.gfx_mod_stat("affection", -randint(1,3))
                if char.get_stat("joy") > 30:
                    $ char.gfx_mod_stat("joy", -randint(0, 1))

                $ iam.refuse_sex_too_many(char)
            else:
                $ iam.refuse_because_of_gender(char)
        else:
            $ iam.int_reward_exp(char)
            $ char.gfx_mod_stat("affection", affection_reward(char, 1.5))
            $ char.gfx_mod_stat("disposition", randint(24, 30))

            $ char.override_portrait("portrait", "shy")
            $ char.show_portrait_overlay("love", "reset")
            $ char_dispo = char.get_stat("affection")
            if check_lovers(char):
                char.say "Your hands slide down [char.pd] body as your lips press [char.pp]."
            elif char_dispo >= 600:
                char.say "You two kiss deeply and passionately. [char.pdC] tongue dances around yours."
            elif char_dispo >= 400:
                char.say "You two kiss deeply and passionately."
            else:
                char.say "Your lips gently slide across [char.pp]."
            $ char.restore_portrait()
            $ char.hide_portrait_overlay()

            if iam.incest(char) and not(check_lovers(char)) and char_dispo < 650:
                "[char.pC] looks a bit uncomfortable."
                $ iam.incest_kiss(char)
            else:
                $ iam.accept_kiss(char)

            if 2*m <= n and dice(50) and dice(char.get_stat("joy")-40) and dice(hero.get_stat("joy")-40):
                $ narrator(choice(["You feel especially close.", "It felt like it could go on forever."]))
                $ char.gfx_mod_stat("joy", randint(0, 1))
                if hero.get_stat("joy") < 80:
                    $ hero.gfx_mod_stat("joy", randint(0, 1))
                $ char.gfx_mod_stat("disposition", randint(1, 2))
                $ char.gfx_mod_stat("affection", affection_reward(char, .7))
                $ iam.int_reward_exp(char)

            $ del char_dispo
    else:
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status == "free":
            $ char.gfx_mod_stat("disposition", -randint(30, 35))
            $ char.gfx_mod_stat("affection", -randint(3,5))
            if char.get_stat("joy") > 80:
                $ char.gfx_mod_stat("joy", -randint(0, 1))

            $ iam.refuse_kiss(char)

            if m > 1 or temp == "blowoff":
                $ char.set_flag("cnd_interactions_blowoff", day+2)
            $ del temp, m, n
            jump girl_interactions_end
        else:
            if m > n:
                $ char.gfx_mod_stat("disposition", -randint(20, 25))
                $ char.gfx_mod_stat("affection", -randint(3,5))
                if char.get_stat("joy") > 30:
                    $ char.gfx_mod_stat("joy", -randint(2, 4))

                $ iam.refuse_sex_too_many(char)
            else:
                $ iam.slave_refuse(char)
    $ del temp, m, n
    jump girl_interactions
