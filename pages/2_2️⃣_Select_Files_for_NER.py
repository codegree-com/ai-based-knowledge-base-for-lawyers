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

# Initialisiert eine leere Liste für ausgewählte Dateien
selected_files = []

# Setzt den Header der Seite
st.header("2️⃣ Dateien für weitere Pseudonymisierung")
# Schreibt eine Beschreibung für den Benutzer
st.write("Bitte wähle alle Dateien aus, welche weitere Pseudonymisierungsmaßnahmen erfordern.")

# Überprüft, ob es Dateien für den Bot gibt
if not st.session_state.files_for_bot:
    # Informiert den Benutzer, dass keine Dateien gefunden wurden
    st.write("Wir konnten keine Dateien finden, welche du für den Bot freigegeben hast. Bitte gehe zurück zu Schritt 1.")
    # Fügt einen Button hinzu, um zur Auswahl zurückzukehren
    if st.button("Zurück zur Auswahl"):
        nav_page("Select_Files_for_Chatbot")

# Überprüft, ob es Dateien für den Bot gibt
if st.session_state.files_for_bot:
    # Ermöglicht die Auswahl von Dateien für die Pseudonymisierung
    selected_files = st.multiselect("Dateien auswählen:", st.session_state.files_for_bot, default=st.session_state.get('files_for_ner', []))
    # Speichert die ausgewählten Dateien im Session-State
    st.session_state.files_for_ner = selected_files  

# Deaktiviert den Button, wenn keine Dateien ausgewählt wurden
if not selected_files:
    st.button("Weiter", disabled=True)
else:
    # Fügt einen Button hinzu, um zur nächsten Seite zu navigieren
    if st.button("Weiter"):
        nav_page("File_Pseudonymization")