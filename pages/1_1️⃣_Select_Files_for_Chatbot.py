import os
import streamlit as st

# Individuelle Navigation für mehrstufige Apps, Quelle: https://github.com/streamlit/streamlit/issues/4832
def nav_page(page_name, timeout_secs=3):
    # Ein JavaScript-Skript, das versucht, zu einer bestimmten Seite zu navigieren
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
                    alert("Navigation zur Seite '" + page_name + "' nach " + timeout_secs + " Sekunde(n) nicht möglich.");
                }}
            }}
            window.addEventListener("load", function() {{
                attempt_nav_page("{page_name}", new Date(), {timeout_secs});
            }});
        </script>
    """
    # Fügt das JavaScript-Skript zur Streamlit-App hinzu
    st.components.v1.html(nav_script)

# Definiert das Verzeichnis für die Dateien
file_directory = "files"
# Listet alle PDF-Dateien im Verzeichnis auf
all_files = [f for f in os.listdir(file_directory) if f.lower().endswith('.pdf')]

# Setzt den Header der Seite
st.header("1️⃣ Dateien für den Chatbot auswählen")
# Schreibt eine Beschreibung für den Benutzer
st.write("Bitte wähle alle Dateien aus, welche du für deinen nächsten Chatbot verwenden willst:")
selected_files = []
# Überprüft, ob es hochgeladene Dateien gibt
if all_files:
    # Ermöglicht die Auswahl von Dateien für den Chatbot
    selected_files = st.multiselect("Dateien für den Chatbot auswählen:", all_files, default=st.session_state.get('files_for_bot', []))
    # Speichert die ausgewählten Dateien im Session-State
    st.session_state.files_for_bot = selected_files

# Überprüft, ob es keine hochgeladenen Dateien gibt
if not all_files:
    # Informiert den Benutzer, dass noch keine Dateien hochgeladen wurden
    st.write("Du hast bislang keine Dateien hochgeladen bitte nehmen das zuerst vor.")
    # Fügt einen Button hinzu, um zum Dateimanager zu navigieren
    if st.button("Zum File-Manager"):
        nav_page("File_Manager")

# Deaktiviert den Button, wenn keine Dateien ausgewählt wurden
if not selected_files:
    st.button("Weiter", disabled=True)
else:
    # Fügt einen Button hinzu, um zur nächsten Seite zu navigieren
    if st.button("Weiter"):
        nav_page("Select_Files_for_NER")