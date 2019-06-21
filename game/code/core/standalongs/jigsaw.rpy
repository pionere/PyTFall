#####################################################################################################
#
#Credits:
#    SusanTheCat - the original code for jigsaw puzzle
#
#    PyTom - "image location picker" code
#
#
#####################################################################################################
init python:
    def piece_dragged(drags, drop):
        drag = drags[0]
        x, y = drag.old_position[0], drag.old_position[1]
        if not drop:
            #drag.snap(x, y, delay=.2)
            return

        piece = drag.drag_name
        piece = piece[:-6]

        dest = drop.drag_name

        if piece != dest:
            #drag.snap(x, y, delay=.2)
            return

        p_x, p_y = piece.split(",")
        p_x, p_y = int(p_x), int(p_y)
        
        a = []
        a.append(drop.drag_joined)
        a.append((drag, 3, 3))
        drop.drag_joined(a)

        renpy.music.play("content/sfx/sound/jp/Pat.mp3", channel="sound")

        my_x = int(p_x*axsize+field_offset_x)
        my_y = int(p_y*aysize+field_offset_y)

        drag.snap(my_x, my_y, delay=.1)
        drag.draggable = False
        placedlist[p_x][p_y] = True

        for i in xrange(grid_width):
            for j in xrange(grid_height):
                if not placedlist[i][j]:
                    return
        return True

label jigsaw_puzzle_start:
    hide screen gallery
    scene bg jigsaw
    with dissolve

    $ grid_width = grid_height = 3  # default values
    $ puzzle_field_size = 655       # should be less then minimal of config.screen_width and config.screen_height values
    $ img_to_play = PyTGFX.scale_img(os.path.join(gallery.girl.path_to_imgfolder, gallery.imagepath), puzzle_field_size, puzzle_field_size)
    $ renpy.call_screen("control_scr", img_to_play)

    python:
        img_width, img_height = img_to_play.load().get_size() # get the real size of the image (true_size)
        puzzle_piece_size = 450       # the size of stencil images that are used to create puzzle piece
        grip_size = 75       # see "_how_to_make_a_tile.png" file
        active_area_size = puzzle_piece_size - (grip_size * 2)

        axsize = float(img_width)/grid_width   # active size of a piece
        aysize = float(img_height)/grid_height

        x_scale_index = axsize/active_area_size
        y_scale_index = aysize/active_area_size

        grip_size_x = grip_size*x_scale_index
        grip_size_y = grip_size*y_scale_index

        img_size_x = int(img_width+2*grip_size_x)
        img_size_y = int(img_height+2*grip_size_y)
        mainimage = im.Composite((img_size_x, img_size_y),
                                 (int(grip_size_x), int(grip_size_y)), img_to_play)

        xsize = int(axsize + 2*grip_size_x)    # a size of a piece with its grip
        ysize = int(aysize + 2*grip_size_y)

        field_offset_x = (config.screen_width - img_width)/2 - grip_size_x    # the offset from top left corner
        field_offset_y = (config.screen_height - img_height)/2 - grip_size_y  # the offset from top left corner

        jigsaw_grid = [[None] * grid_height for i in xrange(grid_width)] 
        for i in xrange(grid_width):
            for j in xrange(grid_height):
                entry = [0, 0, 0, 0] # [top, right, bottom, left]
                jigsaw_grid[i][j] = entry
                # top
                if j != 0:
                    if jigsaw_grid[i][j-1][2] == 1:
                        entry[0] = 2
                    else:
                        entry[0] = 1

                # right
                if (i+1) != grid_width: # not in right_column:
                    entry[1] = randint(1,2)

                # bottom
                if (j+1) != grid_height: # not in bottom_row:
                    entry[2] = randint(1,2)

                # left
                if i != 0:
                    if jigsaw_grid[i-1][j][1] == 1:
                        entry[3] = 2
                    else:
                        entry[3] = 1


        # makes description for each puzzle piece
        piecelist = [[None] * grid_height for i in xrange(grid_width)]
        imagelist = [[None] * grid_height for i in xrange(grid_width)]
        placedlist = [[False] * grid_height for i in xrange(grid_width)]

        free_x = config.screen_width - (img_size_x + axsize)
        free_y = config.screen_height - aysize
        for i in xrange(grid_width):
            for j in xrange(grid_height):
                # set the location of the piece
                piece_x = randrange(free_x)
                piece_y = randrange(free_y) + int(aysize/2)
                if piece_x > free_x/2:
                    piece_x += int(img_size_x + axsize/2)
                piecelist[i][j] = [piece_x, piece_y]

                #devlog.warn("Piece %s,%s at %s:%s" % (i, j, piece_x, piece_y))

                # makes puzzle piece image using its shape description and tile pieces
                # (will rotate them to form top, right, bottom and left sides of puzzle piece)

                # create the mask
                d = Fixed(xysize=(xsize, ysize))
                d.add(Transform("content/gfx/interface/images/jp/_00%s.png"%(jigsaw_grid[i][j][0]), rotate=0, rotate_pad=False, size=(xsize, ysize)))
                d.add(Transform("content/gfx/interface/images/jp/_00%s.png"%(jigsaw_grid[i][j][1]), rotate=90, rotate_pad=False, size=(xsize, ysize)))
                d.add(Transform("content/gfx/interface/images/jp/_00%s.png"%(jigsaw_grid[i][j][2]), rotate=180, rotate_pad=False, size=(xsize, ysize)))
                d.add(Transform("content/gfx/interface/images/jp/_00%s.png"%(jigsaw_grid[i][j][3]), rotate=270, rotate_pad=False, size=(xsize, ysize)))
                # create the piece using the mask
                fixed = Fixed(xysize=(xsize, ysize))
                fixed.add(AlphaMask(im.Crop(mainimage, int(i*axsize), int(j*aysize), xsize, ysize), d))

                # add an almost transparent layer, so the player can grab it FIXME should not be necessary with a fixed RenPy
                fixed.add(Transform(im.Scale("content/gfx/interface/images/jp/_puzzle_field.webp", xsize-2*grip_size_x, ysize-2*grip_size_y), pos=((int(grip_size_x), int(grip_size_y)))))
                imagelist[i][j] = fixed

    jump puzzle

label puzzle:
    scene bg gallery
    call screen jigsaw
    #with dissolve

    #scene bg gallery
    show expression img_to_play at Position(xalign=.5,yalign=.5)
    #with dissolve

    "Congratulations!"
    menu:
        "Play again?"

        "Yes":
            jump jigsaw_puzzle_start

        "No":
            pass

label puzzle_end:
    # cleanup
    python hide:
        cleanup = ["grid_width", "grid_height", "puzzle_field_size", "img_to_play",
                  "img_width", "img_height", "puzzle_piece_size", "grip_size", "active_area_size",
                  "axsize", "aysize", "x_scale_index", "y_scale_index",
                  "grip_size_x", "grip_size_y",
                  "img_size_x", "img_size_y", "mainimage",
                  "xsize", "ysize", "field_offset_x", "field_offset_y",
                  "jigsaw_grid", "i", "j", "entry",
                  "piecelist", "imagelist", "placedlist",
                  "free_x", "free_y",
                  "piece_x", "piece_y", "fixed", "d"]
        for i in cleanup:
            if hasattr(store, i):
                delattr(store, i)
    jump gallery

screen control_scr(preview):
    add preview align .5, .4

    vbox:
        style_group "basic"
        align .1, .4
        spacing 20
        for i in range (2, 11):
            textbutton "[i]" action [SetVariable("grid_height", i), renpy.restart_interaction]

    hbox:
        style_group "basic"
        align .5, .05
        spacing 15
        for i in range (2, 11):
            textbutton "[i]" action [SetVariable("grid_width", i), renpy.restart_interaction]

    $ number_of_pieces = (grid_width*grid_height)
    frame:
        align (.01, .98)
        xpadding 20
        ypadding 20
        style_group "content"
        background Frame("content/gfx/frame/blue_wood.webp", 5, 5)
        label "[number_of_pieces] pieces!" text_size 35 text_color "ivory" align (.5, .5)

    button:
        xysize (100, 40)
        style_group "basic"
        text "Done" size 35
        action Return()
        align (.5, .98)

    use exit_button(size=(60, 60), align=(1.0, .0), action=Jump("puzzle_end"))

screen jigsaw():
    #key "rollback" action NullAction()
    #key "rollforward" action NullAction()
    add im.Scale("content/gfx/frame/MC_bg3.png", img_width, img_height) align .5, .5

    draggroup:
        id "jigsaw"
        for i in xrange(grid_width):
            for j in xrange(grid_height):
                $ name = "%s,%s"%(i, j)
                $ my_x = int(i*axsize+field_offset_x)
                $ my_y = int(j*aysize+field_offset_y)
                drag:
                    drag_name name
                    draggable False
                    droppable True
                    pos (my_x, my_y)
                    add im.Scale("content/gfx/frame/_blank_space.webp", axsize, aysize)

        for i in xrange(grid_width):
            for j in xrange(grid_height):
                $ name = "%s,%s piece"%(i, j)
                drag:
                    dragged piece_dragged
                    droppable 0
                    #tooltip "%s" % name
                    drag_name name
                    pos piecelist[i][j]
                    add imagelist[i][j]

    use exit_button(size=(60, 60), align=(1.0, .0), action=Jump("puzzle_end"))
