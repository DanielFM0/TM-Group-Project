## "Loanwords" and their sentiment in a language

## Abstract
We want to see if "loanwords" from certain languages have a skewed sentiment ratio and if those have anything to do with the historical background of those languages. This was inspired by the hypothesis that words with a Slavic origin in Romanian have a positive sentiment in general, while words with a Turkish origin have a negative sentiment in Romanian. We want to check if this appears in other languages as well and to what extent.

## Research questions
Do "loanwords" have a skewed sentiment ratio depending on the language they come from?
If there is a skewed ratio, can it be attributed to the historical relationship between the people who used those languages?

## Dataset
We've found this to use as a sentiment lexicon: http://sentiment.christopherpotts.net/lexicons.html
As for "loanwords" we've found this website: https://www.ezglot.com/etymologies.php?l=spa&l2=lat&submit=Compare, as well as Wiktionary: https://en.wiktionary.org/wiki/Category:Spanish_terms_borrowed_from_Latin. 
Since the sentiment values will be for English words we'll translate the "loanwords" into English to find their sentiment. Here we're assuming that for the majority of words their sentiment is about the same in different languages, which seems like a fair assumption especially since Europeans have a base shared set of values.


## Documentation
A reference list for sources used can be found in the report, FinalReport.pdf in this repository. All the code used can be found in the functions.py file. You can also find a powerpoint of our presentation given during class. The repository can be found here: https://github.com/DanielFM0/TM-Group-Project.


## Data Sources
opinion-lexicon-English: http://www.cs.uic.edu/~liub/FBS/opinion-lexicon-English.rar 

SentiWordNet_3.0.0.txt: https://github.com/aesuli/SentiWordNet

subjclueslen1-HLTEMNLP05.tff: https://mpqa.cs.pitt.edu/lexicons/subj_lexicon/


