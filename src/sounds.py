import pygame as pg
from typing import List, Dict
import os
import random

# TODO - load sounds from JSON file -  issue#106
from tilemap import ObjectType, WEAPONS

ZOMBIE_HIT = 'zombie hit'
PLAYER_HIT = 'player hit'
ZOMBIE_MOAN = 'zombie moan'
WEAPON_FIRE = 'weapon'
LEVEL_START = 'level_start'
HEALTH_UP = 'health_up'
GUN_PICKUP = 'gun_pickup'

# Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav',
                      'zombie-roar-2.wav', 'zombie-roar-3.wav',
                      'zombie-roar-5.wav', 'zombie-roar-6.wav',
                      'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
WEAPON_SOUNDS = {ObjectType.PISTOL: ['pistol.wav'],
                 ObjectType.SHOTGUN: ['shotgun.wav']}
EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'gun_pickup.wav'}


class SoundEffects(object):
    def __init__(self) -> None:
        self.zombie_hit_sounds: List[pg.mixer.Sound] = []
        self.player_hit_sounds: List[pg.mixer.Sound] = []
        self.zombie_moan_sounds: List[pg.mixer.Sound] = []
        self.weapon_sounds: Dict[ObjectType, List[pg.mixer.Sound]] = {}
        self.effects_sounds: Dict[str, pg.mixer.Sound] = {}

        # Sound loading
        game_folder = os.path.dirname(__file__)
        music_folder = os.path.join(game_folder, 'music')
        snd_folder = os.path.join(game_folder, 'snd')
        pg.mixer.music.load(os.path.join(music_folder, BG_MUSIC))
        for label, file_name in EFFECTS_SOUNDS.items():
            sound_path = os.path.join(snd_folder, file_name)
            self.effects_sounds[label] = pg.mixer.Sound(sound_path)
        for weapon in WEAPONS:
            self.weapon_sounds[weapon] = []
            for sound_file in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(os.path.join(snd_folder, sound_file))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
        for sound_file in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(os.path.join(snd_folder, sound_file))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
        for sound_file in PLAYER_HIT_SOUNDS:
            snd_path = os.path.join(snd_folder, sound_file)
            self.player_hit_sounds.append(pg.mixer.Sound(snd_path))
        for sound_file in ZOMBIE_HIT_SOUNDS:
            snd_path = os.path.join(snd_folder, sound_file)
            self.zombie_hit_sounds.append(pg.mixer.Sound(snd_path))


# Global sound effect object
effects = None


def initialize_sounds() -> None:
    global effects
    effects = SoundEffects()


def play(sound_name: str) -> None:
    effects.effects_sounds[sound_name].play()


def fire_weapon_sound(weapon_type: ObjectType) -> None:
    sound = random.choice(effects.weapon_sounds[weapon_type])
    sound.play()


def spew_vomit_sound() -> None:
    effects.zombie_moan_sounds[2].play()


def player_hit_sound() -> None:
    random.choice(effects.player_hit_sounds).play()


def mob_hit_sound() -> None:
    random.choice(effects.zombie_hit_sounds).play()


def mob_moan_sound() -> None:
    random.choice(effects.zombie_moan_sounds).play()
