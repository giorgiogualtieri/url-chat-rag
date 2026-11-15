import os
import shutil

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from carica_url import carica_url
from dividi_testo import dividi_documenti

# Le due impostazioni che potrai cambiare in futuro
CARTELLA_DB = "chroma_db"
MODELLO_EMBEDDING = "nomic-embed-text"


def crea_embedding():
    """Il 'traduttore' che trasforma il testo in numeri."""
    return OllamaEmbeddings(model=MODELLO_EMBEDDING)


def crea_database(chunk, cartella=CARTELLA_DB):
    """Mette i chunk nell'archivio, partendo ogni volta da un archivio vuoto."""
    # Se esiste un archivio vecchio lo cancelliamo, altrimenti
    # gli stessi chunk finirebbero nell'archivio due volte.
    if os.path.exists(cartella):
        shutil.rmtree(cartella)

    database = Chroma.from_documents(
        documents=chunk,
        embedding=crea_embedding(),
        persist_directory=cartella,
    )
    return database


if __name__ == "__main__":
    url = input("Incolla l'URL da analizzare: ").strip()
    documenti = carica_url(url)
    chunk = dividi_documenti(documenti)

    print()
    print("Chunk da memorizzare:", len(chunk))
    print("Creo gli embedding... (puo richiedere uno o due minuti)")

    database = crea_database(chunk)
    print("Chunk salvati nel database:", len(database.get()["ids"]))

    # Prova della ricerca per somiglianza
    while True:
        domanda = input("\nFai una domanda di prova (premi Invio senza scrivere per uscire): ").strip()
        if not domanda:
            break

        risultati = database.similarity_search(domanda, k=3)
        for numero, risultato in enumerate(risultati, start=1):
            print(f"\n--- Risultato {numero} ---")
            print(risultato.page_content[:300])