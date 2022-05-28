import csv
import re
from nltk.tokenize import word_tokenize


""" PRELIMINARIES """
CREATE_POSITIVE_AND_NEGATIVE_CSVS = False

if CREATE_POSITIVE_AND_NEGATIVE_CSVS:

    with open("all_tweets.csv", mode="r", newline="", encoding="latin-1") as all_tweets,\
            open("negative_tweets.csv", mode="w", newline='', encoding="UTF8") as negative_tweets,\
            open("positive_tweets.csv", mode="w", newline='', encoding="UTF8") as positive_tweets:
        tweet_lines = [[cell.strip(', "') for cell in line.split('"') if cell.strip(", ")
                        and cell not in {"\r\n", "\n"}] for line in all_tweets.readlines()]   # [:100]

        pos_writer = csv.writer(positive_tweets)
        neg_writer = csv.writer(negative_tweets)

        for row in tweet_lines:
            row_reduced = [int(row[0])//4, row[5]]
            if row[0] == '0':
                neg_writer.writerow(row_reduced)
            elif row[0] == '4':
                pos_writer.writerow(row_reduced)

# Test to verify equal ratio of positive and negative tweets
RATIO_TEST = False

if RATIO_TEST:
    with open("negative_tweets.csv", mode="r", newline='', encoding="UTF8") as negative_tweets,\
            open("positive_tweets.csv", mode="r", newline='', encoding="UTF8") as positive_tweets:

        print("POS: ", len(positive_tweets.readlines()))
        print("NEG: ", len(negative_tweets.readlines()))


""" FILTERING """


def los_to_string(list_of_strings):
    result_string = ""
    for s in list_of_strings:
        result_string += s
    return result_string


def has_characters(s):
    return bool(re.search(".*[a-z].*", s))


def string_remove(s, c):
    my_table = s.maketrans(c, '#')
    return_s = ""
    for char in s.translate(my_table):
        if char != '#':
            return_s += char
    return return_s


def remove_junk(s):
    if '\n' in s:
        s = string_remove(s, '\n')
    if '\r' in s:
        s = string_remove(s, '\r')
    if '\t' in s:
        s = string_remove(s, '\t')
    return s


""" To dos: 
    1. Make sure backslashes are removed
    2. Make sure \n and \r\n are removed
    3. lemmatization, Tokenization
    4. Sentiment analysis to verify present classification
    5. Compare words in tweets to loadword datasets
    6. Save results! Runtime will be long! 
"""

excluded_tokens = {} #{'the', 'to', 'be', 'of', 'and', 'are', 'am', 'a', 'm', 'in', 'that', 'have', 'I', 'it', 'on',
                   #'for', 'not', 'if', 'with', 'he', 'she', 'as', 'you', 'do', 'at', 'this', 'his', 'what', 'an',
                   #'her', 'but', 'by', 'from', 'they', 'we', 'say', 'or', 'me', 'will', 'my', 'all', 'our', 'well'
                   #'got', 'here', 'were', 'so', 'up', 'out', 'about', 'who', 'get', 'which', 'go', 'me', 'way',
                   #'when', 'make', 'no', 'can', 'like', 'time', 'into', 'people', 'could', 'then', 'than', 'even',
                   #'were', 'been', 'had', 'now', 'only', 'come', 'its', 'also', 'think', 'back', 'after', 'use'}


def filter_lines(lines):
    tweet_tokens = []
    for line in lines:
        tokens = [token.lower() for token in word_tokenize(remove_junk(line[1]))
                  if token not in excluded_tokens]
        tweet_tokens.append([t for t in tokens if has_characters(t)])
    return tweet_tokens


FILTERING = True
SCAN_LOANWORDS = True

english_source_langs = ["Dutch", "French", "German", "Latin", "Portuguese"]

with open("negative_tweets.csv", mode="r", newline='', encoding="UTF8") as negative_tweets,\
        open("positive_tweets.csv", mode="r", newline='', encoding="UTF8") as positive_tweets:

    if FILTERING:
        neg_lines = [[line.split(",")[0].strip('"\''), los_to_string(line.split(",")[1:])]
                     for line in negative_tweets.readlines()]
        pos_lines = [[line.split(",")[0].strip('"\''), los_to_string(line.split(",")[1:])]
                     for line in positive_tweets.readlines()]

        neg_tokens = filter_lines(neg_lines[:100])
        pos_tokens = filter_lines(pos_lines[:100])

    if FILTERING and SCAN_LOANWORDS:
        loan_word_dict = {}
        source_lang_sent_count = {lang: [0, 0] for lang in english_source_langs}
        for source_lang in english_source_langs:
            with open("data/processed/English"+source_lang+".csv", mode="r", encoding="UTF8") as file:
                reader = csv.reader(file)
                loan_word_dict[source_lang] = [line[0] for line in reader]

        for pos_or_not in [0, 1]:
            for tweet_token_list in [neg_tokens, pos_tokens][pos_or_not]:
                for token in tweet_token_list:
                    for lang in english_source_langs:
                        if token in loan_word_dict[lang]:
                            if pos_or_not:
                                source_lang_sent_count[lang][0] += 1
                            else:  # negative tweet tokens
                                source_lang_sent_count[lang][1] += 1

        print(source_lang_sent_count)
