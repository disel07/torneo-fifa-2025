import json
import datetime
from collections import defaultdict
import operator

# Constants for result types
RES_90 = "90"
RES_RIG_A = "rigori_a"
RES_RIG_B = "rigori_b"
RES_DRAW = "pareggio" # Should not happen in tournament with penalties but kept for safety

def load_matches(filepath="matches.json"):
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data.get("matches", [])
    except FileNotFoundError:
        return []

def calculate_standings(matches):
    # Initialize teams
    teams = defaultdict(lambda: {
        "squadra": "",
        "giornate": 0,
        "gol_fatti": 0,
        "gol_subiti": 0,
        "differenza_reti": 0,
        "punti": 0,
        "h2h": defaultdict(lambda: {"punti": 0, "gf": 0, "gs": 0, "away_goals": 0}) 
    })
    
    # Pre-scan to ensure all teams are in the dict even if they haven't played
    # But since we have a fixed set of matches, we can just rely on the match loop
    # or better, iterate over all matches to find unique teams first.
    all_teams_set = set()
    for m in matches:
        all_teams_set.add(m["squadra_a"])
        all_teams_set.add(m["squadra_b"])
    
    for t in all_teams_set:
        teams[t]["squadra"] = t

    for m in matches:
        if m.get("risultato") is None:
            continue
            
        team_a = m["squadra_a"]
        team_b = m["squadra_b"]
        
        try:
            ga = int(m.get("gol_a", 0))
            gb = int(m.get("gol_b", 0))
        except (ValueError, TypeError):
            continue # Skip invalid match data
            
        res = m["risultato"]
        
        # Update stats
        teams[team_a]["giornate"] += 1
        teams[team_b]["giornate"] += 1
        teams[team_a]["gol_fatti"] += ga
        teams[team_b]["gol_fatti"] += gb
        teams[team_b]["gol_subiti"] += ga
        teams[team_a]["gol_subiti"] += gb
        
        # Points Logic
        pts_a = 0
        pts_b = 0
        
        if res == RES_90:
            if ga > gb:
                pts_a = 3
                pts_b = 0
            elif gb > ga:
                pts_a = 0
                pts_b = 3
            else:
                 # Should not happen with "90" unless draw which is not allowed usually without penalties info
                 # But if result is "pareggio", treat as 1-1
                 pts_a = 1
                 pts_b = 1
        elif res == RES_RIG_A:
            pts_a = 2
            pts_b = 1
        elif res == RES_RIG_B:
            pts_a = 1
            pts_b = 2
        elif res == "pareggio":
             pts_a = 1
             pts_b = 1
        else:
            # Fallback for simple wins marked as "90" but maybe user just put scores
            if ga > gb: pts_a = 3; pts_b = 0
            elif gb > ga: pts_a = 0; pts_b = 3
            else: pts_a = 1; pts_b = 1

        teams[team_a]["punti"] += pts_a
        teams[team_b]["punti"] += pts_b
        
        # H2H Verification
        # Update H2H stats for specific matchup
        teams[team_a]["h2h"][team_b]["punti"] += pts_a
        teams[team_a]["h2h"][team_b]["gf"] += ga
        teams[team_a]["h2h"][team_b]["gs"] += gb
        # Away goals logic: team_b is AWAY in this match (if m['squadra_b'] == team_b)
        # Actually structure implies A vs B. A is Home, B is Away.
        # So B gets away goals.
        teams[team_b]["h2h"][team_a]["away_goals"] += gb
        
        teams[team_b]["h2h"][team_a]["punti"] += pts_b
        teams[team_b]["h2h"][team_a]["gf"] += gb
        teams[team_b]["h2h"][team_a]["gs"] += ga
        # A was Home, so no away goals for A in this match.

    # Derived stats
    for t_name, t_data in teams.items():
        t_data["differenza_reti"] = t_data["gol_fatti"] - t_data["gol_subiti"]

    # Convert to list for sorting
    ranking = list(teams.values())
    
    # Sorting Logic (The complex part)
    # Tiebreakers: 
    # 1. Punti
    # 2. H2H (Points in matches between tied teams -> Goal Diff in h2h -> Away goals in h2h?)
    #    The prompt says: "Scontri diretti: confronta gol fatti vs subiti nei match diretti". 
    #    Implies: Points in H2H first? Or just aggregate score? "Guido 2-2 Filippo e Guido 3-2 Filippo -> Guido ha vinto 5-4" -> This is Aggregate Score.
    #    So H2H Metric = (H2H_GF - H2H_GS).
    # 3. Diff Reti Totale
    # 4. Gol Fatti Totali
    
    def comparison_key(team):
        # We can't easily use a simple key for H2H because it depends on WHO you are tied with.
        # This requires a custom sort or iterative grouping.
        return team["punti"]

    # Simple sort first by points
    ranking.sort(key=lambda x: x["punti"], reverse=True)
    
    # Resolve ties
    # We will implement a custom comparator or iterative bubble sort-like approach for groups of tied teams.
    # Since N=5, we can be robust.
    
    def resolve_ties(group):
        if len(group) <= 1:
            return group
        
        # Check H2H within this specific group
        # Calculate a "mini-league" for the tied teams
        mini_table = {t["squadra"]: {"pts": 0, "gf": 0, "gs": 0, "ag": 0} for t in group}
        
        # Re-scan matches to find those involving ONLY teams in this group
        # Actually we can use the h2h dict we built if simpler, but full scan is safer for multi-way ties
        # The h2h dict is pairwise. For a 3-way tie (A, B, C), we need matches A-B, B-C, A-C.
        
        relevant_teams = set([t["squadra"] for t in group])
        
        for m in matches:
            if m.get("risultato") is None: continue
            ta = m["squadra_a"]
            tb = m["squadra_b"]
            if ta in relevant_teams and tb in relevant_teams:
                 # Recalculate generic points/goals for this mini-league
                 # Note: Prompt example "Guido 2-2 ... Guido 3-2 ... Guido ha vinto 5-4" implies Aggregate Score (Goals) is the metric.
                 # Let's calculate Aggregate Goals Difference in matches between them.
                 
                 # Re-parse result just to be sure
                 ga = int(m.get("gol_a", 0))
                 gb = int(m.get("gol_b", 0))
                 
                 mini_table[ta]["gf"] += ga
                 mini_table[ta]["gs"] += gb
                 mini_table[tb]["gf"] += gb
                 mini_table[tb]["gs"] += ga
                 
                 # Away goals
                 mini_table[tb]["ag"] += gb
                 # ta is home, no away goals
        
        # Sort group based on criteria
        # 1. H2H Goal Diff (GF - GS in mini-table)
        # 2. H2H Away Goals (if needed by "valuta gol fuori casa")
        # 3. Global Diff Reti
        # 4. Global Gol Fatti
        
        def tie_key(t):
            name = t["squadra"]
            mt = mini_table[name]
            h2h_diff = mt["gf"] - mt["gs"]
            h2h_ag = mt["ag"]
            
            return (
                h2h_diff,          # 1. H2H Diff
                h2h_ag,            # 1b. H2H Away Goals (Prompt: "valuta gol fuori casa")
                t["differenza_reti"], # 2. Global Diff
                t["gol_fatti"]     # 3. Global GF
            )
            
        return sorted(group, key=tie_key, reverse=True)

    # Apply tiebreaker to sub-groups of equal points
    final_ranking = []
    i = 0
    while i < len(ranking):
        j = i + 1
        while j < len(ranking) and ranking[j]["punti"] == ranking[i]["punti"]:
            j += 1
        
        # Group from i to j-1 has same points
        group = ranking[i:j]
        sorted_group = resolve_ties(group)
        final_ranking.extend(sorted_group)
        i = j
        
    return final_ranking

def save_standings(ranking, filepath="classifica.json"):
    output = {
        "classifica": [],
        "ultimo_aggiornamento": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    for idx, team in enumerate(ranking, 1):
        # Remove h2h internal data for clean output
        t_clean = {k:v for k,v in team.items() if k != 'h2h'}
        t_clean["posizione"] = idx
        output["classifica"].append(t_clean)
        
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=4)
    print(f"Classifica aggiornata: {filepath}")

if __name__ == "__main__":
    matches = load_matches()
    ranking = calculate_standings(matches)
    save_standings(ranking)
