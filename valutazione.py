import os
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

from chat import rispondi_in_chat
from crea_database import CARTELLA_DB
from domande_risposte import MODELLO_CHAT, PROMPT, apri_database_esistente, prepara_database

URL_TEST = "https://it.wikipedia.org/wiki/Intelligenza_artificiale"
FRASE_RIFIUTO = "non trovo questa informazione"
K_PEZZI = 6  # quanti pezzi consegnare al modello (nelle prove precedenti: 4)

# Le domande di prova.
# "attese": parole che la risposta giusta deve contenere.
# "rifiuto": True se la pagina NON contiene la risposta e il programma deve rifiutarsi.
TEST = [
    {"domanda": "Chi erano McCulloch e Pitts?", "attese": ["1943"], "rifiuto": False},
    {"domanda": "Chi ha proposto il test di Turing e in che anno?", "attese": ["Turing", "1950"], "rifiuto": False},
    {"domanda": "Quando si è tenuta la conferenza di Dartmouth?", "attese": ["1956"], "rifiuto": False},
    {"domanda": "Che cos'è il test di Turing?", "attese": ["intelligente"], "rifiuto": False},
    # --- AGGIUNGI QUI LE TUE 4 DOMANDE, nello stesso formato ---
    # {"domanda": "...", "attese": ["..."], "rifiuto": False},
    {"domanda": "Chi ha vinto i mondiali di calcio del 2018?", "attese": [], "rifiuto": True},
    {"domanda": "Qual è la capitale della Francia?", "attese": [], "rifiuto": True},
]

# La conversazione di prova: la memoria deve capire "lo" e "In che anno?"
CONVERSAZIONE = [
    "Che cos'è il test di Turing?",
    "Chi lo ha inventato?",
    "In che anno?",
]
ATTESA_CONVERSAZIONE = ["1950"]


def valuta_domanda(prova, database):
    """Cerca i pezzi, fa rispondere il modello e controlla il risultato."""
    cercatore = database.as_retriever(search_type="similarity", search_kwargs={"k": K_PEZZI})
    trovati = cercatore.invoke(prova["domanda"])
    contesto = "\n\n".join(pezzo.page_content for pezzo in trovati)

    modello = ChatOllama(model=MODELLO_CHAT, temperature=0)
    risposta = (PROMPT | modello | StrOutputParser()).invoke(
        {"contesto": contesto, "domanda": prova["domanda"]}
    )

    contesto_min = contesto.lower()
    risposta_min = risposta.lower()

    if prova["rifiuto"]:
        recupero = None  # per queste domande la ricerca non c'entra
        corretta = FRASE_RIFIUTO in risposta_min
    else:
        recupero = all(parola.lower() in contesto_min for parola in prova["attese"])
        corretta = all(parola.lower() in risposta_min for parola in prova["attese"])

    return recupero, corretta, risposta


def valuta_conversazione(database):
    """Prova la chat con memoria e controlla se le domande vengono riscritte bene."""
    storico = []
    riscritture_buone = 0
    riscritture_totali = 0
    risposta = ""

    for numero, domanda in enumerate(CONVERSAZIONE):
        risposta, domanda_completa, _ = rispondi_in_chat(domanda, database, storico)
        if numero > 0:
            riscritture_totali += 1
            argomenti = ["turing", "computing machinery"]
            if domanda_completa.strip().endswith("?") and any(a in domanda_completa.lower() for a in argomenti):
                riscritture_buone += 1
            print(f'   "{domanda}" -> riscritta come: {domanda_completa}')
        storico.append(HumanMessage(content=domanda))
        storico.append(AIMessage(content=risposta))

    corretta = all(parola.lower() in risposta.lower() for parola in ATTESA_CONVERSAZIONE)
    return corretta, riscritture_buone, riscritture_totali


if __name__ == "__main__":
    # 1. Prepariamo l'archivio
    if os.path.exists(CARTELLA_DB):
        scelta = input("Esiste gia un archivio. Riusarlo? (s/n): ").strip().lower()
        database = apri_database_esistente() if scelta == "s" else prepara_database(URL_TEST)
    else:
        database = prepara_database(URL_TEST)

    etichetta = input("Nome di questa prova (es. base, bge-m3, nuovo-prompt): ").strip() or "senza nome"

    # 2. Domande singole
    print("\n=== DOMANDE SINGOLE ===")
    recuperi_ok = recuperi_tot = risposte_ok = 0
    for prova in TEST:
        recupero, corretta, risposta = valuta_domanda(prova, database)

        if recupero is not None:
            recuperi_tot += 1
            recuperi_ok += int(recupero)
        risposte_ok += int(corretta)

        stato = "OK" if corretta else "NO"
        testo_recupero = "-" if recupero is None else ("si" if recupero else "no")
        print(f"[{stato}] {prova['domanda']}  (pezzo giusto trovato: {testo_recupero})")
        if not corretta:
            print("     Risposta data:", risposta.replace("\n", " ")[:300])

    # 3. Conversazione con memoria
    print("\n=== CONVERSAZIONE CON MEMORIA ===")
    conv_ok, buone, totali = valuta_conversazione(database)
    print(f"[{'OK' if conv_ok else 'NO'}] Risposta finale contiene {ATTESA_CONVERSAZIONE}")
    print(f"Domande riscritte correttamente (finiscono con '?'): {buone}/{totali}")

    # 4. Riepilogo
    riepilogo = (
        f"{datetime.now():%Y-%m-%d %H:%M} | {etichetta} | "
        f"pezzo giusto trovato: {recuperi_ok}/{recuperi_tot} | "
        f"risposte corrette: {risposte_ok}/{len(TEST)} | "
        f"riscritture buone: {buone}/{totali} | "
        f"modello chat: {MODELLO_CHAT}"
    )
    print("\n=== RIEPILOGO ===")
    print(riepilogo)

    with open("storico_valutazioni.txt", "a", encoding="utf-8") as file:
        file.write(riepilogo + "\n")
    print("Risultato aggiunto a storico_valutazioni.txt")