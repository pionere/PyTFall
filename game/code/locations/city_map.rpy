init python:
    def appearing_for_city_map(show):
        for key in pytfall.maps("pytfall"):
            if key.get("appearing", False) and not key.get("hidden", False):
                keyid = key["id"]
                if show is True:
                    img = "".join(["content/gfx/bg/locations/map_buttons/gismo/", keyid, ".webp"])
                    img = Appearing(img, 50, 200, start_alpha=.1)
                    renpy.show(keyid, what=img, at_list=[Transform(pos=key["pos"])], layer="screens", zorder=2)
                else: #if mode == "hide":
                    renpy.hide(keyid, layer="screens")

label city:
    scene bg pytfall
    $ pytfall.enter_location("city", music=True, env=None)

    show screen city_screen
    with dissolve # dissolve the whole scene, not just the bg
    while 1:
        $ result = ui.interact()

        hide screen city_screen
        if result[0] == "control":
            if result[1] == "return":
                $ global_flags.del_flag("mc_home_location")
                jump mainscreen
            elif result[1] == "hero":
                $ hero_profile_entry = "city"
                jump hero_profile
        elif result[0] == "location":
            jump expression result[1]


screen city_screen():
    on "show":
        action Function(appearing_for_city_map, True)
    on "hide":
        action Function(appearing_for_city_map, False)

    default locs = [l for l in pytfall.maps("pytfall") if not l.get("hidden", False)]
    default selected = None

    add "content/gfx/images/m_1.webp" align (1.0, .0)

    $ prefix = "content/gfx/bg/locations/map_buttons/gismo/"
    for key in locs:
        python:
            keyid = key["id"]
            # Resolve images + Add Appearing where appropriate:
            idle_img = "".join([prefix, keyid, ".webp"])
            if key.get("appearing", False):
                hover_img = PyTGFX.bright_img(idle_img, .08)
                idle_img = im.Alpha(idle_img, alpha=.01)
            else:
                hover_img = "".join([prefix, keyid, "_hover.webp"])
            pos = key["pos"]
        button:
            style "image_button"
            pos pos
            idle_background idle_img
            hover_background hover_img
            selected selected == keyid
            selected_background hover_img
            focus_mask True
            tooltip key["name"]
            action Return(["location", keyid])
            alternate Return(["control", "return"])

    add "content/gfx/frame/h2.webp"

    fixed:
        xysize (164, 78)
        pos (1111, 321)
        text "PyTFall" style "TisaOTMolxm" size 19 align (.5, .5)

    # Right frame:
    ### ----> Top buttons <---- ###
    hbox:
        pos (979, 4)
        spacing 4
        $ img = im.Scale("content/gfx/interface/buttons/journal1.png", 36, 40)
        imagebutton:
            idle img
            hover PyTGFX.bright_img(img, .15)
            tooltip "Quest Journal"
            action ShowMenu("quest_log")
        $ img = im.Scale("content/gfx/interface/buttons/MS.png", 38, 37)
        imagebutton:
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "return"])
            tooltip "Return to Main Screen"
            keysym "mousedown_3"
        $ img = im.Scale("content/gfx/interface/buttons/profile.png", 35, 40)
        imagebutton:
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "hero"])
            tooltip "View Hero Profile"
        $ img = im.Scale("content/gfx/interface/buttons/save.png", 40, 40)
        imagebutton:
            idle img
            hover PyTGFX.bright_img(img, .15)
            tooltip "QuickSave"
            action QuickSave()
        $ img = im.Scale("content/gfx/interface/buttons/load.png", 38, 40)
        imagebutton:
            idle img
            hover PyTGFX.bright_img(img, .15)
            tooltip "QuickLoad"
            action QuickLoad()

    ### ----> Mid buttons <---- ###
    add "coin_top" pos (1015, 58)
    $ temp = gold_text(hero.gold)
    text temp size 18 color "gold" pos (1052, 62) outlines [(1, "#3a3a3a", 0, 0)]
    button:
        style "sound_button"
        pos (1138, 55)
        xysize (35, 35)
        action [SelectedIf(not (_preferences.mute["music"] or _preferences.mute["sfx"])),
        If(_preferences.mute["music"] or _preferences.mute["sfx"],
        true=[Preference("sound mute", "disable"), Preference("music mute", "disable")],
        false=[Preference("sound mute", "enable"), Preference("music mute", "enable")])]

    add PyTGFX.scale_img("content/gfx/frame/frame_ap.webp", 155, 50) pos (1040, 90)
    $ temp = hero.PP / 100 # PP_PER_AP
    text str(temp) style "TisaOTM" color "#f1f1e1" size 24 outlines [(1, "#3a3a3a", 0, 0)] pos (1143, 85)
    fixed:
        pos (1202, 99)
        xsize 72
        text "Day [day]" style "TisaOTMolxm" color "#f1f1e1" size 18
    add "content/gfx/interface/buttons/compass.png" pos (1187, 15)

    add "content/gfx/images/m_2.webp"

    ### ----> Lower buttons (Locations) <---- ###
    side "c r":
        pos (1104, 132)
        xysize (172, 188)
        viewport id "locations":
            draggable True
            mousewheel True
            child_size (170, 1000)
            has vbox style_group "dropdown_gm2" spacing 2
            $ prefix = "content/gfx/interface/buttons/locations/"
            for key in locs:
                $ keyid = key["id"]
                imagebutton:
                    xysize (160, 28)
                    background Frame("".join([prefix, keyid, ".png"]), 5, 5)
                    idle Null()
                    hover Frame("content/gfx/interface/buttons/f1.png", -8, -8)
                    hovered SetScreenVariable("selected", keyid)
                    unhovered SetScreenVariable("selected", None)
                    action Return(["location", keyid])
                    #tooltip key['name']

        vbar value YScrollValue("locations")
