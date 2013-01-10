from collections import defaultdict
import atexit
import re
from math import log as ln
from galgje_utils import debug

pogingen = []
cache = {}

debug("Woorden inlezen...")
all_words = set()
with open('dutch', 'r') as f:
    for line in f:
        word = line.strip().lower()
        all_words.add(word)

debug("Cache inlezen...")
with open("cache", 'r') as f:
    for line in f:
        line = line.strip()
        letter = line[0]
        state = line[1:]
        cache[state] = letter

debug("Cache2 inlezen...")
cache2 = defaultdict(dict)
with open("cache2", 'r') as f:
    for line in f:
        line = line.strip()
        letter,forbidden,template = line.split('|')
        cache2[state][forbidden] = letter

def save_cache2():
    with open('cache2', 'w') as f:
        for template in cache2:
            for forbidden in cache2[template]:
                letter = cache2[template][forbidden]
                f.write("%s|%s|%s\n" % (letter, forbidden, template))

def add_to_cache2(letter, forbidden, template):
    with open('cache2', 'a') as f:
        f.write("%s|%s|%s\n" % (letter, forbidden, template))

def create_re_from_template(template, gerade_letters):
    if not gerade_letters:
        dot = '[a-z]'
    else:
        overgebleven_letters = set('abcdefghijklmnopqrstuvwxyz')
        overgebleven_letters -= gerade_letters
        dot = '[' + ''.join(overgebleven_letters) + ']'
    expr = '^' + template.replace('_', dot) + '$'
    debug("REGEX=%r" % (expr,))
    return re.compile(expr)




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
    #debug("template_union(%r, %r) = %r" % (template, possibility, result))
    return result


def gogogalgje(raad, template):
    alphabet = set('abcdefghijklmnopqrstuvwxyz')
    words = all_words
    letters_die_erin_zitten = set()
    letters_die_er_niet_in_zitten = set()
    succes = False

    while True:
        # Itereren vanaf hier
        match = create_re_from_template(template, letters_die_erin_zitten)
        debug("Rekenen...")

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

        debug("Letters: %s" % ("".join(letters_die_erin_zitten),))
        debug("Woorden: (%d) %s" % (len(words), ",".join(list(words)[:20]),))
        if len(words) == 1:
            print("Het woord is: %s" % (list(words)[0],))
            resultaat, new_template = raad(list(words)[0], template)
            assert resultaat == True
            succes = True
            return succes, list(words)[0]
        if len(words) == 0:
            print("Ik weet het niet!")
            succes = False
            return succes, None

        if template in cache and cache[template] in alphabet:
            debug("In cache")
            top_letter = cache[template]
        else:
            debug("Not in cache, analyzing...")
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
            # debug("Possible outcomes (letters): %r" % (letters,))
            # debug("%d mogelijke uitkomsten, doel is %d (letters)" % (total_letters, target_letters))
            # debug("Options (letters): %r" % (",".join([repr((letter, count)) for count, letter in options_letters]),))
            # optoptions_letters = list()
            # for optioncount, optionletter in options_letters:
            #     optoptions_letters.append((abs(optioncount - target_letters), optionletter))
            # optoptions_letters = list(sorted(optoptions_letters))
            # debug("Optimale options (letters): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_letters]),))

            # options_all = []
            # total_all = 0
            # for letter in possible_outcomes_all:
            #     count = len(possible_outcomes_all[letter])
            #     total_all += count
            #     options_all.append((count, letter))

            # options_all = list(sorted(options_all))
            # target_all = total_all / 2
            # debug("Possible outcomes (all): %r" % (possible_outcomes_all,))
            # debug("%d mogelijke uitkomsten, doel is %d (all)" % (total_all, target_all))
            # debug("Options (all): %r" % (",".join([repr((letter, count)) for count, letter in options_all]),))
            # optoptions_all = list()
            # for optioncount, optionletter in options_all:
            #     optoptions_all.append((abs(optioncount - target_all), optionletter))
            # optoptions_all = list(sorted(optoptions_all))
            # debug("Optimale options (all): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_all]),))

            options_astrid = []
            total_astrid = len(words)
            for letter in possible_outcomes_astrid:
                p_sum = 0.0
                for option in possible_outcomes_astrid[letter]:
                    p_positie = float(possible_outcomes_astrid[letter][option]) / total_astrid
                    # debug("letter=%r, optie=%r, n=%d, p=%.3f" % (
                    #     letter, option, possible_outcomes_astrid[letter][option], p_positie))
                    p_sum += p_positie * ln(p_positie)
                p_nergens = 1.0 - (float(sum(possible_outcomes_astrid[letter].values()))) / total_astrid
                if p_nergens == 0.0:
                    value = 0.0
                else:
                    value = (p_sum + p_nergens * ln(p_nergens)) / p_nergens
                options_astrid.append((value, letter))

            options_astrid = list(sorted(options_astrid))
            # debug("Possible outcomes (astrid): %r" % (possible_outcomes_astrid,))
            # debug("%d mogelijke uitkomsten, doel is -inf (astrid)" % (total_astrid,))
            # debug("Options (astrid): %r" % (",".join([repr((letter, count)) for count, letter in options_astrid]),))
            optoptions_astrid = list()
            for optioncount, optionletter in options_astrid:
                optoptions_astrid.append((abs(optioncount), optionletter))
            optoptions_astrid = list(sorted(optoptions_astrid, reverse=True))
            debug("Optimale options (astrid): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_astrid]),))

            # options_unique = []
            # total_unique = 0
            # for letter in possible_outcomes_unique:
            #     count = len(possible_outcomes_unique[letter])
            #     total_unique += count
            #     options_unique.append((count, letter))

            # options_unique = list(sorted(options_unique))
            # target_unique = total_unique / 2
            # debug("Possible outcomes (unique): %r" % (possible_outcomes_unique,))
            # debug("%d mogelijke uitkomsten, doel is %d (unique)" % (total_unique, target_unique))
            # debug("Options (unique): %r" % (",".join([repr((letter, count)) for count, letter in options_unique]),))
            # optoptions_unique = list()
            # for optioncount, optionletter in options_unique:
            #     optoptions_unique.append((abs(optioncount - target_unique), optionletter))
            # optoptions_unique = list(sorted(optoptions_unique))
            # debug("Optimale options (unique): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_unique]),))

            top_letter = optoptions_astrid[0][1]

        pogingen.append(top_letter)

        words_met_letter = len(letters[top_letter])
        debug("Beste letter: %s (%d van %d, %.2f%%)" % (
            top_letter,words_met_letter, len(words),
            100.0 * float(len(letters[top_letter])) / len(words)))
        resultaat, new_template = raad(top_letter, template)
        if resultaat == True:
            # letter zat erin
            letters_die_erin_zitten.add(top_letter)
            if template not in cache:
                cache[template] = top_letter
        else:
            letters_die_er_niet_in_zitten.add(top_letter)
        template = new_template

        alphabet.remove(top_letter)


def extract_letters(template):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    letters = set()
    for letter in template:
        if letter in alphabet:
            letters.add(letter)
    return letters

def galgje_reentrant(template, letters_die_er_niet_in_zitten):
    forbidden = ''.join(letters_die_er_niet_in_zitten)
    if forbidden in cache2[template]:
        return cache2[template][forbidden]

    # Itereren vanaf hier
    letters_die_erin_zitten = extract_letters(template)
    match = create_re_from_template(template, letters_die_erin_zitten)
    debug("Rekenen...")

    letters = defaultdict(set)
    possible_outcomes_unique = defaultdict(set)
    possible_outcomes_all = defaultdict(list)
    possible_outcomes_astrid = defaultdict(lambda: defaultdict(lambda: 0))
    new_words = set()
    for word in all_words:
        if match.match(word):
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
                new_words.add(word)
    words = new_words

    debug("Letters: %s" % ("".join(letters_die_erin_zitten),))
    debug("Woorden: (%d) %s" % (len(words), ",".join(list(words)[:20]),))
    if len(words) == 1:
        print("Het woord is: %s" % (list(words)[0],))
        return list(words)[0]
    if len(words) == 0:
        print("Ik weet het niet!")
        return None

    alphabet = set('abcdefghijklmnopqrstuvwxyz')
    for i in letters_die_erin_zitten:
        alphabet.remove(i)
    for i in letters_die_er_niet_in_zitten:
        alphabet.remove(i)
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
    # debug("Possible outcomes (letters): %r" % (letters,))
    # debug("%d mogelijke uitkomsten, doel is %d (letters)" % (total_letters, target_letters))
    # debug("Options (letters): %r" % (",".join([repr((letter, count)) for count, letter in options_letters]),))
    # optoptions_letters = list()
    # for optioncount, optionletter in options_letters:
    #     optoptions_letters.append((abs(optioncount - target_letters), optionletter))
    # optoptions_letters = list(sorted(optoptions_letters))
    # debug("Optimale options (letters): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_letters]),))

    # options_all = []
    # total_all = 0
    # for letter in possible_outcomes_all:
    #     count = len(possible_outcomes_all[letter])
    #     total_all += count
    #     options_all.append((count, letter))

    # options_all = list(sorted(options_all))
    # target_all = total_all / 2
    # debug("Possible outcomes (all): %r" % (possible_outcomes_all,))
    # debug("%d mogelijke uitkomsten, doel is %d (all)" % (total_all, target_all))
    # debug("Options (all): %r" % (",".join([repr((letter, count)) for count, letter in options_all]),))
    # optoptions_all = list()
    # for optioncount, optionletter in options_all:
    #     optoptions_all.append((abs(optioncount - target_all), optionletter))
    # optoptions_all = list(sorted(optoptions_all))
    # debug("Optimale options (all): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_all]),))

    options_astrid = []
    total_astrid = len(words)
    for letter in possible_outcomes_astrid:
        p_sum = 0.0
        for option in possible_outcomes_astrid[letter]:
            p_positie = float(possible_outcomes_astrid[letter][option]) / total_astrid
            # debug("letter=%r, optie=%r, n=%d, p=%.3f" % (
            #     letter, option, possible_outcomes_astrid[letter][option], p_positie))
            p_sum += p_positie * ln(p_positie)
        p_nergens = 1.0 - (float(sum(possible_outcomes_astrid[letter].values()))) / total_astrid
        if p_nergens == 0.0:
            value = 0.0
        else:
            value = (p_sum + p_nergens * ln(p_nergens)) / p_nergens
        options_astrid.append((value, letter))

    options_astrid = list(sorted(options_astrid))
    # debug("Possible outcomes (astrid): %r" % (possible_outcomes_astrid,))
    # debug("%d mogelijke uitkomsten, doel is -inf (astrid)" % (total_astrid,))
    # debug("Options (astrid): %r" % (",".join([repr((letter, count)) for count, letter in options_astrid]),))
    optoptions_astrid = list()
    for optioncount, optionletter in options_astrid:
        optoptions_astrid.append((abs(optioncount), optionletter))
    optoptions_astrid = list(sorted(optoptions_astrid, reverse=True))
    debug("Optimale options (astrid): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_astrid]),))

    # options_unique = []
    # total_unique = 0
    # for letter in possible_outcomes_unique:
    #     count = len(possible_outcomes_unique[letter])
    #     total_unique += count
    #     options_unique.append((count, letter))

    # options_unique = list(sorted(options_unique))
    # target_unique = total_unique / 2
    # debug("Possible outcomes (unique): %r" % (possible_outcomes_unique,))
    # debug("%d mogelijke uitkomsten, doel is %d (unique)" % (total_unique, target_unique))
    # debug("Options (unique): %r" % (",".join([repr((letter, count)) for count, letter in options_unique]),))
    # optoptions_unique = list()
    # for optioncount, optionletter in options_unique:
    #     optoptions_unique.append((abs(optioncount - target_unique), optionletter))
    # optoptions_unique = list(sorted(optoptions_unique))
    # debug("Optimale options (unique): %r" % (",".join([repr((letter, dist)) for dist, letter in optoptions_unique]),))

    top_letter = optoptions_astrid[0][1]

    cache2[template][forbidden] = top_letter
    add_to_cache2(top_letter, forbidden, template)

    return top_letter



def raadfn_terminal(letter, template):
    print("!raad %s" % (letter,))
    while True:
        res = input("Zat er een %s in? (j/n) " % (letter,))
        if res in 'nj':
            break
    if res == 'j':
        template = input("Plak het template: ")
        return True, template
    else:
        return False, template


def save_cache():
    debug("Cache schrijven...")
    with open('cache', 'w') as f:
        for template, letter in cache.items():
            f.write("%s%s\n"  % (letter, template))


atexit.register(save_cache)
