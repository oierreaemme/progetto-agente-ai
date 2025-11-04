import google.generativeai as genai
import os
from tavily import TavilyClient  # <-- NOVITÀ: Importiamo il "telefono" di Tavily

# --- STRUMENTO 1: CALCOLATRICE ---
def addizione(numero1: int, numero2: int):
    """
    Usa questa funzione per sommare due numeri.
    """
    print(f"\n[DEBUG: Sto usando lo Strumento CALCOLATRICE per {numero1} + {numero2}]\n")
    return numero1 + numero2

# --- STRUMENTO 2: RICERCA WEB ---
def ricerca_web(query: str):
    """
    Usa questa funzione per cercare sul web informazioni in tempo reale
    o notizie recenti.
    """
    print(f"\n[DEBUG: Sto usando lo Strumento RICERCA WEB per '{query}']\n")
    try:
        # 1. Prendiamo la chiave dal nostro "post-it"
        api_key = os.environ.get("TAVILY_API_KEY")
        
        # 2. Creiamo il "client" (il telefono)
        client = TavilyClient(api_key=api_key)
        
        # 3. Facciamo la ricerca, chiedendo max 3 risultati
        response = client.search(query=query, max_results=3, search_depth="advanced")
        
        # 4. Formattiamo i risultati in un testo pulito
        context = "Risultati della ricerca:\n"
        for result in response['results']:
            context += f"- {result['title']}: {result['content']}\n"
        
        return context  # 5. Restituiamo il testo a Gemini
        
    except Exception as e:
        # Se qualcosa va storto (es. chiave API sbagliata)
        print(f"[ERRORE Ricerca Web]: {e}")
        return "Errore durante la ricerca web."

# --- Configurazione GEMINI (resta uguale) ---
google_api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)
# -----------------------------------

# --- Creazione del modello (CON ENTRAMBI GLI STRUMENTI) ---
model = genai.GenerativeModel(
    'gemini-flash-lite-latest',  # Il nostro motore "go-kart"
    tools=[addizione, ricerca_web]  # <-- NOVITÀ: Ora ha DUE strumenti!
)

# --- Avvio della Chat (resta uguale) ---
chat = model.start_chat(
    enable_automatic_function_calling=True
)

print("--- Agente Gemini Attivo (con Calcolatrice E Ricerca Web) ---")
print("Chiedimi un'addizione o informazioni sul mondo reale!")
print("Scrivi 'esci' per terminare.")

# --- Loop della Chat (resta uguale) ---
while True:
    prompt = input("Tu: ") 

    if prompt.lower() == 'esci':
        print("--- Conversazione Terminata ---")
        break
    
    response = chat.send_message(prompt)
    
    print(f"Gemini: {response.text}")