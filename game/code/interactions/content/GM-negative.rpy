label interactions_harrasment_after_battle: # after MC provoked a free character and won the battle; -->NOT FOR SLAVES<-- since options here are not suitable for them
    # slaves will not attack MC as long as we don't have dungeon, since after that they pretty much have to be there
    $ m = 1 + iam.flag_count_checker(hero, "harrasment_after_battle") # we don't allow to do it infinitely, chance of success reduces after every attempt
    if dice(30*m): # 30%, +30 per attempt
        "Your fight drew the attention of the City Guards. You better leave before they see you."
        $ m = 80
    elif dice(30*m):
        "The fight drew some attention. The safest would be to leave the scene now."
        $ m = 50
    else:
        "There is no one around at the moment..."
        $ m = 10
    menu:
        "[char.name] is unconscious. What do you do?" # after adding dungeon here will be options to get her there; after adding drugs here will be option to force her consume some;
        # no rape since it takes a lot of time, and time here is kinda limited
        "Rob [char.op]":
            if dice(m):
                "Just as you are searching the body for money a city guard towers above you."
                $ del m
                $ iam.end(safe=True)
                $ pytfall.jail.add_prisoner(hero, "Theft", randint(1,4))
                jump hero_in_jail
                with Fade
            if char.gold <= 0:
                "Sadly, [char.p] has no money. What a waste."
            else:
                python hide:
                    char.gfx_mod_stat("disposition", -randint(10, 25))
                    char.gfx_mod_stat("affection", -randint(1,3))
                    g = char.gold
                    g = randint(min(500, 3*g/5), min(1000, 4*g/5))
                    g = max(1, g)
                    narrator("In %s pockets, you found %s Gold. Lucky!" % (char.pd, g))
                    char.take_money(g, reason="Robbery")
                    hero.add_money(g, reason="Robbery")
        "Search [char.op] for items.":
            if dice(m):
                "Just as you are searching the body, a city guard towers above you."
                $ del m
                $ iam.end(safe=True)
                $ pytfall.jail.add_prisoner(hero, "Theft", randint(1,4))
                jump hero_in_jail
                with Fade
            python hide:
                equips = [i for i in char.eqslots.values() if i and i.price <= 1000 and can_transfer(char, hero, i, silent=True, force=True)]
                invs = [i for i in char.inventory.items.keys() if i.price <= 1000 and can_transfer(char, hero, i, silent=True, force=True)]
                if equips or invs:
                    temp = choice(equips + invs)
                    narrator("On %s you found %s!" % (char.op, temp.id))
                    reequip = False
                    if temp not in invs:
                        char.unequip(temp)
                        reequip = True
                    transfer_items(char, hero, temp, amount=1, silent=True, force=True)
                    if reequip:
                        char.auto_equip(char.last_known_aeq_purpose)
                    char.gfx_mod_stat("disposition", -randint(20, 45))
                    char.gfx_mod_stat("affection", -randint(3,5))
                else:
                    narrator("You didn't find anything...")
        "Kill [char.op]" if (char.employer != hero): # direct killing of hired free chars is unavailable, only in dungeon on via other special means
            "[char.pC] stopped moving. Serves [char.op] right."
            python hide:
                hero.gfx_mod_exp(exp_reward(hero, char))
                kill_char(char)
                for member in hero.team:
                    if all([member != hero, member.status != "slave", not("Vicious" in member.traits), not("Yandere" in member.traits)]):
                        if "Virtuous" in member.traits:
                            member.gfx_mod_stat("disposition", -randint(200, 300)) # you really don't want to do it with non evil chars in team
                            member.gfx_mod_stat("affection", -randint(30,50))
                        else:
                            member.gfx_mod_stat("disposition", -randint(100, 200))
                            member.gfx_mod_stat("affection", -randint(20,30))
            if dice(m+10):
                "Just as you are standing above the body, a city guard arrives to the scene. He quickly arrests you."
                $ del m
                $ iam.end(safe=True)
                $ pytfall.jail.add_prisoner(hero, "Murder", randint(10,15))
                jump hero_in_jail
                with Fade
        "Quickly leave before someone sees you.":
            $ pass

    if char.employer != hero:
        $ iam.remove_girl(char)
    $ char.set_flag("cnd_interactions_blowoff", day+5)
    $ del m
    jump girl_interactions_end

label interactions_escalation: # character was provoked to attack MC
    $ iam.set_img("battle", "confident", "angry", exclude=["happy", "suggestive"], type="first_default", add_mood=False)
    $ iam.provoked(char)
    hide screen girl_interactions

    python:
        enemy_team = Team(name="Enemy Team")
        enemy_team.add(char)
        your_team = Team(name="Your Team")
        your_team.add(hero)
        result = iam.select_background_for_fight(iam.label_cache)
        result = run_default_be(enemy_team, your_team=your_team, background=result,
                                end_background=iam.bg_cache, give_up="surrender")

    if result is True:
        python hide:
            char.set_stat("health", 1)
            char.gfx_mod_stat("disposition", -randint(100, 200)) # that's the beaten character, big penalty to disposition
            char.gfx_mod_stat("affection", -randint(20,30))
            for member in hero.team:
                if all([member != hero, member.status != "slave", not("Vicious" in member.traits), not("Yandere" in member.traits)]): # they don't like when MC harasses and then beats other chars, unless they are evil
                    if "Virtuous" in member.traits:
                        member.gfx_mod_stat("disposition", -randint(20, 40)) # double for kind characters
                        member.gfx_mod_stat("affection", -randint(3,5))
                    else:
                        member.gfx_mod_stat("disposition", -randint(10, 20))
                        member.gfx_mod_stat("affection", -randint(1,3))
        $ del result, enemy_team
        $ iam.fight_lost(char)
        jump interactions_harrasment_after_battle
    else:
        $ char.gfx_mod_exp(exp_reward(char, hero))
        show screen girl_interactions
        $ iam.restore_img()
        $ del result, enemy_team
        $ iam.fight_won(char)
        $ char.set_flag("cnd_interactions_blowoff", day+1)
        jump girl_interactions_end

label interactions_stupid:
    $ mode = "intelligence"
    jump interactions_insult
label interactions_weak:
    $ mode = "attack"
    jump interactions_insult
label interactions_ugly:
    $ mode = "charisma"
    jump interactions_insult
label interactions_insult: # (mode)
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_insult")
    if m > 3:
        $ del m, mode
        $ iam.refuse_too_many(char)
        $ char.gfx_mod_stat("disposition", -randint(1, 5))
        $ char.gfx_mod_stat("affection", -randint(1,2))
        if char.get_stat("joy") > 50:
            $ char.gfx_mod_stat("joy", -randint(0, 1))
        jump girl_interactions_end

    $ sub = check_submissivity(char)

    $ char_vals = char.get_stat("character") + char.get_stat(mode)
    if sub == 1:
        $ char_vals *= 1.2
    elif sub == -1:
        $ char_vals *= .8
    $ hero_vals = hero.get_stat("character") + hero.get_stat(mode)

    $ mpl = max(min(hero_vals / float(char_vals+1), 2.0), .5)
    $ del char_vals, hero_vals, mode

    if "Sadist" in hero.traits:
        $ hero.gfx_mod_stat("joy", randint(0, 2))

    if dice(50-25*sub):
        $ char.gfx_mod_stat("character", -randint(0,1))
    $ char.gfx_mod_stat("joy", -randint(2, 4))
    if char.get_stat("disposition") >= 700 or (char.get_stat("disposition") >= 250 and char.status != "slave") or check_lovers(char):
        $ char.gfx_mod_stat("disposition", -round_int(mpl*randint(1, 5)))
        $ char.gfx_mod_stat("affection", -round_int(mpl*randint(0,1)))
        $ iam.got_insulted_hdisp(char)
    elif char.get_stat("disposition") > -100 and char.status=="slave":
        $ char.gfx_mod_stat("disposition", -round_int(mpl*randint(1, 5)))
        $ char.gfx_mod_stat("affection", -round_int(mpl*randint(0,1)))
        $ iam.got_insulted_slave(char)
    else:
        $ char.gfx_mod_stat("disposition", -round_int(mpl*randint(15,25)))
        $ char.gfx_mod_stat("affection", -round_int(mpl*randint(1,2)))
        if m > 1 and iam.silent_check_for_escalation(char, 30):
            $ del m, mpl, sub
            jump interactions_escalation

        $ iam.got_insulted(char)

        if dice(50):
            $ char.set_flag("cnd_interactions_blowoff", day+2+sub)
            $ del m, mpl, sub
            jump girl_interactions_end
    $ del m, mpl, sub
    jump girl_interactions
