label interactions_clever:
    if iam.flag_count_checker(char, "flag_interactions_praise") != 0:
        "You already complimented [char.op] recently, so [char.p]'s not impressed."
        $ iam.refuse_praise(char)
        jump girl_interactions

    "You are trying to compliment [char.pd] intelligence."
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    $ inter_praise = 0
    $ stats = ["charisma", "intelligence", "character", "constitution"]
    $ mean = sum(char.get_stat(i) for i in stats)/len(stats) # we check the difference between the stat and average stats value
    $ char_int = char.get_stat("intelligence")
    if mean >= char_int:
        $ inter_praise += 1

    if hero.get_stat("intelligence") > char_int:
        $ inter_praise += 1

    # we check if the stat is a min stat
    if all(char.get_stat(s) >= char_int for s in stats):
        $ inter_praise += 1

    $ del stats, mean, char_int
    if inter_praise == 3:
        "[char.pC] looks excited."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
    elif inter_praise == 2:
        "[char.pC] looks happy."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.2))
    elif inter_praise == 1:
        "[char.pC] looks a bit happier than before."
    else:
        "[char.pC]'s not impressed at all."
        $ iam.refuse_praise(char)
        $ del inter_praise
        jump girl_interactions

    $ char.gfx_mod_stat("disposition", randint(10, 15)*inter_praise)
    $ char.gfx_mod_stat("affection", affection_reward(char))
    $ char.gfx_mod_stat("joy", randint(4, 6)*inter_praise)

    $ iam.accept_praise(char)
    $ del inter_praise
    jump girl_interactions

label interactions_strong:
    if iam.flag_count_checker(char, "flag_interactions_praise") != 0:
        "You already complimented [char.op] recently, so [char.p]'s not impressed."
        $ iam.refuse_praise(char)
        jump girl_interactions
        
    "You are trying to compliment [char.pd] physique."
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    $ inter_praise = 0
    $ stats = ["charisma", "intelligence", "character", "constitution"]
    $ mean = sum(char.get_stat(i) for i in stats)/len(stats) # we check the difference between the stat and average stats value
    $ char_const = char.get_stat("constitution")
    if mean >= char_const:
        $ inter_praise += 1

    if hero.get_stat("constitution") > char_const:
        $ inter_praise += 1

    # we check if the stat is a min stat
    if all(char.get_stat(s) >= char_const for s in stats):
        $ inter_praise += 1

    $ del stats, mean, char_const
    if inter_praise == 3:
        "[char.pC] looks pleased.."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
    elif inter_praise == 2:
        "[char.pC] looks happy."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.2))
    elif inter_praise == 1:
        "[char.pC] looks a bit happier than before."
    else:
        "[char.pC]'s not impressed at all."
        $ iam.refuse_praise(char)
        $ del inter_praise
        jump girl_interactions

    $ char.gfx_mod_stat("disposition", randint(10, 15)*inter_praise)
    $ char.gfx_mod_stat("affection", affection_reward(char))
    $ char.gfx_mod_stat("joy", randint(4, 6)*inter_praise)

    $ iam.accept_praise(char)
    $ del inter_praise
    jump girl_interactions

label interactions_cute:
    if iam.flag_count_checker(char, "flag_interactions_praise") != 0:
        "You already complimented [char.op] recently, so [char.p]'s not impressed."
        $ iam.refuse_praise(char)
        jump girl_interactions
        
    "You are trying to compliment [char.pd] appearance."
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    $ inter_praise = 0
    $ stats = ["charisma", "intelligence", "character", "constitution"]
    $ mean = sum(char.get_stat(i) for i in stats)/len(stats) # we check the difference between the stat and average stats value
    $ char_charisma = char.get_stat("charisma")
    if mean >= char_charisma:
        $ inter_praise += 1

    if hero.get_stat("charisma") > char_charisma:
        $ inter_praise += 1

    # we check if the stat is a min stat
    if all(char.get_stat(s) >= char_charisma for s in stats):
        $ inter_praise += 1

    $ del stats, mean, char_charisma
    if inter_praise == 3:
        "[char.pC] looks very happy."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
    elif inter_praise == 2:
        "[char.pC] looks happy."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.2))
    elif inter_praise == 1:
        "[char.pC] looks a bit happier than before."
    else:
        "[char.pC]'s not impressed at all."
        $ iam.refuse_praise(char)
        $ del inter_praise
        jump girl_interactions

    $ char.gfx_mod_stat("disposition", randint(10, 15)*inter_praise)
    $ char.gfx_mod_stat("affection", affection_reward(char))
    $ char.gfx_mod_stat("joy", randint(4, 6)*inter_praise)

    $ iam.accept_praise(char)
    $ del inter_praise
    jump girl_interactions
