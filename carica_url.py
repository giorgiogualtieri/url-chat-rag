import os

# Presentiamoci al sito web con un nome, come quando bussi a una porta.
# Deve stare PRIMA dell'import qui sotto.
os.environ.setdefault("USER_AGENT", "url-chat-rag/0.1")

from langchain_community.document_loaders import WebBaseLoader


def carica_url(url):
    """Scarica la pagina all'indirizzo dato e restituisce i documenti con il testo."""
    lettore = WebBaseLoader(url)
    documenti = lettore.load()
    return documenti


if __name__ == "__main__":
    url = input("Incolla l'URL da analizzare: ").strip()
    documenti = carica_url(url)

    print()
    print("Numero di documenti caricati:", len(documenti))

    primo = documenti[0]
    print("Metadati (informazioni sulla pagina):", primo.metadata)
    print("Lunghezza del testo (caratteri):", len(primo.page_content))
    print()
    print("--- Primi 500 caratteri del testo ---")
    print(primo.page_content[:500])