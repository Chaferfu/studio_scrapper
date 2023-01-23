from bs4 import BeautifulSoup
import datetime
import requests
import pytz

def studio_scrap(request):

    URL = "https://www.quickstudio.com/fr/studios/hf-music-studio-14/bookings"
    TIME_FORMAT = "%Hh%M"
    DATE_FORMAT = "%A %d %B"
    LOCALE = pytz.timezone("Europe/Paris")

    SEMAINE = bool(request.args.get("semaine", False))
    DUREE_MINI = int(request.args.get("duree_mini", 0))
    HEURE_MINI = int(request.args.get("heure_mini", 0))
    JOURS_RECHERCHE = int(request.args.get("jours_recherche", 1))

    sessions = []

    if SEMAINE:
        print("Recherche de sessions en semaine")

    if DUREE_MINI:
        print(f"Recherche session de {DUREE_MINI} heures minimum")

    for single_date in (datetime.datetime.now() + datetime.timedelta(n) for n in range(JOURS_RECHERCHE)):

        r = requests.get(url=URL, params={"date": single_date})
        soup = BeautifulSoup(r.text, "html.parser")

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

    if sessions:
        return "<br>".join([f"{session['start'].astimezone(LOCALE).strftime(DATE_FORMAT)}, "
                            f"{session['start'].astimezone(LOCALE).strftime(TIME_FORMAT)} - {session['end'].astimezone(LOCALE).strftime(TIME_FORMAT)} "
                            f"-> Session de {str(session['duration'])} dans {session['room']} ({session['size']})" for session in sessions])
    else:
        return "Aucune session :("
