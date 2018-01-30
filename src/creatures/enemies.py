from typing import NamedTuple, List, Dict, Any

import pygame as pg
from pygame.math import Vector2, Vector3
from pygame.sprite import Group

import images
import settings
import sounds
from creatures.humanoids import Humanoid
from creatures.players import Player
from data.input_output import load_mod_data_kwargs
from effects import DropItem, PlaySound, DrawOnSurface, Effect, Condition, \
    EquipAndUseMod, RandomEventAtRate, Effects, Conditions, PlayRandomSound, \
    FaceAndPursueTarget, TargetClose, StopMotion
from model import Timer
from mods import Mod, ModData

MOB_SPEED = 100
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400

ModSpec = Dict[str, Dict[str, float]]
BehaviorData = Dict[str, Any]


class BaseEnemyData(NamedTuple):
    max_speed: int
    max_health: int
    hit_rect: pg.Rect
    image_file: str
    damage: int
    knockback: int
    conflict_group: Group
    drops_on_kill: str
    death_sound: str
    death_image: str
    behavior_dict: BehaviorData


# TODO(dvirk): Add tests for EnemyData
class EnemyData(BaseEnemyData):
    def __new__(cls, max_speed: float, max_health: int, hit_rect_width: int,
                hit_rect_height: int, image_file: str, damage: int,
                knockback: int = 0, conflict_group: Group = None,
                drops_on_kill: str = None,
                death_sound: str = None, death_image: str = None,
                behavior_dict: BehaviorData = None) -> BaseEnemyData:

        hit_rect = pg.Rect(0, 0, hit_rect_width, hit_rect_height)

        if behavior_dict is None:
            behavior_dict = {}

        return super().__new__(cls,  # type:ignore
                               max_speed, max_health, hit_rect, image_file,
                               damage, knockback, conflict_group,
                               drops_on_kill, death_sound, death_image,
                               behavior_dict)

    def add_quest_group(self, group: Group) -> BaseEnemyData:
        """Generate a new EnemyData with a given conflict group."""
        kwargs = self._asdict()
        kwargs['conflict_group'] = group
        return super().__new__(EnemyData, **kwargs)

    def replace(self, **kwargs: Any) -> BaseEnemyData:
        """Make a new EnemyData with specific parameters replaced.

        key word arguments must match BaseEnemyData.
        """
        new_kwargs = self._asdict()
        for k, v in kwargs.items():
            new_kwargs[k] = v
        return super().__new__(EnemyData, **new_kwargs)


passive_behavior = {
    Effects.STOP_MOTION: {'condition': {'label': Conditions.TARGET_CLOSE,
                                        'logical_not': True,
                                        'threshold': 500}}}
active_behavior = {
    Effects.RANDOM_SOUND: {'condition': {'label': Conditions.RANDOM_RATE,
                                         'rate': 0.2},
                           'sound_files': sounds.ZOMBIE_MOAN_SOUNDS},
    Effects.FACE_AND_PURSUE: {'condition': {'label': Conditions.TARGET_CLOSE,
                                            'threshold': 400}}}

behavior_dict = {'passive': passive_behavior,
                 'active': active_behavior}

mob_data = EnemyData(MOB_SPEED, MOB_HEALTH, 30, 30,  # type: ignore
                     images.MOB_IMG, MOB_DAMAGE, MOB_KNOCKBACK,
                     death_sound='splat-15.wav', death_image=images.SPLAT,
                     behavior_dict=behavior_dict)

quest_behavior = active_behavior.copy()
quest_behavior[Effects.EQUIP_AND_USE_MOD] = {
    'condition': {'label': Conditions.RANDOM_RATE, 'rate': 0.5},
    'mod': 'vomit'}
quest_behavior_dict = {'passive': passive_behavior,
                       'active': quest_behavior}

image_file = 'zombie_red.png'
quest_mob_data = mob_data.replace(max_speed=400, max_health=250,
                                  image_file=image_file, damage=20,
                                  knockback=40, drops_on_kill='pistol',
                                  behavior_dict=quest_behavior_dict)


class Behavior(dict):
    """Represents the possible behavior of an Enemy."""

    def __init__(self, behavior_dict: BehaviorData, player: Humanoid,
                 timer: Timer) -> None:

        for state, state_data in behavior_dict.items():
            state_behavior = {}
            for effect_label, effect_data in state_data.items():
                effect = self._effect_from_data(effect_data, effect_label,
                                                player)

                assert 'condition' in effect_data
                condition_data = effect_data['condition']
                condition = self._condition_from_data(condition_data, player,
                                                      timer)

                state_behavior[effect] = condition
            self[state] = state_behavior

    def _effect_from_data(self, effect_data: Dict, effect_label: str,
                          player: Player) -> Effect:
        if effect_label == Effects.EQUIP_AND_USE_MOD:
            mod_label = effect_data['mod']
            mod = Mod(ModData(**load_mod_data_kwargs(mod_label)))
            effect = EquipAndUseMod(mod)
        elif effect_label == Effects.RANDOM_SOUND:
            sound_files = effect_data['sound_files']
            effect = PlayRandomSound(sound_files)
        elif effect_label == Effects.FACE_AND_PURSUE:
            effect = FaceAndPursueTarget(player)
        elif effect_label == Effects.STOP_MOTION:
            effect = StopMotion()
        else:
            raise NotImplementedError(
                'Unrecognized effect label %s' % (effect_label,))
        return effect

    def _condition_from_data(self, condition_data: Dict, player: Player,
                             timer: Timer) -> Condition:
        condition_label = condition_data['label']
        if condition_label == Conditions.RANDOM_RATE:
            rate = condition_data['rate']
            condition = RandomEventAtRate(timer, rate)
        elif condition_label == Conditions.TARGET_CLOSE:
            threshold = condition_data['threshold']
            condition = TargetClose(player, threshold)
        else:
            raise NotImplementedError(
                'Unrecognized condition label %s' % (condition_label,))
        if 'logical_not' in condition_data:
            condition = ~ condition
        return condition


class Enemy(Humanoid):
    class_initialized = False
    _map_img: pg.Surface = None

    def __init__(self, pos: Vector2, player: Player, data: EnemyData) -> None:
        self._check_class_initialized()
        self._data = data
        super().__init__(data.hit_rect, pos, data.max_health)

        self.damage = data.damage
        self.knockback = data.knockback

        my_groups = [self._groups.all_sprites, self._groups.enemies]
        if data.conflict_group is not None:
            my_groups.append(data.conflict_group)

        pg.sprite.Sprite.__init__(self, my_groups)

        self._kill_effects: List[Effect] = []
        if data.drops_on_kill is not None:
            self._kill_effects.append(DropItem(data.drops_on_kill))
        if data.death_sound is not None:
            self._kill_effects.append(PlaySound(data.death_sound))
        if data.death_image is not None:
            image = images.get_image(data.death_image)
            self._kill_effects.append(DrawOnSurface(self._map_img, image))

        self.status.state = 'passive'

        self.behavior = Behavior(data.behavior_dict, player, self._timer)

        self.target = player

    def kill(self) -> None:
        for effect in self._kill_effects:
            effect.activate(self)
        super().kill()

    @classmethod
    def init_class(cls, map_img: pg.Surface) -> None:
        if not cls.class_initialized:
            cls._map_img = map_img
            cls.class_initialized = True

    @property
    def image(self) -> pg.Surface:
        base_image = images.get_image(self._data.image_file)
        image = pg.transform.rotate(base_image, self.motion.rot)

        if self.status.damaged:
            self._draw_health_bar(image, base_image.get_width())
        return image

    def _draw_health_bar(self, image: pg.Surface, full_width: int) -> None:
        col = self._health_bar_color()
        width = int(full_width * self.status.health / MOB_HEALTH)
        health_bar = pg.Rect(0, 0, width, 7)
        pg.draw.rect(image, col, health_bar)

    def update(self) -> None:
        target_disp = self.target.pos - self.pos
        if self._target_close(target_disp):
            self.status.state = 'active'
        else:
            self.status.state = 'passive'

        for effect, condition in self.behavior[self.status.state].items():
            if condition.check(self):
                effect.activate(self)

        self.motion.update()

        if self.status.is_dead:
            self.kill()

    def _check_class_initialized(self) -> None:
        super()._check_class_initialized()
        if not self.class_initialized:
            raise RuntimeError(
                'Enemy class must be initialized before an object'
                ' can be instantiated.')

    def _avoid_mobs(self) -> None:
        for mob in self._groups.enemies:
            if mob is self:
                continue
            dist = self.pos - mob.pos
            if 0 < dist.length() < AVOID_RADIUS:
                self.motion.acc += dist.normalize()

    def update_acc(self) -> None:
        self.motion.acc = Vector2(1, 0).rotate(-self.motion.rot)
        self._avoid_mobs()
        self.motion.acc.scale_to_length(self._data.max_speed)
        self.motion.acc += self.motion.vel * -1

    @staticmethod
    def _target_close(target_dist: Vector2) -> bool:
        return target_dist.length() < DETECT_RADIUS

    def _health_bar_color(self) -> tuple:
        health_fraction = float(self.status.health) / self.status.max_health
        if health_fraction > 0.5:
            frac = 2 * (1 - health_fraction)
            vec = Vector3(settings.GREEN) * frac
            vec += Vector3(settings.YELLOW) * (1 - frac)
            col = tuple(vec)
        else:
            frac = 2 * health_fraction
            vec = Vector3(settings.YELLOW) * frac
            vec += Vector3(settings.RED) * (1 - frac)
            col = tuple(vec)
        return col
