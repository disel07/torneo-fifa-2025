import json
from ranking_system import Tournament

def main():
    try:
        with open("matches.json", "r") as f:
            matches_data = json.load(f)
    except FileNotFoundError:
        print("matches.json not found. Creating empty list.")
        matches_data = []

    tournament = Tournament()
    tournament.load_matches(matches_data)
    ranking = tournament.calculate_ranking()

    with open("classifica.json", "w") as f:
        json.dump(ranking, f, indent=4)
    
    print("Ranking calculated and saved to classifica.json")
    print(json.dumps(ranking, indent=2))

if __name__ == "__main__":
    main()
