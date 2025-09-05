"""
Data enrichment module for ecommerce analytics.

This module provides functions to enrich cleaned data with additional
calculated fields, business metrics, and analytical dimensions.
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import numpy as np

DATA_DIR = "data"
CLEAN_DATA_DIR = os.path.join(DATA_DIR, "clean_data")
ENRICHED_DATA_DIR = os.path.join(DATA_DIR, "enriched_data")


def _get_file_paths(data_type: str, date) -> tuple:
    """
    Génère les chemins d'entrée et de sortie pour l'enrichissement
    
    Args:
        data_type: Type de données ('clients', 'products', 'orders')
        date: Date des données
        
    Returns:
        tuple: (input_path, output_path)
    """
    input_path = os.path.join(CLEAN_DATA_DIR, data_type, str(date.year), str(date.month), f"{date.day}.parquet")
    output_dir = os.path.join(ENRICHED_DATA_DIR, data_type, str(date.year), str(date.month))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{date.day}.parquet")
    
    return input_path, output_path


def _load_clean_data(input_path: str) -> pd.DataFrame:
    """
    Charge les données nettoyées
    
    Args:
        input_path: Chemin du fichier d'entrée
        
    Returns:
        DataFrame nettoyé
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Clean data file not found: {input_path}")
    
    return pd.read_parquet(input_path)


def _add_temporal_features(df: pd.DataFrame, date_column: str = 'order_date') -> pd.DataFrame:
    """
    Ajoute des caractéristiques temporelles basées sur une colonne de date
    
    Args:
        df: DataFrame à enrichir
        date_column: Nom de la colonne de date
        
    Returns:
        DataFrame enrichi avec les caractéristiques temporelles
    """
    if date_column not in df.columns:
        return df
    
    df[f'{date_column}_year'] = df[date_column].dt.year
    df[f'{date_column}_month'] = df[date_column].dt.month
    df[f'{date_column}_day'] = df[date_column].dt.day
    df[f'{date_column}_weekday'] = df[date_column].dt.weekday
    df[f'{date_column}_week'] = df[date_column].dt.isocalendar().week
    df[f'{date_column}_quarter'] = df[date_column].dt.quarter
    df['is_weekend'] = df[f'{date_column}_weekday'].isin([5, 6])
    
    day_names = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    df['day_name'] = df[f'{date_column}_weekday'].map(dict(enumerate(day_names)))
    
    month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                   'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    df['month_name'] = df[f'{date_column}_month'].map(dict(enumerate(month_names, 1)))
    
    return df


def _add_price_categories(df: pd.DataFrame, price_column: str = 'price') -> pd.DataFrame:
    """
    Ajoute des catégories de prix basées sur les quantiles
    
    Args:
        df: DataFrame à enrichir
        price_column: Nom de la colonne de prix
        
    Returns:
        DataFrame enrichi avec les catégories de prix
    """
    if price_column not in df.columns:
        return df
    
    try:
        df['price_quartile'] = pd.qcut(df[price_column], q=4, labels=['Bas', 'Moyen-', 'Moyen+', 'Élevé'], duplicates='drop')
    except ValueError:
        df['price_quartile'] = 'Standard'
    
    price_mean = df[price_column].mean()
    price_std = df[price_column].std()
    
    df['price_category'] = 'Normal'
    df.loc[df[price_column] < price_mean - price_std, 'price_category'] = 'Économique'
    df.loc[df[price_column] > price_mean + price_std, 'price_category'] = 'Premium'
    
    return df


def _add_quantity_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute des métriques basées sur les quantités
    
    Args:
        df: DataFrame à enrichir
        
    Returns:
        DataFrame enrichi avec les métriques de quantité
    """
    if 'quantity' not in df.columns:
        return df
    
    df['quantity_category'] = pd.cut(df['quantity'], 
                                   bins=[0, 1, 3, 5, float('inf')], 
                                   labels=['Unitaire', 'Petit', 'Moyen', 'Gros'])
    
    df['is_bulk_order'] = df['quantity'] >= 5
    
    return df


def _enrich_orders_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrichit spécifiquement les données de commandes
    
    Args:
        df: DataFrame des commandes
        
    Returns:
        DataFrame enrichi
    """
    df = _add_temporal_features(df, 'order_date')
    df = _add_price_categories(df, 'price')
    df = _add_quantity_metrics(df)
    
    if 'total_amount' in df.columns:
        try:
            df['revenue_category'] = pd.qcut(df['total_amount'], 
                                           q=3, 
                                           labels=['Faible', 'Moyen', 'Élevé'],
                                           duplicates='drop')
        except ValueError:
            df['revenue_category'] = 'Standard'
    
    if 'price' in df.columns and 'quantity' in df.columns:
        df['avg_unit_price'] = df['total_amount'] / df['quantity']
        df['discount_indicator'] = df['price'] < df['avg_unit_price'] * 0.9
    
    return df


def _add_customer_insights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute des insights sur les clients basés sur les données disponibles
    
    Args:
        df: DataFrame à enrichir
        
    Returns:
        DataFrame enrichi avec les insights clients
    """
    if 'customer_id' not in df.columns:
        return df
    
    customer_stats = df.groupby('customer_id').agg({
        'order_id': 'count',
        'total_amount': ['sum', 'mean'],
        'quantity': 'sum'
    }).round(2)
    
    customer_stats.columns = ['order_count', 'total_spent', 'avg_order_value', 'total_items']
    customer_stats = customer_stats.reset_index()
    
    customer_stats['customer_segment'] = 'Standard'
    customer_stats.loc[customer_stats['total_spent'] > customer_stats['total_spent'].quantile(0.8), 'customer_segment'] = 'Premium'
    customer_stats.loc[customer_stats['total_spent'] < customer_stats['total_spent'].quantile(0.2), 'customer_segment'] = 'Économique'
    
    customer_stats.loc[customer_stats['order_count'] > 2, 'customer_type'] = 'Fidèle'
    customer_stats.loc[customer_stats['order_count'] <= 2, 'customer_type'] = 'Occasionnel'
    customer_stats.loc[customer_stats['order_count'] == 1, 'customer_type'] = 'Nouveau'
    
    df = df.merge(customer_stats, on='customer_id', how='left')
    
    return df


def _add_product_insights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajoute des insights sur les produits
    
    Args:
        df: DataFrame à enrichir
        
    Returns:
        DataFrame enrichi avec les insights produits
    """
    if 'product_id' not in df.columns:
        return df
    
    product_stats = df.groupby('product_id').agg({
        'order_id': 'count',
        'quantity': 'sum',
        'total_amount': 'sum',
        'price': 'mean'
    }).round(2)
    
    product_stats.columns = ['product_order_count', 'product_total_qty', 'product_revenue', 'product_avg_price']
    product_stats = product_stats.reset_index()
    
    try:
        product_stats['product_popularity'] = pd.qcut(product_stats['product_order_count'], 
                                                    q=3, 
                                                    labels=['Faible', 'Moyen', 'Élevé'],
                                                    duplicates='drop')
    except ValueError:
        product_stats['product_popularity'] = 'Standard'
    
    try:
        product_stats['product_performance'] = pd.qcut(product_stats['product_revenue'], 
                                                     q=3, 
                                                     labels=['Faible', 'Moyen', 'Élevé'],
                                                     duplicates='drop')
    except ValueError:
        product_stats['product_performance'] = 'Standard'
    
    df = df.merge(product_stats, on='product_id', how='left')
    
    return df


def enrich_orders(date):
    """
    Enrichit les données de commandes pour une date donnée
    
    Args:
        date: Date des données à enrichir
    """
    input_path, output_path = _get_file_paths("orders", date)
    df = _load_clean_data(input_path)
    
    df = _enrich_orders_data(df)
    df = _add_customer_insights(df)
    df = _add_product_insights(df)
    
    df.to_parquet(output_path, index=False)
    print(f"Données de commandes enrichies et sauvegardées : {output_path}")


def enrich_clients(date):
    """
    Enrichit les données clients pour une date donnée
    
    Args:
        date: Date des données à enrichir
    """
    input_path, output_path = _get_file_paths("clients", date)
    df = _load_clean_data(input_path)
    
    if 'registration_date' in df.columns:
        df = _add_temporal_features(df, 'registration_date')
    
    if 'email' in df.columns:
        df['email_domain'] = df['email'].str.split('@').str[1]
        df['email_provider_type'] = df['email_domain'].apply(
            lambda x: 'Gmail' if 'gmail' in str(x).lower() 
                     else 'Yahoo' if 'yahoo' in str(x).lower()
                     else 'Outlook' if 'outlook' in str(x).lower() or 'hotmail' in str(x).lower()
                     else 'Autre'
        )
    
    df.to_parquet(output_path, index=False)
    print(f"Données clients enrichies et sauvegardées : {output_path}")


def enrich_products(date):
    """
    Enrichit les données produits pour une date donnée
    
    Args:
        date: Date des données à enrichir
    """
    input_path, output_path = _get_file_paths("products", date)
    df = _load_clean_data(input_path)
    
    if 'price' in df.columns:
        df = _add_price_categories(df, 'price')
    
    if 'product_name' in df.columns:
        df['product_name_length'] = df['product_name'].str.len()
        df['product_word_count'] = df['product_name'].str.split().str.len()
    
    df.to_parquet(output_path, index=False)
    print(f"Données produits enrichies et sauvegardées : {output_path}")


def enrich_data(date, data_type: Optional[str] = None):
    """
    Fonction générale pour enrichir les données
    
    Args:
        date: Date des données à enrichir
        data_type: Type de données ('clients', 'products', 'orders' ou None pour tous)
    """
    enrichment_functions = {
        'clients': enrich_clients,
        'products': enrich_products,
        'orders': enrich_orders
    }
    
    try:
        if data_type is None:
            for dtype, func in enrichment_functions.items():
                try:
                    func(date)
                except FileNotFoundError as e:
                    print(f"Fichier {dtype} non trouvé pour enrichissement à la date {date}: {e}")
        else:
            if data_type in enrichment_functions:
                enrichment_functions[data_type](date)
            else:
                raise ValueError(f"Type de données non supporté: {data_type}")
        
        print(f"Enrichissement des données terminé pour la date {date}")
        
    except Exception as e:
        print(f"Erreur lors de l'enrichissement des données pour la date {date}: {e}")
        raise


def create_analytics_summary(date):
    """
    Crée un résumé analytique des données enrichies
    
    Args:
        date: Date des données à analyser
    """
    try:
        orders_path = os.path.join(ENRICHED_DATA_DIR, "orders", str(date.year), str(date.month), f"{date.day}.parquet")
        
        if os.path.exists(orders_path):
            df = pd.read_parquet(orders_path)
            
            summary = {
                'date': date.strftime('%Y-%m-%d'),
                'total_orders': len(df),
                'total_revenue': round(df['total_amount'].sum(), 2),
                'avg_order_value': round(df['total_amount'].mean(), 2),
                'unique_customers': df['customer_id'].nunique(),
                'unique_products': df['product_id'].nunique(),
                'weekend_orders_pct': round(df['is_weekend'].sum() / len(df) * 100, 2),
                'bulk_orders_pct': round(df['is_bulk_order'].sum() / len(df) * 100, 2),
            }
            
            summary_df = pd.DataFrame([summary])
            summary_path = os.path.join(ENRICHED_DATA_DIR, f"daily_summary_{date.strftime('%Y_%m_%d')}.parquet")
            summary_df.to_parquet(summary_path, index=False)
            
            print(f"Résumé analytique créé : {summary_path}")
            print("Aperçu du résumé :")
            print(summary_df.to_string(index=False))
            
        else:
            print(f"Aucune donnée de commandes enrichies trouvée pour la date {date}")
            
    except Exception as e:
        print(f"Erreur lors de la création du résumé analytique : {e}")


if __name__ == "__main__":
    from datetime import datetime
    
    test_date = datetime(2024, 5, 3)
    enrich_data(test_date)
    create_analytics_summary(test_date)
