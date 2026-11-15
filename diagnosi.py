from domande_risposte import apri_database_esistente

database = apri_database_esistente()
print("Chunk nell'archivio:", len(database.get()["ids"]))

domanda = input("Domanda: ").strip()

print("\n===== RICERCA SEMPLICE: i 4 pezzi piu vicini =====")
risultati = database.similarity_search_with_score(domanda, k=4)
for numero, (pezzo, distanza) in enumerate(risultati, start=1):
    print(f"\n--- Pezzo {numero} (distanza: {distanza:.3f}) ---")
    print(pezzo.page_content[:300])

print("\n===== RICERCA MMR: 4 pezzi variati =====")
cercatore = database.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 12},
)
for numero, pezzo in enumerate(cercatore.invoke(domanda), start=1):
    print(f"\n--- Pezzo {numero} ---")
    print(pezzo.page_content[:300])