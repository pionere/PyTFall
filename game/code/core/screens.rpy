init python:
    def get_screens(*args):
        """
        Simple checks for active screens.
        Returns True if at least one of the screens is shown and False if not.
        """
        for scr in args:
            if renpy.get_screen(scr):
                return True
        return False

################### Specialized ####################
screen new_style_tooltip():
    layer "tooltips"
    $ tooltip = GetTooltip()

    if tooltip and persistent.tooltips:
#        use new_style_tooltip_content(tooltip)
#
#screen new_style_tooltip_content(tooltip):
        # Get mouse coords:
        python:
            x, y = renpy.get_mouse_pos()
            xval = 1.0 if x > config.screen_width/2 else .0
            yval = 1.0 if y > config.screen_height/2 else .0

        if isinstance(tooltip, basestring):
            frame:
                style_prefix "new_style_tooltip"
                pos (x, y)
                anchor (xval, yval)
                text "[tooltip]"
        elif isinstance(tooltip, list) and tooltip[0] == "be":
            $ combat_skill = tooltip[1]
            frame:
                style_prefix "new_style_tooltip_be_skills"
                pos (x, y)
                anchor (xval, yval)
                xmaximum 400
                has vbox

                $ temp = "".join([BE_Core.DAMAGE_20[t] for t in combat_skill.damage])
                # if "melee" in combat_skill.attributes:
                #     $ line = "{color=red}Melee skill{/color}"
                # elif "ranged" in combat_skill.attributes:
                #     $ line = "{color=green}Ranged skill{/color}"
                # elif "magic" in combat_skill.attributes:
                #     $ line = "{color=green}Magic skill{/color}"
                # else:
                #     $ line = "{color=orange}Status skill{/color}"

                # Elements:
                text "[combat_skill.name]" size 20 color "ivory" outlines [(2, "#3a3a3a", 0, 0)]
                text "[combat_skill.desc]" color "ivory"

                null height 5

                if "inevitable" in combat_skill.attributes:
                    hbox:
                        xsize 170
                        text "Can't be dodged!" italic True
                hbox:
                    xsize 200
                    text "Damage: "
                    text temp align 1.0, .5

                $ value = combat_skill.critpower
                if value != 0:
                    hbox:
                        xsize 200
                        text "Critical damage:"
                        text "%+g%%" % int(value * 100) xalign 1.0
                $ value = combat_skill.effect
                if value != 0:
                    hbox:
                        xsize 200
                        text "Relative power:"
                        text str(value) xalign 1.0
                $ value = combat_skill.multiplier
                if value != 0:
                    hbox:
                        xsize 200
                        text "Damage multiplier:"
                        text str(value) xalign 1.0

                null height 5

                hbox:
                    spacing 10
                    $ value = combat_skill.health_cost
                    if value != 0:
                        if not isinstance(value, int):
                            $ value = "%d %%" % int(value * 100)
                        text "HP: %s"%str(value) color "red"
                    $ value = combat_skill.mp_cost
                    if value != 0:
                        if not isinstance(value, int):
                            $ value = "%d %%" % int(value * 100)
                        text "MP: %s"%str(value) color "royalblue"
                    $ value = combat_skill.vitality_cost
                    if value != 0:
                        if not isinstance(value, int):
                            $ value = "%d %%" % int(value * 100)
                        text "VP: %s"%str(value) color "green"
                    if combat_skill.type.startswith("all"):
                        if combat_skill.piercing:
                            $ value = "All"
                        else:
                            $ value = "First Row"
                    elif combat_skill.piercing:
                        $ value = "Any"
                    else:
                        $ value = "One"
                    text "Target: %s"%value color "gold"

screen quest_notifications(q, type, align=None, autohide=2.5):
    zorder 500

    fixed:
        at slide(so1=(0, -600), eo1=(0, 40), t1=.4,
                 so2=(0, 40), eo2=(0, -600), t2=.6)
        # else:
            # at slide(so1=(0, -600), eo1=(0, 0), t1=1.0,
            #          so2=(0, 0), eo2=(0, -600), t2=1.0)
        if align:
            align align
        else:
            xalign .5
        xysize (500, 200)
        frame:
            background Frame(im.Alpha("content/gfx/frame/ink_box.png", alpha=.65), 10, 10)
            style_group "dropdown_gm2"
            xysize (400, 150)
            align .5, .5
            text q align .5, .5 style "TisaOTM" size 25

            $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 22, 22)
            imagebutton:
                align 1.005, -.03
                idle temp
                hover PyTGFX.bright_img(temp, 0.15)
                action Hide("quest_notifications"), With(dissolve)

        add PyTGFX.scale_img("content/gfx/interface/images/quest.png", 170, 120) pos (100, 0)
        frame:
            pos 400, 140 xanchor 1.0
            xpadding 15
            background Frame(im.Alpha("content/gfx/frame/ink_box.png", alpha=.45), 10, 10)
            text type style "content_text" size 40 color "gold"

    if autohide:
        timer autohide action Hide("quest_notifications")

screen top_stripe(show_return_button=True, return_button_action=None, show_lead_away_buttons=True):

    default return_action = Return(['control', 'return']) if return_button_action is None else return_button_action

    # Top Stripe Frame:
    add "content/gfx/frame/top_stripe.png"

    # Screen frame, always visible:
    if show_return_button:
        add "content/gfx/frame/h3.webp"
    else:
        add "content/gfx/frame/h2.webp"

    # All buttons:
    fixed:
        xysize(config.screen_width, 43)
        hbox:
            style_group "content"
            align .023, .5
            null width 10
            add "coin_top" yalign .5
            null width 5
            fixed:
                xsize 70
                $ g = gold_text(hero.gold)
                text g size 20 color "gold" yalign .5
            null width 15
            text u'Day [day]' size 20 color "ivory" yalign .5
            null width 15

        button:
            style "sound_button"
            pos 240, 3
            xysize (37, 37)
            if _preferences.mute["music"] or _preferences.mute["sfx"]:
                selected False
                action [Preference("sound mute", "disable"), Preference("music mute", "disable")]
                tooltip "UnMute All"
            else:
                selected True
                action [Preference("sound mute", "enable"), Preference("music mute", "enable")]
                tooltip "Mute All"

        # Left HBox: ======================================================>>>>>>
        # AP Frame/Next Day button:
        hbox:
            xalign .45
            spacing 5
            # Remaining AP:
            $ ap_h, pp_h = hero.ap_pp
            $ tt_string = "You have %s Action %s" % (ap_h, plural("Point", ap_h))
            if pp_h:
                $ tt_string += " and %s Partial (Action) %s" % (pp_h, plural("Point", pp_h))
            $ tt_string += " to interact with the world!"
            button:
                ypos 3
                xysize 170, 50
                focus_mask True
                background PyTGFX.scale_img("content/gfx/frame/frame_ap.webp", 170, 50)
                action NullAction()
                tooltip tt_string
                hbox:
                    yalign .1
                    xpos 105
                    label "%d"%ap_h:
                        style "content_label"
                        text_size 23
                        text_color "ivory"
                        text_bold True
                    if pp_h:
                        text "%02d"%pp_h:
                            color "pink"
                            style "proper_stats_text"
                            yoffset 7
            # Next Day:
            if show_lead_away_buttons and renpy.current_screen().tag != "mainscreen":
                $ img = PyTGFX.scale_img("content/gfx/interface/buttons/sunset_s.png", 80, 40)
                imagebutton:
                    idle img
                    hover PyTGFX.bright_img(img, .15)
                    if renpy.current_screen().tag == "next_day":
                        action Return(['control', "next_day_local"])
                    else:
                        action (hs, Jump("next_day"))
                    tooltip "Next Day"
            else:
                null width 80 # just a placeholder to keep the top stripe more static

        # Right HBox:
        hbox:
            align (.9, .5)
            spacing 5
            if False:
                textbutton "F":
                    style "basic_button"
                    text_color "ivory"
                    text_size 20
                    yalign .5
                    action Jump("fonts")
                    tooltip "View available Fonts"

            $ img = PyTGFX.scale_img("content/gfx/interface/icons/win_icon_s.png", 40, 40)
            imagebutton:
                idle img
                hover PyTGFX.bright_img(img, .15)
                action Show("pytfallopedia")
                tooltip "Open PyTFallopedia"

            if renpy.current_screen().tag != "quest_log":
                $ img = PyTGFX.scale_img("content/gfx/interface/buttons/journal1.png", 36, 40)
                imagebutton:
                    idle img
                    hover PyTGFX.bright_img(img, .15)
                    tooltip "Quest Journal"
                    action ShowMenu("quest_log")

            $ img = PyTGFX.scale_img("content/gfx/interface/buttons/preference.png", 39, 40)
            imagebutton:
                idle img
                hover PyTGFX.bright_img(img, .15)
                action Show("s_menu", transition=dissolve)
                tooltip "Game Preferences"
                keysym "K_ESCAPE"

            if show_lead_away_buttons and renpy.current_screen().tag != "mainscreen":
                $ img = PyTGFX.scale_img("content/gfx/interface/buttons/MS.png", 38, 37)
                imagebutton:
                    idle img
                    hover PyTGFX.bright_img(img, .15)
                    tooltip "Return to Main Screen"
                    if renpy.current_screen().tag == "next_day":
                        action return_action
                    else:
                        action (hs, Function(global_flags.del_flag, "mc_home_location"), Jump("mainscreen"))

            if show_lead_away_buttons:
                $ img = PyTGFX.scale_img("content/gfx/interface/buttons/profile.png", 35, 40)
                imagebutton:
                    idle img
                    hover PyTGFX.bright_img(img, .15)
                    action [SetVariable("hero_profile_entry", last_label), hs, Jump("hero_profile")]
                    tooltip "View Hero Profile"

            null width 10

            $ img = PyTGFX.scale_img("content/gfx/interface/buttons/save.png", 40, 40)
            imagebutton:
                idle img
                hover PyTGFX.bright_img(img, .15)
                tooltip "QuickSave"
                action QuickSave()

            $ img = PyTGFX.scale_img("content/gfx/interface/buttons/load.png", 38, 40)
            imagebutton:
                idle img
                hover PyTGFX.bright_img(img, .15)
                tooltip "QuickLoad"
                action QuickLoad()

        if show_return_button:
            default special_screens = ["girl_interactions",
                                       "building_management_leftframe_businesses_mode",
                                       "chars_list", "char_profile"]
            # Reasoning for killing the button for mc_action_ is that we can't return to
            # previous locations from many MC actions, such as working for example.
            # It's not that we'll just get a stack corruption, we'll be risking
            # CTD or collapsing the stack all the way to MainMenu.
            $ img = im.Scale("content/gfx/interface/buttons/close.png", 35, 35)
            imagebutton:
                align (.993, .5)
                idle img
                hover PyTGFX.bright_img(img, .25)
                #insensitive_background PyTGFX.sepia_img(img)
                action return_action
                # sensitive not str(last_label).startswith("mc_action_")
                tooltip "Return to previous screen"
                if not get_screens(*special_screens):
                    keysym "mousedown_3"

screen team_status(team=None, interactive=True, pos=(17, 50), spacing=25):
    $ members = hero.team if team is None else team 
    hbox:
        spacing spacing
        pos pos
        for member in members:
            $ char_profile_img = member.show('portrait', resize=(100, 100), cache=True)
            vbox:
                spacing 1
                xsize 102
                fixed:
                    xalign .5
                    xysize 102, 102
                    if interactive:
                        imagebutton:
                            xysize (102, 102)
                            background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
                            padding (1, 1)
                            idle char_profile_img
                            hover PyTGFX.bright_content(char_profile_img, .15)
                            action Return(member)
                    else:
                        frame:
                            xysize (102, 102)
                            background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
                            padding (1, 1)
                            add char_profile_img

                    $ ap_h, pp_h = member.ap_pp
                    $ tt_string = "%s has %s Action %s" % (member.nickname, ap_h, plural("Point", ap_h))
                    if pp_h:
                        $ tt_string += " and %s Partial (Action) %s" % (pp_h, plural("Point", pp_h))
                    $ tt_string += " to interact with the world!"
                    button:
                        xysize (50, 35)
                        align 1.0, 1.0
                        background Frame("content/gfx/frame/frame_bg.png", 5, 5)
                        text "%d"%ap_h size 17 color "ivory" style "content_label_text" yalign .5
                        text "%02d"%pp_h size 15 color "goldenrod" style "proper_stats_text" xpos 12 yalign .80
                        tooltip tt_string
                        action NullAction()
                bar:
                    right_bar im.Scale("content/gfx/interface/bars/empty_bar2.png", 102, 14)
                    left_bar im.Scale("content/gfx/interface/bars/hp2.png", 102, 14)
                    value member.get_stat("health")
                    range member.get_max("health")
                    thumb None
                    left_gutter 0
                    right_gutter 0
                    xysize (102, 14)
                bar:
                    right_bar im.Scale("content/gfx/interface/bars/empty_bar2.png", 102, 14)
                    left_bar im.Scale("content/gfx/interface/bars/mp2.png", 102, 14)
                    value member.get_stat("mp")
                    range member.get_max("mp")
                    thumb None
                    left_gutter 0
                    right_gutter 0
                    xysize (102, 14)
                bar:
                    right_bar im.Scale("content/gfx/interface/bars/empty_bar2.png", 102, 14)
                    left_bar im.Scale("content/gfx/interface/bars/vitality2.png", 102, 14)
                    value member.get_stat("vitality")
                    range member.get_max("vitality")
                    thumb None
                    left_gutter 0
                    right_gutter 0
                    xysize (102, 14)

screen message_screen(msg, size=(500, 300), use_return=False):
    modal True
    zorder 10

    fixed:
        align(.5, .5)
        xysize(size[0], size[1])
        xfill True
        yfill True

        add im.Scale("content/gfx/frame/frame_bg.png", size[0], size[1])

        vbox:
            style_prefix "proper_stats"
            spacing 30
            align(.5, .5)
            vbox:
                xmaximum (size[0] - 100)
                text msg xalign .5 color "lightgoldenrodyellow" size 20
            textbutton "Ok":
                action If(use_return, true=Return(), false=Hide("message_screen"))
                xsize 120
                xalign .5
                text_yoffset 1
                style "dropdown_gm_button"
                keysym "mousedown_3", "K_RETURN", "K_ESCAPE"

screen pyt_input(default="", text="", length=20, size=(350, 150)):
    use keymap_override
    modal True
    zorder 10

    default text_input = default

    fixed:
        align(.5, .5)
        minimum(size[0], size[1])
        maximum(size[0], size[1])
        xfill True
        yfill True

        add im.Scale("content/gfx/frame/frame_bg.png", size[0], size[1])

        vbox:
            spacing 10
            align(.5, .5)
            text text xalign .5 style "TisaOTM" size 20 color "goldenrod"
            input:
                id "text_input"
                default text_input
                length length
                xalign .5
                style "TisaOTM"
                size 20
                color "white"
                changed SetScreenVariableD("text_input")
            button:
                style "pb_button"
                # xysize (100, 50)
                text "OK"  style "TisaOTM" size 15 color "goldenrod" align (.5, .5)
                xalign .5
                action Return(text_input)
                keysym "input_enter"
    key "K_ESCAPE" action Return(default)
    key "mousedown_3" action Return (default)

screen exit_button(size=(35, 35), align=(1.0, .0), action=Return(['control', 'return'])):
    $ img = im.Scale("content/gfx/interface/buttons/close.png" , size[0], size[1])
    imagebutton:
        align(align[0], align[1])
        idle img
        hover PyTGFX.bright_img(img, .25)
        action action
        keysym "mousedown_3"

screen poly_matrix(matrix, show_exit_button=False, cursor="content/gfx/interface/icons/zoom_glass.png", xoff=20, yoff=20, hidden=[]):
    # If a tuple with coordinates is provided instead of False for show_exit_button, exit button will be placed there.

    #default tooltip = False

    on "hide":
        action SetField(config, "mouse", None), Hide("show_poly_matrix_tt")

    $ func = renpy.curry(point_in_poly)
    for i in matrix:
        if i["id"] not in hidden:
            if "tooltip" in i:
                if "align" in i:
                    python:
                        align = tuple(i["align"])
                        pos = ()
                        anchor = ()
                else:
                    python:
                        align = ()
                        # Get a proper placement:
                        allx, ally = list(), list()

                        for t in i["xy"]:
                            allx.append(t[0])
                            ally.append(t[1])

                        maxx = max(allx)
                        maxy = max(ally)
                        minx = min(allx)
                        miny = min(ally)

                        w, h = config.screen_width, config.screen_height

                        side = i.get("place", "left")

                        if side == "left":
                            pos = (minx - 10, sum(ally)/len(ally))
                            anchor = (1.0, .5)
                        elif side == "right":
                            pos = (maxx + 10, sum(ally)/len(ally))
                            anchor = (.0, .5)
                        elif side == "bottom":
                            pos = (sum(allx)/len(allx), maxy + 10)
                            anchor = (.5, .0)
                        elif side == "top":
                            pos = (sum(allx)/len(allx), miny - 10)
                            anchor = (.5, 1.0)

                button:
                    background Null()
                    focus_mask func(i["xy"])
                    action Return(i["id"])
                    hovered [SetField(config, "mouse", {"default": [(cursor, xoff, yoff)]}),
                                   Show("show_poly_matrix_tt", pos=pos, anchor=anchor, align=align, text=i["tooltip"]), With(dissolve)]
                    unhovered [SetField(config, "mouse", None),
                                       Hide("show_poly_matrix_tt"), With(dissolve)]
            else:
                button:
                    background Null()
                    focus_mask func(i["xy"])
                    action Return(i["id"])
                    hovered SetField(config, "mouse", {"default": [(cursor, xoff, yoff)]})
                    unhovered SetField(config, "mouse", None)

    if show_exit_button:
        textbutton "{size=+10}Close":
            padding 10, 5
            text_yoffset 2
            style "pb_button"
            align show_exit_button
            action Return(False)
            keysym "mousedown_3"

screen show_poly_matrix_tt(pos=(), anchor=(), align=(), text=""):
    zorder 1
    style_prefix "pb"
    button: # Button for simpler styling.
        action None
        if align:
            align align
        if pos:
            pos pos
            anchor anchor
        text text

##############################################################################
screen notify:
    zorder 500

    vbox:
        pos 20, 20
        at fade_in_out(t1=.25, t2=.25)
        style_group "notify_bubble"

        frame:
            background Frame("content/gfx/frame/rank_frame.png", 5, 5)
            padding 10, 5
            xmaximum 600
            text message style "TisaOTMol" color "goldenrod" outlines [(2, "black", 0, 0)]

    timer 4.0 action Hide("notify")

# Settings:
screen s_menu(s_menu="Settings", main_menu=False):
    zorder 10**5 + 1
    modal True

    default tt = Tooltip("Hover cursor over options buttons to see the description.")

    key "mousedown_3" action Hide("s_menu"), With(dissolve)
    key "K_ESCAPE" action Hide("s_menu"), With(dissolve)

    # default s_menu = "Settings"

    add im.Alpha("content/gfx/images/bg_gradient2.webp", alpha=.8)

    frame:
        # at fade_in_out(sv1=.0, ev1=1.0, t1=.7,
                                # sv2=1.0, ev2=.0, t2=.5)
        background Frame(im.Alpha("content/gfx/frame/frame_gp2.webp", alpha=.8), 10, 10)
        align (.315, .5)
        xysize (690, 444)
        style_group "smenu"
        has hbox align (.5, .5) xfill True

        if s_menu == "Settings":
            grid 3 1:
                align (.5, .5)
                spacing 7
                # Left column...
                frame:
                    align (.5, .5)
                    background Frame(im.Alpha("content/gfx/frame/ink_box.png", alpha=.3), 10, 10)
                    xpadding 10
                    ypadding 10
                    has vbox spacing 5
                    # frame:
                        # background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        # xsize 194
                        # ypadding 8
                        # style_group "dropdown_gm2"
                        # has vbox align (.5, .5)

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5) spacing 2
                        frame:
                            xsize 184
                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- Display -") style "TisaOTMolxm"
                        textbutton _("Window") action Preference("display", "window") xsize 150 xalign .5 text_size 16
                        textbutton _("Fullscreen") action Preference("display", "fullscreen") xsize 150 xalign .5 text_size 16

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5) spacing 2
                        frame:
                            xsize 184
                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- Transitions -") style "TisaOTMolxm"
                        textbutton _("All") action Preference("transitions", "all") xsize 150 xalign .5 text_size 16
                        textbutton _("None") action Preference("transitions", "none") xsize 150 xalign .5 text_size 16

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 10
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5) spacing 8
                        frame:
                            xsize 184
                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- Text Speed -") style "TisaOTMolxm"
                        bar value Preference("text speed") align (.5, .5)

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5)
                        textbutton _("Gamepad") action SensitiveIf(GamepadExists()), GamepadCalibrate() xsize 150 text_size 16


                # Middle column...
                frame:
                    align (.5, .5)
                    background Frame(im.Alpha("content/gfx/frame/ink_box.png", alpha=.3), 10, 10)
                    xpadding 10
                    ypadding 10
                    has vbox spacing 5
                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5) spacing 2
                        frame:
                            xsize 184
                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- Skip -") style "TisaOTMolxm"
                        textbutton _("Seen Messages") action Preference("skip", "seen") xsize 150 xalign .5 text_size 16
                        textbutton _("All Messages") action Preference("skip", "all") xsize 150 xalign .5 text_size 16

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5) spacing 2
                        frame:
                            xsize 184
                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- After Choices -") style "TisaOTMolxm"
                        textbutton _("Stop Skipping") action Preference("after choices", "stop") xsize 150 xalign .5 text_size 16
                        textbutton _("Keep Skipping") action Preference("after choices", "skip") xsize 150 xalign .5 text_size 16

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 10
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5)
                        frame:
                            xsize 184
                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- A-Forward Time -") style "TisaOTMolxm"
                        null height 8
                        bar value Preference("auto-forward time") align (.5, .5)
                        if config.has_voice:
                            textbutton _("Wait for Voice") action Preference("wait for voice", "toggle") xsize 150 xalign .5 text_size 16

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5)
                        textbutton _("Begin Skipping") action Preference("begin skipping") xsize 150 text_size 16

                # Right column...
                frame:
                    align (.5, .0)
                    background Frame(im.Alpha("content/gfx/frame/ink_box.png", alpha=.3), 10, 10)
                    xpadding 10
                    ypadding 10
                    has vbox spacing 5

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194

                        ypadding 8
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5) spacing 2
                        frame:
                            xsize 184

                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- Mute -") style "TisaOTMolxm"
                        textbutton "Music" action Preference("music mute", "toggle") xsize 150 xalign .5 text_size 16
                        textbutton "Sound" action Preference("sound mute", "toggle") xsize 150 xalign .5 text_size 16

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 10
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5) spacing 8
                        frame:
                            xsize 184
                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- Music Volume -") align (.5, .0) style "TisaOTMolxm"
                        bar value Preference("music volume") align (.5, .5)

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 10
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5)
                        frame:
                            xsize 184
                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- Sound Volume -") style "TisaOTMolxm"
                        null height 8
                        bar value Preference("sound volume") align (.5, .5)
                        if config.sample_sound:
                            textbutton _("Test"):
                                action Play("sound", config.sample_sound)
                                style "soundtest_button"

        elif s_menu == "Game":
            frame:
                background Frame("content/gfx/frame/ink_box.png", 10, 10)
                xysize (333, 130)
                xpadding 10
                align .5, .1
                text (u"{=stats_text}{color=goldenrod}{size=15}%s" % tt.value) outlines [(1, "#3a3a3a", 0, 0)]
            grid 1 1:
                align (.5, .5)
                spacing 7
                # Left column...
                frame:
                    align (.5, .5)
                    style_prefix "dropdown_gm2"
                    background Frame(im.Alpha("content/gfx/frame/ink_box.png", alpha=.3), 10, 10)
                    xpadding 10
                    ypadding 10
                    has vbox spacing 5
                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        $ msg = "{}\nPanic screen transforms your game window into a system-log. If enabled, press Q whenever you need it.".format("Active" if persistent.unsafe_mode else "Inactive")
                        textbutton _("Panic Screen"):
                            action ToggleField(persistent, "unsafe_mode"), tt.action("")
                            xsize 150
                            xalign .5
                            text_size 16
                            if main_menu or not persistent.tooltips:
                                hovered tt.Action(msg)
                            else:
                                tooltip msg
                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        $ msg = "{}\nShows experience screen after combat.".format("Active" if persistent.battle_results else "Inactive")
                        textbutton _("Battle Results"):
                            action ToggleField(persistent, "battle_results"), tt.action("")
                            xsize 150
                            xalign .5
                            text_size 16
                            if main_menu or not persistent.tooltips:
                                hovered tt.Action(msg)
                            else:
                                tooltip msg
                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        $ msg = "Use %s for targeting in battle engine." % ("menu" if persistent.use_be_menu_targeting else "pointer/arrows")
                        textbutton _("Combat Targeting"):
                            action ToggleField(persistent, "use_be_menu_targeting"), tt.action("")
                            xsize 150
                            xalign .5
                            text_size 16
                            if main_menu or not persistent.tooltips:
                                hovered tt.Action(msg)
                            else:
                                tooltip msg
                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        $ msg = "{}\nSaves your game progress every day. This can be slow, disable if it bothers you.".format("Active" if persistent.auto_saves else "Inactive")
                        textbutton _("AutoSaves"):
                            action ToggleField(persistent, "auto_saves"), tt.action("")
                            xsize 150
                            xalign .5
                            text_size 16
                            if main_menu or not persistent.tooltips:
                                hovered tt.Action(msg)
                            else:
                                tooltip msg
                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        $ msg = "{}\nDisplay notifications as you make progress in Quests.".format("Active" if persistent.use_quest_popups else "Inactive")
                        textbutton _("Quest Pop-Up"):
                            action ToggleField(persistent, "use_quest_popups"), tt.action("")
                            xsize 150
                            xalign .5
                            text_size 16
                            if main_menu or not persistent.tooltips:
                                hovered tt.Action(msg)
                            else:
                                tooltip msg

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 8
                        $ msg = "New-style tooltips %s." % ("enabled" if persistent.tooltips else "disabled")
                        textbutton _("Tooltips"):
                            action ToggleField(persistent, "tooltips"), tt.action("Tooltips Disabled!")
                            xsize 150
                            xalign .5
                            text_size 16
                            if persistent.tooltips:
                                if main_menu:
                                    hovered tt.Action(msg)
                                else:
                                    tooltip msg
                            else:
                                hovered tt.Action(msg)

                    frame:
                        background Frame(im.Alpha("content/gfx/frame/settings1.webp", alpha=.9), 10, 10)
                        xsize 194
                        ypadding 10
                        style_group "dropdown_gm2"
                        has vbox align (.5, .5) spacing 8
                        frame:
                            xsize 184
                            align (.5, .5)
                            background Frame(im.Alpha("content/gfx/frame/stat_box_proper.png", alpha=.9), 10, 10)
                            text _("- Battle Speed -") style "TisaOTMolxm"
                        if persistent.battle_speed == 1.0:
                            $ msg = "Battle Animations run with the default speed."
                        elif persistent.battle_speed > 1.0:
                            $ msg = "Battle Animations run at half of the default speed."
                        else:
                            $ msg = "Battle Animations run %dX the default speed." % (1.0/persistent.battle_speed)
                        bar:
                            align (.5, .5)
                            value FieldValue(BE_Core(), "battle_speed", range=4, offset=-1, step=1, max_is_zero=False, style="slider")
                            changed renpy.restart_interaction
                            if main_menu or not persistent.tooltips:
                                hovered tt.Action(msg)
                            else:
                                tooltip msg

        elif s_menu in ("Save", "Load"):
            vbox:
                yfill True
                xfill True
                spacing 5
                null height 5
                hbox:
                    spacing 3
                    style_group "dropdown_gm2"
                    align (.5, .5)
                    textbutton _("Previous") action FilePagePrevious(), With(dissolve) text_size 16
                    textbutton _("Auto") action FilePage("auto"), With(dissolve) text_size 16
                    textbutton _("Quick") action FilePage("quick"), With(dissolve) text_size 16
                    for i in range(1, 9):
                        textbutton str(i):
                            action FilePage(i), With(dissolve)
                    textbutton _("Next") action FilePageNext(), With(dissolve) text_size 16
                $ columns = 2
                $ rows = 3
                grid columns rows:
                    transpose True
                    style_group "dropdown_gm2"
                    xfill True
                    yfill True
                    spacing -10
                    for i in range(1, columns * rows + 1):

                        $ file_name = FileSlotName(i, columns*rows)
                        $ file_time = FileTime(i, empty=_("Empty Slot"))
                        $ json_info = FileJson(i, empty={})
                        $ save_name = FileSaveName(i)

                        hbox:
                            align (.5, .5)
                            frame:
                                background Frame("content/gfx/frame/MC_bg.png", 10, 10)
                                align (.5, .5)
                                $ portrait = json_info.get("portrait", "")
                                if check_content_extension(portrait) and renpy.loadable(portrait):
                                    $ portrait = PyTGFX.scale_content(portrait, 90, 90)
                                else:
                                    $ portrait = Null(width=90, height=90)
                                add portrait align (.5, .5)
                            button:
                                style "smenu2_button"
                                align (.5, .5)
                                xysize (220, 100)
                                # Save info if we have it:
                                vbox:
                                    xpos 0
                                    yalign .5
                                    spacing -7
                                    if "name" in json_info:
                                        text "[json_info[name]]" style "TisaOTMol" color "gold" size 17
                                    if "level" in json_info:
                                        text "Level: [json_info[level]]" style "TisaOTMol" ypos 0
                                    if "chars" in json_info:
                                        text "Chars: [json_info[chars]]" style "TisaOTMol" ypos 0
                                    if "gold" in json_info:
                                        text "Gold: [json_info[gold]]" style "TisaOTMol" ypos 0
                                    if "buildings" in json_info:
                                        text "Buildings: [json_info[buildings]]" style "TisaOTMol" ypos 0

                                key "save_delete" action FileDelete(i)

                                # Bottom-right:
                                if s_menu == "Save":
                                    action FileSave(i)
                                    text " - [file_name] -" align (1.0, 0) style "TisaOTMol" size 14 outlines [(3, "#3a3a3a", 0, 0), (2, "#458B00", 0, 0), (1, "#3a3a3a", 0, 0)]
                                    text "[file_time!t]\n[save_name!t]" style "TisaOTMol" size 12 align (1.05, 1.25)
                                elif s_menu == "Load":
                                    action FileLoad(i)
                                    text " - [file_name] -" align (1.0, 0) style "TisaOTMol" size 14 outlines [(3, "#3a3a3a", 0, 0),(2, "#009ACD", 0, 0), (1, "#3a3a3a", 0, 0)]
                                    text "[file_time!t]\n[save_name!t]" style "TisaOTMol" size 12 align (1.05, 1.25)
    frame:
        background Frame(im.Alpha("content/gfx/frame/p_frame5.png", alpha=.9), 10, 10)
        align (.765, .505)
        xysize (150, 439)
        style_group "smenu"
        xpadding 8
        has vbox spacing 5 align (.5, .5)
        null height 3
        vbox:
            xfill True
            spacing -10
            align (.5, .5)
            if s_menu == "Settings":
                text "Settings" style "TisaOTMol" size 26 align (.5, .5)
            if s_menu == "Game":
                text "Game" style "TisaOTMol" size 26 align (.5, .5)
            elif s_menu == "Save":
                text "Save" style "TisaOTMol" size 26 align (.5, .5)
            elif s_menu == "Load":
                text "Load" style "TisaOTMol" size 26 align (.5, .5)
        button:
            yalign .5
            action Hide("s_menu"), With(dissolve)
            text "Return" size 18 align (.5, .5) # style "mmenu_button_text"
        button:
            yalign .5
            action SelectedIf(s_menu == "Settings"), Hide("s_menu"), Show("s_menu", s_menu="Settings", main_menu=main_menu), With(dissolve) # SetScreenVariable("s_menu", "Settings")
            text "Settings" size 18 align (.5, .5) # style "mmenu_button_text"
        button:
            yalign .5
            action Hide("s_menu"), With(dissolve), Jump("tagger")
            text "Tagger" size 18 align (.5, .5) # style "mmenu_button_text"
        button:
            yalign .5
            action SelectedIf(s_menu == "Game"), Hide("s_menu"), Show("s_menu", s_menu="Game", main_menu=main_menu), With(dissolve)
            text "Game" size 18 align (.5, .5)
        button:
            yalign .5
            action SensitiveIf(not main_menu), SelectedIf(s_menu == "Save"), Hide("s_menu"), Show("s_menu", s_menu="Save", main_menu=main_menu), With(dissolve)#, SetScreenVariable("s_menu", "Save")
            text "Save" size 18 align (.5, .5) # style "mmenu_button_text"
        button:
            yalign .5
            action SelectedIf(s_menu == "Load"), Hide("s_menu"), Show("s_menu", s_menu="Load", main_menu=main_menu), With(dissolve)#, SetScreenVariable("s_menu", "Load")
            text "Load" size 18 align (.5, .5) # style "mmenu_button_text"
        button:
            yalign .5
            action MainMenu()
            text "Main Menu" size 18 align (.5, .5) #  style "mmenu_button_text"
        button:
            yalign 1.0
            action Quit()
            text "Quit" size 18 align (.5, .5) # style "mmenu_button_text"
        null height 3

screen keymap_override():
    on "show":
        action SetVariable("_skipping", False)
    on "hide":
        action SetVariable("_skipping", True)

    key "hide_windows" action NullAction()
    key "game_menu" action NullAction()
    key "help" action NullAction()
    key "rollback" action NullAction()
    key "rollforward" action NullAction()
    key "skip" action NullAction()
    key "toggle_skip" action NullAction()
    key "fast_skip" action NullAction()
    #key "mouseup_3" action NullAction()
    #key "mousedown_3" action NullAction()
    #key "mouseup_2" action NullAction()
    #key "mousedown_2" action NullAction()

screen panic_screen():
    modal True
    layer "panic"

    default original_transitions_state = _preferences.transitions

    on "show":
        action [PauseAudio("events", True), PauseAudio("events2", True),
                PauseAudio("world", True), PauseAudio("gamemusic", True),
                PauseAudio("music", True), SetField(_preferences, "transitions", 0)]
    on "hide":
        action [SetField(config, "window_title", config.name), PauseAudio("events", False),
                PauseAudio("events2", False), PauseAudio("world", False),
                PauseAudio("gamemusic", False), PauseAudio("music", False),
                SetField(_preferences, "transitions", original_transitions_state),
                SetField(config, "window_icon", "content/gfx/interface/icons/win_icon.png"),
                renpy.game.interface.set_icon]

    use keymap_override

    add "content/gfx/bg/panic_screen.webp" zoom 1.32

    key "q" action Hide("panic_screen")
    key "Q" action Hide("panic_screen")
    key "й" action Hide("panic_screen")
    key "Й" action Hide("panic_screen")

screen give_exp_after_battle(group, enemy_team, ap_used):
    modal True
    zorder 100

    use keymap_override

    default bars = [ExpBarController(c) for c in group]

    frame:
        align (.5, .5)
        background Frame("content/gfx/frame/post_battle.png", 75, 75)
        xpadding 75
        ypadding 75
        has vbox
        # text "You gained [exp] exp" size 20 align (.5, .5) style "proper_stats_value_text" bold True outlines [(1, "#181818", 0, 0)] color "#DAA520"
        text "You've won the battle!" size 20 align (.5, .5) style "proper_stats_value_text" bold True outlines [(1, "#181818", 0, 0)] color "#DAA520"
        null height 15

        for b in bars:
            add b

        # actually give the EXP:
        for b in bars:
            timer .01 action Function(b.mod_exp, exp_reward(b.char, enemy_team, exp_mod=ap_used[b.char])) repeat False

        style_prefix "wood"
        null height 15
        button:
            xalign .5
            xysize (120, 40)
            if all(b.done for b in bars):
                action Return()
                keysym ("K_ESCAPE", "K_RETURN", "mousedown_3")
            text "OK" size 15


screen tutorial(level=1):
    modal True
    zorder 600
    add "content/gfx/tutorials/t" + str(level) + ".webp"

    button:
        background None
        xysize (1280, 720)
        action Hide("tutorial")

screen stars(value, max_value, num_stars=5, func=None, **kwargs):
    python:
        step = max_value / (num_stars * 2)
        images = ["content/gfx/interface/icons/stars/star2a.png", "content/gfx/interface/icons/stars/star3a.png", "content/gfx/interface/icons/stars/star1a.png"]
        if func is not None:
            images = [func(i, **kwargs) for i in images]
    for i in range(5):
        if (2*step) <= value:
            $ i = 0 # full
            $ value -= 2*step
        elif step <= value:
            $ i = 1 # half
            $ value -= step
        else:
            $ i = 2 # empty
        add Transform(images[i], size=(18, 18))

screen digital_keyboard(line=""):
    default current_number = "0"
    modal True

    if line:
        frame:
            background Frame("content/gfx/frame/MC_bg3.png", 5, 5)
            align(.5, .1)
            xysize (600, 100)
            text line color "gold" xalign .5 size 20 outlines [(1, "black", 0, 0)] align (.5, .5) text_align .5

    frame:
        xysize (250, 250)
        background Frame("content/gfx/frame/MC_bg3.png")
        align (.5, .5)

        frame:
            align (.5, .05)
            background Frame("content/gfx/frame/rank_frame.png")
            xysize (200, 45)
            text current_number color "gold" xalign .5 size 20 outlines [(1, "black", 0, 0)] align (1.0, .5)

        vpgrid:
            rows 4
            cols 3
            spacing 5
            align (.5, .7)
            xysize (190, 135)
            for i in range(1, 10):
                $ temp = str(i)
                button:
                    xysize(60, 30)
                    background "content/gfx/interface/buttons/hp_1s.png"
                    hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/hp_1s.png", im.matrix.brightness(.10)))
                    text temp color "gold" size 22 outlines [(1, "black", 0, 0)] align (.5, .5) text_align .5
                    action SetScreenVariable("current_number", temp if current_number == "0" else (current_number + temp))
                    sensitive len(current_number) < 14
                    keysym ("K_KP%d"%i), ("K_%d"%i)
            button:
                xysize(60, 30)
                background "content/gfx/interface/buttons/hp_1s.png"
                hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/hp_1s.png", im.matrix.brightness(.10)))
                text str("C") color "gold" size 22 outlines [(1, "black", 0, 0)] align (.5, .5) text_align .5
                action SetScreenVariable("current_number", "0")
                keysym "K_DELETE", "K_SPACE", "K_CLEAR", "K_KP_PERIOD"
            button:
                xysize(60, 30)
                background "content/gfx/interface/buttons/hp_1s.png"
                hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/hp_1s.png", im.matrix.brightness(.10)))
                text "0" color "gold" size 22 outlines [(1, "black", 0, 0)] align (.5, .5) text_align .5
                action SetScreenVariable("current_number", current_number + "0")
                sensitive len(current_number) < 14 and current_number != "0"
                keysym "K_KP0", "K_0"
            button:
                xysize(60, 30)
                background "content/gfx/interface/buttons/hp_1s.png"
                hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/hp_1s.png", im.matrix.brightness(.10)))
                text str("E") color "gold" size 22 outlines [(1, "black", 0, 0)] align (.5, .5) text_align .5
                action Return(int(current_number))
                keysym "K_KP_ENTER", "K_RETURN"

    key "mousedown_3" action Return(0)
    key "K_ESCAPE" action Return(0)
