from bs4 import BeautifulSoup
import datetime
import requests
import argparse

URL = "https://www.quickstudio.com/fr/studios/hf-music-studio-14/bookings"
TIME_FORMAT = "%Hh%M"
DATE_FORMAT = "%A %d %B"

# Instantiate the parser
parser = argparse.ArgumentParser(description='Affiche les prochaines dispos de studio')
parser.add_argument('--semaine', default=False, action='store_true', help="Si la recherche doit retourner des résultats les soirs de semaine (à partir de 18h)")
parser.add_argument('--mini', type=int, default=0, help="La durée minimale de la session (en heures)")
parser.add_argument('--jours_recherche', type=int, default=1, help="Sur combien de jours dans le futur la recherche doit s'executer")

args = parser.parse_args()
SEMAINE = args.semaine
MINI = args.mini
JOURS_RECHERCHE = args.jours_recherche

sessions = []

if SEMAINE:
    print("Recherche de sessions en semaine (à partir de 18h)")

if MINI:
    print(f"Recherche session de {MINI} heures minimum")

for single_date in (datetime.datetime.now() + datetime.timedelta(n) for n in range(JOURS_RECHERCHE)):

    r = requests.get(url=URL, params={"date": single_date})
    soup = BeautifulSoup(r.text, "html.parser")

    # with open("page.html") as file:
    #     soup = BeautifulSoup(file, "html.parser")

    for room in soup.find_all(class_="room-box"):
        slots = room.find("div", "slots")
        available_slots = slots.find_all(class_="available")
        for slot in available_slots:
            start = int(slot.get('data-start'))
            end = int(slot.get('data-end'))
            date_session_debut = datetime.datetime.fromtimestamp(start)
            date_session_fin = datetime.datetime.fromtimestamp(end)
            if SEMAINE:

                # Si c'est un weekend on passe
                if date_session_debut.weekday() in [5, 6]:
                    continue

                # Si la session termine avant 19 heure on passe 
                if date_session_fin.hour < 19:
                    continue

                # Si la session commence avant 18h on la fait commencer à 18h
                if date_session_debut.hour < 18:
                    date_session_debut = date_session_debut.replace(hour=18)

            duration = date_session_fin - date_session_debut

            # Si la session dure au moins le minimum on l'ajoute a la liste
            if duration >= datetime.timedelta(hours=MINI):

                session = {
                    "room": room.h4.contents[0].strip(),
                    "start": date_session_debut,
                    "end": date_session_fin,
                    "duration": duration
                }
                sessions.append(session)

# Trie les sessions chronologiquement
sessions.sort(key=lambda x: x["start"])

for session in sessions:
    print(f"{session['start'].strftime(DATE_FORMAT)}, {session['start'].strftime(TIME_FORMAT)} - {session['end'].strftime(TIME_FORMAT)} -> Session de {str(session['duration'])} dans {session['room']}")
if not session:
    print("Aucune session ce jour :(")
