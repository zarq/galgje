import sys
from galgje import gogogalgje, pogingen
from galgje_gamemaster import galgje as galgje_master
from galgje_gamemaster import galgje_guess

if len(sys.argv) > 1:
    word = sys.argv[1]
else:
    word = None

state, template = galgje_master(word)

def raadfn(letter, template):
    geraden, goede_letter, template = galgje_guess(state, letter)
    return goede_letter, template

try:
    gogogalgje(raadfn, template)
finally:
    print("Pogingen: %r, %d fouten" % (pogingen, state.fouten))

