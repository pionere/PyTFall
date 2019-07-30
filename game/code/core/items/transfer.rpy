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

screen items_transfer(it_members):
    on "show":
        action Function(it_on_show, it_members)

    default lc = it_members[0]
    default rc = it_members[1]
    default selection = [None, set()]
    default transfer_amount = 1

    add "bg gallery"

    # Title + Exit
    frame:
        background Frame(im.Alpha("content/gfx/frame/Namebox.png", alpha=.9), 10, 10)
        style_group "proper_stats"
        xalign .5
        xysize 320, 30
        text "Transfer Items between Characters!" size 20 align .5, .5 style "content_text" color "ivory" yoffset 3

    fixed:
        align (1.0, 1.0)
        xysize 35, 35
        use exit_button(size=(30, 30), align=(.5, .5))

    # Members + Inventory Pager + Items
    for scr_var, fc, xalign in [("lc", lc, .0), ("rc", rc, 1.0)]:
        vbox:
            spacing -4
            xalign xalign
            frame:
                background Frame("content/gfx/frame/p_frame5.png", 10, 10)
                padding 5, 5
                has vpgrid cols 2 draggable True mousewheel True xysize 331, 300 child_size 330, 10000
                for c in it_members:
                    $ img = c.show("portrait", resize=(80, 80), cache=True)
                    frame:
                        #xpos 1
                        background Frame("content/gfx/frame/p_frame5.png", 4, 4)
                        xysize (165, 120)
                        has vbox spacing 0
                        frame:
                            xalign .5
                            background Frame("content/gfx/frame/Mc_bg3.png", 5, 5)
                            xysize (153, 22)
                            xoffset -2
                            $ font_size = PyTGFX.txt_font_size(c.name, 150, 20, 10)
                            text "[c.name]":
                                style "interactions_text"
                                color ("#FF2500" if c == fc else "gold")
                                size font_size
                                outlines [(1, "#3a3a3a", 0, 0)]
                                align .5, .5
                                layout "nobreak"
                        fixed:
                            xysize (156, 90)
                            imagebutton:
                                align .5, .5
                                style "basic_choice2_button"
                                idle img
                                hover img
                                selected_idle Transform(img, alpha=1.05)
                                action SetScreenVariable(scr_var, c), SelectedIf(c == fc), SensitiveIf(c != (rc if fc == lc else lc))

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

            hbox:
                xysize 341, 40
                yoffset -5
                use paging(bgr="content/gfx/frame/p_frame5.png", xysize=(240, 40), ref=fc.inventory, use_filter=False, align=(.5, .5))

    # Portraits + Info:
    for fc, pos, xanchor in [(lc, (350, 40), 0), (rc, (930, 40), 1.0)]:
        fixed:
            xysize 150, 150
            pos pos
            xanchor xanchor
            # Employment info:
            if isinstance(fc, Char):
                frame:
                    xanchor xanchor
                    xpos (150 * (1 if xanchor == 0 else 0))
                    yalign xanchor
                    background Frame("content/gfx/frame/p_frame5.png", 5, 5)
                    padding 9, 7
                    vbox:
                        text fc.name style "content_text" color "gold" size 20 layout "nobreak" xalign .5
                        $ traits = fc.traits.base_to_string
                        $ action = action_str(fc)
                        text ("%s ---- %s"%(traits, action)) style "content_text" color "ivory" size 18 layout "nobreak" xalign .5

            frame:
                background Frame("content/gfx/frame/Mc_bg3.png", 10, 10)
                align .5, .5
                padding 1, 1
                $ img = fc.show("portrait", resize=(150, 150), cache=True)
                add img

    $ items = selection[1]
    if items:
        # Selected Item(s):
        frame:
            ypos 190
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

        # Amount Buttons:
        fixed:
            xalign .5
            ypos 580
            frame:
                xalign .5
                xysize 200, 53
                background Frame("content/gfx/frame/BG_choicebuttons.png", 10, 10)
                hbox:
                    xfill True
                    hbox:
                        align .0, .6
                        $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_left.png", 30, 30)
                        imagebutton:
                            align (.0, .5)
                            idle img
                            hover PyTGFX.bright_img(img, .15)
                            action SetScreenVariable("transfer_amount", max(1, transfer_amount - 10))
                        $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_left.png", 25, 25)
                        imagebutton:
                            align (.5, .5)
                            idle img
                            hover PyTGFX.bright_img(img, .15)
                            action SetScreenVariable("transfer_amount", max(1, transfer_amount - 5))
                        $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_left.png", 20, 20)
                        imagebutton:
                            align (1.0, .5)
                            idle img
                            hover PyTGFX.bright_img(img, .15)
                            action SetScreenVariable("transfer_amount", max(1, transfer_amount - 1))
                    vbox:
                        xalign .5
                        spacing -4
                        yoffset -9
                        text 'Amount:' style "proper_stats_label_text" align .5, .5 size 18
                        text '[transfer_amount]' style "proper_stats_text" align .5, .5 size 18

                    hbox:
                        align 1.0, .6
                        $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_right.png", 20, 20)
                        imagebutton:
                            align (.0, .5)
                            idle img
                            hover PyTGFX.bright_img(img, .15)
                            action SetScreenVariable("transfer_amount", transfer_amount + 1)
                        $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_right.png", 25, 25)
                        imagebutton:
                            align (.5, .5)
                            idle img
                            hover PyTGFX.bright_img(img, .15)
                            action SetScreenVariable("transfer_amount", transfer_amount + 5)
                        $ img = PyTGFX.scale_img("content/gfx/interface/buttons/blue_arrow_right.png", 30, 30)
                        imagebutton:
                            align (1.0, .5)
                            idle img
                            hover PyTGFX.bright_img(img, .15)
                            action SetScreenVariable("transfer_amount", transfer_amount + 10)

        # Transfer Buttons:
        if len(items) == 1:
            $ temp = "Transfer %d %s from %s to %s!" % (transfer_amount, iter(items).next().id, rc.name, lc.name)
            $ tmp = "Transfer %d %s from %s to %s!" % (transfer_amount, iter(items).next().id, lc.name, rc.name)
        elif transfer_amount == 1:
            $ temp = "Transfer the selected items from %s to %s!" % (rc.name, lc.name)
            $ tmp = "Transfer the selected items from %s to %s!" % (lc.name, rc.name)
        else:
            $ temp = "Transfer the selected items (%d each) from %s to %s!" % (transfer_amount, rc.name, lc.name)
            $ tmp = "Transfer the selected items (%d each) from %s to %s!" % (transfer_amount, lc.name, rc.name)
        $ img = PyTGFX.scale_img("content/gfx/interface/buttons/left0.png", 60, 60)
        imagebutton:
            pos (860, 596)
            idle img
            hover PyTGFX.bright_img(img, .15)
            insensitive PyTGFX.sepia_img(img)
            sensitive (items and lc and rc)
            action Return(["transfer", rc, lc, items, transfer_amount])
            tooltip temp

        $ img = PyTGFX.scale_img("content/gfx/interface/buttons/right0.png", 60, 60)
        imagebutton:
            pos (360, 596)
            idle img
            hover PyTGFX.bright_img(img, .15)
            insensitive PyTGFX.sepia_img(img)
            sensitive (items and lc and rc)
            action Return(["transfer", lc, rc, items, transfer_amount])
            tooltip tmp

    python:
        rc_inv, lc_inv = rc.inventory, lc.inventory
        inv_filter = rc_inv.slot_filter
        if inv_filter != lc_inv.slot_filter:
            inv_filter = None
        inv_sort = rc_inv.final_sort_filter[0]
        if inv_sort != lc_inv.final_sort_filter[0]:
            inv_sort = None
    # Sorting Buttons:
    frame:
        background Frame(im.Alpha(PyTGFX.bright_img("content/gfx/frame/p_frame5.png", -0.1), alpha=.7), 5, 5)
        xalign .5
        ypos config.screen_height - 82
        xysize (345, 40)
        hbox:
            spacing 1
            style_prefix "pb"
            button:
                xsize 110
                action Function(rc_inv.update_sorting, ("id", False)), Function(lc_inv.update_sorting, ("id", False))
                text "Name" style "pb_button_text" yoffset 1
                selected inv_sort == "id"
                tooltip "Sort items by the Name!"
            button:
                xsize 110
                action Function(rc_inv.update_sorting, ("price", True)), Function(lc_inv.update_sorting, ("price", True))
                text "Price" style "pb_button_text" yoffset 1
                selected inv_sort == "price"
                tooltip "Sort items by the Price!"
            button:
                xsize 110
                action Function(rc_inv.update_sorting, ("amount", True)), Function(lc_inv.update_sorting, ("amount", True))
                text "Amount" style "pb_button_text" yoffset 1
                selected inv_sort == "amount"
                tooltip "Sort items by the Amount owned!"

    # Filters Buttons:
    frame:
        style_group "dropdown_gm"
        background Frame("content/gfx/frame/Mc_bg3.png", 10, 10)
        padding 3, 3
        align .5, 1.0
        has hbox spacing 1

        for filter in list(sorted(set(rc_inv.filters + lc_inv.filters))):
            $ img = PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s.png" % filter, 40, 40)
            $ img_hover = PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s hover.png" % filter, 40, 40)
            $ img_selected = PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s selected.png" % filter, 40, 40)
            imagebutton:
                idle img
                hover img_hover
                selected_idle img_selected
                selected_hover PyTGFX.bright_img(img_selected, .10)
                action Function(rc_inv.apply_filter, filter), Function(lc_inv.apply_filter, filter)
                selected filter == inv_filter
