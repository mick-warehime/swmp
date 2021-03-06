import pygame as pg
from typing import Dict
from os import path
import random

from data import input_output

PLAYER_IMG = 'manBlue_gun.png'
LIGHT_MASK = "light_350_soft.png"
LITTLE_BULLET = 'little_bullet.png'
MUZZLE_FLASH1 = 'whitePuff15.png'
MUZZLE_FLASH2 = 'whitePuff16.png'
MUZZLE_FLASH3 = 'whitePuff17.png'
MUZZLE_FLASH4 = 'whitePuff18.png'
PARTYMEMBER1 = 'partymember1.png'
PARTYMEMBER2 = 'partymember2.png'
PARTYMEMBER3 = 'partymember3.png'

ALL_IMAGES = set(
    [PLAYER_IMG, MUZZLE_FLASH1, MUZZLE_FLASH2, MUZZLE_FLASH3, MUZZLE_FLASH4,
     LIGHT_MASK, LITTLE_BULLET, PARTYMEMBER1, PARTYMEMBER2, PARTYMEMBER3])
ALL_IMAGES = set(ALL_IMAGES)
ALL_IMAGES |= input_output.image_filenames()

IMPACTED_FONT = 'Impacted2.0.ttf'
ZOMBIE_FONT = 'ZOMBIE.TTF'
ALL_FONTS = [IMPACTED_FONT, ZOMBIE_FONT]


class Images(object):
    def __init__(self) -> None:
        self.images: Dict[str, pg.Surface] = {}
        self.fonts: Dict[str, str] = {}

        # load all the game files
        img_folder = path.dirname(__file__)
        img_folder = img_folder[:img_folder.index('/src/')] + '/src/img/'

        for img_name in ALL_IMAGES:
            img_path = path.join(img_folder, img_name)
            img = pg.image.load(img_path).convert_alpha()
            self.images[img_name] = img

        for font_name in ALL_FONTS:
            font_path = path.join(img_folder, font_name)
            self.fonts[font_name] = font_path


# global image object for loading image objects
images = None


def initialize_images() -> None:
    global images
    if not images:
        images = Images()


def get_image(image_name: str) -> pg.Surface:
    if not images:
        initialize_images()
    return images.images[image_name]


def get_font(font_name: str) -> str:
    if not images:
        initialize_images()
    return images.fonts[font_name]


def get_muzzle_flash() -> pg.Surface:
    all_flashes = [MUZZLE_FLASH1, MUZZLE_FLASH2,
                   MUZZLE_FLASH3, MUZZLE_FLASH4]
    random_flash = random.choice(all_flashes)
    return get_image(random_flash)


def party_member_image(member_number: int) -> pg.Surface:
    return get_image('partymember%d.png' % member_number)
