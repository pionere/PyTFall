init python:
    class LibraryBooks(_object):
        """Simple class to hold library texts and format them appropriately.
        """
        def __init__(self):
            self.books = {}
            self.book = None

        def __getitem__(self, book):
            if book in self.books:
                return self.books[book]
            else:
                return {}

        def create_new_book(self, name):
            self.books[name] = OrderedDict()
            self.book = name

        def create_main_header(self, header, skip="\n\n", **kwargs):
            """This creates a large header with the name of the book.

            By default uses a bold text.
            """
            if "style" not in kwargs:
                kwargs["style"] = "library_book_header_main"
            self.books[self.book][header + skip] = kwargs

        def create_sub_header(self, header, skip="\n\n", **kwargs):
            """This creates a large header with the name of the book.

            By default uses a bold text.
            """
            if "style" not in kwargs:
                kwargs["style"] = "library_book_header_sub"
            self.books[self.book][header + skip] = kwargs

        def add_text(self, text, skip="\n\n", **kwargs):
            """Plainly adds a body of text to the book.
            """
            if "style" not in kwargs:
                kwargs["style"] = "library_book_content"
            self.books[self.book][text + skip] = kwargs

    def create_lib_books():
        books = LibraryBooks()

        books.create_new_book("Books_1")
        books.create_main_header("World Geography")
        books.add_text("Mundiga, as both the central continent and the world itself are called, is the forth planet from its star.")
        books.add_text("Mundiga has a total of three continents, with the central continent of Mundiga hugging the equatorial regions, with the northern parts of the continent barely reaching the equivalent latitude of the Tropic of Cancer, while the southern coast reaches past the latitude of the Tropic of Capricorn equivilent, tapering down into a long peninsula, not dissimilar to the Horn of South America, culminating in one of the coldest parts of Mundiga, La Tierra De La Fuega, named for the volcanic activity and the magma plumes that periodically blast and scorch the land.")
        books.add_text("The second largest continent, Puerto, is located in a position analogous to Greenland, with roughly the same size and iciness as the island itself.  North and easterly to the central continent, the majority of Puerto is entombed under vast glaciers, with only a thin fringe of coast available for habitation.  The inhabitants of Puerto are primarily fishermen, striving to eck out enough food to allow for survival during the winter season, with perhaps enough of a surplus to trade in exchange for steel tools, weapons, and other necessary technology.")
        books.add_text("The smallest of the three continents is referred to as either Vilnis or as Aenstan.  As the inhabitants of Mundiga, by far the most populous of the continents, call it Vilnis, it shall henceforth in this discussion be called Vilnis.  Southeast of Puerto, and due west of Mundiga, Vilnis is less a continent than a collection of archipelagos, of which there are six, all located in a relatively small portion of the sea.  The six archipelagos circle a shallow inland sea, and are surrounded by deep undersea trenches.  Vilnis is home to a large number of warring tribes of various species, with a few tribes of degenerate elfin-kind warring with a large assortment of humans and humanoids, along with subhuman things, vast sea monsters, and raiding incursions from the land-based nations of Mundiga.  Currently, no one faction controls the Vilnis archipelagos, but the elves have established absolute dominance over one archipelago, with multiple enclaves on two others.  The humans, spread out over three different archipelagos, are currently on the run, but have thus far managed a very successful series of guerrilla actions against both the subhuman beastmen and the elfinkin.  The beastmen are present on all archipelagos except for the archipelago of Utrecht, over which the elves hold sway.  The maraudering sea monsters make travel between the archipelagos a risky business, though they tend to avoid the shallow, intra-archipelago waters.  The nations of Mundiga rely upon Vilnis for a wide assortment of raw materials and some crude products.  To establish control over those resources, and to prevent a neighboring nation from establishing hegemony over those same resources, the governments and mercantile guilds encourage and sponsor the warring tribes, providing weaponry, transport, and information, in exchange for raw material and slaves.")
        books.add_text("Mundiga was once the domain of three empires, known as Medius, Kam-Chou, and Friedwulfa, which engaged in a series of protracted military actions and outright wars until all three were exhausted to the point of collapse.  Once the three old empires collapsed, a legion of autonomous and semi-autonomous principalities, bishoprics, kingdoms, city-states, republics, tyrannies, petty empires, and other small nations spawned from the rotting carcasses of the old orders.  After a long period of anarchy and inter-state warring, a new series of nations congealed out of the wreckage.  Forming either seventeen or eighteen states, depending on the current political state of the nation of Bituous, which is undergoing a war of succession with the sub-region of High Clystra, the nations encompass all of Central, West, North and North-East Mundiga, while South-East and South Mundiga remain in the grasp of constant war, barbarism, and in the case of the far-southerly Tierra de Fuega, the inhabitence of Grendalkin, an absolutely savage species that desire nothing save destruction and pain.")

        books.create_new_book("Books_2")
        books.create_main_header("Ancient History, Part I")
        books.add_text("The very first group of people brought to the World of Mundiga were actually the inhabitants of Puerto, who are characterized by pale skin, thin faces, and either light brown, red, or blonde hair.  While not much is known about the history of the Puertese, it is known that they have descended from a group of servants of some empire who worshipped a Queen who was possibly divine or semi-divine in nature, as she was accorded religious and political power.  The Puertese refer to themselves, not as Puertese, but as Territes.  They speak a tongue that shares some words in common with the tongue of Crossgate, indicating a possible common origin.")
        books.add_text("The Puertese, as we shall call them, arrived approximatly 4000 years ago on the shores of frozen Puerto from wherever they had once lived, and promptly lost half their number to starvation and the low temperatures of the windswept northern continent.  After much labor, a crude collection of barrack-like structures and storage areas were erected out of quarried stone, as well as a meeting hall that occupied the center of the settlement.  A few hundred years later, after a few more arrivals increased the population and diversified the genetic stock, the Puertese abandoned the First City, presumably in the aftermath of a major outbreak of disease, and scattered into a large number of widely separated settlements, each of which were independent fiefdoms.  They created numerous alliances, based on the practice of trading brides to other settlements to reduce inbreeding, and warred and raided each other.  Eventually, approximently one and a half millenia after their arrival in Mundiga, they were united under Clan Chief Fritzjames the Third of the Four-Mast Settlement, who established the inter-clan High Moot that assembles biannually.  The present structure survived the next two and a half thousand years, and has betrayed no signs of change.")
        books.add_text("The next group to arrive in Crossgate arrived roughly five centuries after the arrival of the Puertese, and occupied the area around the Incognitimaris, the semi-landlocked sea that borders the Southwestern coast of Mundiga.  On the shore of the Incognitimaris, they established the city called \"Crucis Portus\", named for the greater than usual Thinny activity in the area, responsible for depositing the city's inhabitants into Mundiga.  We possess a fair amount of information about the builders of Crossgate due to a log kept by the leader of the newly deposited people, who was named Captain Scipius Macer Casca.  Captain Casca's log informs us that his people were once a legion of a mighty empire who, shortly after establishing a camp near the town of \"Pompeii\", were suddenly transported to Mundiga, along with their camp followers.  They eventually settled, established Crossgate, and began a century-long campaign of exploration and conquest across the Western coast of Mudiga.  Along their way, they fought and exterminated a tribe of blue-skinned humanoid savages known as the \"Nahvee\", two different groups of elves, whom they played off one another, known as the \"Ceelee\" and the \"Ughnceelee\", before finally halting after a long war of attrition with another group of humanoids, known as \"The Children of the Sun\".  Each time they conquered a tribe, they attempted to make slaves of the captives, with varying success.  The Nahvee slaves, for example, proved near impossible to control, which led to their subsequent extermination, and the extinction of the Nahvee on Mundiga.  The Elvenkin and Children slaves, on the other hand, became quite pliable after suitable training.  This processing of war prizes created the seed from which the slave trade economic empire that Crossgate is the center of would eventually grow.")
        books.add_text("A century later, the first Grendalkin war began, when a major incursion of Grendalkin (or, Grendalim as the Central Mundigan Peoples call them) came from the south.  Taken completely unaware, the majority of the South-Southwestern holdings of the \"Romansh\", as the inhabitants of Crossgate called themselves, were lost.  Eventually, after seven years of heavy contest over the lands to the southeast of Crossgate, the Grendalkin were halted, and turned back to their southern fastness, but the land was left ravaged for years to come.")
        books.add_text("Roughly fifty years after the first Grendalkin incursion, and two centuries after the Romansh under the self-styled High Consul Scipius Casca arrived on Mundiga, the line of House  Casca was extinguished after a coup led by Commander Pentus Aquilinus, who controlled Legios II and VI, as well as the Crossgate citizens militia and City Guard.  The new High Consul and his line adopted an expansionist policy, similar to the policies of the Cascas during the first century AE (Anno Exsilium).  This renewal of interest in conquest and colonization marks the end of a period of decay that began with the Pyrrhic conquest of the Children of the Sun, and as such, High Consul Aquilinus first turned his attentions to the restoration of hegemony over the western coastal regions of Mundiga, rebuilding the cities and towns that had been abandoned during the Grendalkin incursion.  Upon restoring the Northern Territories (recall, Crucis Portus was built on the Southwestern coast), the Romansh turned their eyes to the East, wishing to strengthen their hold over the Southwestern regions, which, since the incursion now seventy years previous, had been a sea of barbarianism.  Under the eyes of Secondus Aquilinus Supremus, the newly enthroned High Consul, the Legio IV and Legios Servoi V and VIII marched.  There, the professional soldiers of Crucis Portus and the slave soldiers alike distinguished themselves, and won much glory for their city and nation.  Over the next 35 years, each wave of conquest was followed by 2-5 years of construction, as new colonies were erected, and new cities rose in the new lands.")
        books.add_text("While the Romansh civilization flourished in Southwestern and Western Mundiga, while the Puertites still inhabited First City on the frozen coast, and while the Grendalkin fought pitched intertribal wars in the Tierra De La Fuega, a new group of successful arrivals was deposited in the shallow inner sea of Vilnis.  By linguistic and cultural evidence, as well as a few examples of shared histories imported from their old worlds, the new arrivals may have come from the same world as the Puertese, or at least a very similar one.  However, if this theory is correct, than the possibility exists that either the Puertese or the new arrivals, who dubbed themselves \"Eldridgans\", after the ship that carried them to their new world, also traveled through time as well as through space.  If so, than the power of the wormholes is much greater than we have hithero believed.  But, I digress.  The Eldrigans, who arrived in Mundiga during the year 237 AE, were the crew of a warship of great technology, with a steel hull and engines that burnt a kind of distilled oil, called \"deeceall\".  This initial group of settlers was both extraordinarily lucky and unlucky in their  composition and existing structure:  Coming with a strong, mobile fortress and an existent social structure helped the early settlement of the Philidelphian archipelago (the most eastern of the six archipelagos) immensely, as the group managed to avoid the pitfall of anarchy that was the doom of many groups of arrivals.  Unfortunately, the fact that the crew of the warship was entirely male presented a significant problem, as did the lack of stores on board (the ship had only been on a short voyage before its sudden transport, meaning that supplies of food, water, ammunition, medicine, and fuel were low).  The crew settled in a sheltered port, named Port Deliverance by the captain of the ship, and built a collection of wooden barracks surrounded by a palisade, as well as a crude dock for their warship.")
        books.add_text("For the next three years, the crew explored the Philidelphian archipelago, and, after discovering that the soil was hardy enough for agriculture, began planting seeds and growing food, while also using some of the native timber to construct coracles, which, along with the life-boats of the Eldridge, allowed them to fish in the shallow enclosed sea to the west.  Along with fertile soil, the Eldridgans discovered two springs on their archipelago, which ensured their survival.  The only real threats that the Eldridgans had at this point was disease, or possible civil unrest, beside the ticking time-bomb of having no females with which to create a viable population.")

        books.create_new_book("Books_3")
        books.create_main_header("Ancient History, Part II")
        books.add_text("Midway through 241 AE, a Romansh fishing boat, blown badly off-course, landed on the eastern-most atoll of the Philidelphian archipelago, where they were discovered by a pair of Philidelphian fishermen.  Fortunately, neither group decided to attack, as the Romansh fishermen were far too weary after battling the sea for a month, and the Philidelphians were far too relieved to discover that they were not alone on the planet.  The Romansh fishermen were brought to Port Deliverance, where they must have been impressed at the gradually decaying but still majestic Eldridge, which by this time was permanently docked.  While the language barrier proved to be a major problem in these initial communications, as well as with those to follow, the Romansh fishermen had no problem understanding the hospitality of their hosts, who fed them, repaired their boat, and gave them provisions for the return trip to Mundiga.  When they left, an Eldrigan accompanied them.  Second Lieutenant Thomas Salterizzo, picked for his officership, his resemblance to the fishermen, and the fact that the few words of Latin he knew were understood by the Romansh, accompanied the fishermen back across the sea, the city of Crucis Portus, where they arrived in the last week of 241.")
        books.add_text("After the Southwestern subjugation, Quartus Aquilinus Supremus, great-grandson of Pentus Aquilinus, declared the founding of the empire of Medius, with the capital in Crucis Portus.  This empire, spanning the entirety of Western and Southwestern Mundiga, had temporarily ended its expansionistic policy, turning instead its eyes inward, to matters economic and political.  This flourishing of culture brought forth some of the greatest artists, writers, and philosophers of the Early Period.  The Emperor Quartus was a good administrator, not a conqueror like his grandfather and father, and proved his right to rule by the reformation of the legal code, which led to greater rights to freemen, especially the soldier, artisan, and peasant classes, with only a minor curtailing of the rights of nobles and powerful merchants.  However, to appease these significant power blocs, Quartus instituted the idea of slavery as a criminal punishment, where previously slavery had been the sole province of conquered enemies and their descendents.")
        books.add_text("During the second year of his reign, Quartus received Lieutenant Salterizzo in Crucis Portus.  Having spent his month and a half in transit learning passable Romansh, Salterizzo managed to impress Quartus.  Of course, the fact that Salterizzo brought significant technological knowledge, which could propel the Romansh economic, civil, and war engine far forward, also helped greatly.  In exchange for this information, Quartus granted the Eldrigans an economic and political alliance, along with several shiploads of female slaves, and a wide selection of seeds for numerous crops, including cotton, maize, and rice.")
        books.add_text("This new alliance, the Romansh-Eldrigan Pact of 242 AE, proved to be a powerful force, far beyond what Quartus could have ever seen, as the firearms and ammunition technology brought by Salterizzo, along with the recipes for various alloys, the mechanics of crude electrical systems, and the blueprints of major pieces of civic architecture (such as aqueducts, sewers, and mass-produced housing) would prove significant to the Empire for years to come.")
        books.add_text("About twenty years before the Pact of 242, in the far southern region of Mundiga, on the very border of the Tierra De La Fuega, a new group of arrivals were deposited.  Unlike the Puertese, the Romansh, and the Eldrigans, these new arrivals were not humans of some stripe or another; nor were they were-humans, like the Children of the Sun, nor were they elves, like the Ceelee or the Ughnseelee.  In appearance, they resembled a cross between the tall, elongated, centuries extinct Nahvee, with the noticeable difference of having reptiloid rather than feline analogous features (tails, ears, eyes, noses, etc.); their heavily muscled arms and torsos resembled the Grendalkin, as did their taste for blood and the long, sharp claws that they use to spill the same upon the blasted sod.  These lizard-men, known in their own language as the Sse'ruk (translating directly to \"People\"), are colloquially and commonly known as the \"Sharp-Claws\".  The Sharp-Claws arrived on Mundiga in a possibly unique way; instead of being transported via thinny-made portals, the Sharp-Claws are native to our own universe, though not our world.  Descended from the crew of a wayward \"starship\", which to this day they claim allowed them to travel between the stars, their vessel was attacked by a dreadful creature known only as a \"Starfox\", who to this day is spoken of only in whispers.")

        books.create_new_book("Books_4")
        books.create_main_header("Medieval History, Part I")
        books.add_text("The unexpected arrival of the Sharp-Claws on Mundiga led to the halt of all Grendalkin raiding for the next several hundred years, until 497 AE, when the Grendalkin managed to break through Sharp-Claw territory via the village of Marrowak, and briefly raided a number of Romansh settlements in the southern reaches of the Median empire.  Fortunately, at this point, the Grendalkin and Sharp-Claws were both exhausted to the point where neither race had the ability to continue sustained combat, leading to the reaffirmation of imperial authority in Southwestern Mundiga, in the form of the construction of Tarquin's Wall, which sealed off the Southern peninsula from the rest of Mundiga.  The wall, along with the buffer state that the Sharp-Claw tribal territories were effectively turned into, kept the Grendalkin out of the civilized territories for the remainder of the time the Median Empire stood.")
        books.add_text("During the late third century AE, the seeds for the second of the three great empires were deposited in Mundiga.  In the Eastern Mountains, a portal deposited a small number of highly mobile warriors, who were proficient swordsmen and magnificent archers, and were primarily cavalry troops.  Hailing from a mighty army that had overrun a vast portion of their native world, these \"Mongols\" wasted no time in carving out a foothold.  Riding down from the mountain foothills where they found themselves, they conquered the three closest tribes, and began to take wives, find herds, and establish breeding stock.  After the passage of two generations, during which most of the old Mongol ways were preserved, adapted only enough to make survival in Mundiga more likely, the Mongols once again sallied forth, conquering another two tribes, and receiving tribute from numerous other tribes.  The Mongols followed this pattern over the next fifty years, until, in 361 AE, the Mongols successfully attacked and overran the city of Kitchkinet, a walled city that became the seat of power of the miniature empire, as the particularly forward-thinking chief, Besar, who led the conquest saw the benefit of a fixed strong point to fall back on.")
        books.add_text("Fifty-six years after the conquest of Kitchkinet, an increasingly less Mongol culture had coalesced around the city.  The old Mongol ways of tending to flocks and raiding neighbors were still in practice, but agriculture and long-term domiciles had become more common than the old nomadic ways, and a more formalized and rigorous government had begun to form.  The new culture inspired the chieftain, Han He, to take the next step, and formally declare a new empire, with himself at the head.  In 417 AE, the Kam-Chou imperial banner was raised in Kitchkinet for the first time.  The new emperor, to both cement his authority and to create a new avenue for trade, led an expedition to the eastern coast, capturing several towns along the way.  The expedition ended with the capture of the port town of A'ch'ak, which surrendered rather than be sacked.  This expedition increased the territory under the Kaminese banner by an additional half of what their old territory had been, proving the effectiveness of Han He as a leader, and granting him a much stronger power base to pass on to his heirs.")
        books.add_text("It was his grandson, Han Liu, who began to use A'ch'ak as more than a provincial capital and fishing hub, by dispatching ships full of explorers to look for new possible holdings across the seas.  Han Liu's father, Han Teban, had significantly expanded Kaminese territory to the north, but had not actually built much infrastructure, or done much with the new territory beyond extracting tribute.  While Kaminese explorers began to brave the Outer Sea, Han Liu began an ambitious project of laying roads across his territory, radiating from Kitchkinet in all directions, all the way to A'ch'ak and all the other major towns and cities in the empire.  These roads promoted mercantile activities, as well as increasing the centralization of the government, the speed of movement for soldiers and travelers, and the safety of travel throughout the empire.  All of these activities led to an increased yield of tax, as well as the imposition of a systematic code of law across all the imperial provinces.")
        books.add_text("The Kaminese explorers discovered much, traveling across the Outer Sea, including the continent of Puerto, and the western-most archipelago of Vilnis, the Min Archipelago, named for the captain of the ship that discovered it.  Some of their discoveries were positive, such as the Puertese, who, after utterly destroying the only attempt to conquer any part of the Puertese tribes (specifically, the Erebean Ha'Castle Tribe, located closest to the main continent), entered into a somewhat terse, but profitable, trading relationship with the Kaminese.  Others were markedly negative; many islets that were discovered offered no provisions or useful resources to exhausted crews, which meant unprofitable expeditions.  By far the most negative effect of the expeditions was the Kaminese's first encounter with the beastmen who lurked on Vilnis.")
        books.add_text("Since the establishment of the Pact of 242 AE, a strong bond had existed between the Eldrigans and the Romansh.  The Eldrigans got fresh blood and resources that weren't found in Vilnis from the Romansh, as well as news from the outside, and cultural exports.  The Romansh got technical know-how, an increasingly strong naval ally, and materials not found in Mundiga from the Eldrigans.  The Eldrigans used the security of this bond to colonize and take over the Utrecht and Kubo archipelagos, as well as to further expand their capital at Point Deliverance, and to begin the process of building an industrial base.  However, in the year 483 AE, the Eldrigans discovered that they were not alone in the islands - the two western-most archipelagos, the Min and Vater archipelagos were both heavily colonized by a race that made the Grendalkin appear near civilized in comparison:  The Trollocs.  Transported by the black spell of a magus who had sold her soul to an eldritch abomination from beyond the tapestry of the multiverse, the Trollocs were moved to pollute Mundiga with their filth, as they attempted to do in any world they were brought into.  Raving with an insatiable hunger, moved by malign intelligence, and filled with an insatiable lust, the Trollocs (or \"beastmen\") had already rendered the Min and Vater archipelagos into blackened wastelands in the few years that they'd been there.")

        books.create_new_book("Books_5")
        books.create_main_header("Medieval History, Part II")
        books.add_text("The Kaminese expedition, which had been decimated by their brief meeting with Trollocs while attempting a landing on Min archipelago on 459 AE, had returned to Eastern Mundiga, and had warned the Kaminese emperor of what lurked on the islands.  No further Kaminese expeditions were dispatched for the next seven hundred years.  This left the issue of the Trollocs to the Eldrigans and their Romansh allies; until the Romansh returned to Mundiga to deal with the Grendalkin incursion of 497 AE via the Sharp-Claw territory, and to build Tarquin's Wall.")
        books.add_text("In 484 AE, a year after the Eldrigans had first encountered the Trollocs on Vilnis, and twenty five years after the Kaminese expedition to the Min Archipelago barely escaped death in the first known human encounter with Trollocs on Mundiga, the Eldridgans dispatched an expedition to the Vater Archipelago, which was accompanied by a small detachment of Legio XII, in keeping with the Pact of 242.  The expedition, led by Commander Natchez Smith, consisted of eight Eldridgan sloops-of-war, each with a veteran crew of seventy-five sailors, ten petty officers, and three officers, along with a detachment of twenty marines per ship.  A single Romansh ship accompanied the Eldridgan fleet, the Singular, a troop carrier, on which the third century of Legio XII were billeted.  The centurion, Paulus Quina, kept a detailed log of the expedition, which is the sole source of written material concerning the expedition, as the logbooks of the Eldridgans have, somewhere in the last three millennia, been lost to time.  The logbook details the arrival at the ruins of the primitive stockade that the Eldridgans had established on the Vater Archipelago, before the Trollocs had attacked, and describes the landing procedures used when the Eldridgan marines and Romansh legionnaires stormed the beach, slaying roughly forty Trollocs, who had been taken unawares.  Sadly, at this point, both groups of soldiers grew lax, as the soldiers confidence grew to unmerited amounts following such a promising victory.  As a camp was established in the ruins of the old stockade, none of the soldiers (nor, apparently, Centurion Quina) noticed small knots of Trollocs gathering on a nearby hill.  In the dead of night, a horde of at least three thousand Trollocs rushed down the hill, and overran the stockade.  The Centurion and a collection of marines and legionnaires led a fighting retreat back to the landing boats, where they escaped to the sea, leaving behind 187 marine and legionnaire casualties.  Only a quarter of the force that had landed on the beach had survived that appalling night.  The Eldridgan sloops-of-war fended off attempts by Trollocs in boats, captured or otherwise, from following the fleeing survivors.  The cannonade would have done their exiled ancestors proud, as ball after ball of wrought iron sank boatloads of Trollocs, and grape-shot raked the seething mass of horrible bodies that capered on the beach.")
        books.add_text("While the Eldridgan navy reclaimed their honor, the battle illustrated the deficiencies in the marine detachments.  Of the 73 survivors, 61 had been Romansh legionnaires, battle hardened troops from the Sharp-Claw border, where they’d held of raids by the reptilian warriors, and from the eastern border of the empire, where they’d held off incursions by barbarian tribes, who had come to conquer new lands after fleeing before Han Teban’s armies.  On the other hand, the marines of the Eldridgan navy were more experienced in combating smugglers and pirates, experiences that helped very little during the Trolloc attack.  The Eldridgans, determined to fix this deficiency in the sudden awareness of the enemy that lurked so close to the home archipelagoes, purchased the services of two centuries of Romansh legionnaires to use as cadre in the training of a new armed force, the Eldridgan Home Army.  Centurion Quina and his surviving troops were rotated out, and sent back to the homeland for a period of recuperation and debriefing.  The fourth and fifth centuries of the Legio V were brought in, and established a training camp outside of Port Rigby, in the Kubo archipelago, to which volunteers from the civilian population, and transfers from the Navy and Marines were brought.")
        books.add_text("At the camp, the new Eldridgan recruits learned the traditional tightly disciplined fighting formations of the Legios, as well as the wide order skirmishing that had been added to doctrine, to deal with enemies while fighting in forests or in mountains.  The recruits were taught how to use the gladius and shield of the Legio, how to march, and how to use the muskets that had been developed from the technology the Eldridgans themselves had brought hundreds of years earlier.  The combination of close-order musketry, with the shield lines defending the musketeers against counter-attack had led to the dominating tactics of the Legio defending the Median Empire for the last two centuries against all comers. These tactics would prove to be the salvation of the Eldridgan people")
        books.add_text("In the tenth month of 484, the 1st Division of the new Eldridgan Home Army marched from their training grounds at Port Rigby, and boarded naval vessels, which took them to Lacey Island, in the Utrecht Archipelago, the closest point in Eldridgan technology to the infested Vater and Min archipelagoes.  There, on Lacey Island, the 1st Division, along with the finest stone masons and architects from both Crucis Portus and Port Deliverance, built Timothy’s Citadel and Naval Yards over the next four years, using stone quarried on Lacey as material.  The Citadel, rearing high over the island, was surrounded in multiple walls, with a thick central tower standing in the center of the base.  A fortified harbor, built within the second defensive line, provided a naval base within easy striking range of the Vater and Min archipelagoes.  Timothy’s Citadel, built to hold a massive garrison for decades under a state of siege, became the home of the vast majority of the Eldridgan armed forces, as well as a large body of allied troops in the form of the Legios IX, X, and XXIV, who the Emperor, Aetius III Aquilinus Supremus, had sent to ensure that Trollocs would not join the legion of threats that faced the Empire.")
        books.add_text("During the four years spent building the fortress on Lacey Island, the Home Army recruited heavily, and soon had an additional five fully trained divisions, each consisting of one thousand men.  The Navy also recruited heavily, and also began to train its crews with an eye for long range gunnery, extended combat operations against numerous enemies, and counter-boarder tactics, none of which had been used required against the primitive tribal fleets or pirates who had been the primary enemies that the Eldridgan Navy had engaged previously.")

        books.create_new_book("Books_6")
        books.create_main_header("Contemporary History, Part I")
        books.add_text("During the summer of 488, the remainder of the newly trained Home Army moved to join the garrison at Timothy’s Citadel, along with fifty Eldridgan ships, including three dreadnoughts, tasked with providing landing ships with heavy cannonades, to suppress Trolloc presence in the landing zones.  A fleet of eighty Romansh troop carriers accompanied the Eldridgan warships to Timothy’s Citadel, to carry the three Romansh Legios and five Eldridgan Divisions (the 1st Division’s mission was to maintain the garrison of Timothy’s Citadel) to the Vater Archipelago, as well as the light cannon attached to each century and battalion.  Also in the reprisal fleet were twenty civilian transport ships, which would act as the logistical support, hauling rations, medicines, ammunition, and other necessities to campaign.")
        books.add_text("The invasion fleet left Lacey Naval Docks the first day of autumn, 488.  Expecting no naval resistance, the entirety of the warship group was first in the order of march, followed by the troop ships, which were ahead of the logistical ships.  The voyage to the Vater Archipelago lasted eight days, as the fleet matched the speed of the logistical ships, so as to not outpace the necessities of campaign.  Upon arrival, the picket ships located a wide, sheltered beach with easy access to the interior of the main island.  The frigates, having been told the approximate locations of any Trollocs or constructions on the beach, formed a firing line, and began the bombardment of the Vater main island.  At this point, the first surprise of the campaign came in the form of return fire from one of the fortified structures.  The firearms and light artillery left on the beach by the casualties of the exploratory expedition had been adequate to give the beastmen a basic example of gun-casting; the composition of the remnant ammunition had also been discovered, allowing the beastmen access to crude and rather shoddy cannons that fired irregularly shaped lumps of pig-iron.  While these crude artillery pieces had a low rate of fire, and occurred rarely, they were completely unexpected, and led to a marked increase in wariness amongst the commanders of the expedition.")
        books.add_text("Despite the coastal artillery, the combined 39-gun bombardment cleared most of the resistance to a landing out in a brief time, allowing for the landing to begin.  Supported by light cannon fire from accompanying sloops, whose shallower drafts allowed a closer approach to the beach than the frigates were capable of, the veterans of Legio X Vaxillarus, accompanied by the 2nd and 4th Divisions of the Eldridgan Home Army, landed on the Vermin Beach.  Almost as soon as the legionnaires and soldiers had jumped from their landing ships into the shallows, Trollocs boiled out of the shattered ruins of the fortifications and buildings that had encrusted the beach like an infected scab. Charging towards the landing force, the Trollocs were met halfway by volley fire from the majority of the invaders, save for the shield-men who formed a defensive line in front of the musketeers, and the II Century of the Legio, who used rifled guns to pick off the Trollocs who directed the horde.")
        books.add_text("After the initial surge, the Trolloc forces retreated back into their fortifications, prompting another round of bombardment from the frigates.  Surprisingly, despite the proximity of the landing force to the fortifications and the relatively green nature of the sailors manning the cannons, very few friendly fire casualties were reported in the expedition’s reports.")
        books.add_text("Immediately following the second bombardment, the forces already on the land, totaling roughly three thousand, rushed up the beach and entered the fortifications, tunnels, buildings, and dugouts into which the Trollocs had retreated.  They were immediately followed by the second wave of soldiers, in the form of the 3rd and 6th Divisions, and the Legio XXIV.  The third wave, consisting of the 5th Division and Legio IX, moved up onto the beachhead, and began the process of fortifying the beachhead, as well as ensuring that the waterfront was completely clear of Trollocs.")
        books.add_text("Over the course of the next five weeks, the Legios and Divisions would learn a number of interesting facts, both about the habits of the Trollocs, and the nature of this war.  Amongst other things, the fact that the Vater main island was honeycombed by a vast network of tunnels and caves had been completely unknown to the High Command and it was this network that would be the main battlefield of the entire invasion.  The soldiers and legionnaires would also have a unique opportunity to understand the nature of Trollocs:  Created by a wizard goaded on by darkness greater than his ken, the first Trollocs were the horribly mutilated prisoners of the same magus, forcibly merged with demons and beasts of all sorts.  The Trollocs were defined from their very beginnings as beings of infinite hunger for suffering, and for flesh.  Trollocs delight in misery, and cause pain in any way within their capabilities.  While thuggish and small-minded, Trollocs possess an internal malice that manifests itself with a near genius in methods of cruelty unsurpassed in even the dankest slum of Crossgate or in the most infernal mind of the Grendalkin.  Amongst their many habits, Trollocs savor the taste of cooked human flesh, preferably prepared whilest the subject is alive and fully conscience.  Many soldiers, upon taking a Trolloc outpost, had the nauseating experience of discovering partially cooked and eaten comrades")
        books.add_text("The tunnels and caverns of Vater Island severely hampered the advance during the first week of combat, as the tightly confined battlefield made large-unit tactics, the common tactic of both Legios and Divisions, completely impossible to implement.  Soon, a modified plan of battle was devised, where squads (or, in the Legios, decios), would leapfrog up the tunnels in triples, with one squad using melee weapons and shields, the second using muskets, and the third either providing support or moving up to take the first squad’s place, at which point all squads change position.")
        books.add_text("This new method of organized, squad-based combat would lead the combined forces to victory, but only at a horrific cost. Squad after squad disappeared into the tunnels, never to reemerge from the darkness.  Hours of near constant combat turned into days, with the constantly echoing cries, howls, and gibbering of Trollocs audible at all times.")

        books.create_new_book("Books_7")
        books.create_main_header("Contemporary History, Part II")
        books.add_text("One week into the battle, and 18% of the total allied army was either killed or injured.  Two weeks in, and the Army was operating at 72% efficiency.  Fortunately, the rate of casualty decreased after the second week, as the surviving soldiers grew more adapt to fighting their tenacious enemy on his home ground.  By the end of the campaign, at the beginning of Week Five, 57% of the soldiers who had arrived on the Vater Archipelago were still capable of combat operations. Trolloc casualties are not known with any degree of certainty, as the Beastmen are cannibals and frequently ate their fallen, but the number of Trollocs estimated to have fallen over the War of Five Weeks is placed somewhere around seven thousand, nearly twice the number of allied casualties.")
        books.add_text("During the incursion, the naval fleet did not sit idle:  Besides providing logistical support by shipping supplies to the land forces from Port Deliverance and Timothy’s Citadel, the flotilla also blockaded the Vater main island and provided artillery bombardment of any surface level Trolloc positions.  The blockade proved necessary twice over, once as a Trolloc fleet from the Min Archipelago attempted to make landfall on Vater with reinforcements, twice as most of the surviving Vater Trollocs attempted to make a break-out during the last days of the operation.  The containment most involved shelling the Trollocs, and herding the fleeing rabble back towards the pursuing soldiers.  The battle with the Min Trollocs proved the naval superiority of the Eldridgan sailors, as fewer than twenty allied casualties were sustained and no ships were lost, while the Trollocs lost three sloop analogues and most of their crews, as well as losing hundreds of troops to drowning when the suddenly unguarded troop carriers came under fire.")
        books.add_text("After weeks of battle, the Trollocs were finally winkled out from their tunnels; while the continued existence of Trollocs throughout Vilnis indicates that this victory was by no means absolute, a strong victory was definently won.  The victorious soldiers took no prisoners, killing any Trolloc found; during those last days, the howling, near insane faces of the five thousand surviving troops seemed to hold more in common with their foes than with their fellow humans.  The few Trollocs who survived the cleansing of Vater did so by hiding deep in the shadowed recesses of the tunnels under the island.")
        books.add_text("Upon victory, the cratered wasteland that was Vater was set ablaze once more, by the firebombing of the allied forces.  Naphtha was poured into the tunnels and set ablaze, with the intent to suffocate any survivors still in the Deeps.  The entrances to the tunnels were than sealed with the explosive collapse of the surface entrances that the allies had found.  With this final act of destruction, the survivors left with as many of their dead as they could recover.")
        books.add_text("Upon arriving at Timothy’s Citadel a week later, the survivors were given a hero’s welcome, before the grim task of reorganizing the armies could begin.  The Romansh legios opted not to merge, as each still retained their Legio Standard.  However, until recruitment could begin, the Legios IX and XXIV effectively became the seventh, tenth, and eleventh centuries of the Legio X Vaxillarus.  The Eldridgan divisions were hard-hit, especially the 3rd and 4th Divisions.  After some administrative reshuffling, the Eldridgan Home Army shrank from six Divisions to four slightly over-strength Divisions.")
        books.add_text("With the retrospect of those hundreds of years separated from the actual events of the Vater Campaign and the soldiers who fought within those hellish tunnels, the Respected Readers of this tract understand that the almost inevitable byproducts of the weeks-long tunnel battle included the severe mental unbalancing of many soldiers, as well as the mana poisoning of many more, so adverse to human norms is prolonged exposure to the fundamental wrongness that is the Trolloc beastman.  However, our forbearers had no understanding of these manners, and thus were completely mystified by the wave of crime and suffering that followed the returning troops home.  The newly hardened soldiers of the Eldridgan Home Army and Navy had never seen battle on such scale before, and thus were more adversely affected.  Dementia and violence against self and others became common amongst the garrison of Timothy’s Citadel, and in the shipyards of Port Deliverance and Lacey Island.  Similar spikes in incident reports from the Civil Guard archives recovered from the Deliverance ruins show a distinct relationship between the return of troops to homes and outposts, and acts of madness.  More disturbingly even now, a distinct minority of the troops, notably the ones who had been most involved during the mop-up, became corrupted by the evil processes and spells that had first birthed the Trollocs, and had transported them to Mundiga.  Those familiar with the Halfman will know the fear of the eyeless face and the ghastly speeds that they can achieve when stalking their prey.  For a brief time in the winter of 488, an active insurgency of Halfmen ripped through the garrison, as men disappeared while on guard duty, and were found in empty corridors days later.  Eventually, the afflicted soldiers were put down, and a brief lull in combat fell over the Vilnis archipelagoes.")
        books.add_text("Almost as soon as the temporary, brief peace fell over the fractured continent, the Legios were summoned back at the order of the newly enthroned emperor, Aetius IV Aquilinus Supremus, who had succeeded his father after a bad sickness had weakened the once-mighty ruler to debility.  As the Legios returned, the remnants of Legios IX and XXIV were put on recruitment duty, while the Legio X Vaxillarus was redeployed to the southwestern provinces along with Legios III, IV, VII, XI, and XIV, to counter the tenacious presence of the Grendalkin invaders.")
        books.add_text("Two years previous, the Grendalkin had thrust through the Sharp-Claw territories, scattering the tribal forces that had held them at bay over the last three hundred years.  While the advance into the Median provinces was checked at the River of Lavinia by the Legios XX and XXII, in addition to a body of Sharp-Claw survivors, the Grendalkin threat was not truly responded to until 489. Unlike the short, intense Battle of Vater Deeps, the Second Grendalkin incursion was marked by a long series of skirmishes, as raiding parties of Grendalkin were repulsed back across the Lavinia, punctuated by massive rushes of Grendalkin breaking through the lines, before being forced back across the waters.  Despite the length of time involved, the Median Empire was almost dismissive of the struggle as a whole; during the long hiatus from the rest of the world, the Sharp-Claws and Grendalkin had fought a bitter, protracted war of attrition, wearying both sides.  The might of the Grendalkin was almost expended by the time the Sharp-Claw village of Marrowak fell, and the first Grendalkin crossed the Lavinia.  As such, after the initial panic, more effort was put into the construction of a wall to remove the threat of both Sharp-Claw and Grendalkin.  Tarquin’s Wall, named for Legate Halibur Tarquinus Davit, who commanded the Imperial forces throughout the struggle, remains one of the most mammoth building projects ever completed.  Stretching from coast to coast, the Wall effectively sealed the southern peninsula and Tierra Del Fuego away from the rest of Mundiga for centuries.  Built using the principles first introduced by the Eldridgans, reinforced by iron inserts, constructed of hewn granite with inner fill, the Wall alone is formidable; its strength was further reinforced by the tribal magics cast upon it by the surviving Sharp-Claws, who of necessity had allied themselves with the Medians in the effort, as well as numerous cannon emplacements and garrisons.  Built a mile back from the shores of the River Lavinia, a blasted kill zone in front of the gargantuan fortification offered no shelter for encroaching Grendalkin.")
        books.add_text("As the Wall’s construction concluded, the Grendalkin, weary and exhausted of war, departed civilized lands for the last time, returning to their Tierra and the nightmares of children, where they live even today.  The Sharp-Claws, decimated in numbers but partially civilized and allied to the Medians, were gifted with a wide fief in the Eastern Plains, on the border of the Empire, in exchange for fealty to the Emperor.")

        books.create_new_book("Books_8")
        books.create_main_header("The Concept of Elements")
        books.add_text("All magical manifestations in the world originate from one or more arcane sources, known as elements. Presumably, every element has its own endless dimension filled with tremendous powers and mysterious creatures, but only a small part of them capable to reach Mundiga. Eight elements are known at this point, although there are evidences that more, weaker ones may exist. As practice shows, elements are connected, weakening and strengthening each other.")
        books.add_text("Fire. The wildest of all elements bringing a change that can never be undone. In a blink of an eye, it can turn any obstacle to dust leaving nothing but scorched earth in its path. In unskilled hands, it can be more dangerous to its wielders than to their enemies.")
        books.add_text("Water. The most mysterious among the elements. Hiding it twisted and destructive nature under the calm surface. Leaving behind only rumble and bodies as proof of its fatal capabilities.")
        books.add_text("Air. The most agile of the elements, utilizing its transparency and omnipresence to maximum. Being able to strike swiftly and undetected, in capable hands this element does not give opponents much time to defend themselves.")
        books.add_text("Earth. The slowest and sturdiest among the elements. Known for sacrificing speed in exchange for overwhelming destructive power. Unlike other elements that leave evidence of their devastating acts, earth is capable of literally burying the truth.")
        books.add_text("Electricity. The most unstable and transient among the elements. Has control over magnetic and particle-based fields and beams that are deadly but cannot exist for a long time.")
        books.add_text("Ice. The most solid and unchangeable among the elements. Can absorb energy from the environment, strengthening itself and creating ice formations out of nowhere.")
        books.add_text("Light and Darkness The two elements born from desires, thoughts and deeds. Light nests itself inside everyone souls, gaining its force from good acts and pure thoughts. Darkness fuels itself from anger, impure thoughts and evil acts, dwelling deep in everyone’s soul, patiently expanding, slowly consuming one's soul.")
        books.add_text("Every creature, even undead or artificially created one, may have so-called elemental affinity with one or, rarely, more elements. It brings various unique advantages and disadvantages in magic offence and defense. Those who don't have said affinity are called Neutral. It is one of the most popular options among warriors that do not rely on use of magic. It will ensure some degree of resistance from all elements, but on other hand this is possibly the worst choice for any magic user since it greatly weakens all spells.")
        books.add_text("When preparing for battle, one must consider possible weaknesses and strengths of the opponent. Meetings with powerful creatures resistant, immune or even absorbing specific elements are not uncommon. Although the same is true for common weapons and exotic things like poisons, so the best bet is to have as many ways to damage the enemy as possible.")
        return books

label academy_town:
    $ iam.enter_location(badtraits=["Adventurous", "Slime", "Monster"], goodtraits=["Curious"],
                        has_tags=["girlmeets", "schoolgirl"], coords=[[.1, .55], [.45, .64], [.86, .65]])
    # Music
    if not global_flags.has_flag("keep_playing_music"):
        $ PyTFallStatic.play_music("library", fadein=.5)
    $ global_flags.del_flag("keep_playing_music")

    python:
        # Build the actions
        if pytfall.world_actions.location("academy_town"):
            pytfall.world_actions.meet_girls()
            pytfall.world_actions.add("library_matrix", "Read the books", Jump("library_read_matrix"))
            pytfall.world_actions.add("eleven_dialogue", "Find Eleven", Jump("library_eleven_dialogue"))
            pytfall.world_actions.finish()

    scene bg academy_town
    with dissolve
    if not global_flags.has_flag('visited_library'):
        $ global_flags.set_flag('visited_library')
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

    show screen academy_town

    $ pytfall.world_quests.run_quests("auto")
    $ pytfall.world_events.run_events("auto")

    while 1:
        $ result = ui.interact()

        if result[0] == 'jump':
            $ iam.start_int(result[1], img=result[1].show("girlmeets", "schoolgirl", "indoors", exclude=["swimsuit", "wildness", "beach", "pool", "urban", "stage", "onsen"], type="reduce", label_cache=True, gm_mode=True))

        elif result == ['control', 'return']:
            hide screen academy_town
            jump city

label library_eleven_dialogue:
    hide screen academy_town
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
            jump eleven_menu
        "Sell old books" if has_items("Old Books", hero, equipped=False) and global_flags.flag('player_knows_about_eleven_jobs'):
            $ money = has_items("Old Books", hero, equipped=False)*15
            e "{b}I appreciate your concern about the archive collection, [hero.name]. [money] coins should be sufficient.{/b}"
            $ hero.add_money(money, reason="Items")
            $ hero.remove_item("Old Books", has_items("Old Books", hero, equipped=False))
            $ del money
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
            e "{b}I am authorized to buy books to expand the archive collection. The archive doesn't need common books, but you may bring any unusual and rare ones.{/b}"
            $ golem.override_portrait("portrait", "confident")
            e "{b}More importantly, I was entrusted with the task to clear the city from forbidden propaganda. After the war, a lot of leaflets made by rebels left in the city. I am authorized to pay for any prohibited leaflets, which will be destroyed soon after that.{/b}"
            "At these words, his eyes flash brightly, and you can sense his hostility - not towards you, but towards the rebels."
            $ golem.override_portrait("portrait", "angry")
            e "{b}Handle them with care. Once you find one, bring it to me immediately. Otherwise, you will be suspected of treason.{/b}"
            $ golem.override_portrait("portrait", "indifferent")
            if not global_flags.flag('player_knows_about_eleven_jobs'):
                $ global_flags.set_flag('player_knows_about_eleven_jobs')
            jump eleven_menu
        "Leave him be":
            "You step away, and the light in his eyes dims."
            hide npc with dissolve
            $ global_flags.set_flag("keep_playing_music")
            $ del e, golem
            jump academy_town

screen academy_town():
    use top_stripe(True)
    use location_actions("academy_town")

    if iam.show_girls:
        use interactions_meet
    else:
        $ img = im.Scale("content/gfx/interface/icons/library_study.png", 80, 80)
        imagebutton:
            pos (720, 340)
            idle img
            hover PyTGFX.bright_img(img, .15)
            action [Hide("academy_town"), Jump("mc_action_library_study")]
            tooltip "Study"

label library_read_matrix:
    hide screen academy_town
    scene bg academy_town

    python:
        if not hasattr(store, "lib_data"):
            lib_books = create_lib_books()
            lib_data = "code/locations/library/coordinates.json"
            with open(renpy.loader.transfn(lib_data)) as f:
                lib_data = json.load(f)
            del f

    call screen poly_matrix(lib_data, show_exit_button=(1.0, 1.0))
    $ setattr(config, "mouse", None)
    if not _return:
        $ del lib_data, lib_books
        $ global_flags.set_flag("keep_playing_music") 
        jump academy_town
    else:
        call screen library_show_text(lib_books[_return])
        with dissolve

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
                for i in book:
                    add Text(i, **book[i])
        vbar value YScrollValue("vp")

    textbutton "Enough with it":
        style "pb_button"
        align (1.0, 1.0)
        action (Hide("library_show_text", transition=dissolve), Jump("library_read_matrix"))

label mc_action_library_study:
    if not global_flags.flag('studied_library'):
        $ global_flags.set_flag('studied_library')
        "Here you can study various topics with your team."
        extend "The entrance fee is 250 Gold per person."
        "The effectiveness of the session is depending on the size of the team."
        extend "The larger the group, the more you can learn."
        "Be aware that certain personalities do not fit here and might disrupt the group."

        menu:
            "Do you want to leave?"

            "Yes":
                $ global_flags.set_flag("keep_playing_music")
                jump academy_town
            "No":
                $ pass

    if hero.has_flag("dnd_study_at_library"):
        "You already studied at the library today."
        $ global_flags.set_flag("keep_playing_music")
        jump academy_town

    if hero.gold < len(hero.team) * 250:
        if len(hero.team) > 1:
            "You don't have enough gold to cover the fees for of your team."
        else:
            "You don't have enough gold to cover the fee."

        "The fee is 250 Gold per person."
        $ global_flags.set_flag("keep_playing_music")
        jump academy_town

    if not hero.team.take_ap(1):
        if len(hero.team) > 1:
            "Unfortunately, your team is too tired at the moment. Maybe another time."
        else:
            "You don't have Action Points left. Try again tomorrow."

        "Each member of your party must have 1 AP."
        $ global_flags.set_flag("keep_playing_music")
        jump academy_town

    $ hero.take_money(len(hero.team)*250, "Library Fee")
    $ hero.set_flag("dnd_study_at_library")

    call screen library_study
    $ result = _return
    if result:
        $ temp = result[1]
        if len(hero.team) > 1:
            $ members = list(member for member in hero.team if (member != hero))
            if len(members) == 1:
                show expression members[0].get_vnsprite() at center as temp1
                with dissolve
            else:
                show expression members[0].get_vnsprite() at left as temp1
                show expression members[1].get_vnsprite() at right as temp2
                with dissolve
            $ del members
            "You're studying [temp] with your team."
        else:
            "You're studying [temp]."
        $ del temp

        python hide:
            stat_skill = result[2]
            group = hero.team
            mod = len(group)
            misfits = [m for m in group if "Adventurous" in m.traits or "Aggressive" in m.traits]
            misfit = None
            if misfits and dice(len(misfits)*30):
                misfit = choice(misfits)
                narrator("%s could not concentrate and kept disturbing the others." % misfit.name)
                mod /= 2
            for member in group:
                if member in misfits:
                    member.gfx_mod_stat("joy", -randint(2, 4))
                    if member == misfit:
                        continue
                member.gfx_mod_exp(exp_reward(member, group, exp_mod=.5*mod))
                if is_skill(stat_skill):
                    member.gfx_mod_skill(stat_skill, 1, randint(0, mod))
                else:
                    member.gfx_mod_stat(stat_skill, randint(0, mod))
                if member != hero:
                    member.gfx_mod_stat("disposition", randint(1, 2))
                    member.gfx_mod_stat("affection", affection_reward(member, .1))
    else:
        if len(hero.team) > 1:
            "You could not agree on what to study. What a waste of time (and gold)."
        else:
            "You cound not find anything interesting..."
    $ del result
    $ global_flags.set_flag("keep_playing_music")
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
