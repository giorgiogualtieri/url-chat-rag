# URL Chat RAG

Chat con una pagina web: incolli un indirizzo (URL), il programma legge la pagina e puoi farle domande sul contenuto. Funziona interamente sul proprio computer con Ollama, quindi senza costi e senza chiavi API. Ha un'interfaccia web (Streamlit) e una versione da terminale.

## Come funziona

1. **Caricamento:** `WebBaseLoader` scarica la pagina e ne estrae il testo.
2. **Divisione:** il testo viene pulito e tagliato in chunk da 1000 caratteri con 150 di sovrapposizione.
3. **Embedding e archivio:** ogni chunk diventa un vettore (`nomic-embed-text`) e viene salvato in Chroma.
4. **Ricerca:** per ogni domanda si recuperano i 4 chunk più vicini.
5. **Risposta:** `llama3.2` risponde usando solo quei chunk e indica la fonte.
6. **Memoria:** la chat ricorda gli ultimi 3 scambi. Prima di cercare, il modello prova a riscrivere le domande incomplete (per esempio "In che anno?") in domande autonome (vedi i limiti noti).

## Requisiti

- macOS (testato su MacBook Air M1)
- Python 3.12
- [Ollama](https://ollama.com) installato e acceso

## Installazione

```bash
git clone https://github.com/giorgiogualtieri/url-chat-rag.git
cd url-chat-rag
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull nomic-embed-text
ollama pull llama3.2
```

## Uso

**Interfaccia web (consigliata):**

```bash
python -m streamlit run app.py
```

Si apre una pagina nel browser: incolla un URL nella barra laterale, clicca "Carica e analizza" e poi fai le tue domande. Il primo avvio può richiedere un po' di tempo, e anche la preparazione di una pagina richiede uno o due minuti perché gli embedding vengono calcolati in locale. Nell'interfaccia l'archivio è tenuto in memoria e va ricreato a ogni avvio.

**Da terminale:**

```bash
python chat.py
```

Scrivi `nuova` per azzerare la conversazione, oppure premi Invio senza scrivere per uscire. `python domande_risposte.py` è la versione senza memoria: ogni domanda è indipendente.

## Struttura del progetto

| File | Cosa fa |
|---|---|
| `app.py` | Interfaccia web con Streamlit |
| `chat.py` | Chat con memoria della conversazione (terminale) |
| `domande_risposte.py` | Domande e risposte singole, senza memoria |
| `carica_url.py` | Scarica il testo di una pagina web |
| `dividi_testo.py` | Pulisce il testo e lo divide in chunk |
| `crea_database.py` | Crea gli embedding e l'archivio Chroma |
| `esperimento_embedding.py` | Esperimento che mostra la somiglianza tra frasi |
| `diagnosi.py` | Strumento per ispezionare i chunk trovati dalla ricerca |

## Scelte fatte e prove effettuate

Il progetto è stato provato sulla pagina italiana di Wikipedia sull'intelligenza artificiale.

- **Ricerca semplice invece di MMR:** nei miei test l'MMR scartava un chunk pertinente a favore di chunk estranei, quindi uso la ricerca per similarità.
- **Pulizia del testo:** ho rimosso le righe di rimando di Wikipedia ("Lo stesso argomento in dettaglio: ...") e scartato i chunk sotto i 100 caratteri, perché occupavano posti nei risultati senza contenere informazioni.
- **Prompt prudente:** il modello deve rispondere "Non trovo questa informazione nella pagina." se il contesto non contiene la risposta.

| Domanda | Esito |
|---|---|
| Che cos'è il test di Turing? | Risposta fedele alla pagina ma incompleta (manca il criterio di intelligenza); nella versione con memoria la prima risposta è risultata più confusa |
| Quando si è tenuta la conferenza di Dartmouth? | Corretta (1956) |
| Chi ha vinto i mondiali di calcio del 2018? | Corretto rifiuto: l'informazione non è nella pagina |
| Che cos'è l'apprendimento automatico? | **Errata:** ha presentato l'apprendimento per rinforzo come definizione generale |
| Conversazione: "Che cos'è il test di Turing?" → "Chi lo ha inventato?" → "In che anno?" | Risposte finali corrette (Alan Turing, 1950), ma la riscrittura della domanda ha prodotto risposte invece di domande |

## Limiti noti

- **Riscrittura delle domande poco affidabile:** nei test il modello a volte risponde invece di riscrivere (per esempio ha prodotto "1950" al posto di una domanda completa). Le risposte finali sono comunque corrette perché la conversazione precedente contiene già le informazioni, ma la ricerca non beneficia davvero della riscrittura.
- Un modello piccolo e locale (`llama3.2`) è meno affidabile dei modelli grandi: può riassumere tagliando parti importanti o confondere categorie e sottocategorie.
- Sulle domande ampie e concettuali la qualità è più bassa che su quelle precise (date, nomi, concetti ben delimitati).
- La ricerca per significato funziona meno bene se la domanda usa un termine diverso da quello della pagina (per esempio "machine learning" invece di "apprendimento automatico").
- La pulizia del testo è pensata per Wikipedia: su altri siti andrà adattata.
- Le pagine che mostrano il contenuto solo dopo l'esecuzione di codice nel browser non vengono lette correttamente.
- Nell'interfaccia web l'archivio non viene salvato su disco.

## Possibili miglioramenti

- Rendere affidabile la riscrittura delle domande (istruzioni con esempi, oppure un modello più grande).
- Costruire un piccolo insieme di domande di test con risposte attese, per misurare la qualità a ogni modifica.
- Provare un modello di embedding multilingue (`bge-m3`) e un modello di chat più grande.
- Rendere la pulizia del testo configurabile per sito.
- Salvare gli archivi su disco anche nell'interfaccia web.