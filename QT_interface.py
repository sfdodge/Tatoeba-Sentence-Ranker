from language_list import LANGUAGES
from sentence_scorer import SentenceScorer
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class QTSentenceScorer(SentenceScorer, QThread):
    """
    Subclass with ability to send QT messages, and work as a QT thread
    """
    def __init__(self, lang1, lang2, output_number, outfile, parent=None):
        QThread.__init__(self, parent)
        SentenceScorer.__init__(self, lang1, lang2, output_number, outfile)
        self.exiting = False

    def sendMessage(self, msg):
        """
        Function to send progress messages
        """
        print msg
        self.emit(SIGNAL("message"), msg)

    def sendError(self, err):
        """
        Function to send error
        """
        print err
        self.emit(SIGNAL("error"), err)

    def generateScore(self):
        self.start()  # start qt thread

    def __del__(self):
        self.exiting = True
        self.wait()


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.fromComboBox = QComboBox()
        self.fromComboBox.addItems(sorted(LANGUAGES.keys()))
        english_index = self.fromComboBox.findText(u"English")
        self.fromComboBox.setCurrentIndex(english_index)

        self.toComboBox = QComboBox()
        self.toComboBox.addItems(sorted(LANGUAGES.keys()))
        spanish_index = self.toComboBox.findText(u"Spanish")
        self.toComboBox.setCurrentIndex(spanish_index)

        self.nSentenceField = QSpinBox()
        self.nSentenceField.setRange(1, 100000)
        self.nSentenceField.setValue(1000)
        self.fromLabel = QLabel("Source")
        self.toLabel = QLabel("Target")
        self.nSentenceLabel = QLabel("Number of sentences")
        self.generateButton = QPushButton('Generate...')
        self.generateButton.clicked.connect(self.generate)

        grid = QGridLayout()
        grid.addWidget(self.fromLabel, 0, 0)
        grid.addWidget(self.fromComboBox, 0, 1)
        grid.addWidget(self.toLabel, 1, 0)
        grid.addWidget(self.toComboBox, 1, 1)
        grid.addWidget(self.nSentenceLabel, 2, 0)
        grid.addWidget(self.nSentenceField, 2, 1)
        grid.addWidget(self.generateButton, 3, 1)
        self.setLayout(grid)

        self.setWindowTitle("Tatoeba Sentence Ranker")

        self.setFixedSize(QSize(400, 150))

    def generate(self):
        # get filename
        fileName = QFileDialog.getSaveFileName(self,
                                               'Save',
                                               directory="output.csv",
                                               selectedFilter='*.csv')
        if not fileName:
            return

        # get parameters
        lang1 = unicode(self.fromComboBox.currentText().toUtf8(),
                        encoding="UTF-8")
        lang2 = unicode(self.toComboBox.currentText().toUtf8(),
                        encoding="UTF-8")
        num = int(self.nSentenceField.value())

        self.progressDialog = QProgressDialog("Running...",
                                              QString(),
                                              0,
                                              6,
                                              parent=self)
        self.progressDialog.setWindowModality(Qt.WindowModal)
        self.progressDialog.show()

        self.scorer = QTSentenceScorer(LANGUAGES[lang2],
                                       LANGUAGES[lang1],
                                       num,
                                       fileName)
        self.connect(self.scorer, SIGNAL('message'), self.incrementProgress)
        self.connect(self.scorer, SIGNAL('message'), self.progressDialog.setLabelText)
        self.connect(self.scorer, SIGNAL('error'), self.showError)
        self.scorer.generateScore()

    def incrementProgress(self):
        """
        Increment progress bar
        """
        self.progressDialog.setValue(self.progressDialog.value()+1)

    def showError(self, err):
        """
        Popup error message
        """
        self.progressDialog.setValue(6)
        message = QErrorMessage(parent=self)
        message.showMessage(err)


def debug_trace():
    """
    Set a tracepoint in the Python debugger that works with Qt

    From: http://stackoverflow.com/questions/1736015/debugging-a-pyqt4-app
    """
    from PyQt4.QtCore import pyqtRemoveInputHook

    # Or for Qt5
    # from PyQt5.QtCore import pyqtRemoveInputHook

    from pdb import set_trace
    pyqtRemoveInputHook()
    set_trace()
