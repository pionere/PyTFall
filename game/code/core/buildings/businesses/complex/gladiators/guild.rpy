init -6 python: # Guild, Tracker and Log.
    # ======================= (Simulated) Arena code =====================>>>
    class GladiatorsLog(_object):
        """Stores resulting text and data for the gladiator-events. TODO merge with ExplorationLog? Does this even have to be a class?
        """
        def __init__(self, time, combat_log):
            self.day = time              # the day of the event
            self.combat_log = combat_log # the log of the battle

    class GladiatorsEvent(_object):
        def __init__(self, team, opponent, type, day=None):
            self.team = team
            self.opponent = opponent # team or mob(dict)
            self.type = type         # "matchfight", "dogfight", "chainfight", "inhouse"
            self.day = day           # optional, only for Match fight?
            self.repeat = False      # optional, only for "chainfight" and "inhouse" fights True/False
            self.result = None

        def guild_chars(self):
            o = self.opponent
            if isinstance(o, Team) and o and o[0].employer is hero:
                return chain(self.team, o)
            else:
                return self.team

        def enemy_name(self):
            enemy = self.opponent
            return enemy["id"] if self.type == "chainfight" else enemy.gui_name

    class GladiatorsGuild(TaskBusiness):

        def __init__(self):
            super(GladiatorsGuild, self).__init__()

            # Global Values that have effects on the whole business.
            self.teams = list() # List to hold all the teams formed in this guild.
            self.events = list() # List to hold all (active) events.
            self.match_logs = OrderedDict([ # map to hold the battle results
                                ("matchfight", collections.deque(maxlen=200)),
                                ("dogfight", collections.deque(maxlen=200)),
                                ("chainfight", collections.deque(maxlen=200)),
                                ("inhouse", collections.deque(maxlen=200))])

            self.teams.append(Team(name="Spartacea")) # sample team

            # gui
            self.view_mode = "team"   # the selected tab
            #  team screen
            self.selected_team = None # 
            #self.workers initialized later
            #self.guild_teams initialized later
            #  arena screen
            self.combat_type = None
            #  log screen 
            self.selected_log_type = None
            #self.selected_log_entry initialized later

            # ND
            self.reset_nd_fields() 

        def reset_nd_fields(self):
            self.logs = list() # List of all log object we create during the day and ND.
            self.nd_team = set() # set of chars active in the guild 
            self.flag_red = False
            #self.flag_green = False
            self.earned = 0
            self.team_charmod = dict()
            
        def can_close(self):
            return any((e.type == "matchfight" and e.result is None for e in self.events))

        def idle_teams(self):
            active_teams = [t for t in chain(*[(e.team, e.opponent) for e in self.events if e.result is None or e.repeat is True])]
            return [t for t in self.teams if t not in active_teams]

        def load_gui(self):
            # Looks pretty ugly... this might be worth improving upon just for the sake of esthetics.
            _teams = self.teams
            _chars = [w for w in self.building.all_workers if w != hero and ExplorationTask.willing_work(w) and w.is_available]

            # filter chars
            idle_chars = list(chain.from_iterable(t.members for t in _teams))
            _chars = [w for w in _chars if w not in idle_chars]

            # filter teams
            _teams = self.idle_teams()

            # load gui elements
            workers = CharsSortingForGui(_chars, page_size=18)
            workers.occ_filters.add("Combatant")
            workers.filter()
            self.workers = workers

            self.guild_teams = PagerGui(_teams, page_size=9)
            self.gui_events = PagerGui(self.events[:], page_size=8)

            self.selected_log_entry = None

        def clear_gui(self):
            """Clear GUI-object to free memory and eliminate dead references
                @TODO merge with EG.clear_gui?
            """
            self.workers = None
            self.guild_teams = None
            self.gui_events = None

        def update_teams(self):
            gt = self.guild_teams
            gt.pager_content = self.idle_teams()
            gt.page = min(gt.page, gt.max_page())

        def update_fighters(self, chars, new_event):
            """
            Update gladiators (chars) in case a new event is added, or an event is removed
            :param chars: the affected gladiators
            :param new_fighters: set to True if a new event was created 
            """
            if new_event:
                msg = None
                for f in chars:
                    if not f.is_available:
                        if msg is None:
                            msg = "%s is currently unavailable!" % f.name
                        else:
                            msg = "Some of the team members are currently unavailable!"
                        continue
                    f.set_task(GladiatorTask)
                if msg is not None:
                    PyTGFX.message(msg) # continue anyway, this is just a warning for the moment
            else:
                # remove task if there are no other matches for the fighters
                fighters = [f for e in self.events if e.result is None or e.repeat is True for f in e.guild_chars()]

                for f in chars:
                    if f not in fighters and f.task == GladiatorTask:
                        f.set_task(None)

        @staticmethod
        def battle_ready(char):
            """
            Return whether the character is available in the guild.
            """
            return char.employer == hero and char.is_available

        # Teams control/sorting/grouping methods:
        def new_team(self, name):
            t = Team(name=name)
            self.add_team(t)
            self.guild_teams.pager_content.append(t)

        def add_team(self, t):
            self.teams.append(t)

        def remove_team(self, t):
            self.teams.remove(t)
            self.guild_teams.pager_content.remove(t)

        def teams_to_fight(self):
            # Returns a list of teams that can be launched on an exploration run.
            # Must have at least one member and NOT already running exploration!
            return [t for t in self.teams if t and all((self.battle_ready(f) for f in t))]

        # Match-Scheduling
        def filter(self):
            events = self.events
            type = self.combat_type
            if type is None:
                events = events[:]
            else:
                events = [e for e in events if e.type == type]
            ge = self.gui_events
            ge.pager_content = events
            ge.page = min(ge.page, ge.max_page())

        def schedule(self):
            if len(self.events) >= self.capacity:
                return PyTGFX.message("The guild can not manage more events at the moment. Try to raise its capacity!")

            team = self.selected_team
            type = self.combat_type

            fday = None
            if type == "chainfight":
                result = renpy.call_screen("arena_mobs", use_return=True)
                if not result:
                    return
                result = result[2]

                if not pytfall.arena.check_arena_fight(type, team, None):
                    return

            elif type == "matchfight":
                # check arena_permit of the team members:
                for f in team:
                    if f.arena_permit:
                        continue
                    if f.arena_rep < Arena.PERMIT_REP:
                        return PyTGFX.message("%s does not have enough arena reputation to buy an arena permit which is required to participate in matches!" % f.name)
                for f in team:
                    if not f.arena_permit:
                        temp = "{color=gold}%s Gold{/color}" % ("{:,d}".format(Arena.PERMIT_PRICE).replace(",", " "))
                        if renpy.call_screen("yesno_prompt",
                                         message="%s does not have an arena permit yet. Would you like to buy one for %s?" % (f.name, temp),
                                         yes_action=Return(True), no_action=Return(False)):
                            if hero.take_money(Arena.PERMIT_PRICE, reason="Arena Permit"):
                                f.arena_permit = True
                                continue
                            PyTGFX.message("You do not have %s to buy the arena permit!" % temp)
                        return

                result = renpy.call_screen("arena_matches", type="%dv%d"%(len(team), len(team)), use_return=True)
                if not result:
                    return
                result = result[2]

                if not pytfall.arena.check_arena_fight(type, team, result[1]):
                    return

                # register the team
                result[0] = team
                fday = result[2]
                for f in team:
                    f.fighting_days.append(fday)

                result = result[1]

            elif type == "dogfight":
                container = getattr(pytfall.arena, "dogfights_{val}v{val}".format(val=len(team)))
                result = renpy.call_screen("arena_dogfights", container=container, use_return=True)
                if not result:
                    return

                result = result[2]

                if not pytfall.arena.check_arena_fight(type, team, result):
                    return

            elif type == "inhouse":
                container = [t for t in self.teams_to_fight() if t is not team]
                result = renpy.call_screen("arena_dogfights", container=container, use_return=True)
                if not result:
                    return
                result = result[2]

            event = GladiatorsEvent(team, result, type, day=fday)
            self.events.append(event)
            ge = self.gui_events
            ge.pager_content.append(event)
            ge.page = ge.max_page()

            if type != "matchfight" or fday == day:
                self.update_fighters(event.guild_chars(), True)
            self.update_teams()

        # Fighting
        def check_before_fight(self, e, gui):
            # check if the members are willing to fight
            type = e.type
            for f in e.guild_chars():
                if not f.is_available:
                    msg = "%s is not available at the moment!" % f.name
                    if gui:
                        PyTGFX.message(msg)
                    return msg

                if f.status == "slave":
                    if type != "inhouse":
                        msg = "%s is a Slave forbidden from participation in Combat!" % f.name
                        if gui:
                            PyTGFX.message(msg)
                        return msg
                    if f.get_stat("health") < f.get_max("health")/8:
                        if gui:
                            if not renpy.call_screen("yesno_prompt",
                                         message="%s is already pretty damaged. Forcing %s to battle might cost %s life. Is that what you want?" % (f.name, f.op, f.pd),
                                         yes_action=Return(True), no_action=Return(False)):
                                return
                        f.mod_stat("joy", -2)
                        self.logws("joy", -2, f)
                    elif f.PP < 150 or any((f.get_stat(stat) < f.get_max(stat)/2 for stat in ("health", "mp", "vitality"))): # PP_PER_AP, BATTLE_STATS
                        if gui:
                            if not renpy.call_screen("yesno_prompt",
                                         message="%s does not feel ready for a battle, but as a slave %s has to follow orders. Do you want to force %s?" % (f.name, f.p, f.pd),
                                         yes_action=Return(True), no_action=Return(False)):
                                return
                        f.mod_stat("joy", -1)
                        self.logws("joy", -1, f)
                elif type != "matchfight":
                    if f.PP < 150: # PP_PER_AP
                        if gui:
                            iam.refuse_because_tired(f)
                        return "%s does not feel ready for a battle! (AP is too low)" % f.name
                    for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                        if f.get_stat(stat) < f.get_max(stat)/2:
                            if gui:
                                iam.refuse_because_tired(f)
                            return "%s does not feel ready for a battle! (%s is too low)" % (f.name, stat.capitalize())

                if f.task != GladiatorTask and not gui:
                    return "%s has a different assignment at the moment!" % f.name

            # check if the opponent is ready in case of a dogfight
            if type == "dogfight":
                arena = pytfall.arena
                opponent = e.opponent
                if opponent not in chain(arena.dogfights_1v1, arena.dogfights_2v2, arena.dogfights_3v3):
                    msg = "%s is no longer available for a fight!" % opponent.gui_name
                    if gui:
                        PyTGFX.message(msg)
                    return msg

        def fight_event(self, e, logical, gui):
            msg = self.check_before_fight(e, gui)
            if msg:
                return msg
            self.run_event(e, logical, gui)

        def run_event(self, e, logical, gui):
            guild_chars = e.guild_chars()
            # store current stats, prepare off_team:
            member_stats = {f: [f.gold, f.exp, f.arena_rep, f.inventory] for f in guild_chars}
            for f, stats in member_stats.iteritems():
                # BATTLE_STATS + COMBAT_STATS
                combat_stats = {stat: f.get_stat(stat) for stat in ("health", "mp", "vitality", "attack", "defence", "magic", "agility", "intelligence")}
                stats.append(combat_stats)

            off_team = e.team
            for f in off_team:
                # give hero's inventory to the members, so the hero gets the reward
                # TODO: right now the chars can not use the inventory during battle,
                #       so this is fine, but this might change later...
                f.inventory = hero.inventory

            off_team.setup_controller()

            # run the battle
            type = e.type
            opponent = e.opponent
            if type == "chainfight":
                # mutliple fights
                result, combat_log = pytfall.arena.run_chainfight(opponent, off_team, logical)
            elif type == "matchfight":
                result, combat_log = pytfall.arena.run_matchfight(opponent, off_team, logical)
            elif type == "dogfight":
                result, combat_log = pytfall.arena.run_dogfight(opponent, off_team, logical)
            else: # inhouse
                result, combat_log = self.run_dogfight(opponent, off_team, logical)
            e.result = result

            off_team.reset_controller()

            # log the result
            #  guild-log
            self.match_logs[type].append(GladiatorsLog(day, combat_log))
            #  ND-log
            if result[0] == off_team:
                # won battle
                msg = choice(["%s won against %s!",
                              "%s beat %s!",
                              "%s defeated %s!",
                              "%s was victorious against %s!"])
            elif result[0] is None:
                # draw battle
                msg = choice(["The battle between %s and %s ended in a draw!",
                              "%s vs. %s result in draw!",
                              "In the %s vs. %s match the result was a draw!",
                              "%s and %s battle to draw!"])
            else:
                # lost battle
                if not gui and type != "inhouse":
                    # lost battle during ND
                    self.flag_red = True
                msg = choice(["%s lost against %s!",
                              "%s surrendered to %s!",
                              "%s was defeated by %s!"])
            self.logs.append(msg % (off_team.gui_name, e.enemy_name()))

            # Collect rewards:
            for f in off_team:
                stats = member_stats[f]
                gold = f.gold - stats[0]
                if gold:
                    f.take_money(gold, "Gladiators Guild")
                    self.earned += gold
                    hero.add_money(gold, "Gladiators Guild")

                # restore the inventory
                f.inventory = stats[3]

            # update charmod
            for f, stats in member_stats.iteritems():
                v = f.exp - stats[1]
                if v != 0:
                    self.logws("exp", v, f)
                v = f.arena_rep - stats[2]
                if v != 0:
                    self.logws("arena rep", v, f)
                stats = stats[4]
                for stat, v in stats.iteritems():
                    v = f.get_stat(stat) - v
                    if v != 0:
                        self.logws(stat, v, f)
                # check if there was a vulnerable slave in the teams
                if f.status != "slave":
                    continue # not a slave
                bhp = f.get_max("health")/8
                if stats["health"] >= bhp:
                    continue # not vulnerable
                if dice(get_linear_value_of(f.get_stat("health"), 0, 80, bhp, 0)):
                    msg = "%s died in the combat!" % f.name
                    self.logs.append(msg)
                    if gui:
                        PyTGFX.message(msg)
                    else:
                        self.flag_red = True
                    kill_char(f)

            # update team
            self.nd_team.update(guild_chars)
            
            if gui:
                self.update_fighters(guild_chars, False)
                self.update_teams()

        def watch_event(self, e):
            # checks
            if hero.PP < 200: # PP_PER_AP
                return PyTGFX.message("You don't have enough time (2 AP) for that.")
            elif e.type == "matchfight" and not hero.take_money(Arena.match_entry_fee(e.team, e.opponent), "Arena-Match Entry Fee"):
                return PyTGFX.message("You don't have enough Gold!")
            msg = self.check_before_fight(e, True)
            if msg:
                return msg

            # run the event
            member_aps = {f: f.PP for f in e.guild_chars()}

            if e.type == "inhouse":
                bg = "bg b_city_1"
            else:
                bg = "bg battle_arena_1"
            renpy.scene(layer='screens')
            renpy.show(bg)
            #renpy.hide_screen("building_management")

            last_track = renpy.music.get_playing("world")

            self.run_event(e, False, True)

            # adjust hero's ap
            hero.PP -= min(200, max((aps - f.PP) for f, aps in member_aps.iteritems())) # PP_PER_AP

            # return to caller:
            #  show building_management
            renpy.scene()
            renpy.show("bg scroll")
            renpy.show_screen("building_management")
            #  restart sound
            if last_track:
                renpy.music.play(last_track, channel="world", fadein=1)

        def reschedule_event(self, e):
            self.update_fighters(e.guild_chars(), True)

        def toggle_repeat(self, e):
            e.repeat = not e.repeat
            self.update_fighters(e.guild_chars(), e.repeat)
            self.update_teams()

        def remove_event(self, e):
            self.events.remove(e)
            ge = self.gui_events
            ge.pager_content.remove(e)
            ge.page = min(ge.page, ge.max_page())

            self.update_fighters(e.guild_chars(), False)
            self.update_teams()

        # Log-Navigation:
        def page_next(self):
            type, idx = self.selected_log_entry
            match_logs = self.match_logs[type]
            idx += 1
            if match_logs[idx].day == match_logs[idx-1].day:
                idx += 1
            self.selected_log_entry = (type, idx)

        def page_previous(self):
            type, idx = self.selected_log_entry
            if idx == 1:
                idx = 0
            else:
                idx -= 2
                match_logs = self.match_logs[type]
                if match_logs[idx].day != match_logs[idx+1].day:
                    idx += 1
            self.selected_log_entry = (type, idx)

        def jump_to_entry(self, selected_log_type, day):
            if selected_log_type is None:
                self.selected_log_entry = None
            else:
                idx = 0
                match_logs = self.match_logs[selected_log_type]
                while match_logs[idx].day != day:
                    idx += 1
                self.selected_log_entry = (selected_log_type, idx)

        # SimPy methods:
        def business_control(self):
            """SimPy business controller.
            """
            # fight the events
            for e in self.events:
                if e.result is None and (e.day is None or e.day == day):
                    msg = self.fight_event(e, True, False)
                    if msg:
                        self.flag_red = True
                        self.logs.append(msg)

            # filter the events and reset the results
            self.events = [e for e in self.events if e.repeat or (e.day is not None and e.day > day)]
            for e in self.events:
                e.result = None

            # release chars FIXME ND of the chars might complain about missing assignment, etc..?
            self.update_fighters(self.nd_team, False)

            yield self.env.timeout(105) # FIXME MAX_DU

            building = self.building

            # use the HealingSprings
            if self.has_extension(HealingSprings):
                bathers = [w for team in self.teams for w in team if w.PP > 0 and w.is_available] 
                if bathers:
                    teammod = {}
                    for w in bathers:
                        charmod = {}
                        #mod_battle_stats(w, .25 * w.PP / w.setPP)
                        mod = .5 * w.PP / w.setPP
                        for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                            value = round_int(w.get_max(stat)*mod) # mod_battle_stats
                            value = w.mod_stat(stat, value)
                            charmod[stat] = value
                        teammod[w] = charmod
                        w.PP = 0

                    txt = choice(["The members of the guild-teams visited the Healing Springs of the %s.",
                                   "The members of the guild-teams took some time off to visit the Onsen in the %s."])
                    txt = txt % self.name

                    img = nd_report_image(HealingSprings.img, bathers, ("onsen", "no bg"), ("bathing", None), exclude=["nude", "sex"], type="ptls")

                    evt = NDEvent(job=RestTask, loc=building, txt=txt, img=img, charmod=teammod, team=bathers, business=self)
                    NextDayEvents.append(evt)
            else:
                # no healing spring -> normal rest of the gladiators:
                fighters = [w for team in self.teams for w in team if w.PP > 0 and w.is_available and w.task == GladiatorTask]

                for w in fighters:
                    mod = .33 * w.PP / w.setPP
                    for stat in ("health", "mp", "vitality"): # BATTLE_STATS
                        value = round_int(w.get_max(stat)*mod) # mod_battle_stats
                        value = w.mod_stat(stat, value)
                        self.logws(stat, value, w)
                    w.PP = 0

            # Next Day:
            txt = self.logs
            txt.insert(0, "%s Gladiators Report!\n" % building.name)

            # try to assign match fighters for the upcoming day
            for e in self.events:
                if e.type == "matchfight" and e.day == day+1:
                    for f in e.team:
                        if not f.is_available:
                            txt.append("%s is currently unavailable, but %s is going to have a match fight tomorrow!" % (f.name, f.p))
                            self.flag_red = True
                            continue
                        f.set_task(GladiatorTask)

            # add log-entry about the earnings (copy-paste from NDEvent.after_job) TODO ... 
            earned = self.earned
            if earned:
                building.fin.log_logical_income(earned, GladiatorTask.id)
                txt.append("You've earned {color=gold}%d Gold{/color}!" % earned)
            else:
                txt.append("{color=gold}No Gold{/color} was earned!")

            # Build an image combo for the report:
            img = choice(["content/gfx/bg/be/battle_arena_1.webp",
                          "content/gfx/bg/be/battle_dogfights_1.webp",
                          "content/gfx/bg/be/battle_indoor_1.webp"])
            img = nd_report_image(img, self.nd_team, "fighting", exclude=["nude", "sex"])

            # Prepare the event
            evt = NDEvent(type='gladiatorsndreport',
                          img=img,
                          txt=self.logs,
                          team=self.nd_team,
                          charmod=self.team_charmod,
                          loc=building,
                          #green_flag=self.flag_green,
                          red_flag=self.flag_red)
            NextDayEvents.append(evt)

            self.reset_nd_fields()

        def run_dogfight(self, def_team, off_team, logical):
            """
            Same/Similar to arena.run_dogfight, but the fight is not public.
            - Slaves are allowed.
            - Draw is possible.
            - No reputation rewards
            - No gold rewards
            - High EXP
            """
            member_sts = {f: f.status for f in chain(off_team, def_team)}
            for f in chain(off_team, def_team):
                f.status = "free"

            member_aps = {f: f.PP for f in chain(off_team, def_team)}

            global battle
            if logical is True:
                battle = run_auto_be(off_team, def_team, simple_ai=False)
            else:
                renpy.music.stop(channel="world")
                renpy.play(choice(["content/sfx/sound/world/arena/prepare.mp3", "content/sfx/sound/world/arena/new_opp.mp3"]))
                track = get_random_battle_track()
                renpy.music.play(track, fadein=1.5)
                renpy.pause(.5)

                def_team.setup_controller()

                battle = BE_Core(bg="battle_indoor_1", start_sfx=get_random_image_dissolve(1.5),
                                 end_bg="b_city_1", end_sfx=dissolve, give_up="surrender",
                                 max_turns=True, teams=[off_team, def_team]) 
                battle.start_battle()

                # Reset the controllers:
                #off_team.reset_controller()
                def_team.reset_controller()

                renpy.music.stop(fadeout=1.0)

            # restore status of the members
            for f in chain(off_team, def_team):
                f.status = member_sts[f]

            # calculate the spent ap
            for f, aps in member_aps.iteritems():
                member_aps[f] = (aps - f.PP)/100.0 # PP_PER_AP = 100

            # Awards: 
            combat_stats = dict()
            if battle.logical_counter >= battle.max_turns:
                # Draw - No cash, No a-rep and normal EXP. -
                battle.combat_log[-1] = "Battle went on for far too long! It is a draw."
                winner = loser = None

                for team0, team1 in ((off_team, def_team), (def_team, off_team)):
                    for f in team0:
                        statdict = OrderedDict()
                        if f in battle.corpses:
                            statdict["K.O."] = "Yes"
                            mod = .5
                        else:
                            mod = 1.1
                        rew_xp = exp_reward(f, team1, exp_mod=member_aps[f]*mod)
                        f.mod_exp(rew_xp)
                        statdict["Exp"] = rew_xp

                        combat_stats[f] = statdict

            else:
                # Decided - No cash, No a-rep and high EXP. -
                winner = battle.winner
                loser = def_team if winner is off_team else off_team

                for f in winner:
                    statdict = OrderedDict()
                    if f in battle.corpses:
                        statdict["K.O."] = "Yes"
                        mod = 1
                    else:
                        mod = 4
                    rew_xp = exp_reward(f, loser, exp_mod=member_aps[f]*mod)
                    f.mod_exp(rew_xp)
                    statdict["Exp"] = rew_xp

                    combat_stats[f] = statdict

                for f in loser:
                    rew_xp = exp_reward(f, winner, exp_mod=member_aps[f])
                    f.mod_exp(rew_xp)
                    combat_stats[f] = OrderedDict([("K.O.", "Yes"), ("Exp", rew_xp)])

            if not logical:
                renpy.call_screen("arena_aftermatch", off_team, def_team, combat_stats, None if winner is None else (off_team is winner))

            return (winner, loser), list(battle.combat_log)

        def logws(self, stat_skill, value, char):
            teammod = self.team_charmod
            charmod = teammod.get(char, None)
            if charmod is None:
                charmod = {}
                teammod[char] = charmod
            charmod[stat_skill] = charmod.get(stat_skill, 0) + value
