init -11 python:
    def mod_to_tooltip(mod):
        t = ["%s: %+d" % (k, v) for k, v in mod.items()]
        return ", ".join(t)

    def show_all_targeting_closshairs(targets):
        for index, t in enumerate(targets):
            temp = dict(what=crosshair_red,
                        at_list=[Transform(pos=battle.get_cp(t, "center",
                                           use_absolute=True),
                        anchor=(.5, .5))], zorder=t.besk["zorder"]+1)
            renpy.show("enemy__"+str(index), **temp)

    def hide_all_targeting_closshairs(targets):
        for index, t in enumerate(targets):
            renpy.hide("enemy__"+str(index))

    def build_multi_elemental_icon(elements=None, size=70, mc=None):
        if elements is None: # Everything except "Neutral"
            elements = tgs.real_elemental

        fixed = Fixed(xysize=(size, size))
        angle = len(elements)
        if angle <= 1:
            if angle == 1:
                icon = elements[0].icon
                if mc is not None:
                    icon = im.MatrixColor(icon, mc)
                icon = PyTGFX.scale_img(icon, size, size) # TODO scale_content?
                fixed.add(icon)
            return fixed
        angle = 360.0/angle

        sqrt2 = math.sqrt(2)

        csize = size*sqrt2
        crop = (0, 0, csize/2, csize)
        rota_shift = (int((1 - sqrt2)*size/2), int((1 - sqrt2)*size/2))
        for index, e in enumerate(elements):
            icon = e.icon
            if mc is not None:
                icon = im.MatrixColor(icon, mc)
            icon = Transform(icon, rotate=180, size=(size, size))
            icon = Transform(icon, crop=crop, subpixel=True) #, align=(0, 0)
            icon = Transform(icon, subpixel=True, pos=rota_shift)
            fx = Fixed(xysize=(size, size))
            fx.add(icon)
            icon = Transform(fx, rotate=180-angle, subpixel=True)
            icon = Transform(icon, crop=crop, subpixel=True) #, align=(0, 0)
            icon = Transform(icon, subpixel=True, pos=rota_shift)
            fx = Fixed(xysize=(size, size))
            fx.add(icon)
            icon = Transform(fx, rotate=(index*angle), subpixel=True)
            icon = Transform(icon, subpixel=True, pos=rota_shift)
            fixed.add(icon)
        return fixed

    def run_auto_be(off_team, def_team, simple_ai=True):
        off_team.setup_controller(simple_ai)
        def_team.setup_controller(simple_ai)

        global battle
        battle = BE_Core(logical=True, max_turns=True, teams=[off_team, def_team])

        if DEBUG_BE:
            msg = "\n    Custom Logical Combat Scenario ===================================================>>>>"
            msg += "\n{} VS {}".format(str([f.name for f in off_team]), str([f.name for f in def_team]))
            msg += "\nUsing simple ai: {}.".format(simple_ai)
            be_debug(msg)

        tl.start("logical combat: BATTLE")
        battle.start_battle()
        tl.end("logical combat: BATTLE")
        be_debug("\n\n")

        # Reset the controllers:
        off_team.reset_controller()
        def_team.reset_controller()

        return battle

    def get_random_battle_track():
        # get a list of all battle tracks:
        folder = content_path("sfx", "music", "be")
        battle_tracks = [fn for fn in listfiles(folder) if check_music_extension(fn)]
        return os.path.join(folder, choice(battle_tracks))

    def be_hero_escaped(team):
        '''Punish team for escaping'''
        for i in team:
            i.PP = 0
            mod_by_max(i, "vitality", -.3)
            mod_by_max(i, "mp", -.3)

    def run_default_be(enemy_team, your_team=None,
                       background="battle_arena_1", end_background=None,
                       track="random", skill_lvl=float("inf"), give_up=None,
                       slaves=True, prebattle=False, use_items=True, death=False):
        """
        Launches BE with MC team vs provided enemy team, returns True if MC won and vice versa
        - if slaves == True, slaves in MC team will be inside BE with passive AI, otherwise they won't be there
        - background by default is arena, otherwise could be anything,
            like iam.select_background_for_fight(iam.label_cache) for GMs
            or iam.select_background_for_fight(pytfall.world_events.event_instance("event name").label_cache) for events
        - track by default is random, otherwise it could be a path to some track
        - if prebattle is true, there will be prebattle quotes inside BE from characters before battle starts
        - if death == True, characters in MC team will die if defeated, otherwise they will have 1 hp left
        """
        if your_team is None:
            your_team = Team(name="Your Team")
            for member in hero.team:
                if member.status == "free":
                    member.controller = None # no AI -> controlled by the player
                    your_team.add(member)
                elif slaves: # and member.status == "slave"
                    member.controller = BE_AI()
                    your_team.add(member)

        # Controllers:
        enemy_team.setup_controller()

        pre_aps = [member.PP for member in your_team]

        global battle
        battle = BE_Core(bg=background, start_sfx=get_random_image_dissolve(1.5),
                    end_bg=end_background, end_sfx=dissolve,
                    music=track, quotes=prebattle,
                    max_skill_lvl=skill_lvl, give_up=give_up,
                    use_items=use_items, teams=[your_team, enemy_team])
        battle.start_battle()

        your_team.reset_controller()
        enemy_team.reset_controller()

        for member in your_team:
            if member in battle.corpses:
                if death:
                    kill_char(member)
                else:
                    member.set_stat("health", 1)
                    member.mod_stat("joy", -randint(5, 15))

        rv = battle.combat_status
        if rv == "escape":
            be_hero_escaped(your_team)
        elif rv != "surrender":
            rv = battle.win
            if rv is True:
                for mob in enemy_team:
                    if mob.__class__ == Mob:
                        defeated_mobs.add(mob.id)

                ap_used = {}
                for member, aps in zip(your_team, pre_aps):
                    ap_used[member] = (aps - member.PP)/100.0 # PP_PER_AP = 100

                if persistent.battle_results:
                    renpy.call_screen("give_exp_after_battle", your_team, enemy_team, ap_used)
                else:
                    for member in your_team:
                        member.gfx_mod_exp(exp_reward(member, enemy_team, exp_mod=ap_used[member]))

        return rv
