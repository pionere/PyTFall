label school_training:
    # Make sure we set char to the_chosen (means we came from listing)
    python:
        school = pytfall.school
        students = getattr(store, "the_chosen", None)
        if students is None:
            students = [char]

    show screen school_training

    while 1:
        $ result = ui.interact()

        if result[0] == "set_course":
            python hide:
                course = result[1]

                if any((s not in course.students) for s in students):
                    # add students to the course
                    course_type = course.data.get("type", None)
                    tier_low = course.difficulty - 2
                    tier_high = course.difficulty + 1
                    for s in students:
                        # Blocks bad matches between student and course:
                        if s.tier > tier_high:
                            renpy.notify("The course is useless if tier is higher than %s" % tier_high)
                            continue

                        if s.tier < tier_low:
                            renpy.notify("The course requires at least tier %s" % tier_low)
                            continue

                        # Slaves can't do combat:
                        if course_type == "combat":
                            if s.status == "slave":
                                renpy.notify("Slaves cannot take combat courses")
                                continue
                            if "Combatant" not in s.gen_occs:
                                renpy.notify("Free non combatants won't take Combat courses")
                                continue

                        # Free girls without naughty basetraits won't do xxx
                        elif course_type == "xxx":
                            if s.status == "free" and "SIW" not in s.gen_occs:
                                renpy.notify("Free non whores won't take XXX courses")
                                continue

                        curr_course = school.get_course(s)
                        if curr_course != course:
                            s.set_task(StudyingTask, course)
                else:
                    # remove students from the course
                    for s in students:
                        s.set_task(None)
        elif result[0] == "stop_student":
            python hide:
                s = result[1]
                s.set_task(None)
        elif result[0] == "toggle_student":
            python hide:
                s = result[1]
                if s in students:
                    students.remove(s)
                else:
                    students.append(s)
        elif result[0] == "toggle_course":
            python hide:
                course = result[1]
                if result[2] == "remove":
                    for s in course.students:
                        if s in students:
                            students.remove(s) 
                else: # "add"
                    for s in course.students:
                        if s not in students:
                            students.append(s)
        elif result == ["control", "return"]:
            jump return_from_school_training

label return_from_school_training:
    hide screen school_training
    $ del school, students

    if getattr(store, "the_chosen", None) is None:
        jump char_profile
    else:
        $ del the_chosen
        jump chars_list

init python:
    def school_desc_string():
        temp = []
        temp.append("The Beautiful educational facilities in PyTFall offer")
        temp.append("training for free citizens,")
        temp.append("foreigners and slaves alike. Centuries old traditions will make certain")
        temp.append("that no student taking classes here will ever be sad or unhappy.")
        temp.append("Nothing in this world is free and courses here")
        temp.append("will cost you a dime and if you wish to be trained")
        temp.append("by the Masters, a small fortune.")
        rv = " ".join(temp)

        return rv

screen school_training():
    # School info:
    frame:
        style_prefix "content"
        background Frame("content/gfx/frame/mes12.jpg", 10, 10)
        pos 6, 44
        padding 10, 10
        xysize (520, 670)
        has vbox
        null height 3
        label ("[school.name]") xalign .5 text_color "ivory" text_size 25
        null height 3
        frame:
            xalign .5
            background Null()
            foreground Frame("content/gfx/frame/MC_bg2.png", 10, 10)
            add PyTGFX.scale_content(school.img, 450, 300)
        null height 8
        default desc = school_desc_string()
        text "[desc]" color "ivory"
        default selected_list = "courses"
        default hidden_courses = set()
        $ extra_students = [s for s in students if school.get_course(s) is None]
        null height 5
        if selected_list == "extra" and extra_students:
            button:
                background None
                xalign .5
                text "Students in your group who are not taking courses:" color "ivory" hover_color "red"
                action SetScreenVariable("selected_list", "courses")
                tooltip "View active students."
            null height 3
            viewport:
                xsize 500
                draggable True
                mousewheel True
                scrollbars "vertical"
                has vbox xfill True
                for s in extra_students:
                    hbox:
                        xfill True
                        button:
                            xsize 20
                            background None
                            text "+" color "yellow" align (.5, .5)
                            #tooltip "%s is currently in your group." % s.name
                            action NullAction()

                        $ temp = "%s (%s.)" % (s.fullname, roman_num(s.tier))
                        button:
                            xalign -1.0
                            background None
                            text temp color "lawngreen" hover_color "red" xalign .0
                            action Return(["toggle_student", s])
                            tooltip "Remove %s from your group." % s.name
        else:
            $ selected_list = "courses"
            button:
                background None
                xalign .5
                text "Students currently taking courses here:" color "ivory":
                    if extra_students:
                        hover_color "red"
                if extra_students:
                    action SetScreenVariable("selected_list", "extra")
                    tooltip "View students in your group who are not taking courses."
            null height 3
            viewport:
                xsize 500
                draggable True
                mousewheel True
                scrollbars "vertical"
                has vbox xfill True spacing 10
                for c in school.courses:
                    if c.students:
                        vbox:
                            xfill True
                            hbox:
                                xfill True
                                button:
                                    xsize 20
                                    background None
                                    if c in hidden_courses:
                                        text ">" color "yellow" align (.5, .5)
                                        tooltip "Show course members."
                                        action Function(hidden_courses.discard, c)
                                    else:
                                        text "v" color "yellow" align (.5, .5)
                                        tooltip "Hide course members."
                                        action Function(hidden_courses.add, c)

                                $ temp = any(s in students for s in c.students)
                                $ tmp = "%s Course (%s.):" % (c.name, roman_num(c.difficulty))
                                button:
                                    xalign -1.02
                                    background None
                                    text tmp color "goldenrod" hover_color "red"
                                    if temp:
                                        action Return(["toggle_course", c, "remove"])
                                        tooltip "Remove course members from your group."
                                    else:
                                        action Return(["toggle_course", c, "add"])
                                        tooltip "Add course members to your group."

                            if c not in hidden_courses:
                                for s in c.students:
                                    hbox:
                                        xfill True
                                        if s in students:
                                            button:
                                                xsize 20
                                                background None
                                                text "+" color "yellow" align (.5, .5)
                                                #tooltip "%s is currently in your group." % s.name
                                                action NullAction()
                                        else:
                                            null width 20

                                        $ temp = "%s (%s.)" % (s.fullname, roman_num(s.tier))
                                        button:
                                            xalign -1.0
                                            background None
                                            text temp color "lawngreen" hover_color "red" xalign .0
                                            action Return(["toggle_student", s])
                                            if s in students:
                                                tooltip "Remove %s from your group." % s.name
                                            else:
                                                tooltip "Add %s to your group." % s.name
                                        button:
                                            xalign .9
                                            background None
                                            if s in c.completed:
                                                text "(Completed)" color "goldenrod" hover_color "red"
                                            else:
                                                $ days_left = c.days_to_complete - c.students_progress.get(s, 0)
                                                $ can_complete = c.days_remaining >= days_left
                                                if can_complete:
                                                    text "([days_left] days to complete)" color "ivory" hover_color "red"
                                                else:
                                                    text "(can't complete)" color "ivory" hover_color "red"
                                            action Return(["stop_student", s])
                                            tooltip "Stop %s from taking the course." % s.name

    frame:
        style_prefix "content"
        background Frame("content/gfx/frame/mes11.webp", 10, 10)
        padding 10, 10
        xysize (746, 670)
        pos 529, 44
        has vbox spacing 1
        python:
            tier_filter = school.tier_filter
            type_filter = school.type_filter
            courses = [c for c in school.courses if c.difficulty == tier_filter and c.data.get("type", None) in type_filter]

        # filters
        #  tier
        hbox:
            xalign .5
            for i in xrange(MAX_TIER+1):
                textbutton "%s." % roman_num(i):
                    xysize (60, 40)
                    style "smenu1_button"
                    action SetField(school, "tier_filter", i)
                    selected tier_filter == i

        #  type
        hbox:
            xalign .5
            for c in (("xxx", "XXX"), ("combat", "Combat"), (None, "Any")):
                textbutton c[1]:
                    xysize (100, 30)
                    style "mmenu1_button"
                    text_size 16
                    action Function(school.toggle_type_filter, c[0])
                    selected c[0] in type_filter

        # cards of the courses:
        vpgrid:
            draggable True
            mousewheel True
            scrollbars "vertical"
            xysize (740, 610)
            cols 4
            for course in courses:
                button:
                    style "mmenu1_button"
                    margin 2, 2
                    padding 5, 5
                    xysize 180, 350
                    action Return(["set_course", course])
                    tooltip course.tooltip
                    vbox:
                        xalign .5
                        spacing 2
                        text course.name + " Course" xalign .5 color "ivory" style "dropdown_gm2_button_value_text"
                        frame:
                            xalign .5
                            background Null()
                            foreground Frame("content/gfx/frame/MC_bg2.png", 10, 10)
                            add PyTGFX.scale_content(course.img, 150, 150)
                    text "---------------------------------":
                        xalign .5
                        color "ivory"
                        ypos 190
                    vbox:
                        ypos 205
                        xalign .5
                        style_prefix "proper_stats"
                        frame:
                            xysize (160, 20)
                            xalign .5
                            text "Days Left":
                                xalign .02
                                color "#79CDCD"
                                hover_color "ivory"
                                size 15
                            text "[course.days_remaining]/[course.duration]":
                                style_suffix "value_text"
                                hover_color "green"
                                size 14
                                xalign .99 yoffset -1
                        frame:
                            xysize (160, 20)
                            xalign .5
                            text "Days to Complete":
                                xalign .02
                                color "#79CDCD"
                                hover_color "ivory"
                                size 15
                            python:
                                temp = None if students else "--" # days_left
                                tmp = None  # enough days left to complete
                                for s in students:
                                    t = course.days_to_complete - course.students_progress.get(s, 0)
                                    c = "green" if t <= course.days_remaining else "red"
                                    if temp is None:
                                        temp = t
                                        tmp = c
                                    else:
                                        if temp != t:
                                            temp = "--"
                                        if tmp != c:
                                            tmp = None

                            text "[temp]/[course.days_to_complete]":
                                style_suffix "value_text"
                                if tmp is not None:
                                    hover_color tmp
                                size 14
                                xalign .99 yoffset -1

                        frame:
                            xysize (160, 20)
                            xalign .5
                            text "Tier":
                                xalign .02
                                color "#79CDCD"
                                hover_color "ivory"
                                size 15
                            python:
                                temp = None  # appropriate difficulty
                                for s in students:
                                    t = "green" if s.tier <= course.difficulty else "red"
                                    if temp is None:
                                        temp = t
                                    elif temp != t:
                                        temp = None
                                        break
                            text "[course.difficulty]":
                                style_suffix "value_text"
                                if temp is not None:
                                    hover_color temp
                                size 14
                                xalign .99 yoffset -1
                        frame:
                            xysize (160, 20)
                            xalign .5
                            text "Effectiveness":
                                xalign .02
                                color "#79CDCD"
                                hover_color "ivory"
                                size 15
                            text "[course.effectiveness]":
                                style_suffix "value_text"
                                hover_color "green"
                                size 14
                                xalign .99 yoffset -1
                        frame:
                            xysize (160, 20)
                            xalign .5
                            text "Price":
                                xalign .02
                                color "#79CDCD"
                                hover_color "ivory"
                                size 15
                            text "[course.price]":
                                style_suffix "value_text"
                                hover_color "green"
                                size 14
                                xalign .99 yoffset -1
                        frame:
                            xysize (160, 20)
                            xalign .5
                            text "Status":
                                xalign .02
                                color "#79CDCD"
                                hover_color "ivory"
                                size 15
                            python:
                                temp = None if students else "--"  # status
                                for s in students:
                                    t = course.get_status(s)
                                    if temp is None:
                                        temp = t
                                    elif temp != t:
                                        temp = "--"
                                        break
                            text "[temp]":
                                style_suffix "value_text"
                                if temp == "Active!":
                                    color "orange"
                                else:
                                    hover_color "green" size 14
                                xalign .99 yoffset -1

                    python:
                        temp = None  # completed
                        for s in students:
                            t = s in course.completed
                            if temp is None:
                                temp = t
                            elif temp != t:
                                temp = None
                                break
                    if temp is True:
                        add PyTGFX.scale_img("content/gfx/interface/images/completed_stamp.webp", 130, 130):
                            xalign .5 ypos 210


    use top_stripe(True, show_lead_away_buttons=False)
