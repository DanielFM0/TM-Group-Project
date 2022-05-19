import csv
from googletrans import Translator

""" Terminal Command for correct installation: 
pip3 install googletrans==3.1.0a0 
"""

# Retrieve sentiment lexicon from the csv file
words_sentiment = {}
with open('data/processed/words_sentiment.csv', mode='r', newline='') as csv_file:
    reader = csv.reader(csv_file, delimiter=',')
    for row in reader:
        words_sentiment[row[0]] = row[1]
    del words_sentiment['Word']


translator = Translator()

def print_sent_pct(lang, root_lang):
    """ Takes a string root_lang and locates the corresponding .csv file in the
        processed data folder. Prints out the percentages of loanwords from the
        given root language that are positive/negative according to words_sentiment.
        Words that have no sentiment attributed to them in words_sentiment are assumed
        to be neutral. The percentage of classified (= non neutral) words is printed
        as well.
    """
    with open("data/processed/"+lang+root_lang, encoding="latin-1") as lw_file:
        loan_words = [tpl.split(",")[0] for tpl in lw_file.readlines()[1:]]

        if lang != "English":
            loan_words = [translator.translate(w).text for w in loan_words]  # incr. running speed: [... in loan_words[:300]]

        pos, neg, neut = 0, 0, 0
        for lw in loan_words:
            if lw not in words_sentiment:
                neut += 1
            elif words_sentiment[lw] == '1':
                pos += 1
            elif words_sentiment[lw] == '-1':
                neg += 1

        frac_pos, frac_neg = f"{100*pos/(pos + neg):.2f}", f"{100*neg/(pos + neg):.2f}"
        fraction_classified = f"{100*(pos + neg)/(pos + neg + neut):.2f}"

        fraction_dict = {"a positive": frac_pos, "a negative": frac_neg, "any":fraction_classified}
        for key in fraction_dict:
            print("Fraction of "+ lang + " words originating from " + root_lang + " that have " + 
                  key + " sentiment: " + fraction_dict[key] + "%.")


print_sent_pct("English", "French")
print_sent_pct("English", "German")
print_sent_pct("Spanish", "Latin")
