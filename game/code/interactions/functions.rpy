init -11 python:
    def select_girl_room(char, image): # selects room background for interactions, will be based on tiers too eventually
        image_tags = image.get_image_tags()
        if "no bg" in image_tags or "simple bg" in image_tags or "living" in image_tags:
            if char.status == "slave":
                if check_friends(hero, char) or check_lovers(char, hero):
                    return "bg girl_room_s1"
                else:
                    return "bg girl_room_s2"
            else:
                return "bg girl_room"
        elif "beach" in image_tags:
            return "bg city_beach"
        elif "pool" in image_tags:
            return "bg pool_lockers"
        elif "onsen" in image_tags:
            return "bg onsen"
        elif "indoors" in image_tags:
            if "public" in image_tags:
                return "bg city_bar"
            elif "dungeon" in image_tags:
                return "bg slave_market"
            else:
                return "bg girl_room"
        elif "outdoors" in image_tags:
            if "nature" in image_tags:
                if "urban" in image_tags:
                    return "bg city_park"
                else:
                    return "bg forest_3"
            elif "urban" in image_tags:
                return "bg main_street"
            else:
                return "bg wildness"
        else:
            return "bg girl_room"

    # Interactions (Girlsmeets Helper Functions):
    def interactions_influence(c):
        return ((hero.get_stat("charisma")*(1 + c.get_stat("disposition")/(3.0*c.get_max("disposition")))) - c.get_stat("character")) / (c.tier + 1) 

    def interactions_gender_mismatch(char, just_sex=True):
        if just_sex and ct("Open Minded"):
            return False
        if char.gender == "female":
            if hero.gender == "male":
                return ct("Lesbian") and not "Yuri Expert" in hero.traits
            else:
                return not (ct("Lesbian") or ct("Bisexual"))
        else:
            if hero.gender == "male":
                return not (ct("Gay") or ct("Bisexual"))
            else:
                return ct("Gay")

    def interactions_set_repeating_lines_limit(c): # returns the number of character "patience", ie how many repeating lines she's willing to listen in addition to default value
        global hero
        if check_lovers(c, hero):
            patience = 1
        else:
            patience = 0

        if "Well-mannered" in c.traits:
            patience += locked_random("randint", 0, 1)
        elif "Ill-mannered" in c.traits:
            patience -= locked_random("randint", 0, 1)

        if c.status == "slave":
            patience += 1
        patience += interactions_influence(c) / 20
        return patience

    def interactions_drinking_outside_of_inventory(char, count): # allows to raise activation count and become drunk without using real items
        char.up_counter("dnd_drunk_counter", count)
        if char.get_flag("dnd_drunk_counter", 0) >= 35 and not 'Drunk' in char.effects:
            char.enable_effect('Drunk')
        elif 'Drunk' in char.effects and char.AP > 0 and not 'Drinker' in char.effects:
            char.AP -= 1
        return

    def interactions_flag_count_checker(char, char_flag): # this function is used to check how many times a certain interaction was used during the current turn; every interaction should have a unique flag name and call this function after every use
        char_flag = "dnd_" + char_flag
        result = char.get_flag(char_flag, 0)
        char.set_flag(char_flag, result+1)
        return result

    def interactions_silent_check_for_bad_stuff(char): # we check issues without outputting any lines or doing something else, and just return True/False
        if "Food Poisoning" in char.effects:
            return False
        elif char.get_stat("vitality") <= char.get_max("vitality")/10:
            return False
        elif char.get_stat("health") < char.get_max("health")/5:
            return False
        elif (not("Pessimist" in char.traits) and char.get_stat("joy") <= 25) or (("Pessimist" in char.traits) and char.get_stat("joy") < 10):
            return False
        elif char.AP <= 0:
            return False
        else:
            return True

    def interactions_check_for_bad_stuff(char): # we check major issues when the character will refuse almost anything
        if "Food Poisoning" in char.effects:
            char.override_portrait("portrait", "indifferent")
            char.say(choice(["But [char.name] was too ill to pay any serious attention to you.", "But [char.pp] aching stomach completely occupies [char.pp] thoughts."]))
            char.restore_portrait()
            char.gfx_mod_stat("disposition", -randint(2, 5))
            renpy.jump("girl_interactions_end")
        elif char.get_stat("vitality") <= char.get_max("vitality")/10:
            char.override_portrait("portrait", "indifferent")
            char.say(choice(["But [char.name] was too tired to even talk.", "Sadly, [char.name] was not very happy that you interrupted [char.pp] rest.", "But [char.p] is simply too tired to pay any serious attention to you.", "Unfortunately [char.p] so tired [char.p] almost falls asleep on the move."]))
            char.restore_portrait()
            char.gfx_mod_stat("disposition", -randint(5, 10))
            char.mod_stat("vitality", -2)
            renpy.jump("girl_interactions_end")
        elif char.get_stat("health") < char.get_max("health")/5:
            char.override_portrait("portrait", "indifferent")
            char.say(choice(["But [char.name] is too wounded for that.", "But [char.pp] wounds completely occupy [char.pp] thoughts."]))
            char.restore_portrait()
            char.gfx_mod_stat("disposition", -randint(5, 15))
            char.mod_stat("vitality", -2)
            renpy.jump("girl_interactions_end")

    def interactions_check_for_minor_bad_stuff(char): # we check minor issues when character might refuse to do something based on dice
        if (not("Pessimist" in char.traits) and char.get_stat("joy") <= 25) or (("Pessimist" in char.traits) and char.get_stat("joy") < 10):
            if dice(interactions_influence(c)) and dice(80):
                narrator(choice(["It looks like [char.p] is in a bad mood, however you managed to cheer [char.op] up."]))
                char.gfx_mod_stat("disposition", 1)
                char.gfx_mod_stat("affection", affection_reward(char, .1))
                char.gfx_mod_stat("joy", randint(3, 6))
            else:
                narrator(choice(["It looks like [char.p] is in a bad mood today and not does not want to do anything."]))
                renpy.jump ("girl_interactions")
        elif "Down with Cold" in char.effects: #if she's ill, there is a chance that she will disagree to chat
            if dice(interactions_influence(c)) and dice(80):
                narrator(choice(["It looks like [char.p] is not feeling well today, however you managed to cheer [char.op] up a bit."]))
                char.gfx_mod_stat("disposition", 2)
                char.gfx_mod_stat("affection", affection_reward(char, .2))
                char.gfx_mod_stat("joy", randint(1, 5))
            else:
                narrator(choice(["[char.pC] is not feeling well today and not in the mood to do anything."]))
                renpy.jump ("girl_interactions")
        elif char.get_stat("vitality") <= char.get_max("vitality")/5 and dice (35):
            char.override_portrait("portrait", "tired")
            if ct("Impersonal"):
                rc("I don't have required endurance at the moment. Let's postpone it.", "No. Not enough energy.")
            elif ct("Shy") and dice(50):
                rc("W-well, I'm a bit tired right now... Maybe some other time...", "Um, I-I don't think I can do it, I'm exhausted. Sorry...")
            elif ct("Imouto"):
                rc("Noooo, I'm tired. I want to sleep.", "Z-z-z *she falls asleep on the feet*")
            elif ct("Dandere"):
                rc("No. Too tired.", "Not enough strength. I need to rest.")
            elif ct("Tsundere"):
                rc("I must rest at first. Can't you tell?", "I'm too tired, don't you see?! Honestly, some people...")
            elif ct("Kuudere"):
                rc("I'm quite exhausted. Maybe some other time.", "I really could use some rest right now, my body is tired.")
            elif ct("Kamidere"):
                rc("I'm tired, and have to intentions to do anything but rest.", "I need some rest. Please don't bother me.")
            elif ct("Bokukko"):
                rc("Naah, don't wanna. Too tired.", "*yawns* I could use a nap first...")
            elif ct("Ane"):
                rc("Unfortunately I'm quite tired at the moment. I'd like to rest a bit.", "Sorry, I'm quite sleepy. Let's do it another time.")
            elif ct("Yandere"):
                rc("Ahh, my whole body aches... I'm way too tired.", "The only thing I can do properly now is to take a good nap...")
            else:
                rc("*sign* I'm soo tired lately, all I can think about is a cozy warm bed...", "I am ready to drop. Some other time perhaps.")
            char.restore_portrait()
            char.gfx_mod_stat("disposition", -randint(0, 1))
            char.mod_stat("vitality", -randint(1, 2))
            renpy.jump("girl_interactions")

    def interactions_checks_for_bad_stuff_greetings(char): # Special beginnings for greetings if something is off, True/False show that sometimes we even will need to skip a normal greeting altogether
        if "Food Poisoning" in char.effects:
            char.override_portrait("portrait", "indifferent")
            char.say("She does not look good...")
            char.restore_portrait()
            return True
        elif char.get_stat("vitality") <= 40:
            char.override_portrait("portrait", "indifferent")
            char.say("She looks very tired...")
            char.restore_portrait()
            return True
        elif char.get_stat("health") < char.get_max("health")/5:
            char.override_portrait("portrait", "indifferent")
            char.say("She does not look good...")
            char.restore_portrait()
            return True
        elif "Down with Cold" in char.effects:
            char.override_portrait("portrait", "indifferent")
            char.say("She looks a bit pale...")
            char.restore_portrait()
            return False
        elif char.get_stat("joy") <= 25:
            char.override_portrait("portrait", "sad")
            char.say("She looks pretty sad...")
            char.restore_portrait()
            return False
        else:
            return False

    def rc(*args):
        """
        random choice function
        Wrapper to enable simpler girl_meets choices, returns whatever char_gm is set to along with a random line.
        """
        # https://github.com/Xela00/PyTFall/issues/37
        return char.say(choice(list(args)))

    def rts(girl, options):
        """
        Get a random string from a random trait that a girl has.
        girl = The girl to check the traits against.
        options = A dictionary of trait/eval -> (strings,).
        """
        default = options.pop("default", None)
        available = list()

        for trait in options.iterkeys():
            if trait in traits:
                if traits[trait] in girl.traits: available.append(options[trait])
            else:
                if eval(trait, globals(), locals()): available.append(options[trait])

        if not available: trait = default
        else: trait = choice(available)

        if isinstance(trait, (list, tuple)): return choice(trait)
        else: return trait

    def ec(d):
        # Not used atm.
        """
        Expects a dict of k/v pairs as argument. If key is a valid trait, the function will check if character has it.
        Else, the key will be evaluated and value added to the choices.
        This will return a single random choice from all that return true (traits and evals).
        """
        l = list()
        for key in d:
            if key in traits:
                if key in char.traits:
                    l.extend(d[key])
            else:
                if eval(key):
                    l.extend(d[key])
        # raise Exception, l
        if l:
            g(choice(l))
            return True
        else:
            return False

    def ct(*args):
        """
        Check traits function.
        Checks is character in girl_meets has any trait in entered as an argument.
        """
        l = list(args)
        return any(i.id in l for i in char.traits)

    def ctchar(char, *args):
        """
        Check traits function.
        Checks is character in girl_meets has any trait in entered as an argument. Goes with char argument, thus can be used where the game doesn't recognize default "char"
        """
        l = list(args)
        return any(i.id in l for i in char.traits)

    def co(*args):
        """
        Check occupation
        Checks if any of the occupations belong to the character.
        """
        return ct(*args)

    def cgo(*args):
        """
        Checks for General Occupation strings, such as "SIW", "Combatant", "Server", etc.
        """
        gen_occs = set()
        for occ in char.traits:
            if hasattr(occ, "occupations"):
                gen_occs.update(occ.occupations)
        return any(i for i in list(args) if i in gen_occs)

    def cgochar(char, *args):
        """
        Checks for General Occupation strings, such as "SIW", "Combatant", "Server", etc. Goes with char argument, thus can be used where the game doesn't recognize default "char"
        """
        gen_occs = set()
        for occ in char.traits:
            if hasattr(occ, "occupations"):
                gen_occs.update(occ.occupations)
        return any(i for i in list(args) if i in gen_occs)

    # Relationships:
    def check_friends(*args):
        for i in args:
            for z in args:
                if i != z and not i.is_friend(z):
                    return False
        return True

    def set_friends(*args):
        for i in args:
            for z in args:
                if i != z:
                    i.friends.add(z)

    def end_friends(*args):
        for i in args:
            for z in args:
                if i != z and z in i.friends:
                    i.friends.remove(z)

    def check_lovers(*args):
        for i in args:
            for z in args:
                if i != z and not i.is_lover(z):
                    return False
        return True

    def set_lovers(*args):
        for i in args:
            for z in args:
                if i != z:
                    i.lovers.add(z)

    def end_lovers(*args):
        for i in args:
            for z in args:
                if i != z and z in i.lovers:
                    i.lovers.remove(z)

    # Other:
    def find_les_partners():
        """
        Returns a set with if any partner(s) is available and willing at the location.
        (lesbian action)
        *We can move this to GM class and have this run once instead of twice! (menu + label)
        """
        char = store.char

        # First get a set of all girls at the same location as the current character:
        partners = set()
        for i in chars.values():
            if char == i:
                continue
            if set([i.home, i.workplace]).intersection([char.home, char.workplace]):
                partners.add(i)

        # Next figure out if disposition of possible partners towards MC is
        # high enough for them to agree and/or they are lovers of char.
        willing_partners = set()
        for i in partners:
            if not (check_lovers(i, hero) or check_lovers(char, i)):
                continue
            if i.get_stat("vitality") < 25 or i.get_stat("health") < i.get_max("health")*3/5:
                continue
            if i.get_stat("affection") > -50:
                willing_partners.add(i)

        return willing_partners

    def interactions_run_gm_anywhere(char, exit, background, custom=False):
        """
        Runs (or doesn't) gm or interactions with the char based on her status; place is where we jump after gm is over.

        Keyword arguments:
        custom -- Will not jump to any label internally (default False)
        """
        if not isinstance(char, Char):
            char = chars[char]

        if custom:
            gm.start("custom", char, char.get_vnsprite(), exit, background)
        elif chars[char].status == "slave" or not char.is_available:
            narrator("Nobody's here...")
            renpy.jump(place)
        elif char in hero.chars:
            gm.start("girl_interactions", char, char.get_vnsprite(), exit, background)
        else:
            gm.start("girl_meets", char, char.get_vnsprite(), exit, background)

    def interactions_prebattle_line(characters):
        """
        Outputs nonrepeatable prebattle lines for provided characters, except hero if s/he was provided.
        """
        characters = [c for c in characters if c != hero]
        if characters:
            said_lines = set()
            for character in characters:
                if "Impersonal" in character.traits:
                    lines = ["Target acquired, initialising battle mode.", "Enemy spotted. Engaging combat.", "Battle phase, initiation. Weapons online.", "Better start running. I'm afraid I can't guarantee your safety.", "Enemy analysis completed. Switching to the combat routine.", "Target locked on. Commencing combat mode."]
                elif "Imouto" in character.traits:
                    lines = ["Ahaha, we'll totally beat you up!", "Behold of my amazing combat techniques, [mc_ref]! ♪", "All our enemies will be punished! ♫", "Activate super duper mega ultra assault mode! ♪", "Huh? Don't they know we're too strong for them?"]
                elif "Dandere" in character.traits:
                    lines = ["Want to fight? We'll make you regret it.", "Let's end this quickly, [mc_ref]. We have many other things to do.", "Of course we'll win.", "This will be over before you know it.", "If something bad happens to the enemy, don't blame me."]
                elif "Tsundere" in character.traits:
                    lines = ["Well-well. It looks like we have some new targets, [mc_ref] ♪", "Hmph! You're about 100 years too early to defeat us!", "We won't go easy on you!", "There's no way you could win!", "[mc_ref], you can stay back if you wish. I'll show you how it's done.", "I won't just defeat you, I'm gonna shatter you!"]
                elif "Kuudere" in character.traits:
                    lines = ["Oh, you dare to stand against us?", "Fine, we accept your challenge. Let's go, [mc_ref].", "Don't worry, [mc_ref]. This battle will be over soon enough.", "Are you prepared to know our power?", "You picked a fight with the wrong girl."]
                elif "Kamidere" in character.traits:
                    lines = ["Get ready, [mc_ref]. We have some lowlife to crash.", "So you want us to teach you some manners, huh?", "You have made a grave error challenging us. Retreat while you can.", "Time to take out the trash.", "You should leave this place and cower in your home. That is the proper course for one so weak.", "You need to be put back in your place."]
                elif "Bokukko" in character.traits:
                    lines = ["Wanna throw hands, huh? Better be ready to catch them!", "I'm gonna beat you silly! Cover me, [mc_ref]!", "You wanna go? Alrighty, eat some of this!", "Time to kick some ass.", "I'm gonna whack you good!", "All right, let's clean this up fast!"]
                elif "Ane" in character.traits:
                    lines = ["Don't worry, [mc_ref]. I'll protect you.", "Can't say I approve of this sort of thing, but we are out of options, [mc_ref].", "Don't feel sorry for them, [mc_ref]. They asked for it.", "We mustn't let our guard down, [mc_ref]."]
                elif "Yandere" in character.traits:
                    lines = ["Please stand aside, [mc_ref]. Or you'll get blood on you...", "Do not worry. The nothingness is gentle ♪", "Here comes the hurt!", "This could get a little rough... Because I like it rough ♫", "Mind if I go a little nuts, [mc_ref]?"]
                else:
                    lines = ["I suppose we have to use force, [mc_ref]. I'll cover you.", "Alright then. If you want a fight, we'll give it to you!", "Ok, let's settle this.", "I'll fight to my last breath!"]
                result = random.sample(set(lines).difference(said_lines), 1)[0]
                said_lines.add(result)
                result = result.replace("[mc_ref]", character.mc_ref)
                character.override_portrait("portrait", "confident")
                character.say(result)
                character.restore_portrait()

    def interactions_eating_line(characters):
        """
        Outputs nonrepeatable lines during eating for provided characters, except hero if s/he was provided.
        """
        characters = [c for c in characters if c != hero]
        if characters:
            said_lines = set()
            for character in characters:
                if "Impersonal" in character.traits:
                    lines = ["It's all sticky from the sauce... Nn... *chu* Mm... *slurp*", "Nn... mm... Delicious...", "That looks tasty... *slurp*"]
                elif "Shy" in character.traits and dice(50):
                    lines = ["That looks so good! Ah! That one looks good too... Aww, I can't decide...", "Hehe, sweet tea is so calming, isn't it?", "Uhm, w-were you going to eat that? Er... Y-yes, I'll eat it..."]
                elif "Imouto" in character.traits:
                    lines = ["Custard here and chocolate here. Looks delicious, doesn't it? ♪", "So many sweets! What should I start with? ♪", "Oh, that looks yummy... Diggin' in! Nom!"]
                elif "Dandere" in character.traits:
                    lines = ["*munch munch*... Huh? You want some too? Here.", "Omelette rolls are so sweet and sticky...", "Munch munch... Sugar intake is important.", "Thanks for the food... *munch*"]
                elif "Tsundere" in character.traits:
                    lines = ["Ah, I'm tired from eating too much...", "How long do you plan on staring at my lunch? I'm not sharing any.", "Lately, I am worrying quite a bit about calories... But I just can't help myself... ugh..."]
                elif "Kuudere" in character.traits:
                    lines = ["Mmm, this is actually pretty good.", "They don't have any teacakes today..? A pity.", "You've got a good appetite. It's refreshing to see.", "I don't need any... Well, if you insist... *aaaah*..."]
                elif "Kamidere" in character.traits:
                    lines = ["OK, say ah~n... Yeah right, like I would ever do such a thing.", "Can't you just be quiet and eat? It's improper.", "Don't talk to me when I'm eating."]
                elif "Bokukko" in character.traits:
                    lines = ["Hm, which one tastes better... I wonder...", "Nom nom... Mmm, delishus ♪ Back to full health ♪", "Mm, delicious meat. The meatiest of meats. Om nom.", "Let's dig in! Ehehe, egg omelet, egg omelet ♪"]
                elif "Ane" in character.traits:
                    lines = ["This kind of food is good for your health, you know? It'll fill you with lots of energy ♪", "You don't get to be picky. Come, say aaa... ♪", "Now, why don't we have an enjoyable meal?"]
                elif "Yandere" in character.traits:
                    lines = ["...Here, have this too. I'm finished.", "Mmm... Vanilla milkshakes are the best ♪", "I've been gaining weight, so I'm holding back today... Haah...", "Just go ahead and order whatever. I'll leave it up to you."]
                else:
                    lines = ["This place's tea and cake is amazing. The tarts are good, too.", "Ah, that looks yummy ♪", "Let's eaaaat! But, what should I eat first? Hmm..."]
                result = random.sample(set(lines).difference(said_lines), 1)[0]
                said_lines.add(result)
                result = result.replace("[mc_ref]", character.mc_ref)
                character.override_portrait("portrait", "indifferent")
                character.say(result)
                character.restore_portrait()

    def interactions_eating_propose(character):
        """
        Outputs a line before eating for provided character
        """
        if "Impersonal" in character.traits:
            lines = ["Let's have some tea.", "Hey, I was thinking about grabbing a bite.", "How about lunch?"]
        elif "Shy" in character.traits and dice(50):
            lines = ["H-hey, how about a cup of tea?", "I was just thinking about eating something...", "It's lunch time... S-so maybe we..."]
        elif "Imouto" in character.traits:
            lines = ["I really want some sweets ♪ C'mon!", "My tummy's growling. Wanna grab a bite?", "Woo! Lunch time, lunch time! Hurry!"]
        elif "Dandere" in character.traits:
            lines = ["Snack time?", "Want to have a snack?", "Lunch..?"]
        elif "Tsundere" in character.traits:
            lines = ["C-come on, invite me for tea or something.", "Hey... Do you want to grab some food? O-Or something?", "Y-you're going to join me for lunch... okay?"]
        elif "Kuudere" in character.traits:
            lines = ["Would you like to have some tea together?", "Let's get something to eat.", "Are you hungry? How about lunch?"]
        elif "Kamidere" in character.traits:
            lines = ["I think it's time for tea.", "Are you hungry? I was thinking about eating.", "Let's eat, I'm hungry."]
        elif "Bokukko" in character.traits:
            lines = ["Hey, let's have a snack, alright?", "Let's eat something! I'm starved!", "It's time to eat! Come on, let's go!"]
        elif "Ane" in character.traits:
            lines = ["Shall we sip some drinks and take it easy?", "What would you say to a cup of tea with me?", "Would you like to join me for lunch?"]
        elif "Yandere" in character.traits:
            lines = ["Do you want to take a tea break?", "Hey, aren't you hungry? Want to go get something to eat?", "If you'd like, we could have lunch?"]
        else:
            lines = ["Hey, you got some snacks or something? I'm kinda hungry.", "Shall we take a break? I'm hungry.", "Aaah, I'm hungry... What about you?"]
        result = random.choice(lines)
        character.override_portrait("portrait", "indifferent")
        character.say(result)
        character.restore_portrait()

    def interactions_pick_background_for_fight(place):
        """
        Returns suitable background for battles in various locations. Can be used together with gm.label_cache as a place.
        """
        if "park" in place:
            n = randint(1,4)
            back = "content/gfx/bg/be/b_park_" + str(n) + ".webp"
        elif "beach" in place:
            n = randint(1,3)
            back = "content/gfx/bg/be/b_beach_" + str(n) + ".webp"
        elif "forest" in place or "mage" in place:
            n = randint(1,8)
            back = "content/gfx/bg/be/b_forest_" + str(n) + ".webp"
        elif "village" in place:
            back = "content/gfx/bg/be/b_village_1.webp"
        elif "grave" in place:
            back = "content/gfx/bg/be/b_grave_1.webp"
        elif "academy" in place:
            back = "content/gfx/bg/be/b_academy_1.webp"
        elif "arena" in place:
            back = "content/gfx/bg/be/battle_arena_1.webp"
        elif "tavern" in place:
            back = "content/gfx/bg/be/b_tavern_1.webp"
        else:
            n = randint(1,6)
            back = "content/gfx/bg/be/b_city_" + str(n) + ".webp" # city streets are default backgrounds; always used for hired chars from the characters menu atm.
        return back
