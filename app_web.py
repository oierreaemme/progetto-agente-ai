import google.generativeai as genai
import os
from tavily import TavilyClient
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# --- Le tue funzioni "Tool" (rimangono invariate) ---
def addizione(numero1: int, numero2: int):
    print(f"\n[DEBUG: Tool CALCOLATRICE: {numero1} + {numero2}]\n")
    return numero1 + numero2

def ricerca_web(query: str):
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
        return f"Errore durante la ricerca: {e}"

# --- INIZIO APP STREAMLIT ---

st.set_page_config(page_title="Agente AI Autonomo", page_icon="🤖")
st.title("🤖 Agente AI Autonomo")
st.caption("Costruito con Gemini, Tavily e Streamlit")

# --- NUOVO BLOCCO PASSWORD CON GESTIONE DELLO STATO ---

# 1. Inizializza lo stato di autenticazione nello "zainetto" se non esiste
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 2. Se l'utente non è autenticato, mostra la schermata di login
if not st.session_state.authenticated:
    
    # Prova a prendere la password dai secrets, altrimenti usa un default per test locali
    try:
        PASSWORD_CORRETTA = st.secrets["APP_PASSWORD"]
    except:
        print("ATTENZIONE: Password non trovata nei secrets di Streamlit. Uso 'atlas-123' come fallback.")
        PASSWORD_CORRETTA = "atlas-123"

    password_inserita = st.text_input("Inserisci la password per accedere:", type="password")

    if password_inserita: # Controlla solo se l'utente ha scritto qualcosa
        if password_inserita == PASSWORD_CORRETTA:
            # Se la password è corretta, aggiorna lo "zainetto" e RIESEGUI lo script
            st.session_state.authenticated = True
            st.rerun() # Forza un "rerun" immediato
        else:
            st.error("Password errata. Riprova.")
            
# 3. Altrimenti (se l'utente È autenticato), esegui l'applicazione principale
else:
    st.success("Accesso consentito!")
    
    # --- TUTTO IL RESTO DEL CODICE ORA VA QUI DENTRO ---

    # --- Blocco Caricamento File (ORA È NEL POSTO GIUSTO E NON DUPLICATO) ---
    uploaded_file = st.file_uploader(
        "1. Carica il tuo file audio (.wav, .mp3, .flac)", 
        type=['wav', 'mp3', 'flac']
    )

    if uploaded_file is not None:
        temp_dir = "temp_uploads"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.file_path = file_path
        
        st.success(f"File '{uploaded_file.name}' caricato con successo!")
        st.audio(file_path)
    
    # --- Istruzione di Sistema e Chat (ORA SONO NEL POSTO GIUSTO) ---
    data_di_oggi = datetime.now().strftime("%d %B %Y, ore %H:%M")
    
    ISTRUZIONE_DI_SISTEMA = f"""
    Sei un assistente AI esperto... 
    (Il tuo testo dell'istruzione di sistema rimane identico qui)
    """

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

    # Mostra la Cronologia Chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Gestione del Nuovo Input
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
