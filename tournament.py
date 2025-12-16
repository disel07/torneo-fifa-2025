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
    Gestisce la fase playoff (Top 6):
    1. Quarti (Gara Unica):
       - QF1: 3° vs 6°
       - QF2: 4° vs 5°
       (1° e 2° aspettano in semifinale)
    2. Semifinali (Gara Unica):
       - SF1: 1° vs Vincente QF1
       - SF2: 2° vs Vincente QF2
    3. Finalissima:
       - Vincente SF1 vs Vincente SF2
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
    
    if matches_played < total_league_matches:
        print(f"Campionato non finito ({matches_played}/{total_league_matches}). Niente playoff per ora.")
        return

    # League Finished!
    # Ranking: 0=1st, 1=2nd, 2=3rd, 3=4th, 4=5th, 5=6th
    
    # Helper to find a match by ID
    def find_match(pid):
        for m in playoffs:
            if m["id"] == pid: return m
        return None

    # Helper to get winner
    def get_winner(match):
        if not match or not match.get("risultato"): return None
        res = match["risultato"]
        ga = int(match["gol_a"])
        gb = int(match["gol_b"])
        team_a = match["squadra_a"]
        team_b = match["squadra_b"]

        if res == RES_90:
            if ga > gb: return team_a
            if gb > ga: return team_b
            return None 
        elif res == RES_RIG_A: return team_a
        elif res == RES_RIG_B: return team_b
        
        # Fallback
        if ga > gb: return team_a
        if gb > ga: return team_b
        return None

    changed = False

    # --- QUARTI DI FINALE ---
    # QF1: 3rd vs 6th
    qf1 = find_match("QF1")
    if not qf1:
        print("Generazione Quarto 1: 3° vs 6°")
        qf1 = {
            "id": "QF1",
            "type": "quarti",
            "giornata": "Playoff - Quarti",
            "squadra_a": ranking[2]["squadra"], # 3rd
            "squadra_b": ranking[5]["squadra"], # 6th
            "gol_a": None, "gol_b": None, "risultato": None
        }
        playoffs.append(qf1)
        changed = True

    # QF2: 4th vs 5th
    qf2 = find_match("QF2")
    if not qf2:
        print("Generazione Quarto 2: 4° vs 5°")
        qf2 = {
            "id": "QF2",
            "type": "quarti",
            "giornata": "Playoff - Quarti",
            "squadra_a": ranking[3]["squadra"], # 4th
            "squadra_b": ranking[4]["squadra"], # 5th
            "gol_a": None, "gol_b": None, "risultato": None
        }
        playoffs.append(qf2)
        changed = True

    # --- SEMIFINALI ---
    # Need winners of QFs
    winner_qf1 = get_winner(qf1)
    winner_qf2 = get_winner(qf2)
    
    # SF1: 1st vs Winner QF1
    sf1 = find_match("SF1")
    if winner_qf1:
        target_a = ranking[0]["squadra"] # 1st
        target_b = winner_qf1
        
        if not sf1:
            print(f"Generazione Semifinale 1: {target_a} vs {target_b}")
            sf1 = {
                "id": "SF1",
                "type": "semifinale",
                "giornata": "Playoff - Semifinali",
                "squadra_a": target_a,
                "squadra_b": target_b,
                "gol_a": None, "gol_b": None, "risultato": None
            }
            playoffs.append(sf1)
            changed = True
        else:
             # Update if placeholders change (unlikely)
             if sf1["squadra_b"] != target_b:
                 sf1["squadra_b"] = target_b
                 changed = True

    # SF2: 2nd vs Winner QF2
    sf2 = find_match("SF2")
    if winner_qf2:
        target_a = ranking[1]["squadra"] # 2nd
        target_b = winner_qf2
        
        if not sf2:
            print(f"Generazione Semifinale 2: {target_a} vs {target_b}")
            sf2 = {
                "id": "SF2",
                "type": "semifinale",
                "giornata": "Playoff - Semifinali",
                "squadra_a": target_a,
                "squadra_b": target_b,
                "gol_a": None, "gol_b": None, "risultato": None
            }
            playoffs.append(sf2)
            changed = True
        else:
             if sf2["squadra_b"] != target_b:
                 sf2["squadra_b"] = target_b
                 changed = True
    
    # --- FINALISSIMA ---
    winner_sf1 = get_winner(sf1)
    winner_sf2 = get_winner(sf2)
    
    final = find_match("FINAL")
    if winner_sf1 and winner_sf2:
        if not final:
            print(f"Generazione Finalissima: {winner_sf1} vs {winner_sf2}")
            final = {
                "id": "FINAL",
                "type": "finalissima",
                "giornata": "Finalissima",
                "squadra_a": winner_sf1,
                "squadra_b": winner_sf2,
                "gol_a": None, "gol_b": None, "risultato": None
            }
            playoffs.append(final)
            changed = True
        else:
             if final["squadra_a"] != winner_sf1 or final["squadra_b"] != winner_sf2:
                 final["squadra_a"] = winner_sf1
                 final["squadra_b"] = winner_sf2
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
