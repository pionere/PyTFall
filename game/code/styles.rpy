init -3 python:
    # We create a font group to resolve rare characters in pretty fonts so we can use both at the same time.
    tisa_otm_adv = FontGroup().add("fonts/Hosohuwafont.ttf", 0x2E80, 0xFE4F).add("fonts/DejaVuSans.ttf", 0x00A0, 0xE007F).add("fonts/TisaOTM.otf", 0x0020, 0x007f)
    # tisa_otb_adv = FontGroup().add("fonts/", 0x00A0, 0xE007F).add("fonts/TisaOTB.otf", 0x0020, 0x007f)

# Well... better late than never :)
# My first ever style is created here!
# Neow!
init -3:
    # Style resets:
    style say_label:
        clear

    # style window:
        # clear

    # style frame:
    #     clear

    # style say_vbox:
        # clear

    # style say_who_window:
        # clear

    # style say_two_window_vbox:
        # clear

    # style menu_choice:
        # clear

    # style input:
        # clear

    # style hyperlink_text:
        # clear

    # style button:
        # clear

    # style button_text:
        # clear

init -2: # Base Styles like Texts and Buttons just with the basic properties.
    style overframe_1:
        is default
        # padding (0, 0)
        # margin (0, 0)
        background Null()
        foreground Frame("content/gfx/frame/MC_bg2.png", 10, 10)

    # ----------------------------------- Buttons:
    style flashing:
        activate_sound "content/sfx/sound/sys/click_1.ogg"
        # hover_sound "content/sfx/sound/sys/hover.mp3"
        idle_background None
        selected_background None
        insensitive_background None
        hover_background flashing("#0390fc")
        selected_hover_background flashing("#0390fc")

    # Paging buttons:
    style paging_green_button_left:
        clear
        xysize (29, 43)
        background Frame(interfacebuttons + "arrow_left.png")
        hover_background im.MatrixColor(interfacebuttons + "arrow_left.png", im.matrix.brightness(.10))
        insensitive_background im.Sepia(interfacebuttons + "arrow_left.png")
    style paging_green_button_left2x:
        clear
        xysize (43, 43)
        background Frame(interfacebuttons + "arrow_left2x.png")
        hover_background im.MatrixColor(interfacebuttons + "arrow_left2x.png", im.matrix.brightness(.10))
        insensitive_background im.Sepia(interfacebuttons + "arrow_left2x.png")

    style paging_green_button_right:
        clear
        xysize (29, 43)
        background Frame(interfacebuttons + "arrow_right.png")
        hover_background im.MatrixColor(interfacebuttons + "arrow_right.png", im.matrix.brightness(.10))
        insensitive_background im.Sepia(interfacebuttons + "arrow_right.png")
    style paging_green_button_right2x:
        clear
        xysize (43, 43)
        background Frame(interfacebuttons + "arrow_right2x.png")
        hover_background im.MatrixColor(interfacebuttons + "arrow_right2x.png", im.matrix.brightness(.10))
        insensitive_background im.Sepia(interfacebuttons + "arrow_right2x.png")

    # Simple button we use to call the dropdowns:
    # This is a really basic, stripped down button.
    style ddlist_button:
        is button
        background Null()
    style ddlist_text:
        is garamond
        yalign .5
        idle_color ivory
        hover_color red

    # Master Styles of the GREY and BROWNish buttons we use all over the place.
    style basic_choice_button:
        background Frame("content/gfx/interface/buttons/choice_buttons1.png", 10, 10)
        hover_background Frame("content/gfx/interface/buttons/choice_buttons1h.png", 10, 10)
        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/choice_buttons1.png"), 10, 10)
        selected_idle_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons1.png", im.matrix.tint(1, .75, .75)), 10, 10)
        selected_hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons1h.png", im.matrix.tint(.75, .75, 1)), 10, 10)

    style basic_choice2_button:
        background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
        idle_background Frame("content/gfx/interface/buttons/choice_buttons2.png", 5, 5)
        hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.1)), 5, 5)
        selected_background Frame("content/gfx/interface/buttons/choice_buttons2s.png", 5, 5)
        selected_hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2s.png", im.matrix.brightness(.1)), 5, 5)
        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/choice_buttons2.png"), 5, 5)

    # Presently used in Main Menu.
    style mmenu1_button:
        take flashing
        background Frame("content/gfx/interface/buttons/main1.png", 5, 5)
        hover_background  Fixed(Frame("content/gfx/interface/buttons/main1.png", 5, 5),
                                                  flashing(Frame("content/gfx/interface/buttons/flashing2.png", 5, 5)))

    # Parent for the new MM button.
    style smenu1_button:
        take flashing
        background Frame("content/gfx/interface/buttons/s_menu1.png", 5, 5)
        hover_background  Fixed(Frame("content/gfx/interface/buttons/s_menu1.png", 5, 5),
                                flashing(Frame("content/gfx/interface/buttons/flashing2.png", 5, 5)))
        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/s_menu1.png"), 5, 5)

    # Parent for the cool buttons in MCs Profile.
    style hframe_button:
        take flashing
        background Frame("content/gfx/interface/buttons/hp_1s.png", 5, 5)
        hover_background  Fixed(Frame("content/gfx/interface/buttons/hp_1s.png", 5, 5),
                                                  flashing(Frame("content/gfx/interface/buttons/flashing2.png", 5, 5)))
        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/hp_1s.png"), 5, 5)

    # Button used in game menu saves.
    style smenu2_button:
        background Frame("content/gfx/interface/buttons/s_menu2.png", 5, 5)
        hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/s_menu2h.png", im.matrix.brightness(.1)), 5, 5)
        selected_idle_background Frame("content/gfx/interface/buttons/choice_buttons2s.png", 5, 5)
        selected_hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2s.png", im.matrix.brightness(.1)), 5, 5)
        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/s_menu2.png"), 5, 5)

    # Based Wooden buttons we inherited from WM Wood Skin.
    style wood_button:
        is button
        background Frame("content/gfx/interface/buttons/idle_wood.png", 5, 5)
        hover_background Frame("content/gfx/interface/buttons/hover_wood.png", 5, 5)
        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/idle_wood.png"), 5, 5)
        hover_sound "content/sfx/sound/sys/hover_2.wav"

    style wood_text:
        align (.5, .5)
        size 14
        color ivory
        hover_color red
        insensitive_color black

    style left_wood_button:
        is button
        idle_background Frame("content/gfx/interface/buttons/button_wood_left_idle.png", 5, 5)
        hover_background Frame("content/gfx/interface/buttons/button_wood_left_hover.png", 5, 5)
        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/button_wood_left_idle.png"), 5, 5)
        hover_sound "content/sfx/sound/sys/hover_2.wav"

    style right_wood_button:
        is button
        idle_background Frame("content/gfx/interface/buttons/button_wood_right_idle.png", 5, 5)
        hover_background Frame("content/gfx/interface/buttons/button_wood_right_hover.png", 5, 5)
        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/button_wood_right_idle.png"), 5, 5)
        hover_sound "content/sfx/sound/sys/hover_2.wav"

    # This is a simple white, semi transparrent button, prolly should be deleted.
    style white_cry_button:
        background Transform(Frame(im.Twocolor("content/gfx/frame/cry_box.png", white, white), 5, 5), alpha=.8)
        hover_background Transform(Frame(im.MatrixColor(im.Twocolor("content/gfx/frame/cry_box.png", white, aquamarine), im.matrix.brightness(.20)), 5, 5), alpha=.8)
        insensitive_background Transform(Frame(im.Sepia("content/gfx/frame/cry_box.png"), 5, 5), alpha=.8)
        ypadding 3

    # Parent of the Gismo's Blue Marble button that was used in Main Menu Screen for a while.
    style marble_button:
        is button
        idle_background Frame("content/gfx/interface/buttons/marble_button.webp", 5, 5)
        hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/marble_button.webp", im.matrix.brightness(.10)), 5, 5)
        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/marble_button.webp"), 5, 5)

    # Cool Blue button we use in a number of places (Main Screen that leads to Buildings/GL for example)
    style blue1:
        is button
        idle_background Frame("content/gfx/interface/buttons/blue3.png", 5, 5)
        idle_foreground Frame("content/gfx/interface/buttons/f1.png", 5, 5)

        hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/blue3.png", im.matrix.brightness(.15)), 5, 5)
        hover_foreground Frame(im.MatrixColor("content/gfx/interface/buttons/f1.png", im.matrix.brightness(.07)), 5, 5)

        insensitive_background Frame(im.Sepia("content/gfx/interface/buttons/blue3.png"), 5, 5)
        insensitive_foreground Frame("content/gfx/interface/buttons/f1.png", 5, 5)

        selected_idle_background Frame(im.MatrixColor("content/gfx/interface/buttons/blue3.png", im.matrix.tint(.6, .6, .6)), 5, 5)
        selected_idle_foreground Frame("content/gfx/interface/buttons/f1.png", 5, 5)

        selected_hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/blue3.png", im.matrix.tint(.6, .6, .6) * im.matrix.brightness(.15)), 5, 5)
        selected_hover_foreground Frame(im.MatrixColor("content/gfx/interface/buttons/f1.png", im.matrix.brightness(.07)), 5, 5)

    # Decent Wooden button, Used as a ND.
    style op1:
        is button
        idle_background Frame("content/gfx/interface/buttons/op3.png", 5, 5)
        hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/op3.png", im.matrix.brightness(.15)), 5, 5)
        idle_foreground Frame("content/gfx/interface/buttons/f1.png", 5, 5)
        hover_foreground Frame("content/gfx/interface/buttons/f1.png", 5, 5)

    # ---------------------------------- Text:
    # Base Fonts (*Just the fontname/alignment):
    style garamond:
        is text
        antialias True # Text in modern Ren'Py is always aa rendered?
        font "fonts/EBGaramond-Regular.ttf"

    transform caret_alpha:
        Solid(ivory, xysize=(1, 22))
        offset (1, 2)
        block:
            linear .8 alpha .2
            linear .8 alpha 1.0
            repeat

    # style input:
    #     caret caret_alpha()

    style TisaOTM:
        is text
        font tisa_otm_adv
        caret caret_alpha()

    style della_respira:
        is text
        antialias True # Text in modern Ren'Py is always aa rendered?
        font "fonts/dellarespira-regular.ttf"

    style myriadpro_reg:
        is text
        font "fonts/myriadpro-regular.otf"

    style myriadpro_sb:
        is text
        font "fonts/myriadpro-semibold.otf"

    style earthkid is text:
        size 20
        font "fonts/earthkid.ttf"
        align (.5, .5)

    style agrevue is text:
        size 20
        font "fonts/agrevue.ttf"
        align (.5, .5)

    style rubius is text:
        size 20
        font "fonts/rubius.ttf"
        align (.5, .5)

    style TisaSansOT is text:
        size 20
        font "fonts/TisaSansOT.otf"

    style TisaOTB:
        is text
        size 20
        font "fonts/TisaOTB.otf"

    style TisaOTBc:
        is TisaOTB
        align (.5, .5)

    style TisaOTMc:
        is TisaOTM
        align (.5, .5)


init 2: # Advanced style that can carry a lot of properties to be used in screens/labels.
    # ----
    # Customized to specific screens from default choices:
    # Default dropdown/interactions and etc.
    style dropdown_gm_frame:
        is default
        background Frame("content/gfx/frame/BG_choicebuttons.png", 10, 10)
        padding (10, 10)
    style dropdown_gm_text:
        is black_serpent
        xalign .5
    style dropdown_gm_button:
        is basic_choice_button
        size_group "dropdown_gm"
        padding (10, 1)
        xminimum 200
        # xalign 0
    style dropdown_gm_button_text:
        is TisaOTMc
        color black
        size 18

    # Second set of DD buttons:
    style dropdown_gm2_button:
        is basic_choice2_button
        padding (2, 0)
        margin (1, 1)
    style dropdown_gm2_button_text:
        is TisaOTMc
        drop_shadow [(1, 1)]
        drop_shadow_color black
        color "#EEE8CD"
        insensitive_color "#808069"
        size 16
        outlines [(1, "#3a3a3a", 0, 0)]
        selected_outlines [(1, "#8B3E2F", 0, 0)]
    style dropdown_gm2_button_value_text:
        is della_respira
        color "#EEE8CD"
        size 16
        outlines [(1, "#3a3a3a", 0, 0)]
        selected_outlines [(1, "#8B3E2F", 0, 0)]
    style dropdown_gm2_slider:
        is bar
        left_bar im.Scale("content/gfx/interface/bars/pref_full.png", 166, 21)
        right_bar im.Scale("content/gfx/interface/bars/pref_empty.png", 166, 21)
        hover_left_bar im.Scale("content/gfx/interface/bars/pref_full.png", 166, 21)
        hover_right_bar im.Scale("content/gfx/interface/bars/pref_empty.png", 166, 21)
        thumb None #im.Scale("content/gfx/interface/bars/pref_thumb.png", 18, 21)
        hover_thumb  None #im.Scale("content/gfx/interface/bars/pref_thumb.png", 18, 21)
        xmaximum 166
        align (.5, .5)

    # One of the most widely used styles in the game:
    # These are Gismo's Grey Button style we use all over the place.
    style basic_button:
        is basic_choice_button
        ypadding 1
    style basic_button_text:
        is TisaOTMc
        color black
        size 18
    style basic_text:
        is TisaOTMc
        color black
        hover_color red
        outlines [(1, "#aaa697", 0, 0)]
        hover_outlines [(1, "#3a3a3a", 0, 0)]
        size 18

    # Interactions:
    style interactions_text:
        is TisaOTMc
        drop_shadow [(1, 1)]
        drop_shadow_color black
        color "#c8ffff"
        # hover_color "#D2691E"
        size 20

    # This is the main style we'll use for normal content in the game (only the button for now).
    # Basically holds the two of the five fonts used in the game.
    style content:
        is default
    style content_text:
        is garamond
        line_leading -5
        size 17
        color black
    style content_label_text:
        is della_respira
        size 19
        color black

    # Style used for Stats.
    style base_stats_frame: # This one is presently used in the equipment screen. It overrides silly theme settings to allow for a better positioning and more convinient use.
        left_padding 9
        right_padding 11
        top_padding 4
        bottom_padding 1
        xmargin 0
        ymargin 0

    style proper_stats_frame:
        is frame
        background Frame("content/gfx/frame/stat_box_proper.png")
        padding (0, 0)
        margin (0, 0)
    style proper_stats_vbox:
        is vbox
        spacing 1
    style proper_stats_main_frame:
        is frame
        background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
        padding (12, 12)
        margin (0, 0)
    style proper_stats_text:
        is garamond
        color ivory
        outlines [(1, "#3a3a3a", 0, 0)]
        size 18
    style proper_stats_label_text:
        is della_respira
        outlines [(2, "#424242", 0, 0)]
        size 19
        color ivory
    style proper_stats_value_text:
        is della_respira
        outlines [(1, "#3a3a3a", 0, 0)]
        size 14
        color ivory
        yoffset 4
        xalign 1.0

    style pyp_frame:
        is frame
        background Frame("content/gfx/frame/mes11.webp", 10, 10)
        margin (0, 0)
        padding (6, 6)
    style pyp_title_frame:
        is frame
        background Frame("content/gfx/frame/gm_frame.png", 6, 6)
        margin (0, 0)
        padding (35, 6)
    style pyp_vbox:
        is proper_stats_vbox
    style pyp_text:
        is proper_stats_text
        xalign .0
    style pyp_label_text:
        is proper_stats_label_text

    # Style for profile buttons "pb"
    # Pretty and advanced style used in Heros Profile:
    style pb_button:
        is hframe_button
        padding (6, 5)
    style pb_button_text:
        font "fonts/rubius.ttf"
        size 17
        idle_color "#CDCDC1"
        hover_color "#F5F5DC"
        selected_idle_color "#CDAD00"
        selected_hover_color "#CDAD00"
        xalign .5

    style new_style_tooltip_frame:
        clear

        padding (20, 5)
        xminimum 100 xmaximum 350
        background Frame("content/gfx/interface/buttons/hp_1s.png", 5, 5)
    style new_style_tooltip_text:
        font tisa_otm_adv
        size 14
        color "#CDAD00"
        xalign .5
    style new_style_tooltip_be_skills_frame:
        is new_style_tooltip_frame
    style new_style_tooltip_be_skills_text:
        is new_style_tooltip_text
        xalign .0

    # Notifications:
    style notify_bubble:
        is default
    style notify_bubble_frame:
        background "#000"
        minimum (350, 15)
    style notify_bubble_vbox:
        xfill True
    style notify_bubble_text:
        is garamond
        line_leading -5
        size 15
        align (.5, .5)

    # MC Setup Screen:
    style mcsetup_button:
        is button
        xysize (175, 51)
        idle_background Frame("content/gfx/interface/images/story12.png", 1, 1)
        hover_background Frame(im.MatrixColor("content/gfx/interface/images/story12.png", im.matrix.brightness(.1)), 1, 1)
        insensitive_background Frame(im.Sepia("content/gfx/interface/images/story12.png"), 1, 1)
    style mcsetup_text:
        is text
        size 16
        font "fonts/TisaOTm.otf"
        color ivory
        hover_color red
        selected_color green
        insensitive_color "#808069"

    style sqstory_button:
        is button
        background Frame("content/gfx/frame/cry_box.png", 10, 10)
        xysize (60, 60)

    # Interactions are presently using these:
    style main_screen_3_frame:
        # This is for girlsmeets:
        is frame
        background Null()
    style main_screen_3_button:
        is blue1
        xalign .5
        xminimum 180
        xpadding 20
        ypadding 8
        activate_sound "content/sfx/sound/sys/hover_2.wav"
    style main_screen_3_button_text:
        is TisaOTBc
        size 20
        drop_shadow [(1, 1)]
        color azure

    # Used mainly as Next Day Button
    style main_screen_4_button:
        is op1
        xminimum 200
        xpadding 20
        ypadding 10
        activate_sound "content/sfx/sound/sys/hover_2.wav"
    style main_screen_4_button_text:
        is TisaOTBc
        size 20
        drop_shadow [(1, 1)]
        color azure

    # Sound button...
    style sound_button:
        subpixel True
        idle_background Frame(im.Sepia("content/gfx/interface/buttons/sound_icon.png"), 5, 5)
        hover_background Frame(im.MatrixColor(im.Sepia("content/gfx/interface/buttons/sound_icon.png"), im.matrix.brightness(.15)), 5, 5)
        selected_idle_background Frame("content/gfx/interface/buttons/sound_icon.png", 5, 5)
        selected_hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/sound_icon.png", im.matrix.brightness(.15)), 5, 5)

    # Specialized text styles: ===============>
    style TisaOTMol:
        is TisaOTM
        color "#ecc88a"
        size 14
        outlines [(1, "#3a3a3a", 0, 0)]

    style TisaOTMolxm: # With outlines:
        is TisaOTMol
        xalign .5
        size 17

    style library_book_header_main:
        is della_respira
        color black
        xalign .5
        bold True
        size 20

    style library_book_header_sub:
        is library_book_header_main
        size 18

    style library_book_content:
        is garamond
        color black
        size 15

    style black_serpent:
        is text
        size 20
        font "fonts/serpentn.ttf"
        color black
        align (.5, .5)

    style next_day_summary_text is text:
        size 16
        font "fonts/agrevue.ttf"
        color black

    style credits_text:
        font "fonts/rubius.ttf"
        antialias True
        line_spacing 6
        color azure

    style badaboom:
        is text
        antialias True
        size 20
        font "fonts/badaboom.ttf"

    style be_notify:
        is badaboom
        size 60
        color red
        outlines [(3, "#ffff19", 1, 1)]
        drop_shadow [(2, 3)]
        drop_shadow_color black

    # Text that goes with the wc button.
    style white_cry_button_text:
        is text
        xalign 0
        size 12
        bold True
        color black

    style arena_header_text:
        is garamond
        color red
        size 35
        outlines [(3, "#3a3a3a", 1, 1)]
        drop_shadow [(2, 3)]
        drop_shadow_color black

    style arena_badaboom_text:
        align (.5, .5)
        color red + "85"
        hover_color red
        font "fonts/badaboom.ttf"
        size 30

init: # Ren'Py Styles (Or replacements):
    ## FRAMEWORK FOR DIALOGUE
    ## Main (Say) window
    style window is default:
        background Frame("content/gfx/frame/say_window_frame.webp", 50, 50)
        xpos 640
        xfill True
        xmargin 0
        left_padding 205
        right_padding 75
        # xpadding 210
        ypadding 10
        yfill False
        ymargin 0
        yminimum 156
        xmaximum 1100

    ## Name two_window Box
    style say_who_window is default:
        background Frame("content/gfx/frame/Namebox.png", 25, 25)
        yalign 1.0
        pos (165, 38)
        xpadding 3
        ypadding 2
        minimum (115, 28)

    ## Dialogue main window text
    style say_thought:
        is TisaOTM
        size 18
        drop_shadow [(2, 2)]

    ## Dialogue two_window text
    style say_dialogue:
        is TisaOTM
        size 18
        drop_shadow [(2, 2)]

    style say_label:
        is TisaOTMc
        bold False
        size 18

    # Yes/No Prompt:
    style yesno_button:
        is dropdown_gm_button
        xpadding 7
        ypadding 5
        size_group "yesno"

    style yesno_button_text:
        is agrevue
        color black

    style yesno_label_text:
        is content_text
        text_align .5
        size 23
        bold True
        layout "subtitle"

    # # Choice Menu:
    style menu_window is default
    style menu_choice is interactions_text:
        clear

    style menu_choice_button:
        is button
        xminimum int(config.screen_width * .10)
        xmaximum int(config.screen_width * .80)
        xpadding 50
        size_group "choice_menu"
        background Frame("content/gfx/frame/chat_text_box_idle.png", 5, 5)
        hover_background Transform(Frame("content/gfx/frame/chat_text_box_hover.png", 5, 5), xzoom=1.07, yzoom=1.5, align=(.5, .5))
        insensitive_background Frame(im.Sepia("content/gfx/frame/chat_text_box_idle.png"), 5, 5)
        ysize 29

    style menu_choice_button_blue is menu_choice_button:
        background Frame(im.Twocolor("content/gfx/frame/chat_text_box_idle.png", white, blue), 5, 5)
        hover_background Transform(Frame(im.Twocolor("content/gfx/frame/chat_text_box_hover.png", white, blue), 5, 5), xzoom=1.07, yzoom=1.5, align=(.5, .5))

    # Main Menu and Preferences:
    # Gismo's New MM Version!
    style mmenu_button:
        is mmenu1_button
        ypadding 5
        xsize 170
    style mmenu_button_text:
        is smenu_text

    style smenu_button:
        is smenu1_button
        xysize (134, 44)
    style smenu_text:
        is TisaOTMc
        color "#66CDAA"
        hover_color "#CDC673"
        outlines [(1, "#3a3a3a", 0, 0)]
        hover_outlines [(1, "#3a3a3a", 0, 0)]
        selected_idle_color "#CDC673"
        selected_hover_color "#CDC673"
        insensitive_color "#808069"
        size 18
