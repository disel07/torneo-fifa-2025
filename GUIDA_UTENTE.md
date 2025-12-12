# Guida Utente - Torneo FIFA 2025

Questa guida spiega come gestire il torneo e aggiornare i risultati.

## 1. Inserire un nuovo risultato
Tutti i dati sono salvati in `matches.json`.

1. Apri `matches.json` con un editor di testo o IDE.
2. Trova la partita da aggiornare (cerca per ID o nomi squadre).
3. Modifica i campi:
   - `gol_a`: Gol squadra A (numerico)
   - `gol_b`: Gol squadra B (numerico)
   - `risultato`:
     - `"90"`: Vittoria nei 90 minuti.
     - `"pareggio"`: Pareggio (non previsto dal regolamento ma gestito).
     - `"rigori_a"`: Squadra A vince ai rigori (2 pt vs 1 pt).
     - `"rigori_b"`: Squadra B vince ai rigori (1 pt vs 2 pt).

**Esempio:**
```json
{
    "id": 1,
    "giornata": 1,
    "squadra_a": "Guido (Real Madrid)",
    "squadra_b": "Filippo (PSG)",
    "gol_a": 3,
    "gol_b": 3,
    "risultato": "rigori_a"
}
```

## 2. Aggiornare la classifica (Locale)
Se vuoi vedere la classifica aggiornata sul tuo computer:

1. Apri il terminale nella cartella del progetto.
2. Esegui:
   ```bash
   python3 tournament.py
   ```
3. Il file `classifica.json` verrà aggiornato.
4. Ricarica `index.html` nel browser.

## 3. Aggiornare il sito online (GitHub)
Se il progetto è su GitHub:

1. Fai le modifiche a `matches.json`.
2. Esegui i comandi git:
   ```bash
   git add matches.json
   git commit -m "Aggiornato risultato giornata X"
   git push
   ```
3. Aspetta circa 1-2 minuti.
4. Visita il sito pubblicato su GitHub Pages. La classifica si aggiornerà automaticamente grazie alle GitHub Actions.
