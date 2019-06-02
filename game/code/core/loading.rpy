# The whole thing should one day be recoded over a single renpy.list_files loop.
init 11 python:
    def load_webms():
        webms = {}
        for path in renpy.list_files():
            if "content/gfx/autowebm/" in path:
                split_path = path.split("/")
                folder = split_path[-2]
                file = split_path[-1]
                if "mask" in file:
                    webms.setdefault(folder, {})["mask"] = path
                if "movie" in file:
                    webms.setdefault(folder, {})["movie"] = path
                if "moviemask" in file: # rare cases when movie itself is also the mask
                    webms.setdefault(folder, {})["movie"] = path
                    webms.setdefault(folder, {})["mask"] = path

        for folder in webms:
            temp = folder.split(" ")

            tag = temp[0]
            channel = temp[2] if len(temp) == 3 else "main_gfx_attacks"
            loops = temp[1] if len(temp) >= 2 else 1
            if loops == "inf":
                renpy.image(tag, Movie(channel=channel, play=webms[folder]["movie"], mask=webms[folder].get("mask", None)))
            else:
                loops = int(loops)
                renpy.image(tag, MovieLooped(channel=channel, loops=loops, play=webms[folder]["movie"], mask=webms[folder].get("mask", None)))

    load_webms()

init -11 python:
    # ---------------------- Loading game data:
    def load_json(path):
        file = renpy.file(path)
        data = json.load(file, object_pairs_hook=OrderedDict)
        return data

    def load_db_json(fn):
        path = "content/db/" + fn
        return load_json(path)

    def load_team_names(amount):
        rn = load_db_json("names/team_names.json")
        return random.sample(rn, amount)

    def load_male_first_names(amount):
        rn = load_db_json("names/male_first_names.json")
        return random.sample(rn, amount)

    def load_female_first_names(amount):
        file_1 = "names/female_first_names_1.json"
        file_2 = "names/female_first_names_2.json"
        rn = load_db_json(file_1) + load_db_json(file_2)
        return random.sample(rn, amount)

    def load_random_last_names(amount):
        with open(content_path("db/names/last_names.json")) as f:
            rn = json.load(f)
        return random.sample(rn, amount)

    def load_characters(path, cls=None):
        """Loads a Full character from JSON file.

        path: Path to main folder.
        class: Class to use in creating the character.
               If not provided, the JSON data is returned

        This will walk through folders inside of a folder where the path leads, looking for JSONs and reading image tags off file names.
        """
        dir = content_path(path)
        content = dict()

        if cls is not None:
            exist = set(getattr(store, path, {}).keys())

        # Get to a folder with unique girl datafiles and imagefolders:
        for packfolder in os.walk(os.path.join(dir,'.')).next()[1]:
            # Load data files one after another.
            for file in os.walk(os.path.join(dir, packfolder, '.')).next()[2]:
                if not (file.startswith("data") and file.endswith(".json")):
                    continue

                # Load the file:
                in_file = os.path.join(dir, packfolder, file)
                char_debug("Loading from %s!" % str(in_file)) # Str call to avoid unicode
                with open(in_file) as f:
                    ugirls = json.load(f, object_pairs_hook=OrderedDict)

                # Apply the content of the file to the character:
                for gd in ugirls: # We go over each dict one mainaining correct order of application:
                    if "id" not in gd:
                        # Only time we throw an error instead of writing to log.
                        raise Exception("No id was specified in %s JSON Datafile!" % str(in_file))

                    folder = id = gd["id"]
                    _path = os.path.join(dir, packfolder, folder)
                    if os.path.isdir(_path):
                        # We load the new tags!:
                        tagdb.load_tags_folder(folder, _path)

                    if cls is None:
                        # JSON Data only
                        # Set the path to the folder:
                        gd["_path_to_imgfolder"] = _path

                        # validate data so we do not have to to it in runtime
                        if "default_attack_skill" in gd:
                            skill = gd["default_attack_skill"]
                            if skill not in store.battle_skills:
                                char_debug("%s JSON Loading func tried to apply unknown default attack skill: %s!" % (id, skill))
                                gd.pop("default_attack_skill")

                        for key in ("blocked_traits", "ab_traits"):
                            b_traits = gd.get(key, None)
                            if b_traits is not None:
                                drops = []
                                for t in b_traits:
                                    trait = traits.get(t, None)
                                    if trait is None:
                                        char_debug("Unknown trait: %s for random girl: %s in %s!" % (t, id, key))
                                    elif trait.basetrait:
                                        char_debug("Trait: %s for random character: %s is a basetrait which can not be blocked (%s)!" % (t, id, key))
                                    else:
                                        continue
                                    drops.append(t)
                                for t in drops:
                                    b_traits.remove(t)

                        for key in ("personality", "breasts", "penis", "body", "race"):
                            t = gd.get(key, None)
                            if t is not None:
                                field = "gents" if key in ["breasts", "penis"] else key
                                trait = traits.get(t, None)
                                if trait is None:
                                    char_debug("Unknown trait: %s for random girl: %s as %s!" % (t, id, key))
                                elif not getattr(trait, field, False):
                                    char_debug("Trait: %s for random character: %s as %s is invalid (%s of the trait is not True)!" % (t, id, key, field))
                                else:
                                    continue
                                gd.pop(key)

                        b_traits = gd.get("random_traits", None)
                        if b_traits is not None:
                            drops = []
                            for t in b_traits:
                                trait = traits.get(t[0], None)
                                if trait is None:
                                    char_debug("Unknown trait: %s for random girl: %s as 'random_traits'!" % (t[0], id))
                                elif trait.basetrait:
                                    char_debug("Trait: %s for random character: %s as random_traits is invalid (is a basetrait)!" % (t[0], id))
                                else:
                                    continue
                                drops.append(t)
                            for t in drops:
                                b_traits.remove(t)

                        content[id] = gd
                        continue

                    # Char with a specific class
                    if id in exist:
                        continue

                    char = cls()
                    char.id = id
                    # We set the path to the character
                    # so we know where to draw images from:
                    char._path_to_imgfolder = _path

                    # Note: Location is later normalized in init method.
                    for key in ("name", "nickname", "fullname"):
                        temp = gd.get(key, None)
                        if temp is not None:
                            if len(temp) > 20:
                                temp = temp[0:20]
                            setattr(char, key, temp)
                    for key in ("gender", "origin", "gold", "desc", "status", "location", "height", "full_race", "arena_willing"):
                        temp = gd.get(key, None)
                        if temp is not None:
                            setattr(char, key, temp)
                    if not char.name:
                        name = get_first_name(char.gender)
                        char.name = name
                        char.fullname = " ".join([name, get_last_name()])

                    # @Review: We make sure all traits get applied first!
                    for key in ("blocked_traits", "ab_traits"):
                        temp = gd.get(key, None)
                        if temp is not None:
                            b_traits  = set()
                            for t in temp:
                                trait = traits.get(t, None)
                                if trait is None:
                                    char_debug("%s trait is unknown for %s (In %s)!" % (t, id, key))
                                else:
                                    b_traits.add(trait)
                            setattr(char.traits, key, b_traits)

                    # Get and normalize basetraits:
                    temp = gd.get("basetraits", None)
                    if temp is not None:
                        basetraits = set()
                        for t in temp:
                            trait = traits.get(t, None)
                            if trait is None:
                                char_debug("%s basetrait is unknown for %s!" % (t, id))
                            elif trait.basetrait:
                                basetraits.add(trait)
                            else:
                                char_debug("%s is not a basetrait for %s!" % (t, id))

                        if len(basetraits) > 2:
                            basetraits = set(random.sample(tuple(basetraits), 2))

                        # In case that we have basetraits:
                        char.traits.basetraits = basetraits

                        for trait in basetraits:
                            char.apply_trait(trait)

                    for key in ("personality", "breasts", "penis", "body", "race"):
                        t = gd.get(key, None)
                        if t is not None:
                            field = "gents" if key in ["breasts", "penis"] else key
                            trait = traits.get(t, None)
                            if trait is None:
                                char_debug("%s %s is unknown for %s!" % (t, key, id))
                            elif not getattr(trait, field, False):
                                char_debug("Trait: %s for %s as %s is invalid (%s of the trait is not True)!" % (t, id, key, field))
                            else:
                                char.apply_trait(trait)

                    temp = gd.get("elements", None)
                    if temp is not None:
                        for t in temp:
                            trait = traits.get(t, None)
                            if trait is None:
                                char_debug("%s element is unknown for %s!" % (t, id))
                            elif trait.elemental:
                                char.apply_trait(trait)
                            else:
                                char_debug("%s is not an elemental trait for %s!" % (t, id))

                    temp = gd.get("random_traits", None)
                    if temp is not None:
                        for t in temp:
                            trait = traits.get(t[0], None)
                            if trait is None:
                                char_debug("% random trait is unknown for %s!" % (t[0], id))
                            elif trait.basetrait:
                                char_debug("Random trait %s for %s is invalid (is a basetrait)!" % (t[0], id))
                            elif dice(t[1]):
                                char.apply_trait(trait)

                    # if "stats" in gd:
                    #     for stat in gd["stats"]:
                    #         if stat in STATIC_CHAR.STATS:
                    #             value = gd["stats"][stat]
                    #             if stat != "luck":
                    #                 value = int(round(float(value)*char.get_max(stat))/100)
                    #             char.mod_stat(stat, value)
                    #         else:
                    #             devlog.warning("%s stat is unknown for %s!" % (stat, gd["id"]))
                    #     del gd["stats"]
                    #
                    # if "skills" in gd:
                    #     for skill, value in gd["skills"].items():
                    #         if is_skill(skill):
                    #             char.stats.mod_full_skill(skill, value)
                    #         else:
                    #             devlog.warning("%s skill is unknown for %s!" % (skill, gd["id"]))
                    #     del gd["skills"]

                    t = gd.get("default_attack_skill", None)
                    if t is not None:
                        skill = battle_skills.get(t, None)
                        if skill is None:
                            char_debug("%s default attack skill is unknown for %s!" % (t, id))
                        else:
                            char.default_attack_skill = skill

                    temp = gd.get("magic_skills", None)
                    if temp is not None:
                        for t in temp:
                            skill = battle_skills.get(t, None)
                            if skill is None:
                                char_debug("%s magic skill is unknown for %s!" % (t, id))
                            else:
                                char.magic_skills.append(skill)

                    for key in ("color", "what_color"):
                        t = gd.get(key, None)
                        if t is not None:
                            try:
                                color = Color(t)
                            except:
                                debug_str = "%s color supplied to %s is invalid!" % (t, id)
                                char_debug(debug_str)
                                color = "ivory"
                            char.say_style[key] = color

                    char.init() # Normalize!

                    # Tearing up:
                    # if "level" in gd:
                    #     initial_levelup(char, gd["level"])
                    #     del gd["level"]
                    temp = gd.get("tier", None)
                    if temp is None:
                        tier = uniform(.1, .4)
                        tier_up_to(char, tier)
                    else:
                        if isinstance(temp, dict):
                            tier_up_to(char, **temp)
                        else:
                            tier_up_to(char, temp)

                    temp = gd.get("item_up", "auto")
                    if temp == "auto":
                        if char.status == "slave":
                            give_tiered_items(char,
                                            give_civilian_items=True,
                                            give_bt_items=False)
                        else:
                            give_tiered_items(char,
                                            give_civilian_items=True,
                                            give_bt_items=True)
                    elif temp:
                        give_tiered_items(char,
                                        give_civilian_items=True,
                                        give_bt_items=True)

                    char.log_stats()

                    content[char.id] = char

        return content

    def load_special_arena_fighters(gender=None):
        if gender is None:
            females = getattr(store, "female_fighters", {})
            males = getattr(store, "male_fighters", {})
            exist = set(females.keys())
            exist.update(males)
            h = getattr(store, "hero")
            if h:
                exist.add(h.id)
            genders = { "female": "females", "male": "males" }
        else:
            # tagger -> request for json_data only
            females = males = {}
            genders = { gender: gender + "s" }
            
        json_data = load_db_json("arena_fighters.json")
        json_data = {i["name"]: i["basetraits"] for i in json_data}

        random_traits = tuple(traits[t] for t in ["Courageous", "Aggressive", "Vicious"])
        all_elements = tuple(traits[i.id] for i in tgs.elemental)

        dir = content_path("fighters")

        groups = {
            "assassins": traits["Assassin"],
            "healers": traits["Healer"],
            "knights": traits["Knight"],
            "mages": traits["Mage"],
            "maids": traits["Maid"],
            "shooters": traits["Shooter"],
            "warriors": traits["Warrior"],
            "json_adjusted": None,
        }
        for gender, base_folder in genders.iteritems():
            for group, trait in groups.iteritems():
                group_path = os.path.join(dir, base_folder, group)
                if not os.path.isdir(group_path):
                    continue
                for folder in os.listdir(group_path):
                    _path = os.path.join(group_path, folder)
                    if os.path.isdir(_path):
                        tagdb.load_tags_folder(folder, _path)

                    id = folder
                    if females is males:
                        # tagger -> prepare json data
                        data = OrderedDict()
                        if trait is None and id in json_data:
                            # JSON adjusted
                            data["basetraits"] = json_data[id]
                        data["id"] = id
                        data["_path_to_imgfolder"] = _path
                        females[id] = data
                        continue
                    # Allow database to be rebuilt but go no further.
                    if folder in exist:
                        continue

                    elements = None
                    if trait is None: # JSON
                        base = []
                        if id in json_data:
                            for t in json_data[id]:
                                if t in traits:
                                    base.append(traits[t])
                                else:
                                    char_debug("%s basetrait is unknown for %s!" % (t, id))
                    elif group == "assassins":
                        base = [trait]
                    elif group == "healers":
                        base = [trait, traits["Mage"]]
                        elements = [traits["Light"]]
                        if dice(50):
                            elements.append(traits["Water"])
                        if dice(50):
                            elements.append(traits["Air"])
                    elif group == "knights":
                        base = [trait]
                        if dice(50):
                            base.append(traits["Assassin"] if dice(50) else traits["Mage"])
                    elif group == "mages":
                        base = [trait]
                    elif group == "maids":
                        base = [trait, traits["Warrior"]]
                    elif group == "shooters":
                        base = [trait]
                        if dice(50):
                            base.append(traits["Assassin"] if dice(50) else traits["Mage"])
                    else: # group == "warriors":
                        base = [trait]

                    if elements is None:
                        if traits["Mage"] in base:
                            elements = [random.choice(all_elements)]
                        else:
                            elements = [traits["Neutral"]]
                            
                    # Create the fighter entity
                    fighter = NPC()
                    fighter._path_to_imgfolder = _path
                    fighter.id = id
                    fighter.gender = gender
                    if '_' in id:
                        fighter.name = get_first_name(gender)
                        fighter.fullname = " ".join([fighter.name, get_last_name()])
                    else:
                        fighter.name = id
                        fighter.full_name = id
                    fighter.nickname = fighter.name

                    for t in random.sample(base, min(2, len(base))):
                        fighter.traits.basetraits.add(t)
                        fighter.apply_trait(t)

                    for e in random.sample(elements, max(1, len(elements)-randrange(8))):
                        fighter.apply_trait(e)

                    for e in random.sample(random_traits, randint(1, len(random_traits))):
                        fighter.apply_trait(e)

                    fighter.init()

                    # register the fighter in the corresponding set
                    if gender == "female":
                        females[id] = fighter
                    else: # gender == "male":
                        males[id] = fighter

        return males, females
                            
    def load_mobs():
        content = load_db_json("mobs.json")
        mobs = dict()

        for mob in content:
            if "id" not in mob:
                mob["id"] = mob["name"]
            # mob["defeated"] = 0 # We need to track if the mob was defeated for bestiary.

            # make sure the following fields exist so we do not have to check at runtime
            for field in ["attack_skills", "magic_skills", "traits", "basetraits"]:
                if field not in mob:
                    mob[field] = []
            for field in ["stats", "skills"]:
                if field not in mob:
                    mob[field] = {}
            if "min_lvl" not in mob:
                mob["min_lvl"] = 1
            # validate data
            for skill in mob["skills"]:
                if not is_skill(skill):
                    raise Exception("Skill: %s for Mob with id: %s is invalid!" % (skill, mob["id"]))
            front_row = mob.get("front_row", 0)
            if front_row not in [0, 1]:
                mob["front_row"] = 1 if front_row else 0
            mobs[mob["id"]] = mob
        return mobs

    def load_buildings():
        # Load 'static' data of the upgrades
        json_data = load_db_json("buildings/upgrades.json")
        idx = 0
        for upgrade in json_data:
            up = getattr(store, upgrade.pop('class'))

            for key, value in upgrade.iteritems():
                setattr(up, key, value)

            idx += 1
            up.ID = idx

        # Load 'static' data of the businesses
        json_data = load_db_json("buildings/businesses.json")
        idx = 0
        for business in json_data:
            b = getattr(store, business.pop('class'))

            for key, value in business.iteritems():
                setattr(b, key, value)

            idx += 1
            b.ID = idx

        # Load json data of the buildings and the corresponding adverts
        adverts_data = load_db_json("buildings/adverts.json")
        buildings_data = load_db_json("buildings/buildings.json")
        # Populate into building objects:
        buildings = dict()
        idx = 0
        for building in buildings_data:
            b = Building()

            # Create a list of allowed business-instances
            allowed_businesses = building.pop("allowed_businesses", [])
            for business in allowed_businesses:
                if isinstance(business, basestring):
                    cls = business
                    business = {}
                else:
                    cls = business.pop('class')
                bu = getattr(store, cls)
                bu = bu()
                bu.building = b

                # create the list of allowed upgrade instances
                allowed_upgrades = business.pop("allowed_upgrades", bu.allowed_upgrades)
                bu.allowed_upgrades = []
                for u in allowed_upgrades:
                    u = getattr(store, u)
                    u = u()
                    u.building = b
                    bu.allowed_upgrades.append(u)
                
                for key, value in business.iteritems():
                    setattr(bu, key, value)
                b.allowed_businesses.append(bu)

            # create a list of advert-structs
            adverts = building.pop("adverts", [])
            for a in adverts_data:
                if a['name'] in adverts:
                    adv = {'active': False, 'price': 0, 'upkeep': 0}
                    adv.update(a)
                    b.adverts.append(adv)

            # add the prebuilt business-instances
            build_businesses = building.pop("build_businesses", [])
            for bu in b.allowed_businesses:
                if bu.__class__.__name__ in build_businesses:
                    b.build_business(bu)

            # create the list of allowed upgrade instances
            allowed_upgrades = building.pop("allowed_upgrades", [])
            for u in allowed_upgrades:
                u = getattr(store, u)
                u = u()
                u.building = b
                b.allowed_upgrades.append(u) 

            # populate the remaining data
            for key, value in building.iteritems():
                setattr(b, key, value)

            b.init()

            idx += 1
            b.id = idx
            buildings[idx] = b

        return buildings

    def load_traits():
        content = list()
        folder = content_path('db/traits')
        for file in os.listdir(folder):
            # New file "content/db/traits_chances.json" crashes this function as it matches the naming scheme for the traits files, but not the content scheme
            # Added check to remove it from consideration to prevent crashing, should look into changing its name, conforming to scheme, or better check.
            #
            if file.startswith("traits") and file.endswith(".json") and "_chances" not in file:
                in_file = content_path("".join(["db/traits/", file]))
                with open(in_file) as f:
                    content.extend(json.load(f))
        traits = dict()
        for trait in content:
            t = Trait()
            for attr in trait:
                setattr(t, attr, trait[attr])
            # validate traits so we do not have to do that runtime TODO create init method?
            temp = getattr(t, "leveling_stats", None)
            if temp is not None:
                for k in temp:
                    if not (is_stat(k) and k not in STATIC_CHAR.FIXED_MAX):
                        raise Exception("Invalid leveling stat %s in trait %s." % (k, t.id))
            temp = getattr(t, "init_lvlmax", None)
            if temp is not None:
                for k in temp:
                    if not is_stat(k):
                        raise Exception("Invalid init lvl max stat %s in trait %s." % (k, t.id))
            temp = getattr(t, "init_max", None)
            if temp is not None:
                for k in temp:
                    if not is_stat(k):
                        raise Exception("Invalid init max stat %s in trait %s." % (k, t.id))
            temp = getattr(t, "init_mod", None)
            if temp is not None:
                for k in temp:
                    if not is_stat(k):
                        raise Exception("Invalid init mod stat %s in trait %s." % (k, t.id))
            temp = getattr(t, "max", None)
            if temp is not None:
                for k in temp:
                    if not is_stat(k):
                        raise Exception("Invalid max stat %s in trait %s." % (k, t.id))
            temp = getattr(t, "min", None)
            if temp is not None:
                for k in temp:
                    if not is_stat(k):
                        raise Exception("Invalid min stat %s in trait %s." % (k, t.id))
            temp = getattr(t, "mod_stats", None)
            if temp is not None:
                for k in temp:
                    if k != "upkeep" and not is_stat(k):
                        raise Exception("Invalid mod stat %s in trait %s." % (k, t.id))
            temp = getattr(t, "init_skills", None)
            if temp is not None:
                for k in temp:
                    if not is_skill(k):
                        raise Exception("Invalid init skill %s in trait %s." % (k, t.id))
            temp = getattr(t, "mod_skills", None)
            if temp is not None:
                for k in temp:
                    if not is_skill(k):
                        raise Exception("Invalid mod skill %s in trait %s." % (k, t.id))

            # merge be modifiers into a single field
            for field in BE_Modifiers.FIELDS:
                if hasattr(t, field):
                    t.be_modifiers = BE_Modifiers(t)
                    break

            traits[t.id] = t

        # final checks
        for t in traits.values():
            temp = getattr(t, "blocks", None)
            if temp:
                for k in temp:
                    if k not in traits:
                        raise Exception("Invalid trait (%s) to block by %s trait." % (k, t.id))
                t.blocks = [traits[k] for k in temp] # store the references of traits instead of their names
        return traits

    def load_traits_context():
        # This should be reorganized later:
        traits = store.traits
        tgs = object() # TraitGoups!
        tgs.gents = [i for i in traits.itervalues() if i.gents]
        tgs.body = [i for i in traits.itervalues() if i.body]
        tgs.base = [i for i in traits.itervalues() if i.basetrait and not i.mob_only]
        tgs.elemental = [i for i in traits.itervalues() if i.elemental]
        tgs.real_elemental = [i for i in tgs.elemental if i.id != "Neutral"]
        tgs.el_names = set([i.id.lower() for i in tgs.elemental])
        tgs.ct = [i for i in traits.itervalues() if i.character_trait]
        tgs.sexual = [i for i in traits.itervalues() if i.sexual] # This is a subset of character traits!
        tgs.race = [i for i in traits.itervalues() if i.race]
        tgs.client = [i for i in traits.itervalues() if i.client]
        store.tgs = tgs

        # Base classes such as: {"SIW": [Prostitute, Stripper]}
        gen_occ_basetraits = defaultdict(set)
        for t in tgs.base:
            for occ in t.occupations:
                gen_occ_basetraits[occ].add(t)
        store.gen_occ_basetraits = dict(gen_occ_basetraits)

        # initialize static data of BE_Core (might not be the best place, but requires tgs...)
        BE_Core.init()

    def load_fg_areas():
        content = list()
        dir = content_path('db/maps')

        for file in os.walk(os.path.join(dir, '.')).next()[2]:
            if file.endswith(".json"):
                in_file = os.path.join(dir, file)
                with open(in_file) as f:
                    content.extend(json.load(f))

        areas, named_areas = dict(), dict()
        idx = 0
        for area in content:
            a = FG_Area()
            for attr in area:
                setattr(a, attr, area[attr])

            a.init()
            idx += 1
            a.id = idx
            areas[idx] = a
            named_areas[a.name] = a

        # post process to link ids instead of names
        for area in areas.values():
            if area.area:
                if area.area in named_areas:
                    area.area = named_areas[area.area].id
                else:
                    raise Exception("Unknown area '%s' referenced in map '%s'." % (area.area, area.name))
                unlocks = dict()
                for a, v in getattr(area, "unlocks", {}).items():
                    if a in named_areas:
                        a = named_areas[a]
                        unlocks[a.id] = v
                    else:
                        raise Exception("Unknown area '%s' to unlock by map '%s'." % (a, area.name))
                area.unlocks = unlocks

                for m in getattr(area, "mobs", []):
                    if m not in store.mobs:
                        raise Exception("Unknown mobs '%s' in map '%s'." % (m, area.name))

        # initialize the possible objects
        objects = load_db_json('maps/data/objects.json')
        om = dict()
        for o in objects:
            om[o['id']] = o

        for area in areas.values():
            if area.area is None:
                continue # skip main areas
            if hasattr(area, "allowed_objects"):
                allowed_objects = area.allowed_objects
                if not isinstance(allowed_objects, list):
                    allowed_objects = [allowed_objects]
                if len(allowed_objects) != 0 and allowed_objects[0] == "+":
                    # inherit objects from parent
                    allowed_objects = getattr(areas[area.area], "allowed_objects", []) + allowed_objects[1:]
            else:
                # map without set allowed_objects -> use its parent
                allowed_objects = getattr(areas[area.area], "allowed_objects", [])
            aos = OrderedDict()
            for o in allowed_objects:
                if isinstance(o, basestring):
                    o = { "id": o }
                id = o.get("id", None)
                # use the base object setting as default
                obj = om.get(id, None)
                if obj is None:
                    raise Exception("Unknown object '%s' referenced by map(or its parent) '%s'." % (id, area.name))
                obj = deepcopy(obj)
                # update the objects settings by the current attributes
                obj.update(o)
                curr_obj = aos.get(id, None)
                if curr_obj is None:
                    # no previous object with the same id -> done
                    aos[id] = obj
                else:
                    # use previous object as base if exist
                    curr_obj.update(obj)
            def to_object(o, idx):
                #t = []
                o["idx"] = idx[0]
                idx[0] += 1
                #for attr in o:
                #    t.append(attr)
                #temp = collections.namedtuple('temp', t)
                #result = temp(**o)
                result = FG_Object()
                for attr, value in o.items():
                    setattr(result, attr, value)
                return result
            idx = [0]
            area.allowed_objects = list(to_object(o, idx) for o in aos.values())

        return areas

    def load_aeq_purposes():
        data = load_db_json('items/aeq_purposes.json')

        for entry in data:
            id = entry.pop("id")

            if entry.get("fighting", False):
                STATIC_ITEM.FIGHTING_AEQ_PURPOSES.add(id)
            traits = entry.pop("traits", [])
            for t in traits:
                if t in STATIC_ITEM.TRAIT_TO_AEQ_PURPOSE:
                    raise Exception("Trait %s is already set for AEQ_PURPOSE %s, can not be set to %s" % (t, STATIC_ITEM.TRAIT_TO_AEQ_PURPOSE[t], id))
                STATIC_ITEM.TRAIT_TO_AEQ_PURPOSE[t] = id

            # validate the entry
            for t in entry:
                if t not in ["target_stats", "target_skills", "base_purpose", "fighting"]:
                    raise Exception("Unknown field %s in AEQ_PURPOSE %s." % (t, id))

            # convert or initialize these fields to sets
            for t in ("base_purpose", ):
                value = entry.get(t, None)
                value = set(value) if value else set()
                entry[t] = value
            # convert or initialize these fields to dicts
            for t in ("target_stats", "target_skills"):
                value = entry.get(t, None)
                if not value:
                    entry[t] = dict()
                elif not isinstance(value, dict):
                    raise Exception("Field %s of %s must be a map/dict or empty!" % (t, id)) 

            STATIC_ITEM.AEQ_PURPOSES[id] = entry

    def load_items():
        """
        Returns items dict with standard items and gift items to be used during girl_meets.
        """
        content = dict()
        dir = content_path('db/items')
        items = list()
        gifts = list()
        for file in os.walk(os.path.join(dir, '.')).next()[2]:
            if file.endswith(".json"):
                in_file = os.path.join(dir, file)
                if file.startswith("items"):
                    with open(in_file) as f:
                        items.extend(json.load(f))
                elif file.startswith("gifts"):
                    with open(in_file) as f:
                        gifts.extend(json.load(f))

        for item in items:
            iteminst = Item()
            for k, v in item.items():
                setattr(iteminst, k, v)
            iteminst.init()
            content[iteminst.id] = iteminst
        for item in gifts:
            iteminst = Item()
            iteminst.slot = "gift"
            iteminst.type = "gift"
            iteminst.sellable = True
            iteminst.tier = 0
            iteminst.__dict__.update(item)
            content[iteminst.id] = iteminst

        return content

    def load_dungeons():
        content = []
        dir = content_path('db/dungeons')

        for file in os.walk(os.path.join(dir, '.')).next()[2]:
            if file.endswith(".json"):
                in_file = os.path.join(dir, file)
                with open(in_file) as f:
                    content.extend(json.load(f))

        return { d['id']: Dungeon(**d) for d in content }

    def load_battle_skills():
        content = dict()
        battle_skills_data = load_db_json("battle_skills.json")
        fx_maps = ("attacker_action", "attacker_effects", "firing_effects", "projectile_effects", "main_effect", "dodge_effect", "target_sprite_damage_effect", "target_damage_effect", "target_death_effect", "bg_main_effect")

        for skill in battle_skills_data:
            constructor = globals()[skill.pop("class")]
            s = constructor()

            for key, value in skill.iteritems():
                if key in fx_maps:
                    getattr(s, key).update(value)
                elif key == "_DEBUG_BE":
                    if not DEBUG_BE:
                        break
                elif key == "_COMMENT":
                    pass
                else:
                    setattr(s, key, value)
            else:
                s.init()
                content[s.name] = s

        return content

    def start_image_predicition():
        """
        main_menu_predict = ["content/gfx/bg/main.webp",
                             "content/gfx/animations/main_menu/cloud1.webp",
                             "content/gfx/animations/main_menu/fire1.webp",
                             "content/gfx/animations/main_menu/fog1.webp",
                             "content/gfx/interface/icons/credits/dark_hole_idle.png",
                             "content/gfx/interface/icons/credits/dark_hole_hover.png",
                             "content/gfx/interface/icons/credits/x_hole_idle.png",
                             "content/gfx/interface/icons/credits/x_hole_hover.png",
                             "content/gfx/interface/icons/credits/patreonlogoorange.png",
                             "content/gfx/interface/buttons/main1.png",
                             "content/gfx/interface/buttons/flashing2.png",
                             "content/gfx/animations/main_menu/eyes/eyes*.webp",
                             "content/gfx/animations/main_menu/anim_logo/logo*.webp"]
        renpy.start_predict(*main_menu_predict)

        game_prefs_predict = ["content/gfx/interface/buttons/s_menu2.png",
                              "content/gfx/interface/buttons/s_menu2h.png"]
        renpy.start_predict(*game_prefs_predict)
        """        
        #main_img_predict = [item for sl in (("".join(["content/gfx/bg/locations/map_buttons/gismo/", key, ".webp"]),
        #                    "".join(["content/gfx/bg/locations/map_buttons/gismo/", key, "_hover.webp"]),
        #                    "".join(["content/gfx/interface/buttons/locations/", key, ".png"]))
        #                      for key in (i["id"] for i in pytfall.maps("pytfall")))
        #                    for item in sl]
        main_img_predict = ("bg gallery",
                            "bg pytfall",
                            "hearts_flow",
                            "shy_blush",
                            "hearts_rise",
                            "music_note",
                            "content/gfx/frame/h2.webp",
                            "content/gfx/frame/p_frame.png",
                            "content/gfx/frame/rank_frame.png",
                            "content/gfx/frame/frame_ap.webp",
                            "content/gfx/frame/window_frame2.webp",
                            "content/gfx/images/m_1.webp",
                            "content/gfx/images/m_2.webp",
                            #"content/gfx/images/fishy.png",
                            "content/gfx/interface/icons/exp.webp",
                            "content/gfx/interface/icons/gold.png",
                            "content/gfx/interface/icons/win_icon.png",
                            "content/gfx/interface/images/work.webp",
                            "content/gfx/interface/images/money_bag3.png",
                            "content/gfx/interface/buttons/compass.png",
                            "content/gfx/interface/buttons/IT2.png",
                            "content/gfx/interface/buttons/sl_idle.png",
                            "content/gfx/interface/buttons/journal1.png",
                            "content/gfx/interface/buttons/MS.png",
                            "content/gfx/interface/buttons/profile.png",
                            "content/gfx/interface/buttons/preference.png",
                            "content/gfx/interface/buttons/save.png",
                            "content/gfx/interface/buttons/load.png",
                            "content/gfx/interface/buttons/blue3.png",
                            "content/gfx/interface/buttons/locations/*.png",
                            "content/gfx/bg/locations/map_buttons/gismo/*.webp")

        # for i in store.items.values():
        #     main_img_predict.append(i.icon)
        renpy.start_predict(*main_img_predict)

        for scr in ("city_screen", "chars_list", "top_stripe"):
            renpy.start_predict_screen(scr)
