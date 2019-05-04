init python:
    class NextDayStats(_object):
        def __init__(self):
            super(NextDayStats, self).__init__()
            self.event_list = list()
            self.unassigned_chars = 0

        def append(self, evt):
            self.event_list.append(evt)

        def prepare_summary(self):
            # By Actions, Flags and Buildings...

            nd_stats = OrderedDict()

            base = {}
            for j in simple_jobs:
                base[j.type] = 0
            total_clients = 0
            for setup in [b for b in hero.buildings if b.expects_clients] + ["ALL"]:
                a = base.copy()
                r = base.copy()
                e = base.copy()
                for i in e:
                    e[i] = {"count": 0, "red_flag": 0, "green_flag": 0}

                # Actions/Rest first:
                if setup == "ALL":
                    container = hero.chars
                else:
                    container = [c for c in hero.chars if setup == c.workplace]

                for char in container:
                    action = char.action
                    job = char.job
                    
                    cat = getattr(job, "type", "Resting")
                    if cat == "SIW":
                        cat = "Service" # merge SIW and Service jobs
                    if action == job:
                        a[cat] += 1
                    elif action in [RestTask, AutoRestTask]:
                        r[cat] += 1
                    
                    # Events:
                    for event in self.event_list:
                        if setup != "ALL" and event.loc != setup:
                            continue
                        if event.char == char:
                            e[cat]["count"] += 1
                            if event.red_flag:
                                e[cat]["red_flag"] += 1
                            if event.green_flag:
                                e[cat]["green_flag"] += 1

                stats = {"actives": a, "rests": r, "events": e}
                if setup == "ALL":
                    stats["clients"] = total_clients

                    self.nd_all_stats = stats
                else:
                    if setup.maxfame != 0:
                        stats["fame"] = (setup.fame, setup.maxfame)
                    if setup.maxrep != 0:
                        stats["rep"] = (setup.rep, setup.maxrep)
                    if setup.maxdirt != 0:
                        stats["dirt"] = setup.get_dirt_percentage()
                    if setup.maxthreat != 0:
                        stats["threat"] = setup.get_threat_percentage()

                    clients = len(setup.all_clients)
                    stats["clients"] = clients

                    total_clients += clients

                    nd_stats[setup] = stats

            self.nd_stats = nd_stats

            self.hero_hp = hero.get_stat("health")
            self.hero_mp = hero.get_stat("mp")
            self.hero_vp = hero.get_stat("vitality")

            self.hero_max_hp = hero.get_max("health")
            self.hero_max_mp = hero.get_max("mp")
            self.hero_max_vp = hero.get_max("vitality")

            self.hero_income, self.hero_expense, self.hero_total = hero.fin.get_game_total()

            free = slaves = 0
            for char in hero.chars:
                if char.status == "slave":
                    slaves += 1
                else:
                    free += 1
            self.free = free
            self.slaves = slaves

        def get_nd_stats(self):
            return self.nd_stats, self.nd_all_stats

        def get_hero_hp(self):
            return self.hero_hp, self.hero_max_hp
        def get_hero_mp(self):
            return self.hero_mp, self.hero_max_mp
        def get_hero_vp(self):
            return self.hero_vp, self.hero_max_vp

        def get_hero_fin(self):
            return self.hero_income, self.hero_expense, self.hero_total

        def get_chars_dist(self):
            return self.free, self.slaves


label next_day:
    scene

    if getattr(store, "just_view_next_day", False): # Review old reports:
        $ del just_view_next_day
    else: # Do the calculations:
        show screen next_day_calculations

        if global_flags.flag("nd_music_play"):
            $ global_flags.del_flag("nd_music_play")
            $ PyTFallStatic.play_music("pytfall")
        $ global_flags.set_flag("keep_playing_music")

        $ nd_turns = getattr(store, "nd_turns", 1)
        while nd_turns:
            call next_day_calculations from _call_next_day_calculations
            $ nd_turns -= 1
        $ del nd_turns
        # prepare the data to show to the player
        $ NextDayEvents.prepare_summary()
        $ global_flags.set_flag("day_start")

    # Preparing to display ND.
    ####### - - - - - #######
    # Sort data for summary reports:
    $ nd_stats, nd_all_stats = NextDayEvents.get_nd_stats()
    # Setting index and picture
    $ FilteredList = NextDayEvents.event_list
    $ event_index = 0

    hide screen next_day_calculations

    call next_day_controls from _call_next_day_controls
    if _return:
        jump next_day

    hide screen next_day

    if persistent.auto_saves:
        call special_auto_save from _call_special_auto_save

    $ del FilteredList, nd_stats, nd_all_stats, event_index
    jump mainscreen

label next_day_calculations:
    python hide:
        tl.start("Next Day")

        global NextDayEvents
        NextDayEvents = NextDayStats()
        nd_debug("Day: %s, Girls (Player): %s, Girls (Game): %s" % (day, len(hero.chars), len(chars)))

        # Fog of war over fg areas:
        for area in store.fg_areas.values():
            temp = getattr(area, "explored", 0) 
            if temp > 0:
                area.explored -= 1

        # Building events Start:
        tl.start("ND-Rest (Before Work)")
        for c in hero.chars:
            if c.is_available:
                c.nd_rest()
        tl.end("ND-Rest (Before Work)")

        # run the next day logic of the building:
        tl.start("ND-Buildings")
        for b in hero.buildings:
            b.next_day()
        tl.end("ND-Buildings")
        # Building events END.

        ################## Logic ##################
        tl.start("pytfall/calender .next_day")
        pytfall.next_day()
        calendar.next()                 # day + 1 is here.
        tl.end("pytfall/calender .next_day")

        # Reset Flags:
        tl.start("ND-Flags Reset")
        for char in itertools.chain(chars.values(), [hero]):
            for flag in char.flags.keys():
                if flag.startswith("dnd"):
                    char.del_flag(flag)
                elif flag.startswith("cnd") and char.flags[flag] == day:
                    char.del_flag(flag)
        tl.end("ND-Flags Reset")

        tl.start("Quest/Events ND")
        pytfall.world_events.next_day() # Get new set of active events
        pytfall.world_quests.next_day() # Garbage collect quests
        tl.end("Quest/Events ND")

        tl.end("Next Day")

        # Lets free some memory...
        if not day%50:
            renpy.free_memory()

    return

label next_day_controls:
    scene bg profile_2
    show screen next_day
    with dissolve
    while 1:
        $ result = ui.interact()
        if result[0] == 'filter':
            python hide:
                global FilteredList, event_index
                FilteredList = NextDayEvents.event_list
                filter = result[1]
                if filter == 'all':
                    pass
                elif filter == 'red_flags':
                    FilteredList = [e for e in FilteredList if e.red_flag]
                elif filter == 'mc':
                    FilteredList = [e for e in FilteredList if e.type == 'mcndreport']
                elif filter == 'school':
                    order = {"school_nd_report": 1, "course_nd_report": 2}
                    FilteredList = sorted([e for e in FilteredList if e.type in order], key=lambda e: order[e.type])
                elif filter == 'gndreports': # Girl Next Day Reports
                    FilteredList = [e for e in FilteredList if e.type == 'girlndreport']
                elif filter == 'xndreports': # Exploration Next Day Reports
                    FilteredList = [e for e in FilteredList if e.type == 'explorationndreport']
                elif filter == 'building':
                    building = result[2]
                    order = {"buildingreport": 1, "manager_report": 2, "explorationndreport": 3, "jobreport": 4, "taskreport": 5}
                    FilteredList = sorted([e for e in FilteredList if e.loc == building and e.type in order], key=lambda e: order[e.type])
                elif filter == "fighters_guild":
                    order = {"fg_report": 1, "exploration_report": 2, "fg_job": 3}
                    FilteredList = sorted([e for e in FilteredList if e.type in order], key=lambda e: order[e.type])
                else:
                    nd_debug("unhandled filter:%s" % filter, "warn")

                event_index = 0
                if not FilteredList:
                    nd_debug("all NextDayEvents were filtered for: %s." % filter, "warn")
                    # Preventing Index Exception on empty filter
                    FilteredList = NextDayEvents.event_list

        elif result[0] == 'control':
            if result[1] == 'left':
                if event_index > 0:
                    $ event_index -= 1
            elif result[1] == 'right':
                if event_index < len(FilteredList)-1:
                    $ event_index += 1
            elif result[1] == "next_day_local":
                # Special Logic required:
                return True
            elif result[1] == 'return':
                return

label special_auto_save: # since built-in autosave works like shit, I use normal saves to save in auto slots
    $ renpy.notify("Autosaving... You can disable it in game settings")
    if special_save_number > 6:
        $ special_save_number = 1
    python hide:
        temp = "auto-" + str(special_save_number)
        renpy.save(temp)
    $ special_save_number += 1
    return


screen next_day():
    default show_summary = True
    default summary_filter = "buildings" # Not applicable atm
    default report_stats = False


    if show_summary:
        # Right frame (Building/Businesses reports):
        frame:
            background Frame(Transform("content/gfx/frame/p_frame6.png", alpha=.98), 10, 10)
            xysize (581, 683)
            ypos 37
            xalign 1.0
            # ALL Buildings/Workers SUMMARY:
            vbox:
                xalign .38

                frame:
                    style_group "content"
                    xalign .5
                    ypos 5
                    xysize (330, 50)
                    background Frame("content/gfx/frame/namebox5.png", 10, 10)
                    label (u"Buildings") text_size 23 text_color "ivory" align .5, .6
                    add ProportionalScale("content/gfx/images/birds1.webp", 548, 115) pos (-100, 5)

                null height 80
                # ALL Buildings/Workers SUMMARY:
                frame:
                    align .5, .5
                    top_padding 6
                    xysize 515, 136
                    background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                    hbox:
                        xalign .5

                        null width 5

                        # DATA:
                        frame:
                            align .5, .5
                            xysize 300, 122
                            background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 5, 5)
                            style_group "proper_stats"
                            padding 8, 10
                            has vbox spacing 1

                            # Active (Numeric Info):
                            frame:
                                xysize (285, 25)
                                text "Active" yalign .5 xpos 3
                                text str(nd_all_stats["actives"]["Service"]) style_suffix "value_text" xpos 135
                                text str(nd_all_stats["actives"]["Combat"]) style_suffix "value_text" xpos 175
                                text str(nd_all_stats["actives"]["Management"]) style_suffix "value_text" xpos 215
                                text str(nd_all_stats["actives"]["Resting"]) style_suffix "value_text" xpos 255

                            # Resting:
                            frame:
                                xysize (285, 25)
                                text "Resting" yalign .5 xpos 3
                                text str(nd_all_stats["rests"]["Service"]) style_suffix "value_text" xpos 135
                                text str(nd_all_stats["rests"]["Combat"]) style_suffix "value_text" xpos 175
                                text str(nd_all_stats["rests"]["Management"]) style_suffix "value_text" xpos 215
                                text str(nd_all_stats["rests"]["Resting"]) style_suffix "value_text" xpos 255

                            # Events:
                            frame:
                                xysize (285, 25)
                                text "Events" yalign .5 xpos 3
                                text str(nd_all_stats["events"]["Service"]["count"]) style_suffix "value_text" xpos 135
                                hbox:
                                    xpos 138
                                    xmaximum 40
                                    if nd_all_stats["events"]["Service"]["red_flag"]:
                                        button:
                                            yoffset 4
                                            padding 1, 1
                                            background Null()
                                            text "!" style "next_day_summary_text" color "red"
                                            action NullAction()

                                    if nd_all_stats["events"]["Service"]["green_flag"]:
                                        button:
                                            yoffset 4
                                            padding 1, 1
                                            background Null()
                                            text "!" style "next_day_summary_text" color "green"
                                            action NullAction()

                                text str(nd_all_stats["events"]["Combat"]["count"]) style_suffix "value_text" xpos 175
                                hbox:
                                    xpos 178
                                    xmaximum 40
                                    if nd_all_stats["events"]["Combat"]["red_flag"]:
                                        button:
                                            yoffset 4
                                            padding 1, 1
                                            background Null()
                                            text "!" style "next_day_summary_text" color "red"
                                            action NullAction()

                                    if nd_all_stats["events"]["Combat"]["green_flag"]:
                                        button:
                                            yoffset 4
                                            padding 1, 1
                                            background Null()
                                            text "!" style "next_day_summary_text" color "green"
                                            action NullAction()

                                text str(nd_all_stats["events"]["Management"]["count"]) style_suffix "value_text" xpos 215
                                hbox:
                                    xpos 218
                                    xmaximum 40
                                    if nd_all_stats["events"]["Management"]["red_flag"]:
                                        button:
                                            yoffset 4
                                            padding 1, 1
                                            background Null()
                                            text "!" style "next_day_summary_text" color "red"
                                            action NullAction()

                                    if nd_all_stats["events"]["Management"]["green_flag"]:
                                        button:
                                            yoffset 4
                                            padding 1, 1
                                            background Null()
                                            text "!" style "next_day_summary_text" color "green"
                                            action NullAction()

                                text str(nd_all_stats["events"]["Resting"]["count"]) style_suffix "value_text" xpos 255
                                hbox:
                                    xpos 258
                                    xmaximum 40
                                    if nd_all_stats["events"]["Resting"]["red_flag"]:
                                        button:
                                            yoffset 4
                                            padding 1, 1
                                            background Null()
                                            text "!" style "next_day_summary_text" color "red"
                                            action NullAction()

                                    if nd_all_stats["events"]["Resting"]["green_flag"]:
                                        button:
                                            yoffset 4
                                            padding 1, 1
                                            background Null()
                                            text "!" style "next_day_summary_text" color "green"
                                            action NullAction()

                            frame:
                                xysize (285, 25)
                                text "Customers:" xpos 3
                                text str(nd_all_stats["clients"]) style_suffix "value_text" xpos 135

                        null width 4

            # Separate Buildings data ------------------------------------------------->>>
            side "c l":
                style_prefix "proper_stats"
                xalign .5
                ypos 285
                viewport id "Reports":
                    xysize (580, 365)
                    child_size (600, 10000)
                    draggable True
                    mousewheel True
                    has vbox

                    # Buildings:
                    for building, curr_stats in nd_stats.items():
                        # Image/Name:
                        null height 4
                        label "[building.name]" xpos 10
                        null height 1
                        frame:
                            xoffset 9
                            xysize 550, 136
                            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                            hbox:
                                yalign .5
                                null width 10
                                frame:
                                    yalign .5
                                    xysize 95, 95
                                    background Frame("content/gfx/frame/MC_bg3.png", 5, 5)
                                    $ img = im.Scale(building.img, 89, 89)
                                    imagebutton:
                                        align .5, .5
                                        idle img
                                        hover im.MatrixColor(img ,im.matrix.brightness(.15))
                                        action [Return(['filter', 'building', building]), SetScreenVariable("show_summary", None)]
                                        tooltip "View Events in %s building." % building.name

                                    if building.flag_red:
                                        button:
                                            align .95, .95
                                            background Null()
                                            text "!" color "red" size 40 italic True
                                            action NullAction()
                                            tooltip "There are building related events flagged Red!"

                                null width 6

                                # DATA:
                                frame:
                                    align .5, .5
                                    xysize 426, 122
                                    background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 5, 5)
                                    style_prefix "proper_stats"
                                    padding 8, 10
                                    has vbox spacing 1

                                    # Active:
                                    frame:
                                        xysize 410, 25
                                        text "Active" yalign .5 xpos 3
                                        text str(curr_stats["actives"]["Service"]) style_suffix "value_text" xpos 135
                                        text str(curr_stats["actives"]["Combat"]) style_suffix "value_text" xpos 175
                                        text str(curr_stats["actives"]["Management"]) style_suffix "value_text" xpos 215
                                        text str(curr_stats["actives"]["Resting"]) style_suffix "value_text" xpos 255
                                        if "dirt" in curr_stats:
                                            text "Dirt" yalign .5 xpos 285
                                            text ("%d%%" % curr_stats["dirt"]) style_suffix "value_text" xalign .99

                                    # Resting:
                                    frame:
                                        xysize (410, 25)
                                        text "Resting" yalign .5 xpos 3
                                        text str(curr_stats["rests"]["Service"]) style_suffix "value_text" xpos 135
                                        text str(curr_stats["rests"]["Combat"]) style_suffix "value_text" xpos 175
                                        text str(curr_stats["rests"]["Management"]) style_suffix "value_text" xpos 215
                                        text str(curr_stats["rests"]["Resting"]) style_suffix "value_text" xpos 255
                                        if "threat" in curr_stats:
                                            text "Threat" yalign .5 xpos 285
                                            text ("%d%%" % curr_stats["threat"]) style_suffix "value_text" xalign .99

                                    # Events:
                                    frame:
                                        xysize (410, 25)
                                        text "Events" yalign .5 xpos 3
                                        text str(curr_stats["events"]["Service"]["count"]) style_suffix "value_text" xpos 135
                                        hbox:
                                            xpos 137
                                            if curr_stats["events"]["Service"]["red_flag"]:
                                                button:
                                                    yoffset 4
                                                    padding 1, 1
                                                    background Null()
                                                    text "!" style "next_day_summary_text" color "red"
                                                    action NullAction()

                                            if curr_stats["events"]["Service"]["green_flag"]:
                                                button:
                                                    yoffset 4
                                                    padding 1, 1
                                                    background Null()
                                                    text "!" style "next_day_summary_text" color "green"
                                                    action NullAction()

                                        text str(curr_stats["events"]["Combat"]["count"]) style_suffix "value_text" xpos 175
                                        hbox:
                                            xpos 178
                                            xmaximum 40

                                            if curr_stats["events"]["Combat"]["red_flag"]:
                                                button:
                                                    yoffset 4
                                                    padding 1, 1
                                                    background Null()
                                                    text "{color=red}!" style "next_day_summary_text"
                                                    action NullAction()

                                            if curr_stats["events"]["Combat"]["green_flag"]:
                                                button:
                                                    yoffset 4
                                                    padding 1, 1
                                                    background Null()
                                                    text "{color=green}!" style "next_day_summary_text"
                                                    action NullAction()

                                        text str(curr_stats["events"]["Management"]["count"]) style_suffix "value_text" xpos 215
                                        hbox:
                                            xpos 218
                                            xmaximum 40

                                            if curr_stats["events"]["Management"]["red_flag"]:
                                                button:
                                                    yoffset 4
                                                    padding 1, 1
                                                    background Null()
                                                    text "{color=red}!" style "next_day_summary_text"
                                                    action NullAction()

                                            if curr_stats["events"]["Management"]["green_flag"]:
                                                button:
                                                    yoffset 4
                                                    padding 1, 1
                                                    background Null()
                                                    text "{color=green}!" style "next_day_summary_text"
                                                    action NullAction()

                                        text str(curr_stats["events"]["Resting"]["count"]) style_suffix "value_text" xpos 255
                                        hbox:
                                            xpos 258
                                            xmaximum 40

                                            if curr_stats["events"]["Resting"]["red_flag"]:
                                                button:
                                                    yoffset 4
                                                    padding 1, 1
                                                    background Null()
                                                    text "{color=red}!" style "next_day_summary_text"
                                                    action NullAction()

                                            if curr_stats["events"]["Resting"]["green_flag"]:
                                                button:
                                                    yoffset 4
                                                    padding 1, 1
                                                    background Null()
                                                    text "{color=green}!" style "next_day_summary_text"
                                                    action NullAction()

                                        if "fame" in curr_stats:
                                            text "Fame" yalign .5 xpos 285
                                            text ("%d/%d" % curr_stats["fame"]) style_suffix "value_text" xalign .99

                                    frame:
                                        xysize (410, 25)
                                        text "Customers:" xpos 3
                                        text str(curr_stats["clients"]) style_suffix "value_text" xpos 135
                                        if "rep" in curr_stats:
                                            text "Rep." yalign .5 xpos 285
                                            text ("%d/%d" % curr_stats["rep"]) style_suffix "value_text" xalign .99

                vbar value YScrollValue("Reports")

        # Buttons will be drawn over the frame ================================================>>>>
        if summary_filter == "buildings":
            $ start_pos = 844
            for i in ("Servers", "Combatant", "Managers", "Resting"):
                $ start_pos = start_pos + 42
                frame:
                    at rotate_by(45)
                    pos (start_pos, 95)
                    xysize (90, 30)
                    background Frame("content/gfx/interface/buttons/button_wood_right_hover.png", 3, 3)
                    text "[i]" size 12 bold True xalign .4

        # Left Frame ==========================================================================>>>>
        # Finances:
        frame:
            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
            xysize 277, 683 xoffset 3
            ypos 37

            # Day Total ===========================================>>>
            $ fin_inc = hero.fin.game_main_income_log.get(day-1, {})
            $ fin_exp = hero.fin.game_main_expense_log.get(day-1,{})

            frame:
                style_prefix "proper_stats"
                background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 10, 10)
                xysize 270, 670
                xoffset -4

                null height 10

                frame:
                    style "content_frame"
                    xalign .6 ypos 15
                    xysize 210, 40
                    background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.6), 10, 10)
                    label (u"Daily Balance") text_size 23 text_color "ivory" xalign .5 yoffset -4

                vbox:
                    ypos 60
                    $ counter = 0
                    $ max_fields = 21
                    for k, v in fin_inc.iteritems():
                        if v:
                            $ counter += 1
                            frame:
                                xysize 250, 25
                                xoffset 10
                                text "[k]" color "green" xoffset 3
                                text "[v]" color "green" style_suffix "value_text" xoffset -3

                    for k, v in fin_exp.iteritems():
                        if v:
                            $ counter += 1
                            frame:
                                xysize 250, 25
                                xoffset 10
                                text "[k]" color "red" xoffset 3
                                text "[v]" color "red" style_suffix "value_text" xoffset -3

                    # Empty field fillers:
                    for i in xrange(max(0, max_fields-counter)):
                        frame:
                            xysize 250, 25
                            xoffset 10

                python:
                    total_income = 0
                    total_expenses = 0
                    for key in fin_inc:
                        total_income += fin_inc[key]
                    for key in fin_exp:
                        total_expenses += fin_exp[key]
                    total = total_income - total_expenses
                    if total < 0:
                        color = "red"
                    else:
                        color = "green"

                frame:
                    xysize 250, 25
                    yalign .98 xoffset 10
                    text "Total" xoffset 3 color color
                    text "[total]" style_suffix "value_text" xoffset -3 color color

                add ProportionalScale("content/gfx/images/magic2.png", 120, 120) offset 140, -140

        # Middle Frames =======================================================================>>>>
        # Middle Top: Game Total
        frame:
            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
            xysize (430, 220)
            pos (275, 37)
            style_group "content"

            frame:
                ypos 6
                xalign .5
                xysize (380, 50)
                background Frame("content/gfx/frame/namebox5.png", 10, 10)
                label (u"Game Total") text_size 23 text_color "ivory" align .5, .6

            $ income, expense, total = NextDayEvents.get_hero_fin()
            null height 1
            frame:
                align .5, .95
                xysize (414, 150)
                style_prefix "proper_stats"
                background Frame(Transform("content/gfx/frame/p_frame4.png", alpha=.6), 5, 5)
                add ProportionalScale("content/gfx/images/jp1.png", 68, 101) pos (330, 20)
                add ProportionalScale("content/gfx/images/jp2.png", 73, 103) pos (12, 20)

                vbox:
                    align .5, .3
                    frame:
                        xysize 240, 30
                        xalign .5
                        text ("Earnings") color "green" xoffset 2
                        text ("[income]") color "green" style_suffix "value_text" xoffset -2
                    frame:
                        xysize 240, 30
                        xalign .5
                        text ("Expenses") color "red" xoffset 2
                        text ("[expense]") color "red" style_suffix "value_text" xoffset -2

                null height 2
                $ cl = "green" if total > 0 else "red"
                frame:
                    align .5, .90
                    xysize 250, 30
                    frame:
                        text "Total" color cl size 24 xpos 2
                        text "[total]" color cl style_suffix "value_text" xoffset -3 size 19

        # Middle Bottom Frame =================================================================>>>>
        frame:
            pos (275, 252)
            xysize (430, 468)
            background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)

            # Hero Filter/Portrait:
            frame:
                xalign .5
                xysize 414, 120
                background Frame("content/gfx/frame/ink_box.png", 10 ,10)
                $ img = hero.show("portrait", resize=(95, 95), cache=True)
                frame:
                    background Frame("content/gfx/frame/MC_bg3.png", 10 ,10)
                    align .23, .8
                    imagebutton:
                        idle img
                        hover im.MatrixColor(img, im.matrix.brightness(.15))
                        action [Return(['filter', 'mc']), SetScreenVariable("show_summary", None)]
                        tooltip "Show personal MC report!"
                frame:
                    style_group "proper_stats"
                    yalign .5
                    xpos 178
                    xysize 155, 110
                    background Frame(Transform("content/gfx/frame/P_frame2.png", alpha=.6), 10, 10)
                    vbox:
                        label "[hero.name]":
                            text_size 16
                            text_bold True
                            xpos 38
                            yalign .03
                            text_color "ivory"
                        $ temp, tmp = NextDayEvents.get_hero_hp()
                        fixed: # HP
                            xysize (150, 25)
                            xanchor -8
                            bar:
                                yalign .5
                                left_bar ProportionalScale("content/gfx/interface/bars/hp1.png", 150, 20)
                                right_bar ProportionalScale("content/gfx/interface/bars/empty_bar1.png", 150, 20)
                                value temp
                                range tmp
                                thumb None
                                xysize (150, 20)
                            text "HP" size 14 color "ivory" bold True yalign .1 xpos 8
                            text "[temp]" size 14 color ("red" if temp <= tmp*.2 else "ivory") bold True style_suffix "value_text" yoffset -3 xpos 102

                        $ temp, tmp = NextDayEvents.get_hero_mp()
                        fixed: # MP
                            xysize (150, 25)
                            xanchor -5
                            bar:
                                yalign .2
                                left_bar ProportionalScale("content/gfx/interface/bars/mp1.png", 150, 20)
                                right_bar ProportionalScale("content/gfx/interface/bars/empty_bar1.png", 150, 20)
                                value temp
                                range tmp
                                thumb None
                                xysize (150, 20)
                            text "MP" size 14 color "ivory" bold True yalign .8 xpos 7
                            text "[temp]" size 14 color ("red" if temp <= tmp*.2 else "ivory") bold True style_suffix "value_text" yoffset 2 xpos 99

                        $ temp, tmp = NextDayEvents.get_hero_vp()
                        fixed: # VIT
                            xysize (150, 25)
                            xanchor -2
                            bar:
                                yalign .5
                                left_bar ProportionalScale("content/gfx/interface/bars/vitality1.png", 150, 20)
                                right_bar ProportionalScale("content/gfx/interface/bars/empty_bar1.png", 150, 20)
                                value temp
                                range tmp
                                thumb None
                                xysize (150, 20)
                            text "VP" size 14 color "ivory" bold True yalign .8 xpos 7
                            text "[temp]" size 14 color ("red" if temp <= tmp*.2 else "ivory") bold True style_suffix "value_text" yoffset 2 xpos 99
                            add ProportionalScale("content/gfx/images/c1.png", 123, 111) pos (-42, 55)

                # MC (extra info) -------------------------------------------->>>
                # Preparing info:
                $ temp = any(i.type == "mcndreport" and i.red_flag for i in NextDayEvents.event_list)

                if temp:
                    button:
                        align .99, .99
                        background Frame("content/gfx/frame/p_frame5.png", 5, 5)
                        text "!" color "red" size 35 hover_size 40 style "proper_stats_text"
                        action NullAction()
                        tooltip "Red flag in MC's Report!"

            # Group report buttons (School, All, Flagged Red)
            hbox:
                xalign .5 ypos 150
                spacing 20
                # ALL Reports button:
                $ img = "content/gfx/frame/MC_bg3.png"
                button:
                    xysize 95, 95
                    yalign .5
                    idle_background Frame(img, 5 , 5)
                    hover_background Frame(im.MatrixColor(img ,im.matrix.brightness(.2)), 5, 5)
                    text "All" align .5, .5 style "proper_stats_label_text" size 32
                    action [Return(['filter', 'all']), SetScreenVariable("show_summary", None)]
                    tooltip "Show full report tree!"

                # RED FLAG Button:
                # View all red flagged events:
                $ red_flags = any(i.red_flag for i in NextDayEvents.event_list)
                $ img = "content/gfx/frame/p_frame5.png"
                button:
                    yalign .5
                    xysize (90, 90)
                    idle_background Frame(img, 5, 5)
                    if red_flags:
                        hover_background Frame(im.MatrixColor(img, im.matrix.brightness(.10)), 5, 5)
                        tooltip "View all Events flagged Red!"
                        action [Return(['filter', 'red_flags']), SetScreenVariable("show_summary", None)]
                    else:
                        hover_background Frame(img, 5, 5)
                        action NullAction()
                        tooltip "There are no events flagged Red!"
                    text "!" align (.5, .5) color ("red" if red_flags else "grey") size 60 style "proper_stats_text"

                # School:
                # Preparing info:
                python:
                    for school_report in NextDayEvents.event_list:
                        if school_report.type == "school_nd_report":
                            break

                frame:
                    align .02, .98
                    xysize 95, 95
                    padding 2, 2
                    background Frame("content/gfx/frame/MC_bg3.png", 5, 5)
                    $ img = pytfall.school.img
                    button:
                        xysize 90, 90
                        align .5, .5
                        background Frame(img, 10, 10)
                        hover_background Frame(im.MatrixColor(img ,im.matrix.brightness(.15)), 10, 10)
                        action [Return(['filter', 'school']), SetScreenVariable("show_summary", None)]
                        tooltip "View School and School Events!"

                    hbox:
                        align 1.0, 1.0
                        if "New Courses" in school_report.txt:
                            button:
                                xysize 30, 30
                                yalign .5
                                padding 0, 0
                                margin 0, 0
                                background Null()
                                action NullAction()
                                tooltip "New Courses available!"
                                text "+" color "yellow" size 40 style "proper_stats_text" align .5, .5
                        if "Student(s) completed" in school_report.txt:
                            button:
                                xysize 10, 36
                                yalign .5
                                background Null()
                                action NullAction()
                                tooltip "One of your workers has successfully completed their course (this doesn't mean that a course has ended)!"
                                text "!" color "yellow" size 40 style "proper_stats_text" align .5, .5
                        if "Student(s) were sent" in school_report.txt:
                            button:
                                xysize 10, 36
                                yalign .5
                                background Null()
                                action NullAction()
                                tooltip "A course one of your workers attended has ended!"
                                text "!" color "yellow" size 40 style "proper_stats_text" align .5, .5

            $ explorers = any(i.type == "explorationndreport" for i in NextDayEvents.event_list)
            if explorers:
                $ img = "content/gfx/interface/buttons/exploration.webp"
                imagebutton:
                    background Frame("content/gfx/frame/MC_bg3.png", 10, 10)
                    xalign .5 ypos 250
                    padding 3, 3
                    margin 0, 0
                    hover pscale(img, 60, 60) 
                    idle pscale(im.Sepia(img), 60, 60)
                    action [Return(['filter', 'xndreports']), SetScreenVariable("show_summary", None)]
                    tooltip "View the Exploration Guild reports!"

            # # Girls and Other Related data:
            hbox:
                xalign .5 ypos 300
                spacing 80
                # Getting .status field data:
                $ free, slaves = NextDayEvents.get_chars_dist()
                $ red_flags = any(i.type == "girlndreport" and i.red_flag for i in NextDayEvents.event_list)

                vbox:
                    spacing 5
                    yalign .5
                    add ProportionalScale("content/gfx/interface/icons/slave.png", 50, 50)
                    text "[slaves]" xalign .5 style "agrevue"

                frame:
                    xysize 95, 95
                    padding 2, 2
                    background Frame("content/gfx/frame/MC_bg3.png", 5, 5)
                    $ img = "content/gfx/interface/buttons/girls_reports.png"
                    button:
                        align .5, .5
                        xysize 90, 90
                        background Frame(img, 10, 10)
                        hover_background Frame(im.MatrixColor(img ,im.matrix.brightness(.15)), 10, 10)
                        action [Return(['filter', 'gndreports']), SetScreenVariable("show_summary", None)]
                        tooltip "Show personal girl reports!"
                    if red_flags:
                        hbox:
                            align 1.0, 1.0
                            button:
                                xysize 10, 36
                                yalign .5
                                background Null()
                                action NullAction()
                                tooltip "Red flag in Girls personal Reports!"
                                text "!":
                                    style "proper_stats_text"
                                    color "red"
                                    size 40
                                    align .5, .5

                vbox:
                    spacing 5
                    yalign .5
                    add ProportionalScale("content/gfx/interface/icons/free.png", 50, 50)
                    text "[free]" xalign .5 style "agrevue"

            # Data:
            $ temp = NextDayEvents.unassigned_chars
            text "Unassigned: [temp]":
                yalign .5 ypos 420
                style "agrevue"
                color ("red" if temp > 0 else "green")

        use top_stripe(True)

    #  Reports  =============================================================================>>>>
    else:
        key "mousedown_4" action Return(['control', 'right'])
        key "mousedown_5" action Return(['control', 'left'])

        # Image frame:
        $ event = FilteredList[event_index]
        frame:
            pos 0, 0
            xysize 839, 720
            background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
            padding 0, 0
            margin 0, 0

            python:
                # select/load an image according to img
                bg_img = event.img
                char_imgs = None
                # Try to analyze self.img in order to figure out what it represents:
                if isinstance(bg_img, renpy.display.core.Displayable):
                    pass # a standard displayable -> ok
                elif isinstance(bg_img, basestring):
                    if not bg_img:
                        raise Exception("Basestring Supplied as img {}: Ev.type: {}, Ev.loc.name: {}".format(
                                    bg_img,
                                    event.type,
                                    event.loc.name if event.loc else "Unknown"))
                    elif "." in bg_img:
                        pass
                    else:
                        bg_img = event.char.show(bg_img, cache=True)
                elif isinstance(bg_img, list):
                    # list of displayables -> first img is the background, rest is list of char-images
                    char_imgs = bg_img[1:]
                    bg_img = bg_img[0]
                else:
                    nd_debug("Unknown Image Type: {} Provided to Event (Next Day Events class)".format(bg_img), "warning")
                    bg_img = IMG_NOT_FOUND_PATH
                bg_img = pscale(bg_img, *ND_IMAGE_SIZE)

            frame:
                align .5, .5
                padding 5, 5
                margin 0, 0
                background Frame("content/gfx/frame/MC_bg3.png", 10 , 10)
                add bg_img align .5, .5
            if char_imgs is not None:
                $ num_imgs = len(char_imgs)
                $ border, csize = 5, 150
                if num_imgs < 4:
                    frame:
                        background Solid("#00000011")
                        align .5, .9
                        xysize ((csize+border)*num_imgs+border, csize + 2*border)
                        padding border, border
                        margin 0, 0
                        $ xpos = 0
                        for char in char_imgs:
                            fixed:
                                xysize (csize, csize)
                                pos (xpos, 0)
                                add pscale(char, csize, csize) align (.5, .5)
                            $ xpos += csize + border
                else:
                    $ xsize = (csize + border) * num_imgs
                    viewport:
                        align .5, .9
                        xysize (500, csize + 2*border)
                        child_size xsize, csize
                        frame:
                            background Solid("#00000011")
                            xysize (xsize, csize + 2*border)
                            ypadding border
                            at scroll_around(num_imgs*4)
                            $ xpos = 0
                            for char in char_imgs:
                                fixed:
                                    xysize (csize, csize)
                                    pos (xpos, 0)
                                    add pscale(char, csize, csize) align (.5, .5)
                                $ xpos += csize + border

        # Stat Frames:
        $ show_stat_frame = event.charmod or event.team_charmod or event.locmod
        showif show_stat_frame and report_stats:
            # Chars/Teams Stats Frame:
            frame:
                at slide(so1=(136, 0), eo1=(0, 0), t1=.4,
                         so2=(0, 0), eo2=(136, 0), t2=.3)
                background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10)
                pos (690, -2)
                has fixed xysize 136, 400
                python:
                    if event.team_charmod:
                        charmod = event.team_charmod
                        if len(charmod) == 1:
                            char, charmod = next(charmod.iteritems())
                    else:
                        char = None
                        charmod = event.charmod
                if charmod:
                    frame:
                        style_group "content"
                        xalign .5
                        ypos 5
                        xysize (136, 40)
                        background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.7), 10, 10)
                        label (u"Stat Changes:") text_size 18 text_color "ivory" align (.5, .5)

                    # team report with multiple members
                    if charmod == event.team_charmod:
                        # use a slideshow thing for teams:
                        $ num_char = len(charmod)
                        $ xsize, ysize = num_char*136, 355
                        viewport:
                            xalign .5
                            ypos 45
                            xysize (136, ysize)
                            child_size xsize, ysize
                            #for i in range(2):
                            #    fixed:
                            frame:
                                    background Null()
                                    xysize xsize, ysize
                                    #if not i:
                                    #    at mm_clouds(xsize, 0, num_char*4)
                                    #else:
                                    #    at mm_clouds(0, -xsize, num_char*4)
                                    at scroll_around(num_char*4)
                                    $ xpos = 0
                                    for w, mod in charmod.iteritems():
                                        vbox:
                                            style_group "proper_stats"
                                            xsize 136
                                            xpos xpos
                                            spacing 1
                                            frame:
                                                xysize 132, 25
                                                xalign .5
                                                text w.nickname align .5, .5 style "TisaOTM" size 20:
                                                    if len(w.nickname) > 20:
                                                        size 16
                                            null height 4
                                            for key, value in mod.items():
                                                if value != 0:
                                                    frame:
                                                        xalign .5
                                                        xysize 130, 25
                                                        text ("%s:" % key.capitalize()) align .02, .5
                                                        label "[value]" text_color ("lawngreen" if value > 0 else "red") align .98, .5
                                        $ xpos += 136
                    # one worker report(team or not):
                    else:
                        vbox:
                            style_group "proper_stats"
                            xsize 136
                            xalign .5 ypos 45
                            spacing 1
                            if char is not None:
                                frame:
                                    xysize 132, 25
                                    xalign .5
                                    text char.nickname align .5, .5 style "TisaOTM" size 20:
                                        if len(char.nickname) > 20:
                                            size 16
                            for key, value in charmod.items():
                                if value != 0:
                                    frame:
                                        xalign .5
                                        xysize 130, 25
                                        text ("%s:" % key.capitalize()) align .02, .5
                                        label "[value]" text_color ("lawngreen" if value > 0 else "red") align .98, .5

            # Buildings Stats Frame:
            frame background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.98), 10, 10):
                at slide(so1=(136, 0), eo1=(0, 0), t1=.4,
                             so2=(0, 0), eo2=(136, 0), t2=.3)
                pos (690, 406)
                viewport id "nextdaybsf_vp":
                    xysize (136, 305)
                    if event.locmod:
                        vbox:
                            null height 5
                            frame:
                                style_group "content"
                                xalign .5
                                xysize (136, 40)
                                background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.7), 10, 10)
                                label (u"Building Stats:") text_size 18 text_color "ivory" align .5, .5
                            null height 10
                            vbox:
                                style_group "proper_stats"
                                xsize 136
                                spacing 1
                                for key, value in event.locmod.items():
                                    if value != 0:
                                        frame:
                                            xalign .5
                                            xysize 130, 25
                                            python: # Special considerations:
                                                hkey = key
                                                if key in ["dirt", "threat"]:
                                                    neg_color = "lawngreen"
                                                    pos_color = "red"
                                                else:
                                                    neg_color = "red"
                                                    pos_color = "lawngreen"
                                                    if key == "reputation":
                                                        hkey = "Rep"
                                            text (u"%s:" % hkey.capitalize()) align .02, .5
                                            label ("%d" % value) text_color (pos_color if value > 0 else neg_color) align .98, .5

        # Text Frame + Stats Reports Mousearea:
        # frame:
        #     background Frame("content/gfx/frame/p_frame5.png", 10, 10)
        #     xysize (449, 609)
        #     pos (834, -2)
        #     vbox:
                # frame:
                #     background Frame("content/gfx/frame/namebox5.png", 10, 10)
                #     xalign .5
                #     style_prefix "content"
                #     xysize (200, 40)
                #     label (u"Description:") text_size 18 text_color "ivory" align(.5, .6)
        frame:
            background Frame("content/gfx/frame/mes12.jpg")
            xysize 442, 606
            xalign 1.0
            side "c l":
                ypos 5
                xalign .5
                viewport id "nextdaytxt_vp":
                    xysize 420, 580
                    draggable True mousewheel True
                    child_size 400, 10000
                    has vbox xsize 420 xfill True
                    null height 5
                    if isinstance(event.txt, basestring):
                        text event.txt style "TisaOTMol" xalign .5 size 18
                    else:
                        for i in event.txt:
                            text str(i) style "TisaOTMol" xalign .0 size 13
                vbar value YScrollValue("nextdaytxt_vp")

        mousearea:
            area (834, -2, 449, 609)
            hovered SetScreenVariable("report_stats", True)
            unhovered SetScreenVariable("report_stats", False)
        # Bottom Buttons:
        frame:
            background Frame("content/gfx/frame/mes12.jpg")
            align 1.0, 1.0
            xysize 442, 115
            vbox:
                align .5, .5
                spacing 8
                hbox:
                    align (.5, .5)
                    spacing 20
                    button:
                        xysize (120, 40)
                        style "left_wood_button"
                        action Return(['control', 'left'])
                        text "Previous Event" style "wood_text" xalign(.6) size 10
                    frame:
                        align (.5, .5)
                        background Frame(Transform("content/gfx/frame/p_frame5.png", alpha=.9), 5, 5)
                        xysize (100, 40)
                        text(u'Act: %d/%d'%(event_index+1, len(FilteredList))) align (.5, .5) size 16 style "proper_stats_text"
                    button:
                        xysize (120, 40)
                        style "right_wood_button"
                        action Return(['control', 'right'])
                        text "Next Event" style "wood_text" xalign .4 size 10
                hbox:
                    align .5, .5
                    spacing 20
                    textbutton "-Next Day-":
                        style "main_screen_4_button"
                        tooltip "Begin New day and watch the results."
                        action Return(['control', "next_day_local"])
                        text_size 16
                        ypadding 5
                        xysize (150, 40)

                    $ img = im.Scale("content/gfx/interface/buttons/close.png", 40, 40)
                    imagebutton:
                        align (.5, .5)
                        idle img
                        hover im.MatrixColor(img, im.matrix.brightness(.25))
                        action Return(['control', 'return'])
                        tooltip "Return to previous screen!"

                    textbutton "-Summary-":
                        style "main_screen_4_button"
                        tooltip "Back to the Summary!"
                        action SetScreenVariable("show_summary", True)
                        text_size 16
                        ypadding 5
                        xysize 150, 40
                        keysym "mousedown_3"

screen next_day_calculations():
    zorder 20
    text "Processing next day calculations..." font "fonts/badaboom.ttf" color "#daa520" size 35 align(.5, .5) outlines [(2, "black", 0, 0)]
