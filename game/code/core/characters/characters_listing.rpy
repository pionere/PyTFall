init:
    default chars_list_state = None
    python:
        def sorting_for_chars_list():
            return [c for c in hero.chars]

        class CharsListState(_object):
            def __init__(self):
                self.page = 0
                self.page_size = 10

                self.source = CharsSortingForGui(sorting_for_chars_list)

                self.status_filters = None
                #self.location_filters = None
                self.action_filters = None
                self.class_filters = None
                self.home_filters = None
                self.work_filters = None

                self.selected_filters = set()
                self.the_chosen = set()

            def refresh(self):
                # prepare the filters
                self.update_filter_sets()
                # update the chars list only if no filter was selected
                if not self.selected_filters:
                    self.source.filter()
                # remove selected chars which are no longer available
                gone_chars = set()
                for c in self.the_chosen:
                    if not (c.is_available and c in hero.chars):
                        gone_chars.add(c)
                if gone_chars:
                    self.the_chosen -= gone_chars

            def next(self):
                self.page += 1

            def prev(self):
                self.page -= 1

            def page_content(self):
                start = self.page*self.page_size
                return self.source.sorted[start:start+self.page_size]

            def update_filter_sets(self):
                self.status_filters = set()
                #self.location_filters = set()
                self.action_filters = set()
                self.class_filters = set()
                self.home_filters = set()
                self.work_filters = set()
                for c in hero.chars:
                    self.status_filters.add(c.status)
                    #self.locations_filters.add(c.location)
                    self.action_filters.add(c.action)
                    self.home_filters.add(c.home)
                    self.work_filters.add(c.workplace)
                    for bt in c.traits.basetraits:
                        self.class_filters.add(bt)

            def reset_filters(self):
                self.selected_filters = set()
                self.update_filter_sets()

                self.source.clear()
                self.source.filter()

            def toggleChosenMembership(self, chars):
                if self.the_chosen.issuperset(chars):
                    self.the_chosen.difference_update(chars)
                else:
                    self.the_chosen.update(chars)

label chars_list:
    scene bg gallery
    python:
        # lazy init the page state
        if chars_list_state is None:
            chars_list_state = CharsListState()
        chars_list_state.refresh()

    show screen chars_list()
    with dissolve

    python:
        while 1:

            result = ui.interact()

            if result[0] == "control":
                if result[1] == "return":
                    break
            elif result[0] == "dropdown":
                if result[1] == "workplace":
                    renpy.show_screen("set_workplace_dropdown", result[2], pos=renpy.get_mouse_pos())
                elif result[1] == "home":
                    renpy.show_screen("set_home_dropdown", result[2], pos=renpy.get_mouse_pos())
                elif result[1] == "action":
                    renpy.show_screen("set_action_dropdown", result[2], pos=renpy.get_mouse_pos())
            elif result[0] == "choice":
                renpy.hide_screen("chars_list")
                girls = [char for char in chars_list_state.source.sorted if char.is_available and char in hero.chars]
                char = result[1]
                char_profile_entry = "chars_list"
                jump('char_profile')
            elif result[0] == "group":
                if result[1] == "control":
                    char = PytGroup(list(chars_list_state.the_chosen))
                    renpy.show_screen("char_control")
                elif result[1] == "equip":
                    renpy.hide_screen("chars_list")
                    came_to_equip_from = "chars_list"
                    equip_girls = list(chars_list_state.the_chosen)
                    eqtarget = equip_girls[0]
                    jump('char_equip')
                elif result[1] == "training":
                    renpy.hide_screen("chars_list")
                    the_chosen = list(chars_list_state.the_chosen)
                    jump('school_training')

    hide screen chars_list
    jump mainscreen

screen chars_list():
    key "mousedown_3" action Return(['control', 'return']) # keep in sync with button - alternate

    # the number of filtered workers
    $ num_chars = len(chars_list_state.source.sorted)

    # Normalize pages.
    python:
        max_page = 0 if num_chars == 0 else ((num_chars-1)/chars_list_state.page_size)
        if chars_list_state.page > max_page:
            chars_list_state.page = max_page

    # Chars:
    $ charz_list = chars_list_state.page_content()
    if num_chars == 0:
        python:
            if hero.chars:
                msg = "No worker matches the filters."
            else:
                msg = "You don't have any workers." 
        text "[msg]":
            size 40
            color "ivory"
            align .5, .2
            style "TisaOTM"
    else:
        hbox:
            style_group "content"
            spacing 14
            pos 27, 59
            xysize 970, 600
            box_wrap True
            for c in charz_list:
                $ char_profile_img = c.show('portrait', resize=(98, 98), cache=True)
                $ img = "content/gfx/frame/ink_box.png"
                $ available = c.is_available and c in hero.chars
                button:
                    ymargin 0
                    idle_background Frame(Transform(img, alpha=.4), 10 ,10)
                    hover_background Frame(Transform(img, alpha=.9), 10 ,10)
                    xysize (470, 120)
                    alternate Return(['control', 'return']) # keep in sync with mousedown_3
                    if available:
                        action Return(['choice', c])
                        tooltip "Show {}'s Profile!".format(c.name)
                    else:
                        action NullAction()

                    # Image:
                    frame:
                        background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
                        padding 0, 0
                        align 0, .5
                        xysize 100, 100
                        add char_profile_img align .5, .5 alpha .96

                    # Texts/Status:
                    frame:
                        xpos 120
                        xysize (335, 115)
                        background Frame(Transform("content/gfx/frame/p_frame2.png", alpha=.6), 10, 10)
                        vbox:
                            xpos 10

                            # Name
                            label "[c.name]":
                                text_size 18
                                if c.__class__ == Char:
                                    text_color "pink"
                                else:
                                    text_color "goldenrod"

                            # Prof-Classes
                            python:
                                classes = list(t.id for t in c.traits.basetraits)
                                classes.sort()
                                classes = ", ".join(classes)
                            null height 4
                            text "Classes: [classes]" color "goldenrod" size 18

                        if available:
                            vbox:
                                pos 10, 46
                                style_prefix "proper_stats"
                                spacing -5
                                $ circle_green = im.Scale("content/gfx/interface/icons/move15.png", 12, 12)
                                hbox:
                                    add circle_green yalign 0.5 xoffset -2
                                    fixed:
                                        xysize 30, 14
                                        yalign .5
                                        text "Home:" color "ivory" yalign .5 size 14
                                    button:
                                        style_group "ddlist"
                                        xalign .0
                                        if c.status == "slave":
                                            action Return(["dropdown", "home", c])
                                            tooltip "Choose a place for %s to live at!" % c.nickname
                                        else: # Can't set home for free cs, they decide it on their own.
                                            action NullAction()
                                            tooltip "%s is free and decides on where to live at!" % c.nickname
                                        text "[c.home]" size 14
                                hbox:
                                    add circle_green yalign 0.5 xoffset -2
                                    fixed:
                                        xysize 30, 14
                                        yalign .5
                                        text "Work:" color "ivory" yalign .5 size 14
                                    button:
                                        style_group "ddlist"
                                        xalign .0
                                        action Return(["dropdown", "workplace", c])
                                        tooltip "Choose a place for %s to work at!" % c.nickname
                                        text "[c.workplace]" size 14
                                hbox:
                                    add circle_green yalign 0.5 xoffset -2
                                    fixed:
                                        xysize 30, 14
                                        yalign .5
                                        text "Action:" color "ivory" yalign .5 size 14
                                    button:
                                        style_group "ddlist"
                                        xalign .0
                                        action Return(["dropdown", "action", c])
                                        tooltip "Choose a task for %s to do!" % c.nickname
                                        text action_str(c) size 14

                        vbox:
                            align (.96, .035)
                            python:
                                if available:
                                    if c.status == "slave":
                                        status_img = "content/gfx/interface/icons/slave.png"
                                    else:
                                        status_img = "content/gfx/interface/icons/free.png"
                                elif c.action == ExplorationTask:
                                    status_img = "content/gfx/interface/icons/exploring.png"
                                elif c.location == pytfall.jail:
                                    status_img = "content/gfx/interface/icons/arena.png"
                                elif c.location == pytfall.ra:
                                    status_img = "content/gfx/interface/images/MC/reflexes.png"
                                elif c.home == pytfall.afterlife:
                                    status_img = "content/gfx/interface/icons/gravestone.png"
                                else:
                                    status_img = "content/gfx/interface/icons/question.png"
                            add ProportionalScale(status_img, 40, 40)

                        vbox:
                            align 1.0, .6 xoffset 5
                            hbox:
                                xsize 60
                                $ temp = c.PP/100 # PP_PER_AP
                                text "AP:" xalign .0 color "ivory"
                                text str(temp) xalign .1 color "ivory"
                            hbox:
                                xsize 60
                                text "Tier:" xalign .0 color "ivory"
                                text "[c.tier]" xalign .1 color "ivory"

                    # Add to Group Button:
                    if available:
                        if c in chars_list_state.the_chosen:
                            $ img = "content/gfx/interface/icons/checkbox_checked.png"
                        else:
                            $ img = "content/gfx/interface/icons/checkbox_unchecked.png"
                        button:
                            style_group "basic"
                            xysize (25, 25)
                            align 1.0, 1.0 offset 9, -2
                            action ToggleSetMembership(chars_list_state.the_chosen, c)
                            add im.Scale(img, 25, 25) align .5, .5
                            tooltip 'Select the character'

        # Paging:
        if max_page > 0:
            hbox:
                pos 27, 659
                xysize 970, 60

                hbox:
                    style_prefix "paging_green"
                    align .5, .5
                    spacing 20
                    $ curr_page = chars_list_state.page + 1
                    button:
                        style_suffix "button_left"
                        tooltip "Previous Page"
                        action Function(chars_list_state.prev)
                        sensitive curr_page != 1
                        keysym "mousedown_4"

                    text "[curr_page]." color "ivory" yalign .5

                    button:
                        style_suffix "button_right"
                        tooltip "Next Page"
                        action Function(chars_list_state.next)
                        sensitive (curr_page <= max_page)
                        keysym "mousedown_5"

    # Filters:
    frame:
        background Frame(Transform("content/gfx/frame/p_frame2.png", alpha=.55), 10 ,10)
        style_prefix "content"
        xmargin 0
        padding 5, 5
        pos (1005, 47)
        xysize (270, 468)
        vbox:
            xalign .5
            spacing 3
            label "Filters:":
                xalign .5
                text_size 35
                text_color "goldenrod"
                text_outlines [(1, "black", 0, 0)]

            hbox:
                xalign .5
                box_wrap True
                for f, c, t in [('Home', "saddlebrown", 'Toggle home filters'),
                                ('Work', "brown", 'Toggle workplace filters'),
                                ("Status", "green", 'Toggle status filters'),
                                ("Action", "darkblue", 'Toggle action filters'),
                                ('Class', "purple", 'Toggle class filters')]:
                    button:
                        style_prefix "basic"
                        xpadding 6
                        xsize 100
                        action ToggleSetMembership(chars_list_state.selected_filters, f)
                        tooltip t
                        text f color c size 18 outlines [(1, "#3a3a3a", 0, 0)]

                button:
                    style_group "basic"
                    xsize 100
                    action [chars_list_state.reset_filters, renpy.restart_interaction]
                    tooltip 'Reset all filters'
                    text "Reset"

            null height 3

            vpgrid:
                style_prefix "basic"
                xysize 256, 289
                xalign .5
                cols 2
                draggable True edgescroll (30, 100)
                if "Status" in chars_list_state.selected_filters:
                    for f in chars_list_state.status_filters:
                        button:
                            xysize 125, 32
                            action ModFilterSet(chars_list_state.source, "status_filters", f)
                            text f.capitalize() color "green"
                            tooltip 'Toggle the filter'
                if "Home" in chars_list_state.selected_filters:
                    for f in chars_list_state.home_filters:
                        button:
                            xysize 125, 32
                            action ModFilterSet(chars_list_state.source, "home_filters", f)
                            text "[f]" color "saddlebrown":
                                if len(str(f)) > 12:
                                    size 10
                                    line_spacing -6
                                else:
                                    layout "nobreak"
                            tooltip 'Toggle the filter'
                if "Work" in chars_list_state.selected_filters:
                    for f in chars_list_state.work_filters:
                        button:
                            xysize 125, 32
                            action ModFilterSet(chars_list_state.source, "work_filters", f)
                            text "[f]" color "brown":
                                if len(str(f)) > 12:
                                    size 10
                                    line_spacing -6
                                else:
                                    layout "nobreak"
                            tooltip 'Toggle the filter'
                if "Action" in chars_list_state.selected_filters:
                    for f in chars_list_state.action_filters:
                        button:
                            xysize 125, 32
                            action ModFilterSet(chars_list_state.source, "action_filters", f)
                            $ temp = getattr(f, "id", "None")
                            text temp color "darkblue":
                                if len(temp) > 12:
                                    size 10
                                    line_spacing -6
                                else:
                                    layout "nobreak"
                            tooltip 'Toggle the filter'
                if "Class" in chars_list_state.selected_filters:
                    for f in chars_list_state.class_filters:
                        button:
                            xysize 125, 32
                            action ModFilterSet(chars_list_state.source, "class_filters", f)
                            text "[f]" color "purple"
                            tooltip 'Toggle the filter'

    # Sorting
    frame:
        background Frame(Transform("content/gfx/frame/MC_bg.png", alpha=.55), 10 ,10)
        xmargin 0
        padding 5, 5
        pos (1005, 518)
        xysize (270, 50)
        style_group "proper_stats"
        has hbox spacing 10 align .5, .5
        label "Sort:":
            yalign .5 
            text_size 20
            text_color "goldenrod"
            text_outlines [(1, "black", 0, 0)]

        $ options = OrderedDict([("level", "Level"), ("name", "Name"), ("disposition", "Disposition"), ("affection", "Affection"), (None, "-")])
        $ temp = chars_list_state.source.sorting_order
        use dropdown_box(options, max_rows=6, row_size=(160, 30), pos=(1064, 530), value=temp, field=(chars_list_state.source, "sorting_order"), action=Function(chars_list_state.source.filter))

        button:
            xysize (25, 25)
            align 1.0, 0.5 #offset 9, -2
            background Frame(Transform("content/gfx/frame/MC_bg2.png", alpha=.55), 5, 5)
            action ToggleField(chars_list_state.source, "sorting_desc"), Function(chars_list_state.source.filter)
            if chars_list_state.source.sorting_desc:
                add(im.Scale('content/gfx/interface/icons/checkbox_checked.png', 20, 20)) align .5, .5
            else:
                add(im.Scale('content/gfx/interface/icons/checkbox_unchecked.png', 20, 20)) align .5, .5
            tooltip 'Descending order'

    # Mass (de)selection Buttons ====================================>
    hbox:
        pos 1005, 568
        xsize 270
        frame:
            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.9), 10, 10)
            xysize (90, 150)
            style_prefix "basic"
            has vbox spacing 3 align .5, .5
            button: # select all on current listing, deselects them if all are selected
                xysize (66, 40)
                action Function(chars_list_state.toggleChosenMembership, set(charz_list))
                sensitive num_chars != 0
                text "These"
                tooltip "Select all currently visible characters"
            button: # every of currently filtered, also in next tabs
                xysize (66, 40)
                action Function(chars_list_state.toggleChosenMembership, set(chars_list_state.source.sorted))
                sensitive num_chars != 0
                text "All"
                tooltip "Select all characters"
            button: # deselect all
                xysize (66, 40)
                action Function(chars_list_state.the_chosen.clear)
                sensitive chars_list_state.the_chosen
                text "None"
                tooltip "Clear Selection"

        # Mass action Buttons ====================================>
        frame:
            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.9), 10, 10)
            align .5, .5
            style_prefix "basic"
            xysize (170, 150)
            has vbox spacing 3 align .5, .5
            button:
                xysize (150, 40)
                action Return(["group", "control"])
                sensitive chars_list_state.the_chosen
                text "Controls"
                selected False
                tooltip "Set desired behavior for the selected characters"
            button:
                xysize (150, 40)
                action Return(["group", "equip"])
                sensitive chars_list_state.the_chosen
                text "Equipment"
                selected False
                tooltip "Manage the equipment of the selected characters"
            button:
                xysize (150, 40)
                action Return(["group", "training"])
                sensitive chars_list_state.the_chosen
                text "Training"
                selected False
                tooltip "Send the selected characters to School"

    use top_stripe()

screen dropdown_box(options, max_rows, row_size, pos, value=None, field=None, action=None):
    frame:
        align (.5, .5)
        xysize row_size
        $ tmp = options.get(value, "None")
        $ xsize, ysize = row_size
        button:
            background Null()
            xysize row_size
            action Show("dropdown_content", options=options, max_rows=max_rows, row_size=row_size, pos=pos, value=value, field=field, action=action)
            text tmp idle_color "beige" align .5, .5 hover_color "crimson" size min(ysize-5, int(3*xsize/max(1, 2*len(tmp))))
            hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)

screen dropdown_content(options, max_rows, row_size, pos, value=None, field=None, action=None):
    # Trying to create a drop down screen with choices of actions:
    zorder 10
    modal True

    #key "mousedown_4" action NullAction()
    #key "mousedown_5" action NullAction()

    # Get mouse coords:
    python:
        x, y = pos
        if y > config.screen_height/2:
            yval = 1.0
        else:
            y += row_size[1]
            yval = .0
        xsize, ysize = row_size

    frame:
        background Frame(Transform("content/gfx/frame/MC_bg.png", alpha=.55), 10 ,10)
        #style_prefix "content"
        xmargin 0
        padding 5, 5
        pos (x, y)
        yanchor yval
        xsize xsize+10
        ymaximum (ysize*max_rows + 10)
        style_group "proper_stats"
        viewport:
            xsize xsize
            ymaximum ysize*max_rows
            mousewheel True
            has vbox
            for key, option in options.items():
                python:
                    btn_action = []
                    if field is None:
                        btn_action.append(Return(key))
                    else:
                        btn_action.append(SetField(field[0], field[1], key))
                        if action is not None:
                            if not isinstance(action, list):
                                action = [action] 
                            btn_action.extend(action)
                    btn_action.extend([Hide("dropdown_content"), With(Dissolve(0.1))])
                button:
                    background Null()
                    xysize (xsize, ysize)
                    selected key == value
                    action btn_action
                    text option idle_color "beige" hover_color "crimson" selected_color "aqua" align .5, .5 size min(ysize-5, int(3*xsize/max(1, 2*len(option))))
                    hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)
            python:
                rtn_action = []
                if field is None:
                    rtn_action.append(Return(value))
                rtn_action.extend([Hide("dropdown_content"), With(Dissolve(0.1))])
            button:
                background Null()
                xysize (xsize, ysize)
                action rtn_action
                text "Close" idle_color "brown" align .5, .5 hover_color "crimson" 
                hover_background Frame(im.MatrixColor("content/gfx/interface/buttons/choice_buttons2h.png", im.matrix.brightness(.10)), 5, 5)
                keysym "mousedown_3", "K_ESCAPE"
