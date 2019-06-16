label interactions_giftmoney:
    if not char.has_flag("cnd_flag_interactions_giftmoney"):
        $ char.set_flag("cnd_flag_interactions_giftmoney", value=day+3)
    else:
        "You already did this recently, [char.p] does not want to abuse your generosity."
        jump girl_interactions

    $ line = "You have " + str(hero.gold) + " gold. How much money do you want to give?"
    
    $ money = renpy.call_screen("digital_keyboard", line=line)

    if money <= 0 or not money:
        "You changed your mind."
        $ del money
        jump girl_interactions

    if money > hero.gold:
        "You don't have that amount of gold."
        $ del money
        jump girl_interactions

    if char.gold >= locked_random("randint", 500, 1000):
        if round(char.gold/money) > 5:
            $ del money
            $ char.gfx_mod_stat("disposition", -randint(9, 25))
            $ char.gfx_mod_stat("affection", -randint(1,4))
            $ iam.refuse_money(char)
            jump girl_interactions

    if hero.take_money(money, reason="Charity"):
        $ char.add_money(money, reason="Charity")
        "You gave [char.op] [money] Gold."
        if round(char.gold/money) <= 1:
            "She enthusiastically accepts your money. It looks like it's a considerable sum for her."
            $ a = 20
            $ b = 50
            $ mod = 1.5
        elif round(char.gold/money) <= 3:
            "She gratefully accepts your money. Times are tough."
            $ a = 10
            $ b = 25
            $ mod = 1.25
        else:
            "She takes your money."
            $ a = 5
            $ b = 15
            $ mod = 1
        $ iam.int_reward_exp(char, .25*mod)
        $ mod = randint(a, b)
        if char.get_stat("disposition") >= 90:
            $ mod = round(mod/(char.get_stat("disposition")*.01))
        $ char.gfx_mod_stat("disposition", mod)
        $ char.gfx_mod_stat("affection", affection_reward(char, mod*.05, stat="gold"))
        $ del a, b, mod, money
        $ iam.interactions_accept_money(char)
    else:
        "You don't have that amount of gold."
        $ del money
    jump girl_interactions

label interactions_askmoney:
    if not char.has_flag("cnd_flag_interactions_askmoney"):
        $ char.set_flag("cnd_flag_interactions_askmoney", value=day+7)
    else:
        $ char.gfx_mod_stat("disposition", -randint(2, 5))
        $ char.gfx_mod_stat("affection", -randint(0,2))
        $ iam.refuse_recently_gave_money(char)
        jump girl_interactions
    "You asked for [char.pd] help with money."
    if char.get_stat("disposition") >= 400 or char.get_stat("affection") >= 400 or check_lovers(char) or check_friends(char):
        if char.gold < locked_random("randint", 500, 1000):
            $ iam.refuse_not_enough_money(char)
            jump girl_interactions
        elif char.gold > hero.gold*2:
            # make sure the char does not give all their money away, and also does not give too much
            $ temp = randint(min(char.gold/100, 500), min(char.gold/10, 1000))
            if char.take_money(temp, reason="Charity"):
                $ hero.add_money(temp, reason="Charity")
                "She gave you [temp] Gold."
                $ iam.int_reward_exp(char)
                $ char.gfx_mod_stat("disposition", -randint(20, 40))
                $ char.gfx_mod_stat("affection", -randint(8,12))
            $ del temp
        else:
            "But it looks like [char.p] needs the money more than you."
            $ char.gfx_mod_stat("disposition", -randint(10, 20))
            $ char.gfx_mod_stat("affection", -randint(4,6))
            $ iam.refuse_not_enough_money(char)
            jump girl_interactions
    else:
        "But [char.p] doesn't know you well enough yet."
        $ iam.disp_is_too_low_to_give_money(char)
        $ char.gfx_mod_stat("disposition", -randint(5, 15))
        $ char.gfx_mod_stat("affection", -randint(1,3))
    jump girl_interactions

label interactions_give_money:
    $ line = "You have " + str(hero.gold) + " gold. How much money do you want to give?"
    $ money = renpy.call_screen("digital_keyboard", line=line)

    if money <= 0 or not money:
        "You changed your mind."
    elif hero.take_money(money, reason="Exchange"):
        $ char.add_money(money, reason="Exchange")
        "You gave [char.op] [money] Gold."
    else:
        "You don't have that amount of gold."
    $ del money
    jump girl_interactions

label interactions_take_money:
    $ line = "She has " + str(char.gold) + " gold. How much money do you want to take?"
    $ money = renpy.call_screen("digital_keyboard", line=line)
    if not money:
        "You changed your mind."
    elif char.take_money(money, reason="Exchange"):
        $ hero.add_money(money, reason="Exchange")
        "You took [money] Gold."
    else:
        "She doesn't have that amount of gold."
    $ del money
    jump girl_interactions
