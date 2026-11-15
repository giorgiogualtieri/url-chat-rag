import os

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from carica_url import carica_url
from crea_database import CARTELLA_DB, crea_database, crea_embedding
from dividi_testo import dividi_documenti

# Impostazione che potrai cambiare in futuro
MODELLO_CHAT = "llama3.2"

# Il "foglio di istruzioni" che il modello riceve a ogni domanda
PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sei un assistente che risponde in italiano, in modo chiaro e preciso. "
            "Usa SOLO le informazioni presenti nel contesto qui sotto. "
            "Se la risposta non e nel contesto, scrivi: "
            "'Non trovo questa informazione nella pagina.' "
            "Non inventare nulla.",
        ),
        ("human", "Contesto:\n{contesto}\n\nDomanda: {domanda}"),
    ]
)


def prepara_database(url):
    """Scarica la pagina, la divide in chunk e crea l'archivio."""
    documenti = carica_url(url)
    chunk = dividi_documenti(documenti)
    print("Chunk da memorizzare:", len(chunk))
    print("Creo gli embedding... (puo richiedere uno o due minuti)")
    return crea_database(chunk)


def apri_database_esistente():
    """Riapre l'archivio gia creato, senza rifare tutto il lavoro."""
    return Chroma(
        persist_directory=CARTELLA_DB,
        embedding_function=crea_embedding(),
    )


def rispondi(domanda, database):
    """Cerca i pezzi giusti e fa scrivere la risposta al modello."""
        # La ricerca semplice ha dato risultati migliori dell'MMR nei nostri test
    cercatore = database.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )
    trovati = cercatore.invoke(domanda)

    # 2. PREPARA IL FOGLIO: uniamo i pezzi in un unico testo
    contesto = "\n\n".join(pezzo.page_content for pezzo in trovati)

    # 3. RISPONDI: collegamento a catena  prompt -> modello -> testo
    modello = ChatOllama(model=MODELLO_CHAT, temperature=0)
    catena = PROMPT | modello | StrOutputParser()
    risposta = catena.invoke({"contesto": contesto, "domanda": domanda})

    # Le fonti: da quali indirizzi arrivano i pezzi usati
    fonti = sorted({pezzo.metadata.get("source", "sconosciuta") for pezzo in trovati})
    return risposta, fonti


if __name__ == "__main__":
    database = None

    if os.path.exists(CARTELLA_DB):
        scelta = input("Esiste gia un archivio. Vuoi riusarlo senza ricaricare l'URL? (s/n): ").strip().lower()
        if scelta == "s":
            database = apri_database_esistente()

    if database is None:
        url = input("Incolla l'URL da analizzare: ").strip()
        database = prepara_database(url)

    print("\nPronto! Fai le tue domande.")

    while True:
        domanda = input("\nDomanda (premi Invio senza scrivere per uscire): ").strip()
        if not domanda:
            break

        print("Sto pensando...")
        risposta, fonti = rispondi(domanda, database)

        print("\nRISPOSTA:")
        print(risposta)
        print("\nFonti:", ", ".join(fonti))