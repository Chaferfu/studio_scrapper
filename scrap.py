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
parser.add_argument('--duree_mini', type=int, default=0, help="La durée minimale de la session (en heures)")
parser.add_argument('--jours_recherche', type=int, default=1, help="Sur combien de jours dans le futur la recherche doit s'executer")
parser.add_argument('--heure_mini', type=int, default=0, help="A quelle heure la session commence au plus tôt")

args = parser.parse_args()
SEMAINE = args.semaine
DUREE_MINI = args.duree_mini
HEURE_MINI = args.heure_mini
JOURS_RECHERCHE = args.jours_recherche

sessions = []

if SEMAINE:
    print("Recherche de sessions en semaine")

if DUREE_MINI:
    print(f"Recherche session de {DUREE_MINI} heures minimum")

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

                # Si la session commence avant 18h on la fait commencer à 18h
                if date_session_debut.hour < 18:
                    date_session_debut = date_session_debut.replace(hour=18)

            duration = date_session_fin - date_session_debut

            # Si la session dure au moins le minimum on l'ajoute a la liste
            if date_session_debut.hour >= HEURE_MINI and duration >= datetime.timedelta(hours=DUREE_MINI):

                room_name = room.h4.contents[0].strip()

                if not any(bad_room in room_name.lower() for bad_room in ["djing", "drums", "cabine piano", "mao"]):
                    session = {
                        "room": room_name,
                        "start": date_session_debut,
                        "end": date_session_fin,
                        "duration": duration,
                        "size": "".join([r for r in room.find("div", "description").get_text().split() if "m2" in r])
                    }
                    sessions.append(session)

# Trie les sessions chronologiquement
sessions.sort(key=lambda x: x["start"])

for session in sessions:
    print(f"{session['start'].strftime(DATE_FORMAT)}, {session['start'].strftime(TIME_FORMAT)} - {session['end'].strftime(TIME_FORMAT)} -> Session de {str(session['duration'])} dans {session['room']} ({session['size']})")
if not sessions:
    print("Aucune session :(")
