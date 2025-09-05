# 🛒 Ecommerce Analytics - Pipeline de Données

Un pipeline complet d'analyse de données e-commerce avec extraction, nettoyage, enrichissement et calculs analytiques métier.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture du projet](#architecture-du-projet)
- [Installation](#installation)
- [Structure des données](#structure-des-données)
- [Modules principaux](#modules-principaux)
- [Calculs analytiques](#calculs-analytiques)
- [Utilisation](#utilisation)
- [Exemples pratiques](#exemples-pratiques)
- [Structure du projet](#structure-du-projet)

## 🎯 Vue d'ensemble

Ce projet implémente un pipeline de données e-commerce complet permettant de :

- **Extraire** des données de commandes depuis différentes sources
- **Nettoyer** et standardiser les données brutes
- **Enrichir** avec des métriques et dimensions analytiques
- **Calculer** des indicateurs métier essentiels

### 📊 Calculs analytiques implémentés

1. **Stock journalier** = (stock initial - commandes)
2. **Suivi des nouveaux clients** par période
3. **Chiffre d'affaires mensuel** avec analyses détaillées

## 🏗️ Architecture du projet

```
Raw Data → Clean Data → Enriched Data → Analytics
    ↓           ↓            ↓             ↓
  CSV        Parquet      Parquet     Rapports
```

### Pipeline de traitement

1. **Extract** (`extract.py`) - Extraction des données sources
2. **Clean** (`clean.py`) - Nettoyage et validation
3. **Enrich** (`enrich.py`) - Enrichissement avec 29+ nouvelles colonnes
4. **Analytics** (`analytics.py`) - Calculs métier et rapports

## 🚀 Installation

### Prérequis

- Python 3.8+
- pandas
- numpy

### Configuration

```bash
# Cloner le projet
git clone <repository-url>
cd ecommerce-analytics

# Installer les dépendances
pip install -r requirements.txt
```

## 📁 Structure des données

```
data/
├── raw_data/           # Données brutes (CSV)
│   └── orders/
│       └── 2024/5/
│           ├── 3.csv
│           └── 10.csv
├── clean_data/         # Données nettoyées (Parquet)
├── enriched_data/      # Données enrichies (Parquet)
└── analytics/          # Rapports analytiques (Parquet)
```

### Format des données

**Commandes (orders) :**
```
order_id, order_date, customer_id, customer_name, 
product_id, product_name, quantity, price
```

## 🛠️ Modules principaux

### 1. Module de nettoyage (`clean.py`)

Nettoie et standardise les données brutes.

```python
from src.dags.common.clean import clean_data
from datetime import datetime

# Nettoyer toutes les données
clean_data(datetime(2024, 5, 3))

# Nettoyer un type spécifique
clean_data(datetime(2024, 5, 3), 'orders')
```

**Fonctionnalités :**
- Suppression des doublons
- Validation des données critiques
- Nettoyage des formats (emails, dates, prix)
- Conversion en format Parquet optimisé

### 2. Module d'enrichissement (`enrich.py`)

Ajoute des dimensions analytiques avancées.

```python
from src.dags.common.enrich import enrich_data

# Enrichir les données
enrich_data(datetime(2024, 5, 3))
```

**29+ nouvelles colonnes ajoutées :**
- **Temporelles :** `day_name`, `month_name`, `is_weekend`, `quarter`
- **Business :** `price_category`, `customer_segment`, `product_popularity`
- **Calculées :** `total_amount`, `avg_unit_price`, `discount_indicator`

### 3. Module d'analytics (`analytics.py`)

Calculs métier et rapports business.

```python
from src.dags.common.analytics import quick_daily_analytics

# Analyse quotidienne complète
stocks = {1: 100, 4: 200, 10: 140}
quick_daily_analytics(datetime(2024, 5, 3), stocks)
```

## 📊 Calculs analytiques

### 1. 📦 Stock journalier

**Formule :** `Stock restant = Stock initial - Quantités vendues`

```python
from analytics_simple import stock_journalier

stocks = {1: 100, 4: 200, 10: 140}
result = stock_journalier(datetime(2024, 5, 3), stocks)
```

**Résultat :**
| product_id | stock_initial | quantite_vendue | stock_restant |
|------------|---------------|-----------------|---------------|
| 1          | 100           | 4               | 96            |
| 4          | 200           | 5               | 195           |

### 2. 👥 Suivi des nouveaux clients

Tracking des nouveaux clients par jour avec revenus associés.

```python
from analytics_simple import suivi_nouveaux_clients

result = suivi_nouveaux_clients(
    datetime(2024, 5, 1), 
    datetime(2024, 5, 10)
)
```

**Résultat :**
| date       | nouveaux_clients | revenus_nouveaux_clients |
|------------|------------------|--------------------------|
| 2024-05-03 | 6                | 647.44                   |
| 2024-05-10 | 11               | 1743.88                  |

### 3. 💰 Chiffre d'affaires mensuel

Analyse complète du CA mensuel avec métriques détaillées.

```python
from analytics_simple import chiffre_affaires_mensuel

result = chiffre_affaires_mensuel(2024, 5)
```

**Métriques calculées :**
- CA total : 3,701.34€
- Nombre de commandes : 29
- Panier moyen : 127.63€
- CA moyen/jour : 119.40€
- Meilleur jour de ventes
- Performance weekend vs semaine

## 💻 Utilisation

### Utilisation simple (3 lignes)

```python
# Fichier : run_analytics.py
from analytics_simple import stock_journalier, suivi_nouveaux_clients, chiffre_affaires_mensuel
from datetime import datetime

stocks = {1: 100, 4: 200, 10: 140}
stock_journalier(datetime(2024, 5, 3), stocks)
suivi_nouveaux_clients(datetime(2024, 5, 1), datetime(2024, 5, 10))
chiffre_affaires_mensuel(2024, 5)
```

### Pipeline complet

```python
from datetime import datetime
from src.dags.common.clean import clean_data
from src.dags.common.enrich import enrich_data
from src.dags.common.analytics import create_comprehensive_analytics_report

date = datetime(2024, 5, 3)

# 1. Nettoyage
clean_data(date)

# 2. Enrichissement  
enrich_data(date)

# 3. Analytics
stocks = {1: 100, 4: 200, 10: 140, 14: 175, 15: 105, 17: 155}
create_comprehensive_analytics_report(date, date, stocks)
```

## 🎯 Exemples pratiques

### Analyse quotidienne automatisée

```python
from analytics_simple import analyse_complete_simple
from datetime import datetime

# Configuration
stocks_magasin = {
    1: 100,   # Product_1
    4: 200,   # Product_4
    10: 140,  # Product_10
    14: 175,  # Product_14
    15: 105,  # Product_15
    17: 155   # Product_17
}

# Analyse du jour
analyse_complete_simple(datetime(2024, 5, 3), stocks_magasin)
```

### Suivi de performance

```python
# Suivre les ventes sur une semaine
for i in range(7):
    date = datetime(2024, 5, 3) + timedelta(days=i)
    try:
        stock_journalier(date, stocks_magasin)
    except:
        print(f"Pas de données pour {date}")
```

### Rapport mensuel automatique

```python
# Générer un rapport mensuel complet
def rapport_mensuel(annee, mois):
    ca = chiffre_affaires_mensuel(annee, mois)
    clients = suivi_nouveaux_clients(
        datetime(annee, mois, 1),
        datetime(annee, mois, 31)
    )
    
    print(f"=== RAPPORT {annee}-{mois:02d} ===")
    print(f"CA : {ca['ca_total']}€")
    print(f"Nouveaux clients : {clients['nouveaux_clients'].sum()}")

rapport_mensuel(2024, 5)
```

## 📁 Structure du projet

```
ecommerce-analytics/
├── README.md                      # Documentation
├── requirements.txt               # Dépendances
├── data/                         # Données
│   ├── raw_data/                 # Données brutes
│   ├── clean_data/               # Données nettoyées
│   ├── enriched_data/            # Données enrichies
│   └── analytics/                # Rapports analytiques
├── src/
│   └── dags/
│       └── common/
│           ├── extract.py        # Extraction
│           ├── clean.py          # Nettoyage
│           ├── enrich.py         # Enrichissement
│           └── analytics.py      # Analytics avancées
├── analytics_simple.py           # Analytics simplifiées
├── guide_utilisation.py          # Guide d'utilisation
├── run_analytics.py             # Exécution rapide
└── exemple_analytics.py         # Exemples d'usage
```

## 🔧 Configuration

### Personnalisation des stocks

Modifiez les stocks initiaux selon vos produits :

```python
# Dans analytics_simple.py ou vos scripts
MES_STOCKS = {
    1: 150,    # Produit 1 : 150 unités
    2: 200,    # Produit 2 : 200 unités
    3: 100,    # Produit 3 : 100 unités
    # Ajoutez vos produits...
}
```

### Automatisation

Pour automatiser les analyses quotidiennes, ajoutez à votre crontab :

```bash
# Analyse quotidienne à 9h00
0 9 * * * cd /path/to/project && python run_analytics.py
```

## 📈 Métriques disponibles

### Métriques de stock
- Stock initial par produit
- Quantités vendues quotidiennes
- Stock restant
- Alertes de rupture

### Métriques clients
- Nouveaux clients par jour
- Revenus des nouveaux clients
- Taux d'acquisition
- Segmentation client (Premium, Standard, Économique)

### Métriques financières
- Chiffre d'affaires quotidien/mensuel
- Panier moyen
- Performance par jour de la semaine
- Tendances de croissance

## 🚨 Gestion d'erreurs

Le système gère automatiquement :
- Fichiers de données manquants
- Formats de données incorrects  
- Calculs sur datasets vides
- Erreurs de configuration

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Consulter la documentation dans le code
- Vérifier les exemples dans `guide_utilisation.py`

---

**✨ Projet développé dans le cadre de la Data Academy Hub - TP Data Engineering**