#!/bin/bash
echo "=== ESECUZIONE TEST ==="
python3 -m unittest test_tournament.py -v

if [ $? -eq 0 ]; then
    echo ""
    echo "=== TUTTI I TEST PASSATI ==="
    echo "Generazione classifica..."
    python3 tournament.py
    echo "Ecco la classifica:"
    cat classifica.json
else
    echo "ERRORE: I test sono falliti."
fi
