# 🏆 Struttura Fase Finale (Playoff)

Questo documento spiega come il sistema (`tournament.py`) calcola e genera automaticamente le partite dopo la fine del campionato.

## 1. Condizione di Attivazione
Il sistema genera i playoff **SOLO** quando tutte le **28 partite** del calendario regolare sono terminate (ovvero hanno un risultato registrato in `matches.json`).

## 2. Nuovo Formato (Top 6 "Legendary")
Si qualificano le prime **6 squadre** della classifica. 7° e 8° sono eliminate.

### Tabellone
1.  **Quarti di Finale (Gara Secca)**:
    *   **QF1**: 3° Classificato vs 6° Classificato
    *   **QF2**: 4° Classificato vs 5° Classificato
    *   *(1° e 2° Classificato attendono in Semifinale)*

2.  **Semifinali (Gara Secca)**:
    *   **SF1**: 1° Classificato vs Vincente QF1
    *   **SF2**: 2° Classificato vs Vincente QF2

3.  **FINALISSIMA**:
    *   Vincente SF1 vs Vincente SF2

### Visualizzazione
Sulla pagina web apparirà un **Tabellone Leggendario** sopra la classifica, con stile epico (oro/nero), che mostrerà il percorso verso la coppa.

## 3. Dettagli Tecnici
*   **Casa/Fuori**: In base al piazzamento (il migliore gioca in casa/prima nel JSON, ma essendo gara secca il campo è neutro/virtuale).
*   **Pareggi**: In caso di pareggio nei 90', il sistema si aspetta un vincitore (rigori).

---
*Nota: La logica è gestita automaticamente da `tournament.py`.*
