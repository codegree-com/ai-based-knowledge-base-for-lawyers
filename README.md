# Über das Projekt
Dieses Projekt entsteht im Rahmen einer Bachelorarbeit. Es geht, um eine datenschutzkonforme Implementierung einer KI-basierten juristischen Wissensdatenbank, welcher vor der Übermittlung der Daten an das LLM es dem Nutzer erlaubt die Daten zu pseudonymisieren ohne dabei die Bedeutung des Inhaltes zu verlieren. 
# Installation
Im folgenden wird Schritt-für-Schritt die Installation und Anwendung des Programms beschrieben.
## Schritt 1: Github-Repositiry klonen
Um das Programm lokal laufen zu lassen muss zuerst das Github-Repository lokal geklont werden. Am einfachsten geht das über die GitHub CLI mit dem Kommando: 
```
gh repo clone codegree-com/ai-based-knowledge-base-for-lawyers
```
## Schritt 2: OpenAI-API-Keys festlegen
Damit das Programm einwandfrei funktioniert und sowohl die Embeddings als auch die Antworten auf die Nutzerfragen erstellt werden können, sind API-Keys von OpenAI notwendig. Diese können unter https://platform.openai.com/ beantragt werden.
Nach dem Erhalt der OpenAI-Keys müssen diese innerhalb der ```bot_prep.py``` Datei in Zeile 14 ersetzt werden.
## Schritt 3: Requirements installieren
Im Anschluss müssen zuerst die notwendigen Python-Pakete und Libraries installiert werden. 
Dafür existiert im root-Verzeichnis eine requirements.txt-Datei, welche es erlauben alle notwendigen Pakete & Libraries mittels pip (einem Python Package Manager) zu installieren.
Führe dafür folgenden Befehl aus:
```
pip install -r requirements.txt
```
## Schritt 4: Streamlit-Programm ausführen
Nach der erfolgreichen Installation der Pakete mittels pip kann nun das Programm ausgeführt werden. Dazu kann folgender Befehl verwendet werden:
```
streamlit run 0_🗃️File_Manager.py
```
# Verwendung des Programms
Nachdem die Streamlit-Applikation gestartet wurde, kann das Programm verwendet werden. In diesem Abschnitt befassen wir uns mit dem Thema wie die Applikation verwendet werden kann.
## Schritt 1: Dateimanager
Im Dateimanager können wir PDF-Dokumente hochladen und entfernen, welche als Grundlage unserer Wissensdatenbank dienen soll. Mit dem Button "Chatbot erstellen" können wir den Erstellungsprozess beginnen.
## Schritt 2: Dateien für den Chatbot auswählen
Im nächsten Schritt können wir aus unseren hochgeladenen PDF-Dateien auswählen, welche wir davon für den Chatbot verwenden wollen.
## Schritt 3: Dateien für die Pseudonymisiierung auswählen
Nach der Auswahl der Dateien, welche als Grundlage für den Chatbot dienen soll, können wir nun auswählen, welche Dateien weitere Pseudonymisierung benötigen.
## Schritt 4: Vorschau der Pseudonymisiuerng
Im vierten Schritt können wir die erkannten Entitäten des Programms uns anschauen und auswählen welche Entitäten anonymisiert werden sollen. Dabei kann zwischen "Personennamen", "IBAN" und "EMAIL" ausgewählt werden.
### Schritt 4.1. Pseudonymisierung ausführen
Um die Pseudonymisierung der Dokumente zu beginnen, muss der Button "Schritt 1: Daten pseudonymisieren" gedrückt werden. Dadurch wird die Pseudonymisierungsfunktion aufgerufen und der Text wird bei den ausgewählten Entitäten pseudonymisiert.
## Schritt 5: Chatbot verwenden
Im Anschluss wird automatisch die Seite mit dem Chatbot, welcher die Datengrundlage der PDF-Dokumente enthält, geladen. Auf dieser Seite können die Nutzer eine Frage stellen, welche als Kontext die passenden Passagen der jeweiligen Dokumente mitbekommt.
Über dem Gesprächsfenster wird zudem das JSON-Dokument mit den originalen Werten des Dokuments sowie den Werten, die zu Pseudonymisierungszwecken mithilfe der Faker-Library erstellt wurden, angezeigt.
