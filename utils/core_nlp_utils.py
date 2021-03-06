from utils.parsed_sentences_loader import ParsedSentencesLoader
from utils.word import Word
from utils.named_entity_group import NamedEntityGroup


def parse_text(sentences):

    loader = ParsedSentencesLoader()
    parseResult = loader.load(sentences)

    if len(parseResult['sentences']) == 1:
        return parseResult

    wordOffset = 0

    for i in range(len(parseResult['sentences'])):

        if i > 0:
            for j in range(len(parseResult['sentences'][i]['dependencies'])):

                for k in range(1,3):
                    tokens = parseResult['sentences'][i]['dependencies'][j][k].split('-')
                    if tokens[0] == 'ROOT':
                        newWordIndex = 0
                    else:
                        if not tokens[len(tokens)-1].isdigit(): # forced to do this because of entries like u"lost-8'" in parseResult
                            continue
                        newWordIndex = int(tokens[len(tokens)-1])+wordOffset
                    if len(tokens) == 2:
                        parseResult['sentences'][i]['dependencies'][j][k] = tokens[0]+ '-' + str(newWordIndex)
                    else:
                        w = ''
                        for l in range(len(tokens)-1):
                            w += tokens[l]
                            if l < len(tokens)-2:
                                w += '-'
                        parseResult['sentences'][i]['dependencies'][j][k] = w + '-' + str(newWordIndex)

        wordOffset += len(parseResult['sentences'][i]['words'])


    # merge information of all sentences into one
    for i in range(1,len(parseResult['sentences'])):
        parseResult['sentences'][0]['text'] += ' ' + parseResult['sentences'][i]['text']
        for jtem in parseResult['sentences'][i]['dependencies']:
            parseResult['sentences'][0]['dependencies'].append(jtem)
        for jtem in parseResult['sentences'][i]['words']:
            parseResult['sentences'][0]['words'].append(jtem)

    # remove all but the first entry
    parseResult['sentences'] = parseResult['sentences'][0:1]

    return parseResult

##############################################################################################################################
##############################################################################################################################


def nerWordAnnotator(parseResult):

    res = []

    wordIndex = 1
    for i in range(len(parseResult['sentences'][0]['words'])):
        tag = [[parseResult['sentences'][0]['words'][i][1]['CharacterOffsetBegin'], parseResult['sentences'][0]['words'][i][1]['CharacterOffsetEnd']], wordIndex, parseResult['sentences'][0]['words'][i][0], parseResult['sentences'][0]['words'][i][1]['NamedEntityTag']]
        wordIndex += 1

        if tag[3] != 'O':
            res.append(tag)


    return res


def ner(parseResult):

    nerWordAnnotations = nerWordAnnotator(parseResult)

    namedEntities = []
    currentNE = []
    currentCharacterOffsets = []
    currentWordOffsets = []

    for i in range(len(nerWordAnnotations)):

               
        if i == 0:
            currentNE.append(nerWordAnnotations[i][2])
            currentCharacterOffsets.append(nerWordAnnotations[i][0])
            currentWordOffsets.append(nerWordAnnotations[i][1])
            if len(nerWordAnnotations) == 1:
                namedEntities.append([currentCharacterOffsets, currentWordOffsets, currentNE, nerWordAnnotations[i-1][3]])
                break
            continue

        if nerWordAnnotations[i][3] == nerWordAnnotations[i-1][3] and nerWordAnnotations[i][1] == nerWordAnnotations[i-1][1]+1:
            currentNE.append(nerWordAnnotations[i][2])
            currentCharacterOffsets.append(nerWordAnnotations[i][0])
            currentWordOffsets.append(nerWordAnnotations[i][1])
            if i == len(nerWordAnnotations)-1:
                namedEntities.append([currentCharacterOffsets, currentWordOffsets, currentNE, nerWordAnnotations[i][3]])
        else:
            namedEntities.append([currentCharacterOffsets, currentWordOffsets, currentNE, nerWordAnnotations[i-1][3]])
            currentNE = [nerWordAnnotations[i][2]]
            currentCharacterOffsets = []
            currentCharacterOffsets.append(nerWordAnnotations[i][0])
            currentWordOffsets = []
            currentWordOffsets.append(nerWordAnnotations[i][1])
            if i == len(nerWordAnnotations)-1:
                namedEntities.append([currentCharacterOffsets, currentWordOffsets, currentNE, nerWordAnnotations[i][3]])

    return namedEntities


def _find_ne_words(sentence):
    words = []

    for word in sentence:
        if word.is_named_entity():
            words.append(word)

    return words


def find_named_entity_groups(sentence):
    ne_words = _find_ne_words(sentence)
    named_entity_groups = []
    current_ne = []
    current_ne_indicies = []
    previous_word = None

    for i, word in enumerate(ne_words):
        if i == 0:
            current_ne.append(word)
            current_ne_indicies.append(word.index)
            if len(ne_words) == 1:
                named_entity_groups.append(NamedEntityGroup(current_ne_indicies, current_ne, word.ner))
                break
            previous_word = word
            continue

        if word.ner == previous_word.ner and word.index == previous_word.index+1:
            current_ne.append(word)
            current_ne_indicies.append(word.index)
        else:
            named_entity_groups.append(NamedEntityGroup(current_ne_indicies, current_ne, previous_word.ner))
            current_ne = [word]
            current_ne_indicies = [word.index]

        if i == len(ne_words)-1:
            named_entity_groups.append(NamedEntityGroup(current_ne_indicies, current_ne, word.ner))

        previous_word = word

    return named_entity_groups


##############################################################################################################################
def posTag(parseResult):

    res = []

    wordIndex = 1
    for i in range(len(parseResult['sentences'][0]['words'])):
        tag = [[parseResult['sentences'][0]['words'][i][1]['CharacterOffsetBegin'], parseResult['sentences'][0]['words'][i][1]['CharacterOffsetEnd']], wordIndex, parseResult['sentences'][0]['words'][i][0], parseResult['sentences'][0]['words'][i][1]['PartOfSpeech']]
        wordIndex += 1
        res.append(tag)


    return res
##############################################################################################################################




##############################################################################################################################
def lemmatize(parseResult):

    res = []

    wordIndex = 1
    for i in range(len(parseResult['sentences'][0]['words'])):
        tag = [[parseResult['sentences'][0]['words'][i][1]['CharacterOffsetBegin'], parseResult['sentences'][0]['words'][i][1]['CharacterOffsetEnd']], wordIndex, parseResult['sentences'][0]['words'][i][0], parseResult['sentences'][0]['words'][i][1]['Lemma']]
        wordIndex += 1
        res.append(tag)

    return res


def prepareSentence(sentence):
    sentenceParseResult = parse_text(sentence)

    sentenceLemmatized = lemmatize(sentenceParseResult)

    sentencePosTagged = posTag(sentenceParseResult)

    sentenceLemmasAndPosTags = []

    for i in range(len(sentenceLemmatized)):
        sentenceLemmasAndPosTags.append([])

    for i in range(len(sentenceLemmatized)):
        for item in sentenceLemmatized[i]:
            sentenceLemmasAndPosTags[i].append(item)
        sentenceLemmasAndPosTags[i].append(sentencePosTagged[i][3])

    return sentenceLemmasAndPosTags


def prepareSentence2(sentence):
    sentenceParseResult = parse_text(sentence)

    sentenceLemmatized = lemmatize(sentenceParseResult)

    sentencePosTagged = posTag(sentenceParseResult)

    sentenceLemmasAndPosTags = []

    for i in range(len(sentenceLemmatized)):
        sentenceLemmasAndPosTags.append([])

    for i in range(len(sentenceLemmatized)):
        for item in sentenceLemmatized[i]:
            sentenceLemmasAndPosTags[i].append(item)
        sentenceLemmasAndPosTags[i].append(sentencePosTagged[i][3])

    words = []

    for rawWord in sentenceLemmasAndPosTags:
        word = Word(rawWord[1] - 1, rawWord[2])
        word.lemma = rawWord[3]
        word.pos = rawWord[4]
        words.append(word)

    return words

def dependencyParseAndPutOffsets(parseResult):
# returns dependency parse of the sentence whhere each item is of the form (rel, left{charStartOffset, charEndOffset, wordNumber}, right{charStartOffset, charEndOffset, wordNumber})

    dParse = parseResult['sentences'][0]['dependencies']
    words = parseResult['sentences'][0]['words']

    #for item in dParse:
        #print item

    result = []

    for item in dParse:
        newItem = []

        # copy 'rel'
        newItem.append(item[0])

        # construct and append entry for 'left'
        left = item[1][0:item[1].rindex("-")]
        wordNumber = item[1][item[1].rindex("-")+1:]
        if wordNumber.isdigit() == False:
            continue
        left += '{' + words[int(wordNumber)-1][1]['CharacterOffsetBegin'] + ' ' + words[int(wordNumber)-1][1]['CharacterOffsetEnd'] + ' ' + wordNumber + '}'
        newItem.append(left)

        # construct and append entry for 'right'
        right = item[2][0:item[2].rindex("-")]
        wordNumber = item[2][item[2].rindex("-")+1:]
        if wordNumber.isdigit() == False:
            continue
        right += '{' + words[int(wordNumber)-1][1]['CharacterOffsetBegin'] + ' ' + words[int(wordNumber)-1][1]['CharacterOffsetEnd'] + ' ' + wordNumber  + '}'
        newItem.append(right)

        result.append(newItem)

    return result
##############################################################################################################################



##############################################################################################################################
def findParents(dependencyParse, wordIndex, word):
# word index assumed to be starting at 1
# the third parameter is needed because of the collapsed representation of the dependencies...

    wordsWithIndices = ((int(item[2].split('{')[1].split('}')[0].split(' ')[2]), item[2].split('{')[0]) for item in dependencyParse)
    wordsWithIndices = list(set(wordsWithIndices))
    wordsWithIndices = sorted(wordsWithIndices, key=lambda item: item[0])

    wordIndexPresentInTheList = False
    for item in wordsWithIndices:
        if item[0] == wordIndex:
            wordIndexPresentInTheList = True
            break

    parentsWithRelation = []

    if wordIndexPresentInTheList:
        for item in dependencyParse:
            currentIndex = int(item[2].split('{')[1].split('}')[0].split(' ')[2])
            if currentIndex == wordIndex:
                parentsWithRelation.append([int(item[1].split('{')[1].split('}')[0].split(' ')[2]), item[1].split('{')[0], item[0]])
    else:
        # find the closest following word index which is in the list
        nextIndex = 0
        for i in range(len(wordsWithIndices)):
            if wordsWithIndices[i][0] > wordIndex:
                nextIndex = wordsWithIndices[i][0]
                break
        if nextIndex == 0:
            return [] #?
        for i in range(len(dependencyParse)):
            if int(dependencyParse[i][2].split('{')[1].split('}')[0].split(' ')[2]) == nextIndex:
                   pos = i
                   break
        for i in range(pos, len(dependencyParse)):
            try:
                if '_' in dependencyParse[i][0] and word in dependencyParse[i][0]:
                    parent = [int(dependencyParse[i][1].split('{')[1].split('}')[0].split(' ')[2]), dependencyParse[i][1].split('{')[0], dependencyParse[i][0]]
                    parentsWithRelation.append(parent)
                    break
            except:
                break
        
    return parentsWithRelation
##############################################################################################################################




##############################################################################################################################
def findChildren(dependencyParse, wordIndex, word):
# word index assumed to be starting at 1
# the third parameter is needed because of the collapsed representation of the dependencies...

    wordsWithIndices = ((int(item[2].split('{')[1].split('}')[0].split(' ')[2]), item[2].split('{')[0]) for item in dependencyParse)
    wordsWithIndices = list(set(wordsWithIndices))
    wordsWithIndices = sorted(wordsWithIndices, key=lambda item: item[0])

    wordIndexPresentInTheList = False
    for item in wordsWithIndices:
        if item[0] == wordIndex:
            wordIndexPresentInTheList = True
            break

    childrenWithRelation = []

    if wordIndexPresentInTheList:
        #print True
        for item in dependencyParse:
            currentIndex = int(item[1].split('{')[1].split('}')[0].split(' ')[2])
            if currentIndex == wordIndex:
                childrenWithRelation.append([int(item[2].split('{')[1].split('}')[0].split(' ')[2]), item[2].split('{')[0], item[0]])
    else:
        # find the closest following word index which is in the list
        nextIndex = 0
        for i in range(len(wordsWithIndices)):
            if wordsWithIndices[i][0] > wordIndex:
                nextIndex = wordsWithIndices[i][0]
                break

        if nextIndex == 0:
            return []
        for i in range(len(dependencyParse)):
            if int(dependencyParse[i][2].split('{')[1].split('}')[0].split(' ')[2]) == nextIndex:
            # if child index of the word i == next index
                   pos = i
                   break
        for i in range(pos, len(dependencyParse)):
            try:
                if '_' in dependencyParse[i][0] and word in dependencyParse[i][0]:
                    child = [int(dependencyParse[i][2].split('{')[1].split('}')[0].split(' ')[2]), dependencyParse[i][2].split('{')[0], dependencyParse[i][0]]
                    childrenWithRelation.append(child)
                    break
            except:
                break

    return childrenWithRelation

##############################################################################################################################

def read_parsed_sentences(sentence_file):

    sentence_structure = ''
    sentences = []

    for line in sentence_file:

        if line.startswith('Sentence #'):
            if sentence_structure != '':
                sentences.append(sentence_structure)
            sentence_structure = ''

        sentence_structure += line

    sentences.append(sentence_structure)

    return sentences
