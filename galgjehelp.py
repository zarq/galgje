from collections import defaultdict
import re

counts = defaultdict(lambda: 0)

alphabet = set('abcdefghijklmnopqrstuvwxyz')

words = set()

def create_re_from_template(template, gerade_letters):
    if not gerade_letters:
        dot = '.'
    else:
        dot = '[^' + ''.join(gerade_letters) + ']'
    return re.compile('^' + template.replace('_', dot) + '$')

print("Inlezen...")
with open('dutch', 'r') as f:
    for line in f:
        word = line.strip().lower()
        words.add(word)

letters_die_erin_zitten = set()
letters_die_er_niet_in_zitten = set()

def predict_outcome(template, word, letter):
    result = ''
    for tc, wletter in zip(template, word):
        if wletter == letter:
            tc = wletter
        result += tc
    return result

class CountingSet():
    def __init__(self):
        self._data = defaultdict(lambda: 0)

    def add(self, value):
        self._data[value] += 1

    def sorted_(self):
        def g():
            for k, v in self._data:
                yield v, k
        return sorted(g())


def template_union(template, possibility):
    result = ''
    for tc, pc in zip(template, possibility):
        if tc == pc:
            result += tc
        else:
            result += '_'
    #print("template_union(%r, %r) = %r" % (template, possibility, result))
    return result


template = None
while True:
    # Itereren vanaf hier
    if template is None:
        template = input("Plak het template: ")
    match = create_re_from_template(template, letters_die_erin_zitten)
    print("Rekenen...")

    letters = defaultdict(set)
    possible_outcomes = defaultdict(set)
    new_words = set()
    for word in words:
        add = True
        for letter in letters_die_er_niet_in_zitten:
            if letter in word:
                add = False
                break
        for letter in letters_die_erin_zitten:
            if letter not in word:
                add = False
                break
        if add:
            if match.match(word):
                new_words.add(word)
                words = new_words
    print("Analyzing...")
    for word in words:
        for letter in alphabet:
            if letter in word:
                letters[letter].add(word)
                possible_outcomes[letter].add(predict_outcome(template, word, letter))

    def countfn(letter):
        return len(letters[letter])

    def count2fn(letter):
        return len(possible_outcomes[letter])

    options = []
    total = 0
    for letter in possible_outcomes:
        count = len(possible_outcomes[letter])
        total += count
        options.append((count, letter))

    options = list(sorted(options))
    target = total / 2
    optoptions = list()
    for optioncount, optionletter in options:
        optoptions.append((abs(optioncount - target), optionletter))
    optoptions = list(sorted(optoptions))
    print("Options: %r" % (",".join([letter for dist, letter in optoptions]),))
    top_letter = optoptions[0][1]

    print("Letters: %s" % ("".join(letters_die_erin_zitten),))
    print("Woorden: (%d) %s" % (len(words), ",".join(list(words)[:20]),))
    if len(words) == 1:
        print("Het woord is: %s" % (list(words)[0],))
        break
    words_met_letter = len(letters[top_letter])
    if words_met_letter != len(words):
        print("Voorkomendste letter: %s (%d van %d, %.2f%%)" % (
            top_letter,words_met_letter, len(words),
            100.0 * float(len(letters[top_letter])) / len(words)))
    print("!raad %s" % (top_letter,))
    while True:
        res = input("Zat er een %s in? (j/n) " % (top_letter,))
        if res in 'nj':
            break
    if res == 'j':
        # letter zat erin
        letters_die_erin_zitten.add(top_letter)
        template = None
    else:
        letters_die_er_niet_in_zitten.add(top_letter)

    alphabet.remove(top_letter)

