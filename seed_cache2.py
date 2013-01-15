from collections import defaultdict
from galgje import create_re_from_template, extract_letters_str, predict_outcome
from math import log as ln
import time

from galgje_utils import debug
from galgje_gamemaster import galgje as galgje_master
from galgje_gamemaster import galgje_guess
from galgje_gamemaster import GalgjeError

debug("Woorden inlezen...")
all_words = set()
all_words_by_word_length = defaultdict(set)
with open('dutch', 'rU') as f:
    for line in f:
        word = line.strip().lower()
        all_words.add(word)
        all_words_by_word_length[len(word)].add(word)

debug("Cache2 inlezen...")
cache2 = defaultdict(dict)
with open("cache2", 'rU') as f:
    for line in f:
        line = line.strip()
        letter,forbidden,template = line.split('|')
        cache2[template][forbidden] = letter


cache_hits = [0]
cache_misses = [0]
guesses = [0]

def add_to_cache2(letter, forbidden, template):
    with open('cache2', 'a') as f:
        f.write("%s|%s|%s\n" % (letter, forbidden, template))

def match_template(word, template, letters_die_erin_zitten, letters_die_er_niet_in_zitten):
    for tchar, wchar in zip(template, word):
        if tchar == '_':
            if wchar in letters_die_erin_zitten or wchar in letters_die_er_niet_in_zitten:
                return False
        elif tchar != wchar:
            return False
    return True

def galgje_reentrant(template, letters_die_er_niet_in_zitten):
    guesses[0] += 1
    forbidden = ''.join(sorted(letters_die_er_niet_in_zitten))
    if forbidden in cache2[template]:
        cache_hits[0] += 1
        return cache2[template][forbidden]
    cache_misses[0] += 1

    # Itereren vanaf hier
    letters_die_erin_zitten = extract_letters_str(template)
    # match = create_re_from_template(template, letters_die_erin_zitten)
    # debug("Rekenen...")

    possible_outcomes_astrid = defaultdict(lambda: defaultdict(lambda: 0))
    new_words = set()
    for word in all_words_by_word_length[len(template)]:
        if match_template(word, template, letters_die_erin_zitten, letters_die_er_niet_in_zitten):
            new_words.add(word)
    words = new_words

    # debug("Woorden: (%d) %s" % (len(words), ",".join(list(words)[:20]),))
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
                outcome = predict_outcome(template, word, letter)
                possible_outcomes_astrid[letter][outcome] += 1

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

    top_letter = options_astrid[0][1]

    cache2[template][forbidden] = top_letter
    add_to_cache2(top_letter, forbidden, template)

    return top_letter


failed_words = set()
start = time.time()
done_count = 0
for word in all_words:
    state, template = galgje_master(word)

    letters_die_er_niet_in_zitten = set()
    while True:
        try:
            letter = galgje_reentrant(template, letters_die_er_niet_in_zitten)
            if letter == None:
                break
            geraden, goede_letter, template = galgje_guess(state, letter)
            if not goede_letter:
                letters_die_er_niet_in_zitten.add(letter)
            if geraden:
                break
        except GalgjeError:
            failed_words.add(word)
            with open("nietgeraden", "a") as f:
                f.write(word + '\n')
            break

    debug("guesses: %.1f/s, hits=%.1f%%" % (guesses[0]/(time.time() - start),
                                            float(100.0 * cache_hits[0]) / (cache_hits[0] + cache_misses[0])))
    done_count += 1
    done = float(done_count) / len(all_words)
    debug("%.3f%% of %d words" % (done * 100.0, len(all_words)))
    td = time.time() - start
    remaining = float(len(all_words) - done_count) / len(all_words)
    if done > 0:
        debug("ETA: %f seconds" % (td / done * remaining))
    debug("Niet-gerade woorden: %.3f%%" % (float(len(failed_words)) * 100.0 / done_count,))




def save_cache2():
    with open('cache2', 'w') as f:
        for template in cache2:
            for forbidden in cache2[template]:
                letter = cache2[template][forbidden]
                f.write("%s|%s|%s\n" % (letter, forbidden, template))

import atexit
atexit.register(save_cache2)
