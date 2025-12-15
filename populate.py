import json
import os

MATCHES_FILE = "matches.json"

def load_data():
    if os.path.exists(MATCHES_FILE):
        with open(MATCHES_FILE, "r") as f:
            return json.load(f)
    return {"matches": [], "playoffs": []}

def save_data(data):
    with open(MATCHES_FILE, "w") as f:
        json.dump(data, f, indent=4)

def main():
    data = load_data()
    matches = data.get("matches", [])
    
    if not matches:
        print("Nessuna partita trovata.")
        return

    # Filter unplayed matches or show all? Let's show unplayed first.
    unplayed = [m for m in matches if m.get("risultato") is None]
    
    if not unplayed:
        print("Tutte le partite sono state giocate!")
        # Optional: Allow editing played matches? 
        # For simplicity, stick to unplayed for now, or listing all would be too long.
    else:
        print(f"\n--- {len(unplayed)} Partite da giocare ---")
        # Show first 10
        for m in unplayed[:10]:
            print(f"ID: {m['id']} | G{m['giornata']} | {m['squadra_a']} vs {m['squadra_b']}")
        if len(unplayed) > 10:
            print("...")

    match_id = input("\nInserisci ID partita da aggiornare: ").strip()
    
    match = next((m for m in matches if str(m["id"]) == match_id), None)
    
    if not match:
        print("Partita non trovata.")
        return

    print(f"\nModifica risultato: {match['squadra_a']} vs {match['squadra_b']}")
    
    try:
        gol_a = int(input(f"Gol {match['squadra_a']}: "))
        gol_b = int(input(f"Gol {match['squadra_b']}: "))
    except ValueError:
        print("Valore non valido. Inserisci numeri interi.")
        return

    risultato = "90"
    if gol_a > gol_b:
        risultato = "90"
    elif gol_b > gol_a:
        risultato = "90"
    else:
        # Draw
        print("Pareggio! Chi ha vinto ai rigori?")
        print(f"1. {match['squadra_a']}")
        print(f"2. {match['squadra_b']}")
        choice = input("Scelta (1/2): ").strip()
        if choice == "1":
            risultato = "rigori_a"
        elif choice == "2":
            risultato = "rigori_b"
        else:
            print("Scelta non valida, salvataggio annullato.")
            return

    match["gol_a"] = gol_a
    match["gol_b"] = gol_b
    match["risultato"] = risultato
    
    save_data(data)
    print("Risultato salvato con successo!")

if __name__ == "__main__":
    main()
