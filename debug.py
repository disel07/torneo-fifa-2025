import json
try:
    with open('matches.json', 'r') as f:
        data = json.load(f)
        print(f"Loaded {len(data)} matches.")
        if len(data) > 0:
            print("First match keys:", data[0].keys())
            print("First match content:", data[0])
            if 'squadra_a' in data[0]:
                print("Found squadra_a")
            else:
                print("Missing squadra_a")
except Exception as e:
    print(e)
