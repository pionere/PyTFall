init:
    image libido_hearth = "content/gfx/interface/icons/heartbeat.png"

# lines for the future male libido
# You're a little out of juice at the moment, you might want to wait a bit.
# The spirit is willing, but the flesh is spongy and bruised.
screen int_libido_level(sex_scene_libido):
    hbox:
        xpos 50
        ypos 85
        add "content/gfx/interface/icons/heartbeat.png" at sex_scene_libido_hearth(sex_scene_libido)
screen int_libido_level_zero:
    hbox:
        xpos 50
        ypos 85
        anchor (.5, .5)
        add im.Sepia("content/gfx/interface/icons/heartbeat.png")


label interactions_hireforsex: # we go to this label from GM menu hire for sex. it's impossible to hire lovers, however they never refuse to do it for free, unless too tired or something like that
    $ char.del_flag("raped_by_player")
    $ interactions_check_for_bad_stuff(char)
    $ m = interactions_flag_count_checker(char, "flag_interactions_hireforsex")
    if ct("Nymphomaniac"): # how many times one can hire the character per day
        $ n = 4
    elif ct("Frigid"):
        $ n = 1
    else:
        $ n = 2
    if m > n:
        $ del m, n
        call interactions_too_many_sex_lines from _call_interactions_too_many_sex_lines_1
        $ char.gfx_mod_stat("disposition", -randint(15, 35))
        if char.get_stat("joy") > 50:
            $ char.gfx_mod_stat("joy", -randint(2, 4))
            $ char.gfx_mod_stat("affection", -randint(3,5))
        jump girl_interactions
    $ del m, n

    if char.flag("quest_cannot_be_fucked") == True or (ct("Half-Sister") and not "Sister Lover" in hero.traits): # cannot hire h-s for that stuff, only seduce, seems reasonable
        call interactions_sex_disagreement from _call_interactions_sex_disagreement
        jump girl_interactions

    if char.get_stat("vitality") <= char.get_max("vitality")/4 or not char.has_ap(): # no sex with low vitality
        call interactions_refused_because_tired from _call_interactions_refused_because_tired_2
        jump girl_interactions

    $ price = 200 + 200 * char.tier

    if check_friends(char, hero):
        $ price = round(price * .9)
    elif char.get_stat("disposition") < -50:
        $ price = round(price * 1.3)
    if char.get_stat("affection") > 400:
        $ price = round(price * .8)
    elif char.get_stat("affection") < -50:
        $ price = round(price * 1.6)

    if interactions_gender_mismatch(char):
        $ price = round(price * 2.5)
    if ct("Nymphomaniac"):
        $ price = round(price * .95)
    elif ct("Frigid"):
        $ price = round(price * 1.25)
    if ct("Virgin"):
        $ price = round(price * 1.2)

    $ temp = round(hero.get_stat("charisma")/10)
    $ price = round(max(price*.35, price - temp))
    $ del temp

    if ct("Impersonal"):
        $ rc("Affirmative. It will be %d Gold." % price, "Calculations completed. %d Gold to proceed." % price)
    elif ct("Shy") and dice(50):
        $ rc("S-sure. %d Gold, please." % price, "*blushes* I-i-it will be %d Gold..." % price)
    elif ct("Imouto"):
        $ rc("Mmm, I think it should be %d Gold... No, wait, it will be %d Gold. I'm not very good with this stuff, hehe ♪" % (abs(price-randint(15,35)), price), "Ooh, you want to do 'it' with me, don't you? Ok, but it will cost you %d Gold." % price)
    elif ct("Dandere"):
        $ rc("I see. I shall do it for %d Gold." % price, "*she nods* %d Gold." % price)
    elif ct("Tsundere"):
        $ rc("I'll do it for %d Gold. You better be thankful for my low prices." % price, "Fine, fine. I hope you have %d Gold then." % price)
    elif ct("Kuudere"):
        $ rc("It will be %d. And no funny business, understood?" % price, "It will cost you %d Gold. Do you have so much money?" % price)
    elif ct("Kamidere"):
        $ rc("What's that? You want to hire me? I want %d Gold then, money up front." % price, "Hm? You want my body? Well of course you do. %d Gold, and you can have it." % price)
    elif ct("Bokukko"):
        $ rc("Sure thing. That will cost ya %d Gold." % price, "What'ya wanna? Ohoh, you wanna me, don't you? ♪ Alrighty, %d Gold and we good to go."  % price)
    elif ct("Ane"):
        $ rc("Let's see... How about %d Gold? Can you afford me? ♪" % price, "Hm? What's the matter? Need some... special service? For you my price is %d Gold ♪" % price)
    elif ct("Yandere"):
        $ rc("Fine, I want %d Gold. No bargaining." % price, "Well, I suppose we can, if you want to... It will cost %d Gold." % price)
    else:
        $ rc("You want to hire me? Very well, it will be %d Gold." % price, "Of course. For you my body costs %d Gold." % price)
    if hero.gold < price:
        "You don't have that much money."
        $ interactions_flag_count_checker(char, "flag_interactions_hireforsex") # additionally reduce the amount of tries
    else:
        menu:
            "She wants [price] Gold. Do you want to pay?"

            "Yes":
                if hero.take_money(price, reason="Sexual Services"):
                    $ char.add_money(price, reason="Sexual Services")
                    $ del price
                    jump interactions_sex_scene_select_place
                else:
                    "You don't have that much money."
                    $ interactions_flag_count_checker(char, "flag_interactions_hireforsex")
            "No":
                $ char.gfx_mod_stat("disposition", -randint(1, 3))
    $ del price
    jump girl_interactions

label interactions_sex_scene_select_place: # we go here if price for hiring is less than 0, ie no money checks and dialogues required; or after money check was successful
    if ct("Shy"):
        "She's too shy to do it anywhere. You go to her room."
        show bg girl_room with fade
        $ sex_scene_location="room"
    else:
        menu:
            "Where would you like to do it?"

            "Beach":
                show bg city_beach with fade
                $ sex_scene_location="beach"
            "Park":
                show bg city_park with fade
                $ sex_scene_location="park"
            "Room":
                show bg girl_room with fade
                $ sex_scene_location="room"
    $ picture_before_sex = True
    jump interactions_sex_scene_begins

label interactions_sex: # we go to this label from GM menu propose sex
    $ char.del_flag("raped_by_player")
    $ interactions_check_for_bad_stuff(char)
    $ interactions_check_for_minor_bad_stuff(char)
    $ m = interactions_flag_count_checker(char, "flag_interactions_sex")
    $ n = randint(2,3)
    if ct("Nymphomaniac"):
        $ n += 2
    elif check_lovers(char, hero):
        $ n += randint(1,2)
    elif check_friends(char, hero):
        $ n += randint(0,1)

    if m > n:
        $ del m, n
        call interactions_too_many_sex_lines from _call_interactions_too_many_sex_lines_2
        $ char.gfx_mod_stat("disposition", -randint(15, 30))
        $ char.gfx_mod_stat("affection", -randint(4,6))
        if char.get_stat("joy") > 50:
            $ char.gfx_mod_stat("joy", -randint(2, 4))
        jump girl_interactions
    $ del m, n

    if char.flag("quest_cannot_be_fucked") == True: # a special flag for chars we don't want to be accessible unless a quest will be finished
        call interactions_sex_disagreement from _call_interactions_sex_disagreement_2
        jump girl_interactions

    if interactions_gender_mismatch(char):
        if char.status != "slave":
            call interactions_refuse_because_of_gender from _call_interactions_refuse_because_of_gender_2 # you can hire them, but they will never do it for free with wrong orientation
            jump girl_interactions
        $ gender_disagreement = True
    else:
        $ gender_disagreement = False

    if char.get_stat("vitality") < char.get_max("vitality")/4 or not char.has_ap():
        $ del gender_disagreement
        call interactions_refused_because_tired from _call_interactions_refused_because_tired_3
        jump girl_interactions

    $ sub = check_submissivity(char)
    if check_lovers(char, hero): # a clear way to calculate how much disposition is needed to make her agree
        $ disposition_level_for_sex = randint(0, 100) + sub*200 # probably a placeholder until it becomes more difficult to keep lover status
    else:
        $ disposition_level_for_sex = randint(600, 700) + sub*100 # thus weak willed characters will need from 500 to 600 disposition, strong willed ones from 700 to 800, if there are no other traits that change it
    $ del sub

    if 'Horny' in char.effects:
        $ disposition_level_for_sex -= randint(200, 300)

    if char.status == "slave":
        $ disposition_level_for_sex -= 500
        if cgo("SIW"):
            $ disposition_level_for_sex -= 500

    if char.flag("quest_sex_anytime"): # special flag for cases when we don't want character to refuse unless disposition is ridiculously low
        $ disposition_level_for_sex -= 1000

    if 'Drunk' in char.effects: # a bit less disposition for drunk ones
        $ disposition_level_for_sex -= randint(50, 100)

    if cgo("SIW") and char.status == "free":
        if char.get_stat("disposition") >= 400:
            $ disposition_level_for_sex -= randint(50, 100)
        else:
            $ disposition_level_for_sex += randint(50, 100)

    if char.has_flag("flag_int_had_sex_with_mc"):
        $ disposition_level_for_sex -= 50+char.flag("flag_int_had_sex_with_mc")*10 # the more char does it with MC, the less needed disposition is, despite everything else

    # so normal (without flag) required level of disposition could be from 200 to 1200 for non lovers
    if ct("Open Minded"): # open minded trait greatly reduces the needed disposition level
        $ disposition_level_for_sex -= randint(400, 500)
    if disposition_level_for_sex < -500:
        $ disposition_level_for_sex = -500 # normalization, no free sex with too low disposition no matter the character

    if char.get_stat("affection") < disposition_level_for_sex:
        if char.status == "free":
            call interactions_sex_disagreement from _call_interactions_sex_disagreement_3
            $ diff = disposition_level_for_sex - char.get_stat("affection") # the difference between required for sex and current disposition
            if diff <= 100:
                $ char.gfx_mod_stat("disposition", -randint(20, 35)) # if it's low, then disposition penalty will be low too
                $ char.gfx_mod_stat("affection", -randint(8,12))
            else:
                $ char.gfx_mod_stat("disposition", -randint(30, 60)) # otherwise it will be significant
                $ char.gfx_mod_stat("affection", -randint(10,20))
            $ del diff, gender_disagreement, disposition_level_for_sex
            jump girl_interactions
        else:
            call interactions_sex_disagreement_slave from _call_interactions_sex_disagreement_slave
            "She doesn't like you enough yet, but as a slave she has no choice. Do you wish to force her?"
            menu:
                "Yes":
                    if cgo("SIW"):
                        $ char.gfx_mod_stat("joy", -randint(1, 5))
                        if char.get_stat("disposition") > 50:
                            $ char.gfx_mod_stat("disposition", -randint(25, 50))
                        $ char.gfx_mod_stat("affection", -randint(8,12))
                    else:
                        $ char.gfx_mod_stat("joy", -randint(20, 30))
                        $ char.gfx_mod_stat("disposition", -randint(50, 100))
                        $ char.gfx_mod_stat("affection", -randint(15,25))
                        $ char.set_flag("raped_by_player")
                "No":
                    $ del gender_disagreement, disposition_level_for_sex
                    jump girl_interactions
    else:
        if gender_disagreement:
            "Although she prefers females, she reluctantly agrees."
            $ char.gfx_mod_stat("joy", -10)
    $ del gender_disagreement, disposition_level_for_sex

    if not char.has_flag("raped_by_player"):
        call interactions_sex_agreement from _call_interactions_sex_agreement

    if ct("Nymphomaniac") or check_lovers(char, hero) or char.get_stat("affection") >= 600 or char.has_flag("raped_by_player"):
        menu:
            "Where would you like to do it?"

            "Beach":
                show bg city_beach with fade
                $ sex_scene_location = "beach"
            "Park":
                show bg city_park with fade
                $ sex_scene_location = "park"
            "Room":
                show bg girl_room with fade
                $ sex_scene_location = "room"
    elif (char.status == "slave") and ct("Shy"):
        "She is too shy to do it anywhere. You can force her nevertheless, but she prefers her room."
        menu:
            "Where would you like to do it?"
            "Beach":
                show bg city_beach with fade
                $ sex_scene_location="beach"
                if ct("Masochist"):
                    $ char.gfx_mod_stat("joy", 10)
                else:
                    $ char.gfx_mod_stat("joy", -10)
            "Park":
                show bg city_park with fade
                $ sex_scene_location="park"
                if ct("Masochist"):
                    $ char.gfx_mod_stat("joy", 10)
                else:
                    $ char.gfx_mod_stat("joy", -10)
            "Room":
                show bg girl_room with fade
                $ sex_scene_location="room"
    elif ct("Shy"):
        "She's too shy to do it anywhere. You go to her room."
        show bg girl_room with fade
        $ sex_scene_location="room"
    elif ct("Homebody"):
        "She doesn't want to do it outdoors, so you go to her room."
        show bg girl_room with fade
        $ sex_scene_location="room"
    else:
        "She wants to do it in her room."
        show bg girl_room with fade
        $ sex_scene_location = "room"
    $ picture_before_sex = True

label interactions_sex_scene_begins: # here we set initial picture before the scene and set local variables
    $ scene_picked_by_character = True # when it's false, there is a chance that the character might wish to do something on her own

    $ sub = check_submissivity(char)

    if picture_before_sex:
        $ get_picture_before_sex(char, location=sex_scene_location)

    $ sex_count = guy_count = girl_count = together_count = cum_count = mast_count = 0 # these variable will decide the outcome of sex scene
    $ sex_prelude = False
    $ max_sex_scene_libido = sex_scene_libido = get_character_libido(char)
    $ char.take_ap(1)

    $ char.up_counter("flag_int_had_sex_with_mc")

    if not char.has_flag("raped_by_player"):
        call interactions_sex_begins from _call_interactions_sex_begins

    jump interaction_scene_choice

label interaction_scene_choice: # here we select specific scene, show needed image, jump to scene logic and return here after every scene
    if sex_scene_libido > 0:
        show screen int_libido_level(sex_scene_libido)
    else:
        hide screen int_libido_level
        show screen int_libido_level_zero

    if char.get_stat("vitality") <=10:
        jump mc_action_scene_finish_sex
    elif hero.get_stat("vitality") <= 30:
        "You are too tired to continue."
        jump mc_action_scene_finish_sex

    if char.status == "slave":
        if sex_scene_libido == 0:
            "[char.name] doesn't want to do it any longer. You can force [char.op], but it will not be without consequences."
            jump interaction_sex_scene_choice
        if char.get_stat("vitality") <= 30:
            "[char.name] looks very tired."
            jump interaction_sex_scene_choice
    else:
        if sex_scene_libido <= 0:
            "[char.name] doesn't want to do it any longer."
            jump mc_action_scene_finish_sex
        elif char.get_stat("joy") < 30:
            "[char.name] looks upset. Not the best mood for sex."
            jump mc_action_scene_finish_sex
        if char.get_stat("vitality") < 30:
            "[char.name] is too tired to continue."
            jump mc_action_scene_finish_sex

    if not(scene_picked_by_character):
        $ scene_picked_by_character = True

        if dice(sex_scene_libido*10 + 20*sub) and sex_scene_libido > 1  and char.status == "free": # strong willed and/or very horny characters may pick action on their own from time to time
            $ current_action = get_character_wishes(char)
            if current_action == "sex":
                $ current_action = choice(["hand", "foot"])
            elif current_action == "oral":
                $ current_action = choice(["blow", "tits"])
            elif current_action != "anal":
                $ current_action = "vag"
            if sub < 0:
                "[char.pC] is so horny that [char.p] cannot control [char.op]self."
            elif sub == 0:
                "[char.pC] wants to try something else with you."
            else:
                "[char.pC] wants to do something else with you."
            if current_action == "vag" and ct("Virgin"):
                jump interaction_check_for_virginity
            jump interactions_sex_scene_logic_part

label interaction_sex_scene_choice:
    if sex_scene_libido>0:
        show screen int_libido_level(sex_scene_libido)
    else:
        hide screen int_libido_level
        show screen int_libido_level_zero

    if not char.has_flag("raped_by_player"):
        $ scene_picked_by_character = False

    if 'Horny' in char.effects:
        $ char.disable_effect("Horny")
    menu:
        "What would you like to do now?"

        "Ask for striptease" if max_sex_scene_libido == sex_scene_libido and not sex_prelude:
            $ current_action = "strip"
            $ sex_prelude = True
            jump interactions_sex_scene_logic_part

        "Ask [char.op] to play with [char.op]self" if max_sex_scene_libido == sex_scene_libido and not sex_prelude:
            $ current_action = "mast"
            $ sex_prelude = True
            jump interactions_sex_scene_logic_part

        "Cuddle [char.op]":
            $ current_action = "hug"
            jump interactions_sex_scene_logic_part

        "French kiss":
            $ current_action = "kiss"
            jump interactions_sex_scene_logic_part

        "Caress her tits" if char.gender == "female":
            $ current_action = "caresstits"
            jump interactions_sex_scene_logic_part

        "Finger her pussy" if char.gender == "female":
            $ current_action = "fingervag"
            jump interactions_sex_scene_logic_part

        "Lick her pussy" if char.gender == "female":
            $ current_action = "lickvag"
            jump interactions_sex_scene_logic_part

        "Ask for a blowjob":
            $ current_action = "blow"
            jump interactions_sex_scene_logic_part

        "Ask for paizuri" if hero.gender == "male":
            $ current_action = "tits"
            jump interactions_sex_scene_logic_part

        "Ask for a handjob":
            $ current_action = "hand"
            jump interactions_sex_scene_logic_part

        "Ask for a footjob":
            $ current_action = "foot"
            jump interactions_sex_scene_logic_part

        "Ask for sex" if char.gender == "female" and hero.gender == "male":
            if ct("Virgin"):
                jump interaction_check_for_virginity
            else:
                $ current_action = "vag"
                jump interactions_sex_scene_logic_part

        "Ask for anal sex" if hero.gender == "male":
            $ current_action = "anal"
            jump interactions_sex_scene_logic_part

        "That's all.":
            if hasattr(store, "current_action"):
                $ del store.current_action

label mc_action_scene_finish_sex:
    hide screen int_libido_level
    hide screen int_libido_level_zero

    if sex_scene_libido > 3 and char.get_stat("vitality") >= 50 and ct("Nymphomaniac") and not char.has_flag("raped_by_player"):
        $ get_single_sex_picture(char, act="masturbation", location=sex_scene_location, hidden_partner=True)
        "[char.name] is not satisfied yet, so she quickly masturbates right in front of you."
        $ char.gfx_mod_stat("disposition", -round(sex_scene_libido*3))
        $ char.gfx_mod_stat("affection", -1)

    if (together_count > 0 and sex_count >1) or (sex_count >2 and girl_count >=1 and guy_count >= 1):
        $ excluded = ["angry", "sad", "scared", "in pain"]
        $ loc_tag = sex_scene_location
        if sex_scene_location == "room":
            $ loc_tag = "living"
        #elif sex_scene_location == "beach":
        #    $ pass
        elif sex_scene_location == "park":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "wildness"])
        elif sex_scene_location == "forest":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "urban"])

        if char.has_image("profile", loc_tag, exclude=excluded):
            $ gm.set_img("profile", loc_tag, "happy", exclude=excluded, type="reduce")
        else:
            $ gm.set_img("girlmeets", loc_tag, "happy", exclude=excluded, type="reduce")

        if not char.has_flag("raped_by_player"):
            $ char.gfx_mod_stat("disposition", randint(50, 100))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5, "sex"))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5))
            call interactions_after_good_sex from _call_interactions_after_good_sex
        else:
            "She quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 10))
    elif girl_count < 1 and guy_count > 0:
        $ excluded = ["happy", "scared", "in pain", "ecstatic", "suggestive"]
        $ loc_tag = sex_scene_location
        if sex_scene_location == "room":
            $ loc_tag = "living"
        #elif sex_scene_location == "beach":
        #    $ pass
        elif sex_scene_location == "park":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "wildness"])
        elif sex_scene_location == "forest":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "urban"])

        if char.has_image("profile", loc_tag, exclude=excluded):
            $ gm.set_img("profile", loc_tag, "angry", exclude=excluded, type="reduce")
        else:
            $ gm.set_img("girlmeets", loc_tag, "angry", exclude=excluded, type="reduce")

        if not char.has_flag("raped_by_player"):
            $ char.gfx_mod_stat("disposition", -randint(15, 35))
            $ char.gfx_mod_stat("affection", -randint(8,12))
            $ char.gfx_mod_stat("joy", -randint(2, 5))
            call interactions_girl_never_come from _call_interactions_girl_never_come
        else:
            "She quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 10))
    elif girl_count > 0 and guy_count < 1 and cum_count < 1 and sex_count > 0:
        $ excluded = ["happy", "scared", "in pain", "ecstatic", "suggestive"]
        $ loc_tag = sex_scene_location
        if sex_scene_location == "room":
            $ loc_tag = "living"
        #elif sex_scene_location == "beach":
        #    $ pass
        elif sex_scene_location == "park":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "wildness"])
        elif sex_scene_location == "forest":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "urban"])

        if char.has_image("profile", loc_tag, exclude=excluded):
            $ gm.set_img("profile", loc_tag, "sad", exclude=excluded, type="reduce")
        else:
            $ gm.set_img("girlmeets", loc_tag, "sad", exclude=excluded, type="reduce")

        if not char.has_flag("raped_by_player"):
            $ char.gfx_mod_stat("disposition", randint(15, 30))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5, "sex"))
            $ char.gfx_mod_stat("affection", affection_reward(char))
            $ char.gfx_mod_stat("joy", -randint(10, 15))
            call interactions_guy_never_came from _call_interactions_guy_never_came
        else:
            "She quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 15))
    elif (cum_count >=4) and (cum_count > girl_count):
        $ excluded = ["angry", "sad", "scared", "in pain"]
        $ loc_tag = sex_scene_location
        if sex_scene_location == "room":
            $ loc_tag = "living"
        #elif sex_scene_location == "beach":
        #    $ pass
        elif sex_scene_location == "park":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "wildness"])
        elif sex_scene_location == "forest":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "urban"])

        if char.has_image("profile", loc_tag, exclude=excluded):
            $ gm.set_img("profile", loc_tag, "shy", exclude=excluded, type="reduce")
        else:
            $ gm.set_img("girlmeets", loc_tag, "shy", exclude=excluded, type="reduce")

        if not char.has_flag("raped_by_player"):
            $ char.gfx_mod_stat("disposition", randint(25, 50))
            $ char.gfx_mod_stat("affection", affection_reward(char))
            call interactions_guy_cum_alot from _call_interactions_guy_cum_alot
        else:
            "She quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 10))
    elif sex_count < 1 and mast_count < 1:
        $ excluded = ["happy", "scared", "in pain", "ecstatic", "suggestive"]
        $ loc_tag = sex_scene_location
        if sex_scene_location == "room":
            $ loc_tag = "living"
        #elif sex_scene_location == "beach":
        #    $ pass
        elif sex_scene_location == "park":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "wildness"])
        elif sex_scene_location == "forest":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "urban"])

        if char.has_image("profile", loc_tag, exclude=excluded):
            $ gm.set_img("profile", loc_tag, "angry", exclude=excluded, type="reduce")
        else:
            $ gm.set_img("girlmeets", loc_tag, "angry", exclude=excluded, type="reduce")
        if char.status == "slave":
            "She is puzzled and confused by the fact that you didn't do anything. She quickly leaves, probably thinking that you teased her."
        else:
            "She is quite upset and irritated because you didn't do anything. She quickly leaves, probably thinking that you teased her."
            $ char.gfx_mod_stat("disposition", -randint(50, 100))
            $ char.gfx_mod_stat("affection", -randint(8,12))
            $ char.gfx_mod_stat("joy", -randint(15, 30))
            $ char.mod_stat("vitality", -5)
    elif mast_count > 0 and guy_count < 1 and girl_count < 1:
        $ excluded = ["angry", "sad", "scared", "in pain"]
        $ loc_tag = sex_scene_location
        if sex_scene_location == "room":
            $ loc_tag = "living"
        #elif sex_scene_location == "beach":
        #    $ pass
        elif sex_scene_location == "park":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "wildness"])
        elif sex_scene_location == "forest":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "urban"])

        if char.has_image("profile", loc_tag, exclude=excluded):
            $ gm.set_img("profile", loc_tag, "shy", exclude=excluded, type="reduce")
        else:
            $ gm.set_img("girlmeets", loc_tag, "shy", exclude=excluded, type="reduce")

        "She did nothing but masturbated in front of you. Be prepared for rumors about your impotence or orientation."
        if not char.has_flag("raped_by_player"):
            $ char.gfx_mod_stat("disposition", -randint(10, 25))
            $ char.gfx_mod_stat("affection", -randint(0,3))
        call interactions_girl_dissapointed from _call_interactions_girl_dissapointed_3
        $ char.mod_stat("vitality", -5)
    else:
        $ excluded = ["angry", "sad", "scared", "in pain"]
        $ loc_tag = sex_scene_location
        if sex_scene_location == "room":
            $ loc_tag = "living"
        #elif sex_scene_location == "beach":
        #    $ pass
        elif sex_scene_location == "park":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "wildness"])
        elif sex_scene_location == "forest":
            $ loc_tag = "nature"
            $ excluded.extend(["beach", "urban"])

        if char.has_image("profile", loc_tag, exclude=excluded):
            $ gm.set_img("profile", loc_tag, "happy", exclude=excluded, type="reduce")
        else:
            $ gm.set_img("girlmeets", loc_tag, "happy", exclude=excluded, type="reduce")

        if not char.has_flag("raped_by_player"):
            $ char.gfx_mod_stat("disposition", randint(30, 60))
            $ char.gfx_mod_stat("affection", affection_reward(char, .4, "sex"))
            $ char.gfx_mod_stat("affection", affection_reward(char, .4))
            call interactions_after_normal_sex from _call_interactions_after_normal_sex
        else:
            "She quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 10))

    $ gm.restore_img()

    $ del excluded, loc_tag, sub, sex_count, guy_count, girl_count, together_count, cum_count, mast_count, sex_prelude, max_sex_scene_libido, sex_scene_libido, scene_picked_by_character

    jump girl_interactions_end

label interactions_lesbian_choice:
    $ sex_scene_libido -= 1
    # The interactions itself.
    # Since we called a function, we need to do so again (Consider making this func a method so it can be called just once)...
    if ct("Lesbian", "Bisexual", "Open Minded"):
        if char.get_stat("affection") <= 500 or not(check_friends(hero, char) or check_lovers(hero, char)):
            "Unfortunately, she does not want to do it."
            jump interaction_scene_choice
        elif check_lovers(hero, char):
            "She gladly agrees to make a show for you."
        elif check_friends(hero, char) or char.get_stat("affection") > 600:
            "A bit hesitant, she agrees to do it for you."
    else:
        if char.get_stat("affection") <= 600 or not(check_friends(hero, char) or check_lovers(hero, char)) or not(cgo("SIW")):
            "Unfortunately, she does not like girls in that way."
            jump interaction_scene_choice
        elif check_lovers(hero, char):
                "She gladly agrees to make a show for you if there will be some straight sex as well today."
        elif (check_friends(hero, char) or char.get_stat("affection") > 600) and cgo("SIW"):
                "She prefers men but agrees to make a show for you if there will be some straight sex as well today."
    $ willing_partners = find_les_partners()

    # Single out one partner randomly from a set:
    $ char2 = random.sample(willing_partners, 1)[0]

    # We plainly hide the interactions screen to get rid of the image and gradient:
    hide screen girl_interactions

    $ char_sprite = char.get_vnsprite()
    $ char_sprite2 = char2.get_vnsprite()
    "[char.nickname] decided to call [char2.nickname] for the lesbo action!"

    show expression char_sprite at mid_left with dissolve
    char.say "We are going to do 'it'."
    show expression char_sprite at mid_right as char_sprite with move
    show expression char_sprite2 at mid_left as char_sprite2 with dissolve
    char2.say "And..."
    extend "(*looking at you*) Are you planning to watch?"

    hide char_sprite
    hide char_sprite2
    with dissolve

    # Resize images to be slightly smaller than half a screen in width and the screen in height. ProportionalScale will do the rest.
    $ resize = (config.screen_width/2 - 75, config.screen_height - 75)


    show expression char.show("nude", "simple bg", resize=resize, exclude=["sex", "sleeping", "angry", "in pain", "beach", "onsen", "pool", "stage", "dungeon", "bathing"], type="first_default") as xxx at Transform(align=(0, .5)) with moveinright
    show expression char2.show("nude", "simple bg", resize=resize, exclude=["sex", "sleeping", "angry", "in pain", "beach", "onsen", "pool", "stage", "dungeon", "bathing"], type="first_default") as xxx2 at Transform(align=(1.0, .5)) with moveinleft

    # Wait for .25 secs and add soundbyte:
    pause .25
    play events "female/orgasm.mp3"
    $ renpy.pause(5.0)
    hide xxx
    hide xxx2


    show expression char2.get_vnsprite() at left as char_sprite2 with dissolve
    show expression char.get_vnsprite() at right as char_sprite with dissolve
    if sex_scene_libido <= 0:
        $ char.mod_stat("vitality", -20)
        $ char.gfx_mod_stat("joy", -5)
    if char.get_stat("joy") <= 10:
        $ char.gfx_mod_stat("disposition", -5)
        $ char.gfx_mod_stat("affection", -10)
    $ char.mod_stat("health", -2)
    if char.get_skill("oral") < 100 and char.get_skill("sex") < 100 and char2.get_skill("oral") < 100 and char2.get_skill("sex") < 100:
        "They both were not skilled enough to give each other enough pleasure, no matter how they tried. That was quite awkward."
        $ char.gfx_mod_skill("oral", 0, randint (0,1))
        $ char2.gfx_mod_skill("oral", 0, randint (0,1))
        $ char.gfx_mod_skill("sex", 0, randint (0,1))
        $ char2.gfx_mod_skill("sex", 0, randint (0,1))
        $ char.mod_stat("vitality", -20)
        $ char2.mod_stat("vitality", -20)
        $ sex_scene_libido -= 5
        char2.say "..."
        char.say "Sorry..."
    elif char.get_skill("oral") < 100 and char.get_skill("sex") < 100:
        "[char.nickname] was not skilled enough to make her partner cum. On the bright side, [char2.nickname] made her cum a lot."
        $ char.gfx_mod_skill("oral", 0, randint (2,4))
        $ char2.gfx_mod_skill("oral", 0, randint (2,4))
        $ char.gfx_mod_skill("sex", 0, randint (0,1))
        $ char2.gfx_mod_skill("sex", 0, randint (0,1))
        $ char.mod_stat("vitality", -20)
        $ char2.mod_stat("vitality", -15)
        $ sex_scene_libido -= 10
        char.say "Sorry..."
        char2.say "Don't worry. You'll become better in time."
    elif char2.get_skill("oral") < 100 and char2.get_skill("sex") < 100:
        "[char2.nickname] was not skilled enough to make her partner cum. On the bright side, [char.nickname] made her cum a lot."
        $ char.gfx_mod_skill("oral", 0, randint (2,4))
        $ char2.gfx_mod_skill("oral", 0, randint (2,4))
        $ char.gfx_mod_skill("sex", 0, randint (0,1))
        $ char2.gfx_mod_skill("sex", 0, randint (0,1))
        $ char.mod_stat("vitality", -20)
        $ char2.mod_stat("vitality", -15)
        $ sex_scene_libido -= 10
        char2.say "I'm sorry..."
        char.say "Don't be. We had our fun (*looking at you*)."
    else:
        "They both cum a lot. What a beautiful sight."
        $ char.gfx_mod_skill("oral", 0, randint (2,4))
        $ char2.gfx_mod_skill("oral", 0, randint (2,4))
        $ char.gfx_mod_skill("sex", 0, randint (2,4))
        $ char2.gfx_mod_skill("sex", 0, randint (2,4))
        $ char.mod_stat("vitality", -15)
        $ char2.mod_stat("vitality", -15)
        $ sex_scene_libido -= 10
        $ char.gfx_mod_stat("joy", 5)
        $ char2.gfx_mod_stat("joy", 5)
        char2.say "That... wasn't so bad."
        char2.say "We should do that again sometime ♪"
    hide char_sprite2 with dissolve
    hide char_sprite with dissolve

    # Restore the gm image:

    # Show the screen again:
    show screen girl_interactions

    # And finally clear all the variables for global scope:
    $ del resize, char2, willing_partners

    stop events

    # And we're all done!:
    jump interaction_scene_choice


label interactions_sex_scene_logic_part: # here we resolve all logic for changing stats and showing lines after picking a sex scene
    if sex_scene_libido <= 0:
        $ char.mod_stat("vitality", -randint(5, 25))
        $ char.gfx_mod_stat("joy", -randint(3, 6))
    $ char.mod_stat("health", -2)
    if current_action not in ["hug", "kiss", "caresstits", "strip"]:
        $ sex_count += 1
        $ char.gfx_mod_stat("affection", affection_reward(char, .5, "sex"))
        if current_action in ["blow", "tits", "hand", "foot", "vag", "anal"] and "Mana Source" in hero.traits:
            $ mod_by_max(char, "mp", .5)

    if current_action == "hug":
        $ get_single_sex_picture(char, act="2c hug", location=sex_scene_location, hidden_partner=True)
        if char.has_flag("raped_by_player"):
            "You can feel [char.pp] tense up as you put your arm around [char.op]."
        else:
            "[char.name] feels comfortable in your arms. [char.ppC] chest moves up and down as [char.p] breaths."
            if dice(30):
                extend " You can feel [char.pp] heart starts to beat faster. [char.pC] is more aroused now."
                $ sex_scene_libido += 2

    elif current_action == "kiss":
        $ get_single_sex_picture(char, act="2c kiss", location=sex_scene_location, hidden_partner=True)
        if char.has_flag("raped_by_player"):
            "[char.ppC] lips are closed tightly. You have to force your tongue to reach inside."
        else:
            "[char.ppC] soft lips welcoming your approach. Your gently move around, back and forth in [char.pp] mouth."
            if dice(45):
                extend " You don't have to wait too long for a response. [char.pC] is more aroused now."
                $ sex_scene_libido += 2

    elif current_action == "strip":
        $ get_single_sex_picture(char, act="stripping", location=sex_scene_location, hidden_partner=True)

        $ skill_for_checking = char.get_skill("refinement") + char.get_skill("strip")
        $ male_skill_for_checking = 2 * hero.get_skill("refinement")
        $ temp = randint(1, 5)
        if (male_skill_for_checking - skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("strip", 0, temp)
        $ del temp
        $ char.mod_stat("vitality", -randint(1, 5))

        if skill_for_checking >= 1000:
            "[char.pC] looks unbearably hot and sexy. After a short time, you cannot withstand it anymore and begin to masturbate, quickly cumming. [char.pC] looks at you with a smile and superiority in [char.pp] eyes."
        elif skill_for_checking >= 750:
            "[char.ppC] movements are so fascinating that you cannot look away from [char.op]. [char.pC] looks proud and pleased."
        elif skill_for_checking >= 500:
            "Looking at [char.pp] graceful and elegant moves is nice."
        elif skill_for_checking >= 200:
            "[char.pC] did [char.pp] best to show you [char.pp] body, but [char.pp] skills could be improved."
        elif skill_for_checking >= 50:
            "[char.pC] tried [char.pp] best, but the moves were quite clumsy and unnatural. At least [char.p] learned something new today."
        else:
            "It looks like [char.name] barely knows what [char.p] is doing. Even just standing still without clothes would have made a better impression."

        $ del skill_for_checking, male_skill_for_checking

    elif current_action == "mast":
        $ get_single_sex_picture(char, act="masturbation", location=sex_scene_location, hidden_partner=True)
        if char.has_flag("raped_by_player"):
            "[char.pC] pleasures [char.op]self briefly, hesitantly avoiding your glance."
        else:
            if sub > 0:
                "[char.pC] leisurely pleasures [char.op]self for a while, seductively glancing at you."
            elif sub < 0:
                "[char.pC] diligently pleasures [char.op]self for a while until you tell [char.op] to stop."
            else:
                "[char.pC] pleasures [char.op]self briefly, hesitantly avoiding your glance."
            if dice(60):
                extend " [char.pC] is more aroused now."
                $ sex_scene_libido += 2
        $ char.mod_stat("vitality", -randint(5, 10))
        $ mast_count +=1

    elif current_action == "caresstits":
        $ get_single_sex_picture(char, act="2c caresstits", location=sex_scene_location, hidden_partner=True)
        if char.has_flag("raped_by_player"):
            "You grab her tits with force."
            if ct("Big Boobs"):
                extend " You squeeze as much as you can."
            elif ct("Abnormally Large Boobs"):
                extend " Your hands are not big enough to hold her enormous breasts in place."
            elif ct("Small Boobs"):
                extend " You can barely feel them at all."
            else:
                extend " They feel cold but hard."
        else:
            "You hold her breast in your hands. [char.name] looks into your eyes with much expectation."
            if ct("Big Boobs"):
                extend " It feels nice to play around with those beautiful peaches."
            elif ct("Abnormally Large Boobs"):
                extend " Your fingers dig deep into her enormous breasts."
            elif ct("Small Boobs"):
                extend " You can feel as her nips became hard."
            else:
                extend " Her apples fit perfectly."
            $ sex_scene_libido += 2
        $ char.mod_stat("vitality", -randint(1, 5))

    elif current_action == "fingervag":
        $ get_single_sex_picture(char, act="2c vaginalfingering", location=sex_scene_location, hidden_partner=True)
        $ image_tags = gm.get_image_tags()
        $ char_skill_for_checking = 2 * char.get_skill("sex")
        if interactions_gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ skill_for_checking = hero.get_skill("refinement") + hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (char_skill_for_checking - skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ hero.gfx_mod_skill("refinement", 0, temp)
        $ del temp
        $ char.gfx_mod_skill("sex", 0, randint(2, 6))
        $ hero.gfx_mod_skill("sex", 0, randint(1, 4))

        if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
            "[char.name] opens her mouth a bit. Her gaze is filled with anticipation."
        else:
            "[char.name] bites her lips and looks away."
        if not char.has_flag("raped_by_player"):
            extend " As you touch her lips, they become swollen. A drop of fluid glances at the bottom."  
        else:
            extend " Your fingers dig deep into her. You move in and out of her pussy in quick successions." 

        call interaction_sex_scene_check_skill_gives from _call_interaction_sex_scene_check_skill_gives

        $ del char_skill_for_checking, skill_for_checking, image_tags

    elif current_action == "lickvag":
        $ get_single_sex_picture(char, act="2c lickpussy", location=sex_scene_location, hidden_partner=True)
        $ image_tags = gm.get_image_tags()
        $ char_skill_for_checking = 2 * char.get_skill("sex")
        if interactions_gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ skill_for_checking = hero.get_skill("oral") + hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (char_skill_for_checking - skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ hero.gfx_mod_skill("oral", 0, temp)
        $ del temp
        $ char.gfx_mod_skill("sex", 0, randint(2, 6))
        $ hero.gfx_mod_skill("sex", 0, randint(1, 4))

        if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
            "[char.name] spreads her legs to let you closer."
        else:
            "You have to push her legs apart."
        if not char.has_flag("raped_by_player"):
            extend " First your tongue just barely touches her pussy, but soon you reach deeper."
        else:
            extend " As you put your tongue inside her, you flex the muscles in your tongue to widen the gap as much as possible."

        call interaction_sex_scene_check_skill_gives from _call_interaction_sex_scene_check_skill_gives_1

        $ del char_skill_for_checking, skill_for_checking, image_tags

    elif current_action == "blow":
        $ temp = "bc blowjob" if hero.gender == "male" else "bc lickpussy"
        $ get_single_sex_picture(char, act=temp, location=sex_scene_location, hidden_partner=True)
        $ image_tags = gm.get_image_tags()

        $ skill_for_checking = char.get_skill("oral") + char.get_skill("sex")
        if interactions_gender_mismatch(char):
            $ skill_for_checking *= .8
        $ male_skill_for_checking = 2 * hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (male_skill_for_checking - skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("oral", 0, temp)
        $ del temp
        $ char.gfx_mod_skill("sex", 0, randint(1, 4))
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if sub > 0:
            if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
                "[char.name] licks [char.pp] lips, defiantly looking at your crotch."
            else:
                "[char.name] joylessly looks at your crotch."
            if "bc deepthroat" in image_tags:
                extend " She shoves it all the way into her throat."
            elif not char.has_flag("raped_by_player"):
                extend " [char.pC] enthusiastically begins to lick and suck it."
            else:
                extend " [char.pC] begins to lick and suck it."
        elif sub < 0:
            if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
                "Glancing at your crotch, [char.name] is patiently waiting for your orders."
            else:
                "[char.name] is waiting for your orders."
            if hero.gender == "male":
                if "bc deepthroat" in image_tags:
                    extend " You told [char.op] to take your dick in [char.op] mouth as deeply as [char.p] can, and [char.p] diligently obeyed."
                elif not char.has_flag("raped_by_player"):
                    extend " You told [char.op] to lick and suck your dick, and [char.p] immediately obeyed."
                else:
                    extend " You told [char.op] to lick and suck your dick."
            else:
                extend " You told [char.op] to lick and suck your pussy."
        else:
            if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
                "[char.name] quickly approached your crotch."
            else:
                "[char.name] slowly approached your crotch."
            if hero.gender == "male":
                if "bc deepthroat" in image_tags:
                    extend " You shove your dick deep into her throat."
                else:
                    extend " [char.pC] begins to lick and suck your dick."
            else:
                extend " [char.pC] begins to lick and suck your pussy."

        call interaction_sex_scene_check_skill_jobs from _call_interaction_sex_scene_check_skill_jobs

        $ del male_skill_for_checking, skill_for_checking, image_tags

    elif current_action == "tits":
        $ get_single_sex_picture(char, act="bc titsjob", location=sex_scene_location, hidden_partner=True)
        $ image_tags = gm.get_image_tags()

        $ skill_for_checking = char.get_skill("oral") + char.get_skill("sex")
        if interactions_gender_mismatch(char):
            $ skill_for_checking *= .8
        $ male_skill_for_checking = 2 * hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (male_skill_for_checking - skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("oral", 0, temp)
        $ del temp
        $ char.gfx_mod_skill("sex", 0, randint(1, 4))
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
            if sub > 0:
                "[char.name] massages her boobs, defiantly looking at your crotch."
            elif sub < 0:
                "Holding her boobs, [char.name] meekly approaches you."
            else:
                "[char.name] playfully grabs her boobs, looking at you."
        else:
            if sub > 0:
                "[char.name] massages her boobs, preparing them."
            elif sub < 0:
                "[char.name] holds her boobs, meekly looking at you."
            else:
                "[char.name] grabs her boobs and approaches you."
        if ct("Big Boobs"):
            extend " She wraps her big soft breasts around you."
        elif ct("Abnormally Large Boobs"):
            extend " You almost lost yourself in her enormous breasts as they envelop you."
        elif ct("Small Boobs"):
            extend " She begins to rub her small breasts around you assiduously." # assiduously, really? :D
        else:
            extend " She squeezes you between her soft breasts."

        call interaction_sex_scene_check_skill_jobs from _call_interaction_sex_scene_check_skill_jobs_1

        $ del male_skill_for_checking, skill_for_checking, image_tags

    elif current_action == "hand":
        $ temp = "bc handjob" if hero.gender == "male" else "bc vaginalhandjob"
        $ get_single_sex_picture(char, act=temp, location=sex_scene_location, hidden_partner=True)
        $ image_tags = gm.get_image_tags()

        $ skill_for_checking = char.get_skill("oral") + char.get_skill("sex")
        if interactions_gender_mismatch(char):
            $ skill_for_checking *= .8
        $ male_skill_for_checking = 2 * hero.get_skill("sex")
        $ temp = randint(2, 10)
        if (male_skill_for_checking - skill_for_checking) > 250 and dice(75):
            $ temp += randint(2, 10)
        $ char.gfx_mod_skill("sex", 0, temp)
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))
        $ del temp

        if sub > 0:
            "[char.name] grabs you with [char.pp] soft hands."
        elif sub < 0:
            if hero.gender == "male":
                "[char.name] wraps [char.pp] soft hands around your dick."
            else:
                "[char.name] takes your pussy in [char.pp] palms."
        else:
            if hero.gender == "male":
                "[char.name] takes your dick in [char.pp] soft hands."
            else:
                "[char.name] puts [char.pp] hands on your pussy."

        call interaction_sex_scene_check_skill_jobs from _call_interaction_sex_scene_check_skill_jobs_2

        $ del male_skill_for_checking, skill_for_checking, image_tags

    elif current_action == "foot":
        $ temp = "bc footjob" if hero.gender == "male" else "bc vaginalfootjob"
        $ get_single_sex_picture(char, act="bc footjob", location=sex_scene_location, hidden_partner=True)
        $ image_tags = gm.get_image_tags()

        $ skill_for_checking = char.get_skill("refinement") + char.get_skill("sex")
        if interactions_gender_mismatch(char):
            $ skill_for_checking *= .8
        $ male_skill_for_checking = 2 * hero.get_skill("sex")
        $ temp = randint(2, 10)
        if (male_skill_for_checking - skill_for_checking) > 250 and dice(75):
            $ temp += randint(2, 10)
        $ char.gfx_mod_skill("sex", 0, temp)
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))
        $ del temp

        if sub > 0:
            if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
                "With a sly smile [char.name] gets closer to you."
            else:
                "[char.name] gets closer to you."
        elif sub < 0:
            "You asked [char.name] to use [char.pp] feet."
        else:
            "[char.name] sits next to you."
        if hero.gender == "male":
            if ct("Athletic"):
                if ct("Long Legs"):
                    "[char.pC] squeezes your dick between [char.op] long muscular legs and stimulates it until you cum."
                else:
                    "[char.pC] squeezes your dick between [char.op] muscular legs and stimulates it until you cum."
            elif ct("Slim"):
                if ct("Long Legs"):
                    "[char.pC] squeezes your dick between [char.op] long slim legs and stimulates it until you cum."
                else:
                    "[char.pC] squeezes your dick between [char.op] slim legs and stimulates it until you cum."
            elif ct("Lolita"):
                if ct("Long Legs"):
                    "[char.pC] squeezes your dick between [char.op] long thin legs and stimulates it until you cum."
                else:
                    "[char.pC] squeezes your dick between [char.op] thin legs and stimulates it until you cum."
            else:
                if ct("Long Legs"):
                    "[char.pC] squeezes your dick between [char.op] long legs and stimulates it until you cum."
                else:
                    "[char.pC] squeezes your dick between [char.op] legs and stimulates it until you cum."
            if "after sex" in image_tags:
                extend " You generously cover [char.op] body with your thick liquid."

        call interaction_sex_scene_check_skill_jobs from _call_interaction_sex_scene_check_skill_jobs_3

        $ del male_skill_for_checking, skill_for_checking, image_tags

    elif current_action == "vag":
        $ get_single_sex_picture(char, act="2c vaginal", location=sex_scene_location, hidden_partner=True)
        $ image_tags = gm.get_image_tags()

        $ skill_for_checking = char.get_skill("vaginal") + char.get_skill("sex")
        if interactions_gender_mismatch(char):
            $ skill_for_checking *= .8
        $ male_skill_for_checking = hero.get_skill("vaginal") + hero.get_skill("sex")

        if (skill_for_checking - male_skill_for_checking) > 250 and dice(50):
            $ temp = randint(5, 10)
        else:
            $ temp = randint(2, 6)
        $ hero.gfx_mod_skill("vaginal", 0, temp)
        $ temp = randint(1, 5)
        if (male_skill_for_checking - skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("vaginal", 0, temp)
        $ del temp
        $ char.gfx_mod_skill("sex", 0, randint(1, 5))
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if sub > 0:
            if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
                "[char.name] looking forward to something big inside her pussy."
            else:
                "[char.name] unenthusiastically prepares her pussy."
            if "ontop" in image_tags:
                extend " She sits on top of you, immersing your dick inside."
            elif "doggy" in image_tags:
                extend " She bent over, pushing her crotch toward your dick."
            elif "missionary" in image_tags:
                extend " She lay on her back spreading her legs, waiting for your dick."
            elif "onside" in image_tags:
                extend " She lay down on her side, waiting for you to join her."
            elif "standing" in image_tags:
                extend " She spreads her legs waiting for you, not even bothering to lay down."
            elif "spooning" in image_tags:
                extend " She snuggled to you, being in a mood for some spooning."
            elif "sitting" in image_tags:
                extend " She sits on your lap, immersing your dick inside."
            else:
                extend " She confidently pushes your dick inside and starts to move."
        elif sub < 0:
            "[char.name] prepares herself, waiting for further orders."
            if "ontop" in image_tags:
                extend " You ask her to sit on top of you, immersing your dick inside."
            elif "doggy" in image_tags:
                extend " You ask her to bend over, allowing you to take her from behind."
            elif "missionary" in image_tags:
                extend " You ask her to lay on her back and spread legs, allowing you to shove your dick inside."
            elif "onside" in image_tags:
                extend "  You asked her to lay down on her side, allowing you to get inside."
            elif "standing" in image_tags:
                extend " You asked her to spread her legs while standing and pushed your dick inside."
            elif "spooning" in image_tags:
                extend " You asked her to snuggle with you, spooning her in the process."
            elif "sitting" in image_tags:
                extend " You asked her to sit on your lap, immersing your dick inside."
            else:
                extend " You entered her and asked to start moving."
        else:
            if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
                "[char.name] doesn't mind you to do her pussy."
            else:
                "[char.name] silently offers her pussy."
            if "ontop" in image_tags:
                extend " You invite her to sit on top of you, preparing your dick for some penetration."
            elif "doggy" in image_tags:
                extend " She bent over, welcoming your dick from behind."
            elif "missionary" in image_tags:
                extend " She lays on her back and spreads legs, inviting you to enter inside."
            elif "onside" in image_tags:
                extend " She lays down on her side, inviting you to enter inside."
            elif "standing" in image_tags:
                extend " You proceed to penetrate her not even bothering to lay down."
            elif "spooning" in image_tags:
                extend " You two snuggle with each other, trying out spooning."
            elif "sitting" in image_tags:
                extend " She sits on your lap while you prepare your dick for going inside her."
            else:
                extend " You enter her pussy, and you two begin to move."
        call interaction_sex_scene_check_skill_acts from _call_interaction_sex_scene_check_skill_acts

        $ del male_skill_for_checking, skill_for_checking, image_tags

    elif current_action == "anal":
        $ get_single_sex_picture(char, act="2c anal", location=sex_scene_location, hidden_partner=True)
        $ image_tags = gm.get_image_tags()

        $ skill_for_checking = char.get_skill("anal") + char.get_skill("sex")
        if interactions_gender_mismatch(char):
            $ skill_for_checking *= .8
        $ male_skill_for_checking = hero.get_skill("anal") + hero.get_skill("sex")
        if (skill_for_checking - male_skill_for_checking) > 250 and dice(50):
            $ temp = randint(5, 10)
        else:
            $ temp = randint(2, 6)
        $ hero.gfx_mod_skill("anal", 0, temp)
        $ temp = randint(1, 5)
        if (male_skill_for_checking - skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("anal", 0, temp)
        $ del temp
        $ char.gfx_mod_skill("sex", 0, randint(1, 4))
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if sub > 0:
            if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
                "[char.name] looking forward to something big inside [char.pp] ass."
            else:
                "[char.name] unenthusiastically prepares [char.pp] ass."
            if "ontop" in image_tags:
                extend " [char.pC] sits on top of you, immersing your dick inside."
            elif "doggy" in image_tags:
                extend " [char.pC] bent over, pushing [char.pp] anus toward your dick."
            elif "missionary" in image_tags:
                extend " [char.pC] lay on [char.pp] back spreading [char.pp] legs, waiting for your dick."
            elif "onside" in image_tags:
                extend " [char.pC] lay down on [char.pp] side, waiting for you to join [char.pp]."
            elif "standing" in image_tags:
                extend " [char.pC] spreads [char.pp] legs waiting for you, not even bothering to lay down."
            elif "spooning" in image_tags:
                extend " [char.pC] snuggled to you, being in a mood for some spooning."
            elif "sitting" in image_tags:
                extend " [char.pC] sat on your lap, immersing your dick inside."
            else:
                extend " [char.pC] confidently pushes your dick inside and starts to move."
        elif sub < 0:
            "[char.name] prepares herself, waiting for further orders."
            if "ontop" in image_tags:
                extend " You ask [char.pp] to sit on top of you, immersing your dick inside."
            elif "doggy" in image_tags:
                extend " You ask [char.pp] to bend over, allowing you to take [char.pp] from behind."
            elif "missionary" in image_tags:
                extend " You ask [char.pp] to lay on [char.pp] back and spread legs, allowing you to shove your dick inside."
            elif "onside" in image_tags:
                extend "  You asked [char.pp] to lay down on [char.pp] side, allowing you to get inside."
            elif "standing" in image_tags:
                extend " You asked [char.pp] to spread [char.pp] legs and pushed your dick inside."
            elif "spooning" in image_tags:
                extend " You asked [char.pp] to snuggle with you, spooning [char.pp] in the process."
            elif "sitting" in image_tags:
                extend " You asked [char.pp] to sit on your lap, immersing your dick inside."
            else:
                extend " You entered [char.pp] and asked to start moving."
        else:
            if sex_scene_libido > 0 and not char.has_flag("raped_by_player"):
                "[char.name] doesn't mind you to do [char.pp] ass."
            else:
                "[char.name] silently offers [char.pp] ass."
            if "ontop" in image_tags:
                extend " You invite [char.pp] to sit on top of you, preparing your dick for some penetration."
            elif "doggy" in image_tags:
                extend " [char.pC] bent over, welcoming your dick from behind."
            elif "missionary" in image_tags:
                extend " [char.pC] lays on [char.pp] back and spreads legs, inviting you to enter inside."
            elif "onside" in image_tags:
                extend " [char.pC] lays down on [char.pp] side, inviting you to enter inside."
            elif "standing" in image_tags:
                extend " You proceed to penetrate [char.pp] not even bothering to lay down."
            elif "spooning" in image_tags:
                extend " You two snuggle with each other, trying out spooning."
            elif "sitting" in image_tags:
                extend " [char.pC] sits on your lap while you prepare your dick for going inside [char.pp]."
            else:
                extend " You enter [char.pp] anus, and you two begin to move."
        call interaction_sex_scene_check_skill_acts from _call_interaction_sex_scene_check_skill_acts_1

        $ del male_skill_for_checking, skill_for_checking, image_tags

    $ sex_scene_libido -= 1
    jump interaction_scene_choice

label interaction_sex_scene_check_skill_jobs: # skill level check for girl side actions
    if current_action == "hand":
        if skill_for_checking <= 200:
            if sub > 0:
                $ narrator(choice(["She strokes you a bit too quickly, the friction is a bit uncomfortable.", "She begins to stroke you very quickly. But because of the speed your cock often slips out of her hand."]))
            elif sub < 0:
                $ narrator(choice(["She strokes you gently. She isn't quite sure however what to make of the balls.", "She makes up for her inexperience with determination, carefully stroking your cock."]))
            else:
                $ narrator(choice(["She squeezes one of your balls too tightly, but stops when you wince.", "She has a firm grip, and she's not letting go."]))
        elif skill_for_checking < 500:
            if sub > 0:
                $ narrator(choice(["Her fingers cause tingles as they caress the shaft.", "She quickly strokes you, with a very deft pressure."]))
            elif sub < 0:
                $ narrator(choice(["She gently caresses the shaft, and cups the balls in her other hand, giving them a warm massage.", "She moves very smoothly, stroking casually and very gently."]))
            else:
                $ narrator(choice(["Her hands glide smoothly across it.", "She moves her hands up and down. She's a little rough at this, but at she tries her best."]))
        else:
            if sub > 0:
                $ narrator(choice(["Her movements are masterful, her slightest touch starts you twitching.", "Her expert strokes will have you boiling over in seconds."]))
            elif sub < 0:
                $ narrator(choice(["She gently blows across the tip as her finger dance along the shaft.", "She slowly caresses you in a way that makes your blood boil, then pulls back at the last second."]))
            else:
                $ narrator(choice(["She knows what to do now, and rubs you with smooth strokes, focusing occasionally on the head.", "You can't tell where her hand is at any moment, all you know is that it works."]))
        if "after sex" in image_tags:
            "Soon you generously cover her body with your thick liquid."
    elif current_action == "tits":
        if skill_for_checking <= 200:
            if sub > 0:
                $ narrator(choice(["She kind of bounces her tits around your cock.", "She tries to quickly slide the cock up and down between her cleavage, but it tends to slide out."]))
            elif sub < 0:
                $ narrator(choice(["She slides the cock up and down between her cleavage.", "She squeezes her cleavage as tight as she can and rubs up and down."]))
            else:
                $ narrator(choice(["She sort of squishes her breasts back and forth around your cock.", "She slaps her tits against your dick, bouncing her whole body up and down."]))
        elif skill_for_checking < 500:
            if sub > 0:
                $ narrator(choice(["She juggles her breasts up and down around your cock.", "She moves her boobs up and down in a fluid rocking motion."]))
            elif sub < 0:
                $ narrator(choice(["She gently caresses the shaft between her tits.", "She lightly brushes the head with her chin as it pops up between her tits."]))
            else:
                $ narrator(choice(["Sometimes she pauses to rub her nipples across the shaft.", "She rapidly slides the shaft between her tits"]))
        else:
            if sub > 0:
                $ narrator(choice(["She rapidly rocks her breasts up and down around your cock, covering them with drool to keep things well lubed.", "In as she strokes faster and faster, she bends down to suck on the head."]))
            elif sub < 0:
                $ narrator(choice(["In between strokes she gently sucks on the head.", "She drips some spittle down to make sure you're properly lubed."]))
            else:
                $ narrator(choice(["She licks away at the head every time it pops up between her tits.", "She dancers her nipples across the shaft."]))
        if "after sex" in image_tags:
            if sub > 0:
                "At the last moment, she pulls away, covering herself with your thick liquid."
            elif sub < 0:
                "At the last moment, you take it away from her chest, covering her body with your thick liquid."
            else:
                "At the last moment, she asked you to take it away from her chest to cover her body with your thick liquid."
    elif current_action == "blow":
        if skill_for_checking <= 200:
            if sub > 0:
                $ narrator(choice(["Her head bobs rapidly, until she goes a bit too deep and starts to gag.", "She begins to suck very quickly. But because of the speed your cock often pops out of her mouth."]))
            elif sub < 0:
                $ narrator(choice(["She tentatively kisses and licks around the head.", "She licks all over your dick, but she doesn't really have a handle on it."]))
            else:
                $ narrator(choice(["She bobs quickly on your cock, but clamps down a bit too tight.", "She puts the tip in her mouth and starts suck in as hard as she can. She's a little rough at this, but at least she tries her best."]))
        elif skill_for_checking < 500:
            if sub > 0:
                $ narrator(choice(["She licks her way down the shaft, and gently teases the balls.", "Her mouth envelopes the head, then she quickly draws it in and draws back with a pop."]))
            elif sub < 0:
                $ narrator(choice(["She gently caresses the shaft, and cups the balls in her other hand, giving them a warm massage.", "She moves her tongue very smoothly and very gently, keeping her teeth well clear, aside from a playful nip."]))
            else:
                $ narrator(choice(["She's settled into a gentle licking pace that washes over you like a warm bath.", "She licks up and down the shaft. A little rough, but at least she tries her best."]))
        else:
            if sub > 0:
                $ narrator(choice(["She rapidly bobs up and down on your cock, a frenzy of motion.", "She puts the tip into her mouth and her tongue swirls rapidly around it."]))
            elif sub < 0:
                $ narrator(choice(["She gently blows across the head as she covers your cock in smooth licks.", "She moves very smoothly, tongue dancing casually and very gently."]))
            else:
                $ narrator(choice(["Her deft licks are masterful, your cock twitches with each stroke.", "She's really good at this, alternating between deep suction and gentle licks."]))
        if "after sex" in image_tags:
            if sub > 0:
                "At the last moment, she pulls it out, covering herself with your thick liquid."
            elif sub < 0:
                "At the last moment, you pull it out from her mouth, covering her body with your thick liquid."
            else:
                "She asked you to pull it out from her mouth at the last moment to cover her body with your thick liquid."
        $ char.gfx_mod_stat("affection", affection_reward(char, .5, "oral"))
    if skill_for_checking >= 2000:
        "She was so good that you profusely came after a few seconds. Pretty impressive."
        $ char.gfx_mod_stat("joy", randint(3, 5))
        $ hero.mod_stat("joy", randint(4, 6))
    elif skill_for_checking >= 1000:
        "You barely managed to hold out for half a minute in the face of her amazing skills."
        $ char.gfx_mod_stat("joy", randint(2, 4))
        $ hero.mod_stat("joy", randint(3, 5))
    elif skill_for_checking >= 500:
        "It was very fast and very satisfying."
        $ char.gfx_mod_stat("joy", randint(1, 2))
        $ hero.mod_stat("joy", randint(2, 4))
    elif skill_for_checking >= 200:
        "Nothing extraordinary, but it wasn't half bad either."
        $ char.gfx_mod_stat("joy", randint(0, 1))
        $ hero.mod_stat("joy", randint(1, 2))
    elif skill_for_checking >= 100:
        "It took some time and effort on her part. Her skills could be improved."
    elif skill_for_checking >= 50:
        "It looks like [char.name] barely knows what she's doing. Still, she somewhat managed to get the job done."
        $ char.mod_stat("vitality", -randint(5, 10))
    else:
        $ char.mod_stat("vitality", -randint(10, 15))
        "Her moves were clumsy and untimely. By the time she finished the moment had passed, bringing you little satisfaction."
        $ char.gfx_mod_stat("joy", -randint(2, 4))
        $ hero.mod_stat("joy", -randint(1, 2))
    $ sex_count += 1
    if skill_for_checking >= 50:
        $ guy_count +=1
        $ cum_count += 1
    return

label interaction_sex_scene_check_skill_gives: # # skill level check for MC side actions
    if sex_scene_libido > 0:
        if current_action == "lickvag":
            if skill_for_checking >= 2000:
                extend " The pleasure from joy went through her body as she reached an orgasm."
                $ char.gfx_mod_stat("joy", randint(3, 5))
                $ hero.mod_stat("joy", randint(2, 4))
            elif skill_for_checking >= 1000:
                extend " You managed to make her cum multiple times."
                $ char.gfx_mod_stat("joy", randint(2, 4))
                $ hero.mod_stat("joy", randint(1, 2))
            elif skill_for_checking >= 500:
                extend " Finally you made her cum."
                $ char.gfx_mod_stat("joy", randint(1, 2))
                $ hero.mod_stat("joy", randint(0, 1))
            elif skill_for_checking >= 200:
                extend " You licked her pussy until she came. It felt good."
                $ char.gfx_mod_stat("joy", randint(0, 1))
            elif skill_for_checking >= 100:
                extend " You licked her pussy until she came."
                $ hero.mod_stat("vitality", -randint(5, 10))
            elif skill_for_checking >= 50:
                extend " You had some difficulties with bringing her to orgasm but managed to overcome them."
                $ hero.mod_stat("vitality", -randint(10, 15))
            else:
                extend " Unfortunately, you didn't have the skill to satisfy her as well. [char.name] looks disappointed."
                $ hero.mod_stat("vitality", -randint(10, 15))
                $ hero.mod_stat("joy", -randint(0, 2))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5, stat="oral"))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5, stat="vaginal"))
        elif current_action == "fingervag":
            if skill_for_checking >= 2000:
                extend " Your bodies merged into a single entity, filling each other with pleasure and satisfaction."
                $ char.gfx_mod_stat("joy", randint(3, 5))
                $ hero.mod_stat("joy", randint(2, 4))
            elif skill_for_checking >= 1000:
                extend " You managed to make her cum multiple times."
                $ char.gfx_mod_stat("joy", randint(2, 4))
                $ hero.mod_stat("joy", randint(1, 2))
            elif skill_for_checking >= 500:
                extend " Finally you made her cum."
                $ char.gfx_mod_stat("joy", randint(1, 2))
                $ hero.mod_stat("joy", randint(0, 1))
            elif skill_for_checking >= 200:
                extend " You fingered her until she came. It felt good."
                $ char.gfx_mod_stat("joy", randint(0, 1))
            elif skill_for_checking >= 100:
                extend " You fingered her until she came."
                $ hero.mod_stat("vitality", -randint(5, 10))
            elif skill_for_checking >= 50:
                extend " You had some difficulties with bringing her to orgasm but managed to overcome them."
                $ hero.mod_stat("vitality", -randint(10, 15))
            else:
                extend " Unfortunately, you didn't have the skill to satisfy her as well. [char.name] looks disappointed."
                $ hero.mod_stat("vitality", -randint(10, 15))
                $ hero.mod_stat("joy", -randint(0, 2))
            $ char.gfx_mod_stat("affection", affection_reward(char, .7, stat="vaginal"))
    else:
        if skill_for_checking >= 1000:
            extend " You did your best to make her cum, but it brought more pain than pleasure judging by her expression."
        else:
            " She is not in the mood anymore. Your efforts to make her cum were in vain."

    $ sex_count += 1
    if skill_for_checking >= 50:
        $ girl_count += 1
    return

label interaction_sex_scene_check_skill_acts: # skill level check for two sides actions
    if current_action == "vag":
        if skill_for_checking >= 2000:
            "Her technique is fantastic, your bodies move in perfect synchronization, and her pussy feels like velvet."
            $ char.gfx_mod_stat("joy", randint(3, 5))
            $ hero.mod_stat("joy", randint(3, 5))
        elif skill_for_checking >= 1000:
            "Her refined skills, rhythmic movements, and wet hot pussy quickly brought you to the finish."
            $ char.gfx_mod_stat("joy", randint(2, 4))
            $ hero.mod_stat("joy", randint(2, 4))
        elif skill_for_checking >= 500:
            "Her pussy felt very good, her movement patterns and amazing skills quickly exhausted your ability to hold back."
            $ char.gfx_mod_stat("joy", randint(1, 2))
            $ hero.mod_stat("joy", randint(1, 2))
        elif skill_for_checking >= 200:
            "Her movements were pretty good. Nothing extraordinary, but it wasn't half bad either."
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ hero.mod_stat("joy", randint(0, 1))
        elif skill_for_checking >= 100:
            "It took some time and effort on her part. Her pussy could use some training."
            $ char.mod_stat("vitality", -randint(5, 10))
        elif skill_for_checking >= 50:
            "It looks like [char.name] barely knows what she's doing. Still, it's difficult to screw up such a simple task, so eventually, she got the job done."
            $ char.mod_stat("vitality", -randint(10, 15))
        else:
            "Her moves were clumsy and untimely, and her pussy was too dry. Sadly, she was unable to satisfy you adequately."
            $ char.gfx_mod_stat("joy", -randint(2, 4))
            $ hero.mod_stat("joy", -randint(2, 4))
            $ char.mod_stat("vitality", -randint(10, 15))
        $ char.gfx_mod_stat("affection", affection_reward(char, stat="vaginal"))
    elif current_action == "anal":
        if skill_for_checking >= 2000:
            "Her technique is fantastic, your bodies move in perfect synchronization, and her asshole feels nice and tight."
            $ char.gfx_mod_stat("joy", randint(3, 5))
            $ hero.mod_stat("joy", randint(3, 5))
        elif skill_for_checking >= 1000:
            "Her refined skills, rhythmic movements, and tight hot ass quickly brought you to the finish."
            $ char.gfx_mod_stat("joy", randint(2, 4))
            $ hero.mod_stat("joy", randint(2, 4))
        elif skill_for_checking >= 500:
            "Her anus felt very good, her movement patterns and amazing skills quickly exhausted your ability to hold back."
            $ char.gfx_mod_stat("joy", randint(1, 2))
            $ hero.mod_stat("joy", randint(1, 2))
        elif skill_for_checking >= 200:
            "Her movements were pretty good. Nothing extraordinary, but it wasn't half bad either."
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ hero.mod_stat("joy", randint(0, 1))
        elif skill_for_checking >= 100:
            "It took some time and effort on her part. Her anus could use some training."
            $ char.mod_stat("vitality", -randint(5, 10))
        elif skill_for_checking >= 50:
            "It looks like [char.name] barely knows what she's doing. Still, it's difficult to screw up such a simple task, so eventually, she got the job done."
            $ char.mod_stat("vitality", -randint(10, 15))
        else:
            "Her moves were clumsy and untimely, and her anus wasn't quite ready for that. Sadly, she was unable to satisfy you adequately."
            $ char.gfx_mod_stat("joy", -randint(2, 4))
            $ hero.mod_stat("joy", -randint(2, 4))
            $ char.mod_stat("vitality", -randint(10, 15))
        $ char.gfx_mod_stat("affection", affection_reward(char, stat="anal"))
    if sex_scene_libido > 0:
        if male_skill_for_checking >= 2000:
            extend " Your bodies merged into a single entity, filling each other with pleasure and satisfaction."
            $ char.gfx_mod_stat("joy", randint(3, 5))
            $ hero.mod_stat("joy", randint(3, 5))
        elif male_skill_for_checking >= 1000:
            extend " In the end, you both cum together multiple times."
            $ char.gfx_mod_stat("joy", randint(2, 4))
            $ hero.mod_stat("joy", randint(2, 4))
        elif male_skill_for_checking >= 500:
            extend " In the end, you both cum together."
            $ char.gfx_mod_stat("joy", randint(1, 2))
            $ hero.mod_stat("joy", randint(1, 2))
        elif male_skill_for_checking >= 200:
            extend " You fucked her until you both came. It felt good."
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ hero.mod_stat("joy", randint(0, 1))
        elif male_skill_for_checking >= 100:
            extend " You fucked her until you both came."
            $ hero.mod_stat("vitality", -randint(5, 10))
        elif male_skill_for_checking >= 50:
            extend " You had some difficulties with bringing her to orgasm but managed to overcome them."
            $ hero.mod_stat("vitality", -randint(10, 15))
        else:
            extend " Unfortunately, you didn't have the skill to satisfy her as well. [char.name] looks disappointed."
            $ char.gfx_mod_stat("joy", -randint(0, 1))
            $ hero.mod_stat("joy", -randint(0, 1))
            $ hero.mod_stat("vitality", -randint(10, 15))
    else:
        if male_skill_for_checking >= 1000:
            extend " You did your best to make her cum, but it brought more pain than pleasure judging by her expression."
        else:
            " She is not in the mood anymore. Your efforts to make her cum were in vain."

    if "after sex" in image_tags:
        $ cum_count += 1
        if sub > 0:
            "At the last moment, she pulls it out, covering herself with your thick liquid."
        elif sub < 0:
            "At the last moment, you pull it out of her, covering her body with your thick liquid."
        else:
            "She asked you to pull it out from her at the last moment to cover her body with your thick liquid."
    if (male_skill_for_checking) >= 1000 and (skill_for_checking >= 1000):
        $ together_count += 1
    $ sex_count += 1
    if male_skill_for_checking >= 50:
        $ girl_count += 1
    if skill_for_checking >= 50:
        $ guy_count += 1
    if hasattr(store, 'just_lost_virginity'):
        $ del just_lost_virginity
        call interactions_after_virginity_was_taken from _call_interactions_after_virginity_was_taken
    return

label interactions_sex_agreement: # the character agrees to do it
    $ char.override_portrait("portrait", "shy") # TO DO: this part for half-sister is to complex to be handled via properties, thus female lines should be written separately after adding female MC, with direct checks for MC gender
    if ct("Half-Sister") and dice(50):
        if ct("Impersonal"):
            $ rc("I'll take in all your cum, brother.", "Sex with my brother, initiation.", "Let's have incest.", "Even though we're siblings... it's fine to do this, right?", "Let's deepen our bond as siblings.")
        elif ct("Shy") and dice(40):
            $ rc("Umm... anything is fine as long as it's you... brother.", "I-if it's you, b-brother, then anything you do makes me feel good.", "I-is it alright to do something like that with my brother..?")
        elif ct("Imouto"):
            $ rc("Teach me more things, brother!", "Brother, teach me how to feel good!", "Sis... will try her best.", "Sister's gonna show you her skills as a woman.")
        elif ct("Dandere"):
            $ rc("Ah... actually, your sister has been feeling sexually frustrated lately...", "Brother, please do me.", "Even though we're related, we can have sex if we love each other.", "I'm only doing this because you're my brother.", "I'll do whatever you want, brother.", "Brother can do anything with me...")
        elif ct("Kuudere"):
            $ rc("I... I can't believe I'm doing it with my brother...", "Y-you're lusting for your sister? O-okay, you can be my sex partner.", "I... I don't mind doing it even though we're siblings...", "Just for now, we're not siblings... we're just... a man and a woman.")
        elif ct("Tsundere"):
            $ rc("Ugh... I... I have such a lewd brother!", "A-alright, you are allowed to touch me, brother.", "I... I'm only doing this because you're hard, brother.", "Doing this... with my brother... What am I doing?..", "I bet our parents would be so mad...")
        elif ct("Kamidere"):
            $ rc("B...brother...it's... it's wrong to do this...", "E...even though we're siblings...", "Doing such a thing to my brother. Am I a bad big sister?", "My brother is in heat.  That's wonderful.")
        elif ct("Yandere"):
            $ rc("Make love to me, brother. Drive me mad.", "I'm looking forward to see your face writhing in mad ecstacy, bro.", "Shut up and yield yourself to your sister.", "Bro, you're a perv. It runs in the family though.", "Man, who'd have thought that my brother is as perverted as I am...", "As long as the pervy brother has a pervy sis as well, all is right with the world.", "Damn... The thought of incest gets me all excited now...")
        elif ct("Ane"):
            $ rc("This is how you've always wanted to claim me, isn't it?", "Doing such things to your sister... Well, it can't be helped...", "Sis will do her best.", "Let sis display her womanly skills.")
        elif ct("Bokukko"):
            $ rc("You want to have sex with your sister so bad, huh?", "I'm gonna show you that I'm a woman too, bro.", "Right on, brother.  Better you just shut up and don't move.", "Leave this to me, you can rely on sis.", "As long as it's for my brother a couple of indecent things is nothing.")
        else:
            $ rc("It's alright for siblings to do something like this.", "Make your sister feel good.", "We're brother and sister. What we're doing now must remain an absolute secret.", "I'll do my best. I want you to feel good, brother.")

    elif ct("Impersonal"):
        $ rc("You are authorized so long as it does not hurt.", "You can do me if you want.", "Understood. I will... service you...", "I dedicate this body to you.", "Understood. Please demonstrate your abilities.", "If the one corrupting my body is you, then I'll have no regrets.")
    elif ct("Shy") and dice(50):
        $ rc("Sex... O-okay, let's do it...", "D-do you mean...  Ah, y-yes...  If I'm good enough...", "Eeh?! Th-that's... uh... W- well... I do... want to...", "O...okay. I'll do my best.", "I too... wanted to be touched by you...", "Uh... H-how should I say this... It... it'll be great if you could do it gently.",  "Um, I-I want to do it too... Please treat me well.", "Eeh, i-is it ok with someone like me...?", "Umm...  I wanted to do it too... hehe.", "I-if I'm good enough, then however many times you want...", "I-I understand... I will... service you.")
    elif ct("Tsundere"):
        $ rc("*gulp*... W-well... since you're begging to do it with me, I suppose we can...", "It...it can't be helped, right? It... it's not that I like you or anything!", "I-it's not like I want to do it! It's just that you seem to want to do it so much...", "Hhmph... if...if you wanna do it... uh... go all the way with it!", "If you're asking, then I'll listen... B-but it's not like I actually want to do it, too!", "If-if you say that you really, really want it... Then I won't turn you down...", "L.... leave it to me... you idiot...", "God, people like you... Are way too honest about what they want...", "T...that can't be helped, right? B...but that doesn't mean you can do anything you like!", "You're hopeless.... Well, fine then....", "...Yes, yes, I'll do it, I'll do it so...  geez, stop making that stupid face...", "Geez, you take anything you can get...")
    elif ct("Dandere"):
        $ rc("If that's what you desire...", "...Very well then. Please go ahead and do as you like.", "You're welcome to... to do that.",  "I will not go easy on you.", "I... I'm ready for sex.", "...If you do it, be gentle.", "...If you want, do it now.", "...I want to do it, too.", "Ok, but please don't look at my face. That'll help me relax more.")
    elif ct("Kuudere"):
        $ rc("Y-yes... I don't mind letting you do as you please.", "If you feel like it, do what you want with my body...", "...I don't particularly mind.", "Heh. I'm just a girl too, you know. Let's do it.", "What a bother... Alright, I get it.", "...Fine, just don't use the puppy-dog eyes.", "*sigh* ...Fine, fine! I'll do it as many times as you want!", "Fine with me... Wh-what? ...Even I have times when I want to do it...", "If you wanna do it just do what you want.")
    elif ct("Imouto"):
        $ rc("Uhuhu, Well then, I'll be really nice to you, ok? ♪",  "Okayyy! Let's love each other a lot ♪", "Hold me really tight, kiss me really hard, and make me feel really good ♪", "Yeah, let's make lots of love ♪", "I'll do my best to pleasure you!", "Geez, you're so forceful...♪")
    elif ct("Ane"):
        $ rc("Heh, fine, do me to your heart's content.", "If we're going to do it, then let's make it the best performance possible. Promise?", "Come on, show me what you've got...", "This looks like it will be enjoyable.", "If you can do this properly... I'll give you a nice pat on the head.", "Seems like you can't help it, huh...", "Fufufu, please don't overdo it, okay?", "Go ahead and do it as you like, it's okay.", "Very well, I can show you a few things... Hmhm.", "You want to do it with me too? Huhu, by all means.")
    elif ct("Bokukko"):
        $ rc("Wha? You wanna to do it? Geez, you're so hopeless.. ♪", "Right, yeah... As long as you don't just cum on your own, sure, let's do it", "Y-yeah... I sort of want to do it, too... ehehe...", "S-sure... Ehehe, I'm, uh, kind of interested, too...", "Gotcha, sounds like a plan!", "Huhu... I want to do it with a pervert like you.", "Ehehe... In that case, let's go hog wild ♪", "Got'cha. Hehe. Now I won't go easy on you.", "Huhuh, I sort of want to do it too.", "Well, I s'pose once in a while wouldn't hurt ♪")
    elif ct("Yandere"):
        $ rc("You won't be able to think about anybody else besides me after I'm done with you ♪", "Oh? You seem quite confident. I'm looking forward to this ♪", "*giggle* I'll give you a feeling you'll never get from anyone else...", "Yes, let's have passionate sex, locked together ♪", "If we have sex you will never forget me, right? ♪", "Heh heh... You're going to feel a lot of pleasure. Try not to break on me.")
    elif ct("Kamidere"):
        $ rc("That expression on your face... Hehe, do you wanna fuck me that much?", "Fufu... I hope you are looking forward to this...!", "Feel grateful for even having the opportunity to touch my body.", "Alright, I'll just kill some time playing around with your body...", "You're raring to go, aren't you? Very well, let's see what you've got.", "Hhmn... My, my... you love my body so much? Of course you do, it can't be helped.", "Very well, entertain me the best you can.",  "...For now, I'm open to the idea.", "I don't really want to, but since you look so miserable I'll allow it.", "Haa, in the end, it turned out like this...  Fine then, do as you like.")
    else:
        $ rc("Oh... I guess if you like me it's ok.", "If you're so fascinated with me, let's do it.", "If you do it, then... please make sure it feels good.",  "I don't mind. Now get yourself ready before I change my mind.", "You're this horny...? Fine, then...", "Okay... I'd like to.",  "You insist, hm? Right away, then!", "You can't you think of anything else beside having sex? You're such a perv ♪", "You've got good intuition. That was just what I had in mind, hehe ♪", "Yes. Go ahead and let my body overwhelm you.", "All right. Do as you like.")
    $ char.restore_portrait()
    return

label interactions_sex_disagreement: # the character disagrees to do it
    $ char.override_portrait("portrait", "angry")
    if ct("Half-Sister") and dice(65):
        if ct("Impersonal"):
            $ rc("No incest please.", "No. This is wrong.")
        elif ct("Yandere"):
            $ rc("Wait! We're siblings dammit.", "Hey, ummm... Siblings together... Is that really okay?")
        elif ct("Dandere"):
            $ rc("We're siblings. We shouldn't do things like this.", "Do you have sexual desires for your sister...?")
        elif ct("Imouto"):
            $ rc("[hero.hs]! P... please don't say things like that!", "Having sex with a blood relative? That's wrong!")
        elif ct("Tsundere"):
            $ rc("It's... it's wrong to have sexual desire among siblings, isn't it?", "[hero.hs], you idiot! Lecher! Pervert!")
        elif ct("Kuudere"):
            $ rc("...You want your sister's body that much? Pathetic.", "How hopeless can you be to do it with a sibling!")
        elif ct("Ane"):
            $ rc("What? But... I'm your sister.", "Don't you know how to behave yourself, as siblings?")
        elif ct("Kamidere"):
            $ rc("It's unacceptable for siblings to have sex!", "I can't believe... you do that... with your siblings!")
        elif ct("Bokukko"):
            $ rc("Oh boy, you are so weird.", "I'm your sis... Are you really okay with that?")
        else:
            $ rc("No! [hero.hs]! We can't do this!",  "Don't you think that siblings shouldn't be doings things like that?")
    elif ct("Impersonal"):
        $ rc("I see no possible benefit in doing that with you so I will have to decline.", "Keep sexual advances to a minimum.")
    elif ct("Shy") and dice(50):
        $ rc("I... I don't want that! ", "W-we can't do that. ", "I-I don't want to... Sorry.")
    elif ct("Imouto"):
        $ rc("Noooo way!", "I, I think perverted things are bad!", "...I-I'm gonna get mad if you say that stuff, you know? Jeez!", "Y-you dummy! You should be talking about stuff like s-s-sex!")
    elif ct("Dandere"):
        $ rc("You're no good...", "Let's have you explain in full detail why you decided to do that today, hmm?", "You should really settle down.")
    elif ct("Tsundere"):
        $ rc("I'm afraid I must inform you of your utter lack of common sense. Hmph!", "You are so... disgusting!", "You pervy little scamp! Not in a million years!", "Hmph! Unfortunately for you, I'm not that cheap!")
    elif ct("Kuudere"):
        $ rc("G-get the fuck away from me, you disgusting perv.", "...Perv.", "...It looks like I'll have to teach you about this little thing called reality.", "O-of course the answer is no!", "Hmph, how unromantic!", "Don't even suggest something that awful.")
    elif ct("Kamidere"):
        $ rc("Wh-who do you think you are!?", "W-what are you talking about... Of course I'm against that!", "What?! How could you think that I... NO!", "What? Asking that out of the blue? Know some shame!", "The meaning of 'not knowing your place' must be referring to this, eh...?", "I don't know how anyone so despicable as you could exist outside of hell.")
    elif ct("Bokukko"):
        $ rc("He- Hey, Settle down a bit, okay?", "You should keep it in your pants, okay?", "Y-you're talking crazy...", "Hmph! Well no duh!")
    elif ct("Ane"):
        $ rc("If I was interested in that sort of thing I might, but unfortunately...", "Oh my, can't you think of a better way to seduce me?", "No. I have decided that it would not be appropriate.", "I don't think our relationship has progressed to that point yet.", "I think that you are being way too aggressive.", "I'm not attracted to you in ‘that’ way.")
    elif ct("Yandere"):
        $ rc("I've never met someone who knew so little about how pathetic they are.", "...I'll thank you to turn those despicable eyes away from me.", "What? Is that your dying wish? You want to die?")
    else:
        $ rc("No! Absolutely NOT!", "With you? Don't make me laugh.", "Get lost, pervert!", "Woah, hold on there. Maybe after we get to know each other better.", "Don't tell me that you thought I was a slut...?", "How about you fix that 'anytime's fine' attitude of yours, hmm?")
    $ char.restore_portrait()
    return

label interactions_sex_disagreement_slave: # the character disagrees to do it
    $ char.show_portrait_overlay("sweat", "reset")
    $ char.override_portrait("portrait", "indifferent")
    if ct("Impersonal"):
        $ rc("Understood.")
    elif ct("Shy") and dice(50):
        $ rc("Um... I-I see... ")
    elif ct("Imouto"):
        $ rc("If that is your order, [char.mc_ref]...")
    elif ct("Dandere"):
        $ rc("...Do as you please, [char.mc_ref].")
    elif ct("Tsundere"):
        $ rc("Hmph. Go ahead [char.mc_ref], I won't stop you.")
    elif ct("Kuudere"):
        $ rc("I won't resist, [char.mc_ref].")
    elif ct("Kamidere"):
        $ rc("*sigh* If that's how you wish to treat me, [char.mc_ref], then let's do it.")
    elif ct("Bokukko"):
        $ rc("Gotcha. Cant's be helped, I guess.")
    elif ct("Ane"):
        $ rc("Very well, [char.mc_ref]. I obey your order.")
    elif ct("Yandere"):
        $ rc("I see. If I must, [char.mc_ref].")
    else:
        $ rc("Yes, [char.mc_ref]...")
    $ char.restore_portrait()
    $ char.hide_portrait_overlay()
    return

label interaction_check_for_virginity: # here we do all checks and actions with virgin trait when needed
    if ct("Virgin"):
        if "Illusive" in hero.traits or 'Chastity' in char.effects:
            $ current_action = "vag"
            jump interactions_sex_scene_logic_part
        else:
            if char.status == "slave":
                menu:
                    "She warns you that this is her first time. Her value at the market will decrease. Do you want to continue?"
                    "Yes":
                        call interactions_girl_virgin_line from _call_interactions_girl_virgin_line
                    "No":
                        if check_lovers(hero, char) or check_friends(hero, char) or char.get_stat("affection") >= 600:
                            "You changed your mind. She looks a bit disappointed."
                        else:
                            "You changed your mind."
                        jump interaction_scene_choice
            else:
                if (check_lovers(hero, char)) or (check_friends(hero, char) and char.get_stat("affection") >= 600) or ((cgo("SIW") or ct("Nymphomaniac")) and char.get_stat("affection") >= 250) or (ct("Open Minded") and char.get_stat("affection") >= 350):
                    menu:
                        "It looks like this is her first time, and she does not mind. Do you want to continue?"
                        "Yes":
                            call interactions_girl_virgin_line from _call_interactions_girl_virgin_line_1
                            $ char.gfx_mod_stat("disposition", 50)
                            $ char.gfx_mod_stat("affection", affection_reward(char))
                        "No":
                            "You changed your mind. She looks a bit disappointed."
                            jump interaction_scene_choice
                else:
                    "Unfortunately, she's still a virgin and is not ready to part with her virtue just yet."
                    jump interaction_scene_choice

        $ char.remove_trait(traits["Virgin"])
        if "Blood Master" in hero.traits:
            $ char.enable_effect("Blood Connection")
        $ char.mod_stat("health", -10)
    $ current_action = "vag"
    $ just_lost_virginity = True
    jump interactions_sex_scene_logic_part
