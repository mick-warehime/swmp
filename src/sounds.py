import pygame as pg
from typing import List, Dict
import os
import random

import data.input_output

LEVEL_START = 'level_start'

# Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']

EFFECTS_SOUNDS = {LEVEL_START: 'level_start.wav'}

SOUNDS_FROM_DATA = data.input_output.ability_sound_filenames()
SOUNDS_FROM_DATA |= data.input_output.npc_sound_filenames()


class SoundEffects(object):
    def __init__(self) -> None:
        self.zombie_hit_sounds: List[pg.mixer.Sound] = []
        self.player_hit_sounds: List[pg.mixer.Sound] = []
        self.zombie_moan_sounds: List[pg.mixer.Sound] = []
        self.all_sounds: Dict[str, pg.mixer.Sound] = {}

        # Sound loading
        game_folder = os.path.dirname(__file__)
        music_folder = os.path.join(game_folder, 'music')
        snd_folder = os.path.join(game_folder, 'snd')
        pg.mixer.music.load(os.path.join(music_folder, BG_MUSIC))
        for label, file_name in EFFECTS_SOUNDS.items():
            sound_path = os.path.join(snd_folder, file_name)
            sound = pg.mixer.Sound(sound_path)
            self.all_sounds[label] = sound
        for sound_file in PLAYER_HIT_SOUNDS:
            snd_path = os.path.join(snd_folder, sound_file)
            sound = pg.mixer.Sound(snd_path)
            self.player_hit_sounds.append(sound)
            self.all_sounds[sound_file] = sound

        for sound_file in SOUNDS_FROM_DATA:
            if sound_file in self.all_sounds:
                continue
            snd_path = os.path.join(snd_folder, sound_file)
            sound = pg.mixer.Sound(snd_path)
            self.all_sounds[sound_file] = sound


# Global sound effect object
effects = None


def initialize_sounds() -> None:
    global effects
    effects = SoundEffects()


def play(sound_name: str) -> None:
    effects.all_sounds[sound_name].play()


def player_hit_sound() -> None:
    random.choice(effects.player_hit_sounds).play()


def mob_moan_sound() -> None:
    random.choice(effects.zombie_moan_sounds).play()
