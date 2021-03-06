label mainscreen:
    scene black
    with dissolve

    if pytfall.enter_location("main_screen", music=True, env=None):
        # First Run (Fadeout added)
        $ PyTSFX.set_music(False)
        $ PyTSFX.queue_music(10)
        $ PyTSFX.set_music(True)

    show screen mainscreen
    if not persistent.showed_pyp_hint:
        $ persistent.showed_pyp_hint = True
        show screen tutorial

    $ pytfall.world_quests.run_quests("auto") # Run active quests
    $ pytfall.world_events.run_events("auto") # Run current events

    while 1:
        $ result = ui.interact()

        hide screen mainscreen
        jump expression result

screen mainscreen:
    python:
        hero_home = hero.home
        if global_flags.has_flag("game_start"):
            global_flags.del_flag("game_start")
            fadein = 2.0
            location = "mc_bedroom"
        elif global_flags.has_flag("day_start"):
            global_flags.del_flag("day_start")
            fadein = 0.5
            location = "mc_bedroom"
        else:
            fadein = 0
            hh, location = global_flags.get_flag("mc_home_location", [hero_home, "entry"])
            if hh != hero_home:
                location = "entry"
        global_flags.set_flag("mc_home_location", [hero_home, location])

        sections = getattr(hero_home, "sections", None)
        if sections is None:
            location = None
        else:
            section = sections.get(location, None)
            if isinstance(section, basestring):
                section = sections[section]
            if section is None:
                location = None
            else:
                location = section["img"]
                objects = section.get("objects", None)
                if objects is not None:
                    # filter objects
                    #  by dirt:
                    dirt = getattr(hero_home, "dirt", 0)
                    objects = [o for o in objects if o.get("dirt", 0) <= dirt]
                    #  by upgrade:
                    upgrades = [u.__class__.__name__ for u in getattr(hero_home, "upgrades", [])]
                    upgrades.append(None)
                    objects = [o for o in objects if o.get("upgrade", None) in upgrades]
                    #  by business:
                    businesses = [b.__class__.__name__ for b in getattr(hero_home, "businesses", [])]
                    businesses.append(None)
                    objects = [o for o in objects if o.get("business", None) in businesses]
                    #  by business-upgrade
                    business_upgrades = ["/".join(b.__class__.__name__,u.__class__.__name__) for b, upgrades in 
                                            [[b, b.upgrades] for b in getattr(hero_home, "businesses", [])] 
                                         for u in upgrades]
                    business_upgrades.append(None)
                    objects = [o for o in objects if o.get("business_upgrade", None) in business_upgrades]

        if location is None:
            location = "content/buildings/Rooms/street.webp"
            objects = None

    # Home pic + objects:
    frame:
        xysize (config.screen_width, config.screen_height)
        xalign .5
        padding 0, 0
        margin 0, 0
        background PyTGFX.get_content(location)
        at fade_from_to(.0, 1.0, fadein)
    # Overlay objects
        if objects:
            $ objects.sort(key=lambda x: x.get("layer", 0))
            for o in objects:
                $ name = o.get("name", None)
                $ next_loc = o.get("location", None)
                $ tooltip = o.get("tooltip", None)
                $ img = PyTGFX.get_content(o["img"])
                button:
                    style 'image_button'
                    pos o["pos"]
                    idle_background img
                    hover_background PyTGFX.bright_content(img, .25)
                    focus_mask True
                    if name == "gazette":
                        action ToggleField(gazette, "show")
                        tooltip (tooltip or "PyTFall's GAZETTE")
                        sensitive day > 1
                    elif name == "report":
                        tooltip (tooltip or "Review Reports!")
                        action SetVariable("just_view_next_day", True), Hide("mainscreen"), Jump("next_day")
                        sensitive day > 1
                    elif name == "exit":
                        tooltip (tooltip or "Go to the City")
                        action Return("city")
                    elif next_loc is None:
                        action NullAction()
                    else:
                        action Function(global_flags.set_flag, "mc_home_location", [hero_home, next_loc])
                        if tooltip:
                            tooltip tooltip

    frame:
        align (.995, .88)
        background Frame("content/gfx/frame/window_frame2.webp", 30, 30)
        xysize (255, 670)
        xfill True
        yfill True

        add "".join(["content/gfx/interface/images/calendar/","cal ", calendar.moonphase(), ".png"]) xalign .485 ypos 83

        text "%s" % calendar.weekday() color "khaki" font 'fonts/TisaOTM.otf' size 18 kerning -1 xalign .5 ypos 210

        text "%s" % calendar.string() color "khaki" font 'fonts/TisaOTM.otf' size 18 kerning -1 xalign .5 ypos 250

        vbox:
            style_group "main_screen_3"
            xalign .5
            ypos 305
            spacing 15
            textbutton "Characters":
                action Return("chars_list")
                tooltip "A list of all of your workers"
            textbutton "Buildings":
                action Return("buildings_list")
                tooltip "Manage your properties and businesses"
            textbutton "Go to the City":
                action Return("city")
                tooltip 'Explore the city'

            null height 5
            if day > 1:
                hbox:
                    xalign .5
                    spacing 30
                    $ img = PyTGFX.scale_img("content/gfx/interface/images/merchant2.png", 40, 40)
                    imagebutton:
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        tooltip "Review Reports!"
                        action SetVariable("just_view_next_day", True), Hide("mainscreen"), Jump("next_day")
                    $ img = PyTGFX.scale_img(ImageReference("journal"), 40, 40)
                    imagebutton:
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        tooltip "PyTFall's GAZETTE"
                        action ToggleField(gazette, "show")
            else:
                null height 40
            null height 5

            textbutton "-Next Day-":
                style "main_screen_4_button"
                tooltip "Advance to next day!"
                action [Hide("mainscreen"), Jump("next_day")]

    if DEBUG:
        vbox:
            style_group "dropdown_gm"
            spacing 1
            align (.01, .5)
            textbutton "MD test":
                action Hide("mainscreen"), Jump("storyi_start")
            textbutton "Arena Inside":
                action Hide("mainscreen"), Jump("arena_inside")
            textbutton "Realtor":
                action Hide("mainscreen"), Jump("realtor_agency")
            textbutton "Test IAM":
                action Hide("mainscreen"), Jump("test_interactions")
            textbutton "Test IAM Mid-Game":
                action Hide("mainscreen"), Jump("test_interactions_mid")
            textbutton "Test BE":
                action Hide("mainscreen"), Jump("test_be")
            textbutton "Test BE Logical":
                action Hide("mainscreen"), Jump("test_be_logical")
            textbutton "Peak Into SE":
                action Show("se_debugger")
            textbutton "Examples":
                action [Hide("mainscreen"), Jump("examples")]
            textbutton "Show Chars Debug":
                action Show("chars_debug")
            textbutton "Return on callstack":
                action [Hide("mainscreen"), Jump("debug_callstack")]
            textbutton "Clear Console":
                action Jump("force_clear_console")

    showif day > 1 and gazette.show:
        default gazette_map = (
        ("arena", "Today at the Arena!"),
        ("shops", "Shopkeepers in PyTFall reporting:"),
        ("other", "Also:")
        )

        frame:
            background Frame("content/gfx/frame/settings1.webp", 10, 10)
            style_prefix "proper_stats"
            xysize 500, 600
            padding 10, 10
            pos 500, 60
            has vbox spacing 10
            label "PyTFall's GAZETTE" xalign .5
            viewport:
                xysize 480, 550
                xalign .5
                scrollbars "vertical"
                mousewheel True
                has vbox
                for attr, t in gazette_map:
                    $ content = getattr(gazette, attr)
                    if content:
                        label "[t]" text_size 17
                        text "\n".join(content)
                        null height 10
            if gazette.show == "first_view":
                timer 6 action ToggleField(gazette, "show")

        key "mousedown_3" action ToggleField(gazette, "show")
    else:
        key "mousedown_3" action Show("s_menu", transition=dissolve)

    use top_stripe(False)
