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
                    for s in students:
                        # Blocks bad matches between student and course:
                        # Slaves can't do combat:
                        if course_type == "combat" and s.status == "slave":
                            renpy.notify("Slaves cannot take combat courses")
                            continue

                        # Free girls without naughty basetraits won't do xxx
                        c0 = course_type == "xxx"
                        c1 = s.status == "free"
                        c2 = "SIW" not in s.gen_occs
                        if all([c0, c1, c2]):
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
        pos 8, 48
        padding 10, 10
        xysize (500, 666)
        has vbox
        null height 3
        label ("[school.name]") xalign .5 text_color "ivory" text_size 25
        null height 3
        frame:
            xalign .5
            background Null()
            foreground Frame("content/gfx/frame/MC_bg2.png", 10, 10)
            add ProportionalScale(school.img, 450, 300)
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
                xsize 480
                draggable True
                mousewheel True
                scrollbars "vertical"
                vbox:
                    xsize 460
                    for s in extra_students:
                        hbox:
                            xsize 460
                            button:
                                xsize 20
                                background None
                                text "+" color "yellow" align (.5, .5)
                                #tooltip "%s is currently in your group." % s.name
                                action NullAction()

                            button:
                                xalign -1.0
                                background None
                                text ("[s.fullname]") color "lawngreen" hover_color "red" xalign .0
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
                xsize 480
                draggable True
                mousewheel True
                scrollbars "vertical"
                vbox:
                    xsize 460
                    spacing 10
                    for c in school.courses:
                        if c.students:
                            vbox:
                                xsize 460
                                hbox:
                                    xsize 460
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
                                    button:
                                        xalign -1.02
                                        background None
                                        text "[c.name] Course:" color "goldenrod" hover_color "red"
                                        if temp:
                                            action Return(["toggle_course", c, "remove"])
                                            tooltip "Remove course members from your group."
                                        else:
                                            action Return(["toggle_course", c, "add"])
                                            tooltip "Add course members to your group."

                                if c not in hidden_courses:
                                    for s in c.students:
                                        hbox:
                                            xsize 460
                                            if s in students:
                                                button:
                                                    xsize 20
                                                    background None
                                                    text "+" color "yellow" align (.5, .5)
                                                    #tooltip "%s is currently in your group." % s.name
                                                    action NullAction()
                                            else:
                                                null width 20

                                            button:
                                                xalign -1.0
                                                background None
                                                text ("[s.fullname]") color "lawngreen" hover_color "red" xalign .0
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
        xpos 1280-8 xanchor 1.0 ypos 48
        padding 10, 10
        xysize (760, 666)
        has viewport draggable 1 mousewheel 1 scrollbars "vertical"
        hbox:
            xsize 720 box_wrap 1
            for course in school.courses:
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
                            add ProportionalScale(course.img, 150, 150)
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
                        add pscale("content/gfx/interface/images/completed_stamp.webp", 130, 130):
                            xalign .5 ypos 210


    use top_stripe(True, show_lead_away_buttons=False)
