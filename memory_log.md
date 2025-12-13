# 🧠 MEMORY LOG - TORNEO FIFA 2025

**Data Creazione:** 2025-12-13
**Repository:** [https://github.com/disel07/torneo-fifa-2025.git](https://github.com/disel07/torneo-fifa-2025.git)

---

## 📋 Riepilogo Progetto
Sistema autonomo per la gestione del Torneo FIFA 2025. Il sistema calcola automaticamente la classifica basandosi sui risultati inseriti in un file JSON e pubblica una dashboard web aggiornata.

### ⚙️ Componenti Chiave
| File | Scopo |
| :--- | :--- |
| `matches.json` | **Database**. Contiene il calendario di tutte le 20 partite e i risultati. File principale da modificare. |
| `tournament.py` | **Motore**. Script Python che legge `matches.json`, calcola i punti e i tiebreaker, e genera `classifica.json`. |
| `index.html` | **Frontend**. Dashboard Cyberpunk che legge i JSON e mostra classifica e calendario. Live su GitHub Pages. |
| `.github/workflows/update-standings.yml` | **Automazione**. Workflow che esegue `tournament.py` automaticamente ad ogni push su GitHub. |
| `classifica.json` | **Output**. File generato automaticamente dal motore. Non modificare a mano. |

### 📐 Logica Classifica (Tiebreakers)
L'ordine di classifica segue rigorosamente queste regole (già implementate in `tournament.py`):
1.  **Punti Totali** (V=3, Rigori V=2, Rigori P=1, S=0).
2.  **Scontri Diretti** (Se pari punti: chi ha vinto nel complessivo dei match tra i pareggiati).
3.  **Gol Fuori Casa Scontri Diretti** (Se parità assoluta negli scontri diretti).
4.  **Differenza Reti Totale**.
5.  **Gol Fatti Totali**.

---

## 🚀 Istruzioni Migrazione (Nuovo PC)

Per riprendere il lavoro sul portatile, segui questi passaggi:

### 1. Clona la Repository
Apri il terminale (o Git Bash) e scarica il progetto:
```bash
git clone https://github.com/disel07/torneo-fifa-2025.git
cd torneo-fifa-2025
```

### 2. Requisiti di Sistema
Assicurati di avere **Python 3** installato. Verifica con:
```bash
python3 --version
# oppure
python --version
```

### 3. Workflow di Aggiornamento
#### Metodo Veloce (Online)
Non serve installare nulla sul PC se modifichi direttamente da GitHub.com (vedi `GUIDA_UTENTE.md` sezione "Metodo Flash").

#### Metodo Locale (Offline/Terminale)
1. Modifica `matches.json` con i nuovi risultati.
2. (Opzionale) Testa la classifica localmente:
   ```bash
   python3 tournament.py
   # Apri index.html nel browser per vedere il risultato
   ```
3. Carica online:
   ```bash
   git add matches.json
   git commit -m "Aggiornati risultati"
   git push
   ```

### ⚠️ Note Importanti
- **NON modificare `classifica.json` manualmente**. Viene sovrascritto automaticamente.
- Se GitHub Actions fallisce, controlla il tab "Actions" su GitHub per vedere l'errore.
- Il design è contenuto tutto in `index.html` (CSS/JS inclusi), non ci sono file esterni.

---

## 🧪 Stato Attuale
- **Test:** Tutti i unit test (`test_tournament.py`) passano correttamente.
- **Dati:** `matches.json` contiene calendario completo e 1 risultato di prova (Giornata 1).
- **Deploy:** Configurato su GitHub Pages (branch `main`).
