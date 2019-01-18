label city_beach_cafe:
    $ gm.enter_location(goodtraits=["Athletic", "Dawdler", "Always Hungry"], badtraits=["Scars", "Undead", "Furry", "Monster"], curious_priority=False)
    $ coords = [[.2, .75], [.5, .65], [.87, .6]]
    $ global_flags.set_flag("keep_playing_music")
    
    python:
        # Build the actions
        if pytfall.world_actions.location("city_beach_cafe"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.look_around()
            pytfall.world_actions.finish()
    
    scene bg city_beach_cafe
    with dissolve
    show screen city_beach_cafe
    
    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")
        
    while 1:

        $ result = ui.interact()

        if result[0] == 'jump':
            $ gm.start_gm(result[1])
        
        if result[0] == 'control':
            if result[1] == 'return':
                hide screen city_beach_cafe
                jump city_beach_cafe_main
                
                
screen city_beach_cafe:

    use top_stripe(True)
    if not gm.show_girls:
        $ img = im.Scale("content/gfx/interface/buttons/blue_arrow.png", 80, 80)
        imagebutton:
            align (.99, .5)
            idle (img)
            hover (im.MatrixColor(img, im.matrix.brightness(.15)))
            action [Hide("city_beach_cafe"), Jump("city_beach_cafe_main")]
    
    use location_actions("city_beach_cafe")
    
    if gm.show_girls:
        key "mousedown_3" action ToggleField(gm, "show_girls")
    
        add "content/gfx/images/bg_gradient.webp" yalign .45
    
        $ j = 0
        for entry in gm.display_girls():
            hbox:
                align (coords[j])
                $ j += 1
                $ tags = entry.get_tags_from_cache(last_label)
                if not tags:
                    $ beach_tags_list = []
                    # main set
                    if entry.has_image("girlmeets", "beach"):
                        $ beach_tags_list.append(("girlmeets", "beach"))
                    if entry.has_image("girlmeets","swimsuit", "simple bg"):
                        $ beach_tags_list.append(("girlmeets", "swimsuit", "simple bg"))
                    if entry.has_image("girlmeets","swimsuit", "outdoors"):
                        $ beach_tags_list.append(("girlmeets", "swimsuit", "outdoors"))
                    # secondary set if nothing found
                    if not beach_tags_list:
                        if entry.has_image("girlmeets", "outdoors"):
                            $ beach_tags_list.append(("girlmeets", "outdoors"))
                        if entry.has_image("girlmeets", "simple bg"):
                            $ beach_tags_list.append(("girlmeets", "simple bg"))
                    # giveup
                    if not beach_tags_list:
                        $ beach_tags_list.append(("girlmeets", ))
                    $ tags.extend(choice(beach_tags_list))

                use rg_lightbutton(img=entry.show(*tags, exclude=["urban", "wildness", "suburb", "nature", "winter", "night", "formal", "indoor"], type="first_default", label_cache=True, resize=(300, 400), gm_mode=True), return_value=['jump', entry])