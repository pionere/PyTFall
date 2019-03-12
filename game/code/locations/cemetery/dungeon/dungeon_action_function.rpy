init python:
    def dungeon_combat(mob_id, sound=None):
        len_ht = len(hero.team)

        enemy_team = Team(name="Enemy Team", max_size=3)
        min_lvl = max(hero.team.get_level()-5, mobs[mob_id]["min_lvl"])
        for i in range(min(3, len_ht+randint(0, 1))):
            mob = build_mob(id=mob_id, level=randint(min_lvl, min_lvl+10))
            enemy_team.add(mob)

        result = run_default_be(enemy_team,
                                background="content/gfx/bg/be/b_dungeon_1.webp",
                                slaves=False, prebattle=False,
                                death=True, use_items=True) # TODO: maybe make escape working here too?

        if result is True:
            if persistent.battle_results:
                renpy.call_screen("give_exp_after_battle", hero.team, enemy_team)
            else:
                for member in hero.team:
                    member.gfx_mod_exp(exp_reward(member, enemy_team))
        else:
            jump("game_over")

    def dungeon_grab_item(item, sound=None):
        if sound is not None:
            filename, channel = sound
            renpy.play(filename, channel=channel)
        item = store.items[item]
        hero.inventory.append(item)
        dungeon.say([hero.name, "{}! This will come useful!".format(item.id)])
