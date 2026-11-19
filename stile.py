import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400&family=Special+Elite&display=swap');

/* ---- Testo del corpo: Courier Prime ---- */
.stApp, .stApp p, .stApp label, .stApp li, .stApp a,
.stApp input, .stApp textarea, .stApp button {
    font-family: 'Courier Prime', 'Courier New', monospace !important;
    color: #2B2927;
}

/* ---- Titoli e intestazioni: Special Elite ---- */
.stApp h1, .stApp h2, .stApp h3, .stApp .etichetta {
    font-family: 'Special Elite', 'Courier New', monospace !important;
    font-weight: 400 !important;
    color: #2B2927 !important;
}

/* ---- Struttura della pagina ---- */
.block-container { max-width: 900px; padding-top: 5rem; }
[data-testid="stHeader"] { background: #DCD5C7; border-bottom: 4px double #2B2927; }
[data-testid="stSidebar"] { border-right: 1px solid #2B2927; }

/* ---- Testata con il nome del progetto ---- */
.stApp .testata { border-bottom: 4px double #2B2927; padding-bottom: 0.8rem; margin-bottom: 1.5rem; }
.stApp .testata h1 { font-size: 2.8rem !important; letter-spacing: 3px; margin: 0; padding: 0; line-height: 1.2; }
.stApp .testata p { font-style: italic; margin: 0.3rem 0 0 0; font-size: 1.05rem; }

/* ---- Pulsanti: inchiostro su carta, angoli squadrati ---- */
.stButton > button { border-radius: 0 !important; border: 1px solid #2B2927 !important; font-weight: 700 !important; }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: #2B2927 !important; color: #F4F1EA !important;
}
.stButton > button[kind="primary"] p, .stButton > button[data-testid="stBaseButton-primary"] p { color: #F4F1EA !important; }
.stButton > button[kind="secondary"], .stButton > button[data-testid="stBaseButton-secondary"] {
    background: transparent !important; color: #2B2927 !important;
}
.stButton > button:hover { background: #DCD5C7 !important; color: #2B2927 !important; }
.stButton > button:hover p { color: #2B2927 !important; }

/* ---- Casella dell'URL nella sidebar ---- */
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"] {
    background: #F4F1EA !important; border-radius: 0 !important;
}
[data-testid="stTextInput"] [data-baseweb="input"] { border: 1px solid #2B2927 !important; }
[data-testid="stTextInput"] input { background: #F4F1EA !important; color: #2B2927 !important; }

/* ---- Messaggi della chat ---- */
[data-testid="stChatMessage"] {
    background: transparent; border: 1px solid #2B2927; border-radius: 0;
    padding: 0.9rem 1.1rem; margin-bottom: 1rem;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: #DCD5C7; }
[data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none; }
.stApp .etichetta { font-size: 1rem; letter-spacing: 1px; display: block; margin-bottom: 0.3rem; }

/* ---- Fonti e dettagli sotto le risposte ---- */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    font-style: italic; color: #2B2927 !important; opacity: 1 !important;
}

/* ---- Barra di input in basso ---- */
[data-testid="stBottom"], [data-testid="stBottom"] > div { background: #DCD5C7 !important; }
[data-testid="stBottom"] { border-top: 4px double #2B2927; }
[data-testid="stChatInput"] {
    background: #DCD5C7 !important; border: 1px solid #2B2927 !important; border-radius: 0 !important;
}
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"] { background: transparent !important; border-radius: 0 !important; }
[data-testid="stChatInput"] textarea { background: transparent !important; color: #2B2927 !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #2B2927 !important; opacity: 0.72; }

/* ---- Avvisi (verde, rosso...) nei colori della palette ---- */
[data-testid="stAlert"] {
    background: #F4F1EA !important; border: 1px solid #2B2927; border-radius: 0 !important;
}
[data-testid="stAlert"] p { color: #2B2927 !important; }
</style>
"""


def applica_stile():
    """Inietta nella pagina i font e i colori del tema LinkTelex."""
    st.markdown(CSS, unsafe_allow_html=True)