init -1 python:
    # GUI Logic ---------------------------------------------------------------------------------------------
    # One func:
    def point_in_poly(poly, x, y):

        n = len(poly)
        inside = False

        p1x, p1y = poly[0]
        for i in xrange(n+1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    class GuiHeroProfile(_object):
        '''The idea is to try and turn the while loop into the function
        I want girl_meets and quests to work in similar way
        This is basically practicing :)
        '''
        def __init__(self):
            self.finance_filter = "day"
            self.came_from = None # To enable jumping back to where we originally came from.

    class PytGallery(_object):
        """
        PyTFall gallery to view girl's pictures and controls
        """
        def __init__(self, char):
            self.girl = char
            self.default_imgsize = (940, 680)
            self.tag = "profile"
            tagsdict = tagdb.get_tags_per_character(self.girl)
            self.tagsdict = OrderedDict(sorted(tagsdict.items(), key=itemgetter(1), reverse=True))
            self.pathlist = list(tagdb.get_imgset_with_all_tags([char.id, "profile"]))
            self.set_img(self.pathlist[0])

        def screen_loop(self):
            while 1:
                result = ui.interact()

                if result[0] == "image":
                    index = self.pathlist.index(self.imagepath)
                    if result[1] == "next":
                        index += 1
                    elif result[1] == "previous":
                        index -= 1 
                    self.set_img(self.pathlist[index % len(self.pathlist)])
                elif result[0] == "tag":
                    self.tag = result[1]
                    self.pathlist = list(tagdb.get_imgset_with_all_tags([self.girl.id, result[1]]))
                    self.set_img(self.pathlist[0])
                elif result[0] == "view_trans":
                    gallery.trans_view()
                elif result[0] == "control":
                    if result[1] == 'return':
                        break

        @property
        def image(self):
            return ProportionalScale(os.sep.join([self.girl.path_to_imgfolder, self.imagepath]), self.imgsize[0], self.imgsize[1])

        def set_img(self, path):
            self.imagepath = path
            if self.tag in ("vnsprite", "battle_sprite"):
                self.imgsize = self.girl.get_sprite_size(self.tag)
            else:
                self.imgsize = self.default_imgsize

            self.tags = " | ".join([i for i in tagdb.get_image_tags(path)])

        def trans_view(self):
            """
            I want to try and create some form of automated transitions/pics loading for viewing mechanism.
            Transitions are taken from Ceramic Hearts.
            """
            # Get the list of files for transitions first:

            dir = content_path("gfx", "masks")
            all_transitions = [os.path.join(dir, file) for file in listfiles(dir) if check_image_extension(file)]

            # Get the images:
            all_images = self.pathlist * 1
            shuffle(all_images)

            renpy.hide_screen("gallery")
            renpy.with_statement(dissolve)

            renpy.music.play("content/sfx/music/reflection.mp3", fadein=1.5)

            loop = True
            images = transitions = None
            while loop:
                if not images:
                    images = all_images * 1
                if not transitions:
                    transitions = all_transitions * 1

                image = images.pop()
                image = os.path.join(self.girl.path_to_imgfolder, image)
                x, y = renpy.image_size(image)
                rndm = randint(5, 7)
                tag = str(random.random())

                if x > y:
                    ratio = config.screen_height/float(y)
                    if int(round(x * ratio)) <= config.screen_width:
                        image = ProportionalScale(image, config.screen_width, config.screen_height)
                        renpy.show(tag, what=image, at_list=[truecenter, simple_zoom_from_to_with_linear(1.0, 1.5, rndm)])
                    else:
                        image = ProportionalScale(image, 10000, config.screen_height)
                        renpy.show(tag, what=image, at_list=[move_from_to_align_with_linear((.0, .5), (1.0, .5), rndm)])
                elif y > x:
                    ratio = 1366/float(x)
                    if int(round(y * ratio)) <= 768:
                        image = ProportionalScale(image, config.screen_width, config.screen_height)
                        renpy.show(tag, what=image, at_list=[truecenter, simple_zoom_from_to_with_linear(1.0, 1.5, rndm)])
                    else:
                        image = ProportionalScale(image, config.screen_width, 10000)
                        renpy.show(tag, what=image, at_list=[truecenter, move_from_to_align_with_linear((.5, 1.0), (.5, .0), rndm)])
                else:
                    image = ProportionalScale(image, config.screen_width, config.screen_height)
                    renpy.show(tag, what=image, at_list=[truecenter, simple_zoom_from_to_with_linear(1.0, 1.5, rndm)])

                renpy.with_statement(ImageDissolve(transitions.pop(), 3), always=True)

                loop = renpy.call_screen("gallery_trans")
                renpy.hide(tag)

            renpy.music.stop(fadeout=1.0)
            renpy.show_screen("gallery")
            renpy.with_statement(dissolve)


    class CharsSortingForGui(_object):
        """Class we use to sort and filter character for the GUI.

        - Reset is done by a separate function we bind to this class.
        """
        def __init__(self, reset_callable, container=None):
            """
            reset_callable: a funcion to be called without arguments that would return a full, unfiltered list of items to be used as a default.
            container: If not None, we set this contained to self.sorted every time we update. We expect a list with an object and a field to be used with setattr.
            """
            self.reset_callable = reset_callable
            self.target_container = container
            self.sorted = list()

            self.status_filters = set()
            self.action_filters = set()
            self.class_filters = set()
            self.occ_filters = set()
            self.location_filters = set()
            self.home_filters = set()
            self.work_filters = set()

            self.sorting_order = None
            self.sorting_desc = False

        def clear(self):
            self.update(self.reset_callable())
            self.status_filters = set()
            self.action_filters = set()
            self.class_filters = set()
            self.occ_filters = set()
            self.location_filters = set()
            self.home_filters = set()
            self.work_filters = set()

        def update(self, container):
            self.sorted = container
            if self.target_container:
                setattr(self.target_container[0], self.target_container[1], container)

        def filter(self):
            filtered = self.reset_callable()

            # Filters:
            if self.status_filters:
                filtered = [c for c in filtered if c.status in self.status_filters]
            if self.action_filters:
                filtered = [c for c in filtered if c.action in self.action_filters]
            if self.class_filters:
                filtered = [c for c in filtered if c.traits.basetraits.intersection(self.class_filters)]
            if self.occ_filters:
                filtered = [c for c in filtered if self.occ_filters.intersection(c.gen_occs)]
            if self.location_filters:
                filtered = [c for c in filtered if c.location in self.location_filters]
            if self.home_filters:
                filtered = [c for c in filtered if c.home in self.home_filters]
            if self.work_filters:
                filtered = [c for c in filtered if c.workplace in self.work_filters]

            # Sorting:
            order = self.sorting_order
            if order is not None:
                if is_skill(order):
                    filtered.sort(key=lambda x: x.get_skill(order), reverse=self.sorting_desc)
                elif is_stat(order):
                    filtered.sort(key=lambda x: x.get_stat(order), reverse=self.sorting_desc)
                else:
                    filtered.sort(key=attrgetter(order), reverse=self.sorting_desc)

            self.update(filtered)


    class CoordsForPaging(_object):
        """ This class setups up x, y coordinates for items in content list.

        We use this in DragAndDrop.
        Might be I'll just use this in the future to handle the whole thing.
        For now, this will be used in combination with screen language.
        """
        def __init__(self, content, columns=2, rows=6, size=(100, 100), xspacing=10, yspacing=10, init_pos=(0, 0)):
            self.content = content
            self.page = 0
            self.page_size = columns*rows

            self.pos = list()
            x = init_pos[0]
            for c in xrange(columns):
                y = init_pos[1]
                for r in xrange(rows):
                    self.pos.append((x, y))
                    y = y + size[1] + yspacing
                x = x + size[0] + xspacing

        def __len__(self):
            return len(self.content)

        def __iter__(self):
            """We return a list of tuples of [(item, pos), (item, pos), ...]"""
            page = self.page_content
            pos = self.pos[:len(page)]
            return iter(zip(page, pos))

        def __getitem__(self, index):
            # Minding the page we're on!
            return self.content[self.page*self.page_size + index]

        def __nonzero__(self):
            return bool(self.content)

        def get_pos(self, item):
            """Retruns a pos of an item on current page"""
            return self.pos[self.page_content.index(item)]

        # Paging:
        def next_page(self):
            """Next page"""
            self.page += 1
            if self.page >= self.max_page:
                self.page = 0

        def prev_page(self):
            """Previous page"""
            self.page -= 1
            if self.page < 0:
                self.last()

        def last_page(self):
            """Last page"""
            self.page = max(self.max_page - 1, 0)

        def first_page(self):
            self.page = 0

        @property
        def max_page(self):
            return len(self.paged_items)

        @property
        def paged_items(self):
            items = []
            for start in xrange(0, len(self.content), self.page_size):
                items.append(self.content[start:start+self.page_size])
            return items

        @property
        def page_content(self):
            """Get content for current page"""
            items = self.paged_items
            try:
                return items[self.page]
            except IndexError:
                idx = len(items)-1
                if idx >= 0:
                    self.page = idx
                    return items[idx]
                else:
                    self.page = 0
                    return []

        def add(self, item):
            if item not in self.content:
                self.content.append(item)
                return True

        def remove(self, item):
            if item in self.content:
                self.content.remove(item)


    def dragged(drags, drop):
        # Simple func we use to manage drag and drop in team setups and maybe more in the future.
        drag = drags[0]
        x, y = drag.old_position[0], drag.old_position[1]

        if not drop:
            drag.snap(x, y, delay=.2)
            return

        item = drag.drag_name
        src_container = item.get_flag("dnd_drag_container")
        dest_container = drop.drag_name
        if dest_container == src_container:
            drag.snap(x, y, delay=.2)
            return

        if not dest_container.add(item):
            drag.snap(x, y, delay=.4)
            return

        src_container.remove(item)
        drag.snap(x, y)
        drag.unfocus()
        return True
