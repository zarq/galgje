import sys, re
from collections import defaultdict

counts = defaultdict(lambda: 0)

alphabet = set('abcdefghijklmnopqrstuvwxyz')

words = set()
aantal_letters = 7

print("Inlezen...")
count = 0
with open('dutch', 'r') as f:
    for line in f:
        word = line.strip().lower()
        if len(word) == aantal_letters:
            if re.match(r'^[a-z]*$', word):
                words.add(word)
                count += 1
                if count >= 100:
                    break

def add_letter(pattern, word, letter):
    new_pattern = ''
    for pos in range(len(word)):
        if word[pos] == letter:
            new_pattern += letter
        else:
            new_pattern += pattern[pos]
    return new_pattern

print("digraph G {")
for word in words:
    start = '_' * len(word)
    pattern = ''
    print("#word: %r" % (word,))
    def iterate(pattern, word, remaining_letters):
        for letter in remaining_letters:
            if letter in word:
                new_pattern = add_letter(pattern, word, letter)
                print("%s -> %s [label=%s];" % (pattern, new_pattern, letter))
                if new_pattern == word:
                    return
                iterate(new_pattern, word, remaining_letters - set(letter))
    iterate(start, word, alphabet)
print("}")

sys.exit(0)

letters_die_erin_zitten = set()
letters_die_er_niet_in_zitten = set()

while True:
    # Itereren vanaf hier
    print("Rekenen...")

    letters = defaultdict(set)
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
            new_words.add(word)
    words = new_words
    for word in words:
        for letter in alphabet:
            if letter in word:
                letters[letter].add(word)

    def countfn(letter):
        return len(letters[letter])

    gesorteerde_letters = list(sorted(letters, key=countfn, reverse=True))
    print("Letters: %s" % ("".join(letters_die_erin_zitten),))
    print("Overgebleven letters: %s" % ("".join(gesorteerde_letters),))
    print("Woorden: (%d) %s" % (len(words), ",".join(list(words)[:20]),))
    top_letter = gesorteerde_letters[0]
    print("Voorkomendste letter: %s (%d van %d, %.2f%%)" % (
        top_letter, len(letters[top_letter]), len(words),
        100.0 * float(len(letters[top_letter])) / len(words)))
    print("!raad %s" % (top_letter,))
    while True:
        res = input("Zat er een %s in? (j/n) " % (top_letter,))
        if res in 'nj':
            break
    if res == 'j':
        # letter zat erin
        letters_die_erin_zitten.add(top_letter)
    else:
        letters_die_er_niet_in_zitten.add(top_letter)
    alphabet.remove(top_letter)

