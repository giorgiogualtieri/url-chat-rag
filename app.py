import time

import streamlit as st
from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage

from carica_url import carica_url
from chat import rispondi_in_chat
from crea_database import crea_embedding
from dividi_testo import dividi_documenti
from stile import applica_stile

# Il nome del progetto compare nella scheda del browser
st.set_page_config(page_title="LinkTelex")
applica_stile()

st.markdown(
    '<div class="testata"><h1>LinkTelex</h1><p>Parla con una pagina web</p></div>',
    unsafe_allow_html=True,
)

# L'"armadietto" dell'app: ciò che deve restare tra un click e l'altro
if "database" not in st.session_state:
    st.session_state.database = None   # l'archivio dei chunk
    st.session_state.url = ""          # la pagina attiva
    st.session_state.storico = []      # la memoria per il modello
    st.session_state.messaggi = []     # i messaggi mostrati a schermo


def mostra_messaggio(ruolo, testo, dettagli=None):
    """Disegna un messaggio con la sua etichetta (Tu / LinkTelex)."""
    nome = "Tu" if ruolo == "user" else "LinkTelex"
    with st.chat_message(ruolo):
        st.markdown(f'<span class="etichetta">{nome}</span>', unsafe_allow_html=True)
        st.write(testo)
        if dettagli:
            st.caption(dettagli)


# ---------- BARRA LATERALE: caricamento della pagina ----------
with st.sidebar:
    st.header("1. Inserisci il link")
    url = st.text_input("Indirizzo (URL)", placeholder="https://...")

    if st.button("Carica e analizza", type="primary"):
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
        if st.button("Azzera la conversazione", type="secondary"):
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
        mostra_messaggio(messaggio["ruolo"], messaggio["testo"], messaggio.get("dettagli"))

    domanda = st.chat_input("Scrivi una domanda sulla pagina")

    if domanda:
        mostra_messaggio("user", domanda)

        with st.chat_message("assistant"):
            st.markdown('<span class="etichetta">LinkTelex</span>', unsafe_allow_html=True)
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