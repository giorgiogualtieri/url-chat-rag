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
            "Il tuo unico compito e riscrivere l'ultima domanda dell'utente in modo che si capisca da sola, "
            "usando la conversazione per sostituire riferimenti come 'lo', 'quello', 'allora' "
            "o domande troncate come 'In che anno?'. "
            "NON rispondere alla domanda. Scrivi SOLO una domanda, che finisce con un punto interrogativo.\n\n"
            "Esempio 1\n"
            "Domanda precedente: Che cos'e il test di Turing?\n"
            "Ultima domanda: Chi lo ha inventato?\n"
            "Domanda riscritta: Chi ha inventato il test di Turing?\n\n"
            "Esempio 2\n"
            "Domanda precedente: Quando si e tenuta la conferenza di Dartmouth?\n"
            "Ultima domanda: E dove?\n"
            "Domanda riscritta: Dove si e tenuta la conferenza di Dartmouth?\n\n"
            "Esempio 3\n"
            "Domanda precedente: Chi erano McCulloch e Pitts?\n"
            "Ultima domanda: Che cos'e l'apprendimento automatico?\n"
            "Domanda riscritta: Che cos'e l'apprendimento automatico?",
        ),
        MessagesPlaceholder("storico"),
        ("human", "Ultima domanda: {domanda}\nDomanda riscritta:"),
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
        ).replace("Domanda riscritta:", "").strip()

        # Rete di sicurezza: una domanda vera finisce con "?" ed e breve.
        # Se il modello ha risposto invece di riscrivere, usiamo il piano B:
        # l'ultima domanda dell'utente seguita da quella nuova.
        if not domanda_completa.endswith("?") or len(domanda_completa) > 200:
            ultima_domanda_utente = ultimi_messaggi[-2].content
            domanda_completa = f"{ultima_domanda_utente} {domanda}"
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