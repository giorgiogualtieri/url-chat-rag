import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from carica_url import carica_url


def dividi_documenti(documenti, dimensione_chunk=1000, sovrapposizione=150):
    """Pulisce il testo e lo taglia in chunk (pezzi)."""
    # Le pagine web hanno spesso tante righe vuote di seguito:
    # le riduciamo a una sola riga vuota.
    for doc in documenti:
        doc.page_content = re.sub(r"\n\s*\n+", "\n\n", doc.page_content)

    divisore = RecursiveCharacterTextSplitter(
        chunk_size=dimensione_chunk,
        chunk_overlap=sovrapposizione,
    )
    return divisore.split_documents(documenti)


if __name__ == "__main__":
    url = input("Incolla l'URL da analizzare: ").strip()
    documenti = carica_url(url)
    chunk = dividi_documenti(documenti)

    lunghezze = [len(c.page_content) for c in chunk]

    print()
    print("Documenti di partenza:", len(documenti))
    print("Chunk ottenuti:", len(chunk))
    print("Lunghezza media di un chunk:", sum(lunghezze) // len(lunghezze))
    print("Lunghezza del chunk più lungo:", max(lunghezze))

    print()
    print("=== CHUNK 1 ===")
    print(chunk[0].page_content)

    if len(chunk) >= 2:
        print()
        print("=== FINE del chunk 1 (ultimi 150 caratteri) ===")
        print(chunk[0].page_content[-150:])
        print()
        print("=== INIZIO del chunk 2 (primi 150 caratteri) ===")
        print(chunk[1].page_content[:150])
        print()
        print("Metadati del chunk 2:", chunk[1].metadata)