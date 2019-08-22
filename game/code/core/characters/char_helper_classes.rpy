init -10 python:
    ###### Character Helpers ######
    class Tier(_object):
        """This deals with expectations and social status of chars.

        Used to calculate expected wages, upkeep, living conditions and etc.
        I'd love it to contain at least some of the calculations and conditioning for Jobs as well, we can split this if it gets too confusing.
        Maybe some behavior flags and alike can be a part of this as well?
        """
        def __init__(self):
            # self.instance = instance
            self.tier = 0
            self.expected_wage = 10
            self.stored_upkeep = 0

        def get_max_skill(self, skill, tier=None):
            if tier is None:
                tier = self.tier
            if tier == 0:
                tier = .5
            return 5000*tier/MAX_TIER # SKILLS_MAX

        # used in a number of places to guess what the max stat for n tier might be.
        def get_max_stat(self, stat, tier):
            value = STATIC_CHAR.FIXED_MAX.get(stat, None)
            if value is not None:
                return value

            if tier is None:
                tier = self.tier
            return 100 * (tier+1) # MAX_STAT_PER_TIER

        # used in a number of places to guess what the max stat for the current character at tier n might be.
        def get_relative_max_stat(self, stat, tier=None):
            if stat in STATIC_CHAR.FIXED_MAX:
                return self.stats.get_max(stat)

            if tier is None:
                tier = self.tier

            if stat in self.stats.get_base_stats():
                per_tier = 100 # MAX_STAT_PER_TIER
            else:
                per_tier = 50  # MAX_STAT_PER_TIER/2
            return per_tier * (tier+1)

        def recalculate_tier(self):
            """
            I think we should attempt to figure out the tier based on
            level and stats/skills of basetraits.

            level always counts as half of the whole requirement.
            stats and skills make up the other half.

            We will aim at specific values and interpolate.
            In case of one basetrait, we multiply result by 2!
            """
            if self.tier >= MAX_TIER:
                return False

            target_tier = self.tier+1.0 # To get a float for Py2.7
            target_level = (target_tier)*20
            if target_level > self.level:
                # We need 100 points to tier up!
                level_points = self.level*50.0/target_level

                default_points = 12.5
                stats_skills_points = 0
                for trait in self.traits.basetraits:
                    # Skills first (12.5% of the total)
                    base_skills = trait.base_skills
                    trait_bonus = 0
                    for skill, weight in base_skills.iteritems():
                        sp = self.get_skill(skill)
                        sp_required = self.get_max_skill(skill, target_tier)

                        trait_bonus += min(float(sp)/sp_required, 1.1)*weight
                    if trait_bonus is 0:
                        # Some weird ass base trait, we just award 33% of total possible points.
                        trait_bonus = .33
                    else:
                        trait_bonus /= sum(base_skills.itervalues())
                    stats_skills_points += default_points * trait_bonus

                    # Stats second (12.5% of the total)
                    base_stats = trait.base_stats
                    curr_stats = self.stats
                    trait_bonus = 0
                    for stat, weight in base_stats.iteritems():
                        sp = curr_stats.stats[stat] # STAT_STAT
                        sp_required = self.get_relative_max_stat(stat, target_tier)

                        trait_bonus += min(float(sp)/sp_required, 1.1)*weight
                    if trait_bonus is 0:
                        # Some weird ass base trait, we just award 33% of total possible points.
                        trait_bonus = .33
                    else:
                        trait_bonus /= sum(base_stats.itervalues())
                    stats_skills_points += default_points * trait_bonus

                if len(self.traits.basetraits) == 1:
                    stats_skills_points *= 2

                total_points = level_points + stats_skills_points

                # devlog.info("Name: {}, total tier points for Tier {}: {} (lvl: {}, st/sk=total: {}/{}==>{})".format(self.name,
                #                                                                                             int(target_tier),
                #                                                                                             round(total_points),
                #                                                                                             round(level_points),
                #                                                                                             round(stat_bonus),
                #                                                                                             round(skill_bonus),
                #                                                                                             round(stats_skills_points)))

                if total_points < 100:
                    return False

            self.tier += 1
            return True

        def calc_expected_wage(self, kind=None):
            """Amount of money each character expects to get paid for her skillset.
                        (per day)

            Keeping it simple for now:
            - We'll set defaults for all basic occupation types.
            - We'll adjust by tiers.
            - We'll adjust by other modifiers like traits.

            kind: for now, any specific general occupation will do, but
            we may use jobs in the future somehow. We provide this when hiring
            for a specific task. If None, first occupation found when iterating
            default list will do...
            """
            # Slaves don't normally expect to be paid.
            # if self.status == "slave":
            #     return 0

            # Free workers are:
            if kind:
                wage = STATIC_CHAR.BASE_WAGES[kind]
            else:
                wage = 0
                for i in self.gen_occs:
                    w = STATIC_CHAR.BASE_WAGES.get(i, 0)
                    if w > wage:
                        wage = w
                if wage == 0:
                    raise Exception("Impossible character detected! ID: {} ~ BT: {} ~ Gen.Occupations: {}".format(self.id,
                                    ", ".join([str(t) for t in self.traits.basetraits]), ", ".join([str(t) for t in self.gen_occs])))

            # Each tier increases wage by 50% without stacking:
            wage = wage + wage*self.tier*.5

            if "Dedicated" in self.traits:
                wage = wage*.75

            # Normalize:
            wage = max(int(round(wage)), 10)

            self.expected_wage = wage
            return wage

        def get_upkeep(self):
            return self.stored_upkeep

        def calc_upkeep(self):
            upkeep = self.upkeep

            if self.status == 'slave':
                upkeep += STATIC_CHAR.BASE_UPKEEP * self.tier or 1
                upkeep *= uniform(.9, 1.1)
                if "Dedicated" in self.traits:
                    upkeep *= .5

                upkeep = max(upkeep, 1)
            self.stored_upkeep = round_int(upkeep)

        def get_price(self):
            price = 1000 + self.tier*1000 + self.level*100

            if self.status == 'free':
                price *= 2 # in case if we'll even need that for free ones, 2 times more

            return price

        def update_tier_info(self):
            while self.recalculate_tier():
                continue 
            self.calc_expected_wage()
            self.calc_upkeep()

    class Team(_object):
        def __init__(self, name="", implicit=None):
            self.name = name
            self._members = list()
            self.mem_count = 0 # cached value of len(_members)

            # BE Assets:
            self.position = None # BE will set it to "r" or "l" short for left/right on the screen.

            if implicit:
                for member in implicit:
                    self.add(member)

        def __len__(self):
            return self.mem_count

        def __iter__(self):
            return iter(self._members)

        def __getitem__(self, index):
            return self._members[index]

        def __nonzero__(self):
            return self.mem_count != 0

        @property
        def leader(self):
            try:
                return self._members[0]
            except:
                return None

        @property
        def gui_name(self):
            return self._members[0].nickname if self.mem_count == 1 else self.name 

        def add(self, member):
            self._members.append(member)
            self.mem_count += 1

        def remove(self, member):
            self._members.remove(member)
            self.mem_count -= 1

        #def set_leader(self, member):
        #    mems = self._members
        #    if member not in mems:
        #        renpy.notify("%s is not a member of this team!" % member.name)
        #        return
        #    mems.remove(member)
        #    mems.insert(0, member)

        def get_level(self):
            """
            Returns an average level of the team as an integer.
            """
            try:
                return sum((member.level for member in self._members))/self.mem_count
            except ZeroDivisionError:
                return 0

        def get_rep(self):
            """
            Returns the arena reputation of the team.
            """
            try:
                return sum((member.arena_rep for member in self._members))/self.mem_count
            except ZeroDivisionError:
                return 0

        def take_ap(self, value):
            """
            Checks the whole team for enough AP;
            if at least one teammate doesn't have enough AP, AP won't decrease,
            and function will return False, otherwise True
            """
            value *= 100 # PP_PER_AP
            return self.take_pp(value)

        def take_pp(self, value):
            """
            Checks the whole team for enough PP;
            if at least one teammate doesn't have enough PP, PP won't decrease,
            and function will return False, otherwise True
            """
            for i in self._members:
                if i.PP < value:
                    return False
            for i in self._members:
                i.PP -= value
            return True

        # BE Related:
        def reset_controller(self):
            # Resets combat controller
            for m in self._members:
                m.controller = None

        def setup_controller(self, simple_ai=False):
            for m in self._members:
                m.controller = BE_AI() if simple_ai is True else Complex_BE_AI()

    class JobsLogger(_object):
        # Used to log stats and skills during job actions
        def __init__(self):
            self.stats_skills = dict()

        def logws(self, s, value):
            """Logs workers stat/skill to a dict:
            """
            self.stats_skills[s] = self.stats_skills.get(s, 0) + value

        def clear_jobs_log(self):
            self.stats_skills = dict()


    class SmartTracker(collections.MutableSequence):
        def __init__(self, instance, be_skill=True):
            self.instance = instance # Owner of this object, this is being instantiated as character.magic_skills = SmartTracker(character)
            self.normal = set() # Normal we consider anything that's been applied by normal game operations like events, loading routines and etc.
            self.items = dict() # Stuff that's been applied through items, it's a counter as multiple items can apply the same thing (like a trait).
            self.be_skill = be_skill # If we expect a be skill or similar mode.
            self.list = list()

        # the iterator of the MutableSequence is SLOW, use iterator of the list instead
        def __iter__(self): return self.list.__iter__()

        def __len__(self): return len(self.list)

        def __getitem__(self, i): return self.list[i]

        def __delitem__(self, i): del self.list[i]

        def __setitem__(self, i, v):
            self.list[i] = v

        def insert(self, i, v):
            self.list.insert(i, v)

        def __str__(self):
            return str(self.list)

        def append(self, item, normal=True):
            # Overwriting default list method, always assumed normal game operations and never adding through items.
            # ==> For battle & magic skills:
            if self.be_skill:
                if isinstance(item, basestring):
                    item = store.battle_skills.get(item, None)
                    if item is None:
                        raise Exception("Tried to apply unknown skill %s to %s!" % (item, self.instance.__class__))

            num = self.items.get(item, 0)
            if normal: #  Item applied by anything other than that
                self.normal.add(item)
                num += 1
            else:
                num += 1
                self.items[item] = num
                if item in self.normal:
                    num += 1

            if num > 0:
                if item not in self.list:
                    self.list.append(item)
                    return True

        def remove(self, item, normal=True):
            # Overwriting default list method.
            # ==> For battle & magic skills:
            if self.be_skill:
                if isinstance(item, basestring):
                    item = store.battle_skills.get(item, None)
                    if item is None:
                        raise Exception("Tried to remove unknown skill %s from %s!" % (item, self.instance.__class__))

            num = self.items.get(item, 0)
            if normal:
                self.normal.discard(item)
            else:
                num -= 1
                if num == 0:
                    self.items.pop(item)
                else:
                    self.items[item] = num
                if item in self.normal:
                    num += 1

            # The above is enough for magic/battle skills, but for traits...
            # we need to know if the effects should be applied.
            if num <= 0:
                if item in self.list: # DO NOTHING otherwise.
                    self.list.remove(item)
                    return True

    class Trait(_object):
        def __init__(self):
            self.desc = ''
            self.icon = None
            self.hidden = False
            self.mod_stats = dict()
            self.mod_skills = dict()
            self.max = dict()
            self.min = dict()
            self.blocks = list()
            self.effects = list()

            # Occupations related:
            self.occupations = list() # GEN_OCCS (Misnamed here)
            #self.higher_tiers = list() # optional Required higher tier basetraits to enable this trait.

            # self.gender = "unisex" # optional field to restrict usage

            # Types:
            #self.type = "" # Specific type if specified.
            self.basetrait = False
            self.personality = False
            self.race = False
            self.gents = False
            self.body = False
            self.elemental = False

            self.mod_ap = 0 # Will only work on body traits!

            self.mob_only = False
            self.character_trait = False
            self.sexual = False
            self.client = False
            self.market = False

            # Base mods on init:
            self.init_mod = dict() # Mod value setting
            self.init_lvlmax = dict() # Mod value setting
            self.init_max = dict() # Mod value setting
            self.init_skills = dict() # {skill: [actions, training]}

            # Elemental:
            self.font_color = None
            self.resist = list()
            #self.el_absorbs = dict() # Pure ratio, NOT a modificator to a multiplier like for dicts below.
            #self.el_damage = dict()
            #self.el_defence = dict()

            # Special BE Fields:
            self.be_modifiers = None # 'all' be related fields are merged into this (TODO except for the resist...)
            # self.evasion_bonus = () # Bonuses in traits work differently from item bonuses, a tuple of (min_value, max_value, max_value_level) is expected (as a value in dict below) instead!
            # self.ch_multiplier = 0 # Chance of critical hit multi...
            # self.damage_multiplier = 0

            # self.defence_bonus = {} # Delivery! Not damage types!
            # self.defence_multiplier = {}
            # self.delivery_bonus = {} Expects a k/v pair of type: multiplier This is direct bonus added to attack power.
            # self.delivery_multiplier = {}

            self.leveling_stats = dict() # {stat: [lvl_max, max **as mod values]}

            # For BasetTraits, we want to have a list of skills and stats, possibly weighted for evaluation.
            self.base_skills = dict()
            self.base_stats = dict()
            # Where key: value are stat/skill: weight!

        def __str__(self):
            return str(self.id)

    class Traits(SmartTracker):
        def __init__(self, *args, **kwargs):
            """
            Trait effects are being applied per level on activation of a trait and on level-ups.
            """
            # raise Exception(args[0])
            # SmartTracker.__init__(self, args[0])
            super(Traits, self).__init__(args[0])
            # self.instance = args[0]

            self.ab_traits = set()  # Permenatly blocked traits (Absolute Block Traits)
            self.blocked_traits = set()  # Blocked traits

            self.basetraits = set() # A set with basetraits (2 maximum)

        def __getattr__(self, item):
            raise AttributeError("%s object has no attribute named %r" %
                                 (self.__class__.__name__, item))

        def __contains__(self, item):
            if isinstance(item, basestring):
                if item in store.traits: item = store.traits[item]
                else: return False

            return super(Traits, self).__contains__(item)

        @property
        def gen_occs(self):
            # returns a list of general occupation from Base Traits only.
            gen_occs = set(chain.from_iterable(t.occupations for t in self.basetraits))
            return list(gen_occs)

        @property
        def base_to_string(self):
            return ", ".join(sorted(list(str(t) for t in self.basetraits)))

        def apply(self, trait, truetrait=True):
            """
            Activates trait and applies it's effects all the way up to a current level of the characters.
            Truetraits basically means that the trait is not applied thought items (Jobs, GameStart, Events and etc.)
            """
            # If we got a string with a traits name. Let the game throw an error otherwise.
            if isinstance(trait, basestring):
                trait = traits[trait]
            char = self.instance

            # All the checks required to make sure we can even apply this trait: ======================>>
            temp = char.gender
            if getattr(trait, "gender", temp) != temp:
                return

            # We cannot allow "Neutral" element to be applied if there is at least one element present already:
            if trait.id == "Neutral": # and trait.elemental:
                if char.elements:
                    return

            # Blocked traits:
            if trait in self.ab_traits | self.blocked_traits:
                return

            # Unique Traits:
            if trait.personality:
                if hasattr(char, "personality"):
                    return
                else:
                    char.personality = trait
            if trait.race:
                if hasattr(char, "race"):
                    return
                else:
                    char.race = trait
            if trait.gents:
                if hasattr(char, "gents"):
                    return
                else:
                    char.gents = trait
            if trait.body:
                if hasattr(char, "body"):
                    return
                else:
                    char.body = trait

            if not super(Traits, self).append(trait, truetrait):
                return

            # If we got here... we can apply the effect? Maybe? Please? Just maybe? I am seriously pissed at this system right now... ===========>>>

            stats = char.stats
            # If the trait is a basetrait:
            if trait in self.basetraits:
                multiplier = 2 if len(self.basetraits) == 1 else 1
                for k, v in trait.init_lvlmax.iteritems(): # Mod value setting
                    stats.lvl_max[k] += v * multiplier # STAT_LVL_MAX

                for k, v in trait.init_max.iteritems(): # Mod value setting
                    stats.max[k] += v * multiplier # STAT_MAX 

                for k, v in trait.init_mod.iteritems(): # Mod value setting
                    stats.stats[k] += v * multiplier # STAT_STAT

                for k, v in trait.init_skills.iteritems(): # Mod value setting
                    k = stats.skills[k]
                    k[0] += v[0] * multiplier
                    k[1] += v[1] * multiplier

            # Only for body traits:
            if trait.body:
                if trait.mod_ap:
                    char.basePP += trait.mod_ap * 100 # PP_PER_AP

            if truetrait:
                for key, value in trait.max.iteritems():
                    stats.max[key] += value # STAT_MAX
                for key, value in trait.min.iteritems():
                    stats.min[key] += value # STAT_MIN
            else:
                for key, value in trait.max.iteritems():
                    stats.imax[key] += value # STAT_IMAX
                for key, value in trait.min.iteritems():
                    stats.imin[key] += value # STAT_IMIN

            for entry in trait.blocks:
                self.blocked_traits.add(entry)

            # For now just the chars get effects...
            if hasattr(char, "effects"):
                for entry in trait.effects:
                    char.enable_effect(entry)

            for key, mod in trait.mod_skills.iteritems():
                sm = stats.skills_multipliers[key] # skillz muplties
                sm[0] += mod[0]
                sm[1] += mod[1]
                sm[2] += mod[2]

            mod_stats = trait.mod_stats
            if mod_stats:
                temp = mod_stats.get("upkeep", None)
                if temp is not None:
                    char.upkeep += temp[0]
                temp = mod_stats.get("disposition", None)
                if temp is not None:
                    stats._mod_base_stat("disposition", temp[0])
                temp = mod_stats.get("affection", None)
                if temp is not None:
                    stats._mod_base_stat("affection", temp[0])
                stats.apply_trait_statsmod(mod_stats, 0, char.level, truetrait)

            # Adding resisting elements and attacks:
            for i in trait.resist:
                char.resist.append(i, truetrait)

            # NEVER ALLOW NEUTRAL ELEMENT WITH ANOTHER ELEMENT!
            if trait.elemental and trait.id != "Neutral":
                trait = traits["Neutral"]
                if trait in self:
                    self.remove(trait)

        def remove(self, trait, truetrait=True):
            """
            Removes trait and removes it's effects gained up to a current level of the characters.
            Truetraits basially means that the trait is not applied throught items (Jobs, GameStart, Events and etc.)
            """
            # If we got a string with a traits name. Let the game throw an error otherwise.
            if isinstance(trait, basestring):
                trait = traits[trait]
            char = self.instance

            temp = char.gender
            if getattr(trait, "gender", temp) != temp:
                return

            # We Never want to remove a base trait:
            if trait in self.basetraits:
                return

            # WE NEVER REMOVE PERMANENT TRAITS FAMILY:
            if any([trait.personality, trait.race, trait.gents, trait.body]):
                return

            if not super(Traits, self).remove(trait, truetrait):
                return

            stats = char.stats
            if truetrait:
                for key, value in trait.max.iteritems():
                    stats.max[key] -= value # STAT_MAX

                for key, value in trait.min.iteritems():
                    stats.min[key] -= value # STAT_MIN
            else:
                for key, value in trait.max.iteritems():
                    stats.imax[key] -= value # STAT_IMAX

                for key, value in trait.min.iteritems():
                    stats.imin[key] -= value # STAT_IMIN

            if trait.blocks:
                # Update blocked traits
                blocks = set()
                for entry in self:
                    blocks.update(entry.blocks)
                self.blocked_traits = blocks

            # For now just the chars get effects...
            if isinstance(char, Char):
                for entry in trait.effects:
                    char.disable_effect(entry)

            for key, mod in trait.mod_skills.iteritems():
                sm = stats.skills_multipliers[key] # skillz muplties
                sm[0] -= mod[0]
                sm[1] -= mod[1]
                sm[2] -= mod[2]

            mod_stats = trait.mod_stats
            if mod_stats:
                temp = mod_stats.get("upkeep", None)
                if temp is not None:
                    char.upkeep -= temp[0]
                temp = mod_stats.get("disposition", None)
                if temp is not None:
                    stats._mod_base_stat("disposition", -temp[0])
                temp = mod_stats.get("affection", None)
                if temp is not None:
                    stats._mod_base_stat("affection", -temp[0])
                stats.apply_trait_statsmod(mod_stats, char.level, 0, truetrait)

            # Remove resisting elements and attacks:
            for i in trait.resist:
                char.resist.remove(i, truetrait)

            # We add the Neutral element if there are no elements left at all...
            if trait.elemental and not char.elements:
                self.apply(traits["Neutral"])

    class Finances(_object):
        """Helper class that handles finance related matters in order to reduce
        the size of Characters/Buildings classes."""
        def __init__(self, *args, **kwargs):
            """Main logs log actual finances (money moving around)
            Jobs income logs don't do any such thing. They just hold info about
            how much building or character earned for MC or how much MC paid
            to them.
            """
            self.instance = args[0]
            self.todays_main_income_log = dict()
            self.todays_main_expense_log = dict()
            self.todays_logical_income_log = dict()
            self.todays_logical_expense_log = dict()

            self.game_main_income_log = dict()
            self.game_main_expense_log = dict()
            self.game_logical_income_log = dict()
            self.game_logical_expense_log = dict()

            self.income_tax_debt = 0
            self.property_tax_debt = 0

        def add_money(self, value, reason="Other"):
            value = int(round(value))
            self.log_income(value, reason)
            self.instance.gold += value

        def take_money(self, value, reason="Other"):
            value = int(round(value))
            if value <= self.instance.gold:
                self.log_expense(value, reason)
                self.instance.gold -= value
                return True
            return False

        # Logging actual data (money moving around)
        def log_income(self, value, kind):
            """Logs private Income."""
            value = int(round(value))
            temp = self.todays_main_income_log
            temp[kind] = temp.get(kind, 0) + value

        def log_expense(self, value, kind):
            """Logs private expence."""
            value = int(round(value))
            temp = self.todays_main_expense_log
            temp[kind] = temp.get(kind, 0) + value

        # Logging logical data (just for info, relative to MC)
        def log_logical_income(self, value, kind):
            """(Buildings or Chars)"""
            value = int(round(value))
            temp = self.todays_logical_income_log
            temp[kind] = temp.get(kind, 0) + value

        def log_logical_expense(self, value, kind):
            """(Buildings or Chars)"""
            value = int(round(value))
            temp = self.todays_logical_expense_log
            temp[kind] = temp.get(kind, 0) + value

        # Retrieving data:
        def get_data_for_fin_screen(self, type=None):
            if type == "logical":
                all_income_data = self.game_logical_income_log.copy()
                all_income_data[store.day] = self.todays_logical_income_log

                all_expense_data = self.game_logical_expense_log.copy()
                all_expense_data[store.day] = self.todays_logical_expense_log
            if type == "main":
                all_income_data = self.game_main_income_log.copy()
                all_income_data[store.day] = self.todays_main_income_log

                all_expense_data = self.game_main_expense_log.copy()
                all_expense_data[store.day] = self.todays_main_expense_log

            days = set()
            for d, v in chain(all_income_data.iteritems(), all_expense_data.iteritems()):
                if v:
                    days.add(d)
            days.discard(-1)
            days = sorted(days)
            days = days[-7:]
            if days:
                days.append("All")
                all_income_data["All"] = add_dicts(all_income_data.values())
                all_expense_data["All"] = add_dicts(all_expense_data.values())
            return days, all_income_data, all_expense_data

        def get_logical_income(self, kind="all", day=None):
            """Retrieve work income (for buildings/chars?)

            kind = "all" means any income earned on the day.
            """
            if day is None:
                d = self.todays_logical_income_log
            elif day >= store.day:
                raise Exception("Day on income retrieval must be lower than the current day!")
            else:
                d = self.game_logical_income_log[day]

            if kind == "all":
                return sum(val for val in d.itervalues())
            d = d.get(kind, None)
            if d is None:
                raise Exception("Income kind: %s is not valid!" % kind)
            return d

        def get_game_total(self):
            # Total income over the game (Used in ND screen)...
            # Used MAIN dicts
            days, all_income_data, all_expense_data = self.get_data_for_fin_screen("main")
            income = sum(all_income_data.get("All", {}).values())
            expense = sum(all_expense_data.get("All", {}).values())

            total = income - expense
            return income, expense, total

        # Tax related:
        def get_income_tax(self, days=7):
            # MC's Income Tax
            income = tax = 0
            days = store.day - days # the accounting for today is not closed -> _day >= days
            bv = {b: sum(values.itervalues()) for b in self.instance.buildings for _day, values in b.fin.game_logical_income_log.iteritems() if _day >= days}
            income = sum(bv.itervalues())
            if income > 5000:
                for delimiter, mod in pytfall.economy.income_tax:
                    if income <= delimiter:
                        tax = round_int(income*mod)
                        break

                if tax:
                    for b, v in bv.iteritems():
                        _tax = round_int(v*mod)
                        b.fin.log_logical_expense(_tax, "Income Tax")
            return income, tax

        def get_property_tax(self):
            char = self.instance
            ec = store.pytfall.economy

            b_tax = s_tax = 0
            mod = ec.property_tax["real_estate"]
            for p in char.buildings:
                _tax = round_int(p.get_price()*mod)
                p.fin.log_logical_expense(_tax, "Property Tax")
                b_tax += _tax
            mod = ec.property_tax["slaves"]
            for c in char.chars:
                if c.status != "slave":
                    continue
                _tax = round_int(c.get_price()*mod)
                c.fin.log_logical_expense(_tax, "Property Tax")
                s_tax += _tax

            tax = b_tax + s_tax
            return b_tax, s_tax, tax

        # Rest ================================>>>
        def settle_wage(self, txt, mood):
            """
            Settle wages between player and chars.
            Called during next day method per each individual worker.
            """
            char = self.instance
            real_wagemod = char.wagemod
            expected_wage = char.expected_wage
            if char.status == "free":
                # Free chars:
                temp = choice(["%s expects to be compensated for %s services ({color=gold}%d Gold{/color})." % (char.pC, char.pd, expected_wage),
                               "%s expects to be paid a wage of {color=gold}%d Gold{/color}." % (char.pC, expected_wage)])

                tmp = " You chose to pay %s %d%% of that! ({color=gold}%d Gold{/color})"
            else:
                # Slaves:
                temp = choice(["Being a slave, %s doesn't expect to get paid." % char.p,
                               "Slaves don't get paid."])
                if real_wagemod == 0:
                    txt.append(temp)
                    return mood

                tmp = " And yet... you chose to pay %s %d%% of the fair wage! ({color=gold}%d Gold{/color})"

            paid_wage = round_int(expected_wage*real_wagemod/100.0)
            temp += tmp % (char.op, real_wagemod, paid_wage)
            txt.append(temp)

            if paid_wage == 0: # Free char with 0% wage mod
                txt.append("You paid %s nothing..." % char.op)
            elif hero.take_money(paid_wage, reason="Wages"):
                self.add_money(paid_wage, reason="Wages")
                self.log_logical_expense(paid_wage, "Wages")
                if isinstance(char.workplace, Building):
                    char.workplace.fin.log_logical_expense(paid_wage, "Wages")
            else:
                txt.append("You lacked the funds to pay %s the promised wage." % char.op)
                paid_wage = real_wagemod = 0

            # So... if we got this far, we're either talking slaves that player
            # chose to pay a wage or free chars who expect that.
            if char.status == "free":
                if paid_wage == expected_wage:
                    # Paying a fair wage
                    if dice(10): # just a small way to appreciate that:
                        char.mod_stat("disposition", 1)
                        char.mod_stat("joy", 1)
                    return mood

                diff = real_wagemod - 100 # We expected 100% of the wage at least.

                dismod = round_int(diff*.09)
                joymod = round_int(diff*.06)
                if diff > 0:
                    mood = "happy"
                    dismod = max(1, dismod)
                    joymod = max(1, joymod)
                else: #if diff < 0:
                    mood = "angry"
                    mod = 2 - check_submissivity(char) # convert [-1,0,1] to [1,2,3]
                    dismod = min(-2, dismod) * mod
                    joymod = min(-1, joymod) * mod
                    char.mod_stat("affection", affection_reward(char, -1, stat="gold"))
                if DEBUG_CHARS:
                    txt.append("Debug: Disposition mod: {}".format(dismod))
                    txt.append("Debug: Joy mod: {}".format(joymod))
                char.mod_stat("disposition", dismod)
                char.mod_stat("joy", joymod)
            else: # Slave case:
                if paid_wage == 0:
                    txt.append(" But being a slave %s will not hold that against you." % char.nickname)
                else:
                    mood = "happy"
                    diff = real_wagemod # Slaves just get the raw value.
                    dismod = round_int(diff*.15)
                    joymod = round_int(diff*.1)
                    dismod = max(1, dismod)
                    joymod = max(1, joymod)
                    if DEBUG_CHARS:
                        txt.append("Debug: Disposition mod: {}".format(dismod))
                        txt.append("Debug: Joy mod: {}".format(joymod))
                    char.mod_stat("disposition", dismod)
                    char.mod_stat("joy", joymod)

            return mood

        def next_day(self):
            # We log total to -1 key...
            curr_day = store.day

            self.game_main_income_log[curr_day] = self.todays_main_income_log
            self.game_main_expense_log[curr_day] = self.todays_main_expense_log
            self.game_logical_income_log[curr_day] = self.todays_logical_income_log
            self.game_logical_expense_log[curr_day] = self.todays_logical_expense_log

            curr_day -= 10
            for log in [self.game_main_income_log, self.game_main_expense_log,
                        self.game_logical_income_log, self.game_logical_expense_log]:
                for day, info in log.items():
                    if 0 < day < curr_day:
                        log[-1] = add_dicts([log.get(-1, {}), info])
                        del log[day]

            self.todays_main_income_log = dict()
            self.todays_main_expense_log = dict()
            self.todays_logical_income_log = dict()
            self.todays_logical_expense_log = dict()


    class Stats(_object):
        """Holds and manages stats for PytCharacter Classes.
        DEVNOTE: Be VERY careful when accessing this class directly!
        Some of it's methods assume input from self.instance__setattr__ and do extra calculations!
        """
        def __init__(self, instance, stats):
            """
            :param instance: reference to Character object
            :param stats: Expects a dict with statname as key and a list of:
            [stat, min, max, lvl_max, imod, imin, imax] as value.
            Added skills to this class... (Maybe move to a separate class if they get complex?).
            """
            self.instance = instance
            self.stats, self.min, self.max, self.lvl_max, self.imod, self.imin, self.imax = dict(), dict(), dict(), dict(), dict(), dict(), dict()

            # Load the stat values:
            for stat, values in stats.iteritems():
                self.stats[stat] = values[0]
                self.min[stat] = values[1]
                self.max[stat] = values[2]
                self.lvl_max[stat] = values[3]
                self.imod[stat] = values[4]
                self.imin[stat] = values[5]
                self.imax[stat] = values[6]

            # [action_value, training_value]
            self.skills = {s: [0, 0] for s in STATIC_CHAR.SKILLS}
            # [actions_multi, training_multi, value_multi]
            self.skills_multipliers = {s: [1, 1, 1] for s in STATIC_CHAR.SKILLS}

            # Leveling system assets:
            self.goal = 1000
            self.goal_increase = 1000
            self.level = 0
            self.exp = 0

            # Statslog:
            self.log = dict()

        # TODO move these to Traits?
        def get_base_stats(self):
            return set(s for t in self.instance.traits.basetraits for s in t.base_stats)

        def get_base_skills(self):
            return set(s for t in self.instance.traits.basetraits for s in t.base_skills)

        def get_base_ss(self):
            return self.get_base_stats().union(self.get_base_skills())

        def _get_stat(self, key):
            maxval = min(self.max[key] + self.imax[key], self.lvl_max[key]) # STAT_MAX, STAT_IMAX, STAT_LVL_MAX
            minval = self.min[key] + self.imin[key] # STAT_MIN + STAT_IMIN
            val = self.stats[key] + self.imod[key]  # STAT_STAT + STAT_IMOD

            # Normalization:
            if val > maxval:
                val = maxval
            if val < minval:
                val = minval

            return val

        def get_skill(self, skill):
            """
            Returns adjusted skill.
            'Action' skill points become less useful as they exceed training points * 3.
            """
            action, training = self.skills[skill]

            beyond_training = action - (training * 3)
            if beyond_training >= 0:
                action -= beyond_training / 1.5

            training += action
            if training > 5000: # SKILLS_MAX
                training = 5000 # SKILLS_MAX
            return training * max(min(self.skills_multipliers[skill][2], 2.5), .5)

        def __getitem__(self, key):
            return self._get_stat(key)

        def __iter__(self):
            return iter(self.stats) # STAT_STAT

        def get_stat_max(self, key):
            return min(self.max[key], self.lvl_max[key])

        def get_stat_min(self, key):
            return self.min[key]

        def get_max(self, key):
            return max(self.min[key] + self.imin[key], min(self.max[key] + self.imax[key], self.lvl_max[key])) # STAT_MIN STAT_IMIN, STAT_MAX STAT_IMAX, STAT_LVL_MAX

        def get_min(self, key):
            return self.min[key] + self.imin[key]

        def mod_exp(self, value):
            # Assumes input from setattr of self.instance:
            char = self.instance

            value += self.exp
            self.exp = value

            if self.exp < self.goal:
                return

            num_lvl = (self.exp - self.goal)/self.goal_increase + 1
            self.goal += num_lvl * self.goal_increase

            # Normal Max stat Bonuses:
            for stat in self.stats:
                if stat not in STATIC_CHAR.FIXED_MAX:
                    self.lvl_max[stat] += 5 * num_lvl # STAT_LVL_MAX
                    self.max[stat] += 2 * num_lvl     # STAT_MAX

                    # Chance to increase max stats permanently based on level
                    chance = (2*self.level + num_lvl)*num_lvl/ 40.0
                    value = min(random.expovariate(100.0/chance), num_lvl)
                    val = int(value)
                    if val != 0:
                        self.lvl_max[stat] += val     # STAT_LVL_MAX
                        self.max[stat] += val         # STAT_MAX
                        value -= val
                    value *= 100
                    if dice(value):
                        self.lvl_max[stat] += 1       # STAT_LVL_MAX
                    if dice(value):
                        self.max[stat] += 1           # STAT_MAX

                    #if self.level >= 20:
                    #    val = self.level / 20.0
                    #    if dice(val):
                    #        self.lvl_max[stat] +=1
                    #    if dice(val):
                    #        self.max[stat] +=1

            # Super Bonuses from Base Traits:
            traits = char.traits.basetraits
            multiplier = 2 if len(traits) == 1 else 1
            multiplier *= num_lvl
            for trait in traits:
                # Super Stat Bonuses:
                for stat, value in trait.leveling_stats.iteritems():
                    self.lvl_max[stat] += value[0] * multiplier    # STAT_LVL_MAX
                    self.max[stat] += value[1] * multiplier        # STAT_MAX

                # Super Skill Bonuses:
                #for skill in trait.init_skills:
                #    self.mod_full_skill(skill, 20*num_lvl)

            curr_lvl = self.level
            new_lvl = curr_lvl + num_lvl
            self.level = new_lvl

            # Bonuses from traits:
            traits = char.traits
            for trait in traits:
                mod_stats = trait.mod_stats
                if mod_stats:
                    self.apply_trait_statsmod(mod_stats, curr_lvl, new_lvl, trait in traits.normal)
                # TODO mod_skills?

            restore_battle_stats(char)

            self.instance.update_tier_info()

        def apply_trait_statsmod(self, mod_stats, from_lvl, to_lvl, truetrait):
            """Applies "stats_mod" field on characters.
               A mod_stats entry is a pair of integers (x, y), which means the character
               gains x points every y level.
            """
            delta_lvl = to_lvl - from_lvl
            temp = ["disposition", "affection", "upkeep"]
            for key, value in mod_stats.iteritems():
                if key in temp:
                    continue
                mod = value[1]
                delta = delta_lvl / mod
                rem = delta_lvl % mod
                if rem != 0:
                    rem = (to_lvl / mod) - ((to_lvl - rem) / mod)
                    if rem > 0:
                        delta += 1
                    elif rem < 0:
                        delta -= 1
                if delta != 0:
                    delta *= value[0]
                    if truetrait:
                        self._mod_base_stat(key, delta)
                    else:
                        self.imod[key] += delta # STAT_IMOD

        def apply_item_effects(self, item, direction, true_add):
            char = self.instance
            traits = char.traits
            type = item.type
            slot = item.slot

            # Max Stats:
            for stat, value in item.max.items():
                if stat == "defence":
                    if value < 0 and "Elven Ranger" in traits and type in ["bow", "crossbow", "throwing"]:
                        continue
                    if type == "armor" and "Knightly Stance" in traits:
                        value *= 1.3
                    if "Berserk" in traits:
                        value *= .5
                elif stat == "attack":
                    if "Berserk" in traits:
                        value *= 2
                elif stat == "agility":
                    if value < 0 and "Hollow Bones" in traits:
                        continue

                if slot == "smallweapon":
                    if "Left-Handed" in traits:
                        value *= 2
                elif slot == "weapon":
                    if "Left-Handed" in traits:
                        value *= .5

                if type == "sword":
                    if "Sword Master" in traits:
                        value *= 1.3
                elif type == "shield":
                    if "Shield Master" in traits:
                        value *= 1.3
                elif type == "dagger":
                    if "Dagger Master" in traits:
                        value *= 1.3
                elif type == "bow":
                    if "Bow Master" in traits:
                        value *= 1.3

                # Reverse the value if appropriate:
                if not direction:
                    value = -value
                if true_add:
                    self.max[stat] += int(value) # STAT_MAX
                else:
                    self.imax[stat] += int(value) # STAT_IMAX

            # Min Stats:
            for stat, value in item.min.items():
                if stat == "defence":
                    if value < 0 and "Elven Ranger" in traits and type in ["bow", "crossbow", "throwing"]:
                        continue
                    if type == "armor" and "Knightly Stance" in traits:
                        value *= 1.3
                    if "Berserk" in traits:
                        value *= .5
                elif stat == "attack":
                    if "Berserk" in traits:
                        value *= 2
                elif stat == "agility":
                    if value < 0 and "Hollow Bones" in traits:
                        continue

                if slot == "smallweapon":
                    if "Left-Handed" in traits:
                        value *= 2
                elif slot == "weapon":
                    if "Left-Handed" in traits:
                        value *= .5

                if type == "sword":
                    if "Sword Master" in traits:
                        value *= 1.3
                elif type == "shield":
                    if "Shield Master" in traits:
                        value *= 1.3
                elif type == "dagger":
                    if "Dagger Master" in traits:
                        value *= 1.3
                elif type == "bow":
                    if "Bow Master" in traits:
                        value *= 1.3

                # Reverse the value if appropriate:
                if not direction:
                    value = -value
                if true_add:
                    self.min[stat] += int(value) # STAT_MIN
                else:
                    self.imin[stat] += int(value) # STAT_IMIN

            # Items Stats:
            for stat, value in item.mod.items():
                if item.statmax and self.stats[stat] >= item.statmax: # STAT_STAT
                    continue

                # Reverse the value if appropriate:
                original_value = value
                if not direction:
                    value = -value

                if true_add:
                    if stat == "gold":
                        if char.status == "slave" and char.employer == hero:
                            temp = hero
                        else:
                            temp = char
                        if value < 0:
                            temp.take_money(-value, reason="Upkeep")
                        else:
                            temp.add_money(value, reason="Items")
                    elif stat == "exp":
                        self.mod_exp(exp_reward(char, char, exp_mod=float(value)/DAILY_EXP_CORE))
                    else:
                        if type == "food" and 'Fast Metabolism' in char.effects:
                            value *= 2
                        if original_value > 0:
                            if stat == "health":
                                if "Summer Eternality" in traits:
                                    value *= .35
                            elif stat == "mp":
                                if "Winter Eternality" in traits:
                                    value *= .35
                                if "Magical Kin" in traits:
                                    if type == "alcohol":
                                        value *= 2
                                    else:
                                        value *= 1.5
                            elif stat == "vitality":
                                if "Effective Metabolism" in traits:
                                    if type == "food":
                                        value *= 2
                                    else:
                                        value *= 1.5

                        self._mod_base_stat(stat, int(value))
                else:
                    if stat == "defence":
                        if original_value < 0 and "Elven Ranger" in traits and type in ["bow", "crossbow", "throwing"]:
                            continue
                        if type == "armor" and "Knightly Stance" in traits:
                            value *= 1.3
                        if "Berserk" in traits:
                            value *= .5
                    elif stat == "attack":
                        if "Berserk" in traits:
                            value *= 2
                    elif stat == "agility":
                        if original_value < 0 and "Hollow Bones" in traits:
                            continue

                    if slot == "smallweapon":
                        if "Left-Handed" in traits:
                            value *= 2
                    elif slot == "weapon":
                        if "Left-Handed" in traits:
                            value *= .5

                    if type == "sword":
                        if "Sword Master" in traits:
                            value *= 1.3
                    elif type == "shield":
                        if "Shield Master" in traits:
                            value *= 1.3
                    elif type == "dagger":
                        if "Dagger Master" in traits:
                            value *= 1.3
                    elif type == "bow":
                        if "Bow Master" in traits:
                            value *= 1.3

                    self.imod[stat] += int(value) # STAT_IMOD

            if true_add:
                if slot != 'misc' and "Recharging" in traits and "mp" not in item.mod:
                    self._mod_base_stat("mp", 10)
            else:
                # Special modifiers based off traits:
                if "Royal Assassin" in traits and slot not in ["ring", "amulet"]:
                    value = (item.price if direction else -item.price)/100
                    self.imax["attack"] += value        # STAT_IMAX
                    self.imod["attack"] += value        # STAT_IMOD
                elif "Armor Expert" in traits and slot not in ["ring", "amulet"]:
                    value = (item.price if direction else -item.price)/100
                    self.imax["defence"] += value       # STAT_IMAX
                    self.imod["defence"] += value       # STAT_IMOD
                elif "Arcane Archer" in traits and type in ["bow", "crossbow", "throwing"]:
                    max_val = item.max.get("attack", 0)/2
                    mod_val = item.mod.get("attack", 0)/2
                    if not direction:
                        max_val = -max_val
                        mod_val = -mod_val
                    self.imax["magic"] += max_val       # STAT_IMAX
                    self.imod["magic"] += mod_val       # STAT_IMOD

            # Skills:
            for skill, data in item.mod_skills.items():
                s = self.skills[skill] # skillz
                if item.skillmax:
                    if data[3] != 0 and s[0] >= item.skillmax:
                        continue
                    if data[4] != 0 and s[1] >= item.skillmax:
                        continue
                    # FIXME what about the multipliers?

                sm = self.skills_multipliers[skill] # skillz muplties
                if direction:
                    sm[0] += data[0]
                    sm[1] += data[1]
                    sm[2] += data[2]
                    s[0] += data[3]
                    s[1] += data[4]
                else:
                    sm[0] -= data[0]
                    sm[1] -= data[1]
                    sm[2] -= data[2]
                    s[0] -= data[3]
                    s[1] -= data[4]

        def mod_raw_max(self, key, value):
            self.lvl_max[key] += value  # STAT_LVL_MAX
            self.max[key] += value      # STAT_MAX

        def set_base_stat(self, key, value):
            if self.max[key] < value:      # STAT_MAX
                self.max[key] = value      # STAT_MAX
            if self.lvl_max[key] < value:  # STAT_LVL_MAX
                self.lvl_max[key] = value  # STAT_LVL_MAX
            self.stats[key] = value        # STAT_STAT

        def _set_stat(self, key, value):
            self.stats[key] = value        # STAT_STAT

        def _mod_base_stat(self, key, value):
            """
            :param key: the stat to modify
            :param value: the value to modify the stat with
            Modifies the first layer of stats (self.stats)
            A stat can be raised till lvl_max except with negative imod values
            to preserve the interval of possible stat-values (real world example:
            excersicing with extra weights)
            When a stat is decremented, the current limits of the min/max values
            are applied first, then the actual value is applied.
            :returns: the apparent change of the stat
            Check TestSuite.testStats for more details on the expected behaviour.
            """
            curr_value = self._get_stat(key)
            if value >= 0:
                maxval = self.lvl_max[key]
                imod = self.imod[key]
                if imod < 0:
                    maxval -= imod
                stat_value = self.stats[key]                   # STAT_STAT
                value += stat_value
                if value > maxval:
                    if stat_value > maxval:
                        return 0 # do not 'maim' if the value is positive
                    value = maxval

            else:
                # decrement
                imod = self.imod[key]
                stat_value = self.stats[key]                   # STAT_STAT
                maxval = curr_value - imod
                if maxval < stat_value:
                    stat_value = maxval

                value += stat_value

                if value + imod <= 0 and key == "health":
                    value = 1 - imod # use kill_char if you want to remove a char from the game
                    #char = self.instance
                    #if isinstance(char, Player):
                    #    jump("game_over")
                    #elif isinstance(char, Char):
                    #    kill_char(char)
                    #    return

                minval = self.min[key] # TODO use get_min ?
                if value < minval:
                    if stat_value < minval:
                        return 0 # do not 'heal' if the value is negative
                    value = minval

            self.stats[key] = value                        # STAT_STAT

            # return the apparent delta
            return self._get_stat(key) - curr_value

        def _mod_raw_skill(self, key, at, value):
            """Modifies a skill.

            key: the skill to be modified (must be lower case)
            at: 0 - Action Skill
                1 - Training (knowledge part) skill...
            value: the value to be added
            """
            curr_value = self.skills[key][at]

            value *= max(.5, min(self.skills_multipliers[key][at], 2.5)) 
            value *= (1.0 - float(curr_value)/5000) # SKILLS_MAX

            value += curr_value
            self.skills[key][at] = value
            return round_int(value)-round_int(curr_value) # return the real delta

        def mod_full_skill(self, skill, value):
            """This spreads the skill bonus over both action and training.
            """
            self._mod_raw_skill(skill, 0, value/1.5)
            self._mod_raw_skill(skill, 1, value/3.0)

        def degrade_values(self):
            """auto-degrading stats/skills
            """
            for stat in STATIC_CHAR.DEGRADING_STATS:
                value = self._get_stat(stat)
                if value > 100 and dice(value/100):
                    self._mod_base_stat(stat, -1)
            for skill in STATIC_CHAR.SKILLS:
                action, training = self.skills[skill]
                if action > 100 and dice(value/100):
                    self._mod_raw_skill(skill, 0, -1) # out of practice
                if training > 100 and dice(value/100):
                    self._mod_raw_skill(skill, 1, -1) # forget what you've learnt
            joy = self._get_stat("joy")
            if joy > 60:
                self._mod_base_stat("joy", -1)
            elif joy < 40:
                self._mod_base_stat("joy", 1)

        @staticmethod
        def weight_battle_skill(battle_skill, bmpc, _bs_mod_curr, _bs_stats):
            # TODO bind this to BE_Core?
            #                            base_power
            power = (battle_skill.effect + bmpc[1]) * battle_skill.multiplier
            # delivery           
            delivery = battle_skill.delivery
            #                     bonus                                multiplier
            power = (power + _bs_mod_curr[2].get(delivery, 0)) * (1 + _bs_mod_curr[3].get(delivery, 0))
            # elemental bonus
            num = float(len(battle_skill.damage))
            for attr in battle_skill.damage:
                #          el_dmg
                mpl = _bs_mod_curr[4].get(attr, 0)
                if mpl != 0:
                    power *= 1 + mpl/num
            #           damage_multiplier
            power *= 1 + _bs_mod_curr[1]
            #              critical hit
            power *= 1 + _bs_mod_curr[0]*(1.1 + battle_skill.critpower)
            # target(s)
            if battle_skill.type.startswith("all"):
                # "all_enemies", "all_allies"
                if battle_skill.piercing:
                    power *= 1.5 # All
                else:
                    power *= 1.15 # First Row
            elif battle_skill.piercing:
                power *= 1.05 # "Any"
            # cost
            cost = battle_skill.health_cost
            if cost != 0:
                if isinstance(cost, int):
                    cost = float(cost)/_bs_stats[0] # max_hp
                if cost > .05:
                    power *= max(0.1, (1 - cost*10))
            cost = battle_skill.mp_cost
            if cost != 0:
                if isinstance(cost, int):
                    cost = float(cost)/_bs_stats[1] # max_mp
                if cost > .1:
                    power *= max(0.1, (1 - cost*5))
            cost = battle_skill.vitality_cost
            if cost != 0:
                if isinstance(cost, int):
                    cost = float(cost)/_bs_stats[2] # max_vitality
                if cost > .1:
                    power *= max(0.1, (1 - cost*5))
            #temp = ", ".join([str(delivery_multiplier[m]) for m in battle_skill.attributes])
            #devlog.warn("Battle-skill: %s - power: %s ... (base_power:%s, bonus:%s, multiplier:%s, dms:%s target:%s)" % (battle_skill.name, power, bmpc[1], bmpc[3], bmpc[4], temp, battle_skill.type))
            return power

        @staticmethod
        def weight_def_mod(delivery, bmpc, _bs_mod_curr, resists):
            # TODO bind this to BE_Core?
            #                      bonus                                  multiplier
            defense = (bmpc[1] + _bs_mod_curr[7].get(delivery, 0)) * (1 + _bs_mod_curr[8].get(delivery, 0))

            # evasion_bonus
            ev = _bs_mod_curr[9]
            if ev != 0 and delivery in ["melee", "ranged"]:
                defense = defense * (100 + ev) / 100.0

            # el_def
            el_def = _bs_mod_curr[5]
            for type, value in el_def.iteritems():
                if type in resists:
                    continue
                defense *= 1.0 + (value / 40) # 40 is just a guess from len(BE_Core.DAMAGE) * len(BE_Core.DELIVERY)

            # absorbs
            for type, value in _bs_mod_curr[6].iteritems():
                if type in resists:
                    continue
                value = .4 * (1.0 - el_def.get(type, 0)) # absorb worth more, if the char is not protected against that element anyway 
                defense *= 1.0 + (value / 40) # 40 is just a guess from len(BE_Core.DAMAGE) * len(BE_Core.DELIVERY)

            return defense

        def weight_items(self, items, target_stats, target_skills, fighting, upto_skill_limit):
            """
            weights the list of items based on stats for current or future use.

            :param items: the list of items to weight
            :param target_stats: a dict of stat-weight pairs to consider for items
            :param target_skills: similarly, a dict of skill-weight pairs
            :param fighting: check added battle-skills of the items
            :param upto_skill_limit: whether or not to calculate bonus beyond training exactly
            """
            char = self.instance

            _stats_mul_curr_max = {}
            for stat, value in target_stats.iteritems():
                if stat == "exp":
                    value = [value*(1 - float(char.tier)/MAX_TIER), None, None]
                elif stat == "gold":
                    value = [float(value)/max(char.gold, 100), None, None]
                else:            
                    value = [value,
                             self._get_stat(stat),
                             self.get_max(stat),
                             self.stats[stat] + self.imod[stat],   # STAT_STAT + STAT_IMOD
                             self.max[stat] + self.imax[stat],     # STAT_MAX + STAT_IMAX
                             self.lvl_max[stat],                   # STAT_LVL_MAX
                             self.min[stat] + self.imin[stat],     # STAT_MIN  + STAT_IMIN
                             stat in ("health", "vitality", "mp")] # BATTLE_STATS
                    
                _stats_mul_curr_max[stat] = value
            _skills_mul_curr = {skill:
                                  [value, self.get_skill(skill), self.skills_multipliers[skill][2], self.skills[skill][0], self.skills[skill][1]]
                                for skill, value in target_skills.iteritems()}

            is_kamidere, is_tsundere, is_bokukko = False, False, False
            level, char_traits = char.level, char.traits
            for trait in char_traits:
                # Other traits:
                trait = trait.id # never compare trait entity with trait str, it is SLOW
                if trait == "Kamidere":
                    is_kamidere = True
                elif trait == "Tsundere":
                    is_tsundere = True
                elif trait == "Bokukko":
                    is_bokukko = True
            if fighting is True:
                # critical_hit_chance, damage_multiplier, delivery_bonus, delivery_multiplier, el_dmg, el_def, absorbs, defence_bonus, defence_multiplier, evasion_bonus
                _bs_mod_curr = BE_Core.get_trait_modifiers(char_traits, level)
                # critical_hit_chance, damage_multiplier, delivery_bonus, delivery_multiplier, el_dmg, el_def, absorbs, defence_bonus, defence_multiplier, evasion_bonus
                _bs_item_curr = BE_Core.get_item_modifiers(char.eqslots.itervalues())
                BE_Core.merge_modifiers(_bs_mod_curr, _bs_item_curr)

                # TODO bind this to BE_Core ?
                resists = char.resist
                constitution = char.get_stat("constitution")
                intelligence = char.get_stat("intelligence")
                attack = char.get_stat("attack")
                defence = char.get_stat("defence")
                agility = char.get_stat("agility")
                magic = char.get_stat("magic")
                constitution_value = target_stats.get("constitution", 0)
                intelligence_value = target_stats.get("intelligence", 0)
                attack_value = target_stats.get("attack", 0)
                defence_value = target_stats.get("defence", 0)
                agility_value = target_stats.get("agility", 0)
                magic_value = target_stats.get("magic", 0)
                _bs_mul_def_curr = {"melee": [defence_value*.7 + constitution_value*.3, defence*.7 + constitution*.3, None],
                                    "ranged": [defence_value*.7 + agility_value*.3, defence*.7 + agility*.3, None],
                                    "magic": [defence_value*.4 + magic_value*.2 + intelligence_value*.4, defence*.4 + magic*.2 + intelligence*.4, None],
                                    "status": [defence_value*.4 + intelligence_value*.3 + constitution_value*.3, defence*.4 + intelligence*.3 + constitution*.3, None]}
                for delivery, bmpc in _bs_mul_def_curr.iteritems():
                    bmpc[0] /= 4 # len(BE_Core.DELIVERY)
                    bmpc[2] = Stats.weight_def_mod(delivery, bmpc, _bs_mod_curr, resists)

                _bs_mul_power_curr = {"melee": [attack_value*.7 + agility_value*.3, attack*.7 + agility*.3, 0, None],
                                      "ranged": [agility_value*.7 + attack_value*.3, agility*.7 + attack*.3, 0, None],
                                      "magic": [magic_value*.7 + intelligence_value*.3, magic*.7 + intelligence*.3, 0, None],
                                      "status": [intelligence_value*.7 + agility_value*.3, intelligence*.7 + agility*.3, 0, None]}

                _bs_stats = [max(1, char.get_max(stat)) for stat in ("health", "mp", "vitality")] # BATTLE_STATS
                front_row = char.front_row == 1
                char_magics = char.magic_skills
                for battle_skill in itertools.chain(char.attack_skills, char_magics):
                    if front_row is False and battle_skill.range == 1:
                        continue
                    bmpc = _bs_mul_power_curr[battle_skill.delivery]
                    power = Stats.weight_battle_skill(battle_skill, bmpc, _bs_mod_curr, _bs_stats)
                    if power > bmpc[2]: # best power
                        bmpc[2] = power
                        bmpc[3] = battle_skill

                    #devlog.warn("Battle-skill: %s - power: %s" % (battle_skill.name, power))
                #devlog.warn("Attack: %s, Agility: %s, Magic %s, Intelligence %s" % (attack, agility, magic, intelligence))
                #for delivery, power in _bs_mul_power_curr.iteritems():
                #    devlog.warn("Delivery: %s - stats: %s" % (delivery, ", ".join(["%s"%p for p in power])))

            result = []
            for item in items:
                #weights = []
                weights = 0
                for trait in item.badtraits:
                    if trait in char_traits:
                        weights = None
                        break
                if weights is None:
                    #aeq_debug("Ignoring item %s on badtraits.", item)
                    continue

                # Stats:
                slot = item.slot
                for stat, value in item.mod.iteritems():
                    mcm = _stats_mul_curr_max.get(stat, None)
                    if mcm is None:
                        continue
                    # a new max may have to be considered
                    new_max = mcm[2]
                    if new_max is None:
                        # exp/gold
                        #weights.append(mcm[0]*value)
                        weights += mcm[0]*value
                        continue
                        
                    if stat in item.max:
                        #             s_max                    l_max
                        new_max = min(mcm[4] + item.max[stat], mcm[5])

                    if slot == "consumable" and mcm[7]:
                        # one-time restore item -> add value limited by max - s_min
                        change = min(value, new_max - mcm[6])
                    else:
                        # normal item -> check gain
                        # Result:         si_curr                   s_min
                        new_stat = max(min(mcm[3] + value, new_max), mcm[6])
                        change = new_stat - mcm[1] # curr_stat
                        if change != value:
                            # max/min alters the effect of the item -> check for partial gain
                            if change == 0:
                                if value < 0:
                                    # does not help, but does not hurt much either -> skip
                                    continue
                                if slot == "misc" and not item.mreusable:
                                    #weights.append(-100*value)
                                    weights -= 100 * value # add waste TODO should be applied only for equip
                                    #devlog.warn("Waste for Stat-Weight:%s - 0 - %s" % (stat, value))
                                    continue
                                # the item could help, but not now (except for lvl_max)
                                value *= .5 #       l_max        BATTLE_STATS             restore items?
                                if (mcm[3]+value) > mcm[5] and not (mcm[7] and slot == "misc" and item.mreusable):
                                    continue
                                change = value
                            elif change > 0:
                                if item.slot == "misc" and not item.mreusable:
                                    #weights.append(-100*(value - change))
                                    weights -= 100 * (value - change) # add waste TODO should be applied only for equip
                                    #devlog.warn("Waste for Stat-Weight:%s - %s  - %s" % (stat, change, value))
                                    continue
                                # it is worth at least as much as if it would not help now
                                value *= .5
                                if change < value and ((mcm[3] + value) <= mcm[5] or # si_curr + value <= lvl_max
                                         (mcm[7] and slot == "misc")):               # BATTLE_STATS and restore items?
                                    change = value
                    if new_max <= 0:
                        # new max is negative or zero, change must be negative -> make sure the result is negative
                        new_max = 1 
                    # add the fraction increase/decrease
                    #weights.append(mcm[0]*100*change/float(new_max))
                    #weights += mcm[0]*100*change/float(new_max)
                    #devlog.warn("Add Stat-Weight:%s - %s  - %s" % (stat, change, new_max))
                    weights += mcm[0]*change/float(new_max)

                #devlog.warn("Weights after stat:%s" % weights)
                # Max Stats:
                for stat, value in item.max.iteritems():
                    mcm = _stats_mul_curr_max.get(stat, None)
                    if mcm is None:
                        continue
                    #             s_max          l_max
                    new_max = min(mcm[4] + value, mcm[5])
                    change = new_max - mcm[2] # curr_max
                    if change == 0:
                        continue
                    if stat not in item.mod:
                        #                     si_curr  curr_stat
                        change += min(new_max, mcm[3]) - mcm[1]
                    if new_max <= 0:
                        # new max is negative or zero, change must be negative -> make sure the result is negative
                        new_max = 1 
                    # add the fraction increase/decrease
                    #weights.append(mcm[0]*100*change/float(new_max))
                    #weights += mcm[0]*100*change/float(new_max)
                    weights += mcm[0]*change/float(new_max)

                #devlog.warn("Weights after max:%s" % weights)
                # Skills:
                for skill, effect in item.mod_skills.iteritems():
                    smc = _skills_mul_curr.get(skill, None)
                    if smc is None:
                        continue
                    # calculate skill with mods applied, as in apply_item_effects() and get_skill()
                    mod_skill_multiplier = smc[2] + effect[2] # curr_multiplier + mod_multiplier
                    mod_action = smc[3] + effect[3]           # curr_action + mod_action
                    mod_training = smc[4] + effect[4]         # curr_training + mod_training

                    if upto_skill_limit: # more precise calculation of skill limits
                        beyond_training = mod_action - (mod_training * 3)
                        if beyond_training >= 0:
                            mod_action -= beyond_training / 1.5

                    mod_training += mod_action
                    if mod_training > 5000: # SKILLS_MAX
                        mod_training = 5000 # SKILLS_MAX
                    new_skill = mod_training*max(min(mod_skill_multiplier, 2.5), .5)
                    change = new_skill - smc[1] # curr_skill
                    if change == 0:
                        continue
                    # add the fraction increase/decrease
                    #weights.append(smc[0]*100*change/5000.0) # SKILLS_MAX
                    #weights += smc[0]*100*change/5000.0 # SKILLS_MAX
                    weights += smc[0]*change/5000.0 # SKILLS_MAX

                #devlog.warn("Weights after skill:%s" % weights)
                if fighting is True:
                    # gain on current skills
                    #debug_modifiers = ["ch", "damage_mpl", "delivery_bonus", "delivery_mpl", "el_dmg", "el_def", "absorbs", "defence_bonus", "defence_mpl", "ev"]
                    #devlog.warn("Curr modifs:%s" % ", ".join([(debug_modifiers[idx] + ": " + str(i)) for idx, i in enumerate(_bs_mod_curr)]))
                    if item.be_modifiers is None:
                        _bs_mod_new = _bs_mod_curr
                    else:
                        _bs_mod_new = BE_Core.get_item_modifiers((item, ))
                        #devlog.warn("Base-Item modifs:%s" % ", ".join([str(i) for i in _bs_mod_new]))
                        BE_Core.merge_modifiers(_bs_mod_new, _bs_mod_curr)
                    #devlog.warn("AddTraits:%s" % ", ".join([str(i) for i in item.addtraits]))
                    for t in item.addtraits:
                        if t.be_modifiers is None or t in char_traits:
                            continue
                        _bs_trait_new = BE_Core.get_trait_modifiers((t, ), level)
                        #devlog.warn("Trait modifs:%s" % ", ".join([str(i) for i in _bs_mod_trait]))
                        if _bs_mod_new is _bs_mod_curr:
                            _bs_mod_new = deepcopy(_bs_mod_curr)
                        BE_Core.merge_modifiers(_bs_mod_new, _bs_trait_new)
                    # FIXME remove traits? 
                    #devlog.warn("New modifs:%s" % ", ".join([(debug_modifiers[idx] + ": " + str(i)) for idx, i in enumerate(_bs_mod_new)]))
                    if _bs_mod_new is not _bs_mod_curr:
                        # weight offensive modifiers
                        off_mod = any((_bs_mod_new[i] != _bs_mod_curr[i] for i in xrange(6)))
                        if off_mod is True:
                            for bmpc in _bs_mul_power_curr.itervalues():
                                curr_power = bmpc[2]
                                if curr_power == 0:
                                    continue
                                #                              battle_skill
                                power = Stats.weight_battle_skill(bmpc[3], bmpc, _bs_mod_new, _bs_stats)
                                #new_power = power
                                power -= curr_power
                                if power == 0:
                                    continue
                                #weights.append(bmpc[0]*change/curr_power)
                                weights += bmpc[0]*power/float(curr_power)
                                #devlog.warn("Gain on Current Skill: %s" % (bmpc[0]*float(power-curr_power)/curr_power))
                                #devlog.warn("Gain on Current Off Mod (%s): new power:%s, curr power: %s" % (bmpc[0], new_power, curr_power))
                        #devlog.warn("Weights after off:%s" % weights)
                        # weight defensive modifiers
                        def_mod = not off_mod or any((_bs_mod_new[i] != _bs_mod_curr[i] for i in xrange(5, 10)))
                        if def_mod is True:
                            for delivery, bmpc in _bs_mul_def_curr.iteritems():
                                curr_power = bmpc[2]
                                power = Stats.weight_def_mod(delivery, bmpc, _bs_mod_new, resists)
                                #new_power = power
                                if curr_power != 0:
                                    power -= curr_power*.9 # LEEWAY
                                    power /= curr_power
                                weights += bmpc[0]*power
                                #devlog.warn("Gain on Current Def Mod (%s): new power:%s, curr power: %s" % (bmpc[0], new_power, curr_power))

                    #devlog.warn("Weights after curr bs skill:%s" % weights)
                    # gain from new skills
                    # Attacks:
                    if item.attacks is not None:
                        best = {}

                        # check the skills power TODO bind this to BE_Core?
                        for battle_skill in item.attacks:
                            if front_row is False and battle_skill.range == 1:
                                continue
                            delivery = battle_skill.delivery
                            bmpc = _bs_mul_power_curr[delivery]
                            power = Stats.weight_battle_skill(battle_skill, bmpc, _bs_mod_new, _bs_stats)
                            if power > best.get(delivery, 0): # best
                                best[delivery] = power
                                #if bmpc[2] == 0:
                                #    temp = bmpc[0]+power
                                #else:
                                #    temp = bmpc[0]*(power-bmpc[2]/2)/float(bmpc[2])
                                #devlog.warn("Attack skill %s bonus: %s - delivery: %s " % (battle_skill.name, temp, delivery))
                        for delivery, power in best.iteritems():
                            bmpc = _bs_mul_power_curr[delivery]
                            # add the fraction increase/decrease TODO cost?
                            curr_best = bmpc[2]
                            if curr_best != 0:
                                power -= curr_best*.9 # LEEWAY
                                power /= curr_best
                            weights += bmpc[0]*power
                            #if curr_best == 0:
                            #    #weights.append(2*bmpc[0])
                            #    weights += bmpc[0]+power
                            #else:
                            #    #weights.append(bmpc[0]*power/curr_best)
                            #    weights += bmpc[0]*(power-curr_best/2)/float(curr_best)

                    #devlog.warn("Weights after attack:%s" % weights)
                    # Spells:
                    for battle_skill in item.add_be_spells:
                        #if front_row is False and battle_skill.range == 1:
                        #    continue
                        if battle_skill in char_magics:
                            continue
                        bmpc = _bs_mul_power_curr[battle_skill.delivery]
                        power = Stats.weight_battle_skill(battle_skill, bmpc, _bs_mod_new, _bs_stats)
                        #new_power = power
                        curr_best = bmpc[2] # TODO how to differentiate between poison and buff spells?
                        if curr_best != 0:
                            power -= curr_best*.9 # LEEWAY
                            power /= curr_best
                        weights += bmpc[0]*power
                        #if curr_best == 0:
                        #    weights += bmpc[0]+power
                        #else:
                        #    # FIXME right now there is only a single battle_skill per item, might change in the future 
                        #    #weights.append(bmpc[0]*power/curr_best)
                        #    weights += bmpc[0]*float(power-curr_best/2)/curr_best
                        #devlog.warn("Spell: %s - power: %s - relative to %s - weight: %s - mpl: %s" % (battle_skill.name, new_power, curr_best, weights, bmpc[0]))

                #devlog.warn("Weights after fighting:%s" % weights)

                # Other traits and modifiers:
                for trait in item.goodtraits:
                    if trait in char_traits:
                        #weights.append(100)
                        weights *= 2

                #devlog.warn("Weights after good traits:%s" % weights)

                if is_kamidere is True: # Vanity: wants pricy, uncommon items
                    #weights.append((100 - item.chance + min(item.price/10, 100))/2)
                    weights *= (100 - item.chance)/100.0
                elif is_tsundere is True: # stubborn: what s|he won't buy, s|he won't wear.
                    weights *= item.eqchance/100.0
                elif is_bokukko is True: # what the farmer don't know, s|he won't eat.
                    #weights.append(item.chance)
                    weights *= (100 + item.chance)/100.0

                result.append([weights, item])

            if DEBUG_AUTO_ITEM:
                temp = "A-Eq=> %s:" % self.instance.name
                for _weight, item in result:
                    temp += "\n Slot: %s Item: %s ==> Weight: %s" % (item.slot, item.id, _weight)
                aeq_debug(temp)

            return result

        def weight_for_consume(self, items, target_stats):
            """
            weights the list of items based on stats for current consumption.

            :param items: the list of items to weight
            :param target_stats: a dict of stat-weight pairs to consider for items
            """
            char = self.instance

            _stats_mul_curr_max = {}
            for stat in target_stats:
                if stat == "exp":
                    value = [(1 - float(char.tier)/MAX_TIER), None, None]
                elif stat == "gold":
                    value = [1.0/max(char.gold, 100), None, None]
                else: #                                                          STAT_STAT + STAT_IMOD              STAT_MAX + STAT_IMAX        STAT_LVL_MAX              STAT_MIN + STAT_IMIN
                    value = [1, self._get_stat(stat), self.get_max(stat), self.stats[stat] + self.imod[stat], self.max[stat] + self.imax[stat], self.lvl_max[stat], self.min[stat] + self.imin[stat]]
                    
                _stats_mul_curr_max[stat] = value

            # prepare delivery information TODO bind this to BE_Core?
            char_traits = char.traits

            # traits that may influence the item selection process
            appetite = 3
            addiction = 2
            for trait in char_traits:
                trait = trait.id # never compare trait entity with trait str, it is SLOW
                # a clumsy or bad eyesighted person may cause select items not in target stat/skill
                # a stupid person may also select items regardless of target stats
                if trait == "Slim":
                    appetite -= 1
                elif trait == "Always Hungry":
                    appetite += 1
                elif traits == "Heavy Drinker":
                    addiction *= 2
            depressed = 'Depression' in char.effects
            drunk = 'Drunk' in char.effects
            if 'Food Poisoning' in char.effects:
                appetite = -1
            else:
                appetite -= char.get_flag("dnd_food_poison_counter", 0)/2

            result = []
            for item in items:
                if item in char.constemp or item in char.consblock:
                    #aeq_debug("Ignoring item %s on blocks.", item)
                    continue

                #weights = []
                weights = 0
                for trait in item.badtraits:
                    if trait in char_traits:
                        weights = None
                        break
                if weights is None:
                    #aeq_debug("Ignoring item %s on badtraits.", item)
                    continue

                # Stats:
                for stat, value in item.mod.iteritems():
                    mcm = _stats_mul_curr_max.get(stat, None)
                    if mcm is None:
                        if value < 0:
                            if stat == "exp":
                                pass
                            elif stat == "gold":
                                if char.gold >= value*-10:
                                    continue
                            elif self.stats[stat] >= value*-10: # STAT_STAT
                                continue 
                            weights = None
                            break
                        weights -= value # add waste
                        continue
                    if value < 0:
                        weights = None
                        break
                    # a new max may have to be considered
                    new_max = mcm[2]
                    if new_max is None:
                        # exp/gold
                        #weights.append(mcm[0]*value)
                        weights += mcm[0]*value
                        continue

                    if stat in item.max:
                        #             s_max                    l_max
                        new_max = min(mcm[4] + item.max[stat], mcm[5])

                    # Result:         si_curr                    s_min
                    new_stat = max(min(mcm[3] + value, new_max), mcm[6])
                    change = new_stat - mcm[1] # curr_stat
                    # add the gain-waste
                    #weights.append(mcm[0]*100*change/float(new_max))
                    weights += mcm[0] * (2*change-value)

                if weights is None:
                    #aeq_debug("Ignoring item %s on stat mods.", item)
                    continue

                # Max Stats:
                for stat, value in item.max.iteritems():
                    mcm = _stats_mul_curr_max.get(stat, None)
                    if mcm is None:
                        if value < 0:
                            if self.stats[stat] >= value*-10: # STAT_STAT
                                continue 
                            weights = None
                            break
                        weights -= value # add waste
                        continue
                    if value < 0:
                        weights = None
                        break
                    #              s_max          l_max
                    new_max = min(mcm[4] + value, mcm[5])
                    change = new_max - mcm[2] # curr_max
                    if stat not in item.mod:
                        #                     si_curr  curr_stat
                        change += min(new_max, mcm[3]) - mcm[1]
                    # add the gain-waste
                    #weights.append(mcm[0]*100*change/float(new_max))
                    weights += mcm[0]*(2*change-value)

                # Skills:
                for effect in item.mod_skills.itervalues():
                    if effect[2] < 0 or effect[3] < 0 or effect[4] < 0:
                        weights = None
                        break

                if weights is None or weights <= 0:
                    #aeq_debug("Ignoring item %s on gain.", item)
                    continue # we need gain NOW, but there isn't any -> skip

                # Other traits and modifiers:
                if item.type == "alcohol":
                    if drunk:
                        continue
                    if depressed:
                        weights *= addiction
                elif item.type == "food":
                    if appetite < 0:
                        continue
                    weights *= appetite

                if weights <= 0:
                    #aeq_debug("Ignoring item %s on fitness.", item)
                    continue

                result.append([weights, item])

            if DEBUG_AUTO_ITEM:
                temp = "A-Eq=> %s:" % self.instance.name
                for _weight, item in result:
                    temp += "\n Slot: %s Item: %s ==> Weight: %s" % (item.slot, item.id, _weight)
                aeq_debug(temp)

            return result

    class Pronouns(_object):
        # Just to keep huge character class cleaner (smaller)
        # We can move this back before releasing...
        @property
        def mc_ref(self):
            if self._mc_ref is None:
                if self.status == "slave":
                    return "Master"
                else:
                    return hero.name
            else:
                return self._mc_ref

        @property
        def p(self):
            # Subject pronoun (he/she/it): (prolly most used so we don't call it 'sp'):
            if self.gender == "female":
                return "she"
            elif self.gender == "male":
                return "he"
            else:
                return "it"

        @property
        def pC(self):
            # Subject pronoun (he/she/it) capitalized:
            return self.p.capitalize()

        @property
        def op(self):
            # Object pronoun (him, her, it):
            if self.gender == "female":
                return "her"
            elif self.gender == "male":
                return "him"
            else:
                return "it"

        @property
        def opC(self):
            # Object pronoun (him, her, it) capitalized:
            return self.op.capitalize()

        @property
        def pd(self):
            # Possessive determiner (his, her, its):
            # This may 'gramatically' incorrect, cause things (it) cannot possess/own anything but knowing PyTFall :D
            if self.gender == "female":
                return "her"
            elif self.gender == "male":
                return "his"
            else:
                return "its"

        @property
        def pdC(self):
            # Possessive determiner (his, her, its) capitalized::
            return self.pd.capitalize()

        @property
        def pp(self):
            # Possessive pronoun (his, hers, its):
            # This may 'gramatically' incorrect, cause things (it) cannot possess/own anything but knowing PyTFall :D
            if self.gender == "female":
                return "hers"
            elif self.gender == "male":
                return "his"
            else:
                return "its"

        @property
        def hs(self):
            if self.gender == "female":
                return "sister"
            else:
                return "brother"

        @property
        def hsC(self):
            return self.hs.capitalize()

        @property
        def hss(self):
            if self.gender == "female":
                return "sis"
            else:
                return "bro"


    class CharEffect(_object):
        def __init__(self, name, duration=10, ss_mod=None):
            self.name = name
            self.duration = duration # For how long does the effect remain active (if desired)
            self.days_active = 0
            self.ss_mod = ss_mod  # Stats/Skills mod!

        def __repr__(self):
            return str(self.name)

        @property
        def desc(self):
            global effect_descs
            desc = effect_descs.get(self.name, "No Description available.")
            return str(desc)

        def next_day(self, char):
            '''Called on next day, applies effects'''
            self.days_active += 1

            name = self.name
            if name == "Assertive":
                if char.get_stat("character") < char.get_max("character")/2:
                    char.mod_stat("character", 2)
            elif name == "Unstable":
                if self.days_active == self.duration:
                    char.mod_stat("joy", self.ss_mod["joy"])
                    self.duration += randint(2, 4)
                    ss_mod = randrange(22)
                    self.ss_mod['joy'] = (9+ss_mod) if ss_mod > 10 else -(20+ss_mod)
            elif name == "Optimist":
                if char.get_stat("joy") >= 30:
                    char.mod_stat("joy", 1)
            elif name == "Pessimist":
                joy = char.get_stat("joy")
                if joy > 80:
                    char.mod_stat("joy", -2)
                elif joy > 10 and dice(60):
                    char.mod_stat("joy", -1)
            elif name == "Composure":
                joy = char.get_stat("joy")
                if joy < 50:
                    char.mod_stat("joy", 1)
                elif joy > 70:
                    char.mod_stat("joy", -1)
            elif name == "Diffident":
                if char.get_stat("character") > char.get_max("character")/2:
                    char.mod_stat("character", -2)
            elif name == "Vigorous":
                vit = char.get_stat("vitality")
                if vit < char.get_max("vitality")/4:
                    char.mod_stat("vitality", randint(2, 3))
                elif vit < char.get_max("vitality")/2:
                    char.mod_stat("vitality", randint(1, 2))
            elif name == "Kleptomaniac":
                if dice(char.get_stat("luck")+55):
                    char.add_money(randint(5, 25), reason="Kleptomania")
            elif name == "Injured":
                mod = char.get_max("health")/5 - char.get_stat("health")  
                if mod < 0:
                    char.mod_stat("health", mod)
                mod = char.get_max("vitality")/2 - char.get_stat("vitality")
                if mod < 0:
                    char.mod_stat("vitality", mod)
                char.mod_stat("joy", -10)
                char.take_ap(1)
                if self.days_active >= self.duration:
                    self.end(char)
            elif name == "Down with Cold":
                char.mod_stat("health", self.ss_mod["health"])
                char.mod_stat("vitality", self.ss_mod['vitality'])
                char.mod_stat("joy", self.ss_mod['joy'])
                if self.days_active >= self.duration:
                    self.end(char)
            elif name == "Food Poisoning":
                char.mod_stat("health", self.ss_mod["health"])
                char.mod_stat("vitality", self.ss_mod['vitality'])
                char.mod_stat("joy", self.ss_mod['joy'])
                if self.days_active >= self.duration:
                    self.end(char)
            elif name == "Drunk":
                char.mod_stat("vitality", -char.get_flag("dnd_drunk_counter", 0))
                char.mod_stat("health", -10)
                char.mod_stat("joy", -5)
                char.mod_stat("mp", -20)
                if char.status == "free" and char != hero:
                    # unequip unwanted items (not equipped by the char)
                    purpose = None
                    for item in char.eqslots.itervalues():
                        if item is None or item.eqchance > 0:
                            continue
                        if purpose is None:
                            purpose = char.last_known_aeq_purpose
                            purpose = STATIC_ITEM.AEQ_PURPOSES.get(purpose, None)
                            if purpose is None:
                                purpose = set()
                            else:
                                purpose = purpose.get("base_purpose")
                        if item.goodtraits.isdisjoint(char.traits) and purpose.isdisjoint(item.pref_class):
                            char.unequip(item, aeq_mode=True)
                if 'Drinker' not in char.effects: # TODO check for Heavy Drinker trait?
                    char.take_ap(1)
                self.end(char)
            elif name == "Poisoned":
                self.ss_mod["health"] -= self.duration*5
                char.mod_stat("health", self.ss_mod["health"])
                if self.days_active >= self.duration:
                    self.end(char)
            elif name == "Lactation": # TODO add milking activities, to use this fetish more widely
                if char.get_stat("health") >= 30 and char.get_stat("vitality") >= 30:
                    if "Slime" in char.traits:
                        item = "Slime's Milk"
                    else:
                        item = "Bottle of Milk"
                    if char.employer == hero and char.is_available and (char.status == "slave" or check_lovers(char)):
                        boobs = char.gents.id
                        if boobs.startswith("Ab"):  # "Abnormally Large Boobs"
                            num = randint(2, 5)
                        elif boobs.startswith("B"): # "Big Boobs"
                            num = randint(2, 3)
                        elif boobs.startswith("Av"):# "Average Boobs"
                            num = randint(1, 2)
                        else:                       # "Small Boobs"
                            num = 1
                        hero.add_item(item, num)
                    else:
                        # in order to not stack bottles of milk into free chars inventories they get only one, and only if they had 0
                        if not(has_items(item, char, equipped=False)):
                            char.add_item(item)
            elif name == "Regeneration":
                if "Summer Eternality" in char.traits:
                    h = max(1, char.get_max("health")/2)
                else:
                    h = 30
                char.mod_stat("health", h)
            elif name == "MP Regeneration":
                if "Winter Eternality" in char.traits:
                    h = max(1, char.get_max("mp")/2)
                else:
                    h = 30
                char.mod_stat("mp", h)
            elif name == "Small Regeneration":
                char.mod_stat("health", 15)
            elif name == "Blood Connection":
                char.mod_stat("disposition", 2)
                char.mod_stat("character", -1)
            elif name == "Sibling":
                dispo = char.get_stat("disposition")
                if dispo < 100:
                    char.mod_stat("disposition", 2)
                elif dispo < 200:
                    char.mod_stat("disposition", 1)
                if char.get_stat("affection") < 200 and "Sister Lover" in hero.traits:
                    char.mod_stat("affection", 1)

        def end(self, char):
            name = self.name
            if name in char.effects:
                del(char.effects[name])

                # Reset counters to be safe, usually done elsewhere...
                if name == "Exhausted":
                    char.del_flag("exhausted_counter")
                elif name == "Drunk":
                    char.del_flag("dnd_drunk_counter")
                elif name == "Food Poisoning":
                    char.del_flag("dnd_food_poison_counter")
                elif name == "Depression":
                    char.del_flag("depression_counter")
                elif name == "Elation":
                    char.del_flag("elation_counter")

        def enable(self, char):
            char.effects[self.name] = self
