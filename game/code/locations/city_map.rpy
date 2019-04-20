init python:
    def appearing_for_city_map(mode="hide"):
        for key in pytfall.maps("pytfall"):
            if not key.get("hidden", False) and key.get("appearing", False):
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

    default loc_list = ["main_street", "arena_outside", "slave_market", "city_jail", "tavern_town",
                        "city_parkgates", "academy_town", "mages_tower", "village_town",
                        "graveyard_town", "city_beach", "forest_entrance", "hiddenvillage_entrance"]
    default selected = None

    add "content/gfx/images/m_1.webp" align (1.0, .0)

    for key in pytfall.maps("pytfall"):
        if not key.get("hidden", False):
            # Resolve images + Add Appearing where appropriate:
            $ idle_img = "".join(["content/gfx/bg/locations/map_buttons/gismo/", key["id"], ".webp"])
            if key.get("appearing", False):
                $ hover_img = im.MatrixColor(idle_img, im.matrix.brightness(.08))
                $ idle_img = Transform(idle_img, alpha=.01)
            else:
                $ hover_img = "".join(["content/gfx/bg/locations/map_buttons/gismo/", key["id"], "_hover.webp"])
            if "pos" in key:
                $ pos = key["pos"]
            else:
                $ pos = 0, 0
            button:
                style 'image_button'
                pos pos
                idle_background idle_img
                hover_background hover_img
                focus_mask True
                tooltip key["name"]
                action Return(['location', key["id"]])
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
        imagebutton:
            idle im.Scale("content/gfx/interface/buttons/journal1.png", 36, 40)
            hover im.MatrixColor(im.Scale("content/gfx/interface/buttons/journal1.png", 36, 40), im.matrix.brightness(.15))
            tooltip "Quest Journal"
            action ShowMenu("quest_log")
        imagebutton:
            idle im.Scale("content/gfx/interface/buttons/MS.png", 38, 37)
            hover im.MatrixColor(im.Scale("content/gfx/interface/buttons/MS.png", 38, 37), im.matrix.brightness(.15))
            action Return(["control", "return"])
            tooltip "Return to Main Screen"
        imagebutton:
            idle im.Scale("content/gfx/interface/buttons/profile.png", 35, 40)
            hover im.MatrixColor(im.Scale("content/gfx/interface/buttons/profile.png", 35, 40), im.matrix.brightness(.15))
            action [SetField(pytfall.hp, "came_from", last_label), Hide(renpy.current_screen().tag), Jump("hero_profile")]
            tooltip "View Hero Profile"
        imagebutton:
            idle im.Scale("content/gfx/interface/buttons/save.png", 40, 40)
            hover im.MatrixColor(im.Scale("content/gfx/interface/buttons/save.png", 40, 40), im.matrix.brightness(.15))
            tooltip "QuickSave"
            action QuickSave()
        imagebutton:
            idle im.Scale("content/gfx/interface/buttons/load.png", 38, 40)
            hover im.MatrixColor(im.Scale("content/gfx/interface/buttons/load.png", 38, 40), im.matrix.brightness(.15))
            tooltip "QuickLoad"
            action QuickLoad()

    ### ----> Mid buttons <---- ###
    add "coin_top" pos (1015, 58)
    $ g = gold_text(hero.gold)
    text g size 18 color "gold" pos (1052, 62) outlines [(1, "#3a3a3a", 0, 0)]
    button:
        style "sound_button"
        pos (1138, 55)
        xysize (35, 35)
        action [SelectedIf(not (_preferences.mute["music"] or _preferences.mute["sfx"])),
        If(_preferences.mute["music"] or _preferences.mute["sfx"],
        true=[Preference("sound mute", "disable"), Preference("music mute", "disable")],
        false=[Preference("sound mute", "enable"), Preference("music mute", "enable")])]

    add ProportionalScale("content/gfx/frame/frame_ap.webp", 155, 50) pos (1040, 90)
    text "[hero.AP]" style "TisaOTM" color "#f1f1e1" size 24 outlines [(1, "#3a3a3a", 0, 0)] pos (1143, 85)
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
            for loc in pytfall.maps("pytfall"):
                if loc["id"] in loc_list and not key.get("hidden", False):
                    button:
                        xysize (160, 28)
                        idle_background Frame(im.MatrixColor(prefix + loc["id"] + ".png", im.matrix.brightness(.10)), 5, 5)
                        hover_background Frame(im.MatrixColor(prefix + loc["id"] + "_hover.png", im.matrix.brightness(.15)), 5, 5)
                        hovered SetScreenVariable("selected", loc["id"])
                        unhovered SetScreenVariable("selected", None)
                        action Return(['location', loc["id"]])
                        tooltip loc['name']

        vbar value YScrollValue("locations")
