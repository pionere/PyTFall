label girl_interactions_greeting: # because GMs and interactions use different labels for greetings. Should be fixed eventually.
label girl_meets_greeting: # also lines for sad and angry flags are needed. but if they will require interaction rewriting ie 1.3 game version, it's clearly too early for that
    if interactions_checks_for_bad_stuff_greetings(char):
        return
    $ m = interactions_flag_count_checker(char, "flag_interactions_greeting") # probably not the most elegant way to count how many times greeting was shown this day already
    if m < 1:
        call klepto_stealing from _call_klepto_stealing
    if check_lovers(hero, char) and dice(60):
        $ char.override_portrait("portrait", "shy")
        if ct("Half-Sister") and dice(50):
            if ct("Impersonal"):
                $ rc("I love you, even though we're siblings.", "I love you, [hero.hs]. I think.")
            elif ct("Tsundere"):
                $ rc("We're drawn to each other even though we're siblings... it's inevitable that we would fall in love with each other.", "You're the best [hero.hs] ever! Well, if you weren't so perverted you'd be even better... hehe.")
            elif ct("Dandere"):
                $ rc("You are my favourite person.", "Be mine alone, [hero.hs].", "Can't siblings love each other..?")
            elif ct("Kuudere"):
                $ rc("[hero.hs], you belong to only me, got it? I won't let anyone else have you.", "Do you hate it that your sister always takes care of you? If you do... well...")
            elif ct("Imouto"):
                $ rc("Every part of my [hero.hss] belongs to me!", "[hero.hs] and I are bound now. Hehe.", "[hero.hs] is stylish and kind... Hehe....")
            elif ct("Bokukko"):
                $ rc("All I need is you, [hero.hss].", "I won't share my [hero.hs] with anybody!", "Siblings getting along well... Own family is best, na?", "How should I say this... [hero.hs] you're sexy... Hehe!")
            elif ct("Yandere"):
                $ rc("I love you so much, [hero.hs]. You're very special to me.", "If it's for you, [hero.hs]... I'm ready to do anything!", "*She smiles and stares at you.*")
            elif ct("Ane"):
                $ rc("It's natural for siblings to love each other ♥", "Sister will always be here to take care of you.")
            else:
                $ rc("I love everything about you... [hero.hs].", "Please look at your sister... as a woman.", "We're bound together now, even though we're siblings...", "Is it weird for siblings to stick together all the time?")
        elif ct("Shy") and dice(50):
            $ rc("I lik-... I love you...!", "U-Um, er, I, um... I-I... I-I love you!", "Um, ah, er... I...l-li... I li-...! I can't do it!", "Um.... I-I love you very much...", "The two of us are going out... Ahhh...")
        elif ct("Nymphomaniac") and dice(65):
            $ rc("I'm so lewd, aren't I... I'm thinking of you...doing me...", "Hey, what sorts of things do you think we can do, just the two of us?", "You can have me whenever you want!", "We're lovers, so we should act like lovers, we should get gooey and slap thighs.", "Huhu, I love you ♪ Of course, also in a sexual way.", "Even if we are lovers, I wonder what we should do? Ah, you had dirty thoughts just now, didn't you?", "Um... You don't hate naughty girls... right...?")
        elif ct("Impersonal"):
            $ rc("I want to know everything about you. And I want you to know everything about me.", "I'm glad I could meet you.", "As long as we remain lovers, I believe it is essential to have a sensual relationship.", "I'll protect you. You can rely on me.")
        elif ct("Extremely Jealous") and dice(45):
            $ rc("I hate it when you just keep ogling other girls.", "I don't want you flirting with other women.", "I'm sorry, but I dislike it when you get too friendly with other women!", "Hey! Don't look at other girls all the time!", "My heart's feeling uneasy and gloomy... I dislike this feeling.", "Erm... I want you to stop looking at other women so much.")
        elif ct("Kuudere"):
            $ rc("When y-you're around, I can't think straight...", "I c-can help out too if you need me, you know...", "I love you. ...That's it. Got a problem with that?", "P... Please continue to pursue me. My response will always be positive to you.", "You're very dear to me. I want us to stay together...")
        elif ct("Tsundere"):
            $ rc("Wh-what are you planning to have me do...?", "You are NOT to leave my side, okay?", "B-being with you throws me off somehow...", "I deal with your perviness every day, so I deserve some praise!", "Umm... I love you. S-Show a little gratitude for being my choice.", "W-what kind of girls do you like? N-no, pretend I didn't say anything...")
        elif ct("Dandere"):
            $ rc("Sweetheart, sweetheart, sweeeetheart...", "Love you... Mm, it's nothing.", "I want to be with you.", "I want to be your special person...", "I-I'm a lonely person... So don't leave me...", "What can I do to make you look at me...?")
        elif ct("Imouto"):
            $ rc("Hihi, object of my affection. What is up?", "Hehe, we're lovers.... do whatever you like.", "Ehehe, looooove youuuu♪", "I love you♪ I love you sooo much♪", "Have I become like a proper lover now?")
        elif ct("Ane"):
            $ rc("I want to be both your big sister and your wife! ♪", "I love you.  ...No, mere words aren't enough.", "I love you. I don't want to leave your side.", "As I thought, having a caring lover is good ♪", "You'll love me forever, right? ♪", "I'm really happy, you know? To be together like this with you ♪")
        elif ct("Yandere"):
            $ rc("Ah... ehhehe... I'm happy...", "We're lovers, aren't we...? Uhehehe...", "I, I'm your girlfriend, right? ...Ehehe", "I think it's really a good thing I've fallen in love with you.", "Ehehe ♪ Nothing, just looking at your face ♪", "Now how do I get you to fall for me even harder...? Ehehe♪", "It would be nice if we could be together forever.", "We're the most compatible couple in the world, aren't we?")
        elif ct("Kamidere"):
            $ rc("Even though we're lovers, doing nothing but sex stuff is not acceptable!", "Haaa... How'd I fall in love with someone like this...", "Just because we're l-lovers, doesn't mean I will spoil you...", "Well? What does my lover want from me?", "The only thing you'll ever need is me. Oh yes. Just me. Hehe.", "You think it's about time I turned you into my playtoy? ♪")
        elif ct("Bokukko"):
            $ rc("Being subtle is such a bother so let me tell you straight... I love you.", "Even though we're dating now, not all that much has changed, huh...", "Say, what do you like about me? ...it's fine, tell me!", "I love you...I super love you...!")
        else:
            $ rc("I really like you, you know...", "A-As lovers, let's love each other a lot, okay...?", "We shouldn't flirt too much in front of the others, okay?", "I-I love you... Hehehe...♪", "I love you ♪ I love you so much ♪", "I want you to love me more and more! Prepare yourself for it, okay?", "Ehehe, don't you ever, ever leave me...", "I wish we could be together forever...♪", "What do you think other people think when they see us? ...you think maybe, 'Hey, look at that cute couple'...?")
        $ char.restore_portrait()
    elif m < 2:
        $ char_dispo = char.get_stat("disposition")
        if char_dispo <= -200:
            if char.status <> "slave":
                if ct("Yandere"):
                    $ char.override_portrait("portrait", "angry")
                    $ rc("Leave. I don't want to talk to you.",  "What a nuisance...", "Why do you keep bothering me?")
                elif ct("Impersonal"):
                    $ char.override_portrait("portrait", "indifferent")
                    $ rc("State your business and leave.", "I have no interest in you.", "Leave me alone.")
                elif ct("Shy") and dice(50):
                    $ char.override_portrait("portrait", "uncertain")
                    $ rc("P-please, stay away!", "...D-don't come close to me.", "...S-S-Stay away!", "W-w-w-what do you want!?")
                elif ct("Dandere"):
                    $ char.override_portrait("portrait", "indifferent")
                    $ rc("What is it? I want to get back to what I was doing...", "I personally dislike you.", "I believe there is nothing we can talk about.")
                elif ct("Kuudere"):
                    $ char.override_portrait("portrait", "indifferent")
                    $ rc("Hmph, I don't even want to hear it...", "You've got a lot of nerve showing your face around me.", "...I don't think I have reason to talk to you.")
                elif ct("Tsundere"):
                    $ char.override_portrait("portrait", "angry")
                    $ rc("Leave me alone!", "Go away. ...I said get the hell away from me!", "Listening to you is a waste of my time.")
                elif ct("Ane"):
                    $ char.override_portrait("portrait", "indifferent")
                    $ rc("What is it? Please leave me alone.", "I don't really feel like talking to you ", "Could you leave me alone?", "There is not a single shred of merit to your existence.")
                elif ct("Kamidere"):
                    $ char.override_portrait("portrait", "angry")
                    $ rc("It's you again. Don't bother me!", "Could you try to not talk to me, please?  Also, could you not breathe when near me? You're wasting good oxygen.", "Hmph! What an ugly sight.")
                elif ct("Imouto"):
                    $ char.override_portrait("portrait", "angry")
                    $ rc("You dirty little...",  "Jeez! Bug off already!", "You good-for-nothing...")
                elif ct("Bokukko"):
                    $ char.override_portrait("portrait", "angry")
                    $ rc("Why are you bothering me?", "You just won't leave me alone, will you...", "Geez, what's now?")
                else:
                    $ char.override_portrait("portrait", "indifferent")
                    $ rc("...Hey! Could you not get any closer to me, please?", "Sigh... What is it?", "Ah... I-I have stuff to do, so....", "U-Um... right now is a bit, err...")
            else:
                if char_dispo <= -500:
                    $ char.override_portrait("portrait", "sad")
                    char.say "..."
                else:
                    $ char.override_portrait("portrait", "indifferent")
                    if ct("Yandere"):
                        $ rc("Well? If you don't have orders, I have things to do.", "Could you leave me alone, [char.mc_ref]?")
                    elif ct("Impersonal"):
                        $ rc("Orders?..", "..?")
                    elif ct("Shy") and dice(50):
                        $ rc("P-please don't hurt me, [char.mc_ref]...", "W-w-w-what do you want, [char.mc_ref]!?")
                    elif ct("Dandere"):
                        $ rc("I'm listening, [char.mc_ref].", "Yes?.")
                    elif ct("Kuudere"):
                        $ rc("Hmph. Yes?", "...I don't think I have reason to talk to you, [char.mc_ref]. Give me your orders and leave.")
                    elif ct("Tsundere"):
                        $ rc("Well? You want something from me or what?", "*sigh*")
                    elif ct("Ane"):
                        $ rc("What is it? Please leave me alone, [char.mc_ref]...", "I don't really feel like talking to you, [char.mc_ref].")
                    elif ct("Kamidere"):
                        $ rc("You again... <sigh> Yes, [char.mc_ref]?", "[char.mc_ref], could you try to not talk to me without a good reason, please?")
                    elif ct("Imouto"):
                        $ rc("Jeez... I'm listening, [char.mc_ref].", "You again... Ahem, what is it, [char.mc_ref]?")
                    elif ct("Bokukko"):
                        $ rc("Yeah-yeah. I'm here.", "What is it again, [char.mc_ref]?")
                    else:
                        $ rc("*sigh* What is it, [char.mc_ref]?", "...Yes, [char.mc_ref]. I'm here.")

        elif check_friends(hero, char) or (char_dispo >= 500 and char.status <> "slave") or (char_dispo >= 850 and char.status == "slave"):
            $ char.override_portrait("portrait", "happy")
            if ct("Impersonal"):
                $ rc("Talk, I'll listen.", "...Being with you makes me feel extraordinarily comfortable.", "What is your purpose in getting close to me?", "Being with you... calms me.")
            elif ct("Shy") and dice(50):
                $ rc("I-I'm getting a little bit... used to you, [char.mc_ref]...", "Hey, am I... do you... Err... nothing. Never mind.", "Being near you calms me down...", "H-Hi...Is it really ok to talk? I don't want to bother you...", "If I am with you, I...  I-it's nothing...")
            elif ct("Tsundere"):
                $ rc("Come, if you have something to say, say it.", "Don't be so friendly with me, [char.mc_ref]...", "P-please do not act like we are close to each other, [char.mc_ref].")
            elif ct("Dandere"):
                $ rc("Did you need something?", "Maybe... I like your voice.", "It's you. Good to see you, [char.mc_ref]?")
            elif ct("Kuudere"):
                $ rc("You certainly like to be with me, don't you...", "Seriously... why is it so hard to be serious...?", "I'm listening. What is it?", "Is there something you would like to consult with me? It's alright.")
            elif ct("Ane"):
                $ rc("If ever you're in trouble... you can always come to me.", "What's the matter? Need some advice?", "Ah... I was just thinking, it'd be so nice to talk to you... Ehehe.", "If there's anything I can do, please tell me, okay?", "You can call on me anytime. And I'll do the same with you.", "If something's wrong, you can always talk to me.")
            elif ct("Imouto"):
                $ rc("Hn? What's up? You can tell me anything ♪", "For the people I like, I will do my best ♪", "Hi! Tell me, tell me, what'cha doin'?", "Let's have us a chat ♪ Lalala ♪")
            elif ct("Bokukko"):
                $ rc("How's it going? Doing alright?", "Oh, what'cha doing?... What'ya wanna do?", "Ohoh, it's you, [char.mc_ref] ♪", "Yo! What'cha doin'?", "Whazzup?", "Hey [char.mc_ref], let's do something!", "Hey, will you talk with me for a bit?", "C'mon, c'mon, put a smile on!", "Um, so hey, you wanna chat?")
            elif ct("Yandere"):
                $ rc("Eh, what? Do you want to consult with me?", "Huu... You certainly like to be with me, don't you...", "Hm? Something I can do?")
            elif ct("Kamidere"):
                $ rc("Huhu, You seem like you'd be good for some entertainment ♪", "...Do you want to chat with me that badly?", "Ok. I have chosen to give you some of my valuable time today. Don't make me regret that.", "Good timing. Come on, entertain me.", "I have fairly high expectation of you, [char.mc_ref] ♪")
            else:
                $ rc("Hey, how's it going?", "Well, what shall we talk about..?", "What do you want to do?", "Ah, [char.mc_ref]! Let's talk for a while.", "Hi! Another splendid day today!")
                $ char.restore_portrait()
        elif char_dispo and char.status == "slave":
            $ char.override_portrait("portrait", "happy")
            if ct("Impersonal"):
                $ rc("I'm waiting for your orders, [char.mc_ref].", "Yes, [char.mc_ref]. I'm yours to command.", "Another task for me, [char.mc_ref]? I'll do my best.")
            elif ct("Shy") and dice(50):
                $ rc("I-I'm here, [char.mc_ref]. What is your wish?", "If I can do something for you... T-then I w-w-will...", "W-w-what is it, [char.mc_ref]?")
            elif ct("Tsundere"):
                $ rc("Wh-what do you want me to do for you, [char.mc_ref]?", "Well? You want me to do something, don't you? Speak up already.", "I deal with your weird orders every day, [char.mc_ref]. You should be grateful.")
            elif ct("Dandere"):
                $ rc("Did you need something, [char.mc_ref]? I'll do anything.", "May I do something for you, [char.mc_ref]?", "What is your wish, [char.mc_ref]?")
            elif ct("Kuudere"):
                $ rc("Another order, [char.mc_ref]? ", "Of course, [char.mc_ref]. I'm ready to follow your commands.", "[char.mc_ref]? Is there something you want me to do?")
            elif ct("Ane"):
                $ rc("What's the matter? Need something from me, [char.mc_ref]?", "[char.mc_ref], if there's anything I can do, please tell me, okay?", "You can call on me anytime, [char.mc_ref] ♪")
            elif ct("Imouto"):
                $ rc("What's up? You can ask me anything, [char.mc_ref] ♪", "I will do my best for you, [char.mc_ref]!", "Hm? You have a task for me? Tell me, tell me ♪")
            elif ct("Bokukko"):
                $ rc("Oh, [char.mc_ref]. What ya wanna me to do?", "Hey [char.mc_ref], I wanna do something for ya! Any orders?", "Um, you wanna something, [char.mc_ref]?")
            elif ct("Yandere"):
                $ rc("I'm here for you, [char.mc_ref].", "Hm? What would you like me to do, [char.mc_ref]?", "Something I can do, [char.mc_ref]? Ask me anything ♪")
            elif ct("Kamidere"):
                $ rc("Orders for me, [char.mc_ref]? Come on, I'm waiting.", "Your orders are absolute, [char.mc_ref]. Just don't me regret it.", "I suppose I must follow your will, [char.mc_ref]. Have any wishes at the moment?")
            else:
                $ rc("Can I help you with, [char.mc_ref]? Just say the word.", "Yes, [char.mc_ref]? You need my assistance?", "Is there something on your mind, [char.mc_ref]?")
                $ char.restore_portrait()
        else:
            $ char.override_portrait("portrait", "indifferent")
            if char.status <> "slave":
                if ct("Impersonal"):
                    $ rc("State your business.", "You're the kind of person who likes pointless conversations, right?", "...Please do not get any closer.")
                elif ct("Shy") and dice(50):
                    $ rc("Y-yes, did you call?", "...Y-you want something from me?", "Um... W-what is it?", "Y-yes? Wh-what's going on?", "Wha... what is it...?", "U-Umm... What is it...?", "Y-yes, what do you need?", "C-can I help you...?", "Ye...yes?", "What... is wrong...?", "Wh-what is it...?")
                elif ct("Kuudere"):
                    $ rc("Hmph... I wonder if there is any particular purpose to this?", "What business do you have with me?", "Um, was there something you wanted to say?", "Hm? Yes?")
                elif ct("Dandere"):
                    $ rc("If you have business with me, please make it quick.", "You call?", "...?", "...Want something?", "...Hmm?", "...What is it?", "You have business with me...?")
                elif ct("Tsundere"):
                    $ rc("Hmph. I've graced you with my presence, so be thankful.", "So, you want something or what?", "Spit it out already.")
                elif ct("Imouto"):
                    $ rc("Ehehe. What is it? ♪", "Muhuhu ♪ Did you need something?", "Eh? What, what is it?", "Huhu, what is it?", "W-What? Did I do something wrong...?")
                elif ct("Ane"):
                    $ rc("Well, what shall we talk about..?", "Is there something I can help you with...?", "What business do you have with me?", "May I help you?", "...Yes? Did you need me for something?", "Is there... something I can help you with?")
                elif ct("Kamidere"):
                    $ rc("Hm? What? It's not like I have too much time to spend. Yes, that's right. I'm busy.", "...Yes? ...Did you call?", "...Do you want something?", "What is it? I'm busy right now.", "If you have business with me, hurry up and say it.")
                elif ct("Bokukko"):
                    $ rc("Hey-Hey! What do you want?", "Huh? What's up?", "Haa? You got a problem?", "Huh, Is there something you want to know?", "Huh? Do you want something?", "Whazzup?", "Did ya call me?", "Ummm, was there something you wanted to say?")
                elif ct("Yandere"):
                    $ rc("Yes? If you have no business here, then do please vacate from my sight.", "If you've got something to say, look me in the eyes and say it.", "...I don't recall asking to talk to you, so what is it?", "I don't have any business with you. If you do, make it quick.")
                else:
                    $ rc("...Is there something you need?", "Is there something you would like to ask?", "Is something the matter?", "What do you need from me?", "What is it? If you need something, then say it.", "Yes, what is it?", "...Do you need to talk to me?", "Yes? What do you want?", "...? Is there something on my face?", "Do you need something?", "Did you want to say something?", "You have something to tell me?", "Yes, what is it...?")
            else:
                $ char.override_portrait("portrait", "indifferent")
                if ct("Impersonal"):
                    $ rc("Awaiting input.", "Yes, [char.mc_ref]?")
                elif ct("Shy") and dice(30):
                    $ rc("Y-yes, [char.mc_ref]", "Y-you want something from me, [char.mc_ref]?", "Um... Y-yes, [char.mc_ref]?")
                elif ct("Kuudere"):
                    $ rc("I'm here.", "I'm listening, [char.mc_ref].", "Yes? Was there something you wanted?")
                elif ct("Dandere"):
                    $ rc("...[char.mc_ref]?", "You called, [char.mc_ref]?", "...What is it, [char.mc_ref]?")
                elif ct("Tsundere"):
                    $ rc("Hmph. Y-yes, [char.mc_ref].", "Yes, [char.mc_ref]. You want something or what?", "Well, I'm here, [char.mc_ref]. Spit it out already.")
                elif ct("Imouto"):
                    $ rc("What is it, [char.mc_ref]?", "Yes, [char.mc_ref]? Did you need something?", "W-What? Did I do something wrong, [char.mc_ref]?")
                elif ct("Ane"):
                    $ rc("Well, what shall we talk about, [char.mc_ref]?", "May I help you, [char.mc_ref]?", "Yes? Do you need me for something?")
                elif ct("Kamidere"):
                    $ rc("...Yes? Did you call, [char.mc_ref]?", "Do you want something?", "If you have an order for me, say it.")
                elif ct("Bokukko"):
                    $ rc("What do you want, [char.mc_ref]?", "Huh? What's up, [char.mc_ref]?", "Whazzup, [char.mc_ref]?")
                elif ct("Yandere"):
                    $ rc("Is something wrong?", "What is it, [char.mc_ref]?", "...Spit it out already... Er, yes, [char.mc_ref]?")
                else:
                    $ rc("You called, [char.mc_ref]?", "Is something the matter, [char.mc_ref]?", "Yes, what is it, [char.mc_ref]?")
        $ del char_dispo
    elif m < 3:
 # when MC approaches character not the first time; after 4 times we stop showing greetings at all
        if char.get_stat("disposition") <= -50:
            $ char.override_portrait("portrait", "angry")
            char.say "..."
        else:
            $ char.override_portrait("portrait", "indifferent")
            if ct("Impersonal"):
                $ rc("..?", "Awaiting input.", "Hmm?")
            elif ct("Shy") and dice(50):
                $ rc("Y-yes?", "Err... what?", "... *blushes*")
            elif ct("Tsundere"):
                $ rc("Well? What is it this time, [char.mc_ref]?", "You really must have a lot of free time, [char.mc_ref]...")
            elif ct("Dandere"):
                $ rc("You really enjoy talking, don't you?", "I'm here, [char.mc_ref].")
            elif ct("Kuudere"):
                $ rc("Hm? What's the matter?", "I'm listening, [char.mc_ref].")
            elif ct("Ane"):
                $ rc("My, please continue.", "I'm here, [char.mc_ref]. What can I do for you?")
            elif ct("Imouto"):
                $ rc("[char.mc_ref]? What's up?", "Yup, I'm listening, [char.mc_ref].")
            elif ct("Bokukko"):
                $ rc("Whazzup, [char.mc_ref]?", "Yeah?")
            elif ct("Yandere"):
                $ rc("Eh, what?", "Hm? Something I can do, [char.mc_ref]?")
            elif ct("Kamidere"):
                $ rc("Yes? What's wrong, [char.mc_ref]?", "[char.mc_ref]?")
            else:
                $ rc("What is it, [char.mc_ref]?", "Yes?")

    if "Fluffy Companion" in hero.effects and m < 1:
        $ cat = npcs["sad_cat"]
        $ cat.override_portrait("portrait", "happy")
        $ char.override_portrait("portrait", "happy")
        $ char.show_portrait_overlay("note", "reset")
        cat.say "Meow!"
        if ct("Impersonal"):
            $ rc("Oh? I'm sorry, cat, I don't have any treats.")
        elif ct("Shy") and dice(50):
            $ rc("Oh, he's so pretty!")
        elif ct("Tsundere"):
            $ rc("What a cute cat.... What? N-no, I don't want to pet him at all...")
        elif ct("Dandere"):
            $ rc("How cute... May I pet him?.. Thanks. *pets him*")
        elif ct("Kuudere"):
            $ rc("Oh, you have a nice cat there." )
        elif ct("Ane"):
            $ rc("Well hello there, cutey. *pets him*")
        elif ct("Imouto"):
            $ rc("Ohh, a kitty! How cute!")
        elif ct("Bokukko"):
            $ rc("Sup, buddy? Does your master threat you well?")
        elif ct("Yandere"):
            $ rc("You have a cat? Interesting.")
        elif ct("Kamidere"):
            $ rc("Fine, fine, I'll pet you, so be thankful. *pets him*")
        else:
            $ rc("Oh, he's so fluffy and funny, hehe!")
        if char.get_stat("disposition") <= 500:
            $ char.gfx_mod_stat("disposition", locked_random("randint", 5, 10))
        if char.get_stat("affection") <= 500:
            $ char.gfx_mod_stat("affection", affection_reward(char, .5))
        $ cat.restore_portrait()
        $ del cat
    $ del m
    $ char.restore_portrait()
    $ char.hide_portrait_overlay()
    return

label interactions_refuse_because_of_gender:
    $ char.override_portrait("portrait", "indifferent") # obviously will be needed alternative for female MC
    if hero.gender == "male":
        if ct("Impersonal"):
            $ rc("Opposite sex... Dismissed.", "You are a male. Denied.")
        elif ct("Shy"):
            $ rc("Ah, I'm sorry, I can't do that with a boy...", "Um, I-I like girls... Sorry!")
        elif ct("Imouto"):
            $ rc("If you were a girl...it'd be alright, but...", "I don't really like boys... So no.")
        elif ct("Dandere"):
            $ rc("Guys are...not for me.", "Wrong gender. Consider changing it.", "I turn down anyone who's not a girl.")
        elif ct("Kuudere"):
            $ rc("Men for me are...well...", "I'm afraid men are not attractive to me.", "Doing that with a man is... a bit...")
        elif ct("Tsundere"):
            $ rc("Hmph. And that's why I don't like men.", "Ugh, not again... I like girls, understood?", "Huh? You're a guy, so no way!")
        elif ct("Bokukko"):
            $ rc("Ew, don't wanna. You're a guy.", "Nah, I'm not interested in boys. Do you have a sister, by the way?", "Aah, I'm a lesbo, y'know.")
        elif ct("Ane"):
            $ rc("My apologies, I'm a lesbian.", "I'm terribly sorry, but... I can't do that with a man.")
        elif ct("Yandere"):
            $ rc("Sorry, I only like girls.", "I dislike men, nothing personal.", "I... I can't do men.")
        elif ct("Kamidere"):
            $ rc("I have no interest in men.", "Eww. I prefer girls, is it clear?", "Because you're a guy, no.")
        else:
            $ rc("Sorry. I'm weird, so... I'm not into guys.", "Well, I kinda prefer girls... If you know what I mean.", "If you were a girl... it'd be alright, but...")
    else:
        if ct("Impersonal"):
            $ rc("Opposite sex... Dismissed.", "You are a female. Denied.")
        elif ct("Shy"):
            $ rc("Ah, I'm sorry, I can't do that with a girl...", "Um, I-I like boys... Sorry!")
        elif ct("Imouto"):
            $ rc("If you were a boy...it'd be alright, but...", "I don't really like girls... So no.")
        elif ct("Dandere"):
            $ rc("Gals are...not for me.", "Wrong gender. Consider changing it.", "I turn down anyone who's not a boy.")
        elif ct("Kuudere"):
            $ rc("Women for me are...well...", "I'm afraid women are not attractive to me.", "Doing that with a woman is... a bit...")
        elif ct("Tsundere"):
            $ rc("Hmph. And that's why I don't like women.", "Ugh, not again... I like boys, understood?", "Huh? You're a gal, so no way!")
        elif ct("Bokukko"):
            $ rc("Ew, don't wanna. You're a gal.", "Nah, I'm not interested in girls. Do you have a brother, by the way?", "Aah, I'm straight, y'know.")
        elif ct("Ane"):
            $ rc("My apologies, I'm straight.", "I'm terribly sorry, but... I can't do that with a woman.")
        elif ct("Yandere"):
            $ rc("Sorry, I only like boys.", "I dislike women, nothing personal.", "I... I can't do women.")
        elif ct("Kamidere"):
            $ rc("I have no interest in women.", "Eww. I prefer boys, is it clear?", "Because you're a gal, no.")
        else:
            $ rc("Sorry. I'm weird, so... I'm not into gals.", "Well, I kinda prefer boys... If you know what I mean.", "If you were a boy... it'd be alright, but...")

    $ char.restore_portrait()
    return

label interactions_refused_because_tired: # a universal answer for tired characters, when they don't want to do something
    $ char.override_portrait("portrait", "tired")
    if ct("Impersonal"):
        $ rc("I don't have required endurance at the moment. Let's postpone it.", "No. Not enough energy.")
    elif ct("Shy") and dice(50):
        $ rc("W-well, I'm a bit tired right now... Maybe some other time...", "Um, I-I don't think I can do it, I'm exhausted. Sorry...")
    elif ct("Imouto"):
        $ rc("Noooo, I'm tired. I want to sleep.", "Z-z-z *she falls asleep on the feet*")
    elif ct("Dandere"):
        $ rc("No. Too tired.", "Not enough strength. I need to rest.")
    elif ct("Tsundere"):
        $ rc("I must rest at first. Can't you tell?", "I'm too tired, don't you see?! Honestly, some people...")
    elif ct("Kuudere"):
        $ rc("I'm quite exhausted. Maybe some other time.", "I really could use some rest right now, my body is tired.")
    elif ct("Kamidere"):
        $ rc("I'm tired, and have to intentions to do anything but rest.", "I need some rest. Please don't bother me.")
    elif ct("Bokukko"):
        $ rc("Naah, don't wanna. Too tired.", "*yawns* I could use a nap first...")
    elif ct("Ane"):
        $ rc("Unfortunately I'm quite tired at the moment. I'd like to rest a bit.", "Sorry, I'm quite sleepy. Let's do it another time.")
    elif ct("Yandere"):
        $ rc("Ahh, my whole body aches... I'm way too tired.", "The only thing I can do properly now is to take a good nap...")
    else:
        $ rc("*sign* I'm soo tired lately, all I can think about is a cozy warm bed...", "I am ready to drop. Some other time perhaps.")
    $ char.restore_portrait()
    return

label interactions_girl_dissapointed: # a universal answer when character is displeased by something
    $ char.override_portrait("portrait", "indifferent")
    $ char.show_portrait_overlay("sweat", "reset")
    if ct("Impersonal"):
        $ rc("... *you see disappointment in her eyes before she turns away*")
    elif ct("Shy") and dice(50):
        $ rc("I suppose you have your reasons...", "Err... Do you... nothing. Never mind.")
    elif ct("Imouto"):
        $ rc("Whaaa? Are you serious?", "What, that's it? Boring and stupid!")
    elif ct("Dandere"):
        $ rc("Pathetic...", "You are a bad person.")
    elif ct("Tsundere"):
        $ rc("You really must have a lot of free time to fool around like this...", "Hmph! Whatever!")
    elif ct("Kuudere"):
        $ rc("How unreliable...", "That was quite pathetic, admit it.")
    elif ct("Kamidere"):
        $ rc("I expected more from you...", "It was entirely unsightly.")
    elif ct("Bokukko"):
        $ rc("Man, that was lame. I mean, really lame.", "Oh c'mon, it's not even funny!")
    elif ct("Ane"):
        $ rc("My, is that it? I expected something... better.", "*sigh* How troublesome...")
    elif ct("Yandere"):
        $ rc("Such a waste of time...", "... *glares with hostility*")
    else:
        $ rc("*sign* No wonder, my horoscope predicted a bad day.", "... *you see disappointment in her eyes before she turns away*")
    $ char.restore_portrait()
    $ char.hide_portrait_overlay()
    return

label interactions_girl_proposes_sex: # character proposes MC sex
    $ char.override_portrait("portrait", "shy")
    if ct("Impersonal"):
        $ rc("So... do you want to have sex?", "I need sex. Let's do it.", "Please do perverted things to me. I'm ready.", "Please allow me to check if our bodies match. I'll take full responsibility.", "I would like to have sex with you. Is that going to be a problem?", "Can we have sex? I feel like I need it.")
    elif ct("Shy"):
        $ rc("Uh... p-please d-do it for me... my whole body's aching right now...", "Aah... p-please... I-I want it... I can't think of anything else now!", "Ummm.... do you... not wish to do it...? ...I... really want it...", "I-I want to... be... with you...", "Right now... I want you to do it with me now... Please...", "I-I'm actually really good at sex! So... I-I'd like to show you...", "Um, I-I want to do it... So... Could we have sex?")
    elif ct("Imouto"):
        $ rc("Let's do kinky things... Come on? Puh-leaaase.", "I've got a huge favor to ask! Fuck me right now! Pleaaase!", "So, um... are you interested in sex? I mean, uhm... I'd kinda like to... do it with you?", "Uuu... I'm boooored! Let's do something fun! Like um...maybe have sex or something...")
    elif ct("Dandere"):
        $ rc("Looking at you... makes me want to do it. Do you want to?", "You want to feel good too, don't you?", "How about we do *it*? It'll be fine, leave it to me.", "Let's... feel good together.", "Do you want to spend some time inside of me?", "You are interested in sex and stuff, right? In that case, come on...")
    elif ct("Tsundere"):
        $ rc("Hey, want to do it? S-sex, I mean...", "C'mon, you want to do it too, right?", "Maybe I could agree if you asked me...  Geez! I'm telling you it's ok to have sex with me!", "You know... You wanna to have sex... with me?", "D-do you want to do that with me, maybe...? It's fine with me if you want to...", "C'mon. We're doing it. Doing what...? Haven't you figured it out?"),
    elif ct("Kuudere"):
        $ rc("I-I was thinking...That I wanted to be one with you...", "Hey, I want to feel you inside me. Okay?", "Come on, I can tell that you're horny... Feel free to partake of me.", "Uhm... you're interested, right? In sex and stuff...", "H-hey, maybe the two of us could have... an anatomy lesson?", "I sort of want to do it now... You're cool with it, right?")
    elif ct("Kamidere"):
        $ rc("Hey. Want to fuck...?", "Hey, you want to do perverted stuff...?", "So, let's do it. ...Huh? You were watching me because you wanted to fuck, right?", "You want to do me, don't you? Then step up and honestly say, 'hey, I want to do you'!", "What, you're looking at me like you want me, right? Then come over here.", "I'm specially allowing you to do whatever you like with me... You'll do it, right?", "You look like you really want to, so I'll let you do me.")
    elif ct("Bokukko"):
        $ rc("Hey... if you'd like, I'll give ya' some lovin' ♪", "C'mon, it's time to do 'it', what do you say?", "...Okay, that's it! I can't stand it! Sorry, I've gotta fuck ya!", "Hey... You want to have sex, don't ya?", "C'mon, c'mon, let's get kinky? C'mon, let's fuck!", "Shit, I'm horny as hell. Hey? You up for a go?", "Hey... you wanna mess around...? Let's do it while we got some time to kill...", "Aah geez, I can't hold it anymore! Let's fuck!", "Hey, d'you wanna do me? D'you wanna fuck me?")
    elif ct("Ane"):
        $ rc("I was thinking of having sex with you... Is it ok...?", "Do you want to do it right now? I very much approve.", "Um... Is it ok with you if we have sex?", "How about this? That is to say... getting to know each other a bit better through sex?", "If you wish, shall I take care of your sexual needs?", "Excuse me... Would you like to have sex?", "You feel like doing it, don't you...? I really want it right now ♪")
    elif ct("Yandere"):
        $ rc("Come on, I can tell that you're horny... Feel free to partake of me.", "I can do naughty stuff, you know? ...Want to see?", "Hey, you want to do it with me, right? There's no use trying to lie about it.", "Uhuhu... don't you want to have sex with me?", "Come on, I can tell you need some release... just leave it to me.", "Let's do it! Right now! Take off your clothes! Hurry!")
    else:
        $ rc("Hey... Let's have sex.", "Say... d-do you want to do it... too?", "Um.. w-would you mind... having sex with me?", "Um... Please, have sex with me.", "Hey... do you think... we could do it?", "H-hey... Hmm, do I really need to be the one to say it... F-fuck me!", "Hey... I wanna have sex with you. Is that okay?")
    $ char.restore_portrait()
    return

label interactions_sex_begins: # lines in the beginning of a non-rape scene
    $ char.override_portrait("portrait", "shy")
    $ char.show_portrait_overlay("like", "reset")
    if ct("Impersonal"):
        $ rc("So, I'll begin the sexual interaction...", "I want you to feel really good.", "Hmm. Now how should I fuck you?", "Come. Touch me gently...", "...I have high expectations.", "I will try to do my best to meet your expectations.", "Now, let's enjoy some sex.", "I'll serve you.")
    elif ct("Shy"):
        $ rc("I-I'll do my best... for your sake!", "Uhm... I want you... to be gentle...", "Uuh... Don't stare at me so much, it's embarrassing...", "...I'm ready now... Do it any time...", "Uh, uhm, how should I...? Eh? You want it like this...? O-okay! Then, h-here I go...", "As I thought, I'm nervous... B-but that's ok... I prepared myself...", "P-Please look... It's become so gushy just from thinking about you...♪", "Sorry if I'm no good at this...")
    elif ct("Imouto"):
        $ rc("Uhuhu, well then, what should I tease first ♪", "Hm hmm! Be amazed at my fabulous technique!", "Umm... please do perverted things to me ♪", "Hehe, I'm going to move a lot for you...", "Aah... I want you...To love me lots...", "Ehehe... now my clothes are all soaked...", "Ehehe, make me feel really good, okay?", "Please be gentle, ok?")
    elif ct("Dandere"):
        $ rc("Be sure to make me feel good too, ok?", "There's no reason for us to hold back... Come on, let's do this.", "I can't wait any more. Look how wet I am just thinking about you...", "Come on... Let's be one, body and soul.", "I will handle... all of your urges.", "My body can't wait any longer...")
    elif ct("Tsundere"):
        $ rc("S-shut up and... entrust your body to me... Okay?", "Humph! I'll show you I can do it!", "I-I'm actually really good at sex! So... I-I'd like to show you...", "D-do it properly, would you? ...I don't want a shoddy performance." , "I'm gonna have sex with you! ..G-get ready!", "You can be rough, I guess... If it's just a little bit...", "Y-you just need to be still and let me do everything... You got that?", "D-do whatever you want..."),
    elif ct("Kuudere"):
        $ rc("I'm going to make you cum. You had better prepare yourself.", "C'mon, I'll do kinky things, so make the preparations.", "Well then, shall I do something that'll make you feel good?", "Let's make this feel really good.", "L-leave it to me... Here, I'll take off your clothes...", "I-I'll make sure to satisfy you...!", "You can do with me... as you'd like...", "In the end, I'm just a normal woman too, you know...")
    elif ct("Kamidere"):
        $ rc("Hmph, I'll prove that I'm the greatest you'll ever have.", "Now... show me the dirty side of you...", "I won't let you go until I'm fully satisfied, so prepare yourself.", "I'll give you a run you'll never forget ♪", "Okay... I suppose I'll just do as I please, uhuhu...", "Now, why don't you just give up and let me at that body of yours?", "Please, show me what you can do... I'm expecting great things.")
    elif ct("Bokukko"):
        $ rc("C'mon, make me feel completely satisfied!", "You've been holding it in, right? You can do it with me, big time. Really big ♪", "Alright then, I'll give ya' some lovin'.", "You can do whatever you want. T-that's 'cause, I wanna know how you like it...", "C'mon, let's make love till every part of our bodies is tired... Uhuhu...")
    elif ct("Ane"):
        $ rc("Now, let us discover the shape of our love ♪", "Hmhm, what is going to happen to me, I wonder? ♪", "Hehe, I won't let you go... Now quiet down and take this like an adult.", "Fufuh, it's okay to do it a little harder ♪", "Hehe... So you're ready to go just from looking at me?  Hehe, that makes me happy.", "There's no need to be ashamed... Please let me take care of you.", "Hmhm, go easy on me, okay?", "Hmhm, be good to me, will you?")
    elif ct("Yandere"):
        $ rc("Ehehe... you can do whatever you want.", "Huhuhu, I'll give you a really. Good. Time.", "Huhu, so here we are... You can't hold it anymore, right?", "I want to try lots of things with you...", "I can't control myself anymore... uhuhu...", "Please let me have a clear look at your face when you cum.", "Huhuh, you'll fuck me like a beast, right?", "Yes! I can't take it anymore, I want it so bad! Ah!")
    else:
        $ rc("I want to do so many dirty things... I can't hold it back ♪", "Leave it to me! I'll do my very best!", "Prepare to receive loads and loads of my love!", "Hehee, just leave it all to me! I'll make this awesome!", "Hehe, I'll give it everything I've got ♪")
    $ char.restore_portrait()
    $ char.hide_portrait_overlay()
    return

label interactions_seen_mast_propose:
    $ char.override_portrait("portrait", "shy")
    if ct("Impersonal"):
        $ rc("If you got excited watching me, we could... Want to?", "I just can't do it alone... Can I count on you for support?")
    elif ct("Shy") and dice(50):
        $ rc("...T-these perverted feelings... You can make them go away, can't you...?", "I- I'm sorry, I just couldn't hold it in any more... So, please, can we...")
    elif ct("Imouto"):
        $ rc("I can't ask for it any more obviously than this! Just fuck me already, pleaaaaaase!", "Hey, come on, won't you touch me? I can't satisfy myself alone...")
    elif ct("Dandere"):
        $ rc("You caught me... Hey, please, can you take over from here?", "Watching me masturbate got you going, right? You wanna mess me up now, don't you?")
    elif ct("Tsundere"):
        $ rc("Even I m...masturbate sometimes! ...S...so, what will you do?", "Y-you saw me masturbating... I demand s-sex as an apology!"),
    elif ct("Kuudere"):
        $ rc("Hey, if you were watching, you know what I wanna do, right..?", "Nn... This urge, I need you to satisfy it for me...")
    elif ct("Kamidere"):
        $ rc("At this point I don't even care.　Fuck me.", "I've been seen indulging in such a foolish act...　There's nothing left for you to do but take responsibility.")
    elif ct("Bokukko"):
        $ rc("Hey... I want you to help me feel even better... Please...♪", "Masturbating's too much work... Hey, you wanna do it for me?")
    elif ct("Ane"):
        $ rc("I can't simply let you go after you saw me pleasuring myself.", "How convenient, you came in at just the right time... Hey, you know what I mean, right?")
    elif ct("Yandere"):
        $ rc("I'm all warmed up and ready to go... Want to do it?", "I would so much rather you do it than have to do it myself... Won't you?")
    else:
        $ rc("Uuu, it's not enough by myself... Help me out here ♪", "Oh, it's you, [char.mc_ref]... What to join?")
    $ char.restore_portrait()
    return

label interactions_seen_mast:
    $ char.override_portrait("portrait", "shy")
    if ct("Impersonal"):
        $ rc("What is it? I want to get back to what I was doing...", "It looks like I've been caught touching myself.")
    elif ct("Shy"):
        $ rc("Hyah!? I-I'm sorry! I'll wipe it off right away...!", "I-I... what an embarrassing thing to do...")
    elif ct("Imouto"):
        $ rc("Ehehe, I'm all sticky...♪", "I-It's nothing, I was just a little itchy...")
    elif ct("Dandere"):
        $ rc("Aw, I was almost there...", "...Even you have times when you need to...do it yourself, right?")
    elif ct("Tsundere"):
        $ rc("Kuh... Sometimes I masturbate too, you know. What's wrong with that...?!", "...I wasn't really doing anything, you know? Yeah."),
    elif ct("Kuudere"):
        $ rc("Hya!? I-I wasn't... Ah, no, well...You're not wrong, but...", "Even I have times when I wish to console myself.")
    elif ct("Kamidere"):
        $ rc("God, can't you see I'm playing with myself here? What is it?", "...I've shown you something foolish. Please forget about it.")
    elif ct("Bokukko"):
        $ rc("Geez, I was in the zone! Quit bothering me!", "What do you want? And it was just getting good too, jeez...")
    elif ct("Ane"):
        $ rc("Hehe, you caught me...", "Um, that's embarrassing... Please don't look at me so much.")
    elif ct("Yandere"):
        $ rc("Hehehe, I just got a bit horny...", "Hey, can't you take a hint...? I'm kinda busy here...")
    else:
        $ rc("Hyaa!?　Eh, ah, um, I just, well... Ahaha...", "Hyaaah!? I, I don't do anything..!")
    $ char.restore_portrait()
    return

label interactions_too_many_lines: # overused non-sexual line
    $ char.override_portrait("portrait", "indifferent")
    $ char.show_portrait_overlay("angry", "reset")
    if ct("Impersonal"):
        $ rc("I request change of the subject.", "I don't feel the need to discuss this anymore.")
    elif ct("Shy") and dice(50):
        $ rc("Um... Can you stop already?", "Um... Please, this is honestly too much...")
    elif ct("Imouto"):
        $ rc("Stop it, that's annoying and boring!", "Uuuh, aren't you bored, talking about it again and again?")
    elif ct("Dandere"):
        $ rc("...You want to talk about that again?", "...It is a bother talking so much about the same thing.")
    elif ct("Tsundere"):
        $ rc("Geez, give it a rest already!", "Ugh, you're really persistent!"),
    elif ct("Kuudere"):
        $ rc("The more persistent you get, the more I want to shoot down whatever you say.", "Geez, you're too persistent.")
    elif ct("Kamidere"):
        $ rc("How many times are you going to talk about it?", "Why do you keep talking about it? We already discussed it.")
    elif ct("Bokukko"):
        $ rc("Gawd, stop repeating yourself!", "Hey, it becomes annoying. Don't you want to talk about something else?")
    elif ct("Ane"):
        $ rc("You keep going back to the same thing again and again... You're bothering me.", "Persistence is not a virtue, you know?")
    elif ct("Yandere"):
        $ rc("I hate people who are too persistent.", "Give it a rest. We already discussed it.")
    else:
        $ rc("Why do you keep repeating yourself?", "Goodness, how many times are you going to talk about it?")
    "Maybe you should talk about something else."
    $ char.hide_portrait_overlay()
    $ char.restore_portrait()
    return

label interactions_too_many_sex_lines: # overused sexual line
    $ char.override_portrait("portrait", "indifferent")
    $ char.show_portrait_overlay("sweat", "reset")
    if ct("Impersonal"):
        $ rc("I believe it's enough for today.", "I don't feel the need to do it one more time.")
    elif ct("Shy") and dice(50):
        $ rc("S-sorry, let's do it later m-maybe..?", "Um... Please, this is honestly too much for today...")
    elif ct("Imouto"):
        $ rc("Stop it, that's annoying and boring!", "Uuuh, aren't you bored, doing it again and again?")
    elif ct("Dandere"):
        $ rc("...You want to do it again? I don't want to.", "...Let's stop here. I'm tired of it.")
    elif ct("Tsundere"):
        $ rc("Geez, give it a rest already!", "Ugh, you're really persistent. Stop it."),
    elif ct("Kuudere"):
        $ rc("I think we should take a break.", "You're too persistent.")
    elif ct("Kamidere"):
        $ rc("How many times are you going to do it?", "Unfortunately, I have no intentions to do it again.")
    elif ct("Bokukko"):
        $ rc("Geez, enough already! I don't wanna to.", "Hey, it becomes annoying. Don't you want to do something else?")
    elif ct("Ane"):
        $ rc("We keep doing it again and again... Let's stop it, alright?", "Persistence is not a virtue, you know?")
    elif ct("Yandere"):
        $ rc("You are too persistent. I don't feel like it.", "Give it a rest. We already did it.")
    else:
        $ rc("Aren't you tired of it? I am.", "How many times are you going to do it?")
    $ char.restore_portrait()
    $ char.hide_portrait_overlay()
    return

label interactions_frigid_sex_refuse:
    $ char.override_portrait("portrait", "indifferent")
    $ char.show_portrait_overlay("sweat", "reset")
    if ct("Impersonal"):
        $ rc("I don't feel the need to do it right now.")
    elif ct("Shy") and dice(50):
        $ rc("S-sorry, let's do it later m-maybe..?")
    elif ct("Imouto"):
        $ rc("Stop it, that's annoying and boring!", "Uuuh, aren't you bored, doing it again and again?")
    elif ct("Dandere"):
        $ rc("I don't want to.")
    elif ct("Tsundere"):
        $ rc("Geez, give me a break, ok?"),
    elif ct("Kuudere"):
        $ rc("I think I need a break today.")
    elif ct("Kamidere"):
        $ rc("Unfortunately, I have no intentions to do it.")
    elif ct("Bokukko"):
        $ rc("Nah, don't wanna. Don't you want to do something else?")
    elif ct("Ane"):
        $ rc("Apologies, I'm not in the mood today.")
    elif ct("Yandere"):
        $ rc("I don't feel like it.")
    else:
        $ rc("I'm not in the mood, sorry.")
    "Maybe you should try something else."
    $ char.restore_portrait()
    $ char.hide_portrait_overlay()
    return

label interactions_blowoff(char=None, exit=None):
    $ hs()
    show expression char.get_vnsprite() as vn_sprite
    $ char.override_portrait("portrait", "angry")
    $ char.show_portrait_overlay("angry")
    with dissolve

    if ct("Yandere"):
        $ rc("Stay away. It's your final warning.", "You want to die? If not, go away.")
    elif ct("Impersonal"):
        $ rc("...Leave.", "I have no interest in you.")
    elif ct("Shy") and dice(50):
        $ rc("...D-don't come close to me.", "...S-S-Stay away!")
    elif ct("Dandere"):
        $ rc("What is it? I want to get back to what I was doing...", "I personally dislike you.")
    elif ct("Kuudere"):
        $ rc("Hmph, I don't even want to hear it. Go away.", "...I don't think I have reason to talk to you.")
    elif ct("Tsundere"):
        $ rc("Leave me alone!", "Go away. ...I said get the hell away from me!", "...Lowlife.")
    elif ct("Ane"):
        $ rc("Could you leave me alone?", "There is not a single shred of merit to your existence.")
    elif ct("Kamidere"):
        $ rc("You dirty little...", "It's you again. Don't bother me!")
    elif ct("Imouto"):
        $ rc("Jeez! Bug off already!", "You good-for-nothing...")
    elif ct("Bokukko"):
        $ rc("You just won't shut up, will you...", "Geez, you're pissing me off!")
    else:
        $ rc("Leave. I don't want to talk to you.", "Why do you keep bothering me?")

    $ last_label = exit
    hide vn_sprite
    $ char.hide_portrait_overlay()
    $ renpy.show_screen(exit)
    with dissolve
    return

label interactions_alone_together:
    $ char.override_portrait("portrait", "shy")
    if ct("Impersonal"):
        $ rc("No one's around, huh... What shall we do?", "Hmm? Nobody here but us...")
    elif ct("Shy") and dice(50):
        $ rc("Ah, it seems, um... Just us, huh...", "I-I get sort of nervous when we're alone...")
    elif ct("Imouto"):
        $ rc("Ehehe... Come on now, there's nobody here but us.", "Hey, hey... We're all alone, aren't we?")
    elif ct("Dandere"):
        $ rc("We're all by our lonesome, huh...?", "Hm? There's nobody here...")
    elif ct("Tsundere"):
        $ rc("Wh-when did it become...just the two of us...?", "We're alone, now's my chance... Is what you're thinking, isn't it?"),
    elif ct("Kuudere"):
        $ rc("Hm? ...Oh, looks we're all alone.", "So we're the only ones here...")
    elif ct("Kamidere"):
        $ rc("You know, it's just the two of us, hmm...?", "Just you and me now, huh...")
    elif ct("Bokukko"):
        $ rc("Ehehe ♪ It's just the two of us! What'll you do? What do you wanna do??", "Ooh, lookie here, no one's around...")
    elif ct("Ane"):
        $ rc("Oh my, it's just the two of us, isn't it.", "Oh my, we're completely alone, aren't we.")
    elif ct("Yandere"):
        $ rc("It's kind of embarrassing, isn't it? Just the two of us.", "We're alone, aren't we? ...Hmhm ♪")
    else:
        $ rc("There's nobody around... Hehe ♪", "I-Is it alright? We're here...alone together...")
    $ char.restore_portrait()
    return

label interactions_study_together: # not used atm
    $ char.override_portrait("portrait", "confident")
    if ct("Impersonal"):
        $ rc("Want to study at my house?", "If it's you, I'm sure we'll be able to work together. Let's study at my house.")
    elif ct("Shy") and dice(50):
        $ rc("Um... Want to study at my place...?", "Um, if you're free, would you like to come to my place? Just thought we could study together...")
    elif ct("Imouto"):
        $ rc("How about it? If you're free, want to come over and study?", "Hey, you free? You're free, right? You wanna study at my place? Right?")
    elif ct("Dandere"):
        $ rc("Come study at my place?", "How about studying in my house?")
    elif ct("Tsundere"):
        $ rc("You're free, aren't you? Wanna study at my place?", "Come to my house. You can help my with studies, right?"),
    elif ct("Kuudere"):
        $ rc("We're studying at my house. Sound good?", "Hey, wanna come over for studies?")
    elif ct("Kamidere"):
        $ rc("Come to my house. Let's study together.", "Excuse me, would you like to come over to my house and study?")
    elif ct("Bokukko"):
        $ rc("I was thinking about studying at my place, what do you think?", "Want to drop by my house to study?")
    elif ct("Ane"):
        $ rc("Let's go study at my house! I'll make us some tea.", "It would be lovely to have you over to study. What do you say?")
    elif ct("Yandere"):
        $ rc("How about it? Would you like to study at my place?", "If you're free, wanna come over to my place for a study session?")
    else:
        $ rc("I was just about to go home. Mind tutoring me for a bit?", "If you're free, want to come to my house to study?")
    $ char.restore_portrait()
    return

label interactions_study_sex: # not used atm
    $ char.override_portrait("portrait", "shy")
    if ct("Impersonal"):
        $ rc("Come to my room. To study.")
    elif ct("Shy") and dice(50):
        $ rc("Right now, there's no one home... 　So we could study, or do other stuff...", "Would you like to...come to my place? ...T-There's nobody... home right now...")
    elif ct("Imouto"):
        $ rc("H-hey... Want to come over and study? Just so you know, don't do anything perverted, okay?　I'm serious!", "Should we study at my place? Oh, but there's no one else at home, you see...")
    elif ct("Dandere"):
        $ rc("...Come to my house. ...To study, of course.", "Come study and do various other things at my place?")
    elif ct("Tsundere"):
        $ rc("Want to come over? ...T-to study, obviously.", "Come up to my room. ...For studying, of course! Studying!"),
    elif ct("Kuudere"):
        $ rc("Come to my house. You're not allowed to complain.", "Um, so... do you wanna come over and, um...study?")
    elif ct("Kamidere"):
        $ rc("I want you to come to my room. To study or something.", "Um, come study at my house... There's some things I want you to look over...")
    elif ct("Bokukko"):
        $ rc("Hey, wanna come over to my place and hang?", "Want to come over? ...T-to study, of course!")
    elif ct("Ane"):
        $ rc("Hey, if we go to my house we can study lots of different things ♪", "Let's go study at my house! ...Oh, it'll be just innocent studying, you know?", "Might I interest you in coming to my room? We could pool our knowledge together.")
    elif ct("Yandere"):
        $ rc("There's nobody home right now, so... Want to come over and...study?", "Hey... Wanna come to my place to study? What d'you say?")
    else:
        $ rc("Are you free? If you are, then... How about you come over?", "Hey, wanna do something at my house? You know, like, studying or something?")
    $ char.restore_portrait()
    return

label interactions_study_sex_lines: # not used atm
    $ char.override_portrait("portrait", "suggestive")
    if ct("Impersonal"):
        $ rc("Doesn't look like you can concentrate well... That's because...of this, isn't it?", "You looked like you wanted it. I just thought I'd make it easier on you.")
    elif ct("Shy") and dice(50):
        $ rc("Um... I'm sorry. I just wanted to know more about you.", "S-sorry, I couldn't control myself... P-please don't hate me...")
    elif ct("Imouto"):
        $ rc("Hey, I bored... Maybe we should do something else, like, you know...", "Okay, okay! I think we should study some naughty stuff too! Don't you agree?")
    elif ct("Dandere"):
        $ rc("Studying is important, but... So is studying this here.", "Let's study physical education today.")
    elif ct("Tsundere"):
        $ rc("What's wrong? You are not against it, right...?", "W-we can study any time we want, right? So..."),
    elif ct("Kuudere"):
        $ rc("You tempted me. You're not allowed to say no.", "This is also an important subject. Physical education.")
    elif ct("Kamidere"):
        $ rc("My my... You knew things were going to end up like this, right?", "I studied really hard, right?　So I'd like to be rewarded...")
    elif ct("Bokukko"):
        $ rc("Well then, after a bit of light study... Shall we do it?", "Alright, so... There's, you know... other things we can do, right...?")
    elif ct("Ane"):
        $ rc("Ahh... It's so hot in here... What should we do about it... *glance*", "Hmhm, I've thought of something else we might try... Would you care to take a guess?")
    elif ct("Yandere"):
        $ rc("Hehe, studying is great and all, but... Can't I interest you in a little of this right here...?", "Hey, what do you this about studying 'this'? You don't mind, don't you?")
    else:
        $ rc("It'll be alright. As long as we aren't too loud, no one will find out. Right?", "Well then, let's get right to studying 'this' ♪")
    $ char.restore_portrait()
    return

label interactions_teaching_lines: # not used atm
    $ char.override_portrait("portrait", "indifferent")
    if ct("Impersonal"):
        $ rc("Understood. It all makes sense now.")
    elif ct("Shy"):
        $ rc("Ah...that's...really easy to understand... You're amazing...")
    elif ct("Imouto"):
        $ rc("...Wow, that really helped, it's a lot easier to understand now!")
    elif ct("Dandere"):
        $ rc("I see... Thanks for the explanation.")
    elif ct("Tsundere"):
        $ rc("...It pains me to admit it, but I understand now."),
    elif ct("Kuudere"):
        $ rc("That's much easier to understand. You have my thanks.")
    elif ct("Kamidere"):
        $ rc("...Don't get all full of yourself because you can teach a little.")
    elif ct("Bokukko"):
        $ rc("Whoa! I've got it now! Even I can understand it now!")
    elif ct("Ane"):
        $ rc("Just like I thought, you make it seem so much easier to understand.")
    elif ct("Yandere"):
        $ rc("Oh, I see now... That will be helpful.")
    else:
        $ rc("Ah, I see... I think I kinda get it now ♪")
    $ char.restore_portrait()
    return

label interactions_visit_house: # not used atm, maybe will be useful later
    $ char.override_portrait("portrait", "shy")
    if ct("Impersonal"):
        $ rc("I want you to come to my room. I want... to be alone with you.", "I've made space at my house, where we can be alone.")
    elif ct("Shy") and dice(50):
        $ rc("Er, um, so... There's no one at my house today... so... I was thinking we could be alone, maybe...", "H-hey! ...Th-there's no one home... at my place... S-so, maybe we could...")
    elif ct("Imouto"):
        $ rc("Hey, hey, want to come to my house? Muhuhu, actually today there's no one home.", "So, you know, there's no one at my house right now... So... okay?")
    elif ct("Dandere"):
        $ rc("I want you to come to my house... Don't mind the reason, just answer the invitation.", "Come to my bedroom. You don't have to worry... no one's there.")
    elif ct("Tsundere"):
        $ rc("Coincidentally, there's no one else at my home today... No one at all..."),
    elif ct("Kuudere"):
        $ rc("There's nobody at my house right now... How about it?", "No one else is at home today... Will you come over?")
    elif ct("Kamidere"):
        $ rc("You know, today, there's no one at my house... Okay...?", "Since there's no one at my house... How about going there?")
    elif ct("Bokukko"):
        $ rc("H-hey... you should come to my house... You know what I mean, right...?", "Right now there's nobody at my place... Say, you'll come, right?")
    elif ct("Ane"):
        $ rc("If you visit my house, I'll give you a wonderful memory ♪")
    elif ct("Yandere"):
        $ rc("Want to go to my house? Fufu, when we get there, we can have some fun.")
    else:
        $ rc("Um, er... There's no one home at my place right now... Wanna come over?", "You know... right now... There's nobody at my house...")
    $ char.restore_portrait()
    return

label interactions_invite_to_sparring: # used in hidden village at very least, might be useful for other places
    $ char.override_portrait("portrait", "happy")
    if ct("Impersonal"):
        $ rc("Do you want to exercise with me?", "Show me how well you move.", "Please help me practice some.", "Join me for practice.")
    elif ct("Shy") and dice(50):
        $ rc("I thought I would exercise a bit... Um... What do you say we go together...?", "I was t-thinking of doing a bit of exercise... D-do you wanna come along?", "Um, I'd like to practice with you... is that okay...?")
    elif ct("Imouto"):
        $ rc("Hey, It's training time! Together, of course!", "Hey hey, come work out with me for a bit!", "Hey, help me practice a little!")
    elif ct("Dandere"):
        $ rc("Excuse me, I want to build up my strength... Would you like to join me?", "I wish to train my body. Join me?", "Wanna practice with me?")
    elif ct("Tsundere"):
        $ rc("I was thinking about doing some training, how about it?", "Come on, you need to work out. I'll even help you."),
    elif ct("Kuudere"):
        $ rc("I was thinking about training, but I can't do it alone, so...", "Come on, keep me company in my practice, ok?", "Sorry to ask, but I need help with my training.")
    elif ct("Kamidere"):
        $ rc("We can at least exercise together, don't you think?", "Would you care to build up some endurance with me?", "Sorry to ask, but could you join me for warming up?")
    elif ct("Bokukko"):
        $ rc("Yo. Keep me company for practice, it's a pain by myself.", "C'mon, let's exercise together!", "Umm, could you come practice with me?", "Hey, there's an exercise I'd like to have a little help with but...")
    elif ct("Ane"):
        $ rc("I need to lose some weight... Want to join me for some exercise?", "Would you care to join me in training our bodies?", "Hey, do you mind helping me practice a bit?", "I'd like you to help me train for a bit, if that's okay?")
    elif ct("Yandere"):
        $ rc("Hey, how about training for a bit?", "You should get a little exercise... Want to do it together?", "Hey, can you come with me to practice for a while?")
    else:
        $ rc("How about it? Want to go for some light exercise?", "Um, would you like to go exercise?", "Come on, let's practice together?")
    $ char.restore_portrait()
    return

label interactions_invite_to_beach: # used in hidden village atm, will be useful for other places
    $ char.override_portrait("portrait", "happy")
    if ct("Impersonal"):
        $ rc("The water is pretty warm here. Interesting.", "I like this swimsuit, it doesn't restrict my movements.")
    elif ct("Shy"):
        $ rc("Swimsuits are s-so embarrassing... P-please don't look at me too much...", "I was t-thinking of swimming a bit... D-do you want to join?")
    elif ct("Imouto"):
        $ rc("Yay! The water is great, let's go swim!", "Hey, you like my swimsuit, don't you? I think it's pretty cool!")
    elif ct("Dandere"):
        $ rc("The weather is nice. Perfect for swimming.", "Do you like this swimsuit? Me? I think it's ok.")
    elif ct("Tsundere"):
        $ rc("Hey, w-where are you looking it?! Don't stare at my swimsuit!", "Come on, at least swim a bit. I'll even keep you company."),
    elif ct("Kuudere"):
        $ rc("It's pretty hot here. Let's try out the water.", "Hmm, maybe this swimsuit is too revealing after all... Hm? You like it? I s-see...")
    elif ct("Kamidere"):
        $ rc("Ahh, the water looks nice. I'm going to swim.", "What do you think? Does my swimsuit suit me? Of course it does.")
    elif ct("Bokukko"):
        $ rc("C'mon, it's swimming time! Don't lag behind! ♪", "Hmm, this swimsuit is kinda tight... Maybe I should try swimming without it, what do you think? ♪")
    elif ct("Ane"):
        $ rc("My, the weather is pretty nice today. Perfect for swimming.", "What do you think about my swimsuit? It's not too revealing, is it?")
    elif ct("Yandere"):
        $ rc("What is it? You like my swimsuit? I'm glad ♪", "Would you like to swim with me? It will be more fun if we do it together.")
    else:
        $ rc("How about it? Do you like my swimsuit? It wasn't easy to pick a good one, you know.", "Come on, let's swim together! I bet the water feels nice! ♪")
    $ char.restore_portrait()
    return

label interactions_bad_goodbye: # character leaves with bad disposition
    $ char.override_portrait("portrait", "indifferent")
    if ct("Impersonal"):
        $ rc("This is farewell. I can't stand you any longer.", "It's over. I'm leaving. I never want to see you again.")
    elif ct("Shy"):
        $ rc("I-I'm sorry. I can't stay here anymore. Goodbye!", "I guess it couldn't be helped... Haah, I can finally relax...")
    elif ct("Imouto"):
        $ rc("Alright, I'm leaving. I don't want to hear any complaints, okay?", "Hey, could you not get involved with me anymore? Goodbye.")
    elif ct("Dandere"):
        $ rc("This is the end of our partnership. I want nothing more to do with you.", "Our agreement is now done. I want nothing more to do with you.")
    elif ct("Tsundere"):
        $ rc("Goodbye. I can't deal with this anymore.", "Ugh... I can't stay here anymore.　Goodbye."),
    elif ct("Kuudere"):
        $ rc("Bye. Don't come near me again.", "I am cutting off all connections with you. Goodbye.")
    elif ct("Kamidere"):
        $ rc("Oh yeah, I don't need you anymore. See ya.", "Spare me from ever having to be around trash like you again. Goodbye.")
    elif ct("Bokukko"):
        $ rc("See ya. Can't stand to be with you for even a moment longer.", "Yeah, about time. Starting now, you and I are strangers!")
    elif ct("Ane"):
        $ rc("I don't want to be here any more. Goodbye.", "You and I are now complete strangers. This has already been decided.")
    elif ct("Yandere"):
        $ rc("I don't want to see your face anymore. Goodbye.", "I no longer feel like I need to be at your side, so... Farewell.")
    else:
        $ rc("I no longer want to stay here. Goodbye.", "We're complete strangers now. Bye.")
    $ char.restore_portrait()
    return

label interactions_good_goodbye: # character leaves with good disposition
    $ char.override_portrait("portrait", "indifferent")
    if ct("Impersonal"):
        $ rc("See you.")
    elif ct("Shy"):
        $ rc("S-see you later.")
    elif ct("Imouto"):
        $ rc("Bye-bye♪")
    elif ct("Dandere"):
        $ rc("Goodbye then...")
    elif ct("Tsundere"):
        $ rc("Fine, see you later."),
    elif ct("Kuudere"):
        $ rc("Alright, later...")
    elif ct("Kamidere"):
        $ rc("Well, see you then.")
    elif ct("Bokukko"):
        $ rc("'kay, see you around!")
    elif ct("Ane"):
        $ rc("Goodbye. If you'll excuse me, then...")
    elif ct("Yandere"):
        $ rc("Ok, see you next time.")
    else:
        $ rc("Alright, see you.")
    $ char.restore_portrait()
    return

label interactions_character_recovers: # char recovers from wound
    $ char.override_portrait("portrait", "happy")
    if ct("Impersonal"):
        $ rc("I apologize for having made you worry about this incident.")
    elif ct("Shy"):
        $ rc("Um, what happened to me... Oh, I see...")
    elif ct("Imouto"):
        $ char.override_portrait("portrait", "sad")
        $ rc("I-I was really scared, you know?! Uuh, I was so scared～")
    elif ct("Dandere"):
        $ rc("I'm sorry for making you worry... I'm okay now.")
    elif ct("Tsundere"):
        $ rc("What is it? Is it that strange I'm still alive?"),
    elif ct("Kuudere"):
        $ rc("I never thought it'd have to come to that...")
    elif ct("Kamidere"):
        $ rc("Sorry for worrying you. Don't worry, I'm okay now.")
    elif ct("Bokukko"):
        $ rc("Mmm, I'm not really sure what happened, but I'm okay now!")
    elif ct("Ane"):
        $ rc("If you never want to go through something like that, be careful.")
    elif ct("Yandere"):
        $ rc("I'm alright. Seems like I worried you.", "Fufu, I've had a rather thrilling experience...")
    else:
        $ rc("Yeah... I'm okay now. Sorry to make you worried.")
    $ char.restore_portrait()
    return

label klepto_stealing:
    if ct("Kleptomaniac"):
        if dice((hero.get_skill("security")/4.0 - char.get_stat("agility"))/10.0) and dice(hero.get_stat("luck")):
            "Just as you begin to talk to [char.name], you notice that [char.p] tried to steal from you."
            menu:
                "How do you react?"
                "Call the guards!":
                    $ rc("Ohh, please nooo, do not call the police...", "I'm really sorry. Can't we just forget about it?", "Please no. I would do anything to make it up to you.")
                    menu:
                        "Ask [char.op], how [char.p] wants to resolve the issue":
                            if cgo("SIW") and interactions_silent_check_for_bad_stuff(char) and not char.flag("quest_cannot_be_fucked") and (not ct("Half-Sister") or "Sister Lover" in hero.traits):
                                $ rc("I know how to make people happy. Why don't we solve this between us?", "I know many ways to satisfy unhappy customers. I'll tell you more in private.", "Just act like real grown-ups. I'm very good handling private stuff...")
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
                                    $ rc("I can pay you [money].", "Would [money] suffice?", "I have only [money] Gold with me. Is that enough compensation?")
                                else:
                                    $ rc("I have nothing! Please let it go.", "I'm poor, could we just go on?")
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
                                $ rc("I can pay you [money].", "Would [money] suffice?", "I have only [money] Gold with me. Is that enough compensation?")
                            else:
                                $ rc("I have nothing! Please let it go.", "I'm poor, could we just go on?")
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
        $ gm.remove_girl(char)
    else:
        "But there is none around to help."
        extend " You just made a fool of yourself. [char.name] scoffs at you."
        char.say "Hahh, call mommy and cry on her shoulder."
        extend " And leave me alone..."
        $ char.set_flag("cnd_interactions_blowoff", day+1)
    jump girl_interactions_end
