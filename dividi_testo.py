import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from carica_url import carica_url


def dividi_documenti(documenti, dimensione_chunk=1000, sovrapposizione=150, lunghezza_minima=100):
    """Pulisce il testo, lo taglia in chunk e scarta i pezzi troppo corti."""
    for doc in documenti:
        testo = doc.page_content

        # Wikipedia: togliamo le righe che rimandano ad altre pagine
        testo = re.sub(r"(?m)^Lo stesso argomento in dettaglio:.*$", "", testo)

        # Riduciamo le righe vuote di seguito a una sola riga vuota
        testo = re.sub(r"\n\s*\n+", "\n\n", testo)

        doc.page_content = testo

    divisore = RecursiveCharacterTextSplitter(
        chunk_size=dimensione_chunk,
        chunk_overlap=sovrapposizione,
    )
    chunk = divisore.split_documents(documenti)

    # Scartiamo i pezzi troppo corti: di solito sono rumore (menu, rimandi, titoli)
    return [pezzo for pezzo in chunk if len(pezzo.page_content.strip()) >= lunghezza_minima]


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