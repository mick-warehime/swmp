from os import path
from typing import Set, Dict, Union

import yaml

_PROJECTILE_FILE = path.dirname(__file__) + '/projectiles.yml'
_ABILITIES_FILE = path.dirname(__file__) + '/abilities.yml'
_MODS_FILE = path.dirname(__file__) + '/mods.yml'
_ITEMS_FILE = path.dirname(__file__) + '/items.yml'
_NPCS_FILE = path.dirname(__file__) + '/npcs.yml'
_QUEST_FOLDER = path.dirname(__file__) + '/quests/'

with open(_PROJECTILE_FILE, 'r') as stream:
    _projectile_data = yaml.load(stream)

with open(_ABILITIES_FILE, 'r') as stream:
    _abilities_data = yaml.load(stream)

with open(_MODS_FILE, 'r') as stream:
    _mods_data = yaml.load(stream)

with open(_ITEMS_FILE, 'r') as stream:
    _items_data = yaml.load(stream)

with open(_NPCS_FILE, 'r') as stream:
    _npc_data = yaml.load(stream)

KwargType = Dict[str, Union[int, float, bool, str]]


def load_item_data_kwargs(name: str) -> KwargType:
    if name in _items_data:
        return _items_data[name]
    raise KeyError('Item name %s not recognized' % (name,))


def load_mod_data_kwargs(name: str) -> KwargType:
    if name in _mods_data:
        return _mods_data[name]
    raise KeyError('Mod name %s not recognized' % (name,))


def load_ability_data_kwargs(name: str) -> KwargType:
    for ability_type, ability_kwargs in _abilities_data.items():
        if name in ability_kwargs:
            return ability_kwargs[name]
    raise KeyError('Ability name %s not recognized' % (name,))


def load_projectile_data_kwargs(name: str) -> KwargType:
    if name not in _projectile_data:
        raise KeyError('Unrecognized projectile name: %s' % (name,))
    return _projectile_data[name]


def load_npc_data_kwargs(name: str) -> KwargType:
    if name not in _npc_data:
        raise KeyError('Unrecognized npc name: %s' % (name,))
    return _npc_data[name]


def load_quest_data(file_name: str, full_path=False) -> KwargType:

    file_path = file_name if full_path else _QUEST_FOLDER + file_name

    if '.yml' not in file_name:
        file_name += '.yml'

    with open(file_path, 'r') as stream:
        data = yaml.load(stream)
    return data


def is_npc_type(name: str) -> bool:
    assert name not in ('image files', 'sound files')
    return name in _npc_data


def is_item_type(name: str) -> bool:
    return name in _items_data


def image_filenames() -> Set[str]:
    filenames = _item_image_filenames()
    filenames |= _mod_image_filenames()
    filenames |= _projectile_image_filenames()
    filenames |= _npc_image_filenames()
    return filenames


def sound_filenames() -> Set[str]:
    filenames = _ability_sound_filenames()
    filenames |= _npc_sound_filenames()
    return filenames


def _mod_image_filenames() -> Set[str]:
    filenames = set()
    for mod_data_dict in _mods_data.values():
        if 'equipped_image_file' not in mod_data_dict:
            continue  # Skip default specifications
        image_file = mod_data_dict['equipped_image_file']
        if image_file:
            filenames.add(image_file)
        image_file = mod_data_dict['backpack_image_file']
        if image_file:
            filenames.add(image_file)

    return filenames


def _item_image_filenames() -> Set[str]:
    filenames = set()
    for item_dict in _items_data.values():
        filenames.add(item_dict['image_file'])
    return filenames


def _ability_sound_filenames() -> Set[str]:
    filenames = set()
    for ability_types in _abilities_data.values():
        for ability_data in ability_types.values():
            sound_file = ability_data['sound_on_use']
            if sound_file is not None:
                filenames.add(sound_file)
    return filenames


def _projectile_image_filenames() -> Set[str]:
    filenames = set()
    for projectile in _projectile_data.values():
        filenames.add(projectile['image_file'])
    return filenames


def _npc_image_filenames() -> Set[str]:
    return set(_npc_data['image files'].values())


def _npc_sound_filenames() -> Set[str]:
    return set(_npc_data['sound files'].values())
