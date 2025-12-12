import unittest
from tournament import calculate_standings, RES_90, RES_RIG_A, RES_RIG_B

class TestTournament(unittest.TestCase):
    
    def test_points_calculation(self):
        # Match: A wins 3-0
        matches = [
            {"squadra_a": "A", "squadra_b": "B", "gol_a": 3, "gol_b": 0, "risultato": RES_90},
        ]
        rank = calculate_standings(matches)
        team_a = next(t for t in rank if t["squadra"] == "A")
        team_b = next(t for t in rank if t["squadra"] == "B")
        self.assertEqual(team_a["punti"], 3)
        self.assertEqual(team_b["punti"], 0)

        # Match: A wins penalties (2-2 draw)
        matches = [
            {"squadra_a": "A", "squadra_b": "B", "gol_a": 2, "gol_b": 2, "risultato": RES_RIG_A},
        ]
        rank = calculate_standings(matches)
        team_a = next(t for t in rank if t["squadra"] == "A")
        team_b = next(t for t in rank if t["squadra"] == "B")
        self.assertEqual(team_a["punti"], 2)
        self.assertEqual(team_b["punti"], 1)

    def test_tiebreaker_h2h(self):
        # A and B have same points (3 each).
        # Match 1: A beats B 2-0.
        # Match 2: B beats A 3-0.
        # Aggregate: B wins 3-2. B should be first.
        matches = [
            {"squadra_a": "A", "squadra_b": "B", "gol_a": 2, "gol_b": 0, "risultato": RES_90},
            {"squadra_a": "B", "squadra_b": "A", "gol_a": 3, "gol_b": 0, "risultato": RES_90},
            # Dummy games to equalise points if needed, but here simple trade is enough:
            # A has 3 pts, B has 3 pts.
            # H2H: A has +2-3 = -1. B has +3-2 = +1. B wins.
        ]
        rank = calculate_standings(matches)
        self.assertEqual(rank[0]["squadra"], "B")
        self.assertEqual(rank[1]["squadra"], "A")

    def test_tiebreaker_h2h_away_goals(self):
        # A and B same points.
        # A (Home) 1-2 B (Away)
        # B (Home) 0-1 A (Away)
        # Agg: 2-2. 
        # Away goals: B scored 2 at A's home. A scored 1 at B's home. B should win.
        matches = [
            {"squadra_a": "A", "squadra_b": "B", "gol_a": 1, "gol_b": 2, "risultato": RES_90}, # B wins
            {"squadra_a": "B", "squadra_b": "A", "gol_a": 0, "gol_b": 1, "risultato": RES_90}, # A wins
        ]
        rank = calculate_standings(matches)
        self.assertEqual(rank[0]["squadra"], "B")
        self.assertEqual(rank[1]["squadra"], "A")

    def test_tiebreaker_global_diff(self):
        # H2H is perfectly even (1-1, 1-1). 
        # A beats C 5-0. B beats C 1-0.
        # A should be first due to global diff.
        matches = [
            {"squadra_a": "A", "squadra_b": "B", "gol_a": 1, "gol_b": 1, "risultato": "pareggio"},
            {"squadra_a": "B", "squadra_b": "A", "gol_a": 1, "gol_b": 1, "risultato": "pareggio"},
            {"squadra_a": "A", "squadra_b": "C", "gol_a": 5, "gol_b": 0, "risultato": RES_90},
            {"squadra_a": "B", "squadra_b": "C", "gol_a": 1, "gol_b": 0, "risultato": RES_90},
            {"squadra_a": "C", "squadra_b": "D", "gol_a": 0, "gol_b": 0, "risultato": "pareggio"}, # Irrelevant
        ]
        rank = calculate_standings(matches)
        # A: 4 pts, Diff +5. B: 4 pts, Diff +1.
        # H2H is even.
        self.assertEqual(rank[0]["squadra"], "A")

    def test_tiebreaker_goals_scored(self):
        # H2H even. Diff even.
        # A: 5-5 (Diff 0). B: 1-1 (Diff 0).
        # A should be first.
        matches = [
           {"squadra_a": "A", "squadra_b": "B", "gol_a": 0, "gol_b": 0, "risultato": "pareggio"},
           {"squadra_a": "B", "squadra_b": "A", "gol_a": 0, "gol_b": 0, "risultato": "pareggio"},
           # A draws 5-5 with C
           {"squadra_a": "A", "squadra_b": "C", "gol_a": 5, "gol_b": 5, "risultato": "pareggio"},
           # B draws 1-1 with C
           {"squadra_a": "B", "squadra_b": "C", "gol_a": 1, "gol_b": 1, "risultato": "pareggio"},
        ]
        rank = calculate_standings(matches)
        # A: 2 pts, Diff 0, GF 5. B: 2 pts, Diff 0, GF 1.
        self.assertEqual(rank[0]["squadra"], "A")

if __name__ == '__main__':
    unittest.main()
