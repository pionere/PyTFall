init python:
    def appearing_for_city_map(mode="hide"):
        for key in pytfall.maps("pytfall"):
            if key.get("appearing", False) and not key.get("hidden", False):
                idle_img = "".join(["content/gfx/bg/locations/map_buttons/gismo/", key["id"], ".webp"])
                if mode == "show":
                    appearing_img = Appearing(idle_img, 50, 200, start_alpha=.1)
                    pos = key["pos"]
                    renpy.show(idle_img, what=appearing_img, at_list=[Transform(pos=pos)], layer="screens", zorder=2)
                elif mode == "hide":
                    renpy.hide(idle_img, layer="screens")

label city:
    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("pytfall")
    $ global_flags.del_flag("keep_playing_music")

    scene bg pytfall
    show screen city_screen
    with dissolve

    while 1:
        $ result = ui.interact()

        if result[0] == 'control':
            if result[1] == 'return':
                $ global_flags.set_flag("keep_playing_music")
                $ global_flags.del_flag("mc_home_location")
                hide screen city_screen
                with dissolve
                jump mainscreen
        elif result[0] == 'location':
            hide screen city_screen
            jump expression result[1]


screen city_screen():
    on "show":
        action Function(appearing_for_city_map, "show")
    on "hide":
        action Function(appearing_for_city_map, "hide")

    # Keybind as we don't use the topstripe here anymore:
    key "mousedown_3" action Return(['control', 'return'])

    default maps = pytfall.maps("pytfall")
    default loc_list = ["main_street", "arena_outside", "slave_market", "city_jail", "tavern_town",
                        "city_parkgates", "academy_town", "mages_tower", "village_town",
                        "graveyard_town", "city_beach", "forest_entrance", "hiddenvillage_entrance"]
    default selected = None

    add "content/gfx/images/m_1.webp" align (1.0, .0)

    $ prefix = "content/gfx/bg/locations/map_buttons/gismo/"
    for key in maps:
        if not key.get("hidden", False):
            $ keyid = key["id"]
            # Resolve images + Add Appearing where appropriate:
            $ idle_img = "".join([prefix, keyid, ".webp"])
            if key.get("appearing", False):
                $ hover_img = im.MatrixColor(idle_img, im.matrix.brightness(.08))
                $ idle_img = Transform(idle_img, alpha=.01)
            else:
                $ hover_img = "".join([prefix, keyid, "_hover.webp"])
            if "pos" in key:
                $ pos = key["pos"]
            else:
                $ pos = 0, 0
            button:
                style 'image_button'
                pos pos
                idle_background idle_img
                hover_background hover_img
                selected selected == keyid
                selected_background hover_img
                focus_mask True
                tooltip key["name"]
                action Return(['location', keyid])
                alternate Return(['control', 'return'])

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
            hover im.MatrixColor(img, im.matrix.brightness(.15))
            tooltip "Quest Journal"
            action ShowMenu("quest_log")
        $ img = im.Scale("content/gfx/interface/buttons/MS.png", 38, 37)
        imagebutton:
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(.15))
            action Return(["control", "return"])
            tooltip "Return to Main Screen"
        $ img = im.Scale("content/gfx/interface/buttons/profile.png", 35, 40)
        imagebutton:
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(.15))
            action [SetField(pytfall.hp, "came_from", last_label), Hide(renpy.current_screen().tag), Jump("hero_profile")]
            tooltip "View Hero Profile"
        $ img = im.Scale("content/gfx/interface/buttons/save.png", 40, 40)
        imagebutton:
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(.15))
            tooltip "QuickSave"
            action QuickSave()
        $ img = im.Scale("content/gfx/interface/buttons/load.png", 38, 40)
        imagebutton:
            idle img
            hover im.MatrixColor(img, im.matrix.brightness(.15))
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

    add ProportionalScale("content/gfx/frame/frame_ap.webp", 155, 50) pos (1040, 90)
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
        xysize(172, 188)
        viewport id "locations":
            draggable True
            mousewheel True
            child_size (170, 1000)
            has vbox style_group "dropdown_gm2" spacing 2
            $ prefix = "content/gfx/interface/buttons/locations/"
            for key in maps:
                $ keyid = key["id"]
                if keyid in loc_list and not key.get("hidden", False):
                    imagebutton:
                        xysize (160, 28)
                        background Frame("".join([prefix, keyid, ".png"]), 5, 5)
                        idle Null()
                        hover Frame("content/gfx/interface/buttons/f1.png", -8, -8)
                        hovered SetScreenVariable("selected", keyid)
                        unhovered SetScreenVariable("selected", None)
                        action Return(['location', keyid])
                        #tooltip key['name']

        vbar value YScrollValue("locations")
