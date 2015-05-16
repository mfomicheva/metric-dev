from config import *
from nltk.corpus import wordnet
import re
import math
from types import *

def wordRelatednessAlignment(word1, word2, config):

    global stemmer
    global punctuations

    canonical_word1 = canonize_word(word1.form)
    canonical_word2 = canonize_word(word2.form)

    if canonical_word1.isdigit() and canonical_word2.isdigit() and canonical_word1 != canonical_word2:
        return 0

    if word1.pos.lower() == 'cd' and word2.pos.lower() == 'cd' and (not canonical_word1.isdigit() and not canonical_word2.isdigit()) and canonical_word1 <> canonical_word2:
        return 0

    # stopwords can be similar to only stopwords
    if (canonical_word1 in stopwords and canonical_word2 not in stopwords) or (canonical_word1 not in stopwords and canonical_word2 in stopwords):
        return 0

    # punctuations can only be either identical or totally dissimilar
    if canonical_word1 in punctuations or canonical_word2 in punctuations:
        return 0

    if canonical_word1 == canonical_word2:
        lexSim = config.exact

    elif contractionDictionary.check_contraction(canonical_word1, canonical_word2):
        lexSim = config.exact

    elif stemmer.stem(canonical_word1) == stemmer.stem(canonical_word2):
        lexSim = config.stem

    elif word1.lemma == word2.lemma:
        lexSim = config.stem

    elif synonymDictionary.checkSynonymByLemma(word1.lemma, word2.lemma):
        lexSim = config.synonym

    elif presentInPPDB(canonical_word1, canonical_word2):
        lexSim = config.paraphrase

    elif ((not functionWord(word1.form) and not functionWord(word2.form)) or word1.pos[0] == word2.pos[0]) and cosineSimilarity(word1.form, word2.form) > config.related_threshold:

        if word1.form not in punctuations and word2.form not in punctuations:
            lexSim = config.related

    else:
        lexSim = 0.0

    return lexSim

def wordRelatednessScoring(word1, word2, scorer, contextPenalty):

    global stemmer
    global punctuations

    canonical_word1 = canonize_word(word1.form)
    canonical_word2 = canonize_word(word2.form)

    if canonical_word1 == canonical_word2:
        lexSim = scorer.exact

    elif contractionDictionary.check_contraction(canonical_word1, canonical_word2):
        lexSim = scorer.exact

    elif word1.lemma == word2.lemma:
        lexSim = scorer.stem

    elif stemmer.stem(canonical_word1) == stemmer.stem(canonical_word2):
        lexSim = scorer.stem

    elif synonymDictionary.checkSynonymByLemma(word1.lemma, word2.lemma):
        lexSim = scorer.synonym

    elif presentInPPDB(canonical_word1, canonical_word2):
        lexSim = scorer.paraphrase

    else:
        lexSim = scorer.related

    result = lexSim - contextPenalty * scorer.context_importance

    return max(result, scorer.minimal_aligned_relatedness)


def loadWordVectors(vectorsFileName = '/home/tos/workspace/distributed-similarity/deps.words'):

    global wordVector
    vectorFile = open (vectorsFileName, 'r')

    for line in vectorFile:
        if line == '\n':
            continue

        match = re.match(r'^([^ ]+) (.+)',line)
        if type(match) is NoneType:
            continue

        word = match.group(1)
        vector = match.group(2)

        wordVector[word] = vector

def cosineSimilarity(word1, word2):

    global wordVector

    if word1.lower() in wordVector and word2.lower() in wordVector:
        vector1 = wordVector[word1.lower()].split( )
        vector2 = wordVector[word2.lower()].split( )
        sumxx, sumxy, sumyy = 0, 0, 0

        for i in range(len(vector1)):
            x = float(vector1[i])
            y = float(vector2[i])
            sumxx += x * x
            sumyy += y * y
            sumxy += x * y
        return sumxy/math.sqrt(sumxx * sumyy)
    else:
        return 0

def loadPPDB(ppdbFileName = 'Resources/ppdb-1.0-xxxl-lexical.extended.synonyms.uniquepairs'):

    global ppdbDict

    count = 0

    ppdbFile = open(ppdbFileName, 'r')
    for line in ppdbFile:
        if line == '\n':
            continue
        tokens = line.split()
        tokens[1] = tokens[1].strip()
        ppdbDict[(tokens[0], tokens[1])] = 0.6
        count += 1


def presentInPPDB(word1, word2):
    global ppdbDict

    if (word1.lower(), word2.lower()) in ppdbDict:
        return True
    if (word2.lower(), word1.lower()) in ppdbDict:
        return True


def functionWord(word):
    global punctuations
    return (word.lower() in stopwords) or (word.lower() in punctuations)


def canonize_word(word):
    if len(word) > 1:
        canonical_form = word.replace('.', '')
        canonical_form = canonical_form.replace('-', '')
        canonical_form = canonical_form.replace(',', '').lower()
    else:
        canonical_form = word.lower()

    return canonical_form


loadPPDB()
loadWordVectors()
