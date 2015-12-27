import urllib
import tarfile
import os
from operator import itemgetter
import csv

# PARAMS
MAX_SENTENCES = 5000000


class SentenceScorer():
    def __init__(self, lang1, lang2, output_number, outfile):
        self.lang1 = lang1
        self.lang2 = lang2
        self.output_number = output_number
        self.outfile = outfile

    def sendMessage(self, msg):
        """
        Function to send progress messages
        """
        print msg

    def generateScore(self):
        self.run()

    def run(self):
        """
        Main function to generate everything
        """
        # load data
        sentences = self.loadData()

        # check if sentences
        if len(sentences) == 0:
            self.sendMessage("Error: No sentences for this configuration")
            return

        # compute word rank
        word_rank = self.computeFrequency(sentences)

        # score all sentences
        sentence_score = self.computeScore(sentences, word_rank)

        # now simply pop off sentences
        with open(self.outfile, 'w') as f:
            writer = csv.writer(f)

            for i in range(self.output_number):
                try:
                    s_ind = sentence_score.pop(0)
                except:
                    break
                s = sentences[s_ind[0]]

                writer.writerow(s)

        self.sendMessage("Done")
        self.exiting = True

    def loadData(self):
        """
        Loads the sentences from tatoeba
        """

        # if data is not downloaded, the download
        sentence_path = (
            "http://downloads.tatoeba.org/exports/sentences.tar.bz2")
        if not os.path.isfile("sentences.csv"):
            sentence_file = urllib.URLopener()
            self.sendMessage("Downloading sentences...")
            sentence_file.retrieve(sentence_path, "sentences.tar.gz")
            tar = tarfile.open("sentences.tar.gz")
            tar.extractall()
            tar.close()
            os.remove("sentences.tar.gz")

        link_path = "http://downloads.tatoeba.org/exports/links.tar.bz2"
        if not os.path.isfile("links.csv"):
            link_file = urllib.URLopener()
            self.sendMessage("Downloading links...")
            link_file.retrieve(link_path, "links.tar.gz")
            tar = tarfile.open("links.tar.gz")
            tar.extractall()
            tar.close()
            os.remove("links.tar.gz")

        # now load all of the sentences in our target languages
        sentences = {}
        with open("sentences.csv", "r") as ins:
            self.sendMessage("Getting sentences in chosen languages...")
            for line in ins:
                line = line[0:-1]   # gets rid of newline
                split = line.split("\t")
                if split[1] == self.lang1 or split[1] == self.lang2:
                    sentences[split[0]] = (split[1], split[2])

                if len(sentences) > MAX_SENTENCES:
                    print "Reached sentence limit"
                    break

        # now get the pairs in our languages
        # lang1 is first
        pairs = []
        dupes = {}
        with open("links.csv") as ins:
            self.sendMessage("Computing pairs...")
            for line in ins:
                line = line[0:-1]  # gets rid of newline
                split = line.split("\t")
                if split[0] in sentences and split[1] in sentences:
                    if sentences[split[0]][0] == self.lang1:
                        # if sentences are the same, flag as a duplicate
                        if sentences[split[0]][0] == sentences[split[1]][0]:
                            dupes[max(split[0], split[0])] = 1
                            continue

                        if split[0] not in dupes:
                            pairs.append((sentences[split[0]][1],
                                          sentences[split[1]][1]))

        return pairs

    def computeFrequency(self, sentences):
        """
        Computes the word frequency

        Returns a large dictionary where the keys are the word, and the
        value is the rank
        """
        self.sendMessage("Counting words...")

        # first count word frequencies
        word_count = {}
        for s in sentences:
            s = s[0]
            words = self.sentenceToWords(s)
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
        for i, w in enumerate(sorted_words):
            word_rank[w[0]] = i + 1

        return word_rank

    def sentenceToWords(self, sentence):
        """
        Splits a sentence into a list of words
        """
        # make lowercase
        s = sentence.lower()

        # strip punctuation
        import string
        s = s.translate(string.maketrans("", ""), string.punctuation)

        words = s.split(" ")
        return words

    def computeScore(self, sentences, word_rank):
        """
        Computes a score for each sentence. This is stored as a
        dictionary where the key is the sentence id and the value is
        the score

        The score is computing by summing the rank of the words. When
        this is sorted then we will get sentences with smaller
        ammounts of high frequency words
        """
        self.sendMessage("Computing best sentences...")

        scores = []
        for i, s in enumerate(sentences):
            words = self.sentenceToWords(s[0])

            score = 0
            for w in words:
                try:
                    score += word_rank[w]
                except:
                    print "Not in dictionary"
                    pass  # wasn't able to find the word in the dictionary

            scores.append((i, score))

        # now sort by scores
        scores.sort(key=itemgetter(1))
        return scores
