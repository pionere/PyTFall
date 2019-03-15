init python:
    # For now a dedicated sorting funcs, maybe this should be turned into something more generic in the future?
    def all_chars_for_se():
        # We expect a global var bm_building to be set for this!

        # collect the set of all idle characters that are set exploration teams but not exploring:
        # This may be an overkill cause we should really remove workers from teams when we change their locations!
        idle_explorers = set()
        for fg in hero.get_guild_businesses():
            idle_explorers.update(fg.idle_explorers())

        return [w for w in bm_building.all_workers if w.status == "free" and w not in idle_explorers]
