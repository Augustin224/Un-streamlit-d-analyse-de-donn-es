import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Analyse de Données Universel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #031230;
        padding: 15px;
        border-radius: 10px;
    }
    h1 {
        color: #be0d89;
    }
    </style>
""", unsafe_allow_html=True)

# Fonction pour détecter le type de colonnes
def detect_column_types(df):
    """Détecte automatiquement les types de colonnes"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # Tenter de détecter les colonnes de dates non typées
    for col in text_cols:
        try:
            pd.to_datetime(df[col], errors='raise')
            date_cols.append(col)
            text_cols.remove(col)
        except:
            pass
    
    return {
        'numeric': numeric_cols,
        'text': text_cols,
        'date': date_cols
    }

# Fonction pour charger n'importe quel fichier
@st.cache_data
def load_data(file):
    """Charge automatiquement différents types de fichiers"""
    try:
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension in ['csv', 'txt']:
            # Essayer différents séparateurs
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except:
                try:
                    df = pd.read_csv(file, encoding='latin-1')
                except:
                    df = pd.read_csv(file, sep=';', encoding='utf-8')
        
        elif file_extension in ['xlsx', 'xls']:
            # Lire Excel
            excel_file = pd.ExcelFile(file)
            
            # Si plusieurs feuilles, demander laquelle utiliser
            if len(excel_file.sheet_names) > 1:
                sheet_name = st.sidebar.selectbox(
                    "Sélectionner la feuille Excel",
                    excel_file.sheet_names
                )
            else:
                sheet_name = excel_file.sheet_names[0]
            
            df = pd.read_excel(file, sheet_name=sheet_name)
            
            # Nettoyer les en-têtes si nécessaire
            if df.columns[0] == 'Unnamed: 0' or 'Column' in str(df.columns[0]):
                # Vérifier si la première ligne contient les vrais en-têtes
                if df.iloc[0].notna().sum() > df.columns.notna().sum() / 2:
                    df.columns = df.iloc[0]
                    df = df.iloc[1:].reset_index(drop=True)
        
        elif file_extension == 'json':
            df = pd.read_json(file)
        
        else:
            st.error(f"Format de fichier non supporté: .{file_extension}")
            return None
        
        # Nettoyer le DataFrame
        df = df.dropna(how='all')  # Supprimer les lignes complètement vides
        df = df.dropna(axis=1, how='all')  # Supprimer les colonnes complètement vides
        
        # Convertir les colonnes numériques qui sont en texte
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        return df
    
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {e}")
        return None

# Fonction pour générer des données de démonstration
def generate_demo_data():
    """Génère des données de démonstration variées"""
    np.random.seed(42)
    
    demo_type = st.sidebar.radio(
        "Type de données de démonstration",
        ["Ventes", "RH/Employés", "Finance", "Marketing"]
    )
    
    if demo_type == "Ventes":
        vendeurs = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry']
        regions = ['Nord', 'Sud', 'Est', 'Ouest']
        produits = ['Produit A', 'Produit B', 'Produit C', 'Produit D']
        
        data = {
            'Vendeur': np.random.choice(vendeurs, 100),
            'Région': np.random.choice(regions, 100),
            'Produit': np.random.choice(produits, 100),
            'Ventes': np.random.uniform(1000, 50000, 100).round(2),
            'Quantité': np.random.randint(1, 100, 100),
            'Date': pd.date_range('2024-01-01', periods=100, freq='D')
        }
        
    elif demo_type == "RH/Employés":
        departements = ['IT', 'Marketing', 'Ventes', 'RH', 'Finance']
        postes = ['Junior', 'Senior', 'Manager', 'Directeur']
        
        data = {
            'Nom': [f'Employé {i}' for i in range(1, 51)],
            'Département': np.random.choice(departements, 50),
            'Poste': np.random.choice(postes, 50),
            'Salaire': np.random.uniform(30000, 120000, 50).round(2),
            'Ancienneté': np.random.randint(1, 20, 50),
            'Performance': np.random.uniform(60, 100, 50).round(1)
        }
        
    elif demo_type == "Finance":
        categories = ['Revenus', 'Dépenses', 'Investissements', 'Économies']
        
        data = {
            'Catégorie': np.random.choice(categories, 80),
            'Montant': np.random.uniform(-50000, 100000, 80).round(2),
            'Mois': pd.date_range('2024-01-01', periods=80, freq='M').strftime('%B %Y').tolist(),
            'Sous-catégorie': np.random.choice(['Type A', 'Type B', 'Type C'], 80)
        }
        
    else:  # Marketing
        canaux = ['Email', 'Réseaux Sociaux', 'SEO', 'Publicité', 'Direct']
        
        data = {
            'Canal': np.random.choice(canaux, 60),
            'Impressions': np.random.randint(1000, 100000, 60),
            'Clics': np.random.randint(10, 5000, 60),
            'Conversions': np.random.randint(1, 500, 60),
            'Coût': np.random.uniform(100, 10000, 60).round(2),
            'Date': pd.date_range('2024-01-01', periods=60, freq='W')
        }
    
    return pd.DataFrame(data)

# Fonction pour calculer les statistiques
def calculate_stats(df, numeric_cols):
    """Calcule les statistiques clés"""
    stats = {}
    
    for col in numeric_cols:
        stats[col] = {
            'total': df[col].sum(),
            'moyenne': df[col].mean(),
            'median': df[col].median(),
            'min': df[col].min(),
            'max': df[col].max(),
            'std': df[col].std()
        }
    
    return stats

# Header
st.title("📊 Dashboard d'Analyse de Données Universel")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Option de chargement
    data_source = st.radio(
        "Source de données",
        ["Uploader un fichier", "Données de démonstration"]
    )
    
    st.markdown("---")

# Charger les données
df = None

if data_source == "Uploader un fichier":
    uploaded_file = st.sidebar.file_uploader(
        "Charger votre fichier",
        type=['csv', 'xlsx', 'xls', 'txt', 'json'],
        help="Formats supportés: CSV, Excel, TXT, JSON"
    )
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if df is not None:
            st.sidebar.success(f"✅ Fichier chargé: {uploaded_file.name}")
            st.sidebar.info(f"📊 {len(df)} lignes × {len(df.columns)} colonnes")
    else:
        st.info("👆 Veuillez uploader un fichier pour commencer l'analyse")
        st.stop()

else:
    df = generate_demo_data()
    st.info("ℹ️ Affichage des données de démonstration")

# Vérifier que les données sont chargées
if df is None or df.empty:
    st.error("❌ Aucune donnée disponible")
    st.stop()

# Détecter les types de colonnes
col_types = detect_column_types(df)

# Afficher un aperçu rapide
with st.expander("👁️ Aperçu des données (premières lignes)", expanded=False):
    st.dataframe(df.head(10), use_container_width=True)

# Filtres dynamiques dans la sidebar
st.sidebar.markdown("### 🔍 Filtres")

# Filtres pour colonnes textuelles
df_filtered = df.copy()

for col in col_types['text']:
    unique_values = df[col].dropna().unique().tolist()
    if len(unique_values) <= 50:  # Limite pour éviter trop d'options
        selected = st.sidebar.multiselect(
            f"Filtrer par {col}",
            options=unique_values,
            default=unique_values[:min(10, len(unique_values))],
            key=f"filter_{col}"
        )
        if selected:
            df_filtered = df_filtered[df_filtered[col].isin(selected)]

# Filtres pour colonnes numériques
for col in col_types['numeric']:
    if df[col].notna().sum() > 0:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        
        if min_val < max_val:
            selected_range = st.sidebar.slider(
                f"Plage {col}",
                min_val,
                max_val,
                (min_val, max_val),
                key=f"range_{col}"
            )
            df_filtered = df_filtered[
                (df_filtered[col] >= selected_range[0]) & 
                (df_filtered[col] <= selected_range[1])
            ]

# KPIs principaux
st.subheader("📈 Indicateurs Clés")

# Créer des colonnes pour les KPIs
if len(col_types['numeric']) > 0:
    num_kpis = min(4, len(col_types['numeric']))
    kpi_cols = st.columns(num_kpis)
    
    for i, col in enumerate(col_types['numeric'][:num_kpis]):
        with kpi_cols[i]:
            total = df_filtered[col].sum()
            moyenne = df_filtered[col].mean()
            delta = moyenne * 0.12  # Simulation de variation
            
            st.metric(
                label=f"{col} (Total)",
                value=f"{total:,.2f}" if abs(total) < 1000000 else f"{total/1000000:.2f}M",
                delta=f"+{delta:,.2f}"
            )

st.markdown("---")

# Onglets d'analyse
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Vue d'ensemble",
    "📈 Analyses numériques",
    "🔍 Analyses catégorielles",
    "📉 Corrélations",
    "📋 Données brutes"
])

with tab1:
    st.markdown("### 📊 Résumé des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📏 Dimensions")
        st.write(f"**Nombre de lignes:** {len(df_filtered):,}")
        st.write(f"**Nombre de colonnes:** {len(df_filtered.columns)}")
        st.write(f"**Colonnes numériques:** {len(col_types['numeric'])}")
        st.write(f"**Colonnes textuelles:** {len(col_types['text'])}")
        st.write(f"**Colonnes de dates:** {len(col_types['date'])}")
    
    with col2:
        st.markdown("#### ℹ️ Informations")
        missing = df_filtered.isnull().sum().sum()
        total_cells = df_filtered.shape[0] * df_filtered.shape[1]
        st.write(f"**Valeurs manquantes:** {missing:,} ({100*missing/total_cells:.2f}%)")
        st.write(f"**Mémoire utilisée:** {df_filtered.memory_usage(deep=True).sum() / 1024:.2f} KB")
    
    # Graphique de distribution global
    if len(col_types['numeric']) > 0:
        st.markdown("### 📊 Distribution des Variables Numériques")
        
        selected_numeric = st.selectbox(
            "Sélectionner une variable à visualiser",
            col_types['numeric']
        )
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            fig_hist = px.histogram(
                df_filtered,
                x=selected_numeric,
                title=f"Distribution de {selected_numeric}",
                marginal="box"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col_b:
            fig_box = px.box(
                df_filtered,
                y=selected_numeric,
                title=f"Boîte à moustaches - {selected_numeric}"
            )
            st.plotly_chart(fig_box, use_container_width=True)

with tab2:
    st.markdown("### 📈 Analyses des Variables Numériques")
    
    if len(col_types['numeric']) == 0:
        st.warning("⚠️ Aucune colonne numérique détectée dans les données")
    else:
        # Statistiques descriptives
        st.markdown("#### 📊 Statistiques Descriptives")
        stats_df = df_filtered[col_types['numeric']].describe().T
        stats_df = stats_df.round(2)
        st.dataframe(stats_df, use_container_width=True)
        
        # Graphiques de tendance
        if len(col_types['numeric']) >= 2:
            st.markdown("#### 📈 Comparaison de Variables")
            
            col_x, col_y = st.columns(2)
            with col_x:
                x_var = st.selectbox("Variable X", col_types['numeric'], key="x_var")
            with col_y:
                y_var = st.selectbox("Variable Y", col_types['numeric'], key="y_var", index=min(1, len(col_types['numeric'])-1))
            
            # Scatter plot
            color_by = None
            if len(col_types['text']) > 0:
                color_by = st.selectbox("Colorer par", [None] + col_types['text'])
            
            fig_scatter = px.scatter(
                df_filtered,
                x=x_var,
                y=y_var,
                color=color_by,
                title=f"{y_var} vs {x_var}"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Top/Bottom performers
        if len(col_types['numeric']) > 0:
            st.markdown("#### 🏆 Top Performers")
            
            metric_col = st.selectbox("Métrique à analyser", col_types['numeric'], key="top_metric")
            
            if len(col_types['text']) > 0:
                group_by = st.selectbox("Grouper par", col_types['text'], key="group_by")
                
                grouped = df_filtered.groupby(group_by)[metric_col].sum().sort_values(ascending=False)
                
                col_top, col_bottom = st.columns(2)
                
                with col_top:
                    st.markdown(f"**Top 10 - {group_by}**")
                    top_10 = grouped.head(10)
                    
                    # Créer un DataFrame pour Plotly
                    top_10_df = pd.DataFrame({
                        group_by: top_10.index,
                        metric_col: top_10.values
                    })
                    
                    fig_top = px.bar(
                        top_10_df,
                        x=metric_col,
                        y=group_by,
                        orientation='h',
                        title=f"Top 10 par {metric_col}"
                    )
                    st.plotly_chart(fig_top, use_container_width=True)
                
                with col_bottom:
                    st.markdown(f"**Bottom 10 - {group_by}**")
                    bottom_10 = grouped.tail(10)
                    
                    # Créer un DataFrame pour Plotly
                    bottom_10_df = pd.DataFrame({
                        group_by: bottom_10.index,
                        metric_col: bottom_10.values
                    })
                    
                    fig_bottom = px.bar(
                        bottom_10_df,
                        x=metric_col,
                        y=group_by,
                        orientation='h',
                        title=f"Bottom 10 par {metric_col}",
                        color_discrete_sequence=['salmon']
                    )
                    st.plotly_chart(fig_bottom, use_container_width=True)

with tab3:
    st.markdown("### 🔍 Analyses des Variables Catégorielles")
    
    if len(col_types['text']) == 0:
        st.warning("⚠️ Aucune colonne catégorielle détectée dans les données")
    else:
        # Distribution des catégories
        st.markdown("#### 📊 Distribution des Catégories")
        
        cat_col = st.selectbox("Sélectionner une catégorie", col_types['text'], key="cat_analysis")
        
        value_counts = df_filtered[cat_col].value_counts()
        
        col_pie, col_bar = st.columns(2)
        
        with col_pie:
            fig_pie = px.pie(
                values=value_counts.values,
                names=value_counts.index,
                title=f"Répartition - {cat_col}",
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_bar:
            # Créer un DataFrame pour le graphique
            bar_df = pd.DataFrame({
                cat_col: value_counts.index,
                'Nombre': value_counts.values
            })
            
            fig_bar = px.bar(
                bar_df,
                x=cat_col,
                y='Nombre',
                title=f"Distribution - {cat_col}"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Analyse croisée
        if len(col_types['text']) >= 2:
            st.markdown("#### 🔄 Analyse Croisée")
            
            col_cross1, col_cross2 = st.columns(2)
            with col_cross1:
                cat1 = st.selectbox("Première catégorie", col_types['text'], key="cat1")
            with col_cross2:
                cat2 = st.selectbox("Deuxième catégorie", [c for c in col_types['text'] if c != cat1], key="cat2")
            
            cross_tab = pd.crosstab(df_filtered[cat1], df_filtered[cat2])
            
            fig_heatmap = px.imshow(
                cross_tab,
                labels=dict(x=cat2, y=cat1, color="Nombre"),
                title=f"Tableau croisé: {cat1} vs {cat2}",
                aspect="auto",
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

with tab4:
    st.markdown("### 📉 Matrice de Corrélation")
    
    if len(col_types['numeric']) < 2:
        st.warning("⚠️ Besoin d'au moins 2 colonnes numériques pour analyser les corrélations")
    else:
        # Matrice de corrélation
        corr_matrix = df_filtered[col_types['numeric']].corr()
        
        fig_corr = px.imshow(
            corr_matrix,
            labels=dict(color="Corrélation"),
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            title="Matrice de Corrélation",
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1
        )
        
        fig_corr.update_layout(height=600)
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Top corrélations
        st.markdown("#### 🔝 Corrélations les Plus Fortes")
        
        # Extraire les corrélations (sans la diagonale)
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_pairs.append({
                    'Variable 1': corr_matrix.columns[i],
                    'Variable 2': corr_matrix.columns[j],
                    'Corrélation': corr_matrix.iloc[i, j]
                })
        
        corr_df = pd.DataFrame(corr_pairs).sort_values('Corrélation', key=abs, ascending=False)
        st.dataframe(corr_df.head(10), use_container_width=True)

with tab5:
    st.markdown("###  Données Brutes")
    
    # Options d'affichage
    col_opt1, col_opt2, col_opt3 = st.columns(3)
    
    with col_opt1:
        show_all = st.checkbox("Afficher toutes les colonnes", value=True)
    
    with col_opt2:
        rows_to_show = st.number_input(
            "Nombre de lignes à afficher",
            min_value=10,
            max_value=len(df_filtered),
            value=min(100, len(df_filtered)),
            step=10
        )
    
    with col_opt3:
        sort_by = st.selectbox("Trier par", [''] + df_filtered.columns.tolist())
    
    # Préparer le DataFrame d'affichage
    df_display = df_filtered.copy()
    
    if sort_by:
        df_display = df_display.sort_values(sort_by, ascending=False)
    
    if not show_all:
        important_cols = col_types['numeric'][:3] + col_types['text'][:2]
        df_display = df_display[important_cols]
    
    # Afficher le tableau
    st.dataframe(df_display.head(rows_to_show), use_container_width=True, height=400)
    
    # Téléchargements
    st.markdown("###  Télécharger les Données")
    
    col_dl1, col_dl2 = st.columns(2)
    
    with col_dl1:
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=" Télécharger en CSV",
            data=csv,
            file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col_dl2:
        excel_buffer = pd.ExcelWriter('temp.xlsx', engine='openpyxl')
        df_filtered.to_excel(excel_buffer, index=False)
        excel_buffer.close()
        
        with open('temp.xlsx', 'rb') as f:
            st.download_button(
                label=" Télécharger en Excel",
                data=f,
                file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        Dashboard Universel | {len(df_filtered)} lignes analysées | Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    """,
    unsafe_allow_html=True
)