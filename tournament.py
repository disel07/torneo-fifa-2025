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
        "vittorie": 0,
        "vittorie_rig": 0,
        "sconfitte_rig": 0,
        "sconfitte": 0,
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
                teams[team_a]["vittorie"] += 1
                teams[team_b]["sconfitte"] += 1
            elif gb > ga:
                pts_a = 0
                pts_b = 3
                teams[team_b]["vittorie"] += 1
                teams[team_a]["sconfitte"] += 1
            else:
                 # Should not happen with "90" unless draw which is not allowed usually without penalties info
                 # But if result is "pareggio", treat as 1-1
                 pts_a = 1
                 pts_b = 1
                 # Count as draw? Logic currently has no draw field, usually means penalties needed
        elif res == RES_RIG_A:
            pts_a = 2
            pts_b = 1
            teams[team_a]["vittorie_rig"] += 1
            teams[team_b]["sconfitte_rig"] += 1
        elif res == RES_RIG_B:
            pts_a = 1
            pts_b = 2
            teams[team_b]["vittorie_rig"] += 1
            teams[team_a]["sconfitte_rig"] += 1
        elif res == "pareggio":
             pts_a = 1
             pts_b = 1
        else:
            # Fallback for simple wins marked as "90" but maybe user just put scores
            if ga > gb: 
                pts_a = 3; pts_b = 0
                teams[team_a]["vittorie"] += 1
                teams[team_b]["sconfitte"] += 1
            elif gb > ga: 
                pts_a = 0; pts_b = 3
                teams[team_b]["vittorie"] += 1
                teams[team_a]["sconfitte"] += 1
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

def manage_playoffs(ranking):
    """
    Gestisce la fase playoff:
    1. Verifica se il campionato è finito.
    2. Genera le partite dei playoff se non esistono.
    3. Aggiorna lo stato dei playoff in base ai risultati.
    """
    filepath = "matches.json"
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        return

    league_matches = data.get("matches", [])
    playoffs = data.get("playoffs", [])
    
    # 1. Check if League is Finished
    matches_played = sum(1 for m in league_matches if m.get("risultato") is not None)
    total_league_matches = len(league_matches)
    
    # If league not finished, do nothing (or maybe update partials if needed, but safer to wait)
    # Removing this check for testing purposes? No, strictly follow logic to avoid premature generation.
    if matches_played < total_league_matches:
        print(f"Campionato non finito ({matches_played}/{total_league_matches}). Niente playoff per ora.")
        return

    # League Finished! We have the ranking.
    # Ranking is sorted: 0 is 1st, 1 is 2nd, etc.
    # 1st Place: ranking[0] -> Direct Final
    # 2nd Place: ranking[1]
    # 3rd Place: ranking[2]
    # 4th Place: ranking[3]
    # 5th Place: ranking[4]
    
    # Helper to find a match by ID
    def find_match(pid):
        for m in playoffs:
            if m["id"] == pid: return m
        return None

    # Helper to get winner
    def get_winner(match):
        if not match or not match.get("risultato"): return None
        # Logic to determine winner based on score/penalties
        # match has 'gol_a', 'gol_b', 'risultato'
        res = match["risultato"]
        ga = int(match["gol_a"])
        gb = int(match["gol_b"])
        
        team_a = match["squadra_a"]
        team_b = match["squadra_b"]

        if res == RES_90:
            if ga > gb: return team_a
            if gb > ga: return team_b
            # Draw at 90 not usually allowed in elimination without penalties, but if so...
            return None # Ambiguous
        elif res == RES_RIG_A: return team_a
        elif res == RES_RIG_B: return team_b
        elif res == "pareggio": return None # Should trigger replay or penalties
        
        # Fallback
        if ga > gb: return team_a
        if gb > ga: return team_b
        return None

    changed = False

    # --- SEMIFINALS ---
    # SF1: 2nd vs 5th (2nd Home)
    sf1 = find_match("P1")
    if not sf1:
        print("Generazione Semifinale 1: 2° vs 5°")
        sf1 = {
            "id": "P1",
            "type": "semifinale",
            "giornata": "Playoff Semifinali",
            "squadra_a": ranking[1]["squadra"], # 2nd
            "squadra_b": ranking[4]["squadra"], # 5th
            "gol_a": None, "gol_b": None, "risultato": None
        }
        playoffs.append(sf1)
        changed = True

    # SF2: 3rd vs 4th (3rd Home)
    sf2 = find_match("P2")
    if not sf2:
        print("Generazione Semifinale 2: 3° vs 4°")
        sf2 = {
            "id": "P2",
            "type": "semifinale",
            "giornata": "Playoff Semifinali",
            "squadra_a": ranking[2]["squadra"], # 3rd
            "squadra_b": ranking[3]["squadra"], # 4th
            "gol_a": None, "gol_b": None, "risultato": None
        }
        playoffs.append(sf2)
        changed = True

    # --- PLAYOFF FINAL ---
    # Winner SF1 vs Winner SF2
    # Check if Semis have winners
    winner_sf1 = get_winner(sf1)
    winner_sf2 = get_winner(sf2)
    
    pf_final = find_match("P3")
    if winner_sf1 and winner_sf2:
        if not pf_final:
            print(f"Generazione Finale Playoff: {winner_sf1} vs {winner_sf2}")
            pf_final = {
                "id": "P3",
                "type": "finale_playoff",
                "giornata": "Finale Playoff",
                "squadra_a": winner_sf1,
                "squadra_b": winner_sf2,
                "gol_a": None, "gol_b": None, "risultato": None
            }
            playoffs.append(pf_final)
            changed = True
        else:
            # Update participants if changed (unlikely unless rerun)
            if pf_final["squadra_a"] != winner_sf1 or pf_final["squadra_b"] != winner_sf2:
                 pf_final["squadra_a"] = winner_sf1
                 pf_final["squadra_b"] = winner_sf2
                 changed = True
    
    # --- TOURNAMENT FINAL ---
    # 1st Place vs Winner Playoff Final
    winner_pf = get_winner(pf_final)
    first_place = ranking[0]["squadra"]
    
    grand_final = find_match("P4")
    if winner_pf:
        if not grand_final:
            print(f"Generazione Finalissima: {first_place} vs {winner_pf}")
            grand_final = {
                "id": "P4",
                "type": "finalissima",
                "giornata": "Finalissima",
                "squadra_a": first_place,
                "squadra_b": winner_pf,
                "gol_a": None, "gol_b": None, "risultato": None
            }
            playoffs.append(grand_final)
            changed = True
        else:
             if grand_final["squadra_a"] != first_place or grand_final["squadra_b"] != winner_pf:
                 grand_final["squadra_a"] = first_place
                 grand_final["squadra_b"] = winner_pf
                 changed = True

    if changed:
        data["playoffs"] = playoffs
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print("Playoff aggiornati in matches.json")
    else:
        print("Nessun cambiamento nei playoff.")

if __name__ == "__main__":
    matches = load_matches()
    ranking = calculate_standings(matches)
    save_standings(ranking)
    manage_playoffs(ranking)
