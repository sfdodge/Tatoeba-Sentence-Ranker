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
import sys
import urllib2
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# PARAMS
MAX_SENTENCES = 5000000
OUTPUT_NUMBER = 1000
OUTFILE = 'output.csv'

class SentenceScorer(QThread):
    def __init__(self,lang1,lang2,parent = None):
        #super(SentenceScorer, self).__init__()
        QThread.__init__(self,parent)
        self.exiting = False

        self.lang1 = lang1
        self.lang2 = lang2

    def sendMessage(self,msg):
        """
        Function to send progress messages
        """
        print msg
        self.emit(SIGNAL("message"), msg)

    def generateScore(self):
        self.start() # start qt thread
        
    def run(self):
        """
        Main function to generate everything
        """
        # load data
        sentences = self.loadData()

        # compute word rank
        word_rank = self.computeFrequency(sentences)

        # score all sentences
        sentence_score = self.computeScore(sentences,word_rank)

        # now simply pop off sentences
        with open(OUTFILE, 'w') as f:
            writer=csv.writer(f)

            for i in range(OUTPUT_NUMBER):
                s_ind = sentence_score.pop(0)
                s = sentences[s_ind[0]]

                writer.writerow(s)

        self.sendMessage("Done...Output is in output.csv")
        self.exiting = True

    def loadData(self):
        """
        Loads the sentences from tatoeba
        """

        # if data is not downloaded, the download
        sentence_path = "http://downloads.tatoeba.org/exports/sentences.tar.bz2"
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
                    sentences[split[0]] = (split[1],split[2])

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
                line = line[0:-1] # gets rid of newline
                split = line.split("\t")
                if split[0] in sentences and split[1] in sentences:
                    if sentences[split[0]][0] == self.lang1:
                        # if sentences are the same, flag as a duplicate
                        if sentences[split[0]][0] == sentences[split[1]][0]:
                            dupes[max(split[0],split[0])] = 1
                            continue 

                        if split[0] not in dupes:
                            pairs.append((sentences[split[0]][1], sentences[split[1]][1]))

        return pairs

    def computeFrequency(self,sentences):
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
        for i,w in enumerate(sorted_words):
            word_rank[w[0]] = i + 1

        return word_rank

    def sentenceToWords(self,sentence):
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

    def computeScore(self,sentences,word_rank):
        """
        Computes a score for each sentence. This is stored as a dictionary where the
        key is the sentence id and the value is the score

        The score is computing by summing the rank of the words. When this is sorted
        then we will get sentences with smaller ammounts of high frequency words
        """
        self.sendMessage("Computing best sentences...")

        scores = []
        for i,s in enumerate(sentences):
            words = self.sentenceToWords(s[0])

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


    def __del__(self):
        self.exiting = True
        self.wait()


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)


        langs = ('English',
                 'French',
                 'Spanish',
                 'Italian',
                 'German',
                 'Dutch',
                 'Portugese',
                 'Greek',
                 'Russian',
                 'Arabic',
                 'Chinese',
                 'Japanese',
                 'Korean',
                 'Thai')

        self.fromComboBox = QComboBox()
        self.fromComboBox.addItems(langs)
        #self.fromComboBox.setValue('English')
        self.fromSpinBox = QDoubleSpinBox()
        self.fromSpinBox.setRange(1, 100000)
        self.fromSpinBox.setValue(1000)
        self.toComboBox = QComboBox()
        self.toComboBox.addItems(langs)
        #self.toComboBox.setValue('Spanish')
        self.statusLabel = QLabel("")
        self.generateButton = QPushButton('Generate...')
        self.generateButton.clicked.connect(self.generate)

        grid = QGridLayout()
        grid.addWidget(self.fromComboBox, 0, 0)
        grid.addWidget(self.fromSpinBox, 0, 1)
        grid.addWidget(self.toComboBox, 1, 0)
        grid.addWidget(self.generateButton,2,1)
        grid.addWidget(self.statusLabel, 2, 0)
        self.setLayout(grid)

        self.setWindowTitle("Tatoeba Sentence Generator")

        self.scorer = SentenceScorer('fra','eng')
        self.connect(self.scorer,SIGNAL('message'),self.statusLabel.setText)

    def generate(self):
        self.generateButton.setDisabled(True)
        self.scorer.generateScore()
        self.generateButton.setEnabled(True)

app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
