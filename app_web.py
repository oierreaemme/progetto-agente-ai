import google.generativeai as genai
import os
from tavily import TavilyClient
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

load_dotenv() 

# --- Le nostre funzioni "Tool" (Restano identiche) ---
def addizione(numero1: int, numero2: int):
    """Usa questa funzione per sommare due numeri."""
    print(f"\n[DEBUG: Tool CALCOLATRICE: {numero1} + {numero2}]\n")
    return numero1 + numero2

def ricerca_web(query: str):
    """Usa questa funzione per cercare sul web informazioni in tempo reale."""
    print(f"\n[DEBUG: Tool RICERCA WEB: '{query}']\n")
    try:
        api_key = os.environ.get("TAVILY_API_KEY")
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=3, search_depth="advanced")
        context = "Risultati della ricerca:\n"
        for result in response['results']:
            context += f"- {result['title']}: {result['content']}\n"
        return context
    except Exception as e:
        print(f"[ERRORE Ricerca Web]: {e}")
        return f"Errore during la ricerca: {e}"

# --- INIZIO APP STREAMLIT ---

st.set_page_config(page_title="Agente AI Autonomo", page_icon="🤖")

# --- NOVITÀ: Logica di Autenticazione Avanzata ---

# 1. Inizializziamo lo stato di autenticazione nello "zainetto"
if "autenticato" not in st.session_state:
    st.session_state.autenticato = False  # L'utente non è ancora loggato

# 2. Leggiamo la password dalla "cassaforte"
PASSWORD_CORRETTA = os.environ.get("APP_PASSWORD")

# 3. Controlliamo se l'utente è loggato
if st.session_state.autenticato == False:
    # Se NON è loggato, mostriamo il "buttafuori"
    
    st.title("🤖 Agente AI Autonomo")
    st.caption("Accesso Protetto")
    
    password_inserita = st.text_input("Inserisci la password per accedere:", type="password")
    
    if password_inserita == PASSWORD_CORRETTA:
        # Password corretta!
        st.session_state.autenticato = True  # Metti il "pass" nello zainetto
        st.rerun()  # Forza un riavvio immediato della pagina
    
    elif password_inserita: # Se ha scritto qualcosa, ma è sbagliato
        st.error("Password errata. Riprova.")
        
    st.stop() # FERMA TUTTO! Non eseguire il resto dell'app.

# --- SE IL CODICE ARRIVA QUI, SIGNIFICA CHE st.session_state.autenticato È True ---
# L'utente è loggato. Il form di login è stato saltato.

st.title("🤖 Agente AI Autonomo")
st.caption("Costruito con Gemini, Tavily e Streamlit")

# --- Logica dell'Istruzione di Sistema (identica) ---
data_di_oggi = datetime.now().strftime("%d %B %Y, ore %H:%M")
ISTRUZIONE_DI_SISTEMA = f"""
Sei un assistente AI esperto... (IL TUO LUNGO PROMPT DI ISTRUZIONI)
...La data e l'ora attuali sono: **{data_di_oggi}**.
...ESEMPI DI COME DEVI COMPORTARTI...
""" # (Ho abbreviato per leggibilità, tu lascia il tuo prompt intero)

# --- Inizializzazione della Chat (identica) ---
if "chat" not in st.session_state:
    print("Inizializzo un nuovo modello e chat...")
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    genai.configure(api_key=google_api_key)
    
    model = genai.GenerativeModel(
        'gemini-flash-lite-latest',
        tools=[addizione, ricerca_web],
        system_instruction=ISTRUZIONE_DI_SISTEMA
    )
    st.session_state.chat = model.start_chat(
        enable_automatic_function_calling=True
    )
    st.session_state.messages = []

# --- Mostra Cronologia Chat (identica) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- Gestione Nuovo Input (identica) ---
if prompt := st.chat_input("Chiedimi qualcosa..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.spinner("L'agente sta pensando..."):
        response = st.session_state.chat.send_message(prompt)

    response_text = response.text
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.write(response_text)
