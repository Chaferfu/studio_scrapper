from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests

from Session import Session

URL = "https://www.quickstudio.com/fr/studios/hf-music-studio-14/bookings"

def studio_scrap(week_offset, week_only, min_duration_hours, min_hour):

    sessions = []

    if week_only:
        print("Recherche de sessions en semaine")

    if min_duration_hours:
        print(f"Recherche session de {min_duration_hours} heures minimum")

    for single_date in week_range(week_offset, week_only):

        r = requests.get(url=URL, params={"date": single_date})
        soup = BeautifulSoup(r.text, "html.parser")

        for room in get_rooms(soup):
            for slot in get_available_slots(room):
                session = parse_session(room, slot).truncate(min_hour)
                if session.is_valid(min_duration_hours):
                    sessions.append(session)

    # Trie les sessions chronologiquement
    sessions.sort(key=lambda x: x.start)

    return sessions

def week_start(dt):
    start = dt - timedelta(days=dt.weekday(), hours=dt.hour)
    return start

def week_range(week_offset, week_only):
    now = datetime.now()
    week_length = 5 if week_only else 7
    start = week_start(now + timedelta(days=week_offset * 7))
    return (start + timedelta(n) for n in range(week_length))

def get_rooms(soup):
    return soup.find_all(class_="room-box")

def get_available_slots(room):
    slots = room.find("div", "slots")
    return slots.find_all(class_="available")

def parse_session(room, slot) -> Session:
    start = int(slot.get('data-start'))
    end = int(slot.get('data-end'))
    session_start = datetime.fromtimestamp(start)
    session_end = datetime.fromtimestamp(end)

    room_name = room.h4.contents[0].strip()
    size = "".join([r for r in room.find("div", "description").get_text().split() if "m2" in r])
    
    return Session(room_name, session_start, session_end, size)
