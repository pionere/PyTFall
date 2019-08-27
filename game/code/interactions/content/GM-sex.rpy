#init:
#    image libido_hearth = "content/gfx/interface/icons/heartbeat.png"

# lines for the future male libido
# You're a little out of juice at the moment, you might want to wait a bit.
# The spirit is willing, but the flesh is spongy and bruised.
screen int_libido_level(sex_scene_libido):
    hbox:
        xpos 50
        ypos 85
        if sex_scene_libido > 0:
            add "content/gfx/interface/icons/heartbeat.png" at sex_scene_libido_hearth(sex_scene_libido)
        else:
            anchor (.5, .5)
            add im.Sepia("content/gfx/interface/icons/heartbeat.png")

label interactions_hireforsex: # we go to this label from GM menu hire for sex.
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if "SIW" not in char.gen_occs:
        if iam.want_sex(char) is not True or (char.status == "free" and iam.gender_mismatch(char)):
            $ char.gfx_mod_stat("disposition", -randint(15, 35))
            if char.get_stat("joy") > 50:
                $ char.gfx_mod_stat("joy", -randint(2, 4))
                $ char.gfx_mod_stat("affection", -randint(3, 5))
            $ iam.refuse_sex_for_money(char)
            jump girl_interactions
        if iam.check_for_minor_bad_stuff(char):
            jump girl_interactions
    $ m = iam.flag_count_checker(char, "flag_interactions_hireforsex")
    if "Nymphomaniac" in char.traits: # how many times one can hire the character per day
        $ n = 4
    elif "Frigid" in char.traits:
        $ n = 1
    else:
        $ n = 2
    if m > n:
        $ del m, n
        $ iam.refuse_sex_too_many(char)
        $ char.gfx_mod_stat("disposition", -randint(15, 35))
        if char.get_stat("joy") > 50:
            $ char.gfx_mod_stat("joy", -randint(2, 4))
            $ char.gfx_mod_stat("affection", -randint(3, 5))
        jump girl_interactions
    $ del m, n

    if char.flag("quest_cannot_be_fucked") or iam.incest(char): # cannot hire h-s for that stuff, only seduce, seems reasonable
        $ iam.refuse_sex(char)
        jump girl_interactions

    if char.get_stat("vitality") <= char.get_max("vitality")/4 or not char.has_ap(): # no sex with low vitality
        $ iam.refuse_because_tired(char)
        jump girl_interactions

    $ price = char.expected_wage * 10

    if check_friends(char):
        $ price *= .9
    elif char.get_stat("disposition") < -50:
        $ price *= 1.3
    if char.get_stat("affection") > 400:
        $ price *= .8
    elif char.get_stat("affection") < -50:
        $ price *= 1.6

    if iam.gender_mismatch(char):
        $ price *= 2.5
    if "Nymphomaniac" in char.traits:
        $ price *= .95
    elif "Frigid" in char.traits:
        $ price *= 1.25
    if "Virgin" in char.traits:
        $ price *= 1.2

    $ temp = hero.get_stat("charisma")/(max(1, char.get_stat("charisma"))*10)
    $ price = round_int(price*(max(.35, 1 - temp)))
    $ del temp

    $ iam.accept_sex_for_money(char, price)

    if hero.gold < price:
        "You don't have that much money."
        $ iam.flag_count_checker(char, "flag_interactions_hireforsex") # additionally reduce the amount of tries
    else:
        menu:
            "[char.pC] wants [price] Gold. Do you want to pay?"

            "Yes":
                $ hero.take_money(price, reason="Sexual Services")
                $ char.add_money(price, reason="Sexual Services")
                $ del price
                $ raped_by_player = False if "SIW" in char.gen_occs else char.has_flag("raped_by_player")
                jump interactions_sex_scene_select_place
            "No":
                $ char.gfx_mod_stat("disposition", -randint(1, 3))
    $ del price
    jump girl_interactions

label interactions_sex: # we go to this label from GM menu propose sex
    if hero.PP < 100 - iam.PP_COST: # PP_PER_AP
        $ hero.PP += iam.PP_COST
        $ PyTGFX.message("You don't have time (Action Point) for that!")
        jump girl_interactions
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if iam.check_for_minor_bad_stuff(char):
        jump girl_interactions
    $ m = iam.flag_count_checker(char, "flag_interactions_sex")
    $ n = randint(2,3)
    if "Nymphomaniac" in char.traits:
        $ n += 2
    elif check_lovers(char):
        $ n += randint(1,2)
    elif check_friends(char):
        $ n += randint(0,1)

    if m > n:
        $ del m, n
        $ iam.refuse_sex_too_many(char)
        $ char.gfx_mod_stat("disposition", -randint(15, 30))
        $ char.gfx_mod_stat("affection", -randint(4, 6))
        if char.get_stat("joy") > 50:
            $ char.gfx_mod_stat("joy", -randint(2, 4))
        jump girl_interactions
    $ del m, n

    if char.flag("quest_cannot_be_fucked") == True: # a special flag for chars we don't want to be accessible unless a quest will be finished
        $ iam.refuse_sex(char)
        jump girl_interactions

    if char.status == "free" and iam.gender_mismatch(char):
        $ iam.refuse_because_of_gender(char) # you can hire them, but they will never do it for free with wrong orientation
        jump girl_interactions

    if char.get_stat("vitality") < char.get_max("vitality")/4 or not char.has_ap():
        $ iam.refuse_because_tired(char)
        jump girl_interactions

    $ temp = iam.want_sex(char)
    if temp is True:
        if char.status == "slave" and iam.gender_mismatch(char):
            $ temp = "females" if hero.gender == "male" else "males"
            "Although [char.p] prefers [temp], [char.p] reluctantly agrees."
            $ char.gfx_mod_stat("joy", -10)
    else:
        if char.status == "free":
            $ iam.refuse_sex(char)
            # the difference between required for sex and current disposition ...
            if temp == "blowoff":
                #  is high -> significant penalty
                $ char.gfx_mod_stat("disposition", -randint(30, 60))
                $ char.gfx_mod_stat("affection", -randint(10, 20))
            else:
                #  is low -> low penalty
                $ char.gfx_mod_stat("disposition", -randint(20, 35))
                $ char.gfx_mod_stat("affection", -randint(8, 12))
            $ del temp
            jump girl_interactions
        else:
            $ iam.slave_refuse_sex(char)
            "[char.pC] doesn't like you enough yet, but as a slave [char.p] has no choice. Do you wish to force [char.op]?"
            menu:
                "Yes":
                    if "SIW" in char.gen_occs:
                        $ char.gfx_mod_stat("joy", -randint(1, 5))
                        if char.get_stat("disposition") > 50:
                            $ char.gfx_mod_stat("disposition", -randint(25, 50))
                        $ char.gfx_mod_stat("affection", -randint(8, 12))
                    else:
                        $ char.gfx_mod_stat("joy", -randint(20, 30))
                        $ char.gfx_mod_stat("disposition", -randint(50, 100))
                        $ char.gfx_mod_stat("affection", -randint(15, 25))
                    $ char.set_flag("raped_by_player")
                "No":
                    $ del temp
                    jump girl_interactions
    $ del temp

    $ raped_by_player = char.has_flag("raped_by_player")
    if not raped_by_player:
        $ iam.accept_sex(char)
    # restore interaction-cost before take_ap below...
    $ hero.PP += iam.PP_COST
    $ char.PP += iam.PP_COST

label interactions_sex_scene_select_place:
    if "Shy" in char.traits:
        if char.status != "free":
            "[char.pC] is too shy to do it anywhere. You can force [char.op] nevertheless, but [char.p] prefers [char.pd] room."
            menu:
                "Where would you like to do it?"
                "Beach":
                    show bg city_beach with fade
                    $ sex_scene_location = "beach"
                    $ char.gfx_mod_stat("joy", 10 if "Masochist" in char.traits else -10)
                "Park":
                    show bg city_park with fade
                    $ sex_scene_location = "park"
                    $ char.gfx_mod_stat("joy", 10 if "Masochist" in char.traits else -10)
                "Room":
                    show bg girl_room with fade
                    $ sex_scene_location = "room"
        else:
            "[char.pC]'s too shy to do it anywhere. You go to [char.pd] room."
            show bg girl_room with fade
            $ sex_scene_location = "room"
    elif "SIW" in char.gen_occs or "Nymphomaniac" in char.traits or check_lovers(char) or char.get_stat("affection") >= 600 or raped_by_player:
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
    elif "Homebody" in char.traits:
        "[char.pC] doesn't want to do it outdoors, so you go to [char.pd] room."
        show bg girl_room with fade
        $ sex_scene_location = "room"
    else:
        "[char.pC] wants to do it in [char.pd] room."
        show bg girl_room with fade
        $ sex_scene_location = "room"
    $ picture_before_sex = True

label interactions_sex_scene_begins: # here we set initial picture before the scene and set local variables
    $ scene_picked_by_character = True # when it's false, there is a chance that the character might wish to do something on her own

    $ sub = check_submissivity(char)

    if picture_before_sex:
        $ iam.get_picture_before_sex(char, location=sex_scene_location)

    $ sex_count = mc_count = char_count = together_count = cum_count = mast_count = 0 # these variable will decide the outcome of sex scene
    $ sex_prelude = False
    $ max_sex_scene_libido = sex_scene_libido = iam.get_character_libido(char)

    $ char.take_ap(1)
    $ hero.take_ap(1)

    $ char.up_counter("flag_int_had_sex_with_mc")

    if "raped_by_player" not in globals():
        $ raped_by_player = char.has_flag("raped_by_player")
    if not raped_by_player:
        $ iam.before_sex(char)

    jump interaction_scene_choice

label interaction_scene_choice: # here we select specific scene, show needed image, jump to scene logic and return here after every scene
    show screen int_libido_level(sex_scene_libido)

    if char.get_stat("vitality") <= 10:
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

        if dice(sex_scene_libido*10 - 20*sub) and sex_scene_libido > 1 and char.status == "free": # strong willed and/or very horny characters may pick action on their own from time to time
            $ current_action = iam.get_character_wishes(char)
            if sub > 0:
                "[char.pC] is so horny that [char.p] cannot control [char.op]self."
            elif sub == 0:
                "[char.pC] wants to try something else with you."
            else:
                "[char.pC] wants to do something else with you."
            if current_action == "vag":
                $ del current_action
                jump interaction_check_for_virginity
            jump interactions_sex_scene_logic_part

label interaction_sex_scene_choice:
    show screen int_libido_level(sex_scene_libido)

    if not raped_by_player:
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

        "Finger [char.pd] ass":
            $ current_action = "fingerass"
            jump interactions_sex_scene_logic_part

        "Lick [char.pd] ass":
            $ current_action = "lickass"
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
            jump interaction_check_for_virginity

        "Ask for anal sex" if hero.gender == "male":
            $ current_action = "anal"
            jump interactions_sex_scene_logic_part

        "That's all.":
            $ current_action = None # make sure the variable exists

label mc_action_scene_finish_sex:
    hide screen int_libido_level

    if sex_scene_libido > 3 and char.get_stat("vitality") >= 50 and "Nymphomaniac" in char.traits and not raped_by_player:
        $ iam.get_single_sex_picture(char, act="masturbation", location=sex_scene_location, hidden_partner=True)
        "[char.name] is not satisfied yet, so [char.p] quickly masturbates right in front of you."
        $ char.gfx_mod_stat("disposition", -round(sex_scene_libido*3))
        $ char.gfx_mod_stat("affection", -1)

    $ loc_tag = sex_scene_location
    $ excluded = ["scared", "in pain"]
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

    if (together_count > 0 and sex_count > 1) or (sex_count > 2 and char_count > 0 and mc_count > 0):
        $ excluded.extend(["angry", "sad"])
        $ iam.set_img((loc_tag, None), ("profile", "girlmeets"), ("happy", None), exclude=excluded, type="ptls", add_mood=False)

        if not raped_by_player:
            $ char.gfx_mod_stat("disposition", randint(50, 100))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5, "sex"))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5))
            $ iam.after_good_sex(char)
        else:
            "[char.pC] quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 10))
    elif char_count < 1 and mc_count > 0:
        $ excluded.extend(["happy", "ecstatic", "suggestive"])
        $ iam.set_img((loc_tag, None), ("profile", "girlmeets"), ("angry", None), exclude=excluded, type="ptls", add_mood=False)

        if not raped_by_player:
            $ char.gfx_mod_stat("disposition", -randint(15, 35))
            $ char.gfx_mod_stat("affection", -randint(8, 12))
            $ char.gfx_mod_stat("joy", -randint(2, 5))
            $ iam.after_sex_char_never_come(char)
        else:
            "[char.pC] quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 10))
    elif char_count > 0 and mc_count < 1 and cum_count < 1 and sex_count > 0:
        $ excluded.extend(["happy", "ecstatic", "suggestive"])
        $ iam.set_img((loc_tag, None), ("profile", "girlmeets"), ("sad", None), exclude=excluded, type="ptls", add_mood=False)

        if not raped_by_player:
            $ char.gfx_mod_stat("disposition", randint(15, 30))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5, "sex"))
            $ char.gfx_mod_stat("affection", affection_reward(char))
            $ char.gfx_mod_stat("joy", -randint(10, 15))
            $ iam.after_sex_hero_never_come(char)
        else:
            "[char.pC] quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 15))
    elif cum_count > 3 and cum_count > char_count:
        $ excluded.extend(["angry", "sad"])
        $ iam.set_img((loc_tag, None), ("profile", "girlmeets"), ("shy", None), exclude=excluded, type="ptls", add_mood=False)

        if not raped_by_player:
            $ char.gfx_mod_stat("disposition", randint(25, 50))
            $ char.gfx_mod_stat("affection", affection_reward(char))
            $ iam.after_sex_mc_cum_alot(char)
        else:
            "[char.pC] quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 10))
    elif sex_count < 1 and mast_count < 1:
        $ excluded.extend(["happy", "ecstatic", "suggestive"])
        $ iam.set_img((loc_tag, None), ("profile", "girlmeets"), ("angry", None), exclude=excluded, type="ptls", add_mood=False)

        if char.status == "slave":
            "[char.pC] is puzzled and confused by the fact that you didn't do anything. [char.pC] quickly leaves, probably thinking that you teased [char.op]."
        else:
            "[char.pC] is quite upset and irritated because you didn't do anything. [char.pC] quickly leaves, probably thinking that you teased [char.op]."
            $ char.gfx_mod_stat("disposition", -randint(50, 100))
            $ char.gfx_mod_stat("affection", -randint(8,12))
            $ char.gfx_mod_stat("joy", -randint(15, 30))
            $ char.mod_stat("vitality", -5)
    elif mast_count > 0 and mc_count < 1 and char_count < 1:
        $ excluded.extend(["angry", "sad"])
        $ iam.set_img((loc_tag, None), ("profile", "girlmeets"), ("shy", None), exclude=excluded, type="ptls", add_mood=False)

        "[char.pC] did nothing but masturbated in front of you. Be prepared for rumors about your impotence or orientation."
        if not raped_by_player:
            $ char.gfx_mod_stat("disposition", -randint(10, 25))
            $ char.gfx_mod_stat("affection", -randint(0,3))
        $ iam.disappointed(char)
        $ char.mod_stat("vitality", -5)
    else:
        $ excluded.extend(["angry", "sad"])
        $ iam.set_img((loc_tag, None), ("profile", "girlmeets"), ("happy", None), exclude=excluded, type="ptls", add_mood=False)

        if not raped_by_player:
            $ char.gfx_mod_stat("disposition", randint(30, 60))
            $ char.gfx_mod_stat("affection", affection_reward(char, .4, "sex"))
            $ char.gfx_mod_stat("affection", affection_reward(char, .4))
            $ iam.after_normal_sex(char)
        else:
            "[char.pC] quickly dresses up and leaves."
        $ char.mod_stat("vitality", -randint(5, 10))

    $ iam.restore_img()

    $ del excluded, loc_tag, sub, sex_count, mc_count, char_count, together_count, cum_count, mast_count, sex_prelude, max_sex_scene_libido, sex_scene_libido, sex_scene_location, scene_picked_by_character, picture_before_sex, current_action, raped_by_player

    jump girl_interactions_end

label interactions_lesbian_choice:
    $ sex_scene_libido -= 1
    # The interactions itself.
    # Since we called a function, we need to do so again (Consider making this func a method so it can be called just once)...
    if "Lesbian" in char.traits or "Bisexual" in char.traits or "Open Minded" in char.traits:
        if check_lovers(char):
            "She gladly agrees to make a show for you."
        elif check_friends(char) or char.get_stat("affection") > 600:
            "A bit hesitant, she agrees to do it for you."
        else:
            "Unfortunately, she does not want to do it."
            jump interaction_scene_choice
    else:
        if check_lovers(char):
            "She gladly agrees to make a show for you if there will be some straight sex as well today."
        elif (check_friends(char) or char.get_stat("affection") > 600) and "SIW" in char.gen_occs:
            "She prefers men but agrees to make a show for you if there will be some straight sex as well today."
        else:
            "Unfortunately, she does not like girls in that way."
            jump interaction_scene_choice
    $ willing_partners = iam.find_les_partners(char)
    if not willing_partners:
        "Unfortunately, you could not find a willing partner."
        $ del willing_partners
        jump interaction_scene_choice

    # Single out one partner randomly from a set:
    $ char2 = random.choice(willing_partners)

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

    # Resize images to be slightly smaller than half a screen in width and the screen in height. *Scale will do the rest.
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
        $ iam.get_single_sex_picture(char, act="2c hug", location=sex_scene_location, hidden_partner=True)
        if raped_by_player:
            "You can feel [char.pd] tense up as you put your arm around [char.op]."
        else:
            "[char.name] feels comfortable in your arms. [char.pdC] chest moves up and down as [char.p] breaths."
            if dice(40):
                extend " You can feel [char.pd] heart starts to beat faster. [char.pC] is more aroused now."
                $ sex_scene_libido += 2

    elif current_action == "kiss":
        $ iam.get_single_sex_picture(char, act="2c kiss", location=sex_scene_location, hidden_partner=True)
        if raped_by_player:
            "[char.pdC] lips are closed tightly. You have to force your tongue to reach inside."
        else:
            "[char.pdC] soft lips welcoming your approach. Your gently move around, back and forth in [char.pd] mouth."
            if dice(50):
                extend " You don't have to wait too long for a response. [char.pC] is more aroused now."
                $ sex_scene_libido += 2

    elif current_action == "strip":
        $ iam.get_single_sex_picture(char, act="stripping", location=sex_scene_location, hidden_partner=True)

        $ char_skill_for_checking = char.get_skill("refinement") + char.get_skill("strip")
        $ mc_skill_for_checking = 2 * hero.get_skill("refinement")
        $ temp = randint(1, 5)
        if (mc_skill_for_checking - char_skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("strip", 0, temp)
        $ char.mod_stat("vitality", -randint(1, 5))

        if char_skill_for_checking >= 1000:
            "[char.pC] looks unbearably hot and sexy. After a short time, you cannot withstand it anymore and begin to masturbate, quickly cumming. [char.pC] looks at you with a smile and superiority in [char.pd] eyes."
        elif char_skill_for_checking >= 750:
            "[char.pdC] movements are so fascinating that you cannot look away from [char.op]. [char.pC] looks proud and pleased."
        elif char_skill_for_checking >= 500:
            "Looking at [char.pd] graceful and elegant moves is nice."
        elif char_skill_for_checking >= 200:
            "[char.pC] did [char.pd] best to show you [char.pd] body, but [char.pd] skills could be improved."
        elif char_skill_for_checking >= 50:
            "[char.pC] tried [char.pd] best, but the moves were quite clumsy and unnatural. At least [char.p] learned something new today."
        else:
            "It looks like [char.name] barely knows what [char.p] is doing. Even just standing still without clothes would have made a better impression."

        $ del char_skill_for_checking, mc_skill_for_checking, temp

    elif current_action == "mast":
        $ iam.get_single_sex_picture(char, act="masturbation", location=sex_scene_location, hidden_partner=True)
        if raped_by_player:
            "[char.pC] pleasures [char.op]self briefly, hesitantly avoiding your glance."
        else:
            if sub < 0:
                "[char.pC] leisurely pleasures [char.op]self for a while, seductively glancing at you."
            elif sub > 0:
                "[char.pC] diligently pleasures [char.op]self for a while until you tell [char.op] to stop."
            else:
                "[char.pC] pleasures [char.op]self briefly, hesitantly avoiding your glance."
            if dice(60):
                extend " [char.pC] is more aroused now."
                $ sex_scene_libido += 2
        $ char.mod_stat("vitality", -randint(5, 10))
        $ mast_count +=1

    elif current_action == "caresstits":
        $ iam.get_single_sex_picture(char, act="2c caresstits", location=sex_scene_location, hidden_partner=True)
        if raped_by_player:
            "You grab her tits with force."
            if "Big Boobs" in char.traits:
                extend " You squeeze as much as you can."
            elif "Abnormally Large Boobs" in char.traits:
                extend " Your hands are not big enough to hold her enormous breasts in place."
            elif "Small Boobs" in char.traits:
                extend " You can barely feel them at all."
            else:
                extend " They feel cold but hard."
        else:
            "You hold her breast in your hands. [char.name] looks into your eyes with much expectation."
            if "Big Boobs" in char.traits:
                extend " It feels nice to play around with those beautiful peaches."
            elif "Abnormally Large Boobs" in char.traits:
                extend " Your fingers dig deep into her enormous breasts."
            elif "Small Boobs" in char.traits:
                extend " You can feel as her nips became hard."
            else:
                extend " Her apples fit perfectly."
            $ sex_scene_libido += 2
        $ char.mod_stat("vitality", -randint(1, 5))

    elif current_action == "fingervag":
        $ iam.get_single_sex_picture(char, act="2c vaginalfingering", location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_gives from _call_interaction_sex_scene_check_skill_gives

    elif current_action == "lickvag":
        $ iam.get_single_sex_picture(char, act="2c lickpussy", location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_gives from _call_interaction_sex_scene_check_skill_gives_1

    elif current_action == "fingerass":
        $ iam.get_single_sex_picture(char, act="2c analfingering", location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_gives from _call_interaction_sex_scene_check_skill_gives_2

    elif current_action == "lickass":
        $ iam.get_single_sex_picture(char, act="2c lickanus", location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_gives from _call_interaction_sex_scene_check_skill_gives_3

    elif current_action == "blow":
        $ iam.get_single_sex_picture(char, act="bc blowjob" if hero.gender == "male" else "bc lickpussy",
                                 location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_jobs from _call_interaction_sex_scene_check_skill_jobs

    elif current_action == "tits":
        $ iam.get_single_sex_picture(char, act="bc titsjob", location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_jobs from _call_interaction_sex_scene_check_skill_jobs_1

    elif current_action == "hand":
        $ iam.get_single_sex_picture(char, act="bc handjob" if hero.gender == "male" else "bc vaginalhandjob",
                                 location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_jobs from _call_interaction_sex_scene_check_skill_jobs_2

    elif current_action == "foot":
        $ iam.get_single_sex_picture(char, act="bc footjob" if hero.gender == "male" else "bc vaginalfootjob",
                                 location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_jobs from _call_interaction_sex_scene_check_skill_jobs_3

    elif current_action == "vag":
        $ iam.get_single_sex_picture(char, act="2c vaginal", location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_acts from _call_interaction_sex_scene_check_skill_acts

    elif current_action == "anal":
        $ iam.get_single_sex_picture(char, act="2c anal", location=sex_scene_location, hidden_partner=True)

        call interaction_sex_scene_check_skill_acts from _call_interaction_sex_scene_check_skill_acts_1

    $ sex_scene_libido -= 1
    jump interaction_scene_choice

label interaction_sex_scene_check_skill_jobs: # skill level check for char side actions
    $ image_tags = iam.get_image_tags()
    if current_action == "hand":
        $ char_skill_for_checking = char.get_skill("oral") + char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = 2 * hero.get_skill("sex")
        $ temp = randint(2, 10)
        if (mc_skill_for_checking - char_skill_for_checking) > 250 and dice(75):
            $ temp += randint(2, 10)
        $ char.gfx_mod_skill("sex", 0, temp)
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if hero.gender == "male":
            if sub < 0:
                "[char.name] grabs you with [char.pd] soft hands."
            elif sub > 0:
                "[char.name] wraps [char.pd] soft hands around your dick."
            else:
                "[char.name] takes your dick in [char.pd] soft hands."

            if char_skill_for_checking <= 200:
                if sub < 0:
                    $ temp = ("[char.pC] strokes you a bit too quickly, the friction is a bit uncomfortable.", "[char.pC] begins to stroke you very quickly. But because of the speed your cock often slips out of [char.pd] hand.")
                elif sub > 0:
                    $ temp = ("[char.pC] strokes you gently. [char.pC] isn't quite sure however what to make of the balls.", "[char.pC] makes up for [char.pd] inexperience with determination, carefully stroking your cock.")
                else:
                    $ temp = ("[char.pC] squeezes one of your balls too tightly, but stops when you wince.", "[char.pC] has a firm grip, and [char.p] is not letting go.")
            elif char_skill_for_checking < 500:
                if sub < 0:
                    $ temp = ("[char.pdC] fingers cause tingles as they caress the shaft.", "[char.pC] quickly strokes you, with a very deft pressure.")
                elif sub > 0:
                    $ temp = ("[char.pC] gently caresses the shaft, and cups the balls in [char.pd] other hand, giving them a warm massage.", "[char.pC] moves very smoothly, stroking casually and very gently.")
                else:
                    $ temp = ("[char.pdC] hands glide smoothly across it.", "[char.pC] moves [char.pd] hands up and down. [char.pC] is a little rough at this, but [char.p] tries [char.pd] best.")
            else:
                if sub < 0:
                    $ temp = ("[char.pdC] movements are masterful, [char.pd] slightest touch starts you twitching.", "[char.pdC] expert strokes will have you boiling over in seconds.")
                elif sub > 0:
                    $ temp = ("[char.pC] gently blows across the tip as [char.pd] finger dance along the shaft.", "[char.pC] slowly caresses you in a way that makes your blood boil, then pulls back at the last second.")
                else:
                    $ temp = ("[char.pC] knows what to do now, and rubs you with smooth strokes, focusing occasionally on the head.", "You can't tell where [char.pd] hand is at any moment, all you know is that it works.")
        else:
            if sub < 0:
                "[char.name] grabs you with [char.pd] soft hands."
            elif sub > 0:
                "[char.name] takes your pussy in [char.pd] palms."
            else:
                "[char.name] puts [char.pd] hands on your pussy."

            if char_skill_for_checking <= 200:
                if sub < 0:
                    $ temp = ("[char.pC] strokes you a bit too quickly, the friction is a bit uncomfortable.", "[char.pC] begins to stroke you very quickly. But because of the speed your pussy becomes a bit swollen.")
                elif sub > 0:
                    $ temp = ("[char.pC] strokes you gently. [char.pC] isn't quite sure however what to make of the lips.", "[char.pC] makes up for [char.pd] inexperience with determination, carefully stroking your pussy.")
                else:
                    $ temp = ("[char.pC] squeezes your pussy too tightly, but stops when you wince.", "[char.pC] has a firm grip, and [char.p] is not letting go.")
            elif char_skill_for_checking < 500:
                if sub < 0:
                    $ temp = ("[char.pdC] fingers cause tingles as they caress the shaft.", "[char.pC] quickly strokes you, with a very deft pressure.")
                elif sub > 0:
                    $ temp = ("[char.pC] gently caresses your pussy and cups your ass in [char.pd] other hand, giving them a warm massage.", "[char.pC] moves very smoothly, stroking casually and very gently.")
                else:
                    $ temp = ("[char.pdC] hands glide smoothly across it.", "[char.pC] moves [char.pd] hands up and down. [char.pC] is a little rough at this, but [char.p] tries [char.pd] best.")
            else:
                if sub < 0:
                    $ temp = ("[char.pdC] movements are masterful, [char.pd] slightest touch starts you twitching.", "[char.pdC] expert strokes will have you boiling over in seconds.")
                elif sub > 0:
                    $ temp = ("[char.pC] gently blows across the lips as [char.pd] finger dance on your leg.", "[char.pC] slowly caresses you in a way that makes your blood boil, then pulls back at the last second.")
                else:
                    $ temp = ("[char.pC] knows what to do now, and rubs you with smooth strokes.", "You can't tell where [char.pd] hand is at any moment, all you know is that it works.")
        $ narrator(choice(temp))
        if "after sex" in image_tags:
            "Soon you generously cover [char.pd] body with your thick liquid."
    elif current_action == "tits":
        $ char_skill_for_checking = char.get_skill("oral") + char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = 2 * hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (mc_skill_for_checking - char_skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("oral", 0, temp)
        $ char.gfx_mod_skill("sex", 0, randint(1, 4))
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if sex_scene_libido > 0 and not raped_by_player:
            if sub < 0:
                "[char.name] massages her boobs, defiantly looking at your crotch."
            elif sub > 0:
                "Holding her boobs, [char.name] meekly approaches you."
            else:
                "[char.name] playfully grabs her boobs, looking at you."
        else:
            if sub < 0:
                "[char.name] massages her boobs, preparing them."
            elif sub > 0:
                "[char.name] holds her boobs, meekly looking at you."
            else:
                "[char.name] grabs her boobs and approaches you."
        if "Big Boobs" in char.traits:
            extend " She wraps her big soft breasts around you."
        elif "Abnormally Large Boobs" in char.traits:
            extend " You almost lost yourself in her enormous breasts as they envelop you."
        elif "Small Boobs" in char.traits:
            extend " She begins to rub her small breasts around you assiduously." # assiduously, really? :D
        else:
            extend " She squeezes you between her soft breasts."

        if char_skill_for_checking <= 200:
            if sub < 0:
                $ temp = ("She kind of bounces her tits around your cock.", "She tries to quickly slide the cock up and down between her cleavage, but it tends to slide out.")
            elif sub > 0:
                $ temp = ("She slides the cock up and down between her cleavage.", "She squeezes her cleavage as tight as she can and rubs up and down.")
            else:
                $ temp = ("She sort of squishes her breasts back and forth around your cock.", "She slaps her tits against your dick, bouncing her whole body up and down.")
        elif char_skill_for_checking < 500:
            if sub < 0:
                $ temp = ("She juggles her breasts up and down around your cock.", "She moves her boobs up and down in a fluid rocking motion.")
            elif sub > 0:
                $ temp = ("She gently caresses the shaft between her tits.", "She lightly brushes the head with her chin as it pops up between her tits.")
            else:
                $ temp = ("Sometimes she pauses to rub her nipples across the shaft.", "She rapidly slides the shaft between her tits")
        else:
            if sub < 0:
                $ temp = ("She rapidly rocks her breasts up and down around your cock, covering them with drool to keep things well lubed.", "In as she strokes faster and faster, she bends down to suck on the head.")
            elif sub > 0:
                $ temp = ("In between strokes she gently sucks on the head.", "She drips some spittle down to make sure you're properly lubed.")
            else:
                $ temp = ("She licks away at the head every time it pops up between her tits.", "She dancers her nipples across the shaft.")
        $ narrator(choice(temp))
        if "after sex" in image_tags:
            if sub < 0:
                "At the last moment, she pulls away, covering herself with your thick liquid."
            elif sub > 0:
                "At the last moment, you take it away from her chest, covering her body with your thick liquid."
            else:
                "At the last moment, she asked you to take it away from her chest to cover her body with your thick liquid."
    elif current_action == "blow":
        $ char_skill_for_checking = char.get_skill("oral") + char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = 2 * hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (mc_skill_for_checking - char_skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("oral", 0, temp)
        $ char.gfx_mod_skill("sex", 0, randint(1, 4))
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if sub < 0:
            if sex_scene_libido > 0 and not raped_by_player:
                "[char.name] licks [char.pd] lips, defiantly looking at your crotch."
            else:
                "[char.name] joylessly looks at your crotch."
            if "bc deepthroat" in image_tags and hero.gender == "male":
                extend " [char.pC] shoves it all the way into [char.pd] throat."
            elif not raped_by_player:
                extend " [char.pC] enthusiastically begins to lick and suck it."
            else:
                extend " [char.pC] begins to lick and suck it."
        elif sub > 0:
            if sex_scene_libido > 0 and not raped_by_player:
                "Glancing at your crotch, [char.name] is patiently waiting for your orders."
            else:
                "[char.name] is waiting for your orders."
            if hero.gender == "male":
                if "bc deepthroat" in image_tags:
                    extend " You told [char.op] to take your dick in [char.pd] mouth as deeply as [char.p] can, and [char.p] diligently obeyed."
                elif not raped_by_player:
                    extend " You told [char.op] to lick and suck your dick, and [char.p] immediately obeyed."
                else:
                    extend " You told [char.op] to lick and suck your dick."
            else:
                extend " You told [char.op] to lick and suck your pussy."
        else:
            if sex_scene_libido > 0 and not raped_by_player:
                "[char.name] quickly approached your crotch."
            else:
                "[char.name] slowly approached your crotch."
            if hero.gender == "male":
                if "bc deepthroat" in image_tags:
                    extend " You shove your dick deep into [char.pd] throat."
                else:
                    extend " [char.pC] begins to lick and suck your dick."
            else:
                extend " [char.pC] begins to lick and suck your pussy."

        if hero.gender == "male":
            if char_skill_for_checking <= 200:
                if sub < 0:
                    $ temp = ("[char.pdC] head bobs rapidly, until [char.p] goes a bit too deep and starts to gag.", "[char.pC] begins to suck very quickly. But because of the speed your cock often pops out of [char.pd] mouth.")
                elif sub > 0:
                    $ temp = ("[char.pC] tentatively kisses and licks around the head.", "[char.pC] licks all over your dick, but [char.p] doesn't really have a handle on it.")
                else:
                    $ temp = ("[char.pC] bobs quickly on your cock, but clamps down a bit too tight.", "[char.pC] puts the tip in [char.pd] mouth and starts suck in as hard as [char.p] can. [char.pC] is a little rough at this, but at least [char.p] tries [char.pd] best.")
            elif char_skill_for_checking < 500:
                if sub < 0:
                    $ temp = ("[char.pC] licks [char.pd] way down the shaft, and gently teases the balls.", "[char.pdC] mouth envelopes the head, then [char.p] quickly draws it in and draws back with a pop.")
                elif sub > 0:
                    $ temp = ("[char.pC] gently caresses the shaft, and cups the balls in [char.pd] other hand, giving them a warm massage.", "[char.pC] moves [char.pd] tongue very smoothly and very gently, keeping [char.pd] teeth well clear, aside from a playful nip.")
                else:
                    $ temp = ("[char.pC]'s settled into a gentle licking pace that washes over you like a warm bath.", "[char.pC] licks up and down the shaft. A little rough, but at least [char.p] tries [char.pd] best.")
            else:
                if sub < 0:
                    $ temp = ("[char.pC] rapidly bobs up and down on your cock, a frenzy of motion.", "[char.pC] puts the tip into [char.pd] mouth and [char.pd] tongue swirls rapidly around it.")
                elif sub > 0:
                    $ temp = ("[char.pC] gently blows across the head as [char.p] covers your cock in smooth licks.", "[char.pC] moves very smoothly, tongue dancing casually and very gently.")
                else:
                    $ temp = ("[char.pdC] deft licks are masterful, your cock twitches with each stroke.", "[char.pC]'s really good at this, alternating between deep suction and gentle licks.")
            $ narrator(choice(temp))
            if "after sex" in image_tags:
                if sub < 0:
                    "At the last moment, [char.p] pulls it out, covering [char.op]self with your thick liquid."
                elif sub > 0:
                    "At the last moment, you pull it out from [char.pd] mouth, covering [char.pd] body with your thick liquid."
                else:
                    "[char.pC] asked you to pull it out from [char.pd] mouth at the last moment to cover [char.pd] body with your thick liquid."
        else: # female hero -> lick pussy
            if char_skill_for_checking <= 200:
                if sub < 0:
                    $ temp = ("[char.pdC] head bobs rapidly.", "[char.pC] begins to suck very quickly. Because of the speed your pussy become reddish.")
                elif sub > 0:
                    $ temp = ("[char.pC] tentatively kisses and licks in the valley.", "[char.pC] licks all over your pussy, but [char.p] doesn't really have a handle on it.")
                else:
                    $ temp = ("[char.pC] bobs quickly on your pussy, but [char.pd] movements are a bit rough.", "[char.pC] puts [char.pd] mouth on your pussy and starts suck in as hard as [char.p] can. [char.pC] is a little rough at this, but at least [char.p] tries [char.pd] best.")
            elif char_skill_for_checking < 500:
                if sub < 0:
                    $ temp = ("[char.pC] licks [char.pd] way down the valley, and gently teases the anus.", "[char.pdC] mouth envelopes your pussy, then [char.p] quickly draws it in and draws back with a pop.")
                elif sub > 0:
                    $ temp = ("[char.pC] gently caresses the lips and cups the ass-cheeks in [char.pd] other hand, giving them a warm massage.", "[char.pC] moves [char.pd] tongue very smoothly and very gently, keeping [char.pd] teeth well clear, aside from a playful nip.")
                else:
                    $ temp = ("[char.pC]'s settled into a gentle licking pace that washes over you like a warm bath.", "[char.pC] licks up and down the valley. A little rough, but at least [char.p] tries [char.pd] best.")
            else:
                if sub < 0:
                    $ temp = ("[char.pC] rapidly bobs up and down the valley, a frenzy of motion.", "[char.pC] puts [char.pd] mouth on your pussy and [char.pd] tongue runs up and down rapidly.")
                elif sub > 0:
                    $ temp = ("[char.pC] gently blows across the lips as [char.p] covers your pussy in smooth licks.", "[char.pC] moves very smoothly, tongue dancing casually and very gently.")
                else:
                    $ temp = ("[char.pdC] deft licks are masterful, your pussy twitches with each stroke.", "[char.pC]'s really good at this, alternating between deep suction and gentle licks.")
            $ narrator(choice(temp))

        $ char.gfx_mod_stat("affection", affection_reward(char, .5, "oral"))
    elif current_action == "foot":
        $ char_skill_for_checking = char.get_skill("refinement") + char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = 2 * hero.get_skill("sex")
        $ temp = randint(2, 10)
        if (mc_skill_for_checking - char_skill_for_checking) > 250 and dice(75):
            $ temp += randint(2, 10)
        $ char.gfx_mod_skill("sex", 0, temp)
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if sub < 0:
            if sex_scene_libido > 0 and not raped_by_player:
                "With a sly smile [char.name] gets closer to you."
            else:
                "[char.name] gets closer to you."
        elif sub > 0:
            "You asked [char.name] to use [char.pd] feet."
        else:
            "[char.name] sits next to you."
        if hero.gender == "male":
            $ temp = "Long Legs" in char.traits
            if "Athletic" in char.traits:
                if temp:
                    "[char.pC] squeezes your dick between [char.pd] long muscular legs and stimulates it until you cum."
                else:
                    "[char.pC] squeezes your dick between [char.pd] muscular legs and stimulates it until you cum."
            elif "Slim" in char.traits:
                if temp:
                    "[char.pC] squeezes your dick between [char.pd] long slim legs and stimulates it until you cum."
                else:
                    "[char.pC] squeezes your dick between [char.pd] slim legs and stimulates it until you cum."
            elif "Lolita" in char.traits:
                if temp:
                    "[char.pC] squeezes your dick between [char.pd] long thin legs and stimulates it until you cum."
                else:
                    "[char.pC] squeezes your dick between [char.pd] thin legs and stimulates it until you cum."
            else:
                if temp:
                    "[char.pC] squeezes your dick between [char.pd] long legs and stimulates it until you cum."
                else:
                    "[char.pC] squeezes your dick between [char.pd] legs and stimulates it until you cum."
            if "after sex" in image_tags:
                extend " You generously cover [char.pd] body with your thick liquid."
    else:
        $ raise Exception("Char side sexual interaction '%' is not implemented." % current_action)

    if char_skill_for_checking >= 2000:
        "[char.pC] was so good that you profusely came after a few seconds. Pretty impressive."
        $ char.gfx_mod_stat("joy", randint(3, 5))
        $ hero.mod_stat("joy", randint(4, 6))
    elif char_skill_for_checking >= 1000:
        "You barely managed to hold out for half a minute in the face of [char.pd] amazing skills."
        $ char.gfx_mod_stat("joy", randint(2, 4))
        $ hero.mod_stat("joy", randint(3, 5))
    elif char_skill_for_checking >= 500:
        "It was very fast and very satisfying."
        $ char.gfx_mod_stat("joy", randint(1, 2))
        $ hero.mod_stat("joy", randint(2, 4))
    elif char_skill_for_checking >= 200:
        "Nothing extraordinary, but it wasn't half bad either."
        $ char.gfx_mod_stat("joy", randint(0, 1))
        $ hero.mod_stat("joy", randint(1, 2))
    elif char_skill_for_checking >= 100:
        "It took some time and effort on [char.pd] part. [char.pdC] skills could be improved."
    elif char_skill_for_checking >= 50:
        "It looks like [char.name] barely knows what [char.p] is doing. Still, [char.p] somewhat managed to get the job done."
        $ char.mod_stat("vitality", -randint(5, 10))
    else:
        $ char.mod_stat("vitality", -randint(10, 15))
        "[char.pdC] moves were clumsy and untimely. By the time [char.p] finished the moment had passed, bringing you little satisfaction."
        $ char.gfx_mod_stat("joy", -randint(2, 4))
        $ hero.mod_stat("joy", -randint(1, 2))
    if char_skill_for_checking >= 50:
        $ mc_count += 1
        $ cum_count += 1
    $ del mc_skill_for_checking, char_skill_for_checking, image_tags, temp
    return

label interaction_sex_scene_check_skill_gives: # # skill level check for MC side actions
    if current_action == "lickvag":
        $ char_skill_for_checking = 2 * char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = hero.get_skill("oral") + hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (char_skill_for_checking - mc_skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ hero.gfx_mod_skill("oral", 0, temp)
        $ char.gfx_mod_skill("sex", 0, randint(2, 6))
        $ hero.gfx_mod_skill("sex", 0, randint(1, 4))

        if sex_scene_libido > 0 and not raped_by_player:
            "[char.name] spreads her legs to let you closer."
        else:
            "You have to push her legs apart."
        if not raped_by_player:
            extend " First your tongue just barely touches her pussy, but soon you reach deeper."
        else:
            extend " As you put your tongue inside her, you flex the muscles in your tongue to widen the gap as much as possible."

        if sex_scene_libido > 0:
            if mc_skill_for_checking >= 2000:
                extend " The pleasure from joy went through her body as she reached an orgasm."
                $ char.gfx_mod_stat("joy", randint(3, 5))
                $ hero.mod_stat("joy", randint(2, 4))
            elif mc_skill_for_checking >= 1000:
                extend " You managed to make her cum multiple times."
                $ char.gfx_mod_stat("joy", randint(2, 4))
                $ hero.mod_stat("joy", randint(1, 2))
            elif mc_skill_for_checking >= 500:
                extend " Finally you made her cum."
                $ char.gfx_mod_stat("joy", randint(1, 2))
                $ hero.mod_stat("joy", randint(0, 1))
            elif mc_skill_for_checking >= 200:
                extend " You licked her pussy until she came. It felt good."
                $ char.gfx_mod_stat("joy", randint(0, 1))
            elif mc_skill_for_checking >= 100:
                extend " You licked her pussy until she came."
                $ hero.mod_stat("vitality", -randint(5, 10))
            elif mc_skill_for_checking >= 50:
                extend " You had some difficulties with bringing her to orgasm but managed to overcome them."
                $ hero.mod_stat("vitality", -randint(10, 15))
            else:
                extend " Unfortunately, you didn't have the skill to satisfy her. [char.name] looks disappointed."
                $ hero.mod_stat("vitality", -randint(10, 15))
                $ hero.mod_stat("joy", -randint(0, 2))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5, stat="oral") + affection_reward(char, .5, stat="vaginal"))
    elif current_action == "fingervag":
        $ char_skill_for_checking = 2 * char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = hero.get_skill("refinement") + hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (char_skill_for_checking - mc_skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ hero.gfx_mod_skill("refinement", 0, temp)
        $ char.gfx_mod_skill("sex", 0, randint(2, 6))
        $ hero.gfx_mod_skill("sex", 0, randint(1, 4))

        if sex_scene_libido > 0 and not raped_by_player:
            "[char.name] opens her mouth a bit. Her gaze is filled with anticipation."
        else:
            "[char.name] bites her lips and looks away."
        if not raped_by_player:
            extend " As you touch her lips, they become swollen. A drop of fluid glances at the bottom."  
        else:
            extend " Your fingers dig deep into her. You move in and out of her pussy in quick successions." 

        if sex_scene_libido > 0:
            if mc_skill_for_checking >= 2000:
                extend " The pleasure from joy went through her body as she reached an orgasm."
                $ char.gfx_mod_stat("joy", randint(3, 5))
                $ hero.mod_stat("joy", randint(2, 4))
            elif mc_skill_for_checking >= 1000:
                extend " You managed to make her cum multiple times."
                $ char.gfx_mod_stat("joy", randint(2, 4))
                $ hero.mod_stat("joy", randint(1, 2))
            elif mc_skill_for_checking >= 500:
                extend " Finally you made her cum."
                $ char.gfx_mod_stat("joy", randint(1, 2))
                $ hero.mod_stat("joy", randint(0, 1))
            elif mc_skill_for_checking >= 200:
                extend " You fingered her until she came. It felt good."
                $ char.gfx_mod_stat("joy", randint(0, 1))
            elif mc_skill_for_checking >= 100:
                extend " You fingered her until she came."
                $ hero.mod_stat("vitality", -randint(5, 10))
            elif mc_skill_for_checking >= 50:
                extend " You had some difficulties with bringing her to orgasm but managed to overcome them."
                $ hero.mod_stat("vitality", -randint(10, 15))
            else:
                extend " Unfortunately, you didn't have the skill to satisfy her. [char.name] looks disappointed."
                $ hero.mod_stat("vitality", -randint(10, 15))
                $ hero.mod_stat("joy", -randint(0, 2))
            $ char.gfx_mod_stat("affection", affection_reward(char, .7, stat="vaginal"))
    elif current_action == "lickass":
        $ char_skill_for_checking = 2 * char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = hero.get_skill("oral") + hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (char_skill_for_checking - mc_skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ hero.gfx_mod_skill("oral", 0, temp)
        $ char.gfx_mod_skill("sex", 0, randint(2, 6))
        $ hero.gfx_mod_skill("sex", 0, randint(1, 4))

        if sex_scene_libido > 0 and not raped_by_player:
            "[char.name] spreads [char.pd] legs to let you closer."
        else:
            "You have to push [char.pd] legs apart."
        if not raped_by_player:
            extend " First your tongue just barely touches [char.pd] ass, but soon you reach deeper."
        else:
            extend " As you put your tongue inside [char.op], you flex the muscles in your tongue to widen the gap as much as possible."

        if sex_scene_libido > 0:
            if mc_skill_for_checking >= 2000:
                extend " The pleasure from joy went through [char.pd] body as [char.p] reached an orgasm."
                $ char.gfx_mod_stat("joy", randint(3, 5))
                $ hero.mod_stat("joy", randint(2, 4))
            elif mc_skill_for_checking >= 1000:
                extend " You managed to make [char.op] cum multiple times."
                $ char.gfx_mod_stat("joy", randint(2, 4))
                $ hero.mod_stat("joy", randint(1, 2))
            elif mc_skill_for_checking >= 500:
                extend " Finally you made [char.op] cum."
                $ char.gfx_mod_stat("joy", randint(1, 2))
                $ hero.mod_stat("joy", randint(0, 1))
            elif mc_skill_for_checking >= 200:
                extend " You licked [char.pd] ass until [char.p] came. It felt good."
                $ char.gfx_mod_stat("joy", randint(0, 1))
            elif mc_skill_for_checking >= 100:
                extend " You licked [char.pd] ass until [char.p] came."
                $ hero.mod_stat("vitality", -randint(5, 10))
            elif mc_skill_for_checking >= 50:
                extend " You had some difficulties with bringing [char.op] to orgasm but managed to overcome them."
                $ hero.mod_stat("vitality", -randint(10, 15))
            else:
                extend " Unfortunately, you didn't have the skill to satisfy [char.op]. [char.name] looks disappointed."
                $ hero.mod_stat("vitality", -randint(10, 15))
                $ hero.mod_stat("joy", -randint(0, 2))
            $ char.gfx_mod_stat("affection", affection_reward(char, .5, stat="oral") + affection_reward(char, .5, stat="anal"))
    elif current_action == "fingerass":
        $ char_skill_for_checking = 2 * char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = hero.get_skill("refinement") + hero.get_skill("sex")
        $ temp = randint(1, 5)
        if (char_skill_for_checking - mc_skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ hero.gfx_mod_skill("refinement", 0, temp)
        $ char.gfx_mod_skill("sex", 0, randint(2, 6))
        $ hero.gfx_mod_skill("sex", 0, randint(1, 4))

        if sex_scene_libido > 0 and not raped_by_player:
            "[char.name] opens [char.pd] mouth a bit. [char.pdC] gaze is filled with anticipation."
        else:
            "[char.name] bites [char.pd] lips and looks away."
        if not raped_by_player:
            extend " As you touch [char.pd] rear entrance, it reflexively contracts a bit."  
        else:
            extend " Your fingers dig deep into [char.op]. You move in and out of [char.pd] ass in quick successions." 

        if sex_scene_libido > 0:
            if mc_skill_for_checking >= 2000:
                extend " The pleasure from joy went through [char.pd] body as [char.p] reached an orgasm."
                $ char.gfx_mod_stat("joy", randint(3, 5))
                $ hero.mod_stat("joy", randint(2, 4))
            elif mc_skill_for_checking >= 1000:
                extend " You managed to make [char.op] cum multiple times."
                $ char.gfx_mod_stat("joy", randint(2, 4))
                $ hero.mod_stat("joy", randint(1, 2))
            elif mc_skill_for_checking >= 500:
                extend " Finally you made [char.op] cum."
                $ char.gfx_mod_stat("joy", randint(1, 2))
                $ hero.mod_stat("joy", randint(0, 1))
            elif mc_skill_for_checking >= 200:
                extend " You fingered [char.pd] ass until [char.p] came. It felt good."
                $ char.gfx_mod_stat("joy", randint(0, 1))
            elif mc_skill_for_checking >= 100:
                extend " You fingered [char.op] until [char.p] came."
                $ hero.mod_stat("vitality", -randint(5, 10))
            elif mc_skill_for_checking >= 50:
                extend " You had some difficulties with bringing [char.op] to orgasm but managed to overcome them."
                $ hero.mod_stat("vitality", -randint(10, 15))
            else:
                extend " Unfortunately, you didn't have the skill to satisfy [char.op]. [char.name] looks disappointed."
                $ hero.mod_stat("vitality", -randint(10, 15))
                $ hero.mod_stat("joy", -randint(0, 2))
            $ char.gfx_mod_stat("affection", affection_reward(char, .7, stat="anal"))
    else:
        $ raise Exception("MC side sexual interaction '%' is not implemented." % current_action)

    if sex_scene_libido <= 0:
        if mc_skill_for_checking >= 1000:
            extend " You did your best to make [char.op] cum, but it brought more pain than pleasure judging by [char.pd] expression."
        else:
            " [char.pC] is not in the mood anymore. Your efforts to make [char.op] cum were in vain."

    if mc_skill_for_checking >= 50:
        $ char_count += 1
    $ del mc_skill_for_checking, char_skill_for_checking, temp
    return

label interaction_sex_scene_check_skill_acts: # skill level check for two sides actions
    $ image_tags = iam.get_image_tags()
    if current_action == "vag":
        $ char_skill_for_checking = char.get_skill("vaginal") + char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = hero.get_skill("vaginal") + hero.get_skill("sex")

        if (char_skill_for_checking - mc_skill_for_checking) > 250 and dice(50):
            $ temp = randint(5, 10)
        else:
            $ temp = randint(2, 6)
        $ hero.gfx_mod_skill("vaginal", 0, temp)
        $ temp = randint(1, 5)
        if (mc_skill_for_checking - char_skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("vaginal", 0, temp)
        $ char.gfx_mod_skill("sex", 0, randint(1, 5))
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if sub < 0:
            if sex_scene_libido > 0 and not raped_by_player:
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
        elif sub > 0:
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
            if sex_scene_libido > 0 and not raped_by_player:
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

        if char_skill_for_checking >= 2000:
            "Her technique is fantastic, your bodies move in perfect synchronization, and her pussy feels like velvet."
            $ char.gfx_mod_stat("joy", randint(3, 5))
            $ hero.mod_stat("joy", randint(3, 5))
        elif char_skill_for_checking >= 1000:
            "Her refined skills, rhythmic movements, and wet hot pussy quickly brought you to the finish."
            $ char.gfx_mod_stat("joy", randint(2, 4))
            $ hero.mod_stat("joy", randint(2, 4))
        elif char_skill_for_checking >= 500:
            "Her pussy felt very good, her movement patterns and amazing skills quickly exhausted your ability to hold back."
            $ char.gfx_mod_stat("joy", randint(1, 2))
            $ hero.mod_stat("joy", randint(1, 2))
        elif char_skill_for_checking >= 200:
            "Her movements were pretty good. Nothing extraordinary, but it wasn't half bad either."
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ hero.mod_stat("joy", randint(0, 1))
        elif char_skill_for_checking >= 100:
            "It took some time and effort on her part. Her pussy could use some training."
            $ char.mod_stat("vitality", -randint(5, 10))
        elif char_skill_for_checking >= 50:
            "It looks like [char.name] barely knows what she's doing. Still, it's difficult to screw up such a simple task, so eventually, she got the job done."
            $ char.mod_stat("vitality", -randint(10, 15))
        else:
            "Her moves were clumsy and untimely, and her pussy was too dry. Sadly, she was unable to satisfy you adequately."
            $ char.gfx_mod_stat("joy", -randint(2, 4))
            $ hero.mod_stat("joy", -randint(2, 4))
            $ char.mod_stat("vitality", -randint(10, 15))
        $ char.gfx_mod_stat("affection", affection_reward(char, stat="vaginal"))
    elif current_action == "anal":
        $ char_skill_for_checking = char.get_skill("anal") + char.get_skill("sex")
        if iam.gender_mismatch(char):
            $ char_skill_for_checking *= .8
        $ mc_skill_for_checking = hero.get_skill("anal") + hero.get_skill("sex")
        if (char_skill_for_checking - mc_skill_for_checking) > 250 and dice(50):
            $ temp = randint(5, 10)
        else:
            $ temp = randint(2, 6)
        $ hero.gfx_mod_skill("anal", 0, temp)
        $ temp = randint(1, 5)
        if (mc_skill_for_checking - char_skill_for_checking) > 250 and dice(75):
            $ temp += randint(1, 5)
        $ char.gfx_mod_skill("anal", 0, temp)
        $ char.gfx_mod_skill("sex", 0, randint(1, 4))
        $ hero.gfx_mod_skill("sex", 0, randint(2, 6))

        if sub < 0:
            if sex_scene_libido > 0 and not raped_by_player:
                "[char.name] looking forward to something big inside [char.pd] ass."
            else:
                "[char.name] unenthusiastically prepares [char.pd] ass."
            if "ontop" in image_tags:
                extend " [char.pC] sits on top of you, immersing your dick inside."
            elif "doggy" in image_tags:
                extend " [char.pC] bent over, pushing [char.pd] anus toward your dick."
            elif "missionary" in image_tags:
                extend " [char.pC] lay on [char.pd] back spreading [char.pd] legs, waiting for your dick."
            elif "onside" in image_tags:
                extend " [char.pC] lay down on [char.pd] side, waiting for you to join [char.op]."
            elif "standing" in image_tags:
                extend " [char.pC] spreads [char.pd] legs waiting for you, not even bothering to lay down."
            elif "spooning" in image_tags:
                extend " [char.pC] snuggled to you, being in a mood for some spooning."
            elif "sitting" in image_tags:
                extend " [char.pC] sat on your lap, immersing your dick inside."
            else:
                extend " [char.pC] confidently pushes your dick inside and starts to move."
        elif sub > 0:
            "[char.name] prepares [char.op]self, waiting for further orders."
            if "ontop" in image_tags:
                extend " You ask [char.op] to sit on top of you, immersing your dick inside."
            elif "doggy" in image_tags:
                extend " You ask [char.op] to bend over, allowing you to take [char.op] from behind."
            elif "missionary" in image_tags:
                extend " You ask [char.op] to lay on [char.pd] back and spread [char.pd] legs, allowing you to shove your dick inside."
            elif "onside" in image_tags:
                extend "  You asked [char.op] to lay down on [char.pd] side, allowing you to get inside."
            elif "standing" in image_tags:
                extend " You asked [char.op] to spread [char.pd] legs and pushed your dick inside."
            elif "spooning" in image_tags:
                extend " You asked [char.op] to snuggle with you, spooning [char.op] in the process."
            elif "sitting" in image_tags:
                extend " You asked [char.op] to sit on your lap, immersing your dick inside."
            else:
                extend " You entered [char.op] and asked to start moving."
        else:
            if sex_scene_libido > 0 and not raped_by_player:
                "[char.name] doesn't mind you to do [char.pd] ass."
            else:
                "[char.name] silently offers [char.pd] ass."
            if "ontop" in image_tags:
                extend " You invite [char.op] to sit on top of you, preparing your dick for some penetration."
            elif "doggy" in image_tags:
                extend " [char.pC] bent over, welcoming your dick from behind."
            elif "missionary" in image_tags:
                extend " [char.pC] lays on [char.pd] back and spreads [char.pd] legs, inviting you to enter inside."
            elif "onside" in image_tags:
                extend " [char.pC] lays down on [char.pd] side, inviting you to enter inside."
            elif "standing" in image_tags:
                extend " You proceed to penetrate [char.op] not even bothering to lay down."
            elif "spooning" in image_tags:
                extend " You two snuggle with each other, trying out spooning."
            elif "sitting" in image_tags:
                extend " [char.pC] sits on your lap while you prepare your dick for going inside [char.op]."
            else:
                extend " You enter [char.pd] anus, and you two begin to move."

        if char_skill_for_checking >= 2000:
            "[char.pdC] technique is fantastic, your bodies move in perfect synchronization, and [char.pd] asshole feels nice and tight."
            $ char.gfx_mod_stat("joy", randint(3, 5))
            $ hero.mod_stat("joy", randint(3, 5))
        elif char_skill_for_checking >= 1000:
            "[char.pdC] refined skills, rhythmic movements, and tight hot ass quickly brought you to the finish."
            $ char.gfx_mod_stat("joy", randint(2, 4))
            $ hero.mod_stat("joy", randint(2, 4))
        elif char_skill_for_checking >= 500:
            "[char.pdC] anus felt very good, [char.pd] movement patterns and amazing skills quickly exhausted your ability to hold back."
            $ char.gfx_mod_stat("joy", randint(1, 2))
            $ hero.mod_stat("joy", randint(1, 2))
        elif char_skill_for_checking >= 200:
            "[char.pdC] movements were pretty good. Nothing extraordinary, but it wasn't half bad either."
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ hero.mod_stat("joy", randint(0, 1))
        elif char_skill_for_checking >= 100:
            "It took some time and effort on [char.pd] part. [char.pdC] anus could use some training."
            $ char.mod_stat("vitality", -randint(5, 10))
        elif char_skill_for_checking >= 50:
            "It looks like [char.name] barely knows what [char.p] is doing. Still, it's difficult to screw up such a simple task, so eventually, [char.p] got the job done."
            $ char.mod_stat("vitality", -randint(10, 15))
        else:
            "[char.pdC] moves were clumsy and untimely, and [char.pd] anus wasn't quite ready for that. Sadly, [char.p] was unable to satisfy you adequately."
            $ char.gfx_mod_stat("joy", -randint(2, 4))
            $ hero.mod_stat("joy", -randint(2, 4))
            $ char.mod_stat("vitality", -randint(10, 15))
        $ char.gfx_mod_stat("affection", affection_reward(char, stat="anal"))
    else:
        $ raise Exception("Two sided sexual interaction '%' is not implemented." % current_action)

    if sex_scene_libido > 0:
        if mc_skill_for_checking >= 2000:
            extend " Your bodies merged into a single entity, filling each other with pleasure and satisfaction."
            $ char.gfx_mod_stat("joy", randint(3, 5))
            $ hero.mod_stat("joy", randint(3, 5))
        elif mc_skill_for_checking >= 1000:
            extend " In the end, you both cum together multiple times."
            $ char.gfx_mod_stat("joy", randint(2, 4))
            $ hero.mod_stat("joy", randint(2, 4))
        elif mc_skill_for_checking >= 500:
            extend " In the end, you both cum together."
            $ char.gfx_mod_stat("joy", randint(1, 2))
            $ hero.mod_stat("joy", randint(1, 2))
        elif mc_skill_for_checking >= 200:
            extend " You fucked [char.op] until you both came. It felt good."
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ hero.mod_stat("joy", randint(0, 1))
        elif mc_skill_for_checking >= 100:
            extend " You fucked [char.op] until you both came."
            $ hero.mod_stat("vitality", -randint(5, 10))
        elif mc_skill_for_checking >= 50:
            extend " You had some difficulties with bringing [char.op] to orgasm but managed to overcome them."
            $ hero.mod_stat("vitality", -randint(10, 15))
        else:
            extend " Unfortunately, you didn't have the skill to satisfy [char.op] as well. [char.name] looks disappointed."
            $ char.gfx_mod_stat("joy", -randint(0, 1))
            $ hero.mod_stat("joy", -randint(0, 1))
            $ hero.mod_stat("vitality", -randint(10, 15))
    else:
        if mc_skill_for_checking >= 1000:
            extend " You did your best to make [char.op] cum, but it brought more pain than pleasure judging by [char.pd] expression."
        else:
            " [char.pC] is not in the mood anymore. Your efforts to make [char.op] cum were in vain."

    if "after sex" in image_tags:
        $ cum_count += 1
        if sub < 0:
            "At the last moment, [char.p] pulls it out, covering [char.op]self with your thick liquid."
        elif sub > 0:
            "At the last moment, you pull it out of [char.op], covering [char.pd] body with your thick liquid."
        else:
            "[char.pC] asked you to pull it out from [char.op] at the last moment to cover [char.pd] body with your thick liquid."
    if (mc_skill_for_checking) >= 1000 and (char_skill_for_checking >= 1000):
        $ together_count += 1
    if char_skill_for_checking >= 50:
        $ mc_count += 1
    if mc_skill_for_checking >= 50:
        $ char_count += 1
    $ del mc_skill_for_checking, char_skill_for_checking, image_tags, temp
    if hasattr(store, 'just_lost_virginity'):
        $ del just_lost_virginity
        $ iam.after_sex_virginity_taken(char)
    return

label interaction_check_for_virginity: # here we do all checks and actions with virgin trait when needed
    if "Virgin" in char.traits and hero.gender == "male" and char.gender == "female":
        if "Illusive" in hero.traits or "Chastity" in char.effects:
            $ current_action = "vag"
            jump interactions_sex_scene_logic_part
        else:
            if char.status == "slave":
                menu:
                    "She warns you that this is her first time. Her value at the market will decrease. Do you want to continue?"
                    "Yes":
                        $ iam.before_sex_virgin(char)
                    "No":
                        if check_lovers(char) or check_friends(char) or char.get_stat("affection") >= 600:
                            "You changed your mind. She looks a bit disappointed."
                        else:
                            "You changed your mind."
                        jump interaction_scene_choice
            else:
                if (check_lovers(char)) or (check_friends(char) and char.get_stat("affection") >= 600) or (("SIW" in char.gen_occs or "Nymphomaniac" in char.traits) and char.get_stat("affection") >= 250) or ("Open Minded" in char.traits and char.get_stat("affection") >= 350):
                    menu:
                        "It looks like this is her first time, and she does not mind. Do you want to continue?"
                        "Yes":
                            $ iam.before_sex_virgin(char)
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
        $ just_lost_virginity = True
    $ current_action = "vag"
    jump interactions_sex_scene_logic_part
