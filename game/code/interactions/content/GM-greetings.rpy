label girl_interactions_greeting:
    if iam.check_for_bad_stuff_greetings(char):
        return
    $ m = iam.flag_count_checker(char, "flag_interactions_greeting") # probably not the most elegant way to count how many times greeting was shown this day already
    if m < 1:
        call klepto_stealing from _call_klepto_stealing
    if check_lovers(char) and dice(60):
        $ iam.greet_lover(char)
    elif m < 2:
        $ char_dispo = char.get_stat("disposition")
        if char_dispo <= -200:
            if char.status == "free":
                $ iam.greet_bad(char)
            else:
                if char_dispo <= -500:
                    $ char.override_portrait("portrait", "sad")
                    char.say "..."
                    $ char.restore_portrait()
                else:
                    $ iam.greet_bad_slave(char)

        elif check_friends(char) or (char_dispo >= 500 and char.status <> "slave") or (char_dispo >= 850 and char.status == "slave"):
            $ iam.greet_good(char)
        elif char_dispo and char.status == "slave":
            $ iam.greet_good_slave(char)
        else:
            $ iam.greet_neutral(char)
        $ del char_dispo
    elif m < 3:
 # when MC approaches character not the first time; after 4 times we stop showing greetings at all
        if char.get_stat("disposition") <= -50:
            $ char.override_portrait("portrait", "angry")
            char.say "..."
            $ char.restore_portrait()
        else:
            $ iam.greet_many(char)

    if m < 1:
        # meeting the first time -> check if the character has something to tell the MC
        if all((check_submissivity(char) == 1,
                iam.become_lovers(char) is True,
                not iam.gender_mismatch(char, just_sex=False),
                not iam.incest(char),
                not check_lovers(char),
                not char.flag("tried_to_lover"),
                not char.flag("cnd_tried_to_lover"),
                not char.flag("quest_cannot_be_lover"),
                dice(10))):
            # propose relationship
            $ iam.offer_relationship(char)
            menu:
                "Do you want to be [char.pd] lover?"
                "Yes":
                    $ set_lovers(char)
                    $ char.gfx_mod_stat("affection", affection_reward(char))
                    $ char.gfx_mod_stat("joy", 25)
                    if hero.get_stat("joy") < 80:
                        $ hero.gfx_mod_stat("joy", randint(1, 2))
                    $  iam.glad(char)
                "No":
                    $ char.set_flag("cnd_tried_to_lover", day+7)

                    $ char.override_portrait("portrait", "indifferent")
                    $ iam.say_line(char, ("...", "I see...", "Maybe later then..."))
                    $ char.gfx_mod_stat("joy", -randint(4, 8))
                    $ char.restore_portrait()
                "No, and do not bother me again... Ever!":
                    $ char.set_flag("tried_to_lover")

                    $ char.override_portrait("portrait", "sad")
                    $ iam.say_line(char, ("...", "I see..."))
                    $ char.gfx_mod_stat("joy", -randint(12, 20))
                    $ char.restore_portrait()
        if all(("Horny" in char.effects,
                check_lovers(char),
                not char.flag("quest_cannot_be_fucked"),
                iam.silent_check_for_bad_stuff(char))):
            # propose sex
            $ iam.offer_sex(char)
            menu:
                "Do you wish to have sex with [char.name]?"
                "Yes":
                    $ char.disable_effect("Horny")
                    $ del m
                    jump interactions_sex_scene_select_place
                "No":
                    $ char.override_portrait("portrait", "indifferent")
                    $ iam.say_line(char, ("...", "I see...", "Maybe later then..."))
                    $ char.gfx_mod_stat("joy", -randint(1, 5))
                    $ char.restore_portrait()

        elif "Fluffy Companion" in hero.effects:
            # play with the cat
            $ cat = npcs["sad_cat"]
            $ cat.override_portrait("portrait", "happy")
            cat.say "Meow!"
            $ cat.restore_portrait()
            $ iam.cat_line(char)
            if char.get_stat("disposition") <= 500:
                $ char.gfx_mod_stat("disposition", locked_random("randint", 5, 10))
            if char.get_stat("affection") <= 500:
                $ char.gfx_mod_stat("affection", affection_reward(char, .5))
            $ del cat
    $ del m
    return

label interactions_blowoff(char, exit):
    $ hs()
    show expression char.get_vnsprite() as vn_sprite
    with dissolve

    $ iam.blowoff(char)

    hide vn_sprite
    with dissolve

    jump expression exit

label klepto_stealing:
    if "Kleptomaniac" in char.traits:
        if dice((hero.get_skill("security")/4.0 - char.get_stat("agility"))/10.0) and dice(hero.get_stat("luck")):
            "Just as you begin to talk to [char.name], you notice that [char.p] tried to steal from you."
            menu:
                "How do you react?"
                "Call the guards!":
                    $ iam.apology(char)
                    menu:
                        "Ask [char.op], how [char.p] wants to resolve the issue":
                            if "SIW" in char.gen_occs and iam.silent_check_for_bad_stuff(char) and not char.flag("quest_cannot_be_fucked") and not iam.incest(char):
                                $ iam.offer_bribe_sex(char)
                                menu:
                                    "Agree":
                                        jump interactions_sex_scene_select_place
                                    "Forget about the theft-attempt":
                                        $ char.gfx_mod_stat("disposition", randint(2,5))
                                    "No":
                                        jump klepto_police
                            else:
                                $ money = min(100, char.gold/2)
                                if money != 0:
                                    $ iam.offer_bribe(char, money)
                                else:
                                    $ iam.refuse_bribe(char)
                                menu:
                                    "Accept" if money != 0:
                                        $ hero.add_money(money, reason="Extortion")
                                        $ char.take_money(money, reason="Extortion")
                                    "Forget about the theft-attempt":
                                        $ char.gfx_mod_stat("disposition", randint(2,5))
                                    "No":
                                        $ del money
                                        jump klepto_police
                                $ del money
                        "Ask for money":
                            $ money = min(50, char.gold/3)
                            if money != 0:
                                $ iam.offer_bribe(char, money)
                            else:
                                $ iam.refuse_bribe(char)
                            menu:
                                "Accept" if money != 0:
                                    $ hero.add_money(money, reason="Extortion")
                                    $ char.take_money(money, reason="Extortion")
                                "Forget about the theft-attempt":
                                    $ char.gfx_mod_stat("disposition", randint(1,3))
                                "No":
                                    $ del money
                                    jump klepto_police
                            $ del money
                        "Ignore the plea":
                            jump klepto_police
                    char.say "Thank you. It won't happen again, I promise."
                    extend " Please act like nothing happened..."
                "Ignore":
                    $ pass
        elif not dice(hero.get_stat("luck")):
            $ temp = randint(min(10, hero.gold/3), min(50, hero.gold/2))
            $ hero.take_money(temp, reason="Stolen!")
            $ char.add_money(temp, reason="Stealing")
            $ del temp
    return

label klepto_police:
    "You decided to call the guards."
    if dice(50):
        "A nearby city guard quickly arrived to the scene."
        extend " After you explained the situation, [char.name] is taken away."
        extend " Most probably [char.p] will spend a few days in jail now."
        $ char.gfx_mod_stat("disposition", -50)
        $ char.gfx_mod_stat("affection", -20)
        $ pytfall.jail.add_prisoner(char, "Theft", randint(1, 4))
        $ iam.remove_girl(char)
    else:
        "But there is none around to help."
        extend " You just made a fool of yourself. [char.name] scoffs at you."
        char.say "Hahh, call mommy and cry on her shoulder."
        extend " And leave me alone..."
        $ char.set_flag("cnd_interactions_blowoff", day+1)
    jump girl_interactions_end
