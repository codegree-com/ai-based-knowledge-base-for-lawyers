import streamlit as st
import os

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

#### BEGINN HAUPTTEIL ######

# Setzt den Header der Seite
st.header("🗃️ Dateimanager")
# Schreibt eine Beschreibung für den Benutzer
st.write("Im Dateimanager kannst du bereits hochgeladene Dateien unwiderruflich löschen und neue Dateien für deine Chatbots hochladen.")
# Ermöglicht das Hochladen von Dateien
uploaded_files = st.file_uploader("Wähle die passenden Dateien von deinem Rechner aus, um diese hochzuladen.", accept_multiple_files=True, type=['pdf'])
# Holt die gespeicherten Dateien aus dem Session-State
saved_files = st.session_state.get("saved_files", {})

# Geht durch alle hochgeladenen Dateien
for file in uploaded_files:
    # Überprüft, ob die Datei ein PDF ist
    if file.type == "application/pdf":
        # Erstellt einen Pfad für die Datei
        file_path = os.path.join("files", file.name)
        # Öffnet die Datei und schreibt den Inhalt hinein
        with open(file_path, "wb") as f:
            f.write(file.getvalue())
        # Speichert den Dateipfad im Wörterbuch
        saved_files[file.name] = file_path  

# Definiert das Verzeichnis für die Dateien
file_directory = "files"
# Listet alle PDF-Dateien im Verzeichnis auf
all_files = [f for f in os.listdir(file_directory) if f.lower().endswith('.pdf')]

# Überprüft, ob es hochgeladene Dateien gibt
if all_files:
    # Listet die hochgeladenen Dateien auf
    st.write("Bisher hochgeladene Dateien:")
    for file_name in all_files:
        # Fügt einen Löschknopf für jede Datei hinzu
        if st.button(f"🗑️ Lösche {file_name}"):
            # Definiert den Pfad zur Datei
            file_path = os.path.join(file_directory, file_name)
            # Löscht die Datei
            os.remove(file_path)
            # Informiert den Benutzer über die gelöschte Datei
            st.write(f"{file_name} wurde gelöscht.")
else:
    # Informiert den Benutzer, dass noch keine Dateien hochgeladen wurden
    st.write("Du hast noch keine Dateien hochgeladen")

# Deaktiviert den Button, wenn es keine Dateien gibt
if not saved_files and not all_files:
    st.button("🤖 Chatbot erstellen", disabled=True)
else:
    # Fügt einen Button hinzu, um einen Chatbot zu erstellen
    if st.button("🤖 Chatbot erstellen"):
        # Navigiert zur Seite "Select_Files_for_Chatbot"
        nav_page("Select_Files_for_Chatbot")