label graveyard_town:
    $ iam.enter_location(goodtraits=["Undead", "Divine Creature", "Demonic Creature"],
                        badtraits=["Elf", "Android", "Monster", "Human", "Furry", "Slime"],
                        coords=[[.1, .55], [.5, .84], [.92, .45]])
    # Music
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("cemetery", fadein=.5)
    $ global_flags.del_flag("keep_playing_music")

    scene bg graveyard_town
    with dissolve
    show screen graveyard_town

    while 1:
        $ result = ui.interact()

        if result[0] == "jump":
            $ iam.start_int(result[1], img=result[1].show('girlmeets', type="first_default", label_cache=True,
                        exclude=["swimsuit", "wildness", "beach", "pool", "urban", "stage", "onsen", "indoors", "indoor"]))

        elif result == ["control", "return"]:
            hide screen graveyard_town
            jump city

label show_dead_list:
    $ dead_chars = pytfall.afterlife.inhabitants # list of dead characters
    if not dead_chars:
        "You look around, but all tombstones are old and worn out. Nothing interesting."
        $ del dead_chars
        jump graveyard_town

    $ dead_chars = dead_chars.items()
    $ num_chars = len(dead_chars)
    $ number = randint(0, num_chars-1) # start from a random point

    show screen cemetry_list_of_dead_chars
    with dissolve

    hide screen graveyard_town
    with dissolve

    while 1:
        $ result = ui.interact()

        if result == "next":
            $ number -= 1
            if number < 0:
                $ number = num_chars-1
        elif result == "prev":
            $ number += 1
            if number == num_chars:
                $ number = 0
        elif result == "exit":
            hide screen cemetry_list_of_dead_chars
            with dissolve

            $ del dead_chars, num_chars, number
            jump graveyard_town
        elif result[0] == "place":
            $ result = result[1]
            python hide:
                hero.remove_item(result)
                char = dead_chars[number][0]
                flag = char.get_flag("cemetery_flowers", None)
                if flag is None:
                    flag = []
                    char.set_flag("cemetery_flowers", flag)
                flag.append([result, day])
                if dice(10) and not hero.has_flag("cnd_cemetery_flowers"):
                    hero.mod_stat("reputation", 1)
                    hero.set_flag("cnd_cemetery_flowers", day+7)
        elif result[0] == "take":
            $ result = result[1]
            python hide:
                char = dead_chars[number][0]
                flag = char.flag("cemetery_flowers")
                flag.remove(result)
                if not flag:
                    char.del_flag("cemetery_flowers")
                if result[1] == day:
                    hero.add_item(result[0])
                    if dice(10) and not hero.has_flag("cnd_cemetery_flowers"):
                        hero.mod_stat("reputation", -1)
                        hero.set_flag("cnd_cemetery_flowers", day+7)
                elif (result[1] + result[0].cblock) < day:
                    if dice(10) and not hero.has_flag("cnd_cemetery_flowers"):
                        hero.mod_stat("reputation", 1)
                        hero.set_flag("cnd_cemetery_flowers", day+7)

screen cemetry_list_of_dead_chars(): # the list should not be empty!
    python:
        data = dead_chars[number]
        data = [data[0], data[1]]   # 0-1. char, date
        data.append((.5, .5))       # 2. tombstone align
        data.append((234, 420))     # 3. tombstone size
        data.append(99)             # 4. portrait size
        data.append(18)             # 5. text/box size
        charslist = [None, data, None]
        if num_chars >= 3:
            num = (number-1)%num_chars
            data = dead_chars[num]
            data = [data[0], data[1]]   # 0-1. char, date
            data.append((.2, .6))       # 2. tombstone align
            data.append((180, 315))     # 3. tombstone size
            data.append(60)             # 4. portrait size
            data.append(14)             # 5. text/box size
            charslist[0] = data

            num = (number+1)%num_chars
            data = dead_chars[num]
            data = [data[0], data[1]]   # 0-1. char, date
            data.append((.8, .6))       # 2. tombstone align
            data.append((180, 315))     # 3. tombstone size
            data.append(60)             # 4. portrait size
            data.append(14)             # 5. text/box size
            charslist[2] = data

    for data in charslist:
        if data is not None:
            frame:
                align data[2]
                xysize data[3]
                background Frame(im.Scale("content/gfx/frame/tombstone.png", *data[3]))

                # Name, Level, Date:
                $ char, date = data[0], data[1]
                $ char_profile_img = char.show('portrait', 'indifferent', 'happy', resize=(data[4], data[4]), cache=True, type="first_default", add_mood=False)
                vbox:
                    align (.5, .6)
                    frame:
                        background Frame("content/gfx/frame/MC_bg.png")
                        add im.Sepia(char_profile_img) align .5, .5
                        xalign .5
                        xysize (data[4]+3, data[4]+3)

                    spacing 4

                    text char.name xalign .5 size data[5] style "content_text" color "black" outlines [(0, "goldenrod", 1, 2)]:
                        if len(char.name) > 14:
                            size data[5]-4

                    text ("%d lvl" % char.level) xalign .5 size data[5]-2 style "content_text" color "black" outlines [(0, "goldenrod", 1, 2)]

                    text str(date) xalign .5 size data[5]-2 style "content_text" color "black" outlines [(0, "goldenrod", 1, 2)]

                # Flowers:
                $ flowers = char.flag("cemetery_flowers")
                if flowers:
                    $ fsize = data[4]/2
                    viewport:
                        #ysize fsize
                        #xmaximum data[3][0]
                        xysize (min(data[3][0], len(flowers)*fsize), fsize)
                        align (.5, .98)
                        edgescroll (fsize, fsize)
                        has hbox
                        for f in flowers:
                            python:
                                item = f[0]
                                age = day - f[1]
                                bb = item.cblock
                                img = PyTGFX.scale_content(item.icon, fsize, fsize)
                                if age > 2 * bb:
                                    img = PyTGFX.sepia_content(img)
                                elif age > bb:
                                    img = PyTGFX.bright_content(img, -float(age - bb)/(2*bb))
                            imagebutton:
                                align (.5, .5)
                                idle img
                                hover PyTGFX.bright_content(img, .15)
                                action Return(["take", f])
                                tooltip "Take %s away" % item.id

    if num_chars > 1:
        $ img = "content/gfx/interface/buttons/next.png"
        $ img1 = im.Flip(img, horizontal=True)

        imagebutton:
            align (.415, .62)
            idle img1
            hover PyTGFX.bright_img(img1, .15)
            action Return("next")
            keysym "mousedown_4"

        imagebutton:
            align (.59, .62)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return("prev")
            keysym "mousedown_5"

    vbox:
        style_group "wood"
        align (.98, .9)
        for item in ("Blue Rose", "Red Rose", "Wild Flowers"):
            $ item = items[item]
            if has_items(item, hero, equipped=False):
                frame:
                    xysize (80, 80)
                    xalign .5
                    background Frame("content/gfx/frame/frame_it2.png", -1, -1)
                    $ img = PyTGFX.scale_content(item.icon, 70, 70)
                    imagebutton:
                        align (.5, .5)
                        idle img
                        hover PyTGFX.bright_content(img, .15)
                        action Return(["place", item])
                        tooltip "Place a %s" % item.id
        null height 10
        button:
            xysize (120, 40)
            yalign .5
            action Return("exit")
            text "Exit" size 15
            keysym "mousedown_3"

screen graveyard_town():
    use top_stripe(True)

    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Meet Girls":
            action ToggleField(iam, "show_girls")

    if iam.show_girls:
        use interactions_meet
    else:
        $ img = im.Scale("content/gfx/interface/icons/clock.png", 100, 100)
        imagebutton:
            pos (93, 306)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("graveyard_town"), Function(global_flags.set_flag, "keep_playing_music"), Jump("time_temple")]
            tooltip "Temple"
        $ img = im.Scale("content/gfx/interface/icons/cemetery.png", 80, 80)
        imagebutton:
            pos (580, 220)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("graveyard_town"), Jump("show_dead_list")]
            tooltip "Graves"
        $ img = im.Scale("content/gfx/interface/icons/mausoleum.png", 80, 80)
        imagebutton:
            pos (1090, 180)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("graveyard_town"), Jump("enter_dungeon")]
            tooltip "Dungeon\nBeware all who enter here"
