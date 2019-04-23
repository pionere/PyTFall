label village_town:
    $ gm.enter_location(goodtraits=["Scars", "Undead", "Furry", "Monster", "Not Human", "Aggressive", "Vicious", "Sadist"], badtraits=["Sexy Air", "Virtuous", "Optimist", "Peaceful", "Elegant", "Energetic", "Exhibitionist"],
                        curious_priority=False, coords=[[.2, .7], [.45, .72], [.75, .7]])

    # Music related:
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("Town")
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("village_town"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()

    scene bg tavern_town
    with dissolve

    if not global_flags.flag('visited_village_town'):
        $ global_flags.set_flag('visited_village_town')
        "The 'slums' of the city..."
        "The home of poor, miscreants and lawbreakers."
        "Not to mention an occasional escaped slave."

    show screen village_town

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:
        $ result = ui.interact()
        if result[0] == 'jump':
            $ gm.start_gm(result[1], img=result[1].show("girlmeets", "suburb", exclude=["beach", "winter", "night", "formal", "indoors", "swimsuit"], type="first_default", label_cache=True, resize=(300, 400), gm_mode=True))

        elif result[0] == 'control':
            if result[1] == 'return':
                hide screen village_town
                with dissolve
                jump city

screen village_town:
    use top_stripe(True)
    use location_actions("village_town")

    if gm.show_girls:
        key "mousedown_3" action ToggleField(gm, "show_girls")

        add "content/gfx/images/bg_gradient.webp" yalign .45
        for entry, pos in zip(gm.display_girls(), gm.coords):
            hbox:
                align pos
                use rg_lightbutton(return_value=['jump', entry])
    else:
        # Jump buttons:
        $ img = im.Scale("content/gfx/interface/icons/work_shop.png", 80, 80)
        imagebutton:
            align (.05, .75)
            idle (img)
            hover (im.MatrixColor(img, im.matrix.brightness(.15)))
            action [Hide("village_town"), Jump("village_town_work")]

label village_town_work:
    scene bg workshop with dissolve

    if not global_flags.flag('visited_village_town_work'):
        $ global_flags.set_flag('visited_village_town_work')

        $ n = npcs["NKCell_town"].say
        show expression npcs["NKCell_town"].get_vnsprite() as npc
        with dissolve

        "As you approach the place you see a strong woman both of her hand full of items which look like garbage from the distance."
        "You want to get a closer look at it, but she stops in her movements and looks at you."
        n "What!? Are you going to help or just watch?"
        n "There is always a job for the willing, so come and grab these if you want to make yourself useful."
        n "Don't worry, these are mostly garbage, so if you find anything salvable just toss it to the right heap there."
        n "I can not pay much gold, but you get a share from the materials."
        n "Now if you excuse me, I need get back to work."
        n "Ohh, one more thing. You might want to protect your hands from injuries. I suggest a pair of Metal Gloves, but it is up to you."
        hide npc with dissolve
        $ del n

    menu:
        "What do you want to do?"
        "Work 1AP" if hero.has_ap():
            $ time_limit = 100 # PP_PER_AP
        "Work" if hero.PP > 0:
            $ time_limit = None
        "Leave":
            $ global_flags.set_flag("keep_playing_music")
            jump village_town

    python:
        source_items = []
        moving_items = []
        basket = defaultdict(int)
        hand_item = None
        
        hand_protection = hero.eqslots["wrist"]
        item = getattr(hand_protection, "id", False)
        if item in ["Metal Gloves", "Steel Gloves", "Mail Gloves", "Mithril Gloves", "Draconic Leather Gloves"]:
            hand_protection = True
        elif "Bracer" in item or item == "Slave Handcuffs":
            hand_protection = False
        next_pp_time = 0
        used_pp = 0
        running = False
        last_time = 0

        sources = [items[item] for item in ["Bricks", "Stone", "Hay", "Glass", "Steel", "Nails"]]
        shuffle(sources)

        # initial belt
        for item in xrange(randint(5, 10)): # BELT LEFT    ...   RIGHT-LEFT, BELT TOP ...      BOTTOM-TOP-ITEM WIDTH
            source_items.append([choice(sources), [80 + random.random()*100, 100 + random.random()*460]])

    show screen village_town_work
    with dissolve
    
    python hide:
        global source_items, moving_items, basket, hand_item, hand_protection, next_pp_time, used_pp, running, last_time, sources
        while 1:
            result = ui.interact()

            mpos = renpy.get_mouse_pos()
            curr_time = time.time()

            if result == "start":
                running = True
                last_time = next_pp_time = curr_time
                continue
            if running is not True:
                continue

            curr_item = None
            # move the grabbed item
            if hand_item is not None:
                curr_item = hand_item[0]
                item_pos = [mpos[0] + hand_item[1][0], mpos[1] + hand_item[1][1]]
                hand_item[2].append([item_pos, curr_time])
                if result == "drop" or mpos[0] > 300: # SEPARATOR
                    # drop the item
                    source_items.remove(curr_item)
                    
                    speed = last_entry = None
                    for temp in hand_item[2]:
                        if last_entry is not None:
                            last_pos, last_t = last_entry
                            next_pos, next_t = temp
                            dt = float(next_t - last_t)
                            s = [(next_pos[0]-last_pos[0])/dt, (next_pos[1]-last_pos[1])/dt]
                            if speed is None:
                                speed = s
                            else:
                                speed = [(speed[0]+s[0])/2.0, (speed[1]+s[1])/2.0]
                        last_entry = temp

                    curr_item.append(speed)
                    moving_items.append(curr_item)
                    hand_item = None
                else:
                    # move the item
                    curr_item[1] = item_pos
                    
            elif isinstance(result, list):
                # grab the item
                hand_item, item_pos = result
                mqueue = collections.deque(maxlen=10)
                mqueue.append([item_pos, curr_time])
                hand_item = [result, [item_pos[0]-mpos[0], item_pos[1]-mpos[1]], mqueue]

                # injuries
                if hand_protection is True:
                    pass
                elif hand_protection:
                    # bad protection -> chance to lose the item
                    if dice(100.0 / (60 * 7)): # once per week
                        hero.unequip(hand_protection)
                        hero.remove_item(hand_protection)
                        tkwargs = {"color": "dodgerblue", "outlines": [(1, "black", 0, 0)]}
                        gfx_overlay.notify("Your %s is damaged beyond repair. Now you have to work barehanded." % hand_protection.id, tkwargs=tkwargs, duration=2.0)
                        hand_protection = False
                else:
                    # no protection -> chance to injury
                    if dice(100.0 / 60):     # once a day
                        hero.gfx_mod_stat("health", -randint(2, 8))
                        tkwargs = {"color": "tomato", "outlines": [(1, "black", 0, 0)]}
                        gfx_overlay.notify("You hurt yourself as you reach for the item.", tkwargs=tkwargs, duration=2.0)

            dt = curr_time - last_time
            # move the source items
            drops = []
            for item in source_items:
                if item is not curr_item:
                    pos = item[1][0] - dt * 4 # BELT SPEED
                    if pos < 80: # BELT LEFT - ITEM WIDTH/2
                        drops.append(item)
                    else:
                        item[1][0] = pos
            source_items = [i for i in source_items if i not in drops]
            
            # move the moving items
            drops = []
            for item in moving_items:
                if item is not curr_item:
                    pos = item[1]
                    speed = item[2]

                    xpos = pos[0] + dt * speed[0]
                    ypos = pos[1] + dt * speed[1]

                    if xpos < 180: # BELT RIGHT - ITEM WIDTH/2
                        if xpos > 80 and ypos > 80 and ypos < 580: # BELT LEFT - ITEM WIDTH/2 and TOP - ITEM WIDTH/2, BOTTOM - ITEM WIDTH/2
                            # still on the belt -> preserve
                            item.pop()
                            source_items.append(item)
                        drops.append(item)
                    elif ypos > 650: # FLOOR
                        curr_item = item[0]
                        pos = 580 + 100*sources.index(curr_item) # SEPARATOR + DIST - ITEM WIDTH/2
                        if pos <= xpos <= pos + 100: # BASKET WIDTH + ITEM WIDTH
                            basket[item[0]] += 1
                        else:
                            renpy.show(curr_item.id, what=HitlerKaputt(curr_item.icon, 10, offset=(xpos-config.screen_width/2, ypos-config.screen_height)), zorder=100)

                        drops.append(item)
                    elif xpos > config.screen_width: 
                        drops.append(item)
                    else:
                        # TODO check collision

                        pos[0] = xpos
                        pos[1] = ypos

                        # item[2][0] TODO add drag ?
                        speed[1] += 800 * dt # g * dt
            moving_items = [i for i in moving_items if i not in drops]

            # populate the belt
            if random.random() < dt/4: # BELT RIGHT-ITEM-WIDTH/2, BELT TOP ... BOTTOM-TOP-ITEM WIDTH
                source_items.append([choice(sources), [180, 100 + random.random()*460]])

            # start new shift
            if curr_time > next_pp_time:
                if hero.take_pp(10):
                    used_pp += 10
                    next_pp_time += 5 # 5s for 10PP
                    if time_limit is not None and time_limit <= used_pp:
                        result = "stop" 
                else:
                    result = "stop"

            # check to end
            if result == "stop":
                jump("village_town_work_end")

            # end turn
            last_time = curr_time

screen village_town_work:
    # Remaining AP:
    button:
        pos (65, 20)
        xysize 170, 50
        focus_mask True
        background ProportionalScale("content/gfx/frame/frame_ap.webp", 170, 50)
        action NullAction()
        hbox:
            yalign .1
            xpos 105
            $ ap_h, pp_h = hero.ap_pp
            label "%d"%ap_h:
                style "content_label"
                text_size 23
                text_color "ivory"
                text_bold True
            if pp_h:
                text "%02d"%pp_h:
                    color "pink"
                    style "proper_stats_text"
                    yoffset 7

    # belt
    add im.Scale("content/gfx/frame/ink_box.png", 100, 500) pos (100, 100) # BELT RIGHT-LEFT, BOTTOM-TOP ... LEFT, TOP

    # items on the belt
    for item in source_items:
        $ temp, pos = item
        $ img = ProportionalScale(temp.icon, 40, 40)
        button:
            style 'image_button'
            pos (int(pos[0]), int(pos[1]))
            idle_background img
            hover_background im.MatrixColor(img, im.matrix.brightness(.15))
            focus_mask True
            tooltip temp.id
            action Return(item)

    # release button
    $ img = im.Scale("content/gfx/images/button.webp", 160, 40)
    button:
        pos (70, 630)
        xysize 160, 40
        idle_background img
        hover_background im.MatrixColor(img, im.matrix.brightness(.10))
        insensitive_background im.Sepia(img)
        action Return("drop")
        sensitive hand_item is not None
        text "Space" align .5, .5 size 30 color "black"
        keysym "K_SPACE"
        tooltip "Release the item!"

    # separator
    add im.Scale("content/gfx/frame/p_frame7.webp", 4, config.screen_height) pos (300, 0)

    # flying items:
    for item in moving_items:
        $ temp, pos, speed = item
        $ img = ProportionalScale(temp.icon, 40, 40)
        button:
            style 'image_button'
            pos (int(pos[0]), int(pos[1]))
            idle_background img
            hover_background im.MatrixColor(img, im.matrix.brightness(.15))
            focus_mask True
            tooltip temp.id
            action NullAction()

    # baskets
    for idx, item in enumerate(sources):
        $ img = ProportionalScale(item.icon, 60, 60)
        textbutton str(basket[item]):
            xysize (60, 60)
            style 'image_button'
            pos (600 + 100 * idx, 650) # SEPARATOR + DIST, FLOOR
            idle_background img
            hover_background im.MatrixColor(img, im.matrix.brightness(.15))
            focus_mask True
            tooltip item.id
            action NullAction()
            text_size 40
            text_align .5, .5
            text_color "ivory"
            text_outlines [(1, "black", 0, 0)]

    if running is False:
        # Not started
        button:
            style_group "pb"
            action Return("start")
            text "Begin work" style "pb_button_text" size 20
            align .5, .5
            keysym "K_SPACE"

    key "mousedown_3" action Return("stop")

    timer 0.1 action Return("timeout") repeat True

label village_town_work_end:
    hide screen village_town_work
    with dissolve

    # rewards
    python hide:
        # resources
        money = 0
        for item, amount in basket.items():
            if amount == 0:
                continue
            hero.add_item(item, amount)
            gfx_overlay.random_find(item, 'items', amount)
            money += amount

        if money != 0:
            result = randint(money, money*2)
            hero.add_money(result, reason="Job")
            gfx_overlay.random_find(result, 'gold')

        hero.gfx_mod_stat("joy", -randint(used_pp/50, used_pp/20)) # PP_PER_AP

    hero.say "This is all for now."

    # cleanup
    # safe(r) cleanup:
    python hide:
        cleanup = ["source_items", "moving_items", "item",
                  "basket", "hand_item", "hand_protection",
                  "next_pp_time", "used_pp", "sources",
                  "running", "last_time", "time_limit"]
        for i in cleanup:
            if hasattr(store, i):
                delattr(store, i)
    $ global_flags.set_flag("keep_playing_music")
    jump village_town
    