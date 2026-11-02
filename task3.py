import string
import nltk
import matplotlib.pyplot as plt
from nltk import FreqDist
from nltk.corpus import gutenberg, stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer

# Завантаження потрібних ресурсів NLTK
for pkg in ["gutenberg", "punkt", "punkt_tab", "stopwords", "wordnet"]:
    nltk.download(pkg, quiet=True)

raw = gutenberg.raw("austen-sense.txt")
tokens = [t.lower() for t in nltk.word_tokenize(raw)]


def top10_chart(words, title):
    top = FreqDist(words).most_common(10)
    print(f"\n{title}:")
    for w, c in top:
        print(f"  {w}: {c}")
    plt.figure(figsize=(10, 6))
    plt.bar([w for w, _ in top], [c for _, c in top], color="tab:green")
    plt.title(title)
    plt.xlabel("Слово")
    plt.ylabel("Кількість уживань")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()


# 1. Кількість слів і унікальних слів
total = len(tokens)
unique = len(set(tokens))
print("Кількість слів у тексті:", total)
print("Кількість унікальних слів:", unique)
print("Унікальні слова становлять %.2f%% від усіх" % (100 * unique / total))
print("Кожне слово вживається в середньому %.1f раза" % (total / unique))

# 2. Топ 10 слів + діаграма
top10_chart(tokens, "10 найуживаніших слів (до очищення)")

# 3. Без стоп-слів і пунктуації + діаграма
stop = set(stopwords.words("english"))
clean = [t for t in tokens
         if t.isalpha() and t not in stop and t not in string.punctuation]
top10_chart(clean, "10 найуживаніших слів (без стоп-слів і пунктуації)")

# 4. Лематизація та стемінг
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

lemmas = [lemmatizer.lemmatize(w) for w in clean]
stems = [stemmer.stem(w) for w in clean]

print("\n10 найуживаніших слів після лематизації:")
for w, c in FreqDist(lemmas).most_common(10):
    print(f"  {w}: {c}")

print("\n10 найуживаніших слів після стемінгу:")
for w, c in FreqDist(stems).most_common(10):
    print(f"  {w}: {c}")