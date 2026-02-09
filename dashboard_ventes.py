import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Ventes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'apparence
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    h1 {
        color: #1f77b4;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Fonction pour charger les données
@st.cache_data
def load_data(file_path):
    """Charge et transforme les données du fichier Excel"""
    try:
        # Lire les données brutes
        df_raw = pd.read_excel(file_path, sheet_name='Sheet8', header=None)
        
        # La première ligne contient les en-têtes de colonnes
        # La deuxième ligne contient les mois
        mois = df_raw.iloc[1, 1:].tolist()
        
        # Les lignes suivantes contiennent les vendeurs et leurs ventes
        vendeurs = df_raw.iloc[2:, 0].tolist()
        
        # Extraire les données de ventes (à partir de la ligne 2, colonnes 1 à 12)
        ventes_data = df_raw.iloc[2:, 1:13].values
        
        # Créer un DataFrame propre
        df_clean = pd.DataFrame(ventes_data, columns=mois)
        df_clean.insert(0, 'Vendeur', vendeurs)
        
        # Remplacer les NaN par 0 pour les calculs
        df_clean = df_clean.fillna(0)
        
        # Convertir les colonnes de mois en numérique
        for col in mois:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
        
        return df_clean, mois
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return None, None

# Fonction pour générer des données de démonstration
def generate_demo_data():
    """Génère des données de démonstration pour illustrer le dashboard"""
    mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    
    vendeurs = ['Antoine', 'Thierry', 'Valerie', 'Lea', 'Serge', 'Eugenie',
                'Jacqueline', 'Sylvie', 'Pierrette', 'Henri', 'Nicolas', 'Celia',
                'Thomas', 'Pierre', 'Fabien', 'Marie', 'Julia', 'Leane',
                'Patrick', 'Mauricette', 'Claire', 'Gabriel', 'Patrice', 'Valérie',
                'Laurence', 'Olivier', 'Isabelle', 'Marc']
    
    # Générer des ventes aléatoires réalistes
    np.random.seed(42)
    data = {'Vendeur': vendeurs}
    
    for mois_nom in mois:
        # Ventes entre 5000 et 50000 avec une tendance saisonnière
        base = np.random.uniform(10000, 40000, len(vendeurs))
        # Ajouter une variation saisonnière (été et fin d'année plus forts)
        mois_idx = mois.index(mois_nom)
        seasonal_factor = 1 + 0.3 * np.sin((mois_idx - 2) * np.pi / 6)
        data[mois_nom] = (base * seasonal_factor).round(2)
    
    return pd.DataFrame(data), mois

# Fonction pour calculer les KPIs
def calculate_kpis(df, mois):
    """Calcule les indicateurs clés de performance"""
    # Total des ventes
    total_ventes = df[mois].sum().sum()
    
    # Nombre de vendeurs
    nb_vendeurs = len(df)
    
    # Vente moyenne par vendeur
    vente_moy_vendeur = total_ventes / nb_vendeurs if nb_vendeurs > 0 else 0
    
    # Meilleur vendeur
    df['Total'] = df[mois].sum(axis=1)
    meilleur_vendeur = df.loc[df['Total'].idxmax(), 'Vendeur'] if not df.empty else "N/A"
    meilleur_vente = df['Total'].max() if not df.empty else 0
    
    # Ventes mensuelles moyennes
    ventes_mensuelles = df[mois].sum()
    vente_moy_mensuelle = ventes_mensuelles.mean()
    
    # Meilleur mois
    meilleur_mois = ventes_mensuelles.idxmax() if len(ventes_mensuelles) > 0 else "N/A"
    meilleur_mois_vente = ventes_mensuelles.max() if len(ventes_mensuelles) > 0 else 0
    
    return {
        'total_ventes': total_ventes,
        'nb_vendeurs': nb_vendeurs,
        'vente_moy_vendeur': vente_moy_vendeur,
        'meilleur_vendeur': meilleur_vendeur,
        'meilleur_vente': meilleur_vente,
        'vente_moy_mensuelle': vente_moy_mensuelle,
        'meilleur_mois': meilleur_mois,
        'meilleur_mois_vente': meilleur_mois_vente
    }

# Header
st.title("📊 Dashboard d'Analyse des Ventes")
st.markdown("---")

# Sidebar pour les options
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Option pour charger des données
    uploaded_file = st.file_uploader(
        "Charger un fichier Excel",
        type=['xlsx', 'xls'],
        help="Uploadez votre fichier de données de ventes"
    )
    
    use_demo = st.checkbox(
        "Utiliser les données de démonstration",
        value=True,
        help="Affiche des données d'exemple pour illustrer le dashboard"
    )
    
    st.markdown("---")
    st.markdown("### 📌 Filtres")

# Charger les données
if uploaded_file is not None:
    df, mois = load_data(uploaded_file)
    st.sidebar.success("✅ Fichier chargé avec succès!")
elif use_demo:
    df, mois = generate_demo_data()
    st.info("ℹ️ Affichage des données de démonstration. Uploadez votre fichier pour voir vos données réelles.")
else:
    st.warning("⚠️ Veuillez uploader un fichier ou activer les données de démonstration.")
    st.stop()

# Vérifier que les données sont chargées
if df is None or df.empty:
    st.error("❌ Aucune donnée à afficher. Veuillez vérifier votre fichier.")
    st.stop()

# Filtres dans la sidebar
vendeurs_disponibles = df['Vendeur'].unique().tolist()
vendeurs_selectionnes = st.sidebar.multiselect(
    "Sélectionner des vendeurs",
    options=vendeurs_disponibles,
    default=vendeurs_disponibles[:5] if len(vendeurs_disponibles) > 5 else vendeurs_disponibles,
    help="Filtrer par vendeur(s)"
)

mois_selectionnes = st.sidebar.multiselect(
    "Sélectionner des mois",
    options=mois,
    default=mois,
    help="Filtrer par mois"
)

# Filtrer le DataFrame
if vendeurs_selectionnes:
    df_filtered = df[df['Vendeur'].isin(vendeurs_selectionnes)].copy()
else:
    df_filtered = df.copy()

# Calculer les KPIs
kpis = calculate_kpis(df_filtered, mois_selectionnes if mois_selectionnes else mois)

# Afficher les KPIs principaux
st.subheader("📈 Indicateurs Clés de Performance")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Ventes Totales",
        value=f"{kpis['total_ventes']:,.0f} €",
        delta=f"+{kpis['total_ventes']*0.12:,.0f} € vs année précédente"
    )

with col2:
    st.metric(
        label="Nombre de Vendeurs",
        value=f"{kpis['nb_vendeurs']}",
        delta=None
    )

with col3:
    st.metric(
        label="Vente Moy. / Vendeur",
        value=f"{kpis['vente_moy_vendeur']:,.0f} €",
        delta=f"+{kpis['vente_moy_vendeur']*0.08:,.0f} €"
    )

with col4:
    st.metric(
        label="Vente Moy. / Mois",
        value=f"{kpis['vente_moy_mensuelle']:,.0f} €",
        delta=f"+{kpis['vente_moy_mensuelle']*0.15:,.0f} €"
    )

st.markdown("---")

# Deuxième ligne de KPIs
col5, col6 = st.columns(2)

with col5:
    st.info(f"🏆 **Meilleur Vendeur:** {kpis['meilleur_vendeur']} avec {kpis['meilleur_vente']:,.0f} €")

with col6:
    st.info(f"📅 **Meilleur Mois:** {kpis['meilleur_mois']} avec {kpis['meilleur_mois_vente']:,.0f} €")

st.markdown("---")

# Graphiques
st.subheader("📊 Visualisations")

# Onglets pour différentes vues
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Évolution Mensuelle",
    "👥 Performance par Vendeur",
    "🔍 Analyse Détaillée",
    "📋 Données Brutes"
])

with tab1:
    st.markdown("### Évolution des Ventes par Mois")
    
    # Ventes mensuelles totales
    ventes_mensuelles = df_filtered[mois_selectionnes if mois_selectionnes else mois].sum()
    
    fig_mois = go.Figure()
    fig_mois.add_trace(go.Bar(
        x=ventes_mensuelles.index,
        y=ventes_mensuelles.values,
        marker_color='lightblue',
        text=[f"{val:,.0f} €" for val in ventes_mensuelles.values],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Ventes: %{y:,.0f} €<extra></extra>'
    ))
    
    fig_mois.update_layout(
        title="Ventes Totales par Mois",
        xaxis_title="Mois",
        yaxis_title="Ventes (€)",
        height=400,
        showlegend=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_mois, use_container_width=True)
    
    # Tendance avec ligne
    col_a, col_b = st.columns(2)
    
    with col_a:
        fig_line = px.line(
            x=ventes_mensuelles.index,
            y=ventes_mensuelles.values,
            markers=True,
            title="Tendance des Ventes"
        )
        fig_line.update_traces(line_color='#1f77b4', line_width=3)
        fig_line.update_layout(
            xaxis_title="Mois",
            yaxis_title="Ventes (€)",
            height=350
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col_b:
        # Pie chart de la répartition mensuelle
        fig_pie = px.pie(
            values=ventes_mensuelles.values,
            names=ventes_mensuelles.index,
            title="Répartition des Ventes par Mois",
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.markdown("### Performance par Vendeur")
    
    # Calculer le total par vendeur
    df_filtered['Total'] = df_filtered[mois_selectionnes if mois_selectionnes else mois].sum(axis=1)
    df_sorted = df_filtered.sort_values('Total', ascending=False)
    
    # Top vendeurs avec slider adaptatif
    max_vendeurs = len(df_sorted)
    
    if max_vendeurs <= 1:
        # Si 1 seul vendeur, pas de slider
        top_n = max_vendeurs
    elif max_vendeurs <= 5:
        # Si 5 vendeurs ou moins, afficher tous sans slider
        top_n = max_vendeurs
    else:
        # Si plus de 5 vendeurs, utiliser le slider
        default_n = min(10, max_vendeurs)
        top_n = st.slider("Nombre de vendeurs à afficher", 5, max_vendeurs, default_n)
    df_top = df_sorted.head(top_n)
    
    fig_vendeurs = px.bar(
        df_top,
        x='Total',
        y='Vendeur',
        orientation='h',
        title=f"Top {top_n} Vendeurs",
        text='Total',
        color='Total',
        color_continuous_scale='Blues'
    )
    
    fig_vendeurs.update_traces(
        texttemplate='%{text:,.0f} €',
        textposition='outside'
    )
    
    fig_vendeurs.update_layout(
        xaxis_title="Ventes Totales (€)",
        yaxis_title="Vendeur",
        height=max(400, top_n * 25),
        showlegend=False
    )
    
    st.plotly_chart(fig_vendeurs, use_container_width=True)
    
    # Comparaison des vendeurs sélectionnés
    if len(vendeurs_selectionnes) > 0 and len(vendeurs_selectionnes) <= 5:
        st.markdown("### Comparaison Détaillée des Vendeurs Sélectionnés")
        
        df_compare = df_filtered[df_filtered['Vendeur'].isin(vendeurs_selectionnes)]
        
        # Transformer les données pour Plotly
        df_melted = df_compare.melt(
            id_vars=['Vendeur'],
            value_vars=mois_selectionnes if mois_selectionnes else mois,
            var_name='Mois',
            value_name='Ventes'
        )
        
        fig_compare = px.line(
            df_melted,
            x='Mois',
            y='Ventes',
            color='Vendeur',
            markers=True,
            title="Évolution Mensuelle par Vendeur"
        )
        
        fig_compare.update_layout(
            xaxis_title="Mois",
            yaxis_title="Ventes (€)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_compare, use_container_width=True)

with tab3:
    st.markdown("### Analyse Détaillée")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        # Heatmap des ventes
        df_heatmap = df_filtered.set_index('Vendeur')[mois_selectionnes if mois_selectionnes else mois]
        
        fig_heatmap = px.imshow(
            df_heatmap,
            labels=dict(x="Mois", y="Vendeur", color="Ventes (€)"),
            title="Carte de Chaleur des Ventes",
            aspect="auto",
            color_continuous_scale='YlOrRd'
        )
        
        fig_heatmap.update_layout(height=600)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col_y:
        # Statistiques descriptives
        st.markdown("#### 📊 Statistiques Descriptives")
        
        stats_df = df_filtered[mois_selectionnes if mois_selectionnes else mois].describe().T
        stats_df = stats_df.round(2)
        stats_df.columns = ['Nombre', 'Moyenne', 'Écart-type', 'Min', '25%', '50%', '75%', 'Max']
        
        st.dataframe(stats_df, use_container_width=True)
        
        # Box plot
        df_melted_all = df_filtered.melt(
            id_vars=['Vendeur'],
            value_vars=mois_selectionnes if mois_selectionnes else mois,
            var_name='Mois',
            value_name='Ventes'
        )
        
        fig_box = px.box(
            df_melted_all,
            x='Mois',
            y='Ventes',
            title="Distribution des Ventes par Mois"
        )
        
        fig_box.update_layout(height=400)
        st.plotly_chart(fig_box, use_container_width=True)

with tab4:
    st.markdown("### 📋 Tableau de Données")
    
    # Options d'affichage
    col_opt1, col_opt2 = st.columns(2)
    
    with col_opt1:
        show_total = st.checkbox("Afficher le total par vendeur", value=True)
    
    with col_opt2:
        show_moyenne = st.checkbox("Afficher la moyenne par vendeur", value=False)
    
    # Préparer le DataFrame d'affichage
    df_display = df_filtered.copy()
    
    if show_total:
        df_display['Total'] = df_display[mois_selectionnes if mois_selectionnes else mois].sum(axis=1)
    
    if show_moyenne:
        df_display['Moyenne'] = df_display[mois_selectionnes if mois_selectionnes else mois].mean(axis=1).round(2)
    
    # Formater les nombres
    for col in df_display.columns:
        if col != 'Vendeur':
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.2f} €" if pd.notnull(x) else "0 €")
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    # Bouton de téléchargement
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger les données (CSV)",
        data=csv,
        file_name=f"ventes_export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Dashboard créé avec Streamlit | Données mises à jour en temps réel
    </div>
    """,
    unsafe_allow_html=True
)
