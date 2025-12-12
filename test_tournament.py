import unittest
import json
import os
from tournament import Tournament

class TestTournament(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_matches.json'
        
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def create_matches(self, matches):
        with open(self.test_file, 'w') as f:
            json.dump(matches, f)

    def test_basic_points(self):
        """Test simple point calculation (Win=3, Draw=1, Loss=0)"""
        matches = [
            {"home_team": "A", "away_team": "B", "home_score": 2, "away_score": 0, "played": True}, # A:3, B:0
            {"home_team": "C", "away_team": "A", "home_score": 1, "away_score": 1, "played": True}  # C:1, A:1 -> A:4
        ]
        self.create_matches(matches)
        t = Tournament(self.test_file)
        ranking = t.get_ranking()
        
        self.assertEqual(ranking[0]['team'], "A")
        self.assertEqual(ranking[0]['points'], 4)
        self.assertEqual(ranking[1]['team'], "C") # C has 1, B has 0
        self.assertEqual(ranking[2]['team'], "B")

    def test_tiebreaker_points(self):
        """Test simplest tiebreaker: More points wins"""
        matches = [
            {"home_team": "A", "away_team": "B", "home_score": 1, "away_score": 0, "played": True}, # A:3, B:0
        ]
        self.create_matches(matches)
        t = Tournament(self.test_file)
        ranking = t.get_ranking()
        self.assertEqual(ranking[0]['team'], "A")

    def test_tiebreaker_h2h_points(self):
        """Test H2H: Team A and B tied on overall points, but A beat B."""
        # Scenario: 
        # A vs B -> A wins (A=3, B=0)
        # B vs C -> B wins (B=3, C=0)
        # C vs A -> C wins (C=3, A=0)
        # This is a 3-way tie logic, actually. Let's make it simpler for direct H2H.
        
        # A vs B -> A wins (A=3, B=0 in H2H)
        # A vs C -> A loses (A=3)
        # B vs C -> B wins (B=3)
        # Result: A=3, B=3 (Overall). H2H: A beat B.
        matches = [
            {"home_team": "A", "away_team": "B", "home_score": 1, "away_score": 0, "played": True},
            {"home_team": "A", "away_team": "C", "home_score": 0, "away_score": 2, "played": True},
            {"home_team": "B", "away_team": "D", "home_score": 5, "away_score": 0, "played": True}, # B boosts GD to try to trick logic, but H2H comes first
            {"home_team": "A", "away_team": "E", "home_score": 0, "away_score": 10, "played": True} # A terrible GD
        ]
        # A: 3 pts (won vs B, lost vs C, lost vs E)
        # B: 3 pts (lost vs A, won vs D)
        # Note: We need accurate point totals.
        
        # Let's construct explicit equal points scenario.
        # A: 3 pts, B: 3 pts. 
        # A beat B directly.
        matches = [
            {"home_team": "A", "away_team": "B", "home_score": 2, "away_score": 1, "played": True}, # A beats B
            {"home_team": "A", "away_team": "C", "home_score": 0, "away_score": 5, "played": True}, # A loses big
            {"home_team": "B", "away_team": "D", "home_score": 5, "away_score": 0, "played": True}, # B wins big
        ]
        # A: 3 pts, GD -4
        # B: 3 pts, GD +4
        # Even though B has better GD, A should win on H2H.
        
        self.create_matches(matches)
        t = Tournament(self.test_file)
        ranking = t.get_ranking()
        
        # Filter only A and B to check relative order
        ab_rank = [x['team'] for x in ranking if x['team'] in ['A', 'B']]
        self.assertEqual(ab_rank, ['A', 'B'], "A should be above B due to H2H despite worse GD")

    def test_tiebreaker_h2h_gd(self):
        """Test H2H Goal Difference (e.g. 2 legs, points equal)."""
        # A vs B: 2-0
        # B vs A: 3-0 (B wins H2H GD)
        # A and B must have same total points.
        matches = [
            {"home_team": "A", "away_team": "B", "home_score": 2, "away_score": 0, "played": True},
            {"home_team": "B", "away_team": "A", "home_score": 3, "away_score": 0, "played": True}
        ]
        # Both have 3 points.
        # H2H: A won 1, B won 1 (3 pts each H2H).
        # H2H GD: A (+2 -3 = -1), B (-2 +3 = +1). B should be first.
        
        self.create_matches(matches)
        t = Tournament(self.test_file)
        ranking = t.get_ranking()
        
        self.assertEqual(ranking[0]['team'], "B")
        self.assertEqual(ranking[1]['team'], "A")

    def test_tiebreaker_overall_gd(self):
        """Test Overall Goal Difference when H2H is dead even."""
        # A vs B: 1-1
        # A vs C: 5-0 (A: 4pts, GD +5)
        # B vs D: 1-0 (B: 4pts, GD +1)
        matches = [
            {"home_team": "A", "away_team": "B", "home_score": 1, "away_score": 1, "played": True},
            {"home_team": "A", "away_team": "C", "home_score": 5, "away_score": 0, "played": True},
            {"home_team": "B", "away_team": "D", "home_score": 1, "away_score": 0, "played": True},
        ]
        self.create_matches(matches)
        t = Tournament(self.test_file)
        ranking = t.get_ranking()
        
        ab_rank = [x['team'] for x in ranking if x['team'] in ['A', 'B']]
        self.assertEqual(ab_rank, ['A', 'B'], "A should be above B due to Overall GD")

if __name__ == '__main__':
    unittest.main()
