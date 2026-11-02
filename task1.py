import os
import requests
import pandas as pd

BASE_URL = "https://api.worldbank.org/v2"
COUNTRIES = {"UKR": "Україна", "POL": "Польща"}
START, END = 2000, 2023

# Основний показник + два додаткові (пов'язані з ним, той самий період і країни)
INDICATORS = {
    "SP.POP.TOTL": "Population",           # основний: чисельність населення
    "NY.GDP.PCAP.CD": "GDP_per_capita",    # додатковий 1: ВВП на душу населення, $
    "SP.DYN.LE00.IN": "Life_expectancy",   # додатковий 2: очікувана тривалість життя
}
SOURCE_CSV = "worldbank_data.csv"


def load(country, indicator):
    url = f"{BASE_URL}/country/{country}/indicator/{indicator}"
    r = requests.get(url, params={"format": "json", "per_page": 100,
                                  "date": f"{START}:{END}"}, timeout=15)
    r.raise_for_status()
    return {int(i["date"]): i["value"] for i in r.json()[1]}


def build_csv():
    rows = []
    for code, name in COUNTRIES.items():
        data = {col: load(code, ind) for ind, col in INDICATORS.items()}
        for year in range(START, END + 1):
            row = {"Country": name, "Year": year}
            for col in INDICATORS.values():
                row[col] = data[col].get(year)
            rows.append(row)
    pd.DataFrame(rows).to_csv(SOURCE_CSV, index=False, encoding="utf-8-sig")


# 1. Завантаження та доповнення даних
if not os.path.exists(SOURCE_CSV):
    build_csv()
df = pd.read_csv(SOURCE_CSV)

need = [c for c in ("GDP_per_capita", "Life_expectancy") if c not in df.columns]
if need:
    inv = {v: k for k, v in INDICATORS.items()}
    name_to_code = {v: k for k, v in COUNTRIES.items()}
    for col in need:
        cache = {c: load(c, inv[col]) for c in COUNTRIES}
        df[col] = [cache[name_to_code[c]].get(y) for c, y in zip(df["Country"], df["Year"])]
    df.to_csv(SOURCE_CSV, index=False, encoding="utf-8-sig")

# 2. Базовий аналіз
print("Вміст DataFrame:\n", df)
print("\nПерші 3 рядки:\n", df.head(3))
print("\nТипи даних:\n", df.dtypes)
print("\nКількість рядків і стовпців:", df.shape)
print("\nОписова статистика:\n", df.describe())

# 3. Попереднє оброблення
df["Year"] = df["Year"].astype(int)                    # зміна типів
df["Population"] = df["Population"].astype("float64")
df = df.dropna()

df["Population_mln"] = df["Population"] / 1e6          # новий розрахунковий стовпець
df["GDP_total_bln"] = df["GDP_per_capita"] * df["Population"] / 1e9

filtered = df[df["Year"] >= 2010]                      # фільтрація
print("\nЗаписи з 2010 року:\n", filtered.head())

sorted_df = df.sort_values("GDP_per_capita", ascending=False)   # сортування
print("\nТоп-5 за ВВП на душу населення:\n", sorted_df.head())

# 4. Групування та агрегація
grouped = df.groupby("Country").agg(
    Population_mean_mln=("Population_mln", "mean"),
    Population_max_mln=("Population_mln", "max"),
    Population_min_mln=("Population_mln", "min"),
    GDP_per_capita_mean=("GDP_per_capita", "mean"),
    GDP_per_capita_max=("GDP_per_capita", "max"),
    Life_expectancy_mean=("Life_expectancy", "mean"),
    Life_expectancy_min=("Life_expectancy", "min"),
).round(2)
print("\nГрупування за країною:\n", grouped)
print("\nУнікальних країн:", df["Country"].nunique())
print("Унікальних років:", df["Year"].nunique())

# 5. Збереження результатів
grouped.to_csv("analysis_result.csv", encoding="utf-8-sig")
df.to_csv("processed_data.csv", index=False, encoding="utf-8-sig")
print("\nЗбережено: analysis_result.csv (групування) і processed_data.csv (оброблені дані)")