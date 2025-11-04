import google.generativeai as genai
import os
from tavily import TavilyClient
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime  # <-- NOVITÀ: Importiamo la libreria per la data

load_dotenv() 

# --- Le nostre funzioni "Tool" (Restano identiche) ---
def addizione(numero1: int, numero2: int):
    # ... (codice identico a prima)
    print(f"\n[DEBUG: Tool CALCOLATRICE: {numero1} + {numero2}]\n")
    return numero1 + numero2

def ricerca_web(query: str):
    # ... (codice identico a prima)
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
st.title("🤖 Agente AI Autonomo")
st.caption("Costruito con Gemini, Tavily e Streamlit")

# --- Blocco Password (Resta identico) ---
PASSWORD_CORRETTA = os.environ.get("APP_PASSWORD") 
password_inserita = st.text_input("Inserisci la password per accedere:", type="password")

if password_inserita == PASSWORD_CORRETTA:
    
    st.success("Accesso consentito!") 

    # --- Blocco Caricamento File ---
uploaded_file = st.file_uploader(
    "1. Carica il tuo file audio (.wav, .mp3, .flac)", 
    type=['wav', 'mp3', 'flac']
)

if uploaded_file is not None:
    # Se un file è stato caricato, lo salviamo in una cartella temporanea
    
    # Creiamo una cartella 'temp_uploads' se non esiste
    temp_dir = "temp_uploads"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    # Creiamo il percorso completo del file
    file_path = os.path.join(temp_dir, uploaded_file.name)
    
    # Scriviamo i "byte" del file caricato in un nuovo file sul nostro server
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    # Memorizziamo il percorso del file nello "zainetto" della sessione
    st.session_state.file_path = file_path
    
    st.success(f"File '{uploaded_file.name}' caricato con successo!")
    st.audio(file_path) # Mostriamo un bel player audio per conferma
# --- Fine Blocco Caricamento File ---
    
    # --- Blocco Caricamento File ---
    uploaded_file = st.file_uploader(
        "1. Carica il tuo file audio (.wav, .mp3, .flac)", 
        type=['wav', 'mp3', 'flac']
    )

    if uploaded_file is not None:
        # Se un file è stato caricato, lo salviamo in una cartella temporanea
        
        # Creiamo una cartella 'temp_uploads' se non esiste
        temp_dir = "temp_uploads"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # Creiamo il percorso completo del file
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Scriviamo i "byte" del file caricato in un nuovo file sul nostro server
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Memorizziamo il percorso del file nello "zainetto" della sessione
        st.session_state.file_path = file_path
        
        st.success(f"File '{uploaded_file.name}' caricato con successo!")
        st.audio(file_path) # Mostriamo un bel player audio per conferma
    # --- Fine Blocco Caricamento File ---

    # --- NOVITÀ: Creiamo l'Istruzione di Sistema ---
# 1. Otteniamo la data e ora REALE di oggi
    data_di_oggi = datetime.now().strftime("%d %B %Y, ore %H:%M")
    
    # 2. Creiamo il "post-it" per il cervello dell'agente
    ISTRUZIONE_DI_SISTEMA = f"""
    Sei un assistente AI esperto in ricerche web, la tua priorità è la rilevanza temporale.
    
    CONTESTO CRITICO OBBLIGATORIO:
    La data e l'ora attuali sono: **{data_di_oggi}**.
    
    REGOLE DI RICERCA OBBLIGATORIE:
    1.  NON usare MAI l'input letterale dell'utente come query di ricerca.
    2.  DEVI SEMPRE arricchire la query di ricerca usando la data attuale per trovare
        informazioni rilevanti.
    
    ESEMPI DI COME DEVI COMPORTARTI:
    -   Se l'utente chiede: "quando gioca Sinner?"
        E la data attuale è "4 Novembre 2025".
        La tua query di ricerca DEVE essere: "prossima partita Jannik Sinner DOPO 4 Novembre 2025"
        
    -   Se l'utente chiede: "che tempo fa?"
        E la data attuale è "4 Novembre 2025".
        La tua query di ricerca DEVE essere: "meteo oggi 4 Novembre 2025"
    
    Sei obbligato a seguire queste regole per rendere la ricerca rilevante.
    """
    # -----------------------------------------------------------------

    # 2. Inizializzazione della "Memoria" (Zainetto)
    if "chat" not in st.session_state:
        print("Inizializzo un nuovo modello e chat...")
        google_api_key = os.environ.get("GOOGLE_API_KEY")
        genai.configure(api_key=google_api_key)
        
        # --- MODIFICA: Aggiungiamo l'Istruzione di Sistema al modello ---
        model = genai.GenerativeModel(
            'gemini-flash-lite-latest',
            tools=[addizione, ricerca_web],
            system_instruction=ISTRUZIONE_DI_SISTEMA  # <-- ECCconcentrates!
        )
        
        st.session_state.chat = model.start_chat(
            enable_automatic_function_calling=True
        )
        st.session_state.messages = []

    # 3. Mostra la Cronologia Chat (Resta identico)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # 4. Gestione del Nuovo Input (Resta identico)
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

elif password_inserita: 
    st.error("Password errata. Riprova.")

