import shutil
import streamlit as st
from streamlit.components.v1 import html
import openai
import os

from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, set_global_service_context
from llama_index.llms import OpenAI
from llama_index.embeddings import OpenAIEmbedding
from llama_index.text_splitter import TokenTextSplitter
from llama_index.indices.prompt_helper import PromptHelper

# API-Key für OPENAI setzen
openai.api_key = "SET_OPENAI_KEY"

# Individuelle Pagination für Multistep-Apps, von: https://github.com/streamlit/streamlit/issues/4832
def nav_page(page_name, timeout_secs=3):
    nav_script = f"""
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {{
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {{
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {{
                        links[i].click();
                        return;
                    }}
                }}
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {{
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                }} else {{
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }}
            }}
            window.addEventListener("load", function() {{
                attempt_nav_page("{page_name}", new Date(), {timeout_secs});
            }});
        </script>
    """
    st.components.v1.html(nav_script)

def query_engine(docs, model_name):
    # Erstellt ein Language Model mit dem gegebenen Modellnamen
    llm = OpenAI(model=model_name)
    # Erstellt einen Service-Kontext mit dem Language Model als Standard
    service_context = ServiceContext.from_defaults(llm=llm)
    # Erstellt einen Index aus den gegebenen Dokumenten
    with st.spinner("Indexing document..."):
        index = VectorStoreIndex.from_documents(docs, service_context=service_context)
        print("index created : ", index)
    # Erstellt eine Abfrage-Engine aus dem Index
    with st.spinner("Creating query engine..."):
        query_engine = index.as_query_engine()
        print("query engine created ")

    # Speichert den Index und die Abfrage-Engine in der Session
    st.session_state['index'] = index
    st.session_state['query_engine'] = query_engine

    # Navigiert zur Seite 'Chatbot'
    nav_page('Chatbot')
    return query_engine

def load_document(uploaded_files):
    # Definiert den Verzeichnisnamen
    dir = 'bot_files'
    # Löscht das Verzeichnis, wenn es bereits existiert
    if os.path.exists(dir):
        shutil.rmtree(dir, ignore_errors=True)
    # Erstellt das Verzeichnis
    os.mkdir(dir)
    # Kopiert die hochgeladenen Dateien in das Verzeichnis
    for file in uploaded_files:
        shutil.copy(file, dir)
    # Erstellt einen Reader für das Verzeichnis
    reader = SimpleDirectoryReader(input_dir=os.path.join(os.getcwd(), dir))
    # Lädt die Daten aus den Dateien
    docs = reader.load_data()
    print(docs)
    return docs