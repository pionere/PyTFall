label graveyard_town:
    $ iam.enter_location(goodtraits=["Undead", "Divine Creature", "Demonic Creature"],
                        badtraits=["Elf", "Android", "Monster", "Human", "Furry", "Slime"],
                        coords=[[.1, .55], [.5, .84], [.92, .45]])
    # Music
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("cemetery", fadein=.5)
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("graveyard_town"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.finish()

    scene bg graveyard_town
    with dissolve
    show screen graveyard_town

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_gm(result[1], img=result[1].show('girlmeets', type="first_default", label_cache=True,
                        exclude=["swimsuit", "wildness", "beach", "pool", "urban", "stage", "onsen", "indoors", "indoor"]))

        elif result[0] == 'control':
            $ renpy.hide_screen("graveyard_town")
            if result[1] == 'return':
                $ renpy.music.stop(channel="world")
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
                vbox:
                    align (.5, .6)
                    $ character, date = data[0], data[1]

                    if character.has_image('portrait', 'indifferent'):
                        $ char_profile_img = character.show('portrait', 'indifferent', resize=(data[4], data[4]), cache=True)
                    else:
                        $ char_profile_img = character.show('portrait', 'happy', resize=(data[4], data[4]), cache=True, type="reduce")

                    frame:
                        background Frame("content/gfx/frame/MC_bg.png")
                        add im.Sepia(char_profile_img) align .5, .5
                        xalign .5
                        xysize (data[4]+3, data[4]+3)

                    spacing 4

                    text ([character.name]) xalign .5 size data[5] style "content_text" color "black" outlines [(0, "goldenrod", 1, 2)]:
                        if len(character.name) > 14:
                            size data[5]-4

                    text ("[character.level] lvl") xalign .5 size data[5]-2 style "content_text" color "black" outlines [(0, "goldenrod", 1, 2)]

                    text ("[date]") xalign .5 size data[5]-2 style "content_text" color "black" outlines [(0, "goldenrod", 1, 2)]

    if num_chars > 1:
        $ img = "content/gfx/interface/buttons/next.png"
        $ img1 = im.Flip(img, horizontal=True)

        imagebutton:
            align (.415, .62)
            idle (img1)
            hover (im.MatrixColor(img1, im.matrix.brightness(.15)))
            action Return("next")
            keysym "mousedown_4"

        imagebutton:
            align (.59, .62)
            idle (img)
            hover (im.MatrixColor(img, im.matrix.brightness(.15)))
            action Return("prev")
            keysym "mousedown_5"

    vbox:
        style_group "wood"
        align (.9, .9)
        button:
            xysize (120, 40)
            yalign .5
            action Return("exit")
            text "Exit" size 15
            keysym "mousedown_3"

screen graveyard_town():

    use top_stripe(True)

    use location_actions("graveyard_town")

    if not iam.show_girls:
        $ img_cemetery = ProportionalScale("content/gfx/interface/icons/cemetery.png", 80, 80)
        $ img_mausoleum = ProportionalScale("content/gfx/interface/icons/mausoleum.png", 80, 80)
        $ img_time = ProportionalScale("content/gfx/interface/icons/clock.png", 100, 100)
        imagebutton:
            pos(93, 306)
            idle (img_time)
            hover (im.MatrixColor(img_time, im.matrix.brightness(.15)))
            action [Hide("graveyard_town"), Function(global_flags.set_flag, "keep_playing_music"), Jump("time_temple")]
            tooltip "Temple"
        imagebutton:
            pos(580, 220)
            idle (img_cemetery)
            hover (im.MatrixColor(img_cemetery, im.matrix.brightness(.15)))
            action [Hide("graveyard_town"), Jump("show_dead_list")]
            tooltip "Graves"
        imagebutton:
            pos(1090, 180)
            idle (img_mausoleum)
            hover (im.MatrixColor(img_mausoleum, im.matrix.brightness(.15)))
            action [Hide("graveyard_town"), Jump("enter_dungeon")]
            tooltip "Dungeon\nBeware all who enter here"

    if iam.show_girls:
        key "mousedown_3" action ToggleField(iam, "show_girls")
        add "content/gfx/images/bg_gradient.webp" yalign .45
        for entry, pos in zip(iam.display_girls(), iam.coords):
            hbox:
                align pos
                use rg_lightbutton(return_value=['jump', entry])
