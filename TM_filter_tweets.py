import csv
import re
from nltk.tokenize import word_tokenize
from random import choice



""" PRELIMINARIES 
    (in the following, let:         * := "for both positive and negative tweets"; 
                                    SL = "source language"
    )
                                    
    This program executes the following steps:
    
        1. Split 16_000_000 tweets dataset into positive- and negative tweets 
        2. Print their ratio if desired (should be 50:50)
        3. Makes use of Loanword-Datasets while iterating through the tokenized tweets...
            3.1 ...in order to find the absolute number of loanword matches *
            3.2 ...in order to find the number of times a SL has the most loanwords in a tweet * ...
                3.2.1 ...using randomness in case of a tie
                3.2.2 ...using fractions in case of a tie
                3.2.3 ...ignoring ties
            3.3 ...in order to find the percentage of tokens from every SL *
"""
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

excluded_tokens = {}#{'the', 'to', 'be', 'of', 'and', 'are', 'am', 'a', 'm', 'in', 'that', 'have', 'I', 'it', 'on',
                   #'for', 'not', 'if', 'with', 'he', 'she', 'as', 'you', 'do', 'at', 'this', 'his', 'what', 'an',
                   #'her', 'but', 'by', 'from', 'they', 'we', 'say', 'or', 'me', 'will', 'my', 'all', 'our', 'well'
                   #'got', 'here', 'were', 'so', 'up', 'out', 'about', 'who', 'get', 'which', 'go', 'me', 'way',
                   #'when', 'make', 'no', 'can', 'like', 'time', 'into', 'people', 'could', 'then', 'than', 'even',
                   #'were', 'been', 'had', 'now', 'only', 'come', 'its', 'also', 'think', 'back', 'after', 'use'}

def find_highest(dictionary):
    """ Takes a dict that matches keys to positive integers.
            : no index is > 0:
                        returns empty list []                   type = list
            : highest index is > 0 and unique:
                        returns key as string                   type = string
            : multiple identical maximum indexes were found:
                        returns list of keys to these indexes   type = list
    """
    current_max = 0
    key_keys = []
    remain_zero = True
    for key in dictionary:
        n = dictionary[key]
        if current_max < n:
            remain_zero = False
            current_max = n
            key_keys = [key]
        elif current_max == n:
            key_keys.append(key)
    if len(key_keys) == 1:
        return key_keys[0]
    elif remain_zero:
        return []
    return key_keys


def filter_lines(lines):
    tweet_tokens = []
    for line in lines:
        tokens = [token.lower() for token in word_tokenize(remove_junk(line[1]))
                  if token not in excluded_tokens]
        tweet_tokens.append([t for t in tokens if has_characters(t)])
    return tweet_tokens


FILTERING = True
SCAN_LOANWORDS = True

settings = ["ABSOLUTE", "DOMINANT RANDOM", "DOMINANT FRACTION", "DOMINANT IGNORE", "TOTAL FRAC IN %"]
english_source_langs = ["Dutch", "French", "German", "Latin", "Portuguese"]

with open("negative_tweets.csv", mode="r", newline='', encoding="UTF8") as negative_tweets,\
        open("positive_tweets.csv", mode="r", newline='', encoding="UTF8") as positive_tweets:

    if FILTERING:
        neg_lines = [[line.split(",")[0].strip('"\''), los_to_string(line.split(",")[1:])]
                     for line in negative_tweets.readlines()]
        pos_lines = [[line.split(",")[0].strip('"\''), los_to_string(line.split(",")[1:])]
                     for line in positive_tweets.readlines()]

        neg_tokens = filter_lines(neg_lines) # neg_lines[:1200]
        pos_tokens = filter_lines(pos_lines) # # pos_lines[:1200]

    if SCAN_LOANWORDS and FILTERING:
        loan_word_dict = {}
        data_dict = {setting: {lang: [0, 0] for lang in english_source_langs} for setting in settings}
        for source_lang in english_source_langs:
            with open("data/processed/English"+source_lang, mode="r", encoding="UTF8") as file:
                reader = csv.reader(file)
                loan_word_dict[source_lang] = [line[0] for line in reader]

        for pos_or_not in [0, 1]:
            total_tokens = 0 # keep track of total tokens for TOTAL FRACTION IN PCT
            for tweet_token_list in [pos_tokens, neg_tokens][pos_or_not]: # list of tokens of one tweet
                nb_tokens = len(tweet_token_list)    # update token count
                total_tokens += nb_tokens            #
                occurrence_dict = {lang: 0 for lang in english_source_langs}    # saves nb of times that a
                                                                                # token matches a source language
                for token in tweet_token_list:
                    for lang in english_source_langs:
                        if token in loan_word_dict[lang]:
                            data_dict["ABSOLUTE"][lang][pos_or_not] += 1    # save absolute nb of matches per language
                            occurrence_dict[lang] += 1  # update count
                dominant_langs = find_highest(occurrence_dict)
                if isinstance(dominant_langs, str):     # in case of a single most dominant source language
                    for dominant in ["RANDOM", "FRACTION", "IGNORE"]:   # add one to all dominant counting methods
                        data_dict["DOMINANT "+dominant][dominant_langs][pos_or_not] += 1
                elif len(dominant_langs) > 0:   # if multiple highest numbers were found:
                    data_dict["DOMINANT RANDOM"][choice(dominant_langs)][pos_or_not] += 1 # update DOMINANT RANDOM count
                                                                                          # for randomly chosen language
                    for lang in dominant_langs:         # update DOMINANT FRACTION count for all languages
                        data_dict["DOMINANT FRACTION"][lang][pos_or_not] += 1/len(dominant_langs)
            for lang in english_source_langs:   # update fraction of all tokens that stem from each source language...
                data_dict["TOTAL FRAC IN %"][lang][pos_or_not] \
                    = 100*data_dict["ABSOLUTE"][lang][pos_or_not]/total_tokens # ...for both pos. and neg. contexts


''' SAVE RESULTS TO CSV FILE'''

SAVE = True

if SAVE and FILTERING:
    with open("results_tweet_analysis.csv", mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['', "ABSOLUTE", '', "DOMINANT: RND", '', "DOMINANT: FRAC", '',
                        "DOMINANT: IGN", '', "TOTAL PCT", ''])
        writer.writerow(["LANGUAGE"]+5*["positives", "negatives"])
        for lang in english_source_langs:
            row = [lang]
            for setting in settings:
                neg_pos_tpl = data_dict[setting][lang]
                for val in neg_pos_tpl:
                    if isinstance(val, float):
                        row.append(float(f'{val:.4f}'))
                    else:
                        row.append(float(val))
            writer.writerow(row)

PRINT = True

if PRINT and FILTERING:
    for setting in settings:
        print(setting+": "+str(data_dict[setting]))
