# Guida per l'Utente: Come Aggiornare i Risultati

Segui questa guida per inserire i nuovi risultati delle partite e aggiornare la classifica online.

## Prerequisiti
- Git installato sul computer.
- Accesso a questo repository.

## Passo 1: Aggiorna i dati sul tuo PC
1. Apri la cartella del progetto.
2. Apri il file `matches.json` con un editor di testo (es. Blocco Note, VS Code).
3. Aggiungi il nuovo risultato seguendo questo formato:
   ```json
   {
       "id": "11",
       "giornata": 6,
       "squadra_a": "Team A",
       "squadra_b": "Team C",
       "gol_a": 2,
       "gol_b": 1,
       "risultato": "90"
   },
   ```
   *Assicurati di aggiungere una virgola dopo la parentesi graffa di chiusura `}` dell'elemento precedente, se necessario.*
4. Salva il file.

## Passo 2: Invia le modifiche a Internet
Apri il terminale (o Prompt dei comandi) nella cartella del progetto ed esegui questi 3 comandi, uno alla volta:

```bash
git add matches.json
git commit -m "Aggiunto risultato giornata X"
git push
```

## Passo 3: Verifica
1. Vai sulla pagina GitHub del progetto, nella scheda **Actions**.
2. Vedrai un workflow in esecuzione (pallino giallo/verde).
3. Quando diventa verde, la classifica è aggiornata!
4. Visita il link del sito web per vedere la nuova classifica.
