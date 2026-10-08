import os
import json
import argparse
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# ==========================================================
# 1. GESTIONE PARAMETRI ESTERNI (CLI & CONFIG FILE)
# ==========================================================

parser = argparse.ArgumentParser(description="Calcolo metriche di classificazione")
parser.add_argument(
    "--config",
    type=str,
    default="config_esperimento.json",
    help="Percorso del file JSON di configurazione"
)
args = parser.parse_args()

try:
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = json.load(f)
except FileNotFoundError:
    print(f"[ERRORE] File di configurazione non trovato: {args.config}")
    exit(1)

path_gt = cfg["ground_truth"]
file_predizioni = cfg["datasets"]
out_excel = cfg.get("output_excel", "Analisi_Sperimentale.xlsx")
out_tex_metriche = cfg.get("output_latex_metriche", "Tabella_Metriche.tex")
out_tex_errori = cfg.get("output_latex_errori", "Tabella_Errori_Categorie.tex")

# ==========================================================
# 2. CARICAMENTO DINAMICO DEI DATASET
# ==========================================================

try:
    # sep=None e engine="python" permettono a Pandas di capire da solo se il separatore è una virgola o un punto e virgola
    df_gt = pd.read_csv(path_gt, encoding="utf-8-sig", sep=None, engine="python")
    datasets = {nome: pd.read_csv(percorso, encoding="utf-8-sig", sep=None, engine="python") for nome, percorso in file_predizioni.items()}
except UnicodeDecodeError:
    df_gt = pd.read_csv(path_gt, encoding="latin-1", sep=None, engine="python")
    datasets = {nome: pd.read_csv(percorso, encoding="latin-1", sep=None, engine="python") for nome, percorso in file_predizioni.items()}
except FileNotFoundError as e:
    print(f"[ERRORE] Impossibile caricare i file CSV: {e}")
    exit(1)

# ==========================================================
# 3. CALCOLO DELLE METRICHE
# ==========================================================

results = []
error_tables = []

for phase, df in datasets.items():

    # Allineamento e linearizzazione delle matrici
    y_true = df_gt.iloc[:, 1:].values.flatten()
    y_pred = df.iloc[:, 1:].values.flatten()

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="binary", zero_division=0)
    recall = recall_score(y_true, y_pred, average="binary", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="binary", zero_division=0)

    # Exact Match Accuracy (tutte le 7 categorie corrette)
    exact_match = (df_gt.iloc[:, 1:] == df.iloc[:, 1:]).all(axis=1).mean()

    # Matrice di confusione
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    # Conteggio errori per categoria
    errors = (df_gt.iloc[:, 1:] != df.iloc[:, 1:]).sum()
    errors_df = pd.DataFrame({"Categoria": errors.index, "Errori": errors.values})
    errors_df["Fase"] = phase
    error_tables.append(errors_df)

    results.append({
        "Fase": phase,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1,
        "Exact Match": exact_match,
        "TP": tp, "TN": tn, "FP": fp, "FN": fn
    })

# Metriche quantitative di scarto (delta)
quantitative_results = []
for phase, df in datasets.items():
    gt_total = df_gt.iloc[:, 1:].sum(axis=1)
    llm_total = df.iloc[:, 1:].sum(axis=1)
    delta = llm_total - gt_total
    quantitative_results.append({
        "Fase": phase,
        "Media_Delta (mu)": delta.mean(),
        "Dev_Std (sigma)": delta.std()
    })

df_quantitativo = pd.DataFrame(quantitative_results)
df_metriche = pd.DataFrame(results)
tabella_errori = pd.concat(error_tables).pivot(index="Categoria", columns="Fase", values="Errori")

# ==========================================================
# 4. ESPORTAZIONE DEI RISULTATI
# ==========================================================

with pd.ExcelWriter(out_excel, engine="openpyxl") as writer:
    df_gt.to_excel(writer, sheet_name="Ground_Truth", index=False)
    for name, df in datasets.items():
        df.to_excel(writer, sheet_name=name, index=False)
    df_metriche.to_excel(writer, sheet_name="Metriche", index=False)
    tabella_errori.to_excel(writer, sheet_name="Errori_per_Categoria")
    df_quantitativo.to_excel(writer, sheet_name="Metriche_Quantitative", index=False)

df_metriche.to_latex(
    out_tex_metriche,
    index=False,
    float_format="%.3f",
    caption="Metriche prestazionali delle configurazioni analizzate.",
    label="tab:metriche"
)

tabella_errori.to_latex(
    out_tex_errori,
    float_format="%.0f",
    caption="Numero di errori per categoria rispetto al Ground Truth.",
    label="tab:errori_categoria"
)

print(f"[SUCCESS] Elaborazione completata per la configurazione: {args.config}")