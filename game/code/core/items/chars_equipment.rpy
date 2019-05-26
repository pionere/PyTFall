# Temp code, should be moved to items funcs:
init:
    style positive_item_eqeffects_change:
        is text
        size 9
        color "lawngreen"

    style negative_item_eqeffects_chage:
        is positive_item_eqeffects_change
        color "#ff1a1a"

    screen discard_item(eq_sourse, item):
        zorder 10
        modal True

        add Transform("content/gfx/images/bg_gradient2.webp", alpha=.3)
        frame:
            background Frame(Transform("content/gfx/frame/ink_box.png", alpha=.75), 10, 10)
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
                    action Function(eq_sourse.inventory.remove, item), Hide("discard_item"), With(dissolve)
                $ amount = eq_sourse.inventory[item]
                textbutton "{size=-1}Discard All":
                    xalign .5
                    action SensitiveIf(amount > 1), Function(eq_sourse.inventory.remove, item, amount), Hide("discard_item"), With(dissolve)
                textbutton "{size=-1}No":
                    xalign .5
                    action Hide("discard_item"), With(dissolve)

init python:
    def build_str_for_eq(eqtarget, dummy, stat, tempc):
        temp = dummy.get_stat(stat) - eqtarget.get_stat(stat) if dummy else False
        tempmax = dummy.get_max(stat) - eqtarget.get_max(stat) if dummy else False
        if temp: # Case: Any Change to stat
            # The first is the absolute change, we want it to be colored green if it is positive, and red if it is not.
            tempstr = set_font_color("%d" % dummy.get_stat(stat), "green" if temp > 0 else "red")
            # Next is the increase:
            tempstr += ("{=positive_item_eqeffects_change}(+%d){/=}" if temp > 0 else "{=negative_item_eqeffects_chage}(%d){/=}") % temp
        else: # No change at all...
            tempstr = set_font_color("%d" % eqtarget.get_stat(stat), tempc)

        tempstr += set_font_color("/", tempc)

        if tempmax:
            # Absolute change of the max values, same rules as the actual values apply:
            tempstr += set_font_color("%d" % dummy.get_max(stat), "green" if tempmax > 0 else "red")
            tempstr += ("{=positive_item_eqeffects_change}(+%d){/=}" if tempmax > 0 else "{=negative_item_eqeffects_chage}(%d){/=}") % tempmax
        else: # No change at all...
            tempstr += set_font_color("%d" % eqtarget.get_max(stat), tempc)
        return tempstr

label char_equip:
    python:
        focusitem = None
        focusoutfit = None
        unequip_slot = None
        item_direction = None
        dummy = None
        eqsave = [False, False, False]

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
            python:
                renpy.show_screen("equip_for", renpy.get_mouse_pos())
                dummy = None
        elif result[0] == "item":
            if result[1] == 'equip/unequip':
                $ dummy = None # Must be set here so the items that jump away to a label work properly.
                python:
                    # Equipping:
                    if item_direction == 'equip':
                        # Common to any eqtarget:
                        if not can_equip(focusitem, eqtarget, silent=False):
                            focusitem = None
                            focusoutfit = None
                            unequip_slot = None
                            item_direction = None
                            jump("char_equip_loop")

                        # See if we can access the equipment first:
                        if equipment_access(eqtarget, focusitem):
                            # If we're not equipping from own inventory, check if we can transfer:
                            if eqtarget != inv_source:
                                if not transfer_items(inv_source, eqtarget, focusitem):
                                    # And terminate if we can not...
                                    jump("char_equip_loop")

                            # If we got here, we just equip the item :D
                            equip_item(focusitem, eqtarget)
                    elif item_direction == 'unequip':
                        # Check if we are allowed to access inventory and act:
                        if equipment_access(eqtarget, focusitem, unequip=True):
                            eqtarget.unequip(focusitem, unequip_slot)

                            # We should try to transfer items in case of:
                            # We don't really care if that isn't possible...
                            if inv_source != eqtarget:
                                transfer_items(eqtarget, inv_source, focusitem, silent=False)

                    focusitem = None
                    focusoutfit = None
                    unequip_slot = None
                    item_direction = None
            elif result[1] == "discard":
                python:
                    # Check if we can access the inventory:
                    if focusitem.slot == "quest" or focusitem.id in ["Your Pet"]:
                        renpy.call_screen('message_screen', "This item cannot be discarded.")
                    elif equipment_access(inv_source):
                        renpy.call_screen("discard_item", inv_source, focusitem)

                    focusitem = None
                    unequip_slot = None
                    item_direction = None
                    dummy = None
                    eqsave = [False, False, False]
            elif result[1] == "transfer":
                python:
                    if inv_source == hero:
                        transfer_items(hero, eqtarget, focusitem, silent=False)
                    else:
                        transfer_items(eqtarget, hero, focusitem, silent=False)
            elif result[1] == 'equip':
                python:
                    focusitem = result[2]

                    item_direction = 'equip'

                    # # To Calc the effects:
                    dummy = copy_char(eqtarget)
                    equip_item(focusitem, dummy, silent=True)
                    # renpy.show_screen("diff_item_effects", eqtarget, dummy)
            elif result[1] == 'unequip':
                python:
                    unequip_slot = result[3]

                    dummy = copy_char(eqtarget)

                    focusitem = result[2]
                    item_direction = 'unequip'

                    if focusitem:
                        # To Calc the effects:
                        dummy.eqslots[unequip_slot] = focusitem
                        dummy.unequip(focusitem, unequip_slot)
                        #renpy.show_screen("diff_item_effects", eqtarget, dummy)
        elif result[0] == "unequip_all":
            python:
                if equipment_access(eqtarget, silent=False):
                    for slot in eqtarget.eqslots:
                        eqtarget.unequip(slot=slot)
                    del slot

                focusitem = None
                focusoutfit = None
                unequip_slot = None
                item_direction = None
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
        elif result[0] == 'con':
            if result[1] == 'return':
                python:
                    focusitem = None
                    focusoutfit = None
                    unequip_slot = None
                    item_direction = None
                    dummy = None
                    eqsave = [False, False, False]
        elif result[0] == 'control':
            if result[1] == 'return':
                jump char_equip_finish
            else:
                python:
                    focusitem = None
                    focusoutfit = None
                    unequip_slot = None
                    item_direction = None
                    dummy = None

                    index = equip_girls.index(eqtarget)
                    if result[1] == 'left':
                        index -= 1
                    elif result[1] == 'right':
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
            renpy.show_screen("message_screen", "{} dies as a result of item manipulations...".format(eqtarget.fullname))
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
    key "mousedown_3" action Return(['control', 'return'])
    key "mousedown_4" action Function(inv_source.inventory.prev)
    key "mousedown_5" action Function(inv_source.inventory.next)
    key "mousedown_6" action Return(['con', 'return'])

    default stats_display = "stats"
    default skill_display = "combat"

    # BASE FRAME 2 "bottom layer" ====================================>
    add "content/gfx/frame/equipment3.webp"

    # Equipment slots:
    frame:
        pos (425, 10)
        xysize 298, 410
        background Frame(Transform("content/gfx/frame/Mc_bg3.png", alpha=.3), 10, 10)
        use eqdoll(active_mode=True, char=eqtarget, frame_size=[70, 70], scr_align=(.98, 1.0), return_value=['item', "unequip"], txt_size=17, fx_size=(455, 400))

    # BASE FRAME 3 "mid layer" ====================================>
    add "content/gfx/frame/equipment1.webp"

    # Item Info (Mid-Bottom Frame): ====================================>
    hbox:
        align (.388, 1.0)
        spacing 1
        style_group "content"

        # Item Description:
        frame:
            xalign .6
            at fade_in_out()
            background Transform(Frame(im.MatrixColor("content/gfx/frame/Mc_bg3.png", im.matrix.brightness(-0.2)), 5, 5), alpha=.3)
            xysize (710, 296)
            use char_equip_item_info(item=focusitem, size=(703, 287))

    #use char_equip_left_frame(stats_display)

#screen char_equip_left_frame(stats_display):
    # Left Frame: =====================================>
    fixed:
        pos (0, 2)
        xysize (220,724)
        style_group "content"

        # PORTRAIT + Prev/Next buttons ================>
        fixed:
            xysize (220, 110)
            if equip_girls:
                imagebutton:
                    xysize (39, 50)
                    pos (13, 14)
                    action Return(['control', 'left'])
                    idle "content/gfx/interface/buttons/small_button_wood_left_idle.png"
                    hover "content/gfx/interface/buttons/small_button_wood_left_hover.png"
                    tooltip "Previous Character"
                    focus_mask True

            $ img = eqtarget.show("portrait", resize=(100, 100), cache=True)
            imagebutton:
                xysize (100, 100)
                pos (64, 8)
                background Null()
                idle img
                hover im.MatrixColor(img, im.matrix.brightness(0.15))
                action Show("show_trait_info", trait=eqtarget)
                focus_mask True

            if equip_girls:
                imagebutton:
                    xysize (39, 50)
                    pos (175, 14)
                    action Return(['control', 'right'])
                    idle "content/gfx/interface/buttons/small_button_wood_right_idle.png"
                    hover "content/gfx/interface/buttons/small_button_wood_right_hover.png"
                    tooltip "Next Character"
                    focus_mask True

        # NAME ========================================>
        text (u"[eqtarget.name]") color "#ecc88a" font "fonts/TisaOTM.otf" size 28 outlines [(1, "#3a3a3a", 0, 0)] xalign .53 ypos 126

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
                        img = ProportionalScale(group_icon, 20, 20)
                    imagebutton:
                        xalign .75#, .5
                        yoffset 4
                        idle img
                        hover im.MatrixColor(img, im.matrix.brightness(0.15))
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
                    spacing 5
                    pos (4, 40)
                    frame:
                        background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.7)
                        xsize 218
                        padding 6, 6
                        margin 0, 0
                        style_group "proper_stats"
                        has vbox spacing 1
                        # STATS ============================>
                        $ stats = ["constitution", "charisma", "intelligence", "joy"] if eqtarget == hero else ["constitution", "charisma", "intelligence", "character", "joy", "disposition", "affection"]

                        # Health:
                        frame:
                            xysize 204, 25
                            text "Health" xalign .02 color "#CD4F39"
                            $ temp, tmp = eqtarget.get_stat("health"), eqtarget.get_max("health")
                            $ tempc = "red" if temp <= tmp*.3 else "#F5F5DC"
                            $ temp = build_str_for_eq(eqtarget, dummy, "health", tempc)
                            text temp style_suffix "value_text" xalign .98 yoffset 3

                        # Vitality:
                        frame:
                            xysize 204, 25
                            text "Vitality" xalign .02 color "#43CD80"
                            $ temp, tmp = eqtarget.get_stat("vitality"), eqtarget.get_max("vitality")
                            $ tempc = "red" if temp <= tmp*.3 else "#F5F5DC"
                            $ temp = build_str_for_eq(eqtarget, dummy, "vitality", tempc)
                            text temp style_suffix "value_text" xalign .98 yoffset 3

                        # Rest of stats:
                        for stat in stats:
                            frame:
                                xysize 204, 25
                                text stat.capitalize() xalign .02 color "#79CDCD"
                                $ temp = build_str_for_eq(eqtarget, dummy, stat, "#F5F5DC")
                                text temp style_suffix "value_text" xalign .98 yoffset 3

                    # BATTLE STATS ============================>
                    frame:
                        background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.7)
                        xsize 218
                        padding 6, 6
                        style_group "proper_stats"
                        has vbox spacing 1

                        label (u"Battle Stats:") text_size 18 text_color "#CDCDC1" text_bold True xalign .49

                        $ stats = [("attack", "#CD4F39"), ("defence", "#dc762c"), ("magic", "#8470FF"), ("mp", "#009ACD"), ("agility", "#1E90FF"), ("luck", "#00FA9A")]
                        null height 1

                        for stat, color in stats:
                            frame:
                                xysize 204, 25
                                text stat.capitalize() color color
                                if stat == "mp":
                                    $ tempc = "red" if eqtarget.get_stat("mp") <= eqtarget.get_max("mp")*.3 else color
                                else:
                                    $ tempc = color
                                $ temp = build_str_for_eq(eqtarget, dummy, stat, tempc)
                                text temp style_suffix "value_text" xalign .98 yoffset 3

            elif stats_display == "skills" and skill_display == "combat":
                vbox:
                    spacing 5
                    pos (4, 40)
                    frame:
                        background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.7)
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
                        background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.7)
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
                        background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.7)
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
                                #$ skill_old = min(skill_limit, int(eqtarget.get_skill(skill)))
                                $ skill_old = int(eqtarget.get_skill(skill))
                                if getattr(store, "dummy", None) is not None:
                                    #$ skill_new = min(skill_limit, int(dummy.get_skill(skill)))
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
                                                background ProportionalScale("content/gfx/interface/icons/stars/legendary.png", 16, 16)
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
                        background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.7)
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
                        background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.7)
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

    use char_equip_right_frame()

screen char_equip_right_frame():
    # Right Frame: =====================================>
    # TOOLTIP TEXT  ====================================>
    frame:
        pos (930, 4)
        background Frame(Transform("content/gfx/frame/ink_box.png", alpha=.4), 10, 10)
        xpadding 10
        xysize (345, 110)

        python:
            classes = list(t.id for t in eqtarget.traits.basetraits)
            classes.sort()
            classes = ", ".join(classes)

            t = "is %s{vspace=17}Classes: %s\nWork: %s\nAction: %s{/color}" % (eqtarget.status.capitalize(), classes, eqtarget.workplace, action_str(eqtarget))

        text (u"{color=gold}[eqtarget.name]{/color}  {color=#ecc88a}%s" % t) size 14 align (.55, .65) font "fonts/TisaOTM.otf" line_leading -5

    # Right Frame Buttons ====================================>
    vbox:
        pos 937, 118
        xsize 345
        style_prefix "pb"
        hbox:
            xalign .5
            spacing 2
            button:
                xsize 110
                action If(eqtarget != hero, true=[SetVariable("inv_source", hero),
                                                  Function(hero.inventory.apply_filter, eqtarget.inventory.slot_filter),
                                                  Return(['con', 'return']),
                                                  With(dissolve)])
                tooltip "Equip from {}'s Inventory".format(hero.nickname)
                selected eqtarget == hero or inv_source == hero
                text "Hero" style "pb_button_text" yoffset 2
            button:
                xsize 110
                action If(eqtarget != hero, true=[SetVariable("inv_source", eqtarget),
                                                  Function(eqtarget.inventory.apply_filter, hero.inventory.slot_filter),
                                                  Return(['con', 'return']),
                                                  With(dissolve)])
                selected inv_source != hero
                sensitive eqtarget != hero
                tooltip "Equip from {}'s Inventory".format(eqtarget.nickname)
                text "Girl" style "pb_button_text" yoffset 2

    # "Final" Filters (id/price/etc.)
    hbox:
        pos 937, 150
        spacing 1
        style_prefix "pb"
        hbox:
            style_prefix "pb"
            button:
                xsize 110
                action Return(["equip_for"])
                text "Equip For" style "pb_button_text" yoffset 2
            button:
                xsize 110
                action Return(["unequip_all"])
                text "Unequip all" style "pb_button_text" yoffset 2
            button:
                xsize 110
                action If(eqtarget != hero, true=Return(["jump", "item_transfer"]))
                text "Exchange" style "pb_button_text" yoffset 2

    # Auto-Equip/Item Transfer Buttons and Paging: ================>
    frame:
        background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.7)
        pos (931, 184)
        xysize (345, 80)
        has vbox spacing 2 xalign .5
        hbox:
            spacing 1
            style_prefix "pb"
            button:
                xsize 110
                action Function(inv_source.inventory.update_sorting, ("id", False))
                text "Name" style "pb_button_text" yoffset 2
                selected inv_source.inventory.final_sort_filter[0] == "id"
                tooltip "Sort items by the Name!"
            button:
                xsize 110
                action Function(inv_source.inventory.update_sorting, ("price", True))
                text "Price" style "pb_button_text" yoffset 2
                selected inv_source.inventory.final_sort_filter[0] == "price"
                tooltip "Sort items by the Price!"
            button:
                xsize 110
                action Function(inv_source.inventory.update_sorting, ("amount", True))
                text "Amount" style "pb_button_text" yoffset 2
                selected inv_source.inventory.final_sort_filter[0] == "amount"
                tooltip "Sort items by the Amount owned!"
        use paging(ref=inv_source.inventory, use_filter=False, xysize=(240, 30), align=(.5, .5))

    # Gender filter
    default item_genders = ["any", "male", "female"]
    default gender_icons = ["content/gfx/interface/icons/both.png",
                            "content/gfx/interface/icons/male.png",
                            "content/gfx/interface/icons/female.png"]
    default gender_tt = ["Items of all genders are shown!",
                         "Items of Male and Unisex genders are shown!",
                         "Items of Female and Unisex genders are shown!"]
    python:
        index = item_genders.index(inv_source.inventory.gender_filter)
        next_gender = item_genders[(index + 1) % len(item_genders)]

    button:
        pos 935, 260 anchor -.1, 1.0
        xysize 40, 40
        style "pb_button"
        add pscale(gender_icons[index], 30, 30) align .5, .5
        action Function(inv_source.inventory.apply_filter,
                        direction=inv_source.inventory.slot_filter,
                        gender=next_gender)
        tooltip gender_tt[index]

    # Filters: ====================================>
    vpgrid:
        pos (935, 268)
        style_group "dropdown_gm"
        xsize 340
        cols 7 rows 2
        spacing 2
        for filter in inv_source.inventory.filters:
            frame:
                padding 0, 0
                margin 1, 1
                background Null()
                if renpy.loadable("content/gfx/interface/buttons/filters/%s.png" % filter):
                    $ img = ProportionalScale("content/gfx/interface/buttons/filters/%s.png" % filter, 44, 44)
                    $ img_hover = ProportionalScale("content/gfx/interface/buttons/filters/%s hover.png" % filter, 44, 44)
                    $ img_selected = ProportionalScale("content/gfx/interface/buttons/filters/%s selected.png" % filter, 44, 44)
                else:
                    $ img = Solid("#FFF", xysize=(44, 44))
                    $ img_hover = Solid("#FFF", xysize=(44, 44))
                    $ img_selected = Solid("#FFF", xysize=(44, 44))
                imagebutton:
                    idle img
                    hover Transform(img_hover, alpha=1.1)
                    selected_idle img_selected
                    selected_hover Transform(img_selected, alpha=1.15)
                    action [Function(inv_source.inventory.apply_filter, filter),
                            SelectedIf(filter == inv_source.inventory.slot_filter)],
                            #SetVariable("last_inv_filter", filter)]
                    focus_mask True
                    tooltip "{}".format(filter.capitalize())

    # Inventory: ====================================>
    frame:
        pos (931, 372)
        background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.7)
        use items_inv(char=inv_source, main_size=(333, 333), frame_size=(80, 80), return_value=['item', 'equip'])

    # BASE FRAME 1 "top layer" ====================================>
    add "content/gfx/frame/h1.webp"

    imagebutton:
        pos (178, 70)
        idle im.Scale("content/gfx/interface/buttons/close2.png", 35, 35)
        hover im.Scale("content/gfx/interface/buttons/close2_h.png", 35, 35)
        action Return(['control', 'return'])
        tooltip "Return to previous screen!"
    key "mousedown_3" action Return(['control', 'return'])

screen char_equip_item_info(item=None, char=None, size=(635, 380), style_group="content", mc_mode=False):

    key "mousedown_3" action Return(['con', 'return'])

    # One of the most difficult code rewrites I've ever done (How Gismo aligned everything in the first place is a work of (weird and clumsy) art...):
    # Recoding this as three vertically aligned HBoxes...
    if item:
        $ xs = size[0]
        $ ys = size[1]
        fixed:
            style_prefix "proper_stats"
            xysize size

            # Top HBox: Discard/Close buttons and the Item ID:
            hbox:
                align .5, .0
                xsize xs-10
                imagebutton:
                    xalign 0
                    idle ("content/gfx/interface/buttons/discard.png")
                    hover ("content/gfx/interface/buttons/discard_h.png")
                    action Return(["item", "discard"])
                    tooltip "Discard item"
                frame:
                    align .5, .5
                    xysize (439, 35)
                    background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.05)), 10, 10), alpha=.9)
                    label ('[item.id]') text_color "gold" align .5, .5 text_size 19 text_outlines [(1, "black", 0, 0)] text_style "interactions_text"
                imagebutton:
                    xalign 1.0
                    idle ("content/gfx/interface/buttons/close3.png")
                    hover ("content/gfx/interface/buttons/close3_h.png")
                    action Return(['con', 'return'])
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
                    background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.05)), 5, 5), alpha=.9)
                    xysize (180, 130)
                    xpadding 0
                    xmargin 0
                    has vbox spacing 1 xoffset 10
                    null height 15
                    frame:
                        xysize (160, 25)
                        text "Price:" color "gold" xalign .02
                        label '{size=-4}{color=gold}[item.price]' align .98, .5 text_outlines [(1, "#3a3a3a", 0, 0)]
                    frame:
                        xysize (160, 25)
                        text "Slot:" color "#F5F5DC" xalign .02
                        $ slot = EQUIP_SLOTS.get(item.slot, item.slot.capitalize())
                        label ('{color=#F5F5DC}{size=-4}%s'%slot) align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                    frame:
                        xysize (160, 25)
                        text "Type:" color "#F5F5DC" xalign .02
                        label ('{color=#F5F5DC}{size=-4}%s'%item.type.capitalize()) align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                    frame:
                        xysize (160, 25)
                        text "Sex:" color "#F5F5DC" xalign .02
                        $ temp = getattr(item, "gender", "unisex")
                        if item.slot in ["gift", "resources", "loot"]:
                            label "{size=-4}N/A" align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                        elif item.type == "food" and temp == "unisex":
                            label "{size=-4}N/A" align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                        else:
                            $ color = "#FFA54F" if temp == "male" else ("#FFAEB9" if temp == "female" else "#F5F5DC")
                            label ('{size=-4}{color=%s}%s'%(color, temp.capitalize())) align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]

                # Buttons and image:
                button:
                    style_group "pb"
                    align (.0, .5)
                    xysize (80, 45)
                    action SensitiveIf(eqtarget != hero and ((eqtarget.inventory[item] > 0 and inv_source == eqtarget) or (hero.inventory[item] > 0 and inv_source == hero))), Return(['item', 'transfer'])
                    if eqtarget == hero:
                        text "Transfer" style "pb_button_text" align (.5, .5)
                    elif inv_source == hero:
                        tooltip "Transfer {} from {} to {}".format(item.id, hero.nickname, eqtarget.nickname)
                        text "Give to\n {color=#FFAEB9}[eqtarget.nickname]{/color}" style "pb_button_text" align (.5, .5) line_leading 3
                    else:
                        text "Give to\n {color=#FFA54F}[hero.nickname]{/color}" style "pb_button_text" align (.5, .5) line_leading 3
                        tooltip "Transfer {} from {} to {}".format(item.id, eqtarget.nickname, hero.nickname)

                frame:
                    align (.5, .5)
                    background Frame("content/gfx/frame/frame_it2.png", 5, 5)
                    xysize (120, 120)
                    $ temp = ProportionalScale(item.icon, 100, 100)
                    imagebutton:
                        align .5, .5
                        idle temp
                        hover im.MatrixColor(temp, im.matrix.brightness(.15))
                        action Show("show_item_info", item=item)

                if item_direction == 'unequip':
                    $ temp = "Unequip"
                    $ temp_msg = "Unequip {}".format(item.id)
                elif item_direction == 'equip':
                    if item.slot == "consumable":
                        $ temp = "Use"
                        $ temp_msg = "Use {}".format(item.id)
                    else:
                        $ temp = "Equip"
                        $ temp_msg = "Equip {}".format(item.id)
                button:
                    style_group "pb"
                    align (1.0, .5)
                    xysize (80, 45)
                    tooltip temp_msg
                    action SensitiveIf(focusitem), Return(['item', 'equip/unequip'])
                    text "[temp]" style "pb_button_text" align (.5, .5):
                        if item_direction == 'equip' and not can_equip(focusitem, eqtarget):
                            color "red" strikethrough True

                # Right items info (Stats):
                frame:
                    xalign .98
                    background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.05)), 5, 5), alpha=.9)
                    xysize (185, 130)
                    style_group "proper_stats"
                    left_padding 6
                    right_padding 3
                    ypadding 5
                    has viewport draggable True mousewheel True child_size 200, 500
                    vbox:
                        if item.mod:
                            label ('Stats:') text_size 14 text_color "gold" xpos 30
                            vbox:
                                spacing 1
                                for stat, value in item.mod.items():
                                    frame:
                                        xysize (172, 18)
                                        text stat.capitalize() color "#F5F5DC" size 15 xalign .02 yoffset -2
                                        label (u'{color=#F5F5DC}{size=-4}[value]') align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                            null height 3

                        if item.max:
                            label ('Max:') text_size 14 text_color "gold" xpos 30
                            vbox:
                                spacing 1
                                for stat, value in item.max.items():
                                    frame:
                                        xysize (172, 18)
                                        text stat.capitalize() color "#F5F5DC" size 15 xalign .02 yoffset -2
                                        label (u'{color=#F5F5DC}{size=-4}[value]') align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
                            null height 3

                        if item.min:
                            label ('Min:') text_size 14 text_color "gold" xpos 30
                            vbox:
                                spacing 1
                                for stat, value in item.min.items():
                                    frame:
                                        xysize (172, 18)
                                        text stat.capitalize() color "#F5F5DC" size 15 xalign .02 yoffset -2
                                        label (u'{color=#F5F5DC}{size=-4}%d'%value) align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]

            # Bottom HBox: Desc/Traits/Effects/Skills:
            hbox:
                yalign 1.0
                # Traits, Effects:
                frame:
                    background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.05)), 5, 5), alpha=.9)
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
                    background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.1)), 5, 5), alpha=.9)
                    has viewport draggable True mousewheel True
                    text '{color=#ecc88a}[item.desc]{/color}' font "fonts/TisaOTM.otf" size 15 outlines [(1, "#3a3a3a", 0, 0)]


                frame:
                    background Transform(Frame(im.MatrixColor("content/gfx/frame/p_frame5.png", im.matrix.brightness(-0.05)), 5, 5), alpha=.9)
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
                                imagebutton:
                                    align (.0, .0)
                                    idle im.Scale("content/gfx/interface/buttons/edit.png", 16, 20)
                                    hover im.Scale("content/gfx/interface/buttons/edit_h.png", 16, 20)
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
                                use eqdoll(active_mode=True, char=v, scr_align=(.98, 1.0), return_value=['item', "save"], txt_size=17, fx_size=(304, 266))

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

# TODO keep in sync or even merge with show_trait_info
screen show_item_info(item=None):
    #modal True
    $ pos = renpy.get_mouse_pos()
    mousearea:
        area(pos[0], pos[1], 1, 1)
        hovered Show("show_item_info_content", transition=None, item=item)
        unhovered Hide("show_item_info_content"), Hide("show_item_info")

    #key "mousedown_3" action Hide("show_trait_info_content"), Hide("show_trait_info")

screen show_item_info_content(item):
    default pos = renpy.get_mouse_pos()
    python:
        x, y = pos
        if x > config.screen_width/2:
            x -= 20
            xval = 1.0
        else:
            x += 20
            xval = .0
        temp = config.screen_height/3
        if y < temp:
            yval = .0
        elif y > config.screen_height-temp:
            yval = 1.0
        else:
            yval = .5

    fixed:
        pos x, y
        anchor xval, yval
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
                                if item.mtemp > 1:
                                    text (u'Every %d days'%item.mtemp) color "#F5F5DC" size 15 xalign .02
                                else:
                                    text (u'Every day') color "#F5F5DC" size 15 xalign .02 yoffset -2
                            else:
                                if item.mtemp > 1:
                                    text (u'After %d days'%item.mtemp) color "#F5F5DC" size 15 xalign .02
                                else:
                                    text (u'After one day') color "#F5F5DC" size 15 xalign .02
                        if getattr(item, 'mdestruct', False):
                                text (u'Disposable') color "#F5F5DC" size 15 xalign 1.0
                        if getattr(item, 'mreusable', False):
                                text (u'Reusable') color "#F5F5DC" size 15 xalign 1.0
                    if getattr(item, 'statmax', False):
                        frame:
                            xysize (200, 20)
                            text (u'Stat limit') color "#F5F5DC" size 15 xalign .02
                            label (u'{color=#F5F5DC}{size=-4}%d'%item.statmax) align (.98, .5) text_outlines [(1, "#3a3a3a", 0, 0)]
            if getattr(item, 'ctemp', False):
                label (u"Duration:") text_size 14 text_color "gold" xpos 30
                frame:
                    xysize (172, 18)
                    if item.ctemp > 1:
                        text (u'%d days'%item.ctemp) color "#F5F5DC" size 15 xalign .02
                    else:
                        text (u'One day') color "#F5F5DC" size 15 xalign .02 yoffset -2

            $ temp = [t.id for t in item.addtraits if not t.hidden]
            $ tmp = [t.id for t in item.removetraits if not t.hidden]
            if temp or tmp:
                $ any_mod = True
                label (u"Traits:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for trait in temp:
                    frame:
                        xysize 200, 20
                        text trait.title() size 15 color "lime" align .5, .5 text_align .5 outlines [(1, "black", 0, 0)]
                for trait in tmp:
                    frame:
                        xysize 200, 20
                        text trait.title() size 15 color "red" align .5, .5 text_align .5 outlines [(1, "black", 0, 0)]

            if item.addeffects or item.removeeffects:
                $ any_mod = True
                label (u"Effects:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for effect in item.addeffects:
                    frame:
                        xysize 200, 20
                        text effect.title() size 15 color "lime" align .5, .5 text_align .5 outlines [(1, "black", 0, 0)]
                for effect in item.removeeffects:
                    frame:
                        xysize 200, 20
                        text effect.title() size 15 color "red" align .5, .5 text_align .5 outlines [(1, "black", 0, 0)]

            if item.mod_skills or item.add_be_spells or item.attacks:
                $ any_mod = True
                label (u"Skills:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                for skill, data in item.mod_skills.iteritems():
                    frame:
                        xysize 200, 20
                        text skill.title() size 15 color "yellowgreen" align .0, .5 outlines [(1, "black", 0, 0)]

                        $ img_path = "content/gfx/interface/icons/skills_icons/"
                        default PS = ProportionalScale
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
                            label temp text_size 15 align 1.0, .5 text_outlines [(1, "black", 0, 0)]

                if item.add_be_spells:
                    for skill in item.add_be_spells:
                        frame:
                            xysize 200, 20
                            text skill.name size 15 color "yellow" align .5, .5 outlines [(1, "black", 0, 0)]
                if item.attacks:
                    for skill in item.attacks:
                        frame:
                            xysize 200, 20
                            text skill.name size 15 color "yellow" align .5, .5 outlines [(1, "black", 0, 0)]

            $ bem = modifiers_calculator(item)
            if any((bem.elemental_modifier, bem.defence_modifier, bem.evasion_bonus, bem.delivery_modifier, bem.damage_multiplier, bem.ch_multiplier)):
                $ any_mod = True
                use list_be_modifiers(bem)

            if item.be:
                $ any_mod = True
                label (u"Other:") text_size 20 text_color "goldenrod" text_bold True xalign .45
                frame:
                    xysize 200, 20
                    text "Can be used in combat!" align .5, .5 size 15 color "yellowgreen" text_align .5 outlines [(1, "black", 0, 0)]

            if not any_mod:
                label ("- no direct effects -") text_size 15 text_color "goldenrod" text_bold True xalign .45 text_outlines [(1, "black", 0, 0)]

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
