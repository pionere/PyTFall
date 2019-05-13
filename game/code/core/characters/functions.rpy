init -11 python:
    def stop_training(char):
        #since there is no slave training yet, this does nothing
        pass

    def char_is_training(char):
        #since there is no slave training yet, this is always false.
        #Should be updated when Slave Training is implemented.
        return False

    def is_skill(skill):
        return skill in STATIC_CHAR.SKILLS

    def is_stat(stat):
        return stat in STATIC_CHAR.STATS

    def get_average_wage():
        wages = STATIC_CHAR.BASE_WAGES.values()
        wage = sum(wages)/len(wages)
        return round_int(wage)

    def friends_disp_check(char, msg=None):
        """Sets up friendship with characters based on disposition and affection"""
        if hero in char.lovers:
            temp = char.get_stat("affection")
            if (temp < 200 and char.status == "free") or (temp < 50): # and self.status == "slave"):
                    end_lovers(char, hero)
                    if msg is not None:
                        msg.append("%s and you are no longer lovers..." % char.nickname)

        temp = char.get_stat("disposition")
        if hero in char.friends:
            if temp <= 0:
                end_friends(char, hero)
                if msg is not None:
                    msg.append("%s is no longer friends with you..." % char.nickname)
        elif temp > 400:
            set_friends(char, hero)
            if msg is not None:
                msg.append("%s became pretty close to you." % char.nickname)

    def retire_chars_from_building(chars, b):
        for c in chars:
            if c.home == b:
                if c.status == "free" and c != hero:
                    c.home = pytfall.city
                else:
                    c.home = pytfall.streets
            if c.workplace == b:
                c.mod_workplace(None)

    def check_stat_perc(char, stat, value, dir="lower"):
        """Checks if stat/skill is higher/lower (or eq) than given percentage of the max.

        value should be a float to check against. (.1 = 10%, .34 = 34% and etc.)
        """
        if is_stat(stat):
            max_value = char.get_max(stat)
            val = char.get_stat(stat)
            if dir == "lower":
                if val <= max_value*value:
                    return True
            elif dir == "higher":
                if val >= max_value*value:
                    return True
            return False
        elif is_skill(stat):
            raise NotImplementedError("Skills are not yet implemented in this function.")

    def mod_by_max(char, stat, value):
        """Modifies a stat by a float multiplier (value) based of it's max value.
        """
        value = round_int(char.get_max(stat)*value)
        char.mod_stat(stat, value)

    def restore_battle_stats(char):
        for stat in ("health", "mp", "vitality"): # BATTLE_STATS
            char.set_stat(stat, char.get_max(stat))

    def build_multi_elemental_icon(size=70, elements=None):
        if elements is None: # Everything except "Neutral"
            icons = [Transform(e.icon, size=(size, size)) for e in tgs.elemental if e.id != "Neutral"]
        else:
            icons = [Transform(e.icon, size=(size, size)) for e in elements]

        xcsize = round_int(float(size)/(len(icons)))
        fixed = Fixed(xysize=(size, size))
        for index, icon in enumerate(icons):
            crop = (absolute(index*xcsize), absolute(0), xcsize, size)
            xpos = absolute(index*xcsize)
            i = Transform(icon, crop=crop, subpixel=True, xpos=xpos)
            fixed.add(i)
        return fixed

    def action_str(char):
        result = char.action
        if result is None:
            # action not set
            result = "None"
        elif hasattr(result, "id"):
            # standard job/task
            result = result.id
        #else: # string result of PytGroup
        return result

    def trait_info_calculator(char_or_trait):
        if isinstance(char_or_trait, PytCharacter):
            traits = char.traits
            trait_info = Trait()
        else:
            traits = [char_or_trait]
            trait_info = char_or_trait

        # merged info of elemental modifiers:
        elementals = defaultdict(dict)
        for trait in traits:
            temp = getattr(trait, "el_damage", None)
            if temp is not None:
                for element, value in temp.iteritems():
                    elementals[element]["attack"] = elementals[element].get("attack", 0) + int(value*100)

            temp = getattr(trait, "el_defence", None)
            if temp is not None:
                for element, value in temp.iteritems():
                    elementals[element]["defence"] = elementals[element].get("defence", 0) + int(value*100)

            for i in trait.resist:
                elementals[i]["resist"] = True

            temp = getattr(trait, "el_absorbs", None)
            if temp is not None:
                for element, value in temp.iteritems():
                    elementals[element]["abs"] = elementals[element].get("abs", 0) + int(value*100)

        for i in elementals:
            if not "defence" in elementals[i].keys():
                elementals[i]["defence"] = 0

            if not "attack" in elementals[i].keys():
                elementals[i]["attack"] = 0

        # merged info of defence bonus:
        defence_bonus = {}
        for type, value in getattr(trait_info, "defence_bonus", {}).iteritems():
            defence_bonus[type] = [value, 0]
        for type, value in getattr(trait_info, "defence_multiplier", {}).iteritems():
            if type in defence_bonus:
                defence_bonus[type][1] = value
            else:
                defence_bonus[type] = [None, value]

        # merged info of delivery bonus:
        delivery_bonus = {}
        for type, value in getattr(trait_info, "delivery_bonus", {}).iteritems():
            delivery_bonus[type] = [value, 0]
        for type, value in getattr(trait_info, "delivery_multiplier", {}).iteritems():
            if type in delivery_bonus:
                delivery_bonus[type][1] = value
            else:
                delivery_bonus[type] = [None, value]

        return trait_info, elementals, defence_bonus, delivery_bonus

    # GUI helpers:
    def controlled_char(char):
        # used in chars profile, most user interface options disabled if this returns False.
        return char in hero.chars and char.is_available

    # Characters related:
    def get_first_name(sex="female"):
        """Gets a randomly generated first name.

        sex: male/female
        """
        if sex == "female":
            if not store.female_first_names:
                store.female_first_names = load_female_first_names(200)
            return store.female_first_names.pop()
        elif sex == "male":
            if not store.male_first_names:
                store.male_first_names = load_male_first_names(200)
            return store.male_first_names.pop()
        else:
            raise Exception("Unknown argument passed to get_first_name func!")

    def get_last_name():
        if not store.random_last_names:
            store.random_last_names = load_random_last_names(200)
        return random_last_names.pop()

    def get_team_name():
        if not hasattr(store, "random_team_names") or not store.random_team_names:
            store.random_team_names = load_team_names(50)
        return random_team_names.pop()

    def build_mob(id=None, level=1):
        mob = Mob()

        if not id:
            id = choice(mobs.keys())
        elif not id in mobs:
            raise Exception("Unknown id {} when creating a mob!".format(id))

        data = mobs[id]
        mob.id = id

        for i in ("name", "desc", "battle_sprite", "portrait", "origin", "locations", "full_race", "front_row"):
            if i in data:
                setattr(mob, i, data[i])

        for skill, value in data["skills"].iteritems():
            mob.stats.mod_full_skill(skill, value)

        # Get and normalize basetraits:
        mob.traits.basetraits = set(traits[t] for t in data["basetraits"])
        for trait in mob.traits.basetraits:
            mob.apply_trait(trait)

        for trait in data["traits"]:
            mob.apply_trait(trait)

        if "default_attack_skill" in data:
            skill = data["default_attack_skill"]
            mob.default_attack_skill = store.battle_skills[skill]
        for skill in data["attack_skills"]:
            mob.attack_skills.append(store.battle_skills[skill])
        for skill in data["magic_skills"]:
            mob.magic_skills.append(store.battle_skills[skill])

        mob.init()

        level = max(level, data["min_lvl"])
        if level != 1:
            initial_levelup(mob, level)

        stats = mob.stats
        for stat, value in data["stats"].iteritems():
            if stat != "vitality":
                stats._mod_base_stat(stat, value)
            else:
                if stats.max[stat] < value:
                    stats.max[stat] = value
                if stats.lvl_max[stat] < value:
                    stats.lvl_max[stat] = value
                stats.stats[stat] = value

        return mob

    def build_rc(id=None, name=None, last_name=None,
                 bt_go_patterns=None, bt_go_base=None,
                 set_status="free", set_locations=True,
                 tier=0, tier_kwargs=None, add_to_gameworld=True,
                 give_civilian_items=False, give_bt_items=False,
                 spells_to_tier=True):
        '''Creates a random character!
        id: id to choose from the rchars dictionary that holds rGirl loading data.
            from JSON files, will be chosen at random if none available.
        name: (String) Name for the character to use. If None one will be chosen from randomNames file!
        last_name: Same thing only for last name :)
        bt_go_patterns: General occupation patterns to use when creating the character!
            Expects general occupation or list of the same.
            Use create_traits_base function to build basetraits.
            Input could be ["Combatant", "Specialist"] for example, we will pick from all
            Combatant and Specialist bts in the game randomly.
        bt_go_base: a gen.occupation as a base to select the first basetrait. Occasionally a secondary random basetrait is added.
        tier: Tier of the character... floats are allowed.
        add_to_gameworld: Adds to characters dictionary, should always
            be True unless character is created not to participate in the game world...

        give_civilian_items // give_bt_items:
            *Note: bt_ ==> base_traits* (award items for profession)
            Give/Equip item sets using auto_buy without paying cash.
        spells_to_tier: Award spells to the char
        '''
        if tier_kwargs is None:
            tier_kwargs = {}

        rg = rChar()

        if not id:
            id = choice(rchars.keys())
        elif id not in rchars:
            raise Exception("Unknown id %s when creating a random character!" % id)
        data = rchars[id]
        rg.id = id

        # Names/Origin:
        if not name:
            name = get_first_name()
        rg.name = rg.nickname = name

        if not last_name:
            last_name = get_last_name()
        rg.fullname = " ".join([name, last_name])

        origin = data.get("origin", None)
        if origin is None:
            origin = choice(["Alkion", "PyTFall", "Crossgate"])
        elif not isinstance(origin, basestring):
            origin = choice(origin)
        rg.origin = origin

        # Status next:
        if set_status is False:
            pass
        elif set_status is not True:
            rg.status = set_status
        else:
            rg.status = choice(STATIC_CHAR.STATUS)

        # Locations:
        if set_locations is False:
            pass
        elif set_locations is not True:
            rg.home = set_locations
            set_location(rg, None)
        elif set_locations:
            rg.home = pytfall.sm if rg.status == "slave" else pytfall.city
            set_location(rg, None)

        # Common expected data:
        for i in ("gold", "desc", "height", "full_race", "gender"):
            if i in data:
                setattr(rg, i, data[i])

        # Colors in say screen:
        for key in ("color", "what_color"):
            if key in data:
                color = data[key]
                try:
                    color = Color(color)
                except:
                    char_debug("Invalid %s: %s for random character: %s!" % (key, data[key], id))
                    color = "ivory"
                rg.say_style[key] = color

        # BASE TRAITS:
        selection = None
        if bt_go_patterns:
            selection = create_traits_base(bt_go_patterns)
        else:
            if bt_go_base is None:
                if rg.status == "slave":
                    bt_go_base = STATIC_CHAR.SLAVE_GEN_OCCS
                else:
                    bt_go_base = STATIC_CHAR.GEN_OCCS
                bt_go_base = choice(bt_go_base)
            base_traits = list(gen_occ_basetraits[bt_go_base])
            selection = [choice(base_traits)]
            dist = random.random()
            if dist > .7:
                # multiclass
                if dist > .9 or len(base_traits) == 1:
                    # choose an occ from other occ-group
                    curr_occ = bt_go_base
                    if rg.status == "slave":
                        bt_go_base = STATIC_CHAR.SLAVE_GEN_OCCS
                    else:
                        bt_go_base = STATIC_CHAR.GEN_OCCS
                    bt_go_base = [t for t in bt_go_base if bt_go_base != curr_occ]
                    base_traits = tuple(gen_occ_basetraits[choice(bt_go_base)])
                else:
                    # select another occ from the same occ-group
                    base_traits.remove(selection[0])
                selection.append(choice(base_traits))

        basetraits = set()
        for t in selection:
            if isinstance(t, basestring):
                t = traits[t]
            basetraits.add(t)
        rg.traits.basetraits = basetraits
        for t in basetraits:
            rg.apply_trait(t)

        # Blocking traits:
        for key in ("blocked_traits", "ab_traits"):
            if key in data:
                _traits  = set()
                for trait in data[key]:
                    trait = traits[trait]
                    # assert(trait is not None and not trait.basetrait)
                    _traits.add(trait)
                setattr(rg.traits, key, _traits)

        # Traits next:
        if "random_traits" in data:
            for item in data["random_traits"]:
                trait, chance = item
                if dice(chance):
                    trait = traits[trait]
                    # assert(trait is not None and not trait.basetrait)
                    rg.apply_trait(trait)

        # Battle and Magic skills:
        if "default_attack_skill" in data:
            skill = data["default_attack_skill"]
            rg.default_attack_skill = store.battle_skills[skill]

        # Normalizing new character:
        # We simply run the init method of parent class for this:
        rg.init()

        # And at last, leveling up and stats/skills applications:
        tier_up_to(rg, tier, **tier_kwargs)

        # Spells to Tier:
        if spells_to_tier:
            give_tiered_magic_skills(rg)

        # Items, give and/or autoequip:
        give_tiered_items(rg, give_civilian_items, give_bt_items)

        # if equip_to_tier: # Old (faster but less precise) way of giving items:
        #     give_tiered_items(rg, **gtt_kwargs) # (old/simle(er) func)

        # And add to char! :)
        if add_to_gameworld:
            rg.set_flag("from_day_in_game", day)
            rg.log_stats()
            dict_id = "_".join([rg.id, rg.name, rg.fullname.split(" ")[1]])
            rg.dict_id = dict_id
            store.chars[dict_id] = rg

        return rg

    def give_tiered_items(char, give_civilian_items=False, give_bt_items=False):
        """Gives items to a character as well as equips for a specific task.

        Usually ran right after we created the said character.
        """
        if (not give_civilian_items) and (not give_bt_items):
            return

        container = []
        limit_tier = min(((char.tier/2)+1), 5)
        for i in range(limit_tier):
            container.extend(store.tiered_items[i]) # MAX_ITEM_TIER

        if give_civilian_items:
            slots = {slot: 1 for slot in EQUIP_SLOTS}
            char.auto_buy(slots=slots, equip=not give_bt_items, check_money=False, container=container,
                          purpose="Slave" if char.status == "slave" else "Casual",
                          smart_ownership_limit=False)
        if give_bt_items:
            slots = {slot: 1 for slot in EQUIP_SLOTS}
            char.auto_buy(slots=slots, equip=True, check_money=False, container=container,
                          smart_ownership_limit=give_civilian_items, purpose=None)

    def create_traits_base(patterns):
        """Create a pattern with one or two base traits for a character.

        patterns: Single general occupation or list of the same to build a specific pattern from.
        """
        if isinstance(patterns, basestring):
            patterns = [patterns]
        patterns = list(chain.from_iterable(gen_occ_basetraits[p] for p in patterns))
        if len(patterns) > 1 and dice(50):
            return random.sample(patterns, 2)
        else:
            return random.sample(patterns, 1)

    def give_tiered_magic_skills(char, amount=None):
        """Gives spells to the character.

        amount: Amount of skills to give (normal, support).
         *normal: attack spells
         *support: healing and status spells
         If not set, the char will get it based on occupations and tiers.
        """
        tier = min(((char.tier/2)+1), 4) # MAX_MAGIC_TIER = 4
        attributes = set([t.id.lower() for t in char.elements])
        if amount is None:
            if traits["Healer"] in char.traits.basetraits:
                s_amount = max(tier, 2)
            #elif traits["Healer"] in char.traits:
            #    s_amount = max(tier, 1)
            else:
                s_amount = 0

            gen_occs = char.gen_occs
            if "Caster" in gen_occs:
                amount = tier + randint(1, 2)
                s_amount += 1
            elif "Combatant" in gen_occs:
                if "neutral" in attributes:
                    amount = randrange(2)
                else:
                    amount = randrange(3)
            else:
                amount = 0
        else:
            amount, s_amount = amount

        if amount <= 0 and s_amount <= 0:
            return

        for _ in reversed(range(tier+1)):
            if amount > 0:
                if "neutral" in attributes:
                    spells = tiered_magic_skills[_] # [:] - no need for the moment
                else:
                    spells = [s for s in tiered_magic_skills[_] if attributes.intersection(s.attributes)]
                shuffle(spells)
                for s in spells:
                    if s not in char.magic_skills:
                        char.magic_skills.append(s)
                        amount -= 1
                        if amount <= 0:
                            break

            if s_amount > 0:
                spells = tiered_healing_skills[_] # [:] - no need for the moment
                shuffle(spells)
                for s in spells:
                    if s not in char.magic_skills:
                        char.magic_skills.append(s)
                        s_amount -= 1
                        if s_amount <= 0:
                            break

            # print(", ".join([s.name for s in spells]))
            if amount <= 0 and s_amount <= 0:
                break

    def initial_levelup(char, level, max_out_stats=False):
        """
        This levels up the character, usually when it's first created.
        """
        # exp = level*(level-1)*500
        # char.stats.level = 1
        # char.exp = 0
        # char.stats.goal = 1000
        # char.stats.goal_increase = 1000

        exp = level*1000
        char.mod_exp(exp)

        if max_out_stats:
            for stat in char.stats.stats:
                if stat not in STATIC_CHAR.FIXED_MAX:
                    char.mod_stat(stat, char.get_max(stat))
        # --------

    def build_client(id=None, gender="male", rank=1,
                     name=None, last_name=None,
                     pattern=None, likes=None, tier=1):
        """
        This function creates Customers to be used in the jobs.
        Some things are initiated in __init__ and funcs/methods that call this.

        - pattern: Pattern (string) to be supplied to the create_traits_base function.
        - likes: Expects a list/set/tuple of anything a client may find attractive in a worker/building/upgrade, will be added to other likes (mostly traits), usually adds a building...
        """
        client = Customer(gender, rank)

        if not id:
            id = "Client" + str(random.random())
        client.id = id

        # Names:
        if not name:
            name = get_first_name(gender)
        if not last_name:
            last_name = get_last_name()
        client.name = name
        client.fullname = client.nickname = " ".join([name, last_name])

        # Patterns:
        if pattern is None:
            pattern = STATIC_CHAR.GEN_OCCS
        pattern = create_traits_base(pattern)
        for i in pattern:
            client.traits.basetraits.add(i)
            client.apply_trait(i)

        # Add a couple of client traits: <=== This may not be useful...
        trts = random.sample(tgs.client, randint(2, 5))
        for t in trts:
            client.apply_trait(t)

        if dice(20):
            client.apply_trait("Aggressive")

        # Likes:
        # Add some traits from trait groups:
        cl = set()
        cl.add(choice(tgs.gents))
        cl.add(choice(tgs.body))
        cl.add(choice(tgs.race))
        cl.update(random.sample(tgs.base, randint(1, 2)))
        cl.update(random.sample(tgs.elemental, randint(2, 3)))
        cl.update(random.sample(tgs.ct, randint(2, 4)))
        cl.update(random.sample(tgs.sexual, randint(1, 2)))

        if likes:
            cl.update(likes)
            # We pick some of the traits to like/dislike at random.

        #if gender == "female":
        #    cl.add(traits["Lesbian"])
        #else: #if gender == "male":
        #    cl.discard(traits["Lesbian"])

        client.likes = cl

        # We simply run the init method of parent class for this:
        #client.init() - skip for the moment, only used in warriors_quarters.intercept

        tier_up_to(client, tier)

        # meta info TODO might not belong here
        client.dirtmod = get_linear_value_of(rank, 1, 1.0, 7, .5) # MAX_RANK = 7, MIN_RANK = 1
        client.threatmod = get_linear_value_of(rank, 1, 1.0, 7, .5) # MAX_RANK = 7, MIN_RANK = 1
        if "Aggressive" in client.traits:
            client.threatmod *= 4
        return client

    def copy_char(char):
        """Attempt to copy a character by remaking it anew in his own image.
        """
        if isinstance(char, PytGroup):
            char = char._first

        new = char.__class__()

        for attr, value in char.__dict__.items():
            if attr == "effects":
                new.effects = deepcopy(value)
            elif isinstance(value, (bool, float, basestring, int, Trait)):
                setattr(new, attr, value)
            elif isinstance(value, (dict, set)):
                setattr(new, attr, value.copy())
            elif isinstance(value, list):
                char_debug("{}".format(value))
                setattr(new, attr, value[:])

        assign_to = new.stats
        for attr, value in char.stats.__dict__.items():
            if attr == "skills":
                assign_to.skills = deepcopy(value)
            if attr == "skills_multipliers":
                assign_to.skills_multipliers = deepcopy(value)
            elif isinstance(value, (bool, float, basestring, int)):
                setattr(assign_to, attr, value)
            elif isinstance(value, (dict, set)):
                setattr(assign_to, attr, deepcopy(value))
            elif isinstance(value, list):
                setattr(assign_to, attr, value[:])

        # Smart Trackers:
        new.traits.list = char.traits.list[:]
        new.traits.normal = char.traits.normal.copy()
        new.traits.items = char.traits.items.copy()
        new.traits.ab_traits = char.traits.ab_traits.copy()
        new.traits.blocked_traits = char.traits.blocked_traits.copy()
        new.traits.basetraits = char.traits.basetraits.copy()

        new.resist.list = char.resist.list[:]
        new.resist.normal = char.resist.normal.copy()
        new.resist.items = char.resist.items.copy()

        new.attack_skills.list = char.attack_skills.list[:]
        new.attack_skills.normal = char.attack_skills.normal.copy()
        new.attack_skills.items = char.attack_skills.items.copy()

        new.magic_skills.list = char.magic_skills.list[:]
        new.magic_skills.normal = char.magic_skills.normal.copy()
        new.magic_skills.items = char.magic_skills.items.copy()

        return new

    def remove_from_gameworld(char):
        # Try to properly delete the char...
        char.location = None
        char.home = None
        char.reset_workplace_action()

        # Relationships:
        for c in char.friends:
            c.friends.discard(char)
        for c in char.lovers:
            c.lovers.discard(char)

        # SlaveMarket
        pytfall.sm.remove_char(char)
        # Jail
        pytfall.jail.remove_char(char)

        global gm
        gm.remove_girl(char) # gm is poorly named and can be overwritten...

        global chars
        temp = getattr(char, "dict_id", char.id)
        del chars[temp]

        del char

    def kill_char(char):
        # Attempts to remove a character from the game world.
        # This happens automatically if char's health goes 0 or below.
        if "Undead" in char.traits:
            char.set_stat("health", 1)
            return
        if char == hero:
            jump("game_over")

        if char in hero.chars:
            hero.remove_char(char)

        char.home = pytfall.afterlife

        gm.remove_girl(char)

    def tier_up_to(char, tier, level_bios=(.9, 1.1),
                   skill_bios=(.65, 1.0), stat_bios=(.65, 1.0)):
        """Tiers up a character trying to set them up smartly

        @params:
        char: Character object or id
        tier: Tier number to level to (10 is max and basically a God)
        bios: When setting up stats and skills, uniform between the two values
              will be used.
              Level, stats and skills biases work in the same way

        Important: Should only be used right after the character was created!
        """
        # limit tier
        if tier > MAX_TIER:
            tier = MAX_TIER

        level_bios = partial(uniform, level_bios[0], level_bios[1])
        skill_bios = partial(uniform, skill_bios[0], skill_bios[1])
        stat_bios = partial(uniform, stat_bios[0], stat_bios[1])
        # Level with base 20
        level = tier*20
        if level:
            level = round_int(level*level_bios())
            initial_levelup(char, level)

        # devlog.info("")
        # devlog.info("MEOW: Char/Tier: {}/{}".format(char.name, tier))
        # devlog.info("Base: {}".format(char.traits.base_to_string))

        # Do the stats/skills:
        base_skills = set()
        base_stats = set()
        # !!! Using weight may actually confuse thing in here... this needs testing.
        # Also, it may be a good idea to do list(s) of stats/skills every ht char should have a bit of...
        for trait in char.traits.basetraits:
            skills = trait.base_skills
            total_weight_points = sum(skills.values())
            total_skill_points = sum(char.get_max_skill(s, tier)*.6 for s in skills)
            for skill, weight in skills.items():
                # devlog.info("SKILL/Pre-Value: {}/{}".format(skill, char.get_skill(skill)))
                base_skills.add(skill)
                weight_ratio = float(weight)/total_weight_points
                # devlog.info("Weight Ratio: {}".format(weight_ratio))
                sp = total_skill_points*weight_ratio
                # devlog.info("Skill Points: {}".format(sp))
                # # weight_sp = weight_ratio*sp
                # # devlog.info("Weighted Points: {}".format(weight_sp))
                biosed_sp = round_int(sp*skill_bios())
                # devlog.info("Biased Points: {}".format(biosed_sp))

                char.stats.mod_full_skill(skill, biosed_sp)

                # devlog.info("Resulting Skill: {}".format(char.get_skill(skill)))

            stats = trait.base_stats
            total_weight_points = sum(stats.values())
            total_stat_points = sum(char.get_relative_max_stat(s, tier) for s in stats)
            for stat, weight in stats.items():
                base_stats.add(stat)
                weight_ratio = float(weight)/total_weight_points
                sp = total_stat_points*weight_ratio
                # weight_sp = weight_ratio*sp
                biosed_sp = round_int(sp*stat_bios())

                char.mod_stat(stat, biosed_sp)

        # devlog.info("")

        # Now that we're done with baseskills, we can play with other stats/skills a little bit
        base_stats.update(STATIC_CHAR.FIXED_MAX)
        for stat in char.stats.stats:
            if stat not in base_stats:
                value = char.get_max(stat)
                if dice(char.get_stat("luck")*.5):
                    value *= .3
                else:
                    value *= uniform(.05, .15)
                value = round_int(value*stat_bios())
                char.mod_stat(stat, value)
        for skill in char.stats.skills:
            if skill not in base_skills:
                value = char.get_max_skill(skill, tier)
                if dice(char.get_stat("luck")*.5):
                    value *= .3
                else:
                    value *= uniform(.05, .15)
                value = round_int(value*skill_bios())
                char.mod_skill(skill, 0, value)

        char.tier = round_int(tier) # Makes sure we can use float tiers

    def exp_reward(char, difficulty, exp_mod=1): 
        """Adjusts the XP to be given to an actor. Doesn't actually award the EXP.

        char: Target actor.
        difficulty: Ranged 1 to 10. (will be normalized otherwise).
            This can be a number, Team or Char.
        exp_mod: We multiply the result with it. Could be useful when failing
            a task, give at least 10% of the exp (for example) is to set this mod
            to .1 in case of a failed action.
        """
        # find out the difficulty:
        if isinstance(difficulty, Team):
            difficulty = difficulty.get_level()/20.0
        elif isinstance(difficulty, PytCharacter):
            difficulty = difficulty.tier
        elif isinstance(difficulty, (float, int)):
            difficulty = max(0, min(MAX_TIER, difficulty))
        else:
            raise Exception("Invalid difficulty type {} provided to exp_reward function.")

        # Difficulty modifier:
        # Completed task oh higher difficulty:
        char_tier = char.tier
        diff = difficulty - char_tier
        if diff >= 0:
            if diff > 2:
                diff = 2 # max bonus mod possible is 2x the EXP.
        else: # Difficulty was lower
            if diff <= -2:
                return 0
        mod = 1+diff/2.0

        # add tier modifier to limit the value
        mod *= 1 - float(char_tier)/MAX_TIER
        value = DAILY_EXP_CORE * exp_mod * mod

        effects = char.effects
        if "Slow Learner" in effects:
            value *= .9
        if "Fast Learner" in effects:
            value *= 1.1

        return round_int(value)

    def gold_reward(char, value, ap_used=1):
        """
        Similar to above but less strict about the tier limit (let the max-players earn some money)
        """
        mod = 1 - float(char.tier)/(2*MAX_TIER)
        value *= mod * ap_used
        return round_int(value)

    def dice_int(value):
        if dice((abs(value)*100)%100):
            value += (1 if value >= 0 else -1)
        return int(value)

    def limited_affection(char, value):
        curr_affection = char.get_stat("affection")
        if value > 0:
            if curr_affection >= 200:
                return 0
            if curr_affection < 0:
                full_value = -curr_affection
                if value <= full_value:
                    return dice_int(value)
                value -= full_value
                curr_affection = 0
            else:
                value = min(value, 200 - curr_affection)
                full_value = 0
            value *= (1.0 - curr_affection/200.0)
        elif value < 0:
            if curr_affection <= -200:
                return 0
            if curr_affection > 0:
                full_value = -curr_affection
                if value >= full_value:
                    return dice_int(value)
                value -= full_value
                curr_affection = 0
            else:
                value = max(value, -200 - curr_affection)
                full_value = 0
            value *= (1.0 + curr_affection/200.0)

        return dice_int(value)

    def affection_reward(char, value=1, stat=None):
        """
        Adjusts the affection increase of an actor. Doesn't actually raise the affection.
        
        char: the affected actor
        value: the base affection increment
        stat: the stat on which the affection increment is based on
             only the given stat-preference of the actor is counted if defined,
             otherwise every preference of the actor is calculated 
        """
        temp = char.preferences
        if stat is not None:
            temp = temp.get(stat, 0)
            temp = {stat: temp}
        mod = .0
        for k, v in temp.items():
            if k == "gold":
                max_val = 10*char.gold
                val = hero.gold
            elif k == "arena_rep":
                max_val = pytfall.arena.ladder[0].arena_rep * .8
                val = hero.arena_rep
            elif is_stat(k):
                max_val = char.get_max_stat(k, tier=char.tier)
                val = hero.get_stat(k)
            elif is_skill(k):
                max_val = char.get_max_skill(k, tier=char.tier)
                val = hero.get_skill(k)
            else:
                raise Exception("Unknown stat %s in preferences of %s" % (k, char.name))
            mod += v * min(2, float(val) / (max(max_val, 1)))
        mod /= len(temp)
        mod *= DAILY_AFF_CORE

        if "Frigid" in char.traits:
            mod *= .8
        elif "Nymphomaniac" in char.traits:
            mod *= 1.2
        if 'Horny' in char.effects:
            mod *= 1.1

        value *= mod

        temp = ("Lesbian" if char.gender == "female" else "Gay") in char.traits
        if char.gender != hero.gender:
            if temp and "Yuri Expert" not in hero.traits:
                return limited_affection(char, value)
        else:
            if not temp:
                return limited_affection(char, value)
        if "Half-Sister" in char.traits and "Sister Lover" not in hero.traits:
            return limited_affection(char, value)

        return dice_int(value)
    #def get_act(character, tags): # copypaste from jobs without the self part, allows to randomly select one of existing tags sets
    #        acts = list()
    #        for t in tags:
    #            if isinstance(t, tuple):
    #                if character.has_image(*t):
    #                    acts.append(t)
    #            elif isinstance(t, dict):
    #                if character.has_image(*t.get("tags", []), exclude=t.get("exclude", [])) and dice(t.get("dice", 100)):
    #                    acts.append(t)

    #        if acts:
    #            act = choice(acts)
    #        else:
    #            act = None

    #        return act

    # copypaste of get_act from jobs without the self part, allows to randomly select one of existing tags sets
    #  unlike the function from jobs it supports only one set of excluded tags
    def get_simple_act(char, tags, excluded=None):
        acts = list()
        for t in tags:
            if char.has_image(*t, exclude=excluded):
                acts.append(t)
        if acts:
            act = choice(acts)
        else:
            act = None
        return act
