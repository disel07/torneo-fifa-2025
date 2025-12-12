import unittest
from ranking_system import Tournament, Match, TeamStats

class TestRanking(unittest.TestCase):
    def setUp(self):
        self.tournament = Tournament()

    def test_basic_points(self):
        # A beats B 2-0 (3 pts A, 0 pts B)
        # C draws D 1-1, C wins penalties (2 pts C, 1 pt D)
        data = [
            {"id": 1, "home_team": "A", "away_team": "B", "home_score": 2, "away_score": 0, "played": True},
            {"id": 2, "home_team": "C", "away_team": "D", "home_score": 1, "away_score": 1, "played": True, "penalty_winner": "C"}
        ]
        self.tournament.load_matches(data)
        ranking = self.tournament.calculate_ranking()
        
        self.assertEqual(ranking[0]["team"], "A")
        self.assertEqual(ranking[0]["points"], 3)
        self.assertEqual(ranking[1]["team"], "C")
        self.assertEqual(ranking[1]["points"], 2)
        self.assertEqual(ranking[2]["team"], "D")
        self.assertEqual(ranking[2]["points"], 1)
        self.assertEqual(ranking[3]["team"], "B")
        self.assertEqual(ranking[3]["points"], 0)

    def test_h2h_tiebreaker(self):
        # A and B both have 3 points.
        # Match 1: A vs C (A wins 1-0) -> A=3
        # Match 2: B vs D (B wins 5-0) -> B=3 (Better global GD)
        # Match 3: A vs B (A wins 1-0) 
        # Ranking should be: A first (H2H win), even if B has better Global GD.
        
        # Scenario:
        # A beats B 1-0.
        # B beats C 10-0.
        # A loses to D 0-1.
        # Points: A=3, B=3 (assuming other matches don't change this balance, let's keep it simple)
        
        data = [
            # A vs B: A wins 1-0. A gets 3 pts. B gets 0.
            {"id": 1, "home_team": "A", "away_team": "B", "home_score": 1, "away_score": 0, "played": True},
            # B vs C: B wins 10-0. B gets 3 pts.
            {"id": 2, "home_team": "B", "away_team": "C", "home_score": 10, "away_score": 0, "played": True},
            # A vs D: A loses 0-1. A stays at 3 pts.
            {"id": 3, "home_team": "A", "away_team": "D", "home_score": 0, "away_score": 1, "played": True}
        ]
        self.tournament.load_matches(data)
        ranking = self.tournament.calculate_ranking()
        
        # A and B both have 3 points.
        # Global GD: A = 1-1 = 0. B = 10-1 = +9.
        # H2H: A beat B. So A should be ahead.
        
        filtered = [t for t in ranking if t["team"] in ["A", "B"]]
        self.assertEqual(filtered[0]["team"], "A", "A should be ahead of B due to H2H")
        self.assertEqual(filtered[1]["team"], "B")

    def test_complex_tie(self):
        # 3-way tie: A, B, C.
        # A beats B 1-0
        # B beats C 1-0
        # C beats A 2-0
        # H2H mini-table:
        # A: 3 pts, GF=1, GA=2, GD=-1
        # B: 3 pts, GF=1, GA=1, GD=0
        # C: 3 pts, GF=2, GA=1, GD=+1
        # Order should be C, B, A based on H2H Goal Diff.
        
        data = [
            {"id": 1, "home_team": "A", "away_team": "B", "home_score": 1, "away_score": 0, "played": True},
            {"id": 2, "home_team": "B", "away_team": "C", "home_score": 1, "away_score": 0, "played": True},
            {"id": 3, "home_team": "C", "away_team": "A", "home_score": 2, "away_score": 0, "played": True}
        ]
        self.tournament.load_matches(data)
        ranking = self.tournament.calculate_ranking()
        
        teams = [r["team"] for r in ranking]
        self.assertEqual(teams, ["C", "B", "A"])

if __name__ == "__main__":
    unittest.main()
