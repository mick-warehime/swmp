from model import Group


class Conflict(object):
    def __init__(self, conflict_objects: Group) -> None:
        self.initial_size = len(conflict_objects)
        self.size = len(conflict_objects)
        self.objects = conflict_objects

    def is_resolved(self) -> bool:
        return len(self.objects) == 0
