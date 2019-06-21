init -960 python:
    # TODO the objects should be in the PyTGFX namespace, but Renpy seems to have trouble with it
    class ArenaBarMinigame(renpy.Displayable):
        def __init__(self, data, length, **properties):
            super(ArenaBarMinigame, self).__init__(**properties)
            self.slider = "content/gfx/interface/bars/thvslider_thumb.png"
            bar = Transform("content/gfx/interface/bars/vcryslider_full.png", size=(40, length))
            vbox = VBox(xysize=(40, length))

            for color, value in data:
                what = Transform(Solid(color), size=(40, value))
                vbox.add(what)

            fixed = AlphaBlend(bar, bar, vbox, alpha=True)
            self.displayable = fixed

            # Tracking:
            self.next_st = 0
            self.step = 10 # Can control the speed.
            self.change = self.step
            self.interval = .01
            self.max_length = length
            self.value = 0
            self.update = True

        def render(self, width, height, st, at):
            render = renpy.Render(50, self.max_length)
            render.place(self.displayable)

            if self.value >= self.max_length:
                self.value = self.max_length
                self.change = -self.step
            if self.value <= 0:
                self.value = 0
                self.change = self.step

            if self.update and st >= self.next_st:
                self.value += self.change
                self.next_st = st+self.interval

            pos = (42, round_int(self.value))
            slider = Transform(self.slider, pos=pos, anchor=(1.0, .5))
            render.place(slider)

            renpy.redraw(self, 0)
            return render

    class ExpBarController(renpy.Displayable):
        def __init__(self, char, **kwargs):
            super(ExpBarController, self).__init__(**kwargs)
            self.char = char
            self.last_known_level = char.level
            self.active_pool = 0
            self.update_st = 0
            self.set_step()

            self.done = False    # Done adding experience...
            self.running = False # Still adding experience...

        def set_step(self):
            step = round_int(self.char.stats.goal_increase/60.0)
            if str(step).endswith('0'):
                step += 6
            self.step = step

        def mod_exp(self, value):
            self.active_pool += value
            self.update_st = 0
            self.running = True

            renpy.music.play("content/sfx/sound/events/counting_long.ogg", channel="sound", loop=True)
            renpy.redraw(self, 0)

        def bar_and_text(self):
            char = self.char

            fixed = Fixed(xysize=(326, 130)) # Base

            portrait = Fixed(xysize=(102, 102)) # Portrait
            bg = Frame("content/gfx/frame/MC_bg3.png", 10, 10,
                       xysize=(102, 102), align=(.5, .5))
            portrait.add(bg)
            profile_img = char.show("portrait", resize=(98, 98), cache=True)
            portrait.add(Transform(profile_img, align=(.5, .5)))
            fixed.add(portrait)

            # Level:
            ts = "Level {}".format(char.level)
            txt = Text(ts, style="proper_stats_value_text",
                       bold=True, outlines=[(1, "#181818", 0, 0)],
                       size=22, color="#DAA520", pos=(250, 65))
            fixed.add(txt)

            # Bar:
            left_bar = renpy.displayable("content/gfx/interface/bars/exp_full.png")
            right_bar = renpy.displayable("content/gfx/interface/bars/exp_empty.png")
            val = char.stats.exp + char.stats.goal_increase - char.stats.goal
            bar = Bar(value=val,
                    left_bar=left_bar,
                    right_bar=right_bar,
                    range=char.stats.goal_increase,
                    thumb=None, xysize=(324, 25),
                    ypos=102)
            fixed.add(bar)

            # Exp Img:
            img = Image("content/gfx/interface/images/exp_b.png", yalign=1.0)
            fixed.add(img)
            # Exp:
            ts = "{}/{}".format(char.exp, char.stats.goal)
            txt = Text(ts, italic=True, bold=True, size=15,
                       outlines=[(1, "#181818", 0, 0)], color="#DAA520",
                       xalign=.6, ypos=110)
            fixed.add(txt)

            return fixed

        def render(self, width, height, st, at):
            if self.running:
                if self.update_st <= st:
                    char = self.char
                    step = self.step
                    if self.active_pool > step:
                        char.mod_exp(step)
                        self.active_pool -= step
                    else:
                        char.mod_exp(self.active_pool)
                        self.active_pool = 0

                    if self.last_known_level != char.level:
                        self.last_known_level = char.level
                        self.set_step()
                        renpy.music.play("content/sfx/sound/events/go_for_it.mp3", channel="audio")

                    self.update_st = st + .05

            render = renpy.Render(326, 130)
            render.place(self.bar_and_text(), st=st)

            if self.running:
                if not self.active_pool:
                    self.update_st = 0
                    self.running = False
                    self.done = True

                    renpy.music.stop(channel="sound")
                    renpy.restart_interaction()
                else:
                    renpy.redraw(self, 0)
            return render

    class RadarChart(renpy.Displayable):
        def __init__(self, stats, size, xcenter, ycenter, color, **kwargs):
            super(RadarChart, self).__init__(**kwargs)
            # renpy.Displayable.__init__(self, **kwargs)
            self.color = color
            angle = 360 / len(stats)
            self.stat_vertices = [(self.get_tangent_offset(xcenter, ycenter, 90 + (angle*idx), 7 + int(size*stat))) for idx, stat in enumerate(stats)]

        def render(self, width, height, st, at):
            r = renpy.Render(width, height)
            rr = r.canvas()
            rr.polygon(color(self.color), self.stat_vertices)
            return r

        @staticmethod
        def get_tangent_offset(xorigin, yorigin, angle, length):
            return int(xorigin + (cos(radians(angle)) * length)), int(yorigin - (sin(radians(angle)) * length))

    class Mirage(renpy.Displayable):
        def __init__(self, displayable, resize=(1280, 720), ycrop=8, amplitude=0, wavelength=0, **kwargs):
            super(Mirage, self).__init__(**kwargs)
            displayable = Transform(displayable, size=resize)
            self.displayable = list()
            for r in xrange(resize[1]/ycrop):
                y = r * ycrop
                self.displayable.append((Transform(displayable, crop=(0, y, resize[0], ycrop)), y))

            # self.image = [Transform(renpy.easy.displayable(image), crop=(0, i+1, width, 2)) for i in range(height/2)]
            self.amplitude = amplitude
            self.wavelength = wavelength
            self.W2 = config.screen_width * .5

            zoom_factor = 1.0 - self.amplitude
            self.x_zoom_factor = 1 / zoom_factor

        # Stretch each scanline horizontally, oscillating from +amplitude to -amplitude across specified wavelength
        # Shift oscillation over time by st
        def render(self, width, height, st, at):
            math = store.math
            render = renpy.Render(width, height)

            h = 1.0
            for scanline in self.displayable:
                # math.sin(x) returns the sine of x radians
                t = Transform(scanline[0], xzoom = self.x_zoom_factor + (math.sin(h / self.wavelength + st) * self.amplitude), yzoom = (1.01))
                h += 1.0
                child_render = t.render(0, 0, st, at)
                cW, cH = child_render.get_size()
                # final amount subtracted from h sets y placement
                render.blit(child_render, ((self.W2) - (cW * .5), scanline[1]))
            renpy.redraw(self, 0)
            return render

    class ConsitionSwitcher(renpy.Displayable):
        """This plainly switches conditions without reshowing the image/changing any variables by calling update_d() method.

        Presently this is only used in BE to handle BG conditioning.
        This may have to be expanded to handle ATL instructions properly. Just a test for now.
        """
        def __init__(self, start_condition, conditions=None, **kwargs):
            """Expects a dict of conditions={"string": displayable}

            Default is Null() unless specified otherwise.
            """
            super(ConsitionSwitcher, self).__init__(**kwargs)
            if not isinstance(conditions, dict):
                self.conditions = {"default": Null()}
            else:
                self.conditions = {c: renpy.easy.displayable(d) for c, d in conditions.iteritems()}
                self.conditions["default"] = conditions.get("default", Null())

            self.d = self.conditions.get(start_condition, self.conditions["default"])

        def change(self, condition):
            self.d = self.conditions.get(condition, self.conditions["default"])

        def render(self, width, height, st, at):
            render = renpy.Render(width, height)
            cr = self.d.render(width, height, st, at)
            render.blit(cr, (0, 0))
            renpy.redraw(self, 0)
            return render

        def visit(self):
            return self.conditions.values()

    # scaling functions/objects
    class ProportionalScale(im.Scale):
        pass # FIXME obsolete
    """
        '''Resizes a renpy image to fit into the specified width and height.
        The aspect ratio of the image will be conserved.'''
        def __init__(self, im, width, height, bilinear=True, **properties):
            super(ProportionalScale, self).__init__(im, width, height, bilinear, **properties)

        def load(self):
            #if isinstance(self.image, renpy.display.im.ImageBase) and "buildings" in self.image.filename:
            #    devlog.warn("Loading building image: %s" % self.image)
            surf = im.cache.get(self.image)
            width, height = surf.get_size()

            ratio = min(self.width/float(width), self.height/float(height))
            width = int(round(ratio*width))
            height = int(round(ratio*height))

            if self.bilinear:
                try:
                    renpy.display.render.blit_lock.acquire()
                    rv = renpy.display.scale.smoothscale(surf, (width, height))
                finally:
                    renpy.display.render.blit_lock.release()
            else:
                try:
                    renpy.display.render.blit_lock.acquire()
                    rv = renpy.display.pgrender.transform_scale(surf, (width, height))
                finally:
                    renpy.display.render.blit_lock.release()

            return rv
    """
    class TransformScale(im.Scale):
        """
        Resizes a renpy image to fit into the specified width and height using the scaling algorithm of the Transform
        The aspect ratio of the image will be conserved.
        """
        def __init__(self, im, width, height):
            super(TransformScale, self).__init__(im, width, height, bilinear=False)

        def load(self):
            surf = im.cache.get(self.image)
            width, height = surf.get_size()

            ratio = min(self.width/float(width), self.height/float(height))
            width = int(round(ratio*width))
            height = int(round(ratio*height))

            try:
                renpy.display.render.blit_lock.acquire()
                return renpy.display.pgrender.transform_scale(surf, (width, height))
            finally:
                renpy.display.render.blit_lock.release()

    class SmoothScale(im.Scale):
        """
        Resizes a renpy image to fit into the specified width and height using bilinear scaling.
        The aspect ratio of the image will be conserved.
        """
        def __init__(self, im, width, height):
            super(SmoothScale, self).__init__(im, width, height, bilinear=True)

        def load(self):
            surf = im.cache.get(self.image)
            width, height = surf.get_size()

            ratio = min(self.width/float(width), self.height/float(height))
            width = int(round(ratio*width))
            height = int(round(ratio*height))

            try:
                renpy.display.render.blit_lock.acquire()
                return renpy.display.scale.smoothscale(surf, (width, height))
            finally:
                renpy.display.render.blit_lock.release()

    class Appearing(renpy.Displayable):
        """
        An object which changes its opaque based on the distance of the mouse pointer
        """
        def __init__(self, child, opaque_distance, transparent_distance, start_alpha=.0, **kwargs):
            # Pass additional properties on to the renpy.Displayable
            # constructor.
            super(Appearing, self).__init__(**kwargs)

            # The child.
            self.child = renpy.displayable(child)

            # The distance at which the child will become fully opaque, and
            # where it will become fully transparent. The former must be less
            # than the latter.
            self.opaque_distance = opaque_distance
            self.transparent_distance = transparent_distance
            self.start_alpha = start_alpha

            # The alpha channel of the child.
            self.alpha = start_alpha

            # The width and height of us, and our child.
            self.width = 0
            self.height = 0

        def render(self, width, height, st, at):
            # Create a transform, that can adjust the alpha channel of the
            # child.
            t = Transform(child=self.child, alpha=self.alpha)

            # Create a render from the child.
            child_render = renpy.render(t, width, height, st, at)

            # Get the size of the child.
            self.width, self.height = child_render.get_size()

            # Create the render we will return.
            render = renpy.Render(self.width, self.height)

            # Blit (draw) the child's render to our render.
            render.blit(child_render, (0, 0))

            # Return the render.
            return render

        def event(self, ev, x, y, st):
            # Compute the distance between the center of this displayable and
            # the mouse pointer. The mouse pointer is supplied in x and y,
            # relative to the upper-left corner of the displayable.
            distance = math.hypot(x - (self.width / 2), y - (self.height / 2))

            # Base on the distance, figure out an alpha.
            if distance <= self.opaque_distance:
                alpha = 1.0
            elif distance >= self.transparent_distance:
                alpha = self.start_alpha
            else:
                alpha = 1.0 - 1.0 * (distance - self.opaque_distance) / (self.transparent_distance - self.opaque_distance)

            # If the alpha has changed, trigger a redraw event.
            if alpha != self.alpha:
                self.alpha = alpha
                renpy.redraw(self, 0)

            # Pass the event to our child.
            return self.child.event(ev, x, y, st)

        def visit(self):
            return [ self.child ]

    class PyTGFX(_object):
        """ A Namespace for gfx related objects/functions
        """
        #def get_displayable_size(d):
        #    d = renpy.easy.displayable(d)
        #    w, h = d.render(0, 0, 0, 0).get_size()
        #    return int(round(w)), int(round(h))

        scale_img = TransformScale
        smooth_scale_img = SmoothScale

        @staticmethod
        def sepia_img(img):
            return im.Sepia(img)
        #sepia_img = im.Sepia

        @staticmethod
        def bright_img(img, scale):
            """
            Proportionally resizes an image (preserving tha aspect ratio)
            """
            return im.MatrixColor(img, im.matrix.brightness(scale))

        @staticmethod
        def scale_content(img, maxwidth, maxheight):
            if check_movie_extension(img):
                return PyTGFX.scale_movie(img, maxwidth, maxheight)
            else:
                return PyTGFX.scale_img(img, maxwidth, maxheight)

        @staticmethod
        def sepia_content(img):
            """
            Proportionally resizes an image (preserving tha aspect ratio)
            """
            if isinstance(img, Movie):
                return img # FIXME
            else:
                return im.Sepia(img)

        @staticmethod
        def bright_content(img, scale):
            """
            Proportionally resizes an image (preserving tha aspect ratio)
            """
            if isinstance(img, Movie):
                return img # FIXME
            else:
                return im.MatrixColor(img, im.matrix.brightness(scale))

        movie_cache = {}
        @staticmethod
        def scale_movie(path, maxwidth, maxheight):
            global NEXT_MOVIE_CHANNEL
            new_tag = (path, maxwidth, maxheight)
            for tag, movie in PyTGFX.movie_cache.itervalues():
                if tag == new_tag:
                    return movie
            idx = NEXT_MOVIE_CHANNEL
            NEXT_MOVIE_CHANNEL = (NEXT_MOVIE_CHANNEL+1)%MOVIE_CHANNEL_COUNT
            movie = Movie(channel="%02dmovie"%idx, play=path, size=(maxwidth, maxheight))
            PyTGFX.movie_cache[idx] = (new_tag, movie)
            return movie

        def gen_randmotion(count, dist, delay):
            args = [ ]
            for i in xrange(count):
                args.append(anim.State(i, None,
                                       Position(xpos=randint(-dist, dist),
                                                ypos=randint(-dist, dist),
                                                xanchor='left',
                                                yanchor='top',
                                                )))

            for i in xrange(count):
                for j in xrange(count):
                    if i == j:
                        continue

                    args.append(anim.Edge(i, delay, j, MoveTransition(delay)))
            return anim.SMAnimation(0, *args)

        def double_vision_on(img, alpha=.5, count=10, dist=7, delay=.4, clear_scene=True):
            if clear_scene:
                renpy.scene()
            renpy.show(img)
            renpy.show(img, at_list=[Transform(alpha=alpha), PyTGFX.gen_randmotion(count, dist, delay)], tag="blur_image")

        def double_vision_off():
            renpy.hide("blur_image")
            renpy.with_statement(dissolve)

    class GFXOverlay(renpy.Displayable):
        """Quick and reliable way to show overlay of displayable.

        The idea is to create a way to show any number of quick-paced displayable,
            without restrictions often posed by screens and renpy.show.
        I am planning to use this in BE, interactions and whenever we can, really,
            to improve game experience.
        """
        def __init__(self, **kwargs):
            super(GFXOverlay, self).__init__(**kwargs)

            self.active = True

            self.gfx = dict() # killtime: gfx
            self.parse_gfx = dict() # unique_key: [callable, kwargs]
            self.sfx = dict() # startingdelay: sfx

        def add_atl(self, atl, duration, kwargs=None):
            if kwargs is None:
                kwargs = {}

            if duration in self.parse_gfx:
                # Ensure unique key:
                duration += uniform(.0001, .0002)

            self.parse_gfx[duration] = (atl, kwargs)

            renpy.redraw(self, 0)

        def add_sfx(self, sfx, delay=0):
            if delay in self.sfx:
                # Ensure unique key:
                delay += uniform(.0001, .0002)
            # Convert delay to string so we can make a proper timed events of it.
            self.sfx[str(delay)] = sfx

            renpy.redraw(self, 0)

        def be_taunt(self, attacker, skill, duration):
            if getattr(skill, "kind", None) != "assault":
                return

            if isinstance(attacker, Mob):
                simpe_taunts = ["(Makes threatening noises)",
                                "(Looks murderous)",
                                "Urgggg!",
                                "Aaiiiieeee!",
                                "Argghhh!",
                                "Hnrgggg!",
                                "Grrr!"]
            else:
                simpe_taunts = ["You shall perish!",
                                "Die b*tch!",
                                "Disappear!",
                                "Don't take this personally...",
                                "Eat this!",
                                "I don't think you're going to like this",
                                "Let's dance!",
                                "I'm gonna teach you some manners",
                                "It's too late to run",
                                "Doesn't look like much of a challenge",
                                "You're history!",
                                "Have a nice day, hehe!",
                                "Enjoy this!"]

            taunt = choice(simpe_taunts)

            kwargs = dict()

            # Portrait:
            fi = Fixed(xysize=(70, 70), pos=(10, -60))
            frame = Transform("content/gfx/frame/p_frame.png", size=(70, 70))
            fi.add(frame)
            portrait = Transform(attacker.angry_portrait, align=(.5, .5))
            fi.add(portrait)

            fixed = Fixed(xysize=(220, 40))
            fixed.add(fi)

            frame = "content/gfx/interface/buttons/sl_idle.png"
            fixed.add(Transform(frame, size=(220, 40)))
            fixed.add(Text(taunt, size=25,
                           style="be_notify",
                           align=(.5, .5)))

            x, y = battle.get_cp(attacker, type="center")
            kwargs["pos"] = absolute(x), absolute(y)
            kwargs["yoffset"] = -200
            kwargs["d"] = fixed
            kwargs["start"] = 0
            kwargs["duration"] = duration
            self.add_atl(char_stats_effect, duration, kwargs)
            # self.add_sfx("content/sfx/sound/events/bing.ogg", uniform(.5, 1.0))

        def notify(self, msg=None, type="text", tkwargs=None, duration=1.0):
            kwargs = {}

            if type == "fight": # Instead of a text, images are used.
                img = choice(["fight_0", "fight_1", "fight_2"])
                img = renpy.displayable(img)
                self.add_sfx("content/sfx/sound/be/fight.ogg", duration*.5)
            else: # we use text as last resort:
                if tkwargs is None:
                    tkwargs = {}

                default = {"style": "be_notify"}
                default.update(tkwargs)
                img = Text(str(msg), **default)

            kwargs["pos"] = absolute(config.screen_width/2), absolute(0)
            kwargs["yoffset"] = randint(200, 200)
            kwargs["d"] = img
            kwargs["start"] = 0
            kwargs["duration"] = duration
            self.add_atl(char_stats_effect, duration, kwargs)

        def mod_stat(self, stat, value, char):
            if isinstance(char, Char):
                if stat == "affection":
                    self.affection_mod(value)
                elif stat == "disposition":
                    self.disposition_mod(value)
                elif stat == "joy":
                    self.joy_mod(value)
                else:
                    self.mod_char_stat(stat, value, char)
            elif char == hero:
                self.mod_mc_stat(stat, value)

        def mod_char_stat(self, stat, value, char):
            kwargs = dict()

            # Portrait:
            fi = Fixed(xysize=(70, 70))
            frame = Frame("content/gfx/frame/MC_bg.png", 5, 5)
            fi.add(frame)

            portrait = "sad" if value < 0 else "happy"
            portrait = char.show("portrait", portrait, resize=(65, 65), type="reduce", cache=True)
            portrait = Transform(portrait, align=(.5, .5))
            fi.add(portrait)

            fixed = Fixed(xysize=(160, 36))
            if stat == "exp":
                fixed.add(Transform(fi, pos=(5, -15)))
                frame = "content/gfx/interface/icons/exp.webp"
                fixed.add(frame)
            else:
                fixed.add(Transform(fi, pos=(10, -60)))
                frame = "content/gfx/interface/buttons/sl_idle.png"
                fixed.add(frame)

                fixed.add(Text(stat.capitalize(), size=25,
                               style="proper_stats_text", color="#79CDCD",
                               align=(.5, .5)))

            color = "red" if value < 0 else "green"
            fixed.add(Text("%+g" % value, style="proper_stats_value_text", color=color,
                           size=40, pos=(155, 10)))

            time_offset = self.get_time_offset()
            kwargs["pos"] = absolute(randint(150, 900)), absolute(720)
            kwargs["yoffset"] = randint(-400, -350)
            kwargs["d"] = fixed
            kwargs["start"] = time_offset
            duration = uniform(1.8, 2.2)
            kwargs["duration"] = duration
            self.add_atl(char_stats_effect, duration, kwargs)
            self.add_sfx("content/sfx/sound/events/bing.ogg", .5+time_offset)

        def get_time_offset(self):
            offset = 0
            showing = len(self.gfx) + len(self.parse_gfx)

            if showing:
                offset = showing*.3
                offset = min(.7, offset)
            return offset

        def mod_mc_stat(self, stat, value):
            kwargs = dict()

            fixed = Fixed(xysize=(160, 36))
            if stat == "exp":
                t = Transform("content/gfx/interface/icons/exp.webp", align=(.5, .5))
                fixed.add(t)
            else:
                fixed.add(Transform("content/gfx/frame/rank_frame.png", size=(160, 36)))
                fixed.add(Text(stat.capitalize(), size=25,
                               style="proper_stats_text",
                               color="#79CDCD",
                               align=(.5, .5)))

            color = "red" if value < 0 else "green"
            fixed.add(Text("%+g" % value, style="proper_stats_value_text", color=color,
                           size=40, align=(.9, .5), yoffset=25))

            time_offset = self.get_time_offset()
            kwargs["pos"] = randint(150, 900), -50
            kwargs["yoffset"] = randint(130, 170)
            kwargs["d"] = fixed
            kwargs["start"] = time_offset
            duration = uniform(1.8, 2.2)
            kwargs["duration"] = duration
            self.add_atl(mc_stats_effect, duration, kwargs)
            self.add_sfx("content/sfx/sound/events/bing.ogg", .5+time_offset)

        def affection_mod(self, value):
            value = round_int(value)
            kwargs = dict()
            time_offset = self.get_time_offset()

            fixed = Fixed(xysize=(130, 130))
            if value > 0:
                d = Transform("hearts_flow", size=(130, 130), align=(.5, .5))
                fixed.add(d)
                d = Text(str(value), font="fonts/rubius.ttf", color="deeppink",
                         size=60, align=(.5, .5))
                fixed.add(d)
                kwargs["pos"] = randint(680, 920), randint(500, 600)
                kwargs["yoffset"] = randint(-300, -250)
                self.add_sfx("content/sfx/sound/female/uhm.mp3", .3+time_offset)
            else:
                d = Transform("shy_blush", size=(130, 130), align=(.5, .5))
                fixed.add(d)
                d = Text(str(value), font="fonts/rubius.ttf", color="blue",
                         size=60, align=(.5, .5))
                fixed.add(d)
                kwargs["pos"] = randint(680, 920), randint(100, 200)
                kwargs["yoffset"] = randint(250, 300)

            kwargs["d"] = fixed
            kwargs["start"] = time_offset
            duration = uniform(1.2, 2.3)
            kwargs["duration"] = duration
            self.add_atl(affection_effect, duration, kwargs)

        def disposition_mod(self, value):
            value = round_int(value)
            kwargs = dict()
            time_offset = self.get_time_offset()

            if value > 0:
                fixed = Fixed(xysize=(130, 130))
                d = Transform("hearts_rise", size=(130, 130), align=(.5, .5))
                fixed.add(d)
                d = Text(str(value), font="fonts/rubius.ttf", color="pink",
                         size=60, align=(.5, .5))
                fixed.add(d)
                kwargs["pos"] = randint(680, 920), randint(500, 600)
                kwargs["yoffset"] = randint(-300, -250)
            else:
                fixed = Fixed(xysize=(130, 130))
                d = Transform("shy_blush", size=(130, 130), align=(.5, .5))
                fixed.add(d)
                d = Text(str(value), font="fonts/rubius.ttf", color="lightblue",
                         size=60, align=(.5, .5))
                fixed.add(d)
                kwargs["pos"] = randint(680, 920), randint(100, 200)
                kwargs["yoffset"] = randint(250, 300)

            kwargs["d"] = fixed
            kwargs["start"] = time_offset
            duration = uniform(1.2, 2.3)
            kwargs["duration"] = duration
            self.add_atl(affection_effect, duration, kwargs)

        def joy_mod(self, value):
            value = round_int(value)
            kwargs = dict()
            time_offset = self.get_time_offset()

            if value > 0:
                fixed = Fixed(xysize=(130, 130))
                d = Transform("music_note", size=(60, 60), align=(.5, .5))
                fixed.add(d)
                d = Text(str(value), font="fonts/rubius.ttf", color="aqua",
                         size=60, align=(.5, .5))
                fixed.add(d)
                kwargs["pos"] = randint(680, 920), randint(500, 600)
                kwargs["yoffset"] = randint(-300, -250)
            else:
                fixed = Fixed(xysize=(130, 130))
                d = Transform("shy_blush", size=(130, 130), align=(.5, .5))
                fixed.add(d)
                d = Text(str(value), font="fonts/rubius.ttf", color="silver",
                         size=60, align=(.5, .5))
                fixed.add(d)
                kwargs["pos"] = randint(680, 920), randint(100, 200)
                kwargs["yoffset"] = randint(250, 300)

            kwargs["d"] = fixed
            kwargs["start"] = time_offset
            duration = uniform(1.2, 2.3)
            kwargs["duration"] = duration
            self.add_atl(affection_effect, duration, kwargs)

        def random_find(self, item, mode='gold', count=None):
            # Can be used to show that we've found something.
            kwargs = {}

            if mode == 'gold':
                main_icon = PyTGFX.scale_img("content/gfx/interface/images/money_bag3.png",
                                   80, 80)
                main_text = Text(str(item), font="fonts/rubius.ttf", color="gold",
                                         size=40)
                support_icon = PyTGFX.scale_img("content/gfx/interface/icons/gold.png",
                              40, 40)
            elif mode == 'work':
                main_icon = PyTGFX.scale_img("content/gfx/interface/images/work.webp",
                              80, 80)
                main_text = Text(str(item), font="fonts/rubius.ttf", color="gold",
                                         size=40)
                support_icon = PyTGFX.scale_img("content/gfx/interface/icons/gold.png",
                              40, 40)
            elif mode == 'fishy':
                main_icon = PyTGFX.scale_content(item.icon,
                              80, 80)
                main_text = Text(item.id, font="fonts/rubius.ttf", color="gold",
                                         size=40)
                support_icon = PyTGFX.scale_img("content/gfx/images/fishy.png",
                              60, 60)
            elif mode == 'item':
                main_icon = PyTGFX.scale_content(item.icon,
                              80, 80)
                main_text = Text(item.id, font="fonts/rubius.ttf", color="gold",
                                         size=40)
                if count is not None:
                    fixed = VBox()
                    fixed.add(Transform(main_text, xalign=.5))
                    fixed.add(Text("x %d" % count, font="fonts/rubius.ttf", color="gold",
                                         size=40, xalign=.5))
                    main_text = fixed

                support_icon = PyTGFX.scale_img("content/gfx/interface/buttons/IT2.png",
                              40, 40)
            elif mode == 'items':
                # Different mode, similar to MC's Stats:
                main_icon = PyTGFX.scale_content(item.icon,
                              80, 80)
                main_text = Text(item.id, font="fonts/rubius.ttf", color="gold",
                                         size=40)
                if count is not None:
                    fixed = VBox()
                    fixed.add(Transform(main_text, xalign=.5))
                    fixed.add(Text("x %d" % count, font="fonts/rubius.ttf", color="gold",
                                         size=40, xalign=.5))
                    main_text = fixed
                    
                fixed = Fixed(xysize=(100, 100))
                fixed.add(Transform(main_icon, align=(.5, .5)))
                fixed.add(Transform(main_text, align=(.5, 1.0)))

                time_offset = (len(self.gfx) + len(self.parse_gfx))*.5
                kwargs["pos"] = randint(150, 900), -50
                kwargs["yoffset"] = randint(130, 170)
                kwargs["d"] = fixed
                kwargs["start"] = time_offset
                duration = uniform(1.8, 2.2)
                self.gfx = dict() # killtime: gfx

                kwargs["duration"] = duration
                self.add_atl(mc_stats_effect, duration, kwargs)
                self.add_sfx("content/sfx/sound/events/bing.ogg", uniform(.5, 1.0)+time_offset)
                return

            fixed = Fixed(xysize=(100, 100))
            fixed.add(Transform(main_icon, align=(.5, .5)))
            fixed.add(Transform(main_text, align=(.5, 1.0)))
            kwargs["pos"] = 640, 500
            kwargs["yoffset"] = -250
            kwargs["d"] = fixed
            kwargs["start"] = 0
            duration = 2.0
            kwargs["duration"] = duration
            self.add_atl(found_effect, duration, kwargs)
            self.add_sfx("content/sfx/sound/events/go_for_it.mp3")

            # Generate some side effects :D
            support_icon = Transform(support_icon, align=(.5, .5))
            for i in range(randint(15, 25)):
                kwargs = {}
                kwargs["pos"] = randint(500, 750), randint(500, 600)
                kwargs["yoffset"] = randint(-500, -450)

                kwargs["d"] = support_icon
                kwargs["start"] = uniform(.0, 1.0)
                duration = uniform(1.5, 2.0)
                kwargs["duration"] = duration
                self.add_atl(found_effect, duration, kwargs)

        def render(self, width, height, st, at):
            r = renpy.Render(width, height)
            if not self.active:
                return r

            for duration, data in self.parse_gfx.items():
                callable, kwargs = data
                start_delay = kwargs.get("start", 0)
                kwargs["start"] += st
                killtime = start_delay + st + duration
                if killtime in self.gfx:
                    killtime += uniform(.0001, .0002)
                self.gfx[killtime] = callable(**kwargs)

                del self.parse_gfx[duration]

            for killtime, gfx in self.gfx.items():
                # temp = Text(str(gfx), align=(.5, .5))
                r.place(gfx)

                if killtime <= st:
                    del self.gfx[killtime]
                    renpy.redraw(self, 0)

            for delay, sfx in self.sfx.items():
                if isinstance(delay, basestring):
                    del self.sfx[delay]
                    delay = float(delay) + st
                    self.sfx[delay] = sfx
                elif delay <= st:
                    renpy.play(sfx, channel="audio")
                    del self.sfx[delay]

            if self.gfx or self.sfx:
                renpy.redraw(self, .02)
            return r

        def clear(self, mode="all"):
            if mode in ("sfx", "all"):
                self.sfx = dict()
            if mode in ("gfx", "all"):
                self.gfx = dict()
                self.parse_gfx = dict()


    class HitlerKaputt(renpy.Displayable):
        def __init__(self, displayable, crops, neg_range=(-8, -1), pos_range=(1, 8), **kwargs):
            """
            Crops the displayable and sends the bits flying...
            """
            super(HitlerKaputt, self).__init__(**kwargs)
            self.displayable = displayable
            self.crops = crops # This is doubled...

            self.args = None

            self.neg_range = neg_range
            self.pos_range = pos_range

            self.width = 0
            self.height = 0

        def render(self, width, height, st, at):
            if not st:
                self.args = None

            if not self.args:
                t = Transform(self.displayable)
                child_render = renpy.render(t, width, height, st, at)
                self.width, self.height = child_render.get_size()

                # Size of one crop:
                crop_xsize = int(round(self.width / float(self.crops)))
                crop_ysize = int(round(self.height / float(self.crops)))

                # The list:
                args = []
                choices = range(*self.neg_range) + range(*self.pos_range)

                for r in xrange(0, self.crops):
                    for c in xrange(0, self.crops):

                        x = c * crop_xsize
                        y = r * crop_ysize

                        direction = choice(choices), choice(choices)

                        args.append([Transform(t, rotate=randint(0, 90), crop=(x, y, crop_xsize, crop_ysize)),
                                     [x, y],      # coords
                                     direction])  # direction
                self.args = args

            render = renpy.Render(self.width, self.height)
            for cr, coords, direction in self.args:
                cr = renpy.render(cr, width, height, st, at)
                render.blit(cr, tuple(coords))
                coords[0] += direction[0]
                coords[1] += direction[1]
            renpy.redraw(self, 0)
            return render


    class FilmStrip(renpy.Displayable):
        """Simple UDD that cuts a spreadsheet and animates it.
        """
        def __init__(self, displayable, framesize, gridsize, delay, include_frames=None, exclude_frames=None, loop=True, reverse=False, **kwargs):
            """Creates a list of Transforms ready to be rendered. This may take up a little bit more memory than doing the same on the fly but it should be faster.

            @params:
            displayable: Displayable we will cut, usually a path to image.
            framesize: A size of a single frame in pixels.
            gridsize: Height and width of the grid as a tuple: (5, 5) means 5 by 5 frames.
            delay: Time between each frame in seconds.
            include_frames: If not None, espects a list of frames from the sheet that should be incuded in animation. Frames are numbered 0 to z where 0 is the top-left frame and z id the bottom-right frame.
            exclude_frames: If not None, frames to exclude. Rules same as above. Included frame will exclude all but themselves and excuded frames will never be shown.
            loop: Loop endlessly if True, will show the animation once if False.
            reverse: Reverse the order of frames in animation.
            """
            super(FilmStrip, self).__init__(**kwargs)
            self.displayable = renpy.easy.displayable(displayable)
            width, height = framesize
            cols, rows = gridsize

            total_frames = cols * rows

            i = 0

            # Arguments to Animation
            args = []

            for r in range(0, rows):
                for c in range(0, cols):
                    if include_frames and i not in include_frames:
                        i = i + 1
                        continue
                    if exclude_frames and i in exclude_frames:
                        i = i + 1
                        continue

                    x = c * width
                    y = r * height
                    args.append(Transform(self.displayable, crop=(x, y, width, height)))

                    i = i + 1

                    if i == total_frames:
                        break

                if i == total_frames:
                    break

            # Reverse the list:
            if reverse:
                args.reverse()

            self.width, self.height = width, height
            self.frames = args
            self.delay = delay
            self.index = 0
            self.loop = loop

        def render(self, width, height, st, at):
            if not st:
                self.index = 0

            t = self.frames[self.index]

            if self.index == len(self.frames) - 1:
                if self.loop:
                    self.index = 0
            else:
                self.index += 1

            render = renpy.Render(self.width, self.height)
            child_render = t.render(width, height, st, at)
            render.blit(child_render, (0, 0))
            renpy.redraw(self, self.delay)
            return render

        def visit(self):
            return [self.displayable]


    class AnimateFromList(renpy.Displayable):
        def __init__(self, args, loop=True, **kwargs):
            super(AnimateFromList, self).__init__(**kwargs)
            self.images = list()
            for t in args:
                self.images.append([renpy.easy.displayable(t[0]), t[1]])
            self.loop = loop
            self.index = 0

        def render(self, width, height, st, at):
            if not st:
                self.index = 0

            # We just need to animate once over the list, no need for any calculations:
            try:
                index = self.index
                img = self.images[index]
                child_render = img[0].render(width, height, st, at)

                w, h = child_render.get_size()

                render = renpy.Render(w, h)
                render.blit(child_render, (0, 0))
                renpy.redraw(self, img[1])

                index += 1
                if self.loop and index >= len(self.images):
                    index = 0
                self.index = index

                return render
            except IndexError:
                return renpy.Render(0, 0)

        def visit(self):
            return [img[0] for img in self.images]



init -100 python:
    class DisplayableSwitcher(renpy.Displayable, NoRollback):
        DEFAULT = {"d": Null(), "start_st": 0, "pause_st": 0, "force_pause": 0, "force_resume": 0}

        """This plainly switches displayable without reshowing the image/changing any variables by calling change method.
        """

        def __init__(self, start_displayable="default", displayable=None, conditions=None, always_reset=True, **kwargs):
            """Expects a dict of displayable={"string": something we can show in Ren'Py}

            Default is Null() unless specified otherwise.
            """
            super(DisplayableSwitcher, self).__init__(**kwargs)
            if not isinstance(displayable, dict):
                self.displayable = {"default": self.DEFAULT.copy()}
            else:
                self.displayable = {}
                for s, d in displayable.iteritems():
                    self.displayable[s] = self.DEFAULT.copy()
                    d = renpy.easy.displayable(d)
                    if isinstance(d, ImageReference):
                        d = renpy.display.image.images[(d.name)]
                    self.displayable[s]["d"] = d
                    if isinstance(d, renpy.atl.ATLTransformBase):
                        self.displayable[s]["atl"] = d.copy()

                self.displayable["default"] = displayable.get("default", self.DEFAULT.copy())

            if not isinstance(conditions, (tuple, list)):
                self.conditions = None
            else:
                self.conditions = OrderedDict()
                for c, a in conditions:
                    code = renpy.python.py_compile(c, 'eval')
                    self.conditions[code] = a # @Alex: Should prolly be code here instead of c as a key

            self.always_reset = always_reset
            self.d = self.displayable[start_displayable]
            self.animation_mode = "normal"
            self.last_st = 0
            self.last_condition = None

        def per_interact(self):
            if self.conditions:
                for c, v in self.conditions.iteritems():
                    if renpy.python.py_eval_bytecode(c):
                        s = v[0]
                        if len(v) > 1:
                            mode = v[1]
                        else:
                            mode = "normal"

                        # We only want to change if we got a new condition:
                        if self.last_condition != c or (self.always_reset and "reset" in v):
                            self.last_condition = c
                            self.change(s, mode)
                        break

        def change(self, s, mode="normal"):
            self.d = self.displayable[s]

            self.animation_mode = mode
            if mode == "reset":
                self.d["force_restart"] = 1
            elif mode == "pause":
                self.d["pause_st"] = self.last_st - self.d["start_st"]
            elif mode == "resume":
                self.d["force_resume"] = 1

        def render(self, width, height, st, at):
            if not st:
                for d in self.displayable.itervalues():
                    d["start_st"] = 0
                    d["pause_st"] = 0

            rp = store.renpy

            self.last_st = st

            if self.animation_mode == "reset":
                if self.d["force_restart"]:
                    self.d["force_restart"] = 0
                    if "atl" in self.d:
                        self.d["d"].take_execution_state(self.d["atl"])
                        self.d["d"].atl_st_offset = st
                    else:
                        self.d["start_st"] = st
                st = st - self.d["start_st"] if not "atl" in self.d else st
            elif self.animation_mode in ("pause", "show_paused"):
                st = self.d["pause_st"]
            elif self.animation_mode == "resume":
                if self.d["force_resume"]:
                    self.d["force_resume"] = 0
                    self.d["start_st"] = st
                st = st - self.d["start_st"] + self.d["pause_st"]

            d = self.d["d"]
            render = rp.Render(width, height)
            render.place(d)

            rp.redraw(self, 0)
            return render

        def visit(self):
            return [v["d"] for v in self.displayable.values()]


    class MovieLooped(renpy.display.video.Movie):
        """Play Movie Sprites without loops. Until Ren'Py permits that by defualt, this can be used.
        """
        def __init__(self, *args, **kwargs):
            super(MovieLooped, self).__init__(*args, **kwargs)
            self.loops = kwargs.get("loops", 1)

        def play(self, old):
            if old is None:
                old_play = None
            else:
                old_play = old._play

            if self._play != old_play:
                if self._play:
                    renpy.audio.music.play([self._play]*self.loops, channel=self.channel, loop=False, synchro_start=True)

                    if self.mask:
                        renpy.audio.music.play([self.mask]*self.loops, channel=self.mask_channel, loop=False, synchro_start=True)

                else:
                    renpy.audio.music.stop(channel=self.channel)

                    if self.mask:
                        renpy.audio.music.stop(channel=self.mask_channel)




init python:
    def get_size(d):
        d = renpy.easy.displayable(d)
        w, h = d.render(0, 0, 0, 0).get_size()
        return int(round(w)), int(round(h))

    def _shake_function(trans, st, at, dt=.5, dist=256): #dt is duration timebase, dist is maximum shake distance in pixel
        if st <= dt:
            trans.xoffset = int((dt-st)*dist*(.5-random.random())*2)
            trans.yoffset = int((dt-st)*dist*(.5-random.random())*2)
            return .01
        else:
            return None

    def get_random_image_dissolve(time):
        dir = content_path("gfx", "masks")
        transitions = [file for file in listfiles(dir) if check_image_extension(file)]
        if transitions:
            image = os.path.join(dir, choice(transitions))
            return ImageDissolve(image, time)
