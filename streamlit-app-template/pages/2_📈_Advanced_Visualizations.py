import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# Ajout du chemin racine au path pour pouvoir importer utils et config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils import load_data,load_data3

# Configuration de la page
st.set_page_config(page_title="Visualisations Avancées", page_icon="📈", layout="wide")


# Chargement du logo
# logo_path = "assets/images/logo.png"  # Vérifie bien le chemin

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
# col1, col2 = st.columns([1, 3])
# with col1:
#     st.image(logo_path, width=400)
# with col2:
st.markdown("<div class='header'>Hôpitaux Universitaires - Pitié Salpêtrière</div>", unsafe_allow_html=True)



# Chargement des styles CSS personnalisés
with open("assets/css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Titre de la page
st.title("📈 Visualisations Avancées")
st.markdown(
    "Découvrez d'autres types de visualisations pour analyser vos données d'admission."
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

# --------- SECTION 1: CARTE DE CHALEUR DES ADMISSIONS ---------
st.header("📊 Carte de Chaleur des Admissions")

# Options pour la carte de chaleur
heatmap_options = ["Jour de la semaine vs Météo", "Mois vs Météo"]
selected_heatmap = st.radio(
    "Choisir un type de carte de chaleur :", heatmap_options, horizontal=True
)

if selected_heatmap == "Jour de la semaine vs Météo":
    # Agrégation par jour de semaine et météo
    heatmap_data = (
        filtered_df.groupby(["Jour_semaine", "Météo"], observed=True)["Nombre_admissions"].sum().reset_index()
    )

    # Création du pivot pour la heatmap
    heatmap_pivot = heatmap_data.pivot(
        index="Jour_semaine", columns="Météo", values="Nombre_admissions"
    )

    # Ordre des jours de la semaine
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_pivot = heatmap_pivot.reindex(days_order)

    # Création de la heatmap avec Plotly
    fig_heatmap = px.imshow(
        heatmap_pivot.values,
        labels=dict(x="Météo", y="Jour de la semaine", color="Nombre d'Admissions"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale="Blues",
        aspect="auto",
    )

    fig_heatmap.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=30))

    st.plotly_chart(fig_heatmap, use_container_width=True)

else:  # Mois vs Météo
    # Agrégation par mois et météo
    heatmap_data = (
        filtered_df.groupby(["Mois", "Météo"])["Nombre_admissions"].sum().reset_index()
    )

    # Création du pivot pour la heatmap
    heatmap_pivot = heatmap_data.pivot(
        index="Mois", columns="Météo", values="Nombre_admissions"
    )

    # Ordre des mois
    months_order = [
        "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"
    ]
    heatmap_pivot = heatmap_pivot.reindex(months_order)

    # Création de la heatmap avec Plotly
    fig_heatmap = px.imshow(
        heatmap_pivot.values,
        labels=dict(x="Météo", y="Mois", color="Nombre d'Admissions"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale="Blues",
        aspect="auto",
    )

    fig_heatmap.update_layout(height=450, margin=dict(l=20, r=20, t=20, b=30))

    st.plotly_chart(fig_heatmap, use_container_width=True)


# --------- SECTION 2: VISUALISATION HIÉRARCHIQUE DES ADMISSIONS ---------
st.header("📊 Visualisation hiérachique des admissions")

# Options pour la visualisation hiérarchique
hierarchy_options = ["Treemap", "Sunburst"]
selected_hierarchy = st.radio(
    "Choisir un type de visualisation :", hierarchy_options, horizontal=True
)

# Ajout d'une colonne "Année-Mois" pour structurer la hiérarchie temporelle
filtered_df["year_month"] = filtered_df["Date_admission"].dt.strftime("%Y-%m")

# Agrégation des admissions par saison et période (année-mois)
hierarchy_data = (
    filtered_df.groupby(["Saison", "year_month"], observed=True)["Nombre_admissions"].sum().reset_index()
)

if selected_hierarchy == "Treemap":
    # Création du treemap
    fig_hierarchy = px.treemap(
        hierarchy_data,
        path=["Saison", "year_month"],
        values="Nombre_admissions",
        color="Nombre_admissions",
        color_continuous_scale="Blues",
        title="🌍 Répartition des Admissions par Saison et Période",
    )

else:  # Sunburst
    # Création du sunburst
    fig_hierarchy = px.sunburst(
        hierarchy_data,
        path=["Saison", "year_month"],
        values="Nombre_admissions",
        color="Nombre_admissions",
        color_continuous_scale="Blues",
        title="☀️ Répartition des Admissions par Saison et Période",
    )

# Mise en page du graphique
fig_hierarchy.update_layout(height=500, margin=dict(l=20, r=20, t=30, b=30))

# Affichage du graphique
st.plotly_chart(fig_hierarchy, use_container_width=True)


# --------- SECTION 3: ANALYSE COMPARATIVE ---------
st.header("📊 Analyse Comparative des Admissions par Événement Spécial")

# Sélection de deux périodes à comparer
st.markdown("### Comparaison de deux périodes")

col1, col2 = st.columns(2)

with col1:
    period1_start = st.date_input(
        "Période 1 - Début", value=filtered_df["Date_admission"].min().date(), key="period1_start"
    )
    period1_end = st.date_input(
        "Période 1 - Fin",
        value=(filtered_df["Date_admission"].min() + pd.Timedelta(days=90)).date(),
        key="period1_end",
    )

with col2:
    period2_start = st.date_input(
        "Période 2 - Début",
        value=(filtered_df["Date_admission"].max() - pd.Timedelta(days=90)).date(),
        key="period2_start",
    )
    period2_end = st.date_input(
        "Période 2 - Fin", value=filtered_df["Date_admission"].max().date(), key="period2_end"
    )

# Conversion en datetime
period1_start_dt = pd.to_datetime(period1_start)
period1_end_dt = pd.to_datetime(period1_end)
period2_start_dt = pd.to_datetime(period2_start)
period2_end_dt = pd.to_datetime(period2_end)

# Filtrer les données pour chaque période
period1_df = filtered_df[
    (filtered_df["Date_admission"] >= period1_start_dt)
    & (filtered_df["Date_admission"] <= period1_end_dt)
]

period2_df = filtered_df[
    (filtered_df["Date_admission"] >= period2_start_dt)
    & (filtered_df["Date_admission"] <= period2_end_dt)
]

# Agrégation des admissions par événement spécial pour chaque période
period1_events = period1_df.groupby("Evenement_Special")["Nombre_admissions"].sum().reset_index()
period1_events["Période"] = (
    f"Période 1 ({period1_start.strftime('%d/%m/%Y')} - {period1_end.strftime('%d/%m/%Y')})"
)

period2_events = period2_df.groupby("Evenement_Special")["Nombre_admissions"].sum().reset_index()
period2_events["Période"] = (
    f"Période 2 ({period2_start.strftime('%d/%m/%Y')} - {period2_end.strftime('%d/%m/%Y')})"
)

# Combinaison des données des deux périodes
combined_events = pd.concat([period1_events, period2_events])

# Création du graphique comparatif
fig_compare = px.bar(
    combined_events,
    x="Evenement_Special",
    y="Nombre_admissions",
    color="Période",
    barmode="group",
    labels={"Nombre_admissions": "Nombre d'Admissions", "Evenement_Special": "Événement Spécial", "Période": "Période"},
    template="plotly_white",
)

fig_compare.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=20, b=30),
    xaxis_title="",
    yaxis_title="Nombre d'Admissions",
)

st.plotly_chart(fig_compare, use_container_width=True)

# Affichage du pourcentage de variation
if st.checkbox("Afficher le pourcentage de variation"):
    # Calcul des variations
    variation_df = pd.merge(
        period1_events[["Evenement_Special", "Nombre_admissions"]],
        period2_events[["Evenement_Special", "Nombre_admissions"]],
        on="Evenement_Special",
        suffixes=("_période1", "_période2"),
    )

    variation_df["Variation Absolue"] = (
        variation_df["Nombre_admissions_période2"] - variation_df["Nombre_admissions_période1"]
    )
    variation_df["Variation (%)"] = (
        variation_df["Variation Absolue"] / variation_df["Nombre_admissions_période1"] * 100
    ).round(2)

    # Mise en forme pour l'affichage
    variation_display = variation_df[
        [
            "Evenement_Special",
            "Nombre_admissions_période1",
            "Nombre_admissions_période2",
            "Variation Absolue",
            "Variation (%)",
        ]
    ]

    st.dataframe(
        variation_display,
        column_config={
            "Evenement_Special": st.column_config.TextColumn("Événement Spécial"),
            "Nombre_admissions_période1": st.column_config.NumberColumn(
                "Admissions Période 1", format="%d"
            ),
            "Nombre_admissions_période2": st.column_config.NumberColumn(
                "Admissions Période 2", format="%d"
            ),
            "Variation Absolue": st.column_config.NumberColumn(
                "Variation Absolue", format="%d"
            ),
            "Variation (%)": st.column_config.NumberColumn(
                "Variation (%)", format="%.2f%%"
            ),
        },
        hide_index=True,
        use_container_width=True,
    )



# --- FOOTER ---
st.markdown("<div class='footer'>© 2024 - Hôpitaux Universitaires | Tous droits réservés</div>", unsafe_allow_html=True)