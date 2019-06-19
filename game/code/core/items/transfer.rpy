init python:
    def items_transfer(it_members):
        store._skipping = False
        renpy.show_screen("items_transfer", it_members)
        while 1:
            result = ui.interact()
            if isinstance(result, (list, tuple)):
                if result[0] == "control":
                    break
                elif result[0] == "transfer":
                    source, target, items, amount = result[1:]
                    for item in items:
                        for i in xrange(amount):
                            if not transfer_items(source, target, item):
                                break
        renpy.hide_screen("items_transfer")
        store._skipping = True

    def it_on_show(it_members):
        for c in it_members:
            c.inventory.set_page_size(14)

    def it_item_click(selection, source, item):
        selected_items = selection[1]
        selected_source = selection[0]
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]:
            #if selected_source == source:
                if item in selected_items:
                    selected_items.remove(item)
                else:
                    selected_items.add(item)
        elif pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]:
            if selected_source == source:
                if item in selected_items:
                    selected_items.remove(item)
                else:
                    front_idx = tail_idx = item_idx = -1
                    for idx, it in enumerate(source.inventory.page_content):
                        if it == item:
                            item_idx = idx
                        elif it in selected_items:
                            if item_idx == -1:
                                front_idx = idx
                            else:
                                tail_idx = idx
                                break
                    if item_idx == -1:
                        selected_items.add(item)
                    else:
                        if front_idx != -1:
                            selected_items.update([it for it in source.inventory.page_content][front_idx:item_idx+1])
                        elif tail_idx != -1:
                            selected_items.update([it for it in source.inventory.page_content][item_idx:tail_idx+1])
                        else:
                            selected_items.add(item)
            else:
                if item in selected_items:
                    selected_items.remove(item)
                else:
                    selected_items.add(item)
        else:
            if item in selected_items and len(selected_items) == 1 and source == selection[0]:
                selected_items.remove(item)
            else:
                if source is not None:
                    selection[0] = source
                selection[1] = set([item])

screen t_lightbutton(img, size, action, align, sensitive=True, tooltip=None):
    $ img = ProportionalScale(img, *size, align=(.5, .5))
    button:
        xysize 40, 30
        align align
        idle_background img
        hover_background im.MatrixColor(img, im.matrix.brightness(.15), align=(.5, .5))
        insensitive_background im.Sepia(img, align=(.5, .5))
        sensitive sensitive
        action action
        tooltip tooltip
        focus_mask True

screen items_transfer(it_members):
    on "show":
        action Function(it_on_show, it_members)

    default lc = it_members[0]
    default rc = it_members[1]
    default selection = [None, set()]
    default transfer_amount = 1
    default slot_filter = it_members[0].inventory.slot_filter

    add "bg gallery"

    frame:
        background Frame(Transform("content/gfx/frame/Namebox.png", alpha=.9), 10, 10)
        style_group "proper_stats"
        xalign .5
        ypos 42
        xysize 320, 30
        text "Transfer Items between Characters!" size 20 align .5, .5 style "content_text" color "ivory" yoffset 3

    # Left/Right employment info:
    frame:
        background Frame("content/gfx/frame/p_frame5.png", 10, 10)
        style_group "dropdown_gm"
        xysize (1280, 45)
        if isinstance(lc, Char):
            $ traits = lc.traits.base_to_string
            $ action = action_str(lc)
            text ("%s ---- %s"%(traits, action)) align (.09, .5) style "content_text" color "ivory" size 20
        if isinstance(rc, Char):
            $ traits = rc.traits.base_to_string
            $ action = action_str(rc)
            text ("%s ---- %s"%(traits, action)) align (.92, .5) style "content_text" color "ivory" size 20

        use exit_button(size=(35, 35), align=(1.0, .6))

    # inventory pagers
    fixed:
        ypos 673
        xalign .5
        xysize (610, 50)
        hbox:
            xfill True
            use paging(bgr="content/gfx/frame/p_frame5.png", xysize=(190, 50), ref=lc.inventory, use_filter=False, align=(.0, .5))
            use paging(bgr="content/gfx/frame/p_frame5.png", xysize=(190, 50), ref=rc.inventory, use_filter=False, align=(1.0, .5))

    # Members + Items
    for scr_var, fc, xalign in [("lc", lc, .0), ("rc", rc, 1.0)]: # Focused characters...
        vbox:
            ypos 41
            spacing -4
            xalign xalign
            frame:
                background Frame("content/gfx/frame/p_frame5.png", 10, 10)
                padding 5, 5
                has viewport draggable True mousewheel True xysize 331, 300 child_size 330, 10000
                hbox:
                    spacing 1
                    box_wrap True
                    for c in it_members:
                        $ img = c.show("portrait", resize=(70, 70), cache=True)
                        vbox:
                            spacing 1
                            frame:
                                xpos 4
                                background Frame("content/gfx/frame/p_frame5.png", 10, 10)
                                xysize (162, 120)
                                imagebutton:
                                    align .5, .93
                                    style "basic_choice2_button"
                                    idle img
                                    hover img
                                    selected_idle Transform(img, alpha=1.05)
                                    action SetScreenVariable(scr_var, c), SelectedIf(c == fc), SensitiveIf(c != (rc if fc == lc else lc))
                                frame:
                                    xalign .5
                                    background Frame("content/gfx/frame/Mc_bg3.png", 5, 5)
                                    xysize(150, 22)
                                    ypadding 0
                                    text "[c.name]" style "interactions_text" color "gold" selected_color "red" size (14 if len(c.name) > 10 else 20) outlines [(1, "#3a3a3a", 0, 0)] align .5, .5

            frame:
                background Frame("content/gfx/frame/p_frame5.png", 10, 10)
                style_group "dropdown_gm2"
                xysize 341, 380
                has vbox
                for item, amount in [(item, fc.inventory[item]) for item in fc.inventory.page_content]:
                    button:
                        xalign .5
                        xysize (328, 26)
                        action SensitiveIf(amount), Function(it_item_click, selection, fc, item)
                        selected fc == selection[0] and item in selection[1]
                        text "[item.id]" align .0, .5 style "dropdown_gm2_button_text"
                        text "[amount]" align 1.0, .7 style "dropdown_gm2_button_value_text"

    # Filters Buttons:
    frame:
        style_group "dropdown_gm"
        background Frame("content/gfx/frame/Mc_bg3.png", 10, 10)
        ypos 80
        padding 3, 3
        xalign .5
        has hbox spacing 1

        for filter in list(sorted(set(rc.inventory.filters + lc.inventory.filters))):
            $ img = PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s.png" % filter, 40, 40)
            $ img_hover = PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s hover.png" % filter, 40, 40)
            $ img_selected = PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s selected.png" % filter, 40, 40)
            imagebutton:
                idle img
                hover img_hover
                selected_idle img_selected
                selected_hover PyTGFX.bright_img(img_selected, .10)
                action SetScreenVariable("slot_filter", filter), Function(rc.inventory.apply_filter, filter), Function(lc.inventory.apply_filter, filter)
                selected filter == slot_filter
                focus_mask True

    # RC and LC Portraits:
    for fc, pos, xanchor in [(lc, (350, 130), 0), (rc, (930, 130), 1.0)]:
        frame:
            pos pos
            xanchor xanchor
            background Frame("content/gfx/frame/Mc_bg3.png", 10, 10)
            padding 1, 1
            $ img = fc.show("portrait", resize=(150, 150), cache=True)
            imagebutton:
                idle img
                hover PyTGFX.bright_content(img, .15)
                align .5, .5
                tooltip fc.name
                action NullAction()

    $ items = selection[1]
    if items:
        # Transfer Buttons:
        vbox:
            xalign .5
            ypos 160
            #style_group "dropdown_gm"
            frame:
                xalign .5
                xysize 200, 90
                background Frame("content/gfx/frame/BG_choicebuttons.png", 10, 10)
                has vbox
                hbox:
                    xfill True
                    if len(items) == 1:
                        $ temp = "Transfer %d %s from %s to %s!" % (transfer_amount, iter(items).next().id, rc.name, lc.name)
                        $ tmp = "Transfer %d %s from %s to %s!" % (transfer_amount, iter(items).next().id, lc.name, rc.name)
                    elif transfer_amount == 1:
                        $ temp = "Transfer the selected items from %s to %s!" % (rc.name, lc.name)
                        $ tmp = "Transfer the selected items from %s to %s!" % (lc.name, rc.name)
                    else:
                        $ temp = "Transfer the selected items (%d each) from %s to %s!" % (transfer_amount, rc.name, lc.name)
                        $ tmp = "Transfer the selected items (%d each) from %s to %s!" % (transfer_amount, lc.name, rc.name)

                    use t_lightbutton(img='content/gfx/interface/buttons/left.png', size=(25,25), action=Return(["transfer", rc, lc, items, transfer_amount]), align=(0.15, .5),
                                      sensitive=(items and lc and rc), tooltip=temp)

                    use t_lightbutton(img='content/gfx/interface/buttons/right.png', size=(25,25), action=Return(["transfer", lc, rc, items, transfer_amount]), align=(0.85, .5),
                                      sensitive=(items and lc and rc), tooltip=tmp)

                hbox:
                    xfill True
                    xoffset -8
                    spacing -10
                    hbox:
                        align .0, .8
                        spacing -22
                        use t_lightbutton(img='content/gfx/interface/buttons/blue_arrow_left.png', size=(30,30), action=SetScreenVariable("transfer_amount", max(1, transfer_amount - 10)), align=(.0, .5))
                        use t_lightbutton(img='content/gfx/interface/buttons/blue_arrow_left.png', size=(25,25), action=SetScreenVariable("transfer_amount", max(1, transfer_amount - 5)), align=(.5, .5))
                        use t_lightbutton(img='content/gfx/interface/buttons/blue_arrow_left.png', size=(20,20), action=SetScreenVariable("transfer_amount", max(1, transfer_amount - 1)), align=(1, .5))
        
                    vbox:
                        xalign .5
                        spacing -4
                        text 'Amount:' style "proper_stats_label_text" align .5, .5 size 18
                        text '[transfer_amount]' style "proper_stats_text" align .5, .5 size 18

                    hbox:
                        align 1.0, .8
                        spacing -22
                        use t_lightbutton(img='content/gfx/interface/buttons/blue_arrow_right.png', size=(20,20), action=SetScreenVariable("transfer_amount", transfer_amount + 1), align=(.0, .5))
                        use t_lightbutton(img='content/gfx/interface/buttons/blue_arrow_right.png', size=(25,25), action=SetScreenVariable("transfer_amount", transfer_amount + 5), align=(.5, .5))
                        use t_lightbutton(img='content/gfx/interface/buttons/blue_arrow_right.png', size=(30,30), action=SetScreenVariable("transfer_amount", transfer_amount + 10), align=(1.0, .5))

        # Selected Item(s):
        frame:
            ypos 280
            xalign .5
            background Frame("content/gfx/frame/frame_dec_1.png", 10, 10)
            padding 30, 34
            if len(items) == 1:
                use itemstats(item=iter(items).next(), size=(540, 300))
            else:
                vpgrid:
                    cols 6
                    draggable True
                    mousewheel True
                    xysize(540, 300)
                    #yminimum 330
                    spacing 12
                    #scrollbars 'vertical' 

                    $ fc = selection[0]
                    for item in items:
                        frame:
                            background Frame("content/gfx/frame/frame_it2.png", 5, 5)
                            xysize (80, 80)
                            $ img = PyTGFX.scale_content(item.icon, 60, 60)
                            imagebutton:
                                align (.4, .5)
                                idle img
                                hover PyTGFX.bright_content(img, .10)
                                action Function(it_item_click, selection, None, item)
                                tooltip item.id
                            $ amount = fc.inventory[item] if (fc and fc.inventory) else 0 
                            text "[amount]" align 1.0, 1.0 style "dropdown_gm2_button_value_text"
