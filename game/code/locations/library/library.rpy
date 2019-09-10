init python:
    class LibraryBooks(_object):
        """Simple class to hold library texts and format them appropriately.
        """
        def __init__(self):
            self.data = load_json("code/locations/library/coordinates.json")

        def get_book(self, name):
            book_map = dict((i["id"], i) for i in self.data)
            book = book_map[name]

            result = []
            self.add_content(result, book["title"], style="library_book_header_main")
            #self.add_content(result, book["sub_title"], style="library_book_header_sub")
            for i in book["content"]:
                self.add_content(result, "\n\n" + i, style="library_book_content")
            return result

        @staticmethod
        def add_content(book, text, **kwargs):
            """Adds content to the book using kwargs to add style.
            """
            book.append((text, kwargs))

label academy_town:
    scene bg academy_town

    if pytfall.enter_location("library", music=True, env="library", coords=[(.1, .55), (.45, .64), (.86, .65)],
                            badtraits=["Adventurous", "Slime", "Monster"], goodtraits=["Curious"], has_tags=["girlmeets", "schoolgirl"]):
        $ golem = npcs["Eleven"]
        $ e = golem.say
        $ golem.override_portrait("portrait", "indifferent")
        show expression golem.get_vnsprite() as npc
        with dissolve
        "A tall humanoid with glowing eyes and booming voice greets you at the entrance."
        e "{b}Welcome to the archive, [hero.name].{/b}"
        $ golem.override_portrait("portrait", "confident")
        e "{b}Please keep silence and do not disturb other visitors.{/b}"
        $ golem.override_portrait("portrait", "indifferent")
        "Many years ago academy archives were entrusted to him, and since then not a single document was lost. During the last war, he single-handedly destroyed all threats, preserving the whole building intact."
        "He also always knows the name of his interlocutor, even if they never met before. This particular trait made him infamous in the city."
        hide npc with dissolve
        $ del e, golem

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    show screen academy_town
    with dissolve # dissolve the whole scene, not just the bg
    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_int(result[1], img=result[1].show("girlmeets", "schoolgirl", "indoors", exclude=["swimsuit", "wildness", "beach", "pool", "urban", "stage", "onsen"], type="reduce", label_cache=True, gm_mode=True))

        elif result[0] == "control":
            hide screen academy_town
            if result[1] == "return":
                jump city
            elif result[1] == "eleven":
                jump library_eleven_dialogue
            elif result[1] == "read":
                jump library_read_matrix
            elif result[1] == "study":
                jump mc_action_library_study

label library_eleven_dialogue:
    $ golem = npcs["Eleven"]
    $ e = golem.say
    $ golem.override_portrait("portrait", "indifferent")
    show expression golem.get_vnsprite() as npc
    with dissolve
    "The golem stands in the center of the hall, resembling a statue. But his head instantly turns to your direction when you approach."
    e "{b}...{/b}"
    menu eleven_menu:
        "Show leaflets" if has_items("Rebels Leaflet", hero, equipped=False) and global_flags.flag('player_knows_about_eleven_jobs'):
            $ golem_change = ImageDissolve("content/gfx/masks/m12.webp", .5, ramplen=128, reverse=True, time_warp=eyewarp) # masks for changing between eleven sprites
            $ golem_change_back = ImageDissolve("content/gfx/masks/m12.webp", .5, ramplen=128, reverse=False, time_warp=eyewarp)
            hide npc
            show expression golem.show("battle", resize=(800, 600)) as npc
            with golem_change
            $ money = has_items("Rebels Leaflet", hero, equipped=False)*50
            "Without a single word, the golem destroys leaflets in your hands. Warm ash falls on the floor."
            hide npc
            show expression golem.get_vnsprite() as npc
            with golem_change_back
            $ golem.override_portrait("portrait", "confident")
            e "{b}This unit and the city appreciate your services. Keep it up, [hero.name]. Here is your reward, [money] coins.{/b}"
            $ hero.remove_item("Rebels Leaflet", has_items("Rebels Leaflet", hero, equipped=False))
            $ hero.add_money(money, reason="Items")
            $ del money, golem_change, golem_change_back
            $ golem.override_portrait("portrait", "indifferent")
            jump eleven_menu
        "Donate books" if global_flags.flag('player_knows_about_eleven_jobs'):
            $ num = has_items("Old Books", hero, equipped=False)
            if num > 0:
                "How many do you want to donate?"
                menu:
                    "[num]" if num < 10:
                        $ pass
                    "10" if num >= 10:
                        $ num = 10
                    "20" if 50 > num >= 20:
                        $ num = 20
                    "50" if num >= 50:
                        $ num = 50
                    "100" if num >= 100:
                        $ num = 100
                    "All" if num > 10:
                        $ pass
                    "Nevermind":
                        $ num = 0
                if num:
                    e "{b}I appreciate your concern about the archive collection, [hero.name].{/b}"
                    $ hero.remove_item(items["Old Books"], num)
                    $ global_flags.up_counter("library_book_donations", num)
                    $ num = global_flags.flag("library_book_donations") / 100
                    if num:
                        $ hero.mod_stat("reputation", randrange(num))
                        $ global_flags.up_counter("library_book_donations", -100*num)
            else:
                e "{b}Yes, we appreciate any help to extend our archive. Obviously we need rare, old books.{/b}"
            $ del num
            jump eleven_menu
        "Ask about him":
            e "{b}This unit was found and activated during excavations in Crossgate city among other units classified amount of time ago. It was eleventh, so it was called Eleven.{/b}"
            e "{b}After some time, it was bought by PyTFall's government and given the position of Archive Watcher. As the Watcher, this unit is a government official able to enforce rules using any necessary means.{/b}"
            e "{b}Later it was given the order to join military, but this unit is incapable to rewrite core directives once they were set. Therefore it serves as the Archive Watcher to this day.{/b}"
            $ golem.override_portrait("portrait", "confident")
            e "{b}All further information is classified.{/b}"
            $ golem.override_portrait("portrait", "indifferent")
            jump eleven_menu
        "Ask about the archive":
            e "{b}You are free to read all books presenting here. Do not attempt to damage them or take them out of the building.{/b}"
            $ golem.override_portrait("portrait", "confident")
            e "{b}Currently, some books are seized by the government for examination. Please refrain from further questions.{/b}"
            $ golem.override_portrait("portrait", "indifferent")
            jump eleven_menu
        "Ask about job":
            e "{b}I would be glad to expand the archive collection. We do not need common books, but you may bring any unusual and rare ones.{/b}"
            e " {b}I can not pay anything in return, but the people of the city surely benefit from these donations.{/b}"
            $ golem.override_portrait("portrait", "confident")
            e "{b}More importantly, I was entrusted with the task to clear the city from forbidden propaganda. After the war, a lot of leaflets made by rebels left in the city. I am authorized to pay for any prohibited leaflets, which will be destroyed soon after that.{/b}"
            "At these words, his eyes flash brightly, and you can sense his hostility - not towards you, but towards the rebels."
            $ golem.override_portrait("portrait", "angry")
            e "{b}Handle them with care. Once you find one, bring it to me immediately and you will be compensated for your efforts. Otherwise, you will be suspected of treason.{/b}"
            $ golem.override_portrait("portrait", "indifferent")
            $ global_flags.set_flag('player_knows_about_eleven_jobs')
            jump eleven_menu
        "Leave him be":
            "You step away, and the light in his eyes dims."
            hide npc with dissolve
            $ del e, golem
            jump academy_town

screen academy_town():
    use top_stripe(True)

    style_prefix "action_btns"
    frame:
        has vbox
        textbutton "Find Eleven":
            action Return(["control", "eleven"])
        textbutton "Read the books":
            action Return(["control", "read"])
        textbutton "Meet Girls":
            action ToggleField(iam, "show_girls")

    if iam.show_girls:
        use interactions_meet
    else:
        $ img = im.Scale("content/gfx/interface/icons/library_study.png", 80, 80)
        imagebutton:
            pos (720, 340)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action Return(["control", "study"])
            tooltip "Study"

label library_read_matrix:
    if not hasattr(store, "lib_books"):
        $ lib_books = LibraryBooks()

    call screen poly_matrix(lib_books.data, show_exit_button=(1.0, 1.0))

    if _return:
        call screen library_show_text(lib_books.get_book(_return))
        with dissolve
    else:
        $ del lib_books
        jump academy_town

screen library_show_text(book):

    add "content/gfx/frame/library_page.jpg" at truecenter
    side "c r":
        pos (306, 30)
        xysize (675, 670)
        viewport id "vp":
            mousewheel True
            draggable True
            xysize (675, 670)
            vbox:
                null height 10
                for text, style in book:
                    add Text(text, **style)
        vbar value YScrollValue("vp")

    textbutton "Enough with it":
        style "pb_button"
        align (1.0, 1.0)
        action (Hide("library_show_text", transition=dissolve), Jump("library_read_matrix"))
        keysym "mousedown_3"

label mc_action_library_study:
    if not global_flags.flag('studied_library'):
        $ global_flags.set_flag('studied_library')
        "Here you can study various topics with your team."
        extend "The entrance fee is 250 Gold per person."
        "The effectiveness of the session is depending on the size of the team."
        extend "The larger the group, the more you can learn."
        "Be aware that certain personalities do not fit here and might disrupt the group."

        menu:
            "Do you want to study now?"

            "Yes":
                $ pass
            "No":
                jump academy_town

    if hero.gold < len(hero.team) * 250:
        if len(hero.team) > 1:
            "You don't have enough gold to cover the fees for of your team."
        else:
            "You don't have enough gold to cover the fee."

        "The fee is 250 Gold per person."
        jump academy_town

    $ members = hero.team
    if len(members) == 1:
        $ team_pp = hero.PP
        $ team_ap = "You have %d AP."
    else:
        $ team_pp = min(char.PP for char in members)
        $ team_ap = "Your team has %d AP."
    $ team_pp = int(team_pp / 100) # PP_PER_AP 
    if not team_pp:
        if len(members) > 1:
            "Unfortunately, your team is too tired at the moment. Maybe another time."
        else:
            "You don't have Action Points left. Try again tomorrow."

        "Each member of your party must have 1 AP."
        $ del members, team_ap, team_pp
        jump academy_town

    $ hero.take_money(len(members)*250, "Library Fee")

    call screen library_study
    $ result = _return
    if result:
        $ team_ap = (team_ap % team_pp) + " How much time do you want to spend studying?"
        $ team_ap = renpy.call_screen("digital_keyboard", line=team_ap)
        if not team_ap:
            "You wanted to leave, but since you already paid for the entry you decided to stay for a bit."
            $ team_ap = 1
        elif team_ap > team_pp:
            $ team_ap = team_pp

        $ temp = result[1]
        if len(members) > 1:
            if len(members) == 2:
                show expression members[1].get_vnsprite() at center as temp1
                with dissolve
            else:
                show expression members[1].get_vnsprite() at left as temp1
                show expression members[2].get_vnsprite() at right as temp2
                with dissolve
            "You're studying [temp] with your team."
        else:
            "You're studying [temp]."
        $ temp = min(char.tier for char in members if char != hero)
        $ temp = 7 - 2 * len(members) + min(hero.tier - temp, 2) 
        $ iam.study_reward(members, result[2], team_ap, temp)
        $ del temp
    else:
        $ team_ap = 1
        if len(members) > 1:
            "You could not agree on what to study. What a waste of time (and gold)."
        else:
            "You cound not find anything interesting..."
    $ members.take_ap(team_ap)
    $ del result, members, team_ap, team_pp
    jump academy_town

screen library_study():
    vbox:
        style_group "wood"
        xalign .5
        button:
            xysize (250, 40)
            action Return("")
            text "Finish" size 15
            keysym "mousedown_3"

    python:
        options = (["content/items/misc/mc.png", "Chess", "intelligence"],
                   ["content/items/misc/fish.png", "Fishing", "fishing"],
                   ["content/items/misc/swim.png", "Swimming", "swimming"],
                   ["content/items/misc/cc.png", "The Kamasuththra", "sex"])
        step = 360 / len(options)
        var = 0

    for option in options:
        python:
            img = PyTGFX.scale_content(option[0], 100, 100)
            angle = var
            var = var + step
        imagebutton at circle_around(t=10, angle=angle, radius=240):
            idle img
            hover PyTGFX.bright_content(img, .25)
            action Return(option)
            tooltip option[1]
