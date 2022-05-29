import csv

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

        fraction_dict = {"a positive": frac_pos, "a negative": frac_neg, "any":fraction_classified}
        for key in fraction_dict:
            print("Fraction of "+ lang + " words originating from " + root_lang + " that have " + 
                  key + " sentiment: " + fraction_dict[key] + "%.")


#print_sent_pct("English", "French")
#print_sent_pct("English", "German")
for lang in languages:
    print_sent_pct(lang.capitalize(), 'Latin')
