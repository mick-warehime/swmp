import pygame as pg
from typing import List, Dict
import os
import settings
import random

ZOMBIE_HIT = 'zombie hit'
PLAYER_HIT = 'player hit'
ZOMBIE_MOAN = 'zombie moan'
WEAPON_FIRE = 'weapon'
LEVEL_START = 'level_start'
HEALTH_UP = 'health_up'
GUN_PICKUP = 'gun_pickup'


class SoundEffects(object):
    def __init__(self) -> None:
        self.zombie_hit_sounds: List[pg.mixer.Sound] = []
        self.player_hit_sounds: List[pg.mixer.Sound] = []
        self.zombie_moan_sounds: List[pg.mixer.Sound] = []
        self.weapon_sounds: Dict[str, List[pg.mixer.Sound]] = {}
        self.effects_sounds: Dict[str, pg.mixer.Sound] = {}

        # Sound loading
        music_folder = 'music'
        snd_folder = 'snd'
        pg.mixer.music.load(os.path.join(music_folder, settings.BG_MUSIC))
        for label, file_name in settings.EFFECTS_SOUNDS.items():
            sound_path = os.path.join(snd_folder, file_name)
            self.effects_sounds[label] = pg.mixer.Sound(sound_path)
        for weapon in settings.WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for sound_file in settings.WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(os.path.join(snd_folder, sound_file))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
        for sound_file in settings.ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(os.path.join(snd_folder, sound_file))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
        for sound_file in settings.PLAYER_HIT_SOUNDS:
            snd_path = os.path.join(snd_folder, sound_file)
            self.player_hit_sounds.append(pg.mixer.Sound(snd_path))
        for sound_file in settings.ZOMBIE_HIT_SOUNDS:
            snd_path = os.path.join(snd_folder, sound_file)
            self.zombie_hit_sounds.append(pg.mixer.Sound(snd_path))


# Global sound effect object
effects = None


def initialize_sounds() -> None:
    global effects
    effects = SoundEffects()


def play(sound_name: str) -> None:
    effects.effects_sounds[sound_name].play()


def fire_weapon_sound(weapon_name: str) -> None:
    sound = random.choice(effects.weapon_sounds[weapon_name])
    sound.play()


def player_hit_sound() -> None:
    random.choice(effects.player_hit_sounds).play()


def mob_hit_sound() -> None:
    random.choice(effects.zombie_hit_sounds).play()


def mob_moan_sound() -> None:
    random.choice(effects.zombie_moan_sounds).play()
