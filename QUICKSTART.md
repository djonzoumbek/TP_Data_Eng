# 🚀 Guide de démarrage rapide

## En 5 minutes chrono !

### 1. Configuration initiale
```bash
# Installer les dépendances essentielles
pip install pandas numpy pyarrow

# Ou utiliser le fichier requirements simplifié
pip install -r requirements.txt
```

### 2. Tester le projet
```bash
# Test ultra-rapide des 3 calculs analytiques
python run_analytics.py
```

### 3. Personnaliser pour votre usage

Éditez `run_analytics.py` et modifiez :

```python
# VOS stocks de départ
stocks = {
    1: 100,   # Remplacez par vos vrais product_id
    4: 200,   # et quantités de stock
    10: 140,
    14: 175,
    15: 105,
    17: 155
}

# VOTRE date à analyser
date = datetime(2024, 5, 3)  # Changez la date
```

### 4. Résultats obtenus

✅ **Stock journalier** : Qui a vendu quoi, stock restant
✅ **Nouveaux clients** : Tracking acquisition quotidienne  
✅ **CA mensuel** : Chiffre d'affaires + métriques business

### 5. Aller plus loin

- `guide_utilisation.py` - Exemples détaillés
- `analytics_simple.py` - Fonctions individuelles
- `src/dags/common/` - Modules avancés complets

## 🎯 Cas d'usage typiques

**Manager magasin :** Analyse quotidienne des ventes et stocks
**Responsable marketing :** Suivi acquisition clients
**Direction commerciale :** Rapports de CA mensuel
**Data analyst :** Pipeline complet de données

## 🆘 Problème ?

1. Vérifiez que vos données sont dans `data/enriched_data/orders/`
2. Adaptez les stocks et dates dans les scripts
3. Consultez le README.md pour la doc complète

**C'est parti ! 🚀**
