import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class Match:
    id: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    played: bool
    penalty_winner: str = None  # Name of the team who won penalties, if any

@dataclass
class TeamStats:
    name: str
    points: int = 0
    goals_scored: int = 0
    goals_conceded: int = 0
    matches_played: int = 0
    
    @property
    def goal_difference(self) -> int:
        return self.goals_scored - self.goals_conceded

class Tournament:
    def __init__(self):
        self.matches: List[Match] = []
        self.teams: Dict[str, TeamStats] = {}

    def load_matches(self, matches_data: List[dict]):
        self.matches = []
        self.teams = {}
        for m in matches_data:
            match = Match(**m)
            self.matches.append(match)
            if match.home_team not in self.teams:
                self.teams[match.home_team] = TeamStats(match.home_team)
            if match.away_team not in self.teams:
                self.teams[match.away_team] = TeamStats(match.away_team)
            
            if match.played:
                self._process_match(match)

    def _process_match(self, match: Match):
        stats_home = self.teams[match.home_team]
        stats_away = self.teams[match.away_team]
        
        stats_home.matches_played += 1
        stats_away.matches_played += 1
        
        stats_home.goals_scored += match.home_score
        stats_home.goals_conceded += match.away_score
        stats_away.goals_scored += match.away_score
        stats_away.goals_conceded += match.home_score
        
        if match.home_score > match.away_score:
            # Home win 90'
            stats_home.points += 3
        elif match.away_score > match.home_score:
            # Away win 90'
            stats_away.points += 3
        else:
            # Draw -> Look at penalty winner
            if match.penalty_winner == match.home_team:
                stats_home.points += 2
                stats_away.points += 1
            elif match.penalty_winner == match.away_team:
                stats_away.points += 2
                stats_home.points += 1
            else:
                # Fallback if no penalty winner specified (shouldn't happen with valid data)
                # Just give 1 point each? Or raise error? 
                # User rules strictly said 2 pts / 1 pt. 
                # We'll assume valid data.
                pass

    def calculate_ranking(self) -> List[dict]:
        # Convert teams to list
        teams_list = list(self.teams.values())
        
        # Sort logic
        # We need a custom comparator because of the H2H rule which depends on the specific subset of tied teams.
        # Python's sort is stable and we can use a key for simple criteria, but H2H is complex.
        # However, for a small number of teams, we can implement a custom sort function or use a comparison key that allows some recursion or lookup.
        # Actually, the most robust way for H2H is:
        # 1. Group by points.
        # 2. For each group with >1 team, apply H2H sort.
        # 3. If H2H is still tied, apply Global GD.
        # 4. If still tied, apply Global GF.
        
        # Initial sort by points (descending)
        teams_list.sort(key=lambda x: x.points, reverse=True)
        
        # Now we need to resolve ties
        i = 0
        while i < len(teams_list):
            j = i + 1
            while j < len(teams_list) and teams_list[j].points == teams_list[i].points:
                j += 1
            
            # teams_list[i:j] have the same points
            if j - i > 1:
                tied_group = teams_list[i:j]
                self._sort_tied_group(tied_group)
                teams_list[i:j] = tied_group
            
            i = j
            
        return [
            {
                "rank": idx + 1,
                "team": t.name,
                "points": t.points,
                "goals_scored": t.goals_scored,
                "goals_conceded": t.goals_conceded,
                "goal_difference": t.goal_difference,
                "matches_played": t.matches_played
            }
            for idx, t in enumerate(teams_list)
        ]

    def _sort_tied_group(self, group: List[TeamStats]):
        # Custom sort logic for tied group
        # Create a copy because accessing 'group' inside its own sort key function 
        # might reveal an empty/modifying list depending on implementation.
        group_copy = list(group)
        
        def h2h_key(t):
            # Calculate metrics against other teams in THIS tied group
            h2h_points = 0
            h2h_gf = 0
            h2h_ga = 0
            
            others = [x.name for x in group_copy if x.name != t.name]
            
            for m in self.matches:
                if not m.played:
                    continue
                    
                is_home = (m.home_team == t.name)
                is_away = (m.away_team == t.name)
                
                if (is_home and m.away_team in others) or (is_away and m.home_team in others):
                    
                    # Logic for points in H2H
                    pts_home, pts_away = 0, 0
                    if m.home_score > m.away_score:
                        pts_home = 3
                    elif m.away_score > m.home_score:
                        pts_away = 3
                    else:
                        # Draw -> penalties
                        if m.penalty_winner == m.home_team:
                            pts_home, pts_away = 2, 1
                        elif m.penalty_winner == m.away_team:
                            pts_home, pts_away = 1, 2
                        
                    if is_home:
                        h2h_points += pts_home
                        h2h_gf += m.home_score
                        h2h_ga += m.away_score
                    else:
                        h2h_points += pts_away
                        h2h_gf += m.away_score
                        h2h_ga += m.home_score
            
            return (h2h_points, h2h_gf - h2h_ga, h2h_gf) # Points, GD, GF in H2H

        # We sort by:
        # 1. H2H Key (Points, GD, GF in mini-league)
        # 2. Global GD
        # 3. Global GF
        
        group.sort(key=lambda t: (
            h2h_key(t),                 # Tuple (PTS, GD, GF) in H2H
            t.goal_difference,          # Global GD
            t.goals_scored              # Global GF
        ), reverse=True)
