# Tatoeba Sentence Ranker

This is a simple Python script to rank sentences from Tatoeba.org such that the earlier sentences contain more common words and the latter sentences contain more rare words.

Often people say that the most common 1000 words in a language appear 80% (or something like that) of the time in speech or writing. So the obvious thing to do is to create flashcards (using a program like Anki) on these 1000 words. However, by only studying words the grammar and nuance of meaning is completely ignored. I've found that it is better to study sentences because they give a more appropriate meaning (due to context), as well as show the grammar.

I wrote this script to generate sentences for studying languages. The idea is that early sentences should be simpler/easier and progressively get more difficult. The sentences are sourced from Tatoeba.org which provides many translations of simple sentences and words.

To rank the sentence first the most common words are found. The most common word has a score of 1, the second most common has a score of 2, etc. To compute a score for a sentence the scores of the individual words are added. Sentences with lower scores will be shorter and contain more common words. The sentences are sorted according to this order and output to a csv file.

---------------------
## Installation

This script was tested on Python 2.7.

For GUI you need to have PyQT installed. If PyQT is not installed the program will run from the terminal. (Eventually I will distribute an exe for people who don't have python installed.

--------------------
## Running

Run with "python tatoeba_sentence_ranker.py

---------------------
## Known issues

The program uses spaces to determine words, so this will not work with languages that don't use spaces (Eg: Chinese and Japanese)