import time

import streamlit as st
from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage

from carica_url import carica_url
from chat import rispondi_in_chat
from crea_database import crea_embedding
from dividi_testo import dividi_documenti

st.set_page_config(page_title="URL Chat RAG", page_icon="💬")
st.title("Chat con una pagina web")

# L'"armadietto" dell'app: ciò che deve restare tra un click e l'altro
if "database" not in st.session_state:
    st.session_state.database = None   # l'archivio dei chunk
    st.session_state.url = ""          # la pagina attiva
    st.session_state.storico = []      # la memoria per il modello
    st.session_state.messaggi = []     # i messaggi mostrati a schermo

# ---------- BARRA LATERALE: caricamento della pagina ----------
with st.sidebar:
    st.header("1. Carica una pagina")
    url = st.text_input("Indirizzo (URL)", placeholder="https://...")

    if st.button("Carica e analizza"):
        if not url.strip():
            st.warning("Scrivi prima un URL.")
        else:
            try:
                with st.spinner("Leggo la pagina e creo l'archivio... (puo richiedere uno o due minuti)"):
                    documenti = carica_url(url.strip())
                    chunk = dividi_documenti(documenti)
                    # Nome unico per ogni pagina, cosi i chunk di pagine diverse non si mescolano
                    st.session_state.database = Chroma.from_documents(
                        documents=chunk,
                        embedding=crea_embedding(),
                        collection_name=f"pagina_{int(time.time())}",
                    )
                st.session_state.url = url.strip()
                st.session_state.storico = []
                st.session_state.messaggi = []
                st.success(f"Pagina caricata: {len(chunk)} chunk.")
            except Exception as errore:
                st.error(f"Non sono riuscito a caricare la pagina: {errore}")

    if st.session_state.database is not None:
        st.caption(f"Pagina attiva: {st.session_state.url}")
        if st.button("Azzera la conversazione"):
            st.session_state.storico = []
            st.session_state.messaggi = []
            st.rerun()

# ---------- AREA PRINCIPALE: la chat ----------
st.header("2. Fai le tue domande")

if st.session_state.database is None:
    st.info("Carica una pagina dalla barra a sinistra per iniziare.")
else:
    # Ridisegniamo la conversazione fatta finora
    for messaggio in st.session_state.messaggi:
        with st.chat_message(messaggio["ruolo"]):
            st.write(messaggio["testo"])
            if "dettagli" in messaggio:
                st.caption(messaggio["dettagli"])

    domanda = st.chat_input("Scrivi una domanda sulla pagina")

    if domanda:
        with st.chat_message("user"):
            st.write(domanda)

        with st.chat_message("assistant"):
            with st.spinner("Sto pensando..."):
                risposta, domanda_completa, fonti = rispondi_in_chat(
                    domanda, st.session_state.database, st.session_state.storico
                )
            dettagli = f"Domanda capita come: {domanda_completa} | Fonti: {', '.join(fonti)}"
            st.write(risposta)
            st.caption(dettagli)

        # Salviamo lo scambio, sia per lo schermo sia per la memoria del modello
        st.session_state.messaggi.append({"ruolo": "user", "testo": domanda})
        st.session_state.messaggi.append(
            {"ruolo": "assistant", "testo": risposta, "dettagli": dettagli}
        )
        st.session_state.storico.append(HumanMessage(content=domanda))
        st.session_state.storico.append(AIMessage(content=risposta))