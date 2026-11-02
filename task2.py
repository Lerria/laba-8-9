import pandas as pd
import matplotlib.pyplot as plt

FILE = "comptagevelo2011.csv"
YEAR = 2011

df = pd.read_csv(FILE, sep=",", encoding="utf-8")
df.columns = [c.strip() for c in df.columns]

# Прибираємо безіменний стовпець із часом (00:00)
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

# Дата -> індекс
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["Date"]).set_index("Date")

# Усі інші стовпці -> числа, пропуски -> 0
df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

# Первинний аналіз
print(df.head())
print(df.info())
print(df.describe())

tracks = list(df.columns)
print("\nДоріжки у файлі:", tracks)

# Оброблення
per_track = df.sum()
print("\nЗа рік по кожній доріжці:\n", per_track)
print("Загальна кількість велосипедистів за", YEAR, "рік:", int(per_track.sum()))

monthly = df.groupby(df.index.month).sum()
monthly.index.name = "Місяць"
print("\nКількість велосипедистів за місяцями:\n", monthly)

# Три обрані доріжки
three = ["Berri1", "Maisonneuve_1", "Parc"]
print("\nНайпопулярніший місяць для трьох доріжок:")
for t in three:
    print(f"  {t}: місяць {monthly[t].idxmax()} ({int(monthly[t].max())} велосипедистів)")

# Динаміка однієї доріжки
one = "Berri1"
print(f"\nДинаміка доріжки «{one}» за місяцями:\n", monthly[one])

# Графік
plt.figure(figsize=(10, 6))
plt.plot(monthly.index, monthly[one], marker="o", color="tab:blue")
plt.title(f"Кількість велосипедистів на доріжці «{one}» у {YEAR} році")
plt.xlabel("Місяць")
plt.ylabel("Кількість велосипедистів")
plt.xticks(range(1, 13))
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.show()