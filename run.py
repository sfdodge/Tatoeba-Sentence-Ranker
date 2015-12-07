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
    sentences = loadData("spa","eng")

    # compute word rank
    word_rank = computeFrequency(sentences)

    # score all sentences
    sentence_score = computeScore(setences,word_rank)

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
                if sentences[split[0]][0] == sentences[split[1]][0]:
                    continue # the languages are the same
                    
                if sentences[split[0]][0] == lang1:
                    pairs.append((sentences[split[0]][1], sentences[split[1]][1]))
                else:
                    pairs.append((sentences[split[1]][1], sentences[split[0]][1]))
                    
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
        # make lowercase
        s = s.lower()

        # strip punctuation
        import string
        s = s.translate(string.maketrans("",""), string.punctuation)

        words = s.split(" ")
        for w in words:
            try:
                word_count[w] += 1
            except:
                word_count[w] = 1

    # now sort
    import operator
    sorted_words = sorted(word_count.items(),
                      key=operator.itemgetter(1),
                      reverse=True)

    # now output dictionary with key=word value=rank
    word_rank = {}
    for i,w in enumerate(sorted_words):
        word_rank[w[0]] = i + 1

    return word_rank

main()
