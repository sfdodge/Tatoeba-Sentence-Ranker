"""
Tatoeba sentence extractor

Extracts sentences and orders them such that setences with more
frequent words come first

To do:
1. Remove duplicates? (check for links in the same language
2. implement qt interface
3. create readme file
4. Compile exe?
5. pep check
6. github
7. add support for japanese/chinese
"""
import urllib
import tarfile
import os
from operator import itemgetter
import csv

# PARAMS
MAX_SENTENCES = 5000000
OUTPUT_NUMBER = 1000
OUTFILE = 'output.csv'

def main():
    # load data
    sentences = loadData("fra","eng")

    # compute word rank
    word_rank = computeFrequency(sentences)

    # score all sentences
    sentence_score = computeScore(sentences,word_rank)

    # now simply pop off sentences
    with open(OUTFILE, 'w') as f:
        writer=csv.writer(f)

        for i in range(OUTPUT_NUMBER):
            s_ind = sentence_score.pop(0)
            s = sentences[s_ind[0]]

            writer.writerow(s)

def loadData(lang1,lang2):
    """
    Loads the sentences from tatoeba
    """

    # if data is not downloaded, the download
    sentence_path = "http://downloads.tatoeba.org/exports/sentences.tar.bz2"
    if not os.path.isfile("sentences.csv"):
        sentence_file = urllib.URLopener()
        print "Downloading sentences..."
        sentence_file.retrieve(sentence_path, "sentences.tar.gz")
        tar = tarfile.open("sentences.tar.gz")
        tar.extractall()
        tar.close()
        os.remove("sentences.tar.gz")

    link_path = "http://downloads.tatoeba.org/exports/links.tar.bz2"
    if not os.path.isfile("links.csv"):
        link_file = urllib.URLopener()
        print "Downloading links..."
        link_file.retrieve(link_path, "links.tar.gz")
        tar = tarfile.open("links.tar.gz")
        tar.extractall()
        tar.close()
        os.remove("links.tar.gz")

    # now load all of the sentences in our target languages
    sentences = {}
    with open("sentences.csv", "r") as ins:
        print "Getting sentences in chosen languages..."
        for line in ins:
            line = line[0:-1]   # gets rid of newline
            split = line.split("\t")
            if split[1] == lang1 or split[1] == lang2:
                sentences[split[0]] = (split[1],split[2])

            if len(sentences) > MAX_SENTENCES:
                print "Reached sentence limit"
                break
        
    # now get the pairs in our languages
    # lang1 is first
    pairs = []
    dupes = {}
    with open("links.csv") as ins:
        print "Computing pairs..."
        for line in ins:
            line = line[0:-1] # gets rid of newline
            split = line.split("\t")
            if split[0] in sentences and split[1] in sentences:
                if sentences[split[0]][0] == lang1:
                    # if sentences are the same, flag as a duplicate
                    if sentences[split[0]][0] == sentences[split[1]][0]:
                        dupes[max(split[0],split[0])] = 1
                        continue 

                    if split[0] not in dupes:
                        pairs.append((sentences[split[0]][1], sentences[split[1]][1]))
                        
    return pairs

def computeFrequency(sentences):
    """
    Computes the word frequency

    Returns a large dictionary where the keys are the word, and the
    value is the rank
    """
    print "Counting words..."
    
    # first count word frequencies
    word_count = {}
    for s in sentences:
        s = s[0]
        words = sentenceToWords(s)
        for w in words:
            try:
                word_count[w] += 1
            except:
                word_count[w] = 1

    # now sort
    sorted_words = sorted(word_count.items(),
                      key=itemgetter(1),
                      reverse=True)

    # now output dictionary with key=word value=rank
    word_rank = {}
    for i,w in enumerate(sorted_words):
        word_rank[w[0]] = i + 1

    return word_rank

def sentenceToWords(sentence):
    """
    Splits a sentence into a list of words
    """
    # make lowercase
    s = sentence.lower()

    # strip punctuation
    import string
    s = s.translate(string.maketrans("",""), string.punctuation)

    words = s.split(" ")
    return words

def computeScore(sentences,word_rank):
    """
    Computes a score for each sentence. This is stored as a dictionary where the
    key is the sentence id and the value is the score

    The score is computing by summing the rank of the words. When this is sorted
    then we will get sentences with smaller ammounts of high frequency words
    """
    print "Computing best sentences..."

    scores = []
    for i,s in enumerate(sentences):
        words = sentenceToWords(s[0])

        score = 0
        for w in words:
            try:
                score += word_rank[w]
            except:
                print "Not in dictionary"
                pass # wasn't able to find the word in the dictionary

        scores.append((i,score))

    # now sort by scores
    scores.sort(key=itemgetter(1))
    return scores

main()
