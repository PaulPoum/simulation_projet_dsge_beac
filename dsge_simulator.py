import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Simulateur DSGE Cameroun-BEAC",
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
    .scenario-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 4px solid #0072CE;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class DSGEModelCameroon:
    def __init__(self):
        # Paramètres de calibration pour le Cameroun
        self.params = {
            'beta': 0.96,        # Facteur d'actualisation
            'sigma': 2.0,        # Aversion au risque
            'phi': 1.5,          # Élasticité inverse de Frisch
            'theta_c': 0.3,      # Part des importations
            'eta': 1.5,          # Élasticité de substitution
            'delta': 0.1,        # Taux de dépréciation
            'alpha': 0.35,       # Part du capital
            'theta': 0.75,       # Rigidité des prix (Calvo)
            'epsilon': 6.0,      # Élasticité substitution biens
            'mu': 0.02,          # Marge bancaire
            'rr': 0.05,          # Ratio réserves obligatoires
            'rho_g': 0.7,        # Persistance dépenses publiques
            'phi_pi': 1.5,       # Réaction inflation (Taylor)
            'phi_y': 0.5,        # Réaction output gap (Taylor)
            'pi_star': 0.03,     # Cible d'inflation
            'rho_i': 0.8,        # Inertie politique monétaire
        }
        
    def simulate_shock(self, shock_type, shock_size, periods=40):
        """Simule différents types de chocs"""
        # Initialisation des variables
        n_vars = 15
        X = np.zeros((n_vars, periods))
        
        # État stationnaire
        ss = np.zeros(n_vars)
        
        # Matrice de transition (simplifiée)
        A = self._build_transition_matrix()
        
        # Vecteur de choc
        shock_vec = np.zeros(n_vars)
        
        # Définition des indices des variables
        Y, C, I, PI, R, W, L, NX, G, TAU, DEBT, CR, SPREAD, RER, YGAP = range(15)
        
        # Application du choc selon le type
        if shock_type == "monetary":
            shock_vec[R] = shock_size  # Choc taux directeur
        elif shock_type == "fiscal":
            shock_vec[G] = shock_size  # Choc dépenses publiques
        elif shock_type == "productivity":
            shock_vec[Y] = shock_size  # Choc productivité
        elif shock_type == "risk":
            shock_vec[SPREAD] = shock_size  # Choc prime de risque
        elif shock_type == "oil_price":
            shock_vec[PI] = shock_size * 0.3  # Effet sur l'inflation
            shock_vec[NX] = -shock_size * 0.2  # Effet sur balance commerciale
        else:
            # Choc par défaut (productivité)
            shock_vec[Y] = shock_size
        
        # Simulation
        for t in range(1, periods):
            if t == 1:
                X[:, t] = A @ ss + shock_vec
            else:
                X[:, t] = A @ X[:, t-1]
        
        # Conversion en DataFrame
        variables = ['PIB', 'Consommation', 'Investissement', 'Inflation', 'Taux_Interet',
                    'Salaire_Reel', 'Travail', 'Exportations_Nettes', 'Depenses_Publiques',
                    'Recettes_Fiscales', 'Dette_Publique', 'Credit', 'Spread_Bancaire',
                    'Taux_Change_Reel', 'Output_Gap']
        
        df = pd.DataFrame(X.T, columns=variables)
        df['Periode'] = range(periods)
        
        return df
    
    def _build_transition_matrix(self):
        """Construit la matrice de transition du modèle"""
        # Matrice simplifiée pour l'exemple
        # En pratique, cette matrice serait dérivée de la solution du modèle
        A = np.array([
            [0.9, 0.1, 0.05, -0.02, -0.1, 0.05, 0.08, 0.02, 0.05, 0.03, 0.01, 0.1, -0.02, 0.03, 0.9],
            [0.3, 0.8, 0.1, -0.01, -0.05, 0.1, 0.05, 0.01, 0.02, 0.01, 0.0, 0.05, -0.01, 0.01, 0.3],
            [0.2, 0.05, 0.7, -0.01, -0.08, 0.08, 0.1, 0.01, 0.03, 0.01, 0.0, 0.15, -0.02, 0.02, 0.2],
            [0.1, 0.02, 0.01, 0.6, 0.15, 0.03, 0.02, 0.01, 0.02, 0.01, 0.01, 0.02, 0.05, 0.08, 0.1],
            [0.05, 0.01, 0.01, 0.2, 0.8, 0.01, 0.01, 0.0, 0.01, 0.0, 0.01, 0.01, 0.1, 0.05, 0.05],
            [0.15, 0.08, 0.05, 0.02, -0.03, 0.85, 0.2, 0.01, 0.02, 0.01, 0.0, 0.08, -0.01, 0.02, 0.15],
            [0.2, 0.1, 0.08, 0.01, -0.05, 0.15, 0.8, 0.01, 0.03, 0.01, 0.0, 0.1, -0.01, 0.01, 0.2],
            [0.05, 0.01, 0.02, 0.03, -0.02, 0.02, 0.01, 0.7, 0.01, 0.0, 0.0, 0.01, 0.02, 0.3, 0.05],
            [0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.0, 0.7, 0.1, 0.05, 0.01, 0.0, 0.0, 0.02],
            [0.03, 0.02, 0.01, 0.02, 0.01, 0.02, 0.01, 0.0, 0.15, 0.8, 0.1, 0.02, 0.0, 0.0, 0.03],
            [0.01, 0.0, 0.0, 0.01, 0.02, 0.0, 0.0, 0.0, 0.1, 0.05, 0.95, 0.0, 0.01, 0.0, 0.01],
            [0.1, 0.05, 0.15, 0.01, -0.1, 0.08, 0.1, 0.01, 0.02, 0.01, 0.0, 0.8, 0.05, 0.02, 0.1],
            [0.02, 0.01, 0.01, 0.05, 0.1, 0.01, 0.01, 0.01, 0.0, 0.0, 0.01, 0.03, 0.8, 0.05, 0.02],
            [0.03, 0.01, 0.02, 0.08, 0.05, 0.02, 0.01, 0.3, 0.0, 0.0, 0.0, 0.02, 0.05, 0.8, 0.03],
            [0.9, 0.3, 0.2, 0.1, 0.05, 0.15, 0.2, 0.05, 0.02, 0.03, 0.01, 0.1, 0.02, 0.03, 0.8]
        ])
        
        return A

def create_modern_irf_plot(df, shock_name):
    """Crée un graphique moderne des fonctions de réponse impulsionnelle"""
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=('PIB et Composantes', 'Inflation et Taux', 
                       'Variables Financières', 'Secteur Public',
                       'Secteur Extérieur', 'Variables Réelles'),
        vertical_spacing=0.08,
        horizontal_spacing=0.08
    )
    
    # PIB et composantes
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['PIB'], 
                            name='PIB', line=dict(color='#1f77b4')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Consommation'], 
                            name='Consommation', line=dict(color='#ff7f0e')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Investissement'], 
                            name='Investissement', line=dict(color='#2ca02c')), row=1, col=1)
    
    # Inflation et taux
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Inflation'], 
                            name='Inflation', line=dict(color='#d62728')), row=1, col=2)
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Taux_Interet'], 
                            name='Taux Directeur', line=dict(color='#9467bd')), row=1, col=2)
    
    # Variables financières
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Credit'], 
                            name='Crédit', line=dict(color='#8c564b')), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Spread_Bancaire'], 
                            name='Spread Bancaire', line=dict(color='#e377c2')), row=2, col=1)
    
    # Secteur public
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Depenses_Publiques'], 
                            name='Dépenses Publiques', line=dict(color='#7f7f7f')), row=2, col=2)
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Dette_Publique'], 
                            name='Dette Publique', line=dict(color='#bcbd22')), row=2, col=2)
    
    # Secteur extérieur
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Exportations_Nettes'], 
                            name='Exportations Nettes', line=dict(color='#17becf')), row=3, col=1)
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Taux_Change_Reel'], 
                            name='Taux Change Réel', line=dict(color='#ff9896')), row=3, col=1)
    
    # Variables réelles
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Salaire_Reel'], 
                            name='Salaire Réel', line=dict(color='#aec7e8')), row=3, col=2)
    fig.add_trace(go.Scatter(x=df['Periode'], y=df['Travail'], 
                            name='Travail', line=dict(color='#ffbb78')), row=3, col=2)
    
    fig.update_layout(
        height=800,
        title_text=f"Fonctions de Réponse Impulsionnelle - Choc {shock_name}",
        showlegend=True,
        template="plotly_white"
    )
    
    return fig

def generate_analysis_report(df, shock_type, shock_size):
    """Génère un rapport d'analyse automatique"""
    
    # Calcul des impacts maximaux
    max_impact_pib = df['PIB'].max()
    min_impact_pib = df['PIB'].min()
    final_impact_pib = df['PIB'].iloc[-1]
    
    max_impact_inflation = df['Inflation'].max()
    impact_credit = df['Credit'].iloc[8]  # Impact à moyen terme
    
    # Analyse selon le type de choc
    if shock_type == "monetary":
        analysis = f"""
        ## 📈 Analyse du Choc Monétaire (+{shock_size*100:.1f} points de TIAO)
        
        **Transmission du choc :**
        - 🎯 **Impact immédiat** : Hausse des taux → resserrement du crédit
        - ⏳ **Effet retardé** : Baisse de l'investissement et consommation
        - 📉 **Impact final** : Ralentissement de l'activité économique
        
        **Dynamique observée :**
        - Crédit bancaire : {impact_credit:+.3f} (période 8)
        - PIB maximal : {max_impact_pib:+.3f}
        - Inflation : {max_impact_inflation:+.3f}
        
        **Implications politiques :**
        - La BEAC doit anticiper les effets récessifs
        - Coordination nécessaire avec la politique budgétaire
        - Surveillance du canal du crédit bancaire
        """
        
    elif shock_type == "fiscal":
        analysis = f"""
        ## 🇨🇲 Analyse du Choc Budgétaire (+{shock_size*100:.1f}% PIB dépenses)
        
        **Multiplicateur budgétaire :**
        - 📊 **Impact court terme** : Stimulation de la demande
        - 💰 **Effet richesse** : Hausse consommation et investissement
        - 🏛️ **Dynamique dette** : Dégradation temporaire des finances publiques
        
        **Indicateurs clés :**
        - Multiplicateur à 1 an : {df['PIB'].iloc[4]/shock_size:.2f}
        - Impact dette : {df['Dette_Publique'].iloc[-1]:+.3f}
        - Effet inflation : {max_impact_inflation:+.3f}
        
        **Recommandations :**
        - Cibler les dépenses d'investissement productif
        - Plan de consolidation à moyen terme
        - Coordination avec la BEAC sur les implications monétaires
        """
    
    elif shock_type == "productivity":
        analysis = f"""
        ## 🏭 Analyse du Choc de Productivité (+{shock_size*100:.1f}% PTF)
        
        **Effets structurels :**
        - 🚀 **Croissance potentielle** : Amélioration durable
        - 💹 **Gains de compétitivité** : Hausse des exportations
        - 📉 **Pression désinflationniste** : Baisse des prix
        
        **Impacts observés :**
        - PIB : {max_impact_pib:+.3f}
        - Inflation : {max_impact_inflation:+.3f}
        - Exportations : {df['Exportations_Nettes'].max():+.3f}
        
        **Politiques d'accompagnement :**
        - Investissement dans l'éducation et R&D
        - Réformes structurelles pour maintenir les gains
        - Adaptation de la politique monétaire au nouveau potentiel
        """
    
    elif shock_type == "risk":
        analysis = f"""
        ## 📉 Analyse du Choc de Risque (+{shock_size*100:.1f} points de spread)
        
        **Transmission financière :**
        - 🏦 **Coût du crédit** : Hausse des taux pour les emprunteurs
        - 💸 **Rationnement du crédit** : Baisse de l'offre de prêts
        - 📊 **Ralentissement économique** : Impact sur l'investissement
        
        **Indicateurs :**
        - Spread bancaire : {df['Spread_Bancaire'].max():+.3f}
        - Crédit : {impact_credit:+.3f}
        - PIB : {min_impact_pib:+.3f}
        
        **Actions recommandées :**
        - Renforcement de la supervision bancaire
        - Mesures de soutien à l'accès au crédit
        - Communication transparente sur la stabilité financière
        """
    
    elif shock_type == "oil_price":
        analysis = f"""
        ## 🛢️ Analyse du Choc Pétrolier (+{shock_size*100:.1f}% prix)
        
        **Effets termes de l'échange :**
        - 📈 **Revenus d'exportation** : Amélioration pour le Cameroun
        - 💰 **Pressions inflationnistes** : Hausse des coûts de production
        - 📊 **Balance commerciale** : Amélioration temporaire
        
        **Impacts :**
        - Inflation : {max_impact_inflation:+.3f}
        - Exportations nettes : {df['Exportations_Nettes'].max():+.3f}
        - PIB : {max_impact_pib:+.3f}
        
        **Gestion macroéconomique :**
        - Épargne des revenus exceptionnels (fonds souverain)
        - Politique monétaire vigilante sur l'inflation
        - Diversification économique à moyen terme
        """
    
    else:
        # Analyse par défaut pour les chocs non spécifiés
        analysis = f"""
        ## 📊 Analyse du Choc Économique
        
        **Impacts globaux observés :**
        - PIB maximum : {max_impact_pib:+.3f}
        - Inflation : {max_impact_inflation:+.3f}
        - Crédit bancaire : {impact_credit:+.3f}
        - Dette publique : {df['Dette_Publique'].iloc[-1]:+.3f}
        
        **Recommandations générales :**
        - Surveillance continue des indicateurs
        - Coordination des politiques économique et monétaire
        - Communication transparente avec les marchés
        """
    
    return analysis

def main():
    # En-tête moderne
    st.markdown('<h1 class="main-header">🏦 Simulateur DSGE Cameroun-BEAC</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 2rem;'>
    Modèle Dynamique Stochastique d'Équilibre Général pour l'analyse des politiques économiques<br>
    <em>Développé par la Section Suivi des Politiques Economiques et de l'Inclusion Financière</em>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar pour les paramètres
    with st.sidebar:
        st.markdown("### ⚙️ Paramètres de Simulation")
        
        shock_type = st.selectbox(
            "Type de Choc",
            ["monetary", "fiscal", "productivity", "risk", "oil_price"],
            format_func=lambda x: {
                "monetary": "💰 Politique Monétaire (TIAO)",
                "fiscal": "🏛️ Politique Budgétaire",
                "productivity": "🏭 Productivité (PTF)",
                "risk": "📉 Prime de Risque",
                "oil_price": "🛢️ Prix Pétrole"
            }[x]
        )
        
        shock_size = st.slider(
            "Amplitude du Choc (%)",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1
        ) / 100  # Conversion en decimal
        
        periods = st.slider(
            "Périodes de Simulation (trimestres)",
            min_value=20,
            max_value=60,
            value=40,
            step=4
        )
        
        st.markdown("---")
        st.markdown("### 📊 Options d'Affichage")
        show_analysis = st.checkbox("Afficher l'analyse détaillée", value=True)
        show_metrics = st.checkbox("Afficher les métriques clés", value=True)
    
    # Initialisation du modèle
    model = DSGEModelCameroon()
    
    # Simulation
    with st.spinner("🚀 Simulation en cours..."):
        df_simulation = model.simulate_shock(shock_type, shock_size, periods)
    
    # Métriques clés
    if show_metrics:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>📈 PIB Max</h3>
                <h2>{df_simulation['PIB'].max():+.3f}</h2>
                <p>Impact maximum</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>💰 Inflation</h3>
                <h2>{df_simulation['Inflation'].max():+.3f}</h2>
                <p>Point de pourcentage</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🏛️ Dette</h3>
                <h2>{df_simulation['Dette_Publique'].iloc[-1]:+.3f}</h2>
                <p>Impact final</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>💳 Crédit</h3>
                <h2>{df_simulation['Credit'].iloc[8]:+.3f}</h2>
                <p>Période 8</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Graphique principal
    st.markdown("## 📊 Fonctions de Réponse Impulsionnelle")
    shock_display_names = {
        "monetary": "Politique Monétaire",
        "fiscal": "Politique Budgétaire",
        "productivity": "Productivité",
        "risk": "Prime de Risque",
        "oil_price": "Prix Pétrole"
    }
    fig = create_modern_irf_plot(df_simulation, shock_display_names[shock_type])
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse automatique
    if show_analysis:
        st.markdown("## 🧠 Analyse Économique")
        analysis_report = generate_analysis_report(df_simulation, shock_type, shock_size)
        st.markdown(analysis_report)
    
    # Données détaillées
    with st.expander("📋 Données Détaillées de la Simulation"):
        st.dataframe(df_simulation.style.format("{:.4f}"), use_container_width=True)
        
        # Bouton d'export
        csv = df_simulation.to_csv(index=False)
        st.download_button(
            label="📥 Exporter les données CSV",
            data=csv,
            file_name=f"dsge_simulation_{shock_type}.csv",
            mime="text/csv"
        )
    
    # Section de comparaison de scénarios
    st.markdown("## 🔄 Comparaison Multi-Scénarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        compare_shock = st.selectbox(
            "Scénario de comparaison",
            ["monetary", "fiscal", "productivity"],
            format_func=lambda x: {
                "monetary": "Politique Monétaire",
                "fiscal": "Politique Budgétaire", 
                "productivity": "Choc Productivité"
            }[x],
            key="compare"
        )
    
    with col2:
        compare_size = st.slider(
            "Amplitude comparaison (%)",
            min_value=0.1,
            max_value=5.0,
            value=2.0,
            step=0.1,
            key="compare_size"
        ) / 100
    
    if st.button("🔄 Comparer les Scénarios"):
        df_compare = model.simulate_shock(compare_shock, compare_size, periods)
        
        # Graphique de comparaison
        fig_compare = go.Figure()
        
        fig_compare.add_trace(go.Scatter(
            x=df_simulation['Periode'], y=df_simulation['PIB'],
            name=f'Scénario principal ({shock_display_names[shock_type]})',
            line=dict(color='blue', width=3)
        ))
        
        fig_compare.add_trace(go.Scatter(
            x=df_compare['Periode'], y=df_compare['PIB'],
            name=f'Scénario comparé ({shock_display_names[compare_shock]})',
            line=dict(color='red', width=3, dash='dash')
        ))
        
        fig_compare.update_layout(
            title="Comparaison des Impacts sur le PIB",
            xaxis_title="Périodes",
            yaxis_title="Écart (%)",
            template="plotly_white"
        )
        
        st.plotly_chart(fig_compare, use_container_width=True)

if __name__ == "__main__":
    main()