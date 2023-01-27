import pytz
from datetime import timedelta

TIME_FORMAT = "%Hh%M"
DATE_FORMAT = "%A %d %B"
LOCALE = pytz.timezone("Europe/Paris")
ROOMS_BLACKLIST = ["djing", "drums", "cabine piano", "mao"]

def format_date(date, dt_format):
    return date.astimezone(LOCALE).strftime(dt_format)

class Session:
    def __init__(self, room, start, end, size):
        self.room = room
        self.start = start
        self.end = end
        self.size = size

    def duration(self):
        if self.end < self.start:
            return timedelta()
        return self.end - self.start

    def truncate(self, min_hour):
        return Session(self.room, max(self.start, self.start.replace(hour=min_hour, minute=0)), self.end, self.size)

    def room_is_blacklisted(self):
        for fragment in ROOMS_BLACKLIST:
            if fragment.lower() in self.room.lower():
                return True
        return False

    def is_valid(self, min_duration_hours) -> bool:
        if self.duration() < timedelta(hours=min_duration_hours):
            return False
        if self.room_is_blacklisted():
            return False
        return True

    def __str__(self):
        day = format_date(self.start, DATE_FORMAT)
        start = format_date(self.start, TIME_FORMAT)
        end = format_date(self.end, TIME_FORMAT)
        time = f"{start} - {end}"
        text = f"Session de {self.duration()} dans {self.room} ({self.size})"
        return ", ".join([day, time, text])

    def to_html(sessions):
        if not sessions:
            return "No session found :("
        return "<br>".join([str(s) for s in sessions])

    def to_string(sessions):
        if not sessions:
            return "No session found :("
        return "\n".join([str(s) for s in sessions])

