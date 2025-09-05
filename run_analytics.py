"""
ANALYTICS ULTRA-SIMPLE - 3 lignes de code

Utilisation directe des 3 calculs analytiques demandés
"""

from analytics_simple import stock_journalier, suivi_nouveaux_clients, chiffre_affaires_mensuel
from datetime import datetime

# ✅ VOS PARAMÈTRES ICI
stocks = {1: 100, 4: 200, 10: 140, 14: 175, 15: 105, 17: 155}
date = datetime(2024, 5, 3)

# ✅ LES 3 CALCULS EN 3 LIGNES
print("1️⃣ STOCK JOURNALIER = (stock initial - commandes)")
stock_journalier(date, stocks)

print("\n2️⃣ SUIVI DES NOUVEAUX CLIENTS") 
suivi_nouveaux_clients(datetime(2024, 5, 1), datetime(2024, 5, 10))

print("\n3️⃣ CHIFFRE D'AFFAIRES MENSUEL")
chiffre_affaires_mensuel(2024, 5)
