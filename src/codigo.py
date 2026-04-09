"""
Proyecto final — EDA Austin Animal Center
"""

import pandas as pd
import numpy as np

RAW_INTAKES_FILE = "data/raw/Austin_Animal_Center_Intakes.csv"
RAW_OUTCOMES_FILE = "data/raw/Austin_Animal_Center_Outcomes.csv"

PROCESSED_FILE = "data/processed/Austin_Animal_Center_Processed.csv"

TABLES_DIR = "tables/"
OUTCOME_TABLES_DIR = "src/outcomes/tables/"
PLOTS_DIR = "src/outcomes/plots/"
EXCEL_DIR = "src/outcomes/excel/"


# FUNCIONES
def save_table(df, filename):
    """
    Guarda una tabla como CSV
    """
    df.to_csv(TABLES_DIR + filename, index=False, float_format="%.2f")
def print_summary(summary):
    """
    Imprime por pantalla un resumen de las tablas
    """
    print("RESUMEN DE RESULTADOS")

    for name, table in summary.items():
        print(f"\n--- {name.upper()} ---")
        print(f"Filas: {table.shape[0]} | Columnas: {table.shape[1]}")

        if table.shape[0] <= 10:
            print(table.to_string(index=False))
        else:
            print(table.head(10).to_string(index=False))
            print("... (mostrando solo 10 primeras filas)")

def normalize_text(texto):
    """
    Funcion para normalizar a tipo string, quitamos espacios y vacios.
    """
    return texto.astype("string").str.strip().replace({"": pd.NA})

def age_to_days(age_text):
    """
    Convertimos la edad en texto a dias
    """
    if pd.isna(age_text):
        return np.nan

    age_text = str(age_text).strip().lower()
    age_parts = age_text.split()

    if len(age_parts) < 2:
        return np.nan

    try:
        age_value = float(age_parts[0])
    except ValueError:
        return np.nan

    if age_value < 0:
        return np.nan

    age_unit = age_parts[1]

    if "year" in age_unit:
        return age_value * 365
    if "month" in age_unit:
        return age_value * 30
    if "week" in age_unit:
        return age_value * 7
    if "day" in age_unit:
        return age_value

    return np.nan

def age_group(days):
    """
    Funcion que clasifica la edad por grupos
    """
    if pd.isna(days):
        return "Unknown"
    if days < 30:
        return "0-1 month"
    if days < 180:
        return "1-6 months"
    if days < 365:
        return "6-12 months"
    if days < 365 * 3:
        return "1-3 years"
    if days < 365 * 7:
        return "3-7 years"
    return "7+ years"

def split_sex_status(value):
    """
    Separa sexo y estado reproductivo en dos columnas.
    """
    if pd.isna(value):
        return pd.Series([pd.NA, pd.NA])

    sex_text = str(value).strip().lower()

    if sex_text == "unknown":
        return pd.Series(["Unknown", "Unknown"])

    animal_sex = pd.NA
    reproductive_status = pd.NA

    if "female" in sex_text:
        animal_sex = "Female"
    elif "male" in sex_text:
        animal_sex = "Male"

    if "neutered" in sex_text or "spayed" in sex_text:
        reproductive_status = "Fixed"
    elif "intact" in sex_text:
        reproductive_status = "Intact"

    return pd.Series([animal_sex, reproductive_status])

def split_color(value):
    """
    Separa colores cuando hay más de uno separados por /
    """
    if pd.isna(value):
        return pd.Series([pd.NA, pd.NA])

    color_text = str(value).strip()

    if "/" in color_text:
        split_colors = color_text.split("/")
        first_color = split_colors[0].strip().title() if len(split_colors) > 0 else pd.NA
        second_color = split_colors[1].strip().title() if len(split_colors) > 1 else pd.NA
        return pd.Series([first_color, second_color])

    return pd.Series([color_text.title(), pd.NA])

def breed_type(value):
    """
    Clasifica la raza en: Mixed: si contiene 'Mix' o '/' o Pure: en caso contrario
    """
    if pd.isna(value):
        return pd.NA

    breed_text = str(value).strip().lower()

    if "mix" in breed_text or "/" in breed_text:
        return "Mixed"
    return "Pure"

def build_case_id(animal_id, event_number):

    """
    Construye una clave de episodio. Basicamente, una entrada-salida de un animal, ya que hay varias para un mismo animal.
    """
    if pd.isna(animal_id) or pd.isna(event_number):
        return pd.NA
    return f"{animal_id}_{int(event_number)}"

def columns_to_int(table):
    """
    Convierte a entero,nullable las columnasindicadas.
    """
    count_like_columns = [
        "count",
        "n_animals",
        "n_outcomes",
        "n_intakes",
        "missing_count",
        "exact_duplicate_rows",
        "duplicated_animal_id_rows",
        "unique_animal_ids",
        "rows",
        "columns",
        "matched_records",
        "unmatched_records",
        "negative_stay_records",
    ]

    for col in count_like_columns:
        if col in table.columns:
            table[col] = table[col].round(0).astype("Int64")

    return table


# CARGA DE DATOS
def load_data():
    """
    Carga los raw datasets de entradas y salidas del Austin Animal Center.
    """
    intakes = pd.read_csv(RAW_INTAKES_FILE)
    outcomes = pd.read_csv(RAW_OUTCOMES_FILE)
    return intakes, outcomes

# REVISIÓN DE CALIDAD DE DATOS
def review_intakes_data(intakes):
    """
    Revisión inicial del dataset de entradas del animal center
    """
    review = pd.DataFrame({
        "metric": [
            "n_filas",
            "n_columnas",
            "filas_duplicadas",
            "null_animal_id",
            "unico_animal_id",
            "repeatidos_animal_ids",
            "datetime_monthyear_filas_iguales"
        ],
        "value": [
            int(intakes.shape[0]),
            int(intakes.shape[1]),
            int(intakes.duplicated().sum()),
            int(intakes["Animal ID"].isna().sum()),
            int(intakes["Animal ID"].nunique(dropna=True)),
            int(intakes["Animal ID"].duplicated(keep=False).sum()),
            int((intakes["DateTime"] == intakes["MonthYear"]).fillna(False).sum())
        ]
    })

    review["dataset"] = "intakes"
    return review[["dataset", "metric", "value"]]

def review_outcomes_data(outcomes):
    """
    Revisión inicial del dataset de salidas del animal center
    """
    review = pd.DataFrame({
        "metric": [
            "n_filas",
            "n_columnas",
            "filas_duplicadas",
            "null_animal_id",
            "unico_animal_id",
            "repeatidos_animal_ids",
            "datetime_monthyear_filas_iguales"
        ],
        "value": [
            int(outcomes.shape[0]),
            int(outcomes.shape[1]),
            int(outcomes.duplicated().sum()),
            int(outcomes["Animal ID"].isna().sum()),
            int(outcomes["Animal ID"].nunique(dropna=True)),
            int(outcomes["Animal ID"].duplicated(keep=False).sum()),
            int((outcomes["DateTime"] == outcomes["MonthYear"]).fillna(False).sum())
        ]
    })

    review["dataset"] = "outcomes"
    return review[["dataset", "metric", "value"]]

# LIMPIEZA DEL DATASET DE INTAKES Y OUTCOMES
def clean_intakes(intakes):
    """
    Limpieza y transformación del dataset de entradas al Austin center.
    """
    intakes = intakes.copy()

    for column in intakes.columns:
        if intakes[column].dtype == object:
            intakes[column] = normalize_text(intakes[column])

    intakes["Animal ID"] = intakes["Animal ID"].astype("string").str.strip()
    intakes = intakes.dropna(subset=["Animal ID"])
    intakes = intakes.drop_duplicates()

    datetime_format = "%m/%d/%Y %I:%M:%S %p"
    intakes["intake_datetime"] = pd.to_datetime(
        intakes["DateTime"],
        format=datetime_format,
        errors="coerce"
    )

    intakes = intakes.sort_values(["Animal ID", "intake_datetime"]).copy()
    intakes["event_number"] = intakes.groupby("Animal ID").cumcount() + 1
    intakes["case_id"] = intakes.apply(
        lambda row: build_case_id(row["Animal ID"], row["event_number"]),
        axis=1
    )

    intakes["intake_age_days"] = intakes["Age upon Intake"].apply(age_to_days)
    intakes["intake_age_group"] = intakes["intake_age_days"].apply(age_group)

    intakes[["intake_sex", "intake_reproductive_status"]] = (
        intakes["Sex upon Intake"].apply(split_sex_status)
    )

    intakes[["intake_color_1", "intake_color_2"]] = intakes["Color"].apply(split_color)

    intakes["breed_type"] = intakes["Breed"].apply(breed_type)

    intakes["intake_year"] = intakes["intake_datetime"].dt.year.astype("Int64")
    intakes["intake_month"] = intakes["intake_datetime"].dt.month.astype("Int64")
    intakes["intake_day"] = intakes["intake_datetime"].dt.day.astype("Int64")

    intakes_clean = intakes[
        [
            "case_id",
            "Animal ID",
            "event_number",
            "Name",
            "Animal Type",
            "Breed",
            "breed_type",
            "Found Location",
            "Intake Type",
            "Intake Condition",
            "intake_datetime",
            "intake_year",
            "intake_month",
            "intake_day",
            "intake_age_days",
            "intake_age_group",
            "intake_sex",
            "intake_reproductive_status",
            "intake_color_1",
            "intake_color_2"
        ]
    ].copy()

    intakes_clean = intakes_clean.rename(
        columns={
            "Animal ID": "animal_id",
            "Name": "animal_name",
            "Animal Type": "animal_type",
            "Breed": "breed",
            "Found Location": "found_location",
            "Intake Type": "intake_type",
            "Intake Condition": "intake_condition",
        }
    )

    return intakes_clean

def clean_outcomes(outcomes):
    """
    Limpieza y transformación del dataset de salidas del animal center.
    Devuelve un dataset limpio sin columnas originales redundantes.
    """
    outcomes = outcomes.copy()

    for column in outcomes.columns:
        if outcomes[column].dtype == object:
            outcomes[column] = normalize_text(outcomes[column])

    outcomes["Animal ID"] = outcomes["Animal ID"].astype("string").str.strip()
    outcomes = outcomes.dropna(subset=["Animal ID"])
    outcomes = outcomes.drop_duplicates()

    datetime_format = "%m/%d/%Y %I:%M:%S %p"
    outcomes["outcome_datetime"] = pd.to_datetime(
        outcomes["DateTime"],
        format=datetime_format,
        errors="coerce"
    )

    outcomes = outcomes.sort_values(["Animal ID", "outcome_datetime"]).copy()
    outcomes["event_number"] = outcomes.groupby("Animal ID").cumcount() + 1
    outcomes["case_id"] = outcomes.apply(
        lambda row: build_case_id(row["Animal ID"], row["event_number"]),
        axis=1
    )

    outcomes["outcome_age_days"] = outcomes["Age upon Outcome"].apply(age_to_days)
    outcomes["outcome_age_group"] = outcomes["outcome_age_days"].apply(age_group)

    outcomes[["outcome_sex", "outcome_reproductive_status"]] = (
        outcomes["Sex upon Outcome"].apply(split_sex_status)
    )

    outcomes[["outcome_color_1", "outcome_color_2"]] = outcomes["Color"].apply(split_color)

    outcomes["breed_type"] = outcomes["Breed"].apply(breed_type)

    outcomes["outcome_year"] = outcomes["outcome_datetime"].dt.year.astype("Int64")
    outcomes["outcome_month"] = outcomes["outcome_datetime"].dt.month.astype("Int64")
    outcomes["outcome_day"] = outcomes["outcome_datetime"].dt.day.astype("Int64")

    outcomes["date_of_birth"] = pd.to_datetime(outcomes["Date of Birth"], errors="coerce")

    outcomes_clean = outcomes[
        [
            "case_id",
            "Animal ID",
            "event_number",
            "Name",
            "Animal Type",
            "Breed",
            "breed_type",
            "outcome_datetime",
            "outcome_year",
            "outcome_month",
            "outcome_day",
            "date_of_birth",
            "Outcome Type",
            "Outcome Subtype",
            "outcome_age_days",
            "outcome_age_group",
            "outcome_sex",
            "outcome_reproductive_status",
            "outcome_color_1",
            "outcome_color_2"
        ]
    ].copy()

    outcomes_clean = outcomes_clean.rename(
        columns={
            "Animal ID": "animal_id",
            "Name": "animal_name",
            "Animal Type": "animal_type",
            "Breed": "breed",
            "Outcome Type": "outcome_type",
            "Outcome Subtype": "outcome_subtype",
        }
    )

    return outcomes_clean


# MERGE DE DATASETS (MERGE POR ID + EVENT_NUMBER)
def build_final_dataset(intakes, outcomes):
    """
    Unimos ambos datasets mediante el identificador del animal y el número de evento.
    El dataset final no conserva columnas originales redundantes.
    """
    master = intakes.merge(
        outcomes[
            [
                "animal_id",
                "event_number",
                "date_of_birth",
                "outcome_datetime",
                "outcome_year",
                "outcome_month",
                "outcome_day",
                "outcome_type",
                "outcome_subtype",
                "outcome_age_days",
                "outcome_age_group",
                "outcome_sex",
                "outcome_reproductive_status",
            ]
        ],
        on=["animal_id", "event_number"],
        how="left",
    )

    master["has_outcome_record"] = master["outcome_datetime"].notna()

    raw_stay_days = (
        master["outcome_datetime"] - master["intake_datetime"]
    ).dt.total_seconds() / 86400

    master["negative_stay_anomaly"] = raw_stay_days < 0
    master["length_of_stay_days"] = raw_stay_days.round(2)
    master.loc[master["negative_stay_anomaly"], "length_of_stay_days"] = np.nan

    int_cols = [
        "event_number",
        "intake_year",
        "intake_month",
        "intake_day",
        "outcome_year",
        "outcome_month",
        "outcome_day",
    ]

    for col in int_cols:
        if col in master.columns:
            master[col] = master[col].astype("Int64")

    return master

def review_merge(master):
    """
    Genera una tabla resumen sobre la calidad del emparejamiento final.
    """
    merge_quality = pd.DataFrame(
        {
            "registros_con_match": [master["has_outcome_record"].sum()],
            "registros_sin_match": [(~master["has_outcome_record"]).sum()],
            "registros_stay_negativo": [master["negative_stay_anomaly"].sum()],
        }
    )
    return {"merge_quality": columns_to_int(merge_quality)}


# ANÁLISIS DESCRIPTIVO
def descriptive_analysis(master):
    """
    Analisis descriptivo: conteos, distribuciones, tablas por categorias, resumenes por grupos.
    """
    summary = {}

    numeric_vars = ["intake_age_days", "outcome_age_days", "length_of_stay_days"]
    numeric_summary = master[numeric_vars].describe().T
    numeric_summary["median"] = master[numeric_vars].median()
    numeric_summary["missing_count"] = master[numeric_vars].isna().sum()
    numeric_summary["missing_pct"] = (master[numeric_vars].isna().mean() * 100).round(2)
    numeric_summary = numeric_summary.round(2)
    numeric_summary["count"] = numeric_summary["count"].astype("Int64")
    numeric_summary["missing_count"] = numeric_summary["missing_count"].astype("Int64")
    summary["numeric_summary"] = numeric_summary.reset_index().rename(columns={"index": "variable"})

    animals_by_type = (
        master.groupby("animal_type", dropna=False)
        .size()
        .reset_index(name="n_animals")
        .sort_values("n_animals", ascending=False)
    )
    summary["animals_by_type"] = columns_to_int(animals_by_type)

    animals_by_intake_sex = (
        master.groupby("intake_sex", dropna=False)
        .size()
        .reset_index(name="n_animals")
        .sort_values("n_animals", ascending=False)
    )
    summary["animals_by_intake_sex"] = columns_to_int(animals_by_intake_sex)

    animals_by_reproductive_status = (
        master.groupby("intake_reproductive_status", dropna=False)
        .size()
        .reset_index(name="n_animals")
        .sort_values("n_animals", ascending=False)
    )
    summary["animals_by_reproductive_status"] = columns_to_int(animals_by_reproductive_status)

    animals_by_age_group = (
        master.groupby("intake_age_group", dropna=False)
        .size()
        .reset_index(name="n_animals")
        .sort_values("n_animals", ascending=False)
    )
    summary["animals_by_age_group"] = columns_to_int(animals_by_age_group)

    outcomes_by_type = (
        master.groupby("outcome_type", dropna=False)
        .size()
        .reset_index(name="n_outcomes")
        .sort_values("n_outcomes", ascending=False)
    )
    summary["outcomes_by_type"] = columns_to_int(outcomes_by_type)

    stay_by_outcome_type = (
        master.groupby("outcome_type", dropna=False)["length_of_stay_days"]
        .agg(["count", "mean", "median", "min", "max", "std"])
        .round(2)
        .reset_index()
        .sort_values("count", ascending=False)
    )
    summary["stay_by_outcome_type"] = columns_to_int(stay_by_outcome_type)

    stay_by_animal_type = (
        master.groupby("animal_type", dropna=False)["length_of_stay_days"]
        .agg(["count", "mean", "median", "min", "max", "std"])
        .round(2)
        .reset_index()
        .sort_values("count", ascending=False)
    )
    summary["stay_by_animal_type"] = columns_to_int(stay_by_animal_type)

    monthly_outcomes = (
        master.dropna(subset=["outcome_year", "outcome_month"])
        .groupby(["outcome_year", "outcome_month"], dropna=False)
        .size()
        .reset_index(name="n_outcomes")
        .sort_values(["outcome_year", "outcome_month"])
    )
    summary["monthly_outcomes"] = columns_to_int(monthly_outcomes)

    monthly_intakes = (
        master.dropna(subset=["intake_year", "intake_month"])
        .groupby(["intake_year", "intake_month"], dropna=False)
        .size()
        .reset_index(name="n_intakes")
        .sort_values(["intake_year", "intake_month"])
    )
    summary["monthly_intakes"] = columns_to_int(monthly_intakes)

    breed_type_summary = (
        master.groupby("breed_type", dropna=False)
        .size()
        .reset_index(name="n_animals")
        .sort_values("n_animals", ascending=False)
    )
    summary["breed_type_summary"] = columns_to_int(breed_type_summary)


    return summary

# ANÁLISIS ESTADISTICO
def statistical_analysis(master):
    """
    Análisis estadístico: correlacion, dispersion, cuantiles y relaciones internas.
    """
    summary = {}
    numeric_vars = ["intake_age_days", "outcome_age_days", "length_of_stay_days"]

    numeric_quantiles = master[numeric_vars].quantile([0.25, 0.50, 0.75]).round(2)
    numeric_quantiles.index = ["percentil_25", "mediana", "percentil_75"]
    summary["numeric_quantiles"] = numeric_quantiles.reset_index().rename(columns={"index": "quantile"})

    stay_variability_by_outcome_type = (
        master.groupby("outcome_type", dropna=False)["length_of_stay_days"]
        .agg(["count", "mean", "std", "var"])
        .round(2)
        .reset_index()
        .sort_values("count", ascending=False)
    )
    summary["stay_variability_by_outcome_type"] = columns_to_int(stay_variability_by_outcome_type)

    stay_variability_by_animal_type = (
        master.groupby("animal_type", dropna=False)["length_of_stay_days"]
        .agg(["count", "mean", "std", "var"])
        .round(2)
        .reset_index()
        .sort_values("count", ascending=False)
    )
    summary["stay_variability_by_animal_type"] = columns_to_int(stay_variability_by_animal_type)

    intake_age_stats_by_animal_type = (
        master.groupby("animal_type", dropna=False)["intake_age_days"]
        .agg(["count", "mean", "median", "std", "var", "min", "max"])
        .round(2)
        .reset_index()
        .sort_values("count", ascending=False)
    )
    summary["intake_age_stats_by_animal_type"] = columns_to_int(intake_age_stats_by_animal_type)

    outcome_age_stats_by_animal_type = (
        master.groupby("animal_type", dropna=False)["outcome_age_days"]
        .agg(["count", "mean", "median", "std", "var", "min", "max"])
        .round(2)
        .reset_index()
        .sort_values("count", ascending=False)
    )
    summary["outcome_age_stats_by_animal_type"] = columns_to_int(outcome_age_stats_by_animal_type)

    correlation_matrix = master[numeric_vars].corr().round(2).reset_index().rename(columns={"index": "variable"})
    summary["correlation_matrix"] = correlation_matrix

    return summary


# ESCRITURA DE RESULTADOS
def write_outputs(intakes_clean, outcomes_clean, after_merge, summary):
    """
    Guarda datasets procesados y tablas de resultados.
    """
    intakes_clean.to_csv("data/processed/intakes_clean.csv", index=False)
    outcomes_clean.to_csv("data/processed/outcomes_clean.csv", index=False)
    after_merge.to_csv("data/processed/animal_center_final.csv", index=False)

    for name, table in summary.items():
        save_table(table, f"{name}.csv")

def main():
    intakes_raw, outcomes_raw = load_data()

    intakes_review = review_intakes_data(intakes_raw)
    outcomes_review = review_outcomes_data(outcomes_raw)

    intakes_clean = clean_intakes(intakes_raw)
    outcomes_clean = clean_outcomes(outcomes_raw)

    after_merge = build_final_dataset(intakes_clean, outcomes_clean)
    merge_review = review_merge(after_merge)

    descriptive_summary = descriptive_analysis(after_merge)
    statistical_summary = statistical_analysis(after_merge)

    summary = {}
    summary["review_intakes_data"] = intakes_review
    summary["review_outcomes_data"] = outcomes_review
    summary.update(merge_review)
    summary.update(descriptive_summary)
    summary.update(statistical_summary)

    write_outputs(intakes_clean, outcomes_clean, after_merge, summary)

    print_summary(summary)
    print("\nEDA completado")
    print("Dimensión tabla final:", after_merge.shape)


if __name__ == "__main__":
    main()