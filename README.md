# ⚽ Torneo FIFA 2025

Sistema di gestione classifica e calendario per il torneo di FIFA 2025.

## 🚀 Caratteristiche
- **Calcolo automatico**: Script Python che legge i risultati e genera la classifica.
- **Logica Tiebreaker**:
    1. Punti
    2. Scontri diretti (diff. reti H2H, gol fuori casa H2H)
    3. Differenza reti totale
    4. Gol fatti totali
- **Dashboard Cyberpunk**: Interfaccia web moderna Dark/Neon aggiornata in tempo reale.
- **Automazione**: GitHub Actions aggiorna la classifica ad ogni push.

## 📂 Struttura
- `matches.json`: Database delle partite.
- `classifica.json`: Output generato (NON modificare manualmente).
- `tournament.py`: Motore logico.
- `index.html`: Dashboard Frontend.

## 🛠 Installazione
1. Clona la repository.
2. Assicurati di avere Python 3.9+.
3. Apri `index.html` nel browser.

## 📝 Utilizzo
Vedi [GUIDA_UTENTE.md](GUIDA_UTENTE.md) per istruzioni dettagliate su come inserire i risultati.
