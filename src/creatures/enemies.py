from typing import NamedTuple, Dict, Any

import pygame as pg
from pygame.math import Vector2, Vector3
from pygame.sprite import Group

import images
import settings
from creatures.humanoids import Humanoid
from creatures.players import Player
from data.input_output import load_mod_data_kwargs, load_npc_data_kwargs
from effects import DropItem, PlaySound, DrawOnSurface, Effect, Condition, \
    EquipAndUseMod, RandomEventAtRate, Effects, Conditions, PlayRandomSound, \
    FaceAndPursueTarget, TargetClose, StopMotion, IsDead, AlwaysTrue, Kill, \
    EnergyNotFull
from model import Timer
from mods import Mod, ModData

AVOID_RADIUS = 50
DETECT_RADIUS = 400

BehaviorData = Dict[str, Any]


class BaseEnemyData(NamedTuple):
    max_speed: int
    max_health: int
    hit_rect: pg.Rect
    image_file: str
    damage: int
    knockback: int
    conflict_group: Group
    behavior_dict: BehaviorData


class EnemyData(BaseEnemyData):
    def __new__(cls, max_speed: float, max_health: int, hit_rect_width: int,
                hit_rect_height: int, image_file: str, damage: int,
                knockback: int = 0, conflict_group: Group = None,
                behavior: BehaviorData = None) -> BaseEnemyData:

        hit_rect = pg.Rect(0, 0, hit_rect_width, hit_rect_height)

        if behavior is None:
            behavior = {}

        return super().__new__(cls,  # type:ignore
                               max_speed, max_health, hit_rect, image_file,
                               damage, knockback, conflict_group,
                               behavior)

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


mob_data = EnemyData(**load_npc_data_kwargs('mob'))
quest_mob_data = EnemyData(**load_npc_data_kwargs('quest_mob'))


class Behavior(object):
    """Represents the possible behavior of an Enemy."""

    def __init__(self, behavior_dict: BehaviorData, player: Humanoid,
                 timer: Timer, map_image: pg.Surface) -> None:

        self.default_state: Condition = None
        self._state_condition_values: Dict[str, Dict[Condition, int]] = {}
        self._state_effects_conditions: Dict[str, Dict[Effect, Any]] = {}

        self._set_state_condition_values(behavior_dict, player, timer)
        self._set_state_effects_conditions(behavior_dict, player, timer,
                                           map_image)

    def determine_state(self, humanoid: Humanoid) -> str:

        current_state = self.default_state
        highest_priority = 0

        for state, state_conditions in self._state_condition_values.items():
            priority = 0
            for cond, value in state_conditions.items():
                if cond.check(humanoid):
                    priority += value
            if priority > highest_priority:
                highest_priority = priority
                current_state = state

        return current_state

    def do_state_behavior(self, humanoid: Humanoid) -> None:

        state = humanoid.status.state
        for effect, condition in self._state_effects_conditions[state].items():
            if condition.check(humanoid):
                effect.activate(humanoid)

    def _set_state_effects_conditions(self, behavior_dict: BehaviorData,
                                      player: Player,
                                      timer: Timer,
                                      map_image: pg.Surface) -> None:

        for state, state_data in behavior_dict.items():
            effect_datas = state_data['effects']
            state_behavior = {}
            for effect_label, effect_data in effect_datas.items():
                effect = self._effect_from_data(effect_data, effect_label,
                                                player, map_image)

                if effect_data is not None and 'conditions' in effect_data:
                    condition = None
                    for cond_data in effect_data['conditions']:
                        new_cond = self._condition_from_data(cond_data, player,
                                                             timer)
                        if condition is None:
                            condition = new_cond
                        else:
                            condition &= new_cond
                else:
                    condition = AlwaysTrue()

                state_behavior[effect] = condition
            self._state_effects_conditions[state] = state_behavior

    def _set_state_condition_values(self, behavior_dict: BehaviorData,
                                    player: Player, timer: Timer) -> None:
        for state, state_data in behavior_dict.items():

            assert 'conditions' in state_data

            conditions_list = state_data['conditions']
            if 'default' in conditions_list:
                assert self.default_state is None, 'Cannot have more than ' \
                                                   'one default state.'
                self.default_state = state
            else:
                condition_values = {}
                for cond_data in conditions_list:
                    condition = self._condition_from_data(cond_data, player,
                                                          timer)
                    value = self._condition_value_from_data(cond_data)
                    condition_values[condition] = value
                self._state_condition_values[state] = condition_values

    def _effect_from_data(self, effect_data: Dict, effect_label: str,
                          player: Player, map_image: pg.Surface) -> Effect:
        effect_label = Effects(effect_label)
        if effect_label == Effects.EQUIP_AND_USE_MOD:
            mod_label = effect_data['mod']
            mod = Mod(ModData(**load_mod_data_kwargs(mod_label)))
            effect = EquipAndUseMod(mod)
        elif effect_label == Effects.RANDOM_SOUND:
            sound_files = effect_data['sound files']
            effect = PlayRandomSound(sound_files)
        elif effect_label == Effects.FACE_AND_PURSUE:
            effect = FaceAndPursueTarget(player)
        elif effect_label == Effects.STOP_MOTION:
            effect = StopMotion()
        elif effect_label == Effects.DROP_ITEM:
            item_label = effect_data['item_label']
            effect = DropItem(item_label)
        elif effect_label == Effects.KILL:
            effect = Kill()
        elif effect_label == Effects.PLAY_SOUND:
            effect = PlaySound(effect_data['sound file'])
        elif effect_label == Effects.DRAW_ON_MAP:
            effect = DrawOnSurface(map_image, effect_data['image file'])
        else:
            raise NotImplementedError(
                'Unrecognized effect label %s' % (effect_label,))
        return effect

    def _condition_value_from_data(self, condition_data: Dict) -> int:
        assert len(condition_data.keys()) == 1
        label_str = next(iter(condition_data.keys()))
        return condition_data[label_str]['value']

    def _condition_from_data(self, condition_data: Dict, player: Player,
                             timer: Timer) -> Condition:
        assert len(condition_data.keys()) == 1
        label_str = next(iter(condition_data.keys()))
        condition_label = Conditions(label_str)
        condition_data = condition_data[label_str]
        if condition_label == Conditions.RANDOM_RATE:
            rate = condition_data['rate']
            condition = RandomEventAtRate(timer, rate)
        elif condition_label == Conditions.TARGET_CLOSE:
            threshold = condition_data['threshold']
            condition = TargetClose(player, threshold)
        elif condition_label == Conditions.DEAD:
            condition = IsDead()
        elif condition_label == Conditions.ALWAYS:
            condition = AlwaysTrue()
        elif condition_label == Conditions.ENERGY_NOT_FULL:
            condition = EnergyNotFull()
        else:
            raise NotImplementedError(
                'Unrecognized condition label %s' % (condition_label,))
        if condition_data is not None and 'logical_not' in condition_data:
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

        self.behavior = Behavior(data.behavior_dict, player, self._timer,
                                 self._map_img)
        self.status.state = self.behavior.default_state

        self.target = player

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
        width = int(full_width * self.status.health / self.status.max_health)
        health_bar = pg.Rect(0, 0, width, 7)
        pg.draw.rect(image, col, health_bar)

    def update(self) -> None:
        self.status.state = self.behavior.determine_state(self)
        self.behavior.do_state_behavior(self)

        self.motion.update()

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
