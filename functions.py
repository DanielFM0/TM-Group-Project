import csv
import numpy as np
import matplotlib.pyplot as plt
from googletrans import Translator
from bs4 import BeautifulSoup
import requests
from nltk.tokenize import word_tokenize
from random import choice
import re
""" Terminal Command for correct installation: 
pip3 install googletrans==3.1.0a0 
"""

########################## Data collection ####################################


# Website scraping
def scrapeWebsite(url: str) -> None:
    """Scrape the EZGlot webpage given by the url for the words and their origin, then write to csv file.
    """
    words, origins = [], []

    req = requests.get(url)
    # BeautifulSoup makes the html readable and allows useful search functions
    soup = BeautifulSoup(req.text, features="html.parser")

    # Get the languages
    languages = soup.find('h2').text.split('of')
    words.append(languages[1].split()[0])
    origins.append(languages[2].split()[0])

    # Loop through the list of words and their origins
    raw = soup.find('div', class_='relations')
    strings = list(raw.strings)
    for i in range(0, len(strings), 3):
        words.append(strings[i])
        origins.append(strings[i+2])

    # Write the csv file
    with open('data/processed/' + words[0] + origins[0], 'w', encoding='utf-8', newline='') as output:
        writer = csv.writer(output)
        for i in range(len(words)):
            writer.writerow([words[i], origins[i]])

    return None


#scrapeWebsite("https://www.ezglot.com/etymologies.php?l=sqi&l2=tur&submit=Compare")


def scrapeWiktionary(language, origin_language):
    """language/origin_language: formating done automatically. Scrapes the wiktionary language
    """
    language = language.title()
    origin_language = origin_language.title()
    origin_language = origin_language.replace(' ', '_')
    url = 'https://en.wiktionary.org/wiki/Category:' + \
        language + '_terms_derived_from_' + origin_language

    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="html.parser")

    links = soup.find('div', {'id': 'mw-pages'}).find_all('a')
    next = links[-1]['href']
    status = links[-1].text
    words_filtered = []
    while status == 'next page':
        words = []
        words = soup.find('div', {'id': 'mw-pages'}).find("div",
                                                          {"class": "mw-category mw-category-columns"}).text.split('\n')
        for word in words:
            word = word.replace('-', '')
            if word[-1].isupper():
                word = word[:-1]
            if word != '':
                words_filtered.append(word.lower())
        url = 'https://en.wiktionary.org/' + next
        req = requests.get(url)
        soup = BeautifulSoup(req.text, features="html.parser")
        links = soup.find('div', {'id': 'mw-pages'}).find_all('a')
        next = links[-1]['href']
        status = links[-1].text

    with open('data/processed/' + language + origin_language, mode='w', encoding='utf-8', newline='') as output:
        writer = csv.writer(output)
        for i in range(len(words_filtered)):
            writer.writerow([words_filtered[i], 'PLACEHOLDER'])


#scrapeWiktionary('polish', 'german')

# Tweet data


def create_tweets_set(RATIO_TEST):
    """Create the two negative and positive tweet datasets from the original all_tweets file.
    Also print out the ratio if desired, which should be around 50/50.
    """
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
    if RATIO_TEST:
        with open("negative_tweets.csv", mode="r", newline='', encoding="UTF8") as negative_tweets,\
                open("positive_tweets.csv", mode="r", newline='', encoding="UTF8") as positive_tweets:

            print("POS: ", len(positive_tweets.readlines()))
            print("NEG: ", len(negative_tweets.readlines()))


#create_tweets_set()


########################## Data processing ####################################
languages = [
    'albanian',
    'czech',
    'danish',
    'dutch',
    'english',
    'finnish',
    'french',
    'german',
    'hungarian',
    'italian',
    'polish',
    'portuguese',
    'romanian',
    'spanish',
    'swedish']

# Our final sentiment dictionary will be in this dictionary
words_sentiment = {}

# opinion lexicon processing


def oplex_processing(words_sentiment):
    """This function processes the data from our opinion lexicon, by removing dashes and underscores
    and attributing a negative -1 or positive 1 value to the word, and saving this value key pair
    in our dictionary.
    """
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

    return words_sentiment

# SentiWordNet processing


def senti_processing(words_sentiment):
    """Processing for the SentiWordNet data. We split each line since we don't care about the definition or the ID.
    Words were given both a negative or a positive score, so we had to process it differently.
    """
    with open('data/raw/SentiWordNet_3.0.0.txt', encoding='utf-8') as text:
        text_lines = text.readlines()
        for line in text_lines[26:-1]:
            elements = line.split()
            pos_score = float(elements[2])
            neg_score = float(elements[3])
            # some lines have multiple words, but for now those can be ignored
            # some words also appear multiple times, but for now that can also be ignored
            word = elements[4]
            # remove the #num part
            word = word[:word.find('#')]
            word = word.replace('-', ' ')
            word = word.replace('_', ' ')
            # words that are not in the dict are considered to be neutral
            if ((pos_score == 0 and neg_score == 0) or pos_score == neg_score):
                continue
            else:
                words_sentiment[word] = int(sign(pos_score - neg_score))

    return words_sentiment

# subjclueslen1-HLTEMNLP05 processing


def subj_processing(words_sentiment):
    """Processing for our subjclues dataset. It works similarly to our other functions except we have
    to split negative and positive words ourselves.
    """
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

# Write csv file for English sentiment data


#words_sentiment = oplex_processing(words_sentiment)
#words_sentiment = senti_processing(words_sentiment)
#words_sentiment = subj_processing(words_sentiment)


def write_sentiments(word_sentiments):
    with open('data/processed/words_sentiment_english.csv', mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)

        csv_writer.writerow(['Word', 'Sentiment'])

        keys = list(words_sentiment.keys())
        keys.sort()
        csv_writer.writerows([[key, words_sentiment[key]] for key in keys])


#write_sentiments(words_sentiment)


def translate_sentiments(words_sentiment, languages):
    """Translates the words in our words_sentiment to the specified languages and write to the appropriate csv file.
    Since it takes a while we also had it output how far along it was. 
    """

    translator = Translator()

    for lang in languages:
        with open('data/processed/words_sentiment_' + lang + '.csv', mode='w', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)

            csv_writer.writerow(['Word', 'Sentiment'])

            keys = list(words_sentiment.keys())
            keys.sort()

            track = 0
            for key in keys:
                new_key = translator.translate(
                    key, src='english', dest=lang).text
                csv_writer.writerow([new_key, words_sentiment[key]])

                track += 1
                progress = track / len(keys) * 100
                print('%.2f%%' % progress, end='\r')
            print(lang.capitalize() + ' is done!')


#translate_sentiments(words_sentiment, languages)

### Tweet filtering


def los_to_string(list_of_strings):
    """Append a list of strings together
    """
    result_string = ""
    for s in list_of_strings:
        result_string += s
    return result_string


def has_characters(s):
    """Search to see if the string has alphanumeric characters
    """
    return bool(re.search(".*[a-z].*", s))


def string_remove(s, c):
    """Remove all occurrences of a character c in a string s.
    """
    my_table = s.maketrans(c, '#')
    return_s = ""
    for char in s.translate(my_table):
        if char != '#':
            return_s += char
    return return_s


def remove_junk(s):
    """Remove the junk characters, such as \n, from a string
    """
    if '\n' in s:
        s = string_remove(s, '\n')
    if '\r' in s:
        s = string_remove(s, '\r')
    if '\t' in s:
        s = string_remove(s, '\t')
    return s


def find_highest(dictionary):
    """ Takes a dict that matches keys to positive integers.
            : no index is > 0:
                        returns empty list []                   
            : highest index is > 0 and unique:
                        returns key as string                  
            : multiple identical maximum indexes were found:
                        returns list of keys to these indexes   
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
    """Filter the lines given by tokenize them, lowercase and removing junk characters like \n
    """
    tweet_tokens = []
    for line in lines:
        tokens = [token.lower()
                  for token in word_tokenize(remove_junk(line[1]))]
        tweet_tokens.append([t for t in tokens if has_characters(t)])
    return tweet_tokens


########################## Result acquisitions ####################################
# Retrieve sentiment lexicon from the csv file
words_sentiment = {}
for lang in languages:
    with open('data/processed/words_sentiment_' + lang + '.csv', mode='r', newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        current_words_sentiment = {}
        for row in reader:
            current_words_sentiment[row[0]] = row[1]
        del current_words_sentiment['Word']
        words_sentiment[lang] = current_words_sentiment


def print_sent_pct(lang, root_lang):
    """ Takes a string root_lang and locates the corresponding .csv file in the
        processed data folder. Prints out the percentages of loanwords from the
        given root language that are positive/negative according to words_sentiment.
        Words that have no sentiment attributed to them in words_sentiment are assumed
        to be neutral. The percentage of classified (= non neutral) words is printed
        as well.
    """
    with open("data/processed/"+lang+root_lang, encoding="utf-8") as lw_file:
        loan_words = [tpl.split(",")[0] for tpl in lw_file.readlines()[1:]]

        pos, neg, neut = 0, 0, 0
        for lw in loan_words:
            if lw not in words_sentiment[lang.lower()]:
                neut += 1
            elif words_sentiment[lang.lower()][lw] == '1':
                pos += 1
            elif words_sentiment[lang.lower()][lw] == '-1':
                neg += 1

        frac_pos, frac_neg = f"{100*pos/(pos + neg):.2f}", f"{100*neg/(pos + neg):.2f}"
        fraction_classified = f"{100*(pos + neg)/(pos + neg + neut):.2f}"

        fraction_dict = {"a positive": frac_pos,
                         "a negative": frac_neg, "any": fraction_classified}
        for key in fraction_dict:
            print("Fraction of " + lang + " words originating from " + root_lang + " that have " +
                  key + " sentiment: " + fraction_dict[key] + "%.")
        return float(fraction_dict['a negative']) / 100


#print_sent_pct("English", "French")
#print_sent_pct("English", "German")

# Tweet results
settings = ["ABSOLUTE", "DOMINANT RANDOM",
            "DOMINANT FRACTION", "DOMINANT IGNORE", "TOTAL FRAC IN %"]
english_source_langs = ["Dutch", "French", "German", "Latin", "Portuguese"]


def analyze_tweets(settings, english_source_langs):
    """This function works as follows where:  * := "for both positive and negative tweets"; 
                                              SL = "source language":
        1. Makes use of Loanword-Datasets while iterating through the tokenized tweets...
            1.1 ...in order to find the absolute number of loanword matches *
            1.2 ...in order to find the number of times a SL has the most loanwords in a tweet * ...
                1.2.1 ...using randomness in case of a tie
                1.2.2 ...using fractions in case of a tie
                1.2.3 ...ignoring ties
            1.3 ...in order to find the percentage of tokens from every SL *
    """
    with open("negative_tweets.csv", mode="r", newline='', encoding="UTF8") as negative_tweets,\
            open("positive_tweets.csv", mode="r", newline='', encoding="UTF8") as positive_tweets:

        neg_lines = [[line.split(",")[0].strip('"\''), los_to_string(line.split(",")[1:])]
                     for line in negative_tweets.readlines()]
        pos_lines = [[line.split(",")[0].strip('"\''), los_to_string(line.split(",")[1:])]
                     for line in positive_tweets.readlines()]

        neg_tokens = filter_lines(neg_lines)  # neg_lines[:1200]
        pos_tokens = filter_lines(pos_lines)  # pos_lines[:1200]

        loan_word_dict = {}
        data_dict = {setting: {
            lang: [0, 0] for lang in english_source_langs} for setting in settings}
        for source_lang in english_source_langs:
            with open("data/processed/English"+source_lang, mode="r", encoding="UTF8") as file:
                reader = csv.reader(file)
                loan_word_dict[source_lang] = [line[0] for line in reader]

        for pos_or_not in [0, 1]:
            total_tokens = 0  # keep track of total tokens for TOTAL FRACTION IN PCT
            # list of tokens of one tweet
            for tweet_token_list in [pos_tokens, neg_tokens][pos_or_not]:
                nb_tokens = len(tweet_token_list)
                total_tokens += nb_tokens            # update token count
                # saves nb of times that a token matches a source language
                occurrence_dict = {lang: 0 for lang in english_source_langs}
                for token in tweet_token_list:
                    for lang in english_source_langs:
                        if token in loan_word_dict[lang]:
                            # save absolute nb of matches per language
                            data_dict["ABSOLUTE"][lang][pos_or_not] += 1
                            occurrence_dict[lang] += 1  # update count
                dominant_langs = find_highest(occurrence_dict)
                # in case of a single most dominant source language
                if isinstance(dominant_langs, str):
                    # add one to all dominant counting methods
                    for dominant in ["RANDOM", "FRACTION", "IGNORE"]:
                        data_dict["DOMINANT " +
                                  dominant][dominant_langs][pos_or_not] += 1
                # if multiple highest numbers were found:
                elif len(dominant_langs) > 0:
                    # update DOMINANT RANDOM count for randomly chosen language
                    data_dict["DOMINANT RANDOM"][choice(
                        dominant_langs)][pos_or_not] += 1
                    # update DOMINANT FRACTION count for all languages
                    for lang in dominant_langs:
                        data_dict["DOMINANT FRACTION"][lang][pos_or_not] += 1 / \
                            len(dominant_langs)
                    # do nothing to DOMINANT IGNORE count
            # update fraction of all tokens that stem from each source language...
            for lang in english_source_langs:
                data_dict["TOTAL FRAC IN %"][lang][pos_or_not] \
                    = 100*data_dict["ABSOLUTE"][lang][pos_or_not]/total_tokens  # ...for both pos. and neg. contexts

    return data_dict

#data_dict = analyze_tweets(settings, english_source_langs)

def save_data(data_dict, settings, english_source_langs):
    """Save the data in the approriate csv file. Takes a long time!
    """
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


#save_data(data_dict, settings, english_source_langs)


def print_data(data_dict, settings):
    """Print the data for each setting.
    """
    for setting in settings:
        print(setting+": "+str(data_dict[setting]))


#print_data(data_dict, settings)
########################## Visualize data ####################################

def create_and_save_tweet_analysis_plots(load):
    if not load:
        data_dict = analyze_tweets(settings, english_source_langs)
        save_data(data_dict, settings, english_source_langs)

    with open("results_tweet_analysis.csv", mode="r", newline='') as file:
        lines = csv.reader(file)
        relevant_data = {"Dutch": {}, "French": [], "German": [], "Latin": [], "Portuguese": []}
        for line in lines:
            if line[0] in relevant_data:
                relevant_data[line[0]] = [float(val) for val in line[1:3] + line[5:]]

        plots = {"Absolute Context Appearances per Origin Language": 0,
                 "Number of Tweet dominations per Origin Language (FRACTION)": 2,
                 "Number of Tweet dominations per Origin Language (IGNORE)": 4}
                 #"Percentage of all Tokens in all Tweets that originate from each Source Language": 6}
        for key, value in plots.items():
            labels = relevant_data.keys()
            pos_occ = [relevant_data[label][value] for label in labels]
            neg_occ = [relevant_data[label][value + 1] for label in labels]

            pos_occ_scaled = []
            neg_occ_scaled = []

            for i in range(len(pos_occ)):
                pos_occ_scaled.append(pos_occ[i]/(pos_occ[i] + neg_occ[i]))
                neg_occ_scaled.append(neg_occ[i]/(pos_occ[i] + neg_occ[i]))

            x = np.arange(len(labels))  # the label locations
            width = 0.35  # the width of the bars

            fig, ax = plt.subplots()
            fig_sc, ax_sc = plt.subplots()
            rects_1 = ax.bar(x - width/2, pos_occ, width, label='positive occurrences')
            rects_2 = ax.bar(x + width/2, neg_occ, width, label='negative occurrences')
            rects_3 = ax_sc.bar(x - width/2, pos_occ_scaled, width, label='positive occurrences')
            rects_4 = ax_sc.bar(x + width/2, neg_occ_scaled, width, label='negative occurrences')
            # Add some text for labels, title and custom x-axis tick labels, etc.
            ax.set_ylabel(key)
            ax_sc.set_ylabel("percent")
            ax.set_title(key)
            ax_sc.set_title("Scaled " + key.replace("Absolute ", ""))
            ax.set_xticks(x, labels)
            ax_sc.set_xticks(x, labels)
            ax.legend()
            ax_sc.legend()

            ax.bar_label(rects_1, padding=3)
            ax.bar_label(rects_2, padding=3)
            ax_sc.bar_label(rects_3, padding=3)
            ax_sc.bar_label(rects_4, padding=3)

            fig.tight_layout()
            fig_sc.tight_layout()

            plt.show()
            plt.savefig('graphs/' + key.replace(" ", "_") + '.png')

create_and_save_tweet_analysis_plots(True)


def plot_lang(rec_lang, ori_langs):
    '''Do not capitalize the rec_lang but do the others'''
    diff = []
    colors = []
    for lang in ori_langs:
        result = 0.5561128526645768 - \
            print_sent_pct(rec_lang.capitalize(), lang)
        diff.append(result)
        if result < 0.0:
            colors.append('#F13C39')
        else:
            colors.append('#59CB9C')

    fig = plt.figure()
    plt.grid(linestyle='--', axis='y')
    plt.xlabel('Origin languages')
    plt.ylabel('Difference of negative sentiment ratio')
    plt.ylim([-0.55, 0.55])
    plt.title('Sentiment of loanwords in ' + rec_lang.capitalize())
    ax = fig.add_subplot(111)
    ori_langs = [lang.replace('_', ' ') for lang in ori_langs]
    ax.bar(ori_langs, diff, width=0.3, color=colors)
    ax.set_axisbelow(True)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45,
             ha="right", rotation_mode="anchor")
    plt.tight_layout()
    plt.savefig('graphs/' + rec_lang.capitalize() + '.png')


def plot_langs():
    with open("languages.csv", encoding="utf-8") as lw_file:
        rows = lw_file.readlines()
        for row in rows:
            row = row.replace('\n', '').split(',')
            receiving_language = row[0].lower()
            origin_languages = row[1:]
            origin_languages = [lang.replace(' ', '_')
                                for lang in origin_languages]
            plot_lang(receiving_language, origin_languages)


#plot_langs()

########################## Sentiment prediction ####################################
predictions_dict = {
    'French':
    {
        # After the world wars they have been friendly since they fought on the same side
        'English': '+',
        'German': '-',  # Has been at war with German nations long before even the world wars
    },
    'Spanish':
    {
        'Arabic': '-',  # Spanish-Moroccan relations have been bad for a long while
        'Andalusian Arabic': '-',  # The Reconquista
    },
    'Portuguese':
    {
        'Arabic': '-',  # Same as Spain
        'English': '+',  # Oldest alliance up to this day
    },
    'Italian':
    {
        # Sicilian Arabs were enslaved and kicked off the island in the past...
        'Arabic': '-',
        'Old French': '-',  # Italians didn't appreciate the Normans conquering their lands
    },
    'Romanian':
    {
        'French': '+',  # Many Romanian nobles studied in the post-Napoleonic France and returned to Romania as Francophiles
        # Romanians were treated as second class citizens in Transylvania by the Hungarians
        'Hungarian': '-',
        # It is believed that Romanians were friendly with the nearby Slavic tribes
        'Old Church Slavonic': '+',
        'Ottoman Turkish': '-',  # Multiple wars with the Ottomans
    },
    'English':
    {
        'Latin': '+',  # The English looked up to the ancient Romans
        'French': '+',  # After the world wards the countries have been friendly since they fought together
        'German': '-',  # Fought in the world wars and before
        'Dutch': '-',  # Had multiple wars due to trading competition
        # Had multiple wars since the English had claims over the crown of France
        'Middle French': '-',
        'Portuguese': '+',  # Oldest alliance to this day
        'Old French': '+',  # Old French was spoken by the nobility
        'Old Norse': '-',  # Fought multiple wars with the Norse vikings
    },
    'German':
    {
        'French': '-',  # Fought multiple wars even before the world wars
        'English': '-',  # Fought in the world wars
    },
    'Dutch':
    {
        'French': '-',  # France tried and conquered the Netherlands multiple times
        'English': '-',  # Had multiple wars over trade
    },
    'Finnish':
    {
        'Russian': '-',  # The Winter War
        'Swedish': '+',  # The two countries are known for having very good relations
    },
    'Polish':
    {
        'Latin': '+',  # It was used a lot within the upper class of the Polish-Lithuanian Commonwealth
        'German': '-',  # Was invaded by Germany multiple times
    },
}


def test_predictions(prediction_dict):
    """Test our manual predictions based on subjective historical relations by comparing our predictions
    to our results.
    """
    predictions = ''
    results = ''
    with open("languages.csv", encoding="utf-8") as lw_file:
        rows = lw_file.readlines()
        for row in rows:
            row = row.replace('\n', '').split(',')
            receiving_language = row[0]
            origin_languages = row[1:]
            for lang in origin_languages:
                predictions += (predictions_dict[receiving_language][lang])
            for lang in origin_languages:
                result = 0.5561128526645768 - \
                    print_sent_pct(receiving_language.capitalize(),
                                   lang.replace(' ', '_'))
                if result > 0.0:
                    results += '+'
                else:
                    results += '-'

    print(predictions)
    print(results)
    correct = 0
    for i in range(len(predictions)):
        if predictions[i] == results[i]:
            correct += 1
    print(correct)
    print(correct / len(predictions))


#test_predictions()
