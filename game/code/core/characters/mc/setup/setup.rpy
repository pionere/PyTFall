label mc_setup:
    $ persistent.intro = True
    $ fighters = load_characters("fighters", NPC)
    python:
        male_sprites = []
        female_sprites = []
        for fighter in fighters.itervalues():
            if fighter.gender == "male":
                male_sprites.append(fighter)
            else:
                female_sprites.append(fighter)
    $ mc_stories = load_db_json("mc_stories.json")

    $ main_story = None # Fathers occupation
    $ sub_story = None # Father specific occupation
    $ mc_story = None # MCs mother
    $ mc_substory = None # MCs heritage

    scene bg mc_setup
    show screen mc_setup
    with dissolve
    play music "content/sfx/music/world/foregone.ogg" fadein 1.0 fadeout 1.0

    $ global_flags.set_flag("game_start")

    while 1:
        $ result = ui.interact()
        if isinstance(result, basestring):
            $ renpy.notify(traits[result].desc)

        elif result[0] == "control":
            if result[1] == "build_mc":
                $ fighter = result[2]

                jump mc_setup_end

        elif result[0] == "rename":
            $ n = None
            if result[1] == "name":
                $ n = renpy.call_screen("pyt_input", hero.name, "Enter Name", 20)
                if len(n):
                    $ hero.name = n
                    $ hero.nickname = hero.name
                    $ hero.fullname = hero.name
            elif result[1] == "nick":
                $ n = renpy.call_screen("pyt_input", hero.name, "Enter Name", 20)
                if len(n):
                    $ hero.nickname = renpy.call_screen("pyt_input", hero.name, "Enter Nick Name", 20)
            elif result[1] == "full":
                $ n = renpy.call_screen("pyt_input", hero.name, "Enter Full Name", 20)
                if len(n):
                    $ hero.fullname = n
            $ del n

label mc_setup_end:
    $ renpy.scene(layer='screens')
    scene black

    python hide:
        """
        main_story: Merchant
        substory: Caravan
        mc_story: Defender
        mc_substory: Sword
        """
        # cleanup of the fighters:
        del fighters[fighter.id]
        for char in fighters.itervalues():
            char.clear_img_cache()

        # We build the MC here. First we get the classes player picked in the choices screen and add those to MC:
        hero._path_to_imgfolder = fighter._path_to_imgfolder
        hero.id = fighter.id

        temp = set()
        for story in [mc_substory, mc_story, sub_story, main_story]:
            t = story.pop("class", None)
            if t is not None:
                temp.add(t)
                if len(temp) == 2:
                    break
        for t in temp:
            t = traits[t]
            hero.traits.basetraits.add(t)
            hero.apply_trait(t)

        SCROLLS = {"fire": ["Fire Scroll", "Fira Scroll", "Firaga Scroll", "Firaja Scroll", "Fireball Scroll", "Solar Flash Scroll"],
                   "water": ["Water Scroll", "Watera Scroll", "Waterga Scroll", "Waterja Scroll", "Last Drop Scroll", "Geyser Scroll"],
                   "air": ["Aero Scroll", "Aerora Scroll", "Aeroga Scroll", "Aeroja Scroll", "Pressure Scroll", "Air Blast Scroll"],
                   "earth": ["Stone Scroll", "Stonera Scroll", "Stonega Scroll", "Stoneja Scroll", "Breach Scroll", "Transmutation Scroll"],
                   "electricity": ["Thunder Scroll", "Thundara Scroll", "Thundaga Scroll", "Thundaja Scroll", "Ion Blast Scroll", "Electromagnetism Scroll"],
                   "ice": ["Blizzard Scroll", "Blizzara Scroll", "Blizzarga Scroll", "Blizzarja Scroll", "Ice Blast Scroll", "Zero Prism Scroll"],
                   "darkness": ["Dark Scroll", "Darkra Scroll", "Darkga Scroll", "Darkja Scroll", "Eternal Gluttony Scroll", "Black Hole Scroll", "Poison Scroll"],
                   "light": ["Holy Scroll", "Holyra Scroll", "Holyda Scroll", "Holyja Scroll", "Star Light Scroll", "Photon Blade Scroll", "Restoration Scroll", "Revive Scroll"] }

        for story in [main_story, sub_story, mc_story, mc_substory]:
            name = story.pop("name", None)
            temp = story.pop("header", None)
            temp = story.pop("desc", None)
            temp = story.pop("img", None)
            temp = story.pop("choices", None)
            temp = story.pop("gender", None)
            temp = story.pop("traits", None)
            if temp:
                if isinstance(temp, basestring):
                    temp = [temp]
                for t in temp:
                    t = traits[t]
                    hero.apply_trait(t)

            temp = story.pop("bonus", None)
            if temp:
                if temp == "arena_permit":
                    hero.arena_permit = True
                elif temp == "home":
                    # find the second cheapest building (ap) with rooms
                    ba = None #the cheapest building
                    ap = None
                    for b in buildings.values():
                        if b.rooms == 0:
                            continue
                        if ba is None:
                            ba = b
                        elif ba.price > b.price:
                            ap = ba
                            ba = b
                        elif ap is None or ap.price > b.price:
                            ap = b
                    if not ap:
                        ap = ba
                    if ap:
                        hero.buildings.append(ap)
                        hero.home = ap
                elif temp == "magic_skills":
                    give_tiered_magic_skills(hero, amount=[randint(2, 3), 0])
                elif temp == "magic_skill":
                    give_tiered_magic_skills(hero, amount=[1, 0])
                elif temp == "ap":
                    hero.basePP += 100 # PP_PER_AP
                elif isinstance(temp, list) and len(temp) > 1:
                    t = temp[0]
                    if t == "scrolls":
                        t = SCROLLS.get(temp[1], None)
                        if t is None:
                            raise Exception("Unknown element '%s' defined for scrolls in %s" % (temp[1], name))
                        temp = random.sample(t, 3)
                        for t in temp:
                            hero.add_item(items[t])
                    elif t == "gold":
                        hero.add_money(temp[1], "Inheritance")
                    elif t == "arena_rep":
                        hero.arena_rep += randint(*temp[1])
                    elif t == "battle_skill" and len(temp) > 2:
                        hero.default_attack_skill = battle_skills[temp[1]]
                    else:
                        raise Exception("Unrecognized bonus '%s'." % str(temp))
                else:
                    raise Exception("Unrecognized bonus '%s'." % str(temp))

            if len(story) != 0:
                raise Exception("Unrecognized parameters '%s' in story of '%s'." % (str(story), name))

        restore_battle_stats(hero) # We never really want to start with weakened MC?

        high_factor = partial(uniform, .5, .6)
        normal_factor = partial(uniform, .3, .4)

        stats = hero.stats
        base_stats = stats.get_base_stats()
        for s in ['constitution', 'intelligence', 'charisma', 'attack', 'magic', 'defence', 'agility']:
            if s in base_stats:
                value = high_factor()
            else:
                value = normal_factor()
            mod_by_max(hero, s, value)

        base_skills = stats.get_base_skills()
        for s in base_skills:
            value = high_factor()+.2
            # set skill to the given percentage
            stats.skills[s] = [0, 0] 
            value = round_int(hero.get_max_skill(s)*value)
            stats.mod_full_skill(s, value)

        # Add default workable building to MC, but only if we didn't add one in special labels.
        if not [b for b in hero.upgradable_buildings if b.is_business()]:
            # Find the cheapest business-building
            scary = None 
            for b in buildings.values():
                if not b.is_business():
                    continue
                if scary is None or scary.price > b.price:
                    scary = b
            if scary:
                hero.add_building(scary)

        # Add Home apartment (Slums) to MC, unless we have set him up with a home in special labels.
        if not hero.home:
            # Find the cheapest building with rooms
            home = None
            for b in buildings.values():
                if b.rooms == 0:
                    continue
                if home is None or home.price > b.price:
                    home = b
            if home:
                hero.home = home
                hero.add_building(home)

        # Set the default battle skill:
        if not hero.attack_skills:
            hero.attack_skills.append(hero.default_attack_skill)

        # Some money, barely enough to buy a slave and few items.
        hero.add_money(randint(2250, 2300), "Inheritance")

        hero.init()
        hero.log_stats()

    python:
        del fighter
        del female_sprites
        del male_sprites
        del mc_stories
        del mc_substory
        del mc_story
        del sub_story
        del main_story

    return

init: # MC Setup Screens:
    screen mc_setup():
        default sprites = male_sprites if hero.gender == "male" else female_sprites
        default index = 0
        default left_index = -1
        default right_index = 1

        # Rename and Start buttons + Classes are now here as well!!!:
        if getattr(store, "mc_substory", None):
            textbutton "Start Game" text_color "white" text_font "fonts/TisaOTB.otf" text_size 40 at fade_in_out():
                background Transform(Frame("content/gfx/interface/images/story12.png", 5, 5), alpha=1)
                hover_background Transform(Frame(im.MatrixColor("content/gfx/interface/images/story12.png", im.matrix.brightness(.15)), 5, 5), alpha=1)
                align (.46, .93)
                action [Stop("music"), Return(["control", "build_mc", sprites[index]])]
        vbox:
            # align (.37, .10)
            pos (365, 30)
            hbox:
                textbutton "Gender:" text_color "goldenrod" text_font "fonts/TisaOTM.otf" text_size 20:
                    background Transform(Frame("content/gfx/interface/images/story12.png", 5, 5), alpha=.8)
                    xpadding 12
                    ypadding 8
                $ ac_list = [Hide("mc_stories"), Hide("mc_sub_stories"), Hide("mc_sub_texts"),
                     SetVariable("sub_story", None), SetVariable("mc_story", None),
                     SetVariable("mc_substory", None), SetVariable("main_story", None)]
                if hero.gender == "male":
                    $ img = ProportionalScale("content/gfx/interface/icons/male.png", 30, 30)
                    $ temp = "female"
                    $ ss = female_sprites
                else:
                    $ img = ProportionalScale("content/gfx/interface/icons/female.png", 30, 30)
                    $ temp = "male"
                    $ ss = male_sprites
                imagebutton:
                    idle img
                    hover im.MatrixColor(img, im.matrix.brightness(.20))
                    hover_background Transform(Frame("content/gfx/interface/images/story12.png", 1, 1), alpha=.8)
                    action ac_list + [Function(setattr, hero, "gender", temp), SetScreenVariable("sprites", ss)]
                    tooltip "Click to change gender"
                    xpadding 12
                    ypadding 8
            hbox:
                textbutton "Height:" text_color "goldenrod" text_font "fonts/TisaOTM.otf" text_size 20:
                    background Transform(Frame("content/gfx/interface/images/story12.png", 5, 5), alpha=.8)
                    xpadding 12
                    ypadding 8
                $ heights = ["short", "average", "tall"]
                textbutton hero.height.capitalize() text_color "white" text_hover_color "red" text_font "fonts/TisaOTM.otf" text_size 20:
                    background Transform(Frame("content/gfx/interface/images/story12.png", 5, 5), alpha=.8)
                    hover_background Transform(Frame(im.MatrixColor("content/gfx/interface/images/story12.png", im.matrix.brightness(.15)), 5, 5), alpha=1)
                    action SetField(hero, "height", heights[(heights.index(hero.height)+1)%len(heights)])
                    tooltip "Click to change height"
                    xpadding 12
                    ypadding 8
            hbox:
                textbutton "Name:" text_color "goldenrod" text_font "fonts/TisaOTM.otf" text_size 20:
                    background Transform(Frame("content/gfx/interface/images/story12.png", 5, 5), alpha=.8)
                    xpadding 12
                    ypadding 8
                textbutton str(hero.name) text_color "white" text_hover_color "red" text_font "fonts/TisaOTM.otf" text_size 20:
                    background Transform(Frame("content/gfx/interface/images/story12.png", 5, 5), alpha=.8)
                    hover_background Transform(Frame(im.MatrixColor("content/gfx/interface/images/story12.png", im.matrix.brightness(.15)), 5, 5), alpha=1)
                    action Show("char_rename", char=hero)
                    tooltip "Click to change name"
                    xpadding 12
                    ypadding 8

        # MC Sprites:
        hbox:
            spacing 10
            align (.463, .75)
            $ img = ProportionalScale("content/gfx/interface/buttons/blue_arrow_left.png", 40, 40)
            imagebutton:
                yalign .5
                idle img
                hover im.MatrixColor(img, im.matrix.brightness(.20))
                activate_sound "content/sfx/sound/sys/hover_2.wav"
                action [SetScreenVariable("index", (index - 1) % len(sprites)),
                        SetScreenVariable("left_index", (left_index - 1) % len(sprites)),
                        SetScreenVariable("right_index", (right_index - 1) % len(sprites))]
            frame:
                background Frame(Transform("content/gfx/interface/images/story12.png", alpha=.8), 10, 10)
                padding 15, 10
                text "Select your appearance" size 20 font 'fonts/TisaOTm.otf'
            $ img = ProportionalScale("content/gfx/interface/buttons/blue_arrow_right.png", 40, 40)
            imagebutton:
                yalign .5
                idle img
                hover im.MatrixColor(img, im.matrix.brightness(.20))
                activate_sound "content/sfx/sound/sys/hover_2.wav"
                action [SetScreenVariable("index", (index + 1) % len(sprites)),
                        SetScreenVariable("left_index", (left_index + 1) % len(sprites)),
                        SetScreenVariable("right_index", (right_index + 1) % len(sprites))]
        $ temp = Frame("content/gfx/frame/MC_bg3.png", 40, 40)
        frame:
            align .328, .53
            xysize (160, 220)
            background temp
            add im.Sepia(sprites[left_index].show("battle_sprite", resize=(140, 200), cache=True)) align .5, .5
        frame:
            align .586, .53
            xysize (160, 220)
            background temp
            add im.Sepia(sprites[right_index].show("battle_sprite", resize=(140, 200), cache=True)) align .5, .5
        frame:
            align .457, .356
            xysize (160, 220)
            background temp
            add sprites[index].show("battle_sprite", resize=(140, 200), cache=True) align .5, .5
        frame:
            pos 713, 37
            xysize (110, 110)
            background Frame("content/gfx/frame/MC_bg.png", 10, 10)
            add sprites[index].show("portrait", resize=(100, 100), cache=True) align .5, .5

        ### Background Story ###
        add "content/gfx/interface/images/story1.png" align (.002, .09)

        frame: # Text frame for Main Story (Merchant, Warrior, Scholar and Noble)
            background Frame(Transform("content/gfx/interface/images/story12.png", alpha=.8), 10, 10)
            pos 173, 16 anchor .5, .0
            padding 15, 10
            text "Select your origin" size 20 font 'fonts/TisaOTm.otf'

        hbox: # Fathers Main occupation:
            style_group "sqstory"
            pos (30, 65)
            spacing 17
            $ ac_list = [Hide("mc_stories"), Hide("mc_sub_stories"), Hide("mc_sub_texts"),
                         SetVariable("sub_story", None), SetVariable("mc_story", None),
                         SetVariable("mc_substory", None)]
            for branch in mc_stories:
                $ img = im.Scale(branch["img"], 50, 50, align=(.5, .5))
                $ sub_choices = branch.get("choices", None)
                button: ## Merchant ##
                    foreground im.Sepia(img, align=(.5, .5))
                    selected_foreground img
                    idle_foreground im.Sepia(img, align=(.5, .5))
                    hover_foreground im.MatrixColor(img, im.matrix.brightness(.15), align=(.5, .5))
                    if sub_choices:
                        action SelectedIf(main_story == branch), If(store.main_story == branch,
                                  false=ac_list + [SetVariable("main_story", branch),
                                   Show("mc_stories", transition=dissolve, choices=sub_choices)])

    screen mc_texts():
        tag mc_texts
        frame:
            pos (0, 350)
            ysize 370
            background Frame(Transform("content/gfx/frame/MC_bg.png", alpha=1), 30, 30)
            has vbox xsize 350
            if main_story:
                $ temp = main_story.get("header", "")
                if temp:
                    text str(temp) xalign .5 font "fonts/DeadSecretary.ttf" size 22
                $ temp = main_story.get("desc", "")
                if temp:
                    text str(temp) style "garamond" size 18
                use bonuses(main_story)
                if sub_story:
                    null height 15
                    vbox:
                        $ temp = sub_story.get("desc", "")
                        if temp:
                            text str(temp) style "garamond" size 18
                        use bonuses(sub_story)
    screen mc_stories(choices): # This is the fathers SUB occupation choice.
        tag mc_sub
        hbox:
            pos(0, 145)
            style_group "mcsetup"
            box_wrap True
            xsize 360
            for idx, branch in enumerate(choices):
                python:
                    img = im.Scale(branch["img"], 39, 39)
                    sub_choices = branch.get("choices", None)
                    if sub_choices:
                        sepia = False
                    else:
                        sepia = True
                        img = im.Sepia(img)
                button:
                    $ temp = branch.get("name", "")
                    if isinstance(temp, dict):
                        $ temp = temp[hero.gender]
                    if idx % 2:
                        text str(temp) align (1.0, .52)
                        add img align (.0, .5)
                    else:
                        text str(temp) align (.0, .52)
                        add img align (1.0, .5)
                    action SensitiveIf(not sepia), SelectedIf(store.sub_story==branch), If(store.sub_story==branch, false=[Hide("mc_sub_texts"), Hide("mc_texts"),
                                  SetVariable("mc_story", None), SetVariable("mc_substory", None), SetVariable("sub_story", branch),
                                  Show("mc_texts", transition=dissolve),
                                  Show("mc_sub_stories", transition=dissolve, choices=sub_choices)])

    screen mc_sub_stories(choices): # This is the MC occupation choice.
        if choices:
            hbox:
                pos 870, 50
                spacing 10
                for branch in choices:
                        vbox:
                            spacing 2
                            $ img = ProportionalScale(branch["img"], 150, 150, align=(.5, .5))
                            if branch != mc_story:
                                $ img = im.Sepia(img, align=(.5, .5))
                            button:
                                xalign .5
                                xysize (165, 165)
                                background Frame("content/gfx/frame/MC_bg.png", 10, 10)
                                idle_foreground img
                                hover_foreground im.MatrixColor(img, im.matrix.brightness(.10), align=(.5, .5))
                                action Hide("mc_sub_texts"), SetVariable("mc_story", branch), SetVariable("mc_substory", None), Show("mc_sub_texts", transition=dissolve)
                            $ sub_choices = branch.get("choices", None)
                            if sub_choices:
                                hbox:
                                    xalign .5
                                    spacing 1
                                    style_group "sqstory"
                                    for sub in sub_choices:
                                        if sub.get("gender", hero.gender) == hero.gender:
                                            $ img = ProportionalScale(sub["img"], 46, 46, align=(.5, .5))
                                            if mc_substory != sub:
                                                $ img = im.Sepia(img, align=(.5, .5))
                                            button:
                                                background Frame("content/gfx/frame/MC_bg.png", 10, 10)
                                                idle_foreground im.Sepia(img, align=(.5, .5))
                                                hover_foreground im.MatrixColor(img, im.matrix.brightness(.15), align=(.5, .5))
                                                selected_foreground img
                                                action SetVariable("mc_substory", sub), SensitiveIf(branch == mc_story), SelectedIf(mc_substory == sub), Show("mc_sub_texts", transition=dissolve)

    screen mc_sub_texts():
        tag mc_subtexts
        frame:
            background Frame(Transform("content/gfx/frame/MC_bg.png", alpha=1), 30, 30)
            anchor (1.0, 1.0)
            pos (1280, 721)
            xysize (450, 440)
            has vbox xmaximum 430 xfill True xalign .5
            $ temp = mc_story.get("name", None)
            if temp:
                text str(temp) font "fonts/DeadSecretary.ttf" size 28 xalign .5
                null height 10
            $ temp = mc_story.get("desc", None)
            if temp:
                text str(temp) style "garamond" size 18
                use bonuses(mc_story)
                null height 20
            if mc_substory:
                $ temp = mc_substory.get("name", None)
                if temp:
                    text str(temp) font "fonts/DeadSecretary.ttf" size 23 xalign .5
                    null height 5
                $ temp = mc_substory.get("desc", None)
                if temp:
                    text str(temp) style "garamond" size 18
                use bonuses(mc_substory)

    screen bonuses(branch):
        $ result = []
        $ temp = branch.get("class", None)
        if temp:
            $ result.append(set_font_color("+ %s Class" % temp, color="green"))
        $ temp = branch.get("traits", None)
        $ el2color = BE_Core.TYPE_TO_COLOR_MAP
        $ elMastery = {"Master of %s" % el.capitalize() : el for el in el2color}
        $ elem = None
        if temp:
            if isinstance(temp, basestring):
                $ temp = [temp]
            for t in temp:
                $ t_ = t.lower()
                if t_ in el2color:
                    $ elem = t_
                    $ color = el2color[t_]
                    $ t_ = "%s Elemental Ailment" % t
                elif t in elMastery:
                    $ elem = elMastery[t]
                    $ color = el2color[elem]
                    $ t_ = t
                else:
                    $ color = "green"
                    $ t_ = "%s Trait" % t
                $ t_ = set_font_color("%s" % t_, color=color)
                $ result.append(set_font_color("+ {a=%s}%s{/a}" % (t, t_), color=color))
        $ temp = branch.get("bonus", None)
        if temp:
            if temp == "arena_permit":
                $ result.append(set_font_color("+ Arena Permit", color="green"))
            elif temp == "home":
                $ result.append(set_font_color("+ Better Starting Home", color="green"))
            elif temp == "magic_skills":
                if elem in el2color:
                    $ color = el2color[elem]
                    $ temp = elem.capitalize()
                else:
                    $ color = "green"
                    $ temp = "?"
                $ result.append(set_font_color("+ Couple of %s Spells" % temp, color=color))
            elif temp == "magic_skill":
                if elem in el2color:
                    $ color = el2color[elem]
                    $ temp = elem.capitalize()
                else:
                    $ color = "green"
                    $ temp = "?"
                $ result.append(set_font_color("+ One %s Spell" % temp, color=color))
            elif temp == "ap":
                $ result.append(set_font_color("+ One Action Point", color="green"))
            elif isinstance(temp, list) and len(temp) > 1:
                $ t = temp[0]
                if t == "scrolls":
                    $ color = el2color.get(temp[1], "green")
                    $ result.append(set_font_color("+ Three Spell Scrolls", color=color))
                elif t == "gold":
                    $ result.append(set_font_color("+ %d Gold" % temp[1], color="gold"))
                elif t == "arena_rep":
                    $ result.append(set_font_color("+ Arena Reputation", color="green"))
                elif t == "battle_skill" and len(temp) > 2:
                    $ result.append(set_font_color("+ Special attack '%s' when fighting unarmed." % temp[1], color=temp[2]))
                else:
                    $ raise Exception("Unrecognized bonus '%s'." % str(temp))
            else:
                $ raise Exception("Unrecognized bonus '%s'." % str(temp))

        for bonus in result:
            text str(bonus) style "garamond" size 18