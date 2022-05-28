import csv
from bs4 import BeautifulSoup
import requests

def scrapeWebsite(url: str) -> None:
    """Scrape the EZGlot webpage given by the url for the words and their origin, then write to csv file.

    Args:
        url (str): The url for the webpage to scrape
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
    with open('data/processed/' + words[0] + origins[0], 'a', encoding='utf-8', newline='') as output:
        writer = csv.writer(output)
        for i in range(len(words)):
            writer.writerow([words[i], origins[i]])
    
    return None

#scrapeWebsite("https://www.ezglot.com/etymologies.php?l=sqi&l2=tur&submit=Compare")