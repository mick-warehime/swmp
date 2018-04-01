from party_member import PartyMember

class Party(object):

    def __init__(self) -> None:
        self.party_members: List[PartyMember] = []

    def prepare_for_combat(self) -> None:
        for member in self.party_members:
            member.prepare_combat()
        sorted(self.party_members, key=lambda m: m.initiative, reverse=True)

    def add_member(self, member: PartyMember) -> None:
        self.party_members.append(member)

    def remove_member(self, member: PartyMember) -> None:
        self.party_members.remove(member)

    def __setitem__(self, key, value) -> None:
        self.party_members[key] = value

    def __getitem__(self, key) -> None:
        return self.party_members[key]

    def __delitem__(self, key) -> None:
        del self.party_members[key]

    def __len__(self) -> int:
        return len(self.party_members)



