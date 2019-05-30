init python:
    def get_rape_picture(char=None, hidden_partner=False):
        """
        This function returns the best possible rape picture, without specifying where or what kind of action it should have since rape pics are not common enough to be so demanding.
        """
        excluded = ["happy", "confident", "suggestive", "ecstatic", "gay"]
        if char.has_image("normalsex", "rape", exclude=["gay"]):
            if hidden_partner:
                gm.set_img("normalsex", "rape", "partnerhidden", exclude=["gay"], type="reduce")
            else:
                gm.set_img("normalsex", "rape", exclude=["gay"], type="reduce")
        elif char.has_image("normalsex", exclude=excluded):
            if hidden_partner:
                gm.set_img("normalsex", "partnerhidden", exclude=excluded, type="first_default")
            else:
                gm.set_img("normalsex", exclude=excluded, type="first_default")
        else:
            gm.set_img("normalsex", "partnerhidden", "ripped", exclude=["gay", "happy", "confident"], type="reduce")
        return
        
    def get_single_sex_picture(char, act="stripping", location="any", hidden_partner=False):
        """A universal function that returns most suitable sex picture depending on arguments.
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
                optional_included = ["swimsuit"]
        elif location == "park":
            loc_tag = "nature"

            excluded.extend(["beach", "wildness"])
        elif location == "forest":
            loc_tag = "nature"
            excluded.extend(["beach", "urban"])

        if act == "stripping":
            # try to find a stripping image
            if char.has_image("stripping", loc_tag, exclude=excluded):
                gm.set_img("stripping", loc_tag, *optional_included, exclude=excluded, type="reduce")
            else:
                tags = (["simple bg", "stripping"], ["no bg", "stripping"])
                result = get_simple_act(char, tags, excluded)
                if result:
                    result.extend(optional_included)
                    gm.set_img(*result, exclude=excluded, type="reduce")
                else:
                    # could not find a stripping image, check for lingerie or nude pictures
                    excluded.extend(["sleeping", "bathing", "stage", "sex"])

                    if char.has_image("lingerie", loc_tag, exclude=excluded):
                        gm.set_img("lingerie", loc_tag, *optional_included, exclude=excluded, type="reduce")
                    elif char.has_image("nude", loc_tag, exclude=excluded):
                        gm.set_img("nude", loc_tag, *optional_included, exclude=excluded, type="reduce")
                    else:
                        tags = (["simple bg", "nude"], ["no bg", "nude"], ["simple bg", "lingerie"], ["no bg", "lingerie"])
                        result = get_simple_act(char, tags, excluded)
                        if result:
                            result.extend(optional_included)
                            gm.set_img(*result, exclude=excluded, type="reduce")
                        else:
                            # whatever...
                            gm.set_img("nude", loc_tag, *optional_included, exclude=excluded, type="reduce")

        elif act == "masturbation":
            if char.has_image("masturbation", loc_tag, exclude=excluded):
                gm.set_img("masturbation", loc_tag, *optional_included, exclude=excluded, type="reduce")
            else:
                tags = (["simple bg", "masturbation"], ["no bg", "masturbation"])
                result = get_simple_act(char, tags, excluded)
                if result:
                    result.extend(optional_included)
                    gm.set_img(*result, exclude=excluded, type="reduce")
                else:
                    # could not find masturbation image, check for nude pictures
                    excluded.extend(["sleeping", "bathing", "stage", "sex"])

                    gm.set_img("nude", loc_tag, *optional_included, exclude=excluded, type="reduce")

        else: # any 2c/bc sexual act
            # partner filters
            if char.gender == hero.gender:
                excluded.append("straight")
            else:
                excluded.append("gay")
            if hidden_partner:
                optional_included.append("partnerhidden")
            else:
                optional_included.append("sexwithmc")

            # image selection
            if char.has_image(act, loc_tag, exclude=excluded):
                gm.set_img(act, loc_tag, *optional_included, exclude=excluded, type="reduce")
            elif char.has_image("after sex", loc_tag, exclude=excluded):
                gm.set_img("after sex", loc_tag, *optional_included, exclude=excluded, type="reduce")
            else:
                tags = ([act, "simple bg"], [act, "no bg"], ["after sex", "simple bg"], ["after sex", "no bg"])
                result = get_simple_act(char, tags, excluded)
                if result:
                    result.append(optional_included[-1])
                    gm.set_img(*result, exclude=excluded, type="reduce")
                else:
                    excluded.append("sex")
                    gm.set_img("nude", loc_tag, exclude=excluded, type="reduce")

        return
        
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

        if char.has_image(loc_tag, underwear, exclude=excluded):
            gm.set_img(loc_tag, underwear, "nude", exclude=excluded, type="reduce")
        elif char.has_image(loc_tag, "nude", exclude=excluded):
            gm.set_img(loc_tag, "nude", exclude=excluded, type="reduce")
        else:
            tags = (["simple bg", underwear], ["no bg", underwear])
            result = get_simple_act(char, tags, excluded)
            if result:
                result.append("nude")
                gm.set_img(*result, exclude=excluded, type="reduce")
            else:
                tags = (["simple bg", "nude"], ["no bg", "nude"])
                result = get_simple_act(char, tags, excluded)
                if result:
                    gm.set_img(*result, exclude=excluded, type="reduce")
                else:
                    gm.set_img("nude", underwear, exclude=excluded, type="reduce")

        return
        
    def get_character_libido(char, mc=True): # depending on character traits returns relative libido level, ie how much the character wishes to have sex with MC
    # has nothing to do with character's willingness to even start sex; if mc = false then we calculate it not for mc, ie ignore some personal traits
    # it's more or less permanent pseudostat compared to many other games where it changes regularly like health, if not more often

        l = locked_random("randint", 3, 5)
        if "Nymphomaniac" in char.traits:
            l += 2
        elif "Frigid" in char.traits:
            l -= 1
        
        if mc:
            if "Half-Sister" in char.traits and not "Sister Lover" in hero.traits:
                if char.get_stat("affection") >= 700:
                    l += locked_random("randint", 1, 2)
                else:
                    l -= 1
            if check_lovers(hero, char):
                l += 1
            
        if cgochar(char, "SIW") and l < 3: # sex workers can't have it less than 3 though
            l = 3
            
        if "Virgin" in char.traits: # or 2 if virgins...
            l -= 1

        if l < 1:
            l = 1 # normalization, in general libido can be from 1 to 7 for frigid ones and from 3 to 10 for nymphomaniacs
        return l
        
    def get_character_wishes(char): # for taking action during sex scenes, returns action that character is willing to commit on her own
        skills = ["sex", "oral", "anal"]
        if (char.status != "slave" and check_lovers(hero, char)) or "Virgin" not in char.traits:
            skills.extend(["vaginal"])
        skills_values=[]
        for t in skills:
            skills_values.append([t, char.get_skill(t)])
        result = weighted_sample(skills_values)
        if not(result):
            result=choice(skills)
        return result

