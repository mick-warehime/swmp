import pygame as pg
from typing import Dict
from os import path
import random

PLAYER_IMG = 'manBlue_gun.png'
BULLET_IMG = 'bullet.png'
MOB_IMG = 'zombie1_hold.png'
QMOB_IMG = 'zombie_red.png'
SPLAT = 'splat green.png'
MUZZLE_FLASH1 = 'whitePuff15.png'
MUZZLE_FLASH2 = 'whitePuff16.png'
MUZZLE_FLASH3 = 'whitePuff17.png'
MUZZLE_FLASH4 = 'whitePuff18.png'
LIGHT_MASK = "light_350_soft.png"
HEALTH_PACK = 'health_pack.png'
SHOTGUN = 'obj_shotgun.png'
PISTOL = 'obj_pistol.png'
SHOTGUN_MOD = 'mod_shotgun.png'
PISTOL_MOD = 'mod_pistol.png'
WAYPOINT_IMG = 'waypoint.png'

ALL_IMAGES = [PLAYER_IMG, BULLET_IMG, MOB_IMG, SPLAT,
              MUZZLE_FLASH1, MUZZLE_FLASH2, MUZZLE_FLASH3,
              MUZZLE_FLASH4, LIGHT_MASK, HEALTH_PACK, SHOTGUN,
              SHOTGUN_MOD, PISTOL, PISTOL_MOD, QMOB_IMG,
              WAYPOINT_IMG]

IMPACTED_FONT = 'Impacted2.0.ttf'
ZOMBIE_FONT = 'ZOMBIE.TTF'
ALL_FONTS = [IMPACTED_FONT, ZOMBIE_FONT]


class Images(object):
    def __init__(self) -> None:
        self.images: Dict[str, pg.Surface] = {}
        self.fonts: Dict[str, str] = {}

        # load all the game files
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
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
    return images.images[image_name]


def get_font(font_name: str) -> str:
    return images.fonts[font_name]


def get_muzzle_flash() -> pg.Surface:
    all_flashes = [MUZZLE_FLASH1, MUZZLE_FLASH2,
                   MUZZLE_FLASH3, MUZZLE_FLASH4]
    random_flash = random.choice(all_flashes)
    return get_image(random_flash)


def get_item_image(item_name: str) -> pg.Surface:
    if item_name == 'health':
        return get_image(HEALTH_PACK)
    elif item_name == 'shotgun':
        return get_image(SHOTGUN)
    elif item_name == 'pistol':
        return get_image(PISTOL)

    raise ValueError("failure loading image: %s" % item_name)
