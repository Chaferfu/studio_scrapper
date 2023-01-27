import argparse
from Session import Session

from main import studio_scrap

# Instantiate the parser
parser = argparse.ArgumentParser(description='Affiche les prochaines dispos de studio')
parser.add_argument('--week_offset', type=int, default=0, help="La semaine dans laquelle chercher, 0 = semaine courante, 1 = semaine suivante, etc.")
parser.add_argument('--week_only', default=False, action='store_true', help="Si la recherche doit retourner des résultats les soirs de semaine")
parser.add_argument('--min_duration', type=int, default=0, help="La durée minimale de la session (en heures)")
parser.add_argument('--min_hour', type=int, default=0, help="A quelle heure la session commence au plus tôt")
args = parser.parse_args()

print(Session.to_string(studio_scrap(args.week_offset, args.week_only, args.min_duration, args.min_hour)))
