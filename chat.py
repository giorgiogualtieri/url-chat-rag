import os

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from crea_database import CARTELLA_DB
from domande_risposte import MODELLO_CHAT, apri_database_esistente, prepara_database

# Quanti messaggi dello storico ricordiamo (6 = 3 domande + 3 risposte)
MESSAGGI_RICORDATI = 6

# Primo foglio di istruzioni: serve a riscrivere la domanda in modo completo
PROMPT_RIFORMULA = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Ti viene data una conversazione e una nuova domanda dell'utente. "
            "Riscrivi la nuova domanda in modo che si capisca da sola, senza bisogno "
            "della conversazione: sostituisci pronomi e riferimenti come 'lui', 'quello', "
            "'allora' con i nomi precisi. NON rispondere alla domanda. "
            "Se la domanda si capisce gia da sola, riscrivila identica. "
            "Scrivi solo la domanda riscritta, nient'altro.",
        ),
        MessagesPlaceholder("storico"),
        ("human", "{domanda}"),
    ]
)

# Secondo foglio di istruzioni: serve a scrivere la risposta
PROMPT_RISPOSTA = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Sei un assistente che risponde in italiano, in modo chiaro e preciso. "
            "Usa SOLO le informazioni presenti nel contesto. "
            "Se la domanda chiede una definizione, riporta la definizione solo se il contesto "
            "la da esplicitamente. Se il contesto parla soltanto di un tipo particolare, "
            "di un caso o di un esempio dell'argomento, dillo chiaramente, senza presentarlo "
            "come definizione generale. Se nel contesto non c'e nulla che riguardi la domanda, "
            "scrivi: Non trovo questa informazione nella pagina. "
            "Non inventare e non usare conoscenze esterne.\n\n"
            "Contesto:\n{contesto}",
        ),
        MessagesPlaceholder("storico"),
        ("human", "{domanda}"),
    ]
)


def rispondi_in_chat(domanda, database, storico):
    """Riscrive la domanda, cerca i pezzi giusti e scrive la risposta."""
    modello = ChatOllama(model=MODELLO_CHAT, temperature=0)
    ultimi_messaggi = storico[-MESSAGGI_RICORDATI:]

    # 1. RISCRIVI la domanda (solo se c'e gia una conversazione)
    if ultimi_messaggi:
        riscrittura = PROMPT_RIFORMULA | modello | StrOutputParser()
        domanda_completa = riscrittura.invoke(
            {"storico": ultimi_messaggi, "domanda": domanda}
        ).strip()
    else:
        domanda_completa = domanda

    # 2. CERCA i pezzi usando la domanda completa
    cercatore = database.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    trovati = cercatore.invoke(domanda_completa)
    contesto = "\n\n".join(pezzo.page_content for pezzo in trovati)

    # 3. RISPONDI, con lo storico a disposizione
    risposta_catena = PROMPT_RISPOSTA | modello | StrOutputParser()
    risposta = risposta_catena.invoke(
        {"storico": ultimi_messaggi, "contesto": contesto, "domanda": domanda}
    )

    fonti = sorted({pezzo.metadata.get("source", "sconosciuta") for pezzo in trovati})
    return risposta, domanda_completa, fonti


if __name__ == "__main__":
    database = None

    if os.path.exists(CARTELLA_DB):
        scelta = input("Esiste gia un archivio. Vuoi riusarlo senza ricaricare l'URL? (s/n): ").strip().lower()
        if scelta == "s":
            database = apri_database_esistente()

    if database is None:
        url = input("Incolla l'URL da analizzare: ").strip()
        database = prepara_database(url)

    storico = []

    print("\nPronto! Fai le tue domande.")
    print("Scrivi 'nuova' per far dimenticare la conversazione, oppure premi Invio senza scrivere per uscire.")

    while True:
        domanda = input("\nTu: ").strip()
        if not domanda:
            break

        if domanda.lower() == "nuova":
            storico = []
            print("Conversazione azzerata.")
            continue

        print("Sto pensando...")
        risposta, domanda_completa, fonti = rispondi_in_chat(domanda, database, storico)

        print("\n[Domanda capita come]:", domanda_completa)
        print("\nAssistente:", risposta)
        print("\nFonti:", ", ".join(fonti))

        # Aggiungiamo lo scambio alla memoria
        storico.append(HumanMessage(content=domanda))
        storico.append(AIMessage(content=risposta))