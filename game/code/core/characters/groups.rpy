# classes and methods for groups of Characters:
init -8 python:
    class Delegator(_object):
        def __init__(self, l, at, remedy=None, *args, **kwargs):
            self._attrs = ['lst', '_remedy', '_at']
            self.lst = l
            self._at = at
            self._remedy = {} if remedy is None else remedy

        @property
        def _first(self):
            return next(iter(self.lst))

        def _defer(self, arr, at=""):
            # get unique types:
            at = self._at + at
            remedy = self._remedy

            first = next(iter(arr))

            if isinstance(first, (list, tuple)):
                typical = len(first)
            elif isinstance(first, (dict, set)):
                typical = set(first)
            elif isinstance(first, Char): # also includes rChar
                typical = Char
            elif isinstance(first, basestring): # also includes unicode
                typical = basestring
            else:
                typical = type(first)

            for var in arr:
                if isinstance(typical, type):
                    if not isinstance(var, typical) or cmp(first, var) != 0:
                        break
                elif isinstance(var, (list, tuple)):
                    if not isinstance(typical, int) or typical != len(var):
                        break
                elif isinstance(var, (dict, set)):
                    if not isinstance(typical, set) or any(k not in typical for k in var):
                        break
            else:
                # when reached, identical: keys(dict), elements(set), en(list/tuple) => delegated
                if isinstance(typical, type): # ..or both type and value => returned
                    return first

                bracket = "{}" if isinstance(typical, set) else "[]"
                return DeDist(arr, remedy=remedy, at="%s%s" % (at, bracket))

            # else try to get a single value for a list
            rem = self._remedy.get('flatten', None)
            if rem is not None and at in rem:
                return list(frozenset([item for sublist in arr for item in sublist]))

            if not at in remedy:
                renpy.error("%s\n%s\n%s" % (at, str(typical), str(arr)))

            rem = remedy[at]
            if isclass(rem) and issubclass(rem, Delegator):
                return rem(l=arr, at=at, remedy=remedy)

            # In case of an error here: define a remedy for the unlisting
            return rem(arr) if callable(rem) else rem

        def __getattr__(self, item):
            """ an undefined attribute was requested from the group """
            # required for pickle
            if item.startswith('__') and item.endswith('__'):
                return super(Delegator, self).__getattr__(item)

            if [m for m in inspect.getmembers(self._first, inspect.ismethod) if item == m[0]]:

                def wrapper(*args, **kwargs):
                    arr = [getattr(c, item)(*args, **kwargs) for c in self.lst]
                    return self._defer(arr=arr, at=".%s()" % item)

                return wrapper

            return self._defer(arr=[getattr(c, item) for c in self.lst], at=".%s" % item)

        def __setattr__(self, k, v):
            if k != '_attrs' and k not in self._attrs:
                for c in self.lst:
                    setattr(c, k, v)
            else:
                super(Delegator, self).__setattr__(k, v)


    class DeDist(Delegator):
        def __init__(self, *args, **kwargs):
            super(DeDist, self).__init__(*args, **kwargs)

        def __getitem__(self, k):
            return self._defer(arr=[d[k] for d in self.lst])

        def __setitem__(self, k, v):
            for d in self.lst:
                d[k] = v

        def __delitem__(self, k):
            for d in self.lst:
                del d[k]

        def __iter__(self):
            if isinstance(self._first, dict):
                return iter({k: self._defer(arr=[x[k] for x in self.lst]) for k in self._first})

            return iter(self._defer(arr=[list(x)[i] for x in self.lst]) for i in range(len(self._first)))

        def __len__(self):
            return len(self._first)


    class PytGInv(Delegator):
        def __init__(self, inv):
            super(PytGInv, self).__init__(l=inv, at="inventory")
            self._attrs.extend(('slot_filter', 'page'))
            self.slot_filter = False
            self.page = 0

        def __getitem__(self, item):
            if isinstance(item, list):
                return 0
            return min([x[item] for x in self.lst])

        @property
        def filters(self):
            return list(frozenset([item for sublist in self.lst for item in sublist.filters]))

        @property
        def filtered_items(self):
            return set([item for sublist in self.lst for item in sublist.filtered_items])

        @property
        def page_content(self):
            ps = self.page_size
            start = self.page*ps
            return list(self.filtered_items)[start : (start+ps)]

        @property
        def max_page(self):
            ps = self.page_size
            l = len(self.filtered_items)
            return int(l / ps) + (l % ps > 0)

        def next(self):
            """Next page"""
            self.page += 1
            if self.page >= self.max_page:
                self.page = 0

        def prev(self):
            """Previous page"""
            self.page -= 1
            if self.page < 0:
                self.last()

        def first(self):
            """First page"""
            self.page = 0

        def last(self):
            """Last page"""
            self.page = max(self.max_page - 1, 0)

        def remove(self, item, amount=1):
            """ see Inventory.remove(): False means not enough items """
            return all([x.remove(item, amount) for x in self.lst])

        def apply_filter(self, filt):
            if filt in ('next', 'prev'):
                for x in self.lst:
                    x.apply_filter(filt)
            else:
                self.slot_filter = filt
                for x in self.lst:
                    if filt in x.filters:
                        x.apply_filter(filt)
                    else:
                        x.filtered_items = []
            self.page = 0

        def append(self, item, amount=1):
            all([x.append(item, amount) for x in self.lst])


    class PytGroup(Delegator):
        def __init__(self, chars):
            remedy = {
                ".eqslots{}": self._ordered_on_abundance, ".auto_equip()": self._list_for_caller, ".home": "various",
                ".status": "various", ".location": "various", ".workplace": "various", ".action": "Several actions",
                ".autobuy": [], ".front_row": [], ".autoequip": "various", ".job": "Several jobs",
                ".pp": "theirs", ".pd": "their", ".op": "them",
                ".autocontrol{}": [], ".sex_acts{}": [], ".miscblock": [],
                ".flag()": False, ".has_flag()": False, ".is_available": False,
                ".allowed_to_define_autobuy": False, ".allowed_to_define_autoequip": False,
                ".allowed_to_view_personal_finances": False, ".last_known_aeq_purpose": "various",
                "flatten": [".traits", ".attack_skills", ".magic_skills"]
            }
            super(PytGroup, self).__init__(l=chars, remedy=remedy, at="")
            self._attrs.extend(['_inventory', 'img', 'portrait', 'nickname', 'effects', '_stats',
                                'unselected'])

            self._inventory = PytGInv([c.inventory for c in self.lst])
            self.img = "content/gfx/interface/images/group.png"
            self.portrait = "content/gfx/interface/images/group_portrait.png"
            self.nickname = "group"
            self.effects = {}
            stat_remedy = {'.stats._get_stat()': self._average, '.stats._raw_skill()': self._average}
            self._stats = Delegator(l=[c.stats for c in self.lst], remedy=stat_remedy, at=".stats")
            self.unselected = set()

        def __new__(cls, chars):
            return next(iter(chars)) if len(chars) == 1 else super(PytGroup, cls).__new__(cls, chars)

        # for pickle & __new__ (__getnewargs__ and __repr__)
        def __getnewargs__(self):
            return (PytGroup.__repr__(self),)

        def __repr__(self):
            return '<PytGroup %r>' % self.lst

        def __len__(self):
            return len(self.lst)

        @property
        def gen_occs(self):
            chars = list(self.lst)
            occs = set(chars[0].gen_occs)
            for c in chars:
                occs = occs.intersection(c.gen_occs)
            return list(occs)

        def get_valid_jobs(self):
            chars = list(self.lst)
            jobs = set(chars[0].get_valid_jobs())
            for c in chars:
                jobs = jobs.intersection(c.get_valid_jobs())
            return list(jobs)

        def get_wanted_jobs(self):
            chars = list(self.lst)
            jobs = set(chars[0].get_wanted_jobs())
            for c in chars:
                jobs = jobs.intersection(c.get_wanted_jobs())
            return list(jobs)

        def get_willing_jobs(self):
            chars = list(self.lst)
            jobs = set(chars[0].get_willing_jobs())
            for c in chars:
                jobs = jobs.intersection(c.get_willing_jobs())
            return list(jobs)

        @property
        def name(self):
            return "A group of %d" % len(self)

        @property
        def all(self):
            return sorted(list(self.lst) + list(self.unselected))

        @property
        def shuffled(self):
            return random.sample(self.lst, len(self))

        @property
        def inventory(self):
            self._inventory.lst = [c.inventory for c in self.lst]
            return self._inventory

        @property
        def stats(self):
            self._stats.lst = [c.stats for c in self.lst]
            return self._stats

        @property
        def given_items(self):
            return {k:min([c.given_items[k] for c in self.lst]) for k in self._first.given_items}

        @property
        def wagemod(self):
            return round_int(self._average([c.wagemod for c in self.lst]))
        @wagemod.setter
        def wagemod(self, v):
            for c in self.lst:
                c.wagemod = v

        def show(self, what, resize=(None, None), cache=True):
            if what == "portrait":
                what = self.portrait
            elif what != self.img:
                what = self.img

            return ProportionalScale(what, resize[0], resize[1])

        # remedy functions below here
        def _list_for_caller(self, arr):
            return arr

        def _ordered_on_abundance(self, arr):
            return sorted(set(arr), reverse=True, key=lambda e: arr.count(e) if e else -1)

        def _average(self, arr):
            return round(float(sum(arr)) / max(len(arr), 1), 1)
