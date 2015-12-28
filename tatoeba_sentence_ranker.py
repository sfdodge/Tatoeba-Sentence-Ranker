"""
Tatoeba sentence extractor

Extracts sentences and orders them such that setences with more
frequent words come first

To do:
1. Compile exe?
2. add support for japanese/chinese
"""
import sys
try:
    from QT_interface import Form, QTSentenceScorer
    USE_QT = True
except:
    from sentence_scorer import SentenceScorer
    USE_QT = False

VERSION = 1.0

# Available Languages
from language_list import LANGUAGES


def console_main():
    """
    Run program from console
    """
    print "=" * 60
    print "Tatoeba sentence ranker - Version " + str(VERSION)
    print "=" * 60

    source = ""
    while True:
        source = raw_input(
            "Source language? (Enter for default English)").title()

        if source == "":
            print "Using default English"
            source = "English"

        if source not in LANGUAGES.keys():
            print "Invalid language"
            print "Available languages:"
            print [l for l in sorted(LANGUAGES.keys())]
        else:
            break

    target = ""
    while True:
        target = raw_input("Target language?").title()

        if target not in LANGUAGES.keys():
            print "Invalid language"
            print "Available languages:"
            print [l for l in sorted(LANGUAGES.keys())]
        else:
            break

    number = 0
    while True:
        number = raw_input(
            "How many sentences to rank? (Enter for default 1000)")

        if number == "":
            print "Using default 1000 sentences"
            number = 1000
            break

        if not number.isdigit():
            print "Should be an integer number"
        else:
            number = int(number)
            break

    outfile_name = ""
    while True:
        outfile_name = raw_input(
            "Output filename: (Enter for default output.csv)")

        if outfile_name == "":
            print "Using default name output.csv"
            outfile_name = "output.csv"
            break

        try:
            file = open(outfile_name, 'r+')
            break
        except IOError:
            print 'Please enter a valid file name'

    # now finally generate the sentences
    print "=" * 60
    scorer = SentenceScorer(LANGUAGES[target],
                            LANGUAGES[source],
                            number,
                            outfile_name)
    scorer.generateScore()


############################################################
if __name__ == "__main__":
    if USE_QT:
        from PyQt4.QtGui import QApplication
        app = QApplication(sys.argv)
        form = Form()
        form.show()
        app.exec_()
    else:
        console_main()
