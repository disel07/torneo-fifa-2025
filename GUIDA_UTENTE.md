# 📖 Guida Semplice - Torneo FIFA 2025

Ecco come gestire il tuo torneo in pochi passi.

## 1. Aggiornare i Risultati ⚽
Tutti i dati delle partite sono nel file `matches.json`.

1.  Apri il file `matches.json` (basta un doppioclick o tasto destro -> Apri con Blocco Note/TextEditor).
2.  Cerca la partita che hanno appena giocato (es. *Guido vs Filippo*).
3.  Modifica solo questi 3 numeri:
    *   `"gol_a"`: I gol della prima squadra.
    *   `"gol_b"`: I gol della seconda squadra.
    *   `"risultato"`: Scrivi chi ha vinto:
        *   `"90"` -> Se la partita è finita ai tempi regolamentari.
        *   `"rigori_a"` -> Se la prima squadra ha vinto ai rigori.
        *   `"rigori_b"` -> Se la seconda squadra ha vinto ai rigori.

**Esempio Pratico:**
Se Guido vince 3 a 2 contro Filippo ai tempi regolamentari:
```json
"gol_a": 3,
"gol_b": 2,
"risultato": "90"
```

## 2. Calcolare la Classifica 📈
Dopo aver salvato `matches.json`:

1.  Apri la cartella del progetto.
2.  Fai doppio click sul file `run.sh` (o esegui `python3 tournament.py` dal terminale se preferisci).
3.  Questo aggiornerà automaticamente la classifica e il sito.

## 3. Vedere la Classifica 💻
Basta aprire il file `index.html` con il tuo browser (Chrome, Safari, Edge).
Vedrai la classifica aggiornata, le statistiche e le prossime partite.

## 🏆 Playoff (Automatici)
Non devi fare nulla!
Quando avrai inserito **tutti i risultati** delle 20 partite di campionato:
1.  Il sistema creerà **automaticamente** le partite delle Semifinali in fondo alla lista delle partite.
2.  Giocate le semifinali e inserite i risultati come sempre.
3.  Il sistema creerà automaticamente la Finale Playoff e poi la Finalissima.

Divertitevi! 🎮
