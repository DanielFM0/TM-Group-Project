from processing import words_sentiment


def print_sentiment_percent(root_lang):
    """ Takes a string root_lang and locates the corresponding .csv file in the
        processed data folder. Prints out the percentages of loanwords from the
        given root language that are positive/negative according to words_sentiment.
        Words that have no sentiment attributed to them in words_sentiment are assumed
        to be neutral. The percentage of classified (= non neutral) words is printed
        as well.
    """
    with open("data/processed/"+root_lang, encoding="latin-1") as lw_file:
        loan_words = [tpl.split(",")[0] for tpl in lw_file.readlines()[1:]]
        pos, neg, neut = 0, 0, 0
        for lw in loan_words:
            if lw not in words_sentiment:
                neut += 1
            elif words_sentiment[lw] == 1:
                pos += 1
            else:
                neg += 1

        fraction_pos = f"{100*pos/(pos + neg):.2f}"
        fraction_neg = f"{100*neg/(pos + neg):.2f}"
        fraction_classified = f"{100*(pos + neg)/(pos + neg + neut):.2f}"

        lang = root_lang.replace("English", "")

        print("Fraction of English words originating from "+lang+
              " that have a positive sentiment: "+fraction_pos+"%.")
        print("Fraction of English words originating from "+lang+
              " that have a negative sentiment: "+fraction_neg+"%.")
        print("Fraction of English words originating from "+lang+
              " that have a any sentiment: "+fraction_classified+"%.")


# print_sentiment_percent("EnglishFrench")
# print_sentiment_percent("EnglishGerman")
