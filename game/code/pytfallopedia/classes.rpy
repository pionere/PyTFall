init python:
    class PyTFallopedia(_object):
        def __init__(self):
            root = ["", "pyp_root", None, []]
            self.focused_page = root

            self.root = root

            curr_menu = self.add_menu("General", "pyp_general", root)
            self.add_menu("Game Settings", "pyp_game_settings", curr_menu)
            self.add_menu("Flow of Time", "pyp_time_flow", curr_menu)
            self.add_menu("Action Points", "pyp_action_points", curr_menu)
            self.add_menu("Next Day", "pyp_next_day", curr_menu)
            self.add_menu("Controls", "pyp_controls", curr_menu)
            self.add_menu("Gazette", "pyp_gazette", curr_menu)

            curr_menu = self.add_menu("Characters", "pyp_characters", root)
            self.add_menu("Locations", "pyp_ctrl", curr_menu)
            self.add_menu("Tiers/Level", "pyp_tiers", curr_menu)
            sub_menu = self.add_menu("Traits", "pyp_traits", curr_menu)
            self.add_menu("Classes", "pyp_classes", sub_menu)
            self.add_menu("Fixed Traits", "pyp_fixed_traits", sub_menu)
            self.add_menu("Elements", "pyp_elements", sub_menu)
            self.add_menu("Effects", "pyp_effects", sub_menu)
            self.add_menu("Stats", "pyp_stats", curr_menu)
            self.add_menu("Skills", "pyp_skills", curr_menu)
            self.add_menu("Controls", "pyp_char_controls", curr_menu)
            self.add_menu("Status", "pyp_status", curr_menu)
            self.add_menu("Actions", "pyp_action_points", curr_menu)

            curr_menu = self.add_menu("City", "pyp_city", root)
            self.add_menu("Interactions", "pyp_interactions", curr_menu)
            self.add_menu("MC Actions", "pyp_mc_actions", curr_menu)
            self.add_menu("Slave Market", "pyp_slave_market", curr_menu)
            self.add_menu("NPCs", "pyp_npcs", curr_menu)
            self.add_menu("Arena", "pyp_arena", curr_menu)
            self.add_menu("Main Street", "pyp_main_street", curr_menu)

            curr_menu = self.add_menu("Combat", "pyp_battle_engine", root)
            self.add_menu("Teams", "pyp_teams", curr_menu)
            self.add_menu("Attacks", "pyp_attacks", curr_menu)
            self.add_menu("Magic", "pyp_magic", curr_menu)
            self.add_menu("Items", "pyp_be_items", curr_menu)
            self.add_menu("Escape", "pyp_escape", curr_menu)

            curr_menu = self.add_menu("Items", "pyp_items", root)
            self.add_menu("Consumable", "pyp_consumables", curr_menu)
            self.add_menu("Weapons", "pyp_weapons", curr_menu)
            self.add_menu("Unequipable", "pyp_materials", curr_menu)
            self.add_menu("Equippable", "pyp_equippables", curr_menu)
            self.add_menu("MISC", "pyp_misc", curr_menu)
            self.add_menu("Stats/Skills", "pyp_stats_bonuses", curr_menu)
            self.add_menu("Inventory", "pyp_inventory", curr_menu)
            self.add_menu("Shopping", "pyp_shopping", curr_menu)
            self.add_menu("Auto Equip", "pyp_auto_equip", curr_menu)
            self.add_menu("Transfer", "pyp_transfer", curr_menu)
            self.add_menu("Storage", "pyp_storage", curr_menu)

            curr_menu = self.add_menu("Buildings&Businesses", "pyp_buildings_and_businesses", root)
            self.add_menu("Buildings", "pyp_buildings", curr_menu)
            self.add_menu("Businesses", "pyp_businesses", curr_menu)
            self.add_menu("Clients", "pyp_clients", curr_menu)
            self.add_menu("Building Stats", "pyp_building_stats", curr_menu)
            self.add_menu("Advertising", "pyp_advertising", curr_menu)
            self.add_menu("Management", "pyp_manager", curr_menu)
            self.add_menu("Controls", "pyp_buildings_controls", curr_menu)
            self.add_menu("Workers", "pyp_workers", curr_menu)
            self.add_menu("Choosing Workers", "pyp_chworkers", curr_menu)
            self.add_menu("Jobs", "pyp_jobs", curr_menu)
            self.add_menu("Simulation", "pyp_simulation", curr_menu)

            curr_menu = self.add_menu("Exploration Guild", "pyp_se_guild", root)
            self.add_menu("Teams Management", "pyp_se_teams", curr_menu)
            self.add_menu("Exploration Report", "pyp_se_log", curr_menu)
            self.add_menu("Exploration GUI", "pyp_se_exploration_1", curr_menu)
            self.add_menu("Exploration Log", "pyp_se_exploration_2", curr_menu)

            self.add_menu("School", "pyp_school", root)

            curr_menu = self.add_menu("Quest&Events", "pyp_quests_and_events", root)
            self.add_menu("Quests", "pyp_quests", curr_menu)
            self.add_menu("Events", "pyp_events", curr_menu)

        def add_menu(self, name, screen, parent):
            _menu = [name, screen, parent, []]
            parent[3].append(_menu)
            return _menu

        def close(self):
            renpy.hide_screen(self.focused_page[1])
            self.focused_page = self.root

            Hide("pytfallopedia", transition=dissolve)()

        def open(self, page):
            curr_page = self.focused_page
            renpy.hide_screen(curr_page[1])
            self.focused_page = page
            Show(page[1])()
            renpy.restart_interaction()

        def back(self):
            curr_page = self.focused_page
            parent = curr_page[2]
            renpy.hide_screen(curr_page[1])
            if parent != self.root and not curr_page[3]:
                # a leaf -> go back twice to skip the entry screen
                parent = parent[2]
            self.focused_page = parent
            parent_page = parent[1]
            if parent != self.root:
                renpy.show_screen(parent_page)

