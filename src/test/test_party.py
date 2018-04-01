from unittest import TestCase
from src.creatures.party import Party, example_party


class TestParty(TestCase):

    def test_create_party(self) -> None:
        party = example_party()
        party_size = len(party)

        count = 0
        for _ in party.party_members:
            count += 1
        self.assertEqual(party_size, count)

    def test_party_speed(self) -> None:
        party = example_party()

        m = party[0]

        self.assertTrue(m.can_reach(0, 0))
        self.assertTrue(m.can_reach(m.speed, 0))
        self.assertFalse(m.can_reach(m.speed, m.speed))
