init -2 python:
    # Interactions (Girlsmeets decisions):
    class InteractionsDecisions(_object):
        @staticmethod
        def become_lovers(character):
            l_ch = 0

            char_traits = character.traits
            if "Shy" in char_traits:
                l_ch -= 10
            if "Virgin" in char_traits:
                l_ch -= 10
            elif "MILF" in char_traits:
                l_ch += 10
            if "Nymphomaniac" in char_traits:
                l_ch += 30
            if "Frigid" in char_traits:
                l_ch -= 30
            if "Impersonal" in char_traits:
                l_ch += 50
            elif "Kuudere" in char_traits:
                l_ch += 30
            elif "Dandere" in char_traits:
                l_ch += 20
            elif "Tsundere" in char_traits:
                l_ch += 40
            elif "Imouto" in char_traits:
                l_ch += 60
            elif "Bokukko" in char_traits:
                l_ch += 70
            elif "Ane" in char_traits:
                l_ch += 50
            elif "Kamidere" in char_traits:
                l_ch += 60
            elif "Yandere" in char_traits:
                l_ch += 80
            else:
                l_ch += 70

            if character.status == "slave":
                l_ch += 200

            return character.get_stat("affection") >= (600 - l_ch)

        @staticmethod
        def want_hug(character):
            l_ch = check_submissivity(character) * 50
            if "SIW" not in character.gen_occs:
                l_ch += 200

            if character.get_stat("affection") > l_ch or iam.slave_siw_check(character):
                return True

            if character.get_stat("affection") <= (l_ch - 50):
                return "blowoff"
            return False

        @staticmethod
        def want_buttgrab(character):
            l_ch = 50 + (check_submissivity(character) * 50)
            if "SIW" not in character.gen_occs:
                l_ch += 200

            if character.get_stat("affection") > l_ch or iam.slave_siw_check(character):
                return True

            if character.get_stat("affection") < (l_ch - 50):
                return "blowoff"
            return False

        @staticmethod
        def want_breastgrab(character):
            l_ch = 100 + (check_submissivity(character) * 50)
            if "SIW" not in character.gen_occs:
                l_ch += 200

            if character.get_stat("affection") > l_ch or iam.slave_siw_check(character):
                return True

            if character.get_stat("affection") < (l_ch - 50):
                return "blowoff"
            return False

        @staticmethod
        def want_kiss(character):
            l_ch = 100 + (check_submissivity(character) * 50)
            if "SIW" not in character.gen_occs:
                l_ch += 250

            if character.get_stat("affection") > l_ch or iam.slave_siw_check(character):
                return True

            if character.get_stat("affection") < (l_ch - 50):
                return "blowoff"
            return False
