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
    # Initialize teams structure
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
    
    # Process matches
    for m in matches:
        # Register teams even if no result yet
        teams[m["squadra_a"]]["squadra"] = m["squadra_a"]
        teams[m["squadra_b"]]["squadra"] = m["squadra_b"]

        if m.get("risultato") is None:
            continue
            
        team_a = m["squadra_a"]
        team_b = m["squadra_b"]
        
        try:
            ga = int(m.get("gol_a", 0))
            gb = int(m.get("gol_b", 0))
        except (ValueError, TypeError):
            continue 
            
        res = m["risultato"]
        
        # Update General Stats
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
                pts_a, pts_b = 3, 0
                teams[team_a]["vittorie"] += 1
                teams[team_b]["sconfitte"] += 1
            elif gb > ga:
                pts_a, pts_b = 0, 3
                teams[team_b]["vittorie"] += 1
                teams[team_a]["sconfitte"] += 1
            else:
                pts_a, pts_b = 1, 1 
        elif res == RES_RIG_A:
            pts_a, pts_b = 2, 1
            teams[team_a]["vittorie_rig"] += 1
            teams[team_b]["sconfitte_rig"] += 1
        elif res == RES_RIG_B:
            pts_a, pts_b = 1, 2
            teams[team_b]["vittorie_rig"] += 1
            teams[team_a]["sconfitte_rig"] += 1
        elif res == "pareggio":
             pts_a, pts_b = 1, 1
        else:
            # Fallback based on score
            if ga > gb: 
                pts_a, pts_b = 3, 0
                teams[team_a]["vittorie"] += 1
                teams[team_b]["sconfitte"] += 1
            elif gb > ga: 
                pts_a, pts_b = 0, 3
                teams[team_b]["vittorie"] += 1
                teams[team_a]["sconfitte"] += 1
            else: 
                pts_a, pts_b = 1, 1

        teams[team_a]["punti"] += pts_a
        teams[team_b]["punti"] += pts_b
        
        # Update H2H Stats
        teams[team_a]["h2h"][team_b]["punti"] += pts_a
        teams[team_a]["h2h"][team_b]["gf"] += ga
        teams[team_a]["h2h"][team_b]["gs"] += gb
        
        teams[team_b]["h2h"][team_a]["punti"] += pts_b
        teams[team_b]["h2h"][team_a]["gf"] += gb
        teams[team_b]["h2h"][team_a]["gs"] += ga
        teams[team_b]["h2h"][team_a]["away_goals"] += gb

    # Calculate Goal Difference
    for t_data in teams.values():
        t_data["differenza_reti"] = t_data["gol_fatti"] - t_data["gol_subiti"]

    ranking = list(teams.values())
    
    # Sorting: 1. Points
    ranking.sort(key=lambda x: x["punti"], reverse=True)
    
    # Resolve Ties (Sub-groups)
    def resolve_ties(group):
        if len(group) <= 1: return group
        
        relevant_teams = set(t["squadra"] for t in group)
        mini_table = {t: {"gf": 0, "gs": 0, "ag": 0} for t in relevant_teams}
        
        for m in matches:
            if m.get("risultato") is None: continue
            ta, tb = m["squadra_a"], m["squadra_b"]
            if ta in relevant_teams and tb in relevant_teams:
                 ga = int(m.get("gol_a", 0))
                 gb = int(m.get("gol_b", 0))
                 
                 mini_table[ta]["gf"] += ga; mini_table[ta]["gs"] += gb
                 mini_table[tb]["gf"] += gb; mini_table[tb]["gs"] += ga
                 mini_table[tb]["ag"] += gb
        
        def tie_key(t):
            name = t["squadra"]
            mt = mini_table[name]
            return (
                mt["gf"] - mt["gs"],   # 1. H2H Diff
                mt["ag"],              # 2. H2H Away Goals
                t["differenza_reti"],  # 3. Global Diff
                t["gol_fatti"]         # 4. Global GF
            )
            
        return sorted(group, key=tie_key, reverse=True)

    final_ranking = []
    i = 0
    while i < len(ranking):
        j = i + 1
        while j < len(ranking) and ranking[j]["punti"] == ranking[i]["punti"]:
            j += 1
        final_ranking.extend(resolve_ties(ranking[i:j]))
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
