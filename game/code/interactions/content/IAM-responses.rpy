init -2 python:
    # Interactions (Girlsmeets conversation-lines):
    class InteractionsResponses(_object):
        @staticmethod
        def say_line(character, lines, mood="indifferent", overlay_args=None, msg_args=None, gossip=False):
            result = random.choice(lines)
            text_args = {"[mc_ref]": character.mc_ref,
                         "[p]": character.p,
                         "[op]": character.op,
                         "[pp]": character.pp,
                         "[pd]": character.pd,
                         "[pC]": character.pC}
            if msg_args is not None:
                text_args.update(msg_args)
            for k, v in text_args.iteritems():
                result = result.replace(k, v)
            character.override_portrait("portrait", mood, add_mood=False)
            if overlay_args is not None:
                character.show_portrait_overlay(*overlay_args)
            if gossip is True:
                character.say("... " + result + " ...")
                #character.say("... ")
                ## record_say...
                ##renpy.store._last_say_who = character
                #renpy.store._last_say_what = "... "
                ##renpy.store._last_say_args = ()
                ##renpy.store._last_say_kwargs = {}
                #extend(result)
                #extend(" ...")
            else:
                character.say(result)
            if overlay_args is not None:
                character.hide_portrait_overlay()
            character.restore_portrait()

        @staticmethod
        def greet_lover(character):
            """
            Outputs a line when a lover greets the MC
            """
            char_traits = character.traits
            mood = character.get_mood_tag(True)
            if mood in ("indifferent", "confident", "happy", "suggestive"):  
                if "Half-Sister" in char_traits and dice(50):
                    if "Impersonal" in char_traits:
                        lines = ("I love you, even though we're siblings.", "I love you, [hero.hs].")
                    elif "Tsundere" in char_traits:
                        lines = ("We're drawn to each other even though we're siblings... it's inevitable that we would fall in love with each other.", "You're the best [hero.hs] ever! Well, if you weren't so perverted you'd be even better... hehe.")
                    elif "Dandere" in char_traits:
                        lines = ("You are my favourite person.", "Be mine alone, [hero.hs].", "Can't siblings love each other..?")
                    elif "Kuudere" in char_traits:
                        lines = ("[hero.hs], you belong to only me, got it? I won't let anyone else have you.", "Do you hate it that your sister always takes care of you? If you do... well...")
                    elif "Imouto" in char_traits:
                        lines = ("Every part of my [hero.hss] belongs to me!", "[hero.hs] and I are bound now. Hehe.", "[hero.hs] is stylish and kind... Hehe....")
                    elif "Bokukko" in char_traits:
                        lines = ("All I need is you, [hero.hss].", "I won't share my [hero.hs] with anybody!", "Siblings getting along well... Own family is best, na?", "How should I say this... [hero.hs] you're sexy... Hehe!")
                    elif "Yandere" in char_traits:
                        lines = ("I love you so much, [hero.hs]. You're very special to me.", "If it's for you, [hero.hs]... I'm ready to do anything!", "*[pC] smiles and stares at you.*")
                    elif "Ane" in char_traits:
                        lines = ("It's natural for siblings to love each other ♥", "Sister will always be here to take care of you.")
                    else:
                        lines = ("I love everything about you... [hero.hs].", "Please look at your sister... as a woman.", "We're bound together now, even though we're siblings...", "Is it weird for siblings to stick together all the time?")
                elif "Shy" in char_traits and dice(50):
                    lines = ("I lik-... I love you...!", "U-Um, er, I, um... I-I... I-I love you!", "Um, ah, er... I...l-li... I li-...! I can't do it!", "Um.... I-I love you very much...", "The two of us are going out... Ahhh...")
                elif "Nymphomaniac" in char_traits and dice(65):
                    lines = ("I'm so lewd, aren't I... I'm thinking of you...doing me...", "Hey, what sorts of things do you think we can do, just the two of us?", "You can have me whenever you want!", "We're lovers, so we should act like lovers, we should get gooey and slap thighs.", "Huhu, I love you ♪ Of course, also in a sexual way.", "Even if we are lovers, I wonder what we should do? Ah, you had dirty thoughts just now, didn't you?", "Um... You don't hate naughty girls... right...?")
                elif "Impersonal" in char_traits:
                    lines = ("I want to know everything about you. And I want you to know everything about me.", "I'm glad I could meet you.", "As long as we remain lovers, I believe it is essential to have a sensual relationship.", "I'll protect you. You can rely on me.")
                elif "Extremely Jealous" in char_traits and dice(45):
                    lines = ("I hate it when you just keep ogling other girls.", "I don't want you flirting with other women.", "Don't get too friendly with other women!", "Hey! Don't look at other girls all the time!", "Erm... I want you to stop looking at other women so much.")
                elif "Kuudere" in char_traits:
                    lines = ("When y-you're around, I can't think straight...", "Just tell me if you need me, okay?", "I love you. ...That's it. Got a problem with that?", "P... Please continue to pursue me. My response will always be positive to you.", "You're very dear to me. I want us to stay together...")
                elif "Tsundere" in char_traits:
                    lines = ("Wh-what are you planning to have me do...?", "You are NOT to leave my side, okay?", "B-being with you throws me off somehow...", "I deal with your perviness every day, so I deserve some praise!", "Umm... I love you. S-Show a little gratitude for being my choice.", "W-what kind of girls do you like? N-no, pretend I didn't say anything...")
                elif "Dandere" in char_traits:
                    lines = ("Sweetheart, sweetheart, sweeeetheart...", "Love you... Mm, it's nothing.", "I want to be with you.", "I want to be your special person...", "I-I'm a lonely person... So don't leave me...", "What can I do to make you look at me...?")
                elif "Imouto" in char_traits:
                    lines = ("Hihi, object of my affection. What is up?", "Hehe, we're lovers.... do whatever you like.", "Ehehe, looooove youuuu♪", "I love you♪ I love you sooo much♪", "Have I become like a proper lover now?")
                elif "Ane" in char_traits:
                    lines = ("I want to be both your big sister and your wife! ♪", "I love you.  ...No, mere words aren't enough.", "I love you. I don't want to leave your side.", "As I thought, having a caring lover is good ♪", "You'll love me forever, right? ♪", "I'm really happy, you know? To be together like this with you ♪")
                elif "Yandere" in char_traits:
                    lines = ("Ah... ehhehe... I'm happy...", "We're lovers, aren't we...? Uhehehe...", "I'm really happy being your girlfriend! ...Ehehe", "I think it's really a good thing I've fallen in love with you.", "Ehehe ♪ Nothing, just looking at your face ♪", "Now how do I get you to fall for me even harder...? Ehehe♪", "It would be nice if we could be together forever.", "We're the most compatible couple in the world! Do you feel the same?")
                elif "Kamidere" in char_traits:
                    lines = ("Even though we're lovers, doing nothing but sex stuff is not acceptable!", "Haaa... How'd I fall in love with someone like this...", "Just because we're l-lovers, doesn't mean I will spoil you...", "Well? What does my lover want from me?", "The only thing you'll ever need is me. Oh yes. Just me. Hehe.", "You think it's about time I turned you into my playtoy? ♪")
                elif "Bokukko" in char_traits:
                    lines = ("Being subtle is such a bother so let me tell you straight... I love you.", "Even though we're dating now, not all that much has changed, huh...", "Say, what do you like about me? ...it's fine, tell me!", "I love you...I super love you...!")
                else:
                    lines = ("I really like you, you know...", "A-As lovers, let's love each other a lot, okay...?", "We shouldn't flirt too much in front of the others, okay?", "I-I love you... Hehehe...♪", "I love you ♪ I love you so much ♪", "I want you to love me more and more! Prepare yourself for it, okay?", "Ehehe, don't you ever, ever leave me...", "I wish we could be together forever...♪", "What do you think other people think when they see us? ...you think maybe, 'Hey, look at that cute couple'...?")
                if mood != "suggestive":
                    mood = "shy"
            elif mood == "uncertain":
                if "Half-Sister" in char_traits and dice(50):
                    if "Impersonal" in char_traits:
                        lines = ("I love you, even though we're siblings.", "I love you, [hero.hs]. I think.")
                    elif "Tsundere" in char_traits:
                        lines = ("We're drawn to each other even though we're siblings... it's inevitable that we would fall in love with each other.", "You're the best [hero.hs] ever! Well, if you weren't so perverted you'd be even better... hehe.")
                    elif "Dandere" in char_traits:
                        lines = ("You are my favourite person.", "Be mine alone, [hero.hs].", "Can't siblings love each other..?")
                    elif "Kuudere" in char_traits:
                        lines = ("[hero.hs], you belong to only me, got it? I won't let anyone else have you.", "Do you hate it that your sister always takes care of you? If you do... well...")
                    elif "Imouto" in char_traits:
                        lines = ("Every part of my [hero.hss] belongs to me!", "[hero.hs] and I are bound now. Hehe.", "[hero.hs] is stylish and kind... Hehe....")
                    elif "Bokukko" in char_traits:
                        lines = ("All I need is you, [hero.hss].", "I won't share my [hero.hs] with anybody!", "Siblings getting along well... Own family is best, na?", "How should I say this... [hero.hs] you're sexy... Hehe!")
                    elif "Yandere" in char_traits:
                        lines = ("I love you so much, [hero.hs]. You're very special to me.", "If it's for you, [hero.hs]... I'm ready to do anything!", "*[pC] smiles and stares at you.*")
                    elif "Ane" in char_traits:
                        lines = ("It's natural for siblings to love each other ♥", "Sister will always be here to take care of you.")
                    else:
                        lines = ("I love everything about you... [hero.hs].", "Please look at your sister... as a woman.", "We're bound together now, even though we're siblings...", "Is it weird for siblings to stick together all the time?")
                elif "Shy" in char_traits and dice(50):
                    lines = ("I lik-... I love you...!", "U-Um, er, I, um... I-I... I-I love you!", "Um, ah, er... I...l-li... I li-...! I can't do it!", "Um.... I-I love you very much...", "The two of us are going out... Ahhh...")
                elif "Nymphomaniac" in char_traits and dice(65):
                    lines = ("I'm so lewd, aren't I... I'm thinking of you...doing me...", "Hey, what sorts of things do you think we can do, just the two of us?", "You can have me whenever you want!", "We're lovers, so we should act like lovers, we should get gooey and slap thighs.", "Huhu, I love you ♪ Of course, also in a sexual way.", "Even if we are lovers, I wonder what we should do? Ah, you had dirty thoughts just now, didn't you?", "Um... You don't hate naughty girls... right...?")
                elif "Impersonal" in char_traits:
                    lines = ("I want to know everything about you. And I want you to know everything about me.", "I'm glad I could meet you.", "As long as we remain lovers, I believe it is essential to have a sensual relationship.", "I'll protect you. You can rely on me.")
                elif "Extremely Jealous" in char_traits and dice(45):
                    lines = ("I don't like it when you just keep ogling other girls.", "Please, stop flirting with other women.", "I'm sorry, but I dislike it when you get too friendly with other women!", "Hey! Don't look at other girls all the time!", "My heart's feeling uneasy and gloomy... I dislike this feeling.", "Erm... I want you to stop looking at other women so much.")
                elif "Kuudere" in char_traits:
                    lines = ("When y-you're around, I can't think straight...", "I c-can help out too if you need me, you know...", "I love you. ...That's it. Got a problem with that?", "P... Please continue to pursue me. My response will always be positive to you.", "You're very dear to me. I want us to stay together...")
                elif "Tsundere" in char_traits:
                    lines = ("Wh-what are you planning to have me do...?", "You are NOT to leave my side, okay?", "B-being with you throws me off somehow...", "I deal with your perviness every day, so I deserve some praise!", "Umm... I love you. S-Show a little gratitude for being my choice.", "W-what kind of girls do you like? N-no, pretend I didn't say anything...")
                elif "Dandere" in char_traits:
                    lines = ("Sweetheart, sweetheart, sweeeetheart...", "Love you... Mm, it's nothing.", "I want to be with you.", "I want to be your special person...", "I-I'm a lonely person... So don't leave me...", "What can I do to make you look at me...?")
                elif "Imouto" in char_traits:
                    lines = ("Hihi, object of my affection. What is up?", "Hehe, we're lovers.... do whatever you like.", "Ehehe, looooove youuuu♪", "I love you♪ I love you sooo much♪", "Have I become like a proper lover now?")
                elif "Ane" in char_traits:
                    lines = ("I want to be both your big sister and your wife! ♪", "I love you.  ...No, mere words aren't enough.", "I love you. I don't want to leave your side.", "As I thought, having a caring lover is good ♪", "You'll love me forever, right? ♪", "I'm really happy, you know? To be together like this with you ♪")
                elif "Yandere" in char_traits:
                    lines = ("Ah... ehhehe... I'm happy...", "We're lovers, aren't we...? Uhehehe...", "I, I'm your girlfriend, right? ...Ehehe", "I think it's really a good thing I've fallen in love with you.", "Ehehe ♪ Nothing, just looking at your face ♪", "Now how do I get you to fall for me even harder...? Ehehe♪", "It would be nice if we could be together forever.", "We're the most compatible couple in the world, aren't we?")
                elif "Kamidere" in char_traits:
                    lines = ("Even though we're lovers, doing nothing but sex stuff is not acceptable!", "Haaa... How'd I fall in love with someone like this...", "Just because we're l-lovers, doesn't mean I will spoil you...", "Well? What does my lover want from me?", "The only thing you'll ever need is me. Oh yes. Just me. Hehe.", "You think it's about time I turned you into my playtoy? ♪")
                elif "Bokukko" in char_traits:
                    lines = ("Being subtle is such a bother so let me tell you straight... I love you.", "Even though we're dating now, not all that much has changed, huh...", "Say, what do you like about me? ...it's fine, tell me!", "I love you...I super love you...!")
                else:
                    lines = ("I really like you, you know...", "A-As lovers, let's love each other a lot, okay...?", "We shouldn't flirt too much in front of the others, okay?", "I-I love you... Hehehe...♪", "I love you ♪ I love you so much ♪", "I want you to love me more and more! Prepare yourself for it, okay?", "Ehehe, don't you ever, ever leave me...", "I wish we could be together forever...♪", "What do you think other people think when they see us? ...you think maybe, 'Hey, look at that cute couple'...?")
                mood = "shy"
            elif mood in ("sad", "tired", "in pain"):
                if "Half-Sister" in char_traits and dice(50):
                    if "Impersonal" in char_traits:
                        lines = ("I love you, even though we're siblings.", "I love you, [hero.hs]. I think.")
                    elif "Tsundere" in char_traits:
                        lines = ("We're drawn to each other even though we're siblings... it's inevitable that we would fall in love with each other.", "You're the best [hero.hs] ever! Well, if you weren't so perverted you'd be even better... hehe.")
                    elif "Dandere" in char_traits:
                        lines = ("You are my favourite person.", "Be mine alone, [hero.hs].", "Can't siblings love each other..?")
                    elif "Kuudere" in char_traits:
                        lines = ("[hero.hs], you belong to only me, got it? I won't let anyone else have you.", "Do you hate it that your sister always takes care of you? If you do... well...")
                    elif "Imouto" in char_traits:
                        lines = ("Every part of my [hero.hss] belongs to me!", "[hero.hs] and I are bound now.", "[hero.hsC] is stylish and kind...")
                    elif "Bokukko" in char_traits:
                        lines = ("All I need is you, [hero.hss].", "I won't share my [hero.hs] with anybody!", "Siblings getting along well... Own family is best, na?", "How should I say this... [hero.hs], I need you...")
                    elif "Yandere" in char_traits:
                        lines = ("I love you so much, [hero.hs]. You're very special to me.", "If it's for you, [hero.hs]... I'm ready to do anything!", "*[pC] stares at you with dreamy eyes.*")
                    elif "Ane" in char_traits:
                        lines = ("It's natural for siblings to love each other ♥", "Sister will always be here to take care of you.")
                    else:
                        lines = ("I love everything about you... [hero.hs].", "Please look at your sister... as a woman.", "We're bound together now, even though we're siblings...", "Is it weird for siblings to stick together all the time?")
                elif "Shy" in char_traits and dice(50):
                    lines = ("I lik-... I love you...", "U-Um, I-I love you very much...", "Um, ah, really, er... I like you.", "The two of us are going out... Ahhh...")
                elif "Impersonal" in char_traits:
                    lines = ("I want to know everything about you. And I want you to know everything about me.", "I'm glad I could meet you.", "As long as we remain lovers, I believe it is essential to have a sensual relationship.", "I'll protect you. You can rely on me.")
                elif "Extremely Jealous" in char_traits and dice(45):
                    lines = ("I hate it when you just keep ogling other girls.", "I don't want you flirting with other women.", "I'm sorry, but I dislike it when you get too friendly with other women!", "Hey! Don't look at other girls all the time!", "My heart's feeling uneasy and gloomy... I dislike this feeling.", "Erm... I want you to stop looking at other women so much.")
                elif "Kuudere" in char_traits:
                    lines = ("When y-you're around, I can't think straight...", "I c-can help out too if you need me, you know...", "I love you. ...That's it. Got a problem with that?", "P... Please continue to pursue me. My response will always be positive to you.", "You're very dear to me. I want us to stay together...")
                elif "Tsundere" in char_traits:
                    lines = ("Wh-what are you planning to have me do...?", "You are NOT to leave my side, okay?", "B-being with you throws me off somehow...", "I deal with your perviness every day, so I deserve some praise!", "Umm... I love you. S-Show a little gratitude for being my choice.", "W-what kind of girls do you like? N-no, pretend I didn't say anything...")
                elif "Dandere" in char_traits:
                    lines = ("Sweetheart, sweetheart, sweetheart...", "Love you... Mm, it's nothing.", "I want to be with you.", "I want to be your special person...", "I-I'm a lonely person... So don't leave me...", "What can I do to make you look at me...?")
                elif "Imouto" in char_traits:
                    lines = ("Hey, object of my affection. What is it?", "We're lovers.... do whatever you like.", "Have I become like a proper lover now?")
                elif "Ane" in char_traits:
                    lines = ("I want to be both your big sister and your wife!", "I love you.  ...No, mere words aren't enough.", "I love you. I don't want to leave your side.", "As I thought, having a caring lover is good...", "You'll love me forever, right?")
                elif "Yandere" in char_traits:
                    lines = ("Ah... I'm glad to have you by my side...", "We're still lovers, aren't we...?", "I, I'm your girlfriend, right? ... It is so nice...", "I think it's really a good thing I've fallen in love with you.", "Looking at your face bring me peace...", "It would be nice if we could be together forever.", "We're the most compatible couple in the world, aren't we?")
                elif "Kamidere" in char_traits:
                    lines = ("Even though we're lovers, doing nothing but sex stuff is not acceptable!", "Haaa... How'd I fall in love with someone like this...", "Just because we're l-lovers, doesn't mean I will spoil you...", "Well? What does my lover want from me?", "The only thing you'll ever need is me. Oh yes. Just me. Hehe.", "You think it's about time I turned you into my playtoy? ♪")
                elif "Bokukko" in char_traits:
                    lines = ("Being subtle is such a bother so let me tell you straight... I love you.", "Even though we're dating now, not all that much has changed, huh...", "Say, what do you like about me? ...it's fine, tell me!", "I love you...I super love you...!")
                else:
                    lines = ("I really like you, you know...", "A-As lovers, let's love each other a lot, okay...?", "We shouldn't flirt too much in front of the others, okay?", "I-I love you... Hehehe...♪", "I love you ♪ I love you so much ♪", "I want you to love me more and more! Prepare yourself for it, okay?", "Ehehe, don't you ever, ever leave me...", "I wish we could be together forever...♪", "What do you think other people think when they see us? ...you think maybe, 'Hey, look at that cute couple'...?")
                mood = "shy"
            else:
                raise Exception("Mood %s is not implemented for greet_lover!" % mood)
            iam.say_line(character, lines, mood)

        @staticmethod
        def greet_good(character):
            """
            Outputs a line when the character greets the MC with high disposition
            """
            char_traits = character.traits
            mood = character.get_mood_tag(True)
            if mood == "indifferent":
                if "Impersonal" in char_traits:
                    lines = ("Talk, I'll listen.", "It is good to have you around.", "It is nice to see you again.")
                elif "Shy" in char_traits and dice(50):
                    lines = ("I-I'm getting a little bit... used to you, [mc_ref]...", "Hey, am I... do you... Err... nothing. Never mind.", "Being near you calms me down...", "H-Hi...Is it really ok to talk? I don't want to bother you...", "If I am with you, I...  I-it's nothing...")
                elif "Tsundere" in char_traits:
                    lines = ("Come. If you have something to say, say it.", "Yes? Do you want to tell me something, [mc_ref]?")
                elif "Dandere" in char_traits:
                    lines = ("Did you need something?", "Maybe... I like your voice.", "It's you. Good to see you, [mc_ref]?")
                elif "Kuudere" in char_traits:
                    lines = ("You certainly like to be with me, don't you...", "Seriously... why is it so hard to be serious...?", "I'm listening. What is it?", "Is there something you would like to consult with me? It's alright.")
                elif "Ane" in char_traits:
                    lines = ("If ever you're in trouble... you can always come to me.", "What's the matter? Need some advice?", "Ah... I was just thinking, it'd be so nice to talk to you...", "If there's anything I can do, please tell me, okay?", "You can call on me anytime. And I'll do the same with you.", "If something's wrong, you can always talk to me.")
                elif "Imouto" in char_traits:
                    lines = ("Hn? What's up? You can tell me anything ♪", "For the people I like, I will do my best ♪", "Hi! Tell me, tell me, what'cha doin'?", "Let's have us a chat ♪ Lalala ♪")
                elif "Bokukko" in char_traits:
                    lines = ("How's it going? Doing alright?", "Oh, what'cha doing?... What'ya wanna do?", "Ohoh, it's you, [mc_ref] ♪", "Yo! What'cha doin'?", "Whazzup?", "Hey [mc_ref], let's do something!", "Hey, will you talk with me for a bit?", "C'mon, c'mon, put a smile on!", "Um, so hey, you wanna chat?")
                elif "Yandere" in char_traits:
                    lines = ("Eh, what? Do you want to consult with me?", "Huu... You certainly like to be with me, don't you...", "Hm? Something I can do?")
                elif "Kamidere" in char_traits:
                    lines = ("Huhu, You seem like you'd be good for some entertainment ♪", "...Do you want to chat with me that badly?", "Ok. I have chosen to give you some of my valuable time today. Don't make me regret that.", "Good timing. Come on, entertain me.", "I have fairly high expectation of you, [mc_ref] ♪")
                else:
                    lines = ("Hey, how's it going?", "Well, what shall we talk about..?", "What do you want to do?", "Ah, [mc_ref]! Let's talk for a while.", "Hi! Another splendid day today!")
                mood = "happy"
            elif mood == "confident":
                if "Impersonal" in char_traits:
                    lines = ("Talk, I'll listen.", "Your presence makes me feel comfortable.", "Talk to me, I like to hear your voice!")
                elif "Shy" in char_traits and dice(50):
                    lines = ("I-I'm getting a little bit... used to you, [mc_ref]...", "Being near you calms me down...", "H-Hi...Is it really ok to talk? I don't want to bother you...", "If I am with you, I...  I-it's nothing...")
                elif "Tsundere" in char_traits:
                    lines = ("If you have something to say, say it.", "Don't be so friendly with me, [mc_ref]...", "Please do not act like we are close to each other, [mc_ref].")
                elif "Dandere" in char_traits:
                    lines = ("Did you need something?", "Maybe... I like your voice.", "It's you. Good to see you, [mc_ref]?")
                elif "Kuudere" in char_traits:
                    lines = ("You certainly like to be with me, don't you...", "Seriously... why is it so hard to be serious...?", "I'm listening. What is it?", "Is there something you would like to consult with me? It's alright.")
                elif "Ane" in char_traits:
                    lines = ("Are you in trouble? You know you can rely on me, right?", "What's the matter? Need some advice?", "Ah... I was just thinking, it'd be so nice to talk to you.", "If there's anything I can do, please tell me, okay?", "You can call on me anytime. And I'll do the same with you.", "If something's wrong, you can always talk to me.")
                elif "Imouto" in char_traits:
                    lines = ("Hn? What's up? You can tell me anything ♪", "For the people I like, I will do my best ♪", "Hi! Tell me, tell me, what'cha doin'?", "Let's have us a chat ♪ Lalala ♪")
                elif "Bokukko" in char_traits:
                    lines = ("How's it going? Doing alright?", "Oh, what'cha doing?... What'ya wanna do?", "Ohoh, it's you, [mc_ref] ♪", "Yo! What'cha doin'?", "Whazzup?", "Hey [mc_ref], let's do something!", "Hey, will you talk with me for a bit?", "C'mon, c'mon, put a smile on!", "Um, so hey, you wanna chat?")
                elif "Yandere" in char_traits:
                    lines = ("Eh, what? Do you want to consult with me?", "Huu... You certainly like to be with me, don't you...", "Hm? Something I can do?")
                elif "Kamidere" in char_traits:
                    lines = ("Huhu, You seem like you'd be good for some entertainment ♪", "...Do you want to chat with me that badly?", "Ok. I have chosen to give you some of my valuable time today. Don't make me regret that.", "Good timing. Come on, entertain me.", "I have fairly high expectation of you, [mc_ref] ♪")
                else:
                    lines = ("Hey, how's it going?", "Well, what shall we talk about..?", "What do you want to do?", "Ah, [mc_ref]! Let's talk for a while.", "Hi! Another splendid day today!")
                mood = "happy"
            elif mood == "uncertain":
                if "Impersonal" in char_traits:
                    lines = ("Yes? I'm listening.", "I think your presence has a good effect on me.", "What is your purpose in getting close to me?", "Being with you... calms me.")
                elif "Shy" in char_traits and dice(50):
                    lines = ("I-I'm getting a little bit... used to you, [mc_ref]...", "Hey, am I... do you... Err... nothing. Never mind.", "Being near you calms me down...", "H-Hi...Is it really ok to talk? I don't want to bother you...", "If I am with you, I...  I-it's nothing...")
                elif "Tsundere" in char_traits:
                    lines = ("Come. You have something to say?", "Uhm.. you are too friendly with me, [mc_ref]...", "Do you really think we are getting closer, [mc_ref]?")
                elif "Dandere" in char_traits:
                    lines = ("Did you need something?", "Maybe... I like your voice.", "It's you. Good to see you, [mc_ref]?")
                elif "Kuudere" in char_traits:
                    lines = ("You certainly like to be with me, don't you...", "Seriously... why is it so hard to be serious...?", "I'm listening. What is it?", "Is there something you would like to consult with me? It's alright.")
                elif "Ane" in char_traits:
                    lines = ("If ever you're in trouble... please, let me know.", "What's the matter?", "Ah, it is nice to talk to you again.", "Anything I can do for you?", "Is something's wrong? You can always talk to me.")
                elif "Imouto" in char_traits:
                    lines = ("Hn? What's up? You can tell me anything.", "For the people I like, I will do my best. Promise.")
                elif "Bokukko" in char_traits:
                    lines = ("How's it going? Doing alright?", "Oh, what'cha doing?... What'ya wanna do?", "Ohoh, it's you, [mc_ref] ♪", "Yo! What'cha doin'?", "Whazzup?", "Hey [mc_ref], let's do something!", "Hey, will you talk with me for a bit?", "C'mon, c'mon, put a smile on!", "Um, so hey, you wanna chat?")
                elif "Yandere" in char_traits:
                    lines = ("Eh, what? Do you want to consult with me?", "Huu... You certainly like to be with me, don't you...", "Hm? Something I can do?")
                elif "Kamidere" in char_traits:
                    lines = ("Huhu, You seem like you'd be good for some entertainment ♪", "...Do you want to chat with me that badly?", "Ok. I have chosen to give you some of my valuable time today. Don't make me regret that.", "Good timing. Come on, entertain me.", "I have fairly high expectation of you, [mc_ref] ♪")
                else:
                    lines = ("Hey, how's it going?", "Well, what shall we talk about..?", "What do you want to do?", "Ah, [mc_ref]! Let's talk for a while.", "Hi! Another splendid day today!")
                mood = "happy"
            elif mood in ("happy", "suggestive"):
                if "Impersonal" in char_traits:
                    lines = ("Please talk! I'm all ears.", "Being with you makes me feel comfortable.", "Being with you... calms me.")
                elif "Shy" in char_traits and dice(50):
                    lines = ("I-I'm getting a little bit... used to you, [mc_ref]...", "Hey, am I... do you... Err... nothing. Never mind.", "Being near you calms me down...", "H-Hi...Is it really ok to talk? I don't want to bother you...", "If I am with you, I...  I-it's nothing...")
                elif "Tsundere" in char_traits:
                    lines = ("Come, if you have something to say, say it.", "Why are you so friendly with me, [mc_ref]?", "Are we really getting closer, [mc_ref]?")
                elif "Dandere" in char_traits:
                    lines = ("Did you need something?", "Maybe... I like your voice.", "It's you. Good to see you, [mc_ref]?")
                elif "Kuudere" in char_traits:
                    lines = ("You certainly like to be with me, don't you...", "Seriously... why is it so hard to be serious...?", "I'm listening. What is it?", "Is there something you would like to consult with me? It's alright.")
                elif "Ane" in char_traits:
                    lines = ("If ever you're in trouble... you can always come to me.", "What's the matter? Need some advice?", "Ah... I was just thinking, it'd be so nice to talk to you... Ehehe.", "If there's anything I can do, please tell me, okay?", "You can call on me anytime. And I'll do the same with you.", "If something's wrong, you can always talk to me.")
                elif "Imouto" in char_traits:
                    lines = ("Hn? What's up? You can tell me anything ♪", "For the people I like, I will do my best ♪", "Hi! Tell me, tell me, what'cha doin'?", "Let's have us a chat ♪ Lalala ♪")
                elif "Bokukko" in char_traits:
                    lines = ("How's it going? Doing alright?", "Oh, what'cha doing?... What'ya wanna do?", "Ohoh, it's you, [mc_ref] ♪", "Yo! What'cha doin'?", "Whazzup?", "Hey [mc_ref], let's do something!", "Hey, will you talk with me for a bit?", "C'mon, c'mon, put a smile on!", "Um, so hey, you wanna chat?")
                elif "Yandere" in char_traits:
                    lines = ("Eh, what? Do you want to consult with me?", "Huu... You certainly like to be with me, don't you...", "Hm? Something I can do?")
                elif "Kamidere" in char_traits:
                    lines = ("Huhu, You seem like you'd be good for some entertainment ♪", "...Do you want to chat with me that badly?", "Ok. I have chosen to give you some of my valuable time today. Don't make me regret that.", "Good timing. Come on, entertain me.", "I have fairly high expectation of you, [mc_ref] ♪")
                else:
                    lines = ("Hey, how's it going?", "Well, what shall we talk about..?", "What do you want to do?", "Ah, [mc_ref]! Let's talk for a while.", "Hi! Another splendid day today!")
                mood = "happy"
            elif mood in ("sad", "tired", "in pain"):
                if "Impersonal" in char_traits:
                    lines = ("Talk, I'm listening.", "Uhm... It is good to have you around...", "I hope your presence will help me to calm down.")
                elif "Shy" in char_traits and dice(50):
                    lines = ("I-I'm getting a little bit... used to you, [mc_ref]...", "Hey, am I... do you... Err... nothing. Never mind.", "Being near you calms me down...", "H-Hi...Is it really ok to talk? I don't want to bother you...", "If I am with you, I...  I-it's nothing...")
                elif "Tsundere" in char_traits:
                    lines = ("Come, if you have something to say, say it.", "Don't be so friendly with me, [mc_ref]...", "P-please do not act like we are close to each other, [mc_ref].")
                elif "Dandere" in char_traits:
                    lines = ("Did you need something?", "Maybe... I like your voice.", "It's you. Good to see you, [mc_ref]?")
                elif "Kuudere" in char_traits:
                    lines = ("You certainly like to be with me, don't you...", "Seriously... why is it so hard to be serious...?", "I'm listening. What is it?", "Is there something you would like to consult with me? It's alright.")
                elif "Ane" in char_traits:
                    lines = ("If ever you're in trouble... you can always come to me.", "What's the matter? Need some advice?", "Ah... I was just thinking, it'd be so nice to talk to you... Ehehe.", "If there's anything I can do, please tell me, okay?", "You can call on me anytime. And I'll do the same with you.", "If something's wrong, you can always talk to me.")
                elif "Imouto" in char_traits:
                    lines = ("Yes? What's up?", "Hi! Tell me, what you're doin'?")
                elif "Bokukko" in char_traits:
                    lines = ("How's it going? Doing alright?", "Oh, how are you doing, [mc_ref]?", "Oh, it's you, [mc_ref]!", "Yo! What'cha doin'?", "Hey [mc_ref], how are you doing?", "Hey, will you talk with me for a bit?", "Um, so hey, you wanna chat?")
                elif "Yandere" in char_traits:
                    lines = ("Eh, what? Do you want to consult with me?", "Huu... You certainly like to be with me, don't you...", "Hm? Something I can do?")
                elif "Kamidere" in char_traits:
                    lines = ("You seem like you'd be good for some entertainment.", "...Do you want to chat with me that badly?", "Ok. I have chosen to give you some of my valuable time today. Don't make me regret that.", "Good timing... Come on, entertain me.", "I hope you are going to entertain me, [mc_ref].")
                else:
                    lines = ("Hey, how's it going?", "Well, what shall we talk about..?", "What do you want to do?", "Ah, [mc_ref]! Let's talk for a while.", "Hey, [mc_ref]. Do you want to talk?")
                mood = "uncertain"
            else:
                raise Exception("Mood %s is not implemented for greet_good!" % mood)
            iam.say_line(character, lines, mood)

        @staticmethod
        def greet_good_slave(character):
            """
            Outputs a line when a slave greets the MC with normal disposition
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I'm waiting for your orders, [mc_ref].", "Yes, [mc_ref]. I'm yours to command.", "Another task for me, [mc_ref]? I'll do my best.")
            elif "Shy" in char_traits and dice(50):
                lines = ("I-I'm here, [mc_ref]. What is your wish?", "If I can do something for you... T-then I w-w-will...", "W-w-what is it, [mc_ref]?")
            elif "Tsundere" in char_traits:
                lines = ("Wh-what do you want me to do for you, [mc_ref]?", "Well? You want me to do something, don't you? Speak up already.", "I deal with your weird orders every day, [mc_ref]. You should be grateful.")
            elif "Dandere" in char_traits:
                lines = ("Did you need something, [mc_ref]? I'll do anything.", "May I do something for you, [mc_ref]?", "What is your wish, [mc_ref]?")
            elif "Kuudere" in char_traits:
                lines = ("Another order, [mc_ref]? ", "Of course, [mc_ref]. I'm ready to follow your commands.", "[mc_ref]? Is there something you want me to do?")
            elif "Ane" in char_traits:
                lines = ("What's the matter? Need something from me, [mc_ref]?", "[mc_ref], if there's anything I can do, please tell me, okay?", "You can call on me anytime, [mc_ref] ♪")
            elif "Imouto" in char_traits:
                lines = ("What's up? You can ask me anything, [mc_ref] ♪", "I will do my best for you, [mc_ref]!", "Hm? You have a task for me? Tell me, tell me ♪")
            elif "Bokukko" in char_traits:
                lines = ("Oh, [mc_ref]. What ya wanna me to do?", "Hey [mc_ref], I wanna do something for ya! Any orders?", "Um, you wanna something, [mc_ref]?")
            elif "Yandere" in char_traits:
                lines = ("I'm here for you, [mc_ref].", "Hm? What would you like me to do, [mc_ref]?", "Something I can do, [mc_ref]? Ask me anything ♪")
            elif "Kamidere" in char_traits:
                lines = ("Orders for me, [mc_ref]? Come on, I'm waiting.", "Your orders are absolute, [mc_ref]. Just don't me regret it.", "I suppose I must follow your will, [mc_ref]. Have any wishes at the moment?")
            else:
                lines = ("Can I help you with, [mc_ref]? Just say the word.", "Yes, [mc_ref]? You need my assistance?", "Is there something on your mind, [mc_ref]?")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def greet_neutral(character):
            """
            Outputs a line when the character greets the MC with neutral disposition
            """
            char_traits = character.traits
            mood = character.get_mood_tag(True)
            if mood == "indifferent":
                if "Impersonal" in char_traits:
                    lines = ("State your business.", "Something happened, or what?", "... What's the matter?")
                elif "Shy" in char_traits and dice(50):
                    lines = ("Y-yes, did you call?", "...Y-you want something from me?", "Um... W-what is it?", "Y-yes? Wh-what's going on?", "Wha... what is it...?", "U-Umm... What is it...?", "Y-yes, what do you need?", "C-can I help you...?", "Ye...yes?", "What... is wrong...?", "Wh-what is it...?")
                elif "Kuudere" in char_traits:
                    lines = ("Hmph... what is it?", "What business do you have with me?", "Um, was there something you wanted to say?", "Hm? Yes?")
                elif "Dandere" in char_traits:
                    lines = ("Please make it quick.", "You call?", "...?", "...Want something?", "...Hmm?", "...What is it?", "You have business with me...?")
                elif "Tsundere" in char_traits:
                    lines = ("Hmph. Do you have something to say?", "So, you want something or what?", "What is it?")
                elif "Imouto" in char_traits:
                    lines = ("Ehhe. What is it? ♪", "Muhuhu ♪ Did you want to talk to me?", "Eh? What, what is it?", "Hn. What is it?")
                elif "Ane" in char_traits:
                    lines = ("Well, what do you want to talk about?", "Is there something I can help you with?", "What business do you have with me?", "May I help you?", "...Yes? Did you need me for something?", "Is there... something I can help you with?")
                elif "Kamidere" in char_traits:
                    lines = ("Hm? What? It's not like I have too much time to spend. Yes, that's right. I'm busy.", "...Yes? ...Did you call?", "...Do you want something?", "What is it? I'm busy right now.", "If you have business with me, hurry up and say it.")
                elif "Bokukko" in char_traits:
                    lines = ("Hey-Hey! What do you want?", "Huh? What's up?", "Haa? You got a problem?", "Huh, Is there something you want to know?", "Huh? Do you want something?", "Whazzup?", "Did ya call me?", "Ummm, was there something you wanted to say?")
                elif "Yandere" in char_traits:
                    lines = ("Yes? What is it?", "You want something?", "Make it quick...", "What do you want from me?")
                else:
                    lines = ("...Is there something you need?", "Is there something you would like to ask?", "Is something the matter?", "What do you need from me?", "What is it? If you need something, then say it.", "Yes, what is it?", "...Do you need to talk to me?", "Yes? What do you want?", "...? Is there something on my face?", "Do you need something?", "Did you want to say something?", "You have something to tell me?", "Yes, what is it...?")
            elif mood == "confident":
                if "Impersonal" in char_traits:
                    lines = ("State your business.", "You want something?", "Do you need my help?")
                elif "Kuudere" in char_traits:
                    lines = ("Yes? What do you want?", "What business do you have with me?", "Um, was there something you wanted to say?", "Hm? Yes?")
                elif "Dandere" in char_traits:
                    lines = ("Make it quick.", "You call?", "...?", "...Want something?", "...Hmm?", "...What is it?", "You have business with me...?")
                elif "Tsundere" in char_traits:
                    lines = ("Hmph. I've graced you with my presence, so be thankful.", "So, you want something or what?", "What?")
                elif "Imouto" in char_traits:
                    lines = ("Hey, what is it? ♪", "Muhuhu ♪ Did you need something?", "What, what is it?", "Huhu, what is it?")
                elif "Ane" in char_traits:
                    lines = ("Well, what shall we talk about?", "What business do you have with me?", "May I help you?", "Yes? Did you need me for something?", "Is there something I can help you with?")
                elif "Kamidere" in char_traits:
                    lines = ("Hm? What? It's not like I have too much time to spend. Yes, that's right. I'm busy.", "...Yes? ...Did you call?", "...Do you want something?", "What is it? I'm busy right now.", "If you have business with me, hurry up and say it.")
                elif "Bokukko" in char_traits:
                    lines = ("Hey-Hey! What do you want?", "Huh? What's up?", "Haa? You got a problem?", "Huh, Is there something you want to know?", "Huh? Do you want something?", "Whazzup?", "Did ya call me?", "Ummm, you wanted to say something?")
                elif "Yandere" in char_traits:
                    lines = ("Make it quick, I don't have time for everybody.", "What do you want to say?", "What do you want from me?", "Hurry, I have things to do.")
                else:
                    lines = ("...Is there something you need?", "Is there something you would like to ask?", "Is something the matter?", "What do you need from me?", "What is it? If you need something, then say it.", "Yes, what is it?", "...Do you need to talk to me?", "Yes? What do you want?", "...? Is there something on my face?", "Do you need something?", "Did you want to say something?", "You have something to tell me?", "Yes, what is it...?")
            elif mood == "uncertain":
                if "Impersonal" in char_traits:
                    lines = ("Ehm, what do you want?", "Are you talking to me?")
                elif "Shy" in char_traits:
                    lines = ("Y-yes, did you call?", "...Y-you want something from me?", "Um... W-what is it?", "Y-yes? Wh-what's going on?", "Wha... what is it...?", "U-Umm... What is it...?", "Y-yes, what do you need?", "C-can I help you...?", "Ye...yes?", "What... is wrong...?", "Wh-what is it...?")
                elif "Kuudere" in char_traits:
                    lines = ("Hmph... I wonder if there is any particular purpose to this?", "What business do you have with me?", "Um, was there something you wanted to say?", "Hm? Yes?")
                elif "Dandere" in char_traits:
                    lines = ("If you have business with me, please make it quick.", "You call?", "...?", "...Want something?", "...Hmm?", "...What is it?", "You have business with me...?")
                elif "Tsundere" in char_traits:
                    lines = ("Hmph. Do you want to say something?", "So, you want something?", "Yes? What is it?", "You want something?")
                elif "Imouto" in char_traits:
                    lines = ("Ehehe. What is it?", "Did you need something?", "Eh? What, what is it?", "Huhu, what is it?", "W-What? Did I do something wrong...?")
                elif "Ane" in char_traits:
                    lines = ("Ehm... what shall we talk about?", "What business do you have with me?", "How may I help you?", "...Yes? Did you need me for something?", "Is there... something I can help you with?")
                elif "Kamidere" in char_traits:
                    lines = ("Hm? What? It's not like I have too much time to spend. Yes, that's right. I'm busy.", "...Yes? ...Did you call?", "...Do you want something?", "What is it? I'm busy right now.", "If you have business with me, hurry up and say it.")
                elif "Bokukko" in char_traits:
                    lines = ("Hey-Hey! What do you want?", "Huh? What's up?", "Haa? You got a problem?", "Huh, Is there something you want to know?", "Huh? Do you want something?", "Whazzup?", "Did ya call me?", "Ummm, was there something you wanted to say?")
                elif "Yandere" in char_traits:
                    lines = ("Yes? Do you have something to tell me?", "If you've got something to say, look me in the eyes and say it.", "...I don't recall asking to talk to you, so what is it?", "I don't have any business with you. If you do, make it quick.")
                else:
                    lines = ("...Is there something you need?", "Is there something you would like to ask?", "Is something the matter?", "What do you need from me?", "What is it? If you need something, then say it.", "Yes, what is it?", "...Do you need to talk to me?", "Yes? What do you want?", "...? Is there something on my face?", "Do you need something?", "Did you want to say something?", "You have something to tell me?", "Yes, what is it...?")
            elif mood in ("happy", "suggestive"):
                if "Impersonal" in char_traits:
                    lines = ("State your business.", "Yes, what is it?", "I'm all ears.")
                elif "Kuudere" in char_traits:
                    lines = ("What business do you have with me?", "Um, was there something you wanted to say?", "Hm? Yes?")
                elif "Dandere" in char_traits:
                    lines = ("You call?", "...?", "...Want something?", "...Hmm?", "...What is it?", "You have business with me...?")
                elif "Tsundere" in char_traits:
                    lines = ("Hmph. I've graced you with my presence, so be thankful.", "So, tell me. What do you want?")
                elif "Imouto" in char_traits:
                    lines = ("Ehehe. What is it? ♪", "Muhuhu ♪ Did you need something?", "Huhu, what is it?")
                elif "Ane" in char_traits:
                    lines = ("Well, what shall we talk about?", "Is there something I can help you with...?", "May I help you?", "...Yes? Did you need me for something?", "Is there something I can help you with?")
                elif "Kamidere" in char_traits:
                    lines = ("Hm? What? It's not like I have too much time to spend. Yes, that's right. I'm busy.", "...Yes? ...Did you call?", "...Do you want something?", "What is it? I'm busy right now.", "If you have business with me, hurry up and say it.")
                elif "Bokukko" in char_traits:
                    lines = ("Hey-Hey! What do you want?", "Huh? What's up?", "Haa? You got a problem?", "Huh, Is there something you want to know?", "Huh? Do you want something?", "Whazzup?", "Did ya call me?", "Ummm, was there something you wanted to say?")
                elif "Yandere" in char_traits:
                    lines = ("Yes? What do you want from me?", "You want to tell me something?", "What is it?", "Please, make it quick.")
                else:
                    lines = ("...Is there something you need?", "Is there something you would like to ask?", "Is something the matter?", "What do you need from me?", "What is it? If you need something, then say it.", "Yes, what is it?", "...Do you need to talk to me?", "Yes? What do you want?", "...? Is there something on my face?", "Do you need something?", "Did you want to say something?", "You have something to tell me?", "Yes, what is it...?")

                mood = "happy" if dice(50) else "indifferent"
            elif mood in ("sad", "tired", "in pain"):
                if "Impersonal" in char_traits:
                    lines = ("State your business.", "You're the kind of person who likes pointless conversations, right?", "...Please do not get any closer.")
                elif "Shy" in char_traits and dice(50):
                    lines = ("Y-yes, did you call?", "...Y-you want something from me?", "Um... W-what is it?", "Y-yes? Wh-what's going on?", "Wha... what is it...?", "U-Umm... What is it...?", "Y-yes, what do you need?", "C-can I help you...?", "Ye...yes?", "What... is wrong...?", "Wh-what is it...?")
                elif "Kuudere" in char_traits:
                    lines = ("Hmph... I wonder what do you want from me?", "What business do you have with me?", "Um, was there something you wanted to say?", "Hm? Yes?")
                elif "Dandere" in char_traits:
                    lines = ("If you have business with me, please make it quick.", "You call?", "...?", "...Want something?", "...Hmm?", "...What is it?", "You have business with me...?")
                elif "Tsundere" in char_traits:
                    lines = ("Hmph. What on earth do you want from me?", "So, you want something or what?", "Spit it out already.")
                elif "Imouto" in char_traits:
                    lines = ("Eh? What, what is it?", "Hn, what is it?", "W-What? Did I do something wrong...?")
                elif "Ane" in char_traits:
                    lines = ("Well, what shall we talk about..?", "Is there something I can help you with...?", "What business do you have with me?", "May I help you?", "...Yes? Did you need me for something?", "Is there... something I can help you with?")
                elif "Kamidere" in char_traits:
                    lines = ("Hm? What? It's not like I have too much time to spend. Yes, that's right. I'm busy.", "...Yes? ...Did you call?", "...Do you want something?", "What is it? I'm busy right now.", "If you have business with me, hurry up and say it.")
                elif "Bokukko" in char_traits:
                    lines = ("Hey-Hey! What do you want?", "Huh? What's up?", "Haa? You got a problem?", "Huh, Is there something you want to know?", "Huh? Do you want something?", "Whazzup?", "Did ya call me?", "Ummm, was there something you wanted to say?")
                elif "Yandere" in char_traits:
                    lines = ("Yes? If you have no business here, then do please vacate from my sight.", "If you've got something to say, look me in the eyes and say it.", "...I don't recall asking to talk to you, so what is it?", "I don't have any business with you. If you do, make it quick.")
                else:
                    lines = ("...Is there something you need?", "Is there something you would like to ask?", "Is something the matter?", "What do you need from me?", "What is it? If you need something, then say it.", "Yes, what is it?", "...Do you need to talk to me?", "Yes? What do you want?", "...? Is there something on my face?", "Do you need something?", "Did you want to say something?", "You have something to tell me?", "Yes, what is it...?")
            else:
                raise Exception("Mood %s is not implemented for greet_neutral!" % mood)
            iam.say_line(character, lines, mood)

        @staticmethod
        def greet_neutral_slave(character):
            """
            Outputs a line when the character greets the MC with neutral disposition
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Awaiting input.", "Yes, [mc_ref]?")
            elif "Shy" in char_traits and dice(30):
                lines = ("Y-yes, [mc_ref]", "Y-you want something from me, [mc_ref]?", "Um... Y-yes, [mc_ref]?")
            elif "Kuudere" in char_traits:
                lines = ("I'm here.", "I'm listening, [mc_ref].", "Yes? Was there something you wanted?")
            elif "Dandere" in char_traits:
                lines = ("...[mc_ref]?", "You called, [mc_ref]?", "...What is it, [mc_ref]?")
            elif "Tsundere" in char_traits:
                lines = ("Hmph. Y-yes, [mc_ref].", "Yes, [mc_ref]. You want something or what?", "Well, I'm here, [mc_ref]. Spit it out already.")
            elif "Imouto" in char_traits:
                lines = ("What is it, [mc_ref]?", "Yes, [mc_ref]? Did you need something?", "W-What? Did I do something wrong, [mc_ref]?")
            elif "Ane" in char_traits:
                lines = ("Well, what shall we talk about, [mc_ref]?", "May I help you, [mc_ref]?", "Yes? Do you need me for something?")
            elif "Kamidere" in char_traits:
                lines = ("...Yes? Did you call, [mc_ref]?", "Do you want something?", "If you have an order for me, say it.")
            elif "Bokukko" in char_traits:
                lines = ("What do you want, [mc_ref]?", "Huh? What's up, [mc_ref]?", "Whazzup, [mc_ref]?")
            elif "Yandere" in char_traits:
                lines = ("Is something wrong?", "What is it, [mc_ref]?", "...Spit it out already... Er, yes, [mc_ref]?")
            else:
                lines = ("You called, [mc_ref]?", "Is something the matter, [mc_ref]?", "Yes, what is it, [mc_ref]?")
            iam.say_line(character, lines)

        @staticmethod
        def greet_bad(character):
            """
            Outputs a line when a free character greets the MC with low disposition
            """
            char_traits = character.traits
            mood = character.get_mood_tag(True)
            if mood == "indifferent":
                if "Yandere" in char_traits:
                    mood = "angry"
                    lines = ("Leave. I don't want to talk to you.",  "What a nuisance...", "Why do you keep bothering me?")
                elif "Impersonal" in char_traits:
                    lines = ("State your business and leave.", "I have no interest in you.", "Leave me alone.")
                elif "Shy" in char_traits and dice(50):
                    mood = "uncertain"
                    lines = ("P-please, stay away!", "...D-don't come close to me.", "...S-S-Stay away!", "W-w-w-what do you want!?")
                elif "Dandere" in char_traits:
                    lines = ("What is it? I want to get back to what I was doing...", "I personally dislike you.", "I believe there is nothing we can talk about.")
                elif "Kuudere" in char_traits:
                    lines = ("Hmph, I don't even want to hear it...", "You've got a lot of nerve showing your face around me.", "...I don't think I have reason to talk to you.")
                elif "Tsundere" in char_traits:
                    mood = "angry"
                    lines = ("Leave me alone!", "Go away. ...I said get the hell away from me!", "Listening to you is a waste of my time.")
                elif "Ane" in char_traits:
                    lines = ("What is it? Please leave me alone.", "I don't really feel like talking to you ", "Could you leave me alone?", "There is not a single shred of merit to your existence.")
                elif "Kamidere" in char_traits:
                    mood = "angry"
                    lines = ("It's you again. Don't bother me!", "Could you try to not talk to me, please?  Also, could you not breathe when near me? You're wasting good oxygen.", "Hmph! What an ugly sight.")
                elif "Imouto" in char_traits:
                    mood = "angry"
                    lines = ("You dirty little...",  "Jeez! Bug off already!", "You good-for-nothing...")
                elif "Bokukko" in char_traits:
                    mood = "angry"
                    lines = ("Why are you bothering me?", "You just won't leave me alone, will you...", "Geez, what's now?")
                else:
                    lines = ("...Hey! Could you not get any closer to me, please?", "Sigh... What is it?", "Ah... I-I have stuff to do, so....", "U-Um... right now is a bit, err...")
            elif mood == "confident":
                if "Yandere" in char_traits:
                    lines = ("Leave. I don't want to talk to you.",  "What a nuisance...", "Why do you keep bothering me?")
                elif "Impersonal" in char_traits:
                    lines = ("State your business and leave!", "I have no interest in you!", "Leave me alone!")
                elif "Dandere" in char_traits:
                    lines = ("What is it? I want to get back to what I was doing...", "I personally dislike you.", "I believe there is nothing we can talk about.")
                elif "Kuudere" in char_traits:
                    lines = ("Hmph, I don't even want to hear it...", "You've got a lot of nerve showing your face around me.", "...I don't think I have reason to talk to you.")
                elif "Tsundere" in char_traits:
                    lines = ("Leave me alone!", "Go away. ...I said get the hell away from me!", "Listening to you is a waste of my time.")
                elif "Ane" in char_traits:
                    lines = ("What is it? Leave me alone.", "I don't want to talk to you!", "Could you leave me alone?!")
                elif "Kamidere" in char_traits:
                    lines = ("It's you again. Don't bother me!", "Could you try to not talk to me, please?  Also, could you not breathe when near me? You're wasting good oxygen.", "Hmph! What an ugly sight.")
                elif "Imouto" in char_traits:
                    lines = ("You dirty little...",  "Jeez! Bug off already!", "You good-for-nothing...")
                elif "Bokukko" in char_traits:
                    lines = ("Why are you bothering me?", "You just won't leave me alone, will you...", "Geez, what's now?")
                else:
                    lines = ("...Hey! Could you not get any closer to me, please?", "Sigh... What is it?", "Ah... I-I have stuff to do, so....", "U-Um... right now is a bit, err...")
                mood = "angry"
            elif mood == "uncertain":
                mood = "indifferent"
                if "Yandere" in char_traits:
                    lines = ("Leave. I don't want to talk to you.",  "What a nuisance...", "Why do you keep bothering me?")
                elif "Impersonal" in char_traits:
                    lines = ("State your business and leave.", "I have no interest in you.", "Leave me alone.")
                elif "Shy" in char_traits and dice(50):
                    mood = "uncertain"
                    lines = ("P-please, stay away!", "...D-don't come close to me.", "...S-S-Stay away!", "W-w-w-what do you want!?")
                elif "Dandere" in char_traits:
                    lines = ("What is it? I want to get back to what I was doing...", "I personally dislike you.", "I believe there is nothing we can talk about.")
                elif "Kuudere" in char_traits:
                    lines = ("Hmph, I don't even want to hear it...", "You've got a lot of nerve showing your face around me.", "...I don't think I have reason to talk to you.")
                elif "Tsundere" in char_traits:
                    lines = ("Leave me alone!", "Go away. ...I said get the hell away from me!", "Listening to you is a waste of my time.")
                elif "Ane" in char_traits:
                    lines = ("What is it? Please leave me alone.", "I don't really feel like talking to you ", "Could you leave me alone?", "There is not a single shred of merit to your existence.")
                elif "Kamidere" in char_traits:
                    lines = ("It's you again. Don't bother me!", "Could you try to not talk to me, please?  Also, could you not breathe when near me? You're wasting good oxygen.", "Hmph! What an ugly sight.")
                elif "Imouto" in char_traits:
                    lines = ("Jeez! Bug off already!", "You good-for-nothing...")
                elif "Bokukko" in char_traits:
                    lines = ("Why are you bothering me?", "You just won't leave me alone, will you...", "Geez, what's now?")
                else:
                    lines = ("...Hey! Could you not get any closer to me, please?", "Sigh... What is it?", "Ah... I-I have stuff to do, so....", "U-Um... right now is a bit, err...")
            elif mood in ("happy", "suggestive"):
                if "Yandere" in char_traits:
                    lines = ("Leave. I don't want to talk to you.",  "What a nuisance...", "Why do you keep bothering me?")
                elif "Impersonal" in char_traits:
                    lines = ("State your business and leave.", "I have no interest in you.", "Leave me alone.")
                elif "Dandere" in char_traits:
                    lines = ("What is it? I want to get back to what I was doing...", "I personally dislike you.", "I believe there is nothing we can talk about.")
                elif "Kuudere" in char_traits:
                    lines = ("Hmph, I don't even want to hear it...", "You've got a lot of nerve showing your face around me.", "...I don't think I have reason to talk to you.")
                elif "Tsundere" in char_traits:
                    lines = ("Leave me alone!", "Go away. ...I said get the hell away from me!", "Listening to you is a waste of my time.")
                elif "Ane" in char_traits:
                    lines = ("What is it? Please leave me alone.", "I don't really feel like talking to you ", "Could you leave me alone?", "There is not a single shred of merit to your existence.")
                elif "Kamidere" in char_traits:
                    lines = ("It's you again. Don't bother me!", "Could you try to not talk to me, please?  Also, could you not breathe when near me? You're wasting good oxygen.", "Hmph! What an ugly sight.")
                elif "Imouto" in char_traits:
                    lines = ("You dirty little...",  "Jeez! Bug off already!", "You good-for-nothing...")
                elif "Bokukko" in char_traits:
                    lines = ("Why are you bothering me?", "You just won't leave me alone, will you...", "Geez, what's now?")
                else:
                    lines = ("...Hey! Could you not get any closer to me, please?", "Sigh... What is it?", "Ah... I-I have stuff to do, so....", "U-Um... right now is a bit, err...")
                mood = "angry"
            elif mood in ("sad", "tired", "in pain"):
                if "Yandere" in char_traits:
                    lines = ("Leave. I don't want to talk to you.",  "What a nuisance...", "Why do you keep bothering me?")
                elif "Impersonal" in char_traits:
                    lines = ("State your business and leave.", "I have no interest in you.", "Leave me alone.")
                elif "Shy" in char_traits and dice(50):
                    lines = ("P-please, stay away!", "...D-don't come close to me.", "...S-S-Stay away!", "W-what do you want!?")
                elif "Dandere" in char_traits:
                    lines = ("What is it? I want to get back to what I was doing...", "I personally dislike you.", "I believe there is nothing we can talk about.")
                elif "Kuudere" in char_traits:
                    lines = ("Hmph, I don't even want to hear it...", "You've got a lot of nerve showing your face around me.", "...I don't think I have reason to talk to you.")
                elif "Tsundere" in char_traits:
                    lines = ("Leave me alone!", "Go away. ... Now!", "Listening to you is a waste of my time.")
                elif "Ane" in char_traits:
                    lines = ("What is it? Please leave me alone.", "I don't really feel like talking to you ", "Could you leave me alone?", "There is not a single shred of merit to your existence.")
                elif "Kamidere" in char_traits:
                    lines = ("It's you again. Don't bother me!", "Could you try to not talk to me, please?  Also, could you not breathe when near me? You're wasting good oxygen.", "Hmph! What an ugly sight.")
                elif "Imouto" in char_traits:
                    lines = ("You dirty little...",  "Jeez! Bug off already!", "You good-for-nothing...")
                elif "Bokukko" in char_traits:
                    lines = ("Why are you bothering me?", "You just won't leave me alone, will you...", "Geez, what's now?")
                else:
                    lines = ("...Hey! Could you not get any closer to me, please?", "Sigh... What is it?", "Ah... I-I have stuff to do, so....", "U-Um... right now is a bit, err...")
            else:
                raise Exception("Mood %s is not implemented for greet_bad!" % mood)
            iam.say_line(character, lines, mood)

        @staticmethod
        def greet_bad_slave(character):
            """
            Outputs a line when a slave character greets the MC with low disposition
            """
            char_traits = character.traits
            if "Yandere" in char_traits:
                lines = ("Well? If you don't have orders, I have things to do.", "Could you leave me alone, [mc_ref]?")
            elif "Impersonal" in char_traits:
                lines = ("Orders?..", "..?")
            elif "Shy" in char_traits and dice(50):
                lines = ("P-please don't hurt me, [mc_ref]...", "W-w-w-what do you want, [mc_ref]!?")
            elif "Dandere" in char_traits:
                lines = ("I'm listening, [mc_ref].", "Yes?.")
            elif "Kuudere" in char_traits:
                lines = ("Hmph. Yes?", "...I don't think I have reason to talk to you, [mc_ref]. Give me your orders and leave.")
            elif "Tsundere" in char_traits:
                lines = ("Well? You want something from me or what?", "*sigh*")
            elif "Ane" in char_traits:
                lines = ("What is it? Please leave me alone, [mc_ref]...", "I don't really feel like talking to you, [mc_ref].")
            elif "Kamidere" in char_traits:
                lines = ("You again... <sigh> Yes, [mc_ref]?", "[mc_ref], could you try to not talk to me without a good reason, please?")
            elif "Imouto" in char_traits:
                lines = ("Jeez... I'm listening, [mc_ref].", "You again... Ahem, what is it, [mc_ref]?")
            elif "Bokukko" in char_traits:
                lines = ("Yeah-yeah. I'm here.", "What is it again, [mc_ref]?")
            else:
                lines = ("*sigh* What is it, [mc_ref]?", "...Yes, [mc_ref]. I'm here.")
            iam.say_line(character, lines)

        @staticmethod
        def greet_many(character):
            """
            Outputs a line when the character greets the MC after many encounters
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("..?", "Awaiting input.", "Hmm?")
            elif "Shy" in char_traits and dice(50):
                lines = ("Y-yes?", "Err... what?", "... *blushes*")
            elif "Tsundere" in char_traits:
                lines = ("Well? What is it this time, [mc_ref]?", "You really must have a lot of free time, [mc_ref]...")
            elif "Dandere" in char_traits:
                lines = ("You really enjoy talking, don't you?", "I'm here, [mc_ref].")
            elif "Kuudere" in char_traits:
                lines = ("Hm? What's the matter?", "I'm listening, [mc_ref].")
            elif "Ane" in char_traits:
                lines = ("My, please continue.", "I'm here, [mc_ref]. What can I do for you?")
            elif "Imouto" in char_traits:
                lines = ("[mc_ref]? What's up?", "Yup, I'm listening, [mc_ref].")
            elif "Bokukko" in char_traits:
                lines = ("Whazzup, [mc_ref]?", "Yeah?")
            elif "Yandere" in char_traits:
                lines = ("Eh, what?", "Hm? Something I can do, [mc_ref]?")
            elif "Kamidere" in char_traits:
                lines = ("Yes? What's wrong, [mc_ref]?", "[mc_ref]?")
            else:
                lines = ("What is it, [mc_ref]?", "Yes?")
            iam.say_line(character, lines)

        @staticmethod
        def cat_line(character):
            """
            Outputs a line when the character plays with the MC's cat
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Oh? I'm sorry, cat, I don't have any treats.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("Oh, he's so pretty!", )
            elif "Tsundere" in char_traits:
                lines = ("What a cute cat.... What? N-no, I don't want to pet him at all...", )
            elif "Dandere" in char_traits:
                lines = ("How cute... May I pet him?.. Thanks. *pets him*", )
            elif "Kuudere" in char_traits:
                lines = ("Oh, you have a nice cat there.", )
            elif "Ane" in char_traits:
                lines = ("Well hello there, cutey. *pets him*", )
            elif "Imouto" in char_traits:
                lines = ("Ohh, a kitty! How cute!", )
            elif "Bokukko" in char_traits:
                lines = ("Sup, buddy? Does your master threat you well?", )
            elif "Yandere" in char_traits:
                lines = ("You have a cat? Interesting.", )
            elif "Kamidere" in char_traits:
                lines = ("Fine, fine, I'll pet you, so be thankful. *pets him*", )
            else:
                lines = ("Oh, he's so fluffy and funny, hehe!", )
            iam.say_line(character, lines, "happy", ("note", "reset"))

        @staticmethod
        def blowoff(character):
            """
            Outputs a line when the character is pissed at the MC
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("...Leave.", "I have no interest in you.")
            elif "Yandere" in char_traits:
                lines = ("Stay away. It's your final warning.", "You want to die? If not, go away.")
            elif "Shy" in char_traits and dice(50):
                lines = ("...D-don't come close to me.", "...S-S-Stay away!")
            elif "Dandere" in char_traits:
                lines = ("What is it? I want to get back to what I was doing...", "I personally dislike you.")
            elif "Kuudere" in char_traits:
                lines = ("Hmph, I don't even want to hear it. Go away.", "...I don't think I have reason to talk to you.")
            elif "Tsundere" in char_traits:
                lines = ("Leave me alone!", "Go away. ...I said get the hell away from me!", "...Lowlife.")
            elif "Ane" in char_traits:
                lines = ("Could you leave me alone?", "There is not a single shred of merit to your existence.")
            elif "Kamidere" in char_traits:
                lines = ("You dirty little...", "It's you again. Don't bother me!")
            elif "Imouto" in char_traits:
                lines = ("Jeez! Bug off already!", "You good-for-nothing...")
            elif "Bokukko" in char_traits:
                lines = ("You just won't shut up, will you...", "Geez, you're pissing me off!")
            else:
                lines = ("Leave. I don't want to talk to you.", "Why do you keep bothering me?")
            iam.say_line(character, lines, "angry", ("angry", ))

        @staticmethod
        def prebattle_line(characters):
            """
            Outputs nonrepeatable prebattle lines for provided characters, except hero if s/he was provided.
            """
            said_lines = set()
            for character in characters:
                if character == hero:
                    continue
                char_traits = character.traits
                if "Impersonal" in char_traits:
                    lines = ["Target acquired, initialising battle mode.", "Enemy spotted. Engaging combat.", "Battle phase, initiation. Weapons online.", "Better start running. I'm afraid I can't guarantee your safety.", "Enemy analysis completed. Switching to the combat routine.", "Target locked on. Commencing combat mode."]
                elif "Imouto" in char_traits:
                    lines = ["Ahaha, we'll totally beat you up!", "Behold of my amazing combat techniques, [mc_ref]! ♪", "All our enemies will be punished! ♫", "Activate super duper mega ultra assault mode! ♪", "Huh? Don't they know we're too strong for them?"]
                elif "Dandere" in char_traits:
                    lines = ["Want to fight? We'll make you regret it.", "Let's end this quickly, [mc_ref]. We have many other things to do.", "Of course we'll win.", "This will be over before you know it.", "If something bad happens to the enemy, don't blame me."]
                elif "Tsundere" in char_traits:
                    lines = ["Well-well. It looks like we have some new targets, [mc_ref] ♪", "Hmph! You're about 100 years too early to defeat us!", "We won't go easy on you!", "There's no way you could win!", "[mc_ref], you can stay back if you wish. I'll show you how it's done.", "I won't just defeat you, I'm gonna shatter you!"]
                elif "Kuudere" in char_traits:
                    lines = ["Oh, you dare to stand against us?", "Fine, we accept your challenge. Let's go, [mc_ref].", "Don't worry, [mc_ref]. This battle will be over soon enough.", "Are you prepared to know our power?", "You picked a fight with the wrong girl."]
                elif "Kamidere" in char_traits:
                    lines = ["Get ready, [mc_ref]. We have some lowlife to crash.", "So you want us to teach you some manners, huh?", "You have made a grave error challenging us. Retreat while you can.", "Time to take out the trash.", "You should leave this place and cower in your home. That is the proper course for one so weak.", "You need to be put back in your place."]
                elif "Bokukko" in char_traits:
                    lines = ["Wanna throw hands, huh? Better be ready to catch them!", "I'm gonna beat you silly! Cover me, [mc_ref]!", "You wanna go? Alrighty, eat some of this!", "Time to kick some ass.", "I'm gonna whack you good!", "All right, let's clean this up fast!"]
                elif "Ane" in char_traits:
                    lines = ["Don't worry, [mc_ref]. I'll protect you.", "Can't say I approve of this sort of thing, but we are out of options, [mc_ref].", "Don't feel sorry for them, [mc_ref]. They asked for it.", "We mustn't let our guard down, [mc_ref]."]
                elif "Yandere" in char_traits:
                    lines = ["Please stand aside, [mc_ref]. Or you'll get blood on you...", "Do not worry. The nothingness is gentle ♪", "Here comes the hurt!", "This could get a little rough... Because I like it rough ♫", "Mind if I go a little nuts, [mc_ref]?"]
                else:
                    lines = ["I suppose we have to use force, [mc_ref]. I'll cover you.", "Alright then. If you want a fight, we'll give it to you!", "Ok, let's settle this.", "I'll fight to my last breath!"]
                result = random.sample(set(lines).difference(said_lines), 1)[0]
                said_lines.add(result)
                result = result.replace("[mc_ref]", character.mc_ref)
                character.override_portrait("portrait", "confident")
                character.say(result)
                character.restore_portrait()
    
        @staticmethod
        def eating_line(characters):
            """
            Outputs nonrepeatable lines during eating for provided characters, except hero if s/he was provided.
            """
            said_lines = set()
            for character in characters:
                if character == hero:
                    continue
                char_traits = character.traits
                if "Impersonal" in char_traits:
                    lines = ["It's all sticky from the sauce... Nn... *chu* Mm... *slurp*", "Nn... mm... Delicious...", "That looks tasty... *slurp*"]
                elif "Shy" in char_traits and dice(50):
                    lines = ["That looks so good! Ah! That one looks good too... Aww, I can't decide...", "Hehe, sweet tea is so calming, isn't it?", "Uhm, w-were you going to eat that? Er... Y-yes, I'll eat it..."]
                elif "Imouto" in char_traits:
                    lines = ["Custard here and chocolate here. Looks delicious, doesn't it? ♪", "So many sweets! What should I start with? ♪", "Oh, that looks yummy... Diggin' in! Nom!"]
                elif "Dandere" in char_traits:
                    lines = ["*munch munch*... Huh? You want some too? Here.", "Omelette rolls are so sweet and sticky...", "Munch munch... Sugar intake is important.", "Thanks for the food... *munch*"]
                elif "Tsundere" in char_traits:
                    lines = ["Ah, I'm tired from eating too much...", "How long do you plan on staring at my lunch? I'm not sharing any.", "Lately, I am worrying quite a bit about calories... But I just can't help myself... ugh..."]
                elif "Kuudere" in char_traits:
                    lines = ["Mmm, this is actually pretty good.", "They don't have any teacakes today..? A pity.", "You've got a good appetite. It's refreshing to see.", "I don't need any... Well, if you insist... *aaaah*..."]
                elif "Kamidere" in char_traits:
                    lines = ["OK, say ah~n... Yeah right, like I would ever do such a thing.", "Can't you just be quiet and eat? It's improper.", "Don't talk to me when I'm eating."]
                elif "Bokukko" in char_traits:
                    lines = ["Hm, which one tastes better... I wonder...", "Nom nom... Mmm, delicious ♪ Back to full health ♪", "Mm, delicious meat. The meatiest of meats. Om nom.", "Let's dig in! Ehehe, egg omelet, egg omelet ♪"]
                elif "Ane" in char_traits:
                    lines = ["This kind of food is good for your health, you know? It'll fill you with lots of energy ♪", "You don't get to be picky. Come, say aaa... ♪", "Now, why don't we have an enjoyable meal?"]
                elif "Yandere" in char_traits:
                    lines = ["...Here, have this too. I'm finished.", "Mmm... Vanilla milkshakes are the best ♪", "I've been gaining weight, so I'm holding back today... Haah...", "Just go ahead and order whatever. I'll leave it up to you."]
                else:
                    lines = ["This place's tea and cake is amazing. The tarts are good, too.", "Ah, that looks yummy ♪", "Let's eaaaat! But, what should I eat first? Hmm..."]
                result = random.sample(set(lines).difference(said_lines), 1)[0]
                said_lines.add(result)
                result = result.replace("[mc_ref]", character.mc_ref)
                character.override_portrait("portrait", "indifferent", add_mood=False)
                character.say(result)
                character.restore_portrait()

        @staticmethod
        def eating_propose(character):
            """
            Outputs a line when a character proposes to eat something
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Let's have some tea.", "Hey, I was thinking about grabbing a bite.", "How about lunch?")
            elif "Shy" in char_traits and dice(50):
                lines = ("H-hey, how about a cup of tea?", "I was just thinking about eating something...", "It's lunch time... S-so maybe we...")
            elif "Imouto" in char_traits:
                lines = ("I really want some sweets ♪ C'mon!", "My tummy's growling. Wanna grab a bite?", "Woo! Lunch time, lunch time! Hurry!")
            elif "Dandere" in char_traits:
                lines = ("Snack time?", "Want to have a snack?", "Lunch..?")
            elif "Tsundere" in char_traits:
                lines = ("C-come on, invite me for tea or something.", "Hey... Do you want to grab some food? O-Or something?", "Y-you're going to join me for lunch... okay?")
            elif "Kuudere" in char_traits:
                lines = ("Would you like to have some tea together?", "Let's get something to eat.", "Are you hungry? How about lunch?")
            elif "Kamidere" in char_traits:
                lines = ("I think it's time for tea.", "Are you hungry? I was thinking about eating.", "Let's eat, I'm hungry.")
            elif "Bokukko" in char_traits:
                lines = ("Hey, let's have a snack, alright?", "Let's eat something! I'm starved!", "It's time to eat! Come on, let's go!")
            elif "Ane" in char_traits:
                lines = ("Shall we sip some drinks and take it easy?", "What would you say to a cup of tea with me?", "Would you like to join me for lunch?")
            elif "Yandere" in char_traits:
                lines = ("Do you want to take a tea break?", "Hey, aren't you hungry? Want to go get something to eat?", "If you'd like, we could have lunch?")
            else:
                lines = ("Hey, you got some snacks or something? I'm kinda hungry.", "Shall we take a break? I'm hungry.", "Aaah, I'm hungry... What about you?")
            iam.say_line(character, lines)

        @staticmethod
        def icecream_propose(character):
            """
            Outputs a line when a character proposes to eat an icecream
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Let's have an icecream.", "Hey, I was thinking about having an icecream.", "How about an icecream?")
            elif "Shy" in char_traits and dice(50):
                lines = ("H-hey, how about an icecream?", "I was just thinking about having an icecream...", "It's so hot... S-so maybe we...")
            elif "Imouto" in char_traits:
                lines = ("I really want some sweets ♪ C'mon!", "I could really have an icecream now. Wanna join?", "Woo! Icecream, icecream! Hurry!")
            elif "Dandere" in char_traits:
                lines = ("Icecream?", "Want to have an icecream?", "Icecream..?")
            elif "Tsundere" in char_traits:
                lines = ("C-come on, invite me for an icecream or something.", "Hey... Do you want to have an icecream? O-Or later?", "Y-you're going to join me for an icecream... okay?")
            elif "Kuudere" in char_traits:
                lines = ("Would you like to have some icecream together?", "Let's get an icecream.", "Is'nt it so hot? How about an icecream?")
            elif "Kamidere" in char_traits:
                lines = ("I think it's time for an icecream.", "Let's have an icecream, I'm really longing for it.")
            elif "Bokukko" in char_traits:
                lines = ("Hey, let's have an icecream, alright?", "Let's eat an icecream! I haven't had one in ages!", "It's time to have an icecream! Come on, let's go!")
            elif "Ane" in char_traits:
                lines = ("Shall we have an icecream and enjoy the sun?", "What would you say to an icecream with me?", "Would you like to join me for an icecream?")
            elif "Yandere" in char_traits:
                lines = ("Do you want to have an icecream?", "Hey, aren't you sweating on the sun? Want to have an icecream?", "If you'd like, we could have an icecream?")
            else:
                lines = ("Hey, you got something to cool down? It is kinda hot on the sun.", "Shall we take a break? I want some icecream.", "Aaah, I want an icecream... What about you?")
            iam.say_line(character, lines)

        @staticmethod
        def accept_invite(character):
            """
            Output line when a character accepts the invitation of the hero to have some ice-cream
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Alright. Let's go.", "That is a good idea.", "On my way.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Oh, ok... I-I can join you.", "Er, um... Ok, why not?")
            elif "Tsundere" in char_traits:
                lines = ("Alright then. If that is what you want.", "Yes, I might join you there.",)
            elif "Kuudere" in char_traits:
                lines = ("Well... since you offered... *smiles*", "That's very kind of you. I accept your proposal.", "Oh, that is a pretty good idea. Let's go!")
            elif "Yandere" in char_traits:
                lines = ("I can't say no to such a nice offer. <blush>", "I don't mind if you want to. *smiles*")
            elif "Dandere" in char_traits:
                lines = ("...Thanks for the invitation.", "Okay... Thanks.")
            elif "Ane" in char_traits:
                lines = ("Oh my, of course ♪", "Trying to earn points, huh? <giggle>", "Oh, yes. Gladly. *smiles*")
            elif "Imouto" in char_traits:
                lines = ("Oh! Can't wait! <giggles>", "Hehehe, why not? If you really want to.")
            elif "Kamidere" in char_traits:
                lines = ("I will accept your proposal; as a first-class lady.", "<Laughs> Ok, if you insist.", "Yes, I'm not going to refuse your proposal.")
            elif "Bokukko" in char_traits:
                lines = ("Oh? Alright. Now?", "Yeah, that is fine with me.")
            else:
                lines = ("Thanks for the offer! I accept it.", "Yes, I accept it.", "Great! Let's go ♪", "Well, I won't say no to that ♪")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def icecream_line(character):
            """
            Outputs line when a character is out with the hero to eat an ice-cream
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Delicious. This lucuma is really great.", "That pistachio looks tasty.")
            elif "Shy" in char_traits and dice(50):
                lines = ("That looks so good! Ah! That one looks good too... Aww, I can't decide...", "Uhm, which one... which one?... Neapolitan it is...", "Maybe I should try their cookie dough ice cream...")
            elif "Imouto" in char_traits:
                lines = ("Ohoh, they have spumoni again! Looks delicious, doesn't it? ♪", "Oh, that spumoni looks yummy... Nom...", "Wha.. I have try that tutti frutti! ♪", "Hehe, what a nice tutti frutti ♪")
            elif "Dandere" in char_traits:
                lines = ("Mmm... their maple ice cream is amazing...", "Hehe, this grape ice cream looks really fancy ♪", "*slurp* Strawberry is yummy...")
            elif "Tsundere" in char_traits:
                lines = ("Ah, I think I stick to mango today.", "Let's have this durian.", "Mint chocolate is the best composition of all ♪")
            elif "Kuudere" in char_traits:
                lines = ("Mmm, vanilla is always a safe bet.", "Their chocolate is really tasty today ♪", "Mmm... You can never go wrong if you choose cherry, hehe.")
            elif "Kamidere" in char_traits:
                lines = ("OK, I really have to try this Moon Mist!", "Silence! I want to enjoy the taste of the Blue Moon.", "You do not know what good is if you haven't tried the Blue Moon.")
            elif "Bokukko" in char_traits:
                lines = ("Mmm, delicious ♪ Want to try this halva?", "Nom nom... coconut is the best ♪")
            elif "Ane" in char_traits:
                lines = ("Mmm... I longed to have this stracciatella for so long! ♪", "Do you want to try this mamey? It is really delicious.", "The green tea flavour works wonders in ice cream as well! ♪")
            elif "Yandere" in char_traits:
                lines = ("Mmm... Yes. I knew their teaberry is really fine.", "You should try this teaberry as well!", "Mmm... the lemon ice cream is tasty ♪")
            else:
                lines = ("Nom... yammy... Tiger tail is yammy as always ♪", "Mmm... Ah... This grape nut is awesome ♪", "Hehe, vanilla is always pretty good ♪")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def cafe_line(character):
            """
            Outputs line when a character is out with the hero to drink a cafe
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("One Frappuccino please, the usual.", "Can I have an Affogate, please?... Thanks.")
            elif "Shy" in char_traits and dice(50):
                lines = ("I... I think I'll just have a Galão.", "Uhm, I would like a Bicerin, please...")
            elif "Imouto" in char_traits:
                lines = ("Uhuh, a Mocha. Yummy ♪", "Oh, can I have a bit more chocolate on my Mocha? Thanks ♪", "Hehe, this Eiskaffee is sooo sweet! Yupie ♪")
            elif "Dandere" in char_traits:
                lines = ("Uhm... A caffe latte, please...", "I just want a cafe au lait a day and I'm content.", "*slurp* ... Mmm... *slurp*")
            elif "Tsundere" in char_traits:
                lines = ("A Cafe Bombon, please! Not stirred!", "Cafè melange please, with just a bit of cream on the top!")
            elif "Kuudere" in char_traits:
                lines = ("I would like to have a Cubano, please!", "Sometimes a simple Breve is all you need, right? ♪")
            elif "Kamidere" in char_traits:
                lines = ("I always wonder where they get their Kopi Luwak from.", "Nothing is comparable to their Kopi Luwak. Mmm...", "Uhh, too much milk in this Macchiato, but at least its smell is OK *inhales*", "I want a Caffe Macchiato, please!")
            elif "Bokukko" in char_traits:
                lines = ("*slurp* Mmm... Nothing beats an Espresso ♪", "The smell of this Turkish Coffee is amazing ♪")
            elif "Ane" in char_traits:
                lines = ("*inhales* Mmm... Corretto, my favorite! ♪", "Mmm... I could spend a day next to a Carajillo ♪")
            elif "Yandere" in char_traits:
                lines = ("Mmm... This Yuanyang is perfect.", "Their Cortado could use a bit more milk, but it is tasty anyway.")
            else:
                lines = ("Mmm.. Perfect. All I wanted is this Americano... ♪", "*slurp* Uh, this Cappuccino is still hot...")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def study_line_learn(character):
            """
            Outputs line when a character learned something from the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Understood. It all makes sense now.", )
            elif "Shy" in char_traits:
                lines = ("Ah...that's...really easy to understand... You're amazing...", )
            elif "Imouto" in char_traits:
                lines = ("...Wow, that really helped, it's a lot easier to understand now!", )
            elif "Dandere" in char_traits:
                lines = ("I see... Thanks for the explanation.", )
            elif "Tsundere" in char_traits:
                lines = ("...It pains me to admit it, but I understand now.", )
            elif "Kuudere" in char_traits:
                lines = ("That's much easier to understand. You have my thanks.", )
            elif "Kamidere" in char_traits:
                lines = ("...Don't get all full of yourself because you can teach a little.", )
            elif "Bokukko" in char_traits:
                lines = ("Whoa! I've got it now! Even I can understand it now!", )
            elif "Ane" in char_traits:
                lines = ("Just like I thought, you make it seem so much easier to understand.", )
            elif "Yandere" in char_traits:
                lines = ("Oh, I see now... That will be helpful.", )
            else:
                lines = ("Ah, I see... I think I kinda get it now ♪", )
            iam.say_line(character, lines, "happy")

        @staticmethod
        def study_line_teach(character):
            """
            Outputs line when a character taught something to the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Do you see? It makes sense now, right?", "Okay, now you learned something new.")
            elif "Shy" in char_traits:
                lines = ("Alright... I-I hope I could help...", "Em... Is it clear now?", "I... don't know how to explain it better, but this is it...")
            elif "Imouto" in char_traits:
                lines = ("... Wow, I'm really glad I could teach you something! ♪", "Hehe, I could teach you something as well ♪")
            elif "Dandere" in char_traits:
                lines = ("You see? I hope it is clear now.", )
            elif "Tsundere" in char_traits:
                lines = ("... Just remember what I told you, and it will be fine.", "It is quite obvious, don't you think?")
            elif "Kuudere" in char_traits:
                lines = ("Do you see? It is quite reasonable, if you think about it.", )
            elif "Kamidere" in char_traits:
                lines = ("You can always learn from me if you want to.", )
            elif "Bokukko" in char_traits:
                lines = ("I hope you get it now, because I do not know how else I could explain it to you.", )
            elif "Ane" in char_traits:
                lines = ("Oh, I really hope I could help you out here.", "I'm glad that I could show you something new.")
            elif "Yandere" in char_traits:
                lines = ("Got it now? Or should we go through it again?", )
            else:
                lines = ("It is nice to share my knowledge with someone.", )
            iam.say_line(character, lines, "confident")

        @staticmethod
        def refuse_invite_too_many(character):
            """
            Outputs a line when a character refuses the invitation of the hero due to too many attempt
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Nah, not now.", "Maybe later, ok?", "No, that would be too much.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I-I think I can do it right now...", "It's... I.. I don't want, sorry...")
            elif "Tsundere" in char_traits:
                lines = ("Stop! That's enough!", "What's wrong with you? I can't spend my whole life with you...")
            elif "Kuudere" in char_traits:
                lines = ("What do you think you're doing? We went out not long ago.", "Stop it. I have enough for the moment.")
            elif "Yandere" in char_traits:
                lines = ("Don't you think that it is enough for the moment?", "Huh? Another invitation?")
            elif "Dandere" in char_traits:
                lines = ("Another invitation? Why? ...", "One more invitation? Why?")
            elif "Ane" in char_traits:
                lines = ("I appreciate the thought, but that was enough for the moment.", "Oh, but we went out together not long ago!")
            elif "Imouto" in char_traits:
                lines = ("Wha? I have enough!", "Ugh. I have more than enough. Boring!")
            elif "Kamidere" in char_traits:
                lines = ("I won't stop you if you want to go there, but I have better things to do now.", "Pfft. Another invitation? Isn't it boring?")
            elif "Bokukko" in char_traits:
                lines = ("C'mon, really? Can't you come up with a better idea?", "Can't you think of something else?")
            else:
                lines = ("Sorry, I don't want to go out now.", "It's enough for the moment, don't you think?")
            iam.say_line(character, lines)

        @staticmethod
        def refuse_invite_any(character):
            """
            Outputs a line when a character refuses the invitation of the hero without giving a reason
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I can not accept your offer.", "I have to refuse your offer.", "Thanks, but no thanks.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I-I think I can not do it right now...", "It's... I.. I don't want, sorry...")
            elif "Tsundere" in char_traits:
                lines = ("No, that is not for me!", "I have to refuse that offer.")
            elif "Kuudere" in char_traits:
                lines = ("I can't do it.", "No, this is not the right time.")
            elif "Yandere" in char_traits:
                lines = ("I have to refuse your offer.", "This offer does not fit for me, so I have to refuse it.", "I have to refuse your invitation.")
            elif "Dandere" in char_traits:
                lines = ("Ehrm, I don't want to.", "I-I... Sorry... Not now.")
            elif "Ane" in char_traits:
                lines = ("I appreciate the thought, but I can not accept your invitation.", "Oh, but this is not the right time for me.")
            elif "Imouto" in char_traits:
                lines = ("Wha? I can't!", "Ugh. I can't do it right now.")
            elif "Kamidere" in char_traits:
                lines = ("I can not accept your offer.", "I have to refuse your offer.", "I have to refuse your invitation.")
            elif "Bokukko" in char_traits:
                lines = ("No can do, sorry...", "Please, invite someone else. I can't go right now.")
            else:
                lines = ("Sorry, bad timing.", "Does not work for me at the moment...")
            iam.say_line(character, lines)

        @staticmethod
        def invite_pay(character):
            """
            Outputs line when a character pays instead of the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I guess it is me, who has to pay.", "Well, if you can't pay I take it over...")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I-I think I can help you out to pay...", "It's... I.. I have the money if you don't...")
            elif "Tsundere" in char_traits:
                lines = ("Since you obviously can't pay, I take the lead now!", "Next time bring more money, now I have to pay!")
            elif "Kuudere" in char_traits:
                lines = ("I guess it is only me who can think in advance. Next time bring money if you invite someone!", "Right. So now I have to pay. You just wanted to be invited, right?")
            elif "Yandere" in char_traits:
                lines = ("You can't be serious, inviting someone with an empty wallet!", "It is kinda low to invite someone without having the means to actually pay.", "I'm going to pay since we are already here now, but it is better if it won't happen again.")
            elif "Dandere" in char_traits:
                lines = ("Ehrm, I have the necessary money to pay.", "I-I think it is better if I pay now.")
            elif "Ane" in char_traits:
                lines = ("Oh, my... Now I have to cover the cost of your invitation.", "Oh, don't worry, I can pay this time.")
            elif "Imouto" in char_traits:
                lines = ("Wha? You can't pay? You leecher!", "Ugh. If you can't pay, I guess I have no other choice...")
            elif "Kamidere" in char_traits:
                lines = ("Fine! I pay. This time.", "I guess I have no other choice than to pay.")
            elif "Bokukko" in char_traits:
                lines = ("That is just great.... Ok-ok, I pay...", "Good job, obviously now I have to pay...")
            else:
                lines = ("Just leave it to me. I can pay.", "Don't mind! I can pay this time.")
            iam.say_line(character, lines)

        @staticmethod
        def invite_not_pay(character):
            """
            Outputs line when a character refuses to pay instead of the hero
            """
            char_traits = character.traits
            mood = "angry"
            if "Impersonal" in char_traits:
                lines = ("I'm not going to pay for your bad decisions.", "I hope you do not expect me to pay...")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I-I think it better to leave now...", "It's... I.. I have to leave now...")
                mood = "sad"
            elif "Tsundere" in char_traits:
                lines = ("Did you expect me to pay? You can forget about that!", "You really wanted me to pay? You are out of your mind!")
            elif "Kuudere" in char_traits:
                lines = ("You must be joking. Who is going to pay?", "You think they just give it for free?")
            elif "Yandere" in char_traits:
                lines = ("I'm not going to help you out this time!", "This is really stupid! No gold, hah... Let's just leave!")
            elif "Dandere" in char_traits:
                lines = ("Ehrm, no money? We need to skip this now...", "It is... time to go, I guess...")
            elif "Ane" in char_traits:
                lines = ("My... I can't help you now, so why don't we just leave?", "Oh, I guess without money we have to change our plan.")
                mood = "indifferent"
            elif "Imouto" in char_traits:
                lines = ("Wha? You can't pay? Me neither!", "Ugh. That is it then. Bring more gold next time!")
            elif "Kamidere" in char_traits:
                lines = ("Please, don't even try to excuse yourself! Let's just leave and next time bring money if you invite someone.", "You left your wallet at home, right? Ehh...")
            elif "Bokukko" in char_traits:
                lines = ("It is kinda stupid to walk in here with an empty wallet.", "I'm not going to pay and you knew it, right?", "That is then! If you can't pay...")
            else:
                lines = ("I think we have to go now, since your wallet is empty...", "I guess, it is time to find something less expensive.")
                mood = "indifferent"
            iam.say_line(character, lines, mood)

        @staticmethod
        def refuse_to_give(character):
            """
            Output line when a character denies to give money or to access to an item.
            """
            global block_say
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Denied.", "It won't happen.")
            elif "Shy" in char_traits and dice(50):
                lines = ("S-sorry, I can't do it...", "Um, that's... not something I'm willing to do.")
            elif "Tsundere" in char_traits:
                lines = ("Yeah, right. Don't even think about it, smartass.", "Not in a thousand years.")
            elif "Kuudere" in char_traits:
                lines = ("I don't think so.", "I don't see the point.")
            elif "Yandere" in char_traits:
                lines = ("I don't feel like it. Bother someone else.", "Right. As if I'm going to listen you.")
            elif "Dandere" in char_traits:
                lines = ("No. Go away.", "I don't want to.")
            elif "Ane" in char_traits:
                lines = ("Unfortunately, I must refuse.", "No, I believe it would be highly unwise.")
            elif "Imouto" in char_traits:
                lines = ("Whaat?! Why should I do that?!", "No way!")
            elif "Kamidere" in char_traits:
                lines = ("I refuse. Get lost.", "Know your place, fool.")
            elif "Bokukko" in char_traits:
                lines = ("Not gonna happen.", "Nah, don't wanna.")
            else:
                lines = ("I think this is not a good idea.", "Why should I do it?")
            block_say = True
            iam.say_line(character, lines)
            block_say = False

        @staticmethod
        def items_deny_access(character):
            """
            Output line when a character denies access to an item.
            """
            global block_say
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Denied. It belongs only to me.", "You are not authorised to dispose of my property.")
            elif "Shy" in char_traits and dice(50):
                lines = ("W... what are you doing? It's not yours...", "Um, could you maybe stop touching my things, please?")
            elif "Dandere" in char_traits:
                lines = ("Don't touch my stuff without permission.", "I'm not giving it away.")
            elif "Kuudere" in char_traits:
                lines = ("Would you like fries with that?", "Perhaps you would like me to give you the key to my flat where I keep my money as well?")
            elif "Yandere" in char_traits:
                lines = ("Please refrain from touching my property.", "What do you think you doing with my belongings?")
            elif "Tsundere" in char_traits:
                lines = ("Like hell am I giving away!", "Hey, hands off!")
            elif "Imouto" in char_traits:
                lines = ("No way! Go get your own!", "Don't be mean! It's mine!")
            elif "Bokukko" in char_traits:
                lines = ("Hey, why do ya take my stuff?", "Not gonna happen. It's mine alone.")
            elif "Kamidere" in char_traits:
                lines = ("And what makes you think I will allow anyone to take my stuff?", "Refrain from disposing of my property unless I say otherwise.")
            elif "Ane" in char_traits:
                lines = ("Please, don't touch it. Thanks.", "Excuse me, I do not wish to part with it.")
            else:
                lines = ("Hey, I need this too, you know.", "Eh? Can't you just buy your own?")
            block_say = True
            iam.say_line(character, lines)
            block_say = False

        @staticmethod
        def items_deny_bad_item(character):
            """
            Output line when a character does not want to equip a bad item.
            """
            global block_say
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I don't need it. It's useless.", "I' afraid I'm incompatible with this thing.")
            elif "Shy" in char_traits and dice(50):
                lines = ("It's... for me? Um... I don't really need it...", "It's a... what is this, exactly? ...I see. Sorry, but...")
            elif "Tsundere" in char_traits:
                lines = ("Who would want this crap?", "Whaaat? What am I supposed to do with this?!")
            elif "Kuudere" in char_traits:
                lines = ("And what should I do with this... thing?", "You know, someone like me has no use for this.")
            elif "Yandere" in char_traits:
                lines = ("What were you thinking? This is awful!", "This is absolute junk. I'm offended.")
            elif "Dandere" in char_traits:
                lines = ("I don't want it.", "This item gives me a terrible feeling.")
            elif "Ane" in char_traits:
                lines = ("Not to be ungrateful, but... I really don't like this.", "This is... interesting choice, but I think I'll pass.")
            elif "Imouto" in char_traits:
                lines = ("Hey! I don't want this!", "Yuck, what is this? Looks terrible...")
            elif "Kamidere" in char_traits:
                lines = ("This junk isn't useful at all.", "Please refrain from bothering me with this in the future.")
            elif "Bokukko" in char_traits:
                lines = ("Hey, is this a joke? What am I supposed to do with this?", "Get this thing away from me.")
            else:
                lines = ("Thanks, but I don't like these kinds of things.", "I'm sorry, but I absolutely hate this.")
            block_say = True
            iam.say_line(character, lines, overlay_args=("sweat", "reset"))
            block_say = False

        @staticmethod
        def items_deny_good_item(character):
            """
            Output line when a character does not want to unequip a good item.
            """
            global block_say
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I don't want to part with it. I like it very much.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("It's... necessary for me. Um... I really need it...", )
            elif "Tsundere" in char_traits:
                lines = ("Why would I put it away?", "Whaaat? This item is really necessary for me!")
            elif "Kuudere" in char_traits:
                lines = ("And why should I put this away?", "You know, someone like me has a real use for this.")
            elif "Yandere" in char_traits:
                lines = ("What were you thinking? I still need this!", "Hey, I still want to use this!")
            elif "Dandere" in char_traits:
                lines = ("I'm still using this!", "This item is bound to me.")
            elif "Ane" in char_traits:
                lines = ("Not to be ungrateful, but... I really need this.", "Sorry, but I think this could still be useful to me.")
            elif "Imouto" in char_traits:
                lines = ("Hey! I don't want to part with this!", "Yuck. I'm still using this, you know?")
            elif "Kamidere" in char_traits:
                lines = ("This item is still useful to me.", "Please refrain from bothering me with this in the future.")
            elif "Bokukko" in char_traits:
                lines = ("Hey, is this a joke? What am I supposed to do without this?", )
            else:
                lines = ("I'm sorry, but I absolutely need this.", )
            block_say = True
            iam.say_line(character, lines)
            block_say = False

        @staticmethod
        def items_deny_equip_bad(character):
            """
            Output line when a character really does not want to (un)equip an item.
            """
            global block_say
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Access denied.", "You are not authorised to make such decisions.")
            elif "Shy" in char_traits:
                lines = ("Um... I prefer to leave it for the moment.", )
            elif "Dandere" in char_traits:
                lines = ("I'm fine as it is.", "I don't feel like it.")
            elif "Kuudere" in char_traits:
                lines = ("I'm perfectly fine without your advices, thank you very much.", "I can handle myself without your intervention.")
            elif "Yandere" in char_traits:
                lines = ("I don't think we are close enough to even discuss such things.", "It's not for you to decide.")
            elif "Tsundere" in char_traits:
                lines = ("I can manage my things without your help!", "Hey, don't just decide something like that on your own!")
            elif "Imouto" in char_traits:
                lines = ("You think I'm too stupid to take care of myself?", "Hey! Don't tell me what to do, I'm not a kid!")
            elif "Bokukko" in char_traits:
                lines = ("Hey, aren't you too cocky tellin' me what to do?", )
            elif "Kamidere" in char_traits:
                lines = ("You think I just will agree to do anything for you?", "If you wish to control someone's life, get yourself a pretty slave.")
            elif "Ane" in char_traits:
                lines = ("Thanks for the proposition, but I'm fine.", "I find this quite inappropriate.")
            else:
                lines = ("No, I don't want to.", "Eh? I think I'm doing great already.", "Don't worry, I think I can manage my stuff.")
            block_say = True
            iam.say_line(character, lines)
            block_say = False

        @staticmethod
        def items_deny_equip_neutral(character):
            """
            Output line when a character just does not want to (un)equip an item.
            """
            global block_say
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I do not think that is a good idea.", "No can do, sorry.")
            elif "Shy" in char_traits:
                lines = ("M-maybe another time?", "Um... I'll think about it.")
            elif "Dandere" in char_traits:
                lines = ("Sorry, but I have to refuse your proposal.", "I don't want that, sorry.")
            elif "Kuudere" in char_traits:
                lines = ("For the moment, I prefer to follow my own instinct on such matters.", "I don't think I need advice right now...")
            elif "Yandere" in char_traits:
                lines = ("I prefer to decide on my own what to wear.", "It's better to keep it as it is for the moment.")
            elif "Tsundere" in char_traits:
                lines = ("I can manage my things just fine, thanks!", "I think I'm can decide something like that on my own!")
            elif "Imouto" in char_traits:
                lines = ("Please, let me decide what to wear!", "Just leave it to me, I'm an adult!")
            elif "Bokukko" in char_traits:
                lines = ("Nah, not in the mood for this stuff...", )
            elif "Kamidere" in char_traits:
                lines = ("I don't think I can accept that.", "Let's just leave it for the moment.")
            elif "Ane" in char_traits:
                lines = ("Thanks for the proposition, but I'm fine.", "Sorry, but I would rather not.")
            else:
                lines = ("Sorry, but I don't want to.", "Thanks for the care, but I have to refuse it.")
            block_say = True
            iam.say_line(character, lines)
            block_say = False

        @staticmethod
        def good_goodbye(character):
            """
            Output line when a character leaves with good disposition
            """
            global block_say
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("See you.", )
            elif "Shy" in char_traits:
                lines = ("S-see you later.", )
            elif "Imouto" in char_traits:
                lines = ("Bye-bye♪", )
            elif "Dandere" in char_traits:
                lines = ("Goodbye then...", )
            elif "Tsundere" in char_traits:
                lines = ("Fine, see you later.", )
            elif "Kuudere" in char_traits:
                lines = ("Alright, later...", )
            elif "Kamidere" in char_traits:
                lines = ("Well, see you then.", )
            elif "Bokukko" in char_traits:
                lines = ("'kay, see you around!", )
            elif "Ane" in char_traits:
                lines = ("Goodbye. If you'll excuse me, then...", )
            elif "Yandere" in char_traits:
                lines = ("Ok, see you next time.", )
            else:
                lines = ("Alright, see you.", )
            block_say = True
            iam.say_line(character, lines)
            block_say = False

        @staticmethod
        def bad_goodbye(character):
            """
            Output line when a character leaves with bad disposition
            """
            global block_say
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("This is farewell. I can't stand you any longer.", "It's over. I'm leaving. I never want to see you again.")
            elif "Shy" in char_traits:
                lines = ("I-I'm sorry. I can't stay here anymore. Goodbye!", "I guess it couldn't be helped... Haah, I can finally relax...")
            elif "Imouto" in char_traits:
                lines = ("Alright, I'm leaving. I don't want to hear any complaints, okay?", "Hey, could you not get involved with me anymore? Goodbye.")
            elif "Dandere" in char_traits:
                lines = ("This is the end of our partnership. I want nothing more to do with you.", "Our agreement is now done. I want nothing more to do with you.")
            elif "Tsundere" in char_traits:
                lines = ("Goodbye. I can't deal with this anymore.", "Ugh... I can't stay here anymore.　Goodbye.")
            elif "Kuudere" in char_traits:
                lines = ("Bye. Don't come near me again.", "I am cutting off all connections with you. Goodbye.")
            elif "Kamidere" in char_traits:
                lines = ("Oh yeah, I don't need you anymore. See ya.", "Spare me from ever having to be around trash like you again. Goodbye.")
            elif "Bokukko" in char_traits:
                lines = ("See ya. Can't stand to be with you for even a moment longer.", "Yeah, about time. Starting now, you and I are strangers!")
            elif "Ane" in char_traits:
                lines = ("I don't want to be here anymore. Goodbye.", "You and I are now complete strangers. This has already been decided.")
            elif "Yandere" in char_traits:
                lines = ("I don't want to see your face anymore. Goodbye.", "I no longer feel like I need to be at your side, so... Farewell.")
            else:
                lines = ("I no longer want to stay here. Goodbye.", "We're complete strangers now. Bye.")
            block_say = True
            iam.say_line(character, lines)
            block_say = False

        @staticmethod
        def accept_badgift(character):
            """
            Output line when a character receives a bad gift
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I don't need it.", "Can I return it later?", "What's it for?", "Please, never bring this to me again.", "This isn't exactly my favourite...")
            elif "Shy" in char_traits and dice(50):
                lines = ("<sigh>", "It's... for me? Um... why?", "Uh, it's for me? Ah... It's a... what is this, exactly? ...I see.")
            elif "Tsundere" in char_traits:
                lines = ("Who would want this crap?", "Hmph! What an idiot!", "Whaaat? What am I supposed to do with this?!", "How stupid are you?! <[p] looks ready to throw it at you>", "What the...? This is terrible!")
            elif "Kuudere" in char_traits:
                lines = ("Just this? Don't expect any thanks.", "And what should I do with this... thing?", "You know, someone like me has no use for this.", "Oh? I thought you knew me better than that.", "Is this a gift? Oh...", "Is this some kind of mean joke?")
            elif "Yandere" in char_traits:
                lines = ("What were you thinking? This is awful!", "This is absolute junk. I'm offended.", "Ugh...that's such a stupid gift.", "It looks like your gifts are as desirable as you are right now.")
            elif "Dandere" in char_traits:
                lines = ("I don't want it.", "Oh. I guess I'll take it.", "..? <[p] does not look any happier>", "This is a pretty terrible gift, isn't it?", "This item gives me a terrible feeling. I'll have to dispose of it.")
            elif "Ane" in char_traits:
                lines = ("Not to be ungrateful, but... I really don't like this.", "<Sigh> I'll take it, but only this once.", "Umm... this is... interesting.", "Well, I guess it's the thought that counts...")
            elif "Imouto" in char_traits:
                lines = ("Hey! I don't want this!", "Oh, a present!... Ack! <[op] mood does a 180>", "Yuck! You thought I would like this?", "*sigh* This makes me depressed.", "Yuck, what is this? This isn't very fun...")
            elif "Kamidere" in char_traits:
                lines = ("This junk isn't useful at all.", "Hmm... I'm not a huge fan of this.", "This is probably the worst gift I've ever seen. Thanks a lot.", "Please refrain from bothering me with this in the future.")
            elif "Bokukko" in char_traits:
                lines = ("Man... this is bad...", "Hmm, so my zodiac was right... today's a bad day.", "Hey, is this a joke? What am I supposed to do with this?")
            else:
                lines = ("Hmm... I guess everyone has different tastes...", "Thanks, but I don't like these kinds of things.", "I'll receive it, but... <sigh>", "Ugh...I'm sorry, but I absolutely hate this.")
            iam.say_line(character, lines, overlay_args=("sweat", "reset"))

        @staticmethod
        def accept_goodgift(character):
            """
            Output line when a character receives a good gift
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Don't mind if I do.", "Thank you. I'll take it.", "I suddenly feel better now.", "I'll take that off your hands, if you don't mind.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Oh... th-thank you.", "Er, um... Thank you!", "<Blush> Is it ok if I take this?..", "That's... very nice.")
            elif "Tsundere" in char_traits:
                lines = ("What's this? To do something for someone like me... A-alright then.", "I was just thinking that I wanted one of these.", "Isn't this... too fancy for me?", "Hmm? Not bad. Thank you.",)
            elif "Kuudere" in char_traits:
                lines = ("Well... since you offered... <smiling>", "That's very kind of you. I like this.", "Oh, this is pretty good. I'll take it.", "You did good with this one, [mc_ref]. Thanks." )
            elif "Yandere" in char_traits:
                lines = ("Now I have something you've given me. <blush>", "I don't mind if you spoil me. <smiles>", "*gasp*...for me? Thank you!")
            elif "Dandere" in char_traits:
                lines = ("...Thanks.", "Is it ok if I have this? Thanks.", "Is it alright for me to have this?", "Thanks.")
            elif "Ane" in char_traits:
                lines = ("Thank you. You have my regards.", "Oh my, I'm grateful ♪", "Trying to earn points, huh? <giggle>", "Oh, this is rather good.", "Oh, goodness! Are you sure? Thanks!")
            elif "Imouto" in char_traits:
                lines = ("Oh! You got me something! <giggles>", "Hehehe, if you keep doing this I'll be spoiled.", "Waa? Giving me things all of the sudden...", "I love presents! Thank you!")
            elif "Kamidere" in char_traits:
                lines = ("I will accept this; as a first-class lady.", "<Laughs> You just keep giving me things.", "Yes, this is how you should be treating me.")
            elif "Bokukko" in char_traits:
                lines = ("Oh? This is pretty good! Thanks.", "Yeah, looks good! Thanks!", "This is a fun gift. Thanks!", "Oh, a present! Thank you!", "This is a super gift! Thank you!")
            else:
                lines = ("Thank you so much!", "Yes, you have my thanks.", "Thank you...! I'm happy.", "This is a really nice gift! Thank you!", "Haha. Can't say 'no' to that.",  "No! I won't take it! Just kidding ♪", "Well, that's nice.")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def accept_perfectgift(character):
            """
            Output line when a character receives a perfect gift
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("You really know what I like, don't you?", "It's incredible. Thank you.", "It... it's perfect.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Oh!! A-amazing!", "<Blush> Is it alright if I have something this incredible?..", "Waaaa!? Is it worth it? ...Giving me something this valuable?")
            elif "Tsundere" in char_traits:
                lines = ("I-if you keep giving me things like this... <she's blushing>", "Am I really that special to you? ...I see <her face is completely red>", "I-it's not like I like it a lot!")
            elif "Kuudere" in char_traits:
                lines = ("Wh-where did you get one of these?! You're awesome!", "Tch... you're getting me indebted to you, [mc_ref].")
            elif "Yandere" in char_traits:
                lines = ("You are sweet,[mc_ref]... thank you... I like it.", "Oh, this is my favourite thing! ♪", "That's such a nice gift. Thank you!")
            elif "Dandere" in char_traits:
                lines = ("I really love this. How did you know?", "Thanks, I like this.", "<[op] smile is radiant>")
            elif "Ane" in char_traits:
                lines = ("Oh, you're such a sweetheart! I really love this!", "You're giving this... to me? I love it ♪ <smiles gently>", "With this we can get married! Just kidding ♪ <giggles>", "Oh my. It's really too much... <blush>", "Oh my, it looks wonderful! That's very kind of you.")
            elif "Imouto" in char_traits:
                lines = ("Hurray!", "Thank you! Chuuu ♥", "You didn't take out a loan for this, I hope ♪", "I seriously love this! You're the best, [mc_ref]!", "*gasp* ...Wow! Thank you!")
            elif "Kamidere" in char_traits:
                lines = ("Fantastic! You have a great taste.", "How... don't go blowing your money, alright? <[p]'s got a huge grin>", "[mc_ref], this is a beautiful gift! Thank you.")
            elif "Bokukko" in char_traits:
                lines = ("Man, this is good stuff... thanks!", "A-are you a mind reader? Because that would be unfair! ♥ <hugs> ♥", "Is that...? This is spectacular! Whoa! No way! Thank you!", "Hey, hey! Now this is really something! Thanks a million!")
            else:
                lines = ("I'm so happy! Many thanks, [mc_ref].", "You're amazing. This is exactly what I wanted! Thank you.", "Oh, you shouldn't have. Thank you, I really love this.", "This gift is fabulous! Thank you so much!")
            iam.say_line(character, lines, "shy", ("note", "reset"))

        @staticmethod
        def accept_sell(character):
            """
            Output line when a character sells an item because the hero tell them to
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Well, if you say so.", "Alright, I can live without it.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Uhm.. Ok... right...", "Ehm.. right... yes...", "Right, right...")
            elif "Tsundere" in char_traits:
                lines = ("Not that I needed anyway.", "Oh that? I don't use it anymore.")
            elif "Kuudere" in char_traits:
                lines = ("Yes, I though about to get rid of it for ages.", "Alright. It is useless anyway.")
            elif "Yandere" in char_traits:
                lines = ("Ok, I don't see a reason to keep it.", "Yes, I think I'm better off without it.")
            elif "Dandere" in char_traits:
                lines = ("Yes. You are right... I don't need that anymore.", "I guess it was not used anyway...")
            elif "Ane" in char_traits:
                lines = ("Ooh right. I don't need it anymore.", "Yes, you are right. Please get rid of this for me, will you?")
            elif "Imouto" in char_traits:
                lines = ("Huhu, make free space for something new, right? ♪", "You want to make my life lighter, right? ♪")
            elif "Kamidere" in char_traits:
                lines = ("Fine, it is just a useless item.", "I don't use it, so just get rid of it!")
            elif "Bokukko" in char_traits:
                lines = ("Man, why did I have this in the first place?", "Of course, there is no need for that anymore!")
            else:
                lines = ("Now that you mention it, it is really useless.", "Thanks, I wanted to sell this for some time.")
            iam.say_line(character, lines)

        @staticmethod
        def refuse_shop(character):
            """
            Output line when a character refuses a shopping gift because they have it already
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("This particular item is not required at the moment.", "I have one of these already.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I-I can not accept this...", "It's... I already have one, sorry...")
            elif "Tsundere" in char_traits:
                lines = ("As expected from an idiot like you. I already have one!", "Another one? Really? What's wrong with you?")
            elif "Kuudere" in char_traits:
                lines = ("Why would I want an another one of these?", "Stop it. I have this already.")
            elif "Yandere" in char_traits:
                lines = ("Don't you see? I have this already.", "Huh? Do you think I should collect these?")
            elif "Dandere" in char_traits:
                lines = ("Another one?..", "One more? Why?")
            elif "Ane" in char_traits:
                lines = ("I appreciate the thought, but I don't really want one more of this.", "Oh, but I have this already. Don't you remember?")
            elif "Imouto" in char_traits:
                lines = ("Wha? I have it already!", "Ugh. I have this already. Boring!")
            elif "Kamidere" in char_traits:
                lines = ("You can't remember something so simple? Pathetic.", "Pfft. Naturally, I have no need for another one of these.")
            elif "Bokukko" in char_traits:
                lines = ("C'mon, really? Another one of these?", "Another one? Do you think I'm obsessed with these?")
            else:
                lines = ("Sorry, I don't want another one of these.", "I don't think I need more of these.")
            iam.say_line(character, lines, overlay_args=("puzzled", "reset"))

        @staticmethod
        def refuse_gift(character):
            """
            Output line when a character refuses a gift
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("This particular item is not required at the moment.", "I have one of these already.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I-I think you gave it to me already...", "It's... I already have one, sorry...")
            elif "Tsundere" in char_traits:
                lines = ("As expected from an idiot like you.", "Again? Really? What's wrong with your head?")
            elif "Kuudere" in char_traits:
                lines = ("What do you think you're doing? You already gave it.", "Stop it. I have this already.")
            elif "Yandere" in char_traits:
                lines = ("Don't you remember? I have this already.", "Huh? You want to give me this again?")
            elif "Dandere" in char_traits:
                lines = ("Again?..", "One more? Why?")
            elif "Ane" in char_traits:
                lines = ("I appreciate the thought, but giving the same gift again and again is not a good idea.", "Oh, but I have this already. Don't you remember?")
            elif "Imouto" in char_traits:
                lines = ("Wha? I have it already!", "Ugh. I have this already. Boring!")
            elif "Kamidere" in char_traits:
                lines = ("You can't remember something so simple? Pathetic.", "Pfft. Naturally, I have no need for another one of these.")
            elif "Bokukko" in char_traits:
                lines = ("C'mon, really? Another one of these?", "Another one? Do you have a collection or something?")
            else:
                lines = ("Sorry, I don't want another one of these.", "Didn't you give me it not so long ago?")
            iam.say_line(character, lines, overlay_args=("puzzled", "reset"))

        @staticmethod
        def refuse_gift_too_many(character):
            """
            Output line when a character refuses a gift because the hero gave too many already
            """
            char_traits = character.traits
            mood, overlay_args = "indifferent", None
            if "Impersonal" in char_traits:
                lines = ("Nah.. I have enough things from you already.", "Thanks, but no thanks.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I-I think that's enough for the moment...", "It's... Not necessary, sorry...")
                mood = "sad"
            elif "Tsundere" in char_traits:
                lines = ("Stop! That's enough!", "What's wrong with you? I got more than enough things from you...")
                overlay_args = ("angry", "reset")
            elif "Kuudere" in char_traits:
                lines = ("What do you think you're doing? You already gave me so many things.", "Stop it. I have enough for the moment.")
                overlay_args = ("angry", "reset")
            elif "Yandere" in char_traits:
                lines = ("Don't you think that it is enough for the moment?", "Huh? You want to give me this as well?")
                overlay_args = ("puzzled", "reset")
            elif "Dandere" in char_traits:
                lines = ("This as well? ...", "One more? Why?")
                mood = "tired"
            elif "Ane" in char_traits:
                lines = ("I appreciate the thought, but giving so many gifts is not a good idea.", "Oh, but I have so many things already. Don't you think?")
            elif "Imouto" in char_traits:
                lines = ("Wha? I have enough!", "Ugh. I have more than enough. Boring!")
            elif "Kamidere" in char_traits:
                lines = ("You want to suffocate with your presents? Pathetic.", "Pfft. Don't even try to buy me with your gifts...")
            elif "Bokukko" in char_traits:
                lines = ("C'mon, really? Another one of these?", "Do you have a lot of useless stuff or what?")
            else:
                lines = ("Sorry, I don't want any more of your stuff.", "Didn't you give me enough already?")
            iam.say_line(character, lines, mood=mood, overlay_args=overlay_args)

        @staticmethod
        def refuse_money(character):
            """
            Output line when a character refuses money
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I don't need it.", "What do you expect me to do with this money?")
            elif "Shy" in char_traits and dice(50):
                lines = ("It's... for me? ...Um, thanks, but I cannot accept it.", "Oh... th-thank you, but I d-don't need it.")
            elif "Tsundere" in char_traits:
                lines = ( "Huh? You think I'm that poor?!", "Hmph! I don't need your money! Idiot...")
            elif "Kuudere" in char_traits:
                lines = ("Too bad, I'm not that cheap.", "I can perfectly live without your money, thanks you very much.")
            elif "Yandere" in char_traits:
                lines = ("Money? I don't need them.", "I'm not interested.")
            elif "Dandere" in char_traits:
                lines = ("I don't want it.", "No thanks.")
            elif "Ane" in char_traits:
                lines = ("Not to be ungrateful, but... I really don't need money.", "I appreciate it, but I'm capable to live on my own.")
            elif "Imouto" in char_traits:
                lines = ("Oh, a present! ...Money? Boring!", "Hey, I don't want your money!")
            elif "Kamidere" in char_traits:
                lines = ("Is it the best you can do? Hehe, seems like you need money more than me ♪", "Is that all? Really? Pathetic.")
            elif "Bokukko" in char_traits:
                lines = ("Wha? Money? Huhu, don't need them ♪", "Hey, is this a joke?")
            else:
                lines = ("Thanks, but no thanks.", "Um, I think you should keep these money for yourself.")
            iam.say_line(character, lines, overlay_args=("puzzled", "reset"))

        @staticmethod
        def accept_money(character):
            """
            Output line when a character accepts money
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Thanks for your donation.", "I accept it. You have my thanks.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Oh... th-thank you.", "<Blush> Is it ok if I take this?...")
            elif "Tsundere" in char_traits:
                lines = ("I guess I could use some... A-alright then.", "Your money? Are you sure..? Fine then, thanks.")
            elif "Kuudere" in char_traits:
                lines = ("Well... since you offered... I could use some.", "...Thank you. I promise to spend them wisely.")
            elif "Yandere" in char_traits:
                lines = ("You want to give me money?.. Fine, I don't mind.", "Alright, but I'll give you something in return one day, ok?")
            elif "Dandere" in char_traits:
                lines = ("Is it really ok? Thanks then.", "Thanks.")
            elif "Ane" in char_traits:
                lines = ("Thank you. You have my regards.", "Oh my, I'm grateful. I'll be sure to put your money to good use.")
            elif "Imouto" in char_traits:
                lines = ("Oh! Money! ♪ <giggles>", "Hehehe, if you keep doing this I'll be spoiled.")
            elif "Kamidere" in char_traits:
                lines = ("I'm accepting your generous offer.", "Very well. You have my gratitude.")
            elif "Bokukko" in char_traits:
                lines = ("Oh? This is pretty cool! Thanks.", "Hey, thanks. It's shoppin' time ♪")
            else:
                lines = ("Thank you! I greatly appreciate it.", "Um, thank you. Can't say 'no' to free money, I guess ♪")
            iam.say_line(character, lines, "happy", ("note", "reset"))

        @staticmethod
        def refuse_recently_gave_money(character):
            """
            Output line when a character recently gave money to the hero and refusing to give more
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Denied. Your requests are too frequent.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("I-I'd really like to... But... Um... Sorry.", )
            elif "Tsundere" in char_traits:
                lines = ("What, again?! What happened to the money I gave you the last time?", )
            elif "Kuudere" in char_traits:
                lines = ("Show some restraint. You cannot depend on others all the time.", )
            elif "Yandere" in char_traits:
                lines = ("You want my money again? I don't feel like it, sorry. Maybe next time.", )
            elif "Dandere" in char_traits:
                lines = ("No. You ask too much.", )
            elif "Ane" in char_traits:
                lines = ("You need to learn how to live on your own. Let's discuss it again after a while, alright?", )
            elif "Imouto" in char_traits:
                lines = ("Whaat? Again? All you think about is money!!", )
            elif "Kamidere" in char_traits:
                lines = ("I don't think so. Get a job, will you?", )
            elif "Bokukko" in char_traits:
                lines = ("No way! If you goin' to ask for money so often, I will become poor too.", )
            else:
                lines = ("I cannot help you again, sorry. Maybe another time.", )
            iam.say_line(character, lines, overlay_args=("sweat", "reset"))

        @staticmethod
        def refuse_not_enough_money(character):
            """
            Output line when a character does not have enough money
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Denied. Not enough funds.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("Err... S-sorry, I don't have much money at the moment...", )
            elif "Tsundere" in char_traits:
                lines = ("*sigh* I'm not made of money, you know.", )
            elif "Kuudere" in char_traits:
                lines = ("I'm afraid you overestimate me. I'm not that rich *sadly smiles*", )
            elif "Yandere" in char_traits:
                lines = ("*sigh* I barely make ends meet, so... no.", )
            elif "Dandere" in char_traits:
                lines = ("No. I need money too.", )
            elif "Ane" in char_traits:
                lines = ("Unfortunately, I can't afford it.", )
            elif "Imouto" in char_traits:
                lines = ("Ugh... I don't have much money. Sorry ♪", )
            elif "Kamidere" in char_traits:
                lines = ("I refuse. Since I'm low on gold, my own needs take priority.", )
            elif "Bokukko" in char_traits:
                lines = ("Not gonna happen. I'm running out of money.", )
            else:
                lines = ("I cannot help you, sorry. Maybe another time.", )
            iam.say_line(character, lines)

        @staticmethod
        def refuse_praise(character):
            """
            Output line when a character refuses a praise attempt
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Does that usually work?", "Bigmouth.", "...What do you want?", "...You talk too much.", "<[pC] completely ignores you>", "...and?")
            elif "Shy" in char_traits and dice(50):
                lines = ("U-um, you were talking to me? Oh ... <[p]'s embarrassed>", "Pl-please ... stop...", "Don't ... make fun of me.", "Well ... that ... <[p] looks like [p] wants to run away>", "Ah, I-I'm not... S-sorry...", "Really? I don't think... I-I'm sorry.", "<looks uncomfortable> No, I... umn... sorry.")
            elif "Imouto" in char_traits:
                lines = ("Huhu, you're far too obvious.", "Eh? You sound like a perv!", "Booring!", "Huhn, who would fall for a line like that?")
            elif "Kuudere" in char_traits:
                lines = ("Stop that. Empty praises won't do you any good.", "You can stop talking now.", "Can't find something better to say?", "All talk and nothing to back it up. What are you even trying to do?", "*sigh*...  I don't really have time for this.")
            elif "Dandere" in char_traits:
                lines = ("Can we end this conversation here?", "That's...not true.", "Not funny.", "*sigh*... thank you...<looks bored>", "Please, drop this flattery.")
            elif "Tsundere" in char_traits:
                lines = ("I won't be fooled by beautiful words.", "I find that extremely hard to believe.", "What? I have no idea what you're talking about.", "Lay off the jokes; there's already one attached to the front of your head!")
            elif "Kamidere" in char_traits:
                lines = ("Don't try to pull the wool over my eyes. I know what you're after.", "Don't you have something better to do?", "What do you want, anyway?", "Are you making fun of me?", "What a supremely boring joke. You've got awful taste.")
            elif "Ane" in char_traits:
                lines = ("Whatever are you saying?", "That is simply not true.", "Can we talk about something else?", "<looks unimpressed> Thank you...", "Thanks, but please leave me alone, I'm not interested", "I'm sorry, but I don't have time for this.", "I don't think you are being sincere.")
            elif "Bokukko" in char_traits:
                lines = ("Eeh, I wouldn't say that...", "That can't be right, hey?", "Eh? But that's wrong, right?", "But that's not true at all?", "Eh? What are you talking about?")
            elif "Yandere" in char_traits:
                lines = ("Don't mock me.", "I don't understand, what?", "That's not true.", "Don't try too hard, you'll hurt yourself.", "That's definitely not true, so relax, okay?", "Please, don't bother me.")
            else:
                lines = ("Sorry, not interested.", "How many girls have you said that to today?", "...I'm sorry, did you say something?", "That doesn't sound sincere at all.", "You don't have to say things you don't mean.", "Too bad. I'm not going to fall for that.", "What is it? I don't get what you mean.", "Well... guess so. <unimpressed>", "You don't sound as if you mean it.")
            iam.say_line(character, lines)

        @staticmethod
        def accept_praise(character):
            """
            Output line when a character accepts a praise
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("There's no need to state the obvious.", "I... see. *[p] looks happier than before*", "I thank you.")
            elif "Shy" in char_traits and dice(30):
                lines = ("Th-thanks...", "You think so? <blush>", "<[pC] quickly looks away, [op] face red>", "You're ... nice...", "I've never... really been praised much.", "Y-yes... thank you very much... ", "Th... thanks... ", "Ah... ah... really...? I'm so happy...  ", "T-thank you...")
            elif "Imouto" in char_traits:
                lines = ("Haha, thank you ♪", "Huhu ♪ Are you interested in me?", "Fuaaah... Aww, praise me more...", "Really? I'm so happy!", "Ehehe...you praised me ♪")
            elif "Kuudere" in char_traits:
                lines = ("Thanks, but it's nothing to boast of.", "Heh, good one.", "Of course.", "Um, there's tons of people better than me...", "Is that how you see me...", "Hm? Oh, thanks.")
            elif "Dandere" in char_traits:
                lines = ("..You're too kind.", "It's very nice of you to say so.", "Thank you... very much.", "Hearing that makes me happy, even if it's just flattery.")
            elif "Tsundere" in char_traits:
                lines = ("Such flattery won't work on me! <it totally looks like it's working>", "I, I knew that, of course...", "Huh, you finally figured that out?", "It's not like I'm happy or anything. But for now I'll accept your praise.")
            elif "Ane" in char_traits:
                lines = ("Well, I do like being praised.", "Well, that was certainly witty.", "O-Oh stop, you're embarrassing me ♪", "Thank you, I'm very pleased.", "My, I am happy to hear that.")
            elif "Kamidere" in char_traits:
                lines = ("Thanks, but it's nothing worth mentioning.", "Be a little serious please. ...eh... you are?", "What was that? Are you planning to ask me out?", "You can say that all you want, I'm not going to give you anything ♪")
            elif "Bokukko" in char_traits:
                lines = ("Hey, I really might be cool <giggles>", "Well, I am cool! Hmph!", "Hehe, did you fall for me?", "Eh? You're interested in me? That's some good taste, really good!", "Hm-hmm! That's right, respect me lots!", "Well, that's just the way it goes, y'know?", "Thanksies ♪")
            elif "Yandere" in char_traits:
                lines = ("Thank you, I'm glad to hear that.", "I sure hope you don't go saying that to every other girl too.", "You are sweet.", "D-don't say that... I'm starting to blush.")
            else:
                lines = ("Hehe, thanks.", "Thanks for the compliment.", "<Smiles> Yes, go on ...", "Alright, you've got my attention <blush>", "Aww, so sweet ♪", "You don't have to say that. <[p]'s blushing and smiling>", "Gosh, flattery won't get you anything from me, you know?", "Ehehe, thank you very much ♪", "Oh, you're exaggerating.", "Thank you, I'm very pleased.")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def refuse_sparring(character):
            """
            Output line when the character refuses the sparring offer of the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Denied.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("S-sorry, I don't think I can...", )
            elif "Imouto" in char_traits:
                lines = ("Sounds boring... Think I'm gonna pass.", )
            elif "Dandere" in char_traits:
                lines = ("Thanks, but I will refrain.", )
            elif "Tsundere" in char_traits:
                lines = ("Are you out of your mind? Why should I agree to that?", )
            elif "Kuudere" in char_traits:
                lines = ("No. Don't want to.", )
            elif "Kamidere" in char_traits:
                lines = ("Just forget about it. I have enough things to worry about already.", )
            elif "Bokukko" in char_traits:
                lines = ("Nah, too much trouble.", )
            elif "Ane" in char_traits:
                lines = ("Sorry, I'm not really up to it.", )
            elif "Yandere" in char_traits:
                lines = ("No, I have no such intentions.", )
            else:
                lines = ("Sorry, not interested.", )
            iam.say_line(character, lines)

        @staticmethod
        def sparring_start(character):
            """
            Output line when a character and the hero starts a sparring challenge
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Understood. Initialising battle mode.", "Very well. Switching to training mode.")
            elif "Imouto" in char_traits:
                lines = ("Behold of my amazing combat techniques, [mc_ref]! ♪", "Activate super duper mega ultra assault mode! ♪")
            elif "Dandere" in char_traits:
                lines = ("Let's end this quickly, [mc_ref]. We have many other things to do.",  "Let's see who's stronger.")
            elif "Kuudere" in char_traits:
                lines = ("Fine, I accept your challenge.", "Let's fight fair and square.")
            elif "Tsundere" in char_traits:
                lines = ("I won't go easy on you!", "Fine, I'll show you how it's done.")
            elif "Bokukko" in char_traits:
                lines = ("I'm gonna whack you good!", "All right, let's clean this up fast!")
            elif "Ane" in char_traits:
                lines = ("Hehe, let's both do our best.", "Fine, but let's be careful, ok?")
            elif "Kamidere" in char_traits:
                lines = ("Alright, let's see what you can do.", "I suppose I have a few minutes to spare.")
            elif "Yandere" in char_traits:
                lines = ("Sure, but don't blame me if it gets a little rough...", "I'll try to be gentle, but no promises.")
            else:
                lines = ("I don't mind. Let's do it.", "Sure, I can use some exercises. ♪")
            iam.say_line(character, lines, "confident")

        @staticmethod
        def sparring_end(character):
            """
            Output line after a sparring between the character and the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Practice is over. Switching to standby mode.", "An unsurprising victory.")
            elif "Imouto" in char_traits:
                lines = ("Woohoo! Getting stronger every day!", "Haha, it was fun! We should do it again!")
            elif "Dandere" in char_traits:
                lines = ("Guess that does it. Good fight.", "Ok, I suppose we can leave it at this.")
            elif "Kuudere" in char_traits:
                lines = ("You are a worthy opponent.", "We both still have much to learn.")
            elif "Tsundere" in char_traits:
                lines = ("Jeez, now I'm tired after all that.", "Haaa... It was pretty intense.")
            elif "Bokukko" in char_traits:
                lines = ("Oh, we done fighting already?", "Not a bad exercise, was it?")
            elif "Ane" in char_traits:
                lines = ("Oh my, I think I may have overdone it a little. Apologies.", "It didn't look pretty, but what matters is who's standing at the end.")
            elif "Kamidere" in char_traits:
                lines = ("I'm tired. We are done here.", "I suppose it was a valuable experience.")
            elif "Yandere" in char_traits:
                lines = ("Sorry, I got carried away. But you did well nevertheless.", "Goodness, look at this. I got my clothes all dirty.")
            else:
                lines = ("You're pretty good.", "Phew... We should do this again sometime.")
            iam.say_line(character, lines)

        @staticmethod
        def archery_start(character):
            """
            Output line when a character and the hero starts an archery challenge
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Understood. Initialising battle mode.", "Very well. Switching to training mode.")
            elif "Imouto" in char_traits:
                lines = ("Behold of my amazing techniques, [mc_ref]!")
            elif "Dandere" in char_traits:
                lines = ("Let's end this quickly, [mc_ref]. We have many other things to do.",  "Let's see who's better.")
            elif "Kuudere" in char_traits:
                lines = ("Fine, I accept your challenge.", "Let's fight fair and square.")
            elif "Tsundere" in char_traits:
                lines = ("I won't go easy on you!", "Fine, I'll show you how it's done.")
            elif "Bokukko" in char_traits:
                lines = ("I'm gonna whack you good!", "All right, let's get over with this fast!")
            elif "Ane" in char_traits:
                lines = ("Hehe, let's both do our best.", "Fine, let's find out who is better at this!")
            elif "Kamidere" in char_traits:
                lines = ("Alright, let's see what you can do.", "I suppose, I have a few minutes to spare.")
            elif "Yandere" in char_traits:
                lines = ("Sure, but don't blame me if your ass is gonna be kicked...", "I'll try to be gentle, but no promises.")
            else:
                lines = ("I don't mind. Let's do it.", "Sure, I can use some practice.")
            iam.say_line(character, lines, "confident")

        @staticmethod
        def archery_end(character):
            """
            Output line when a character and the hero ends an archery challenge
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Practice is over. Switching to standby mode.", "All right, let's get back to normal.")
            elif "Imouto" in char_traits:
                lines = ("Woohoo! Getting better every day!", "Haha, it was fun! We should do it again!")
            elif "Dandere" in char_traits:
                lines = ("Guess that does it. Good fight.", "Ok, I suppose we can leave it at this.")
            elif "Kuudere" in char_traits:
                lines = ("You are a worthy opponent.", "We both still have much to learn.")
            elif "Tsundere" in char_traits:
                lines = ("Jeez, now I'm tired after all that.", "Haaa... It was pretty fun.")
            elif "Bokukko" in char_traits:
                lines = ("Oh, we done already?", "Not a bad exercise, was it?")
            elif "Ane" in char_traits:
                lines = ("Oh my, I think I may have overdone it a little. Apologies.", )
            elif "Kamidere" in char_traits:
                lines = ("I'm tired. We are done here.", "I suppose it was a valuable experience.")
            elif "Yandere" in char_traits:
                lines = ("Sorry, I got carried away. But you did well nevertheless.", "Goodness, look at this. I got my clothes all wet.")
            else:
                lines = ("You're pretty good.", "Phew... We should do this again sometime.")
            iam.say_line(character, lines)

        @staticmethod
        def refuse_because_of_incest(character):
            """
            Output line when the character refuses something because it would be an incest
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Step back, I'm your sister.", "No! I'm still your sister...")
            elif "Imouto" in char_traits:
                lines = ("Hey, stop! I'm your sister!", "Nonsense, that would be incest!")
            elif "Dandere" in char_traits:
                lines = ("Can't do it, sorry. We are siblings...", "I have to refuse it, I'm your sister.")
            elif "Kuudere" in char_traits:
                lines = ("Won't happen. We are siblings.", "Not a chance. We are related.")
            elif "Tsundere" in char_traits:
                lines = ("Not in your lifetime. I'm your sister.", "Are you crazy? We are siblings.")
            elif "Bokukko" in char_traits:
                lines = ("You must be joking, right? We are related.", "Right, as if siblings should do that...")
            elif "Ane" in char_traits:
                lines = ("I'm really sorry, but I would not feel comfortable with it. I'm your sister after all.", "I do not want to offend you, but I have to refuse it since we are siblings.")
            elif "Kamidere" in char_traits:
                lines = ("I think I have to refuse that. We are siblings.", "For real? I suppose you did not think this through, we are related.")
            elif "Yandere" in char_traits:
                lines = ("Sorry, but this won't work, we are related.", "I don't think siblings should do that.")
            else:
                lines = ("Please, think again. We are siblings.", "There must be other options, we are related.")
            iam.say_line(character, lines)

        @staticmethod
        def refuse_because_of_gender(character):
            """
            Output line when the character refuses something because of gender mismatch
            """
            char_traits = character.traits
            if hero.gender == "male":
                if "Impersonal" in char_traits:
                    lines = ("Opposite sex... Dismissed.", "You are a male. Denied.")
                elif "Shy" in char_traits:
                    lines = ("Ah, I'm sorry, I can't do that with a boy...", "Um, I-I like girls... Sorry!")
                elif "Imouto" in char_traits:
                    lines = ("If you were a girl...it'd be alright, but...", "I don't really like boys... So no.")
                elif "Dandere" in char_traits:
                    lines = ("Guys are...not for me.", "Wrong gender. Consider changing it.", "I turn down anyone who's not a girl.")
                elif "Kuudere" in char_traits:
                    lines = ("Men for me are...well...", "I'm afraid men are not attractive to me.", "Doing that with a man is... a bit...")
                elif "Tsundere" in char_traits:
                    lines = ("Hmph. And that's why I don't like men.", "Ugh, not again... I like girls, understood?", "Huh? You're a guy, so no way!")
                elif "Bokukko" in char_traits:
                    lines = ("Ew, don't wanna. You're a guy.", "Nah, I'm not interested in boys. Do you have a sister, by the way?", "Aah, I'm a lesbo, y'know.")
                elif "Ane" in char_traits:
                    lines = ("My apologies, I'm a lesbian.", "I'm terribly sorry, but... I can't do that with a man.")
                elif "Yandere" in char_traits:
                    lines = ("Sorry, I only like girls.", "I dislike men, nothing personal.", "I... I can't do men.")
                elif "Kamidere" in char_traits:
                    lines = ("I have no interest in men.", "Eww. I prefer girls, is it clear?", "Because you're a guy, no.")
                else:
                    lines = ("Sorry. I'm weird, so... I'm not into guys.", "Well, I kinda prefer girls... If you know what I mean.", "If you were a girl... it'd be alright, but...")
            else:
                if "Impersonal" in char_traits:
                    lines = ("Opposite sex... Dismissed.", "You are a female. Denied.")
                elif "Shy" in char_traits:
                    lines = ("Ah, I'm sorry, I can't do that with a girl...", "Um, I-I like boys... Sorry!")
                elif "Imouto" in char_traits:
                    lines = ("If you were a boy...it'd be alright, but...", "I don't really like girls... So no.")
                elif "Dandere" in char_traits:
                    lines = ("Gals are...not for me.", "Wrong gender. Consider changing it.", "I turn down anyone who's not a boy.")
                elif "Kuudere" in char_traits:
                    lines = ("Women for me are...well...", "I'm afraid women are not attractive to me.", "Doing that with a woman is... a bit...")
                elif "Tsundere" in char_traits:
                    lines = ("Hmph. And that's why I don't like women.", "Ugh, not again... I like boys, understood?", "Huh? You're a gal, so no way!")
                elif "Bokukko" in char_traits:
                    lines = ("Ew, don't wanna. You're a gal.", "Nah, I'm not interested in girls. Do you have a brother, by the way?", "Aah, I'm straight, y'know.")
                elif "Ane" in char_traits:
                    lines = ("My apologies, I'm straight.", "I'm terribly sorry, but... I can't do that with a woman.")
                elif "Yandere" in char_traits:
                    lines = ("Sorry, I only like boys.", "I dislike women, nothing personal.", "I... I can't do women.")
                elif "Kamidere" in char_traits:
                    lines = ("I have no interest in women.", "Eww. I prefer boys, is it clear?", "Because you're a gal, no.")
                else:
                    lines = ("Sorry. I'm weird, so... I'm not into gals.", "Well, I kinda prefer boys... If you know what I mean.", "If you were a boy... it'd be alright, but...")
            iam.say_line(character, lines)

        @staticmethod
        def refuse_because_tired(character):
            """
            Output line when the character refuses something because she/he is tired
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I don't have required endurance at the moment. Let's postpone it.", "No. Not enough energy.")
            elif "Shy" in char_traits and dice(50):
                lines = ("W-well, I'm a bit tired right now... Maybe some other time...", "Um, I-I don't think I can do it, I'm exhausted. Sorry...")
            elif "Imouto" in char_traits:
                lines = ("Noooo, I'm tired. I want to sleep.", "Z-z-z *she falls asleep on the feet*")
            elif "Dandere" in char_traits:
                lines = ("No. Too tired.", "Not enough strength. I need to rest.")
            elif "Tsundere" in char_traits:
                lines = ("I must rest at first. Can't you tell?", "I'm too tired, don't you see?! Honestly, some people...")
            elif "Kuudere" in char_traits:
                lines = ("I'm quite exhausted. Maybe some other time.", "I really could use some rest right now, my body is tired.")
            elif "Kamidere" in char_traits:
                lines = ("I'm tired, and have to intentions to do anything but rest.", "I need some rest. Please don't bother me.")
            elif "Bokukko" in char_traits:
                lines = ("Naah, don't wanna. Too tired.", "*yawns* I could use a nap first...")
            elif "Ane" in char_traits:
                lines = ("Unfortunately I'm quite tired at the moment. I'd like to rest a bit.", "Sorry, I'm quite sleepy. Let's do it another time.")
            elif "Yandere" in char_traits:
                lines = ("Ahh, my whole body aches... I'm way too tired.", "The only thing I can do properly now is to take a good nap...")
            else:
                lines = ("*sign* I'm soo tired lately, all I can think about is a cozy warm bed...", "I am ready to drop. Some other time perhaps.")
            iam.say_line(character, lines, "tired")

        @staticmethod
        def accept_hire(character):
            """
            Output line when the character accepts the hire offer of the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("You want me work for you. Understood.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("P-please take care of me...", )
            elif "Imouto" in char_traits:
                lines = ("Okey! Just, you know, don't boss me around too much ♪", )
            elif "Dandere" in char_traits:
                lines = ("Your proposition meets my goals. I accept it.", )
            elif "Tsundere" in char_traits:
                lines = ("Fine, fine. If you want it so much, I won't refuse.", )
            elif "Kuudere" in char_traits:
                lines = ("Very well. Please treat me well.", )
            elif "Kamidere" in char_traits:
                lines = ("I suppose I don't have any reasons to refuse.", )
            elif "Bokukko" in char_traits:
                lines = ("Sure, why not. Just be a good boss, ok?", )
            elif "Ane" in char_traits:
                lines = ("It's an acceptable proposition.", )
            elif "Yandere" in char_traits:
                lines = ("I don't have any objections.", )
            else:
                lines = ("Alright, I agree ♪", )
            iam.say_line(character, lines)

        @staticmethod
        def refuse_hire(character):
            """
            Output line when the character refuses the hire offer of the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Denied.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("S-sorry, I don't think I can...", )
            elif "Imouto" in char_traits:
                lines = ("Sounds boring... Think I'm gonna pass.", )
            elif "Dandere" in char_traits:
                lines = ("Thanks, but I will refrain.", )
            elif "Tsundere" in char_traits:
                lines = ("Are you out of your mind? Why should I agree to that?", )
            elif "Kuudere" in char_traits:
                lines = ("No. Don't want to.", )
            elif "Kamidere" in char_traits:
                lines = ("Please don't involve me in your business. I have enough things to worry about already.", )
            elif "Bokukko" in char_traits:
                lines = ("Nah, too much trouble.", )
            elif "Ane" in char_traits:
                lines = ("Sorry. Maybe some other time.", )
            elif "Yandere" in char_traits:
                lines = ("No, I have no such intentions.", )
            else:
                lines = ("Sorry, not interested.", )
            iam.say_line(character, lines)

        @staticmethod
        def accept_relationship(character):
            """
            Output line when the character accepts to enter in a relationship with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("You want me to have an affair with you. Understood.", "As you wish. I'm yours.", "I understand. I suppose we're now lovers.")
            elif "Shy" in char_traits and dice(20):
                lines = ("I-If you're okay with me...", "V-very well...  I-I'll work hard to be a woman fit to be with you.", "F-fine then...")
            elif "Imouto" in char_traits:
                lines = ("Mufufu... Behold, the birth of a new lovey-dovey couple!", "I-I um, I like you too, actually, ehehe♪", "Yes... Give me lots of love, please ♪")
            elif "Dandere" in char_traits:
                lines = ("Okay. From this moment on, we are completely bound by destiny... Ehe.", "I will dedicate all of my passionate feelings to you.")
            elif "Kuudere" in char_traits:
                lines = ("There's nothing about you I hate. I suppose I could let you have an affair with me.", "I don't mind, but... Prepare yourself.", "I'm, umm... yours...", "Are you really ok with me? Okay, let's go out together.")
            elif "Tsundere" in char_traits:
                lines = ("Haah... Why did I fall in love with someone like this...? I guess it's fine, though.", "Hmph... It's YOU we're talking about, so I thought something like this might happen.")
            elif "Bokukko" in char_traits:
                lines = ("I-I guess I could if you're g-gonna go that far.", "You've got weird taste, falling for a girl like me... Don't regret this, okay?", "I like you too, so we should be good to go, right?")
            elif "Ane" in char_traits:
                lines = ("Hmhm, I'll try establishing a relationship.", "Hmhmhm... I'm quite the troublesome woman, you know...?", "I swear I'll make you happy!")
            elif "Kamidere" in char_traits:
                lines = ("Yes, I suppose it's time things got serious.", "I feel the same way.", "Alright, you'd better take good care of me as your girlfriend.")
            elif "Yandere" in char_traits:
                lines = ("Of course! Now no one can keep us apart! Hehe ♪", "We're sweethearts now?　Finally! ♪", "I want to be yours as well ♪", "Huhu, I'm not responsible if you regret it...", "You wanna do something dirty with me, right? You'd better!")
            else:
                lines = ("Yes... I'll be by your side forever... Hehehe ♪", "O-Okay... Ahaha, this is kinda embarrassing...", "I guess I'm your girlfriend now. Hehe ♪")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def refuse_relationship(character):
            """
            Output line when the character refuses to enter in a relationship with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Unable to process.", "I'm sorry, but I must refuse you.")
            elif "Shy" in char_traits and dice(30):
                lines = ("Sorry... I'm... still not ready to go that far...", "Ah... Eh... Aah! This is a joke... Right?")
            elif "Imouto" in char_traits:
                lines = ("Sure, wh-... Mmmm! ...Come to think of it...it's a bad idea after all...", "Ufufu, I'm not falling for that joke!", "Geez♪, stop joking around♪")
            elif "Dandere" in char_traits:
                lines = ("Nice weather today.", "I am not interested at the moment.", "Sorry, you're not my type.")
            elif "Kuudere" in char_traits:
                lines = ("That...wasn't very funny, you know?", "...No.", "I'm not strong enough to date someone I don't care for...", "...L-let me think about it.")
            elif "Tsundere" in char_traits:
                lines = ("Hmph. You're out of your league.", "How about you go kill yourself?", "Y...you idiot! D... don't say something so embarassing like that!", "Jeez, please take your relationships more seriously!")
            elif "Bokukko" in char_traits:
                lines = ("Drop it, this sounds like it'll be a huge pain in the ass.", "S-stop asking that stuff, you embarrass me...", "No way, what kind of girl do you think I am, geez...", "But you're my friend. Friends are friends, duh.")
            elif "Ane" in char_traits:
                lines = ("...I'm sure you'll find someone that matches you better than I do.", "There's no sense losing your head over something you can't possibly achieve, you know?", "I'm sorry, but I can't go out with you", "I appreciate your feelings... But I can't answer them.")
            elif "Yandere" in char_traits:
                lines = ("No way!", "Don't ask me that", "What d'you mean...?", "Come on, if you wanna have me you gotta get out there and break a leg.")
            elif "Kamidere" in char_traits:
                lines = ("That's not for you to decide.", "That's too bad, I have no interest in you.", "That sort of relationship will be a big problem for both of us, you know?", "Being in a relationship is more trouble than it's worth.", "No way. I mean, you're just not good enough for me.")
            else:
                lines = ("I-I'm sorry! Let's just be good friends!", "That's... I'm sorry! Please let's continue being good friends!", "What's your problem? Saying that out of nowhere.", "That's nice of you to say, but... I can't help you there.")
            iam.say_line(character, lines)

        @staticmethod
        def offer_relationship(character):
            """
            Output line when the character offer to enter in a relationship with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I love you. I want to stay by your side.", "I love you. Let me hear your answer.", "I request permission to date you.", "I seem to have taken a liking to you...  Please go out with me.")
            elif "Shy" in char_traits and dice(50):
                lines = ("I... like you, and I want to be with you forever...", "I-I-I-I am in love with y-you...", "Sorry... No matter what I do, I can't get you out of my head... So... Go out with me!", "Do you want to try, um...going out with me?")
            elif "Imouto" in char_traits:
                lines = ("I-I... I love... you... I'm in love with you...", "Uhm... I love you! ...Please go out with me!", "I really like you, you know... So um...I want you to go out with me!")
            elif "Dandere" in char_traits:
                lines = ("I want to be your special person...", "I love you... Please let me be beside you, from now on.", "It seems like I really fell in love with you... So... won't you make me your lover?")
            elif "Tsundere" in char_traits:
                lines = ("L-listen up. I'm only gonna say this once.. I love you... S-so! G-go out with me!", "I l-like you... Like you so much that I can't do anything about it!", "So, um... Should we, maybe, start dating... or something?", "I'll only say this once, so listen up... I love you... I want you to date me!")
            elif "Kuudere" in char_traits:
                lines = ("*sigh*... Dammit, I won't hide it anymore... I just can't help it... I'm totally in love with you...", "Even though I don't get it myself... It seem like I've fallen in love with you.", "E-Excuse me... would you like to date me?")
            elif "Kamidere" in char_traits:
                lines = ("This really sucks for me, but... I love you... I said I love you!", "I like you... I love you. I'd like to hear how you feel.", "There's nothing about you I hate. So, would you become my lover?")
            elif "Bokukko" in char_traits:
                lines = ("Um... Would you try going out with me? I mean... I'm in love with you...", "You know, the two of us get along really well, right? So then, well... Do you want to try going out with me...?", "Um, so... What're your thoughts on like, me bein' your girlfriend...?")
            elif "Ane" in char_traits:
                lines = ("It seems like I fell in love with you... Won't you go out with me?", "I've fallen in love with you... Won't you go out with me?", "If I'm not a bother, would you... like to go out together?", "I love you... Please go out with me.")
            elif "Yandere" in char_traits:
                lines = ("I love you! Your heart and soul, I want it all!", "I... I like you! Please be my lover!", "I love you... Please date me.", "Um... I love you.. So be my 'darling'!")
            else:
                lines = ("I... love you. Please go out with me!", "I... I love you... M-make me your girlfriend!", "Hey, listen. I want you... to go out with me.", "I love you... I want to be by your side forever... So, please be my sweetheart!", "Um, so hey... I like you, please go out with me...")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def accept_movein(character):
            """
            Output line when the character accepts to move-in with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Sure thing.", "As you wish.", "Of course, but I need my own room.")
            elif "Shy" in char_traits and dice(20):
                lines = ("I-If you're okay with me...", "V-very well...  I-I'll work hard to fit in.", "F-fine then...")
            elif "Imouto" in char_traits:
                lines = ("Mufufu... Let us build a new nest ♪!", "I-I um, I was thinking about it too, actually, ehehe♪")
            elif "Dandere" in char_traits:
                lines = ("Okay. From this on we have something to build upon, right?", "I will dedicate my time to create warm environment for us.")
            elif "Kuudere" in char_traits:
                lines = ("There's nothing against it, so I suppose I could move in with you.", "I don't mind, but... Prepare yourself.", "I'm, umm... ready to move in...", "Are you really ok with me? Okay, let's live together.")
            elif "Tsundere" in char_traits:
                lines = ("Haah... Well, OK. This was inevitable, right?", "Hmph... How did we end up like this...? I guess it's fine, though.", "Alright, I guess this is supposed to happen...")
            elif "Bokukko" in char_traits:
                lines = ("I-I guess I could if you're g-gonna go that far.", "It is fine by me. I hope you won't regret this later.", "I think I could live there too, so why not?")
            elif "Ane" in char_traits:
                lines = ("Hmhm, I'll try to fit in.", "Hmhmhm... I'm quite the troublesome woman, you know...?", "I hope I won't disturb you!")
            elif "Kamidere" in char_traits:
                lines = ("Yes, I suppose it's time things got serious.", "I feel this is necessary to advance our relationship.", "Alright, you'd better take good care of me.")
            elif "Yandere" in char_traits:
                lines = ("Of course! Can't wait to spend more time with you! Hehe ♪", "Finally we're not separated for so long! ♪", "I want to be with you as much as possible ♪", "Hehe, I guess you like to be with me as well! ♪")
            else:
                lines = ("Yes... I think this is the right thing to do... Hehehe ♪", "O-Okay... I guess nothing speaks against it, haha ♪", "Alright, are we now a family? Hehe ♪")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def refuse_movein_disp(character):
            """
            Output line when the character refuses to move-in due to low disp (not lover)
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Denied.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("S-sorry, I don't think I can...", )
            elif "Imouto" in char_traits:
                lines = ("Don't think we are that close.", )
            elif "Dandere" in char_traits:
                lines = ("Thanks, but I will refrain.", )
            elif "Tsundere" in char_traits:
                lines = ("Are you out of your mind? Why should I agree to that?", "We are not that close!")
            elif "Kuudere" in char_traits:
                lines = ("No. Don't want to.", )
            elif "Kamidere" in char_traits:
                lines = ("Please don't involve me in your business. I have enough things to worry about already.", )
            elif "Bokukko" in char_traits:
                lines = ("Nah, too much trouble.", )
            elif "Ane" in char_traits:
                lines = ("Sorry. Maybe some other time.", )
            elif "Yandere" in char_traits:
                lines = ("I'm not sure it is a good idea, we hardly know each other.", )
            else:
                lines = ("Sorry, not interested.", )
            iam.say_line(character, lines)

        @staticmethod
        def refuse_movein_home(character):
            """
            Output line when the character refuses to move-in due to the bad quality of the home
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Nope, that place would not suit me.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("S-sorry, I don't think I want to move there...", )
            elif "Imouto" in char_traits:
                lines = ("Don't think that place would suit me.", )
            elif "Dandere" in char_traits:
                lines = ("Thanks, but my place is fine for me!", )
            elif "Tsundere" in char_traits:
                lines = ("You ought to find a better place before you suggest such a thing.", )
            elif "Kuudere" in char_traits:
                lines = ("No. Don't want to move there.", )
            elif "Kamidere" in char_traits:
                lines = ("Please, find a better place before you suggest something like that.", )
            elif "Bokukko" in char_traits:
                lines = ("Nah, my place is better for me.", )
            elif "Ane" in char_traits:
                lines = ("Sorry. The place where I live now suffice for the moment.", )
            elif "Yandere" in char_traits:
                lines = ("I'm not sure it is a good idea. My place is good enough for me.", )
            else:
                lines = ("Sorry, no. Why would I do that?", )
            iam.say_line(character, lines)

        @staticmethod
        def refuse_movein_dirt(character):
            """
            Output line when the character refuses to move-in due to dirt in the home
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("No way. Are you suggesting I could live in a dirt like that?", )
            elif "Shy" in char_traits and dice(50):
                lines = ("You really want me to move in «there»?", )
            elif "Imouto" in char_traits:
                lines = ("Huh? That place is like a pig stall!", )
            elif "Dandere" in char_traits:
                lines = ("Uhm.. Are you serious? Get rid of the piles of dirt first!", )
            elif "Tsundere" in char_traits:
                lines = ("Into that shit-hole? You expect me to clean your underwear too?", )
            elif "Kuudere" in char_traits:
                lines = ("No. Don't want to live on a pile of dirt.", )
            elif "Kamidere" in char_traits:
                lines = ("You better clean up that place before I even consider moving in there.", )
            elif "Bokukko" in char_traits:
                lines = ("Nah, how could I live in such a mess?!", )
            elif "Ane" in char_traits:
                lines = ("Hey, you might want to clean up that mess before!", )
            elif "Yandere" in char_traits:
                lines = ("What? You mean you expect me to live in such a dirty place?", )
            else:
                lines = ("Why would I want to live on a pile of dirt?", )
            iam.say_line(character, lines, overlay_args=("angry", "reset"))

        @staticmethod
        def refuse_movein_space(character):
            """
            Output line when the character refuses to move-in due to not enough room
            """
            # TODO traits
            lines = ("That place is too small for us.", )
            iam.say_line(character, lines)

        @staticmethod
        def accept_moveout(character):
            """
            Output line when the character accepts to move-out from the hero
            """
            # TODO traits
            lines = ("If that's what you want.", "As you wish. Bye.", "I understand. I suppose that was it.")
            iam.say_line(character, lines)

        @staticmethod
        def comment_job_new(character):
            """
            Output line when the character is asked about the job while she/he just started
            """
            # TODO traits
            if character.status == "free":
                lines = ("I'm still adjusting to the new position.", "I'm trying to find my bearings with this new career.")
            else:
                lines = ("I want to serve you better, [mc_ref].", "A new master takes a while to get used to...")
            iam.say_line(character, lines)

        @staticmethod
        def comment_job_very_low_disp(character):
            """
            Output line when a character with very low disposition is asked about the job
            """
            char_traits = character.traits
            if character.status == "free":
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("... *[pC] doesn't want to talk*", "I don't think I'll linger here for a long time.", "I do not wish to about it. Leave me alone.")
                elif "Shy" in char_traits:
                    lines = ("Um... I-I don't think this job is for me...", "I... I'm looking for another job... Sorry.")
                else:
                    lines = ("You're a terrible employer; I have no idea why I'm still working here...", "Maybe I should try to beg in the streets instead of this 'job'...")
            else:
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("...I don't want to live.", "My life is awful. I want to end this...", "... <[pC] looks extremely depressed>")
                elif "Shy" in char_traits:
                    lines = ("...I don't know what to do. This job is awful.", "I should do something, because this won't end well...", "... <[pC] looks extremely depressed>")
                else:
                    lines = ("I wish that I the resolve to kill myself...", "My life in your service is awful.", "Just sell me off to someone. To anyone!")
            iam.say_line(character, lines)

        @staticmethod
        def comment_job_low_disp_high_joy(character):
            """
            Output line when a character with low disposition but high joy is asked about the job
            """
            char_traits = character.traits
            if character.status == "free":
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("I don't like my job.", "You are a bad employer.")
                elif "Shy" in char_traits:
                    lines = ("I-I'm fine. J-just wish I had a better job... No, nevermind.", "I'm fine, I think... I-I mean it's not such a bad job, there are much worse ones!")
                else:
                    lines = ("I'm fine, but I just wish you weren't such a terrible employer.", "As good as can be expected under the circumstances, 'boss'...")
            else:
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("I suppose a slave like me doesn't have much of a choice.", "I follow your orders. That's all.")
                elif "Shy" in char_traits:
                    lines = ("Um, I do my best. Even though my master is... Nevermind, sorry.", "[mc_ref], please be nice to me... I'll work harder, I promise.")
                else:
                    lines = ("I am 'ok'. Just wish I had a better owner...", "I guess it is better than the slave market. A bit.")
            iam.say_line(character, lines)

        @staticmethod
        def comment_job_low_disp_low_joy(character):
            """
            Output line when a character with low disposition and joy is asked about the job
            """
            char_traits = character.traits
            if character.status == "free":
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("I hate my job.", "I'm not in the mood. Why? Because of my job, obviously.")
                elif "Shy" in char_traits:
                    lines = ("I wish I had a better job... S-sorry.", "I-I don't particularly like my job. M-maybe I should try something else...")
                else:
                    lines = ("I'm sad and you are the worst... what else do you want me to say?", "I'm looking for new employment opportunities; that's how I'm feeling...")
            else:
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("...I want another owner.", "I wish I had a better life as a slave.")
                elif "Shy" in char_traits:
                    lines = ("...Yes, [mc_ref]. I'm fine. <you notice tears in [pd] eyes>")
                else:
                    lines = ("There isn't much to say... I'm sad and you're mean...", "I feel like it would be better if you sold me off at the next auction.")
            iam.say_line(character, lines, "sad")

        @staticmethod
        def comment_job_low_joy(character):
            """
            Output line when a character with normal disposition and low joy is asked about the job
            """
            char_traits = character.traits
            if character.status == "free":
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("I like my job. I think.", "Not bad. It's not perfect, but...")
                elif "Shy" in char_traits:
                    lines = ("I'm just a bit sad today, b-but my job is nice.", "Um, I'm ok, I think. You can't be happy all the time, r-right?")
                else:
                    lines = ("Not very chipper but I hope things become better soon.", "Bit sad, if truth be told. Don't want to complain though.")
            else:
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("Nothing to worry about, [mc_ref].", "Good enough.")
                elif "Shy" in char_traits:
                    lines = ("Y-yes, [mc_ref]. I can do it, I know I can!", "It's normal, I suppose...")
                else:
                    lines = ("I'm a bit sad, but you are kind so I'm looking for a brighter tomorrow!", "You've been very nice to me in general, so I won't complain!")
            iam.say_line(character, lines)

        @staticmethod
        def comment_job_high_joy(character):
            """
            Output line when a character with normal disposition and high joy is asked about the job
            """
            char_traits = character.traits
            if character.status == "free":
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("I like my job. Nothing more to say.", "No complaints.")
                elif "Shy" in char_traits:
                    lines = ("I-I like my job. T-thank you.", "I-I'm perfectly fine! <shyly smiling>")
                else:
                    lines = ("I'm happy and this job is not so bad.", "I'm comfortable and content with this arrangement.")
            else:
                if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                    lines = ("I'm satisfied with everything, [mc_ref].", "I am at your service, [mc_ref]. My life is my job.")
                elif "Shy" in char_traits:
                    lines = ("E-everything is well, [mc_ref]! <shyly smiling>", "It's fine. Thanks for asking, [mc_ref]. <blushes>")
                else:
                    lines = ("I'm very well, thank you [mc_ref]!", "I am satisfied with my life and job as a slave.")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def comment_joy_low(character, mood):
            """
            Output line when a character with low joy is asked about how she/he feels
            """
            char_traits = character.traits
            if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                lines = ("I'm not in the mood today.", "I'm just a bit sad. That's all.")
            elif "Shy" in char_traits:
                lines = ("I'm kinda sad...", "I-I cried a bit some time ago. Why? Because I felt like it...")
            else:
                lines = ("I'm depressed. Don't wanna talk about it.", "I'm sad. Isn't it obvious to you?")
            iam.say_line(character, lines, mood)

        @staticmethod
        def comment_joy_neutral(character, mood):
            """
            Output line when a character with normal joy is asked about how she/he feels
            """
            char_traits = character.traits
            if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                lines = ("I'm perfectly calm.", "Don't concern yourself about me, I'm fine.")
            elif "Shy" in char_traits:
                lines = ("Um, I suppose I'm ok.", "N-nothing to worry about, I'm f-fine.")
            else:
                lines = ("I'm ok, I guess.", "Everything is as usual.")
            iam.say_line(character, lines, mood)

        @staticmethod
        def comment_joy_high(character, mood):
            """
            Output line when a character with high joy is asked about how she/he feels
            """
            char_traits = character.traits
            if "Impersonal" in char_traits or "Dandere" in char_traits or "Kuudere" in char_traits:
                lines = ("I'm pretty happy. I think.", "I'm fine. <barely smiling>")
            elif "Shy" in char_traits:
                lines = ("I think I'm... happy.", "<shyly smiling> I'm in a good mood today...")
            else:
                lines = ("I'm quite happy.", "You could say I enjoy my life.")
            iam.say_line(character, lines, mood)

        @staticmethod
        def incest_kiss(character):
            """
            Output line when the character kisses the hero, but contemplating about the incest they commit
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("It's okay for siblings to kiss, isn't it?", "Do you like your sister's kisses?")
            elif "Yandere" in char_traits:
                lines = ("Such an act... kissing... my [hero.hs]...", "I wonder... if you should proceed to do this... to your sister?")
            elif "Dandere" in char_traits:
                lines = ("This is different from the kisses we had when we were little...", "...[hero.hs], you taste pretty good.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Do you like... kissing... your sister?", "[hero.hs], you're so gentle...")
            if "Imouto" in char_traits:
                lines = ("I want to keep kissing you, [hero.hss]! Hehe ♪", "How does it taste to kiss your sister?")
            elif "Kamidere" in char_traits:
                lines = ("I'm kissing with my [hero.hs]... T...this is just wrong...", "You love your sister that much..?")
            elif "Tsundere" in char_traits:
                lines = ("D...doing such lewd things even though we're siblings... Isn't this incest?", "Doing such things to your sister... *sigh* Well, it can't be helped...")
            elif "Kuudere" in char_traits:
                lines = ("I'm kissing my [hero.hs] like this... I'll never be forgiven for doing this...", "Ugh... I... I can't believe I have such a lewd [hero.hs]...")
            elif "Ane" in char_traits:
                lines = ("You really like my lips, [hero.hs]? ♪", "Do you really like kissing your sis that much?")
            elif "Bokukko" in char_traits:
                lines = ("What's it like to kiss your sister? Does it taste good?", "Going after your sister? Man, what a hopeless [hero.hs] you are... ♪")
            else:
                lines = ("Isn't it a bit strange to kiss your sister?", "I'm your sis... Are you really okay with that?")
            iam.say_line(character, lines, "uncertain")

        @staticmethod
        def accept_kiss(character):
            """
            Output line when the character accepts the kiss of the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("*kiss* Kissing is nothing that special.", "*kiss* My body's getting hotter.", "*kiss*... Hn... I can still taste you.", "*kiss* Your lips feel a little dry... *lick lick lick* That's much better.")
            elif "Yandere" in char_traits:
                lines = ("*kiss* *slurp* *slosh* <[p]'s making patterns with [pd] tongue>", "*kiss* ... *giggle* *kiss*", "momph *kiss* dufu *kiss* gae *kiss* mnn... <trying to talk, perhaps?>", "...Haah... It tastes like you... Hehe ♪", "Huff, *smooch*, *slurp*... Hehe, I got my tongue inside...")
            elif "Shy" in char_traits and dice(50):
                lines = ("Huh... *kiss*... We k-kissed...", "*kiss*  We... kissed... <gives you a dreamy smile>", "Ahm, *slurp, kiss*......kissing feels good...", "*kiss* Nnn... <looks at you dreamily>", "<Gently kisses you> H...how's this? Does it f... feel good...? It... it feels good for me...", "*kiss* ...Did I do that right...?", "Is this really ok...? ...*kiss*...", "<closes [pd] eyes> *kiss* hn...")
            elif "Nymphomaniac" in char_traits and dice(35):
                lines = ("*kiss* Mmmf ♪　Nnh, nnf, mmmf... No, we're gonna kiss more ♪ ...nnf, mmmf♪", "*kiss* This isn't going to end with just a kiss, right?", "*kiss* Even though we're just kissing... I'm already...")
            elif "Dandere" in char_traits:
                lines = ("*kiss* ...Where did you learn to kiss like this?", "*kiss* ...Not enough. More.", "Nn, aah, haah... You're tickling my tongue...", "*kiss*... *smooch*... *huff*... your breath... so hot...", "Do you desire my lips? *kiss*", "*kiss*...  Hn... you like kissing...?")
            elif "Kuudere" in char_traits:
                lines = ("Ok, but don't go overboard. *kiss*", "Nhn... Ah... Do you like my kisses?", "Nh...chu...nnhu...chu... Nhn...chu... Y-you're overdoing it, idiot...", "I-I suppose we can... *kiss*", "*kiss* Ah... J-Jeez, that was too sudden...", "Mmmh, nn, chu, mmchu, nn... Hoh is id, my kish? Nmu, nn, chupuru... nfuu ♪", "Mmh... Nmmh?! You bit my lips! Geez!")
            elif "Tsundere" in char_traits:
                lines = ("*kiss* !? Wh-what do you think you're doing all of a sudden...? Geez.", "Nnn, nn... Ah... Done already...? !? I-I didn't say anything!", "*kiss*, hn, hnn... Puah! Geez! How long are you planning on doing that?!", "*kiss*, *lick*... Hn aah... Geez, too much tongue!", "Hn *kiss*... hnn... Y-you're embarrassing me, geez...", "*kiss* ... Geez! Who told you it was ok to kiss!", "*smooch*, hnn... I don't want, *kiss*, you to, *slurp*, let me go...", "Mmh, chu, nnh... mmmhah!　Jeez, how long are you gonna do this for!")
            elif "Ane" in char_traits:
                lines = ("*kiss* ...Hmhm, there's a kiss mark on you.", "*kiss* ...Hmhm, you're pretty good.", "*kiss* Kissing is a token of my affection...", "*kiss*...Hn... Just having our lips touch like this... makes me so excited.", "*kiss* My heart just beat faster for a bit.", "*kiss* That was a wonderful kiss.", "*kiss* Well now, it was a pleasant experience ♪", "*kiss*... My, you are a good kisser!")
            elif "Bokukko" in char_traits:
                lines = ("*kiss*... What, what? You like kissing me that much?", "Haa, *kiss*, *smooch*, hnm, Puaah! ...haa haa, I totally forgot, to breathe, haaa...", "*kiss*... Hm...? What did you eat today...?", "*smooch*... Hm, if you can lick, so can I...", "*Kiss* I wonder, was it good?", "*kiss* You're skilful, aren't ya?", "*kiss*... Mmmph, nn, mmh, chu, so lewd, geez...")
            elif "Imouto" in char_traits:
                lines = ("*smooch* Ehehe, that's a bit embarrassing ♪", "*smooch*, ahm, *lick*... My tongue moved by itself...", "*kiss*, hn... *slurp*, *kiss*... Ehehe♪ My tongue, it feels good right ♪", "*kiss* Hnn, you're not going to use your tongue? Huhu ♪", "*lick, kiss*... *lick*, hn...  I licked you a lot.. ♪", "*smooch* Hehe, we kissed ♪", "Hn, *kiss*... Haa... Your breath is tickling me...", "Ehehe, kiss time ♪ *kiss*", "Mhm, nnh, chu, hmm...nnh, mmh... Puah!　Gosh, I'm out of breath...")
            elif "Kamidere" in char_traits:
                lines = ("*kiss* How about at least trying to look a bit happier?", "*kiss*... Felt good, right?", "*smooch*... Getting excited?", "*kiss*... I'll leave you with that much.", "Hn, *smoooch*...  Uhuh, now you've got a hickey ♪", "*Kiss*... Haha, why's your face getting so red? ♪", "I, too, can be sweet sometimes... *kiss*, ahm... *smooch*...")
            else:
                lines = ("Don't say anything.... *kiss*", "*kiss*, *lick*, I like, *kiss*, this...", "*kiss*, hmm... *sigh*, kissing feels so good...", "*kiss*...  My heart's racing ♪", "Hmm... *kiss, kiss*, ahm,.. I like... kissing... Hn, *smooch*...", "*slurp, kiss* Kissing this rough... feels so good.", "*kiss* You're sweet...", "Ahm... *kiss, lick*... nnn... Do you think touching tongues is a little... sexy?")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def refuse_kiss(character):
            """
            Output line when the character refuses the kiss of the hero
            """
            char_traits = character.traits
            mood = "indifferent"
            if "Impersonal" in char_traits:
                lines = ("I see no possible benefit in doing that with you so I will have to decline.", "Denied. Please refrain from this in the future.")
            elif "Shy" in char_traits and dice(50):
                mood = "shy"
                lines = ("I... I don't want!", "W-we can't do that. ", "I-I don't want to... Sorry.")
            elif "Imouto" in char_traits:
                mood = "angry"
                lines = ("Noooo way!", "...I-I'm gonna get mad if you that that stuff, you know? Jeez!", "Y-you dummy! Stay away!")
            elif "Dandere" in char_traits:
                lines = ("You're no good...", "You should really settle down.", "No, not with you.")
            elif "Tsundere" in char_traits:
                mood = "angry"
                lines = ("I'm afraid I must inform you of your utter lack of common sense. Hmph!", "You are so... disgusting!", "You pervy little scamp! Not in a million years!")
            elif "Kuudere" in char_traits:
                mood = "angry"
                lines = ("...Perv. Stay away from me, got it?", "...It looks like I'll have to teach you about this little thing called reality.", "O-of course the answer is no!")
            elif "Kamidere" in char_traits:
                mood = "angry"
                lines = ("Wh-who do you think you are!?", "W-what? Of course I'm against that!", "The meaning of 'not knowing your place' must be referring to this, eh...?")
            elif "Bokukko" in char_traits:
                lines = ("He-hey, settle down a bit, okay?", "You should keep it in your pants, okay?", "Hmph! Well no duh!")
            elif "Ane" in char_traits:
                lines = ("If I was interested in that sort of thing I might, but unfortunately...", "No. I have decided that it would not be appropriate.", "I think that you are being way too aggressive.")
            elif "Yandere" in char_traits:
                lines = ("I've never met someone who knew so little about how pathetic they are.", "...I'll thank you to turn those despicable eyes away from me.", "Stay away from me.")
            else:
                lines = ("With you? Of course not!", "Huh?! No, I don't want to! Pervert...", "Woah, hold on there. Maybe after we get to know each other better.")
            iam.say_line(character, lines, mood, ("sweat", "reset"))

        @staticmethod
        def accept_flirt(character):
            """
            Output line when the character accepts the flirt of the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("To express it in words is very difficult...", "Infatuation and love are different. Infatuation will fade, but love's memory continues forever.", "I think it is a good thing to be loved by someone.")
            elif "Shy" in char_traits and dice(40):
                lines = ("Lovers... Th-they're supposed to...hold hands, after all... Right?", "Wh-what comes after a k-kiss is... It's... Awawa...", "If it's the person you love, just having them turn around and smile... Is enough to make you happy...", "Love... sure is a good thing...")
            elif "Nymphomaniac" in char_traits and dice(40):
                lines = ("*sigh* I always have such a high libido...", "Um... Love can start from lust... right?", "If you are in love, having sex is totally normal, right?", "People are no more than animals, so it's only natural to copulate...", "Well, doing perverted stuff is proof that you're healthy.", "Me thinking about sex? Not at all... Great. Now that you brought it up...")
            elif ("Bisexual" in char_traits or "Lesbian" in char_traits) and dice(20):
                lines = ("Love runs deeper than gender.", )
            elif "Dandere" in char_traits:
                lines = ("If you like them, you like them. If you hate them, you hate them. That's all there is to it.", "My dream yesterday... It was so lovey-dovey and erotic.", "Getting close to people other than the one you love is kind of...", "You can still live a good life without a lover, don't you think?")
            elif "Tsundere" in char_traits:
                lines = ("M...men and women feel arousal differently.... F-f-forget what I just said!", "Thick and hard? What the... You idiot, what are you saying! That's not what you meant? ... You idiot!", "E-even I want to be a good bride someday, you know...?", "Things like l-love or affection, are all excuses.")
            elif "Kuudere" in char_traits:
                lines = ("To feel the same feelings towards each other... To be partners for life... That's what I long for.", "Two people in love devoting themselves to each other, that sounds like pure bliss to me...", "True love isn't about showing off to everyone else... It's the small things you do for your partner that matter.", "There's gotta be someone willing to support me out there somewhere...", "Chance encounters only happen with both time and luck... Well, I suppose you could call it fate.")
            elif "Imouto" in char_traits:
                lines = ("That's weird... Today's love fortune was supposed to be a sure thing... Hmm...", "That book is very interesting... A boy and a girl who you'd think are twins get together, but in fact...", "L-love and affection and th-that stuff, I don't really get it very well...", "If I'm going to date someone, they should be rich ♪, and want kids ♪ And they should be totally committed to me ♪")
            elif "Ane" in char_traits:
                lines = ("You're deciding who will be your partner for life.　It would be strange not to be worried about it.", "I think just having the one you love beside you is the ultimate happiness.", "I need a person whom I can rely on.", "Lost loves are important to build character, I think.", "As you've probably noticed, I'm the devoted type ♪", "Of course, I'd wanna stay by my loved one's side. Or, rather than being by their side, it's more, like, I want to support them?")
            elif "Kamidere" in char_traits:
                lines = ("Seriously, how can I... think of such unpleasant thoughts...", "When my body gets hot, it's like my discipline starts to crumble...", "There are things more important than physical infatuation.", "Making lovers my playthings is a simple matter for one such as I. Eheh!", "Love is nothing but an expression of ego, you know.", "You can't disobey your instincts. Isn't keeping up this charade painful for you?")
            elif "Bokukko" in char_traits:
                lines = ("Love is a competition! A conflict! A war!", "If the other person won't give you a second glance, you need to make 'em. It's simple, really.", "Love, hmm ♪ ... Hn, just thinking about it makes me sort of embarrassed...", "I'm gonna be the bestest wife!", "Is this that fate thing they're talking about?")
            elif "Yandere" in char_traits:
                lines = ("Huhu, a girl in love is invincible ♪", "Nothing motivates you quite like 'love', huh...", "If it's just with their mouth, everyone can talk about love. Even though none of them know how hard it is in reality...", "I want to try many different ways to kiss, I think...")
            else:
                lines = ("Getting your heart broken is scary, but everything going too well is kinda scary for its own reasons too.", "One day, I want to be carried like a princess by the one I love ♪...", "Hehe! Love conquers all!", "I'm the type to stick to the one I love.", "Being next to someone who makes you feel safe, that must be happiness...", "Everyone wants to fall in love, I suppose. Don't you think?")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def refuse_interaction(character):
            """
            Output line when the character refuses an interaction with the hero
            """
            if character.status == "free":
                char_traits = character.traits
                mood = "indifferent"
                if "Impersonal" in char_traits:
                    lines = ("Denied.", "It's none of your business.", "...")
                elif "Shy" in char_traits:
                    mood = "shy"
                    lines = ("I-I won't tell you... ", "I don't want to talk... sorry.", "W-Well... I d-don't want to tell you...", "Ah, ugh... Do I have to tell you...?")
                elif "Dandere" in char_traits:
                    lines = ("I don't feel the need to answer that question.", "...Let's talk later...maybe.", "I'm not going to tell you.")
                elif "Kuudere" in char_traits:
                    lines = ("I've got no reason to tell you.", "I'm not in the mood for that right now.", "Why do I have to tell you?")
                elif "Tsundere" in char_traits:
                    lines = ("Hmph! Who would tell you!", "Eh? You expect me to tell you?", "It's none of your business.")
                elif "Imouto" in char_traits:
                    lines = ("Uhuhu, I won't tell you!", "It's a secret!", "Umm, is it bad if I don't answer...?")
                elif "Yandere" in char_traits:
                    lines = ("I'm not in a mood for chatting.", "...I don't feel like answering.")
                elif "Kamidere" in char_traits:
                    lines = ("And what will hearing that do for you?", "And what good would knowing that do you?")
                elif "Ane" in char_traits:
                    lines = ("Sorry, can we talk later?", "Sorry, but I don't want to answer.", "*sigh*... Don't you have anything else to do?")
                elif "Bokukko" in char_traits:
                    lines = ("Eh, say what?", "Why do I hafta give you an answer?", "I'm not gonna answer that.")
                else:
                    lines = ("I don't want to answer.", "I don't want to talk now.", "Must I give you an answer?")
                iam.say_line(character, lines, mood)
            else:
                narrator(choice(["But it only led to awkward silence.", "But it had no positive effect whatsoever.", "But it was kind of one-sided."]))

        @staticmethod
        def accept_hug(character):
            """
            Output line when the character accepts a hug from the hero
            """
            char_traits = character.traits
            mood = "confident"
            if "Impersonal" in char_traits:
                lines = ("Yes? Is something wrong?", "Having your arms around me is so comfortable.", "You are... very warm.", "I'm for you to embrace.", "If you want to feel my warmth, it would be my pleasure.")
            elif "Shy" in char_traits and dice(30):
                mood = "shy"
                lines = ("I feel like I'm safe.", "Being so close...", "A... are you feeling cold? It's m... much warmer like this, right?", "It's... it's okay to do it like this, right?", "Y-yes... Please hold me... hold me tight...")
            elif "Nymphomaniac" in char_traits and dice(25):
                mood = "shy"
                lines = ("Geez, you're such a perv ♪", "Hau ♪... I'm...starting to feel funny...", "Being so close... Exciting?")
            elif "Kamidere" in char_traits:
                lines = ("Having your arms around me is so comfortable.", "When you're so gentle I get embarrassed all of a sudden...", "D-did something happen?", "You can hear the sound of my heart beating.")
            elif "Kuudere" in char_traits:
                lines = ("I-I'm not a body pillow...", "...Jeez, how long are you going to do this? ...It's embarrassing.", "W-what are you doing so suddenly?!", "W-what are you nervous for? I'm the one who's embarrassed here...", "Oh...? This is nice, isn't it...? Being just like this.")
            elif "Dandere" in char_traits:
                lines = ("...My face is burning.", "It feels better this way.", "Ah... Hold me tighter.", "Hmhmm... I expected perverted things... Pity.", "...Nice to see you too, [mc_ref].")
            elif "Tsundere" in char_traits:
                lines = ("H-Huh? Why is my pulse getting so...", "Hey you, who said you could get this close without permission?", "D-don't do anything weird, okay...?", "I-I'm not n-nervous or anything...", "It's... it's okay to do it like this, right?", "How long do you plan to... It's embarrassing!", "I-it's not like getting a hug is surprising, right?")
            elif "Imouto" in char_traits:
                lines = ("Okay, I'll comfort you...  There, there ♪", "<Hugs you back with a smile> Heheh ♪ Let's stay like this just a bit more ♪", "What, what? Did something happen?", "Come, come! Come to my chest! ♪", "I-isn't something touching...?　R-really?", "Hehehe... It feels kinda warm...")
            elif "Ane" in char_traits:
                lines = ("Well, aren't you too close ♪", "Hm? You're kind of close... Oh, so that's what this is all about...", "Fufu, you're like a spoiled kid...♪", "Come on, hold me tighter.", "There's no helping it. Only a little longer, got it?", "Hn... Yeah, alright, if it's just a hug...")
            elif "Yandere" in char_traits:
                lines = ("Mhmhm ♪　Go ahead, come a little closer ♪", "Nnh...more, squeeze me tighter...", "Um... Don't hold out on me, okay...? Go a little harder...", "It's just a hug, but... It feels so nice ♪", "Let me melt in your arms...")
            elif "Bokukko" in char_traits:
                lines = ("How's it feel, holding me...?", "Wha... What's this? Heartbeat?", "Doesn't this make you happy?", "Yeah. It really feels nice to embrace you ♪", "Geez, quit flailing around. It's just a hug!", "Ah, hey... Fine, just a little...")
            else:
                lines = ("There's no helping it, huh? Come to me.", "Whoa there... Are you all right? Hold onto me tightly.", "Can you hear my heartbeat too?", "Yes, you can hold me tighter if you wish.", "...Hmm, it feels good to be held like this ♪", "<Hugs you tightly> What do you think? Can you feel me up against you?")
            iam.say_line(character, lines, mood, ("zoom_slow", "reset"))

        @staticmethod
        def refuse_hug(character):
            """
            Output line when the character refuses a hug from the hero
            """
            char_traits = character.traits
            mood = "indifferent"
            if "Impersonal" in char_traits:
                lines = ("Please get off me, I can't breathe.", "<she moved back you as you tried to hug her>")
            elif "Shy" in char_traits and dice(50):
                mood = "shy"
                lines = ("Ah... ah! W... what are you doing!?", "Please, leave me alone...", "W-w-w-what are you doing so suddenly?!")
            elif "Dandere" in char_traits:
                lines = ("...Please don't get so close.", "I won't let you.", "<Steps back> No.")
            elif "Kuudere" in char_traits:
                lines = ("<Shrinks back> Don't get weird.", "Hands off.")
            elif "Ane" in char_traits:
                lines = ("[mc_ref], I don't need comforting or anything....", "I'm sorry, I'm not really in the mood right now.", "Sorry, but I don't want to.", "Please, keep your distance.")
            elif "Kamidere" in char_traits:
                lines = ("<Steps back> W...what are you... doing!?", "<Escapes your embrace> This... This is embarrassing after all... Stop it.", "Stop it. This is embarrassing.")
            elif "Imouto" in char_traits:
                lines = ("Kya! He- hey, Let go of me...", "<Escapes your embrace> No waay!", "<slipped away from you> Hehe, you won't catch me ♪", "Uuu... I'm boooored! Let's do something else!")
            elif "Tsundere" in char_traits:
                lines = ("No, cut it out!", "W-What's with you all of a sudden!?", "W-Why do we have to do that!?")
            elif "Bokukko" in char_traits:
                lines = ("<Escapes your embrace> Nice try!", "Kya! He-hey, let go of me!", "Wha-wha-what is this about? Let me go!")
            elif "Yandere" in char_traits:
                lines = ("<Steps back> Don't think so.", "Let me go at once!", "You're making me uncomfortable.")
            else:
                lines = ("What are you doing all of a sudden!?", "[mc_ref], you're too close, too clooose.", "What are you doing! Please don't touch me!", "<Steps back> I don't want to.")
            iam.say_line(character, lines, mood)

        @staticmethod
        def incest_touch_cheek(character):
            """
            Output line when the character allows the hero to touch her/his cheek, but contemplating about the incest they commit
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Is it okay for siblings to touch like that?", "Do you like your sister?")
            elif "Yandere" in char_traits:
                lines = ("Such an act... touching... from my [hero.hs]...", "I wonder... if you should proceed to do this... to your sister?")
            elif "Dandere" in char_traits:
                lines = ("This is different from the time when we were little...", "...[hero.hs], your hands are so comforting.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Do you like... touching... your sister?", "[hero.hs], you're so gentle...")
            if "Imouto" in char_traits:
                lines = ("I want you to hold me, [hero.hss]! Hehe ♪", "How does it feel to touch your sister?")
            elif "Kamidere" in char_traits:
                lines = ("Letting my [hero.hs] touch like this... T...this is just wrong...", "You love your sister that much..?")
            elif "Tsundere" in char_traits:
                lines = ("D...doing such lewd things even though we're siblings... Isn't this incest?", "Doing such things to your sister... *sigh* Well, it can't be helped...")
            elif "Kuudere" in char_traits:
                lines = ("I let my [hero.hs] touch like this... I'll never be forgiven for doing this...", "Ugh... I... I can't believe I have such a lewd [hero.hs]...")
            elif "Ane" in char_traits:
                lines = ("You really like me, [hero.hs]? ♪", "Do you really like touching your sis that much?")
            elif "Bokukko" in char_traits:
                lines = ("What's it like to touch your sister? Does it feel good?", "Going after your sister? Man, what a hopeless [hero.hs] you are... ♪")
            else:
                lines = ("Isn't it a bit strange to touch your sister?", "I'm your sis... Are you really okay with that?")
            iam.say_line(character, lines, "uncertain")

        @staticmethod
        def accept_touch_cheek(character):
            """
            Output line when the character accepts a cheek-touch from the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("*blushes*... Hn... I like this.", "*blushes* You want something?", "*closes [pd] eyes*... Hn... I can feel you.")
            elif "Yandere" in char_traits:
                lines = ("<puts [pd] hand on yours> ... Hn... good...", "*blushes* ... *giggle* This I like ♪", "Mph.. *blushes* ... *smiles*")
            elif "Shy" in char_traits and dice(50):
                lines = ("Huh... *blushes*... You touched me...", "*blushes*  You, your hand touched... <gives you a dreamy smile>", "Ahm, *smiles*......this feels good...", "*smiles* Nnn... <looks at you dreamily>", "*blushes* H...how's does this f... feel so good...?", "*blushes* ... It... it feels good for me...", "Is this really ok...? ...*smiles*...", "<closes [pd] eyes> hn...")
            elif "Dandere" in char_traits:
                lines = ("*smiles* ... *looks into your eyes* ...Yes?", "*blushes* ...Hn...Not enough. More.", "Nn, aah, haah... Your hands are cold *giggle*", "*looks into your eyes*... Wanna say something? ...", "*smiles*...  Hn... you like to touch me...?")
            elif "Kuudere" in char_traits:
                lines = ("*blushes* Ok, that is fine by me.", "Nhn... Do you want to tell me something?", "Nh...*smiles* This makes me feel good.", "Ah... J-Jeez, that want to make me blush?", "Mmh... Nmmh?! Did you wash your hands?")
            elif "Tsundere" in char_traits:
                lines = ("Huh!? Wh-what do you think you're doing? Geez.*blushes*", "Nnn, nn... *blushes* Ah... Done already...? !? I-I didn't say anything!", "*blushes*, hn, hnn... Puah! Geez! How long are you planning on doing that?!", "Mmh, *blushes* nnh... Jeez, how long are you gonna do this for!")
            elif "Ane" in char_traits:
                lines = ("*smiles* ...Hmhm, this makes me feel safe.", "Hn... <puts [pd] hand on yours> ... Thanks [mc_ref].", "My, you know how to comfort me *smiles*...")
            elif "Bokukko" in char_traits:
                lines = ("... Hn.. What, what? You like touching me that much?", "Haha... I hope your hands are not dirty ♪", "This feels good, thanks!")
            elif "Imouto" in char_traits:
                lines = ("*blushes* Ehehe, this is a bit embarrassing ♪", "*giggle*, ahm... yes...", "*blushes*, hn... *giggle*... Ehehe♪", "Ehehe, it feels good right ♪")
            elif "Kamidere" in char_traits:
                lines = ("*smiles*... Felt good, thanks!", "*smiles*... Want to tell me more?", "*blushes*... I'll leave you with that much.")
            else:
                lines = ("Don't say anything.... hn...", "*smiles*, hmm... *sigh*, this feels so good...", "*dreaming*...  that is right.")
            iam.say_line(character, lines, "shy", ("zoom_fast", "reset"))

        @staticmethod
        def refuse_touch_cheek(character):
            """
            Output line when the character refuses a cheek-touch from the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I see you lack common sense.", "It is better if you don't do that.", "It hurts.", "Why are you touching me? So annoying.")
            elif "Yandere" in char_traits:
                lines = ("Hey, stop! Don't do that!", "Touching is forbidden. Stop.", "You have some nerve putting your hands on me!", "Could you refrain from touching me with your dirty hands?")
            elif "Shy" in char_traits and dice(50):
                lines = ("No... D-don't... Do that!", "W-w-what? D-don't do it please...", "Wah! Why would you even try?!", "I think you should stop right there.", "P-please stop doing this!")
            elif "Dandere" in char_traits:
                lines = ("Why are you touching me without permission!?", "If you keep doing that, I'm leaving.", "Please do not do it again.", "Stop harassing me!")
            elif "Tsundere" in char_traits:
                lines = ("Kyaa-! Y... you idiot!", "Ow! How dare you!", "Y-you dumbass! Have you lost your mind?!", "Stop. That. Riiiight. Nooooooow!", "Hey, you creep, what do you think you're doing!?", "Aah! C...cut it out!", "Hya, what are you doing, it's dirty!")
            elif "Kuudere" in char_traits:
                lines = ("What?! What is the meaning of this? Hey!", "...Hey! Why are you touching me?!", "Show some restraint with your indecent actions.", "...Tch. What a perv.", "Hmph. You should be grateful I'm so lenient today.")
            elif "Ane" in char_traits:
                lines = ("You're too sure about yourself. Consider a bit more self-restraint, okay?", "Come on, don't touch me now.", "I'm gonna scold you if you continue.", "That really wasn't appropriate. Keep your distance.")
            elif "Kamidere" in char_traits:
                lines = ("D-don't be touching me!", "What are you doing, geez!", "I don't want your touch!", "S-stop that! Get your hands away from me!", "Hya! Stop acting like a pervert!", "Geez, stop that!")
            elif "Bokukko" in char_traits:
                lines = ("Umm... Don't go touchin' me...", "Da heck ya' doing?", "Owwie... Geez... why'd you do that..?", "Whoa, what're you doing, geez...", "Fweh, hey, don't touch me!", "What the hell!? What are you doin'!?")
            elif "Imouto" in char_traits:
                lines = ("Geez! If you don't stop, I'm gonna get mad!", "Nooo, what are you doing!?", "Hya! Don't touch me!", "O-owowowowow! Sto-, Wai-, AGYAAA!!", "Hey! What are you doing?!")
            else:
                lines = ("Geez! Try again if want to see me angry.", "Whoa! Hey, don't just touch me out of the blue!", "Do this sort of thing with someone else...!", "Hey! Quit it, already!", "Aah! C...cut it out! ", "What are you doing, you sneak?")
            iam.say_line(character, lines, "angry", ("angry", "reset"))

        @staticmethod
        def accept_grab_butt(character):
            """
            Output line when the character accepts a butt-grab from the hero
            """
            char_traits = character.traits
            mood = "happy"
            if "Impersonal" in char_traits:
                lines = ("...That's it? You're not going any further?", "Aah... my hips... it feels... kind of strange.", "Hnn, fuaah... if you touch there, I won't be able to hold myself back...")
            elif "Yandere" in char_traits:
                lines = ("<[pC] joyfully slaps you back.>", "Ha... That touching... so lewd...", "Such a perverted hand...", "You'd better have a follow-up to that, [mc_ref] ♪")
            elif "Shy" in char_traits and dice(50):
                mood = "shy"
                lines = ("Aauh... Wh-what's up...?", "Nwa, Y-you surprised me...", "Umm... I get nervous when others touch me.", "U-uhm... touch me more gently, please...")
            elif "Nymphomaniac" in char_traits and dice(40):
                lines = ("...Alright, any lower and I'll have to charge extra.", "Hehehe, I just got a bit horny...", "That... Ahh... Hehe... So perverted...", "Hnn.... you can touch me in more interesting places if you want...", "You're lewd ♪", "Ahaha, you're pervy ♪", "If you keep touching me, I'll touch you back ♪")
            elif "Kamidere" in char_traits:
                lines = ("Hyaa! G-Geez! Don't do that out of the blue.", "You can touch me just a bit... Just a bit, got it?", "Hn, ah... If you touch like that, it's sort of perverse...", "Hn... How is it? Have I got a tasty ass?", "Ahn... It looks like I've found someone with perverted hands.")
            elif "Kuudere" in char_traits:
                lines = ("Wha! Such a surprise attack is not fair!", "Even if you touch me, nothing interesting is going to happen.", "Kyah!? You touched me someplace weird, that's why...!", "Kuh... Why do I feel so...", "...I don't mind if it's you.")
            elif "Dandere" in char_traits:
                lines = ("Is touching me really that fun? I don't really get it... but if you're enjoying it, then sure, I guess.", "If it wasn't you I'd have filed a city guards report.", "...I feel aroused.", "Nn?! This is just... a physiological reaction...", "Nnn... Somehow, my body is getting hotter...")
            elif "Tsundere" in char_traits:
                lines = ("Wha! D-don't be such a perv when you touch me!", "Kuh... This is so humiliating, so disgraceful... But I...", "Hhmn... My-My... you love my body so much? Of course you do, it can't be helped.", "Ah! Y-y-you idiot... D...don't do that!")
            elif "Bokukko" in char_traits:
                lines = ("Geez, you're hopeless ♪", "Hyah! What's that, that's sneaky!", "Hm? If you do that, I'll treat you roughly too ♪", "Hey, c'mon... don't go touching me anywhere weird... Ah!")
            elif "Imouto" in char_traits:
                lines = ("Hyaa! T-that tickles...!", "So lewd...Uhuhuhuhu.. ♪", "Wha?! Why you are touching me there?", "Uh, I'm spoiled, huh? Ehehe... I... like it... Ahh...")
            elif "Ane" in char_traits:
                lines = ("*giggle* How troublesome ♪", "So pushy...  Are you proposing or something?", "Hmhm, don't feel like you have to hold back, hey?", "Hmhm, are you getting turned on?", "Your appetite for lust is proof of your health.")
            else:
                lines = ("Hya! If you keep doing that, I'll get in the mood...", "Teasing people isn't good, you know ♪", "Kya...  Doing this all of sudden, that surprised me.", "Whoa... We're energetic, aren't we...", "Hya! S-such shameful hands... hnn", "Ooh! Are you hinting at something there, [mc_ref]? ♥")
            iam.say_line(character, lines, mood, ("zoom_fast", "reset"))

        @staticmethod
        def refuse_grab_butt(character):
            """
            Output line when the character refuses a butt-grab from the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I see you lack common sense.", "How about you stop your pointless struggling?", "It hurts.", "Why are you touching me? So annoying.")
            elif "Yandere" in char_traits:
                lines = ("Hey, it hurts! Stop it!", "Touching is forbidden. That hand, don't blame me if it falls off.", "You have some nerve putting your hands on me!", "Could you refrain from touching me with your dirty hands?")
            elif "Shy" in char_traits and dice(50):
                lines = ("No... D-don't... Do that!", "W-w-what? D-don't do it please...", "Wah! Th-That scared me!", "I think you shouldn't do p-perverted things..", "P-please stop doing this!")
            elif "Dandere" in char_traits:
                lines = ("Why are you touching me without permission!?", "If you have the free time to be doing that, I'm leaving.", "That hurts... Please do not do it again.", "Stop your sexual harassments.")
            elif "Tsundere" in char_traits:
                lines = ("Kyaa-! Y... you idiot!", "Ow! How dare you!", "Y-you dumbass! You pervert!", "Quit. That. Riiiight. Nooooooow!", "Hey, you creep, what do you think you're doing!?", "Aah! C...cut it out!", "Hya, what are you doing, it's dirty!", "Fuwa! Don't rub such weird places!")
            elif "Kuudere" in char_traits:
                lines = ("What?! What is the meaning of this? Hey!", "...Hey! Why are you touching me?!", "Show some restraint with your indecent actions.", "...Tch. What a perv.", "Hmph. You should be grateful I'm so lenient today.")
            elif "Ane" in char_traits:
                lines = ("You're too lustful. Consider a bit more self-restraint, okay?", "Come now, don't touch anywhere inappropriate.", "I'm gonna scold you if you continue.", "That really wasn't appropriate. Keep your distance.")
            elif "Kamidere" in char_traits:
                lines = ("D-don't be touching anywhere weird!", "What are you doing, geez!", "Don't touch me in weird places!", "Hyauu! Hey! Nn, sexual harassment is not allowed!", "Hnyaah! Geez, don't grab me in weird places!", "S-stop that! Despicable!", "Hya! Stop acting like a pervert!", "Geez, stop that!")
            elif "Bokukko" in char_traits:
                lines = ("Umm... Don't go touchin' me...", "Da heck ya' doing?", "Owwie... Geez... why'd you do that..?", "Whoa, what're you doing, geez...", "Fweh, hey, don't touch that!", "What the hell!? What are you doin'!?")
            elif "Imouto" in char_traits:
                lines = ("Geez! If you don't stop, I'm gonna get mad!", "Nooo, what are you doing!?", "Hya! Don't touch me there!", "*sob* that hurts...", "O-owowowowow! Sto-, Wai-, AGYAAA!!", "Hey! Where are you aiming?!")
            else:
                lines = ("Geez! If you don't stop, I'll get angry.", "Whoa! Hey, don't just touch me out of the blue!", "[mc_ref]...! I'd rather you do this sort of thing with someone else...!", "Hey! Quit it, already!", "Aah! C...cut it out! ", "What are you doing over there, you sneak?", "Hmph, how unromantic! Know some shame!")
            iam.say_line(character, lines, "angry", ("angry", "reset"))

        @staticmethod
        def accept_grab_breast(character):
            """
            Output line when the character accepts a breast-grab from the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Hn... You shouldn't grope people... Ah... ♪", "This is...unexpectedly embarrassing.", "...Do you like my tits?", "You're rubbing my nipples.", "Uh... my chest, it feels so tight.", "Hnn, no matter how hard you squeeze, nothing will come out, auh.", "Hnn, you don't need to rub so hard...", "Can't control yourself?")
            elif "Half-Sister" in char_traits and dice(30):
                lines = ("Ah... tell me... what do you think about your sister's body...?", "It's... it's wrong to lust for your sister....", "A-are you getting excited over your sister's body?", "I wonder... if you should proceed to do this... to your sister?")
            elif "Shy" in char_traits and dice(50):
                lines = ("Ah... your hand is so gentle...", "When I get touched so much, [mc_ref], I get confused...", "Aah... N...no... If you do it like that...I...", "P... please be more... gentle...", "Y-yes... You can... like this...", "Uah, ah, hnn, I'm sorry, I didn't know I was so perverted...")
            elif "Dandere" in char_traits:
                lines = ("Nn... Right there...is good.", "I love when you slowly rub my breasts.", "Aah... t...this is also... a form of massage... aaah...", "Hnn, is my chest... soft...?", "M...more... my body... feels so hot...", "Becoming... more perverted... by the minute...", "Ah. Feels much better than rubbing myself...", "My nipples are tingling... Feels weird...")
            elif "Kuudere" in char_traits:
                lines = ("Hnn, you don't need to rub so hard...", "I... Ah... Do you like my boobs...?", "Ah... You've got some nerve, grabbing me like that all of a sudden...", "Nn!? Don't pinch...! ...Ahn!", "Ngh... These things just get in the way...", "Nn...mm... Are you...trying to make them bigger...?")
            elif "Tsundere" in char_traits:
                lines = ("Kya, hnn, geez, you've got such perverted hands!", "No... This is no good... Ahhh... Doing a thing like this...", "Hey! Not there... Don't be so pushy. You can't...", "Nnnaaah! Stop being so rough, you dummy...!", "Kyauu! You idiot! Stop pulling on them!", "N...no... I...I don't feel a thing at all.", "Ah! Jeez, why does everyone go for my breasts!?")
            elif "Imouto" in char_traits:
                lines = ("Hnn... Uhuhu, If you want to rub them, then just go for it ♪", "Huh... My nipples are getting harder and harder...?", "Aah... I want you to touch it more, wauu, more, ah, more...", "Eh! Huhu ♪ My nipples are getting harder, can you tell?", "...What is it? Are my breasts working you up? ♪", "J-Just for a little bit, okay?", "Hya! N-no, stop ♪ Hahya, please, stop ♪", "Haha, that tickles ♪")
            elif "Kamidere" in char_traits:
                lines = ("Uah, don't just run up and touch them... Hnn, how long are you... Hauu...", "Hnn, ah, wait, what are you... Geez, just do whatever you want! <resigned>", "Do you... like my breasts...that much?", "Uwah, that is a really perverted face, you know? Ahaha, that's so cute ♪", "Hnnn, I know, aauh, that my breasts are incredible, but... haaa...", "Huhu, I like that perverted side of you ♪", "My tits feel great, don't they?")
            elif "Bokukko" in char_traits:
                lines = ("Kya!? Don't...grope them... Ah...", "Oh, this is nice... my body feels light ♪", "Ah... That's crafty of ya...", "Who'd have thought it would feel so good from just breast-fondling...", "Kya! Geez... If you're gonna play with it, be gentle... Hauu...♪", "Aahhh... you can do it harder if you want ♪")
            elif "Ane" in char_traits:
                lines = ("Mm... You're considerably skilled.　Ah...oh yes, please, over there too...", "Be as spoiled as you like. I'll accept all of it ♪", "There... When you fondle gently, it feels really good...", "Ah... please keep rubbing me like that...", "Gently rubbing me like this... It's very good.", "When you play with my breasts like that my body feels so light." , "Yes, like that. Be gentle with them...")
            elif "Yandere" in char_traits:
                lines = ("This feeling... from your massage... is so good.", "...You're surprisingly bold. I like that.", "Mmh, little to the left... Ah yes, yes, right there, oh god...", "Hyah! Ahn... please, spare me from this lewdness ♪", "Ah... Right there, keep your hands there...")
            else:
                lines = ("Nnn... It's okay to rub it just a little.", "Mm... Being touched every now and then isn't so bad, I guess?", "My soft tits feel good, don't they?", "Ah... You like my breasts, don't you?", "Y... Yes... Continue massaging... like that.", "Aah... my chest... it feels so good.", "Hnnn, you've got... some naughty hands... uhn!", "It feels good... m...my nipples... What you did just now felt so good... ♪")
            iam.say_line(character, lines, "shy", ("zoom_fast", "reset"))

        @staticmethod
        def refuse_grab_breast(character):
            """
            Output line when the character refuses a breast-grab from the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Don't ever think about it.", "Don't touch me.", "You're damaging the shape of my breasts.", "You shouldn't grope people.")
            if "Yandere" in char_traits:
                lines = ("Hey, it hurts! Stop it!", "How... dare you!", "Huhuhuh... I wonder how warm it would be to bathe in your blood...?")
            elif "Shy" in char_traits and dice(50):
                lines = ("N... no... s...stop... p... please stop...", "Ugh... what... w...w-w-wwhat are you doing!?", "*sob* Why you are so mean...", "NO! D-don't do that!", "N-no, you can't, that's too p-perverted...")
            elif "Kuudere" in char_traits:
                lines = ("You graceless swine! Can you not calm down a little?", "Kya! W-what are you doing!?", "...! Who told you you could touch me there!?", "Nn...Where in the world are you touching? Jeez...!", "Geez! Don't touch them!", "Wha-... What? Aah... Wai-... Idiot! Stop it!")
            elif "Dandere" in char_traits:
                lines = ("No, cut it out!", "Ugh... not there... stop.", "Eh? W-, ah, wait, that's too fast! Uwaa!", "Nya! Don't rub right there! Don't be mean...")
            elif "Tsundere" in char_traits:
                lines = ("What?! You dumbass, what are you doing?!", "Kyaa-! Y... you idiot!", "Hey, what do you think you're grabbing at?!", "Wha!? N-no! Why would I enjoy it!?", "G-geez... NOW I'm angry!", "That's terrible! You beast! Pervert! Idiot!")
            elif "Ane" in char_traits:
                lines = ("Stop. I feel ill.", "That's sexual harassment, you know?", "If you grasp them so rough they'll lose shape.", "Auh! Uuh, my boobs aren't for rubbing, hyauh! Geez, stop it, hnaaah!", "This is a bit too daring.", "I think you have gone a bit too far.", "Stop it! I don't want this.")
            elif "Bokukko" in char_traits:
                lines = ("Hey! Where do ya think you're touching, you pervert!", "Whoah, wait! Where are you touching me?", "Hya! ...What are you, a molester!?",  "Hey! Don't be such an asshole.", "W-wait, hey, you're going too far!..")
            elif "Imouto" in char_traits:
                lines = ("Huh? Stop it! Where are you touching!?", "Kyaa! Geez! Help! There's a lewd molester here!", "Oww..! You've made me mad..!", "Hyauuu! Noo, youuu, boob freak!", "Hey, get away from me!", "Jeez, don't be doing lewd stuff, okay?", "Whoa, what're you trying to do?!")
            elif "Kamidere" in char_traits:
                lines = ("How filthy. Get away from me!", "What an idiot. What do you mean by 'Oops'?", "How dare you?! Know your place your filthy piece of trash!", "Piss off you fucktard!", "<jumps away> Ha! Like I'll ever let a loser like you touch me.")
            else:
                lines = ("You certainly have courage, asshole!", "What are you doing!!! They are not an invitation, asshole!", "Hey! Where are those hands of yours going?", "Don't touch me, asshole!", "You're... terrible! Must you do such a thing!", "What are you trying to...?! To hell with you!", "You filthy pig! Who gave you permission to touch me?!")
            iam.say_line(character, lines, "angry", ("angry", "reset"))

        @staticmethod
        def slave_refuse(character):
            """
            Output line when a slave refuses but has not other option than remain silent
            """
            lines = ("...", )
            iam.say_line(character, lines, overlay_args=("sweat", "reset"))

            narrator("%s doesn't resist, but also doesn't respond to your actions." % character.pC)

        @staticmethod
        def disappointed(character):
            """
            Output line when a character is disappointed by the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("... *you see disappointment in [pd] eyes before [p] turns away*", )
            elif "Shy" in char_traits and dice(50):
                lines = ("I suppose you have your reasons...", "Err... Do you... nothing. Never mind.")
            elif "Imouto" in char_traits:
                lines = ("Whaaa? Are you serious?", "What, that's it? Boring and stupid!")
            elif "Dandere" in char_traits:
                lines = ("Pathetic...", "You are a bad person.")
            elif "Tsundere" in char_traits:
                lines = ("You really must have a lot of free time to fool around like this...", "Hmph! Whatever!")
            elif "Kuudere" in char_traits:
                lines = ("How unreliable...", "That was quite pathetic, admit it.")
            elif "Kamidere" in char_traits:
                lines = ("I expected more from you...", "It was entirely unsightly.")
            elif "Bokukko" in char_traits:
                lines = ("Man, that was lame. I mean, really lame.", "Oh c'mon, it's not even funny!")
            elif "Ane" in char_traits:
                lines = ("My, is that it? I expected something... better.", "*sigh* How troublesome...")
            elif "Yandere" in char_traits:
                lines = ("Such a waste of time...", "... *glares with hostility*")
            else:
                lines = ("*sign* No wonder, my horoscope predicted a bad day.", "... *you see disappointment in [pd] eyes before [p] turns away*")
            iam.say_line(character, lines, overlay_args=("sweat", "reset"))

        @staticmethod
        def glad(character):
            """
            Output line when a character is glad because of something done by the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("... *[p] is looking at you, smiling*", )
            elif "Shy" in char_traits and dice(50):
                lines = ("Uhm... I'm really glad about it.", )
            elif "Imouto" in char_traits:
                lines = ("Whaaa! I'm soo glad! ♪", )
            elif "Dandere" in char_traits:
                lines = ("Right, that is good.", )
            elif "Tsundere" in char_traits:
                lines = ("Alright, finally... ♪", )
            elif "Kuudere" in char_traits:
                lines = ("Good, good. That's it.", )
            elif "Kamidere" in char_traits:
                lines = ("*nods* I'm really glad!", )
            elif "Bokukko" in char_traits:
                lines = ("This makes me really happy!", )
            elif "Ane" in char_traits:
                lines = ("Oh-My.. *[p] is looking at you with glowing eyes*", "*sigh* How nice...")
            elif "Yandere" in char_traits:
                lines = ("That is it! ♪", "So glad it is done ♪")
            else:
                lines = ("Haha.. I'm really happy!", "Yes ♪ You made me really happy!")
            iam.say_line(character, lines, overlay_args=("note", "reset"))

        @staticmethod
        def after_normal_sex(character):
            """
            Output line after the character had a not good and not bad sex (no rape) with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I can still feel you between my legs.", "So how was it, sex with me? Are you satisfied?", "Yeah... felt good.", "Haa... Satisfying...", "Please entertain me again sometime.")
            elif "Shy" in char_traits:
                lines = ("I... I wonder how good I was... I don't want you to hate me...", "I-I need to reflect... On the things that I've done...", "Aah... I want it like that, again... Maybe I'm a really dirty girl..?", "I'm very happy... Because... you know... huhuh...")
            elif "Nymphomaniac" in char_traits and dice(40):
                lines = ("Hehe... It looks like we were naughty, huh...", "Ehehe... I feel like doing it again...", "Um, how about we do it again? Maybe even two or three more times, if you want...")
            elif "Tsundere" in char_traits:
                lines = ("Well, that didn't feel too bad.", "Geez, what are you grinning for!? Yes, yes, it felt good, I get it!", "D-did I... make a funny face? Geez, I'm so embarrassed...", "W-what... Of course it felt good! You got a problem with that!?", "Geez, it was standing up so stiffly, I just couldn't stop myself!")
            elif "Dandere" in char_traits:
                lines = ("I want to do it again sometime...", "Did I... do well? I see. Thank you so much.", "It still feels like you are inside me.", "*huff* I can't go on... anymore... *puff*", "That felt really good... I'd be happy to do it again with you sometime.")
            elif "Kuudere" in char_traits:
                lines = ("Mmmfhh... I really am exhausted... You should take it easy too.", "That was awesome... Huhuh, let's do it again real soon.", "Geez, me doing such a thing... But it does feel really good...", "Well then... Let's do this again sometime, alright?")
            elif "Imouto" in char_traits:
                lines = ("Hey, hey, was I sexy or what?", "Ehehe... I'm good in bed, right?", "Hehe, it looks like we've been naughty...", "Haaaa... Sex really is wonderful...", "Huhuh, the sex felt really nice. Thank you ♪", "Hey, hey, what'd you think? It felt good, right? Tell me straight ♪", "Making love is a wonderful thing, hmhm ♪")
            elif "Ane" in char_traits:
                lines = ("What did you think? It felt wonderful, right?", "*sigh*... I'm exhausted... Hehe ♪", "I didn't expect it to be that good... Good job, hehe.", "Huhu... please keep desiring me as many times as you want.", "You did it very well... Uhuhu, it felt great.", "I'm ready for you any time, okay? ♪")
            elif "Bokukko" in char_traits:
                lines = ("Hum, thank you for letting me cum...", "Muhuhu... your orgasm face is nice ♪", "Geez... You made me feel so too good...", "Weeell, I s'pose you're pretty good. Not as good as me, though.")
            elif "Yandere" in char_traits:
                lines = ("How was it? Are you refreshed? ...Fufu, you should thank me.", "That wasn't bad, I guess... I'm sure you'll do even better next time.", "How does my face look when I cum? ...It doesn't go weird, does it?", "Ahaha ♪　It's so floppy ♪ And warm ♪")
            elif "Kamidere" in char_traits:
                lines = ("Aaaah, that was great... It was really awesome.", "Kuuh... Y-you're fucking like a cat in heat! There's no way I can continue after this...", "It felt really good. Well done.", "It wasn't bad, I guess... Yeah... I won't turn you down if you ask again.", "I expect next time will be equally enjoyable.")
            else:
                lines = ("That felt so good... Let's do it again someday.", "Hey, it felt good, right?", "Well, I'm looking forward to the next time.", "We really, really have to do this again ♪", "Ehehe, I'll let you borrow me again sometime.")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def after_good_sex(character):
            """
            Output line after the character had a very good sex (no rape) with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Thanks for your hard work... Let's have fun the next time too.", "When we make direct contact, it feels like we are melting into each other.", "I thought you would break me...", "I came too much...", "I guess it's possible for something to feel too good...")
            elif "Shy" in char_traits and dice(65):
                lines = ("Ah, please, don't make me feel so much pleasure... You'll turn me into a bad girl...", "No, please... I can't look you in the eye right now...", "Uuugh... I did such an embarrassing thing... Pl-please forget about it...", "Auh... I'm sorry for being so perverted...")
            elif "Nymphomaniac" in char_traits and dice(40):
                lines = ("Hafu... It was totally worth it practising with all those bananas...♪", "That was incredible... I thought I was gonna lose myself there.", "Ah ♪, I did it again today... Alright, starting tomorrow I'll control myself!")
            elif "Tsundere" in char_traits:
                lines = ("I-I was... C-cute? ...S-Shut up! One more word and I'll kill you!", "You made me cum so many times, it's kind of frustrating...", "Hu-hmph! Don't get a big head just 'cause you did it right once!", "H-hmph! Just because you're a little good doesn't make you the best in the world!", "I-it's not like you've got good technique or anything! Don't get so full of yourself!")
            elif "Dandere" in char_traits:
                lines = ("If you do it like that, anyone would go crazy...", "Mn... You did good...", "...It looks like we're a good match.", "We're quite compatible, you and I." "I came way too many times... Haa...", "D-do I also have such a shameful erotic face?", "Whew... I came so much... I surprised myself...")
            elif "Kuudere" in char_traits:
                lines = ("You're really good... I came right away...", "...Please don't look at me. At least for now.", "Yeah, I knew you were the type who gets things done.", "Wh-what? Y-you know just where I like it...?", "Uuu... It did feel amazing... but... I thought you were gonna rip me apart...")
            elif "Imouto" in char_traits:
                lines = ("You got me off just like that... You're like some kind of pro!", "Ah... I came right away... You're so good at this...", "I felt so good... Huhu, you are pretty good at this.", "Haah, I came so fast... What's wrong with me?")
            elif "Ane" in char_traits:
                lines = ("Exhausted? ...But you'll be wanting to do it again soon, right?　Hmhm ♪", "You're so good. ...Hmhm.", "Oh my, you've already found all my weak spots.", "Haah... If you make me feel pleasure this intense... I won't be able to live without you ♪", "Hauh... ok, that really was going too far... But it did feel really good...", "My goodness, you've really gotten quite skilled at this♪")
            elif "Bokukko" in char_traits:
                lines = ("Hehe, well? What, you totally looked like you enjoyed that", "Haah♪... Man, sex feels sooo good♪", "Fuwa... I turned into such a pervert... that surprised me...", "Ehehe, thanks for timing it just right...♪")
            elif "Yandere" in char_traits:
                lines = ("Nh... I came so much... Hehehe♪" , "That felt incredible... Fufu, thank you!♪", "This kind of sex really leaves my heart satisfied...", "Ehehe... We had sex ♪ Sex, sex, sex sex sex sexsexsexsehehe ♪ Ahahahaha ♪", "I've got so much love, I think I may go crazy...", "To be violently messed up like this, isn't so bad sometimes... huhu ♪")
            elif "Kamidere" in char_traits:
                lines = ("There there, that felt pretty damn good, hey?", "Aau... I thought I was going to break...",  "Mmh... I could become addicted to this pleasure.", "Ah... If it's this good, I guess it's ok to do it everyday.", "It just so happened that I got more sensitive all of a sudden, alright?")
            else:
                lines = ("Ahh... My hips are all worn out... Ahaha", "It kinda feels like we're one body one mind now ♪", "Haah... Well done... Was it good for you...?", "Haah... Your sexual technique is simply admirable...", "Sorry, it felt so good that I didn't want to stop...", "Haa... It looks like the two of us are pretty compatible...", "Ah, I can't even move... That felt too amazing...")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def after_sex_mc_cum_alot(character):
            """
            Output line after the character had a sex with the hero who cum a lot
            """
            char_traits = character.traits
            if hero.gender == "male":
                if "Impersonal" in char_traits:
                    lines = ("Is it normal for someone to be able to cum so much? Are you not a human?", "As a side note, creampies are okay.", "Nn... Your load exceeded my maximum capacity...", "I have all your weak spots memorized.", "Your semen will be my food.")
                elif "Shy" in char_traits:
                    lines = ("Y-You came so much... You were really saving it up...!", "Snf snf... It smells...", "I-I... what an embarrassing thing to do...", "I-I can't believe I... did that... Aaahhh...", "I made you feel really good, huh... I-I'm glad...")
                elif "Nymphomaniac" in char_traits and dice(40):
                    lines = ("Hehehe, thanks for the meal ♪", "The flavor of semen differs depending on the food you eat and how you're feeling...", "What a perverted scent... ehehe.", "Huhuh... look at me, I'm a dirty girl covered in your spunk.")
                elif "Tsundere" in char_traits:
                    lines = ("Geez, you got so much on my face that some went up my nose!", "T-That's embarrassing! Geez...", "I'm happy that you came so many times because of me, but... Didn't you cum too much?", "Yes, yes, you did well by cumming so much... Seriously...", "And? I'm great, right? ...Tell me that I am G-R-E-A-T!")
                elif "Dandere" in char_traits:
                    lines = ("Your semen's still so warm...", "I could get used to this scent...", "You came quite a bit...", "Don't worry, it's not unpleasant. Don't hold back on me next time.", "I became all slimy...", "How was it? My technique is something else, don't you think?", "I love it... when you cum for me.")
                elif "Kuudere" in char_traits:
                    lines = ("Um, so, are you gonna be okay, cumming that much?", "...Where did this much even come from?", "I know it feels good, but...you came too much.", "My god, are you bottomless...?", "So, what did you think...? I won't let you say that it didn't feel great!")
                elif "Imouto" in char_traits:
                    lines = ("Hey, lookie lookie! Look how much you came ♪", "Hehehe... It feels kinda warm...", "Nnh, hey look ♪ It's all that semen you shot out ♪", "Hey, can't you change the taste? Something that goes down a little easier would be nice.", "You've marked me with your cum, ehehe", "Waa, It's sticky... Did you cum a lot?", "I-I don't have a runny nose! This is semen!")
                elif "Ane" in char_traits:
                    lines = ("Fuaha... You came so much...♪", "Hehehe, your sweet spots were so easy to find ♪", "There's so much of your cum... Hmhm, want me to drink it?", "Mhmhm, you seem to be quite satisfied.", "That was enjoyable in its own way, thank you.", "Are you okay letting that much out... not dehydrated?", "My, such thick semen... It might get stuck in throat if one won't be careful.")
                elif "Bokukko" in char_traits:
                    lines = ("You really went all out... Is that how good it felt?", "More protein than I should be having... Oh well.", "...You look pretty strung out, hey? Eat up and get a good night's sleep, mkay?", "Ugh, my face is all sticky... But this is how I'm supposed to take it, right?")
                elif "Yandere" in char_traits:
                    lines = ( "Hehe... What a nice smell... I want to smell it forever...", "I know every inch of your body better than anyone.", "Hmhm, the face you make when you cum is adorable.", "It felt good, right? That's great...", "Uhuhu, it's good to know that I could be of use...")
                elif "Kamidere" in char_traits:
                    lines = ("Ew, I'm all sticky... Does the smell even come off...?", "Ahh, you're so naughty to cum this much...", "Nha... H-haven't you got anything to wipe with?", "I need to take a shower...", "Geez, to cum just from a little teasing... That's pathetic.", "Heh, should I tie a ribbon on it so you don't cum so fast?", "You REALLY let loose a lot of this stuff, huh...")
                else:
                    lines = ("Wow, look, look! Look at all of it... How did you even cum this much ♪...", "You came so much...", "Are you okay? Want some water? Are you going to be okay without rehydrating yourself?", "If it felt good for you, then that makes me feel good, too.")
            else:
                if "Impersonal" in char_traits:
                    lines = ("Is it normal for someone to be able to cum so much? Are you not a human?", "I have all your weak spots memorized.")
                elif "Shy" in char_traits:
                    lines = ("Y-You came so much... You were really saving it up...!", "Snf snf... It smells...", "I-I... what an embarrassing thing to do...", "I-I can't believe I... did that... Aaahhh...", "I made you feel really good, huh... I-I'm glad...")
                elif "Nymphomaniac" in char_traits and dice(40):
                    lines = ("Hehehe, thanks for the meal ♪", "What a perverted scent... ehehe.", "Huhuh... look at me, I'm a dirty girl covered in your spunk.")
                elif "Tsundere" in char_traits:
                    lines = ("T-That's embarrassing! Geez...", "I'm happy that you came so many times because of me, but... Didn't you cum too much?", "Yes, yes, you did well by cumming so much... Seriously...", "And? I'm great, right? ...Tell me that I am G-R-E-A-T!")
                elif "Dandere" in char_traits:
                    lines = ("Your fluids is still so warm...", "I could get used to this scent...", "You came quite a bit...", "Don't worry, it's not unpleasant. Don't hold back on me next time.", "I became all slimy...", "How was it? My technique is something else, don't you think?", "I love it... when you cum for me.")
                elif "Kuudere" in char_traits:
                    lines = ("Um, so, are you gonna be okay, cumming that much?", "I know it feels good, but...you came too much.", "My god, are you bottomless...?", "So, what did you think...? I won't let you say that it didn't feel great!")
                elif "Imouto" in char_traits:
                    lines = ("Hey, lookie lookie! Look how much you came ♪", "Hehehe... It feels kinda warm...", "You've marked me with your scent, ehehe", "Waa, It's sticky... Did you cum a lot?")
                elif "Ane" in char_traits:
                    lines = ("Fuaha... You came so much...♪", "Hehehe, your sweet spots were so easy to find ♪", "Mhmhm, you seem to be quite satisfied.", "That was enjoyable in its own way, thank you.", "Are you okay letting that much out... not dehydrated?")
                elif "Bokukko" in char_traits:
                    lines = ("You really went all out... Is that how good it felt?", "More excercise than I should be having... Oh well.", "...You look pretty strung out, hey? Eat up and get a good night's sleep, mkay?")
                elif "Yandere" in char_traits:
                    lines = ( "Hehe... What a nice smell... I want to smell you forever...", "I know every inch of your body better than anyone.", "Hmhm, the face you make when you cum is adorable.", "It felt good, right? That's great...", "Uhuhu, it's good to know that I could be of use...")
                elif "Kamidere" in char_traits:
                    lines = ("Ew, I'm all wet... Should I take a shower?", "Ahh, you're so naughty to cum this much...", "Nha... H-haven't you got anything to wipe with?", "I need to take a shower...", "Geez, to cum just from a little teasing... That's pathetic.", "You REALLY let loose quite easily, huh...")
                else:
                    lines = ("Wow, look, look! How did you even cum this much ♪...", "You came so much...", "Are you okay? Want some water? Are you going to be okay without rehydrating yourself?", "If it felt good for you, then that makes me feel good, too.")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def after_sex_char_never_come(character):
            """
            Output line after the character had a sex with the hero, but the MC was unable to satisfy the char
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Doesn't it count as sex only if we've actually both came?", "I'm not sure how to feel about this kind of sex.", "I guess you need to get used to this. Can I count on you to practice with me?")
            elif "Shy" in char_traits:
                lines = ("But I'm still not... You're so cruel...", "But I'm... Not yet...", "Is... is it already over? No, that's fine...")
            elif "Tsundere" in char_traits:
                lines = ("Uuh... But, but...! I just got so horny!", "Gosh, how could you forget! About what...? About me c-cumming!!", "Hey, can't you even tell whether or not your partner came?")
            elif "Dandere" in char_traits:
                lines = ("...What? Done already?", "Did you...do that...on purpose?", "I can't say I really approve of this sort of one-sided sex...", "Hmph, so selfish...")
            elif "Kuudere" in char_traits:
                lines = ("I'll forgive you this time, but...be ready for the next.", "Tch, and it was just getting good.", "I know you want to feel good, but you could throw me a bone... It's nothing...", "Really... isn't that kinda unfair?")
            elif "Imouto" in char_traits:
                lines = ("Mrrr♪, I still haven't cum yet!", "Didn't you forgot...the important stuff? I mean... me...", "Huh? Are we already done? But...", "That was fast... whatever it was, it was way too quick!")
            elif "Ane" in char_traits:
                lines = ("Hey, you do know what an orgasm is, yes? ...Then you understand, right?", "Come now, there's still something you haven't done, right?", "...What's wrong? You didn't do much...", "I haven't been satisfied yet...", "Don't worry, it'll get better... Next time, let's try to make it so both of us enjoy it.")
            elif "Bokukko" in char_traits:
                lines = ("Stopping after you've only satisfied yourself? You're the lowest.", "Hold on, aren't you forgetting something? ...Yeah, that! You know, that...yeah... N-not that!", "Wha-... but we barely did anything!")
            elif "Yandere" in char_traits:
                lines = ("What's the meaning of this? I wanted to do it, you know...", "No-no-no, there's no way we can just end it like that...", "Come on, now, you can do better than that...", "Haa... That's unfair...")
            elif "Kamidere" in char_traits:
                lines = ("No self-centred sex allowed, you can't skip the important parts!", "I am not pleased. Please figure out the reason on your own.", "I'm still far from being satisfied though...", "You're still a long way from satisfying me... Work on it for next time.")
            else:
                lines = ("Hey! I-I didn't came at all!", "I haven't had anywhere near enough yet, you know?", "Th-this happens sometimes, right...? Still...", "Eh, but I only got a little! Geez...", "Wait, I haven't even came yet!")
            iam.say_line(character, lines, overlay_args=("angry", "reset"))

        @staticmethod
        def after_sex_hero_never_come(character):
            """
            Output line after the character had a sex with the hero, but the char was unable to satisfy the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("...Was my technique that bad?", "I'm sorry, I'm just so incompetent...", "I feel like that was all about me... I apologize.")
            elif "Shy" in char_traits:
                lines = ("I'm sorry... I wasn't very good...", "Sorry... Because of my weakness...", "I'm very sorry... Y-yes, I made sure to practice...")
            elif "Tsundere" in char_traits:
                lines = ("S-sorry... I'll try harder next time, okay...?", "I-if I'm bad at this, j-just say so already...", "Wh-what? Are you trying to say I'm bad at this? ...Kuh, just you wait.")
            elif "Dandere" in char_traits:
                lines = ("This was not something I had any control over... Sorry.", "Please forgive me, this is all due to my insufficient knowledge.")
            elif "Kuudere" in char_traits:
                lines = ( "I can't even satisfy you... What am I missing?", "Forgive me for having disappointed you... How can I fix things?")
            elif "Imouto" in char_traits:
                lines = ("Was it not good for you? ...Sorry", "...My bad. I'm sorry, ok?", "Ah, um... Next time, I'll make you feel good...")
            elif "Ane" in char_traits:
                lines = ("I was unable to satisfy you... My apologies...", "I'm so sorry...I couldn't satisfy you...", "I'm bad at this, so...maybe you can teach me how?")
            elif "Bokukko" in char_traits:
                lines = ("Jeez, how come you never came!", "Is it cause I'm so bad? ...I'm sorry, okay?")
            elif "Yandere" in char_traits:
                lines = ("I'm sorry... I'll do something about it next time, so forgive me, okay?", "Mmm, I need to learn more about your body, huh...")
            elif "Kamidere" in char_traits:
                lines = ( "Hmph, if you didn't want it you could've refused, you know?", "It's your own fault for masturbating so much you can't finish.", "W-what's with this face that says '[pC] did [pd] best...'?!")
            else:
                lines = ("Um. I'm sorry! I'll study up for next time.", "Sorry... I'll do some more studying, so...")
            iam.say_line(character, lines, "shy", ("scared", "reset"))

        @staticmethod
        def before_sex_virgin(character):
            """
            Output line before the character is having a sex with the hero and losing her virginity (no rape)
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I'm not going to stay a virgin all my life. Please make me an ex-virgin.", "W-would you make me... a woman?", "You can confirm for yourself that I'm a virgin.", "I understand... When you put it in, please tear my hymen apart slowly, okay?", "This is my first time, so I won't be any good... Please help and guide me.", "You're going to break my hymen... Okay.")
            elif "Shy" in char_traits:
                lines = ("Um, I'm a virgin! ...Please, umm, take my first time...", "I, um... I've never did it before... So...", "I've never done this before, but... If you'll be gentle, then...", "Eh? H-how would we do that... Eh!? Th-that goes... in here...? Y-yeah! ...Let's do it...", "Pl-please... Be my... first time...", "I'm, uh... still... a virgin, okay? So... you know...")
            elif "Nymphomaniac" in char_traits and dice(40):
                lines = ("...T-this is...unexpectedly embarrassing... It is my first time and all.", "Y-you'll have to teach me a few things...")
            elif "Tsundere" in char_traits:
                lines = ("F-fine then, let's get to it! I-it's not like this is my first time, okay!?", "H-hmph! Sex is nothing to me! Fine, let's do this!", "I-if you say you want it, I can give you my virginity... If you'd like...?", "O-okay... But! This is my first time, so... be gentle... Y-you got that!?", "I-if you really, really want my ch-chastity... Then I'll give it to you...")
            elif "Dandere" in char_traits:
                lines = ("...I don't mind if it's you. Teach me to fuck.", "...If you're alright with me being inexperienced, then let's do it.", "You'll be my first partner.", "Very well. I will give you my chastity.", "It's my.. first time. I'm giving it to you.", "I'm inexperienced, but I hope that you enjoy my performance.")
            elif "Kuudere" in char_traits:
                lines = ("I've... never done it before... Okay, then let's do it.", "Take my virginity. It's n-not really a big deal, you don't have to overthink it.", "I-it's my first time... So I want you to do it gently.", "Yeah, my cherry is still right where nature put it... Please pop it gently, okay?", "I feel like I should warn you that... That I'm a v-virgin... So... you know...")
            elif "Imouto" in char_traits:
                lines = ("Alright, you're going to be my first.", "I-if you're okay with me... I don't know if I'll be very good at it, ahaha...", "U-Um, well... If you're gentle...♪", "Umm... I-I don't know how it's done! ...Please, take the lead...")
            elif "Ane" in char_traits:
                lines = ("Hmhm, I'm still a virgin. Please be gentle with me... I'll be angry if you're not, ok?", "Hmhm, it looks like you'll become my first...", "I'm a virgin but... I want you to make me a woman.", "Hey... This is my first time... Could I entrust that to you?", "I've never done it before, so don't complain, okay?")
            elif "Bokukko" in char_traits:
                lines = ("Virgins are a real pain. You okay with that?", "Yeah, okay, take my virginity.", "You know, mine... Mine's new, unbroken seal and everything... no one's been there before...", "A-are you okay with me even if I'm still a virgin? ...V-very well, challenge accepted!")
            elif "Yandere" in char_traits:
                lines = ("Yes... My chastity... is yours...", "I've heard how it works, but... I don't have any experience, okay?", "You can't become a 'woman' without having sex right? Well, I want to be a 'woman'...", "I know the idea of it... But I never actually did it before. Is that still okay...?")
            elif "Kamidere" in char_traits:
                lines = ("My first time... Will be tested on your body.", "Hmph, you'll do as my first partner.", "I don't really like pain... I'm okay. let's do it.", "Hurry up and do it, or I'll give my virginity away to whoever.", "Right now, an unplucked fruit is standing before you. Hungry?")
            else:
                lines = ("I've never done it before, but... I think I could do it with you.", "It's my first, so... Be gentle, alright?", "Hmm... well, it should be fine if it's with you you, first time or not.", "I-it's okay with you if I make you my first partner... Right...?")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def after_sex_virginity_taken(character):
            """
            Output line after the character had a sex with the hero and lost her virginity (no rape)
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("With this, next time I'll be able to feel good, right?", "Hmm, It did hurt, but... I'm happy.", "It was so big that I thought it would hurt a lot... It is all because of your gentleness. Thank you very much.", "Hm... So this makes me an ex-virgin, it seems.")
            elif "Shy" in char_traits:
                lines = ("Uh, i-it's ok... I can endure it...", "Kuh... I'm okay... But... I didn't think it would hurt so much...", "I-It's alright. It did hurt a little, but... I'm really happy ♪", "I-It's okay... You were very gentle...")
            elif "Tsundere" in char_traits:
                lines = ("Uuh... That really hurt... Of-of course you could have helped it!", "Kuh... I had to go through this one day anyway so it's fine!", "Kuh... This pain makes the world so dazzling...", "What's with this...? Why does it hurt so much? Geez...")
            elif "Dandere" in char_traits:
                lines = ("I can still feel the pain of it going in... But it only hurt at first, you know? I wonder how it'll feel next time.", "This pain... it's carved into my body and my heart... I'll never forget this.", "...No, I'm okay. It just... hurt a little more than I expected.", "This pain...I am sure it will become an unforgettable memory...")
            elif "Kuudere" in char_traits:
                lines = ("Kuh... It hurts and it's not easy to do... Will it really begin to feel good...?", "Tch!... I-it's not... okay... It hurt so much...", "Kuh... This much pain is nothing...", "Ku... So this is the pain of deflowering... I'm jealous that men don't need to suffer the first time...")
            elif "Imouto" in char_traits:
                lines = ("Uuh... It was scary, and painful... Sniff... Be a little more gentle next time...", "Aha, now I've become an adult... after that... uhuhu...", "Uuu, it still stings... It's gonna be okay, right...?", "Uu... Should I smear some medicine on it...?", "Fufu, I gave you my first time ♪")
            elif "Ane" in char_traits:
                lines = ("As I expected, the first time hurt...", "How was my first? Did it make you happy...?", "Ouch... er, n-no, I'm fine... This is another good memory.", "Kuh, I'll need to practice to get used to this, I think... Of course you'll help me, don't you?")
            elif "Bokukko" in char_traits:
                lines = ("Does it hurt this bad for everyone? And they still do it?", "Damn! That really freakin' hurt! Buy me something as an apology, kay?", "The time has come! Virginity lost!", "I can still feel you inside me... So this is sex huh...?")
            elif "Yandere" in char_traits:
                lines = ("Hmm... Next time it'll feel good right? Hehe, I can't wait.", "Ahhh, it hurts... I-it can't be helped...", "Ugh... That really hurt... I'm glad I will never have to do that again...", "Phew... It really went in there, huh... It did kind of hurt, though...")
            elif "Kamidere" in char_traits:
                lines = ("Ugh. Can this really begin to feel good...?", "Haa... Geez, It hurt and it's disgusting, that's the worst...", "Hng... It hurt and I'm tired... Do people really enjoy this sorta thing...?", "Tch... Huhu, I guess, I won't be called a virgin anymore...", "Nnn.... It's my first time, of course it hurts.")
            else:
                lines = ( "Khh... That, that hurt a little bit...", "Ouch... I need to get more practice taking it in...", "Aauu... It hurt even more than I expected...", "I'm fine... This pain is something I have to overcome, so...")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def offer_sex(character):
            """
            Output line whe the character proposes to have an intercourse with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("So... do you want to have sex?", "I need sex. Let's do it.", "Please do perverted things to me. I'm ready.", "Please allow me to check if our bodies match. I'll take full responsibility.", "I would like to have sex with you. Is that going to be a problem?", "Can we have sex? I feel like I need it.")
            elif "Shy" in char_traits:
                lines = ("Uh... p-please d-do it for me... my whole body's aching right now...", "Aah... p-please... I-I want it... I can't think of anything else now!", "Ummm.... do you... not wish to do it...? ...I... really want it...", "I-I want to... be... with you...", "Right now... I want you to do it with me now... Please...", "I-I'm actually really good at sex! So... I-I'd like to show you...", "Um, I-I want to do it... So... Could we have sex?")
            elif "Imouto" in char_traits:
                lines = ("Let's do kinky things... Come on? Puh-leaaase.", "I've got a huge favor to ask! Fuck me right now! Pleaaase!", "So, um... are you interested in sex? I mean, uhm... I'd kinda like to... do it with you?", "Uuu... I'm boooored! Let's do something fun! Like um...maybe have sex or something...")
            elif "Dandere" in char_traits:
                lines = ("Looking at you... makes me want to do it. Do you want to?", "You want to feel good too, don't you?", "How about we do *it*? It'll be fine, leave it to me.", "Let's... feel good together.", "Do you want to spend some time inside of me?", "You are interested in sex and stuff, right? In that case, come on...")
            elif "Tsundere" in char_traits:
                lines = ("Hey, want to do it? S-sex, I mean...", "C'mon, you want to do it too, right?", "Maybe I could agree if you asked me...  Geez! I'm telling you it's ok to have sex with me!", "You know... You wanna to have sex... with me?", "D-do you want to do that with me, maybe...? It's fine with me if you want to...", "C'mon. We're doing it. Doing what...? Haven't you figured it out?")
            elif "Kuudere" in char_traits:
                lines = ("I-I was thinking...That I wanted to be one with you...", "Hey, I want to feel you inside me. Okay?", "Come on, I can tell that you're horny... Feel free to partake of me.", "Uhm... you're interested, right? In sex and stuff...", "H-hey, maybe the two of us could have... an anatomy lesson?", "I sort of want to do it now... You're cool with it, right?")
            elif "Kamidere" in char_traits:
                lines = ("Hey. Want to fuck...?", "Hey, you want to do perverted stuff...?", "So, let's do it. ...Huh? You were watching me because you wanted to fuck, right?", "You want to do me, don't you? Then step up and honestly say, 'hey, I want to do you'!", "What, you're looking at me like you want me, right? Then come over here.", "I'm specially allowing you to do whatever you like with me... You'll do it, right?", "You look like you really want to, so I'll let you do me.")
            elif "Bokukko" in char_traits:
                lines = ("Hey... if you'd like, I'll give ya' some lovin' ♪", "C'mon, it's time to do 'it', what do you say?", "...Okay, that's it! I can't stand it! Sorry, I've gotta fuck ya!", "Hey... You want to have sex, don't ya?", "C'mon, c'mon, let's get kinky? C'mon, let's fuck!", "Shit, I'm horny as hell. Hey? You up for a go?", "Hey... you wanna mess around...? Let's do it while we got some time to kill...", "Aah geez, I can't hold it anymore! Let's fuck!", "Hey, d'you wanna do me? D'you wanna fuck me?")
            elif "Ane" in char_traits:
                lines = ("I was thinking of having sex with you... Is it ok...?", "Do you want to do it right now? I very much approve.", "Um... Is it ok with you if we have sex?", "How about this? That is to say... getting to know each other a bit better through sex?", "If you wish, shall I take care of your sexual needs?", "Excuse me... Would you like to have sex?", "You feel like doing it, don't you...? I really want it right now ♪")
            elif "Yandere" in char_traits:
                lines = ("Come on, I can tell that you're horny... Feel free to partake of me.", "I can do naughty stuff, you know? ...Want to see?", "Hey, you want to do it with me, right? There's no use trying to lie about it.", "Uhuhu... don't you want to have sex with me?", "Come on, I can tell you need some release... just leave it to me.", "Let's do it! Right now! Take off your clothes! Hurry!")
            else:
                lines = ("Hey... Let's have sex.", "Say... d-do you want to do it... too?", "Um.. w-would you mind... having sex with me?", "Um... Please, have sex with me.", "Hey... do you think... we could do it?", "H-hey... Hmm, do I really need to be the one to say it... F-fuck me!", "Hey... I wanna have sex with you. Is that okay?")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def offer_sex_for_money(character):
            """
            Output line whe the character proposes to have an intercourse with the hero for gold
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Hey, want to have some fun?", "Why don't we get to 'it', hmm?")
            elif "Shy" in char_traits and dice(50):
                lines = ("Ehm.. why don't we have some good time together?", "Ghm, would you like to have some fun with me?")
            elif "Imouto" in char_traits:
                lines = ("We could have some fun business together, don't you think?", "I know some great tricks in the bed! Want to test me? ♪")
            elif "Dandere" in char_traits:
                lines = ("You could spend some quality time with me. Do you want to?", "I could show you the heaven if you want, hm?")
            elif "Tsundere" in char_traits:
                lines = ("Hey, do you wanna experience real pleasure?", "Let me bring you to heaven! What do you say?")
            elif "Kuudere" in char_traits:
                lines = ("How about some private time together?", "Let's satisfy the needs of both of us, do you agree?")
            elif "Kamidere" in char_traits:
                lines = ("If I look at you, I get the feeling that you could really use my 'services'! Agree?", "I sense a real tension in you. Why don't you let me help you with that?")
            elif "Bokukko" in char_traits:
                lines = ("Look at my body, it could really have some uses, right?", "Come and let's have sex, okay?")
            elif "Ane" in char_traits:
                lines = ("Hey sweetie, I could help you to forget all your problems ♪ What do you say?", "Why don't you put your body in my care, honey?")
            elif "Yandere" in char_traits:
                lines = ("Wanna check out my quality 'services'?", "Are you just looking, or do you want to get in the adult business with me?")
            else:
                lines = ("I could help you to release some tension, don't you think?", "My 'services' are really helpful, wanna try?")
            iam.say_line(character, lines, "suggestive")

        @staticmethod
        def accept_sex_for_money(character, price):
            """
            Output line whe the character accept to have an intercourse with the hero for gold
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Affirmative. It will be [price] Gold.", "Calculations completed. [price] Gold to proceed.")
            elif "Shy" in char_traits and dice(50):
                lines = ("S-sure. [price] Gold, please.", "*blushes* I-i-it will be [price] Gold...")
            elif "Imouto" in char_traits:
                lines = ("Mmm, I think it should be %d Gold... No, wait, it will be [price] Gold. I'm not very good with this stuff, hehe ♪" % abs(price-randint(15,35)), "Ooh, you want to do 'it' with me, don't you? Ok, but it will cost you [price] Gold.")
            elif "Dandere" in char_traits:
                lines = ("I see. I shall do it for [price] Gold.", "*[p] nods* [price] Gold.")
            elif "Tsundere" in char_traits:
                lines = ("I'll do it for [price] Gold. You better be thankful for my low prices.", "Fine, fine. I hope you have [price] Gold then.")
            elif "Kuudere" in char_traits:
                lines = ("It will be [price]. And no funny business, understood?", "It will cost you [price] Gold. Do you have so much money?")
            elif "Kamidere" in char_traits:
                lines = ("What's that? You want to hire me? I want [price] Gold then, money up front.", "Hm? You want my body? Well of course you do. [price] Gold, and you can have it.")
            elif "Bokukko" in char_traits:
                lines = ("Sure thing. That will cost ya [price] Gold.", "Ohoh, you wanna me, don't you? ♪ Alrighty, [price] Gold and we good to go.")
            elif "Ane" in char_traits:
                lines = ("Let's see... How about [price] Gold? Can you afford me? ♪", "Need some... special service? For you my price is [price] Gold ♪")
            elif "Yandere" in char_traits:
                lines = ("Fine, I want [price] Gold. No bargaining.", "Well, if you want to... It will cost [price] Gold.")
            else:
                lines = ("You want to hire me? Very well, it will be [price] Gold.", "Of course. For you my body costs [price] Gold.")
            iam.say_line(character, lines, msg_args={"[price]": str(price)})

        @staticmethod
        def refuse_sex_for_money(character):
            """
            Output line when the character refuses to have an intercourse with the hero for gold
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I see no benefit in doing that so I will have to decline.", "Keep your offer to someone else.")
            elif "Shy" in char_traits and dice(50):
                lines = ("I... I don't want that! ", "W-we can't do that. ", "I-I don't want to... Sorry.")
            elif "Imouto" in char_traits:
                lines = ("Noooo way!", "I, I'm not for sale, you know!", "I-I'm gonna get mad if you say such things, you know? Jeez!")
            elif "Dandere" in char_traits:
                lines = ("You're no good...", "Why would you offer me something like that?", "Do you know who you are talking to?")
            elif "Tsundere" in char_traits:
                lines = ("Your utter lack of common sense is still surprising. Hmph!", "You are so... disgusting!", "You pervy little scamp! Not in a million years!", "Hmph! Unfortunately for you, my body is not for sale!")
            elif "Kuudere" in char_traits:
                lines = ("G-get the fuck away from me, you disgusting perv.", "...Perv.", "...It looks like I'll have to teach you about this little thing called reality.", "O-of course the answer is no!", "Hmph, how unromantic!", "Don't even suggest something that awful.")
            elif "Kamidere" in char_traits:
                lines = ("Wh-who do you think I am!?", "W-what are you talking about... Of course NOT!", "What?! How could you think that I... NO!", "What? Asking that out of the blue? Know some shame!", "The meaning of 'not knowing your place' must be referring to this, eh...?", "I don't know how anyone so despicable as you could exist outside of hell.")
            elif "Bokukko" in char_traits:
                lines = ("He- Hey, Settle down a bit, okay?", "Keep your dirty money away from me, okay?", "Y-you're talking crazy...", "Hmph! Well no duh!")
            elif "Ane" in char_traits:
                lines = ("If I was interested in that sort of thing I might, but unfortunately...", "Oh my, can't you think of a better way?", "No. I have decided that it would not be appropriate.", "I don't think your offer is really appropriate.", "I think that you are out of your mind.")
            elif "Yandere" in char_traits:
                lines = ("I've never met someone who knew so little about how pathetic they are.", "What? Are you out of your mind? You want to die?")
            else:
                lines = ("No! Absolutely NOT!", "Get lost, pervert!", "Woah, hold on there. What exactly do you think I am?", "Don't tell me that you thought I was a slut...?")
            iam.say_line(character, lines, "angry")

        @staticmethod
        def before_sex(character):
            """
            Output line after the character accepted to have an intercourse with the hero (no rape)
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("So, I'll begin the sexual interaction...", "I want you to feel really good.", "Hmm. Now how should I fuck you?", "Come. Touch me gently...", "...I have high expectations.", "I will try to do my best to meet your expectations.", "Now, let's enjoy some sex.", "I'll serve you.")
            elif "Shy" in char_traits:
                lines = ("I-I'll do my best... for your sake!", "Uhm... I want you... to be gentle...", "Uuh... Don't stare at me so much, it's embarrassing...", "...I'm ready now... Do it any time...", "Uh, uhm, how should I...? Eh? You want it like this...? O-okay! Then, h-here I go...", "As I thought, I'm nervous... B-but that's ok... I prepared myself...", "P-Please look... It's become so gushy just from thinking about you...♪", "Sorry if I'm no good at this...")
            elif "Imouto" in char_traits:
                lines = ("Uhuhu, well then, what should I tease first ♪", "Hm hmm! Be amazed at my fabulous technique!", "Umm... please do perverted things to me ♪", "Hehe, I'm going to move a lot for you...", "Aah... I want you...To love me lots...", "Ehehe... now my clothes are all soaked...", "Ehehe, make me feel really good, okay?", "Please be gentle, ok?")
            elif "Dandere" in char_traits:
                lines = ("Be sure to make me feel good too, ok?", "There's no reason for us to hold back... Come on, let's do this.", "I can't wait any more. Look how wet I am just thinking about you...", "Come on... Let's be one, body and soul.", "I will handle... all of your urges.", "My body can't wait any longer...")
            elif "Tsundere" in char_traits:
                lines = ("S-shut up and... entrust your body to me... Okay?", "Humph! I'll show you I can do it!", "I-I'm actually really good at sex! So... I-I'd like to show you...", "D-do it properly, would you? ...I don't want a shoddy performance." , "I'm gonna have sex with you! ..G-get ready!", "You can be rough, I guess... If it's just a little bit...", "Y-you just need to be still and let me do everything... You got that?", "D-do whatever you want...")
            elif "Kuudere" in char_traits:
                lines = ("I'm going to make you cum. You had better prepare yourself.", "C'mon, I'll do kinky things, so make the preparations.", "Well then, shall I do something that'll make you feel good?", "Let's make this feel really good.", "L-leave it to me... Here, I'll take off your clothes...", "I-I'll make sure to satisfy you...!", "You can do with me... as you'd like...", "In the end, I'm just a normal woman too, you know...")
            elif "Kamidere" in char_traits:
                lines = ("Hmph, I'll prove that I'm the greatest you'll ever have.", "Now... show me the dirty side of you...", "I won't let you go until I'm fully satisfied, so prepare yourself.", "I'll give you a run you'll never forget ♪", "Okay... I suppose I'll just do as I please, uhuhu...", "Now, why don't you just give up and let me at that body of yours?", "Please, show me what you can do... I'm expecting great things.")
            elif "Bokukko" in char_traits:
                lines = ("C'mon, make me feel completely satisfied!", "You've been holding it in, right? You can do it with me, big time. Really big ♪", "Alright then, I'll give ya' some lovin'.", "You can do whatever you want. T-that's 'cause, I wanna know how you like it...", "C'mon, let's make love till every part of our bodies is tired... Uhuhu...")
            elif "Ane" in char_traits:
                lines = ("Now, let us discover the shape of our love ♪", "Hmhm, what is going to happen to me, I wonder? ♪", "Hehe, I won't let you go... Now quiet down and take this like an adult.", "Fufuh, it's okay to do it a little harder ♪", "Hehe... So you're ready to go just from looking at me?  Hehe, that makes me happy.", "There's no need to be ashamed... Please let me take care of you.", "Hmhm, go easy on me, okay?", "Hmhm, be good to me, will you?")
            elif "Yandere" in char_traits:
                lines = ("Ehehe... you can do whatever you want.", "Huhuhu, I'll give you a really. Good. Time.", "Huhu, so here we are... You can't hold it anymore, right?", "I want to try lots of things with you...", "I can't control myself anymore... uhuhu...", "Please let me have a clear look at your face when you cum.", "Huhuh, you'll fuck me like a beast, right?", "Yes! I can't take it anymore, I want it so bad! Ah!")
            else:
                lines = ("I want to do so many dirty things... I can't hold it back ♪", "Leave it to me! I'll do my very best!", "Prepare to receive loads and loads of my love!", "Hehee, just leave it all to me! I'll make this awesome!", "Hehe, I'll give it everything I've got ♪")
            iam.say_line(character, lines, overlay_args=("sweat", "reset"))

        @staticmethod
        def accept_sex(character):
            """
            Output line when the character accepts to have an intercourse with the hero
            """
            char_traits = character.traits
            if "Half-Sister" in char_traits and dice(50):
                if "Impersonal" in char_traits:
                    lines = ("I'll take in all your cum, [hero.hs].", "Sex with my [hero.hs], initiation.", "Let's have incest.", "Even though we're siblings... it's fine to do this, right?", "Let's deepen our bond as siblings.")
                elif "Shy" in char_traits and dice(40):
                    lines = ("Umm... anything is fine as long as it's you... [hero.hs].", "I-if it's you, [hero.hs], then anything you do makes me feel good.", "I-is it alright to do something like that with my [hero.hs]..?")
                elif "Imouto" in char_traits:
                    lines = ("Teach me more things, [hero.hs]!", "[hero.hsC], teach me how to feel good!", "Sis... will try her best.", "Sister's gonna show you her skills as a woman.")
                elif "Dandere" in char_traits:
                    lines = ("Ah... actually, your sister has been feeling sexually frustrated lately...", "[hero.hsC], please do me.", "Even though we're related, we can have sex if we love each other.", "I'm only doing this because you're my [hero.hs].", "I'll do whatever you want, [hero.hs].", "[hero.hsC] can do anything with me...")
                elif "Kuudere" in char_traits:
                    lines = ("I... I can't believe I'm doing it with my [hero.hs]...", "Y-you're lusting for your sister? O-okay, you can be my sex partner.", "I... I don't mind doing it even though we're siblings...", "Just for now, we're not siblings... we're just... a flesh of human.")
                elif "Tsundere" in char_traits:
                    lines = ("Ugh... I... I have such a lewd [hero.hs]!", "A-alright, you are allowed to touch me, [hero.hs].", "I... I'm only doing this because you're turned on, [hero.hs].", "Doing this... with my [hero.hs]... What am I doing?..", "I bet our parents would be so mad...")
                elif "Kamidere" in char_traits:
                    lines = ("Uhm... [hero.hs]... it's... it's wrong to do this...", "E...even though we're siblings...", "Doing such a thing to my [hero.hs]. Am I a bad big sister?", "My [hero.hs] is in heat. That's wonderful.")
                elif "Yandere" in char_traits:
                    lines = ("Make love to me, [hero.hs]. Drive me mad.", "I'm looking forward to see your face writhing in mad ecstacy, bro.", "Shut up and yield yourself to your sister.", "[hero.hsC], you're a perv. It runs in the family though.", "Man, who'd have thought that my [hero.hs] is as perverted as I am...", "As long as the pervy [hero.hs] has a pervy sis as well, all is right with the world.", "Damn... The thought of incest gets me all excited now...")
                elif "Ane" in char_traits:
                    lines = ("This is how you've always wanted to claim me, isn't it?", "Doing such things to your sister... Well, it can't be helped...", "Sis will do her best.", "Let sis display her womanly skills.")
                elif "Bokukko" in char_traits:
                    lines = ("You want to have sex with your sister so bad, huh?", "I'm gonna show you that I'm a woman too, [hero.hss].", "Right on, [hero.hs].  Better you just shut up and don't move.", "Leave this to me, you can rely on sis.", "As long as it is for my [hero.hs] a couple of indecent things is nothing.")
                else:
                    lines = ("It's alright for siblings to do something like this.", "Make your sister feel good.", "We're siblings. What we're doing now must remain an absolute secret.", "I'll do my best. I want you to feel good, [hero.hs].")
        
            elif "Impersonal" in char_traits:
                lines = ("You are authorized so long as it does not hurt.", "You can do me if you want.", "Understood. I will... service you...", "I dedicate this body to you.", "Understood. Please demonstrate your abilities.", "If the one corrupting my body is you, then I'll have no regrets.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Sex... O-okay, let's do it...", "D-do you mean...  Ah, y-yes...  If I'm good enough...", "Eeh?! Th-that's... uh... W- well... I do... want to...", "O...okay. I'll do my best.", "I too... wanted to be touched by you...", "Uh... H-how should I say this... It... it'll be great if you could do it gently.",  "Um, I-I want to do it too... Please treat me well.", "Eeh, i-is it ok with someone like me...?", "Umm...  I wanted to do it too... hehe.", "I-if I'm good enough, then however many times you want...", "I-I understand... I will... service you.")
            elif "Tsundere" in char_traits:
                lines = ("*gulp*... W-well... since you're begging to do it with me, I suppose we can...", "It...it can't be helped, right? It... it's not that I like you or anything!", "I-it's not like I want to do it! It's just that you seem to want to do it so much...", "Hhmph... if...if you wanna do it... uh... go all the way with it!", "If you're asking, then I'll listen... B-but it's not like I actually want to do it, too!", "If-if you say that you really, really want it... Then I won't turn you down...", "L.... leave it to me... you idiot...", "God, people like you... Are way too honest about what they want...", "T...that can't be helped, right? B...but that doesn't mean you can do anything you like!", "You're hopeless.... Well, fine then....", "...Yes, yes, I'll do it, I'll do it so...  geez, stop making that stupid face...", "Geez, you take anything you can get...")
            elif "Dandere" in char_traits:
                lines = ("If that's what you desire...", "...Very well then. Please go ahead and do as you like.", "You're welcome to... to do that.",  "I will not go easy on you.", "I... I'm ready for sex.", "...If you do it, be gentle.", "...If you want, do it now.", "...I want to do it, too.", "Ok, but please don't look at my face. That'll help me relax more.")
            elif "Kuudere" in char_traits:
                lines = ("Y-yes... I don't mind letting you do as you please.", "If you feel like it, do what you want with my body...", "...I don't particularly mind.", "Heh. I'm just a girl too, you know. Let's do it.", "What a bother... Alright, I get it.", "...Fine, just don't use the puppy-dog eyes.", "*sigh* ...Fine, fine! I'll do it as many times as you want!", "Fine with me... Wh-what? ...Even I have times when I want to do it...", "If you wanna do it just do what you want.")
            elif "Imouto" in char_traits:
                lines = ("Uhuhu, Well then, I'll be really nice to you, ok? ♪",  "Okayyy! Let's love each other a lot ♪", "Hold me really tight, kiss me really hard, and make me feel really good ♪", "Yeah, let's make lots of love ♪", "I'll do my best to pleasure you!", "Geez, you're so forceful...♪")
            elif "Ane" in char_traits:
                lines = ("Heh, fine, do me to your heart's content.", "If we're going to do it, then let's make it the best performance possible. Promise?", "Come on, show me what you've got...", "This looks like it will be enjoyable.", "If you can do this properly... I'll give you a nice pat on the head.", "Seems like you can't help it, huh...", "Fufufu, please don't overdo it, okay?", "Go ahead and do it as you like, it's okay.", "Very well, I can show you a few things... Hmhm.", "You want to do it with me too? Huhu, by all means.")
            elif "Bokukko" in char_traits:
                lines = ("Wha? You wanna to do it? Geez, you're so hopeless.. ♪", "Right, yeah... As long as you don't just cum on your own, sure, let's do it", "Y-yeah... I sort of want to do it, too... ehehe...", "S-sure... Ehehe, I'm, uh, kind of interested, too...", "Gotcha, sounds like a plan!", "Huhu... I want to do it with a pervert like you.", "Ehehe... In that case, let's go hog wild ♪", "Got'cha. Hehe. Now I won't go easy on you.", "Huhuh, I sort of want to do it too.", "Well, I s'pose once in a while wouldn't hurt ♪")
            elif "Yandere" in char_traits:
                lines = ("You won't be able to think about anybody else besides me after I'm done with you ♪", "Oh? You seem quite confident. I'm looking forward to this ♪", "*giggle* I'll give you a feeling you'll never get from anyone else...", "Yes, let's have passionate sex, locked together ♪", "If we have sex you will never forget me, right? ♪", "Heh heh... You're going to feel a lot of pleasure. Try not to break on me.")
            elif "Kamidere" in char_traits:
                lines = ("That expression on your face... Hehe, do you wanna fuck me that much?", "Fufu... I hope you are looking forward to this...!", "Feel grateful for even having the opportunity to touch my body.", "Alright, I'll just kill some time playing around with your body...", "You're raring to go, aren't you? Very well, let's see what you've got.", "Hhmn... My, my... you love my body so much? Of course you do, it can't be helped.", "Very well, entertain me the best you can.",  "...For now, I'm open to the idea.", "I don't really want to, but since you look so miserable I'll allow it.", "Haa, in the end, it turned out like this...  Fine then, do as you like.")
            else:
                lines = ("Oh... I guess if you like me it's ok.", "If you're so fascinated with me, let's do it.", "If you do it, then... please make sure it feels good.",  "I don't mind. Now get yourself ready before I change my mind.", "You're this horny...? Fine, then...", "Okay... I'd like to.",  "You insist, hm? Right away, then!", "You can't you think of anything else beside having sex? You're such a perv ♪", "You've got good intuition. That was just what I had in mind, hehe ♪", "Yes. Go ahead and let my body overwhelm you.", "All right. Do as you like.")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def refuse_sex(character):
            """
            Output line when the character refuses to have an intercourse with the hero
            """
            char_traits = character.traits
            if "Half-Sister" in char_traits and dice(65):
                if "Impersonal" in char_traits:
                    lines = ("No incest please.", "No. This is wrong.")
                elif "Yandere" in char_traits:
                    lines = ("Wait! We're siblings dammit.", "Hey, ummm... Siblings together... Is that really okay?")
                elif "Dandere" in char_traits:
                    lines = ("We're siblings. We shouldn't do things like this.", "Do you have sexual desires for your sister...?")
                elif "Imouto" in char_traits:
                    lines = ("[hero.hsC]! P... please don't say things like that!", "Having sex with a blood relative? That's wrong!")
                elif "Tsundere" in char_traits:
                    lines = ("It's... it's wrong to have sexual desire among siblings, isn't it?", "[hero.hsC], you idiot! Lecher! Pervert!")
                elif "Kuudere" in char_traits:
                    lines = ("...You want your sister's body that much? Pathetic.", "How hopeless can you be to do it with a sibling!")
                elif "Ane" in char_traits:
                    lines = ("What? But... I'm your sister.", "Don't you know how to behave yourself, as siblings?")
                elif "Kamidere" in char_traits:
                    lines = ("It's unacceptable for siblings to have sex!", "I can't believe... you do that... with your siblings!")
                elif "Bokukko" in char_traits:
                    lines = ("Oh boy, you are so weird.", "I'm your sis... Are you really okay with that?")
                else:
                    lines = ("No! [hero.hsC]! We can't do this!",  "Don't you think that siblings shouldn't be doings things like that?")
            elif "Impersonal" in char_traits:
                lines = ("I see no possible benefit in doing that with you so I will have to decline.", "Keep sexual advances to a minimum.")
            elif "Shy" in char_traits and dice(50):
                lines = ("I... I don't want that! ", "W-we can't do that. ", "I-I don't want to... Sorry.")
            elif "Imouto" in char_traits:
                lines = ("Noooo way!", "I, I think perverted things are bad!", "...I-I'm gonna get mad if you say that stuff, you know? Jeez!", "Y-you dummy! You should not be talking about stuff like s-s-sex!")
            elif "Dandere" in char_traits:
                lines = ("You're no good...", "Let's have you explain in full detail why you decided to do that today, hmm?", "You should really settle down.")
            elif "Tsundere" in char_traits:
                lines = ("I'm afraid I must inform you of your utter lack of common sense. Hmph!", "You are so... disgusting!", "You pervy little scamp! Not in a million years!", "Hmph! Unfortunately for you, I'm not that cheap!")
            elif "Kuudere" in char_traits:
                lines = ("G-get the fuck away from me, you disgusting perv.", "...Perv.", "...It looks like I'll have to teach you about this little thing called reality.", "O-of course the answer is no!", "Hmph, how unromantic!", "Don't even suggest something that awful.")
            elif "Kamidere" in char_traits:
                lines = ("Wh-who do you think you are!?", "W-what are you talking about... Of course I'm against that!", "What?! How could you think that I... NO!", "What? Asking that out of the blue? Know some shame!", "The meaning of 'not knowing your place' must be referring to this, eh...?", "I don't know how anyone so despicable as you could exist outside of hell.")
            elif "Bokukko" in char_traits:
                lines = ("He- Hey, Settle down a bit, okay?", "You should keep it in your pants, okay?", "Y-you're talking crazy...", "Hmph! Well no duh!")
            elif "Ane" in char_traits:
                lines = ("If I was interested in that sort of thing I might, but unfortunately...", "Oh my, can't you think of a better way to seduce me?", "No. I have decided that it would not be appropriate.", "I don't think our relationship has progressed to that point yet.", "I think that you are being way too aggressive.", "I'm not attracted to you in ‘that’ way.")
            elif "Yandere" in char_traits:
                lines = ("I've never met someone who knew so little about how pathetic they are.", "...I'll thank you to turn those despicable eyes away from me.", "What? Is that your dying wish? You want to die?")
            else:
                lines = ("No! Absolutely NOT!", "With you? Don't make me laugh.", "Get lost, pervert!", "Woah, hold on there. Maybe after we get to know each other better.", "Don't tell me that you thought I was a slut...?", "How about you fix that 'anytime's fine' attitude of yours, hmm?")
            iam.say_line(character, lines, "angry")

        @staticmethod
        def slave_refuse_sex(character):
            """
            Output line when the slave refuses to have an intercourse with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Understood.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I-I see... ", )
            elif "Imouto" in char_traits:
                lines = ("If that is your order, [mc_ref]...", )
            elif "Dandere" in char_traits:
                lines = ("...Do as you please, [mc_ref].", )
            elif "Tsundere" in char_traits:
                lines = ("Hmph. Go ahead [mc_ref], I won't stop you.", )
            elif "Kuudere" in char_traits:
                lines = ("I won't resist, [mc_ref].", )
            elif "Kamidere" in char_traits:
                lines = ("*sigh* If that's how you wish to treat me, [mc_ref], then let's do it.", )
            elif "Bokukko" in char_traits:
                lines = ("Gotcha. Cant's be helped, I guess.", )
            elif "Ane" in char_traits:
                lines = ("Very well, [mc_ref]. I obey your order.", )
            elif "Yandere" in char_traits:
                lines = ("I see. If I must, [mc_ref].", )
            else:
                lines = ("Yes, [mc_ref]...", )
            iam.say_line(character, lines, overlay_args=("sweat", "reset"))

        @staticmethod
        def refuse_sex_too_many(character):
            """
            Output line when the character refuses to have an intercourse with the hero, because of too much sex
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I believe it's enough for today.", "I don't feel the need to do it one more time.")
            elif "Shy" in char_traits and dice(50):
                lines = ("S-sorry, let's do it later m-maybe..?", "Um... Please, this is honestly too much for today...")
            elif "Imouto" in char_traits:
                lines = ("Stop it, that's annoying and boring!", "Uuuh, aren't you bored, doing it again and again?")
            elif "Dandere" in char_traits:
                lines = ("...You want to do it again? I don't want to.", "...Let's stop here. I'm tired of it.")
            elif "Tsundere" in char_traits:
                lines = ("Geez, give it a rest already!", "Ugh, you're really persistent. Stop it.")
            elif "Kuudere" in char_traits:
                lines = ("I think we should take a break.", "You're too persistent.")
            elif "Kamidere" in char_traits:
                lines = ("How many times are you going to do it?", "Unfortunately, I have no intentions to do it again.")
            elif "Bokukko" in char_traits:
                lines = ("Geez, enough already! I don't wanna to.", "Hey, it becomes annoying. Don't you want to do something else?")
            elif "Ane" in char_traits:
                lines = ("We keep doing it again and again... Let's stop it, alright?", "Persistence is not a virtue, you know?")
            elif "Yandere" in char_traits:
                lines = ("You are too persistent. I don't feel like it.", "Give it a rest. We already did it.")
            else:
                lines = ("Aren't you tired of it? I am.", "How many times are you going to do it?")
            iam.say_line(character, lines, overlay_args=("sweat", "reset"))

        @staticmethod
        def refuse_too_many(character):
            """
            Output line when the character refuses to talk due to too many attempts
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I request change of the subject.", "I don't feel the need to discuss this anymore.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... Can you stop already?", "Um... Please, this is honestly too much...")
            elif "Imouto" in char_traits:
                lines = ("Stop it, that's annoying and boring!", "Uuuh, aren't you bored, talking about it again and again?")
            elif "Dandere" in char_traits:
                lines = ("...You want to talk about that again?", "...It is a bother talking so much about the same thing.")
            elif "Tsundere" in char_traits:
                lines = ("Geez, give it a rest already!", "Ugh, you're really persistent!")
            elif "Kuudere" in char_traits:
                lines = ("The more persistent you get, the more I want to shoot down whatever you say.", "Geez, you're too persistent.")
            elif "Kamidere" in char_traits:
                lines = ("How many times are you going to talk about it?", "Why do you keep talking about it? We already discussed it.")
            elif "Bokukko" in char_traits:
                lines = ("Gawd, stop repeating yourself!", "Hey, it becomes annoying. Don't you want to talk about something else?")
            elif "Ane" in char_traits:
                lines = ("You keep going back to the same thing again and again... You're bothering me.", "Persistence is not a virtue, you know?")
            elif "Yandere" in char_traits:
                lines = ("I hate people who are too persistent.", "Give it a rest. We already discussed it.")
            else:
                lines = ("Why do you keep repeating yourself?", "Goodness, how many times are you going to talk about it?")
            iam.say_line(character, lines, overlay_args=("angry", "reset"))

        @staticmethod
        def refuse_talk_any(character):
            """
            Output line when the character refuses to talk at all
            """
            char_traits = character.traits
            mood = "defiant"
            if "Impersonal" in char_traits:
                lines = ("I request change of the subject.", "I don't really like this empty talk.")
                mood = "indifferent"
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... Could we talk about something else?", "Um... Please, this is honestly not that interesting...")
                mood = "uncertain"
            elif "Imouto" in char_traits:
                lines = ("Stop it, that's annoying and boring!", "Uuuh, what exactly do you want?")
            elif "Dandere" in char_traits:
                lines = ("Yeah-yeah... Whatever...", "... It is really a bother to talk about this now...")
                mood = "indifferent"
            elif "Tsundere" in char_traits:
                lines = ("Geez, can't you leave this subject?", "Ugh, you're really annoying!")
            elif "Kuudere" in char_traits:
                lines = ("Please stop if you have nothing to say!", "Not really interested in your empty talk...")
            elif "Kamidere" in char_traits:
                lines = ("You know, I'm really not interested in this!", "Can't you see I'm bored by your talk?")
            elif "Bokukko" in char_traits:
                lines = ("Gawd, stop bothering me with your nonsense!", "Hey, don't you want to talk about something else?")
            elif "Ane" in char_traits:
                lines = ("You're bothering me... Can't you stop now?", "Do you have something to say?")
            elif "Yandere" in char_traits:
                lines = ("I hate people who can't see when they are not needed.", "Are you finished now?")
            else:
                lines = ("This topic is really boring, don't you think?", "Goodness, could you actually say something?")
            iam.say_line(character, lines, mood)

        @staticmethod
        def provoked(character):
            """
            Output line when the character is provoked/upset by the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I now regard you as my enemy, and I will put you down by force.", "Understood... Let us discuss this matter with our fists.", "I don't want this to be a big deal. So let's just do it as quickly as possible.", "I will erase you.")
            elif "Imouto" in char_traits:
                lines = ("I have to hit you, or I won't be able calm myself!", "I'm toootally gonna make you cry!", "Ahaha, time to pound your face in!", "I-I'm going to make you accept your punishment!")
            elif "Dandere" in char_traits:
                lines = ("I'll make you regret to have angered me.", "You're ugly on the inside... Let's end this quickly.", "Seems like I have no choice but to restrain you physically.", "I'm selling a fist to the face. Please purchase one.")
            elif "Tsundere" in char_traits:
                lines = ("You insolent prick... I'll beat you here and now!", "Fufhn! I challenge you!", "Today's the day you stop getting away with this!", "It looks like I have no choice but... to do this!")
            elif "Kuudere" in char_traits:
                lines = ("Feel my anger with every bone in your body!", "You've got guts, but it won't keep you in one piece!", "I'll accept your challenge... And I'll acknowledge that you have some courage.", "Hmph. It's too late for regrets... Nothing's going to stop me now!")
            elif "Kamidere" in char_traits:
                lines = ("Aah, I'm pissed off now! Get ready!", "I'll teach you the meaning of pain!", "Come on... Hurry up and bring it.", "Kuh, don't come crying when you get hurt...!", "It seems like I need to teach you some manners.")
            elif "Bokukko" in char_traits:
                lines = ("So, I'm seriously angry now!", "Ok, I'm gonna hit you now. Just once. Well, I guess I'll smack you two or three more times after that. We clear?", "Hey, can I hit you? It's okay, right? Hey, hey!", "Lemme borrow that mug of yours real quick. 'Cause I'm gonna turn it into my personal punching bag.", "I kinda wanna deck you one. Don't move, 'kay?")
            elif "Ane" in char_traits:
                lines = ("It looks like you're never going to shape up unless I punish you...", "Just give me a moment please, it'll all end soon.", "I don't usually approve of this sort of thing, but I can't take it anymore!", "Please choose. Sit quietly and get hit, or struggle and get hit.")
            elif "Yandere" in char_traits:
                lines = ("You... have a shadow of death hanging over you...", "I'll pay you back in pain!", "Very well. I'll make it so you won't even be able to stand!", "You're at the end of your rope I'll wager.")
            else:
                lines = ("Geez, now I'm pissed!", "Geez, I will never forgive you!", "I can't deal with this. I want to hit you so bad I can't stop myself!", "Since it's come down to this, I'll have to use force!", "I didn't want to have to fight... but it seems like there's no other choice.")
            iam.say_line(character, lines, "angry")

        @staticmethod
        def fight_won(character):
            """
            Output line when the character won a fight against the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Just as I expected.", "The difference in power is so obvious.", "Now do you understand your own powerlessness?", "Not really a fair fight, was it?", "I'm not good at holding back.", "I think you underestimated me.")
            elif "Imouto" in char_traits:
                lines = ("Flawless victory! ♪", "Special service! I up my attacks by twenty percent ♪", "This must be my lucky day! Want more? ♪", "You're no match for me! ♪", "Ha! This is kiddy stuff!")
            elif "Dandere" in char_traits:
                lines = ("This victory was assured.", "That's what happens when you get in my way.", "You should pick your fights better.", "Like crashing a bug. Squish.", "That was easy. *Yawn*")
            elif "Tsundere" in char_traits:
                lines = ("Hah! Big mouth and little muscles!", "...Hmph! Did you really think you could win against me?", "Hmph, of course it was going to end this way.", "That wasn't much harder than combat practice...", "Over already? I'm just starting to get serious!", "Hmph! Laughable.", "Regret messing with me? Well it's too late now!")
            elif "Kuudere" in char_traits:
                lines = ("Cowards never win.", "Hmph. You're out of your league.", "I win, you lose, we're done.", "Phew, what a waste of time...", "And stay down.", "Tch, what a stupid waste of time.", "I will not deny you tried, but crude effort is no match for true ability.", "Is that it? I hardly did a thing.")
            elif "Kamidere" in char_traits:
                lines = ("Hmph, not even worth talking about...", "Hmph, charging in without knowing your opponent's strength... You're nothing but a stupid, weak animal.", "This is what you deserve.", "Oh, how pitiful!", "Hmph. They were pretty weak.", "Never stood a chance...")
            elif "Bokukko" in char_traits:
                lines = ("How much more of this you want?",  "'Course I won.", "Ahaha ♪ I'm so strong ♪", "Huh, so that's all you got?", "Piece of cake! ♪", "Is that it? I thought that would be tougher.", "I've got lots more where this comes from!")
            elif "Ane" in char_traits:
                lines = ("You should learn when to draw back.", "Phew, I wonder if you'll still stand up to me after that?",  "If you get in my way then I have no choice.", "Hmm. Was you too weak or I was too strong?", "Some problems cannot be solved by words alone.")
            elif "Yandere" in char_traits:
                lines = ("Lie on the ground... as you are...", "Another one bites the dust. I like it when it gets messy ♪", "That wasn't a battle, that was assisted suicide...", "Death is better than you deserve.", "I feel nothing for my enemy.", "Did that hurt? I hope it did ♪")
            else:
                lines = ("That was your best?", "Now you know the difference between us.", "Not much of a challenge.")
            iam.say_line(character, lines, "confident")

        @staticmethod
        def fight_lost(character):
            """
            Output line when the character lost a fight against the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Ugh... I underestimated you...", "I've failed...", "So I was defeated...", "My limbs are immobile...")
            elif "Imouto" in char_traits:
                lines = ("Oh, it hurts...", "Ugh, this wasn't supposed to happen...", "Ah...ahaha... I lost...", "I-I haven't...lost...yet...uu...")
            elif "Dandere" in char_traits:
                lines = ("Ugh... I lost...", "Kuh... Guess I got careless...", "It seems I can do no more...", "I... I cannot move...")
            elif "Tsundere" in char_traits:
                lines = ("Auu... This is terrible...", "I cannot allow myself... to be humiliated so...", "Why... has it come to this...?", "Tch... to think that I'd...")
            elif "Kuudere" in char_traits:
                lines = ("Uuu... How foolish of me...", "...I-impossible...I have been...", "Kuh... That's all I can...", "Tch... Damn it...!")
            elif "Kamidere" in char_traits:
                lines = ("Ugh... Frustrating...", "Guh... How did I...", "...Really, just... not my day...", "Why... can't I move?!")
            elif "Bokukko" in char_traits:
                lines = ("Why... did this happen...", "This... this isn't the way it's supposed to be...", "Uuh... I'm so uncool...", "Owie... This sucks...")
            elif "Ane" in char_traits:
                lines = ("Kuu... Why, like this...", "Ugh... How could this happened...", "Kuh, I misread you...", "I guess I wasn't strong enough...")
            elif "Yandere" in char_traits:
                lines = ("It has come to this...", "No... it cannot be...!", "Shit... This is... nothing...", "I... didn't expect that...")
            else:
                lines = ("Kuh, damn, you got me...", "Ugh, what the hell... geez...", "Kuh... You're... pretty good...", "But how... could I... ugh...")
            iam.say_line(character, lines, "angry")

        @staticmethod
        def got_insulted(character):
            """
            Output line when the character is insulted by the MC
            """
            char_traits = character.traits
            if character.status == "free":
                mood = "angry"
                if "Impersonal" in char_traits:
                    lines = ("...I see that you have a hostility problem.", "I can't believe you can look me in the eyes and say those things.", "...Are you talking about me? I see, so that's what you think of me.")
                elif "Shy" in char_traits and dice(50):
                    lines = ("Th-That's terrible! It's way too much!", "Th-that's... so cruel of you to say...", "N-no way... you're horrible...", "T-That's not true!")
                elif "Imouto" in char_traits:
                    lines = ("Hah! Y-You think that kind of abuse will have any effect on m-me?", "I'm so pissed off!", "I-I... I'm not like that!", "LA LA I CAN'T HEAR YOU!")
                elif "Dandere" in char_traits:
                    lines = ("...Are you trying to make me angry?", "...Are you teasing me?", "Do you want me to hate you that much?", "All bark and no bite. As they say.", "Was that meant to be an insult just now? How rude.")
                elif "Tsundere" in char_traits:
                    lines = ("You... you insolent swine!", "I-I will not forgive you!", "What was that?! Try saying that one more time!", "Hmph, I don't want to hear that from you!", "E-even if you say that, it doesn't mean anything to me, you know!")
                elif "Kuudere" in char_traits:
                    lines = ("...What did you say? Who do you think you are?", "Oooh, it's ok for me to accept this as a challenge, right...?", "Shut your mouth. Or do you want me to shut it for you?", "Oh, do you want to get hurt that badly?")
                elif "Kamidere" in char_traits:
                    lines = ("Huhn? It seem you want to make me your enemy.", "Oh? Is your mouth all you know how to use?", "Bring your face over here so I can slap it!", "You're really trash, aren't you...")
                elif "Bokukko" in char_traits:
                    lines = ("What's that? Are you picking a fight with me?", "...Hey, you. You're ready for a pounding, yeah?", "Hey fucker, you trying to start a fight?!", "Oh, so talkin's all you're good at, huh...")
                elif "Ane" in char_traits:
                    lines = ("You shouldn't say things like that.", "Hmm, I didn't know you were the type to say things like that...", "My, you have some nerve.", "Good grief... Your parents did a terrible job raising you.")
                elif "Yandere" in char_traits:
                    lines = ("What's that? You say you want to get hurt?", "...You should... be careful, when walking at night.", "Please die and come back as a better person, for everyone's sake.")
                else:
                    lines = ("Th-that's a terrible thing to say!", "Wh-why would you say that, that's so cruel...", "All talk and nothing to back it up. What are you even trying to do?", "What's your problem? Saying that out of nowhere.")
            else:
                mood = "indifferent"
                if "Impersonal" in char_traits:
                    lines = ("...I see that you have a hostility problem.", "I can't believe you can look me in the eyes and say those things.", "...Are you talking about me? I see, so that's what you think of me.")
                elif "Shy" in char_traits and dice(50):
                    lines = ("Th-That's terrible...", "Th-that's... so cruel of you to say...", "N-no way... you're horrible...", "T-That's not true!")
                elif "Imouto" in char_traits:
                    lines = ("Hah! Y-You think that kind of abuse will have any effect on m-me?", "I-I... I'm not like that!", "Ugh... *sniff* *sniff*")
                elif "Dandere" in char_traits:
                    lines = ("...Are you trying to make me angry?", "...Are you teasing me?", "Do you hate me that much?", "Was that meant to be an insult just now? How rude.")
                elif "Tsundere" in char_traits:
                    lines = ("I-I will not forgive you!", "Hmph, I don't want to hear that from you!", "E-even if you say that, it doesn't mean anything to me, you know!")
                elif "Kuudere" in char_traits:
                    lines = ("...What did you say? Who do you think you are?", "Oooh, so brave in front of a slave...", "Shut your mouth...", "One day, saying these things will get you hurt...")
                elif "Kamidere" in char_traits:
                    lines = ("Huhn? It seem you want to make me your enemy.", "Oh? Is your mouth all you know how to use?", "You're really trash, aren't you...")
                elif "Bokukko" in char_traits:
                    lines = ("Are you picking a fight with me? Well too bad, I won't give you the pleasure.", "...Hey, what's wrong with you? Why are you harassing me like that?", "Oh, so talkin's all you're good at, huh...")
                elif "Ane" in char_traits:
                    lines = ("You shouldn't say things like that.", "Hmm, I didn't know you were the type to say things like that...", "Good grief... Your parents did a terrible job raising you.")
                elif "Yandere" in char_traits:
                    lines = ("Hey, it would be better if you didn't talk like that.", "I swear, one day you'll regret it...", "Please die and come back as a better person, for everyone's sake.")
                else:
                    lines = ("Th-that's a terrible thing to say!", "Wh-why would you say that, that's so cruel...", "What's your problem? Saying that out of nowhere.")
            iam.say_line(character, lines, mood)

        @staticmethod
        def got_insulted_hdisp(character):
            """
            Output line when a character with high disposition is insulted by the MC
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Huh? You kidding?", "Excuse me?")
            elif "Shy" in char_traits and dice(50):
                lines = ("Ah... Eh... Aah! This is a joke... Right?", "Umm... Ah! Th-that was funny, wasn't it?")
            elif "Imouto" in char_traits:
                lines = ("Ufufu, I'm not falling for that joke!", "Haha, what are you talking about?")
            elif "Dandere" in char_traits:
                lines = ("Not funny.", "I will overlook it this time, but that's harassment, you know?")
            elif "Tsundere" in char_traits:
                lines = ("Wha!? ...That...wasn't very funny, you know?", "W-What are you saying? Jeez, stop joking like that...")
            elif "Kuudere" in char_traits:
                lines = ("That was quite the harsh joke.", "Hah, ain't that a funny joke.")
            elif "Kamidere" in char_traits:
                lines = ("Geez, stop joking around.", "What a supremely boring joke. You've got awful taste.")
            elif "Bokukko" in char_traits:
                lines = ("Jeez, your jokes are so mean.", "Mm, sounds kinda boring, y'know?")
            elif "Ane" in char_traits:
                lines = ("Oh, you, stop it with your childish pranks.", "Mumu... Looking forward to seeing my reaction, are you? Well too bad, I won't give you the satisfaction ♪")
            elif "Yandere" in char_traits:
                lines = ("Go easy on the jokes, hey?", "Hey now, that's harsh for a joke.")
            else:
                lines = ("Come on, knock it off with the jokes!", "Jeez, stop playing around.")
            iam.say_line(character, lines)

        @staticmethod
        def got_insulted_slave(character):
            """
            Output line when a slave is insulted by the MC
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Huh? If I did something wrong, please tell me immediately, [mc_ref].", "Is there something wrong with my behavior? Please clarify.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Eh... S-sorry... W-what's this about? D-did I upset you somehow?", "P-please don't be mad at me...")
            elif "Imouto" in char_traits:
                lines = ("Wha? Stop calling me that, [mc_ref]! Or I'm g-gonna cry!", "You big meanie... *sniff*")
            elif "Dandere" in char_traits:
                lines = ("...Understood. May I return to my duties now, [mc_ref]?", "What's the point of insulting your own properly, [mc_ref]? I don't understand.")
            elif "Tsundere" in char_traits:
                lines = ("Hmhm! You think it's funny to abuse your slaves? Idiot...", "W-What are you saying? And here I do my best to follow you orders... Jeez...")
            elif "Kuudere" in char_traits:
                lines = ("That was quite harsh, [mc_ref]. Is something wrong?", "Hah, you really need a hobby, [mc_ref]... No, abusing your slaves is not one.")
            elif "Kamidere" in char_traits:
                lines = ("*sigh* Stop messing around, [mc_ref]. Just tell what do you need.", "Great, now I've been abused. Happy now, [mc_ref]?")
            elif "Bokukko" in char_traits:
                lines = ("Oh boy. You are so mean to me today, [mc_ref].", "Okish, if you say so. Anything else, [mc_ref]?")
            elif "Ane" in char_traits:
                lines = ("[mc_ref], calling me names won't solve anything.", "Gosh, please grow up a little, [mc_ref]. Treating loyal slaves like that is unacceptable.")
            elif "Yandere" in char_traits:
                lines = ("I'm sorry I cannot be a better person for you, [mc_ref].", "[mc_ref], are you mad at me? If so, I will accept anything to make you forgive me.")
            else:
                lines = ("*sigh* If abusing me makes you feel better, then it can't be helped...", "That was uncalled for, [mc_ref]. Seriously...")
            iam.say_line(character, lines)

        @staticmethod
        def accept_lover_end_mc(character):
            """
            Output line when the character and the MC break their relationship (the hero initiates it)
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Well... There's nothing that can be done about it.", "I...see. That's a shame.", "Hm... Then I suppose this is the end, I understand.", "Starting now, you and I are strangers.")
            elif "Shy" in char_traits and dice(50):
                lines = ("You're... right... Yes, thank you for everything until now...", "I'm sorry... I... I guess I was a failure of a woman...", "I'm sorry... I'm so worthless...", "I-if you hate me, then you should've just said it straight...", "...I see. Thanks for everything...", "...I understand. But, please, don't forget about me...")
            elif "Imouto" in char_traits:
                lines = ("I-I won't be lonely... I'll be fine, so...", "I'm sorry... I was too immature... I'm sorry...", "I see... Still, it was fun while it lasted...")
            elif "Dandere" in char_traits:
                lines = ("Is that so... I apologize for having been such an imperfect woman...", "Certainly, let us both see the end of this limitless futility.", "Is that so... I guess it couldn't be helped... That makes us strangers now.")
            elif "Tsundere" in char_traits:
                lines = ("Hmph! Fine, then! The one who will crawl back is you!", "Just get out of here already. And don't let me see you again.", "You really don't care about me at all, huh?")
            elif "Kuudere" in char_traits:
                lines = ("...Fine. Go away. ...I said get the hell away from me!", "I understand... It's going to be a little lonely...", "Is that so. Very well, now disappear before I beat you to a pulp.", "If that's really how you want things... Then I guess I don't have much choice but to accept.")
            elif "Kamidere" in char_traits:
                lines = ("If you didn't love me, you could've said so earlier... Goodbye...", "Hmph, you'll regret breaking up with me, I promise you...", "I see... It had to happen sometime, huh... Yeah... you're right...")
            elif "Bokukko" in char_traits:
                lines = ("Oh... Yeah, I suppose this is as good a time as any...", "I see... that's too bad... Really...", "Man, well I guess I can't do anything about it...")
            elif "Ane" in char_traits:
                lines = ("If being with me bothers you, then leave. You've got others anyway, right?", "Is that so... I guess the time has come... I understand.", "I don't... want to be with you any more.")
            elif "Yandere" in char_traits:
                lines = ("...Yeah. Being with someone like me is impossible, I guess. It's fine. Bye bye...", "If that is what you desire... Then so be it...", "I'm grateful for the time we spent together...")
            else:
                lines = ("What a shame, I'd thought it would have worked out better... It really is a shame...", "...If you say it has to be like that, then it can't helped...", "I understand... Thank you for having loved me...")
            iam.say_line(character, lines)

        @staticmethod
        def lover_end(character):
            """
            Output line when the character and the MC break their relationship (the character initiates it)
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Don't follow me around anymore. I... want to break up.", "I'm sorry, I can't be with you anymore.", "I feel like I have to bring this to an end, for the sake of the future.")
            elif "Shy" in char_traits and dice(50):
                lines = ("I'm sorry... I can't bring myself to like you anymore...", "Um... Let's break up... I can't keep this up...", "I'm sorry ... I can't love you from my heart... We should break up.")
            elif "Imouto" in char_traits:
                lines = ("Um, you know... Maybe we should go our separate ways...?", "If you don't love someone, you should break up with them, right? So anyway, could we break up?", "Hey, I kinda wanna stop dating you...")
            elif "Dandere" in char_traits:
                lines = ("My patience with you has come to an end. Our association ends here.", "Let's break up already... It'll definitely be for the best.", "We should break up. I'm no longer in love with you.")
            elif "Tsundere" in char_traits:
                lines = ("You were a disappointment. We're over. Now.", "Hey... I've fallen out of love with you. Let's break up.", "It seems that I'm no longer needed. Isn't that right?")
            elif "Kuudere" in char_traits:
                lines = ("Haah... It was a mistake to date someone like you...", "I can't keep going out with you anymore. Let's break up.", "Sorry... I can't think of you as my number one anymore.", "I'm sorry, I just can't stand to be with you anymore.")
            elif "Kamidere" in char_traits:
                lines = ("Being in a relationship is more trouble than it's worth. I knew this wouldn't work out.", "When you become as popular as me, you'll never be short on people to date. So I'm done with you.", "I've grown tired of you, so I don't need you anymore.")
            elif "Bokukko" in char_traits:
                lines = ("I have no interest in you anymore. Let's break up.", "Don't you want to break up with me? You do, don't you?", "Ah, sorry, I don't really like you anymore. We're over.")
            elif "Ane" in char_traits:
                lines = ( "I've had enough... I no longer want to be by your side.", "I'm not strong enough to date someone I don't care for...", "Let's break up. It's for the best, for both of us.", "I think it'll be better if you look for someone that's more suited for you.")
            elif "Yandere" in char_traits:
                lines = ("I'm sorry for being so inconsiderate, but... forget about me...", "I... don't think of you as the one anymore...", "I don't have it in me to love you any longer. Let's end this.")
            else:
                lines = ("Jeez, I don't want to date someone I can't stand.", "I can't think of you as my number one anymore. We are done...", "I don't think this is working out. Let's break up.", "I've been thinking a lot lately... I think things would be better off if we broke up.")
            iam.say_line(character, lines)

        @staticmethod
        def refuse_lover_end_mc(character):
            """
            Output line when the MC wants to break the relationship, but the character does not let it go
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I'll never let go of you. For the rest of my life.", "...Impossible. That could never, ever happen.", "I have no intention of letting you go.", "Denied. That's not for you to decide.")
            elif "Shy" in char_traits and dice(50):
                lines = ("N-Never! I'll do anything... I'll love you even more...!", "I'm afraid we cannot be separated. We are bound by fate after all...", "Huh? ...Y-you must be really tired, let's take it easy for now, okay?", "...Sorry, there's no way I could give you up.", "I'll do better, I promise... so... I'm sorry... I'm so pathetic...", "I... I don't want that! Please, don't leave me...")
            elif "Imouto" in char_traits:
                lines = ("Eh? Why? I still love you lots, you know?", "Oh you, always with the jokes ♪ You're just testing my love, right? You big meanie! ♪", "Abso. Lutely. Not! I'm not letting you go! We'll always be together!")
            elif "Dandere" in char_traits:
                lines = ("I am terribly sorry. I did not show you enough affection, did I?", "Don't even try. I never want to leave you.", "That's impossible. We're gonna be together forever.")
            elif "Tsundere" in char_traits:
                lines = ("You're my life partner, this' already been decided. There's nothing that can keep us apart at this point.", "What are you saying...? Our bond is eternal, don't you know?", "Oh, are you being tsundere? You don't need to be that way, dummy ♪")
            elif "Kuudere" in char_traits:
                lines = ("What do you mean? The two of us are fated to never be apart.", "You own me. And I own you.", "Rest assured. You don't need to test me like that, I won't let you go. Hmhm ♪")
            elif "Kamidere" in char_traits:
                lines = ("Why is that? There's no reason for us to break up, is there?", "Oh please, you're just trying grab more of my attention, aren't you? Geez ♪", "Oh..? do you really think I'd let you slip through my fingers?")
            elif "Bokukko" in char_traits:
                lines = ("Hehe... You're testing me, aren't you? ...I get it, I get it already... hehehe", "I gotcha, I just have to try harder, right? Ehehe...♪", "Eh? You and I share the same fate. Breaking up is unthinkable!")
            elif "Ane" in char_traits:
                lines = ("W-why are you saying that...? Even though I love you so much... Why...!?", "If there's something about me that's inadequate, I swear I'll fix it...! So, please... Let me stay by your side...!")
            elif "Yandere" in char_traits:
                lines = ("...Who's the one trying to lead you astray? Who is it! Hey, tell me. TELL ME!", "What are you saying? Until they put us in the same grave, you're mine!", "...Who stole you from me? Who's the one trying to stand between us?")
            else:
                lines = ("Come on, knock it off with the jokes!", "Jeez, stop playing around.", "Huh? No way, you're mine, after all.")
            iam.say_line(character, lines)

        @staticmethod
        def offer_lover_again(character):
            """
            Output line when the character wants to renew the relationship with the MC
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I want to mend our broken relationship. Please.", "Hey... Can we... start over?", "Can we... start over?")
            elif "Shy" in char_traits and dice(50):
                lines = ("I... I can't go on without you... So please, let me date you again.", "I know it's selfish of me... But...I just can't forget about you...")
            elif "Imouto" in char_traits:
                lines = ("...D-don't you think it's about time we... went back to how we were before?", "Hey... I... want to get back together.", "Umm... Seems like I'm still in love with you... So, can we get back together...?")
            elif "Dandere" in char_traits:
                lines = ("I just can't forget about you... Do you want to try starting over?","Would it be possible for us to fix what we had?", "Be with me again. ...I need you.")
            elif "Tsundere" in char_traits:
                lines = ("Um, so...I, I wanna go out with you again...", "I can't... I simply can't give up on you... Let me be with you, one more time.", "Call me weak or whatever, I don't care. I just...I want us to start over!")
            elif "Kuudere" in char_traits:
                lines = ("I want to be by your side again. It's all I can think about lately...", "You're the one who soothes my heart the most, after all... Want to start over again?", "Perhaps it is stubborn of me, but... I would like to reconcile with you.")
            elif "Kamidere" in char_traits:
                lines = ("Hey, I'd like a chance for us to start things over.", "We can still go back to how things used to be, you know?", "I realized... I'm still in love with you after all.")
            elif "Bokukko" in char_traits:
                lines = ("Y'see, like... Y'wanna try goin' back to the way things were before?", "Mmh, it just doesn't do it for me if it isn't you. Can we...go out again?", "I-if you're okay with it, I'd like us to get back together... What do you think?")
            elif "Ane" in char_traits:
                lines = ("I'll fix whatever's wrong with me, so... Please, just let me be with you again.", "I can't seem to forget about you no matter what I do... I want to start things over with you.")
            elif "Yandere" in char_traits:
                lines = ("I want to give us another try. ...Please.", "Sorry... No matter what I do, I can't get you out of my head... So...")
            else:
                lines = ("Hey, could we maybe... see if we can work things out again?", "If we were to be together again, I'd... No... Please, one more time, be with me!")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def apology(character):
            """
            Output line when the character says sorry
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Sorry. My bad.", "I am very sorry.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I-I... I-I'm s-sor...ry...", "I-I'm so sorry... How could I...")
            elif "Imouto" in char_traits:
                lines = ("I'm sowweeeeee, forgive meeeeee...", "I'm sorry, I'm sorry, I'm sorry!")
            elif "Dandere" in char_traits:
                lines = ("...My bad. Forgive me.", "...Sorry about that.")
            elif "Tsundere" in char_traits:
                lines = ("I-I'm sorry... I said I was sorry, alright?", "I'm honestly really sorry!")
            elif "Kuudere" in char_traits:
                lines = ("I was wrong... It's as you see, forgive me...", "I'm sorry... Forgive me.", "Sorry, I guess that was a bit thoughtless...")
            elif "Kamidere" in char_traits:
                lines = ("It is my fault, isn't it... Forgive me.", "I suppose I could offer you an apology. I'm sorry.")
            elif "Bokukko" in char_traits:
                lines = ("I'm sorry. I did something terrible...", "Um, so, ...'m sorry.", "Well, y'know... Sorry.")
            elif "Ane" in char_traits:
                lines = ("Please find it in your heart to forgive me.", "I really need to apologize.")
            elif "Yandere" in char_traits:
                lines = ("I'm very sorry, I just...", "I'm sorry, if you could somehow forgive me...", "I'm responsible for all of this! I am so, so sorry!")
            else:
                lines = ("Um... I'm sorry...", "Sorry, please forgive me...")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def offer_bribe(character, amount):
            """
            Output line when the character tries to bribe the hero
            """
            # TODO traits
            lines = ("I can pay you [amount].", "Would [amount] suffice?", "I have only [amount] Gold with me. Is that enough compensation?")
            iam.say_line(character, lines, "uncertain", msg_args={"[amount]": str(amount)})

        @staticmethod
        def offer_bribe_sex(character):
            """
            Output line when the character tries to bribe the hero with sex
            """
            # TODO traits
            lines = ("I know how to make people happy. Why don't we solve this between us?", "I know many ways to satisfy unhappy customers. I'll tell you more in private.", "Just act like real grown-ups. I'm very good handling private stuff...")
            iam.say_line(character, lines, "suggestive")

        @staticmethod
        def refuse_bribe(character):
            """
            Output line when the character can not bribe the hero, because of lack of money
            """
            # TODO traits
            lines = ("I have nothing! Please let it go.", "I'm poor, could we just go on?")
            iam.say_line(character, lines, "sad")

        @staticmethod
        def got_injured(character):
            """
            Output line when the character suffers an injury
            """
            global block_say
            char_traits = character.traits
            mood = "indifferent"
            if "Impersonal" in char_traits:
                lines = ("Uff... I got hurt...", )
            elif "Shy" in char_traits:
                mood = "sad"
                lines = ("Um, what happened to me... Oh, I see...", )
            elif "Imouto" in char_traits:
                mood = "scared"
                lines = ("Ouch?! Uuh, I'm bleeding!", )
            elif "Dandere" in char_traits:
                lines = ("Ohh well... Now I got hurt...", )
            elif "Tsundere" in char_traits:
                lines = ("What is it? Just a small bruise.", )
            elif "Kuudere" in char_traits:
                lines = ("Ehh.. Why does this happen always to me?", )
            elif "Kamidere" in char_traits:
                lines = ("Uhh... Don't worry, I'm going to be fine.", )
            elif "Bokukko" in char_traits:
                lines = ("Mmm. Nothing, but a scratch.", )
            elif "Ane" in char_traits:
                lines = ("Oh my... Another wound, but it is going to heal soon.", )
            elif "Yandere" in char_traits:
                lines = ("Oh... I'm alright... Or will be soon...", )
            else:
                lines = ("Right. Nothing... It is just a wound to tend to.", )
            block_say = True
            iam.say_line(character, lines, mood)
            block_say = False

        @staticmethod
        def refuse_swing(character):
            """
            Output line when the character refuses to go to the swinger club with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I see no possible benefit in going there with you so I will have to decline.", "Keep sexual deviations to a minimum.")
            elif "Shy" in char_traits and dice(50):
                lines = ("I... I don't want that! ", "W-we can't do that. ", "I-I don't want to... Sorry.")
            elif "Imouto" in char_traits:
                lines = ("Noooo way!", "I, I think perverted things are bad!", "...I-I'm gonna get mad if you suggest such things, you know? Jeez!", "Y-you dummy! You should not go to such place!")
            elif "Dandere" in char_traits:
                lines = ("You're no good...", "Let's have you explain in full detail why you decided to do that today, hmm?", "You should really think before you try to drag me into such things...")
            elif "Tsundere" in char_traits:
                lines = ("I'm afraid I must inform you of your utter lack of common sense. Hmph!", "You are so... disgusting!", "You pervy little scamp! Not in a million years!")
            elif "Kuudere" in char_traits:
                lines = ("G-get the fuck away from me, you disgusting perv.", "...Perv.", "...It looks like I'll have to teach you about this little thing called reality.", "O-of course the answer is no!", "Don't even suggest something that awful.")
            elif "Kamidere" in char_traits:
                lines = ("Wh-who do you think you are!?", "W-what are you talking about... Of course I'm against that!", "What?! How could you think that I... NO!", "What? Suggesting that out of the blue? Know some shame!", "The meaning of 'not knowing your place' must be referring to this, eh...?", "I don't know how anyone so despicable as you could exist outside of hell.")
            elif "Bokukko" in char_traits:
                lines = ("He- Hey, let us go somewhere else, okay?", "Find someone else if you want to visit such a place, okay?", "Y-you're crazy...", "Hmph! Well no duh!")
            elif "Ane" in char_traits:
                lines = ("If I was interested in that sort of thing I might, but unfortunately...", "Oh my, can't you think of something more reasonable?", "No. I have decided that it would not be appropriate.", "I don't think I would like to visit such a place. With or without you...", "I think that you are being way too insensitive.")
            elif "Yandere" in char_traits:
                lines = ("I've never met someone who knew so little about how pathetic they are.", "...I'll thank you to just let me leave now.", "What? Is that your dying wish? You want to die?")
            else:
                lines = ("No! Absolutely NOT!", "With you? Don't make me laugh.", "Get lost, pervert!", "Woah, hold on there. How did this even cross your mind?", "Don't tell me that you thought I was a slut...?", "How about you fix that 'anything goes' attitude of yours, hmm?")
            iam.say_line(character, lines, "angry")

        ##############################          GREETINGS          ##############################

        @staticmethod
        def greeting_cafe(character):
            """
            Output line when the NPC greets the hero in the cafe
            assumptions: the value of reputation is between -1000 and 1000
                         the value of fame is between 0 and 1000
            """
            rep, fame = hero.get_stat("reputation"), hero.get_stat("fame")
            overlay_args = None
            if rep > 600:
                if fame > 750:
                    lines = ("Welcome back! Your table is ready as always!", )

                    mood = "shy" if dice(50) else "ecstatic"
                    overlay_args=("like", "reset")
                elif fame > 500:
                    lines = ("Welcome back! Please, have a seat!", )

                    mood = "happy"
                    overlay_args=("note", "reset")
                elif fame > 250:
                    lines = ("Welcome back! Can I get you a table?", )

                    mood = "happy" if dice(50) else "confident"
                    if dice(25):
                        overlay_args=("note", "reset")
                else:
                    lines = ("Welcome! Can I get you a table?", )

                    mood = "confident"
            elif rep > 200:
                # reputation 200 .. 600
                if fame > 750:
                    lines = ("My pleasure to see you again! Can I get you a table?", )

                    mood = "shy" if dice(50) else "happy"
                    overlay_args=("like" if dice(25) else "note", "reset")
                elif fame > 500:
                    lines = ("It is a pleasure to see you! Do you want a table?", )

                    mood = "happy"
                    if dice(50):
                        overlay_args=("note", "reset")
                elif fame > 250:
                    lines = ("Welcome back! Do you want a table?", )

                    mood = "confident"
                else:
                    lines = ("Welcome! Do you want a table?", )

                    mood = "indifferent"
            elif rep > -200:
                # reputation -200 .. 200
                if fame > 750:
                    lines = ("I'm glad to see you again! Do you want a table?", )

                    mood = "happy"
                elif fame > 500:
                    lines = ("It is nice to see you. Do you want a table?", )

                    mood = "happy" if dice(50) else "uncertain"
                elif fame > 250:
                    lines = ("Yes? Can I get you a table?", )

                    mood = "uncertain"
                else:
                    lines = ("Welcome. Do you want a table?", )

                    mood = "indifferent"
            elif rep > -600:
                # reputation -600 .. -200
                if fame > 750:
                    lines = ("We have expecting you, %s!" % ("Madame" if hero.gender == "female" else "Sir"), )

                    mood = "scared" if dice(50) else "sad"
                    overlay_args=("sweat" if dice(50) else "scared", "reset")
                elif fame > 500:
                    lines = ("If you want a table, just let me know.", )

                    mood = "sad" if dice(50) else "uncertain"
                    if dice(50):
                        overlay_args=("sweat", "reset")
                elif fame > 250:
                    lines = ("What do you want? A table?", )

                    mood = "defiant"
                    if dice(25):
                        overlay_args=("sweat", "reset")
                else:
                    lines = ("Do you want a table?", )

                    mood = "indifferent"
            else:
                # reputation -1000 .. -600
                if fame > 750:
                    lines = ("A table is ready as soon as you want one!", )

                    mood = "scared"
                    overlay_args=("scared", "reset")
                elif fame > 500:
                    lines = ("Yes, %s?!" % ("Madame" if hero.gender == "female" else "Sir"), )

                    mood = "sad"
                    overlay_args=("sweat", "reset")
                elif fame > 250:
                    lines = ("What can I get you?", )

                    mood = "uncertain"
                    if dice(50):
                        overlay_args=("sweat", "reset")
                else:
                    lines = ("Do you want a table?", )

                    mood = "defiant"

            iam.say_line(character, lines, mood, overlay_args)

        ##############################           GOSSIPS           ##############################

        @staticmethod
        def gossip_peevish_in_forest(character):
            """
            Output line when the character gossips about peevish's whereabout
            """
            char_traits = character.traits
            mood = "indifferent"
            if "Impersonal" in char_traits:
                lines = ("The stories about the strange AND magical creature of the forest... Isn't it the same?", )
            elif "Shy" in char_traits:
                lines = ("Um, you heard these strange stories about a magical creature living in the forest?", )
            elif "Imouto" in char_traits:
                mood = "scared"
                lines = ("There lives a magical creature right next to the city. You can hear strange stories about it!", )
            elif "Dandere" in char_traits:
                lines = ("Where can you be safe when there lives an invisible 'magical' creature right next to the city?", )
            elif "Tsundere" in char_traits:
                lines = ("A strange creature in the forest they say? Who isn't strange is some ways, right?", )
            elif "Kuudere" in char_traits:
                lines = ("Everyone talks about a magical creature in the forest, but why should I care?", )
            elif "Kamidere" in char_traits:
                lines = ("That magical creature in the forest must be really powerful if it can hide in plain sight.", )
            elif "Bokukko" in char_traits:
                lines = ("Hah. Some says they saw a strange creature in the forest, but I really doubt it.", )
            elif "Ane" in char_traits:
                lines = ("Did you hear? They say some strange creature lives in the forest right next to the city.", )
            elif "Yandere" in char_traits:
                lines = ("The magical creature of the forest must feel really lonely sometimes, don't you think?", )
            else:
                lines = ("I hope the strange, magical creature of the forest won't disturb us in the city.", )
            iam.say_line(character, lines, mood, gossip=True)

        @staticmethod
        def gossip_aine_in_park(character):
            """
            Output line when the character gossips about aine's whereabout
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("It should be prohibited to beome invisible. It is really upsets people, even in public places like the park.", )
            elif "Shy" in char_traits:
                lines = ("You also heard the rumors about the ghost of the park? I hope it is just a wind.", )
            elif "Imouto" in char_traits:
                lines = ("Sometimes when I walk in the park, I get the feeling that I'm not alone!", )
            elif "Dandere" in char_traits:
                lines = ("Nowadays you have to avoid being alone in the park. There are rumors about a 'fairy'...", )
            elif "Tsundere" in char_traits:
                lines = ("The fairy of the park should really stop scaring the people. It is a fairy after all, right?", )
            elif "Kuudere" in char_traits:
                lines = ("And now a 'ghost' in the park... Does it really bother anyone?", )
            elif "Kamidere" in char_traits:
                lines = ("There can not be a fairy in the park. A real fairy would not scare people like that.", )
            elif "Bokukko" in char_traits:
                lines = ("I heard someone was spooked by a ghost in the park. How naïve..", )
            elif "Ane" in char_traits:
                lines = ("Ohh dear, that poor fairy in the park must have lost its way..", )
            elif "Yandere" in char_traits:
                lines = ("I guess that the magical creature in the park is sometimes surprised by us the same as some of us by them.", )
            else:
                lines = ("With the fairy in the park I think we start to get overrun by non-humans.", )
            iam.say_line(character, lines, gossip=True)

        ##############################     TODO unused methods     ##############################

        @staticmethod
        def demand_apology(character):
            """
            Output line when the character demands an apology from the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Apologize. Then we'll talk.", "I won't forgive you unless you apologize.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Please apologize...", "Isn't there... something you want to apologize about first?")
            elif "Imouto" in char_traits:
                lines = ("Umm, if you grovel in the dirt for me, I'll forgive you...", "I might consider forgiving you if you grovel pitifully.")
            elif "Dandere" in char_traits:
                lines = ("I'll forgive you if you apologize.", "Is it impossible for you to give an apology?", "...You should know that I haven't forgiven you just yet.")
            elif "Tsundere" in char_traits:
                lines = ("It'd be nice if you apologized, you know...!", "...Apologize. APOLOGIZE!")
            elif "Kuudere" in char_traits:
                lines = ("What, not even a single word of apology?", "Until you apologize I'm not talking to you.")
            elif "Kamidere" in char_traits:
                lines = ("Huh? Apologize first.", "Um... Where is my «I'm sorry»?")
            elif "Bokukko" in char_traits:
                lines = ("Hm, finally feel like apologizin'?", "Hey, don't you think there's something you oughta be apologizing for?", "C'mon now, hurry up and apologize. It's for your own good, y'know?")
            elif "Ane" in char_traits:
                lines = ("Oh dear, do you not know how to apologize?", "I will not forgive you until you reflect on what you've done.")
            elif "Yandere" in char_traits:
                lines = ("Apologize. Did you not hear me? It means tell me you're sorry.", "...I demand an apology.")
            else:
                lines = ("Start apologizing, please! I'll let you know when it's enough.", "Hey, isn't there something you need to apologize for first...?")
            iam.say_line(character, lines)

        @staticmethod
        def accept_apology(character):
            """
            Output line when the character accepts an apology from the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I understand. However, do not think that this will happen another time.", "...Never again, okay?")
            elif "Imouto" in char_traits:
                lines = ("...If you say you'll never do it again, then... Alright...", "Fine, fine, I'll forgive you...", "Hrmm... just this once, okay?")
            elif "Dandere" in char_traits:
                lines = ("...I don't really mind.", "I suppose I could...", "...Please do not do it again.")
            elif "Tsundere" in char_traits:
                lines = ("Well I guess I could if you're gonna go that far.", "Hmph... I haven't COMPLETELY forgiven you, okay?")
            elif "Kuudere" in char_traits:
                lines = ("Hmph... There won't be a next time.", "Hm, I'm too soft... Just this once, alright?", "...I'll let it slide.")
            elif "Kamidere" in char_traits:
                lines = ("...Haah... I'm not mad at you anymore.", "Hmph. You should be grateful I'm so lenient.", "...Yeaaah, yeaaah. I get it. I'll forgive you, just get off my case already.")
            elif "Bokukko" in char_traits:
                lines = ("Hmph... And now you know never to do that again.", "Fine, if you insist...", "It's fine, I don't really care anymore.")
            elif "Ane" in char_traits:
                lines = ("Well, I was being childish too... Sorry.", "Yes... Let's reconcile.", "Hmhm, it seems you've reflected on your actions. Well done.")
            elif "Yandere" in char_traits:
                lines = ("If you do it again, I'll be even angrier, okay?", "Well, I've got no reason not to forgive you.")
            else:
                lines = ("It's okay, I'll forgive you this time.", "...Just this once. Got it?", "...Alright, I'll put my trust in you one more time.")
            iam.say_line(character, lines)

        @staticmethod
        def refuse_apology(character):
            """
            Output line when the character refuses an apology from the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Forgiving you is not something I am capable of.", "I won't forgive you...")
            elif "Imouto" in char_traits:
                lines = ("I-I'll never forgive you...!", "I'll never forgive you!", "Aaahhh... can't hear a thing...")
            elif "Dandere" in char_traits:
                lines = ("I'll never forgive you. Ever.", "I will never forgive you.", "I will definitely not forgive you.")
            elif "Tsundere" in char_traits:
                lines = ("Unforgivable. Absolutely not!", "I am DEFINITELY not letting you off the hook for this one!")
            elif "Kuudere" in char_traits:
                lines = ("Is this your shitty attempt at 'sincerity'?", "I will not forgive this, definitely not.", "I will not forgive you.")
            elif "Kamidere" in char_traits:
                lines = ("You think I'll forgive you with an apology like that?", "I won't forgive this easily.", "Hmph. You think I'd let you off the hook that easily?")
            elif "Bokukko" in char_traits:
                lines = ("Huh? ...You thought I'd forgive you?", "I'm neeeeever gonna forgive you!", "Wha? As if I'd forgive ya.")
            elif "Ane" in char_traits:
                lines = ("I'll never forgive you.", "I won't forgive you, no matter what.", "I don't think you've properly thought about what you've done yet.")
            elif "Yandere" in char_traits:
                lines = ("I'm not forgiving you, no matter what!", "Unforgivable...")
            else:
                lines = ("I'm not going to forgive you, ever!", "I'll never forgive you, you got that?", "Sorry...I can't trust you just yet.")
            iam.say_line(character, lines)

        @staticmethod
        def broken_promise(character):
            """
            Output line when the character realizes the MC does not keep his/her promise
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I suppose the promise was but lip service... after all.", "You don't keep promises, do you...")
            elif "Shy" in char_traits and dice(50):
                lines = ("It's okay, I'm sure you have your priorities too, right...? But still...", "It's fine... I didn't think you'd show up anyway.")
            elif "Imouto" in char_traits:
                lines = ("I was so lonely, all by myself...", "...I even waited for you.")
            elif "Dandere" in char_traits:
                lines = ("I was waiting forever...", "You promised...", "It seems I have been thoroughly fooled.")
            elif "Tsundere" in char_traits:
                lines = ("Why didn't you come...? You idiot...", "You idiot! Liar! I can't believe this!")
            elif "Kuudere" in char_traits:
                lines = ("Tch. I guess a promise with me just isn't worth remembering, huh...", "Is it too much for you to keep even a single promise?")
            elif "Kamidere" in char_traits:
                lines = ("You're horrible... I was waiting the whole time...", "Jeez, why didn't you show up? Keep your promises!")
            elif "Bokukko" in char_traits:
                lines = ("You're the kind of trash that can't even keep a little promise, aren't you.", "What d'you think promises are for? Hmm?")
            elif "Ane" in char_traits:
                lines = ("No, no, it's okay. Everyone has times when they can't make it...", "If you couldn't make it, I wish you'd just said so... Otherwise, it's just too cruel.")
            elif "Yandere" in char_traits:
                lines = ("I waited so long for you... ", "...You never came. I waited so long and you never came!")
            else:
                lines = ("That's no good. You have to keep your promises...", "Jeez, how come you never came!")
            iam.say_line(character, lines, "sad")

        @staticmethod
        def offer_seen_mast(character):
            """
            Output line when the character wants the hero to join his/her masturbation
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("If you got excited watching me, we could... Want to?", "I just can't do it alone... Can I count on you for support?")
            elif "Shy" in char_traits and dice(50):
                lines = ("...T-these perverted feelings... You can make them go away, can't you...?", "I- I'm sorry, I just couldn't hold it in any more... So, please, can we...")
            elif "Imouto" in char_traits:
                lines = ("I can't ask for it any more obviously than this! Just fuck me already, pleaaaaaase!", "Hey, come on, won't you touch me? I can't satisfy myself alone...")
            elif "Dandere" in char_traits:
                lines = ("You caught me... Hey, please, can you take over from here?", "Watching me masturbate got you going, right? You wanna mess me up now, don't you?")
            elif "Tsundere" in char_traits:
                lines = ("Even I m...masturbate sometimes! ...S...so, what will you do?", "Y-you saw me masturbating... I demand s-sex as an apology!")
            elif "Kuudere" in char_traits:
                lines = ("Hey, if you were watching, you know what I wanna do, right..?", "Nn... This urge, I need you to satisfy it for me...")
            elif "Kamidere" in char_traits:
                lines = ("At this point I don't even care.　Fuck me.", "I've been seen indulging in such a foolish act...　There's nothing left for you to do but take responsibility.")
            elif "Bokukko" in char_traits:
                lines = ("Hey... I want you to help me feel even better... Please...♪", "Masturbating's too much work... Hey, you wanna do it for me?")
            elif "Ane" in char_traits:
                lines = ("I can't simply let you go after you saw me pleasuring myself.", "How convenient, you came in at just the right time... Hey, you know what I mean, right?")
            elif "Yandere" in char_traits:
                lines = ("I'm all warmed up and ready to go... Want to do it?", "I would so much rather you do it than have to do it myself... Won't you?")
            else:
                lines = ("Uuu, it's not enough by myself... Help me out here ♪", "Oh, it's you, [mc_ref]... What to join?")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def seen_mast(character):
            """
            Output line when the character is caught by the hero while masturbating
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("What is it? I want to get back to what I was doing...", "It looks like I've been caught touching myself.")
            elif "Shy" in char_traits:
                lines = ("Hyah!? I-I'm sorry! I'll wipe it off right away...!", "I-I... what an embarrassing thing to do...")
            elif "Imouto" in char_traits:
                lines = ("Ehehe, I'm all sticky...♪", "I-It's nothing, I was just a little itchy...")
            elif "Dandere" in char_traits:
                lines = ("Aw, I was almost there...", "...Even you have times when you need to...do it yourself, right?")
            elif "Tsundere" in char_traits:
                lines = ("Kuh... Sometimes I masturbate too, you know. What's wrong with that...?!", "...I wasn't really doing anything, you know? Yeah.")
            elif "Kuudere" in char_traits:
                lines = ("Hya!? I-I wasn't... Ah, no, well...You're not wrong, but...", "Even I have times when I wish to console myself.")
            elif "Kamidere" in char_traits:
                lines = ("God, can't you see I'm playing with myself here? What is it?", "...I've shown you something foolish. Please forget about it.")
            elif "Bokukko" in char_traits:
                lines = ("Geez, I was in the zone! Quit bothering me!", "What do you want? And it was just getting good too, jeez...")
            elif "Ane" in char_traits:
                lines = ("Hehe, you caught me...", "Um, that's embarrassing... Please don't look at me so much.")
            elif "Yandere" in char_traits:
                lines = ("Hehehe, I just got a bit horny...", "Hey, can't you take a hint...? I'm kinda busy here...")
            else:
                lines = ("Hyaa!?　Eh, ah, um, I just, well... Ahaha...", "Hyaaah!? I, I don't do anything..!")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def refuse_sex_frigid(character):
            """
            Output line when a frigid character refuses an intercourse with the hero
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I don't feel the need to do it right now.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("S-sorry, let's do it later m-maybe..?", )
            elif "Imouto" in char_traits:
                lines = ("Stop it, that's annoying and boring!", "Uuuh, aren't you bored, doing it again and again?")
            elif "Dandere" in char_traits:
                lines = ("I don't want to.", )
            elif "Tsundere" in char_traits:
                lines = ("Geez, give me a break, ok?", )
            elif "Kuudere" in char_traits:
                lines = ("I think I need a break today.", )
            elif "Kamidere" in char_traits:
                lines = ("Unfortunately, I have no intentions to do it.", )
            elif "Bokukko" in char_traits:
                lines = ("Nah, don't wanna. Don't you want to do something else?", )
            elif "Ane" in char_traits:
                lines = ("Apologies, I'm not in the mood today.", )
            elif "Yandere" in char_traits:
                lines = ("I don't feel like it.", )
            else:
                lines = ("I'm not in the mood, sorry.", )
            iam.say_line(character, lines, overlay_args=("sweat", "reset"))

        @staticmethod
        def alone_together(character):
            """
            Output line when the character and the MC are alone together
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("No one's around, huh... What shall we do?", "Hmm? Nobody here but us...")
            elif "Shy" in char_traits and dice(50):
                lines = ("Ah, it seems, um... Just us, huh...", "I-I get sort of nervous when we're alone...")
            elif "Imouto" in char_traits:
                lines = ("Ehehe... Come on now, there's nobody here but us.", "Hey, hey... We're all alone, aren't we?")
            elif "Dandere" in char_traits:
                lines = ("We're all by our lonesome, huh...?", "Hm? There's nobody here...")
            elif "Tsundere" in char_traits:
                lines = ("Wh-when did it become...just the two of us...?", "We're alone, now's my chance... Is what you're thinking, isn't it?")
            elif "Kuudere" in char_traits:
                lines = ("Hm? ...Oh, looks we're all alone.", "So we're the only ones here...")
            elif "Kamidere" in char_traits:
                lines = ("You know, it's just the two of us, hmm...?", "Just you and me now, huh...")
            elif "Bokukko" in char_traits:
                lines = ("Ehehe ♪ It's just the two of us! What'll you do? What do you wanna do??", "Ooh, lookie here, no one's around...")
            elif "Ane" in char_traits:
                lines = ("Oh my, it's just the two of us, isn't it.", "Oh my, we're completely alone, aren't we.")
            elif "Yandere" in char_traits:
                lines = ("It's kind of embarrassing, isn't it? Just the two of us.", "We're alone, aren't we? ...Hmhm ♪")
            else:
                lines = ("There's nobody around... Hehe ♪", "I-Is it alright? We're here...alone together...")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def offer_study_together(character):
            """
            Output line when the character proposes the MC to study together
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Want to study at my house?", "If it's you, I'm sure we'll be able to work together. Let's study at my house.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... Want to study at my place...?", "Um, if you're free, would you like to come to my place? Just thought we could study together...")
            elif "Imouto" in char_traits:
                lines = ("How about it? If you're free, want to come over and study?", "Hey, you free? You're free, right? You wanna study at my place? Right?")
            elif "Dandere" in char_traits:
                lines = ("Come study at my place?", "How about studying in my house?")
            elif "Tsundere" in char_traits:
                lines = ("You're free, aren't you? Wanna study at my place?", "Come to my house. You can help my with studies, right?")
            elif "Kuudere" in char_traits:
                lines = ("We're studying at my house. Sound good?", "Hey, wanna come over for studies?")
            elif "Kamidere" in char_traits:
                lines = ("Come to my house. Let's study together.", "Excuse me, would you like to come over to my house and study?")
            elif "Bokukko" in char_traits:
                lines = ("I was thinking about studying at my place, what do you think?", "Want to drop by my house to study?")
            elif "Ane" in char_traits:
                lines = ("Let's go study at my house! I'll make us some tea.", "It would be lovely to have you over to study. What do you say?")
            elif "Yandere" in char_traits:
                lines = ("How about it? Would you like to study at my place?", "If you're free, wanna come over to my place for a study session?")
            else:
                lines = ("I was just about to go home. Mind tutoring me for a bit?", "If you're free, want to come to my house to study?")
            iam.say_line(character, lines, "confident")

        @staticmethod
        def offer_study_sex(character):
            """
            Output line when the character proposes the MC to 'study' together
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Come to my room. To study.", )
            elif "Shy" in char_traits and dice(50):
                lines = ("Right now, there's no one home... So we could study, or do other stuff...", "Would you like to...come to my place? ...T-There's nobody... home right now...")
            elif "Imouto" in char_traits:
                lines = ("H-hey... Want to come over and study? Just so you know, don't do anything perverted, okay?　I'm serious!", "Should we study at my place? Oh, but there's no one else at home, you see...")
            elif "Dandere" in char_traits:
                lines = ("...Come to my house. ...To study, of course.", "Come study and do various other things at my place?")
            elif "Tsundere" in char_traits:
                lines = ("Want to come over? ...T-to study, obviously.", "Come up to my room. ...For studying, of course! Studying!")
            elif "Kuudere" in char_traits:
                lines = ("Come to my house. You're not allowed to complain.", "Um, so... do you wanna come over and, um...study?")
            elif "Kamidere" in char_traits:
                lines = ("I want you to come to my room. To study or something.", "Um, come study at my house... There's some things I want you to look over...")
            elif "Bokukko" in char_traits:
                lines = ("Hey, wanna come over to my place and hang?", "Want to come over? ...T-to study, of course!")
            elif "Ane" in char_traits:
                lines = ("Hey, if we go to my house we can study lots of different things ♪", "Let's go study at my house! ...Oh, it'll be just innocent studying, you know?", "Might I interest you in coming to my room? We could pool our knowledge together.")
            elif "Yandere" in char_traits:
                lines = ("There's nobody home right now, so... Want to come over and...study?", "Hey... Wanna come to my place to study? What d'you say?")
            else:
                lines = ("Are you free? If you are, then... How about you come over?", "Hey, wanna do something at my house? You know, like, studying or something?")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def before_study_sex(character):
            """
            Output line when the character and the MC are studying, but they got bored
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Doesn't look like you can concentrate well... That's because...of this, isn't it?", "You looked like you wanted it. I just thought I'd make it easier on you.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Um... I'm sorry. I just wanted to know more about you.", "S-sorry, I couldn't control myself... P-please don't hate me...")
            elif "Imouto" in char_traits:
                lines = ("Hey, I bored... Maybe we should do something else, like, you know...", "Okay, okay! I think we should study some naughty stuff too! Don't you agree?")
            elif "Dandere" in char_traits:
                lines = ("Studying is important, but... So is studying this here.", "Let's study physical education today.")
            elif "Tsundere" in char_traits:
                lines = ("What's wrong? You are not against it, right...?", "W-we can study any time we want, right? So...")
            elif "Kuudere" in char_traits:
                lines = ("You tempted me. You're not allowed to say no.", "This is also an important subject. Physical education.")
            elif "Kamidere" in char_traits:
                lines = ("My my... You knew things were going to end up like this, right?", "I studied really hard, right?　So I'd like to be rewarded...")
            elif "Bokukko" in char_traits:
                lines = ("Well then, after a bit of light study... Shall we do it?", "Alright, so... There's, you know... other things we can do, right...?")
            elif "Ane" in char_traits:
                lines = ("Ahh... It's so hot in here... What should we do about it... *glance*", "Hmhm, I've thought of something else we might try... Would you care to take a guess?")
            elif "Yandere" in char_traits:
                lines = ("Hehe, studying is great and all, but... Can't I interest you in a little of this right here...?", "Hey, what do you this about studying 'this'? You don't mind, don't you?")
            else:
                lines = ("It'll be alright. As long as we aren't too loud, no one will find out. Right?", "Well then, let's get right to studying 'this' ♪")
            iam.say_line(character, lines, "suggestive")

        @staticmethod
        def offer_visit(character):
            """
            Output line when the character invites the MC to his/her room
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("I want you to come to my room. I want... to be alone with you.", "I've made space at my house, where we can be alone.")
            elif "Shy" in char_traits and dice(50):
                lines = ("Er, um, so... There's no one at my house today... so... I was thinking we could be alone, maybe...", "H-hey! ...Th-there's no one home... at my place... S-so, maybe we could...")
            elif "Imouto" in char_traits:
                lines = ("Hey, hey, want to come to my house? Muhuhu, actually today there's no one home.", "So, you know, there's no one at my house right now... So... okay?")
            elif "Dandere" in char_traits:
                lines = ("I want you to come to my house... Don't mind the reason, just answer the invitation.", "Come to my bedroom. You don't have to worry... no one's there.")
            elif "Tsundere" in char_traits:
                lines = ("Coincidentally, there's no one else at my home today... No one at all...", )
            elif "Kuudere" in char_traits:
                lines = ("There's nobody at my house right now... How about it?", "No one else is at home today... Will you come over?")
            elif "Kamidere" in char_traits:
                lines = ("You know, today, there's no one at my house... Okay...?", "Since there's no one at my house... How about going there?")
            elif "Bokukko" in char_traits:
                lines = ("H-hey... you should come to my house... You know what I mean, right...?", "Right now there's nobody at my place... Say, you'll come, right?")
            elif "Ane" in char_traits:
                lines = ("If you visit my house, I'll give you a wonderful memory ♪", )
            elif "Yandere" in char_traits:
                lines = ("Want to go to my house? Fufu, when we get there, we can have some fun.", )
            else:
                lines = ("Um, er... There's no one home at my place right now... Wanna come over?", "You know... right now... There's nobody at my house...")
            iam.say_line(character, lines, "shy")

        @staticmethod
        def offer_sparring(character):
            """
            Output line when the character invites the MC to a sparring
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("Do you want to exercise with me?", "Show me how well you move.", "Please help me practice some.", "Join me for practice.")
            elif "Shy" in char_traits and dice(50):
                lines = ("I thought I would exercise a bit... Um... What do you say we go together...?", "I was t-thinking of doing a bit of exercise... D-do you wanna come along?", "Um, I'd like to practice with you... is that okay...?")
            elif "Imouto" in char_traits:
                lines = ("Hey, It's training time! Together, of course!", "Hey hey, come work out with me for a bit!", "Hey, help me practice a little!")
            elif "Dandere" in char_traits:
                lines = ("Excuse me, I want to build up my strength... Would you like to join me?", "I wish to train my body. Join me?", "Wanna practice with me?")
            elif "Tsundere" in char_traits:
                lines = ("I was thinking about doing some training, how about it?", "Come on, you need to work out. I'll even help you.")
            elif "Kuudere" in char_traits:
                lines = ("I was thinking about training, but I can't do it alone, so...", "Come on, keep me company in my practice, ok?", "Sorry to ask, but I need help with my training.")
            elif "Kamidere" in char_traits:
                lines = ("We can at least exercise together, don't you think?", "Would you care to build up some endurance with me?", "Sorry to ask, but could you join me for warming up?")
            elif "Bokukko" in char_traits:
                lines = ("Yo. Keep me company for practice, it's a pain by myself.", "C'mon, let's exercise together!", "Umm, could you come practice with me?", "Hey, there's an exercise I'd like to have a little help with but...")
            elif "Ane" in char_traits:
                lines = ("I need to lose some weight... Want to join me for some exercise?", "Would you care to join me in training our bodies?", "Hey, do you mind helping me practice a bit?", "I'd like you to help me train for a bit, if that's okay?")
            elif "Yandere" in char_traits:
                lines = ("Hey, how about training for a bit?", "You should get a little exercise... Want to do it together?", "Hey, can you come with me to practice for a while?")
            else:
                lines = ("How about it? Want to go for some light exercise?", "Um, would you like to go exercise?", "Come on, let's practice together?")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def offer_beach(character):
            """
            Output line when the character invites the MC to the beach
            """
            char_traits = character.traits
            if "Impersonal" in char_traits:
                lines = ("The water is pretty warm here. Interesting.", "I like this swimsuit, it doesn't restrict my movements.")
            elif "Shy" in char_traits:
                lines = ("Swimsuits are s-so embarrassing... P-please don't look at me too much...", "I was t-thinking of swimming a bit... D-do you want to join?")
            elif "Imouto" in char_traits:
                lines = ("Yay! The water is great, let's go swim!", "Hey, you like my swimsuit, don't you? I think it's pretty cool!")
            elif "Dandere" in char_traits:
                lines = ("The weather is nice. Perfect for swimming.", "Do you like this swimsuit? Me? I think it's ok.")
            elif "Tsundere" in char_traits:
                lines = ("Hey, w-where are you looking it?! Don't stare at my swimsuit!", "Come on, at least swim a bit. I'll even keep you company.")
            elif "Kuudere" in char_traits:
                lines = ("It's pretty hot here. Let's try out the water.", "Hmm, maybe this swimsuit is too revealing after all... Hm? You like it? I s-see...")
            elif "Kamidere" in char_traits:
                lines = ("Ahh, the water looks nice. I'm going to swim.", "What do you think? Does my swimsuit suit me? Of course it does.")
            elif "Bokukko" in char_traits:
                lines = ("C'mon, it's swimming time! Don't lag behind! ♪", "Hmm, this swimsuit is kinda tight... Maybe I should try swimming without it, what do you think? ♪")
            elif "Ane" in char_traits:
                lines = ("My, the weather is pretty nice today. Perfect for swimming.", "What do you think about my swimsuit? It's not too revealing, is it?")
            elif "Yandere" in char_traits:
                lines = ("What is it? You like my swimsuit? I'm glad ♪", "Would you like to swim with me? It will be more fun if we do it together.")
            else:
                lines = ("How about it? Do you like my swimsuit? It wasn't easy to pick a good one, you know.", "Come on, let's swim together! I bet the water feels nice! ♪")
            iam.say_line(character, lines, "happy")

        @staticmethod
        def after_rest(character):
            """
            Output line when the character recovers from an injury
            """
            char_traits = character.traits
            mood = "happy"
            if "Impersonal" in char_traits:
                lines = ("I apologize for having made you worry about this incident.", )
            elif "Shy" in char_traits:
                lines = ("Um, what happened to me... Oh, I see...", )
            elif "Imouto" in char_traits:
                mood = "sad"
                lines = ("I-I was really scared, you know?! Uuh, I was so scaredď˝ž", )
            elif "Dandere" in char_traits:
                lines = ("I'm sorry for making you worry... I'm okay now.", )
            elif "Tsundere" in char_traits:
                lines = ("What is it? Is it that strange I'm still alive?", )
            elif "Kuudere" in char_traits:
                lines = ("I never thought it'd have to come to that...", )
            elif "Kamidere" in char_traits:
                lines = ("Sorry for worrying you. Don't worry, I'm okay now.", )
            elif "Bokukko" in char_traits:
                lines = ("Mmm, I'm not really sure what happened, but I'm okay now!", )
            elif "Ane" in char_traits:
                lines = ("If you never want to go through something like that, be careful.", )
            elif "Yandere" in char_traits:
                lines = ("I'm alright. Seems like I worried you.", "Fufu, I've had a rather thrilling experience...", )
            else:
                lines = ("Yeah... I'm okay now. Sorry to make you worried.", )
            iam.say_line(character, lines, mood)

#label interactions_yandere_attack:
#    $ char.override_portrait("portrait", "indifferent")
#    $ rc("Ufufu... If I had done this from the very start, I would have avoided all of those painful memories...", "Let's love each other again in the afterlife...", "Huhuhuh... You didn't think you could betray me and get off scott free, did you...? Come on... say something for yourself... come ooon...!", "Huhuhuh... I wonder how warm it would be to bathe in your blood...?", "If you won't belong to me... Then you won't... belong to anyone...", "Everything is your fault. Yours... YOUUUUUURS! ! !", "Pft... kuku... Ahaha... Ahahaha... HAH HAH HAH HAH HAH!!", "Hahah... I just figured out how we can be together forever...", "Hey... If you're reborn... Be sure to find me again... okay...", "Ah, hahahahahahahaha... diediediediediediediediediediedie DIE!!", "You're not good enough to live in this world. So I'll erase you. Bye-bye.")
#    $ char.restore_portrait()
#    return

######
    #if gm_last_success:
    #    if ct("Yandere"):
    #        $ rc("Nfufu, boo-biesâ™Ş boo-biesâ™Ş -bies â™Ş", "Interested, aren't you? <smiles mischievously>")
    #    elif ct("Shy") and dice(30):
    #        $ rc("U-Um... Please don't stare at me so much...", "Even though this is embarrassing... I'm glad...", "Don't look at me like that... I-I'm not embarrassed!")
    #    elif ct("Kamidere"):
    #        $ rc("Do you seriously think so?", "Thanks, but next time keep talk like that for private, ok? ", "So you are that type of person...", "Thanks, I grew them myself.", "Thanks. {p=.5}Hey, enough. How long will you stare for?!")
    #    elif ct("Ane"):
    #        $ rc("My, don't stare so hard, okay...?", "If you're gonna look, pay me the viewer's fee!â™Ş", "Thanks, but please don't stare like that, it's embarrassing.", "Do you like my breasts? Glad to hear it...")
    #    elif ct("Imouto"):
    #        $ rc("Huhu â™Ş Lookie, these are my awesome boobs â™Ş", "Geez, don't loooook â™Ş")
    #    elif ct("Kuudere"):
    #        $ rc("G-go ahead, if you're going to look then look!", "D-don't look... You can't!")
    #    elif ct("Tsundere"):
    #        $ rc("Wh-who said you could look?", "Uuu... Stop staring at me like that...")
    #    elif ct("Dandere"):
    #        $ rc("Hmmm... Interested?", "You like my body? ...good.")
    #    elif ct("Bokukko"):
    #        $ rc("Hah hah hah! Go ahead, envy my boobs! Worship them!", "Hmm, already captivated by my exquisite breasts, huh!")
    #    else:
    #        $ rc("Itâ€™s alright to look, but touching is not allowed, oo... fufufu.", "[hero.name], just where are you looking at? Itâ€™s alright, look at much as you like.", "Like the view? <pushes her chest up in a pose>", "Do you like my breasts? Glad to hear it...", "You're so perverted. <giggles>", "My body gets you excited, doesn't it?", "Thanks... Hey! Is that why you are interested in me?", "You think so? I'm glad...", "Really? I'm glad to hear that.")
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

# USED TO BE FRIENDSHIP LINES, MAY BE USEFUL IN THE FUTURE
        # if ct("Impersonal"):
            # $ rc("Very well.", "Alright.")
        # elif ct("Shy") and dice(50):
            # $ rc("Umm... That is... I-I'm in your care...!", "I think of you as a precious friend too.")
        # elif ct("Kuudere"):
            # $ rc("I can't think of any reason to refuse. Sure, why not.", "...It looks like we're a good match.")
        # elif ct("Dandere"):
            # $ rc("I agree.", "I understand...", "Please...take good care of me.")
        # elif ct("Tsundere"):
            # $ rc("I suppose I have no choice.", "Fine ...I-it's not like this makes me happy!")
        # elif ct("Imouto"):
            # $ rc("R-Really...? Fuaah, I'm so glad!", "We'll be friends forever, right?", "Hehehe â™Ş We somehow became good friends, huh?")
        # elif ct("Bokukko"):
            # $ rc("Hmm, okay, sounds good!", "I s'pose I could.", "Feels nice having someone support me for a change.")
        # elif ct("Ane"):
            # $ rc("Yes, that would be acceptable.", "It looks like you and I could be good partners.")
        # elif ct("Kamidere"):
            # $ rc("Yes, with pleasure. Treat me well, okay? â™Ş", "Please continue to be good friends with me.")
        # elif ct("Yandere"):
            # $ rc("I have the feeling I could get along with you.",  "Well, we get along fine... Alright.")
        # else:
           # $ rc("Mm, alright.", "Okay!", "Hehehe, it's great to be friends â™Ş", "Of course. Let's get along â™Ş")
    # else:
        # $ char.override_portrait("portrait", "indifferent")
        # if ct("Impersonal"):
            # $ rc("Not interested.", "I cannot understand. Please give me a detailed explanation.")
        # elif ct("Shy") and dice(50):
            # $ rc("I-I'm really sorry...", "Another time, maybe...")
        # elif ct("Tsundere"):
            # $ rc("Huh? Why should I agree to that?", "Uh? Wha...what are you talking about?")
        # elif ct("Kuudere"):
            # $ rc("There's all sorts of problems with that.", "A bother. Don't want to.")
        # elif ct("Dandere"):
            # $ rc("Smells suspicious. I will refrain.", "If I feel like it.")
        # elif ct("Imouto"):
            # $ rc("Umm, uh... Sorry. Hehe â™Ş", "Sure... Pfft... Just kidding, I lied!")
        # elif ct("Yandere"):
           # $ rc("I don't see any prerequisites to this.", "I don't trust you.")
        # elif ct("Ane"):
            # $ rc("Could you perhaps not get me involved in this? It is quite the bother.", "Sorry. Maybe some other time.")
        # elif ct("Kamidere"):
            # $ rc("I don't think I should...", "No way! You're looking at me all lewd!")
        # elif ct("Bokukko"):
            # $ rc("Ah... This's kind of a huge pain...", "Mm, sounds kinda boring, y'know?")
        # else:
            # $ rc("I don't feel like it.", "Something about this seems kinda suspicious... I think I'll pass.")
