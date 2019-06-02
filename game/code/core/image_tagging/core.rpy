# The image tagging system of PyTFall:
init -9 python:
    class TagDatabase(_object):
        '''Maps image tags to image paths.

        sample entry of self.tagmap:
        tag : set([relative path to image 1, relative path to image 2, ...])
        '''
        def __init__(self):
            # maps image tags to sets of image paths
            tags_dict = load_db_json("image_tags.json")
            tags_dict = {k:v for g in [group["tags"] for group in tags_dict.values()] for k, v in g.iteritems()}
            #all_tags = [v for g in [group["tags"] for group in tags_dict.values()] for v in g.values()]
            all_tags = tags_dict.values()

            self.tags_dict = tags_dict
            self.all_tags = set(all_tags)
            self.tagmap = {tag: set() for tag in all_tags}

            # stores relative paths to untagged images
            self.untagged = set()

        def load_tags_folder(self, folder, path):
            img_set = set()
            tags_dict = self.tags_dict
            tagmap = self.tagmap
            for fn in os.listdir(path):
                if not check_image_extension(fn):
                    continue
                # Add filename to girls id:
                img_set.add(fn)

                # Add filename to the recognized tags:
                try:
                    tags = fn.split("-")[1:]
                    tags[-1] = tags[-1].split(".")[0]
                    for tag in tags:
                        tn = tags_dict.get(tag, None)
                        if tn is not None:
                            tagmap[tn].add(fn)
                        else:
                            char_debug("Unknown image tag: %s, fn: %s, path: %s" % (tag, fn, path))
                except IndexError:
                    char_debug("Invalid file path for image: %s in folder %s" % (fn, path))
            tagmap[folder] = img_set

        # access the database
        #-----------------------------------
        def get_image_tags(self, image_path):
            """Returns a list of tags bound to the image.
            """
            image_name = image_path.split(os.sep)[-1]
            image_name_base = image_name.split(".")[0]
            obfuscated_tags = image_name_base.split("-")[1:]
            tags_dict = self.tags_dict
            return [t for t in (tags_dict.get(tag, None) for tag in obfuscated_tags) if t is not None]

        def get_imgset_with_tag(self, tag):
            '''Returns a set of paths to images, all of which are tagged
            '''
            return self.tagmap.get(tag, set()).copy()

        def get_imgset_with_all_tags(self, tags):
            '''Returns a set of images that are all tagged with all specified tags.
            '''
            data = [self.get_imgset_with_tag(tag) for tag in tags]
            return set.intersection(*data)

        def remove_excluded_images(self, data, excludedtags):
            """Get rid of all images tagged with excludedtags.
            """
            exclude = [self.get_imgset_with_tag(tag) for tag in excludedtags]
            exclude = set.union(*exclude)
            data.difference_update(exclude)
            return data

        def get_tags_per_character(self, character):
            """
            Returns a dict of tags as keys and amount of tags in the database
            character = character object
            4 Post-@ code review: Is this a stupid way of doing it? ==> It was...
            """
            tags = defaultdict(int)
            images = self.get_imgset_with_tag(character.id)
            for img in images:
                tags_per_path = self.get_image_tags(img)
                for tag in tags_per_path:
                    tags[tag] += 1
            return tags

        def get_tags_per_path(self, path):
            """
            Returns a set of tags got from the image path in the database
            path = path to a file
            """
            tags = set([])
            for tag, images in self.tagmap.iteritems():
                if path in images:
                    tags.add(tag)
            return tags

        # dump the database
        #-----------------------------------
        def map_images_to_tags(self):
            '''Returns a dict of image path keys and sets of tags as values.
            '''
            imgmap = {}
            for tag, imgpaths in self.tagmap.iteritems():
                for p in imgpaths:
                    try:
                        tagset = imgmap[p]
                    except KeyError:
                        tagset = set()
                        imgmap[p] = tagset
                    tagset.add(tag)
            return imgmap

        def dump_json(self, targetfiles=[]):
            '''Dumps the tag information into tags.json files.

            targetfiles is a list of paths to files.
            If targetfiles is empty, a single tags.json file will be written to
            the game directory and will contain the complete database contents.
            '''
            # ensure that all target files have valid paths
            if not targetfiles:
                targets = {os.path.join(gamedir, "tags.json") : {}}
            else:
                targets = {}
                for p in targetfiles:
                    normpath = normalize_path(p)
                    targets[normpath] = {}
            for t in targets.keys():
                dirpath = os.path.dirname(t)
                if not os.path.exists(dirpath):
                    tagslog.error("directory does not exist: %s" % dirpath)
                    targets.pop(t)
            # separate database content by targetdir
            targetdirs = {}
            for t in targets:
                td = os.path.dirname(t)
                targetdirs[td] = t
            imgmap = self.map_images_to_tags()
            for imgpath in imgmap:
                taglist = sorted(imgmap[imgpath])
                normimgpath = normalize_path(imgpath)
                found = False
                for td in targetdirs:
                    if normimgpath.startswith(td):
                        targetfile = targetdirs[td]
                        targets[targetfile][imgpath] = taglist
                        found = True
                        break
                if not found:
                    tagslog.error("could not find target directory for %s" % imgpath)
            # write one JSON file per target directory
            for t in targets:
                imgmap = targets[t]
                tagslog.debug("writing tags to %s" % t)
                tagsfile = open(t, "w")
                json.dump(imgmap, tagsfile, indent=4, sort_keys=True)


    class Tagger(_object):
        '''Backend supporting the in-game tagger
        '''
        def __init__(self):
            self.pagesize = 30

            tag_groups = load_db_json("image_tags.json")
            self.tag_groups = tag_groups
            # map of tag to (tag-key, color) pairs
            self.tagsmap = {v:(k, color) for g, color in [(group["tags"], group["color"]) for group in tag_groups.values()] for k, v in g.iteritems()}

            self.selected_groups = list()
            self.tag_options = list()

            self.load_tag_chars("chars")

            char = next(iter(self.all_chars.itervalues()))
            self.select_char(char)

            if "pytfall" in globals():
                self.return_action = [Show("s_menu", main_menu=True), With(dissolve)]
            else:
                self.return_action = Return(None)

        def load_tag_chars(self, group):
            """load characters from the game context or from the json files
            :param group: one of 'rchars', 'chars', 'npcs', 'fighters'
            """
            if "traits" not in globals():
                store.traits = load_traits()
                store.battle_skills = load_battle_skills()
                load_traits_context()
            all_chars = load_characters(group)

            self.all_chars = all_chars
            self.list_group = group

        def base_folder(self):
            group = tagr.list_group
            if group == "rchars":
                return "random"
            if group == "chars":
                return "Naruto"
            if group == "npcs":
                return "thugs"
            # fighters
            return "json_adjusted"

        def group_fields(self):
            if self.char_group == "rchars":
                return (("id", "text"),
                        ("desc", "text"),
                        ("origin", "text"),
                        ("race", "Unknown"),
                        ("full_race", "text"),
                        ("color", "text"),
                        ("what_color", "text"),
                        ("height", "average"),
                        ("gender", "female"),
                        ("gold", "number"),
                        #("basetraits", "list"),
                        ("personality", "Deredere"),
                        ("breasts", "Average Boobs"),
                        ("penis", "Average Dick"),
                        ("body", "text"),
                        #("blocked_traits", "list"),
                        #("ab_traits", "list"),
                        #("elements", "list"),
                        #("traits", "list"),
                        ("random_traits", "list"),
                        ("default_attack_skill", "Fist Attack"),
                        #("magic_skills", "list"),
                        #("status", "text"),
                        #("location", "text"),
                        #("tier", "number"),
                        #("item_up", "text"),
                        #("arena_willing", "text"),
                        )
            else: #if self.char_group in ("chars", "npcs"):
                return (("id", "text"),
                        ("name", "text"),
                        ("nickname", "text"),
                        ("fullname", "text"),
                        ("desc", "text"),
                        ("origin", "text"),
                        ("race", "Unknown"),
                        ("full_race", "text"),
                        ("color", "text"),
                        ("what_color", "text"),
                        ("height", "average"),
                        ("gender", "female"),
                        ("gold", "number"),
                        ("basetraits", "list"),
                        ("personality", "Deredere"),
                        ("breasts", "Average Boobs"),
                        ("penis", "Average Dick"),
                        ("body", "text"),
                        #("blocked_traits", "list"),
                        #("ab_traits", "list"),
                        ("elements", "list"),
                        ("traits", "list"),
                        #("random_traits", "list"),
                        ("default_attack_skill", "Fist Attack"),
                        ("magic_skills", "list"),
                        ("status", "free"),
                        ("location", "text"),
                        ("tier", "number"),
                        ("item_up", "text"),
                        ("arena_willing", "text"),
                        )
            #else: # "female"/"male" _fighters
            #    return (("id", "text"),
            #            ("basetraits", "list"),
            #            ("gender", "female"),
            #            )
                

        def select_char(self, char):
            self.char = char
            self.char_group = self.list_group
            self.images = sorted(tagdb.get_imgset_with_tag(char["id"]))
            #images = [images[i:i+30] for i in range(0, len(images), 30)]
            self.imagespage = 0
            self.path_to_pic = char["_path_to_imgfolder"]
            self.pic = self.tagz = self.oldtagz = None

        def create_char(self, folder, id):
            folder = os.path.normpath(folder)
            id = os.path.normpath(id)
            if os.sep in id or os.sep in folder:
                return "Subfolders are not supported!"
            if id in self.all_chars:
                return "ID Already Exists!"
            group = self.list_group
            dir = group
            dir = content_path(dir)
            dir = os.path.join(dir, folder)
            # create base folder
            try:
                os.mkdir(dir)
            except:
                pass
            dir = os.path.join(dir, id)
            # create json
            char = OrderedDict([("id", id), ("_path_to_imgfolder", dir)])
            self.char_edit = char
            self.char_group = group
            self.save_json()
            # create folder
            try:
                os.mkdir(dir)
            except:
                # existing folder -> load the files
                self.load_tag_chars(group)
            # select the new char
            self.select_char(char)
            self.all_chars[id] = char

        def select_image(self, image):
            self.pic = image
            self.tagz = tagdb.get_image_tags(image)
            self.oldtagz = self.tagz[:]

        def save_image(self, pic=None):
            if pic is None:
                pic = self.pic
                tagz = self.tagz
                update_tagger = True
            else:
                tagz = tagdb.get_image_tags(pic)
                update_tagger = False

            n = pic.split(".")[0].split("-")[0] + "-"         # ID-
            n += "-".join([self.tagsmap[k][0] for k in tagz]) # tagz
            n += "." + pic.split(".")[-1]                     # .extension

            self.rename_tag_file(pic, n, update_tagger)
            return n

        def next_page(self):
            self.imagespage += 1
            self.imagespage %= ((len(self.images)-1) / self.pagesize) + 1

        def previous_page(self):
            self.imagespage -= 1
            self.imagespage %= ((len(self.images)-1) / self.pagesize) + 1

        def page_images(self):
            return self.images[self.imagespage*self.pagesize:(self.imagespage+1)*self.pagesize]

        def select_tag_group(self, group):
            self.selected_groups.append(group)
            tags = self.tag_groups[group]["tags"]
            self.tag_options.extend(tags.itervalues())

        def remove_tag_group(self, group):
            self.selected_groups.remove(group)
            tags = self.tag_groups[group]["tags"]
            for tag in tags.itervalues():
                self.tag_options.remove(tag)

        def tag_group_all(self):
            groups = self.selected_groups
            if groups:
                for g in self.selected_groups[:]:
                    self.remove_tag_group(g)
            else:
                for g in self.tag_groups:
                    self.select_tag_group(g)

        def sort_tags(self):
            self.tag_options.sort()

        @staticmethod
        def is_valid(image_path):
            tagz = len(tagdb.get_image_tags(image_path))
            alltagz = image_path.split(os.sep)[-1].split(".")[0].split("-")
            return tagz != 0 and tagz == len(alltagz) - 1

        def generate_ids(self, repair):
            # generate ID prefix for files without one in the chars folder
            images = self.images

            num = len(images)
            num = max(4, int(math.log(num, 16)) + 1)

            reserved = set()
            badimages = []
            for img in images:
                prefix = img.split("-")[0]
                if len(prefix) == num:
                    try:
                        idx = int(prefix, 16)
                        if idx not in reserved:
                            reserved.add(idx)
                            continue
                    except:
                        pass
                badimages.append(img)

            images = badimages

            result = dict()
            idx = 0
            num = "{:0>%d}" % num
            for img in images:
                while idx in reserved:
                    idx += 1
                n = num.format(hex(idx)[2:].upper())
                n += "-" + img

                self.rename_tag_file(img, n, False)
                result[img] = n
                idx += 1

            if repair:
                for img, n in result.iteritems():
                    result[img] = self.save_image(n)

            # update tagger
            images = self.images
            for img, n in result.iteritems():
                images[images.index(img)] = n
            images.sort()
            self.imagespage = 0
            self.pic = self.tagz = self.oldtagz = None

        def rename_tag_file(self, curr_file, new_file, update_tagger=True):
            oldf = os.path.join(self.path_to_pic, curr_file)
            newf = os.path.join(self.path_to_pic, new_file)
            try:
                os.rename(oldf, newf)

                # update tagdb
                charid = self.char["id"]
                oldtagz = tagdb.get_image_tags(curr_file)
                oldtagz.append(charid)
                tagz = tagdb.get_image_tags(new_file)
                tagz.append(charid)
                for tag in oldtagz:
                    tagdb.tagmap[tag].remove(curr_file)
                for tag in tagz:
                    tagdb.tagmap[tag].add(new_file)

                # update tagger
                if update_tagger:
                    tagz.pop() # charid

                    # select image
                    self.tagz = tagz
                    self.oldtagz = tagz[:]
                    self.pic = new_file

                    self.images[self.images.index(curr_file)] = new_file
            except Exception as e:
                e = unicode(str(e), errors='replace')
                e = e.replace("[", "[[")#.replace("]", "]]")
                renpy.show_screen("message_screen", u"Failed to rename the file!\n current file: %s\n new file: %s\n reason: %s" % (curr_file, new_file, e))

        def save_json(self):
            json_data = self.char_edit
            fields = self.group_fields()
            for field, type in fields:
                value = json_data.get(field, None)
                if type == "list":
                    if not value:
                        json_data.pop(field, None)
                elif type in ["text", "number"]:
                    if value == "":
                        json_data.pop(field, None)
                else:
                    if value == type:
                        json_data.pop(field, None)

            path = json_data.pop("_path_to_imgfolder")
            _path = path.split(os.sep)
            folder = _path[-1]
            _path[-1] = "data_" + folder + ".json"
            _path = os.sep.join(_path)
            with open(_path, 'w') as outfile:
                json.dump([json_data], outfile, indent=4)

            # restore path-to-imgfolder
            json_data["_path_to_imgfolder"] = path
            self.char = json_data
            self.char_edit = None

    # enable logging
    if DEBUG_LOG:
        tagslog = devlog.getChild("tags")
