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
            call interactions_not_enough_gold from _call_interactions_not_enough_gold
            $ char.gfx_mod_stat("disposition", -randint(9, 25))
            $ char.gfx_mod_stat("affection", -randint(1,4))
            $ del money
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
        call interactions_enough_gold from _call_interactions_enough_gold
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25*mod))
        $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.25*mod))
        $ mod = randint(a, b)
        if char.get_stat("disposition") >= 90:
            $ mod = round(mod/(char.get_stat("disposition")*.01))
        $ char.gfx_mod_stat("disposition", mod)
        $ char.gfx_mod_stat("affection", affection_reward(char, mod*.05, stat="gold"))
        $ del a, b, mod, money
    else:
        "You don't have that amount of gold."
        $ del money
    jump girl_interactions

label interactions_askmoney:
    if not char.has_flag("cnd_flag_interactions_askmoney"):
        $ char.set_flag("cnd_flag_interactions_askmoney", value=day+7)
    else:
        call interactions_recently_gave_money from _call_interactions_recently_gave_money
        $ char.gfx_mod_stat("disposition", -randint(2, 5))
        $ char.gfx_mod_stat("affection", -randint(0,2))
        jump girl_interactions
    "You asked for [char.pp] help with money."
    if char.get_stat("disposition") >= 400 or char.get_stat("affection") >= 400 or check_lovers(char, hero) or check_friends(char, hero):
        if char.gold < locked_random("randint", 500, 1000):
            call interactions_girl_is_too_poor_to_give_money from _call_interactions_girl_is_too_poor_to_give_money
            jump girl_interactions
        elif char.gold > hero.gold*2:
            # make sure the char does not give all their money away, and also does not give too much
            $ temp = randint(min(char.gold/100, 500), min(char.gold/10, 1000))
            if char.take_money(temp, reason="Charity"):
                $ hero.add_money(temp, reason="Charity")
                "She gave you [temp] Gold."
                $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
                $ char.gfx_mod_stat("disposition", -randint(20, 40))
                $ char.gfx_mod_stat("affection", -randint(8,12))
                $ del temp
        else:
            "But it looks like [char.p] needs the money more than you."
            call interactions_girl_is_too_poor_to_give_money from _call_interactions_girl_is_too_poor_to_give_money_1
            $ char.gfx_mod_stat("disposition", -randint(10, 20))
            $ char.gfx_mod_stat("affection", -randint(4,6))
            jump girl_interactions
    else:
        "But [char.p] doesn't know you well enough yet."
        $ interactions_girl_disp_is_too_low_to_give_money(char)
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

label interactions_not_enough_gold:
    $ char.override_portrait("portrait", "indifferent")
    $ char.show_portrait_overlay("puzzled", "reset")
    if ct("Impersonal"):
        $ rc("I don't need it.", "What do you expect me to do with this money?")
    elif ct("Shy") and dice(50):
        $ rc("It's... for me? ...Um, thanks, but I cannot accept it.", "Oh... th-thank you, but I d-don't need it.")
    elif ct("Tsundere"):
        $ rc( "Huh? You think I'm that poor?!", "Hmph! I don't need your money! Idiot...")
    elif ct("Kuudere"):
        $ rc("Too bad, I'm not that cheap.", "I can perfectly live without your money, thanks you very much.")
    elif ct("Yandere"):
        $ rc("Money? I don't need them.", "I'm not interested.")
    elif ct("Dandere"):
        $ rc("I don't want it.", "No thanks.")
    elif ct("Ane"):
        $ rc("Not to be ungrateful, but... I really don't need money.", "I appreciate it, but I'm capable to live on my own.")
    elif ct("Imouto"):
        $ rc("Oh, a present! ...Money? Boring!", "Hey, I don't want your money!")
    elif ct("Kamidere"):
        $ rc("Is it the best you can do? Hehe, seems like you need money more than me ♪", "Is that all? Really? Pathetic.")
    elif ct("Bokukko"):
        $ rc("Wha? Money? Huhu, don't need them ♪", "Hey, is this a joke?")
    else:
       $ rc("Thanks, but no thanks.", "Um, I think you should keep these money for yourself.")
    $ char.restore_portrait()
    $ char.hide_portrait_overlay()
    return

label interactions_enough_gold:
    $ char.override_portrait("portrait", "happy")
    $ char.show_portrait_overlay("note", "reset")
    if ct("Impersonal"):
        $ rc("Thanks for your donation.", "I accept it. You have my thanks.")
    elif ct("Shy") and dice(50):
        $ rc("Oh... th-thank you.", "<Blush> Is it ok if I take this?...")
    elif ct("Tsundere"):
        $ rc("I guess I could use some... A-alright then.", "Your money? Are you sure..? Fine then, thanks.")
    elif ct("Kuudere"):
        $ rc("Well... since you offered... I could use some.", "...Thank you. I promise to spend them wisely.")
    elif ct("Yandere"):
        $ rc("You want to give me money?.. Fine, I don't mind.", "Alright, but I'll give you something in return one day, ok?")
    elif ct("Dandere"):
        $ rc("Is it really ok? Thanks then.", "Thanks.")
    elif ct("Ane"):
        $ rc("Thank you. You have my regards.", "Oh my, I'm grateful. I'll be sure to put your money to good use.")
    elif ct("Imouto"):
        $ rc("Oh! Money! ♪ <giggles>", "Hehehe, if you keep doing this I'll be spoiled.")
    elif ct("Kamidere"):
        $ rc("I'm accepting your generous offer.", "Very well. You have my gratitude.")
    elif ct("Bokukko"):
        $ rc("Oh? This is pretty cool! Thanks.", "Hey, thanks. It's shoppin' time ♪")
    else:
        $ rc("Thank you! I greatly appreciate it.", "Um, thank you. Can't say 'no' to free money, I guess ♪")
    $ char.restore_portrait()
    $ char.hide_portrait_overlay()
    return

label interactions_recently_gave_money:
    $ char.override_portrait("portrait", "indifferent")
    $ char.show_portrait_overlay("sweat", "reset")
    if ct("Impersonal"):
        $ rc("Denied. Your requests are too frequent.")
    elif ct("Shy") and dice(50):
        $ rc("I-I'd really like to... But... Um... Sorry.")
    elif ct("Tsundere"):
        $ rc("What, again?! What happened to the money I gave you the last time?")
    elif ct("Kuudere"):
        $ rc("Show some restraint. You cannot depend on others all the time.")
    elif ct("Yandere"):
        $ rc("You want my money again? I don't feel like it, sorry. Maybe next time.")
    elif ct("Dandere"):
        $ rc("No. You ask too much.")
    elif ct("Ane"):
        $ rc("You need to learn how to live on your own. Let's discuss it again after a while, alright?")
    elif ct("Imouto"):
        $ rc("Whaat? Again? All you think about is money!!")
    elif ct("Kamidere"):
        $ rc("I don't think so. Get a job, will you?")
    elif ct("Bokukko"):
        $ rc("No way! If you goin' to ask for money so often, I will become poor too.")
    else:
        $ rc("I cannot help you again, sorry. Maybe another time.")
    $ char.hide_portrait_overlay()
    $ char.restore_portrait()
    return

label interactions_girl_is_too_poor_to_give_money:
    $ char.override_portrait("portrait", "indifferent")
    if ct("Impersonal"):
        $ rc("Denied. Not enough funds.")
    elif ct("Shy") and dice(50):
        $ rc("Err... S-sorry, I don't have much money at the moment...")
    elif ct("Tsundere"):
        $ rc("*sigh* I'm not made of money, you know.")
    elif ct("Kuudere"):
        $ rc("I'm afraid you overestimate me. I'm not that rich *sadly smiles*")
    elif ct("Yandere"):
        $ rc("*sigh* I barely make ends meet, so... no.")
    elif ct("Dandere"):
        $ rc("No. I need money too.")
    elif ct("Ane"):
        $ rc("Unfortunately, I can't afford it.")
    elif ct("Imouto"):
        $ rc("Ugh... I don't have much money. Sorry ♪")
    elif ct("Kamidere"):
        $ rc("I refuse. Since I'm low on gold, my own needs take priority.")
    elif ct("Bokukko"):
        $ rc("Not gonna happen. I'm running out of money.")
    else:
        $ rc("I cannot help you, sorry. Maybe another time.")
    $ char.restore_portrait()
    return
