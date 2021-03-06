from enum import Enum
from random import uniform, choice
from typing import Any, List

from pygame.math import Vector2
from pygame.transform import rotate

from conditions import CooldownCondition
from model import GameObject
from projectiles import ProjectileData, ProjectileFactory, MuzzleFlash
from view import images, sounds
from view.screen import ScreenAccess


class Effects(Enum):
    EQUIP_AND_USE_MOD = 'equip and use mod'
    RANDOM_SOUND = 'random sound'
    FACE_AND_PURSUE = 'face and pursue target'
    STOP_MOTION = 'stop motion'
    DROP_ITEM = 'drop item'
    KILL = 'kill'
    PLAY_SOUND = 'play sound'
    DRAW_ON_MAP = 'draw image on map'
    FACE = 'face target'


class Effect(object):
    """Implements an effect on a Humanoid."""

    def activate(self, humanoid: Any) -> None:
        raise NotImplementedError


class StopMotion(Effect):
    def activate(self, humanoid: Any) -> None:
        humanoid.motion.stop()


class EquipAndUseMod(Effect):
    def activate(self, humanoid: Any) -> None:
        humanoid.inventory.equip(self._mod)
        humanoid.ability_caller(self._mod.loc)()

    def __init__(self, mod: Any) -> None:
        self._mod = mod


class UpdateLastUse(Effect):
    def __init__(self, cool_down_condition: CooldownCondition) -> None:
        self._cool_down_condition = cool_down_condition

    def activate(self, humanoid: Any) -> None:
        self._cool_down_condition.update_last_use(humanoid)


class Heal(Effect):
    def __init__(self, heal_amount: int) -> None:
        self._heal_amount = heal_amount

    def activate(self, humanoid: Any) -> None:
        humanoid.status.increment_health(self._heal_amount)


class Recharge(Effect):
    def __init__(self, recharge_amount: int) -> None:
        self._recharge_amount = recharge_amount

    def activate(self, humanoid: Any) -> None:
        humanoid.energy_source.increment_energy(self._recharge_amount)


class ExpendEnergy(Effect):
    def __init__(self, energy_required: int) -> None:
        self._energy_required = energy_required

    def activate(self, humanoid: Any) -> None:
        assert hasattr(humanoid, 'energy_source')
        humanoid.energy_source.expend_energy(self._energy_required)


class PlaySound(Effect):
    def __init__(self, sound_file: str) -> None:
        self._sound_file = sound_file

    def activate(self, humanoid: Any) -> None:
        sounds.play(self._sound_file)


class DrawOnScreen(Effect, ScreenAccess):
    def __init__(self, to_draw_file: str, angled: bool = False) -> None:
        super().__init__()
        self._to_draw_file = to_draw_file
        self._angled = angled

    def activate(self, humanoid: Any) -> None:
        pos = humanoid.pos
        image = images.get_image(self._to_draw_file)
        if self._angled:
            image = rotate(image, humanoid.motion.rot)
        w = image.get_width() / 2
        h = image.get_height() / 2
        self.screen.blit(image, pos - Vector2(w, h))


class PlayRandomSound(Effect):
    def __init__(self, sound_files: List[str]) -> None:
        assert sound_files, 'At least one sound file must be specified.'
        self._sound_files = sound_files

    def activate(self, humanoid: Any) -> None:
        sound_file = choice(self._sound_files)
        sounds.play(sound_file)


class Kickback(Effect):
    def __init__(self, kickback: int) -> None:
        self._kickback = kickback

    def activate(self, humanoid: Any) -> None:
        humanoid.motion.vel = Vector2(-self._kickback, 0).rotate(
            -humanoid.motion.rot)


class MakeProjectile(Effect):
    def __init__(self, projectile_data: ProjectileData, spread: int,
                 projectile_count: int) -> None:
        self._factory = ProjectileFactory(projectile_data)
        self._spread = spread
        self._count = projectile_count

    def activate(self, humanoid: Any) -> None:
        pos = humanoid.pos
        rot = humanoid.motion.rot

        direction = Vector2(1, 0).rotate(-rot)
        barrel_offset = Vector2(30, 10)
        origin = pos + barrel_offset.rotate(-rot)

        for _ in range(self._count):
            spread = uniform(-self._spread, self._spread)
            self._factory.build(origin, direction.rotate(spread))


class MuzzleFlashEffect(Effect):
    def activate(self, humanoid: Any) -> None:
        direction = humanoid.motion.direction
        direction = direction.rotate(20)
        MuzzleFlash(humanoid.pos + 22 * direction)


class DropItem(Effect):
    def __init__(self, item_label: str) -> None:
        self.item_label = item_label

    def activate(self, humanoid: Any) -> None:
        # TODO(dvirk): I need to import locally to avoid circular import
        # errors. Is this bad?
        from data.constructors import build_map_object
        build_map_object(self.item_label, humanoid.pos)


class FaceAndPursueTarget(Effect):
    def __init__(self, target: GameObject) -> None:
        self._target = target

    def activate(self, humanoid: Any) -> None:
        target_disp = self._target.pos - humanoid.pos
        humanoid.motion.rot = target_disp.angle_to(Vector2(1, 0))
        # TODO(dvirk): update_acc is only a method for Enemy. This is a bit
        # kludgy.
        humanoid.update_acc()


class FaceTarget(Effect):
    def __init__(self, target: GameObject) -> None:
        self._target = target

    def activate(self, humanoid: Any) -> None:
        target_disp = self._target.pos - humanoid.pos
        humanoid.motion.rot = target_disp.angle_to(Vector2(1, 0))


class Kill(Effect):
    def activate(self, humanoid: Any) -> None:
        humanoid.kill()
