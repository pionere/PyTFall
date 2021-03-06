init -9 python:
    class STATIC_ITEM():
        __slots__ = ("FIGHTING_AEQ_PURPOSES", "AEQ_PURPOSES", "TRAIT_TO_AEQ_PURPOSE", "NOT_USABLE", "NOT_TRANSFERABLE", "NOT_SELLABLE")
        FIGHTING_AEQ_PURPOSES = set()   # \
        AEQ_PURPOSES = dict()           # - Initialized at startup by load_aeq_purposes()
        TRAIT_TO_AEQ_PURPOSE = dict()   # /
        NOT_USABLE = set(["gift", "quest", "loot", "resources"])
        NOT_TRANSFERABLE = set(["gift", "quest"])
        NOT_SELLABLE = set(["quest"])

    ####### Equipment Classes ########
    class Item(_object):
        def __init__(self):
            self.desc = ""
            self.slot = "consumable"
            self.type = None
            self.mod = {}
            self.mod_skills = {}
            self.max = {}
            self.min = {}
            self.addtraits = []
            self.removetraits = []
            self.add_be_spells = []
            self.attacks = None
            self.addeffects = []
            self.removeeffects = []
            self.goodtraits = set()
            self.badtraits = set()
            self.pref_class = []

            # Rules:
            self.usable = None
            self.transferable = None
            self.sellable = None
            self.be = False # could be used in battle engine

            # mostly not used atm, decides if we should hide the item effects;
            # does hide effects for gifts which have not been used at least once, becoming False afterwards
            #self.hidden = True optional field
            self.jump_to_label = None
            self.price = 0
            # self.gender = 'unisex' optional field
            self.unique = "" # Should be girls id in case of unique item.
            self.statmax = False
            self.skillmax = False
            self.infinite = False
            self.locations = []
            self.chance = 50
            self.eqchance = 0 # equip chance

            self.tier = 0     # Tier of an item to match class tier, 0 - 4 is the range.
            # self.level = 0 We're using tiers for now.
            # Level is how an item compares to it's relatives
            # I'd like this to be set for all items one days
            # Excalibur for example is 10, the shittiest sword is 1
            # Same can be done for food, scrolls and practically any item in the game.
            # Groups may even start at high values, if items are really good and/or expensive
            # And no shit item exists within the same group
            # Basically, you when we check for level, we want to know how the item
            # is valued in the game on scale from 0 - 10.

            # BE attributes:
            self.be_modifiers = None
            # self.evasion_bonus = 0 # Needs a int, will be used a percentage (1 = 1%)
            # self.ch_multiplier = 0 # Chance of critical hit multi...
            # self.damage_multiplier = 0

            # self.defence_bonus = {} # Delivery! Not damage types!
            # self.defence_multiplier = {}
            # self.delivery_bonus = {} Expects a k/v pair of type: multiplier This is direct bonus added to attack power.
            # self.delivery_multiplier = {}
            # why is it commented out though? BE attributes are widely used by items...

        def init(self):
            if not hasattr(self, "id"):
                raise Exception("Missing id of an item!")

            # Rules:
            if self.usable is None:
                if self.slot in STATIC_ITEM.NOT_USABLE:
                    self.usable = False
                else:
                    self.usable = True

            if self.transferable is None:
                if self.slot in STATIC_ITEM.NOT_TRANSFERABLE:
                    self.transferable = False
                else:
                    self.transferable = True

            if self.sellable is None:
                if self.slot in STATIC_ITEM.NOT_SELLABLE or self.price == 0:
                    self.sellable = False
                else:
                    self.sellable = True

            if self.type is None:
                self.type = self.slot

            if self.slot == 'consumable':
                if not hasattr(self, 'cblock'):
                    self.cblock = False

                if not hasattr(self, 'ctemp'):
                    self.ctemp = False
                # Disabling maxes if ctemp is active:
                if self.ctemp:
                    self.skillmax = False
                    self.statmax = False
            elif self.slot == 'misc':
                if not hasattr(self, 'mtemp'):
                    self.mtemp = 10
                if not hasattr(self, 'mdestruct'):
                    self.mdestruct = False
                if not hasattr(self, 'mreusable'):
                    self.mreusable = False
            else:
                # Ensures normal behavior:
                self.statmax = False
                self.skillmax = False

            # validate and link references so we do not have to check runtime
            for skill in self.mod_skills:
                if not is_skill(skill):
                    raise Exception("Invalid mod skill '%s' for item %s!" % (skill, self.id))

            if self.removetraits:
                try:
                    self.removetraits = [traits[t] for t in self.removetraits]
                except:
                    raise Exception("Invalid trait to remove '%s' for item %s!" % (t, self.id))
            if self.addtraits:
                try:
                    self.addtraits = [traits[t] for t in self.addtraits]
                except:
                    raise Exception("Invalid trait to add '%s' for item %s!" % (t, self.id))

            if self.goodtraits:
                try:
                    self.goodtraits = set(traits[t] for t in self.goodtraits)
                except:
                    raise Exception("Invalid good-trait '%s' for item %s!" % (t, self.id))
            if self.badtraits:
                try:
                    self.badtraits = set(traits[t] for t in self.badtraits)
                except:
                    raise Exception("Invalid bad-trait '%s' for item %s!" % (t, self.id))

            if self.add_be_spells:
                try:
                    self.add_be_spells = [battle_skills[s] for s in self.add_be_spells]
                except:
                    raise Exception("Invalid battle skill '%s' added by item %s!" % (s, self.id))
            if self.attacks is not None:
                try:
                    self.attacks = [battle_skills[s] for s in self.attacks]
                except:
                    raise Exception("Invalid attack skill '%s' added by item %s!" % (s, self.id))

            if self.jump_to_label and self.pref_class:
                raise Exception("Invalid pref_class/jump_to_label settings (%s/%s) for item %s (these fields are exclusive)!" % (", ".join(self.pref_class), self.jump_to_label, self.id))

            # merge be modifiers into a single field
            for field in BE_Modifiers.FIELDS:
                if hasattr(self, field):
                    self.be_modifiers = BE_Modifiers(self)
                    break

        def __str__(self):
            return str(self.id)

    # Inventory with listing
    # this is used together with a specialized screens/functions
    class Inventory(_object):
        SLOT_FILTERS = {"all": ("weapon", "smallweapon", "head", "body", "wrist",
            "feet", "cape", "amulet", "ring", "consumable", "gift", "misc", "quest",
            "resources", "loot"),
            "quest": ("quest", "resources", "loot")}

        def __init__(self, per_page):
            self.filtered_items = list() # Handles actual filtered items instances.
            self.items = OrderedDict() # Handles item/amount pairs.

            # Paging:
            self.set_page_size(per_page)
            self.filter_index = 0

            # Filters:
            self.slot_filter = 'all' # Active Slot filter.
            self.final_sort_filter = ("id", False) # We feel second arg to reverse of sort!
            self.gender_filter = "any"

        # Filters:
        @property
        def filters(self):
            """Returns a selection of available filters for the occasion"""
            filters = ["all"]
            availible_item_slots = set(item.slot for item in self.items.iterkeys())

            # Special cases:
            if "loot" in availible_item_slots:
                availible_item_slots.remove("loot")
                availible_item_slots.add("quest")
            if "resources" in availible_item_slots:
                availible_item_slots.remove("resources")
                availible_item_slots.add("quest")

            return filters + list(sorted(availible_item_slots))

        def update_sorting(self, final_sort_filter=None, gender=None):
            if final_sort_filter is not None:
                self.final_sort_filter = final_sort_filter
            if gender is not None:
                self.gender_filter = gender

            # Genders:
            gf = self.gender_filter
            if gf != "any":
                self.filtered_items = [i for i in self.filtered_items if getattr(i, "gender", gf) == gf]

            # Complex:
            key, reverse = self.final_sort_filter
            if self.final_sort_filter[0] in ["id", "price"]:
                self.filtered_items.sort(key=attrgetter(key), reverse=reverse)
            elif self.final_sort_filter[0] == "amount":
                sorted_items = {}
                for item in self.filtered_items:
                    sorted_items[item] = self.items[item]
                sorted_items = OrderedDict(sorted(sorted_items.items(),
                                key=itemgetter(1), reverse=self.final_sort_filter[1]))
                self.filtered_items = sorted_items.keys()

        def apply_filter(self, direction, gender=None):
            """Filter for items.

            Presently filtered by slot.
            """
            filters = self.filters

            if direction in set(self.SLOT_FILTERS["all"]).union(self.SLOT_FILTERS.keys()):
                self.slot_filter = direction
            else:
                if direction == 'next':
                    self.filter_index = (self.filter_index + 1) % len(filters)
                elif direction == 'prev':
                    self.filter_index = (self.filter_index - 1) % len(filters)
                else:
                    try: # We try to get the correct filter, but it could be a fail...
                        self.filter_index = filters.index(self.slot_filter)
                    except:
                        # Explicitly silenced Exception. We set the index to "all" (0) which is always available!
                        self.filter_index = 0
                self.slot_filter = filters[self.filter_index]

            self.filtered_items = list(item for item in self.items.iterkeys() if item.slot in self.SLOT_FILTERS.get(self.slot_filter, [self.slot_filter]))

            self.update_sorting(gender=gender)

            self.page = 0 # min(max(0, self.max_page-1), self.page)

        # Paging:
        def set_page_size(self, size):
            self.page_size = size
            self.page = 0

        def next(self):
            """Next page"""
            self.page += 1
            if self.page > self.max_page:
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
            self.page = self.max_page

        @property
        def page_content(self):
            """Get content for current page"""
            start = self.page*self.page_size
            return self.filtered_items[start:start+self.page_size]

        @property
        def max_page(self):
            """Max page(idx) assuming page_size > 1"""
            return int(float(len(self.filtered_items)-1)/self.page_size) # round towards zero... thanks, python...

        # Add/Remove/Clear:
        def append(self, item, amount=1):
            """
            Add an item to inv and recalc max page.
            After rescaling, both remove and append methods are overkill.
            In case of game code review, one should prolly be removed.
            """
            if isinstance(item, basestring):
                item = store.items[item]

            num = self.items[item] = self.items.get(item, 0) + amount
            if num == amount:
                # append only if this is a new item, otherwise auto_buy with its re-equip is going to mess up the current content
                self.filtered_items.append(item)

            #self.items[item] = self.items.get(item, 0) + amount
            #if item not in self.filtered_items:
            #    self.filtered_items.append(item)

        def remove(self, item, amount=1):
            """Removes given amount of items from inventory.

            Returns True if in case of success and False if there aren't enough items.
            """
            if isinstance(item, basestring):
                item = store.items[item]

            num = self.items.get(item, 0) - amount
            if num < 0:
                return False
            if num == 0:
                self.items.pop(item, 0)
                if item in self.filtered_items:
                    self.filtered_items.remove(item)
                    num = self.max_page
                    if self.page > num:
                        self.page = num
            else:
                self.items[item] = num
            return True

        def clear(self):
            """Removes ALL items from inventory!!!
            """
            self.items = OrderedDict()
            self.filtered_items = list()

        # Easy access (special methods):
        def __contains__(self, item):
            if isinstance(item, basestring):
                item = store.items.get(item, None)
            return item in self.items

        def __getitem__(self, item):
            """Returns an amount of specific item in inventory.
            """
            if isinstance(item, basestring):
                item = store.items.get(item, None)
            return self.items.get(item, 0)

        def __len__(self):
            """Returns total amount of items in the inventory.
            """
            return sum(self.items.values())

        def __nonzero__(self):
            return bool(self.items)

        def __iter__(self):
            return iter(self.items)

    # Shops Classes:
    class ItemShop(_object):
        '''Any shop that sells items ;)
        '''
        def __init__(self, name, location=None, gold=10000, visible=True, sells=[], sell_margin=.8, buy_margin=1.2):
            """Takes:
            name = the name of the shop
            location = the name of the shop as it is referenced by the items.locations. Defaults to name.
            gold = amount of gold shop has on start-up (int)
            visible = If the shop is visible to the player (bool), false is not used at the moment
            sells = list of all the item types this shop should trade.
            sell_margin = at the shop items from the player are sold with this margin 
            buy_margin = at the shop the player must pay this margin for the items 
            """
            self.name = name
            self.location = name if location is None else location
            self.gold = self.normal_gold_amount = gold
            self.visible = visible
            self.sells = set(sells)
            self.sell_margin = sell_margin
            self.buy_margin = buy_margin

            self.inventory = Inventory(18)
            self.restockday = 0
            self.total_items_price = 0 # 25% of items price sold to shop goes to shop's gold on next gold update

            self.restock()

        def check_sell(self, item, price):
            """Checks in an item can be sold to a shop.
            """
            if item.unique:
                return "Unique items cannot be sold!"
            if not item.sellable:
                return "This item cannot be sold!"
            if "any" not in shop.sells and shop.location not in item.locations and item.type.lower() not in shop.sells:
                return "This shop doesn't buy such things."
            if shop.gold < price:
                return "This shop doesn't have enough money."
            return None

        def restock(self):
            '''Restock this shop
            Chance for an item appearing and amount of items are taken from the Item class
            '''
            inventory = self.inventory
            inventory.clear()

            location = self.location
            for item in store.items.itervalues():
                if location in item.locations and dice(item.chance):
                    if item.infinite:
                        x = 100
                    else:
                        x = 1 + round_int(item.chance/10.0)
                    inventory.append(item=item, amount=x)

            # Gazette:
            if self.visible:
                msg = choice(["%s Restocked!",
                              "New merchandise arrived at %s.",
                              "Check out the new arrivals at %s."]) % self.name
                gazette.shops.append(msg)

            self.restockday += locked_random("randint", 3, 7)

        def next_day(self):
            '''Basic counter to be activated on next day
            '''
            if day >= self.restockday:
                self.restock()
                if self.total_items_price > 0:
                    self.gold += self.total_items_price /4
                    self.total_items_price = 0

            base = self.normal_gold_amount
            if self.gold < base:
                self.gold += int(random.uniform(.2, .3) * base)
            elif self.gold < 2*base:
                self.gold += int(random.uniform(.1, .15) * base)
            else:
                self.gold = int(random.uniform(.6, .8) * self.gold)

    class GeneralStore(ItemShop):
        pass # FIXME obsolete

    class CafeShop(ItemShop):
        def __init__(self, **kwargs):
            super(CafeShop, self).__init__("Cafe", **kwargs)
            self.servers = None

        @property
        def waitress(self):
            if self.servers is None:
                self.init_day()
            return self.servers[0]

        @property
        def server(self):
            if self.servers is None:
                self.init_day()
            return self.servers[0]

        def init_day(self):
            servers = [npcs[w] for w in ["Mel_cafe", "Monica_cafe", "Chloe_cafe"]]
            shuffle(servers)
            self.servers = servers

        def next_day(self):
            super(CafeShop, self).next_day()
            self.servers = None

    class Tavern(ItemShop):
        def __init__(self, **kwargs):
            super(Tavern, self).__init__("Tavern", **kwargs)
            self.status = None
            self.bet = 5 # defaul dice bet

        def next_day(self):
            super(Tavern, self).next_day()
            # every day tavern can randomly have one of three statuses, depending on the status it has very different activities available
            self.status = weighted_choice([["cozy", 40], ["lively", 40], ["brawl", 20]])