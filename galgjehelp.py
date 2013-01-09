from collections import defaultdict
import re
from math import log as ln

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
    possible_outcomes_unique = defaultdict(set)
    possible_outcomes_all = defaultdict(list)
    possible_outcomes_astrid = defaultdict(lambda: defaultdict(lambda: 0))
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

    print("Letters: %s" % ("".join(letters_die_erin_zitten),))
    print("Woorden: (%d) %s" % (len(words), ",".join(list(words)[:20]),))
    if len(words) == 1:
        print("Het woord is: %s" % (list(words)[0],))
        break

    print("Analyzing...")
    for word in words:
        for letter in alphabet:
            if letter in word:
                letters[letter].add(word)
                outcome = predict_outcome(template, word, letter)
                possible_outcomes_unique[letter].add(outcome)
                possible_outcomes_all[letter].append(outcome)
                possible_outcomes_astrid[letter][outcome] += 1

    # options_letters = []
    # total_letters = len(words)
    # for letter in letters:
    #     count = len(letters[letter])
    #     # total_letters += count
    #     options_letters.append((count, letter))

    # options_letters = list(sorted(options_letters))
    # target_letters = total_letters / 2
    # print("Possible outcomes (letters): %r" % (letters,))
    # print("%d mogelijke uitkomsten, doel is %d (letters)" % (total_letters, target_letters))
    # print("Options (letters): %r" % (",".join([repr((letter, count)) for count, letter in options_letters]),))
    # optoptions_letters = list()
    # for optioncount, optionletter in options_letters:
    #     optoptions_letters.append((abs(optioncount - target_letters), optionletter))
    # optoptions_letters = list(sorted(optoptions_letters))
    # print("Optimale options (letters): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_letters]),))

    # options_all = []
    # total_all = 0
    # for letter in possible_outcomes_all:
    #     count = len(possible_outcomes_all[letter])
    #     total_all += count
    #     options_all.append((count, letter))

    # options_all = list(sorted(options_all))
    # target_all = total_all / 2
    # print("Possible outcomes (all): %r" % (possible_outcomes_all,))
    # print("%d mogelijke uitkomsten, doel is %d (all)" % (total_all, target_all))
    # print("Options (all): %r" % (",".join([repr((letter, count)) for count, letter in options_all]),))
    # optoptions_all = list()
    # for optioncount, optionletter in options_all:
    #     optoptions_all.append((abs(optioncount - target_all), optionletter))
    # optoptions_all = list(sorted(optoptions_all))
    # print("Optimale options (all): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_all]),))

    options_astrid = []
    total_astrid = len(words)
    for letter in possible_outcomes_astrid:
        p_sum = 0.0
        for option in possible_outcomes_astrid[letter]:
            p_positie = float(possible_outcomes_astrid[letter][option]) / total_astrid
            # print("letter=%r, optie=%r, n=%d, p=%.3f" % (
            #     letter, option, possible_outcomes_astrid[letter][option], p_positie))
            p_sum += p_positie * ln(p_positie)
        p_nergens = 1.0 - (float(sum(possible_outcomes_astrid[letter].values()))) / total_astrid
        if p_nergens == 0.0:
            value = -100000000000000000000000.0
        else:
            value = (p_sum + p_nergens * ln(p_nergens)) / p_nergens
        options_astrid.append((value, letter))

    options_astrid = list(sorted(options_astrid))
    # print("Possible outcomes (astrid): %r" % (possible_outcomes_astrid,))
    # print("%d mogelijke uitkomsten, doel is -inf (astrid)" % (total_astrid,))
    # print("Options (astrid): %r" % (",".join([repr((letter, count)) for count, letter in options_astrid]),))
    optoptions_astrid = list()
    for optioncount, optionletter in options_astrid:
        optoptions_astrid.append((abs(optioncount), optionletter))
    optoptions_astrid = list(sorted(optoptions_astrid, reverse=True))
    print("Optimale options (astrid): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_astrid]),))

    # options_unique = []
    # total_unique = 0
    # for letter in possible_outcomes_unique:
    #     count = len(possible_outcomes_unique[letter])
    #     total_unique += count
    #     options_unique.append((count, letter))

    # options_unique = list(sorted(options_unique))
    # target_unique = total_unique / 2
    # print("Possible outcomes (unique): %r" % (possible_outcomes_unique,))
    # print("%d mogelijke uitkomsten, doel is %d (unique)" % (total_unique, target_unique))
    # print("Options (unique): %r" % (",".join([repr((letter, count)) for count, letter in options_unique]),))
    # optoptions_unique = list()
    # for optioncount, optionletter in options_unique:
    #     optoptions_unique.append((abs(optioncount - target_unique), optionletter))
    # optoptions_unique = list(sorted(optoptions_unique))
    # print("Optimale options (unique): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_unique]),))

    top_letter = optoptions_astrid[0][1]

    words_met_letter = len(letters[top_letter])
    print("Beste letter: %s (%d van %d, %.2f%%)" % (
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

