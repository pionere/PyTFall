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
        pass # FIXME obsolete

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

        @property
        def image(self):
            return PyTGFX.scale_content(os.path.join(self.girl.path_to_imgfolder, self.imagepath), self.imgsize[0], self.imgsize[1])

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
            all_images = self.pathlist
            shuffle(all_images)

            renpy.hide_screen("gallery")
            renpy.with_statement(dissolve)

            renpy.music.play("content/sfx/music/reflection.mp3", fadein=1.5)

            tag = "gallery_tv_img"
            loop = first = True
            images = transitions = None
            while loop:
                if not images:
                    images = all_images * 1
                if not transitions:
                    transitions = all_transitions * 1

                image = images.pop()
                image = os.path.join(self.girl.path_to_imgfolder, image)
                x, y = renpy.image_size(image)

                rndm = randint(3, 5)
                ratio = min(config.screen_width/float(x), config.screen_height/float(y))
                if ratio < 1.5:
                    # image fits to the screen (can be resized without much distortion)
                    if ratio < 1.2:
                        # almost exact fit to the screen -> add at least a bit of zoom-effect
                        zoom_from = ratio - .4
                    else:
                        # the image must be resized anyway -> zoom from original size to the screen
                        zoom_from = 1.0
                    image = PyTGFX.scale_img(image, x, y)
                    at_list=[truecenter, simple_zoom_from_to_with_linear(zoom_from, ratio, rndm)]
                else:
                    # image is too small -> zoom from resized to the original image
                    image = PyTGFX.scale_img(image, config.screen_width, config.screen_height)
                    at_list=[truecenter, simple_zoom_from_to_with_linear(1.0, 1.0/ratio, rndm)]

                renpy.show(tag, what=image, at_list=at_list)
                if first is True:
                    # first time run without transition effect
                    first = False
                else:
                    renpy.with_statement(ImageDissolve(transitions.pop(), 3), always=True)

                loop = renpy.call_screen("gallery_trans")
                renpy.hide(tag)

            renpy.music.stop(fadeout=1.0)
            renpy.show_screen("gallery")
            renpy.with_statement(dissolve)


    class PagerGui(_object):
        def __init__(self, content, page_size=10):
            self.pager_content = content

            self.page = 0
            self.page_size = page_size
            
        def next_page(self):
            self.page += 1

        def prev_page(self):
            self.page -= 1

        def max_page(self):
            """Max page assuming page_size > 1"""
            return (len(self.pager_content)-1)/self.page_size

        def last_page(self):
            """Last page"""
            self.page = self.max_page()

        def first_page(self):
            self.page = 0

        def page_content(self):
            start = self.page*self.page_size
            return self.pager_content[start:start+self.page_size]

    class CharsSortingForGui(PagerGui):
        """Class we use to sort and filter character for the GUI.

        - Reset is done by a separate function we bind to this class.
        """
        def __init__(self, content, page_size=10):
            """
            content: the list of all chars
            container: If not None, we set this container to self.sorted every time we update. We expect a list with an object and a field to be used with setattr.
            """
            super(CharsSortingForGui, self).__init__(content, page_size)

            self.all_content = content

            self.sorting_order = None
            self.sorting_desc = False

            self.clear()

        def clear(self):
            self.pager_content = self.all_content
            self.status_filters = set()
            self.action_filters = set()
            self.class_filters = set()
            self.occ_filters = set()
            self.location_filters = set()
            self.home_filters = set()
            self.work_filters = set()

        def filter(self):
            filtered = self.all_content

            # Filters:
            filters = self.status_filters
            if filters:
                filtered = [c for c in filtered if c.status in filters]
            filters = self.action_filters
            if filters:
                filtered = [c for c in filtered if c.action in filters]
            filters = self.class_filters
            if filters:
                filtered = [c for c in filtered if c.traits.basetraits.intersection(filters)]
            filters = self.occ_filters
            if filters:
                filtered = [c for c in filtered if filters.intersection(c.gen_occs)]
            filters = self.location_filters
            if filters:
                filtered = [c for c in filtered if c.location in filters]
            filters = self.home_filters
            if filters:
                filtered = [c for c in filtered if c.home in filters]
            filters = self.work_filters
            if filters:
                filtered = [c for c in filtered if c.workplace in filters]

            # Sorting:
            order = self.sorting_order
            if order is not None:
                if is_skill(order):
                    key = lambda x: x.get_skill(order)
                elif is_stat(order):
                    key = lambda x: x.get_stat(order)
                else:
                    key = attrgetter(order)
                filtered = sorted(filtered, key=key, reverse=self.sorting_desc) # make sure the original content is left intact

            self.pager_content = filtered

        # TODO extended functionality for the pager (add/remove)
        # might not be the best place...
        def add(self, item):
            if item not in self.all_content:
                self.all_content.append(item)
                self.pager_content.append(item)
                return True

        def remove(self, item):
            if item in self.all_content:
                self.all_content.remove(item)
                if item in self.pager_content:
                    self.pager_content.remove(item)

    class CoordsForPaging(_object):
        pass # FIXME obsolete

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
