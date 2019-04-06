# The generic event for recapturing slaves that have escaped during look around actions.
#
label runaway_char_recapture(event):
    # Get the specific char
    $ char = pytfall.ra.get_look_around_char(event)

    hero.say "Wait! Is that?..{w} It is!"

    "You sneak forwards carefully, trying hard not to alert your prey.\nWhen you get close enough..."

    hero.say "Ah ha!{nw}"

    char.say "Ah! What? No!{nw}"

    "You grab [char.name]'s arm and hold on tightly as she tries to struggle."

    hero.say "I got you! You won't be escaping again."

    char.say "..."

    # Return the character to the player
    $ pytfall.ra.retrieve(char)

    return
