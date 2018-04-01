from creatures.party_member import PartyMember
from typing import List


class Party(object):

    def __init__(self) -> None:
        self.party_members: List[PartyMember] = []
        self._active_member_idx = 0
        self.active_member_moved = False

    def prepare_for_combat(self) -> None:
        for member in self.party_members:
            member.prepare_combat()
        self.party_members = sorted(self.party_members,
                                    key=lambda m: m.initiative, reverse=True)

    def add_member(self, member: PartyMember) -> None:
        self.party_members.append(member)

    def remove_member(self, member: PartyMember) -> None:
        self.party_members.remove(member)

    @property
    def active_member(self) -> PartyMember:
        return self.party_members[self._active_member_idx]

    def member_is_active(self, idx: int) -> bool:
        return idx == self._active_member_idx

    def next_member(self)-> None:
        self.active_member_moved = False
        idx = self._active_member_idx
        self._active_member_idx = (idx + 1) % len(self.party_members)

    def __setitem__(self, key: int, value: PartyMember) -> None:
        self.party_members[key] = value

    def __getitem__(self, key: int) -> None:
        return self.party_members[key]

    def __delitem__(self, key: int) -> None:
        del self.party_members[key]

    def __len__(self) -> int:
        return len(self.party_members)
