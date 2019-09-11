label city_beach_left:
    scene bg city_beach_left

    $ pytfall.enter_location("city_beach_left", music=True, env="beach_main", coords=[(.15, .5), (.5, .45), (.7, .8)],
                             goodtraits=["Athletic", "Dawdler"], badtraits=["Scars", "Undead", "Furry", "Monster"])

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen city_beach_left
    with dissolve # dissolve the whole scene, not just the bg
    while 1:
        $ result = ui.interact()

        if result[0] == "jump":
            python hide:
                char = result[1]
                iam.start_int(char, img=iam.select_beach_img_tags(char))
        elif result[0] == "control":
            hide screen city_beach_left
            if result[1] == "return":
                jump city_beach
            elif result[1] == "cafe":
                jump city_beach_cafe_main
            elif result[1] == "fish":
                jump fishing_logic
            elif result[1] == "rest":
                jump mc_action_city_beach_rest

screen city_beach_left():
    use top_stripe(True)

    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Look Around":
            action Function(pytfall.look_around)
        textbutton "Meet Girls":
            action ToggleField(iam, "show_girls")

    if iam.show_girls:
        use interactions_meet
    else:
        # Jump buttons:
        $ img = im.Scale("content/gfx/interface/icons/beach_cafe.png", 80, 80)
        imagebutton:
            pos (380, 300)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "cafe"])
            tooltip "Beach Café"

        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80)
        imagebutton:
            align (.99, .5)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "return"])

        $ img = im.Scale("content/gfx/interface/icons/beach_fishing.png", 90, 90)
        imagebutton:
            pos(960, 400)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "fish"])
            tooltip "Fishing Docks"


        $ img = im.Scale("content/gfx/interface/icons/beach_resting.png", 90, 90)
        imagebutton:
            pos (400, 545)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "rest"])
            tooltip "Rest"

label mc_action_city_beach_rest:
    show bg beach_rest with dissolve
    if hero.has_flag("dnd_rest_at_beach"):
        "You already relaxed at the beach today. Doing it again will lead to sunburns."
        jump city_beach_left
    $ hero.set_flag("dnd_rest_at_beach")

    if len(hero.team) > 1:
        python hide:
            global picture
            tags = ("rest", "bathing", "sleeping")
            tags = [(tag, 0) for tag in tags]
            tags.append((None, 6))
            tags = [(("beach", 3), ("no bg", 4), ("simple bg", 5)), (("swimsuit", 1), (None, 2)), tags]
            excluded = ["sex", "stripping"]
            picture = [char.show(*tags, exclude=excluded, resize=iam.IMG_SIZE, type="ptls") for char in hero.team if char != hero]

        if len(picture) == 1:
            show expression picture[0] at truecenter as temp1
            with dissolve
        elif len(picture) == 2:
            show expression picture[0] at center_left as temp1
            show expression picture[1] at center_right as temp2
            with dissolve
        $ del picture

        "You're relaxing at the beach with your team."

        $ members = []
        python hide:
            for member in hero.team:
                if member == hero:
                    continue
                if "Horny" not in member.effects:
                    continue
                if not iam.silent_check_for_bad_stuff(member):
                    continue
                if iam.gender_mismatch(member) or iam.incest(member):
                    continue
                if check_lovers(member) or member.get_stat("affection") >= 500:
                    members.append(member)

        if members:
            $ char = choice(members)
            hide temp1
            hide temp2
            # jump interactions_sex_scene_begins

            python hide:
                global msg, picture
                if hero.gender == "male":
                    tags = ["bc handjob", "bc blowjob", "bc footjob"]
                    if char.gender == "female":
                        tags.append("bc titsjob")
                    msg = "Unfortunately %s forgot %s sunscreen today, so you had no choice but to provide another liquid as a replacement." % (char.name, char.pd) 
                else:
                    if char.gender == "male":
                        tags = ("2c handjob", "2c blowjob", "2c footjob", "2c titsjob")
                        msg = "Unfortunately you forgot your sunscreen today, so you had no choice but to use a replacement."
                    else: 
                        tags = ("bc hug", "2c hug")
                        msg = "Unfortunately you forgot your sunscreen today and %s already applied hers. You had no choice but to use her body." % char.name

                tags = [(tag, 0) for tag in tags]
                tags.append((None, 6))
                tags = [(("beach", 3), ("no bg", 4), ("simple bg", 5)), (("swimsuit", 1), (None, 2)), tags]
                excluded = ["rape", "bdsm", "group", "forced", "sad", "angry", "in pain"]
                picture = char.show(*tags, exclude=excluded, resize=iam.IMG_SIZE, type="ptls")

            show expression picture at truecenter with dissolve

            $ narrator(msg)
            $ char.gfx_mod_skill("sex", 0, 1)
            $ hero.gfx_mod_skill("sex", 0, 1)
            $ hero.gfx_mod_stat("joy", randint(0, 1))
            $ char.gfx_mod_stat("disposition", 3)
            $ char.gfx_mod_stat("affection", affection_reward(char))
            $ del msg, picture, char
        $ del members

    else:
        "You're relaxing at the beach."

    python hide:
        for member in hero.team:
            member.gfx_mod_stat("vitality", randint(10, 15))
            if "Adventurous" not in member.traits:
                member.gfx_mod_stat("joy", randint(0, 1))
            if member != hero:
                member.gfx_mod_stat("disposition", 1)
                member.gfx_mod_stat("affection", affection_reward(member, .1))

    jump city_beach_left

label fishing_logic_mor_quest_part:
    if hero.has_flag("dnd_mor_fish_quest"):
        $ fish, num = hero.flag("dnd_mor_fish_quest")
        if fish is None:
            # quest already done today
            m "Sorry, I don't have anything else at the moment. Maybe tomorrow."
            $ del fish, num
            return
        # no rerolling quest after asking again at the same day
    else:
        # roll a fish to catch
        $ fish = hero.get_skill("fishing")
        $ fish = list(i for i in items.values() if i.type == "fish" and "Fishing" in i.locations and 10 <= i.price <= fish)
        if not fish:
            m "Yeah, I have special requests sometimes, but you need to learn something about fishing for a start. Practice a bit, ok?"
            $ del fish
            return

        $ fish = random.choice(fish)
        $ num = locked_random("randint", 3, 10)
        $ hero.set_flag("dnd_mor_fish_quest", (fish, num))
    m "I need some [fish.id]. About [num] should be enough. Think you can handle it?"
    menu:
        "Yes":
            m "Awesome!"
            $ advance_quest("Fishery", "Mor asked you to catch some %s, about %s should be sufficient." % (fish.id, num), to=1, clear_logs=True, fish=fish, num_fish=num)
        "No":
            m "Your choice. You know where to find me."
    $ del fish, num
    return

label fishing_logic_mor_quest_bring:
    $ fish, num = q.flag("fish"), q.flag("num_fish")
    if hero.has_flag("dnd_mor_fish_quest"): # only one quest per day
        $ hero.set_flag("dnd_mor_fish_quest", (None, None))
    $ hero.remove_item(fish, num)
    $ price = fish.price * num * 4
    $ hero.add_money(price, reason="Quests")
    m "Magnificent. Take your reward, [price] coins, and these baits. It's much more than any city merchant can give you, trust me."
    if dice(20):
        $ hero.add_item("Magic Bait", 3)
        "You've obtained 3 Magic Baits!"
    elif dice(40):
        $ hero.add_item("Good Bait", 4)
        "You've obtained 4 Good Baits!"
    else:
        $ hero.add_item("Simple Bait", 6)
        "You've obtained 6 Simple Baits!"
    $ finish_quest("Fishery", "You brought required fish to Mor and got your reward.")
    $ del fish, num, price
    return

label fishing_logic_mor_dialogue:
    show expression npcs["Mor"].get_vnsprite() as npc
    with dissolve
    m "Hey, what's up?"
    menu Mor_dialogue_usual:
        "Fishing Requests" if q.stage != 1:
            call fishing_logic_mor_quest_part from _call_fishing_logic_mor_quest_part
            jump Mor_dialogue_usual
        "Bring the Fish" if (q.stage == 1 and has_items(q.flag("fish"), hero, equipped=False) >= q.flag("num_fish")):
            call fishing_logic_mor_quest_bring from _fishing_logic_mor_quest_bring
            jump Mor_dialogue_usual
        "Buy a Fishing Pole (250G)" if hero.gold >= 250:
            $ hero.take_money(250, reason="Items")
            $ hero.add_item("Fishing Pole")
            m "Nice, there you go! Happy fishing!"
            jump Mor_dialogue_usual
        "Ask about fishing":
            m "Oh, it's very simple. You only need a fishing rod and good eyes."
            m "And as my father used to say: 'The fastest fish are not always the best'... Or something along the lines..."
            m "Of course, you also can try diving to find something good in the water, but trust me, it won't be easy."
            jump Mor_dialogue_usual
        "Ask about fishing skill":
            m "Your catch is as good as your fishing skills. Practice makes perfect, so be sure to fish a lot if want something valuable!"
            m "You won't catch anything useful at first, but don't let it discourage you."
            m "Besides, my dad sometimes drinks in the tavern with his friends, you can ask them for some tips."
            jump Mor_dialogue_usual
        "Ask about bait":
            m "You don't have to use bait. Fishing poles already have a basic lure attached. But the real thing can help a lot."
            m "They allow more attempts than usual, plus the chance to catch something amazing is higher."
            m "But the better the bait, the more skill it requires. You won't be able to use them if your skill is too low."
            m "The General Shop sells them sometimes. But really good bait is not so easy to find."
            jump Mor_dialogue_usual
        "That's all for now":
            m "Okay. Bye!"
            hide npc with dissolve

label fishing_logic:
    # during fishing itself only practical part of skill could be improved; theoretical part will be available via items and asking fishermen in tavern
    scene bg fishing_bg with dissolve

    $ m = npcs["Mor"].say
    if not global_flags.has_flag('visited_fish_city_beach'):
        $ register_quest("Fishery")
        show expression npcs["Mor"].get_vnsprite() as npc
        with dissolve
        "A small boy fishes on the pier. Noticing you, he puts his fishing rod on the ground and approaches."
        m "Hey there, stranger! It looks like it's your first time here. Would you like to buy a Fishing Pole?"
        m "We offer a discount for newbies, so it's only 250 coins!"
        menu Mor_dialogue:
            "Who are you?":
                m "Me? I'm Mor. I'm helping my father. He's a fisherman. He usually takes a boat to catch more fish, and I stay here."
                jump Mor_dialogue
            "Buy the Pole" if hero.gold >= 250:
                $ hero.take_money(250, reason="Items")
                $ hero.add_item("Fishing Pole")
                m "Nice, there you go! Happy fishing!"
                m "If you have any questions about fishing, I'm usually here."
            "Don't buy the Pole":
                m "Fine by me. But you won't find it cheaper! I'm usually here if you change your mind."
        $ global_flags.set_flag('visited_fish_city_beach')
        hide npc with dissolve
    $ q = pytfall.world_quests.quest_instance("Fishery")
    menu beach_fighing_menu:
        "What do you want to do?"

        "Find Mor":
            jump fishing_logic_mor_dialogue
        "Check Mor requests" if q.stage != 1:
            show expression npcs["Mor"].get_vnsprite() as npc
            with dissolve
            call fishing_logic_mor_quest_part from _call_fishing_logic_mor_quest_part_1
            hide npc with dissolve
            jump beach_fighing_menu
        "Bring the Fish" if (q.stage == 1 and has_items(q.flag("fish"), hero, equipped=False) >= q.flag("num_fish")):
            show expression npcs["Mor"].get_vnsprite() as npc
            with dissolve
            call fishing_logic_mor_quest_bring from _fishing_logic_mor_quest_bring_1
            hide npc with dissolve
            jump beach_fighing_menu
        "Try Fishing (-1 AP)":
            $ del m, q
            jump mc_action_beach_start_fishing
        "Nothing":
            $ del m, q
            jump city_beach_left

label mc_action_beach_start_fishing:
    if not has_items("Fishing Pole", hero, equipped=True):
        "You don't have an equipped fishing rod at the moment. Try to get one from local shops."
        jump city_beach_left
    elif not hero.has_ap():
        "You don't have Action Points left. Try again tomorrow."
        jump city_beach_left
    else:
        $ min_fish_price = 0
        $ fishing_attempts = 3

        # bites increase min price of available items;
        # bites increase min price of available items; they are useless if skill is too low
        # so they only can be used with more or less high skillthey are useless if skill
        # is too low so they only can be used with more or less high skill
        python:
            fishing_skill = round_int(hero.get_skill("fishing"))
            c0 = (items["Simple Bait"] in hero.inventory and fishing_skill >= 30)
            c1 = (items["Good Bait"] in hero.inventory and fishing_skill >= 100)
            c2 = (items["Magic Bait"] in hero.inventory and fishing_skill >= 200)

        if any([c0, c1, c2]):
            menu:
                "Don't use any bait":
                    $ fishing_attempts = 3
                "Use Simple Bait" if c0:
                    $ min_fish_price += 10
                    $ hero.remove_item("Simple Bait")
                    $ fishing_attempts = 4
                "Use Good Bait" if c1:
                    $ min_fish_price += 50
                    $ hero.remove_item("Good Bait")
                    $ fishing_attempts = 5
                "Use Magic Bait" if c2:
                    $ min_fish_price += 100
                    $ hero.remove_item("Magic Bait")
                    $ fishing_attempts = 6
                "Cancel":
                    $ del c0, c1, c2, fishing_skill, fishing_attempts, min_fish_price
                    jump city_beach_left

        # Get a list of fishing items player is skilled enough to fish out (real fishes have doubled chance)
        $ loots = [(item, item.chance*2 if item.type == "fish" else item.chance) for item in items.values() if "Fishing" in item.locations and min_fish_price <= item.price <= fishing_skill]
        $ hero.take_ap(1)
        $ renpy.start_predict("content/gfx/images/fishy.png", "content/gfx/interface/icons/fishing_hook.png", "content/gfx/animations/bubbles_webm/movie.webm", "content/gfx/animations/bubbles_webm/mask.webm", "content/gfx/animations/water_texture_webm/movie.webm")
        image fishing_circles_webm = Transform(Movie(channel="main_gfx_attacks", play="content/gfx/animations/bubbles_webm/movie.webm", mask="content/gfx/animations/bubbles_webm/mask.webm"), zoom=.4, alpha=.4)
        image fishing_circles_webm_alpha = Transform(Movie(channel="main_gfx_attacks", play="content/gfx/animations/bubbles_webm/movie.webm", mask="content/gfx/animations/bubbles_webm/mask.webm"), zoom=.8, alpha=1.0)
        image water_texture__ = Movie(channel="movie", play="content/gfx/animations/water_texture_webm/movie.webm")
        while fishing_attempts > 0:
            $ fishing_attempts -= 1
                
            $ num_fish = randint(1 + (hero.get_stat("luck")/7), 8)

            call screen fishing_area(num_fish)

            $ stop_fishing = _return
            $ setattr(config, "mouse", None)

            if stop_fishing:
                $ exit_string = "This is tiring, back to the beach!"
                jump end_fishing 
                   
            $ item = weighted_choice(loots)
            if item is None:
                $ exit_string = "Damn' it got away..."
                jump end_fishing

            $ hero.add_item(item)
            $ gfx_overlay.random_find(item, 'fishy')

            $ renpy.pause(.5, hard = True)
            pause .5

            # the less item's chance field, the more additional bonus to fishing;
            # with 90 chance it will be +1, with less than 1 chance about 10
            python hide:
                temp = round_int((100-item.chance)*.1) + randint(1, 2)
                hero.gfx_mod_skill("fishing", 0, temp)

label end_fishing:
    $ renpy.stop_predict("content/gfx/images/fishy.png", "content/gfx/interface/icons/fishing_hook.png", "content/gfx/animations/bubbles_webm/movie.webm", "content/gfx/animations/bubbles_webm/mask.webm", "content/gfx/animations/water_texture_webm/movie.webm")
    $ hero.say(getattr(store, "exit_string", "This is all for now."))
    # safe(r) cleanup:
    python hide:
        cleanup = ["fishing_attempts", "min_fish_price",
                  "c0", "c1", "c2", "fishing_skill",
                  "num_fish", "stop_fishing", "exit_string",
                  "item", "loots"]
        for i in cleanup:
            if hasattr(store, i):
                delattr(store, i)
    jump city_beach_left

screen fishing_area(num_fish):
    hbox:
        xsize 1280
        box_wrap True
        for i in xrange(15):
            add "water_texture__"

    for i in range(0, num_fish):
        imagebutton:
            at random_fish_movement # Randomization is now done here.
            idle "fishing_circles_webm"
            hover "fishing_circles_webm_alpha"
            action Return(False)
            hovered SetField(config, "mouse", {"default": [("content/gfx/interface/icons/fishing_hook.png", 20, 20)]})
            unhovered SetField(config, "mouse", None)
    key "mousedown_3" action (Hide("fishing_area"), Return(True))
