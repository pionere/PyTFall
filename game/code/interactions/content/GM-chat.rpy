# general chat
label interactions_smalltalk:
    "You have a small chat with [char.nickname]."
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if iam.check_for_minor_bad_stuff(char):
        jump girl_interactions
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_general")
    $ n = 2 + iam.repeating_lines_limit(char)
    if m > n:
        if m > 1:
            $ iam.refuse_too_many(char)
        else:
            $ iam.refuse_talk_any(char)
        $ del m, n
        $ char.gfx_mod_stat("disposition", -randint(3, 6))
        $ char.gfx_mod_stat("affection", -randint(0, 3))
        if char.get_stat("joy") > 80:
            $ char.gfx_mod_stat("joy", -1)
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -1)
        jump girl_interactions
    if char.get_stat("disposition") >= 100:
        if dice(5):
            $ gossip = iam.world_gossips.get_gossip()
            if gossip:
                $ gossip = getattr(iam, gossip.func)
                $ gossip(char)
        if "Impersonal" in char.traits or "Dandere" in char.traits or "Shy" in char.traits:
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
            $ iam.int_reward_exp(char)
            $ char.gfx_mod_stat("affection", affection_reward(char, .1))
    elif char.get_stat("disposition") >= -100:
        if "Impersonal" in char.traits or "Dandere" in char.traits or "Shy" in char.traits:
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
    $ iam.int_reward_exp(char)
    $ del m, n
    jump girl_interactions

# ask about job
label girl_interactions_aboutjob: # TO DO: here would help additional logic based on actual recent jobs events
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if iam.flag_count_checker(char, "flag_interactions_aboutjob") != 0:
        $ iam.refuse_too_many(char)
        $ char.gfx_mod_stat("disposition", -randint(4,6))
        $ char.gfx_mod_stat("affection", -randint(1,2))
        jump girl_interactions

    if char.flag("daysemployed") < 5:
        # Less than 10 days in service:
        $ iam.comment_job_new(char)

        $ char.gfx_mod_stat("disposition", 1)
        $ char.gfx_mod_stat("affection", affection_reward(char, .5))
        $ char.gfx_mod_stat("joy", 1)
    elif char.get_stat("disposition") <= -350:
        $ iam.comment_job_very_low_disp(char)

        $ char.gfx_mod_stat("disposition", randint(0, 1))
        $ char.gfx_mod_stat("affection", affection_reward(char, .25))
    elif char.get_stat("disposition") <= -50:
        if char.get_stat("joy") >= 50:
            $ iam.comment_job_low_disp_high_joy(char)
        else:
            $ iam.comment_job_low_disp_low_joy(char)
        $ char.gfx_mod_stat("disposition", randint(1, 2))
        $ char.gfx_mod_stat("affection", affection_reward(char))
        $ char.gfx_mod_stat("joy", randint(0, 1))
    else:
        if char.get_stat("joy") >= 50:
            $ iam.comment_job_high_joy(char)
        else:
            $ iam.comment_job_low_joy(char)
        $ char.gfx_mod_stat("disposition", randint(1, 3))
        $ char.gfx_mod_stat("affection", affection_reward(char))
        $ char.gfx_mod_stat("joy", randint(0, 1))
        $ char.restore_portrait()

    $ iam.int_reward_exp(char)

    jump girl_interactions

# ask how she feels
label interactions_how_feels:
    if iam.flag_count_checker(char, "flag_interactions_how_feels") != 0:
        $ iam.refuse_too_many(char)
        $ char.gfx_mod_stat("disposition", -randint(4,6))
        $ char.gfx_mod_stat("affection", -randint(1,2))
        jump girl_interactions

    if "Food Poisoning" in char.effects: # at least no penalty to disposition, unlike other cases with food poisoning
        $ iam.say_line(char, ("I ate something wrong. Ow-ow-ow...", "Ouh. I think I need to use bathroom again..."), "sad")
        jump girl_interactions_end
    elif "Down with Cold" in char.effects or (char.get_stat("health") < char.get_max("health")/5) or char.get_stat("joy") < 25: # we select one suitable image in the very beginning
        $ mood = "sad"
    elif char.get_stat("vitality") < char.get_max("vitality")/3:
        $ mood = "tired"
    elif "Drunk" in char.effects:
        $ mood = "uncertain"
    elif "Shy" in char.traits:
        $ mood = "shy"
    elif char.get_stat("joy") > 70:
        $ mood = "happy"
    else:
        $ mood = "indifferent"

    if 'Down with Cold' in char.effects: #illness
        $ iam.say_line(char, ("I think I caught a cold...", "I'm not feeling well today. *sneezes*", "I have a fever... <She looks pale>"), "sad")

    if "Drunk" in char.effects:
        $ iam.say_line(char, ("I feel a bit dizzy...", "I think I drunk a bit too much. *hukk*", "Ehm... Just one more drink... I guess..."), "uncertain")

    #body checks
    if char.get_stat("vitality") <= char.get_max("vitality")/10:
        $ iam.say_line(char, ("I want to sleep so badly... <yawns>", "I'm very tired lately... <yawns>"), mood)
    elif char.get_stat("vitality") < char.get_max("vitality")/3:
        $ iam.say_line(char, ("My body a bit tired.", "I could use some rest.", "I feel weakness, I really should rest more..."), mood)
    elif char.get_stat("vitality") >= char.get_max("vitality")*9/10:
        $ iam.say_line(char, ("I'm full of strength and energy.", "My body rested very well lately."), mood)

    if char.get_stat("health") <= char.get_max("health")/3:
        $ iam.say_line(char, ("My whole body hurts. I think I need a doctor.", "My body is not feeling very well lately... I could use some medical attention."), "sad")
    elif char.get_stat("health") >= char.get_max("health")*9/10 and mood != "sad" and mood != "tired":
        $ iam.say_line(char, ("My body is in top condition.", "My health is pretty good lately."), mood)

    if "Caster" in char.gen_occs:
        if char.get_stat("mp") <= char.get_max("mp")/5:
            $ iam.say_line(char, ("I feel drained.", "My mind is tired. Perhaps I should use magic less frequently."), "tired")
        elif char.get_stat("mp") >= char.get_max("mp")*9/10 and mood != "sad" and mood != "tired":
            $ iam.say_line(char, ("I feel like magic overflows me.", "I'm filled with magic energy."), mood)

    if char.get_stat("joy") <= 30: #begin joy checks
        $ iam.comment_joy_low(char, mood)
    elif char.get_stat("joy") >= 65:
        $ iam.comment_joy_high(char, mood)
    else:
        $ iam.comment_joy_neutral(char, mood)
    $ del mood

    $ char.gfx_mod_stat("disposition", randint(2, 4))
    $ char.gfx_mod_stat("affection", affection_reward(char))

    $ iam.int_reward_exp(char)

    jump girl_interactions

# ask about her
label interactions_about_char:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if iam.check_for_minor_bad_stuff(char):
        jump girl_interactions
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_about_char")
    $ n = 2 + iam.repeating_lines_limit(char)
    if m > n:
        if m > 1:
            $ iam.refuse_too_many(char)
        else:
            $ iam.refuse_talk_any(char)
        $ del m, n
        $ char.gfx_mod_stat("disposition", -randint(1, 5))
        $ char.gfx_mod_stat("affection", -randint(0, 2))
        if char.get_stat("joy") > 40:
            $ char.gfx_mod_stat("joy", -randint(0, 2))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -1)
        jump girl_interactions

    if char.get_stat("disposition") <= 50:
        $ del m, n
        $ char.gfx_mod_stat("disposition", -randint(3, 10))
        $ char.gfx_mod_stat("affection", -randint(0, 2))
        $ char.gfx_mod_stat("joy", -randint(0, 1))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status != "free":
            "You tried to know [char.nickname] better."
        $ iam.refuse_interaction(char)
        jump girl_interactions

    $ lines = []
    python hide:
        char_traits = char.traits
        for trait in char_traits:
            trait = trait.id
            if trait == "Big Boobs" or trait == "Abnormally Large Boobs":
                t_lines = ["I notice men, everyone of them, staring at nothing but my boobs.", "I've outgrown yet another bra... I wish something could be done about this...", "Hey, [char.mc_ref], do you know what my charms are? Ufu, shall I show you? I'm pretty sure I can make your heart skip a beat ♪", "All the men just keep staring at my breasts. Are such big ones really that fascinating?", "The reason you're interested in me is my big breasts, right?", "They say that big breasts are the best, but truth be told they're heavy and make the shoulders stiff, not good at all."]
            elif trait == "Small Boobs":
                t_lines = ["I read lately that the hunt is on for small breasts. Who cares about big tits!", "It's better without large breasts. They'd only get in the way... Probably...", "Small breasts have their good points as well, don't you think? You do think so, right?"]
            elif trait == "Lesbian":
                t_lines = ["I am REALLY interested in female's body curves.", "I would like to go to an all girls' school. Imagine, only girls, everywhere... That would be great...", "I'd like to bring a cute girl home.", "Isn't it normal to be attracted to charming girls? I think it's totally proper ♪", "Something I like? Hmm... Maybe watching cute girls?", "Girls look really cute, don't they? I just want to eat one up.", "I like cute things. Like girls, for example.", "If I were a boy, I sure would explore every inch of the girl I was dating..."]
            elif trait == "Bisexual":
                t_lines = ["In love, gender makes no difference...", "I like boys and girls alike ♫"]
            elif trait == "Fire":
                t_lines = ["I'm pretty good with fire magic."]
            elif trait == "Water":
                t_lines = ["I'm pretty good with water magic."]
            elif trait == "Air":
                t_lines = ["I'm pretty good with air magic."]
            elif trait == "Earth":
                t_lines = ["I'm pretty good with earth magic."]
            elif trait == "Darkness":
                t_lines = ["I'm pretty good with dark magic."]
            elif trait == "Light":
                t_lines = ["I'm pretty good with light magic."]
            elif trait == "Electricity":
                t_lines = ["I'm pretty good with electricity magic."]
            elif trait == "Ice":
                t_lines = ["I'm pretty good with ice magic."]
            elif trait == "Neutral":
                t_lines = ["They say some people have no talent for magic. I'm one of them, it seems."]
            elif trait == "Dawdler":
                t_lines = ["Hey, have you heard the saying, “Good things come to those who sleep?” ... Uh, and wait?", "I always get sleepy after a meal... It's just natural providence.", "Fuwa... This season sure makes me sleepy...", "No matter how much I sleep I can't get enough of it....", "*Yawn* You know lack of sleep is damaging to the skin.", "There are days when I just don't feel like doing anything... a lot of them, actually."]
            elif trait == "Frigid":
                t_lines = ["Why does everyone get so excited about underwear? It's just fabric...", "Relations should be clean and wholesome, an example to others."]
            elif trait == "Exhibitionist":
                t_lines = ["Have you ever thought of doing it in public? Just imagine all those eyes...", "It would be a waste not to show some skin when the weather is nice.", "It arouses me when strangers are staring... Stripping me with their eyes..."]
            elif trait == "Clumsy":
                t_lines = ["It's common place to spill all the contents when opening a bag of candy, isn't it?", "I broke another plate. How many has it been now..? I wish I could do something about this."]
            elif trait == "Sexy Air":
                t_lines = ["Everyone keeps saying that the way I lick my lips is incredibly erotic.", "I like to use my tongue to play around with candy in my mouth. Don't you?", "Aah, I wanna eat something sour..."]
            elif trait == "Nymphomaniac":
                t_lines = ["No matter how much I do it, I still can't cool down. Hehe, what do you *think* I'm talking about?", "I've been having these unintentional s... sexual urges lately....", "My body gets horny all on its on even when I'm by myself... It's so frustrating!", "I can become horny just like that all of a sudden... And before I even realize, I'm already..."]
            elif trait == "Virtuous":
                t_lines = ["It would be great if people would be nicer to each other...", "I did some volunteer work the other day, it was a pleasant experience.", "It really pains me when I see someone suffering.", "It’s the most elevating feeling when you can help someone, isn’t it?"]
            elif trait == "Vicious":
                t_lines = ["Those disgusting beggars... If you want money, go and earn them! What's the problem?", "The other day a man tried to steal my purse. He won't bother anyone anymore. <ominously grins>"]
            elif trait == "Sadist":
                t_lines = ["I want to violate someone with a strap-on. You game?", "It makes me so wet when my lover gets a scared look.", "Huhu, discipline is lovely, isn't it..."]
            elif trait == "Psychic":
                t_lines = ["Just small gestures and facial expressions can reveal even the most ulterior motives.", "I can tell a lot about your personality just from your posture.", "It's not difficult for me to guess what people will do, if I'm able to observe them for a while.", "While it's hard to tell the motives of some, the majority of people are so predictable...", "It's hard to predict the movements of a warrior. They are trained to hide their thoughts.", "You... have a shadow of death hanging over you... No, it's nothing. Nevermind that.", "A spell has been cast... Long ago... But it's still here... Hm? Did I just... said something?"]
            elif trait == "Serious":
                t_lines = ["Only with a clear mind can you be truly effective. Emotions just get in the way.", "Nothing good can come from being too emotional.", "If a problem has a solution, there's no reason to be worried. And if it doesn't... then there's no reason to be worried either.", "Anger or tears cannot solve anything."]
            elif trait == "Masochist":
                t_lines = ["I don't hate the pain. Because...it can feel good in its own way...", "Tied up and blindfolded... Isn't it exciting?", "Being mistreated a little... can be fun....", "No, I don't like pain. Even so, sometimes chains are... oh no, what am I saying?!", "If you tied me up... the experience... Both my body and soul... Oh no, what am I saying..."]
            elif trait == "Athletic":
                t_lines = ["I may look slow, but I'm actually really good at sports.", "I think it's important to keep yourself in good shape.", "Want to race? I won't lose.", "I went exercising and ran up quite a sweat. It's a good feeling."]
            elif trait == "Artificial Body":
                t_lines = ["Do I actually appear human to you? Oh nothing, nevermind that.", "I can keep going even without much sleep. Isn't that great?", "I've been having these weird dreams where I'm me, yet, I'm not me.... I wonder what this could be about...."]
            elif trait == "Neat":
                t_lines = ["It's a good day for doing laundry.", "When you don't diligently clean wet areas of the house you can get an outbreak of mold and various bacteria.", "For some reason, the dust on the windowsill really bothers me.", "Most people don't like them, but chores are an important job, too.", "You can make any place clean and cozy with thorough work.", "Chores take much less time when properly organized.", "Pleasant service is the foundation of any successful business. Nothing can drive off customers faster than rudeness.", "Cleanliness is next to godliness. Don't you agree?"]
            elif trait == "Messy":
                t_lines = ["It's fine to skip a bath if you don't reek of sweat.", "Do you think I'm sweaty? Some perv in the alley told me he likes sweaty ones. Yuicks.", "My room might look like it's in a mess, but I always know where to find anything there."]
            elif trait == "Heavy Drinker":
                t_lines = ["You wanna have a drinking contest? Hehe, I won't lose to you.", "I say, there's always a reason to drink."]
            elif trait == "Curious":
                t_lines = ["Experiencing new things is loads of fun, isn't it?", "The truth always comes up at the very end... No, it's nothing.", "Huh? Hey, I found some more money... Oh wait, it's just a shiny rock.", "Want to see the shells I picked up at the beach?", "I spent a long time chasing a really cute cat I saw.", "In order to keep up with the latest fads, intelligence gathering is essential.", "Strolling through town is a nice change of pace."]
            elif trait == "Shy":
                t_lines = ["It would be good... if I could just be a bit more confident... I think...", "I'm no good with public speaking...", "I don't like being competitive...", "Umm, I'm... not really good with standing out...", "I don't like making eye contact...", "...Appearing in front of people... I'm reluctant...", "I'm not fond of... talking to people..."]
            elif trait == "Elf":
                t_lines = ["Gardening is so much fun, you know?", "Sometimes I feed forest animals next to the city."]
            elif trait == "Always Hungry":
                t_lines = ["I'm still hungry, no matter how much I eat.", "I can eat nonstop, is there something wrong with that?", "No matter how much I devour, my stomach is still empty. Am I still growing or something?", "You'll get heat fatigue if you don't eat properly.", "I wonder why I'm always so hungry. I'm not gaining much weight, so it's fine, but...", "I really do eat too much but I still manage to keep in shape, so....", "I've got a craving for sweets just now...", "I've had a huge appetite lately. If this continues then I might gain weight... This has to stop."]
            elif trait == "Slim":
                t_lines = ["I have a great figure, don't you think?", "No matter how much I eat, I never get fat. I'm so lucky with my body ♫"]
            elif trait == "Chubby":
                t_lines = ["I may be a bit chubby, but men like it.", "I thought about a diet, but I just can't resist fresh cupcakes ♫"]
            elif trait == "Scars":
                t_lines = ["I tried many doctors, but they all said that my scars cannot be healed. *sigh*"]
            elif trait == "Energetic":
                t_lines = ["I always was a good runner. I'm good at moving fast.", "I hate waiting, and I hate when people have to wait me."]
            elif trait == "Optimist":
                t_lines = ["They say I'm always cheerful. I just enjoy my life, that's all.", "Hey, do you know this one? <tells you an anecdote> A good one, eh?"]
            elif trait == "Pessimist":
                t_lines = ["It's not like I dislike jokes... I just don't find most of them funny enough.", "The world is cruel and unforgiving... You can't hide this truth behind jokes."]
            elif trait == "Aggressive":
                t_lines = ["They say I'm too hot-headed. But it's not my fault when they try to pick a fight with me!", "I smacked that rude shopkeeper the other day right in the face. Will teach him a lesson how to talk with customers."]
            elif trait == "Courageous":
                t_lines = ["Some my friends afraid of darkness, can you imagine that? Even as a child I was not afraid of it, or anything else.", "Don't move, you have a spider on your shoulder. <calmly removes it> Here."]
            elif trait == "Coward":
                t_lines = ["The other day I noticed a bug under my bed... <shudders>", "I dislike dark places. And night. Why? Because... because it's so dark that I cannot see a thing!"]
            elif trait == "Nerd":
                t_lines = ["As a child I liked to to read books more than to play with peers, so they teased me a lot. Nothing changed since then..."]
            elif trait == "Strange Eyes":
                t_lines = ["People often say that my eyes are unusual. What do you think of them?", "Do you like my eyes? As a child I was often teased because of them."]
            elif trait == "Long Legs":
                t_lines = ["It takes so much time to find the right dress, because there is never one with the right size.", "My legs are always in the way. It only helps if I need to reach something high."]
            elif trait == "Manly":
                t_lines = ["Do you like my muscles? It took a while to build them.", "Everyone should build [char.op]self some muscles for self-protection, don't you think?"]
            elif trait == "Lolita":
                t_lines = ["My body is so small, everyone think I'm still a child.", "Maybe I should drink more milk to grow up... What do you think?"]
            elif trait == "Alien":
                t_lines = ["This place is so strange. I don't think I'll ever get used to it completely.", "Everything was very different where I used to live. But... I like it here too."]
            elif trait == "Great Arse":
                t_lines = ["I notice men often staring at my ass. What's wrong with them?", "The other day I dropped my purse and bent down to pick it up. All the men in the street started to applaud me. It was sooo embarrassing!"]
            elif trait == "Not Human":
                t_lines = ["Some humans don't like my appearance. But I don't care.", "The other day they refused to serve me in that fancy cafe because I'm not human enough. Can you imagine that?!"]
            elif trait == "Homebody":
                t_lines = ["I like my home a lot. I don't understand all those travellers and adventurers.", "I think living every day as an ordinary girl is the ultimate happiness.", "I enjoy reading in the bath. It's nice to do in such a confined space."]
            elif trait == "Natural Follower":
                t_lines = ["I'm not a leader, I never wanted to be one. Too much responsibility."]
            elif trait == "Natural Leader":
                t_lines = ["People say I'm quite charismatic. I bet I'd be a good leader, don't you thing? <smiles>"]
            elif trait == "Well-mannered":
                t_lines = ["They say nothing costs so little and is valued so much as courtesy. I always keep that in mind."]
            elif trait == "Ill-mannered":
                t_lines = ["People often tell me that I lack politeness. Fucking hypocrites! I just say what I really think, nothing more."]
            elif trait == "Extremely Jealous":
                t_lines = ["Ohh, I don't want to talk about myself, but tell me about your latest 'conquers'!"]
            elif trait == "Half-Sister":
                if "Yandere" in char_traits:
                    t_lines = ["Now that I think about it, I spent more time with you than Mom and Dad.", "We used to play doctor and tear off each other's clothes, heh.", "We used to bathe together, so... you got to touch sister's body all over....", "Whenever we took a bath together, I used to wash your every nook and cranny. And I mean EVERY nook and cranny ♪"]
                elif "Impersonal" in char_traits:
                    t_lines = ["Do you remember how you used to pull pranks on me?", "I have always observed you. I know all there is to your character.", "I've known what kinds of sexual fetishes you have since a long time ago."]
                elif "Tsundere" in char_traits:
                    t_lines = ["We used to take a bath together back in the days, didn't we? Now...? B...but... hey! You know we shouldn't do that!", "You've always gone out of your way to protect your sister. I should thank you for that.", "I went overboard when I tried to discipline you back when we were little. To be honest, I'm sorry about that now.", "Remember that collection of dirty magazines you used to cherish? I was the one who threw them away. I am... still sorry about that."]
                elif "Dandere" in char_traits:
                    t_lines = ["We've been together since we were small... Have you had enough of it? Well, I'm still not tired of it yet.", "You've taught me all kinds of things since a long time ago... even perverted things.", "You used to play doctor with me all the time... You were so perverted, even back then."]
                elif "Kuudere" in char_traits:
                    t_lines = ["I used to be a crybaby? D-don't remind me of such things...", "M-my promise to marry you? T-there's no way I'd remember something like that!", "Getting engaged with my [hero.hs]... I only thought that was possible back when we're kids.", "You always protected me. Therefore, I decided that I had to become strong."]
                elif "Ane" in char_traits:
                    t_lines = ["Hehe, you've grown so much... That makes your sis proud.", "You weren't able to fall asleep without sis by your side when we were little.", "Whenever I wore a skirt, you always tried to peek underneath it... You were already so perverted when we were little.", "I've taken care of you since you were little. Therefore, sister knows everything about you.", "When we were younger, I was always by your side because I swore I would always protect you."]
                elif "Imouto" in char_traits:
                    t_lines = ["I used to think I'd get as tall as you.", "You remember we used to play shop when we were little? Wha... You should forget about THAT game!", "You have protected me from bullies when I was little.... That made me so happy."]
                elif "Kamidere" in char_traits:
                    t_lines = ["I decided that you'd be mine when I was still very little.", "You've belonged to sis ever since you were born.", "You're my [hero.hs] who I've personally helped to raise. There's no way I'd let you go."]
                elif "Bokukko" in char_traits:
                    t_lines = ["When we were little, didn't you say you'd make me your wife someday or something?", "When we were kids, we went exploring in the forest together and we both got lost.", "We used to climb fences and then jump off them. The two of us got injuries all over.", "You used to be so wee and now that huge, na?"]
                else:
                    t_lines = ["We used to bathe together a lot when we were little ♪", "The bath used to be our playground... but you tickled me way too much.", "When it was night time, you would always try to slip into my bed unnoticed.", "You used to tag along with me wherever I went when we were little."]
                t_lines.extend(["Do you miss our father? ...Yes, I miss him too.", "We should chat more often. We are family after all."])
            else:
                char_debug("Character gives no information about her/his trait: %s" % trait)
                continue
            lines.append(choice(t_lines))

        if "Combatant" in char.gen_occs:
            if "Shy" in char_traits or "Coward" in char_traits:
                lines.append(choice(["I have been trained in combat, but I really dislike violence.", "I know a lot about self-defense... but I really hope that I wouldn’t ever need to use it.", "I know how to use a weapon... but it still scares me a bit.", "I can do well in combat training, but in practice...", "They say that I may have the skill, but not the spirit of a warrior...", "I carry a weapon, but I don’t think I would have the heart to hurt someone."]))
            else:
                if "Virtuous" in char_traits:
                    lines.append(choice(["I know how to pacify someone without hurting them. That’s the right way to do it.", "I learned how to fight so I can protect others."]))
                if "Adventurous" in char_traits:
                    lines.append(choice(["I like to sharpen my battle skills.", "I enjoy exploring catacombs.", "A duel sounds interesting, do you mind?"]))
                lines.append(choice(["I have been trained in combat. So you better not be trying anything funny <grins>", "I may not look like it, but I can handle my weapons really well.", "Some creeps tried to ambush me once. I gave them plenty of time to repent at the infirmary.", "Sometimes I watch the matches in the arena to get inspiration to improve my own technique.", "It's better to know how to defend yourself in this town. You never know what may happen."]))
        else:
            if "Adventurous" in char_traits:
                lines.append(choice(["I always dreamed about my own adventures. But I never had a combat training, so... <sigh>"]))

        if "Caster" in char.gen_occs:
            lines.append(choice(["I like to study magic.", "Arcane arts are passion of mine", "Magic is so fascinating, I can't live without it!"]))

        if "Server" in char.gen_occs:
            lines.append(choice(["I'm just an ordinary worker, I guess.", "I work where I can. You can't be picky if you want to pay your bills."]))

        if "SIW" in char.gen_occs:
            lines.append(choice(["I enjoy sex, thus I enjoy my job <grins>", "I think there is nothing wrong with selling your body as long as you having fun and it's well paid."]))

    python hide:
        prefs = {"gold": [["I really hate that everything revolves around money in this city."],
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

        ch_prefs = char.preferences
        mod = len(STATIC_CHAR.PREFS) / float(len(ch_prefs))
        for k, v in prefs.iteritems():
            w = ch_prefs.get(k, 0)
            w *= mod
            if w < 20:
                lines.append(choice(v[0]))
            elif w > 80:
                lines.append(choice(v[1]))

        # if there is not enough specific answers, a vague one is added to the list
        if len(lines) < 3:
            lines.append(choice(["Hm? A little of this, a little of that?", "...I don't really have much to say.", "Nothing much, there's nothing worth mentioning.", "What I'm doing? The usual stuff...", "I'm just normal, I guess.", "I like just about anything.", "Hmm, there's not much to talk about.", "Now that I think about it... am I just boring?", "I'm just about average, I guess."]))

    $ iam.say_line(char, lines)

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
        $ iam.int_reward_exp(char)

    $ char.gfx_mod_stat("disposition", randint(5, 15))
    $ char.gfx_mod_stat("affection", affection_reward(char))

    $ iam.int_reward_exp(char)

    $ del lines, m, n
    jump girl_interactions

# ask about occupation
label interactions_aboutoccupation:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if iam.flag_count_checker(char, "flag_interactions_aboutoccupation") > 1:
        $ iam.refuse_too_many(char)
        $ char.gfx_mod_stat("disposition", -5)
        $ char.gfx_mod_stat("affection", -1)
        jump girl_interactions

    if char.get_stat("disposition") <= -250 and char.status == "free":
        $ char.gfx_mod_stat("disposition", -5)
        $ char.gfx_mod_stat("affection", -1)
        $ iam.refuse_interaction(char)
        jump girl_interactions

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
        options["Prostitute"] = ("I'm a fancy %s." % ("girl" if char.gender == "female" else "boy"), "I'm a merchant. And my merchandise is my beautiful body ♪", "I provide personal services. I mean very personal.", "I sell my love to those who need it.")
        options["Mage"] = ("I'm a magician.", "I have arcane energies at my command.", "I have a magical talent. It's very useful in many cases.")
        options["Warrior"] = ("I was trained to fight.", "I have combat training.", "I know how to fight.", "I know how to behave on the battlefield.")

        temp = [t.id for t in char.traits.basetraits]
        for base, values in options.iteritems():
            if base in temp:
                iam.say_line(char, values)
                temp.remove(base)

    $ iam.int_reward_exp(char, .15)

    jump girl_interactions

label interactions_interests:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if iam.check_for_minor_bad_stuff(char):
        jump girl_interactions
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_interests")
    $ n = 2 + iam.repeating_lines_limit(char)
    if m > n:
        if m > 1:
            $ iam.refuse_too_many(char)
        else:
            $ iam.refuse_talk_any(char)
        $ del m, n
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
        $ iam.refuse_interaction(char)
        jump girl_interactions

    $ lines = []
    python hide:
        char_traits = char.traits
        for trait in char_traits:
            trait = trait.id
            if trait == "Big Boobs":
                t_lines = ["She complains how a big chest spoils the posture. You sympathize with her, very convincingly and almost sincerely."]                
            elif trait == "Abnormally Large Boobs":
                t_lines = ["You vaguely remember your conversation, paying most of your attention to her amazing chest.", "She complains about high costs for the purchase of new bra. It appears that the fabric is not strong enough to withstand such loads. Without knowing what reaction she expected, you keep your poker face."]
            elif trait == "Small Boobs":
                t_lines = ["She starts a conversation about irrelevance of chest size. You carefully assent, trying to not piss her off."]
            elif trait == "Lesbian":
                t_lines = ["[char.pC] seems to know every detail when you talk about the body of other women."]
            elif trait == "Bisexual":
                t_lines = ["With [char.op] it is easy to find someone to talk about, because [char.p] is interested in both genders."]
            elif trait == "Fire":
                t_lines = ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of fire."]
            elif trait == "Water":
                t_lines = ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of water."]
            elif trait == "Air":
                t_lines = ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of air."]
            elif trait == "Earth":
                t_lines = ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of earth."]
            elif trait == "Darkness":
                t_lines = ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of darkness."]
            elif trait == "Light":
                t_lines = ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of light."]
            elif trait == "Electricity":
                t_lines = ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of electricity."]
            elif trait == "Ice":
                t_lines = ["Your conversation turns to magic, and [char.p] enthusiastically tells you the intricacies of dealing with the power of ice."]
            elif trait == "Neutral":
                t_lines = ["Your conversation turns to magic, but [char.p] seems uninterested in the topic."]
            elif trait == "Dawdler":
                t_lines = ["You have a lazy, indolent discussion. It looks like [char.p] is half asleep.", "[char.pC] pensively tells you about [char.pd] recent dreams. You begin to feel drowsy."]
            elif trait == "Frigid":
                t_lines = ["You try to steer the conversation to more intimate topics, but [char.p] appears completely uninterested."]
            elif trait == "Exhibitionist":
                t_lines = ["[char.pC] tells you pretty hot stories about [char.pd] exhibitionistic adventures in a local park."]
            elif trait == "Clumsy":
                t_lines = ["You talk about misfortunes caused by [char.pd] clumsiness. You heroically hold back a smile and comfort [char.op] instead."]
            elif trait == "Sexy Air":
                t_lines = ["You try to pay attention to what [char.p] says, but [char.pd] innocent movements keeps distracting you."]
            elif trait == "Nymphomaniac":
                t_lines = ["An innocent conversation turns into the discussion about sexual positions. [char.pC]'s really into this stuff.", "[char.pC] passionately talks about [char.pd] recent sexual adventures. Wow."]
            elif trait == "Virtuous":
                t_lines = ["[char.pC] tells about [char.pd] volunteer work. It's nice, but a bit boring."]
            elif trait == "Vicious":
                t_lines = ["[char.pC] gossips with obvious pleasure about [char.pd] acquaintance's misfortunes."]
            elif trait == "Sadist":
                t_lines = ["[char.pC] keeps surprising you with [char.pd] ideas, what [char.p] would do to certain people you both know."]
            elif trait == "Psychic":
                t_lines = ["It's difficult to participate in the conversation when your interlocutor knows your words in advance. [char.pC] seems to enjoy teasing you, however.", "[char.pC] complains about headaches, dizziness and other neural disorders that are common for psychics."]
            elif trait == "Serious":
                t_lines = ["You have a very serious conversation about local politics and taxes. You feel squeezed like a lemon.", "[char.pC] gives you a lecture about the importance of planning for the future. You heroically hold back a yawn."]
            elif trait == "Masochist":
                t_lines = ["[char.pC] explains how much [char.p] want to experience 'forbidden' situations even if it might appear unpleasant to others."]
            elif trait == "Athletic":
                t_lines = ["You discuss beach volleyball which became quite popular among local girls lately.", "You discuss places for swimming. It looks like most girls prefer beaches to pools because it's free."]
            elif trait == "Artificial Body":
                t_lines = ["Tempted by curiosity, you ask about [char.pd] artificial body. [char.pdC] explanations are very long and confusing.", "You discuss the regular maintenance required by [char.pd] body. It's a pretty complex, but piquant conversation."]
            elif trait == "Neat":
                t_lines = ["[char.pC] gives a long talk about how some people just leave a complete mess even after a short time."]
            elif trait == "Messy":
                t_lines = ["[char.pC] complains that people want [char.op] to clean up everything, even though they knew that [char.p] is going to come back later."]
            elif trait == "Heavy Drinker":
                t_lines = ["You discuss various types of alcohol, sharing your drinking experience."]
            elif trait == "Curious":
                t_lines = ["You exchange the latest news and gossip. [char.pC] really knows a lot about it."]
            elif trait == "Shy":
                t_lines = ["[char.pC] admits that [char.p] has troubles to open up and that [char.p] needs time to feel comfortable with others."]
            elif trait == "Elf":
                t_lines = ["[char.pC] talks about animals and the trees and how they live together."]
            elif trait == "Always Hungry":
                t_lines = ["You talk about food for some time. It looks like [char.p] can continue it for hours, so you carefully interrupt the conversation."]
            elif trait == "Slim":
                t_lines = ["You compliment [char.pd] figure and the conversation quickly turns toward healthy lifestyle. Ugh.", "[char.pC] brags about [char.pd] metabolism, allowing [char.op] to eat sweets and not get fat. You envy [char.op]."]
            elif trait == "Chubby":
                t_lines = ["You have a lively discussion about your favorite local bakeries and pastry shops.", "Your conversation turns toward cooking, and [char.p] shares some of [char.pd] recipes. They are all pretty high in calories..."]
            elif trait == "Scars":
                t_lines = ["She complains about how [char.pd] scars cause inconvenience. You comfort [char.op]."]
            elif trait == "Energetic":
                t_lines = ["While you have a conversation with [char.op], it seems [char.p] can not stand still."]
            elif trait == "Optimist":
                t_lines = ["It looks like [char.p] is in a good mood. Laughing and joking during your conversation, [char.p] quickly turns it into a humorous one.", "You exchange your freshest anecdotes."]
            elif trait == "Pessimist":
                t_lines = ["It looks like [char.p]'s not in the mood. Your conversation is pretty gloomy, though you managed to cheer [char.op] up a bit."]
            elif trait == "Aggressive":
                t_lines = ["[char.pC] tells you about the latest argument [char.p] had with other customers while waiting in the long line."]
            elif trait == "Courageous":
                t_lines = ["[char.pC] is baffled when you try to talk about the dangers in the wilderness.", "As you chat it turns out, that for [char.op], going to the catacombs is the same as going to shopping."]
            elif trait == "Coward":
                t_lines = ["You can see the fear in [char.pd] eyes as you talk about the catacombs, even though you are in the safety of the city."]
            elif trait == "Nerd":
                t_lines = ["You discuss new books in local stores and libraries.", "Somehow your conversation comes to board games, and [char.p] enthusiastically explains to you the intricate rules of one of them."]
            elif trait == "Strange Eyes":
                t_lines = ["[char.pC] notices how you look at [char.pd] unusual eyes. Embarrassed, [char.p] refuses to look at you or discuss anything."]
            elif trait == "Long Legs":
                t_lines = ["During your small conversation you can't help but glance at [char.pd] long legs. It looks like [char.p] is used to it and doesn't care much."]
            elif trait == "Manly":
                t_lines = ["[char.pC] gives you a lecture on how to build your muscles properly. You feel a bit offended, but keep your cool.", "[char.pC] casually remarks that you should exercise more often, and gives you some advice."]
            elif trait == "Lolita":
                t_lines = ["[char.pC] complains about how hard it is to find adult clothes for [char.pd] figure. You're trying to take [char.op] away from this sensitive topic.", "[char.pC] tells you funny stories about disappointed (and imprisoned) pedophiles confused by [char.pd] body size. What a strange topic."]
            elif trait == "Alien":
                t_lines = ["[char.pC] talks about [char.pd] homeland. You are listening with interest.", "You discuss local events [char.p] witnessed. [char.pC] doesn't understand the meaning of some of them, and you spend some of your time to explain."]
            elif trait == "Great Arse":
                t_lines = ["You try to keep it to small talk, trying not to think about [char.pd] gorgeous butt and what would you do if you were behind [char.op]."]
            elif trait == "Not Human":
                t_lines = ["[char.pC] talks about [char.pd] issues to fit in due to [char.pd] appearance."]
            elif trait == "Homebody":
                t_lines = ["[char.pC] talks about [char.pd] room, and how much time [char.p] spent decorating it."]
            elif trait == "Natural Follower":
                t_lines = ["[char.pC] is a good listener, so you have to do the talking (and questioning)."]
            elif trait == "Natural Leader":
                t_lines = ["You can not choose the topic during your conversation, because [char.p] wants to set the pace and direction."]
            elif trait == "Well-mannered":
                t_lines = ["You have a pleasant chat with [char.op]. [char.pC] knows when to listen and when to talk."]
            elif trait == "Ill-mannered":
                t_lines = ["You try to have a conversation with [char.op], but [char.p] keeps interrupting you."]
            elif trait == "Extremely Jealous":
                t_lines = ["[char.pC] inquires about your intimate relationships. You carefully dispel [char.pd] concern, trying not to make definitive statements."]
            elif trait == "Half-Sister":
                t_lines = ["You discuss your common father. The sad discussion quickly turns into a sarcastic one, when you try to count all his lovers and daughters.", "[char.pC] tells you about [char.pd] mother. You listen in silence, trying to imagine yours.", "You spend time together you reminiscing about fun and embarrassing moments from your childhood."]
            else:
                char_debug("Character does not talk about her/his trait: %s" % trait)
                continue
            lines.append(choice(t_lines))

        if "Combatant" in char.gen_occs:
            if "Shy" in char_traits or "Coward" in char_traits:
                lines.append(choice(["Even though [char.p] is trained in combat, [char.p] become silent whenever you try to ask about [char.pd] exploits in the wilderness."]))
            else:
                if "Virtuous" in char_traits:
                    lines.append(choice(["Tells you about how [char.p] saved someone from wild animals."]))
                if "Adventurous" in char_traits:
                    lines.append(choice(["[char.pC] talks about [char.pd] recent trips in the forest.", "[char.pC] tell you stories about the catacombs."]))
            lines.append(choice(["You discuss the recent fights at the arena and their participants.", "You discuss a variety of fighting styles."]))
        else:
            if "Adventurous" in char_traits:
                lines.append(choice(["When you talk about the recent gossips from the wilderness, [char.p] looks away with a dreamy eyes as if [char.p] would not pay attention."]))

        if "Caster" in char.gen_occs:
            lines.append(choice(["[char.pC] enthusiastically talks about mysteries of arcane arts.", "You discuss [char.pd] magical studies."]))

        if "Server" in char.gen_occs:
            lines.append(choice(["[char.pC] recounts rumors that [char.p] heard from customers lately. People tend to not notice service workers when they are not needed."]))

        if "SIW" in char.gen_occs:
            lines.append(choice(["You gossip about the strangeness of some of [char.pd] customers."]))

    # if there is not enough specific answers, a vague one is added to the list
    if len(lines) < 3:
        $ lines.append(choice(["You chat for some time."]))

    $ narrator(choice(lines))

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
        $ iam.int_reward_exp(char, .1)

    $ char.gfx_mod_stat("disposition", randint(10, 20))
    $ char.gfx_mod_stat("affection", affection_reward(char))

    $ iam.int_reward_exp(char, .15)

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

    $ del m, n, lines
    jump girl_interactions

# flirt
label interactions_flirt:
    if iam.check_for_bad_stuff(char):
        jump girl_interactions_end
    if iam.check_for_minor_bad_stuff(char):
        jump girl_interactions
    $ m = 1 + iam.flag_count_checker(char, "flag_interactions_flirt")
    $ n = 1 + iam.repeating_lines_limit(char)
    if m > n:
        if m > 1:
            $ iam.refuse_too_many(char)
        else:
            $ iam.refuse_talk_any(char)
        $ char.gfx_mod_stat("disposition", -randint(5, 15))
        $ char.gfx_mod_stat("affection", -randint(0, 2))
        if char.get_stat("joy") > 30:
            $ char.gfx_mod_stat("joy", -randint(2, 4))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
    elif char.get_stat("affection") <= 150 or char.get_stat("disposition") <= 50:
        $ char.gfx_mod_stat("disposition", -randint(5, 10))
        $ char.gfx_mod_stat("affection", -randint(0,2))
        $ char.gfx_mod_stat("joy", -randint(0, 1))
        if hero.get_stat("joy") > 70:
            $ hero.gfx_mod_stat("joy", -randint(0, 1))
        if char.status != "free":
            "You tried to flirt with [char.nickname]."
        $ iam.refuse_interaction(char)
    else:
        $ iam.accept_flirt(char)

        if 2*m <= n and dice(50) and dice(char.get_stat("joy")-40):
            $ narrator(choice(["You feel especially close."]))
            $ char.gfx_mod_stat("joy", randint(0, 1))
            $ char.gfx_mod_stat("affection", affection_reward(char))
            $ iam.int_reward_exp(char, .10)
            if hero.get_stat("joy") < 80:
                $ hero.gfx_mod_stat("joy", randint(0, 1))

        $ iam.int_reward_exp(char)

        $ char.gfx_mod_stat("disposition", randint(5, 15))
        $ char.gfx_mod_stat("affection", affection_reward(char))

    $ del m, n
    jump girl_interactions

# testing stuff
label interactions_disp:
    $ char.gfx_mod_stat("disposition", 250)
    $ char.gfx_mod_stat("affection", 250)
    jump girl_interactions

label interactions_becomefr:
    $ char.gfx_mod_stat("disposition", 500)
    $ char.gfx_mod_stat("affection", 500)
    $ set_friends(char)
    jump girl_interactions

label interactions_becomelv:
    $ char.gfx_mod_stat("disposition", 500)
    $ char.gfx_mod_stat("affection", 500)
    $ set_lovers(char)
    jump girl_interactions
