# Temp code, should be moved to items funcs:
init:
    style positive_item_eqeffects_change:
        is text
        size 9
        color "lawngreen"

    style negative_item_eqeffects_change:
        is positive_item_eqeffects_change
        color "#ff1a1a"

    screen discard_item(source, item):
        zorder 10
        modal True
        python:
            tmp = source.inventory[item]
            if source != hero:
                if not can_transfer(source, hero, item, amount=1, silent=True):
                    tmp = 0
                elif not can_transfer(source, hero, item, amount=tmp, silent=True):
                    tmp = 1

        add im.Alpha("content/gfx/images/bg_gradient2.webp", alpha=.3)
        frame:
            background Frame(im.Alpha("content/gfx/frame/ink_box.png", alpha=.75), 10, 10)
            style_group "dropdown_gm2"
            align .42, .61
            xsize 500
            padding 10, 10
            margin 0, 0
            has vbox spacing 5 xfill True
            text "{=TisaOTM}{size=-3}Discard {color=#ffd700}[item.id]{/color}?" xalign .52 color "#ecc88a"
            hbox:
                xalign .5
                spacing 10
                textbutton "{size=-1}Yes":
                    xalign .5
                    action Return(1)
                    sensitive tmp > 0
                textbutton "{size=-1}Discard All":
                    xalign .5
                    action Return(tmp)
                    sensitive tmp > 1
                textbutton "{size=-1}No":
                    xalign .5
                    action Return(0)

init python:
    def build_str_for_eq(eqtarget, dummy, stat, tempc):
        temp = dummy.get_stat(stat) - eqtarget.get_stat(stat) if dummy else False
        tempmax = dummy.get_max(stat) - eqtarget.get_max(stat) if dummy else False
        if temp: # Case: Any Change to stat
            # The first is the absolute change, we want it to be colored green if it is positive, and red if it is not.
            tempstr = set_font_color("%d" % dummy.get_stat(stat), "green" if temp > 0 else "red")
            # Next is the increase: (positive_item_eqeffects_change / negative_item_eqeffects_change)
            tempstr += "{=%s_item_eqeffects_change}(%+d){/=}" % (("positive" if temp > 0 else "negative"), temp)
        else: # No change at all...
            tempstr = set_font_color("%d" % eqtarget.get_stat(stat), tempc)

        tempstr += set_font_color("/", tempc)

        if tempmax:
            # Absolute change of the max values, same rules as the actual values apply:
            tempstr += set_font_color("%d" % dummy.get_max(stat), "green" if tempmax > 0 else "red")
            # Next is the increase: (positive_item_eqeffects_change / negative_item_eqeffects_change)
            tempstr += "{=%s_item_eqeffects_change}(%+d){/=}" % (("positive" if tempmax > 0 else "negative"), tempmax)
        else: # No change at all...
            tempstr += set_font_color("%d" % eqtarget.get_max(stat), tempc)
        return tempstr

    def char_equip_reset_fields():
        global focusitem, focusoutfit, unequip_slot, item_direction, dummy, eqsave
        focusitem = None
        focusoutfit = None
        unequip_slot = None
        item_direction = None
        dummy = None
        eqsave = [False, False, False]

label char_equip:
    python:
        char_equip_reset_fields()

        if eqtarget == hero or len(equip_girls) == 1:
            equip_girls = None

        inv_source = eqtarget
        # feature turned off, because it is more usable this way (allows the player to track the inventory changes)
        #if not "last_inv_filter" in globals():
        #    last_inv_filter = "all"
        #inv_source.inventory.apply_filter(last_inv_filter)

    scene bg gallery3

    $ renpy.retain_after_load()
    show screen char_equip

label char_equip_loop:
    while 1:
        $ result = ui.interact()
        #$ char = eqtarget

        if not result:
            jump char_equip_loop

        if result[0] == "jump":
            if result[1] == "item_transfer":
                hide screen char_equip
                python hide:
                    if equip_girls:
                        index = equip_girls.index(eqtarget)
                        if index == 0:
                            equip_chars = equip_girls
                        else:
                            equip_chars = equip_girls[index:] + equip_girls[:index]
                    else:
                        equip_chars = [eqtarget]
                    items_transfer([hero] + equip_chars)
                show screen char_equip
        elif result[0] == "equip_for":
            $ renpy.show_screen("equip_for", renpy.get_mouse_pos())
            $ char_equip_reset_fields()
        elif result[0] == "item":
            if result[1] == "equip/unequip":
                    # Equipping:
                    if item_direction == "equip":
                        # Common to any eqtarget:
                        if can_equip(focusitem, eqtarget) and \
                           equipment_access(eqtarget, focusitem) and \
                           (eqtarget == inv_source or transfer_items(inv_source, eqtarget, focusitem)):

                            # If we got here, we just equip the item :D
                            $ eqtarget.equip(focusitem)

                            $ char_equip_reset_fields()
                    elif item_direction == "unequip":
                        # Check if we are allowed to access inventory and act:
                        if equipment_access(eqtarget, focusitem, unequip=True):
                            $ eqtarget.unequip(focusitem, unequip_slot)

                            $ char_equip_reset_fields()
            elif result[1] == "discard":
                python:
                    # Check if we can access the inventory:
                    if focusitem.slot == "quest" or focusitem.id == "Your Pet":
                        PyTGFX.message("This item cannot be discarded.")
                    else:
                        num = renpy.call_screen("discard_item", inv_source, focusitem)
                        if num != 0:
                            inv_source.inventory.remove(focusitem, num)

                            char_equip_reset_fields()
                        del num
            elif result[1] == "transfer":
                python:
                    source = result[2]
                    target = result[3]
                    if can_transfer(source, target, focusitem):
                        if item_direction == "unequip":
                            # unequip transfer (reequip)
                            # Remark: assumes a transfer is more strict than an equipment_access
                            #  otherwise it should be called as well, but at the moment ownership
                            #  is not checked in the equipment_access
                            purpose = source.last_known_aeq_purpose
                            source.unequip(focusitem, unequip_slot)

                            transfer_items(source, target, focusitem)
                            if source.autoequip:
                                source.auto_equip(purpose)
                            del purpose

                            char_equip_reset_fields()
                        else:
                            # just transfer
                            transfer_items(source, target, focusitem)

                            if focusitem not in source.inventory:
                                char_equip_reset_fields()
                    del source, target
            elif result[1] == "equip":
                python:
                    focusitem = result[2]
                    item_direction = "equip"

                    # # To Calc the effects:
                    dummy = copy_char(eqtarget)
                    if can_equip(focusitem, dummy, silent=True):
                        dummy.equip(focusitem)
                    # renpy.show_screen("diff_item_effects", eqtarget, dummy)
            elif result[1] == "unequip":
                python:
                    focusitem = result[2]
                    unequip_slot = result[3]
                    item_direction = "unequip"

                    # To Calc the effects:
                    dummy = copy_char(eqtarget)
                    dummy.unequip(focusitem, unequip_slot)
                    #renpy.show_screen("diff_item_effects", eqtarget, dummy)
        elif result[0] == "unequip_all":
            python hide:
                for temp in eqtarget.eqslots.itervalues():
                    if temp and not equipment_access(eqtarget, temp, unequip=True):
                        break
                else:
                    for temp in eqtarget.eqslots:
                        eqtarget.unequip(slot=temp)

                    char_equip_reset_fields()
        elif result[0] == "outfit":
            if result[1] == "create":
                python hide:
                    n = renpy.call_screen("pyt_input", "", "Enter Name", 12)
                    if len(n):
                        _eqsave = eqtarget.eqslots.copy()
                        _eqsave["name"] = n
                        eqtarget.eqsave.append(_eqsave)
            elif result[1] == "rename":
                python:
                    _eqsave = result[2]
                    n = renpy.call_screen("pyt_input", _eqsave["name"], "Enter Name", 12)
                    if len(n):
                        _eqsave["name"] = n
                    del _eqsave, n
            elif result[1] == "save":
                python:
                    _eqsave = result[2]
                    _eqsave.update(eqtarget.eqslots)
                    
                    if focusoutfit == _eqsave:
                        dummy = copy_char(eqtarget)
                    del _eqsave
            elif result[1] == "remove":
                python:
                    _eqsave = result[2]
                    eqtarget.eqsave.remove(_eqsave)
                    if focusoutfit == _eqsave:
                        focusoutfit = None
                        dummy = None
                    del _eqsave, eqsave[0]
                    eqsave.append(0)
            elif result[1] == "focus":
                $ focusoutfit = result[2]

                # To Calc the effects:
                $ dummy = copy_char(eqtarget)
                if eqtarget == hero:
                    # make sure dummy lets us equip FIXME not perfect...
                    $ dummy.mod_stat("disposition", dummy.get_max("disposition"))
                # force the copy of the inventory
                $ dummy.inventory.items = eqtarget.inventory.items.copy()
                $ dummy.load_equip(focusoutfit, silent=True)
        elif result[0] == "con":
            if result[1] == "return":
                $ char_equip_reset_fields()
        elif result[0] == "control":
            if result[1] == "return":
                jump char_equip_finish
            else:
                python:
                    char_equip_reset_fields()

                    index = equip_girls.index(eqtarget)
                    if result[1] == "left":
                        index -= 1
                    elif result[1] == "right":
                        index += 1
                    char = equip_girls[index % len(equip_girls)]

                    if char.inventory.page_size != 16:
                        char.inventory.set_page_size(16)
                    if inv_source == eqtarget:
                        inv_source = char
                        #inv_source.inventory.apply_filter(last_inv_filter)

                    eqtarget = char

label char_equip_finish:
    hide screen char_equip

    python:
        # Reset all globals so screens that lead here don't get thrown off:
        del focusitem, focusoutfit, unequip_slot, item_direction, dummy, eqsave, inv_source, equip_girls
        equipment_safe_mode = False

        # eqtarget.inventory.female_filter = False
        # hero.inventory.female_filter = False
        if eqtarget.location == pytfall.afterlife:
            PyTGFX.message("%s dies as a result of item manipulations..." % eqtarget.fullname)
            del eqtarget, came_to_equip_from
            jump("mainscreen")

    $ last_label = came_to_equip_from
    $ del eqtarget, came_to_equip_from
    jump expression last_label

screen equip_for(pos=()):
    zorder 3
    modal True

    key "mousedown_4" action NullAction()
    key "mousedown_5" action NullAction()

    python:
        x, y = pos
        if x > 1000:
            xval = 1.0
        else:
            xval = .0
        if y > 500:
            yval = 1.0
        else:
            yval = .0

        specializations = OrderedDict()
        eq_free = eqtarget.status == "free"
        eq_slave = eqtarget.status == "slave"

        specializations["Casual"] = True
        if eq_slave:
            # slaves
            specializations["Slave"] = True
            jobs = [ManagerJob, WhoreJob, StripJob, CleaningJob, BarJob, WranglerJob]
        else:
            if eq_free:
                # free workers
                if "Combatant" in eqtarget.gen_occs:
                    specializations["Barbarian"] = True
                    specializations["Shooter"] = True
                if "Caster" in eqtarget.gen_occs:
                    specializations["Battle Mage"] = True
                    specializations["Mage"] = True
            #else: mixed groups
            jobs = eqtarget.get_willing_jobs()
        target_jobs = eqtarget.get_wanted_jobs()
        for job in jobs:
            specializations[job.aeq_purpose] = eqtarget == hero or (job in target_jobs and specializations.get(job.aeq_purpose, True))

    frame:
        style_group "dropdown_gm"
        pos (x, y)
        anchor (xval, yval)
        vbox:
            text "Equip For:" xalign 0 style "della_respira" color "ivory"
            null height 5

            for purpose, want in specializations.items():
                textbutton "%s%s" % (purpose, "" if want else "*"):
                    xminimum 200
                    action [Function(eqtarget.auto_equip, purpose), Hide("equip_for"), With(dissolve)]
                    if not want:
                        tooltip "%s does not want to work in this." % eqtarget.name
                    text_underline purpose == eqtarget.last_known_aeq_purpose

            null height 5
            use aeq_button(eqtarget)

            null height 5
            textbutton "Close":
                action Hide("equip_for"), With(dissolve)
                keysym "mousedown_3"

init python:
    def ce_on_show():
        eqtarget.inventory.set_page_size(16)
        hero.inventory.set_page_size(16)

screen char_equip():
    on "show":
        action Function(ce_on_show)
 
    modal True

    # Useful keymappings
    if focusitem:
        key "mousedown_2" action Return(["item", "equip/unequip"])
    else:
        key "mousedown_2" action NullAction()
    key "mousedown_3" action Return(["control", "return"])
    key "mousedown_4" action Function(inv_source.inventory.prev)
    key "mousedown_5" action Function(inv_source.inventory.next)
    key "mousedown_6" action Return(["con", "return"])

    default stats_display = "stats"
    default skill_display = "combat"

    # BASE FRAME 2 "bottom layer" ====================================>
    add "content/gfx/frame/equipment3.webp"

    # Equipment slots:
    frame:
        pos (425, 10)
        xysize 298, 410
        background Frame(im.Alpha("content/gfx/frame/Mc_bg3.png", alpha=.3), 10, 10)
        use eqdoll(source=eqtarget, outfit=False, fx_size=(455, 400), scr_align=(.98, 1.0), frame_size=[70, 70], return_value=["item", "unequip"])

    # BASE FRAME 3 "mid layer" ====================================>
    add "content/gfx/frame/equipment1.webp"

    #use char_equip_left_frame(stats_display)

#screen char_equip_left_frame(stats_display):
    # Left Frame: =====================================>
    fixed:
        pos (0, 2)
        xysize (220, 724)
        style_group "content"

        # PORTRAIT + Prev/Next buttons ================>
        fixed:
            xysize (220, 110)
            if equip_girls:
                imagebutton:
                    xysize (39, 50)
                    pos (13, 14)
                    action Return(["control", "left"])
                    idle "content/gfx/interface/buttons/small_button_wood_left_idle.png"
                    hover "content/gfx/interface/buttons/small_button_wood_left_hover.png"
                    tooltip "Previous Character"
                    focus_mask True
                    keysym "K_LEFT"

            $ img = eqtarget.show("portrait", resize=(100, 100), cache=True)
            imagebutton:
                xysize (100, 100)
                pos (64, 8)
                background Null()
                idle img
                hover PyTGFX.bright_content(img, 0.15)
                action Show("popup_info", content="trait_info_content", param=eqtarget)
                focus_mask True

            if equip_girls:
                imagebutton:
                    xysize (39, 50)
                    pos (175, 14)
                    action Return(["control", "right"])
                    idle "content/gfx/interface/buttons/small_button_wood_right_idle.png"
                    hover "content/gfx/interface/buttons/small_button_wood_right_hover.png"
                    tooltip "Next Character"
                    focus_mask True
                    keysym "K_RIGHT"

            imagebutton:
                pos (178, 70)
                idle im.Scale("content/gfx/interface/buttons/close2.png", 35, 35)
                hover im.Scale("content/gfx/interface/buttons/close2_h.png", 35, 35)
                action Return(["control", "return"])
                tooltip "Return to previous screen!"

        # NAME ========================================>
        hbox:
            xfill True
            ysize 48
            ypos 120
            $ temp = eqtarget.name
            text temp color "#ecc88a" font "fonts/TisaOTM.otf" size 28 outlines [(1, "#3a3a3a", 0, 0)] align .55, .5:
                if len(temp) > 12:
                    size 18

        # LVL =========================================>
        hbox:
            xsize 220
            ypos 168
            label "Lvl [eqtarget.level]" text_color "#CDAD00" text_font "fonts/Rubius.ttf" text_size 16 text_outlines [(1, "#3a3a3a", 0, 0)] xalign .53

        # Left Frame Buttons: =========================>
        vbox:
            xsize 220
            ypos 185
            style_prefix "pb"
            spacing 1
            hbox:
                xalign .5
                spacing 1
                button:
                    xsize 70
                    action SetScreenVariable("stats_display", "stats"), With(dissolve)
                    text "Stats" style "pb_button_text" yoffset 2
                button:
                    xsize 70
                    action SetScreenVariable("stats_display", "traits"), With(dissolve)
                    text "Traits" style "pb_button_text" yoffset 2

            fixed:
                xsize 220
                button:
                    xalign .5
                    xsize 70
                    action SetScreenVariable("stats_display", "skills"), With(dissolve)
                    text "Skills" style "pb_button_text" yoffset 2
                if stats_display == "skills":
                    python:
                        if skill_display == "combat":
                            group_icon = "content/gfx/interface/icons/combat.webp"
                            group_tt = "Combat skills are shown!"
                            next_group = "other"
                        else:
                            group_icon = "content/gfx/interface/images/student.png"
                            group_tt = "Non-combat skills are shown!"
                            next_group = "combat"
                        img = PyTGFX.scale_img(group_icon, 20, 20)
                    imagebutton:
                        xalign .75#, .5
                        yoffset 4
                        idle img
                        hover PyTGFX.bright_img(img, 0.15)
                        action SetScreenVariable("skill_display", next_group)
                        tooltip group_tt

        # Stats/Skills:
        vbox:
            yfill True
            yoffset 200
            spacing 2
            xmaximum 218

            if stats_display == "stats":
                vbox:
                    spacing 3
                    pos (4, 40)
                    # STATS ===================================>
                    frame:
                        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
                        xsize 218
                        padding 6, 6
                        margin 0, 0
                        style_group "proper_stats"
                        has vbox spacing 1
                        python:
                            stats = ["constitution", "charisma", "intelligence", "joy"] if eqtarget == hero else ["constitution", "charisma", "intelligence", "character", "joy", "disposition", "affection"]
                            stats = [[stat, "#79CDCD"] for stat in stats] # stat_color
                            stats = [["health", "#CD4F39"], ["vitality", "#43CD80"]] + stats
                            for stat in stats:
                                stat.append("#F5F5DC") # value_color

                        fixed:
                            xysize 204, 28 
                            label (u"Stats:") text_size 18 text_color "#CDCDC1" text_bold True xalign .5
                            $ img = PyTGFX.scale_img("content/gfx/interface/icons/info.webp", 12, 12)
                            imagebutton:
                                align (.98, 0.1)
                                focus_mask True
                                idle img
                                hover PyTGFX.bright_img(img, 0.15)
                                action Show("popup_info", content="stat_info_content", param=(eqtarget, stats))

                        for stat, stat_color, value_color in stats:
                            frame:
                                xysize 204, 25
                                text stat.capitalize() xalign .02 color stat_color
                                if stat in ["health", "vitality"]:
                                    $ tempc = "red" if eqtarget.get_stat(stat) <= eqtarget.get_max(stat)*.3 else value_color
                                else:
                                    $ tempc = value_color
                                $ temp = build_str_for_eq(eqtarget, dummy, stat, tempc)
                                text temp style_suffix "value_text" xalign .98 yoffset 3

                    # BATTLE STATS ============================>
                    frame:
                        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
                        xsize 218
                        padding 6, 6
                        margin 0, 0
                        style_group "proper_stats"
                        has vbox spacing 1

                        python:
                            stats = [["attack", "#CD4F39"], ["defence", "#dc762c"], ["magic", "#8470FF"], ["mp", "#009ACD"], ["agility", "#1E90FF"], ["luck", "#00FA9A"]]
                            for stat in stats:
                                stat.append(stat[1])

                        fixed:
                            xysize 204, 28
                            label (u"Battle Stats:") text_size 18 text_color "#CDCDC1" text_bold True xalign .5
                            $ img = PyTGFX.scale_img("content/gfx/interface/icons/info.webp", 12, 12)
                            imagebutton:
                                align (.98, 0.1)
                                focus_mask True
                                idle img
                                hover PyTGFX.bright_img(img, 0.15)
                                action Show("popup_info", content="stat_info_content", param=(eqtarget, stats))

                        for stat, stat_color, value_color in stats:
                            frame:
                                xysize 204, 25
                                text stat.capitalize() color stat_color
                                if stat == "mp":
                                    $ tempc = "red" if eqtarget.get_stat(stat) <= eqtarget.get_max(stat)*.3 else value_color
                                else:
                                    $ tempc = value_color
                                $ temp = build_str_for_eq(eqtarget, dummy, stat, tempc)
                                text temp style_suffix "value_text" xalign .98 yoffset 3

            elif stats_display == "skills" and skill_display == "combat":
                vbox:
                    spacing 5
                    pos (4, 40)
                    frame:
                        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
                        xsize 218
                        padding 6, 6
                        margin 0, 0
                        style_group "proper_stats"
                        has vbox spacing 1 xfill True

                        label (u"Attacks:") text_size 18 text_color "#CDCDC1" text_bold True xalign .49 text_outlines [(3, "#424242", 0, 0), (2, "#8B0000", 0, 0), (1, "#424242", 0, 0)]

                        if getattr(store, "dummy", None) is not None:
                            $ t_old = set(eqtarget.attack_skills)
                            $ t_new = set(dummy.attack_skills)

                            $ temp = t_new.difference(t_old)
                            $ t_old = t_old.difference(t_new)

                            $ t_new = sorted(list(temp), key=attrgetter("name"))
                            $ t_old = sorted(list(t_old), key=attrgetter("name"))
                        else:
                            $ t_old = t_new = []

                        viewport:
                            xysize (218, 200)
                            edgescroll (40, 40)
                            draggable True
                            mousewheel True
                            has vbox spacing 1

                            $ xsize, ysize = 208, 22
                            # Added attack skills
                            for skill in t_new:
                                use skill_info(skill, xsize, ysize, idle_color="#43CD80")

                            # Removed attack skills
                            for skill in t_old:
                                use skill_info(skill, xsize, ysize, idle_color="#CD4F39", strikethrough=True)

                            # Remaining attack skills
                            $ temp = set(t_new + t_old)
                            for skill in eqtarget.attack_skills:
                                if skill not in temp:
                                    use skill_info(skill, xsize, ysize, idle_color="#F5F5DC")

                    frame:
                        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
                        xsize 218
                        padding 6, 6
                        margin 0, 0
                        style_group "proper_stats"

                        has vbox spacing 1 xfill True
                        label (u"Spells:") text_size 18 text_color "#CDCDC1" text_bold True xalign .49 text_outlines [(3, "#424242", 0, 0), (2, "#104E8B", 0, 0), (1, "#424242", 0, 0)]

                        if getattr(store, "dummy", None) is not None:
                            $ t_old = set(eqtarget.magic_skills)
                            $ t_new = set(dummy.magic_skills)

                            $ temp = t_new.difference(t_old)
                            $ t_old = t_old.difference(t_new)

                            $ t_new = sorted(list(temp), key=attrgetter("name"))
                            $ t_old = sorted(list(t_old), key=attrgetter("name"))
                        else:
                            $ t_old = t_new = []

                        viewport:
                            xysize (218, 175)
                            edgescroll (40, 40)
                            draggable True
                            mousewheel True
                            has vbox spacing 1

                            $ xsize, ysize = 208, 22
                            # Added magic skills
                            for skill in t_new:
                                use skill_info(skill, xsize, ysize, idle_color="#43CD80")

                            # Removed magic skills
                            for skill in t_old:
                                use skill_info(skill, xsize, ysize, idle_color="#CD4F39", strikethrough=True)

                            # Remaining magic skills
                            $ temp = set(t_new + t_old)
                            for skill in eqtarget.magic_skills:
                                if skill not in temp:
                                    use skill_info(skill, xsize, ysize, idle_color="#F5F5DC")

            elif stats_display == "skills": # and skill_display == "other":
                vbox:
                    spacing 5
                    pos (4, 40)
                    frame:
                        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
                        xsize 218
                        padding 6, 6
                        margin 0, 0
                        style_prefix "proper_stats"
                        has viewport xysize (218, 454) draggable True mousewheel True child_size (218, 1000)
                        vbox:
                            spacing 1
                            $ base_ss = eqtarget.stats.get_base_ss()
                            for skill in eqtarget.stats.skills:
                                $ skill_limit = int(eqtarget.get_max_skill(skill))
                                $ skill_old = int(eqtarget.get_skill(skill))
                                if getattr(store, "dummy", None) is not None:
                                    $ skill_new = int(dummy.get_skill(skill))
                                else:
                                    $ skill_new = skill_old
                                # We don't care about the skill if it's less than 10% of limit:
                                if skill in base_ss or skill_old > skill_limit/10 or skill_new > skill_limit/10:
                                    frame:
                                        xysize (208, 27)
                                        xpadding 2
                                        text skill.capitalize() color "gold" size 18 xoffset 10 # style_suffix "value_text" 
                                        if skill in base_ss:
                                            button:
                                                xysize 16, 16
                                                xoffset -3
                                                background PyTGFX.scale_img("content/gfx/interface/icons/stars/legendary.png", 16, 16)
                                                action NullAction()
                                                tooltip "This is a Class Skill!"
                                        if skill_old == skill_new:
                                            hbox:
                                                xalign 1.0
                                                yoffset 4
                                                use stars(skill_old, skill_limit)
                                        elif skill_old > skill_new:
                                            hbox:
                                                xalign 1.0
                                                yoffset 4
                                                use stars(skill_old, skill_limit, func=im.MatrixColor, matrix=im.matrix.tint(1, .25, .25))
                                            hbox:
                                                xalign 1.0
                                                yoffset 4
                                                use stars(skill_new, skill_limit)
                                        else: # skill_old < skill_new
                                            hbox:
                                                xalign 1.0
                                                yoffset 4
                                                use stars(skill_new, skill_limit, func=im.MatrixColor, matrix=im.matrix.tint(.25, 1, .25))
                                            hbox:
                                                xalign 1.0
                                                yoffset 4
                                                use stars(skill_old, skill_limit)

            elif stats_display == "traits":
                vbox:
                    spacing 5
                    pos (4, 40)
                    frame:
                        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
                        xsize 218
                        padding 6, 6
                        margin 0, 0
                        style_group "proper_stats"
                        has vbox spacing 1 xfill True

                        label (u"Traits:") text_size 18 text_color "#CDCDC1" text_bold True xalign .49

                        $ t_cur = [t for t in eqtarget.traits if not any([t.basetrait, t.personality, t.race, t.hidden])]
                        if getattr(store, "dummy", None) is not None:
                            $ t_old = set(t_cur)
                            $ t_new = set(t for t in dummy.traits if not any([t.basetrait, t.personality, t.race, t.hidden]))

                            $ temp = t_new.difference(t_old)
                            $ t_old = t_old.difference(t_new)

                            $ t_new = sorted(list(temp), key=attrgetter("id"))
                            $ t_old = sorted(list(t_old), key=attrgetter("id"))
                        else:
                            $ t_old = t_new = []

                        viewport:
                            xysize (218, 200)
                            edgescroll (40, 40)
                            draggable True
                            mousewheel True
                            has vbox spacing 1

                            $ xsize, ysize = 208, 22
                            # New traits
                            for trait in t_new:
                                if not trait.hidden:
                                    use trait_info(trait, xsize, ysize, idle_color="#43CD80")

                            # Removed traits
                            for trait in t_old:
                                if not trait.hidden:
                                    use trait_info(trait, xsize, ysize, idle_color="#CD4F39", strikethrough=True)

                            # Remaining traits
                            $ temp = set(t_new + t_old)
                            for trait in t_cur:
                                if not trait.hidden and trait not in temp:
                                    use trait_info(trait, xsize, ysize, idle_color="#F5F5DC")

                    frame:
                        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
                        xsize 218
                        padding 6, 6
                        margin 0, 0
                        style_group "proper_stats"
                        has vbox spacing 1 xfill True

                        label (u"Effects:") text_size 18 text_color "#CDCDC1" text_bold True xalign .49

                        if getattr(store, "dummy", None) is not None:
                            $ t_old = set(t.name for t in eqtarget.effects.itervalues())
                            $ t_new = set(t.name for t in dummy.effects.itervalues())

                            $ temp = t_new.difference(t_old)
                            $ t_old = t_old.difference(t_new)

                            $ t_new = sorted(list(temp))
                            $ t_old = sorted(list(t_old))
                        else:
                            $ t_old = t_new = []

                        viewport:
                            xysize (218, 175)
                            edgescroll (40, 40)
                            draggable True
                            mousewheel True
                            has vbox spacing 1

                            $ xsize, ysize = 208, 22
                            # Added effects
                            for effect in t_new:
                                $ effect = CharEffect(effect)
                                use effect_info(effect, xsize, ysize, idle_color="#43CD80")

                            # Removed effects
                            for effect in t_old:
                                $ effect = CharEffect(effect)
                                use effect_info(effect, xsize, ysize, idle_color="#CD4F39", strikethrough=True)

                            # Remaining effects
                            $ temp = set(t_new + t_old)
                            for effect in eqtarget.effects.itervalues():
                                if effect.name not in temp:
                                    use effect_info(effect, xsize, ysize, idle_color="#F5F5DC")

    #use char_equip_right_frame()

#screen char_equip_right_frame():
    # Right Frame: =====================================>
    # TOOLTIP TEXT  ====================================>
    frame:
        pos (930, 4)
        background Frame(im.Alpha("content/gfx/frame/ink_box.png", alpha=.4), 10, 10)
        xpadding 10
        xysize (345, 110)

        python:
            classes = list(t.id for t in eqtarget.traits.basetraits)
            classes.sort()
            classes = ", ".join(classes)

            t = "is %s{vspace=17}Classes: %s\nWork: %s\nAction: %s{/color}" % (eqtarget.status.capitalize(), classes, eqtarget.workplace, action_str(eqtarget))

        text (u"{color=gold}[eqtarget.name]{/color}  {color=#ecc88a}%s" % t) size 14 align (.55, .65) font "fonts/TisaOTM.otf" line_leading -5

    # Right Frame Buttons ====================================>
    fixed:
        pos 937, 118
        xsize 345
        style_prefix "pb"
        if inv_source == hero:
            $ temp = "Your Inventory"
        else:
            $ temp = "%s's Inventory" % set_font_color(inv_source.nickname, "pink" if inv_source.gender == "female" else "paleturquoise")
        text temp color "#CDCDC1" size 19 font "fonts/rubius.ttf" xalign .5 outlines [(1, "black", 0, 0)] #yalign .5 #style "pb_button_text"
        $ img = im.Scale("content/gfx/interface/buttons/switch.png", 20, 20)
        if inv_source == hero:
            $ swap_source = eqtarget
        else:
            $ swap_source = hero
            $ img = im.Flip(img, horizontal=True, vertical=True)
        imagebutton:
            xalign .9
            idle img
            hover PyTGFX.bright_img(img, .15)
            insensitive im.Sepia(img)
            action [SetVariable("inv_source", swap_source),
                    Function(swap_source.inventory.apply_filter, inv_source.inventory.slot_filter),
                    Return(["con", "return"]),
                    With(dissolve)]
            sensitive eqtarget != hero
            tooltip "Equip from {}'s Inventory".format(swap_source.nickname)

    # "Final" Filters (id/price/etc.)
    hbox:
        pos 937, 146
        spacing 1
        style_prefix "pb"
        button:
            xsize 110
            action Return(["equip_for"])
            text "Equip For" style "pb_button_text" yoffset 1
        button:
            xsize 110
            action Return(["unequip_all"])
            text "Unequip all" style "pb_button_text" yoffset 1
        button:
            xsize 110
            action If(eqtarget != hero, true=Return(["jump", "item_transfer"]))
            text "Exchange" style "pb_button_text" yoffset 1

    # Auto-Equip/Item Transfer Buttons and Paging: ================>
    $ inventory = inv_source.inventory
    frame:
        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
        pos (931, 180)
        xysize (345, 80)
        has vbox spacing 2 xalign .5
        hbox:
            spacing 1
            style_prefix "pb"
            button:
                xsize 110
                action Function(inventory.update_sorting, ("id", False))
                text "Name" style "pb_button_text" yoffset 1
                selected inventory.final_sort_filter[0] == "id"
                tooltip "Sort items by the Name!"
            button:
                xsize 110
                action Function(inventory.update_sorting, ("price", True))
                text "Price" style "pb_button_text" yoffset 1
                selected inventory.final_sort_filter[0] == "price"
                tooltip "Sort items by the Price!"
            button:
                xsize 110
                action Function(inventory.update_sorting, ("amount", True))
                text "Amount" style "pb_button_text" yoffset 1
                selected inventory.final_sort_filter[0] == "amount"
                tooltip "Sort items by the Amount owned!"
        use paging(ref=inventory, use_filter=False, xysize=(240, 30), align=(.5, .5))

    # Gender filter
    default item_genders = ["any", "male", "female"]
    default gender_icons = ["content/gfx/interface/icons/both.png",
                            "content/gfx/interface/icons/male.png",
                            "content/gfx/interface/icons/female.png"]
    default gender_tt = ["Items of all genders are shown!",
                         "Items of Male and Unisex genders are shown!",
                         "Items of Female and Unisex genders are shown!"]
    python:
        index = item_genders.index(inventory.gender_filter)
        next_gender = item_genders[(index + 1) % len(item_genders)]

    button:
        pos 935, 256 anchor -.1, 1.0
        xysize 40, 40
        style "pb_button"
        add PyTGFX.scale_img(gender_icons[index], 30, 30) align .5, .5
        action Function(inventory.apply_filter,
                        direction=inventory.slot_filter,
                        gender=next_gender)
        tooltip gender_tt[index]

    # Filters: ====================================>
    vpgrid:
        pos (935, 270)
        style_group "dropdown_gm"
        xsize 340
        cols 7 rows 2
        spacing 2
        for filter in inventory.filters:
            frame:
                padding 0, 0
                margin 1, 1
                background Null()
                $ img = PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s.png" % filter, 44, 44)
                $ img_hover = PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s hover.png" % filter, 44, 44)
                $ img_selected = PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s selected.png" % filter, 44, 44)
                imagebutton:
                    idle img
                    hover img_hover
                    selected_idle img_selected
                    selected_hover PyTGFX.bright_img(img_selected, .10)
                    action Function(inventory.apply_filter, filter) #, SetVariable("last_inv_filter", filter)]
                    selected filter == inventory.slot_filter
                    focus_mask True
                    tooltip filter.capitalize()

    # Inventory: ====================================>
    frame:
        pos (931, 372)
        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
        use items_inv(inv=inventory, main_size=(333, 333), frame_size=(80, 80), return_value=["item", "equip"])

    # Item Info (Mid-Bottom Frame): ====================================>
    hbox:
        align (.388, 1.0)
        spacing 1
        style_group "content"

        # Item Description/Outfits:
        frame:
            xalign .6
            at fade_in_out()
            background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/Mc_bg3.png", -0.2), alpha=.3), 5, 5)
            xysize (710, 296)
            #use char_equip_item_info(item=focusitem, size=(703, 287))

#screen char_equip_item_info(item=None, char=None, size=(635, 380)):
            # One of the most difficult code rewrites I've ever done (How Gismo aligned everything in the first place is a work of (weird and clumsy) art...):
            # Recoding this as three vertically aligned HBoxes...
            if focusitem:
                $ item, xs, ys = focusitem, 703, 287
                fixed:
                    style_prefix "proper_stats"
                    xysize (xs, ys)

                    # Top HBox: Discard/Close buttons and the Item ID:
                    hbox:
                        align .5, .0
                        xsize xs-10
                        $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/discard.png", 22, 22)
                        imagebutton:
                            align 0, .5
                            idle temp
                            hover PyTGFX.bright_img(temp, 0.15)
                            insensitive PyTGFX.sepia_img(temp)
                            action Return(["item", "discard"])
                            sensitive inv_source.inventory[item] > 0
                            tooltip "Discard item"
                        frame:
                            align .5, .5
                            xysize (439, 35)
                            background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.05), alpha=.9), 10, 10)
                            label ('[item.id]') text_color "gold" align .5, .5 text_size 19 text_outlines [(1, "black", 0, 0)] text_style "interactions_text"
                        $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/close4.png", 20, 20)
                        imagebutton:
                            align .98, .5
                            idle temp
                            hover PyTGFX.bright_img(temp, 0.15)
                            action Return(["con", "return"])
                            tooltip "Close item info"

                    # Separation Strip (Outside of alignments):
                    label ('{color=#ecc88a}--------------------------------------------------------------------------------------------------') xalign .5 ypos 25
                    label ('{color=#ecc88a}--------------------------------------------------------------------------------------------------') xalign .5 ypos 163

                    # Mid HBox:
                    hbox:
                        xsize xs
                        xalign .5
                        ypos 47
                        spacing 5

                        # Left Items Info:
                        frame:
                            xalign .02
                            style_prefix "proper_stats"
                            background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.05), alpha=.9), 5, 5)
                            xysize (180, 130)
                            xpadding 0
                            xmargin 0
                            has vbox spacing 1 xoffset 10
                            null height 13
                            frame:
                                xysize (160, 25)
                                text "Price:" color "gold" xalign .02
                                label str(item.price) text_color "gold" text_size 15 align .98, .5 text_outlines [(1, "#3a3a3a", 0, 0)]
                            frame:
                                xysize (160, 25)
                                text "Slot:" color "#F5F5DC" xalign .02
                                $ slot = EQUIP_SLOTS.get(item.slot, item.slot.capitalize())
                                label slot text_color "#F5F5DC" text_size 15 align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                            frame:
                                xysize (160, 25)
                                text "Type:" color "#F5F5DC" xalign .02
                                label item.type.capitalize() text_color "#F5F5DC" text_size 15 align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                            frame:
                                xysize (160, 25)
                                text "Sex:" color "#F5F5DC" xalign .02
                                $ color = "#F5F5DC"
                                $ temp = getattr(item, "gender", "unisex")
                                if item.slot in ["gift", "resources", "loot"]:
                                    $ temp = "N/A"
                                elif item.type == "food" and temp == "unisex":
                                    $ temp = "N/A"
                                elif temp == "female":
                                    $ color = "#FFAEB9" 
                                elif temp == "male":
                                    $ color = "#FFA54F"
                                label temp.capitalize() text_color color text_size 15 align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]

                        # Buttons and image:
                        if item_direction == "unequip":
                            $ temp_source = eqtarget
                            $ temp_target = hero
                        else:
                            $ temp_source = inv_source
                            $ temp_target = eqtarget if inv_source == hero else hero
                        button:
                            style_group "pb"
                            align (.0, .5)
                            xysize (80, 45)
                            action Return(["item", "transfer", temp_source, temp_target])
                            sensitive eqtarget != hero
                            if eqtarget == hero:
                                text "Transfer" style "pb_button_text" align (.5, .5)
                            else:
                                tooltip "Transfer %s from %s to %s" % (item.id, temp_source.nickname, temp_target.nickname)
                                text "Give to\n{color=#FFAEB9}[temp_target.nickname]{/color}" style "pb_button_text" align (.5, .5) line_leading 3

                        frame:
                            align (.5, .5)
                            background Frame("content/gfx/frame/frame_it2.png", 5, 5)
                            xysize (120, 120)
                            $ temp = PyTGFX.scale_content(item.icon, 100, 100)
                            imagebutton:
                                align .5, .5
                                idle temp
                                hover PyTGFX.bright_content(temp, .15)
                                action Show("popup_info", content="item_info_content", param=item)

                        if item_direction == "unequip":
                            $ temp = "Unequip"
                        elif item_direction == "equip":
                            if item.slot == "consumable":
                                $ temp = "Use"
                            else:
                                $ temp = "Equip"
                        $ temp_msg = " ".join([temp, item.id])
                        button:
                            style_group "pb"
                            align (1.0, .5)
                            xysize (80, 45)
                            tooltip temp_msg
                            action SensitiveIf(focusitem), Return(["item", "equip/unequip"])
                            text temp style "pb_button_text" align (.5, .5):
                                if item_direction == "equip" and not can_equip(focusitem, eqtarget, silent=True):
                                    color "red" strikethrough True

                        # Right items info (Stats):
                        frame:
                            xalign .98
                            background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.05), alpha=.9), 5, 5)
                            xysize (185, 130)
                            style_group "proper_stats"
                            left_padding 6
                            right_padding 3
                            ypadding 5
                            has viewport draggable True mousewheel True child_size 200, 500
                            vbox:
                                if item in eqtarget.constemp:
                                    $ temp = eqtarget.constemp[item]
                                    null height 3
                                    frame:
                                        xysize (172, 18)
                                        text u"{i}Remaining %s: %d{/i}" % (plural("day", temp), temp) color "yellowgreen" size 15 xalign .5 yoffset -2

                                if item in eqtarget.miscitems:
                                    $ temp = item.mtemp - eqtarget.miscitems[item] 
                                    null height 3
                                    frame:
                                        xysize (172, 18)
                                        text u"{i}Remaining %s: %d{/i}" % (plural("day", temp), temp) color "yellowgreen" size 15 xalign .5 yoffset -2

                                if item.mod:
                                    label u"Stats:" text_size 14 text_color "gold" xpos 30
                                    vbox:
                                        spacing 1
                                        for stat, value in item.mod.items():
                                            frame:
                                                xysize (172, 18)
                                                text stat.capitalize() color "#F5F5DC" size 15 xalign .02 yoffset -2
                                                label str(value) text_color "#F5F5DC" text_size 15 align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                                    null height 3

                                if item.max:
                                    label u"Max:" text_size 14 text_color "gold" xpos 30
                                    vbox:
                                        spacing 1
                                        for stat, value in item.max.items():
                                            frame:
                                                xysize (172, 18)
                                                text stat.capitalize() color "#F5F5DC" size 15 xalign .02 yoffset -2
                                                label str(value) text_color "#F5F5DC" text_size 15 align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                                    null height 3

                                if item.min:
                                    label u"Min:" text_size 14 text_color "gold" xpos 30
                                    vbox:
                                        spacing 1
                                        for stat, value in item.min.items():
                                            frame:
                                                xysize (172, 18)
                                                text stat.capitalize() color "#F5F5DC" size 15 xalign .02 yoffset -2
                                                label str(value) text_color "#F5F5DC" text_size 15 align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                                    null height 3

                    # Bottom HBox: Desc/Traits/Effects/Skills:
                    hbox:
                        yalign 1.0
                        # Traits, Effects:
                        frame:
                            background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.05), alpha=.9), 5, 5)
                            xysize 158, 104
                            padding 2, 3
                            has viewport draggable True mousewheel True

                            # Traits:
                            vbox:
                                style_group "proper_stats"
                                xsize 154
                                $ temp = [t for t in item.addtraits if not t.hidden]
                                if temp:
                                    label ('Adds Traits:') text_size 14 text_color "gold" xpos 10
                                    for trait in temp:
                                        use trait_info(trait, 146, 20)
                                    null height 2
                                $ temp = [t for t in item.removetraits if not t.hidden]
                                if temp:
                                    label ('Removes Traits:') text_size 14 text_color "gold" xpos 10
                                    for trait in temp:
                                        use trait_info(trait, 146, 20)
                                    null height 2
                                if item.addeffects:
                                    label ('Adds Effects:') text_size 14 text_color "gold" xpos 10
                                    for effect in item.addeffects:
                                        $ effect = CharEffect(effect)
                                        use effect_info(effect, 146, 20)
                                    null height 2
                                if item.removeeffects:
                                    label ('Removes Effects:') text_size 14 text_color "gold" xpos 10
                                    for effect in item.removeeffects:
                                        $ effect = CharEffect(effect)
                                        use effect_info(effect, 146, 20)
                                    #null height 2

                        frame:
                            xysize 382, 104
                            padding 10, 5
                            background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.9), 5, 5)
                            has viewport draggable True mousewheel True
                            text '{color=#ecc88a}[item.desc]{/color}' font "fonts/TisaOTM.otf" size 15 outlines [(1, "#3a3a3a", 0, 0)]

                        frame:
                            background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.05), alpha=.9), 5, 5)
                            xysize 158, 104
                            padding 2, 3
                            has viewport draggable True mousewheel True
                            if item.add_be_spells or item.attacks:
                                vbox:
                                    xsize 154
                                    style_group "proper_stats"
                                    label ('Adds Skills:') text_size 14 text_color "gold" xpos 10
                                    if item.add_be_spells:
                                        for skill in item.add_be_spells:
                                            use skill_info(skill, 146, 20)
                                        null height 2
                                    if item.attacks:
                                        for skill in item.attacks:
                                            use skill_info(skill, 146, 20)
                                        #null height 2

            else: # equipment saves
                frame:
                    style_prefix "proper_stats"
                    background Null()
                    left_padding 66
                    hbox:
                        for i, v in enumerate(eqtarget.eqsave):
                            vbox:
                                frame:
                                    xpadding -50
                                    background Null()
                                    style_prefix "pb"
                                    hbox:
                                        button:
                                            xysize (90, 30)
                                            selected eqsave[i]
                                            if focusoutfit == v:
                                                action ToggleDict(eqsave, i), SetVariable("focusoutfit", None), SetVariable("dummy", None), With(dissolve)
                                                tooltip "Hide the outfit"
                                            elif eqsave[i]:
                                                action Return(["outfit", "focus", v]), With(dissolve)
                                                tooltip "Try the outfit"
                                            else:
                                                action ToggleDict(eqsave, i), With(dissolve)
                                                tooltip "Show the outfit"

                                            text str(v["name"]) underline (focusoutfit == v) style "pb_button_text"
                                        $ temp = PyTGFX.scale_img("content/gfx/interface/buttons/edit.png", 16, 16)
                                        imagebutton:
                                            align (.0, .0)
                                            idle temp
                                            hover PyTGFX.bright_img(temp, 0.15)
                                            focus_mask True
                                            action Return(["outfit", "rename", v])
                                            tooltip "Rename the outfit"
                                        button:
                                            align (.5, .5)
                                            xysize (30, 30)
                                            action SensitiveIf(any(eqtarget.eqslots.values())), SetDict(eqsave, i, True), Return(["outfit", "save", v]), With(dissolve)
                                            text u"\u2193" align .5, .5
                                            padding (9, 1)
                                            tooltip "Update the outfit with the current equipment"
                                        if any(eqtarget.eqsave[i].values()):
                                            button:
                                                align (.5, .5)
                                                xysize (30, 30)
                                                action Function(eqtarget.load_equip, v), With(dissolve)
                                                text u"\u2191" align .5, .5
                                                padding (9, 1)
                                                tooltip "Use the outfit"
                                            button:
                                                align (.5, .5)
                                                xysize (30, 30)
                                                action Return(["outfit", "remove", v]), With(dissolve)
                                                text u"\u00D7" align .5, .5
                                                padding (8, 1)
                                                tooltip "Discard the outfit"
                                frame:
                                    xysize (234, 246)
                                    background Null()
                                    if eqsave[i]:
                                        use eqdoll(source=v, outfit=True, fx_size=(304, 266), scr_align=(.98, 1.0), frame_size=[55, 55], return_value=["item", "save"])

                        if len(eqtarget.eqsave) < 3:
                            vbox:
                                frame:
                                    background Null()
                                    style_prefix "pb"
                                    hbox:
                                        xalign .5
                                        button:
                                            xysize (90, 30)
                                            action SensitiveIf(any(eqtarget.eqslots.values())), SetDict(eqsave, len(eqtarget.eqsave), True), Return(["outfit", "create"]), With(dissolve)
                                            tooltip "Create a new outfit based on the current equipment"
                                            text "..." style "pb_button_text"

    # BASE FRAME 1 "top layer" ====================================>
    add "content/gfx/frame/h1.webp"

screen item_info_content(param, pos, anchor):
    default item = param
    fixed:
        pos pos
        anchor anchor
        fit_first True
        frame:
            background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
            padding 10, 10
            has vbox style_prefix "proper_stats" spacing 1

            $ any_mod = False
            if item.mod:
                $ any_mod = True
                label (u"Stats:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for stat, value in item.mod.iteritems():
                    frame:
                        xysize 200, 20
                        text stat.title() size 15 color "#79CDCD" align .0, .5 outlines [(1, "black", 0, 0)]
                        $ txt_color = "red" if value < 0 else "lime"
                        label "%+g" % value text_size 15 text_color txt_color align 1.0, .5 text_outlines [(1, "black", 0, 0)]
            if item.max:
                $ any_mod = True
                label (u"Max:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for stat, value in item.max.iteritems():
                    frame:
                        xysize 200, 20
                        $ txt_color = "red" if value < 0 else "lime"
                        text stat.title() size 15 color "#79CDCD" align .0, .5 outlines [(1, "black", 0, 0)]
                        label "%+g" % value text_size 15 text_color txt_color align 1.0, .5 text_outlines [(1, "black", 0, 0)]
            if item.min:
                $ any_mod = True
                label (u"Min:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for stat, value in item.min.iteritems():
                    frame:
                        xysize 200, 20
                        $ txt_color = "red" if value < 0 else "lime"
                        text stat.title() size 15 color "#79CDCD" align .0, .5 outlines [(1, "black", 0, 0)]
                        label "%+g" % value text_size 15 text_color txt_color align 1.0, .5 text_outlines [(1, "black", 0, 0)]
            if getattr(item, 'mtemp', False):
                label (u"Frequency:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                vbox:
                    frame:
                        xysize (200, 20)
                        if hasattr(item, 'mreusable'):
                            if item.mreusable:
                                $ temp = (u'Every %d days'%item.mtemp) if item.mtemp > 1 else u'Every day'
                            else:
                                $ temp = (u'After %d days'%item.mtemp) if item.mtemp > 1 else u'After one day'
                            text temp color "#F5F5DC" size 15 xalign .02 yoffset -2
                        if getattr(item, 'mdestruct', False):
                            text (u'Disposable') color "#F5F5DC" size 15 xalign 1.0 yoffset -2
                        if getattr(item, 'mreusable', False):
                            text (u'Reusable') color "#F5F5DC" size 15 xalign 1.0 yoffset -2
                    if getattr(item, 'statmax', False):
                        frame:
                            xysize (200, 20)
                            text (u'Stat limit') color "#F5F5DC" size 15 xalign .02 yoffset -2
                            label str(item.statmax) text_size 15 text_color "#F5F5DC" text_outlines [(1, "#3a3a3a", 0, 0)] xalign 1.0 yoffset -1
            if getattr(item, "cblock", False) or getattr(item, "ctemp", False):
                label (u"Frequency:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                if getattr(item, "cblock", False):
                    frame:
                        xysize (200, 20)
                        $ temp = (u'After %d days'%item.cblock) if item.cblock > 1 else u'After one day'
                        text temp color "#F5F5DC" size 15 xalign 1.0 yoffset -2
                if getattr(item, "ctemp", False):
                    frame:
                        xysize (200, 20)
                        text (u'Duration') color "#F5F5DC" size 15 xalign .02 yoffset -2
                        $ temp = (u'%d days'%item.ctemp) if item.ctemp > 1 else u'One day'
                        text temp color "#F5F5DC" size 15 xalign 1.0 yoffset -2

            $ temp = [t.id for t in item.addtraits if not t.hidden]
            $ tmp = [t.id for t in item.removetraits if not t.hidden]
            if temp or tmp:
                $ any_mod = True
                label (u"Traits:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for trait in temp:
                    frame:
                        xysize 200, 20
                        text trait.title() size 15 color "lime" outlines [(1, "black", 0, 0)] xalign .5 yoffset -1
                for trait in tmp:
                    frame:
                        xysize 200, 20
                        text trait.title() size 15 color "red" outlines [(1, "black", 0, 0)] xalign .5 yoffset -1

            if item.addeffects or item.removeeffects:
                $ any_mod = True
                label (u"Effects:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for effect in item.addeffects:
                    frame:
                        xysize 200, 20
                        text effect.title() size 15 color "lime" outlines [(1, "black", 0, 0)] xalign .5 yoffset -1
                for effect in item.removeeffects:
                    frame:
                        xysize 200, 20
                        text effect.title() size 15 color "red" outlines [(1, "black", 0, 0)] xalign .5 yoffset -1

            if item.mod_skills or item.add_be_spells or item.attacks:
                $ any_mod = True
                label (u"Skills:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for skill, data in item.mod_skills.iteritems():
                    frame:
                        xysize 200, 20
                        text skill.title() size 15 color "yellowgreen" outlines [(1, "black", 0, 0)] xalign .02 yoffset -1

                        $ img_path = "content/gfx/interface/icons/skills_icons/"
                        default PS = PyTGFX.scale_img
                        button:
                            style "default"
                            xysize 20, 18
                            action NullAction()
                            align .99, .5
                            if data[0] > 0:
                                add PS(img_path + "left_green.png", 20, 20)
                            elif data[0] < 0:
                                add PS(img_path + "left_red.png", 20, 20)
                            if data[1] > 0:
                                add PS(img_path + "right_green.png", 20, 20)
                            elif data[1] < 0:
                                add PS(img_path + "right_red.png", 20, 20)
                            if data[2] > 0:
                                add PS(img_path + "top_green.png", 20, 20)
                            elif data[2] < 0:
                                add PS(img_path + "top_red.png", 20, 20)

                        $ temp = ""
                        $ value = data[3]
                        if value:
                            $ txt_color = "red" if value < 0 else "lime"
                            $ temp += set_font_color("%+g" % value, txt_color)
                        $ value = data[4]
                        if value:
                            if temp:
                                $ temp += ", "
                            $ txt_color = "red" if value < 0 else "lime"
                            $ temp += set_font_color("%+g" % value, txt_color)
                        if temp:
                            label temp text_size 15 text_outlines [(1, "black", 0, 0)] xalign 1.0 yoffset -1

                if item.add_be_spells:
                    for skill in item.add_be_spells:
                        frame:
                            xysize 200, 20
                            text skill.name size 15 color "yellow" outlines [(1, "black", 0, 0)] xalign .5 yoffset -1
                if item.attacks:
                    for skill in item.attacks:
                        frame:
                            xysize 200, 20
                            text skill.name size 15 color "yellow" outlines [(1, "black", 0, 0)] xalign .5 yoffset -1

            $ bem = modifiers_calculator(item)
            if any((bem.elemental_modifier, bem.defence_modifier, bem.evasion_bonus, bem.delivery_modifier, bem.damage_multiplier, bem.ch_multiplier)):
                $ any_mod = True
                use list_be_modifiers(bem)

            if item.be or item.jump_to_label:
                $ any_mod = True
                label (u"Other:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                if item.be:
                    frame:
                        xysize 200, 20
                        text "Can be used in combat!" size 15 color "yellowgreen" outlines [(1, "black", 0, 0)] xalign .5 yoffset -1

                if item.jump_to_label:
                    frame:
                        xysize 200, 20
                        text "Special item!" size 15 color "yellowgreen" outlines [(1, "black", 0, 0)] xalign .5 yoffset -1

            if not any_mod:
                label ("- no direct effects -") text_size 15 text_color "goldenrod" text_bold True text_outlines [(1, "black", 0, 0)] xalign .45 yoffset -1

screen stat_info_content(param, pos, anchor):
    $ char, stats = param
    fixed:
        pos pos
        anchor anchor
        fit_first True
        frame:
            background Frame("content/gfx/frame/p_frame52.webp", 10, 10)
            padding 10, 10
            has vbox style_prefix "proper_stats" spacing 1
            
            hbox:
                frame:
                    xysize 80, 20
                    # "stat"
                frame:
                    xysize 50, 20
                    text "min" size 15 color "grey" bold True align .5, .5 outlines [(1, "black", 0, 0)]
                frame:
                    xysize 70, 20
                    text "level-max" size 15 color "grey" bold True align .5, .5 outlines [(1, "black", 0, 0)]

            for stat, stat_color, value_color in stats:
                hbox:
                    frame:
                        xysize 80, 20
                        text stat.capitalize() size 15 color stat_color align 0.02, .5 outlines [(1, "black", 0, 0)]
                    frame:
                        xysize 50, 20
                        $ val = char.stats.get_min(stat)
                        if val:
                            text "%d" % val size 15 color value_color align 0.5, .5 outlines [(1, "black", 0, 0)]
                    frame:
                        xysize 70, 20
                        text "%d" % char.stats.lvl_max[stat] size 15 color value_color align 0.5, .5 outlines [(1, "black", 0, 0)]

screen diff_item_effects(char, dummy):
    zorder 10
    textbutton "X":
        align (1.0, .0)
        action Hide("diff_item_effects"), With(dissolve)
    frame:
        xysize (1000, 500)
        background Solid("#F00", alpha=.1)
        align (.1, .5)
        has hbox

        vbox:
            text "Stats:"
            for stat in char.stats:
                text "[stat]: {}".format(dummy.get_stat(stat) - char.get_stat(stat))
        vbox:
            text "Max Stats:"
            for stat in char.stats:
                text "[stat]: {}".format(dummy.get_max(stat) - char.get_max(stat))
        vbox:
            for skill in char.stats.skills:
                text "[skill]: {}".format(dummy.get_skill(skill) - char.get_skill(skill))
        vbox:
            text "Traits (any):"
            python:
                t_old = set(t.id for t in char.traits)
                t_new = set(t.id for t in dummy.traits)
                temp = t_new.difference(t_old)
                temp = sorted(list(temp))
            for t in temp:
                text "[t]"
