"""
Data cleaning module for ecommerce analytics.

This module provides functions to clean and preprocess raw data files
for clients, products, and orders, converting them to optimized parquet format.
"""

import pandas as pd
import os
import re
from typing import List, Dict, Callable, Optional

DATA_DIR = "data"
CLEAN_DATA_DIR = os.path.join(DATA_DIR, "clean_data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw_data")


def _get_file_paths(data_type: str, date) -> tuple:
    """
    Génère les chemins d'entrée et de sortie pour un type de données et une date donnés
    
    Args:
        data_type: Type de données ('clients', 'products', 'orders')
        date: Date des données
        
    Returns:
        tuple: (input_path, output_path)
    """
    input_path = os.path.join(RAW_DATA_DIR, data_type, str(date.year), str(date.month), f"{date.day}.csv")
    output_dir = os.path.join(CLEAN_DATA_DIR, data_type, str(date.year), str(date.month))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{date.day}.parquet")
    
    return input_path, output_path


def _load_and_basic_clean(input_path: str) -> pd.DataFrame:
    """
    Charge un fichier CSV et effectue le nettoyage de base
    
    Args:
        input_path: Chemin du fichier d'entrée
        
    Returns:
        DataFrame nettoyé
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    df = pd.read_csv(input_path)
    df.drop_duplicates(inplace=True)
    
    return df


def _clean_text_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Nettoie les colonnes de texte (suppression des espaces, normalisation)
    
    Args:
        df: DataFrame à nettoyer
        columns: Liste des noms de colonnes à nettoyer
        
    Returns:
        DataFrame avec les colonnes nettoyées
    """
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    return df


def _clean_numeric_columns(df: pd.DataFrame, columns: List[str], positive_only: bool = True) -> pd.DataFrame:
    """
    Nettoie les colonnes numériques
    
    Args:
        df: DataFrame à nettoyer
        columns: Liste des noms de colonnes à nettoyer
        positive_only: Si True, garde uniquement les valeurs positives
        
    Returns:
        DataFrame avec les colonnes nettoyées
    """
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if positive_only:
                df = df[df[col] > 0]
    
    return df


def _apply_clients_specific_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique le nettoyage spécifique aux clients
    
    Args:
        df: DataFrame des clients
        
    Returns:
        DataFrame nettoyé
    """
    critical_columns = ['client_id', 'customer_id']
    df.dropna(subset=[col for col in critical_columns if col in df.columns], inplace=True)
    
    if 'email' in df.columns:
        df['email'] = df['email'].astype(str).str.lower().str.strip()
        df = df[df['email'].str.contains('@', na=False)]
        df = df[~df['email'].isin(['nan', '', 'null', 'none'])]
    
    text_columns = ['customer_name', 'first_name', 'last_name', 'address', 'city']
    df = _clean_text_columns(df, text_columns)
    
    if 'phone' in df.columns:
        df['phone'] = df['phone'].astype(str).str.strip()
        df['phone'] = df['phone'].str.replace(r'[^\d\+\-\s\(\)]', '', regex=True)
    
    return df


def _apply_products_specific_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique le nettoyage spécifique aux produits
    
    Args:
        df: DataFrame des produits
        
    Returns:
        DataFrame nettoyé
    """
    critical_columns = ['product_id', 'product_name']
    df.dropna(subset=[col for col in critical_columns if col in df.columns], inplace=True)
    
    text_columns = ['product_name', 'category', 'brand', 'description']
    df = _clean_text_columns(df, text_columns)
    
    numeric_columns = ['price', 'cost', 'weight']
    df = _clean_numeric_columns(df, numeric_columns, positive_only=True)
    
    return df


def _apply_orders_specific_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique le nettoyage spécifique aux commandes
    
    Args:
        df: DataFrame des commandes
        
    Returns:
        DataFrame nettoyé
    """
    critical_columns = ['order_id', 'customer_id', 'product_id']
    df.dropna(subset=[col for col in critical_columns if col in df.columns], inplace=True)
    
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
        df.dropna(subset=['order_date'], inplace=True)
    
    text_columns = ['customer_name', 'product_name', 'status']
    df = _clean_text_columns(df, text_columns)
    
    numeric_columns = ['quantity', 'price']
    df = _clean_numeric_columns(df, numeric_columns, positive_only=True)
    
    if 'quantity' in df.columns and 'price' in df.columns:
        df['total_amount'] = df['quantity'] * df['price']
    
    return df


def _clean_data_generic(date, data_type: str, cleaning_function: Callable[[pd.DataFrame], pd.DataFrame]) -> None:
    """
    Fonction générique pour nettoyer les données
    
    Args:
        date: Date des données à nettoyer
        data_type: Type de données ('clients', 'products', 'orders')
        cleaning_function: Fonction de nettoyage spécifique à appliquer
    """
    input_path, output_path = _get_file_paths(data_type, date)
    
    df = _load_and_basic_clean(input_path)
    df = cleaning_function(df)
    
    df.to_parquet(output_path, index=False)
    print(f"Fichier {data_type} nettoyé et enregistré dans : {output_path}")


def clean_clients(date):
    """
    Nettoie les données clients pour une date donnée
    
    Args:
        date: Date des données à nettoyer
    """
    _clean_data_generic(date, "clients", _apply_clients_specific_cleaning)


def clean_products(date):
    """
    Nettoie les données produits pour une date donnée
    
    Args:
        date: Date des données à nettoyer
    """
    _clean_data_generic(date, "products", _apply_products_specific_cleaning)


def clean_orders(date):
    """
    Nettoie les données commandes pour une date donnée
    
    Args:
        date: Date des données à nettoyer
    """
    _clean_data_generic(date, "orders", _apply_orders_specific_cleaning)


def clean_data(date, data_type: Optional[str] = None):
    """
    Fonction générale pour nettoyer les données selon le type spécifié
    
    Args:
        date: Date des données à nettoyer
        data_type: Type de données ('clients', 'products', 'orders' ou None pour tous)
    """
    cleaning_functions = {
        'clients': clean_clients,
        'products': clean_products,
        'orders': clean_orders
    }
    
    try:
        if data_type is None:
            for dtype, func in cleaning_functions.items():
                try:
                    func(date)
                except FileNotFoundError as e:
                    print(f"Fichier {dtype} non trouvé pour la date {date}: {e}")
        else:
            if data_type in cleaning_functions:
                cleaning_functions[data_type](date)
            else:
                raise ValueError(f"Type de données non supporté: {data_type}. Types supportés: {list(cleaning_functions.keys())}")
        
        print(f"Nettoyage des données terminé pour la date {date}")
        
    except Exception as e:
        print(f"Erreur lors du nettoyage des données pour la date {date}: {e}")
        raise


if __name__ == "__main__":
    from datetime import datetime
    
    test_date = datetime(2024, 5, 3)
    clean_data(test_date)
