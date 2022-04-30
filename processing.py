import csv
from numpy import sign

words_sentiment = {}

# opinion lexicon processing
with open('data/raw/opinion-lexicon-English/negative-words.txt', encoding='ibm852') as text:
    words = text.readlines()
    for word in words[31:]:
        word = word[:-1]
        word = word.replace('-', ' ')
        word = word.replace('_', ' ')
        words_sentiment[word] = -1
with open('data/raw/opinion-lexicon-English/positive-words.txt', encoding='ibm852') as text:
    words = text.readlines()
    for word in words[30:]:
        word = word[:-1]
        word = word.replace('-', ' ')
        word = word.replace('_', ' ')
        words_sentiment[word] = 1

# SentiWordNet processing
# WARNING: THIS HAS A LOT OF WORDS, BUT THEY SEEM OF A LOWER QUALITY, SO FOR NOW
# IGNORE THESE. WE CAN USE THEM IF WE FIND WE HAVE TOO LITTLE WORDS
# with open('data/raw/SentiWordNet_3.0.0.txt', encoding='utf-8') as text:
#     text_lines = text.readlines()
#     for line in text_lines[26:-1]:
#         elements = line.split()
#         pos_score = float(elements[2])
#         neg_score = float(elements[3])
#         # some lines have multiple words, but for now those can be ignored
#         # some words also appear multiple times, but for now that can also be ignored
#         word = elements[4]
#         # remove the #num part
#         word = word[:word.find('#')]
#         word = word.replace('-', ' ')
#         word = word.replace('_', ' ')
#         # words that are not in the dict are considered to be neutral
#         if ((pos_score == 0 and neg_score == 0) or pos_score == neg_score):
#             continue
#         else:
#             words_sentiment[word] = int(sign(pos_score - neg_score))

# subjclueslen1-HLTEMNLP05 processing
with open('data/raw/subjclueslen1-HLTEMNLP05.tff', encoding='utf-8') as text:
    text_lines = text.readlines()
    for line in text_lines[:12]:
        elements = line.split()
        sentiment = elements[-1][14:]
        if sentiment == 'negative':
            sentiment = -1
        elif sentiment == 'positive':
            sentiment = 1
        else:
            continue
        word = elements[2][6:]
        word = word.replace('-', ' ')
        word = word.replace('_', ' ')
        words_sentiment[word] = sentiment

# Write csv file
with open('data/processed/words_sentiment.csv', mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(['Word', 'Sentiment'])

    keys = list(words_sentiment.keys())
    keys.sort()
    csv_writer.writerows([[key, words_sentiment[key]] for key in keys])