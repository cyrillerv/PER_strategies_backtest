from pathlib import Path
import json 
import pandas as pd
from tqdm import tqdm


def load_variables(fields):
    if fields == [] :
        return {}
    dossier = Path(r"data\variables")
    all_files = [f for f in dossier.iterdir() if f.is_file()]

    field_files = []

    if "all" in [f.lower() for f in fields]:
        field_files = all_files
    else:
        for field in fields:
            found = False
            for file in all_files:
                if field.lower() == file.stem.lower():
                    field_files.append(file)
                    found = True
                    break
            if not found:
                print(f"Warning: file for field '{field}' not found in data folder.")

    dic_df = {}
    for file in tqdm(field_files, desc="Loading data..."):
        field_name = file.stem  # nom du fichier sans extension
        extension = file.suffix.lower()  # avec le point, ex: '.csv'
        if extension == ".csv" :
            df = pd.read_csv(file)
            dic_df[field_name] = df
        elif "sector" in field_name.lower() and extension == ".json" :
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
            dic_df["Sectors"] = data

    return dic_df



def load_main_data() :
    dossier = Path("data")
    field_files = [f for f in dossier.iterdir() if f.is_file()]

    if "per" not in [i.stem.lower() for i in field_files] :
        print(f"Error: PER file not found in data folder. You must name it 'PER' and include it in the inputs of the function.")
    if "stockprices" not in [i.stem.lower() for i in field_files] :
        print(f"Error: StockPrices file not found in data folder. You must name it 'StockPrices' and include it in the inputs of the function.")

    dic_df = {}
    for file in tqdm(field_files, desc="Loading data..."):
        field_name = file.stem  # nom du fichier sans extension
        extension = file.suffix.lower()  # avec le point, ex: '.csv'
        if field_name.lower() == 'stockprices' and extension == ".csv" :
            df = pd.read_csv(file)
            dic_df['StockPrices'] = df
        elif field_name.lower() == 'per' and extension == ".csv" :
            df = pd.read_csv(file)
            dic_df['PER'] = df
        elif field_name.lower() == 'etf_bench' and extension == ".csv" :
            df = pd.read_csv(file)
            dic_df['Factors'] = df

    return dic_df