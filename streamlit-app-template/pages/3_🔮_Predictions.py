import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
import joblib

# Ajout du chemin racine au path pour pouvoir importer utils et config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils import load_data, load_data3

# Configuration de la page
st.set_page_config(page_title="Prédictions", page_icon="🔮", layout="wide")

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
st.title("🔮 Prédictions & Estimations")
st.markdown("Projections basées sur les modèles de ML et de TS développés sur vos données historiques.")

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
    key="date_range_pred",
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
    key="c=saisons_pred",
)

# Application des filtres
filtered_df = df[
    (df["Date_admission"] >= start_datetime) 
    & (df["Date_admission"] <= end_datetime) 
    & (df["Saison"].isin(selected_saisons))
]


# --------- SECTION 1:  PREDICTIONS  ---------
st.header("📈 Projections des Admissions")

# Tri des données par date pour l'affichage correct
filtered_df = filtered_df.sort_values("Date_admission")

# Affichage des admissions journalières sans agrégation mensuelle
fig_admissions = px.line(
    filtered_df,
    x="Date_admission",
    y="Nombre_admissions",
    markers=True,
    title="Admissions Journalières Historiques",
    labels={"Nombre_admissions": "Nombre d'Admissions", "Date_admission": "Date"},
    template=config.PLOT_CONFIG["template"],
    color_discrete_sequence=[config.COLORS["primary"]],
)

# Mise en page du graphique
fig_admissions.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=50, b=30),
    xaxis_title="",
    yaxis_title="Admissions",
)

# Affichage du graphique dans Streamlit
st.plotly_chart(fig_admissions, use_container_width=True)

# --------- SECTION 2: PARAMÈTRES DE PROJECTION ---------
st.subheader("📊 Paramètres de Projection")

col1, col2 = st.columns(2)

with col1:
    num_days = st.slider(
        "Nombre de jours à projeter",
        min_value=1,
        max_value=90,
        value=30,
        step=1,
        key="num_days",
    )

with col2:
    temperature_projection = st.number_input(
        "Température moyenne prévue (°C)",
        min_value=-10.0,
        max_value=40.0,
        value=15.0,
        step=0.5,
        key="temperature_projection",
    )

# Autres paramètres (Vacances scolaires et Événement Spécial)
col3, col4 = st.columns(2)

with col3:
    vacances_projection = st.selectbox(
        "Vacances scolaires",
        options=["Oui", "Non"],
        index=1,
        key="vacances_projection",
    )

    evenement_projection = st.selectbox(
        "Événement Spécial",
        options=["Aucun", "Pollens allergènes", "Épidémie de grippe", "Canicule", "Épidémie de gastro"],
        index=0,
        key="evenement_projection",
    )

# --------- CHARGEMENT DES TRANSFORMATEURS ---------
@st.cache_resource
def load_transformers():
    ordinal_encoder = joblib.load("models/ordinal_encoder.pkl")
    onehot_encoder = joblib.load("models/onehot_encoder.pkl")
    scaler = joblib.load("models/scaler.pkl")
    return ordinal_encoder, onehot_encoder, scaler

ordinal_encoder, onehot_encoder, scaler = load_transformers()

# --------- CHARGEMENT DU MODÈLE PROPHET ---------
@st.cache_resource
def load_prophet_model():
    return joblib.load("models/prophet_model.pkl")

prophet_model = load_prophet_model()

# --------- APPLICATION DU PRÉPROCESSING ---------
# Création du DataFrame des jours à projeter
future_dates = pd.date_range(start=df["Date_admission"].max(), periods=num_days + 1, freq="D")[1:]
future_df = pd.DataFrame({"ds": future_dates})

# Transformation des variables catégoriques
future_df["Jour_semaine"] = future_df["ds"].dt.day_name()
future_df["Mois"] = future_df["ds"].dt.month_name()
future_df["Saison"] = future_df["ds"].dt.month.map({12: "Hiver", 1: "Hiver", 2: "Hiver",
                                                    3: "Printemps", 4: "Printemps", 5: "Printemps",
                                                    6: "Été", 7: "Été", 8: "Été",
                                                    9: "Automne", 10: "Automne", 11: "Automne"})

# Encodage ordinal
future_df[["Jour_semaine", "Mois", "Saison"]] = ordinal_encoder.transform(future_df[["Jour_semaine", "Mois", "Saison"]])

# Encodage OneHot pour l'Événement Spécial uniquement (sans météo)
nb_rows = len(future_df)
encoded_array = onehot_encoder.transform(pd.DataFrame({
    "Evenement_Special": [evenement_projection for _ in range(nb_rows)]  # Répéter l'événement spécial pour chaque ligne
}))
encoded_features = pd.DataFrame(encoded_array, columns=onehot_encoder.get_feature_names_out(["Evenement_Special"]))

# Ajout des variables projetées
future_df["Vacances_scolaires"] = 1 if vacances_projection == "Oui" else 0
# Transformer la température en un DataFrame pour correspondre au nombre de lignes de `future_df`
temp_scaled = scaler.transform(pd.DataFrame({"Température": [temperature_projection] * len(future_df)}))

# Appliquer la transformation correctement
future_df["Température"] = temp_scaled.flatten()


# Fusion des données encodées
future_df = pd.concat([future_df, encoded_features], axis=1)

# --------- PRÉDICTION AVEC PROPHET ---------
forecast = prophet_model.predict(future_df)

# --------- COMBINAISON AVEC DONNÉES HISTORIQUES ---------
historical_df = df[["Date_admission", "Nombre_admissions"]].rename(columns={"Date_admission": "ds", "Nombre_admissions": "y"})
historical_df["type"] = "Historique"

projection_df = forecast[["ds", "yhat"]].rename(columns={"yhat": "y"})
projection_df["type"] = "Projection"

# Convertir les prédictions en entiers
projection_df["y"] = projection_df["y"].round().astype(int)

combined_df = pd.concat([historical_df, projection_df])

# --------- AFFICHAGE DES PROJECTIONS ---------
fig_forecast = px.line(
    combined_df,
    x="ds",
    y="y",
    color="type",
    markers=True,
    title="📈 Prédiction des Admissions Hospitalières",
    labels={"y": "Nombre d'Admissions", "ds": "Date", "type": "Données"},
    template="plotly_white",
    color_discrete_map={"Historique": "blue", "Projection": "red"},
)

fig_forecast.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=50, b=30),
    xaxis_title="",
    yaxis_title="Admissions",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

st.plotly_chart(fig_forecast, use_container_width=True)

# --------- OPTION DE TÉLÉCHARGEMENT DES PROJECTIONS ---------
csv_buffer = projection_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Télécharger les prédictions (CSV)",
    data=csv_buffer,
    file_name="predictions_admissions.csv",
    mime="text/csv",
)


# --------- SECTION 3: PRÉDICTION DES EFFECTIFS MÉDICAUX ---------
st.subheader("📊 Prédiction des Effectifs Médicaux")

# --------- CHARGEMENT DES MODÈLES ---------
@st.cache_resource
def load_personnel_models():
    model_medecins = joblib.load("models/model_nb_medecins.pkl")
    model_infirmiers = joblib.load("models/model_nb_infirmiers.pkl")
    model_aides_soignants = joblib.load("models/model_nb_aides_soignants.pkl")
    return model_medecins, model_infirmiers, model_aides_soignants

model_medecins, model_infirmiers, model_aides_soignants = load_personnel_models()

# --------- PRÉPARATION DES DONNÉES POUR LA PRÉDICTION ---------
# On ajoute le nombre d'admissions prédites dans `future_df`
future_df["Nombre_admissions"] = projection_df["y"]

# Retirer la colonne "ds" avant la prédiction (XGBoost ne supporte pas les dates)
future_df_xgb = future_df.drop(columns=["ds"], errors="ignore")

# Récupération des features utilisées lors de l'entraînement
expected_features = model_medecins.feature_names_in_

# Réordonner les colonnes et supprimer celles qui ne sont pas nécessaires
future_df_xgb = future_df_xgb[expected_features]

# Prédiction des effectifs
nb_medecins_pred = model_medecins.predict(future_df_xgb).round().astype(int)
nb_infirmiers_pred = model_infirmiers.predict(future_df_xgb).round().astype(int)
nb_aides_soignants_pred = model_aides_soignants.predict(future_df_xgb).round().astype(int)

# Création du DataFrame des prédictions
projection_personnel_df = projection_df.copy()
projection_personnel_df["Nb_medecins"] = nb_medecins_pred
projection_personnel_df["Nb_infirmiers"] = nb_infirmiers_pred
projection_personnel_df["Nb_aides_soignants"] = nb_aides_soignants_pred

# --------- COMBINAISON AVEC DONNÉES HISTORIQUES ---------
historical_personnel_df = df[["Date_admission", "Nombre_admissions", "Nb medecin", "Nb infirmier", "Nb aide soignant"]].rename(
    columns={"Date_admission": "ds", "Nb medecin": "Nb_medecins", "Nb infirmier": "Nb_infirmiers", "Nb aide soignant": "Nb_aides_soignants"}
)
historical_personnel_df["type"] = "Historique"
projection_personnel_df["type"] = "Projection"

combined_personnel_df = pd.concat([historical_personnel_df, projection_personnel_df])

# --------- AFFICHAGE DES PRÉDICTIONS ---------
# Création des trois graphiques séparés

fig_medecins = px.line(
    combined_personnel_df,
    x="ds",
    y="Nb_medecins",
    color="type",
    markers=True,
    title="📈 Prédiction du Nombre de Médecins",
    labels={"ds": "Date", "Nb_medecins": "Nombre de Médecins"},
    template="plotly_white",
    color_discrete_map={"Historique": "blue", "Projection": "red"},
)

fig_infirmiers = px.line(
    combined_personnel_df,
    x="ds",
    y="Nb_infirmiers",
    color="type",
    markers=True,
    title="📈 Prédiction du Nombre d'Infirmiers",
    labels={"ds": "Date", "Nb_infirmiers": "Nombre d'Infirmiers"},
    template="plotly_white",
    color_discrete_map={"Historique": "blue", "Projection": "red"},
)

fig_aides_soignants = px.line(
    combined_personnel_df,
    x="ds",
    y="Nb_aides_soignants",
    color="type",
    markers=True,
    title="📈 Prédiction du Nombre d'Aides-Soignants",
    labels={"ds": "Date", "Nb_aides_soignants": "Nombre d'Aides-Soignants"},
    template="plotly_white",
    color_discrete_map={"Historique": "blue", "Projection": "red"},
)

# Affichage des graphiques dans trois colonnes

st.plotly_chart(fig_medecins, use_container_width=True)
st.plotly_chart(fig_infirmiers, use_container_width=True)
st.plotly_chart(fig_aides_soignants, use_container_width=True)

# --------- AFFICHAGE DU TABLEAU DES PRÉDICTIONS ---------
st.subheader("📋 Résumé des Prédictions")
st.dataframe(projection_personnel_df, use_container_width=True)

# --------- OPTION DE TÉLÉCHARGEMENT DES PRÉDICTIONS ---------
csv_buffer = projection_personnel_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Télécharger les prédictions (CSV)",
    data=csv_buffer,
    file_name="predictions_personnel.csv",
    mime="text/csv",
)



# --- FOOTER ---
st.markdown("<div class='footer'>© 2024 - Hôpitaux Universitaires | Tous droits réservés</div>", unsafe_allow_html=True)