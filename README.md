# Torneo di Calcio - Classifica Automatica

Questo progetto gestisce la classifica di un torneo di calcio. La classifica viene calcolata automaticamente da GitHub Actions ogni volta che il file dei risultati (`matches.json`) viene aggiornato.

## Come funziona
1. I risultati delle partite sono salvati in `matches.json`.
2. Quando fai un commit e push di modifiche a `matches.json`, parte un'automazione.
3. Lo script `tournament.py` calcola la nuova classifica.
4. Il file `classifica.json` viene aggiornato e committato automaticamente nel repository.
5. La pagina web (`index.html`) legge `classifica.json` e mostra la classifica aggiornata (tramite fetch JS o caricamento statico nel workflow, a seconda della configurazione).

## Link Utili
- **Sito Web Classifica**: [Inserisci qui il link di GitHub Pages una volta attivo]
- **Risultati (JSON)**: `matches.json`
