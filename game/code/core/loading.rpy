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
        data = json.load(file)
        return data

    def load_db_json(fn):
        path = "content/db/" + fn
        return load_json(path)

    def load_tags_folder(folder, path):
        img_set = set()
        for fn in os.listdir(path):
            if check_image_extension(fn):
                tags = fn.split("-")
                try:
                    del tags[0]
                    tags[-1] = tags[-1].split(".")[0]
                except IndexError:
                    raise Exception("Invalid file path for image: %s in folder %s" % (fn, path))
                for tag in tags:
                    if tag not in tags_dict:
                        raise Exception("Unknown image tag: %s, fn: %s, path: %s" % (tag, fn, path))
                    tagdb.tagmap[tags_dict[tag]].add(fn)
                # Adding filenames to girls id:
                img_set.add(fn)
        tagdb.tagmap[folder] = img_set

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

    def load_characters(path, cls):
        """Loads a Full character from JSON file.

        path: Path to main folder.
        class: Class to use in creating the character.

        This will walk through folders inside of a folder where the path leads, looking for JSONs and reading image tags off file names.
        """
        dir = content_path(path)
        dirlist = os.listdir(dir)
        content = dict()

        exist = getattr(store, "chars", {}).keys()
        exist.extend(getattr(store, "npcs", {}).keys())

        # Get to a folder with unique girl datafiles and imagefolders:
        for packfolder in os.walk(os.path.join(dir,'.')).next()[1]:
                # Load data files one after another.
                for file in os.walk(os.path.join(dir, packfolder, '.')).next()[2]:
                    if file.startswith("data") and file.endswith(".json"):
                        # Load the file:
                        in_file = os.sep.join([dir, packfolder, file])
                        char_debug("Loading from %s!"%str(in_file)) # Str call to avoid unicode
                        with open(in_file) as f:
                            ugirls = json.load(f)

                        # Apply the content of the file to the character:
                        for gd in ugirls: # We go over each dict one mainaining correct order of application:
                            if "id" not in gd:
                                # Only time we throw an error instead of writing to log.
                                raise Exception("No id was specified in %s JSON Datafile!" % str(in_file))

                            folder = id = gd["id"]
                            _path = os.sep.join([dir, packfolder, folder])
                            if os.path.isdir(_path):
                                # We load the new tags!:
                                load_tags_folder(folder, _path)

                            if id in exist:
                                continue

                            char = cls()
                            char.id = id
                            # We set the path to the character
                            # so we know where to draw images from:
                            setattr(char, "_path_to_imgfolder",
                                    "/".join(["content/{}".format(path),
                                              packfolder, folder]))

                            # Check if there is a gender:
                            if "gender" in gd:
                                char.gender = gd["gender"]

                            # @Review: We make sure all traits get applied first!
                            for key in ("blocked_traits", "ab_traits"):
                                if key in gd:
                                    _traits  = set()
                                    for t in gd[key]:
                                        if t in store.traits:
                                            _traits.add(store.traits[t])
                                        else:
                                            char_debug("%s trait is unknown for %s (In %s)!" % (t, gd["id"], key))
                                    setattr(char.traits, key, _traits)

                            # Get and normalize basetraits:
                            if "basetraits" in gd:
                                basetraits = set()
                                if gd["basetraits"]:
                                    for trait in gd["basetraits"]:
                                        if trait in traits:
                                            basetraits.add(traits[trait])
                                        else:
                                            char_debug("%s besetrait is unknown for %s!" % (trait, gd["id"]))

                                if len(basetraits) > 2:
                                    while len(basetraits) > 2:
                                        basetraits.pop()

                                # In case that we have basetraits:
                                if basetraits:
                                    char.traits.basetraits = basetraits

                                for trait in char.traits.basetraits:
                                    char.apply_trait(trait)

                            for key in ("personality", "breasts", "body", "race"):
                                if key in gd:
                                    trait = gd[key]
                                    if trait in traits:
                                        char.apply_trait(traits[trait])
                                    else:
                                        char_debug("%s %s is unknown for %s!" % (trait, key, gd["id"]))

                            if "elements" in gd:
                                for trait in gd["elements"]:
                                    if trait in traits:
                                        char.apply_trait(traits[trait])
                                    else:
                                        char_debug("%s element is unknown for %s!" % (trait, gd["id"]))

                            if "traits" in gd:
                                for trait in gd["traits"]:
                                    if trait in traits:
                                        char.apply_trait(traits[trait])
                                    else:
                                        char_debug("%s trait is unknown for %s!" % (trait, gd["id"]))

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
                            #         if char.stats.is_skill(skill):
                            #             char.stats.mod_full_skill(skill, value)
                            #         else:
                            #             devlog.warning("%s skill is unknown for %s!" % (skill, gd["id"]))
                            #     del gd["skills"]

                            if "default_attack_skill" in gd:
                                skill = gd["default_attack_skill"]
                                if skill in store.battle_skills:
                                    char.default_attack_skill = store.battle_skills[skill]
                                else:
                                    char_debug("%s JSON Loading func tried to apply unknown default attack skill: %s!" % (gd["id"], skill))

                            if "magic_skills" in gd:
                                # Skills can be either a list or a dict:
                                skills = gd["magic_skills"]
                                if isinstance(skills, list):
                                    pass
                                else:
                                    skills = skills.keys()
                                for skill in skills:
                                    if skill in store.battle_skills:
                                        skill = store.battle_skills[skill]
                                        char.magic_skills.append(skill)
                                    else:
                                        char_debug("%s JSON Loading func tried to apply unknown battle skill: %s!" % (gd["id"], skill))

                            for key in ("color", "what_color"):
                                if key in gd:
                                    if gd[key] in globals():
                                        color = getattr(store, gd[key])
                                    else:
                                        try:
                                            color = Color(gd[key])
                                        except:
                                            debug_str = "{} color supplied to {} is invalid!".format(gd[key], gd["id"])
                                            char_debug(debug_str)
                                            color = ivory
                                    char.say_style[key] = color

                            # Note: Location is later normalized in init method.
                            for key in ("name", "nickname", "fullname", "origin", "gold", "desc", "status", "location", "height", "full_race"):
                                if key in ["name", "nickname", "fullname"] and key in gd:
                                    if len(gd[key]) > 20:
                                        temp = gd[key][0:20]
                                        setattr(char, key, gd[key][0:20])
                                    else:
                                        setattr(char, key, gd[key])
                                elif key in gd:
                                    setattr(char, key, gd[key])

                            char.init() # Normalize!

                            # Tearing up:
                            # if "level" in gd:
                            #     initial_levelup(char, gd["level"])
                            #     del gd["level"]
                            if "tier" in gd:
                                tier = gd["tier"]
                                if isinstance(tier, dict):
                                    tier_up_to(char, **tier)
                                else:
                                    tier_up_to(char, tier)
                            else:
                                tier = uniform(.1, .4)
                                tier_up_to(char, tier)

                            item_up = gd.get("item_up", "auto")
                            if item_up == "auto":
                                if char.status == "slave":
                                    initial_item_up(char,
                                                    give_civilian_items=True,
                                                    give_bt_items=False)
                                else:
                                    initial_item_up(char,
                                                    give_civilian_items=True,
                                                    give_bt_items=True)
                            elif item_up:
                                initial_item_up(char,
                                                give_civilian_items=True,
                                                give_bt_items=True)

                            char.log_stats()

                            content[char.id] = char

        return content

    def load_random_characters():
        dir = content_path('rchars')
        dirlist = os.listdir(dir)
        content = dict()

        #exist = getattr(store, "rchars", {}).keys()

        # Loading all rgirls into the game:
        for packfolder in os.walk(os.path.join(dir,'.')).next()[1]:
            for file in os.walk(os.path.join(dir, packfolder, '.')).next()[2]:
                if file.startswith('data') and file.endswith('.json'):
                    # Load the file:
                    in_file = os.path.join(dir, packfolder, file)
                    char_debug("Loading from %s!"%str(in_file)) # Str call to avoid unicode
                    with open(in_file) as f:
                        rgirls = json.load(f)

                    for gd in rgirls:
                        # @Review: We will return dictionaries instead of blank instances of rGirl from now on!
                        # rg = rChar()
                        if "id" not in gd:
                            # Only time we throw an error instead of writing to log.
                            raise Exception("No id was specified in %s JSON Datafile!" % str(in_file))

                        folder = id = gd["id"]

                        # We load the new tags!:
                        _path = os.path.join(dir, packfolder, folder)
                        if os.path.isdir(_path):
                            load_tags_folder(folder, _path)

                        #if id in exist:
                        #    continue

                        # Set the path to the folder:
                        gd["_path_to_imgfolder"] = os.path.join("content", "rchars", packfolder, folder)

                        content[id] = gd

        return content

    def load_special_arena_fighters():
        females = getattr(store, "female_fighters", {})
        males = getattr(store, "male_fighters", {})
        exist = females.keys()
        exist.extend(males.keys())
        h = getattr(store, "hero")
        if h:
            exist.append(h.id)
        json_data_raw = load_db_json("arena_fighters.json")
        json_data = {}
        for i in json_data_raw:
            json_data[i["name"]] = i["basetraits"]

        tagdb = store.tagdb
        tags_dict = store.tags_dict

        random_traits = tuple(traits[t] for t in ["Courageous", "Aggressive", "Vicious"])
        all_elements = tuple(traits[i.id] for i in tgs.elemental)

        dir = content_path("fighters")
        genders = { "female": "females", "male": "males" }
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
                group_path = os.sep.join([dir, base_folder, group])
                if not os.path.isdir(group_path):
                    continue
                for folder in os.listdir(group_path):
                    _path = os.sep.join([group_path, folder])
                    if os.path.isdir(_path):
                        load_tags_folder(folder, _path)

                    # Allow database to be rebuilt but go no further.
                    if folder in exist:
                        continue
                    id = folder
                    path = os.sep.join(["content", "fighters", base_folder, group, folder])

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
                    fighter._path_to_imgfolder = path
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

                    for e in random.sample(elements, max(1, len(elements)-randint(0, 7))):
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
                    b.add_business(bu)

            # create the list of allowed upgrade-classes
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
            traits[t.id] = t
        return traits

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
                    devlog.warning("Unknown area '%s' referenced in map '%s'." % (area.area, area.name))
                unlocks = dict()
                for a, v in area.unlocks.items():
                    if a in named_areas:
                        a = named_areas[a]
                        unlocks[a.id] = v
                    else:
                        devlog.warning("Unknown area '%s' to unlock by map '%s'." % (a, area.name))
                area.unlocks = unlocks

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
                    devlog.warning("Unknown object '%s' referenced by map(or its parent) '%s'." % (id, area.name))
                    continue
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
            for attr in item:
                # We prolly want to convert to objects in case of traits:
                if attr in ("badtraits", "goodtraits"):
                    setattr(iteminst, attr, set(traits[i] for i in item[attr])) # More convinient to have these as sets...
                else:
                    setattr(iteminst, attr, item[attr])
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
        fx_maps = ("attacker_action", "attacker_effects", "main_effect", "dodge_effect", "target_sprite_damage_effect", "target_damage_effect", "target_death_effect", "bg_main_effect")

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