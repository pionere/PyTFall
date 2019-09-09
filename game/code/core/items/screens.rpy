screen items_inv(inv=None, main_size=(553, 282), frame_size=(90, 90), return_value=['item', 'get']):
    frame:
        background Null()
        xysize main_size
        has hbox box_wrap True
        for item in inv.page_content:
            frame:
                xysize frame_size
                background Frame("content/gfx/frame/frame_it2.png", -1, -1)
                $ img = PyTGFX.scale_content(item.icon, 70, 70)
                imagebutton:
                    align (.5, .5)
                    idle img
                    hover PyTGFX.bright_content(img, .15)
                    action Return(return_value+[item])

                label (u"{color=#ecc88a}%d" % inv[item]):
                    align (.995, .995)
                    style "stats_label_text"
                    text_size 18
                    text_outlines [(2, "#9c8975", 0, 0), (1, "black", 0, 0)]

screen eqdoll(source, outfit, fx_size, scr_align, frame_size, return_value):
    # source = source of equipment slots (char or outfit)
    # Doll if the source is a char ------------------------------------->
    if not outfit:
        add (source.show("vnsprite", resize=(288, 400), cache=True)) alpha .9 align (.5, 1.0)

    # Slots ------------------------------------------------------------>
    fixed:
        style_group "content"
        align scr_align
        xysize fx_size

        default equipSlotsPositions = {"head": (.2, .1),
                                       "body": (.2, .3),
                                       "amulet": (1.0, .3),
                                       "cape": (1.0, .1),
                                       "weapon": (.2, .5),
                                       "smallweapon": (1.0, .5),
                                       "feet": (1.0, .7),
                                       "misc": (.025, .41),
                                       "wrist": (.2, .7),
                                       "ring": (1.18, .2),
                                       "ring1": (1.18, .4),
                                       "ring2": (1.18, .6)}
        $ slots = source if outfit else source.eqslots
        for slot, pos in equipSlotsPositions.items():
            python:
                equipment = slots[slot]

                bg = "content/gfx/frame/frame_it2.png"
                if equipment:
                    # Frame background:
                    img = equipment.icon
                    equipment = [equipment, slot]
                else:
                    bg = im.Twocolor(bg, "grey", "black")
                    key = "ring" if slot.startswith("ring") else slot
            frame:
                background im.Scale(bg, *frame_size)
                pos (pos[0] + (0 if not outfit or pos[0] < .5 else -0.619), pos[1])
                xysize frame_size
                if equipment:
                    if not outfit:
                        $ img = PyTGFX.scale_content(img, frame_size[0]*.78, frame_size[1]*.78)
                        imagebutton:
                            align (.5, .5)
                            idle img
                            hover PyTGFX.bright_content(img, .15)
                            action Return(return_value+equipment)
                    else:
                        add PyTGFX.scale_content(img, frame_size[0]*.71, frame_size[1]*.71) align (.5, .5)
                else:
                    add im.Alpha(PyTGFX.scale_img("content/gfx/interface/buttons/filters/%s_bg.png"%key, frame_size[0]*.71, frame_size[1]*.71), alpha=.35) align (.5, .5)

screen shopping(left_ref=None, right_ref=None):
    use shop_inventory(ref=left_ref, x=.0)
    use shop_inventory(ref=right_ref, x=1.0)

    if focus:
        vbox:
            align .5, .5
            frame:
                background Frame("content/gfx/frame/frame_dec_1.png", 30, 30)
                xalign .5
                padding 30, 30
                use itemstats(item=focus, size=(580, 350))

            null height 3

            frame:
                background Frame("content/gfx/frame/p_frame5.png", 10, 10)
                xalign .5
                padding 10, 10

                has vbox ysize 100

                frame:
                    xalign .5
                    style_prefix "proper_stats"
                    $ total_price = item_price * amount
                    padding 3, 3
                    fixed:
                        xysize 250, 25
                        label "Retail Price:" text_color "gold" text_size 22 xalign .0 yalign .5
                        label "[total_price]" text_color "gold" text_size 22 xalign 1.0 yalign .5

                fixed:
                    xsize 180
                    xalign .5
                    # left arrows
                    $ img = PyTGFX.scale_img('content/gfx/interface/buttons/blue_arrow_left.png', 25, 25)
                    imagebutton:
                        align (0, .5)
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Return(['control', -10])
                    $ img = PyTGFX.scale_img('content/gfx/interface/buttons/blue_arrow_left.png', 30, 30)
                    imagebutton:
                        align (.1, .5)
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Return(['control', -5])
                    $ img = PyTGFX.scale_img('content/gfx/interface/buttons/blue_arrow_left.png', 40, 40)
                    imagebutton:
                        align (.25, .5)
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Return(['control', -1])
                    text str(amount) align .5, .5 color "ivory" style "proper_stats_label_text" size 36
                    # right arrows
                    $ img = PyTGFX.scale_img('content/gfx/interface/buttons/blue_arrow_right.png', 40, 40)
                    imagebutton:
                        align (.75, .5)
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Return(['control', 1])
                    $ img = PyTGFX.scale_img('content/gfx/interface/buttons/blue_arrow_right.png', 30, 30)
                    imagebutton:
                        align (.9, .5)
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Return(['control', 5])
                    $ img = PyTGFX.scale_img('content/gfx/interface/buttons/blue_arrow_right.png', 25, 25)
                    imagebutton:
                        align (1.0, .5)
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Return(['control', 10])

                button:
                    style_prefix "basic"
                    action Return(['item', 'buy/sell'])
                    xsize 100
                    xalign .5
                    if purchasing_dir == "buy":
                        text "Buy"
                    elif purchasing_dir == "sell":
                        text "Sell"

    fixed:
        xoffset -281
        use exit_button

screen itemstats(item=None, size=(635, 380), style_group="content", mc_mode=False):
    if item:
        vbox:
            xysize size
            align .5, .5
            frame:
                xalign .5
                xysize (440, 40)
                background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                label '[item.id]' text_color "gold" xalign .5 text_size 20 text_outlines [(1, "black", 0, 0)] text_style "interactions_text"

            vbox:
                align .5, .5
                label ('{color=#ecc88a}----------------------------------------') xalign .5
                hbox:
                    xalign .5
                    xfill True
                    frame:
                        xalign .0
                        yalign .5
                        background Frame("content/gfx/frame/frame_it2.png", 5, 5)
                        xysize (130, 130)
                        $ temp = PyTGFX.scale_content(item.icon, 110, 110)
                        imagebutton:
                            align .5, .5
                            idle temp
                            hover PyTGFX.bright_content(temp, .15)
                            action Show("popup_info", content="item_info_content", param=item)
                    frame:
                        background Frame("content/gfx/frame/p_frame4.png", 10, 10)
                        padding 15, 15
                        align .5, .5
                        style_prefix "proper_stats"
                        has vbox spacing 1
                        frame:
                            xysize 195, 22
                            padding 4, 1
                            text ('Price:') color "gold" xalign .0 yoffset -1
                            label ('[item.price]') xalign 1.0 text_size 18 text_color "gold" yoffset -2
                        frame:
                            xysize 195, 22
                            padding 4, 1
                            text ('Slot:') color "ivory" xalign .0 yoffset -1
                            $ slot = EQUIP_SLOTS.get(item.slot, item.slot.capitalize())
                            label ('{size=-3}[slot]') align 1.0, .5
                        frame:
                            xysize 195, 22
                            padding 4, 1
                            text ('Type:') color "ivory" yalign .5
                            label ('{size=-3}%s'%item.type.capitalize()) xalign 1.0 text_size 18 yoffset -2
                        frame:
                            xysize 195, 22
                            padding 4, 1
                            text ('Sex:') color "ivory" xalign .0 yoffset -1
                            $ temp = getattr(item, "gender", "unisex")
                            if item.slot in ("gift", "resources", "loot"):
                                label "N/A" xalign 1.0 text_size 18 yoffset -2
                            elif item.type == "food" and temp == 'unisex':
                                label "N/A" xalign 1.0 text_size 18 yoffset -2
                            elif temp in ("female", "male"):
                                label temp.capitalize() xalign 1.0 text_size 18 yoffset -2 text_color ("#FFA54F" if temp == "male" else "#FFAEB9")
                            else:
                                label temp.capitalize() xalign 1.0 text_size 18 yoffset -2
                    frame:
                        xalign 1.0
                        xysize (165, 130)
                        background Frame("content/gfx/frame/p_frame7.webp", 5, 5)
                        has viewport mousewheel True draggable True style_group "proper_stats" xysize (165, 122) child_size 160, 500
                        vbox:
                            spacing 1
                            if item.mod:
                                label ('Stats:') text_size 16 text_color "gold" xpos 10
                                for stat, value in item.mod.items():
                                    frame:
                                        xysize 153, 20
                                        text stat.capitalize() color "ivory" size 16 align (.02, .5)
                                        label (u'{size=-4}[value]') align (.98, .5)
                                null height 2
                            if item.max:
                                label ('Max:') text_size 16 text_color "gold" xpos 10
                                for stat, value in item.max.items():
                                    frame:
                                        xysize 153, 20
                                        text stat.capitalize() color "ivory" size 16 align (.02, .5)
                                        label u'{size=-4}[value]' align (.98, .5)
                                null height 2
                            if item.min:
                                label ('Min:') text_size 16 text_color "gold" xpos 10
                                for stat, value in item.min.items():
                                    frame:
                                        xysize 153, 20
                                        text stat.capitalize() color "ivory" size 16 align (.02, .5)
                                        label (u'{size=-4}%d'%value) align (.98, .5)
                                null height 2
                            $ temp = [t for t in item.addtraits if not t.hidden]
                            if temp:
                                label ('Adds Traits:') text_size 16 text_color "gold" xpos 10
                                for trait in temp:
                                    use trait_info(trait, 153, 20)
                                null height 2
                            $ temp = [t for t in item.removetraits if not t.hidden]
                            if temp:
                                label ('Removes Traits:') text_size 16 text_color "gold" xpos 10
                                for trait in temp:
                                    use trait_info(trait, 153, 20)
                                null height 2
                            if item.add_be_spells or item.attacks:
                                label ('Adds Skills:') text_size 16 text_color "gold" xpos 10
                                if item.add_be_spells:
                                    for skill in item.add_be_spells:
                                        use skill_info(skill, 153, 20)
                                if item.attacks:
                                    for skill in item.attacks:
                                        use skill_info(skill, 153, 20)
                                null height 2
                            if item.addeffects:
                                label ('Adds Effects:') text_size 16 text_color "gold" xpos 10
                                for effect in item.addeffects:
                                    $ effect = CharEffect(effect)
                                    use effect_info(effect, 153, 20)
                                null height 2
                            if item.removeeffects:
                                label ('Removes Effects:') text_size 16 text_color "gold" xpos 10
                                for effect in item.removeeffects:
                                    $ effect = CharEffect(effect)
                                    use effect_info(effect, 153, 20)
                                null height 2
                label ('{color=#ecc88a}----------------------------------------') xalign .5
                frame:
                    xalign .5
                    background Frame("content/gfx/frame/p_frame7.webp", 10, 10)
                    has viewport mousewheel True xysize (460, 100)
                    text '[item.desc]' style "TisaOTM" size 16 color "gold"

# Inventory paging
screen paging(path="content/gfx/interface/buttons/",
              bgr="content/gfx/frame/BG_choicebuttons_flat.png",
              use_filter=True, ref=None, xysize=(270, 60), align=(.5, .0)):
    frame:
        background Frame(bgr, 10, 10, yoffset=5)
        xysize xysize
        align align
        style_group "content"

        vbox:
            align .5, .5
            null height 10
            # Filter
            if use_filter:
                hbox:
                    xmaximum xysize[0] - 15
                    xfill True
                    xalign .5
                    $ img = path + 'prev.png'
                    imagebutton:
                        align .0, .5
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Function(ref.apply_filter, "prev")

                    $ slot = EQUIP_SLOTS.get(ref.slot_filter, ref.slot_filter.capitalize())
                    label "[slot] " align .5, .5  text_color "ivory"

                    $ img = path + 'next.png'
                    imagebutton:
                        align 1.0, .5
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Function(ref.apply_filter, "next")
            # Listing
            hbox:
                align .5, .5
                xmaximum xysize[0] - 5
                xfill True
                hbox:
                    align (.0, .5)
                    $ img = path + 'first.png'
                    imagebutton:
                        yalign .5
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Function(ref.first)
                    $ img = path + 'prev.png'
                    imagebutton:
                        yalign .5
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Function(ref.prev)
                label ("%d - %d"%(ref.page+1, ref.max_page+1)) align (.5, .5) text_color "ivory"
                hbox:
                    align (1.0, .5)
                    $ img = path + 'next.png'
                    imagebutton:
                        yalign .5
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Function(ref.next)
                    $ img = path + 'last.png'
                    imagebutton:
                        yalign .5
                        idle img
                        hover PyTGFX.bright_img(img, .15)
                        action Function(ref.last)

screen shop_inventory(ref=None, x=.0):
    on "show":
        action SetField(ref.inventory, "filter_index", 0), Function(ref.inventory.apply_filter, "all")

    #key "mousedown_4" action Function(ref.inventory.next)
    #key "mousedown_5" action Function(ref.inventory.prev)

    frame at fade_in_out(t1=.5, t2=.5):
        style_group "content"
        background Frame(im.Alpha("content/gfx/frame/mes11.webp", alpha=.5), 5, 5)
        xalign x
        yfill True
        has vbox
        use paging(ref=ref.inventory, xysize=(260, 90))

        null height 5

        hbox:
            xalign .5
            add im.Scale("content/gfx/interface/icons/gold.png", 25, 25) align (.0, .5)
            null width 10
            $ g = gold_text(ref.gold)
            text g align (.5, 1.0) color "gold" size 23

        null height 5

        if isinstance(ref, ItemShop):
            label "[ref.name]" text_color "ivory" xalign .5
        elif isinstance(ref, PytCharacter):
            label "[ref.nickname]" text_color "ivory" xalign .5
        else:
            label "Inventory" text_color "ivory" xalign .5

        null height 5

        use items_inv(inv=ref.inventory, main_size=(268, 522), frame_size=(85, 85), return_value=["item", ref])

# Control loop for shopping?
label shop_control:
    $ result = ui.interact()
    if result[0] == "item":
        if result[1] in (char, shop):
            $ amount = 1
            $ focus = result[2]
            if result[1] == char:
                $ purchasing_dir = 'sell'
                $ item_price = int(focus.price*shop.sell_margin)
            else:
                $ purchasing_dir = 'buy'
                $ item_price = int(focus.price*shop.buy_margin)

        elif result[1] == 'buy/sell':
            if purchasing_dir == 'buy':
                if char.take_money(item_price*amount, "Items"):
                    python hide:
                        PyTSFX.purchase()

                        total = item_price*amount
                        shop.inventory.remove(focus, amount)
                        char.inventory.append(focus, amount)
                        shop.gold += total
                        shop.total_items_price -= total
                    $ amount = 1
                    $ focus = None
                else:
                    $ renpy.say("", choice(["Not enough money.", "No freebees.", "You'll need more money for this purchase"]))
            elif purchasing_dir == 'sell':
                $ total = item_price*amount
                $ msg = shop.check_sell(focus, total)
                if msg is None:
                    python hide:
                        PyTSFX.purchase()

                        char.add_money(total, reason="Items")
                        char.inventory.remove(focus, amount)
                        shop.inventory.append(focus, amount)
                        shop.gold -= total
                        shop.total_items_price += total
                    $ amount = 1
                    $ focus = None
                else:
                    $ renpy.say("", msg)
                $ del msg, total

    elif result[0] == 'control':
        $ result = result[1]
        if isinstance(result, basestring):
            if result == 'return':
                return
        else:
            $ amount += result
            if result > 0:
                if purchasing_dir == 'sell':
                    $ amount = min(amount, char.inventory[focus])
                else: # if purchasing_dir == 'buy':
                    $ amount = min(amount, shop.inventory[focus])
            else:
                $ amount = max(amount, 1)
    jump shop_control
