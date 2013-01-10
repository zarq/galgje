from galgje import *

template = input("Plak het template: ")
succes, woord = gogogalgje(raadfn_terminal, template)
if succes:
    print("Het woord is: %r" % (woord,))


print("Succes: %r; pogingen: %r" % (succes, pogingen))
