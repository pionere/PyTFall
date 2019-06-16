label fonts:
    call screen fonts

screen fonts():
    zorder 1000
    default fonts = [os.path.join("fonts", file) for file in listfiles(renpy.loader.transfn("fonts"))]
    default index = 0
    default group = None

    add Solid("black")

    vbox:
        align (.5, .1)

        python:
            if not group:
                font = fonts[index]
                font_name = font[6:]
            else:
                font = group
                font_name = "GroupTest"

        vbox:
            text font_name
            text u"Hyūga Hinata" font font
            hbox:
                text "Charisma" font font
                null width 30
                text "1590" font font
            text u" & * + # %"  font font
            text u" & * + # %"  font font
            text u" ¼ ½  ¾"  font font
            text u"❤ ☀ ☆ ☂ ☻ ♞ ☯ ☭ ☢ € → ☎ ❄ ♫ ✂ ▷ ✇ ♎ ⇧ ☮ ⌘ 　 ー"  font font

    hbox:
        align (.5, .8)
        spacing 10
        textbutton "<--" action SetScreenVariable("index", (index - 1) % len(fonts)), SetScreenVariable("group", None)
        textbutton "Group Test" action SetScreenVariable("group", tisa_otm_adv)
        textbutton "-->" action SetScreenVariable("index", (index + 1) % len(fonts)), SetScreenVariable("group", None)

    textbutton "Close":
        align (.5, 1.0)
        action Hide("fonts"), Jump("mainscreen")
        keysym "mousedown_3"
