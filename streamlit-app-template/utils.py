import pandas as pd
from datetime import datetime


def load_data(file_path):
    """Charge et prépare les données pour l'analyse"""
    # Détermine le format en fonction de l'extension
    if file_path.endswith(".parquet"):
        df = pd.read_parquet(file_path)
    else:
        df = pd.read_csv(file_path)

    # Conversion des colonnes de date si nécessaire
    if not pd.api.types.is_datetime64_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])

    return df

def corriger_annee(date):
    if date.year == 2025:
        return date.replace(year=2022)
    elif date.year == 2026:
        return date.replace(year=2023)
    elif date.year == 2027:
        return date.replace(year=2024)
    else:
        return date
    

def definir_tranche_age(age):
    if age < 18:
        return "Moins de 18ans"
    elif 18 <= age < 40:
        return "Jeune adulte"
    elif 40 <= age < 65:
        return "Adulte"
    else:
        return "Senior"
    

def load_data2(file_path):
    """Charge et prépare les données pour l'analyse"""
    # Détermine le format en fonction de l'extension
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
        df["Date_heure_admission"] = pd.to_datetime(df["Date_heure_admission"])
        df["Date_heure_admission"] = df["Date_heure_admission"].apply(corriger_annee)
        df["Date_admission"] = df["Date_heure_admission"].dt.date
        df["Annee"] = df["Date_heure_admission"].dt.year
        df["Tranche_age"] = df["Âge"].apply(definir_tranche_age)
            # Assurer l'ordre des mois
        mois_ordre = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        df["Mois"] = pd.Categorical(df["Mois"], categories=mois_ordre, ordered=True)
        # Assurer l'ordre des jours de la semaine
        jours_ordre = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        df["Jour_semaine"] = pd.Categorical(df["Jour_semaine"], categories=jours_ordre, ordered=True)

    else:
        df = pd.read_parquet(file_path)

    # Conversion de la colonne Date_heure_admission au bon format
    if not pd.api.types.is_datetime64_dtype(df["Date_admission"]):
        df["Date_admission"] = pd.to_datetime(df["Date_admission"])
    
    return df

def load_data3(file_path):
    """Charge et prépare les données pour l'analyse"""
    # Détermine le format en fonction de l'extension
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
        df["Date_heure_admission"] = pd.to_datetime(df["Date_heure_admission"])
        df["Date_heure_admission"] = df["Date_heure_admission"].apply(corriger_annee)
        df["Date_admission"] = df["Date_heure_admission"].dt.date
        df["Annee"] = df["Date_heure_admission"].dt.year 
        date_limite = datetime.strptime("2024-11-15", "%Y-%m-%d").date()
        df = df[df["Date_admission"] <= date_limite] 
        # Assurer l'ordre des mois
        mois_ordre = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        df["Mois"] = pd.Categorical(df["Mois"], categories=mois_ordre, ordered=True)
        # Assurer l'ordre des jours de la semaine
        jours_ordre = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        df["Jour_semaine"] = pd.Categorical(df["Jour_semaine"], categories=jours_ordre, ordered=True)
        admission_df = df.groupby("Date_admission", observed=True).agg({
            "Jour_semaine": "first",
            "Mois": "first",
            "Annee": 'first',
            "Saison": "first",
            "Vacances_scolaires": "first",
            "Température": "mean",
            "Météo": lambda x: x.mode()[0] if not x.mode().empty else None,
            "Lits occupes": "sum",
            "Materiel utilise": "sum",
            "Nb medecin": "sum",
            "Nb infirmier": "sum",
            "Nb aide soignant": "sum" ,
            "Evenement_Special": "first"
        }).reset_index()

        admission_df["Température"] = admission_df["Température"].round().astype(int)
        admission_df["Nb medecin"] = (admission_df["Nb medecin"] / 4).round().astype(int)
        admission_df["Nb infirmier"] = (admission_df["Nb infirmier"] / 4).round().astype(int)
        admission_df["Nb aide soignant"] = (admission_df["Nb aide soignant"] / 4).round().astype(int)

        admission_df["Nombre_admissions"] = df.groupby("Date_admission").size().values
        admission_df = admission_df.sort_values(by="Date_admission")

    else:
        df = pd.read_parquet(file_path)

    # Conversion de la colonne Date_heure_admission au bon format
    if not pd.api.types.is_datetime64_dtype(admission_df["Date_admission"]):
        admission_df["Date_admission"] = pd.to_datetime(admission_df["Date_admission"])
    
    return admission_df


def filter_dataframe(df, start_date=None, end_date=None, categories=None):
    """Filtre le DataFrame selon les critères spécifiés"""
    filtered_df = df.copy()

    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df["date"] >= start_date) & (filtered_df["date"] <= end_date)
        ]

    if categories and len(categories) > 0:
        filtered_df = filtered_df[filtered_df["category"].isin(categories)]

    return filtered_df
