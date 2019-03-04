label interactions_clever:
    if interactions_flag_count_checker(char, "flag_interactions_praise") != 0:
        "You already complimented [char.op] recently, so [char.p]'s not impressed."
        call praise_nope from _call_praise_nope_1
        jump girl_interactions

    "You are trying to compliment [char.pp] intelligence."
    $ interactions_check_for_bad_stuff(char)
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

    $ del stats
    $ del mean
    $ del char_int
    if inter_praise == 3:
        "[char.pC] looks excited."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.33))
    elif inter_praise == 2:
        "[char.pC] looks happy."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.33*.8))
    elif inter_praise == 1:
        "[char.pC] looks a bit happier than before."
    else:
        "[char.pC]'s not impressed at all."
        call praise_nope from _call_praise_nope
        jump girl_interactions

    $ char.gfx_mod_stat("disposition", randint(10, 15)*inter_praise)
    $ char.gfx_mod_stat("affection", affection_reward(char))
    $ char.gfx_mod_stat("joy", randint(15, 20))

    call praise_yes from _call_praise_yes
    $ del inter_praise
    jump girl_interactions

label interactions_strong:
    if interactions_flag_count_checker(char, "flag_interactions_praise") != 0:
        "You already complimented [char.op] recently, so [char.p]'s not impressed."
        call praise_nope from _call_praise_nope_3
        jump girl_interactions
        
    "You are trying to compliment [char.pp] physique."
    $ interactions_check_for_bad_stuff(char)
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

    $ del stats
    $ del mean
    $ del char_const
    if inter_praise == 3:
        "[char.pC] looks pleased.."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.33))
    elif inter_praise == 2:
        "[char.pC] looks happy."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.33*.8))
    elif inter_praise == 1:
        "[char.pC] looks a bit happier than before."
    else:
        "[char.pC]'s not impressed at all."
        call praise_nope from _call_praise_nope_2
        jump girl_interactions

    $ char.gfx_mod_stat("disposition", randint(10, 15)*inter_praise)
    $ char.gfx_mod_stat("affection", affection_reward(char))
    $ char.gfx_mod_stat("joy", randint(15, 20))

    call praise_yes from _call_praise_yes_1
    $ del inter_praise
    jump girl_interactions

label interactions_cute:
    if interactions_flag_count_checker(char, "flag_interactions_praise") != 0:
        "You already complimented [char.op] recently, so [char.p]'s not impressed."
        call praise_nope from _call_praise_nope_5
        jump girl_interactions
        
    "You are trying to compliment [char.pp] appearance."
    $ interactions_check_for_bad_stuff(char)
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

    $ del stats
    $ del mean
    $ del char_charisma
    if inter_praise == 3:
        "[char.pC] looks very happy."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.33))
    elif inter_praise == 2:
        "[char.pC] looks happy."
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.33*.8))
    elif inter_praise == 1:
        "[char.pC] looks a bit happier than before."
    else:
        "[char.pC]'s not impressed at all."
        call praise_nope from _call_praise_nope_4
        jump girl_interactions

    $ char.gfx_mod_stat("disposition", randint(10, 15)*inter_praise)
    $ char.gfx_mod_stat("affection", affection_reward(char))
    $ char.gfx_mod_stat("joy", randint(15, 20))

    call praise_yes from _call_praise_yes_2
    $ del inter_praise
    jump girl_interactions

label praise_nope:
    $ char.override_portrait("portrait", "indifferent")
    if ct("Impersonal"):
        $ rc("Does that usually work?", "Bigmouth.", "...What do you want?", "...You talk too much.", "<[char.pC] completely ignores you>", "...and?")
    elif ct("Shy") and dice(50):
        $ rc("U-um, you were talking to me? Oh ... <[char.p]'s embarrassed>", "Pl-please ... stop...", "Don't ... make fun of me.", "Well ... that ... <[char.p] looks like [char.p] wants to run away>", "Ah, I-I'm not... S-sorry...", "Really? I don't think... I-I'm sorry.", "<looks uncomfortable> No, I... umn... sorry.")
    elif ct("Imouto"):
        $ rc("Huhu, you're far too obvious.", "Eh? You sound like a perv!", "Booring!", "Huhn, who would fall for a line like that?")
    elif ct("Kuudere"):
        $ rc("Stop that. Empty praises won't do you any good.", "You can stop talking now.", "Can't find something better to say?", "All talk and nothing to back it up. What are you even trying to do?", "*sigh*...  I don't really have time for this.")
    elif ct("Dandere"):
        $ rc("Can we end this conversation here?", "That's...not true.", "Not funny.", "*sigh*... thank you...<looks bored>", "Please, drop this flattery.")
    elif ct("Tsundere"):
        $ rc("I won't be fooled by beautiful words.", "I find that extremely hard to believe.", "What? I have no idea what you're talking about.", "Lay off the jokes; there's already one attached to the front of your head!")
    elif ct("Kamidere"):
        $ rc("Don't try to pull the wool over my eyes. I know what you're after.", "Don't you have something better to do?", "What do you want, anyway?", "Are you making fun of me?", "What a supremely boring joke. You've got awful taste.")
    elif ct("Ane"):
        $ rc("Whatever are you saying?", "That is simply not true.", "Can we talk about something else?", "<looks unimpressed> Thank you...", "Thanks, but please leave me alone, I'm not interested", "I'm sorry, but I don't have time for this.", "I don't think you are being sincere.")
    elif ct("Bokukko"):
        $ rc("Eeh, I wouldn't say that...", "That can't be right, hey?", "Eh? But that's wrong, right?", "But that's not true at all?", "Eh? What are you talking about?")
    elif ct("Yandere"):
        $ rc("Don't mock me.", "I don't understand, what?", "That's not true.", "Don't try too hard, you'll hurt yourself.", "That's definitely not true, so relax, okay?", "Please, don't bother me.")
    else:
        $ rc("Sorry, not interested.", "How many girls have you said that to today?", "...I'm sorry, did you say something?", "That doesn't sound sincere at all.", "You don't have to say things you don't mean.", "Too bad. I'm not going to fall for that.", "What is it? I don't get what you mean.", "Well... guess so. <unimpressed>", "You don't sound as if you mean it.")
    $ char.restore_portrait()
    return

label praise_yes:
    $ char.override_portrait("portrait", "happy")
    if ct("Impersonal"):
        $ rc("There's no need to state the obvious.", "I... see. *[char.p] looks happier than before*", "I thank you.")
    elif ct("Shy") and dice(30):
        $ rc("Th-thanks...", "You think so? <blush>", "<[char.pC] quickly looks away, [char.op] face red>", "You're ... nice...", "I've never... really been praised much.", "Y-yes... thank you very much... ", "Th... thanks... ", "Ah... ah... really...? I'm so happy...  ", "T-thank you...")
    elif ct("Imouto"):
        $ rc("Haha, thank you ♪", "Huhu ♪ Are you interested in me?", "Fuaaah... Aww, praise me more...", "Really? I'm so happy!", "Ehehe...you praised me ♪")
    elif ct("Kuudere"):
        $ rc("Thanks, but it's nothing to boast of.", "Heh, good one.", "Of course.", "Um, there's tons of people better than me...", "Is that how you see me...", "Hm? Oh, thanks.")
    elif ct("Dandere"):
        $ rc("..You're too kind.", "It's very nice of you to say so.", "Thank you... very much.", "Hearing that makes me happy, even if it's just flattery.")
    elif ct("Tsundere"):
        $ rc("Such flattery won't work on me! <it totally looks like it's working>", "I, I knew that, of course...", "Huh, you finally figured that out?", "It's not like I'm happy or anything. But for now I'll accept your praise.")
    elif ct("Ane"):
        $ rc("Well, I do like being praised.", "Well, that was certainly witty.", "O-Oh stop, you're embarrassing me ♪", "Thank you, I'm very pleased.", "My, I am happy to hear that.")
    elif ct("Kamidere"):
        $ rc("Thanks, but it's nothing worth mentioning.", "Be a little serious please. ...eh... you are?", "What was that? Are you planning to ask me out?", "You can say that all you want, I'm not going to give you anything ♪")
    elif ct("Bokukko"):
        $ rc("Hey, I really might be cool <giggles>", "Well, I am cool! Hmph!", "Hehe, did you fall for me?", "Eh? You're interested in me? That's some good taste, really good!", "Hm-hmm! That's right, respect me lots!", "Well, that's just the way it goes, y'know?", "Thanksies ♪")
    elif ct("Yandere"):
        $ rc("Thank you, I'm glad to hear that.", "I sure hope you don't go saying that to every other girl too.", "You are sweet.", "D-don't say that... I'm starting to blush.")
    else:
        $ rc("Hehe, thanks.", "Thanks for the compliment.", "<Smiles> Yes, go on ...", "Alright, you've got my attention <blush>", "Aww, so sweet ♪", "You don't have to say that. <[char.p]'s blushing and smiling>", "Gosh, flattery won't get you anything from me, you know?", "Ehehe, thank you very much ♪", "Oh, you're exaggerating.", "Thank you, I'm very pleased.")
    $ char.restore_portrait()
    return
######
    #if gm_last_success:
    #    if ct("Yandere"):
    #        $ rc("Nfufu, boo-bies♪ boo-bies♪ -bies ♪", "Interested, aren't you? <smiles mischievously>")
    #    elif ct("Shy") and dice(30):
    #        $ rc("U-Um... Please don't stare at me so much...", "Even though this is embarrassing... I'm glad...", "Don't look at me like that... I-I'm not embarrassed!")
    #    elif ct("Kamidere"):
    #        $ rc("Do you seriously think so?", "Thanks, but next time keep talk like that for private, ok? ", "So you are that type of person...", "Thanks, I grew them myself.", "Thanks. {p=.5}Hey, enough. How long will you stare for?!")
    #    elif ct("Ane"):
    #        $ rc("My, don't stare so hard, okay...?", "If you're gonna look, pay me the viewer's fee!♪", "Thanks, but please don't stare like that, it's embarrassing.", "Do you like my breasts? Glad to hear it...")
    #    elif ct("Imouto"):
    #        $ rc("Huhu ♪ Lookie, these are my awesome boobs ♪", "Geez, don't loooook ♪")
    #    elif ct("Kuudere"):
    #        $ rc("G-go ahead, if you're going to look then look!", "D-don't look... You can't!")
    #    elif ct("Tsundere"):
    #        $ rc("Wh-who said you could look?", "Uuu... Stop staring at me like that...")
    #    elif ct("Dandere"):
    #        $ rc("Hmmm... Interested?", "You like my body? ...good.")
    #    elif ct("Bokukko"):
    #        $ rc("Hah hah hah! Go ahead, envy my boobs! Worship them!", "Hmm, already captivated by my exquisite breasts, huh!")
    #    else:
    #        $ rc("It’s alright to look, but touching is not allowed, oo... fufufu.", "[hero.name], just where are you looking at? It’s alright, look at much as you like.", "Like the view? <pushes her chest up in a pose>", "Do you like my breasts? Glad to hear it...", "You're so perverted. <giggles>", "My body gets you excited, doesn't it?", "Thanks... Hey! Is that why you are interested in me?", "You think so? I'm glad...", "Really? I'm glad to hear that.")
#
    #else:
    #    if ct("Shy") and dice(30):
    #        $ rc("Ummm... Please don't look....", "D...don't... say that!", "D-don't say such strange things...", "Uu... Don't say such a thing...", "Uwaa! T-this is, that's... I'm, that's... Ugh...")
    #    elif ct("Impersonal"):
    #        $ rc("I can't really say I'm pleased.", "You are being weird.", "Would you please refrain from commenting on my appearance?")
    #    elif ct("Kamidere"):
    #        $ rc("It's a good idea to not talk like that, got it?", "Wipe that smug expression from your face.", "Cut that perverted talk.", "*sigh* Just be quiet, okay?")
    #    elif ct("Tsundere"):
    #        $ rc("Y-you were thinking about something weird, weren't you?", "What are you talking about, geez...?")
    #    elif ct("Kuudere"):
    #        $ rc("...Perv.", "Shut up. That's disgusting.")
    #    elif ct("Bokukko"):
    #        $ rc("D-don't stare! It's totally embarrassing...", "Wh-why are you looking at me with such perverted eyes...")
    #    elif ct("Ane"):
    #        $ rc("That's no good, you'll dampen the mood like that.")
    #    elif ct("Dandere"):
    #        $ rc("...Pervert.", "Weirdo...", "...annoying.", "...Shut up.", "Not for you.")
    #    else:
    #        $ rc("What are you looking at, you idiot.", "I'll shut that annoying mouth of yours, physically.", "That was really kinky.", "What? Stop staring.", "*sigh*... Okay, that's enough...", "That was a bit over the top for a compliment.", "What are you saying, geez!", "Get lost, pervert!", "Hey, look at my eyes not my chest. OK?", "You're annoying...")
    #
    #jump girl_interactions
