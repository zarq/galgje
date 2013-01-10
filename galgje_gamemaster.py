import re
from galgje_utils import debug
import random as random_
choice = random_.Random().choice
del random_

debug("Woorden inlezen...")
all_words = []
with open('dutch', 'r') as f:
    for line in f:
        word = line.strip().lower()
        all_words.append(word)

def update_template(template, word, letter):
    res = ''
    for tc, wc in zip(template, word):
        if wc == letter:
            res += wc
        else:
            res += tc
    return res


class GalgjeState(object):
    def __init__(self):
        self.word = None
        self.template = None


class GalgjeError(Exception):
    pass

def galgje(word=None):
    if word is None:
        word = choice(all_words)
    template = re.sub('[a-z]', '_', word)
    print("Galgjewoord: %r" % (template,))
    state = GalgjeState()
    state.word = word
    state.template = template
    state.fouten = 0
    return state, template

def galgje_guess(state, letter):
    goede_letter = False
    geraden = False

    if len(letter) > 1:  # woord raden
        if letter == state.word:
            print("Geraden! Het was %r" % (state.word,))
            goede_letter = True
            geraden = True
        else:
            state.fouten += 1
            if state.fouten > 5:
                print("Helaas. Het woord was %r" % (state.word,))
                raise GalgjeError()
        return geraden, goede_letter, state.template

    template = state.template
    if letter in state.word:
        template = update_template(state.template, state.word, letter)
        state.template = template
        goede_letter = True
    else:
        state.fouten += 1
        if state.fouten > 5:
            print("Helaas. Het woord was %r" % (state.word,))
            raise GalgjeError()

    if template == state.word:
        print("Geraden! Het was %r" % (state.word,))
        geraden = True

    return geraden, goede_letter, template


