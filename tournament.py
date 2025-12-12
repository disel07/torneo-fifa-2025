import json
from collections import defaultdict
from itertools import combinations
import functools
import os

class Tournament:
    def __init__(self, matches_file='matches.json'):
        self.matches_file = matches_file
        self.matches = []
        self.teams = set()
        
    def load_data(self):
        """Loads match data from JSON file."""
        try:
            with open(self.matches_file, 'r') as f:
                self.matches = json.load(f)
                
            # Extract unique teams
            for m in self.matches:
                if 'home_team' in m: self.teams.add(m['home_team'])
                if 'away_team' in m: self.teams.add(m['away_team'])
            
            # Filter None if any
            self.teams.discard(None)
            
        except FileNotFoundError:
            print(f"Error: {self.matches_file} not found.")
            self.matches = []
        except Exception as e:
            print(f"Error loading data: {e}")
            self.matches = []

    def calculate_stats(self):
        """Calculates base stats for each team."""
        stats = defaultdict(lambda: {
            'points': 0, 'played': 0, 'won': 0, 'drawn': 0, 'lost': 0,
            'gf': 0, 'ga': 0, 'gd': 0
        })
        
        for m in self.matches:
            if not m.get('played') or m.get('home_score') is None or m.get('away_score') is None:
                continue
                
            h = m['home_team']
            a = m['away_team']
            hs = m['home_score']
            as_ = m['away_score']
            
            stats[h]['played'] += 1
            stats[a]['played'] += 1
            stats[h]['gf'] += hs
            stats[a]['gf'] += as_
            stats[h]['ga'] += as_
            stats[a]['ga'] += hs
            stats[h]['gd'] += (hs - as_)
            stats[a]['gd'] += (as_ - hs)
            
            if hs > as_:
                stats[h]['points'] += 3
                stats[h]['won'] += 1
                stats[a]['lost'] += 1
            elif hs < as_:
                stats[a]['points'] += 3
                stats[a]['won'] += 1
                stats[h]['lost'] += 1
            else:
                stats[h]['points'] += 1
                stats[a]['points'] += 1
                stats[h]['drawn'] += 1
                stats[a]['drawn'] += 1
                
        return dict(stats)

    def get_h2h_stats(self, team_a, team_b):
        """Calculates specific Head-to-Head stats between two teams."""
        points_a = 0
        points_b = 0
        gd_a = 0
        
        for m in self.matches:
            if not m.get('played') or m.get('home_score') is None: continue
            
            if m['home_team'] == team_a and m['away_team'] == team_b:
                hs, as_ = m['home_score'], m['away_score']
                if hs > as_: points_a += 3
                elif hs < as_: points_b += 3
                else: 
                    points_a += 1
                    points_b += 1
                gd_a += (hs - as_)
                
            elif m['home_team'] == team_b and m['away_team'] == team_a:
                hs, as_ = m['home_score'], m['away_score']
                if hs > as_: points_b += 3
                elif hs < as_: points_a += 3
                else:
                    points_a += 1
                    points_b += 1
                gd_a -= (hs - as_) # from perspective of A (A is away)

        return points_a, points_b, gd_a

    def compare_teams(self, team_a_name, team_b_name, all_stats):
        """
        Comparator function for sorting.
        Returns:
        -1 if team_a should come BEFORE team_b (Better)
         1 if team_a should come AFTER team_b (Worse)
         0 if equal
        """
        stats_a = all_stats.get(team_a_name, {'points': 0, 'gf': 0, 'gd': 0})
        stats_b = all_stats.get(team_b_name, {'points': 0, 'gf': 0, 'gd': 0})

        # 1. Total Points
        if stats_a['points'] != stats_b['points']:
            return -1 if stats_a['points'] > stats_b['points'] else 1
        
        # 2. Head-to-Head Points
        h2h_pts_a, h2h_pts_b, h2h_gd_a = self.get_h2h_stats(team_a_name, team_b_name)
        
        if h2h_pts_a != h2h_pts_b:
            return -1 if h2h_pts_a > h2h_pts_b else 1
            
        # 3. Head-to-Head Goal Difference
        if h2h_gd_a != 0:
            return -1 if h2h_gd_a > 0 else 1

        # 4. Overall Goal Difference
        if stats_a['gd'] != stats_b['gd']:
            return -1 if stats_a['gd'] > stats_b['gd'] else 1

        # 5. Overall Goals Scored
        if stats_a['gf'] != stats_b['gf']:
            return -1 if stats_a['gf'] > stats_b['gf'] else 1

        return 0

    def get_ranking(self):
        self.load_data()
        stats = self.calculate_stats()
        
        # Convert teams set to list to sort
        sorted_teams = list(self.teams)
        
        # Use functools.cmp_to_key to use our custom comparator
        # We need to bind the stats to the comparator
        comparator = functools.partial(self.compare_teams, all_stats=stats)
        
        sorted_teams.sort(key=functools.cmp_to_key(comparator))
        
        # Format output
        ranking = []
        for i, team in enumerate(sorted_teams, 1):
            s = stats.get(team, {'points': 0, 'played': 0, 'won': 0, 'drawn': 0, 'lost': 0, 'gf': 0, 'ga': 0, 'gd': 0})
            ranking.append({
                'rank': i,
                'team': team,
                'points': s['points'],
                'played': s['played'],
                'w': s['won'],
                'd': s['drawn'],
                'l': s['lost'],
                'gf': s['gf'],
                'ga': s['ga'],
                'gd': s['gd']
            })
            
        return ranking

    def save_ranking(self, output_file='classifica.json'):
        ranking = self.get_ranking()
        with open(output_file, 'w') as f:
            json.dump(ranking, f, indent=4)
        print(f"Ranking saved to {output_file}")

if __name__ == "__main__":
    t = Tournament()
    t.save_ranking()
