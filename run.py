"""
Tatoeba sentence extractor
"""
import urllib
import tarfile
import os

# PARAMS
MAX_SENTENCES = 10000

def main():
    # load data
    sentences = loadData("kor","eng")
    import ipdb; ipdb.set_trace()

    # compute frequency
    word_freq = computeFrequency(sentences)

    # score all sentences
    sentence_score = computeScore(setences,word_freq)

    # now simply pop off as much as you want
    f.open()
    for i in range(N):
        s = sentence_score.pop()

        writeToCSV(f,s)

    f.close()

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
    with open("links.csv") as ins:
        print "Computing pairs..."
        for line in ins:
            line = line[0:-1] # gets rid of newline
            split = line.split("\t")
            if split[0] in sentences and split[1] in sentences:
                if sentences[split[0]][0] == lang1:
                    pairs.append((sentences[split[0]][1], sentences[split[1]][1]))
                else:
                    pairs.append((sentences[split[1]][1], sentences[split[0]][1]))
                    
    return pairs

def computeFrequency(setences):
    """
    Computes the word frequency

    Returns a large dictionary where the keys are the word, and the
    value is the rank
    """
    pass

main()
