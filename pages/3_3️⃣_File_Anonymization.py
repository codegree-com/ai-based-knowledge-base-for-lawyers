import json
import streamlit as st
import spacy
from spacy.tokens import Doc, Span
from spacy_streamlit import visualize_ner
import PyPDF2
import os
import re
from faker import Faker
import uuid
from bot_prep import query_engine, load_document


# Individuelle Pagination für Multistep-Apps, von: https://github.com/streamlit/streamlit/issues/4832
def nav_page(page_name, timeout_secs=5):
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

# Initialisiere Faker mit deutschen Standardeinstellungen
fake = Faker(['de_DE'])

### REGEX DEFINITION ###
# Definiere das benutzerdefinierte Regex-Muster für IBAN
iban_pattern = r'\b[A-Z]{2}[0-9]{2}(?:\s?[A-Z0-9]{4}){1,7}\b'
# Definiere das benutzerdefinierte Regex-Muster für E-Mails
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
### ENDE REGEX ###

### NER Anpassung ####
# Lade das Sprachmodell
nlp = spacy.load("de_core_news_lg")

# Aktualisiere das Labels-Schema des Modells, um das neue "IBAN"-Label einzuschließen
ner = nlp.get_pipe("ner")
ner.add_label("IBAN")
ner.add_label("EMAIL")

@spacy.Language.component("set_iban_label")
def set_iban_label(doc):
    # Suche nach Übereinstimmungen mit dem IBAN-Muster im Text
    matches = re.finditer(iban_pattern, doc.text)
    spans = []
    for match in matches:
        # Konvertiere Zeichenindizes in Token-Start- und -Endindizes
        start, end = match.span()
        span_tokens = [token for token in doc if token.idx >= start and token.idx + len(token) <= end]
        if span_tokens:
            # Erstelle einen Span aus den Tokens und weise das "IBAN"-Label zu
            span = Span(doc, span_tokens[0].i, span_tokens[-1].i + 1, label="IBAN")
            spans.append(span)
    # Filtere überlappende Entitäten heraus
    filtered_ents = [ent for ent in doc.ents if not any(ent.start < span.end and ent.end > span.start for span in spans)]
    doc.ents = filtered_ents + spans
    return doc

@spacy.Language.component("set_email_label")
def set_email_label(doc):
    # Suche nach Übereinstimmungen mit dem E-Mail-Muster im Text
    matches = re.finditer(email_pattern, doc.text)
    spans = []
    for match in matches:
        # Konvertiere Zeichenindizes in Token-Start- und -Endindizes
        start, end = match.span()
        span_tokens = [token for token in doc if token.idx >= start and token.idx + len(token) <= end]
        if span_tokens:
            # Erstelle einen Span aus den Tokens und weise das "EMAIL"-Label zu
            span = Span(doc, span_tokens[0].i, span_tokens[-1].i + 1, label="EMAIL")
            spans.append(span)
    # Filtere überlappende Entitäten heraus
    filtered_ents = [ent for ent in doc.ents if not any(ent.start < span.end and ent.end > span.start for span in spans)]
    doc.ents = filtered_ents + spans
    return doc

# Füge die benutzerdefinierte Komponente "set_iban_label" zur "ner"-Pipeline hinzu
nlp.add_pipe("set_iban_label", after="ner")

# Füge die benutzerdefinierte Komponente "set_email_label" zur "ner"-Pipeline hinzu
nlp.add_pipe("set_email_label", after="ner")
### ENDE NER Anpassung ####


### FUNKTION ZUR PSEUDONYMISIERUNG DER DATEN ###
def anonymize_data():

    # Session-ID initialisieren
    session_id = uuid.uuid4()
    st.session_state.session_id = session_id

    # PDF zum Text umwandeln und NER anwenden
    selected_files = st.session_state.files_for_ner
    file_texts = {}

    for file_path in selected_files:
        full_file_path = os.path.join("files", file_path)
        with open(full_file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_number in range(len(reader.pages)):
                text += reader.pages[page_number].extract_text()
            file_texts[file_path] = text
            text += "mein E-Mail adresse ist perica.glavas@web.de test@rest.de oder alternativ kumpel@rumpel.de und meine IBAN lautet DE75512108001245126199 oder BA393385804800211234 oder AT483200000012345864"

        doc = nlp(text)

        # Gewünschte Labels für NER definieren
        label_mapping = {"Personen": "PER", "E-Mail-Adressen": "EMAIL"}
        desired_labels = [label_mapping.get(label, label) for label in st.session_state.ner_categories]

        # Leeres Dictionary für die Entitäten erstellen
        entities = {label: set() for label in desired_labels}

        # Über alle Entiäten des Dokumentes iterieren
        for ent in doc.ents:
            # Wenn entity labels = desired_labels, füge den Wert hinzu
            if ent.label_ in desired_labels:
                entities[ent.label_].add(ent.text)

        # Umwandlung des Sets zu einer Liste zur weiteren Verarbeitung
        entities = {label: list(values) for label, values in entities.items()}

        # Mapping der Namen zur Faker-Methode
        faker_methods = {"PER": fake.name, "EMAIL": fake.email, "IBAN": fake.iban}

        # Leeres Dictionary initialisieren für die pseudonymsierten Daten
        anonymized_entities = {}

        # Über die Entiäten iterieren und durch Faker-Datensätze austauschen
        for label, values in entities.items():
            faker_method = faker_methods.get(label)
            if faker_method:
                anonymized_entities[label] = [faker_method() for _ in values]
        
        # Pseudonymisierte Werte durch die originalen Werte im Text ersetzen
        for label, fake_values in anonymized_entities.items():
            for original_value, fake_value in zip(entities[label], fake_values):
                text = text.replace(original_value, fake_value)
        
        # Pseudonymsierten Text in einer separaten Datei speichern
        new_file_path = os.path.join("files", f"{session_id}_{os.path.basename(file_path)}.txt")
        with open(new_file_path, 'w', encoding="utf-8") as file:
            file.write(text)

        # Leeres Dictionary, welches die orignalen und pseudonymsierten Werte enthält, um diese wieder rückgängig machen zu können
        original_and_fake_entities = {}

        # Speichere den Wert beider Entitäten
        for label, values in entities.items():
            original_and_fake_entities[label] = list(zip(values, anonymized_entities[label]))

        # Speichere die original_and_fake_entities in einem separaten JSON-File
        json_file_path = os.path.join("files", f"{session_id}_{os.path.basename(file_path)}.json")
        with open(json_file_path, 'w') as file:
            json.dump(original_and_fake_entities, file, ensure_ascii=False)

        # Erstelle eine Liste von Dateien, die nicht anonymisiert wurden, indem du die Dateien filterst, die nicht in 'files_for_ner' sind, aus 'files_for_bot'
        unanonimized_files = list(filter(lambda x: x not in st.session_state.files_for_ner, st.session_state.files_for_bot))

        # Erstelle eine Liste von modifizierten Namen für die anonymisierten Dateien, indem du die Session-ID und den Dateinamen zusammenfügst
        modified_names = [str(st.session_state.session_id)+'_'+anon_file+'.txt' for anon_file in st.session_state.files_for_ner]
        
        # Erstelle eine Liste von Dateipfaden, indem du den Ordnerpfad "files" mit den Dateinamen der nicht anonymisierten und anonymisierten Dateien zusammenfügst
        files_input = [os.path.join("files", filename) for filename in unanonimized_files+modified_names]
        
        # Definiere den Namen das zu verwendenden LLM-Modells
        model_name = "gpt-3.5-turbo"

        # Lade die Dokumente mit der Funktion 'load_document'
        reader = load_document(files_input)

        # Führe die Abfrage-Engine mit dem Reader aller Dateien und dem Modellnamen aus
        query_engine(reader, model_name, )
### ENDE DER PSEUDONYMSIERUNG ###

# Initialisiere eine leere Liste für NER-Kategorien
ner_categories = []

# Setze den Header der Seite
st.header("3️⃣ NER Vorschau: Datei-Anonymisierung")

# Schreibe eine Beschreibung für die Streamlit-Seite
st.write("Bitte wähle aus, welche Art an sensiblen Daten anonymisiert werden sollen. Falls keine anonymisiert werden sollen, so kannst du direkt auf 'Chabot erstellen' drücken. Direkt unter der Auswahl findest du eine Vorschau der einzelnen Dateien mit den jeweiligen Entitäten.")

# Lasse den Benutzer auswählen, welche Kategorien von Daten anonymisiert werden sollen
selected_categories = st.multiselect("Folgende sensible Daten sollen anonymisiert werden:", ["Personen", "IBAN", "E-Mail-Adressen"])

# Überprüfe, ob keine Option ausgewählt ist und zeige eine Warnung an
if not selected_categories:
    st.warning("Bitte wähle mindestens eine Kategorie aus.")

# Führe nur fort, wenn mindestens eine Kategorie ausgewählt ist
else:
    st.session_state.ner_categories = selected_categories

# Füge dies am Anfang deines Skripts hinzu
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

# Füge dies dort hinzu, wo der Button erscheinen soll
if not st.session_state.button_clicked and selected_categories:
    if st.button('Schritt 1: Daten anonymisieren'):
        # Führe die Funktion zur Datenanonymisierung aus, wenn der Button geklickt wird
        anonymize_data()
        # Setze den Status des Buttons auf "geklickt"
        st.session_state.button_clicked = True

# Verarbeite den Text und visualisiere NER
selected_files = st.session_state.files_for_ner
file_texts = {}

# Iteriere über die ausgewählten Dateien
for file_path in selected_files:
    full_file_path = os.path.join("files", file_path)
    with open(full_file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        # Extrahiere den Text aus jeder Seite der PDF-Datei
        for page_number in range(len(reader.pages)):
            text += reader.pages[page_number].extract_text()
        file_texts[file_path] = text
        # Füge zusätzlichen Text hinzu (dies scheint nur für Testzwecke zu sein)
        text += "mein E-Mail adresse ist perica.glavas@web.de test@rest.de oder alternativ kumpel@rumpel.de und meine IBAN lautet DE75512108001245126199 oder BA393385804800211234 oder AT483200000012345864"

    # Verarbeite den Text mit dem NLP-Modell
    doc = nlp(text)

    # Definiere die Labels, die du ausschließen möchtest
    unwanted_labels = {"ORG", "LOC", "MISC"}

    # Stelle beim Visualisieren sicher, dass unerwünschte Labels ausgeschlossen und das neue "IBAN"-Label eingeschlossen wird
    labels = [label for label in ner.labels if label not in unwanted_labels]
    
    # Definiere ein Farbschema für die Labels
    color_scheme = {"PER": "linear-gradient(90deg, #a8e063, #56ab2f)","IBAN": "linear-gradient(90deg, #aa9cfc, #fc9ce7)", "EMAIL": "linear-gradient(90deg, #fc9d9a, #f9cdad)"}

    # Visualisiere nur die gewünschten Labels
    visualize_ner(doc, labels=labels, key=f"ner_visualization_{file_path}", show_table=False, title=f"Entitätenvorschau für {file_path}", colors=color_scheme)
