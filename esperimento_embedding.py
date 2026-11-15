import numpy as np
from langchain_ollama import OllamaEmbeddings

embedding = OllamaEmbeddings(model="nomic-embed-text")

frase1 = "Mi piacciono molto i cani"
frase2 = "Adoro i cuccioli di cane"
frase3 = "Oggi fuori c'e un tempo bruttissimo"

# Trasformiamo ogni frase in una lista di numeri (le sue coordinate)
v1 = embedding.embed_query(frase1)
v2 = embedding.embed_query(frase2)
v3 = embedding.embed_query(frase3)

print("Quanti numeri formano un embedding:", len(v1))
print("I primi 5 numeri della frase 1:", v1[:5])


def somiglianza(a, b):
    """Misura quanto due liste di numeri sono vicine: 1 = identiche, 0 = senza legami."""
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


print()
print("Cani vs cuccioli (stesso argomento):", round(somiglianza(v1, v2), 3))
print("Cani vs tempo (argomenti diversi):  ", round(somiglianza(v1, v3), 3))
print("Cuccioli vs tempo (diversi):        ", round(somiglianza(v2, v3), 3))