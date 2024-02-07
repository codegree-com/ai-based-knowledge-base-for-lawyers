import json
import streamlit as st
import os
from bot_prep import query_engine, load_document
from streamlit_chat import message
from llama_index.prompts  import PromptTemplate
from llama_index.chat_engine.condense_question import CondenseQuestionChatEngine
from llama_index.llms import ChatMessage, MessageRole


query_engine=st.session_state['query_engine']
index = st.session_state['index']

# Ein PromptTemplate wird erstellt, das als Vorlage für die Fragen dient, die an den Chatbot gestellt werden.
# Es enthält Platzhalter für den Chatverlauf, die nachfolgende Nachricht und die eigenständige Frage.
custom_prompt = PromptTemplate("""\
Angesichts einer Unterhaltung (zwischen Mensch und Assistent) und einer nachfolgenden Nachricht vom Menschen, \
schreibe die Nachricht um, so dass sie eine eigenständige Frage darstellt, die den gesamten relevanten Kontext \
aus der Unterhaltung einfängt.

<Chatverlauf> 
{chat_history}

<Follow Up Nachricht>
{question}

<Eigenständige Frage>
""")

# Erstellt eine Liste von Pfaden zu JSON-Dateien, die geladen werden sollen. 
# Die Dateinamen basieren auf der Session-ID und den Dateinamen, die in 'files_for_ner' gespeichert sind.
json_to_load = [os.path.join("files", str(st.session_state.session_id)+'_'+anon_file+'.json') for anon_file in st.session_state.files_for_ner]

# Liest die JSON-Dateien und konvertiert sie.
data_json = [json.loads(open(file, 'r').read()) for file in json_to_load]

# Erstellt eine benutzerdefinierte Chat-Historie, die als Anfangspunkt für die Konversation mit dem Chatbot dient.
# Die Historie besteht aus einer Nachricht vom Benutzer und einer Antwort vom Assistenten.
custom_chat_history = [
    ChatMessage(
        role=MessageRole.USER, 
        content='Hallo Assistent, gegeben ist ein Dokument. Bitte beantworte die Frage, indem du den Kontext und die Informationen des Dokuments verstehst. Nutze dein eigenes Wissen und Verständnis, um die Frage zu beantworten.'
    ), 
    ChatMessage(
        role=MessageRole.ASSISTANT, 
        content='Okay, alles klar.'
    )
]

# Zugriff auf die 'query_engine' aus dem Session-Zustand
query_engine = st.session_state['query_engine']

# Erstellung der Chat-Engine mit den Standardwerten. 
# Die 'query_engine', das 'custom_prompt' und die 'custom_chat_history' werden als Parameter übergeben.
chat_engine = CondenseQuestionChatEngine.from_defaults(
    query_engine=query_engine, 
    condense_question_prompt=custom_prompt,
    chat_history=custom_chat_history
)

# Ausgabe der JSON-Daten auf der Streamlit-Oberfläche
st.write(data_json)

# Senden einer Testnachricht ("Hello!") an den Chat-Engine und Speichern der Antwort
response = chat_engine.chat("Hallo!")

# Definition einer Funktion, die eine Anfrage an den Chat-Engine sendet und die Antwort streamt
def conversational_chat(query):
    streaming_response = chat_engine.stream_chat(query)
    response_tokens = []
    for token in streaming_response.response_gen:
        response_tokens.append(token)
    return ''.join(response_tokens)

# Initialisierung der Session-Zustandsvariablen, wenn sie noch nicht existieren
if 'history' not in st.session_state:
    st.session_state['history'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = ["Hey! Frag mich alles über die Dokumente 🤗"]

if 'past' not in st.session_state:
    st.session_state['past'] = ["Hey! 👋"]

# Erstellung von Containern für die Anzeige der Antworten
response_container = st.container()
container = st.container()

# Innerhalb des Containers wird ein Formular erstellt
with container:
    # Erstellung eines Formulars mit der Schlüsselbezeichnung 'my_form', das bei Absendung geleert wird
    with st.form(key='my_form', clear_on_submit=True):
        # Erstellung eines Texteingabefelds für die Benutzerfrage
        user_input = st.text_input("Deine Frage:", placeholder="Worum geht das Dokument?", key='input')
        # Erstellung eines Absende-Buttons für das Formular
        submit_button = st.form_submit_button(label='Absenden')
        
    # Wenn der Absende-Button gedrückt wurde und eine Benutzereingabe vorhanden ist
    if submit_button and user_input:
        # Die Benutzereingabe wird an die Chat-Funktion gesendet und die Antwort wird in 'output' gespeichert
        output = conversational_chat(user_input)
        # Für jede JSON-Datei in 'data_json'
        for data in data_json:
            # Versuche, die "PER"-Schlüsselwerte zu ersetzen
            try:
                if len(data["PER"])!=0:
                    for per_change in data["PER"]:
                        idx = output.find(per_change[1])
                        if idx != -1:
                            output = output.replace(per_change[1], per_change[0])
            except KeyError:
                pass
            # Versuche, die "EMAIL"-Schlüsselwerte zu ersetzen
            try:
                if len(data["EMAIL"])!=0:
                    for per_change in data["EMAIL"]:
                        idx = output.find(per_change[1])
                        if idx != -1:
                            output = output.replace(per_change[1], per_change[0])
            except KeyError:
                pass
            # Versuche, die "IBAN"-Schlüsselwerte zu ersetzen
            try:
                if len(data["IBAN"])!=0:
                    for per_change in data["IBAN"]:
                        idx = output.find(per_change[1])
                        if idx != -1:
                            output = output.replace(per_change[1], per_change[0])
            except KeyError:
                pass
            
        # Füge die Benutzereingabe zur 'past'-Liste im Session-Zustand hinzu
        st.session_state['past'].append(user_input)
        # Füge die generierte Antwort zur 'generated'-Liste im Session-Zustand hinzu
        st.session_state['generated'].append(output)

# Gesprächsverlauf visualieren
if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="avataaars")
            message(st.session_state["generated"][i], key=str(i), avatar_style="identicon")
