import sys, time
from galgje import gogogalgje, pogingen
from galgje_gamemaster import galgje as galgje_master
from galgje_gamemaster import galgje_guess

start = time.time()
aantal = 0

while True:
    state, template = galgje_master(None)
    pogingen.clear()

    def raadfn(letter, template):
        geraden, goede_letter, template = galgje_guess(state, letter)
        return goede_letter, template

    try:
        gogogalgje(raadfn, template)
    except:
        pass
    print("Pogingen: %r, %d fouten" % (pogingen, state.fouten))

    aantal += 1
    print("%d, %.1f/s" % (aantal, float(aantal)/(time.time()-start)))
