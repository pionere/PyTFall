init -2 python:
    # Utility funcs to alias otherwise long command lines:
    def register_gossip(*args, **kwargs):
        """
        Registers a new gossip in an init block (and now in labels as well!).
        """
        gossip = WorldGossip(*args, **kwargs)
        if hasattr(store, "iam"):
            wg = iam.world_gossips
        else:
            wg = world_gossips
        wg.append(gossip)

    def stop_gossip(gossip_id):
        iam.world_gossips.stop_gossip(gossip_id)

    class WorldGossip(_object):
        def __init__(self, id, func, dice):
            self.id = id
            self.func = func
            self.dice = dice

    class WorldGossipsManager(_object):
        def __init__(self, data):
            """
            Creates the manager and copies the pre-existsing gossips into itself.
            """
            self.gossips = deepcopy(data)

        def get_gossip(self):
            gossips = [g for g in self.gossips if dice(g.dice)]
            if gossips:
                return choice(gossips)

        def stop_gossip(self, gossip_id):
            for g in self.gossips:
                if g.id == gossip_id:
                    self.gossips.remove(g)
                    break

    # Interactions (Girlsmeets Helper Functions):
    class InteractionsHelper(_object):
        @staticmethod
        def select_char_room(char):
            if char.status == "slave":
                if check_friends(char) or check_lovers(char):
                    return "girl_room_s1"
                else:
                    return "girl_room_s2"
            else:
                return "girl_room"

        @staticmethod
        def select_char_location(char, image_tags): # selects room background for interactions
            # select bg based on the location-tags
            if "beach" in image_tags:
                return "city_beach"
            elif "pool" in image_tags:
                return "pool_lockers"
            elif "onsen" in image_tags:
                return "onsen"
            elif "living" in image_tags:
                pass #return iam.select_char_room(char)
            elif "indoors" in image_tags:
                if "public" in image_tags:
                    return "city_bar"
                elif "dungeon" in image_tags:
                    return "slave_market"
                else:
                    pass # return iam.select_char_room(char)
            elif "outdoors" in image_tags:
                if "nature" in image_tags:
                    if "urban" in image_tags:
                        return "city_park"
                    else:
                        return "forest_%d" % randint(1, 4)
                elif "urban" in image_tags:
                    return "main_street"
                else:
                    return "wildness"
            elif "urban" in image_tags:
                return "main_street"
            elif "wildness" in image_tags:
                return "wildness"
            elif "suburb" in image_tags:
                return "hiddenvillage_alley"
            elif "stage" in image_tags:
                return "stage"
            elif "public" in image_tags:
                return "city_bar"
            elif "nature" in image_tags:
                return "forest_%d" % randint(1, 4)
            elif "dungeon" in image_tags:
                return "slave_market"
            elif "no bg" in image_tags or "simple bg" in image_tags:
                # no location information -> try to select location based on the clothes
                if "swimsuit" in image_tags:
                    return "city_beach"
                if "sportswear" in image_tags:
                    return "city_park"
                if "formal" in image_tags:
                    return "main_street"
                if "ninja" in image_tags or "armor" in image_tags or "miko" in image_tags:
                    return "arena_outside"
                if "yukata" in image_tags:
                    return "onsen"
                if "nurse" in image_tags:
                    return "infirmary"
                if "schoolgirl" in image_tags:
                    return "academy_town"
                #if "lingerie" in image_tags or "indoor" in image_tags or "no clothes" in image_tags:
                #    return iam.select_char_room(char)
                # TODO "everyday", "transformed", "cosplay", "ripped", "revealing", "cow", "cat", "bunny", "dog", "maid", "after sex" ?
            # last fall-back -> in her/his room
            return iam.select_char_room(char)

        @staticmethod
        def select_background_for_fight(place):
            """
            Returns suitable background for battles in various locations. Can be used together with iam.label_cache as a place.
            """
            if "park" in place:
                n = randint(1, 4)
                back = "content/gfx/bg/be/b_park_" + str(n) + ".webp"
            elif "beach" in place:
                n = randint(1, 3)
                back = "content/gfx/bg/be/b_beach_" + str(n) + ".webp"
            elif "forest" in place or "mage" in place:
                n = randint(1, 8)
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
                n = randint(1, 6)
                back = "content/gfx/bg/be/b_city_" + str(n) + ".webp" # city streets are default backgrounds; always used for hired chars from the characters menu atm.
            return back

        @staticmethod
        def select_beach_img_tags(char, location="beach"):
            """Selects and returns a suitable image when the player meets a character on the beach.
            """
            if location == "beach_cafe":
                clothes = [("swimsuit", 4), (None, 5)]
                locations = [("outdoors", 0), ("beach", 1), ("no bg", 2), ("simple bg", 3), (None, 6)]
            else:
                clothes = [("swimsuit", 3), (None, 4)]
                locations = [(location, 0), ("no bg", 1), ("simple bg", 2), (None, 5)]
            return char.show("girlmeets", clothes, locations, type="ptls", label_cache=True, gm_mode=True)

        @staticmethod
        def get_single_sex_picture(char, act="stripping", location="any", hidden_partner=False):
            """A universal function that selects most suitable sex picture depending on arguments.
            char - character id
            act - sex act; list of possible acts can be seen in the first check here
            location - location where is happens; the function supports following locations: park, forest, beach, room, any (aka simple bg/no bg)
            all other cases are too rare anyway, and should be handled manually
            hidden_partner - should it try to show the hidden partner pictures first, or it doesn't matter; doesn't work for strip and after_sex, obviously
            """
            # prepare excludeds
            excluded = ["in pain", "scared", "angry", "sad", "rape", "forced", "group"]

            # prepare for location
            loc_tag = location
            optional_included = []
            if location == "room":
                loc_tag = "living"
            elif location == "beach":
                if dice(50):
                    optional_included = [("swimsuit", None)]
            elif location == "park":
                loc_tag = "nature"

                excluded.extend(["beach", "wildness"])
            elif location == "forest":
                loc_tag = "nature"
                excluded.extend(["beach", "urban"])

            if act == "stripping":
                # try to find a stripping image
                excluded.extend(["sleeping", "bathing", "stage", "sex"])
                iam.set_img(("stripping", "lingerie", "nude"), (loc_tag, "no bg", "simple bg"), *optional_included, exclude=excluded, type="ptls")

            elif act == "masturbation":
                excluded.extend(["sleeping", "bathing", "stage", "sex"])
                iam.set_img(("masturbation", "lingerie", "nude"), (loc_tag, "no bg", "simple bg"), *optional_included, exclude=excluded, type="ptls")

            else: # any 2c/bc sexual act
                # partner filters
                if char.gender == hero.gender:
                    excluded.append("straight")
                else:
                    excluded.append("gay")
                if hidden_partner:
                    optional_included.append(("partnerhidden", None))
                else:
                    optional_included.append(("sexwithmc", None))

                iam.set_img((act, "after sex", "lingerie", "nude"), (loc_tag, "no bg", "simple bg"), *optional_included, exclude=excluded, type="ptls")

        @staticmethod
        def get_picture_before_sex(char=None, location="room"): # here we set initial picture before the scene begins depending on location
            excluded = ["sex", "sleeping", "angry", "in pain", "sad", "scared", "bathing"]
            # prepare for location
            loc_tag = location
            underwear = "lingerie"
            if location == "room":
                loc_tag = "living"
            elif location == "beach":
                underwear = "swimsuit"
            elif location == "park":
                loc_tag = "nature"
                excluded.extend(["beach", "wildness"])
            elif location == "forest":
                loc_tag = "nature"
                excluded.extend(["beach", "urban"])

            iam.set_img((loc_tag, "no bg", "simple bg"), (underwear, "nude"), exclude=excluded, type="ptls")

        @staticmethod
        def get_character_libido(char, mc=True): # depending on character traits returns relative libido level, ie how much the character wishes to have sex with MC
        # has nothing to do with character's willingness to even start sex; if mc = false then we calculate it not for mc, ie ignore some personal traits
        # it's more or less permanent pseudostat compared to many other games where it changes regularly like health, if not more often
            l = locked_random("randint", 3, 5)
            if "Nymphomaniac" in char.traits:
                l += 2
            elif "Frigid" in char.traits:
                l -= 1

            if mc:
                if iam.incest(char):
                    if char.get_stat("affection") >= 700:
                        l += locked_random("randint", 1, 2)
                    else:
                        l -= 1
                if check_lovers(char):
                    l += 1

            if l < 3 and "SIW" in char.gen_occs: # sex workers can't have it less than 3 though
                l = 3

            if "Virgin" in char.traits: # or 2 if virgins...
                l -= 1

            if l < 1:
                l = 1 # normalization, in general libido can be from 1 to 7 for frigid ones and from 3 to 10 for nymphomaniacs
            return l

        @staticmethod
        def get_character_wishes(char): # for taking action during sex scenes, returns action that character is willing to commit on her own
            skills = ["sex", "oral"]
            if hero.gender == "male":
                skills.append("anal")
                if char.gender == "female" and ((char.status != "slave" and check_lovers(char)) or "Virgin" not in char.traits):
                    skills.append("vaginal")
            skills = [[t, char.get_skill(t)] for t in skills]
            result = weighted_sample(skills)
            if not result:
                result = choice(skills)[0]

            # convert skills to acts
            if result == "sex":
                result = choice(["hand", "foot"])
            elif result == "oral":
                if hero.gender == "male":
                    result = choice(["blow", "tits"])
                else:
                    result = "blow"
            elif result == "vaginal":
                result = "vag"
            return result

        @staticmethod
        def slave_siw_check(c): # slaves-SIWs allow more than other characters
            return c.status == "slave" and ("SIW" in c.gen_occs) and c.get_stat("disposition") >= -150

        @staticmethod
        def hero_influence(c):
            # TODO check_friends/check_lovers?
            result = hero.get_stat("charisma")*(1 + c.get_stat("disposition")/(3.0*c.get_max("disposition")))
            result = (result - c.get_stat("character")) / (c.tier + 1)
            if "Drunk" in c.effects:
                result *= 1.1
            return result 

        @staticmethod
        def gender_mismatch(char, just_sex=True):
            if just_sex and "Open Minded" in char.traits:
                return False
            if char.gender == "female":
                if hero.gender == "male":
                    return "Lesbian" in char.traits and not "Yuri Expert" in hero.traits
                else:
                    return not ("Lesbian" in char.traits or "Bisexual" in char.traits)
            else:
                if hero.gender == "male":
                    return not ("Gay" in char.traits or "Bisexual" in char.traits)
                else:
                    return "Gay" in char.traits

        @staticmethod
        def incest(char):
            return "Half-Sister" in char.traits and "Sister Lover" not in hero.traits

        @staticmethod
        def repeating_lines_limit(c):
            # returns the number of character "patience", ie how many repeating lines she's willing to listen in addition to default value
            if check_lovers(c):
                patience = 1
            else:
                patience = 0

            if "Well-mannered" in c.traits:
                patience += locked_random("randint", 0, 1)
            elif "Ill-mannered" in c.traits:
                patience -= locked_random("randint", 0, 1)

            if c.status == "slave":
                patience += 1
            patience += iam.hero_influence(c) / 20
            return patience

        @staticmethod
        def drinking_outside_of_inventory(char, count):
            # allows to raise activation count and become drunk without using real items
            char.up_counter("dnd_drunk_counter", count)
            if char.get_flag("dnd_drunk_counter", 0) >= (45 if "Heavy Drinker" in char.traits else 30) and not 'Drunk' in char.effects:
                char.enable_effect('Drunk')
            elif 'Drunk' in char.effects and not 'Drinker' in char.effects:
                char.take_ap(1)

        @staticmethod
        def flag_count_checker(char, char_flag):
            # this function is used to check how many times a certain interaction was used during the current turn;
            #  every interaction should have a unique flag name and call this function after every use
            char_flag = "dnd_" + char_flag
            result = char.get_flag(char_flag, 0)
            char.set_flag(char_flag, result+1)
            return result

        @staticmethod
        def silent_check_for_bad_stuff(char):
            # we check issues without outputting any lines or doing something else, and just return True/False
            for e in char.effects:
                if e in ["Food Poisoning", "Depression", "Exhausted"]:
                    return False
            if char.get_stat("vitality") <= char.get_max("vitality")/10:
                return False
            if char.get_stat("health") < char.get_max("health")/5:
                return False
            joy = char.get_stat("joy")
            if joy < 10 or ("Pessimist" not in char.traits and joy <= 25):
                return False
            return True

        @staticmethod
        def silent_check_for_escalation(char, base):
            # check if the character is willing to fight the player
            if "Combatant" not in char.gen_occs:
                return False
            if not iam.silent_check_for_bad_stuff(char):
                return False
            if char.PP < 200: # PP_PER_AP
                return False
            if "Aggressive" in char.traits:
                base *= 2
            return dice(base)

        @staticmethod
        def check_for_bad_stuff(char):
            # we check major issues when the character will refuse almost anything
            if "Food Poisoning" in char.effects:
                char.override_portrait("portrait", "indifferent")
                char.say(choice(["But %s was too ill to pay any serious attention to you." % char.name, "But %s aching stomach completely occupies %s thoughts." % (char.pd, char.pd)]))
                char.restore_portrait()
                char.gfx_mod_stat("disposition", -randint(2, 5))
                return True
            elif char.get_stat("vitality") <= char.get_max("vitality")/10:
                char.override_portrait("portrait", "indifferent")
                char.say(choice(["But %s was too tired to even talk." % char.name, "Sadly, %s was not very happy that you interrupted %s rest." % (char.name, char.pd), "But %s is simply too tired to pay any serious attention to you." % char.p, "Unfortunately %s so tired %s almost falls asleep on the move." % (char.p, char.p)]))
                char.restore_portrait()
                char.gfx_mod_stat("disposition", -randint(5, 10))
                char.mod_stat("vitality", -2)
                return True
            elif char.get_stat("health") < char.get_max("health")/5:
                char.override_portrait("portrait", "indifferent")
                char.say(choice(["But %s is too wounded for that." % char.name, "But %s wounds completely occupy %s thoughts." % (char.pd, char.pd)]))
                char.restore_portrait()
                char.gfx_mod_stat("disposition", -randint(5, 15))
                char.mod_stat("vitality", -2)
                return True
            return False

        @staticmethod
        def check_for_minor_bad_stuff(char):
            # we check minor issues when character might refuse to do something based on dice
            if char.get_stat("joy") < 10 or (char.get_stat("joy") <= 25 and "Pessimist" not in char.traits):
                if dice(iam.hero_influence(char)) and dice(80):
                    narrator("It looks like %s is in a bad mood, however you managed to cheer %s up." % (char.p, char.op))
                    char.gfx_mod_stat("disposition", 1)
                    char.gfx_mod_stat("affection", affection_reward(char, .1))
                    char.gfx_mod_stat("joy", randint(3, 6))
                else:
                    narrator("It looks like %s is in a bad mood today and not does not want to do anything." % char.p)
                    return True
            elif "Down with Cold" in char.effects or "Injured" in char.effects: #if she's ill, there is a chance that she will disagree to chat
                if dice(iam.hero_influence(char)) and dice(80):
                    narrator("It looks like %s is not feeling well today, however you managed to cheer %s up a bit." % (char.p, char.op))
                    char.gfx_mod_stat("disposition", 2)
                    char.gfx_mod_stat("affection", affection_reward(char, .2))
                    char.gfx_mod_stat("joy", randint(1, 5))
                else:
                    narrator("%s is not feeling well today and not in the mood to do anything." % char.pC)
                    return True
            elif char.get_stat("vitality") <= char.get_max("vitality")/5 and dice(35):
                iam.refuse_because_tired(char)

                char.gfx_mod_stat("disposition", -randint(0, 1))
                char.mod_stat("vitality", -randint(1, 2))
                return True
            return False

        @staticmethod
        def check_for_bad_stuff_greetings(char):
            # Special beginnings for greetings if something is off, True/False show that sometimes we even will need to skip a normal greeting altogether
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

        @staticmethod
        def find_les_partners(character):
            """
            Returns a list with if any partner(s) is available and willing at the location.
            (lesbian action)
            *We can move this to GM class and have this run once instead of twice! (menu + label)
            """
            # First get a set of all girls at the same location as the current character:
            char_locs = set([character.home, character.workplace])
            partners = set()
            for i in chars.values():
                if character == i:
                    continue
                if not char_locs.isdisjoint([i.home, i.workplace]):
                    partners.add(i)

            # Next figure out if disposition of possible partners towards MC is
            # high enough for them to agree and/or they are lovers of char.
            willing_partners = []
            for i in partners:
                if not (check_lovers(i) or check_lovers(character, i)):
                    continue
                if i.get_stat("vitality") < 25 or i.get_stat("health") < i.get_max("health")*3/5:
                    continue
                if i.get_stat("affection") > -50:
                    willing_partners.append(i)

            return willing_partners

        @staticmethod
        def int_reward_exp(char, mod=.25):
            hero.gfx_mod_exp(exp_reward(hero, char, exp_mod=mod))
            char.gfx_mod_exp(exp_reward(char, hero, exp_mod=mod))