init python:
    class PyTSFX(_object):
        """ A Namespace for sfx related objects/functions
        There are four types of audio effects in the game: generic music, location specific music, ambiance sound and event specific sounds
        The corresponding channels are gamemusic, music, world and events/events2/sound respectively.
        Gamemusic and music are controlled by set_music, while the ambiance is handled by set_env.

        Gamemusic and music are exlusive. If the set_music is called by True/False the music is turned on/off. If the set_music receives a
        specific music file, it the gamemusic is paused and the given music is going to be played on the music channel. 
        The generic music is played from the content/sfx/music folder in a random order.

        The location specific ambiance sound is generated from the content/sfx/sound/world using the location as a file-prefix. The ambiance
        is selected when the player enters a location and looped till the location is not changed.
        """
        world_sfx = dict()
        world_env = None

        @staticmethod
        def load_world(key):
            dir = content_path("sfx", "sound", "world") # see register_channel("world"...) in initialization.rpy
            #cc = renpy.audio.audio.get_channel("world") TODO might be a better solution?
            #dir = renpy.loader.transfn(cc.file_prefix)
            PyTSFX.world_sfx[key] = [fn for fn in listfiles(dir) if fn.startswith(key) and check_music_extension(fn)]

        @staticmethod
        def queue_env():
            cc = renpy.audio.audio.get_channel("world")
            if cc.queue: # FIXME should not be necessary with the latest renpy
                #devlog.warn("Queuing World is called but it should not have been: %d" % len(cc.queue))
                return
            files = cc.get_playing()
            if files:
                # FIXME add queue entries?
                #files = [f[f.index(">"):] if f.startswith("<from") else f for f in files]
                if files.startswith("<from"):
                    files = files[files.index(">")+1:]
                renpy.music.queue(files, channel="world")
            else:
                if DEBUG_LOG:
                    devlog.warn("Queuing World Failed in env: %s" % PyTSFX.world_env)

        @staticmethod
        def set_env(key, fade=0):
            if PyTSFX.world_env == key:
                return
            if key is None:
                renpy.music.stop(channel="world", fadeout=fade)
            else:
                if key not in PyTSFX.world_sfx:
                    PyTSFX.load_world(key)
                files = PyTSFX.world_sfx[key]
                if files:
                    files = choice(files)
                    # TODO find out the length of the track in a better way...
                    renpy.music.play(files, channel="world")
                    #renpy.audio.renpysound.advance_time()
                    renpy.pause(.01) # let the 'world' run a bit, otherwise the duration won't be recognized...
                    start = renpy.music.get_duration(channel="world")
                    if DEBUG_LOG:
                        if start == 0: 
                            devlog.warn("Duration of %s (env-sound) is not recognized!" % files)
                        else:
                            devlog.warn("Duration of %s (env-sound) is recognized as %s!" % (files, start))
                    if start != 0:
                        start = time.time() % start
                        files = "<from %d>" % start + files
                    renpy.music.play(files, channel="world", fadein=fade, loop=False)
                    renpy.music.set_queue_empty_callback(PyTSFX.queue_env, channel="world")
                else:
                    renpy.music.stop(channel="world", fadeout=fade)
            PyTSFX.world_env = key

        @staticmethod
        def queue_music(fadein=0.2):
            cc = renpy.audio.audio.get_channel("gamemusic")
            if cc.queue: # FIXME should not be necessary with the latest renpy
                #devlog.warn("Queuing GameMusic is called but it should not have been: %d" % len(cc.queue))
                return
            dir = content_path("sfx", "music")
            files = [fn for fn in listfiles(dir) if check_music_extension(fn)]
            shuffle(files) # shuffle to prevent overuse of a single music
            renpy.music.queue(files, channel="gamemusic", fadein=fadein)

        @staticmethod
        def set_music(play):
            music = renpy.music
            cc = "gamemusic"
            if play is True:
                if not music.get_playing(channel=cc):
                    music.set_queue_empty_callback(PyTSFX.queue_music, channel=cc)
                music.set_pause(False, channel=cc)
            else:
                music.set_pause(True, channel=cc)
                if play is not False:
                    music.play(play)
                    return
                #renpy.music.set_pause(not play, channel="gamemusic")
            music.stop()

        @staticmethod
        def get_random_battle_track():
            # get a list of all battle tracks:
            folder = content_path("sfx", "music", "be")
            battle_tracks = [fn for fn in listfiles(folder) if check_music_extension(fn)]
            return os.path.join(folder, choice(battle_tracks))

        @staticmethod
        def purchase():
            renpy.sound.play("content/sfx/sound/events/purchase_1.ogg")