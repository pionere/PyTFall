# general chat
label interactions_smalltalk:
    "You have a small chat with [char.nickname]."
    $ interactions_check_for_bad_stuff(char)
    $ interactions_check_for_minor_bad_stuff(char)
    $ m = 1 + interactions_flag_count_checker(char, "flag_interactions_general")
    $ n = 2 + interactions_set_repeating_lines_limit(char)
    if m > n:
        $ del m, n
        call interactions_too_many_lines from _call_interactions_too_many_lines_1
        $ char.gfx_mod_stat("disposition", -randint(3,6))
        $ char.gfx_mod_stat("affection", -randint(0,3))
        if char.get_stat("joy") > 80:
            $ char.gfx_mod_stat("joy", -1)
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -1)
        jump girl_interactions
    if char.get_stat("disposition") >= 100:
        if ct("Impersonal", "Dandere", "Shy"):
            $ narrator(choice(["[char.pC] didn't talked much, but [char.pC] enjoyed your company nevertheless.",
                               "You had to do most of the talking, but [char.p] listened you with a smile.",
                               "[char.pC] welcomed the chance to spend some time with you.",
                               "[char.pC] is visibly at ease when talking to you, even though [char.p] didn't talked much."]))
        else:
            $ narrator(choice(["It was quite a friendly chat.",
                               "You gossiped like close friends.",
                               "[char.pC] welcomed the chance to spend some time with you.",
                               "[char.pC] is visibly at ease when talking to you.",
                               "You both have enjoyed the conversation."]))

        if 2*m <= n and dice(50) and dice(char.get_stat("joy")) and dice(hero.get_stat("joy")):
            $ narrator(choice(["You feel especially close.", "[char.pC] was much more approachable."]))
            $ hero.gfx_mod_stat("joy", randint(0, 1))
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ char.gfx_mod_stat("disposition", randint(1, 2))
            $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
            $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.25))
            $ char.gfx_mod_stat("affection", affection_reward(char, .1))
    elif char.get_stat("disposition") >= -100:
        if ct("Impersonal", "Dandere", "Shy"):
            $ narrator(choice(["But there was a lot of awkward silence.", "But you had to do most of the talking.", "There is no sign of [char.op] opening up to you yet.", "But it was kind of one-sided."]))
        else:
            $ narrator(choice(["It's all a little bit stiff.", "There's some reservation though...", "It's hard to find common ground.", "But it was somewhat forced."]))
        if 2*m <= n and dice(50):
            $ narrator(choice(["At least [char.p] was more attentive.", "[char.pC] did not cut you short, though..."]))
    else:
        $ narrator(choice(["It looks like there's a good amount of mistrust between you.", "But it was difficult for both of you.", "Sadly, [char.p] was not very interested in chatting with you.", "It was clearly uncomfortable for [char.op] to speak to you.", "[char.pC] was suspicious of you the entire time and never let [char.op] guard down."]))
    if m <= -250:
        $ m = randint(1, 3)
    elif m <= 0:
        $ m = randint(2, 5)
    elif m <= 200:
        $ m = randint(1, 4)
    elif dice(30):
        $ m = randint(1, 2)
    elif dice(50):
        $ m = 1
    else:
        $ char.gfx_mod_stat("joy", 1)
        $ m = 0
    $ char.gfx_mod_stat("disposition", m)
    $ char.gfx_mod_stat("affection", affection_reward(char, .5))
    $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
    $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.25))
    $ del m, n
    jump girl_interactions

# ask about job
label girl_interactions_aboutjob: # TO DO: here would help additional logic based on actual recent jobs events
    $ interactions_check_for_bad_stuff(char)
    $ m = interactions_flag_count_checker(char, "flag_interactions_aboutjob")
    if m >= 1:
        $ del m
        call interactions_too_many_lines from _call_interactions_too_many_lines_2
        $ char.gfx_mod_stat("disposition", -randint(4,6))
        $ char.gfx_mod_stat("affection", -randint(1,2))
        jump girl_interactions
    $ del m

    if char.flag("daysemployed") < 5:
        # Less than 10 days in service:
        $ char.override_portrait("portrait", "indifferent")
        if char.status != "slave":
            $ rc("I'm still adjusting to the new position.", "I'm trying to find my bearings with this new career.")
        else:
            $ rc("I want to serve you better, [char.mc_ref].", "A new master takes a while to get used to...")
        $ char.gfx_mod_stat("disposition", 1)
        $ char.gfx_mod_stat("affection", affection_reward(char, .5))
        $ char.gfx_mod_stat("joy", 1)
        $ char.restore_portrait()
    elif char.get_stat("disposition") <= -350:
        $ char.override_portrait("portrait", "sad")
        if char.status != "slave":
            if ct("Impersonal", "Dandere", "Kuudere"):
                $ rc("... *[char.pC] doesn't want to talk*", "I don't think I'll linger here for a long time.", "I do not wish to about it. Leave me alone.")
            elif ct("Shy"):
                $ rc("Um... I-I don't think this job is for me...", "I... I'm looking for another job... Sorry.")
            else:
                $ rc("You're a terrible employer; I have no idea why I'm still working here...", "Maybe I should try to beg in the streets instead of this 'job'...")
        else:
            if ct("Impersonal", "Dandere", "Kuudere", "Shy"):
                $ rc("...I don't want to live.", "My life is awful. I want to end this...", "... <She looks extremely depressed>")
            else:
                $ rc("I wish that I the resolve to kill myself...", "My life in your service is awful.", "Just sell me off to someone. To anyone!")
        $ char.gfx_mod_stat("disposition", randint(0, 1))
        $ char.gfx_mod_stat("affection", affection_reward(char, .25))
        $ char.restore_portrait()
    elif char.get_stat("disposition") <= -50:
        $ char.override_portrait("portrait", "indifferent")
        if char.status != "slave":
            if char.get_stat("joy") >= 50:
                if ct("Impersonal", "Dandere", "Kuudere"):
                    $ rc("I don't like my job.", "You are a bad employer.")
                elif ct("Shy"):
                    $ rc("I-I'm fine. J-just wish I had a better job... No, nevermind.", "I'm fine, I think... I-I mean it's not such a bad job, there are much worse ones!")
                else:
                    $ rc("I'm fine, but I just wish you weren't such a terrible employer.", "As good as can be expected under the circumstances, 'boss'...")
            else:
                if ct("Impersonal", "Dandere", "Kuudere"):
                    $ rc("I hate my job.", "I'm not in the mood. Why? Because of my job, obviously.")
                elif ct("Shy"):
                    $ rc("I wish I had a better job... S-sorry.", "I-I don't particularly like my job. M-maybe I should try something else...")
                else:
                    $ rc("I'm sad and you are the worst... what else do you want me to say?", "I'm looking for new employment opportunities; that's how I'm feeling...")
        else:
            if char.get_stat("joy") >= 50:
                if ct("Impersonal", "Dandere", "Kuudere"):
                    $ rc("I suppose a slave like me doesn't have much of a choice.", "I follow your orders. That's all.")
                elif ct("Shy"):
                    $ rc("Um, I do my best. Even though my master is... Nevermind, sorry.", "[char.mc_ref], please be nice to me... I'll work harder, I promise.")
                else:
                    $ rc("I am 'ok'. Just wish I had a better owner...", "I guess it is better than the slave market. A bit.")
            else:
                if ct("Impersonal", "Dandere", "Kuudere"):
                    $ rc("...I want another owner.", "I wish I had a better life as a slave.")
                elif ct("Shy"):
                    $ rc("...Yes, [char.mc_ref]. I'm fine. <you notice tears in [char.pp] eyes>")
                else:
                    $ rc("There isn't much to say... I'm sad and you're mean...", "I feel like it would be better if you sold me off at the next auction.")
        $ char.gfx_mod_stat("disposition", randint(1, 2))
        $ char.gfx_mod_stat("affection", affection_reward(char))
        $ char.gfx_mod_stat("joy", randint(0, 1))
        $ char.restore_portrait()
    else:
        $ char.override_portrait("portrait", "happy")
        if char.status != "slave":
            if char.get_stat("joy") >= 50:
                if ct("Impersonal", "Dandere", "Kuudere"):
                    $ rc("I like my job. Nothing more to say.", "No complaints.")
                elif ct("Shy"):
                    $ rc("I-I like my job. T-thank you.", "I-I'm perfectly fine! <shyly smiling>")
                else:
                    $ rc("I'm happy and this job is not so bad.", "I'm comfortable and content with this arrangement.")
            else:
                if ct("Impersonal", "Dandere", "Kuudere"):
                    $ rc("I like my job. I think.", "Not bad. It's not perfect, but...")
                elif ct("Shy"):
                    $ rc("I'm just a bit sad today, b-but my job is nice.", "Um, I'm ok, I think. You can't be happy all the time, r-right?")
                else:
                    $ rc("Not very chipper but I hope things become better soon.", "Bit sad, if truth be told. Don't want to complain though.")
        else:
            if char.get_stat("joy") >= 50:
                if ct("Impersonal", "Dandere", "Kuudere"):
                    $ rc("I'm satisfied with everything, [char.mc_ref].", "I am at your service, [char.mc_ref]. My life is my job.")
                elif ct("Shy"):
                     $ rc("E-everything is well, [char.mc_ref]! <shyly smiling>", "It's fine. Thanks for asking, [char.mc_ref]. <blushes>")
                else:
                      $ rc("I'm very well, thank you [char.mc_ref]!", "I am satisfied with my life and job as a slave.")
            else:
                if ct("Impersonal", "Dandere", "Kuudere"):
                    $ rc("Nothing to worry about, [char.mc_ref].", "Good enough.")
                elif ct("Shy"):
                    $ rc("Y-yes, [char.mc_ref]. I can do it, I know I can!", "It's normal, I suppose...")
                else:
                    $ rc("I'm a bit sad, but you are kind so I'm looking for a brighter tomorrow!", "You've been very nice to me in general, so I won't complain!")
        $ char.gfx_mod_stat("disposition", randint(1, 3))
        $ char.gfx_mod_stat("affection", affection_reward(char))
        $ char.gfx_mod_stat("joy", randint(0, 1))
        $ char.restore_portrait()

    $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
    $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.25))

    jump girl_interactions

# ask how she feels
label interactions_howshefeels:
    $ m = interactions_flag_count_checker(char, "flag_interactions_howshefeels")
    if m >= 5: # we don't have to limit it because of bonuses (there are none), but because of the common sense
        $ del m
        call interactions_too_many_lines from _call_interactions_too_many_lines_3
        $ char.gfx_mod_stat("disposition", -randint(4,6))
        $ char.gfx_mod_stat("affection", -randint(1,2))
        jump girl_interactions
    $ del m
    if 'Food Poisoning' in char.effects: # at least no penalty to disposition, unlike other cases with food poisoning
        $ char.override_portrait("portrait", "sad")
        $ rc("I ate something wrong. Ow-ow-ow...", "Ouh. I think I need to use bathroom again...")
        $ char.restore_portrait()
        jump girl_interactions_end
    elif 'Down with Cold' in char.effects or char.get_stat("vitality") < round(char.get_max("vitality")*.3) or (char.get_stat("health") < char.get_max("health")/5) or char.get_stat("joy") < 25: # we select one suitable image in the very beginning
        $ char.override_portrait("portrait", "sad")
    elif char.get_stat("joy") > 70:
        if ct("Shy"):
            $ char.override_portrait("portrait", "shy")
        else:
            $ char.override_portrait("portrait", "happy")
    else:
        if ct("Shy"):
            $ char.override_portrait("portrait", "shy")
        else:
            $ char.override_portrait("portrait", "indifferent")

    if 'Down with Cold' in char.effects: #illness
        $ rc("I think I caught a cold...", "I'm not feeling well today. *sneezes*", "I have a fever... <She looks pale>")

    #body checks
    if char.get_stat("vitality") <= char.get_max("vitality")/10:
        $ rc("I want to sleep so badly... <yawns>", "I'm very tired lately... <yawns>")
    elif char.get_stat("vitality") < char.get_max("vitality")/3:
        $ rc("My body a bit tired.", "I could use some rest.", "I feel weakness, I really should rest more...")
    elif char.get_stat("vitality") >= char.get_max("vitality")*9/10:
        $ rc("I'm full of strength and energy.", "My body rested very well lately.")

    if char.get_stat("health") <= char.get_max("health")/3:
        $ rc("My whole body hurts. I think I need a doctor.", "My body is not feeling very well lately... I could use some medical attention.")
    elif char.get_stat("health") >= char.get_max("health")*9/10 and not('Food Poisoning' in char.effects) and not('Down with Cold' in char.effects):
        $ rc("My body is in top condition.", "My health is pretty good lately.")

    if cgo("Caster"):
        if char.get_stat("mp") <= char.get_max("mp")/5:
            $ rc("I feel drained.", "My mind is tired. Perhaps I should use magic less frequently.")
        elif char.get_stat("mp") >= char.get_max("mp")*9/10:
            $ rc("I feel like magic overflows me.", "I'm filled with magic energy.")

    if char.get_stat("joy") <= 30: #begin joy checks
        if ct("Impersonal", "Dandere"):
            $ rc("I'm not in the mood today.", "I'm just a bit sad. That's all.")
        elif ct("Shy"):
            $ rc("I'm kinda sad...", "I-I cried a bit some time ago. Why? Because I felt like it...")
        else:
            $ rc("I'm depressed. Don't wanna talk about it.", "I'm sad. Isn't it obvious to you?")
    elif char.get_stat("joy") >= 65:
        if ct("Impersonal", "Dandere", "Kuudere"):
            $ rc("I'm pretty happy. I think.", "I'm fine. <barely smiling>")
        elif ct("Shy"):
            $ rc("I think I'm... happy.", "<shyly smiling> I'm in a good mood today...")
        else:
            $ rc("I'm quite happy.", "You could say I enjoy my life.")
    else:
        if ct("Impersonal", "Dandere", "Kuudere"):
            $ rc("I'm perfectly calm.", "Don't concern yourself about me, I'm fine.")
        elif ct("Shy"):
            $ rc("Um, I suppose I'm ok.", "N-nothing to worry about, I'm f-fine.")
        else:
            $ rc("I'm ok, I guess.", "Everything is as usual.")

    $ char.restore_portrait()

    $ char.gfx_mod_stat("disposition", randint(2, 4))
    $ char.gfx_mod_stat("affection", affection_reward(char))

    $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
    $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.25))

    jump girl_interactions

# ask about her
label interactions_abouther:
    $ interactions_check_for_bad_stuff(char)
    $ interactions_check_for_minor_bad_stuff(char)
    $ m = 1 + interactions_flag_count_checker(char, "flag_interactions_abouther")
    $ n = 2 + interactions_set_repeating_lines_limit(char)
    if m > n:
        $ del m, n
        call interactions_too_many_lines from _call_interactions_too_many_lines_4
        $ char.gfx_mod_stat("disposition", -randint(1, 5))
        $ char.gfx_mod_stat("affection", -randint(0,2))
        if char.get_stat("joy") > 40:
            $ char.gfx_mod_stat("joy", -randint(0,2))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -1)
        jump girl_interactions

    if char.get_stat("disposition") <= 50:
        $ del m, n
        $ char.gfx_mod_stat("disposition", -randint(3, 10))
        $ char.gfx_mod_stat("affection", -randint(0,2))
        $ char.gfx_mod_stat("joy", -randint(0, 1))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status != "free":
            "You tried to know [char.nickname] better."
        jump interactions_refused

    $ gm_abouther_list = []
    if ct("Half-Sister"):
        if ct("Yandere"):
            $ gm_abouther_list.append(choice(["Now that I think about it, I spent more time with you than Mom and Dad.", "We used to play doctor and tear off each other's clothes, heh.", "We used to bathe together, so... you got to touch sister's body all over....", "Whenever we took a bath together, I used to wash your every nook and cranny. And I mean EVERY nook and cranny ♪"]))
        elif ct("Impersonal"):
            $ gm_abouther_list.append(choice(["Do you remember how you used to pull pranks on me?", "I have always observed you. I know all there is to your character.", "I've known what kinds of sexual fetishes you have since a long time ago."]))
        elif ct("Tsundere"):
            $ gm_abouther_list.append(choice(["We used to take a bath together back in the days, didn't we? Now...? B...but... hey! You know we shouldn't do that!", "You've always gone out of your way to protect your sister. I should thank you for that.", "I went overboard when I tried to discipline you back when we were little. To be honest, I'm sorry about that now.", "Remember that collection of dirty magazines you used to cherish? I was the one who threw them away. I am... still sorry about that."]))
        elif ct("Dandere"):
            $ gm_abouther_list.append(choice(["We've been together since we were small... Have you had enough of it? Well, I'm still not tired of it yet.", "You've taught me all kinds of things since a long time ago... even perverted things.", "You used to play doctor with me all the time... You were so perverted, even back then."]))
        elif ct("Kuudere"):
            $ gm_abouther_list.append(choice(["I used to be a crybaby? D-don't remind me of such things...", "M-my promise to marry you? T-there's no way I'd remember something like that!", "Getting engaged with my [hero.hs]... I only thought that was possible back when we're kids.", "You always protected me. Therefore, I decided that I had to become strong."]))
        elif ct("Ane"):
            $ gm_abouther_list.append(choice(["Hehe, you've grown so much... That makes your sis proud.", "You weren't able to fall asleep without sis by your side when we were little.", "Whenever I wore a skirt, you always tried to peek underneath it... You were already so perverted when we were little.", "I've taken care of you since you were little. Therefore, sister knows everything about you.", "When we were younger, I was always by your side because I swore I would always protect you."]))
        elif ct("Imouto"):
            $ gm_abouther_list.append(choice(["I used to think I'd get as tall as you.", "You remember we used to play shop when we were little? Wha... You should forget about THAT game!", "You have protected me from bullies when I was little.... That made me so happy."]))
        elif ct("Kamidere"):
            $ gm_abouther_list.append(choice(["I decided that you'd be mine when I was still very little.", "You've belonged to sis ever since you were born.", "You're my [hero.hs] who I've personally helped to raise. There's no way I'd let you go."]))
        elif ct("Bokukko"):
            $ gm_abouther_list.append(choice(["When we were little, didn't you say you'd make me your wife someday or something?", "When we were kids, we went exploring in the forest together and we both got lost.", "We used to climb fences and then jump off them. The two of us got injuries all over.", "You used to be so wee and now that huge, na?"]))
        else:
            $ gm_abouther_list.append(choice(["We used to bathe together a lot when we were little ♪", "The bath used to be our playground... but you tickled me way too much.", "When it was night time, you would always try to slip into my bed unnoticed.", "You used to tag along with me wherever I went when we were little."]))

    if ct("Big Boobs", "Abnormally Large Boobs") and dice(80):
        $ gm_abouther_list.append(choice(["I notice men, everyone of them, staring at nothing but my boobs.", "I've outgrown yet another bra... I wish something could be done about this...", "Hey, [char.mc_ref], do you know what my charms are? Ufu, shall I show you? I'm pretty sure I can make your heart skip a beat ♪", "All the men just keep staring at my breasts. Are such big ones really that fascinating?", "The reason you're interested in me is my big breasts, right?", "They say that big breasts are the best, but truth be told they're heavy and make the shoulders stiff, not good at all."]))

    if ct("Small Boobs") and dice(80):
        $ gm_abouther_list.append(choice(["I read lately that the hunt is on for small breasts. Who cares about big tits!", "It's better without large breasts. They'd only get in the way... Probably...", "Small breasts have their good points as well, don't you think? You do think so, right?"]))

    if ct("Lesbian"):
        $ gm_abouther_list.append(choice(["I am REALLY interested in female's body curves.", "I would like to go to an all girls' school. Imagine, only girls, everywhere... That would be great...", "I'd like to bring a cute girl home.", "Isn't it normal to be attracted to charming girls? I think it's totally proper ♪", "Something I like? Hmm... Maybe watching cute girls?", "Girls look really cute, don't they? I just want to eat one up.", "I like cute things. Like girls, for example.", "If I were a boy, I sure would explore every inch of the girl I was dating..."]))

    if ct("Bisexual"):
        $ gm_abouther_list.append(choice(["In love, gender makes no difference...", "I like boys and girls alike ♫"]))

    if ct("Fire"):
        $ gm_abouther_list.append(choice(["I'm pretty good with fire magic."]))
    if ct("Water"):
        $ gm_abouther_list.append(choice(["I'm pretty good with water magic."]))
    if ct("Air"):
        $ gm_abouther_list.append(choice(["I'm pretty good with air magic."]))
    if ct("Earth"):
        $ gm_abouther_list.append(choice(["I'm pretty good with earth magic."]))
    if ct("Darkness"):
        $ gm_abouther_list.append(choice(["I'm pretty good with dark magic."]))
    if ct("Light"):
        $ gm_abouther_list.append(choice(["I'm pretty good with light magic."]))
    if ct("Electricity"):
        $ gm_abouther_list.append(choice(["I'm pretty good with electricity magic."]))
    if ct("Ice"):
        $ gm_abouther_list.append(choice(["I'm pretty good with ice magic."]))
    if ct("Neutral"):
        $ gm_abouther_list.append(choice(["They say some people have no talent for magic. I'm one of them, it seems."]))

    if ct("Slim"):
        $ gm_abouther_list.append(choice(["I have a great figure, don't you think?", "No matter how much I eat, I never get fat. I'm so lucky with my body ♫"]))

    if ct("Chubby"):
        $ gm_abouther_list.append(choice(["I may be a bit chubby, but men like it.", "I thought about a diet, but I just can't resist fresh cupcakes ♫"]))

    if ct("Scars"):
        $ gm_abouther_list.append(choice(["I tried many doctors, but they all said that my scars cannot be healed. *sigh*"]))

    if ct("Energetic"):
        $ gm_abouther_list.append(choice(["I always was a good runner. I'm good at moving fast.", "I hate waiting, and I hate when people have to wait me."]))

    if ct("Optimist"):
        $ gm_abouther_list.append(choice(["They say I'm always cheerful. I just enjoy my life, that's all.", "Hey, do you know this one? <tells you an anecdote> A good one, eh?"]))

    if ct("Pessimist"):
        $ gm_abouther_list.append(choice(["It's not like I dislike jokes... I just don't find most of them funny enough.", "The world is cruel and unforgiving... You can't hide this truth behind jokes."]))

    if ct("Aggressive"):
        $ gm_abouther_list.append(choice(["They say I'm too hot-headed. But it's not my fault when they try to pick a fight with me!", "I smacked that rude shopkeeper the other day right in the face. Will teach him a lesson how to talk with customers."]))

    if ct("Courageous"):
        $ gm_abouther_list.append(choice(["Some my friends afraid of darkness, can you imagine that? Even as a child I was not afraid of it, or anything else.", "Don't move, you have a spider on your shoulder. <calmly removes it> Here."]))

    if ct("Coward"):
        $ gm_abouther_list.append(choice(["The other day I noticed a bug under my bed... <shudders>", "I dislike dark places. And night. Why? Because... because it's so dark that I cannot see a thing!"]))

    if ct("Nerd"):
        $ gm_abouther_list.append(choice(["As a child I liked to to read books more than to play with peers, so they teased me a lot. Nothing changed since then..."]))

    if ct("Strange Eyes"):
        $ gm_abouther_list.append(choice(["People often say that my eyes are unusual. What do you think of them?", "Do you like my eyes? As a child I was often teased because of them."]))

    if ct("Manly"):
        $ gm_abouther_list.append(choice(["Do you like my muscles? It took a while to build them.", "Everyone should build [char.op]self some muscles for self-protection, don't you think?"]))

    if ct("Lolita"):
        $ gm_abouther_list.append(choice(["My body is so small, everyone think I'm still a child.", "Maybe I should drink more milk to grow up... What do you think?"]))

    if ct("Alien"):
        $ gm_abouther_list.append(choice(["This place is so strange. I don't think I'll ever get used to it completely.", "Everything was very different where I used to live. But... I like it here too."]))

    if ct("Great Arse"):
        $ gm_abouther_list.append(choice(["I notice men often staring at my ass. What's wrong with them?", "The other day I dropped my purse and bent down to pick it up. All the men in the street started to applaud me. It was sooo embarrassing!"]))

    if ct("Not Human"):
        $ gm_abouther_list.append(choice(["Some humans don't like my appearance. But I don't care.", "The other day they refused to serve me in that fancy cafe because I'm not human enough. Can you imagine that?!"]))

    if cgo("Combatant"):
        if ct("Shy", "Coward"):
            $ gm_abouther_list.append(choice(["I have been trained in combat, but I really dislike violence.", "I know a lot about self-defense... but I really hope that I wouldn’t ever need to use it.", "I know how to use a weapon... but it still scares me a bit.", "I can do well in combat training, but in practice...", "They say that I may have the skill, but not the spirit of a warrior...", "I carry a weapon, but I don’t think I would have the heart to hurt someone."]))
        elif ct("Virtuous"):
            $ gm_abouther_list.append(choice(["I know how to pacify someone without hurting them. That’s the right way to do it.", "I learned how to fight so I can protect others."]))
        elif ct("Adventurous"):
            $ gm_abouther_list.append(choice(["I like to sharpen my battle skills.", "I enjoy exploring catacombs.", "A duel sounds interesting, do you mind?"]))
        else:
            $ gm_abouther_list.append(choice(["I have been trained in combat. So you better not be trying anything funny <grins>", "I may not look like it, but I can handle my weapons really well.", "Some creeps tried to ambush me once. I gave them plenty of time to repent at the infirmary.", "Sometimes I watch the matches in the arena to get inspiration to improve my own technique.", "It's better to know how to defend yourself in this town. You never know what may happen, especially if you are a woman."]))

    if ct("Homebody"):
        $ gm_abouther_list.append(choice(["I like my home a lot. I don't understand all those travellers and adventurers.", "I think living every day as an ordinary girl is the ultimate happiness.", "I enjoy reading in the bath. It's nice to do in such a confined space."]))

    if ct("Natural Follower"):
        $ gm_abouther_list.append(choice(["I'm not a leader, I never wanted to be one. Too much responsibility."]))

    if ct("Natural Leader"):
        $ gm_abouther_list.append(choice(["People say I'm quite charismatic. I bet I'd be a good leader, don't you thing? <smiles>"]))

    if ct("Well-mannered"):
        $ gm_abouther_list.append(choice(["They say nothing costs so little and is valued so much as courtesy. I always keep that in mind."]))

    if ct("Ill-mannered"):
        $ gm_abouther_list.append(choice(["People often tell me that I lack politeness. Fucking hypocrites! I just say what I really think, nothing more."]))

    if ct("Half-Sister"):
        $ gm_abouther_list.append(choice(["Do you miss our father? ...Yes, I miss him too.", "We should chat more often. We are family after all."]))

    if not(cgo("Combatant")) and ct("Adventurous"):
        $ gm_abouther_list.append(choice(["I always dreamed about my own adventures. But I never had a combat training, so... <sigh>"]))

    if cgo("Caster"):
        $ gm_abouther_list.append(choice(["I like to study magic.", "Arcane arts are passion of mine", "Magic is so fascinating, I can't live without it!"]))

    if cgo("Server"):
        $ gm_abouther_list.append(choice(["I'm just an ordinary worker, I guess.", "I work where I can. You can't be picky if you want to pay your bills."]))

    if cgo("SIW"):
        $ gm_abouther_list.append(choice(["I enjoy sex, thus I enjoy my job <grins>", "I think there is nothing wrong with selling your body as long as you having fun and it's well paid."]))

    if ct("Dawdler"):
        $ gm_abouther_list.append(choice(["Hey, have you heard the saying, “Good things come to those who sleep?” ... Uh, and wait?", "I always get sleepy after a meal... It's just natural providence.", "Fuwa... This season sure makes me sleepy...", "No matter how much I sleep I can't get enough of it....", "*Yawn* You know lack of sleep is damaging to the skin.", "There are days when I just don't feel like doing anything... a lot of them, actually."]))

    if ct("Frigid"):
        $ gm_abouther_list.append(choice(["Why does everyone get so excited about underwear? It's just fabric...", "Relations should be clean and wholesome, an example to others."]))

    if ct("Exhibitionist"):
        $ gm_abouther_list.append(choice(["Have you ever thought of doing it in public? Just imagine all those eyes...", "It would be a waste not to show some skin when the weather is nice.", "It arouses me when strangers are staring... Stripping me with their eyes..."]))

    if ct("Clumsy"):
        $ gm_abouther_list.append(choice(["It's common place to spill all the contents when opening a bag of candy, isn't it?", "I broke another plate. How many has it been now..? I wish I could do something about this."]))

    if ct("Sexy Air"):
        $ gm_abouther_list.append(choice(["Everyone keeps saying that the way I lick my lips is incredibly erotic.", "I like to use my tongue to play around with candy in my mouth. Don't you?", "Aah, I wanna eat something sour..."]))

    if ct("Nymphomaniac"):
        $ gm_abouther_list.append(choice(["No matter how much I do it, I still can't cool down. Hehe, what do you *think* I'm talking about?", "I've been having these unintentional s... sexual urges lately....", "My body gets horny all on its on even when I'm by myself... It's so frustrating!", "I can become horny just like that all of a sudden... And before I even realize, I'm already..."]))

    if ct("Virtuous"):
        $ gm_abouther_list.append(choice(["It would be great if people would be nicer to each other...", "I did some volunteer work the other day, it was a pleasant experience.", "It really pains me when I see someone suffering.", "It’s the most elevating feeling when you can help someone, isn’t it?"]))

    if ct("Vicious"):
        $ gm_abouther_list.append(choice(["Those disgusting beggars... If you want money, go and earn them! What's the problem?", "The other day a man tried to steal my purse. He won't bother anyone anymore. <ominously grins>"]))

    if ct("Sadist"):
        $ gm_abouther_list.append(choice(["I want to violate someone with a strap-on. You game?", "It makes me so wet when my lover gets a scared look.", "Huhu, discipline is lovely, isn't it..."]))

    if ct("Psychic"):
        $ gm_abouther_list.append(choice(["Just small gestures and facial expressions can reveal even the most ulterior motives.", "I can tell a lot about your personality just from your posture.", "It's not difficult for me to guess what people will do, if I'm able to observe them for a while.", "While it's hard to tell the motives of some, the majority of people are so predictable...", "It's hard to predict the movements of a warrior. They are trained to hide their thoughts.", "You... have a shadow of death hanging over you... No, it's nothing. Nevermind that.", "A spell has been cast... Long ago... But it's still here... Hm? Did I just... said something?"]))

    if ct("Serious"):
        $ gm_abouther_list.append(choice(["Only with a clear mind can you be truly effective. Emotions just get in the way.", "Nothing good can come from being too emotional.", "If a problem has a solution, there's no reason to be worried. And if it doesn't... then there's no reason to be worried either.", "Anger or tears cannot solve anything."]))

    if ct("Masochist"):
        $ gm_abouther_list.append(choice(["I don't hate the pain. Because...it can feel good in its own way...", "Tied up and blindfolded... Isn't it exciting?", "Being mistreated a little... can be fun....", "No, I don't like pain. Even so, sometimes chains are... oh no, what am I saying?!", "If you tied me up... the experience... Both my body and soul... Oh no, what am I saying..."]))

    if ct("Athletic"):
        $ gm_abouther_list.append(choice(["I may look slow, but I'm actually really good at sports.", "I think it's important to keep yourself in good shape.", "Want to race? I won't lose.", "I went exercising and ran up quite a sweat. It's a good feeling."]))

    if ct("Artificial Body"):
        $ gm_abouther_list.append(choice(["Do I actually appear human to you? Oh nothing, nevermind that.", "I can keep going even without much sleep. Isn't that great?", "I've been having these weird dreams where I'm me, yet, I'm not me.... I wonder what this could be about...."]))

    if ct("Neat"):
        $ gm_abouther_list.append(choice(["It's a good day for doing laundry.", "When you don't diligently clean wet areas of the house you can get an outbreak of mold and various bacteria.", "For some reason, the dust on the windowsill really bothers me.", "Most people don't like them, but chores are an important job, too.", "You can make any place clean and cozy with thorough work.", "Chores take much less time when properly organized.", "Pleasant service is the foundation of any successful business. Nothing can drive off customers faster than rudeness.", "Cleanliness is next to godliness. Don't you agree?"]))

    if ct("Messy"):
        $ gm_abouther_list.append(choice(["It's fine to skip a bath if you don't reek of sweat.", "Do you think I'm sweaty? Some perv in the alley told me he likes sweaty ones. Yuicks.", "My room might look like it's in a mess, but I always know where to find anything there."]))

    if ct("Heavy Drinker"):
        $ gm_abouther_list.append(choice(["You wanna have a drinking contest? Hehe, I won't lose to you.", "I say, there's always a reason to drink."]))

    if ct("Curious"):
        $ gm_abouther_list.append(choice(["Experiencing new things is loads of fun, isn't it?", "The truth always comes up at the very end... No, it's nothing.", "Huh? Hey, I found some more money... Oh wait, it's just a shiny rock.", "Want to see the shells I picked up at the beach?", "I spent a long time chasing a really cute cat I saw.", "In order to keep up with the latest fads, intelligence gathering is essential.", "Strolling through town is a nice change of pace."]))

    if ct("Shy"):
        $ gm_abouther_list.append(choice(["It would be good... if I could just be a bit more confident... I think...", "I'm no good with public speaking...", "I don't like being competitive...", "Umm, I'm... not really good with standing out...", "I don't like making eye contact...", "...Appearing in front of people... I'm reluctant...", "I'm not fond of... talking to people..."]))

    if ct("Elf"):
        $ gm_abouther_list.append(choice(["Gardening is so much fun, you know?", "Sometimes I feed forest animals next to the city."]))

    if ct("Always Hungry"):
        $ gm_abouther_list.append(choice(["I'm still hungry, no matter how much I eat.", "I can eat nonstop, is there something wrong with that?", "No matter how much I devour, my stomach is still empty. Am I still growing or something?", "You'll get heat fatigue if you don't eat properly.", "I wonder why I'm always so hungry. I'm not gaining much weight, so it's fine, but...", "I really do eat too much but I still manage to keep in shape, so....", "I've got a craving for sweets just now...", "I've had a huge appetite lately. If this continues then I might gain weight... This has to stop."]))

    $ pref_list = {"gold": [["I really hate that everything revolves around money in this city."],
                            ["Successful people are only successful, because they had something to start with."]],
                   "fame": [["Never trust the crowd to make the right decision."],
                            ["One has to have good connections if they want to achieve anything in this city."]],
                   "reputation": [["Not long ago the king was passing near by me on the street. Everyone was awestruck by him. So disgusting..."],
                                  ["I would love to meet the king sometime."]],
                   "arena_rep": [["It is quite pointless to fight just for to show. Real heros need to put themselfs to worthy cause."],
                                  ["Real fighters can not just sit back and relax. They must maintain their reputation by showing their strength."]],
                   "charisma": [["I tend to ignore people who think only look matters."],
                                ["Not everyone is born to be a leader."]],
                   "constitution": [["Common people just use their endurance, but it is important to step back sometimes."],
                                    ["You can always reach your goals, just have to put yourself to the task."]],
                   "character": [["Just because someone does not change their opinion, does not mean that they are unique."],
                                 ["The average people change with the winds."]],
                   "intelligence": [["I really loath people who boast about their knowledge."],
                                    ["There is so much to study at the library. I think it is even impossible to learn everything."]],
                   "attack": [["It is sickening that some people can not solve their problems in a peaceful way."],
                              ["If nothing else, the force is always there as a last resort."]],
                   "magic": [["I'm really afraid that sometime someone lose control of the power their acquired."],
                             ["So much can be achieved using the powers of the ancestors."]],
                   "defence": [["I do not really like overprotective people. I can take care of myself!"],
                               ["It is really important to feel safe around your closest friends, don't you think?"]],
                   "agility": [["If someone bends easily, they are going to be bent, right?"],
                               ["Dancing is an important part of our social life."]],
                   "luck": [["Some people bet everything on poor luck, then wonder why they lose."],
                            ["There are people who got everything by luck, I really envy them."]],
                   "vaginal": [["Todays people are so conservative in their thinking."],
                               ["I feel like much can be achieved by convervative approach."]],
                   "anal": [["I prefer to look at people face-to-face, always afraid that they stab me in the back."],
                            ["There is always an other option if the common way is closed."]],
                   "oral": [["People have to be on the same level when they are approaching each other, right?"],
                            ["Sometimes you give, sometimes you get. The important thing is to feel good. Am I right?"]],
                   "sex": [["Maybe I was born in the wrong world. Everyone wants the same."],
                           ["Never had trouble to find something to do."]],
                   "group": [["I do not really like crowded places."],
                             ["It is really boring to do the same over and over again."]],
                   "bdsm": [["I think there are people who do not value their freedom enough."],
                            ["It is really hard to earn someones trust. That is why it is so valuable."]]}

    python hide:
        for k, v in char.preferences.items():
            if v < 20:
                gm_abouther_list.append(choice(pref_list[k][0]))
            elif v > 80:
                gm_abouther_list.append(choice(pref_list[k][1]))

    # if there is not enough specific answers, a vague one is added to the list
    if len(gm_abouther_list) < 3:
        $ gm_abouther_list.append(choice(["Hm? A little of this, a little of that?", "...I don't really have much to say.", "Nothing much, there's nothing worth mentioning.", "What I'm doing? The usual stuff...", "I'm just normal, I guess.", "I like just about anything.", "Hmm, there's not much to talk about.", "Now that I think about it... am I just boring?", "I'm just about average, I guess."]))

    $ rc(*gm_abouther_list)

    if 2*m <= n and dice(50) and dice(char.get_stat("joy")-20):
        if char.get_stat("disposition") >= 400:
            $ narrator(choice(["You feel especially close."]))
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ char.gfx_mod_stat("disposition", randint(1, 2))
        else:
            $ narrator(choice(["She was much more approachable."]))
            $ char.gfx_mod_stat("disposition", randint(2, 6))
        if hero.get_stat("joy") < 80:
            $ hero.gfx_mod_stat("joy", randint(0, 1))
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
        $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.25))

    $ char.gfx_mod_stat("disposition", randint(5, 15))
    $ char.gfx_mod_stat("affection", affection_reward(char))

    $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
    $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.25))

    $ del gm_abouther_list, pref_list, m, n
    jump girl_interactions

# ask about occupation
label interactions_aboutoccupation:
    $ interactions_check_for_bad_stuff(char)
    $ m = interactions_flag_count_checker(char, "flag_interactions_aboutoccupation")
    if m > 5:
        $ del m
        call interactions_too_many_lines from _call_interactions_too_many_lines_5
        $ char.gfx_mod_stat("disposition", -5)
        $ char.gfx_mod_stat("affection", -1)
        jump girl_interactions
    $ del m

    if char.get_stat("disposition") <= -250 and char.status == "free":
        $ char.gfx_mod_stat("disposition", -5)
        $ char.gfx_mod_stat("affection", -1)
        jump interactions_refused

    python hide:
        options = OrderedDict()
        options["Knight"] = ("I'm more like a bodyguard.", "In battle I was taught to protect others.", "My job is to hold the enemy.")
        options["Shooter"] = ("I prefer to keep the enemy at a distance.", "I prefer to use ranged weapons.", "I'm a pretty good marksman.")
        options["Assassin"] = ("I was taught the art of stealthy assassination.", "I'm an assassin. They never see me coming.", "I have had training to kill at any cost. So my methods are... concealed.")
        options["Healer"] = ("I know a lot about healing magic.", "My job is to heal wounds.", "I'm a healer, my magic helps other people.")
        options["Stripper"] = ("I specialize in erotic dances.", "I'm undressing on stage, if you know what I mean.")
        options["Maid"] = ("I perform menial tasks around the household.", "I'm a professional maid.")
        options["Cleaner"] = ("I'm good at cleaning stuff.", "I'm a just a cleaner.")
        options["Barmaid"] = ("I'm a decent bartender.", "I'm decent at pouring drinks and chatting with people about their problems.")
        options["Manager"] = ("I know a thing or two about managing.", "I know how to manage people.")
        options["Prostitute"] = ("I'm a fancy girl.", "I'm a merchant. And my merchandise is my beautiful body ♪", "I provide personal services. I mean very personal.", "I sell my love to those who need it.")
        options["Mage"] = ("I'm a magician.", "I have arcane energies at my command.", "I have a magical talent. It's very useful in many cases.")
        options["Warrior"] = ("I was trained to fight.", "I have combat training.", "I know how to fight.", "I know how to behave on the battlefield.")

        temp = [t.id for t in char.traits.basetraits]
        for base, values in options.iteritems():
            if base in temp:
                rc(*values)
                temp.remove(base)

        #gen_occ_options = OrderedDict()
        #gen_occ_options["Combatant"] = ["I can fight pretty well!"]
        #gen_occ_options["Caster"] = ['I am very decent at spellcasting!']
        #gen_occ_options["Server"] = ["I specialize in service industry!"]
        #gen_occ_options["Specialist"] = ["I am Specialist!"]
        #gen_occ_options["SIW"] = ["I specialize in Adult Industry!"]
        for t in temp:
            rc("Something is amiss with my profession: %s... (Please tell the Devs about that!)" % t)

    $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.15))
    $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.15))

    jump girl_interactions

label interactions_interests:
    $ interactions_check_for_bad_stuff(char)
    $ interactions_check_for_minor_bad_stuff(char)
    $ m = 1 + interactions_flag_count_checker(char, "flag_interactions_interests")
    $ n = 2 + interactions_set_repeating_lines_limit(char)
    if m > n:
        $ del m, n
        call interactions_too_many_lines from _call_interactions_too_many_lines_6
        $ char.gfx_mod_stat("disposition", -randint(5, 10))
        $ char.gfx_mod_stat("affection", -randint(1,3))
        if char.get_stat("joy") > 40:
            $ char.gfx_mod_stat("joy", -randint(1, 2))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        jump girl_interactions

    if char.get_stat("disposition") <= 100:
        $ del m, n
        $ char.gfx_mod_stat("disposition", -randint(3, 10))
        $ char.gfx_mod_stat("affection", -randint(0,2))
        $ char.gfx_mod_stat("joy", -randint(0, 1))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status != "free":
            "You tried to know [char.nickname] better."
        jump interactions_refused

    $ line = rts(char, {
        "Exhibitionist": ["[char.pC] tells you pretty hot stories about [char.op] exhibitionistic adventures in a local park."],
        "Athletic": ["You discuss beach volleyball which became quite popular among local girls lately.", "You discuss places for swimming. It looks like most girls prefer beaches to pools because it's free."],
        "Manly": ["[char.pC] gives you a lecture on how to build your muscles properly. You feel a bit offended, but keep your cool.", "[char.pC] casually remarks that you should exercise more often, and gives you some advice."],
        "Chubby": ["You have a lively discussion about your favorite local bakeries and pastry shops.", "Your conversation turns toward cooking, and [char.p] shares some of [char.pp] recipes. They are all pretty high in calories..."],
        "Slim": ["You compliment [char.op] figure, and the conversation quickly turns toward healthy lifestyle. Ugh.", "[char.pC] brags about [char.op] metabolism, allowing [char.op] to eat sweets and not get fat. You envy [char.op]."],
        "Alien": ["[char.pC] talks about [char.pp] homeland. You are listening with interest.", "You discuss local events [char.p] witnessed. [char.pC] doesn't understand the meaning of some of them, and you spend some of your time to explain."],
        "Half-Sister": ["You discuss your common father. The sad discussion quickly turns into a sarcastic one, when you try to count all his lovers and daughters.", "[char.pC] tells you about [char.pp] mother. You listen in silence, trying to imagine yours.", "You spend time together you reminiscing about fun and embarrassing moments from your childhood."],
        "Scars": ["She complains about how [char.pp] scars cause inconvenience. You comfort [char.op]."],
        "Artificial Body": ["Tempted by curiosity, you ask about [char.op] artificial body. [char.opC] explanations are very long and confusing.", "You discuss the regular maintenance required by [char.op] body. It's a pretty complex, but piquant conversation."],
        "Lolita": ["[char.pC] complains about how hard it is to find adult clothes for [char.op] figure. You're trying to take [char.op] away from this sensitive topic.", "[char.pC] tells you funny stories about disappointed (and imprisoned) pedophiles confused by [char.op] body size. What a strange topic."],
        "Strange Eyes": ["[char.pC] notices how you look at [char.op] unusual eyes. Embarrassed, [char.p] refuses to look at you or discuss anything."],
        "Great Arse": ["You try to keep it to small talk, trying not to think about [char.op] gorgeous butt and what would you do if you were behind [char.op]."],
        "Long Legs": ["During your small conversation you can't help but glance at [char.op] long legs. It looks like [char.p] is used to it and doesn't care much."],
        "Abnormally Large Boobs": ["You vaguely remember your conversation, paying most of your attention to [char.op] amazing chest.", "[char.pC] complains about high costs for the purchase of new bra. It appears that the fabric is not strong enough to withstand such loads. Without knowing what reaction [char.p] expected, you keep your poker face."],
        "Big Boobs": ["[char.pC] complains how a big chest spoils the posture. You sympathize with [char.op], very convincingly and almost sincerely."],
        "Small Boobs": ["[char.pC] starts a conversation about irrelevance of chest size. You carefully assent, trying to not piss [char.op] off."],
        "Fire": ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of fire."],
        "Water": ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of water."],
        "Air": ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of air."],
        "Earth": ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of earth."],
        "Ice": ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of ice."],
        "Electricity": ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of electricity."],
        "Light": ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of light."],
        "Darkness": ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of darkness."],
        "Nerd": ["You discuss new books in local stores and libraries.", "Somehow your conversation comes to board games, and [char.p] enthusiastically explains to you the intricate rules of one of them."],
        "Psychic": ["It's difficult to participate in the conversation when your interlocutor knows your words in advance. [char.pC] seems to enjoy teasing you, however.", "[char.pC] complains about headaches, dizziness and other neural disorders that are common for psychics."],
        "Optimist": ["It looks like [char.p] is in a good mood. Laughing and joking during your conversation, [char.p] quickly turns it into a humorous one.", "You exchange your freshest anecdotes."],
        "Pessimist": ["It looks like [char.p]'s not in the mood. Your conversation is pretty gloomy, though you managed to cheer [char.op] up a bit."],
        "Serious": ["You have a very serious conversation about local politics and taxes. You feel squeezed like a lemon.", "[char.pC] gives you a lecture about the importance of planning for the future. You heroically hold back a yawn."],
        "Extremely Jealous": ["[char.pC] inquires about your relationships with other girls. You carefully dispel [char.op] concern, trying not to make definitive statements."],
        "Virtuous": ["[char.pC] tells about [char.op] volunteer work. It's nice, but a bit boring."],
        "Vicious": ["[char.pC] gossips with obvious pleasure about [char.op] acquaintance's misfortunes."],
        "Dawdler": ["You have a lazy, indolent discussion. It looks like [char.p]'s half asleep.", "[char.pC] pensively tells you about [char.op] recent dreams. You begin to feel drowsy."],
        "Clumsy": ["You talk about misfortunes caused by [char.op] clumsiness. You heroically hold back a smile and comfort [char.op] instead."],
        "Nymphomaniac": ["An innocent conversation turns into the discussion about sexual positions. [char.pC]'s really into this stuff.", "[char.pC] passionately talks about [char.op] recent sexual adventures. Wow."],
        "Heavy Drinker": ["You discuss various types of alcohol, sharing your drinking experience."],
        "Always Hungry": ["You talk about food for some time. It looks like [char.p] can continue it for hours, so you carefully interrupt the conversation."],
        "Curious": ["You exchange the latest news and gossip. [char.pC] really knows a lot about it."],
        "cgo('Combatant')": ["You discuss the recent fights at the arena and their participants.", "You discuss a variety of fighting styles."],
        "cgo('Caster')": ["[char.pC] enthusiastically talks about mysteries of arcane arts.", "You discuss [char.op] magical studies."],
        "cgo('SIW')": ["You gossip about the strangeness of some of [char.op] customers."],
        "cgo('Server')": ["[char.pC] recounts rumors that [char.p] heard from customers lately. People tend to not notice service workers when they are not needed."],
        "default": ["You chat for some time."]
        })

    $ narrator(line)

    if 2*m <= n and dice(50) and dice(char.get_stat("joy")-20):
        if char.get_stat("disposition") >= 400:
            $ narrator(choice(["You feel especially close."]))
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ char.gfx_mod_stat("disposition", randint(1, 2))
        else:
            $ narrator(choice(["She was much more approachable."]))
            $ char.gfx_mod_stat("disposition", randint(2, 6))
        if hero.get_stat("joy") < 80:
            $ hero.gfx_mod_stat("joy", randint(0, 1))
        $ char.gfx_mod_stat("affection", affection_reward(char))
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.1))
        $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.1))

    $ char.gfx_mod_stat("disposition", randint(10, 20))
    $ char.gfx_mod_stat("affection", affection_reward(char))
    
    $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.15))
    $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.15))

    if char.get_stat("joy") >= 65:
        if dice(char.get_stat("joy")-20):
            "It was a very lively and enjoyable conversation."
            $ char.gfx_mod_stat("joy", randint(3, 5))
        else:
            "It was a pretty lively conversation."
            $ char.gfx_mod_stat("joy", randint(2, 4))
        if hero.get_stat("joy") < 80:
            $ hero.gfx_mod_stat("joy", randint(0, 1))
    elif char.get_stat("joy") >= 30:
        if dice(char.get_stat("joy") + 20):
            "You had a fairly normal conversation."
            $ char.gfx_mod_stat("joy", randint(1, 3))
        else:
            "You had a short conversation."
    else:
        "It was a short and not very pleasant conversation."
        $ char.gfx_mod_stat("joy", -randint(0, 2))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 2))

    $ del m, n, line
    jump girl_interactions

# flirt
label interactions_flirt:
    $ interactions_check_for_bad_stuff(char)
    $ interactions_check_for_minor_bad_stuff(char)
    $ m = 1 + interactions_flag_count_checker(char, "flag_interactions_flirt")
    $ n = 1 + interactions_set_repeating_lines_limit(char)
    if m > n:
        $ del m, n
        call interactions_too_many_lines from _call_interactions_too_many_lines_7
        $ char.gfx_mod_stat("disposition", -randint(5,15))
        $ char.gfx_mod_stat("affection", -randint(0,2))
        if char.get_stat("joy") > 30:
            $ char.gfx_mod_stat("joy", -randint(2, 4))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        jump girl_interactions

    if char.get_stat("affection") <= 150 or char.get_stat("disposition") <= 50:
        $ del m, n
        $ char.gfx_mod_stat("disposition", -randint(5, 10))
        $ char.gfx_mod_stat("affection", -randint(0,2))
        $ char.gfx_mod_stat("joy", -randint(0, 1))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status != "free":
            "You tried to flirt with [char.nickname]."
        jump interactions_refused

    $ char.override_portrait("portrait", "shy")

    if ct("Impersonal"):
        $ rc("To express it in words is very difficult...", "Infatuation and love are different. Infatuation will fade, but love's memory continues forever.", "I think it is a good thing to be loved by someone.")
    elif ct("Shy") and dice(40):
        $ rc("Lovers... Th-they're supposed to...hold hands, after all... Right?", "Wh-what comes after a k-kiss is... It's... Awawa...", "If it's the person you love, just having them turn around and smile... Is enough to make you happy...", "Love... sure is a good thing...")
    elif ct("Nymphomaniac") and dice(40):
        $ rc("*sigh* I always have such a high libido...", "Um... Love can start from lust... right?", "If you are in love, having sex is totally normal, right?", "People are no more than animals, so it's only natural to copulate...", "Well, doing perverted stuff is proof that you're healthy.", "Me thinking about sex? Not at all... Great. Now that you brought it up...")
    elif ct("Bisexual", "Lesbian") and dice(20):
        $ rc("Love runs deeper than gender.")
    elif ct("Dandere"):
        $ rc("If you like them, you like them. If you hate them, you hate them. That's all there is to it.", "My dream yesterday... It was so lovey-dovey and erotic.", "Getting close to people other than the one you love is kind of...", "You can still live a good life without a lover, don't you think?")
    elif ct("Tsundere"):
        $ rc("M...men and women feel arousal differently.... F-f-forget what I just said!", "Thick and hard? What the... You idiot, what are you saying! That's not what you meant? ... You idiot!", "E-even I want to be a good bride someday, you know...?", "Things like l-love or affection, are all excuses.")
    elif ct("Kuudere"):
        $ rc("To feel the same feelings towards each other... To be partners for life... That's what I long for.", "Two people in love devoting themselves to each other, that sounds like pure bliss to me...", "True love isn't about showing off to everyone else... It's the small things you do for your partner that matter.", "There's gotta be someone willing to support me out there somewhere...", "Chance encounters only happen with both time and luck... Well, I suppose you could call it fate.")
    elif ct("Imouto"):
        $ rc("That's weird... Today's love fortune was supposed to be a sure thing... Hmm...", "That book is very interesting... A boy and a girl who you'd think are twins get together, but in fact...", "L-love and affection and th-that stuff, I don't really get it very well...", "If I'm going to date someone, they should be rich ♪, and want kids ♪ And they should be totally committed to me ♪")
    elif ct("Ane"):
        $ rc("You're deciding who will be your partner for life.　It would be strange not to be worried about it.", "I think just having the one you love beside you is the ultimate happiness.", "I need a person whom I can rely on.", "Lost loves are important to build character, I think.", "As you've probably noticed, I'm the devoted type ♪", "Of course, I'd wanna stay by my loved one's side. Or, rather than being by their side, it's more, like, I want to support them?")
    elif ct("Kamidere"):
        $ rc("Seriously, how can I... think of such unpleasant thoughts...", "When my body gets hot, it's like my discipline starts to crumble...", "There are things more important than physical infatuation.", "Making lovers my playthings is a simple matter for one such as I. Eheh!", "Love is nothing but an expression of ego, you know.", "You can't disobey your instincts. Isn't keeping up this charade painful for you?")
    elif ct("Bokukko"):
        $ rc("Love is a competition! A conflict! A war!", "If the other person won't give you a second glance, you need to make 'em. It's simple, really.", "Love, hmm ♪ ... Hn, just thinking about it makes me sort of embarrassed...", "I'm gonna be the bestest wife!", "Is this that fate thing they're talking about?")
    elif ct("Yandere"):
        $ rc("Huhu, a girl in love is invincible ♪", "Nothing motivates you quite like 'love', huh...", "If it's just with their mouth, everyone can talk about love. Even though none of them know how hard it is in reality...", "I want to try many different ways to kiss, I think...")
    else:
        $ rc("Getting your heart broken is scary, but everything going too well is kinda scary for its own reasons too.", "One day, I want to be carried like a princess by the one I love ♪...", "Hehe! Love conquers all!", "I'm the type to stick to the one I love.", "Being next to someone who makes you feel safe, that must be happiness...", "Everyone wants to fall in love, I suppose. Don't you think?")
    $ char.restore_portrait()

    if 2*m <= n and dice(50) and dice(char.get_stat("joy")-40):
        $ narrator(choice(["You feel especially close."]))
        $ char.gfx_mod_stat("joy", randint(0, 1))
        $ char.gfx_mod_stat("affection", affection_reward(char))
        $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.10))
        $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.10))
        if hero.get_stat("joy") < 80:
            $ hero.gfx_mod_stat("joy", randint(0, 1))

    $ hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=.25))
    $ char.gfx_mod_exp(exp_reward(char, hero, exp_mod=.25))

    $ char.gfx_mod_stat("disposition", randint(5, 15))
    $ char.gfx_mod_stat("affection", affection_reward(char))

    $ del m, n
    jump girl_interactions

# interaction check fail
label interactions_refused:
    $ char.override_portrait("portrait", "indifferent")
    if char.status == "free":
        if ct("Impersonal"):
            $ rc("Denied.", "It's none of your business.", "...")
        elif ct("Shy"):
            $ char.override_portrait("portrait", "shy")
            $ rc("I-I won't tell you... ", "I don't want to talk... sorry.", "W-Well... I d-don't want to tell you...", "Ah, ugh... Do I have to tell you...?")
        elif ct("Dandere"):
            $ rc("I don't feel the need to answer that question.", "...Let's talk later...maybe.", "I'm not going to tell you.")
        elif ct("Kuudere"):
            $ rc("I've got no reason to tell you.", "I'm not in the mood for that right now.", "Why do I have to tell you?")
        elif ct("Tsundere"):
            $ rc("Hmph! Who would tell you!", "Eh? You expect me to tell you?", "It's none of your business.")
        elif ct("Imouto"):
            $ rc("Uhuhu, I won't tell you!", "It's a secret!", "Umm, is it bad if I don't answer...?")
        elif ct("Yandere"):
            $ rc("I'm not in a mood for chatting.", "...I don't feel like answering.")
        elif ct("Kamidere"):
            $ rc("And what will hearing that do for you?", "And what good would knowing that do you?")
        elif ct("Ane"):
            $ rc("Sorry, can we talk later?", "Sorry, but I don't want to answer.", "*sigh*... Don't you have anything else to do?")
        elif ct("Bokukko"):
            $ rc("Eh, say what?", "Why do I hafta give you an answer?", "I'm not gonna answer that.")
        else:
            $ rc("I don't want to answer.", "I don't want to talk now.", "Must I give you an answer?")
    else:
        $ narrator(choice(["But it only led to awkward silence.", "But it had no positive effect whatsoever.", "But it was kind of one-sided."]))
    $ char.restore_portrait()
    jump girl_interactions

# testing stuff
label interactions_disp:
    $ char.gfx_mod_stat("disposition", 250)
    $ char.gfx_mod_stat("affection", 250)
    jump girl_interactions

label interactions_becomefr:
    $ char.gfx_mod_stat("disposition", 500)
    $ char.gfx_mod_stat("affection", 500)
    $ set_friends(hero, char)
    jump girl_interactions

label interactions_becomelv:
    $ char.gfx_mod_stat("disposition", 500)
    $ char.gfx_mod_stat("affection", 500)
    $ set_lovers(hero, char)
    jump girl_interactions
