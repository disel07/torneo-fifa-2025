import json
import os

def load_matches():
    if os.path.exists("matches.json"):
        with open("matches.json", "r") as f:
            return json.load(f)
    return []

def save_matches(matches):
    with open("matches.json", "w") as f:
        json.dump(matches, f, indent=4)

def main():
    print("Add a new match result")
    matches = load_matches()
    
    # Simple auto-increment ID
    new_id = matches[-1]["id"] + 1 if matches else 1
    
    home_team = input("Home Team: ").strip()
    away_team = input("Away Team: ").strip()
    
    while True:
        try:
            home_score = int(input(f"Score {home_team}: "))
            break
        except ValueError:
            print("Invalid number")
            
    while True:
        try:
            away_score = int(input(f"Score {away_team}: "))
            break
        except ValueError:
            print("Invalid number")
    
    penalty_winner = None
    if home_score == away_score:
        print("Match drawn. Who won on penalties?")
        print(f"1. {home_team}")
        print(f"2. {away_team}")
        while True:
            choice = input("Choice (1/2): ").strip()
            if choice == "1":
                penalty_winner = home_team
                break
            elif choice == "2":
                penalty_winner = away_team
                break
            else:
                print("Invalid choice")
    
    match = {
        "id": new_id,
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
        "played": True
    }
    
    if penalty_winner:
        match["penalty_winner"] = penalty_winner
        
    matches.append(match)
    save_matches(matches)
    print("Match added successfully!")

if __name__ == "__main__":
    main()
