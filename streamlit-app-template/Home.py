import pandas as pd
import plotly.express as px
import streamlit as st
import io
from pathlib import Path

from utils import load_data, load_data2

# Configuration de la page
st.set_page_config(
    page_title="Data Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Définir le chemin absolu du logo
logo_path = Path(__file__).parent / "assets" / "images" / "logo.png"
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



css_file = Path(__file__).parent / "assets" / "css" / "style.css"
# Chargement des styles CSS personnalisés
with open(css_file, "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Titre principal
st.title("🚀 Data Analytics Dashboard")
st.markdown("### Bienvenue dans votre tableau de bord d'analyse de données")

# Sidebar pour les filtres généraux
st.sidebar.header("Filtres Globaux")
st.sidebar.info("Ces filtres s'appliquent à toutes les pages de l'application.")




# Chargement et mise en cache des données
@st.cache_data
def get_data():
    return load_data2("data/dataset_admission.csv")


df = get_data()

# Filtres pour la période
start_date, end_date = st.sidebar.date_input(
    "Période d'admission",
    value=(df["Date_admission"].min().date(), df["Date_admission"].max().date()),
    key="date_range_home",
)

# Conversion des dates en datetime pour la compatibilité
start_datetime = pd.to_datetime(start_date)
end_datetime = pd.to_datetime(end_date)

# Filtre pour le sexe
all_sexes = df["Sexe"].unique().tolist()
selected_sexes = st.sidebar.multiselect(
    "Sélectionner le sexe",
    options=all_sexes,
    default=all_sexes,
    key="sexes_home",
)

# Filtre pour la gravité
all_gravites = df["Gravité"].unique().tolist()
selected_gravites = st.sidebar.multiselect(
    "Sélectionner la gravité",
    options=all_gravites,
    default=all_gravites,
    key="gravites_home",
)

# Filtre pour le mode d'arrivée
all_modes_arrivee = df["Mode d'arrivée"].unique().tolist()
selected_modes_arrivee = st.sidebar.multiselect(
    "Sélectionner le mode d'arrivée",
    options=all_modes_arrivee,
    default=all_modes_arrivee,
    key="modes_arrivee_home",
)

# Filtre pour le type d'hospitalisation
all_types_hosp = df["Type d'hospitalisation"].unique().tolist()
selected_types_hosp = st.sidebar.multiselect(
    "Sélectionner le type d'hospitalisation",
    options=all_types_hosp,
    default=all_types_hosp,
    key="types_hosp_home",
)

# Filtre pour les services
all_services = df["Service d'admission"].unique().tolist()
selected_services = st.sidebar.multiselect(
    "Sélectionner des services",
    options=all_services,
    default=all_services,
    key="services_home",
)

# Filtre pour les saisons
all_saisons = df["Saison"].unique().tolist()
selected_saisons = st.sidebar.multiselect(
    "Sélectionner des saisons",
    options=all_saisons,
    default=all_saisons,
    key="c=saisons_home",
)

# Application des filtres
filtered_df = df[
    (df["Date_admission"] >= start_datetime) 
    & (df["Date_admission"] <= end_datetime) 
    & (df["Service d'admission"].isin(selected_services)) 
    & (df["Saison"].isin(selected_saisons))
    & (df["Sexe"].isin(selected_sexes)) 
    & (df["Gravité"].isin(selected_gravites)) 
    & (df["Mode d'arrivée"].isin(selected_modes_arrivee)) 
    & (df["Type d'hospitalisation"].isin(selected_types_hosp))
]

# Affichage des indicateurs principaux
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Admissions", len(filtered_df))

with col2:
    st.metric("Durée Moyenne du Séjour", round(filtered_df["Durée du séjour estimé"].mean(), 1)) # type: ignore

with col3:
    lits_occupes_total = filtered_df["Lits occupes"].fillna(0).sum()

    if len(filtered_df) > 0:
        taux_occupation = (lits_occupes_total / len(filtered_df)) * 100
        st.metric("Taux d'Occupation des Lits", f"{int(round(taux_occupation, 1))}%")
    else:
        st.metric("Taux d'Occupation des Lits", "nan")
with col4:
    temperature_moyenne = round(filtered_df["Température"].mean()) if not filtered_df["Température"].isna().all() else 0
    st.metric("Température Moyenne", f"{temperature_moyenne}°C")
# Ajout de nouveaux KPI
col5, col6, col7, col8 = st.columns(4)

with col5:
    materiel_utilise = filtered_df["Materiel utilise"].sum()
    st.metric("Total Matériel Consommé", int(materiel_utilise))
with col6:
    total_medecins = (filtered_df["Nb medecin"].sum() / 4).round().astype(int)
    st.metric("Nombre de Médecins Mobilisés", int(total_medecins))
with col7:
    total_infirmiers = (filtered_df["Nb infirmier"].sum() / 4).round().astype(int)
    st.metric("Nombre d'Infirmiers Mobilisés", int(total_infirmiers))
with col8:
    total_aide_soignants = (filtered_df["Nb aide soignant"].sum() / 4).round().astype(int)
    st.metric("Nombre AS Mobilisés", int(total_aide_soignants))


# Évolution des admissions
st.subheader("📈 Évolution des Admissions")
admissions_over_time = (
    filtered_df.groupby(pd.to_datetime(filtered_df["Date_admission"]).dt.to_period("M"))
    .agg({"ID_patient": "count"})
    .reset_index()
)
admissions_over_time["Date_admission"] = admissions_over_time["Date_admission"].dt.to_timestamp()

fig = px.line(
    admissions_over_time,
    x="Date_admission",
    y="ID_patient",
    title="Admissions Mensuelles",
    labels={"ID_patient": "Nombre d'Admissions", "Date_admission": "Mois"},
    template="plotly_white",
)
fig.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

# Aperçu des données
with st.expander("Aperçu des données"):
    st.dataframe(filtered_df.head(50), use_container_width=True)
    
    # Option pour télécharger les données filtrées en CSV
    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="Télécharger les données filtrées (CSV)",
        data=csv_buffer.getvalue(),
        file_name="donnees_filtrees.csv",
        mime="text/csv",
    )

st.markdown("\n") 

# Affichage des camemberts
st.subheader("📊 Profil des Patients")
col_pie1, col_pie2 = st.columns(2)

with col_pie1:
    fig_age = px.pie(filtered_df, names="Tranche_age", title="Répartition par Tranche d'Âge")
    fig_age.update_layout(legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1))
    st.plotly_chart(fig_age, use_container_width=True)

with col_pie2:
    fig_sexe = px.pie(filtered_df, names="Sexe", title="Répartition par Sexe", hole=0.4)
    fig_sexe.update_layout(legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1))
    st.plotly_chart(fig_sexe, use_container_width=True)


# Répartition des admissions par vacances scolaires et événements spéciaux
st.subheader("🏥 Répartition des Admissions par Facteurs Spéciaux")
col_pie3, col_pie4 = st.columns(2)

with col_pie3:
    fig_vacances = px.pie(filtered_df, names="Vacances_scolaires", title="Admissions pendant les Vacances Scolaires")
    fig_vacances.update_layout(legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1))
    st.plotly_chart(fig_vacances, use_container_width=True)

with col_pie4:
    fig_evenements = px.pie(filtered_df, names="Evenement_Special", title="Admissions lors d'Événements Spéciaux")
    fig_evenements.update_layout(legend=dict(yanchor="middle", y=0.5, xanchor="left", x=1))
    st.plotly_chart(fig_evenements, use_container_width=True)



# Sélection de la vue
st.subheader("🔍 Sélectionnez une vue")
vue_selection = st.radio("Selectionner", ["Vue Mensuelle", "Vue Journalière", "Vue Annuelle"], horizontal=True, label_visibility="hidden" )

if vue_selection == "Vue Mensuelle":
    x_axis = "Mois"
    category_orders = {"Mois": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]}
elif vue_selection == "Vue Journalière":
    x_axis = "Jour_semaine"
    category_orders = {"Jour_semaine": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
else:
    x_axis = "Annee"
    category_orders = {}

# Graphique Admissions empilées par la sélection
st.subheader(f"📊 Admissions par Service : {vue_selection}")
admissions_service = filtered_df.groupby([x_axis, "Service d'admission"], observed=True).agg({"ID_patient": "count"}).reset_index()
fig_service = px.bar(
    admissions_service,
    x=x_axis,
    y="ID_patient",
    color="Service d'admission",
    title=f"Admissions {vue_selection} par Service",
    labels={"ID_patient": "Nombre d'Admissions", x_axis: x_axis},
    barmode="relative",
    category_orders=category_orders,
    template="plotly_white",
)
st.plotly_chart(fig_service, use_container_width=True)

st.subheader(f"📊 Admissions par niveau de Gravité : {vue_selection}")
admissions_gravite = filtered_df.groupby([x_axis, "Gravité"], observed=True).agg({"ID_patient": "count"}).reset_index()
fig_gravite = px.bar(
    admissions_gravite,
    x=x_axis,
    y="ID_patient",
    color="Gravité",
    title=f"Admissions {vue_selection} par Gravité",
    labels={"ID_patient": "Nombre d'Admissions", x_axis: x_axis},
    barmode="relative",
    category_orders=category_orders,
    template="plotly_white",
)
st.plotly_chart(fig_gravite, use_container_width=True)


st.subheader("🚑 Mode d'arrivée et hospitalisation")
col_bar1, col_bar2 = st.columns(2)
# Graphique Admissions par Mode d'Arrivée
with col_bar1:
    admissions_mode = df.groupby("Mode d'arrivée", observed=True).agg({"ID_patient": "count"}).reset_index()
    fig_mode = px.bar(
        admissions_mode,
        x="Mode d'arrivée",
        y="ID_patient",
        title="Admissions par Mode d'Arrivée",
        labels={"ID_patient": "Nombre d'Admissions", "Mode d'arrivée": "Mode d'Arrivée"},
        color = "Mode d'arrivée",
        template="plotly_white",
    )
    st.plotly_chart(fig_mode, use_container_width=True)

# Graphique Admissions par Type d'Hospitalisation
with col_bar2:
    admissions_hosp = df.groupby("Type d'hospitalisation", observed=True).agg({"ID_patient": "count"}).reset_index()
    fig_hosp = px.pie(
        admissions_hosp,
        names="Type d'hospitalisation",
        values="ID_patient",
        title="Admissions par Type d'Hospitalisation",
        template="plotly_white",
    )
    st.plotly_chart(fig_hosp, use_container_width=True)

# Graphique Durée Moyenne de Séjour par Service avec Type d'Hospitalisation
st.subheader("⏳ Durée Moyenne de Séjour par Service et Type d'Hospitalisation")
duree_service = df.groupby(["Service d'admission", "Type d'hospitalisation"], observed=True).agg({"Durée du séjour estimé": "mean"}).reset_index()
fig_duree = px.bar(
    duree_service,
    x="Service d'admission",
    y="Durée du séjour estimé",
    color="Type d'hospitalisation",
    title="Durée Moyenne de Séjour par Service",
    labels={"Durée du séjour estimé": "Durée Moyenne (jours)", "Service d'admission": "Service"},
    barmode="relative",
    template="plotly_white",
)
st.plotly_chart(fig_duree, use_container_width=True)


# --- FOOTER ---
st.markdown("<div class='footer'>© 2024 - Hôpitaux Universitaires | Tous droits réservés</div>", unsafe_allow_html=True)