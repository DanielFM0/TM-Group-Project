import csv


""" PRELIMINARIES 
    
    This is laid out to work with the 1.6 Million Tweets dataset (https://www.kaggle.com/kazanova/sentiment140) in CSV format,
    saved as "all_tweets.csv" in the same folder as this file.
    
"""
CREATE_POSITIVE_AND_NEGATIVE_CSVS = True

if CREATE_POSITIVE_AND_NEGATIVE_CSVS:

    with open("all_tweets.csv", mode="r", newline="", encoding="latin-1") as all_tweets,\
            open("negative_tweets.csv", mode="w", newline='', encoding="UTF8") as negative_tweets,\
            open("neutral_tweets.csv", mode="w", newline='', encoding="UTF8") as neutral_tweets,\
            open("positive_tweets.csv", mode="w", newline='', encoding="UTF8") as positive_tweets:
        tweet_lines = [[cell.strip(', "') for cell in line.split('"') if cell.strip(", ")
                        and cell not in {"\r\n", "\n"}] for line in all_tweets.readlines()]   # [:100]

        pos_writer = csv.writer(positive_tweets)
        neut_writer = csv.writer(neutral_tweets)
        neg_writer = csv.writer(negative_tweets)

        for row in tweet_lines:
            row_reduced = [int(row[0])//4, row[5]]
            if row[0] == '0':
                neg_writer.writerow(row_reduced)
            elif row[0] == '2':
                neut_writer.writerow(row_reduced)
            elif row[0] == '4':
                pos_writer.writerow(row_reduced)

# Test to verify equal ratio of positive and negative tweets
RATIO_TEST = True

if RATIO_TEST:
    with open("negative_tweets.csv", mode="r", newline='', encoding="UTF8") as negative_tweets,\
        open("neutral_tweets.csv", mode="r", newline='', encoding="UTF8") as neutral_tweets,\
            open("positive_tweets.csv", mode="r", newline='', encoding="UTF8") as positive_tweets:

        print("POS: ", len(positive_tweets.readlines()))
        print("NEUT: ", len(neutral_tweets.readlines()))
        print("NEG: ", len(negative_tweets.readlines()))


""" FILTERING """
FILTERING = True

def concatenate(list_of_lists):
    result = ""
    for some_list in list_of_lists:
        result += some_list
    return result

""" To dos: 
    1. Make sure backslashes are removed
    2. Make sure \n and \r\n are removed
    3. lemmatization, Tokenization
    4. Sentiment analysis to verify present classification
    5. Compare words in tweets to loadword datasets
    6. Save results! Runtime will be long! 
"""

if FILTERING:
    with open("negative_tweets.csv", mode="r", newline='', encoding="UTF8") as negative_tweets,\
        open("neutral_tweets.csv", mode="r", newline='', encoding="UTF8") as neutral_tweets,\
            open("positive_tweets.csv", mode="r", newline='', encoding="UTF8") as positive_tweets:
        neg_lines = [[line.split(",")[0].strip('"\''), concatenate(line.split(",")[1:])]
                     for line in negative_tweets.readlines()]
        for line in neg_lines:
            print(line)
