init -1 python:
    class Dungeon(_object):
        def __init__(self, **kwargs):
            for k in kwargs:
                if k != "r" and k != "map":
                    super(Dungeon, self).__setattr__(k, kwargs[k])
            self._map = kwargs['map']
            self.said = None
            self.next_events = deque()
            self.show_map = False
            self.can_move = True
            self.timer = None
            self.light = ""
            self.timed = {}

        def say(self, who, what, **kwargs):
            # a message will be displayed for a time, dependent on its length
            sound = kwargs.get("sound", None)
            if sound:
                renpy.play(*sound)

            timer = kwargs.get("timer", None)
            if not timer:
                timer = max(len(what) / 20.0, .5)

            self.said = [who, what, None, None]

            self.add_timer(timer, [{"function": "delsay", "arguments": [self.said] }])

        def delsay(self, msg):
            if self.said is msg:
                self.said = None

        def delitem(self, name, arguments):
            item = getattr(self, name)
            item.__delitem__(arguments)

        def add_timer(self, timer, functions):
            self.timer = min(self.timer, timer) if self.timer is not None else timer
            timestr = timer + time.time()
            funclist = list(functions)
            funclist.append({"function": "delitem", "arguments": ["timed", timestr]})
            self.timed[timestr] = funclist

        def enter(self, at=None, function=None, load=None):
            if at:
                self.hero = at

            if not hasattr(self, "smallMap"):
                self.smallMap = SpriteManager(ignore_time=True)
                self._mapped = []
                for n,i in enumerate(self._map):
                    solids = []
                    for m in range(len(i)):
                        solid = Solid("#0000", xysize=(6,6))
                        solids.append(solid)
                        s = self.smallMap.create(solid)
                        s.x = 6*m + 3
                        s.y = 6*n + 43
                    self._mapped.append(solids)

                self.arrowtext = Text(" ", size=10)
                self.arrow = self.smallMap.create(self.arrowtext)
                self.arrow.x = (self.hero['x'] - .2)*6 + 9
                self.arrow.y = (self.hero['y'] - .4)*6 + 49

                for p, m in self.spawn.iteritems():
                    m['mob'] = build_mob(id=m['name'], level=m['level'])

                    self.add_timer(m['timer'], [{"function": "_move_npc", "arguments": [p, m] }])

            return self.hero

        def load(self, name, **arguments):
            store.dungeon = store.dungeons[name]
            store.pc = store.dungeon.enter(**arguments)

        def exit(self, label="graveyard_town", **kwargs):
            if renpy.call_screen("yesno_prompt",
                                 message="Do you want to leave?",
                                 yes_action=Return(True), no_action=Return(False)):
                # reset hero position
                del self.hero

                # cleanup globals
                vars = ["dungeon", "pc", "mpos", "mpos2", "sided", "blend", "areas", "shown",
                        "hotspots", "distance", "lateral", "x", "y", "front_str",
                        "k", "d_items", "d_hotspots", "actions", "ri", "n", "e",
                        "situ", "pt", "it", "img_name", "brightness", "spawn", "ori",
                        "transparent_area", "bx", "by", "at", "to", "pos", "access_denied",
                        "dungeon_location", "dungeons", "event", "current_time", "t"]
                for i in vars:
                    if hasattr(store, i):
                        delattr(store, i)

                jump(label)

        def _move_npc(self, at_str, m):
            if not at_str in self.spawn:
                if DEBUG_LOG:
                    devlog.warn("spawn at %s already died?" % at_str)
                return

            at = eval(at_str)

            to = at # per default stay in position
            attack = False
            dx = adx = self.hero['x'] - at[0]
            dy = ady = self.hero['y'] - at[1]
            if adx < 0:
                adx = -adx
            if ady < 0:
                ady = -ady
            if adx <= 5 and ady <= 5:
                # if within 5 of hero move about.
                if adx != 0:
                    if adx == dx:
                        pos = (at[0] + 1, at[1])
                        ori = 1
                    else:
                        pos = (at[0] - 1, at[1])
                        ori = 3
                    access_denied = self.no_access(at, pos, ori, is_spawn=True)
                    if not access_denied:
                        to = pos
                    elif access_denied == "hero collision":
                        attack = True
                if ady != 0 and not attack:
                    if ady == dy:
                        pos = (at[0], at[1] + 1)
                        ori = 0
                    else:
                        pos = (at[0], at[1] - 1)
                        ori = 2
                    access_denied = self.no_access(at, pos, ori, is_spawn=True)
                    if not access_denied:
                        to = pos
                    elif access_denied == "hero collision":
                        attack = True
            if attack:
                # auto attack by monsters
                hs = dungeon.spawn_hotspots[m["name"]]
                # remove the mob(s)
                del self.spawn[at_str]
                self.next_events.extend(hs["actions"])
                return
            to_str = str(to)
            if to != at:
                del(self.spawn[at_str])
                self.spawn[to_str] = m

            self.add_timer(m['timer'], [{"function": "_move_npc", "arguments": [to_str, m] }])

        def map(self, x, y, color=None):
            if y < 0 or y >= len(self._map) or x < 0 or x >= len(self._map[y]):
                return "#"

            if color:
                self._mapped[y][x].color = color

            return self._map[y][x]

        def teleport(self, pt=None):
            if not pt: # using map hotspot
                pt = renpy.get_mouse_pos()
                pt = ((pt[0] - 3) / 6, (pt[1]-43) / 6)

            self.hero['x'] = pt[0]
            self.hero['y'] = pt[1]
            if len(pt) > 2: # to also set rotation: -1 for left/up, non-current direction is zero
                self.her['dx'] = pt[2]
                self.her['dy'] = pt[3]

        def play(self, sound, channel="sound", condition=True):
            if condition and not renpy.music.is_playing(channel):
                renpy.play(sound, channel)

        def no_access(self, at, to, ori, is_spawn=False):
            if pc['x'] == to[0] and pc['y'] == to[1]:
                return "hero collision" # for spawn movement

            tostr = str(to)
            if tostr in self.spawn:
                return "spawn collision"

            (src, dest) = (self.map(*at), self.map(*to))

            if dest in self.access[ori]:
                if src in self.access[ori] or (not is_spawn and src in self.conditional_access[ori]):
                    return
                self.play(self.sound['locked'], condition=not is_spawn, channel="sound")
                return "access denied"

            if is_spawn:
                return "spawn moment denied"

            if dest in self.conditional_access[ori]:
                if tostr not in self.access_condition:
                    return
                elif 'access' in self.access_condition[tostr] and self.access_condition[tostr]['access']:
                    return
                else:
                    # TODO dungeon: check for condition(s), key..? (requires inventory)
                    self.play(self.sound['locked'], condition=not is_spawn, channel="sound")
                    return "access denied"

            self.play(self.sound['bump'], condition=not is_spawn, channel="sound")
            return "wall collision"

        def function(self, function, arguments, **kwargs):
            # only allow functions of this class
            func = getattr(self, function)
            func(*arguments, **kwargs)

        @staticmethod
        def combat(mob_id, sound=None):
            len_ht = len(hero.team)

            enemy_team = Team(name="Enemy Team", max_size=3)
            min_lvl = max(hero.team.get_level()-5, mobs[mob_id]["min_lvl"])
            for i in range(min(3, len_ht+randint(0, 1))):
                mob = build_mob(id=mob_id, level=randint(min_lvl, min_lvl+10))
                enemy_team.add(mob)

            result = run_default_be(enemy_team, background="content/gfx/bg/be/b_dungeon_1.webp", death=True) # TODO: maybe make escape working here too?

            if result is not True:
                jump("game_over")

        def grab_item(self, item, sound=None):
            if sound is not None:
                filename, channel = sound
                renpy.play(filename, channel=channel)
            item = store.items[item]
            hero.inventory.append(item)
            self.say(hero.name, "%s! This will come useful!" % item.id)

transform sprite_default(xx, yy, xz, yz, rot=None):
    xpos xx
    ypos yy
    xzoom xz
    yzoom yz
    rotate rot
    subpixel True

screen dungeon_move(hotspots):
    tag dungeon

    # Screen which shows move buttons and a minimap
    for sw in reversed(shown):
        if isinstance(sw, list):
            if sw[2]:
                python:
                    light_matrix = im.matrix.brightness(-math.sqrt(sw[3]**2 + sw[2]**2)/(5.8 if dungeon.light else 4.5))
                    if isinstance(sw[0], Item):
                        mco = im.MatrixColor(sw[0].icon, light_matrix)
                        (width, height) = mco.image.load().get_size()

                        xz=1.0/(1.5 + math.log(sw[2], 2))
                        xx=int(float(renpy.config.screen_width - (width/2)*xz) * (.5 + float(sw[3]) / float(1 + sw[2])))

                        yz = xz/1.75
                        yy=int((renpy.config.screen_height - height*xz) * (.5 + 1.0 / float(1.0 + sw[2])))
                        rot = sw[1]['rot'] if 'rot' in sw[1] else None #15.0+float(abs(sw[3])*distance)
                    elif isinstance(sw[0], Mob):
                        mco = im.MatrixColor(sw[0].battle_sprite, light_matrix)
                        (width, height) = mco.image.load().get_size()

                        sz = float(sw[1]['size']) if 'size' in sw[1] else 1.3
                        xz=2.0/(1.5 + math.log(sw[2], 2))
                        xx=int(float(renpy.config.screen_width - width*xz) * (.5 + float(sw[3]) / float(1 + sw[2])))


                        yz = xz
                        lowness = float(renpy.config.screen_height)
                        if 'yoffs' in sw[1]:
                            lowness += float(sw[1]['yoffs'])
                        yy=int(float(lowness - height*xz) * (.5 + .5 / float(.0001 + sw[2])))
                        rot=None

                add mco at [sprite_default(xx, yy, xz, yz, rot)]

        elif not isinstance(sw, basestring):
            add sw
        elif renpy.has_image(sw):
            add sw

    use top_stripe(False, show_lead_away_buttons=False)
    use team_status(True)

    # if dungeon.show_map:
    add dungeon.smallMap:
        pos (450, 50)

    if hotspots:
        imagemap:
            alpha False
            ground "content/dungeon/bluegrey/dungeon_blank.webp"
            for hs in hotspots:
                hotspot (hs['spot'][0], hs['spot'][1], hs['spot'][2], hs['spot'][3]) action Return(value=hs['actions'])

    if dungeon.said:
        use say(dungeon.said[0], dungeon.said[1], dungeon.said[2], dungeon.said[3])
        $ actions = [Function(dungeon.delsay, dungeon.said), Return(value="event_list")]
        key "K_RETURN" action actions
        key "mousedown_1" action actions

    elif dungeon.can_move:
        key "focus_left" action NullAction()
        key "focus_right" action NullAction()
        key "focus_up" action NullAction()
        key "focus_down" action NullAction()

        imagebutton:
            pos (190, 600)
            idle im.Scale("content/gfx/interface/buttons/blue_arrow_up.png", 50, 36)
            action Return(value=8)
            keysym "K_KP8", "K_UP", "repeat_K_KP8", "repeat_K_UP"
        imagebutton:
            pos (190, 650)
            idle im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow_up.png", 50, 36), vertical=True)
            action Return(value=2)
            keysym "K_KP2", "K_DOWN", "repeat_K_KP2", "repeat_K_DOWN"
        imagebutton:
            pos (135, 605)
            idle im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow_r.png", 36, 50), horizontal=True)
            action Return(value=4)
            keysym "K_KP4", "K_LEFT"
        imagebutton:
            pos (245, 605)
            idle im.Scale("content/gfx/interface/buttons/blue_arrow_r.png", 36, 50)
            action Return(value=6)
            keysym "K_KP6", "K_RIGHT"
        imagebutton:
            pos (145, 660)
            idle im.Flip(im.Scale("content/gfx/interface/buttons/blue_arrow.png", 36, 50), horizontal=True)
            action Return(value=7)
            keysym "K_KP7", "repeat_K_KP7"
        imagebutton:
            pos (248, 660)
            idle im.Scale("content/gfx/interface/buttons/blue_arrow.png", 36, 50)
            action Return(value=9)
            keysym "K_KP9", "repeat_K_KP9"

            # if config.developer:
                # textbutton "U" action Return(value="update map") xcenter .2 ycenter .8
                # key "K_u" action Return(value="update map")
                # key "K_p" action Function(scrap.put, SCRAP_TEXT, str((pc['x'], pc['y'])))
                # key "K_o" action Return(value="mpos")
                # key "K_g" action SetField(dungeon, "show_map", "teleport")
        key "K_m" action ToggleField(dungeon, "show_map")
        key "K_l" action ToggleField(dungeon, "light", "_torch", "")

    if dungeon.next_events:
        timer .1 action Return(value="event_list")
    elif dungeon.timer:
        timer dungeon.timer action Return(value="event_list")

style move_button_text:
    size 60

label enter_dungeon:
    if day < global_flags.get_flag("can_access_cemetery_dungeon", 0):
        $ temp = global_flags.flag("can_access_cemetery_dungeon")-day
        if temp >= 2:
            "You can not enter the dungeon for [temp] more days."
        else:
            "To enter the dungeon you have to wait till tomorrow."
        $ global_flags.set_flag("keep_playing_music")
        $ del temp
        jump graveyard_town

    menu:
        "This old dungeon looks dangerous. Are you sure you want to go in?"
        "Yes":
            $ global_flags.set_flag("can_access_cemetery_dungeon", day+randint(3, 5))
        "No":
            $ global_flags.set_flag("keep_playing_music")
            jump graveyard_town

    python:
        # Create a dungeon stage
        dungeon = dungeons['Mausoleum1']
        if hasattr(dungeon, "hero"):
            pc = dungeon.enter()
        else:
            pc = dungeon.enter(at={ "x": 1, "y": 1, "dx": 1, "dy": 0 })
            dungeon.say("", "You enter the mausoleum. The door shuts behind you; you cannot get out this way!")
        mpos = None
    # Music
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("dungeon", fadein=.5)
    $ global_flags.del_flag("keep_playing_music")

    # Place a player position on a dungeon stage.
    # dx,dy means direction. If dy=1, it's down. If dx=-1, it's left.

label enter_dungeon_r:
    while True:
        # Composite background images.
        scene
        python:
            # compile front to back, a list of what area are walls to be shown, behind wall we don't show.
            sided = ["%s%s_left%dc", "%s%s_left%db", "%s%s_left%d", "%s%s_front%d", "%s%s_right%d", "%s%s_right%db", "%s%s_right%dc"]
            blend = dungeon.area
            areas = deque([[0, 0]])
            shown = []
            hotspots = []

            #if config.developer and dungeon.show_map == "teleport":
            #    hotspots.append({'spot': [3, 43, len(dungeon._map[0])*6, len(dungeon._map)*6],
            #                     'actions': [{ "function": "teleport", "arguments": [] }] })

            renpy.show(dungeon.background % dungeon.light)

            while areas:
                (distance, lateral) = areas.popleft()

                x = pc['x'] + distance*pc['dx'] - lateral*pc['dy']
                y = pc['y'] + lateral*pc['dx'] + distance*pc['dy']

                if distance == 1 and lateral == 0: # actions can be apply to front
                    front_str = str((x, y))
                    if front_str in dungeon.area_hotspots:
                        hotspots.extend(dungeon.area_hotspots[front_str])

                    for k in ["item", "renderitem", "spawn"]:

                        d_items = getattr(dungeon, k)
                        d_hotspots = getattr(dungeon, "%s_hotspots" % k)

                        if front_str in d_items:
                            actions = []
                            for ri in [d_items[front_str]] if k == "spawn" else d_items[front_str]:
                                n = ri['name']
                                if n in d_hotspots:
                                    e = d_hotspots[n].copy()
                                    actions.extend(e['actions'])
                                    e['actions'] = actions
                                    hotspots.append(e)
                            if actions:
                                # remove the item/spawn when clicked
                                actions.insert(0, { "function": "delitem", "arguments": [k, front_str]})

                situ = dungeon.map(x, y)

                if situ in dungeon.container:
                    # FIXME use position lookup, for some container may first have to add front (cover) image (or modify image)
                    pt = str((x, y))
                    if pt in dungeon.renderitem:
                        for ri in dungeon.renderitem[pt]:
                            img_name = sided[lateral+3] % ('dungeon_'+ri['name'], dungeon.light, distance)
                            img_func = ri.get("function", None)
                            if img_func is not None and img_func.startswith("im.matrix."):
                                img_name = content_path("dungeon", ri['name']+dungeon.light, img_name+".webp")
                                if renpy.loadable(img_name):
                                    # distance darkening
                                    brightness = im.matrix.brightness(-math.sqrt(lateral**2 + distance**2)/(5.8 if dungeon.light else 4.5))
                                    shown.append(im.MatrixColor(img_name, eval(img_func)(*ri["arguments"]) * brightness))
                            else:
                                shown.append(img_name)

                    if pt in dungeon.item:
                        for it in dungeon.item[pt]:
                            shown.append([items[it['name']], it, distance, lateral])

                    if pt in dungeon.spawn:
                        spawn = dungeon.spawn[pt]
                        shown.append([spawn['mob'], spawn, distance, lateral])

                # also record for minimap
                for k in dungeon.minimap:
                    if situ in k:
                        dungeon.map(x, y, renpy.easy.color(dungeon.minimap[k]))
                        break
                else:
                    dungeon.map(x, y, renpy.easy.color(dungeon.minimap['ground']))

                if pc['dy'] == -1:
                    dungeon.arrowtext.set_text("↑")
                    dungeon.arrow.y = (pc['y'] - .4)*6 + 43
                elif pc['dx'] == 1:
                    dungeon.arrowtext.set_text("→")
                    dungeon.arrow.y = (pc['y'] - .5)*6 + 43
                elif pc['dy'] == 1:
                    dungeon.arrowtext.set_text("↓")
                    dungeon.arrow.y = (pc['y'] - .4)*6 + 43
                else:
                    dungeon.arrowtext.set_text("←")
                    dungeon.arrow.y = (pc['y'] - .5)*6 + 43

                dungeon.arrow.x = (pc['x'] - .2)*6 + 3

                if situ in dungeon.visible: # a wall or so, need to draw.
                    if isinstance(blend[situ], list):
                        if len(blend[situ]) == 2: # left-right symmetry
                            shown.append(sided[lateral+3] % ('dungeon_'+blend[situ][abs(pc['dx'])], dungeon.light, distance))
                        else: # no symmetry, 4 images.
                            ori = 1 - pc['dx'] - pc['dy'] + (1 if pc['dx'] > pc['dy'] else 0)
                            shown.append(sided[lateral+3] % ('dungeon_'+blend[situ][ori], dungeon.light, distance))
                    else: # symmetric, or simply rendered in only one symmetry
                        shown.append(sided[lateral+3] % ('dungeon_'+blend[situ], dungeon.light, distance))

                transparent_area = dungeon.transparent[abs(pc['dx'])]

                if situ in transparent_area or (situ in dungeon.visible and not renpy.has_image(shown[-1])): # need to draw what's behind it.
                    # after `or' prevents adding areas twice. If the area diagonally nearer to hero is
                    # a wall, the area is not yet drawn, draw it, unless we cannot see it.
                    (bx, by) = (x-pc['dx'], y-pc['dy'])
                    if lateral >= 0 and (distance == lateral*2 or distance > lateral*2
                                         and dungeon.map(bx-pc['dy'], by+pc['dx']) not in transparent_area
                                         and ((distance == 1 and lateral == 0) or dungeon.map(bx, by) in transparent_area)):
                        areas.append([distance, lateral + 1])

                    if lateral <= 0 and (distance == -lateral*2 or distance > -lateral*2
                                         and dungeon.map(bx+pc['dy'], by-pc['dx']) not in transparent_area
                                         and ((distance == 1 and lateral == 0) or dungeon.map(bx, by) in transparent_area)):
                        areas.append([distance, lateral - 1])

                    if distance < 5:
                        areas.append([distance + 1, lateral])

        $ renpy.block_rollback()

        call screen dungeon_move(hotspots)

        python:
            at = (pc['x'], pc['y'])
            ori = 1 - pc['dx'] - pc['dy'] + (1 if pc['dx'] > pc['dy'] else 0)
            to = None

            if isinstance(_return, list):
                dungeon.next_events.extend(_return)
            elif _return == 2:
                to = (pc['x']-pc['dx'], pc['y']-pc['dy'])
            elif _return == 4:
                (pc['dx'], pc['dy']) = (pc['dy'], -pc['dx'])
            elif _return == 6:
                (pc['dx'], pc['dy']) = (-pc['dy'], pc['dx'])
            elif _return == 7:
                to = (pc['x']+pc['dy'], pc['y']-pc['dx'])
                ori = ori ^ 2
            elif _return == 8:
                to = (pc['x']+pc['dx'], pc['y']+pc['dy'])

            elif _return == 9:
                to = (pc['x']-pc['dy'], pc['y']+pc['dx'])

                ori = ori ^ 2
            elif _return == "update map":
                dungeon_location = dungeon.hero
                dungeons = load_dungeons()
                dungeon = dungeons[dungeon.id]
                dungeon.enter(at=dungeon_location)
            elif _return == "mpos": # XXX: dev mode
                if mpos:
                    mpos2 = renpy.get_mouse_pos()
                    scrap.put(SCRAP_TEXT, str((mpos[0], mpos[1], mpos2[0] - mpos[0], mpos2[1] - mpos[1])))
                    mpos = None
                else:
                    mpos = renpy.get_mouse_pos()
            elif _return in hero.team:
                came_to_equip_from = "enter_dungeon_r"
                eqtarget = _return
                equip_girls = [_return]
                global_flags.set_flag("keep_playing_music")
                equipment_safe_mode = True
                renpy.jump("char_equip")

            if to:
                access_denied = dungeon.no_access(at, to, ori)
                if not access_denied:
                    # move to the new position
                    (pc['x'], pc['y']) = to
                    if str(to) in dungeon.event:
                        # trigger events at the new position
                        dungeon.next_events.extend(dungeon.event[str(to)])
                elif access_denied == "spawn collision":
                    # auto attack monsters
                    to = str(to)
                    spawn = dungeon.spawn[to]
                    # prepare actions with the removal of the mobs at the front
                    actions = dungeon.spawn_hotspots[spawn["name"]]["actions"]
                    actions = [{ "function": "delitem", "arguments": ["spawn", to]}] + actions
                    dungeon.next_events.extend(actions)

            while dungeon.next_events:
                event = dungeon.next_events.popleft()
                at = event.get("at", 0)
                if at == 0:
                    dungeon.function(**event)
                else:
                    dungeon.add_timer(at, [event])

            # do any expired timer events
            if dungeon.timer is not None:
                dungeon.timer = None
                current_time = time.time()
                for t in dungeon.timed.keys():
                    if not dungeon.timer or t - current_time < dungeon.timer:
                        if t < current_time:
                            for event in list(dungeon.timed[t]): # copy: key may be removed
                                dungeon.function(**event)
                        else:
                            dungeon.timer = t - current_time


# Assign background images.
# "left0" means a wall on the lefthand, "front2" means a further wall on the front, and so on. field of view:
#
# left5c, left5b, left5, front5, right5, right5b, right5c
# left4c, left4b, left4, front4, right4, right4b, right4c
#         left3b, left3, front3, right3, right3b
#         left2b, left2, front2, right2, right2b
#                 left1, front1, right1
#                 left0, <hero>, right0
