# 🏦 Simulateur DSGE Cameroun-BEAC

## 📋 Description

Simulation et l'analyse des impacts des décisions de politique monétaire de la BEAC sur l'économie camerounaise. Ce modèle DSGE (Dynamic Stochastic General Equilibrium) permet d'évaluer quantitativement les effets des chocs économiques sur les principaux agrégats macroéconomiques.

## 🎯 Objectifs

- **Analyser** l'impact des décisions de politique monétaire BEAC
- **Simuler** différents scénarios de chocs économiques
- **Visualiser** les fonctions de réponse impulsionnelle
- **Produire** des recommandations de politique économique

## 🚀 Fonctionnalités

### 🔬 Types de Chocs Simulés

1. **💰 Politique Monétaire (TIAO)** : Variation du taux directeur BEAC  
2. **🏛️ Politique Budgétaire** : Choc sur les dépenses publiques  
3. **🏭 Productivité (PTF)** : Choc de productivité totale des facteurs  
4. **📉 Prime de Risque** : Variation du spread bancaire  
5. **🛢️ Prix Pétrole** : Choc sur les termes de l'échange  

### 📊 Analyses Fournies

- **Fonctions de Réponse Impulsionnelle (IRF)** sur 15 variables macroéconomiques  
- **Métriques clés** en temps réel  
- **Analyse économique automatique** avec recommandations  
- **Comparaison multi-scénarios**  
- **Export des données** de simulation  

### 🎨 Interface Moderne

- Design responsive avec couleurs du Cameroun  
- Graphiques interactifs Plotly  
- Cartes de métriques animées  
- Navigation intuitive  

## 🛠️ Installation

### Prérequis

- Python 3.8 ou supérieur  
- pip (gestionnaire de packages Python)  

### Installation des Dépendances

```bash
# Cloner le repository (si applicable)
git clone <votre-repository>
cd simulation_projet_dsge_beac

# Installer les dépendances
pip install streamlit plotly pandas numpy scipy matplotlib seaborn
```

### Lancement de l'Application

```bash
streamlit run dsge_simulator.py
```

L'application sera accessible à l'adresse : `http://localhost:8501`

## 📈 Variables du Modèle

### Variables Macroéconomiques Simulées

| Variable | Description |
|----------|-------------|
| `PIB` | Production agrégée |
| `Consommation` | Consommation des ménages |
| `Investissement` | Formation brute de capital fixe |
| `Inflation` | Taux d'inflation domestique |
| `Taux_Interet` | Taux directeur BEAC (TIAO) |
| `Salaire_Reel` | Salaire réel |
| `Travail` | Offre de travail |
| `Exportations_Nettes` | Balance commerciale |
| `Depenses_Publiques` | Dépenses du gouvernement |
| `Recettes_Fiscales` | Revenus fiscaux |
| `Dette_Publique` | Stock de dette publique |
| `Credit` | Crédit bancaire |
| `Spread_Bancaire` | Marge d'intérêt bancaire |
| `Taux_Change_Reel` | Taux de change réel |
| `Output_Gap` | Écart de production |

### Paramètres de Calibration

| Paramètre | Valeur | Description |
|-----------|---------|-------------|
| `beta` | 0.96 | Facteur d'actualisation |
| `sigma` | 2.0 | Aversion au risque |
| `phi` | 1.5 | Élasticité inverse de Frisch |
| `theta_c` | 0.3 | Part des importations |
| `alpha` | 0.35 | Part du capital |
| `theta` | 0.75 | Rigidité des prix (Calvo) |
| `phi_pi` | 1.5 | Réaction à l'inflation (Taylor) |
| `phi_y` | 0.5 | Réaction à l'output gap |

## 🎮 Utilisation

### 1. Configuration de la Simulation

1. **Sélectionnez le type de choc** dans la sidebar  
2. **Ajustez l'amplitude du choc** (0.1% à 5.0%)  
3. **Définissez la période de simulation** (20 à 60 trimestres)  
4. **Choisissez les options d'affichage**  

### 2. Analyse des Résultats

- **Métriques clés** : Impact maximum sur PIB, inflation, dette, crédit  
- **Graphiques IRF** : Visualisation interactive des 15 variables  
- **Analyse économique** : Rapport automatique avec recommandations  
- **Données détaillées** : Tableau exportable des résultats  

### 3. Comparaison de Scénarios

- Comparez deux scénarios différents  
- Visualisez les différences d'impact sur le PIB  
- Exportez les résultats pour analyse approfondie  

## 📊 Exemples d'Analyse

### Choc Monétaire (+1% TIAO)
- **Impact PIB** : -0.8% après 1 an  
- **Effet inflation** : -0.5 point après 8 trimestres  
- **Transmission** : Canal du crédit → investissement → consommation  

### Choc Budgétaire (+2% PIB dépenses)
- **Multiplicateur** : 0.6 à 1 an  
- **Impact dette** : +1.2% PIB  
- **Effet inflation** : +0.3 point  

## 🏛️ Contexte Institutionnel

### Cadre de Modélisation
- **Modèle DSGE** petite économie ouverte  
- **Spécificités CEMAC** : Ancrage à l'euro, gestion des réserves  
- **Contraintes institutionnelles** : Critères de convergence  

### Utilisation Politique
- **Analyse ex-ante** des décisions de politique économique  
- **Évaluation** de la coordination budgétaire-monétaire  
- **Simulation** de scénarios de crise  

## 🔧 Structure du Code

```
simulation_projet_dsge_beac/
│
├── dsge_simulator.py          # Application principale Streamlit
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation
└── data/                      # Données de calibration (optionnel)
    ├── historical_data.csv
    └── calibration_params.json
```

### Composants Principaux

1. **`DSGEModelCameroon`** : Classe principale du modèle DSGE  
2. **`simulate_shock()`** : Méthode de simulation des chocs  
3. **`create_modern_irf_plot()`** : Génération des graphiques  
4. **`generate_analysis_report()`** : Analyse automatique des résultats  

## 📈 Extensions Futures

- [ ] Intégration de données historiques camerounaises  
- [ ] Calibration bayésienne des paramètres  
- [ ] Module de prévision conditionnelle  
- [ ] Interface d'estimation en temps réel  
- [ ] Export de rapports PDF automatisés  
- [ ] Module de stress-testing  

## 🤝 Contribution

### Développement
1. Forkez le projet  
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)  
3. Committez vos changements (`git commit -m 'Add some AmazingFeature'`)  
4. Pushez la branche (`git push origin feature/AmazingFeature`)  
5. Ouvrez une Pull Request  

### Améliorations Suggérées
- Intégration avec bases de données BEAC/INS  
- Modules d'analyse de robustesse  
- Interface multilingue (Français/Anglais)  

## 📝 Références

### Publications Académiques
- Gali, J. (2015). *Monetary Policy, Inflation, and the Business Cycle*  
- Smets, F., & Wouters, R. (2003). *An estimated dynamic stochastic general equilibrium model of the euro area*  
- Schmitt-Grohé, S., & Uribe, M. (2003). *Closing small open economy models*  

### Documentation Technique
- [Streamlit Documentation](https://docs.streamlit.io/)  
- [Plotly Python Graphing Library](https://plotly.com/python/)  
- [Dynare Manual](http://www.dynare.org/documentation-and-support/manual)  

## 📄 Licence

Ce projet est développé pour la **Section Suivi des Politiques Economiques et de l'Inclusion Financière** du Cameroun.

## 📞 Support

Pour toute question ou problème technique :  
- **Développement** : Équipe de modélisation économique  
- **Contenu économique** : Section Suivi des Politiques Economiques  
- **Données** : Service de la statistique  

---

**Développé avec ❤️ pour l'analyse économique du Cameroun**
- **POUM BIMBAR Paul Ghislain** : poum.bimbar@onacc.cm
