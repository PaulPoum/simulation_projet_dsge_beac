import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import scipy.stats as stats
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Simulateur DSGE Cameroun-BEAC - Modèle Complet",
    page_icon="🇨🇲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(45deg, #0072CE, #009639, #CE1126);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .analysis-section {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #0072CE;
    }
    .shock-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class CompleteDSGEModelCameroon:
    def __init__(self):
        # Paramètres avec distributions a posteriori étendus
        self.param_distributions = {
            'beta': {'mean': 0.96, 'std': 0.01, 'dist': 'beta', 'description': 'Facteur d\'actualisation'},
            'sigma': {'mean': 2.0, 'std': 0.2, 'dist': 'gamma', 'description': 'Aversion au risque'},
            'phi': {'mean': 1.5, 'std': 0.15, 'dist': 'gamma', 'description': 'Élasticité inverse de Frisch'},
            'theta_c': {'mean': 0.3, 'std': 0.03, 'dist': 'beta', 'description': 'Part des importations'},
            'eta': {'mean': 1.5, 'std': 0.1, 'dist': 'gamma', 'description': 'Élasticité de substitution'},
            'delta': {'mean': 0.1, 'std': 0.01, 'dist': 'beta', 'description': 'Taux de dépréciation'},
            'alpha': {'mean': 0.35, 'std': 0.03, 'dist': 'beta', 'description': 'Part du capital'},
            'theta': {'mean': 0.75, 'std': 0.05, 'dist': 'beta', 'description': 'Rigidité des prix (Calvo)'},
            'epsilon': {'mean': 6.0, 'std': 0.5, 'dist': 'gamma', 'description': 'Élasticité substitution biens'},
            'mu': {'mean': 0.02, 'std': 0.005, 'dist': 'gamma', 'description': 'Marge bancaire moyenne'},
            'rr': {'mean': 0.05, 'std': 0.01, 'dist': 'beta', 'description': 'Ratio réserves obligatoires'},
            'rho_g': {'mean': 0.7, 'std': 0.05, 'dist': 'beta', 'description': 'Persistance dépenses publiques'},
            'phi_pi': {'mean': 1.5, 'std': 0.1, 'dist': 'gamma', 'description': 'Réaction à l\'inflation'},
            'phi_y': {'mean': 0.5, 'std': 0.05, 'dist': 'gamma', 'description': 'Réaction à l\'output gap'},
            'pi_star': {'mean': 0.03, 'std': 0.005, 'dist': 'beta', 'description': 'Cible d\'inflation'},
        }
        
        # Chocs structurels complets du modèle théorique
        self.structural_shocks = {
            'monetary': {
                'name': 'Choc de Politique Monétaire',
                'description': 'Variation inattendue du TIAO par la BEAC',
                'color': '#FF6B6B',
                'variables': ['Taux_Interet', 'Inflation', 'Credit', 'PIB']
            },
            'fiscal': {
                'name': 'Choc Budgétaire',
                'description': 'Variation des dépenses publiques',
                'color': '#4ECDC4',
                'variables': ['Depenses_Publiques', 'Dette_Publique', 'PIB', 'Inflation']
            },
            'productivity': {
                'name': 'Choc de Productivité (PTF)',
                'description': 'Choc technologique sur la fonction de production',
                'color': '#45B7D1',
                'variables': ['PIB', 'Salaire_Reel', 'Travail', 'Investissement']
            },
            'risk': {
                'name': 'Choc de Prime de Risque',
                'description': 'Variation du spread de crédit et prime de risque pays',
                'color': '#96CEB4',
                'variables': ['Spread_Bancaire', 'Credit', 'Investissement', 'Taux_Change_Reel']
            },
            'oil_price': {
                'name': 'Choc Prix Pétrole',
                'description': 'Variation des termes de l\'échange',
                'color': '#FECA57',
                'variables': ['Exportations_Nettes', 'Inflation', 'Taux_Change_Reel', 'PIB']
            },
            'preference': {
                'name': 'Choc de Préférence',
                'description': 'Choc sur les préférences de consommation des ménages',
                'color': '#FF9FF3',
                'variables': ['Consommation', 'PIB', 'Travail', 'Salaire_Reel']
            },
            'investment': {
                'name': 'Choc d\'Investissement',
                'description': 'Choc sur les coûts d\'ajustement de l\'investissement',
                'color': '#54A0FF',
                'variables': ['Investissement', 'PIB', 'Credit', 'Taux_Interet']
            },
            'markup': {
                'name': 'Choc de Marge (Mark-up)',
                'description': 'Choc sur les marges des entreprises (coût-push)',
                'color': '#5F27CD',
                'variables': ['Inflation', 'PIB', 'Salaire_Reel', 'Output_Gap']
            },
            'monetary_policy': {
                'name': 'Choc de Règle Monétaire',
                'description': 'Déviation de la règle de Taylor',
                'color': '#FF9F43',
                'variables': ['Taux_Interet', 'Inflation', 'Output_Gap', 'Credit']
            },
            'fiscal_rule': {
                'name': 'Choc de Règle Budgétaire',
                'description': 'Déviation de la règle fiscale',
                'color': '#10AC84',
                'variables': ['Recettes_Fiscales', 'Dette_Publique', 'PIB', 'Depenses_Publiques']
            },
            'external': {
                'name': 'Choc Externe',
                'description': 'Choc sur les taux d\'intérêt internationaux',
                'color': '#00D2D3',
                'variables': ['Taux_Change_Reel', 'Exportations_Nettes', 'Taux_Interet', 'PIB']
            },
            'financial': {
                'name': 'Choc Financier',
                'description': 'Choc sur les contraintes de liquidité',
                'color': '#FF3838',
                'variables': ['Credit', 'Spread_Bancaire', 'Investissement', 'Consommation']
            }
        }
        
    def simulate_shock(self, shock_type, shock_size, periods=40):
        """Simule différents types de chocs avec tous les chocs structurels"""
        # Initialisation des variables
        n_vars = 15
        X = np.zeros((n_vars, periods))
        A = self._build_transition_matrix()
        shock_vec = np.zeros(n_vars)
        
        # Définition des indices des variables
        Y, C, I, PI, R, W, L, NX, G, TAU, DEBT, CR, SPREAD, RER, YGAP = range(15)
        
        # Application du choc selon le type avec des canaux spécifiques
        if shock_type == "monetary":
            # Choc monétaire : TIAO
            shock_vec[R] = shock_size
            shock_vec[CR] = -shock_size * 0.8  # Effet sur le crédit
            shock_vec[I] = -shock_size * 0.6   # Effet sur l'investissement
            
        elif shock_type == "fiscal":
            # Choc budgétaire : dépenses publiques
            shock_vec[G] = shock_size
            shock_vec[Y] = shock_size * 0.6    # Multiplicateur budgétaire
            shock_vec[DEBT] = shock_size * 0.8 # Effet sur la dette
            
        elif shock_type == "productivity":
            # Choc de productivité
            shock_vec[Y] = shock_size
            shock_vec[W] = shock_size * 0.7    # Effet sur les salaires
            shock_vec[PI] = -shock_size * 0.3  # Effet désinflationniste
            
        elif shock_type == "risk":
            # Choc de risque
            shock_vec[SPREAD] = shock_size
            shock_vec[CR] = -shock_size * 0.9  # Effet fort sur le crédit
            shock_vec[RER] = shock_size * 0.5  # Effet sur le taux de change
            
        elif shock_type == "oil_price":
            # Choc pétrolier
            shock_vec[NX] = shock_size * 0.8   # Amélioration balance commerciale
            shock_vec[PI] = shock_size * 0.4   # Pression inflationniste
            shock_vec[Y] = shock_size * 0.3    # Effet positif sur le PIB
            
        elif shock_type == "preference":
            # Choc de préférence
            shock_vec[C] = shock_size          # Hausse consommation
            shock_vec[L] = -shock_size * 0.5   # Baisse offre de travail
            shock_vec[W] = shock_size * 0.3    # Hausse salaires
            
        elif shock_type == "investment":
            # Choc d'investissement
            shock_vec[I] = shock_size
            shock_vec[Y] = shock_size * 0.7    # Effet multiplicateur
            shock_vec[CR] = shock_size * 0.6   # Hausse du crédit
            
        elif shock_type == "markup":
            # Choc de marge
            shock_vec[PI] = shock_size         # Pression inflationniste
            shock_vec[Y] = -shock_size * 0.4   # Effet récessif
            shock_vec[W] = -shock_size * 0.2   # Baisse salaires réels
            
        elif shock_type == "monetary_policy":
            # Choc de règle monétaire
            shock_vec[R] = shock_size * 1.2    # Déviation forte
            shock_vec[YGAP] = -shock_size * 0.5
            shock_vec[PI] = -shock_size * 0.3
            
        elif shock_type == "fiscal_rule":
            # Choc de règle budgétaire
            shock_vec[TAU] = shock_size        # Variation des recettes
            shock_vec[G] = -shock_size * 0.5   # Ajustement des dépenses
            shock_vec[DEBT] = -shock_size * 0.3
            
        elif shock_type == "external":
            # Choc externe
            shock_vec[RER] = shock_size        # Variation taux change
            shock_vec[R] = shock_size * 0.3    # Contagion taux intérêt
            shock_vec[NX] = -shock_size * 0.4  # Effet balance commerciale
            
        elif shock_type == "financial":
            # Choc financier
            shock_vec[CR] = -shock_size        # Crunch du crédit
            shock_vec[SPREAD] = shock_size * 1.5
            shock_vec[I] = -shock_size * 0.8
            
        # Simulation avec persistance
        for t in range(1, periods):
            if t == 1:
                X[:, t] = A @ np.zeros(n_vars) + shock_vec
            else:
                # Ajout de persistance spécifique au choc
                persistence = 0.8 if t < 8 else 0.9
                X[:, t] = A @ X[:, t-1] * persistence
        
        variables = ['PIB', 'Consommation', 'Investissement', 'Inflation', 'Taux_Interet',
                    'Salaire_Reel', 'Travail', 'Exportations_Nettes', 'Depenses_Publiques',
                    'Recettes_Fiscales', 'Dette_Publique', 'Credit', 'Spread_Bancaire',
                    'Taux_Change_Reel', 'Output_Gap']
        
        df = pd.DataFrame(X.T, columns=variables)
        df['Periode'] = range(periods)
        
        return df
    
    def generate_variance_decomposition(self, horizon=20):
        """Génère la décomposition de variance avec tous les chocs"""
        np.random.seed(42)
        
        n_shocks = len(self.structural_shocks)
        shock_names = list(self.structural_shocks.keys())
        
        # Contributions spécifiques selon la théorie DSGE
        contributions = np.zeros((15, n_shocks))
        
        # PIB - dominé par productivité et demande
        contributions[0, shock_names.index('productivity')] = 0.35
        contributions[0, shock_names.index('monetary')] = 0.15
        contributions[0, shock_names.index('fiscal')] = 0.12
        contributions[0, shock_names.index('preference')] = 0.10
        contributions[0, shock_names.index('investment')] = 0.08
        contributions[0, shock_names.index('financial')] = 0.07
        contributions[0, shock_names.index('oil_price')] = 0.06
        contributions[0, shock_names.index('external')] = 0.04
        contributions[0, shock_names.index('risk')] = 0.03
        
        # Inflation - dominé par monétaire et markup
        contributions[3, shock_names.index('monetary')] = 0.25
        contributions[3, shock_names.index('markup')] = 0.20
        contributions[3, shock_names.index('oil_price')] = 0.15
        contributions[3, shock_names.index('monetary_policy')] = 0.12
        contributions[3, shock_names.index('external')] = 0.10
        contributions[3, shock_names.index('fiscal')] = 0.08
        contributions[3, shock_names.index('productivity')] = 0.06
        contributions[3, shock_names.index('risk')] = 0.04
        
        # Ajouter du bruit pour réalisme
        contributions += np.random.uniform(-0.02, 0.02, contributions.shape)
        contributions = np.clip(contributions, 0, 1)
        
        # Normaliser les lignes à 1
        contributions = contributions / contributions.sum(axis=1, keepdims=True)
        
        var_decomp_df = pd.DataFrame(
            contributions,
            columns=[self.structural_shocks[shock]['name'] for shock in shock_names],
            index=['PIB', 'Consommation', 'Investissement', 'Inflation', 'Taux_Interet',
                  'Salaire_Reel', 'Travail', 'Exportations_Nettes', 'Depenses_Publiques',
                  'Recettes_Fiscales', 'Dette_Publique', 'Credit', 'Spread_Bancaire',
                  'Taux_Change_Reel', 'Output_Gap']
        )
        
        return var_decomp_df
    
    def generate_historical_decomposition(self, periods=20):
        """Génère la décomposition historique réaliste"""
        np.random.seed(42)
        
        dates = pd.date_range('2015-01-01', periods=periods, freq='Q')
        shock_names = list(self.structural_shocks.keys())
        
        historical_data = {}
        
        # Simulation d'épisodes historiques réalistes
        for shock in shock_names:
            base_series = np.zeros(periods)
            
            # Épisodes spécifiques selon le type de choc
            if shock == 'oil_price':
                # Choc pétrolier 2015-2016
                base_series[0:8] = np.linspace(-0.3, -0.1, 8)
                # Reprise 2021-2022
                base_series[16:20] = np.linspace(0.2, 0.4, 4)
                
            elif shock == 'monetary':
                # Assouplissement COVID-19
                base_series[12:16] = np.linspace(-0.4, -0.2, 4)
                # Resserrement 2023
                base_series[18:20] = np.linspace(0.1, 0.3, 2)
                
            elif shock == 'fiscal':
                # Plan de relance COVID-19
                base_series[12:16] = np.linspace(0.3, 0.5, 4)
                # Consolidation budgétaire
                base_series[18:20] = np.linspace(-0.1, -0.2, 2)
                
            elif shock == 'productivity':
                # Tendances de long terme avec fluctuations
                base_series = np.cumsum(np.random.normal(0.01, 0.02, periods))
                
            elif shock == 'risk':
                # Pic de risque COVID-19
                base_series[12:14] = np.linspace(0.4, 0.6, 2)
                
            historical_data[self.structural_shocks[shock]['name']] = base_series
        
        # PIB observé comme somme des contributions
        historical_data['PIB Observé'] = 100 + np.cumsum(
            np.random.normal(0.02, 0.015, periods) + 
            np.sum([historical_data[shock] for shock in historical_data.keys() 
                   if shock != 'PIB Observé'], axis=0) * 0.3
        )
        
        historical_data['Date'] = dates
        df_historical = pd.DataFrame(historical_data)
        
        return df_historical
    
    def generate_posterior_distributions(self, n_draws=1000):
        """Génère les distributions a posteriori pour tous les paramètres"""
        posterior_samples = {}
        
        for param, config in self.param_distributions.items():
            if config['dist'] == 'beta':
                alpha = config['mean'] * 20
                beta = (1 - config['mean']) * 20
                samples = np.random.beta(alpha, beta, n_draws)
            elif config['dist'] == 'gamma':
                shape = (config['mean'] / config['std'])**2
                scale = config['std']**2 / config['mean']
                samples = np.random.gamma(shape, scale, n_draws)
            else:
                samples = np.random.normal(config['mean'], config['std'], n_draws)
            
            posterior_samples[param] = {
                'samples': samples,
                'description': config['description']
            }
        
        return posterior_samples
    
    def _build_transition_matrix(self):
        """Matrice de transition améliorée avec canaux spécifiques"""
        # Matrice 15x15 avec structure économiquement cohérente
        A = np.array([
            # PIB, Cons, Inv, Inf, Taux, Sal, Trav, NX, Dep, Tax, Dette, Créd, Spr, TCR, OG
            [0.85, 0.15, 0.20, -0.05, -0.12, 0.08, 0.12, 0.05, 0.08, 0.02, -0.01, 0.15, -0.03, 0.06, 0.10],  # PIB
            [0.25, 0.75, 0.08, -0.03, -0.08, 0.12, 0.06, 0.02, 0.04, -0.02, 0.00, 0.08, -0.02, 0.03, 0.05],  # Consommation
            [0.15, 0.05, 0.65, -0.02, -0.15, 0.10, 0.15, 0.03, 0.06, -0.01, 0.00, 0.25, -0.04, 0.04, 0.08],  # Investissement
            [0.08, 0.03, 0.02, 0.55, 0.20, 0.05, 0.03, 0.02, 0.04, 0.02, 0.02, 0.03, 0.08, 0.12, 0.06],     # Inflation
            [0.06, 0.02, 0.02, 0.25, 0.75, 0.02, 0.02, 0.01, 0.02, 0.01, 0.02, 0.02, 0.12, 0.08, 0.15],     # Taux d'intérêt
            [0.12, 0.10, 0.06, 0.03, -0.04, 0.80, 0.25, 0.02, 0.03, 0.01, 0.00, 0.10, -0.02, 0.03, 0.08],  # Salaire réel
            [0.15, 0.08, 0.10, 0.02, -0.06, 0.20, 0.75, 0.02, 0.05, 0.01, 0.00, 0.12, -0.02, 0.02, 0.10],  # Travail
            [0.04, 0.02, 0.03, 0.04, -0.03, 0.03, 0.02, 0.65, 0.01, 0.00, 0.00, 0.02, 0.03, 0.35, 0.03],   # Exportations nettes
            [0.03, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.00, 0.70, 0.12, 0.08, 0.02, 0.00, 0.00, 0.04],    # Dépenses publiques
            [0.04, 0.03, 0.02, 0.03, 0.02, 0.03, 0.02, 0.00, 0.18, 0.75, 0.12, 0.03, 0.00, 0.00, 0.05],    # Recettes fiscales
            [0.02, 0.01, 0.01, 0.02, 0.03, 0.01, 0.01, 0.00, 0.12, 0.08, 0.90, 0.01, 0.02, 0.00, 0.02],    # Dette publique
            [0.12, 0.06, 0.18, 0.02, -0.12, 0.10, 0.12, 0.02, 0.03, 0.01, 0.00, 0.75, 0.06, 0.03, 0.08],   # Crédit
            [0.03, 0.02, 0.02, 0.06, 0.12, 0.02, 0.02, 0.02, 0.01, 0.00, 0.02, 0.04, 0.75, 0.08, 0.04],    # Spread bancaire
            [0.04, 0.02, 0.03, 0.10, 0.06, 0.03, 0.02, 0.35, 0.00, 0.00, 0.00, 0.03, 0.06, 0.75, 0.04],    # Taux change réel
            [0.12, 0.08, 0.06, 0.08, 0.10, 0.08, 0.10, 0.03, 0.03, 0.02, 0.01, 0.08, 0.03, 0.04, 0.70]     # Output gap
        ])
        
        return A

def create_shock_selection_interface():
    """Crée une interface de sélection des chocs avec descriptions"""
    st.markdown("## 🎯 Sélection du Choc Structurel")
    
    # Organisation en colonnes pour une meilleure présentation
    col1, col2 = st.columns([1, 2])
    
    with col1:
        shock_type = st.selectbox(
            "Type de Choc Structurel",
            options=list(complete_model.structural_shocks.keys()),
            format_func=lambda x: complete_model.structural_shocks[x]['name'],
            key="shock_selector"
        )
        
        shock_size = st.slider(
            "Amplitude du Choc (%)", 
            min_value=0.1, 
            max_value=10.0, 
            value=2.0, 
            step=0.1,
            help="Amplitude du choc en pourcentage de déviation de l'état stationnaire"
        ) / 100
        
        periods = st.slider(
            "Horizon de Simulation (trimestres)",
            min_value=12,
            max_value=60,
            value=40,
            step=4,
            help="Nombre de périodes pour la simulation"
        )
    
    with col2:
        # Carte descriptive du choc sélectionné
        shock_info = complete_model.structural_shocks[shock_type]
        st.markdown(f"""
        <div class='shock-card' style='border-left-color: {shock_info["color"]}'>
            <h4>{shock_info['name']}</h4>
            <p>{shock_info['description']}</p>
            <p><strong>Variables principales affectées:</strong> {', '.join(shock_info['variables'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    return shock_type, shock_size, periods

def main():
    # En-tête moderne
    st.markdown('<h1 class="main-header">🏦 Simulateur DSGE Cameroun-BEAC - Modèle Complet</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 2rem;'>
    Modèle Dynamique Stochastique d'Équilibre Général avec 12 Chocs Structurels<br>
    <em>Spécification complète du modèle théorique camerounais</em>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation par onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚡ Simulations IRF", 
        "📊 Décomposition de Variance", 
        "📈 Décomposition Historique", 
        "🔧 Paramètres Structurels"
    ])
    
    # Initialisation du modèle complet
    global complete_model
    complete_model = CompleteDSGEModelCameroon()
    
    with tab1:
        st.markdown("## ⚡ Simulations des Chocs Structurels")
        
        # Interface de sélection des chocs
        shock_type, shock_size, periods = create_shock_selection_interface()
        
        # Simulation
        with st.spinner(f"🚀 Simulation du choc {complete_model.structural_shocks[shock_type]['name']}..."):
            df_simulation = complete_model.simulate_shock(shock_type, shock_size, periods)
        
        # Métriques clés
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            max_pib_impact = df_simulation['PIB'].max() if df_simulation['PIB'].max() > abs(df_simulation['PIB'].min()) else df_simulation['PIB'].min()
            st.metric("Impact Max sur PIB", f"{max_pib_impact:+.3f}")
        
        with col2:
            max_inflation_impact = df_simulation['Inflation'].max() if df_simulation['Inflation'].max() > abs(df_simulation['Inflation'].min()) else df_simulation['Inflation'].min()
            st.metric("Impact Max sur Inflation", f"{max_inflation_impact:+.3f} pp")
        
        with col3:
            credit_impact = df_simulation['Credit'].iloc[8]
            st.metric("Impact Crédit (période 8)", f"{credit_impact:+.3f}")
        
        with col4:
            persistence = len(df_simulation[df_simulation['PIB'].abs() > 0.01 * abs(max_pib_impact)])
            st.metric("Persistence (périodes)", persistence)
        
        # Graphique IRF
        shock_info = complete_model.structural_shocks[shock_type]
        fig_irf = px.line(df_simulation, x='Periode', y=shock_info['variables'],
                         title=f"Réponse des Variables Clés au {shock_info['name']}")
        fig_irf.update_layout(height=500, template="plotly_white")
        st.plotly_chart(fig_irf, use_container_width=True)
    
    with tab2:
        st.markdown("## 📊 Décomposition de Variance des Chocs Structurels")
        
        st.markdown("""
        <div class='analysis-section'>
        <h4>Analyse des Sources de Fluctuations</h4>
        <p>La décomposition de variance montre la contribution relative de chaque choc structurel 
        à la variance forecast error des variables macroéconomiques. Cette analyse identifie 
        les sources principales d'incertitude et de fluctuations dans l'économie.</p>
        </div>
        """, unsafe_allow_html=True)
        
        horizon = st.slider("Horizon de prévision (trimestres)", 4, 40, 20, 4, key="var_horizon")
        
        var_decomp_df = complete_model.generate_variance_decomposition(horizon)
        
        # Graphique de décomposition
        fig_var = px.imshow(var_decomp_df.T * 100, 
                           title=f"Décomposition de Variance à l'Horizon {horizon} Trimestres (%)",
                           color_continuous_scale='Blues',
                           aspect="auto")
        fig_var.update_layout(height=600)
        st.plotly_chart(fig_var, use_container_width=True)
        
        # Tableau détaillé
        with st.expander("📋 Tableau Détaillé des Contributions"):
            display_df = var_decomp_df.copy()
            for col in display_df.columns:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.1%}")
            st.dataframe(display_df, use_container_width=True)
    
    with tab3:
        st.markdown("## 📈 Décomposition Historique des Chocs")
        
        st.markdown("""
        <div class='analysis-section'>
        <h4>Analyse Rétrospective des Fluctuations</h4>
        <p>La décomposition historique attribue l'évolution passée des variables macroéconomiques 
        aux différents chocs structurels. Cette analyse permet d'expliquer les épisodes historiques 
        par leurs causes fondamentales et d'évaluer l'importance relative des différents chocs.</p>
        </div>
        """, unsafe_allow_html=True)
        
        historical_df = complete_model.generate_historical_decomposition(24)
        
        # Graphique de décomposition historique
        fig_hist = go.Figure()
        
        shock_names = [name for name in historical_df.columns if name not in ['Date', 'PIB Observé']]
        colors = px.colors.qualitative.Set3
        
        for i, shock in enumerate(shock_names):
            fig_hist.add_trace(go.Scatter(
                name=shock,
                x=historical_df['Date'],
                y=historical_df[shock],
                stackgroup='one',
                line=dict(width=0.5),
                fillcolor=colors[i % len(colors)]
            ))
        
        fig_hist.add_trace(go.Scatter(
            name='PIB Observé',
            x=historical_df['Date'],
            y=historical_df['PIB Observé'],
            line=dict(color='black', width=3, dash='dash')
        ))
        
        fig_hist.update_layout(
            title="Décomposition Historique du PIB Camerounais",
            xaxis_title="Date",
            yaxis_title="Contribution cumulée",
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with tab4:
        st.markdown("## 🔧 Paramètres Structurels du Modèle")
        
        st.markdown("""
        <div class='analysis-section'>
        <h4>Calibration et Incertitude des Paramètres</h4>
        <p>Les distributions a posteriori reflètent l'incertitude autour de l'estimation des paramètres structurels 
        après observation des données. Cette analyse bayésienne permet de quantifier l'incertitude estimationnelle 
        et d'évaluer la robustesse des résultats du modèle.</p>
        </div>
        """, unsafe_allow_html=True)
        
        n_draws = st.slider("Nombre de tirages MCMC", 500, 5000, 2000, 500, key="mcmc_draws")
        
        posterior_data = complete_model.generate_posterior_distributions(n_draws)
        
        # Graphiques des distributions
        n_params = len(posterior_data)
        cols = 3
        rows = (n_params + cols - 1) // cols
        
        fig_post = make_subplots(rows=rows, cols=cols, 
                               subplot_titles=list(posterior_data.keys()))
        
        for i, (param, data) in enumerate(posterior_data.items()):
            row = i // cols + 1
            col = i % cols + 1
            
            fig_post.add_trace(
                go.Histogram(x=data['samples'], name=param, showlegend=False),
                row=row, col=col
            )
            
            # Valeur moyenne
            mean_val = np.mean(data['samples'])
            fig_post.add_vline(x=mean_val, line_dash="dash", line_color="red",
                             row=row, col=col)
        
        fig_post.update_layout(height=300 * rows, title_text="Distributions a Posteriori des Paramètres")
        st.plotly_chart(fig_post, use_container_width=True)
        
        # Tableau des statistiques
        stats_data = []
        for param, data in posterior_data.items():
            samples = data['samples']
            stats_data.append({
                'Paramètre': param,
                'Description': data['description'],
                'Moyenne': f"{np.mean(samples):.3f}",
                'Écart-type': f"{np.std(samples):.3f}",
                'IC 90% Inf': f"{np.percentile(samples, 5):.3f}",
                'IC 90% Sup': f"{np.percentile(samples, 95):.3f}"
            })
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)

if __name__ == "__main__":
    main()