import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
from statsmodels.tsa.seasonal import seasonal_decompose

# Ajout du chemin racine au path pour pouvoir importer utils et config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils import load_data, load_data3

# Configuration de la page
st.set_page_config(page_title="Analyse Exploratoire", page_icon="📊", layout="wide")

# Chargement du logo
logo_path = "assets/images/logo.png"  # Vérifie bien le chemin

# --- HEADER ---
st.markdown(
    """
    <style>
        .header {
            background-color: #003366;
            padding: 30px;
            text-align: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
            border-radius: 10px;
        }
        .footer {
            position: bottom;
            bottom: 0;
            width: 100%;
            background-color: #003366;
            color: white;
            text-align: center;
            padding: 10px;
            font-size: 14px;
            border-radius: 10px;
        }
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Affichage du logo et du titre
col1, col2 = st.columns([1, 3])
with col1:
    st.image(logo_path, width=400)
with col2:
    st.markdown("<div class='header'>Hôpitaux Universitaires - Pitié Salpêtrière</div>", unsafe_allow_html=True)



# Chargement des styles CSS personnalisés
with open("assets/css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Titre de la page
st.title("📊 Analyse Exploratoire des Données")
st.markdown(
    "Explorez vos données d'admissions pour découvrir des tendances et des insights. Ces données sont regroupés par jour."
)


# Chargement et mise en cache des données
@st.cache_data
def get_data():
    return load_data3("data/dataset_admission.csv")


df = get_data()

# Sidebar pour les filtres
st.sidebar.header("Filtres d'Analyse")

# Filtres pour la période
start_date, end_date = st.sidebar.date_input(
    "Période d'admission",
    value=(df["Date_admission"].min().date(), df["Date_admission"].max().date()),
    key="date_range_explore",
)

# Conversion des dates en datetime pour la compatibilité
start_datetime = pd.to_datetime(start_date)
end_datetime = pd.to_datetime(end_date)

# Filtre pour les saisons
all_saisons = df["Saison"].unique().tolist()
selected_saisons = st.sidebar.multiselect(
    "Sélectionner des saisons",
    options=all_saisons,
    default=all_saisons,
    key="c=saisons_explore",
)

# Application des filtres
filtered_df = df[
    (df["Date_admission"] >= start_datetime) 
    & (df["Date_admission"] <= end_datetime) 
    & (df["Saison"].isin(selected_saisons))
]

# --------- SECTION 1: VUE D'ENSEMBLE DES DONNÉES ---------
st.header("Vue d'ensemble des données")

# Affichage des métriques clés dans des colonnes
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Nombre Total d'Admissions", filtered_df["Nombre_admissions"].sum())

with col2:
    temperature_moyenne = round(filtered_df["Température"].mean()) if not filtered_df["Température"].isna().all() else 0
    st.metric("Température Moyenne", f"{temperature_moyenne}°C")

with col3:
    st.metric("Nombre Total de Lits Occupés", filtered_df["Lits occupes"].sum())

with col4:
    medecins_moyen = round(filtered_df["Nb medecin"].mean()) if not filtered_df["Nb medecin"].isna().all() else 0
    st.metric("Moyenne Médecins Mobilisés", medecins_moyen)

# Aperçu des données filtrées
with st.expander("Aperçu des données"):
    st.dataframe(filtered_df.head(10), use_container_width=True)


# --------- SECTION 2: RÉPARTITION DES ADMISSIONS PAR ÉVÉNEMENT SPÉCIAL ---------
st.header("Répartition des Admissions par Événement Spécial")

# Calcul des admissions par événement spécial
admissions_by_event = filtered_df.groupby("Evenement_Special", observed=True)["Nombre_admissions"].sum().reset_index()
admissions_by_event = admissions_by_event.sort_values("Nombre_admissions", ascending=False)

# Visualisation des admissions par événement spécial avec un graphique en barres
fig_event = px.bar(
    admissions_by_event,
    x="Evenement_Special",
    y="Nombre_admissions",
    color="Evenement_Special",
    labels={"Nombre_admissions": "Nombre d'Admissions", "Evenement_Special": "Événement Spécial"},
    template=config.PLOT_CONFIG["template"],
    color_discrete_sequence=config.PLOT_CONFIG["color_discrete_sequence"],
)

fig_event.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=20, b=30),
    showlegend=False,
    xaxis_title="",
    yaxis_title="Nombre d'Admissions",
)

st.plotly_chart(fig_event, use_container_width=True)


# --------- SECTION 3: ANALYSE TEMPORELLE ---------
st.header("Analyse Temporelle des Admissions")

# Options d'analyse temporelle
time_options = ["Jour de la semaine", "Mois", "Année", "Saison"]
selected_time_analysis = st.radio(
    "Choisir une analyse temporelle :", time_options, horizontal=True
)

if selected_time_analysis == "Jour de la semaine":
    # Ordre des jours de la semaine
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Agrégation des admissions par jour de la semaine
    admissions_by_day = filtered_df.groupby("Jour_semaine", observed=True)["Nombre_admissions"].sum().reset_index()
    admissions_by_day["Jour_semaine"] = pd.Categorical(admissions_by_day["Jour_semaine"], categories=days_order, ordered=True)
    admissions_by_day = admissions_by_day.sort_values("Jour_semaine")

    # Visualisation des admissions par jour de la semaine
    fig_time = px.line(
        admissions_by_day,
        x="Jour_semaine",
        y="Nombre_admissions",
        markers=True,
        labels={"Nombre_admissions": "Nombre d'Admissions", "Jour_semaine": "Jour de la semaine"},
        template=config.PLOT_CONFIG["template"],
        color_discrete_sequence=[config.COLORS["primary"]],
    )

elif selected_time_analysis == "Mois":
    # Agrégation des admissions par mois
    admissions_by_month = filtered_df.groupby("Mois", observed=True)["Nombre_admissions"].sum().reset_index()

    # Visualisation des admissions par mois
    fig_time = px.line(
        admissions_by_month,
        x="Mois",
        y="Nombre_admissions",
        markers=True,
        labels={"Nombre_admissions": "Nombre d'Admissions", "Mois": "Mois"},
        template=config.PLOT_CONFIG["template"],
        color_discrete_sequence=[config.COLORS["primary"]],
    )

elif selected_time_analysis == "Année":
    # Agrégation des admissions par année
    admissions_by_year = filtered_df.groupby("Annee", observed=True)["Nombre_admissions"].sum().reset_index()

    # Visualisation des admissions par année
    fig_time = px.bar(
        admissions_by_year,
        x="Annee",
        y="Nombre_admissions",
        labels={"Nombre_admissions": "Nombre d'Admissions", "Annee": "Année"},
        template=config.PLOT_CONFIG["template"],
        color_discrete_sequence=[config.COLORS["primary"]],
    )

else:  # Saison
    # Agrégation des admissions par saison
    admissions_by_season = filtered_df.groupby("Saison", observed=True)["Nombre_admissions"].sum().reset_index()

    # Visualisation des admissions par saison
    fig_time = px.bar(
        admissions_by_season,
        x="Saison",
        y="Nombre_admissions",
        labels={"Nombre_admissions": "Nombre d'Admissions", "Saison": "Saison"},
        template=config.PLOT_CONFIG["template"],
        color_discrete_sequence=[config.COLORS["primary"]],
    )

# Ajustements du graphique
fig_time.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=20, b=30),
    xaxis_title="",
    yaxis_title="Nombre d'Admissions",
)

st.plotly_chart(fig_time, use_container_width=True)



# --------- SECTION 4: ANALYSE DES ADMISSIONS PAR MÉTÉO ---------
st.header("Analyse des Admissions par Météo")

# Agrégation des admissions par météo
admissions_by_weather = filtered_df.groupby("Météo", observed=True)["Nombre_admissions"].sum().reset_index()
admissions_by_weather = admissions_by_weather.sort_values("Nombre_admissions", ascending=False)

# Visualisation des admissions par condition météorologique
fig_weather = px.bar(
    admissions_by_weather,
    x="Météo",
    y="Nombre_admissions",
    color="Météo",
    labels={"Nombre_admissions": "Nombre d'Admissions", "Météo": "Conditions Météorologiques"},
    template=config.PLOT_CONFIG["template"],
    color_discrete_sequence=config.PLOT_CONFIG["color_discrete_sequence"],
)

# Ajustement du layout
fig_weather.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=20, b=30),
    xaxis_title="",
    yaxis_title="Nombre d'Admissions",
    showlegend=False,
)

# Affichage du graphique
st.plotly_chart(fig_weather, use_container_width=True)


# --------- SECTION 5: ÉVOLUTION DU PERSONNEL HOSPITALIER ---------
st.header("Évolution du Personnel Hospitalier")

# Agrégation des admissions et personnel hospitalier par mois
admissions_personnel_mensuelles = filtered_df.groupby(filtered_df["Date_admission"].dt.to_period('M')).agg({
    "Nb medecin": "sum",
    "Nb infirmier": "sum",
    "Nb aide soignant": "sum"
}).reset_index()

# Conversion des périodes en datetime pour Plotly
admissions_personnel_mensuelles["Date_admission"] = admissions_personnel_mensuelles["Date_admission"].astype(str)

# Création du graphique interactif avec Plotly
fig_personnel = px.line(
    admissions_personnel_mensuelles,
    x="Date_admission",
    y=["Nb medecin", "Nb infirmier", "Nb aide soignant"],
    markers=True,
    labels={"Date_admission": "Mois", "value": "Nombre de Personnel"},
    title="",
    template=config.PLOT_CONFIG["template"],
    color_discrete_sequence=config.PLOT_CONFIG["color_discrete_sequence"],
)

# Personnalisation des couleurs et de la légende
fig_personnel.update_traces(mode='lines+markers')
fig_personnel.update_layout(
    height=450,
    margin=dict(l=20, r=20, t=40, b=30),
    xaxis_title="Date (Année-Mois)",
    yaxis_title="Effectif Total",
    legend_title="Catégorie de Personnel",
)

# Affichage du graphique
st.plotly_chart(fig_personnel, use_container_width=True)


# --------- SECTION 6: ANALYSE DE LA SAISONNALITÉ ---------
st.header("Analyse de la Saisonnalité des Admissions")

# Préparation des données pour l'analyse
filtered_df["Date_admission"] = pd.to_datetime(filtered_df["Date_admission"])  # Assurer que c'est bien une date
admissions_series = filtered_df.set_index("Date_admission")["Nombre_admissions"]

# Vérifier si la série a suffisamment de points pour la décomposition
if len(admissions_series) > 365:  # Vérification pour éviter les erreurs sur séries courtes
    decomposition = seasonal_decompose(admissions_series, model="additive", period=365)  # Utilisation d'une période mensuelle pour détecter la saisonnalité

    # Graphique de la série originale
    fig_original = px.line(
        x=admissions_series.index, 
        y=admissions_series.values, 
        labels={"x": "Date", "y": "Nombre d'Admissions"},
        title="📈 Série Temporelle des Admissions (Originale)",
    )

    # Graphique de la tendance
    fig_trend = px.line(
        x=admissions_series.index, 
        y=decomposition.trend, 
        labels={"x": "Date", "y": "Tendance"},
        title="📉 Tendance des Admissions"
    )

    # Graphique de la saisonnalité
    fig_seasonal = px.line(
        x=admissions_series.index, 
        y=decomposition.seasonal, 
        labels={"x": "Date", "y": "Saisonnalité"},
        title="🌍 Saisonnalité des Admissions"
    )

    # Graphique du résidu (bruit)
    fig_residual = px.line(
        x=admissions_series.index, 
        y=decomposition.resid, 
        labels={"x": "Date", "y": "Résidu (Bruit)"},
        title="🎭 Résidu (Bruit Aléatoire)"
    )

    # Affichage des graphiques dans Streamlit
    st.plotly_chart(fig_original, use_container_width=True)
    st.plotly_chart(fig_trend, use_container_width=True)
    st.plotly_chart(fig_seasonal, use_container_width=True)
    st.plotly_chart(fig_residual, use_container_width=True)

else:
    st.warning("⚠️ Pas assez de données filtrées pour effectuer une décomposition saisonnière (minimum 1 an de données requis).")



# --- FOOTER ---
st.markdown("<div class='footer'>© 2024 - Hôpitaux Universitaires | Tous droits réservés</div>", unsafe_allow_html=True)