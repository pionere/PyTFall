label interactions_giftmoney:
    if char.has_flag("cnd_flag_interactions_giftmoney"):
        "You already did this recently, [char.p] does not want to abuse your generosity."
        jump girl_interactions

    $ line = "You have " + str(hero.gold) + " gold. How much money do you want to give?"
    $ money = renpy.call_screen("digital_keyboard", line=line)

    if money <= 0 or not money:
        "You changed your mind."
    elif money > hero.gold:
        "You don't have that amount of gold."
    elif char.gold >= randint(500, 1000) and round(char.gold/money) > 5: 
        $ iam.dispo_reward(char, -randint(15, 20))
        $ char.gfx_mod_stat("affection", -randint(1,4))
        $ iam.refuse_money(char)
    else:
        "You gave [char.op] [money] Gold."
        if round(char.gold/money) <= 1:
            "[char.pC] enthusiastically accepts your money. It looks like it's a considerable sum for [char.op]."
            $ a = 30
            $ b = 40
            $ mod = 1.5
        elif round(char.gold/money) <= 3:
            "[char.pC] gratefully accepts your money. Times are tough."
            $ a = 15
            $ b = 20
            $ mod = 1.25
        else:
            "[char.pC] takes your money."
            $ a = 8
            $ b = 12
            $ mod = 1
        $ iam.accept_money(char)
        $ iam.int_reward_exp(char, .25*mod)
        $ mod = randint(a, b)
        $ iam.dispo_reward(char, mod)
        $ char.gfx_mod_stat("affection", affection_reward(char, mod*.05, stat="gold"))
        $ hero.take_money(money, reason="Charity")
        $ char.add_money(money, reason="Charity")
        $ char.set_flag("cnd_flag_interactions_giftmoney", value=day+3)
        $ del a, b, mod

    $ del money, line
    jump girl_interactions

label interactions_askmoney:
    if char.has_flag("cnd_flag_interactions_askmoney"):
        $ iam.dispo_reward(char, -randint(3, 5))
        $ char.gfx_mod_stat("affection", -randint(0,2))
        $ iam.refuse_recently_gave_money(char)
        jump girl_interactions

    "You asked for [char.pd] help with money."
    $ char.set_flag("cnd_flag_interactions_askmoney", value=day+7)
    if char.get_stat("disposition") >= 400 or char.get_stat("affection") >= 400 or check_lovers(char) or check_friends(char):
        if char.gold < locked_random("randint", 500, 1000):
            $ iam.refuse_not_enough_money(char)
            jump girl_interactions
        elif char.gold > hero.gold*2:
            # make sure the char does not give all their money away, and also does not give too much
            $ temp = randint(min(char.gold/100, 500), min(char.gold/10, 1000))
            if char.take_money(temp, reason="Charity"):
                $ hero.add_money(temp, reason="Charity")
                "[char.pC] gave you [temp] Gold."
                $ iam.int_reward_exp(char)
                $ iam.dispo_reward(char, -randint(25, 35))
                $ char.gfx_mod_stat("affection", -randint(8,12))
            $ del temp
        else:
            "But it looks like [char.p] needs the money more than you."
            $ iam.dispo_reward(char, -randint(8, 12))
            $ char.gfx_mod_stat("affection", -randint(4,6))
            $ iam.refuse_not_enough_money(char)
            jump girl_interactions
    else:
        "But [char.p] doesn't know you well enough yet."
        $ iam.refuse_to_give(char)
        $ iam.dispo_reward(char, -randint(8, 12))
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
    $ del money, line
    jump girl_interactions

label interactions_take_money:
    $ line = "[char.pC] has " + str(char.gold) + " gold. How much money do you want to take?"
    $ money = renpy.call_screen("digital_keyboard", line=line)

    if money <= 0 or not money:
        "You changed your mind."
    elif char.take_money(money, reason="Exchange"):
        $ hero.add_money(money, reason="Exchange")
        "You took [money] Gold."
    else:
        "[char.pC] doesn't have that amount of gold."
    $ del money, line
    jump girl_interactions
