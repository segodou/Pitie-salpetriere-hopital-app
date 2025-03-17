# Streamlit App Template

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Un template moderne et structuré pour créer des applications d'analyse de données et de business intelligence avec Streamlit. Optimisé pour des données au format Parquet et utilisant Plotly pour des visualisations interactives.

## 🌟 Fonctionnalités

- **Structure multi-pages** pour une organisation claire et une navigation intuitive
- **Dashboard interactif** avec KPIs et visualisations dynamiques
- **Tableaux de bord thématiques** (exploration, visualisations avancées, prédictions)
- **Support pour Parquet** - format optimisé pour l'analyse de données
- **Visualisations interactives** avec Plotly

## 📂 Structure du projet

```
├── Home.py                # Page d'accueil (fichier principal)
├── config.py              # Configuration globale
├── utils.py               # Fonctions utilitaires
├── .streamlit/
│   └── config.toml        # Configuration Streamlit
├── assets/
│   ├── css/
│   │   └── style.css      # Styles CSS personnalisés
│   └── images/            # Images pour l'application
│   │   └── logo.png       
├── data/
│   └── dataset_admission  # Données de ventes (générées)
├── models/
│   └── .pkl               # Dossier pour les modèles
└── pages/                 # Pages supplémentaires
    ├── 1_📊_Exploratory_Analysis.py
    ├── 2_📈_Advanced_Visualizations.py
    └── 3_🔮_Predictions.py
```

## ⚙️ Installation

### Prérequis

- Python 3.9 ou supérieur
- [uv](https://github.com/astral-sh/uv) (recommandé pour une installation rapide)

### Installation avec uv

```bash
# Cloner le dépôt
git clone https://github.com/segodou/Pitie-salpetriere-hopital-app.git
cd streamlit-app-template

# Créer et activer un environnement virtuel avec uv
uv venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

# Installer les dépendances avec uv
uv pip install -e .
```

## 📊 Utilisation

### Génération des données exemple

Options disponibles :
- `--samples` : Nombre de transactions à générer (défaut: 10000)
- `--start` : Date de début au format YYYY-MM-DD (défaut: 2022-01-01)
- `--end` : Date de fin au format YYYY-MM-DD (défaut: 2023-12-31)
- `--output` : Chemin où enregistrer le fichier (défaut: data/sales_data.csv)
- `--format` : Format de sortie ('csv' ou 'parquet')

### Lancement de l'application

```bash
streamlit run Home.py
```

L'application sera accessible à l'adresse `http://localhost:8501` par défaut.

## 📋 Pages de l'application

1. **🏠 Home (Tableau de Bord Principal)**  
   - Vue d’ensemble des indicateurs clés : nombre total d’admissions, durée moyenne de séjour, etc.  
   - Évolution des admissions hospitalières sous forme de courbes interactives. 
   - Répartition des admissions par sexe, tranche d’âge, gravité, service hospitalier, mode d’arrivée et type d’hospitalisation.  
   - Filtres généraux permettant d’ajuster la période d’analyse et les variables pertinentes pour toutes les pages.  

2. **📊 Exploratory Analysis (Analyse Exploratoire des Admissions)**  
   - Analyse temporelle : évolution des admissions par jour, mois, année et saison pour identifier les tendances.  
   - Corrélations entre les admissions et les facteurs externes : météo, événements spéciaux, vacances scolaires.  
   - Étude de saisonnalité avec une décomposition des tendances des admissions hospitalières.  

3. **📈 Advanced Visualizations (Visualisations Avancées)**  
   - Carte de chaleur des admission pour observer l’influence de la météo et des jours de la semaine.  
   - Visualisations hiérarchiques (Treemap, Sunburst) montrant la répartition des admissions par saison et période spécifique.  
   - Analyse comparative des admissions entre deux périodes sélectionnées, permettant d’évaluer les fluctuations et d’anticiper les besoins.  

4. **🔮 Predictions (Prédictions et Projections)**  
   - Prédiction des admissions hospitalières grâce au modèle Prophet, avec ajustement des paramètres tels que la saison et les événements spéciaux.  
   - Projection du personnel hospitalier (médecins, infirmiers, aides-soignants) en fonction des admissions prévues, grâce aux modèles XGBoost et Régression Linéaire.  
   - Affichage des projections sur des graphiques interactifs, permettant de comparer les tendances historiques et les prévisions.  
   - Téléchargement des projections au format CSV, incluant les admissions prédites et les effectifs hospitaliers recommandés.  


## 🧩 Dépendances principales

- streamlit
- pandas
- plotly
- numpy
- pyarrow (pour la prise en charge de Parquet)
- statsmodels
- joblib
- prophet
- scikit-learn
- xgboost

## 💻 Développement

### Outils de développement

Ce projet utilise plusieurs outils pour maintenir la qualité du code :

- **pre-commit** : Vérifications automatiques avant chaque commit
- **ruff** : Linter et formateur pour Python
- **isort** : Tri des imports Python
- **uv** : Gestionnaire de paquets et d'environnements virtuels

### Configuration pre-commit

Les hooks pre-commit suivants sont configurés :

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.10
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: [--profile=black]
```

### Installation des hooks pre-commit

```bash
pip install pre-commit
pre-commit install
```

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).

```
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
