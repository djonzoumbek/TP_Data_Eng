"""
Analytics simple pour ecommerce - 3 calculs essentiels

Ce module fournit les 3 calculs analytiques de base :
1. Stock journalier = (stock initial - commandes)
2. Suivi des nouveaux clients
3. Chiffre d'affaires mensuel
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict

DATA_DIR = "data"
ENRICHED_DATA_DIR = os.path.join(DATA_DIR, "enriched_data")


def stock_journalier(date, stock_initial: Dict[int, int]):
    """
    Calcule le stock journalier : stock initial - commandes
    
    Args:
        date: Date pour le calcul
        stock_initial: Dictionnaire {product_id: quantité_initiale}
        
    Returns:
        DataFrame avec stock_initial, quantité_vendue, stock_restant
    """
    try:
        # Charger les commandes du jour
        orders_path = os.path.join(ENRICHED_DATA_DIR, "orders", 
                                  str(date.year), str(date.month), f"{date.day}.parquet")
        
        if not os.path.exists(orders_path):
            print(f"Pas de commandes pour {date.strftime('%Y-%m-%d')}")
            return pd.DataFrame()
        
        df_orders = pd.read_parquet(orders_path)
        
        # Calculer les quantités vendues par produit
        ventes = df_orders.groupby('product_id')['quantity'].sum()
        
        # Créer le résultat
        resultats = []
        for product_id, stock_init in stock_initial.items():
            quantite_vendue = ventes.get(product_id, 0)
            stock_restant = stock_init - quantite_vendue
            
            resultats.append({
                'product_id': product_id,
                'stock_initial': stock_init,
                'quantite_vendue': quantite_vendue,
                'stock_restant': stock_restant
            })
        
        df_result = pd.DataFrame(resultats)
        print(f"Stock calculé pour {date.strftime('%Y-%m-%d')} :")
        print(df_result.to_string(index=False))
        
        return df_result
        
    except Exception as e:
        print(f"Erreur calcul stock : {e}")
        return pd.DataFrame()


def suivi_nouveaux_clients(date_debut, date_fin):
    """
    Suit les nouveaux clients jour par jour
    
    Args:
        date_debut: Date de début
        date_fin: Date de fin
        
    Returns:
        DataFrame avec nouveaux clients par jour
    """
    try:
        clients_deja_vus = set()
        resultats = []
        
        current_date = date_debut
        while current_date <= date_fin:
            orders_path = os.path.join(ENRICHED_DATA_DIR, "orders",
                                      str(current_date.year), str(current_date.month), 
                                      f"{current_date.day}.parquet")
            
            nouveaux_clients_jour = 0
            revenus_nouveaux = 0
            
            if os.path.exists(orders_path):
                df_orders = pd.read_parquet(orders_path)
                
                # Identifier les nouveaux clients
                clients_jour = set(df_orders['customer_id'].unique())
                nouveaux_clients = clients_jour - clients_deja_vus
                nouveaux_clients_jour = len(nouveaux_clients)
                
                # Calculer leurs revenus
                if nouveaux_clients:
                    df_nouveaux = df_orders[df_orders['customer_id'].isin(nouveaux_clients)]
                    revenus_nouveaux = df_nouveaux['total_amount'].sum()
                
                clients_deja_vus.update(clients_jour)
            
            resultats.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'nouveaux_clients': nouveaux_clients_jour,
                'revenus_nouveaux_clients': round(revenus_nouveaux, 2)
            })
            
            current_date += timedelta(days=1)
        
        df_result = pd.DataFrame(resultats)
        total_nouveaux = df_result['nouveaux_clients'].sum()
        total_revenus = df_result['revenus_nouveaux_clients'].sum()
        
        print(f"Suivi nouveaux clients du {date_debut.strftime('%Y-%m-%d')} au {date_fin.strftime('%Y-%m-%d')} :")
        print(df_result.to_string(index=False))
        print(f"\nTotal nouveaux clients : {total_nouveaux}")
        print(f"Total revenus nouveaux clients : {total_revenus:.2f}")
        
        return df_result
        
    except Exception as e:
        print(f"Erreur suivi clients : {e}")
        return pd.DataFrame()


def chiffre_affaires_mensuel(annee: int, mois: int):
    """
    Calcule le chiffre d'affaires mensuel
    
    Args:
        annee: Année (ex: 2024)
        mois: Mois (1-12)
        
    Returns:
        Dict avec les métriques mensuelles
    """
    try:
        # Parcourir tous les jours du mois
        ca_quotidien = []
        
        # Premier jour du mois
        premier_jour = datetime(annee, mois, 1)
        
        # Dernier jour du mois
        if mois == 12:
            dernier_jour = datetime(annee + 1, 1, 1) - timedelta(days=1)
        else:
            dernier_jour = datetime(annee, mois + 1, 1) - timedelta(days=1)
        
        current_date = premier_jour
        while current_date <= dernier_jour:
            orders_path = os.path.join(ENRICHED_DATA_DIR, "orders",
                                      str(current_date.year), str(current_date.month),
                                      f"{current_date.day}.parquet")
            
            ca_jour = 0
            nb_commandes = 0
            
            if os.path.exists(orders_path):
                df_orders = pd.read_parquet(orders_path)
                ca_jour = df_orders['total_amount'].sum()
                nb_commandes = len(df_orders)
            
            ca_quotidien.append({
                'jour': current_date.day,
                'ca_jour': ca_jour,
                'nb_commandes': nb_commandes
            })
            
            current_date += timedelta(days=1)
        
        # Calculer les totaux
        df_ca = pd.DataFrame(ca_quotidien)
        ca_total = df_ca['ca_jour'].sum()
        nb_commandes_total = df_ca['nb_commandes'].sum()
        ca_moyen_jour = ca_total / len(df_ca) if len(df_ca) > 0 else 0
        panier_moyen = ca_total / nb_commandes_total if nb_commandes_total > 0 else 0
        
        # Meilleur et pire jour
        meilleur_jour = df_ca.loc[df_ca['ca_jour'].idxmax()]
        pire_jour = df_ca.loc[df_ca['ca_jour'].idxmin()]
        
        resultats = {
            'annee': annee,
            'mois': mois,
            'ca_total': round(ca_total, 2),
            'nb_commandes_total': nb_commandes_total,
            'ca_moyen_par_jour': round(ca_moyen_jour, 2),
            'panier_moyen': round(panier_moyen, 2),
            'meilleur_jour': f"{meilleur_jour['jour']} ({meilleur_jour['ca_jour']:.2f})",
            'pire_jour': f"{pire_jour['jour']} ({pire_jour['ca_jour']:.2f})"
        }
        
        print(f"Chiffre d'affaires {annee}-{mois:02d} :")
        print(f"CA total : {resultats['ca_total']}")
        print(f"Nombre de commandes : {resultats['nb_commandes_total']}")
        print(f"CA moyen/jour : {resultats['ca_moyen_par_jour']}")
        print(f"Panier moyen : {resultats['panier_moyen']}")
        print(f"Meilleur jour : {resultats['meilleur_jour']}")
        print(f"Pire jour : {resultats['pire_jour']}")
        
        return resultats
        
    except Exception as e:
        print(f"Erreur calcul CA : {e}")
        return {}


def analyse_complete_simple(date, stock_initial: Dict[int, int]):
    """
    Effectue les 3 analyses en une fois pour une date donnée
    
    Args:
        date: Date à analyser
        stock_initial: Stocks initiaux
    """
    print(f"=== ANALYSE SIMPLE - {date.strftime('%Y-%m-%d')} ===")
    print("=" * 50)
    
    # 1. Stock journalier
    print("\n📦 STOCK JOURNALIER")
    print("-" * 20)
    stock_journalier(date, stock_initial)
    
    # 2. Nouveaux clients (juste pour ce jour)
    print("\n👥 NOUVEAUX CLIENTS")
    print("-" * 20)
    suivi_nouveaux_clients(date, date)
    
    # 3. CA mensuel
    print("\n💰 CHIFFRE D'AFFAIRES MENSUEL")
    print("-" * 30)
    chiffre_affaires_mensuel(date.year, date.month)


if __name__ == "__main__":
    # Exemple d'utilisation
    print("=== DEMO ANALYTICS SIMPLE ===")
    
    # Définir les stocks initiaux
    mes_stocks = {
        1: 100,   # Product_1
        4: 200,   # Product_4
        10: 140,  # Product_10
        14: 175,  # Product_14
        15: 105,  # Product_15
        17: 155   # Product_17
    }
    
    # Date à analyser
    date_analyse = datetime(2024, 5, 3)
    
    # Effectuer l'analyse complète
    analyse_complete_simple(date_analyse, mes_stocks)
    
    print("\n" + "="*50)
    print("✅ ANALYSE TERMINÉE !")
    print("\n🔧 UTILISATION :")
    print("1. Modifiez 'mes_stocks' avec vos vrais produits")
    print("2. Changez 'date_analyse' pour analyser d'autres jours")
    print("3. Utilisez les fonctions individuellement si besoin")
