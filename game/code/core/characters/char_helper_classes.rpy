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

        def get_max_skill(self, skill, tier=None):
            if tier is None:
                tier = self.tier or .5
            return SKILLS_MAX[skill]*(tier*.1)

        def get_relative_max_stat(self, stat, tier=None):
            # used in a number of places to guess what the max stat for n tier might be.
            if tier is None:
                tier = self.tier or .5

            if stat in self.stats.get_base_ss():
                max_val = 1000
            else:
                max_val = 500

            return max_val*(tier*.1)

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
                #self.tier = MAX_TIER
                return False

            target_tier = self.tier+1.0 # To get a float for Py2.7
            target_level = (target_tier)*20
            if target_level > self.level:
                tier_points = 0 # We need 100 to tier up!

                level_points = self.level*50.0/target_level

                default_points = 12.5
                skill_bonus = stat_bonus = 0
                for trait in self.traits.basetraits:
                    # Skills first (We calc this as 12.5% of the total)
                    skills = trait.base_skills
                    if not skills: # Some weird ass base trait, we just award 33% of total possible points.
                        skill_bonus += default_points*.33
                    else:
                        total_weight_points = sum(skills.values())
                        for skill, weight in skills.items():
                            weight_ratio = float(weight)/total_weight_points
                            max_p = default_points*weight_ratio

                            sp = self.get_skill(skill)
                            sp_required = self.get_max_skill(skill, target_tier)

                            skill_bonus += min(float(sp)/sp_required, 1.1)*max_p

                    stats = trait.base_stats
                    if not stats: # Some weird ass base trait, we just award 33% of total possible points.
                        stat_bonus += default_points*.33
                    else:
                        total_weight_points = sum(stats.values())
                        for stat, weight in stats.items():
                            weight_ratio = float(weight)/total_weight_points
                            max_p = default_points*weight_ratio

                            sp = self.stats.stats[stat]
                            if stat in STATIC_CHAR.FIXED_MAX:
                                sp_required = self.get_max(stat)
                            else:
                                sp_required = self.get_relative_max_stat(stat, target_tier)

                            stat_bonus += min(float(sp)/sp_required, 1.1)*max_p

                stats_skills_points = skill_bonus + stat_bonus
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

            self.tier = min(MAX_TIER, self.tier+1)
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
                for i in ["Combatant", "Specialist", "SIW", "Server"]:
                    if i in self.gen_occs:
                        wage = STATIC_CHAR.BASE_WAGES[i]
                        break
                else:
                    raise Exception("Impossible character detected! ID: {} ~ BT: {} ~ Occupations: {}".format(self.id,
                                    ", ".join([str(t) for t in self.traits.basetraits]), ", ".join([str(t) for t in self.occupations])))

            # Each tier increases wage by 50% without stacking:
            wage = wage + wage*self.tier*.5

            if "Dedicated" in self.traits:
                wage = wage*.75

            # Normalize:
            wage = max(int(round(wage)), 10)

            self.expected_wage = wage
            return wage

        def update_tier_info(self, kind=None):
            while self.recalculate_tier():
                continue 
            self.calc_expected_wage(kind=kind)

        # We need "reverse" calculation for when leveling up characters
        # Mainly to figure out their skill levels, maybe moar in the future
        def level_up_tier_to(self, level):
            level_mod = level*.5 # We take level 200 as max...

            skills = {}
            # First, we get highest skill relevance from basetraits:
            for bt in self.traits.basetraits:
                for skill, value in bt.base_skills.items():
                    skills[skill] = max(skills.get(skill, 0), value)

            # Bit of an issue here is that we do not mind threathholds, not sure that it's a good thing.
            for skill, value in skills.items():
                value = (MAX_SKILLS[skill]*.01*value)*(.01*level_mod)
                self.stats.mod_full_skill(skill, value)


    class Team(_object):
        def __init__(self, name="", implicit=None, free=False, max_size=3):
            if not implicit:
                implicit = list()
            self.name = name
            self.implicit = implicit
            self.max_size = max_size
            self._members = list()
            self._leader = None
            self.free = free # Free teams do not have any implicit members.

            # BE Assests:
            self.position = None # BE will set it to "r" or "l" short for left/right on the screen.

            if self.implicit:
                for member in self.implicit:
                    self.add(member)

        def __len__(self):
            return len(self._members)

        def __iter__(self):
            return iter(self._members)

        def __getitem__(self, index):
            return self._members[index]

        def __nonzero__(self):
            return bool(self._members)

        @property
        def members(self):
            return self._members

        @property
        def leader(self):
            try:
                return self.members[0]
            except:
                return self._leader

        def add(self, member):
            if member in self:
                notify("Impossible to join the same team twice")

            if len(self._members) >= self.max_size:
                notify("{} team cannot have more than {} members!".format(self.name, self.max_size))
            else:
                if not self.free and not self.leader:
                    self._leader = member
                    if member not in self.implicit:
                        self.implicit.append(member)
                self._members.append(member)
                return True

        def remove(self, member):
            if member in self.implicit or member not in self._members:
                notify("%s is not a member of this team or an implicit member of this team!"%member.name)
            else:
                self._members.remove(member)

        def set_leader(self, member):
            if member not in self._members:
                notify("%s is not a member of this team!"%member.name)
                return
            if self.leader:
                self.implicit.remove(self.leader)
            self._leader = member
            self.implicit.insert(0, member)

        def get_level(self):
            """
            Returns an average level of the team as an integer.
            """
            av_level = 0
            for member in self._members:
                av_level += member.level
            return int(math.ceil(av_level/len(self._members)))

        def get_rep(self):
            """
            Returns average of arena reputation of a team as an interger.
            """
            arena_rep = 0
            for member in self._members:
                arena_rep += member.arena_rep
            return int(math.ceil(arena_rep/len(self._members)))

        # BE Related:
        def reset_controller(self):
            # Resets combat controller
            for m in self.members:
                m.controller = None


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
            self.list = _list()

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
                    if item in store.battle_skills:
                        item = store.battle_skills[item]
                    else:
                        char_debug("Tried to apply unknown skill %s to %s!" % (item, self.instance.__class__))
                        return
            if normal: #  Item applied by anything other than that
                self.normal.add(item)
            else:
                self.items[item] = self.items.get(item, 0) + 1

            # The above is enough for magic/battle skills, but for traits...
            # we need to know if the effects should be applied.
            c_absolute = item not in self.list # DO NOTHING otherwise.
            total = bool(item in self.normal) + self.items.get(item, 0)
            if c_absolute and total > 0:
                self.list.append(item)
                return True

        def remove(self, item, normal=True):
            # Overwriting default list method.
            # ==> For battle & magic skills:
            if self.be_skill:
                if isinstance(item, basestring):
                    if item in store.battle_skills:
                        item = store.battle_skills[item]
                    else:
                        char_debug("Tried to remove unknown skill %s from %s!" % (item, self.instance.__class__))
                        return
            if normal:
                self.normal.discard(item)
            else:
                self.items[item] = self.items.get(item, 0) - 1

            # The above is enough for magic/battle skills, but for traits...
            # we need to know if the effects should be applied.
            c_absolute = item in self.list # DO NOTHING otherwise.
            total = bool(item in self.normal) + self.items.get(item, 0)
            if c_absolute and total <= 0:
                self.list.remove(item)
                return True


    class Trait(_object):
        def __init__(self):
            self.desc = ''
            self.icon = None
            self.hidden = False
            self.mod = dict() # To be removed!
            self.mod_stats = dict()
            self.mod_skills = dict()
            self.max = dict()
            self.min = dict()
            self.blocks = list()
            self.effects = list()

            # Occupations related:
            self.occupations = list() # GEN_OCCS (Misnamed here)
            self.higher_tiers = list() # Required higher tier basetraits to enable this trait.

            self.sex = "unisex" # Until we set this up in traits: this should be "unisex" by default.

            # Types:
            self.type = "" # Specific type if specified.
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

            # Elemental:
            self.font_color = None
            self.resist = list()
            self.el_name = ""
            self.el_absorbs = dict() # Pure ratio, NOT a modificator to a multiplier like for dicts below.
            self.el_damage = dict()
            self.el_defence = dict()
            self.el_special = dict()

            # Base mods on init:
            self.init_mod = dict() # Mod value setting
            self.init_lvlmax = dict() # Mod value setting
            self.init_max = dict() # Mod value setting
            self.init_skills = dict() # {skill: [actions, training]}

            # Special BE Fields:
            # self.evasion_bonus = () # Bonuses in traits work differently from item bonuses, a tuple of (min_value, max_value, max_value_level) is expected (as a value in dict below) instead!
            # self.ch_multiplier = 0 # Critical hit multi...
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
            if not isinstance(trait, Trait):
                trait = store.traits[trait]
            char = self.instance

            # All the checks required to make sure we can even apply this fucking trait: ======================>>
            if trait.sex not in ["unisex", char.gender]:
                return

            # We cannot allow "Neutral" element to be applied if there is at least one element present already:
            if trait.elemental and trait.id == "Neutral":
                if char.elements:
                    return

            # Blocked traits:
            if trait in self.ab_traits | self.blocked_traits:
                return

            # Unique Traits:
            if trait.personality:
                if list(t for t in self if t.personality):
                    return
                else:
                    char.personality = trait
            if trait.race:
                if list(t for t in self if t.race):
                    return
                else:
                    char.race = trait
            if trait.gents:
                if list(t for t in self if t.gents):
                    return
                else:
                    char.gents = trait
            if trait.body:
                if list(t for t in self if t.body):
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
                for stat in trait.init_lvlmax: # Mod value setting
                    if stat in stats:
                        stats.lvl_max[stat] += trait.init_lvlmax[stat]*multiplier
                    else:
                        msg = "'%s' trait tried to apply unknown init lvl max stat: %s!"
                        char_debug(str(msg % (trait.id, stat)))

                for stat in trait.init_max: # Mod value setting
                    if stat in stats:
                        stats.max[stat] += trait.init_max[stat]*multiplier
                    else:
                        msg = "'%s' trait tried to apply unknown init max stat: %s!"
                        char_debug(str(msg % (trait.id, stat)))

                # for stat in trait.init_mod: # Mod value setting
                #     if stat in stats:
                #         stats.stats[stat] += trait.init_mod[stat] * multiplier
                #     else:
                #         msg = "'%s' trait tried to apply unknown init max stat: %s!"
                #         char_debug(str(msg % (trait.id, stat)))

                # for skill in trait.init_skills: # Mod value setting
                #     if skill in stats.skills:
                #         stats.skills[skill][0] += trait.init_skills[skill][0] * multiplier
                #         stats.skills[skill][1] += trait.init_skills[skill][1] * multiplier
                #     else:
                #         msg = "'%s' trait tried to apply unknown init skillt: %s!"
                #         char_debug(str(msg % (trait.id, skill)))

            # Only for body traits:
            if trait.body:
                if trait.mod_ap:
                    char.baseAP += trait.mod_ap

            for key in trait.max:
                if key in stats.max:
                    stats.max[key] += trait.max[key]
                else:
                    msg = "'%s' trait tried to apply unknown max stat: %s!"
                    char_debug(str(msg % (trait.id, key)))

            for key in trait.min:
                # Preventing traits from messing up minimums of stats by pushing them into negative territory. @Review: No longer required as per new stats code.
                if key in stats.min:
                    stats.min[key] += trait.min[key]
                else:
                    msg = "'%s' trait tried to apply unknown min stat: %s!"
                    char_debug(str(msg % (trait.id, key)))

            for entry in trait.blocks:
                if entry in traits:
                    self.blocked_traits.add(traits[entry])
                else:
                    char_debug(str("Tried to block unknown trait: %s, id: %s, class: %s" % (entry, char.id, char.__class__)))

            # For now just the girls get effects...
            if hasattr(char, "effects"):
                for entry in trait.effects:
                    char.enable_effect(entry)

            if trait.mod_stats:
                temp = trait.mod_stats.get("upkeep", None)
                if temp is not None:
                    char.upkeep += temp[0]
                temp = trait.mod_stats.get("disposition", None)
                if temp is not None:
                    char.mod_stat("disposition", temp[0])
                temp = trait.mod_stats.get("affection", None)
                if temp is not None:
                    char.mod_stat("affection", temp[0])
                char.stats.apply_trait_statsmod(trait, 0, char.level)

            if hasattr(trait, "mod_skills"):
                for key in trait.mod_skills:
                    if key in STATIC_CHAR.SKILLS:
                        sm = stats.skills_multipliers[key] # skillz muplties
                        m = trait.mod_skills[key] # mod
                        sm[0] += m[0]
                        sm[1] += m[1]
                        sm[2] += m[2]
                    else:
                        msg = "'%s' trait tried to apply unknown skill: %s!"
                        char_debug(str(msg % (trait.id, key)))

            # Adding resisting elements and attacks:
            for i in trait.resist:
                char.resist.append(i)

            # NEVER ALLOW NEUTRAL ELEMENT WITH ANOTHER ELEMENT!
            if trait.elemental:
                if trait.id != "Neutral" and traits["Neutral"] in self:
                    self.remove(traits["Neutral"])

            # Finally, make sure stats are working:
            char.stats.normalize_stats()

        def remove(self, trait, truetrait=True):
            """
            Removes trait and removes it's effects gained up to a current level of the characters.
            Truetraits basially means that the trait is not applied throught items (Jobs, GameStart, Events and etc.)
            """
            # If we got a string with a traits name. Let the game throw an error otherwise.
            if not isinstance(trait, Trait):
                trait = store.traits[trait]
            char = self.instance

            if trait.sex not in ["unisex", char.gender]:
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
            for key in trait.max:
                if key in stats.max:
                    stats.max[key] -= trait.max[key]
                else:
                    char_debug(str('Maximum Value: %s for Trait: %s does not exist' % (key, trait.id)))

            for key in trait.min:
                if key in stats.min:
                    # Preventing traits from messing up minimums of stats by pushing them into negative territory. @Review: No longer required as per new stats code.
                    # if(self.stats.min[key] - trait.min[key]) >= 0:
                    stats.min[key] -= trait.min[key]
                else:
                    msg = "'%s' trait tried to apply unknown min stat: %s!"
                    char_debug(str(msg % (trait.id, key)))

            if trait.blocks:
                _traits = set()
                for entry in trait.blocks:
                    if entry in traits:
                        _traits.add(traits[entry])
                    else:
                        char_debug(str("Tried to block unknown trait: %s, id: %s, class: %s" % (entry, char.id, char.__class__)))
                self.blocked_traits -= _traits

            # Ensure that blocks forced by other traits were not removed:
            for entry in self:
                self.blocked_traits = self.blocked_traits.union(entry.blocks)

            # For now just the girls get effects...
            if isinstance(char, Char):
                for entry in trait.effects:
                    self.instance.disable_effect(entry)

            if trait.mod_stats:
                temp = trait.mod_stats.get("upkeep", None)
                if temp is not None:
                    char.upkeep -= temp[0]
                temp = trait.mod_stats.get("disposition", None)
                if temp is not None:
                    char.mod_stat("disposition", -temp[0])
                temp = trait.mod_stats.get("affection", None)
                if temp is not None:
                    char.mod_stat("affection", -temp[0])
                char.stats.apply_trait_statsmod(trait, char.level, 0)

            if hasattr(trait, "mod_skills"):
                for key in trait.mod_skills:
                    if key in STATIC_CHAR.SKILLS:
                        sm = stats.skills_multipliers[key] # skillz muplties
                        m = trait.mod_skills[key] # mod
                        sm[0] -= m[0]
                        sm[1] -= m[1]
                        sm[2] -= m[2]
                    else:
                        msg = "'%s' trait tried to apply unknown skill: %s!"
                        char_debug(str(msg % (trait.id, key)))

            # Remove resisting elements and attacks:
            for i in trait.resist:
                self.instance.resist.remove(i)

            # We add the Neutral element if there are no elements left at all...
            if not self.instance.elements:
                self.apply("Neutral")

            # Finally, make sure stats are working:
            char.stats.normalize_stats()


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

            days = []
            for d in all_income_data:
                if all_income_data[d] or all_expense_data[d]:
                    days.append(d)
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
            if day and day >= store.day:
                raise Exception("Day on income retrieval must be lower than the current day!")

            if not day:
                d = self.todays_logical_income_log
            else:
                d = self.game_logical_income_log[day]

            if kind == "all":
                return sum(val for val in d.values())
            elif kind in d:
                return d[kind]
            else:
                raise Exception("Income kind: {} is not valid!".format(kind))

        def get_game_total(self):
            # Total income over the game (Used in ND screen)...
            # Used MAIN dicts
            days, all_income_data, all_expense_data = self.get_data_for_fin_screen("main")
            income = sum(all_income_data.get("All", {}).values())
            expense = sum(all_expense_data.get("All", {}).values())

            total = income - expense
            return income, expense, total

        # Tax related:
        def get_income_tax(self, days=7, log_finances=False):
            # MC's Income Tax
            char = self.instance
            ec = store.pytfall.economy
            tax = 0
            income = 0
            taxable_buildings = [i for i in char.buildings if hasattr(i, "fin")]

            for b in taxable_buildings:
                fin_log = b.fin.game_logical_income_log
                for _day in fin_log:
                    if _day > store.day - days:
                        income += sum(fin_log[_day].values())

            if income > 5000:
                for delimiter, mod in ec.income_tax:
                    if income <= delimiter:
                        tax = round_int(income*mod)
                        break

            if log_finances and tax:
                # We have no choice but to do the whole routine again :(
                # Final value may be off but +/- 1 gold due to rounding
                # in this simplified code. I may perfect this one day...
                for b in taxable_buildings:
                    fin_log = b.fin.game_logical_income_log
                    for _day in fin_log:
                        if _day > store.day - days:
                            _income = sum(fin_log[_day].values())
                            _tax = round_int(_income*mod)
                            b.fin.log_logical_expense(_tax, "Income Tax")
            return income, tax

        def get_property_tax(self, log_finances=False):
            char = self.instance
            ec = store.pytfall.economy
            properties = char.buildings

            slaves = [c for c in char.chars if c.status == "slave"]
            b_tax = round_int(sum([p.price for p in properties])*ec.property_tax["real_estate"])
            s_tax = round_int(sum([s.fin.get_price() for s in slaves])*ec.property_tax["slaves"])

            if log_finances:
                for p in properties:
                    _tax = round_int(p.price*ec.property_tax["real_estate"])
                    if hasattr(p, "fin"): # Simpler location do not have fin module
                        p.fin.log_logical_expense(_tax, "Property Tax")
                for s in slaves:
                    _tax = round_int(s.fin.get_price()*ec.property_tax["slaves"])
                    s.fin.log_logical_expense(_tax, "Property Tax")

            tax = b_tax + s_tax
            return b_tax, s_tax, tax

        def get_total_taxes(self, days=7):
            return self.get_income_tax(days) + self.get_property_tax

        # Rest ================================>>>
        def settle_wage(self, txt, mood):
            """
            Settle wages between player and chars.
            Called during next day method per each individual girl.
            """
            char = self.instance

            real_wagemod = char.wagemod
            got_paid = False

            if char.status == "slave":
                temp = choice(["Being a slave, %s doesn't expect to get paid." % char.p,
                               "Slaves don't get paid."])
                paid_wage = round_int(char.expected_wage/100.0*real_wagemod) if real_wagemod else 0
                if paid_wage == 0:
                    txt.append(temp)
                    return mood
                temp += " And yet... you chose to pay %s %d%% of the fair wage (%d Gold)!" % (char.op, real_wagemod, paid_wage)
                txt.append(temp)
            else: # Free girls:
                expected_wage = char.expected_wage
                temp = choice(["%s expects to be compensated for %s services ({color=[gold]}%d Gold{/color})." % (char.pC, char.pp, expected_wage),
                               "%s expects to be paid a wage of {color=[gold]}%d Gold{/color}." % (char.pC, expected_wage)])
                paid_wage = round_int(expected_wage/100.0*real_wagemod)
                temp += " You chose to pay %s %d%% of that! ({color=[gold]}%d Gold{/color})" % (char.pp, real_wagemod, paid_wage)
                txt.append(temp)

            if not paid_wage: # Free girl with 0% wage mod
                txt.append("You paid %s nothing..." % char.op)
            elif hero.take_money(paid_wage, reason="Wages"):
                self.add_money(paid_wage, reason="Wages")
                self.log_logical_expense(paid_wage, "Wages")
                if isinstance(char.workplace, Building):
                    char.workplace.fin.log_logical_expense(paid_wage, "Wages")
                got_paid = True
            else:
                txt.append("You lacked the funds to pay %s the promised wage." % char.pp)
                if char.status == "slave":
                    temp += " But being a slave %s will not hold that against you." % char.nickname
                    return mood

            # So... if we got this far, we're either talking slaves that player
            # chose to pay a wage or free girls who expect that.
            if char.status == "free":
                if got_paid:
                    diff = real_wagemod - 100 # We expected 100% of the wage at least.
                else:
                    diff = -100 # Failing to pay anything at all... huge penalty
                dismod = .09
                joymod = .06
                if diff > 0:
                    mood = "happy"
                    dismod = max(1, round_int(diff*dismod))
                    joymod = max(1, round_int(diff*joymod))
                    if DEBUG:
                        txt.append("Debug: Disposition mod: {}".format(dismod))
                        txt.append("Debug: Joy mod: {}".format(joymod))
                    char.mod_stat("disposition", dismod)
                    char.mod_stat("joy", joymod)
                elif diff < 0:
                    mood = "angry"
                    dismod = min(-2, round_int(diff*dismod)) * (char.tier or 1)
                    joymod = min(-1, round_int(diff*joymod)) * (char.tier or 1)
                    if DEBUG:
                        txt.append("Debug: Disposition mod: {}".format(dismod))
                        txt.append("Debug: Joy mod: {}".format(joymod))
                    char.mod_stat("disposition", dismod)
                    char.mod_stat("joy", joymod)
                else: # Paying a fair wage
                    if dice(10): # just a small way to appreciate that:
                        char.mod_stat("disposition", 1)
                        char.mod_stat("joy", 1)
            else: # Slave case:
                mood = "happy"
                diff = real_wagemod # Slaves just get the raw value.
                dismod = .1
                joymod = .1
                dismod = max(1, round_int(diff*dismod))
                joymod = max(1, round_int(diff*joymod))
                if DEBUG:
                    txt.append("Debug: Disposition mod: {}".format(dismod))
                    txt.append("Debug: Joy mod: {}".format(joymod))
                char.mod_stat("disposition", dismod)
                char.mod_stat("joy", joymod)

            return mood

        def get_price(self):
            char = self.instance

            price = 1000 + char.tier*1000 + char.level*100

            if char.status == 'free':
                price *= 2 # in case if we'll even need that for free ones, 2 times more

            return price

        def get_upkeep(self):
            return self.stored_upkeep

        def calc_upkeep(self):
            char = self.instance
            upkeep = char.upkeep

            if char.status == 'slave':
                upkeep += STATIC_CHAR.BASE_UPKEEP * char.tier or 1
                upkeep *= uniform(.9, 1.1)
                if "Dedicated" in char.traits:
                    upkeep *= .5

                upkeep = max(upkeep, 1)
            self.stored_upkeep = round_int(upkeep)

        def next_day(self):
            # We log total to -1 key...
            cut_off_day = store.day - 10

            self.game_main_income_log[store.day] = self.todays_main_income_log.copy()
            self.game_main_expense_log[store.day] = self.todays_main_expense_log.copy()
            self.game_logical_income_log[store.day] = self.todays_logical_income_log.copy()
            self.game_logical_expense_log[store.day] = self.todays_logical_expense_log.copy()

            for log in [self.game_main_income_log, self.game_main_expense_log,
                        self.game_logical_income_log, self.game_logical_expense_log]:
                for day, info in log.items():
                    if 0 < day < cut_off_day:
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
        def __init__(self, *args, **kwargs):
            """
            instance = reference to Character object
            Expects a dict with statname as key and a list of:
            [stat, min, max, lvl_max] as value.
            Added skills to this class... (Maybe move to a separate class if they get complex?).
            DevNote: Training skills have a capital letter in them, action skills do not.
                This should be done thought the class of the character and NEVER using self.mod_skill directly!
            """
            self.instance = args[0]
            self.stats, self.imod, self.min, self.max, self.lvl_max = dict(), dict(), dict(), dict(), dict()

            # Load the stat values:
            for stat, values in kwargs.get("stats", {}).iteritems():
                self.stats[stat] = values[0]
                self.imod[stat] = 0
                self.min[stat] = values[1]
                self.max[stat] = values[2]
                self.lvl_max[stat] = values[3]

            # [action_value, training_value]
            self.skills = dict()
            for s in STATIC_CHAR.SKILLS:
                self.skills[s] = list([0, 0])
            # {k: [0, 0] for k in STATIC_CHAR.SKILLS}
            # [actions_multi, training_multi, value_multi]
            # self.skills_multipliers = {k: [1, 1, 1] for k in self.skills}
            self.skills_multipliers = dict()
            for s in self.skills:
                self.skills_multipliers[s] = list([1, 1, 1])

            # Leveling system assets:
            self.goal = 1000
            self.goal_increase = 1000
            self.level = 0
            self.exp = 0

            # Statslog:
            self.log = dict()

        def get_base_stats(self):
            return set(s for t in self.instance.traits.basetraits for s in t.base_stats)

        def get_base_skills(self):
            return set(s for t in self.instance.traits.basetraits for s in t.base_skills)

        def get_base_ss(self):
            return self.get_base_stats().union(self.get_base_skills())

        def _action_skill(self, key):
            """Raw Skills:
            [action_value, training_value]
            """
            return self.skills[key][0]

        def _get_stat(self, key):
            maxval = self.get_max(key)
            minval = self.min[key]
            val = self.stats[key] + self.imod[key]

            # Normalization:
            if val > maxval:
                val = maxval
            elif val < minval:
                val = minval

            return val

        def get_skill(self, skill):
            """
            Returns adjusted skill.
            'Action' skill points become less useful as they exceed training points * 3.
            """
            action = self.skills[skill][0]
            training = self.skills[skill][1]

            training_range = training * 3
            beyond_training = action - training_range

            if beyond_training >= 0:
                training += training_range + beyond_training / 3.0
            else:
                training += action
            return training * max(min(self.skills_multipliers[skill][2], 2.5), .5)

        def normalize_stats(self, stats=None):
            # Makes sure main stats dict is properly aligned to max/min values

            if not stats:
                stats = self.stats

            for stat in stats:
                val = self.stats[stat]
                minval = self.min[stat]
                maxval = self.get_max(stat)
                if val > maxval:
                    self.stats[stat] = maxval
                if val < minval:
                    self.stats[stat] = minval

        def __getitem__(self, key):
            return self._get_stat(key)

        def __iter__(self):
            return iter(self.stats)

        def get_max(self, key):
            return min(self.max[key], self.lvl_max[key])

        def mod_exp(self, value):
            # Assumes input from setattr of self.instance:
            char = self.instance

            value += self.exp
            self.exp = value

            if self.exp >= self.goal:
                num_lvl = (self.exp - self.goal)/self.goal_increase + 1
                self.goal += num_lvl * self.goal_increase

                # Normal Max stat Bonuses:
                for stat in self.stats:
                    if stat not in STATIC_CHAR.FIXED_MAX:
                        self.lvl_max[stat] += 5 * num_lvl
                        self.max[stat] += 2 * num_lvl

                        # Chance to increase max stats permanently based on level
                        chance = (2*self.level + num_lvl)*num_lvl/ 40.0
                        value = min(random.expovariate(100.0/chance), num_lvl)
                        val = int(value)
                        if val != 0:
                            self.lvl_max[stat] += val
                            self.max[stat] += val
                            value -= val
                        value *= 100
                        if dice(value):
                            self.lvl_max[stat] += 1
                        if dice(value):
                            self.max[stat] += 1

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
                    for stat in trait.leveling_stats:
                        if stat not in STATIC_CHAR.FIXED_MAX and stat in self.stats:
                            self.lvl_max[stat] += trait.leveling_stats[stat][0] * multiplier
                            self.max[stat] += trait.leveling_stats[stat][1] * multiplier
                        else:
                            msg = "Trait %s tried to raise unknown stat %s on leveling up (max mods) to %s!"
                            char_debug(str(msg % (trait.id, stat, char.__class__)))

                    # Super Skill Bonuses:
                    for skill in trait.init_skills:
                        if is_skill(skill):
                            self.mod_full_skill(skill, 20*num_lvl)
                        else:
                            msg = "Trait %s tried to raise unknown skill %s on leveling up to %s!"
                            char_debug(str(msg % (trait.id, skill, char.__class__)))

                self.level += num_lvl

                # Bonuses from traits:
                for trait in char.traits:
                    self.apply_trait_statsmod(trait, self.level-num_lvl, self.level)

                self.stats["health"] = self.get_max("health")
                self.stats["mp"] = self.get_max("mp")
                self.stats["vitality"] = self.get_max("vitality")

                self.instance.update_tier_info()

        def apply_trait_statsmod(self, trait, from_lvl, to_lvl):
            """Applies "stats_mod" field on characters.
               A mod_stats entry is a pair of integers (x, y), which means the character
               gains x points every y level.
            """
            delta_lvl = to_lvl - from_lvl
            temp = ["disposition", "affection", "upkeep"]
            for key in trait.mod_stats:
                if key in temp:
                    continue
                mod = trait.mod_stats[key][1]
                delta = delta_lvl / mod
                rem = delta_lvl % mod
                if rem != 0:
                    rem = (to_lvl / mod) - ((to_lvl - rem) / mod)
                    if rem > 0:
                        delta += 1
                    elif rem < 0:
                        delta -= 1
                if delta != 0:
                    self._mod_base_stat(key, delta * trait.mod_stats[key][0])

        def _mod_base_stat(self, key, value):
            # Modifies the first layer of stats (self.stats)
            # As different character types may come with different stats.
            curr_value = self.stats[key]
            value += curr_value

            if value <= 0 and key == 'health':
                value = 1 # use kill_char if you want to remove a char from the game
                #char = self.instance
                #if isinstance(char, Player):
                #    jump("game_over")
                #elif isinstance(char, Char):
                #    kill_char(char)
                #    return

            maxval = self.get_max(key)
            minval = self.min[key]

            if value >= maxval:
                value = maxval
            elif value <= minval:
                value = minval
            self.stats[key] = value
            return value - curr_value # return the real delta

        def _mod_raw_skill(self, key, at, value):
            """Modifies a skill.

            key: the skill to be modified (must be lower case)
            at: 0 - Action Skill
                1 - Training (knowledge part) skill...
            value: the value to be added
            """

            curr_value = self.get_skill(key)
            skill_max = SKILLS_MAX[key]
            if curr_value >= skill_max:
                return 0 # Maxed out...

            value *= max(.5, min(self.skills_multipliers[key][at], 2.5))

            threshold = SKILLS_THRESHOLD[key]
            beyond_training = curr_value - threshold

            if beyond_training > 0: # insufficient training... lessened increase beyond
                at_zero = skill_max - threshold
                value *= max(.1, 1 - float(beyond_training)/at_zero)

            curr_value = self.skills[key][at]
            value += curr_value
            self.skills[key][at] = value
            return round_int(value)-round_int(curr_value) # return the real delta

        def mod_full_skill(self, skill, value):
            """This spreads the skill bonus over both action and training.
            """
            self._mod_raw_skill(skill, 0, value*(2/3.0))
            self._mod_raw_skill(skill, 1, value*(1/3.0))

        def eval_inventory(self, inventory, weighted, target_stats, target_skills,
                           exclude_on_skills, exclude_on_stats,
                           base_purpose, sub_purpose, limit_tier=False,
                           chance_func=None, min_value=-5,
                           upto_skill_limit=False,
                           check_money=False,
                           smart_ownership_limit=True):
            """
            weigh items in inventory based on stats.

            weighted: weights per item will be added to this
            inventory: the inventory to evaluate items from
            target_stats: a list of stats to consider for items
            target_skills: similarly, a list of skills
            exclude_on_stats: items will be excluded if stats in this list are negatively affected
            exclude_on_skills: similarly, a list of skills
            chance_func(): function that takes the item and returns a chance, between 0 and 100
            min_value: at what (negative) value the weight will become zero
            upto_skill_limit: whether or not to calculate bonus beyond training exactly

            # Auto-buy related.
            check_money: check is char has enough cash to buy the items.
            """

            # call the functions for these only once
            char = self.instance
            _stats_curr = {}
            _stats_max = {}
            skills = {s: self.get_skill(s) for s in target_skills}
            for stat in target_stats:
                _stats_curr[stat] = self._get_stat(stat) # current stat value
                _stats_max[stat] = self.get_max(stat)   # current stat max

            # Add basetraits and occupations to basepurposes:
            base_purpose.update(bt.id for bt in char.traits.basetraits)
            base_purpose.update(str(t) for t in char.occupations)
            base_purpose.add("Any")

            # per item the nr of weighting criteria may vary. At the end all of them are averaged.
            # if an item has less than the most weights the remaining are imputed with 50 weights
            # Nor sure why????
            # most_weights = {slot: 0 for slot in weighted}

            for item in inventory:
                slot = item.slot
                if smart_ownership_limit is True:
                    owned = count_owned_items(char, item)
                    if slot == "ring":
                        if owned >= 3:
                            continue
                    elif slot == "consumable":
                        if owned >= 5:
                            continue
                    elif owned >= 1:
                        continue
                    elif slot == "misc" and item in char.miscblock:
                        continue

                if slot not in weighted:
                    aeq_debug("Ignoring item %s on slot", item.id)
                    continue

                if limit_tier is not False and item.tier > limit_tier:
                    aeq_debug("Ignoring item %s on tier.", item.id)
                    continue

                # Gender:
                if item.sex not in (char.gender, "unisex"):
                    aeq_debug("Ignoring item %s on gender.", item.id)
                    continue

                # Money (conditioned):
                if check_money is True:
                    if char.gold < item.price:
                        aeq_debug("Ignoring item %s on money.", item.id)
                        continue

                #if "Slave" in base_purpose and "Slave" in item.pref_class:
                #    weights = [200] # As all slave items are shit anyway...
                #else:
                weights = chance_func(item) if chance_func else [item.eqchance]
                if weights is None: # We move to the next item!
                    aeq_debug("Ignoring item %s on weights.", item.id)
                    continue

                # Handle purposes:
                if not base_purpose.isdisjoint(item.pref_class):
                    weights.append(200)
                elif not sub_purpose.isdisjoint(item.pref_class):
                    weights.append(125)
                else: # 'Any'
                    # If no purpose is valid for the item, we want nothing to do with it.
                    if slot not in ("misc", "consumable"):
                        aeq_debug("Ignoring item %s on purpose.", item.id)
                        continue
                    weights.append(55)

                # Stats:
                for stat, value in item.mod.iteritems():
                    if stat in exclude_on_stats and value < min_value:
                        weights.append(-100 + value*10)
                        continue

                    if stat in _stats_curr:
                        # a new max may have to be considered
                        new_max = min(self.max[stat] + item.max[stat], self.lvl_max[stat]) if stat in item.max else _stats_max[stat]
                        if not new_max:
                            continue # Some weird exception?

                        # Get the resulting value:
                        new_stat = max(min(self.stats[stat] + self.imod[stat] + value, new_max), self.min[stat])

                        curr_stat = _stats_curr[stat]
                        if curr_stat == new_stat:
                            # the item could help, but not now
                            if value > 0:
                                weights.append(min(25, value*5))
                        elif curr_stat < new_stat:
                            # add the fraction increase/decrease
                            temp = 100*(new_stat - curr_stat)/new_max
                            weights.append(50 + temp)
                        else: # Item lowers the stat for the character
                            if stat not in exclude_on_stats:
                                change = curr_stat - new_stat
                                # proceed if it does not take off more than 20% of our stat...
                                if change <= curr_stat/5:
                                    continue
                            # We want nothing to do with this item.
                            weights = None
                            break

                if weights is None:
                    continue # Loop did not finish -> skip

                # Max Stats:
                for stat, value in item.max.iteritems():
                    if stat in exclude_on_stats and value < 0:
                        weights.append(-50 + value*5)
                        continue

                    if stat in _stats_max:
                        new_max = min(self.max[stat] + value, self.lvl_max[stat])
                        curr_max = _stats_max[stat]
                        if new_max == curr_max:
                            continue
                        elif new_max > curr_max:
                            weights.append(50 + min(new_max-curr_max, 50))
                        else: # Item lowers max of this stat for the character:
                            if True: #if stat not in exclude_on_stats:
                                change = curr_max-new_max
                                # proceed if it does not take off more than 20% of our stat...
                                if change <= curr_max/5:
                                    continue
                            # We want nothing to do with this item.
                            weights = None
                            break

                if weights is None:
                    continue # Loop did not finish -> skip
 
                # Skills:
                for skill, effect in item.mod_skills.iteritems():
                    temp = sum(effect)
                    if skill in exclude_on_skills and temp < 0:
                        weights.append(-100)
                        continue

                    if skill in skills:
                        value = skills[skill]
                        skill_remaining = SKILLS_MAX[skill] - value
                        if skill_remaining > 0:
                            # calculate skill with mods applied, as in apply_item_effects() and get_skill()
                            mod_action = self.skills[skill][0] + effect[3]
                            mod_training = self.skills[skill][1] + effect[4]
                            mod_skill_multiplier = self.skills_multipliers[skill][2] + effect[2]

                            if upto_skill_limit: # more precise calculation of skill limits
                                training_range = mod_training * 3
                                beyond_training = mod_action - training_range
                                if beyond_training >= 0:
                                    mod_training += training_range - mod_action + beyond_training/3.0

                            mod_training += mod_action
                            new_skill = mod_training*max(min(mod_skill_multiplier, 2.5), .5)
                            if new_skill < min_value:
                                weights.append(-111)
                                continue

                            saturated_skill = max(value + 100, new_skill)
                            mod_val = 50 + 100*(new_skill - value) / saturated_skill
                            if mod_val > 100 or mod_val < -100:
                                aeq_debug("Unusual mod value for skill %s: %s", skill, mod_val)
                            weights.append(mod_val)

                weighted[slot].append([weights, item])


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
        def pp(self):
            # Possessive pronoun (his, her, its):
            # This may 'gramatically' incorrect, cause things (it) cannot possess/own anything but knowing PyTFall :D
            if self.gender == "female":
                return "her"
            elif self.gender == "male":
                return "his"
            else:
                return "its"

        @property
        def ppC(self):
            # Possessive pronoun (his, hers, its) capitalized::
            return self.pp.capitalize()

        @property
        def hs(self):
            if self.gender == "female":
                return "sister"
            else:
                return "brother"

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

            if ss_mod is None:
                self.ss_mod = {} # Stats/Skills mod!
            else:
                self.ss_mod = ss_mod

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

            if self.name == "Poisoned":
                self.ss_mod["health"] -= self.duration*5
                char.mod_stat("health", self.ss_mod["health"])
                if self.days_active >= self.duration:
                    self.end(char)
            elif self.name == "Unstable":
                if self.days_active == self.duration:
                    char.mod_stat("joy", self.ss_mod["joy"])
                    self.duration += randint(2, 4)
                    self.ss_mod['joy'] = randint(20, 30) if randrange(2) else -randint(20, 30)
            elif self.name == "Optimist":
                if char.get_stat("joy") >= 30:
                    char.mod_stat("joy", 1)
            elif self.name == "Blood Connection":
                char.mod_stat("disposition", 2)
                char.mod_stat("character", -1)
            elif self.name == "Regeneration":
                h = 30
                if "Summer Eternality" in char.traits:
                    h += char.get_max("health")/2
                char.mod_stat("health", max(1, h))
            elif self.name == "MP Regeneration":
                h = 30
                if "Winter Eternality" in char.traits:
                    h += char.get_max("mp")/2
                char.mod_stat("mp", max(1, h))
            elif self.name == "Small Regeneration":
                char.mod_stat("health", 15)
            elif self.name == "Depression":
                if char.get_stat("joy") >= 30:
                    self.end(char)
            elif self.name == "Elation":
                if char.get_stat("joy") < 95:
                    self.end(char)
            elif self.name == "Pessimist":
                if char.get_stat("joy") > 80:
                    char.mod_stat("joy", -2)
                elif char.get_stat("joy") > 10 and dice(60):
                    char.mod_stat("joy", -1)
            elif self.name == "Assertive":
                if char.get_stat("character") < char.get_max("character")/2:
                    char.mod_stat("character", 2)
            elif self.name == "Diffident":
                if char.get_stat("character") > char.get_max("character")/2:
                    char.mod_stat("character", -2)
            elif self.name == "Composure":
                if char.get_stat("joy") < 50:
                    char.mod_stat("joy", 1)
                elif char.get_stat("joy") > 70:
                    char.mod_stat("joy", -1)
            elif self.name == "Vigorous":
                if char.get_stat("vitality") < char.get_max("vitality")/4:
                    char.mod_stat("vitality", randint(2, 3))
                elif char.get_stat("vitality") < char.get_max("vitality")/2:
                    char.mod_stat("vitality", randint(1, 2))
            elif self.name == "Down with Cold":
                char.mod_stat("health", self.ss_mod["health"])
                char.mod_stat("vitality", self.ss_mod['vitality'])
                char.mod_stat("joy", self.ss_mod['joy'])
                if self.days_active >= self.duration:
                    self.end(char)
            elif self.name == "Kleptomaniac":
                if dice(char.get_stat("luck")+55):
                    char.add_money(randint(5, 25), reason="Kleptomania")
            elif self.name == "Injured":
                if char.get_stat("health") > char.get_max("health")/5:
                    char.set_stat("health", char.get_max("health")/5)
                if char.get_stat("vitality") > char.get_max("vitality")/2:
                    char.set_stat("vitality", char.get_max("vitality")/2)
                char.mod_stat("joy", -10)
            elif self.name == "Exhausted":
                char.mod_stat("vitality", -char.get_max("vitality")/5)
            elif self.name == "Lactation": # TODO add milking activities, to use this fetish more widely
                if char.get_stat("health") >= 30 and char.get_stat("vitality") >= 30 and char in hero.chars and char.is_available:
                    if char.status == "slave" or check_lovers(char, hero):
                        if "Small Boobs" in char.traits:
                            if "Slime" in char.traits:
                                hero.add_item("Slime's Milk")
                            else:
                                hero.add_item("Bottle of Milk")
                        elif "Average Boobs" in char.traits:
                            if "Slime" in char.traits:
                                hero.add_item("Slime's Milk", randint(1, 2))
                            else:
                                hero.add_item("Bottle of Milk", randint(1, 2))
                        elif "Big Boobs" in char.traits:
                            if "Slime" in char.traits:
                                hero.add_item("Slime's Milk", randint(2, 3))
                            else:
                                hero.add_item("Bottle of Milk", randint(2, 3))
                        else:
                            if "Slime" in char.traits:
                                hero.add_item("Slime's Milk", randint(2, 5))
                            else:
                                hero.add_item("Bottle of Milk", randint(2, 5))
                    else:
                        if "Slime" in char.traits:
                            if not(has_items("Slime's Milk", [char])):
                                char.add_item("Slime's Milk")
                        else:
                            if not(has_items("Bottle of Milk", [char])): # in order to not stack bottles of milk into free chars inventories they get only one, and only if they had 0
                                char.add_item("Bottle of Milk")
            elif self.name == "Silly":
                if char.get_stat("intelligence") >= 200:
                    char.mod_stat("intelligence", -20)
                elif char.get_stat("intelligence") >= 100:
                    char.mod_stat("intelligence", -10)
                elif char.get_stat("intelligence") >= 25:
                    char.mod_stat("intelligence", -5)
                else:
                    char.set_stat("intelligence", 20)
            elif self.name == "Intelligent":
                if char.get_stat("joy") >= 75 and char.get_stat("vitality") >= char.get_max("vitality")*.75 and char.get_stat("health") >= char.get_max("health")*.75:
                    char.mod_stat("intelligence", 1)
            elif self.name == "Sibling":
                if char.get_stat("disposition") < 100:
                    char.mod_stat("disposition", 2)
                elif char.get_stat("disposition") < 200:
                    char.mod_stat("disposition", 1)
            elif self.name == "Drunk":
                char.mod_stat("vitality", -char.get_flag("dnd_drunk_counter", 0))
                char.mod_stat("health", -10)
                char.mod_stat("joy", -5)
                char.mod_stat("mp", -20)
                self.end(char)
            elif self.name == "Food Poisoning":
                char.mod_stat("health", self.ss_mod["health"])
                char.mod_stat("vitality", self.ss_mod['vitality'])
                char.mod_stat("joy", self.ss_mod['joy'])
                if self.days_active >= self.duration:
                    self.end(char)

        def end(self, char):
            if self.name in char.effects:
                del(char.effects[self.name])

                # Reset counters to be safe, usually done elsewhere...
                if self.name == "Exhausted":
                    char.del_flag("exhausted_counter")
                elif self.name == "Drunk":
                    char.del_flag("dnd_drunk_counter")
                elif self.name == "Food Poisoning":
                    char.del_flag("dnd_food_poison_counter")
                elif self.name == "Depression":
                    char.del_flag("depression_counter")
                elif self.name == "Elation":
                    char.del_flag("elation_counter")

        def enable(self, char):
            # Prevent same effect from being enable twice (and handle exceptions)
            if self.name in char.effects:
                return
            else:
                char.effects[self.name] = self
