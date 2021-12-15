from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from classes import ApiSession
from tqdm import tqdm
from random import randint

def generate_deck(S: ApiSession, term, deck_size, desc_length):
    """Function to generate a set of extracts from a single user-entered term using the Wikipedia API"""
    deck_size = int(deck_size)
    article_links = S.get_links(term)
    longest_articles = S.get_longest_articles(article_links, deck_size)

    # For each article title, pull the page contents from Wikipedia API
    # I wonder if I need to land these in a dict, or if I can just land them directly into the corpus?
    extracts = {term:S.get_article_extract(term)}
    print("Pulling article extracts...")
    for article in tqdm(longest_articles):
        title = article[0]
        extract = S.get_article_extract(title)
        extracts[title] = extract
    # Perform TF-IDF comparisons
    corpus = []
    titles = []
    for key in extracts:
        titles.append(key)
        corpus.append(extracts[key])
    vect = TfidfVectorizer(stop_words="english", ngram_range=(1,3))
    tfidf = vect.fit_transform(corpus)
    pairwise_similarity = tfidf * tfidf.T
    arr = pairwise_similarity.toarray()
    np.fill_diagonal(arr, np.nan)
    root_similarity = arr[0]
    # So we have our list of how similar each document is to the root document.
    # Let's associate them with their article titles, and then sort by similarity.
    similars = [(page, similarity) for page,similarity in zip(titles,root_similarity)]
    similars.sort(key=lambda tup: tup[1], reverse=True)
    cards = {}
    for page in similars[1:int(deck_size)+1]:
        title = page[0]
        intro_end = extracts[title].find("\n\n\n")
        if desc_length > 0 and desc_length <= intro_end:
            description = extracts[title][:desc_length]
        else: 
            description = extracts[title][:intro_end]
        cards[title] = description
    return cards

def output_to_json(cards):
    """
    Output cards as a JSON object of title: extract
    """
    pass

if __name__ == "__main__":
    S = ApiSession()
    article_title = None
    while article_title == None:
        term = input("Enter page to scan: ")
        # Check to see if the term has a corresponding wiki article
        article_title = S.validate_term(term)
    deck_size = input("Enter number of cards to generate: ")
    print("This program can generate cards with long extracts or short.")
    print("300 characters generally returns the first several sentences.")
    print("Enter 0 if you want to return the entire introduction section.")
    desc_length = int(input("Please enter the number of characters you'd like included in the extract: "))
    while desc_length < 0:
        desc_length = int(input("Please input a non-negative number: "))
    cards = generate_deck(S, article_title, deck_size, desc_length)
    print("Deck complete.")
    print("Enter 'cards' to view your cards one at a time, 'titles' to see a list of all your card titles, 'json' to output to JSON, or 'quit' to quit.")
    run = True
    while run:
        command = input("> ").lower()
        if command == "quit":
            run = False
        elif command == "cards":
            view_cards = True
            curr_card = 0
            titles = list(cards.keys())
            command = None
            print("Enter 'n' to view the next card, 'p' to view the previous card, 'r' to view a random card, or 'q' to return to the main menu.")
            while view_cards:
                if command == 'n':
                    if curr_card < len(titles)-1:
                        curr_card += 1
                    else:
                        curr_card = 0
                elif command == 'p':
                    if curr_card > 0:
                        curr_card -= 1
                    else:
                        curr_card = len(titles)-1
                elif command == 'r':
                    curr_card = randint(0,len(titles)-1)
                else:
                    print("Command not recognized.")
                    print("Enter 'n' to view the next card, 'p' to view the previous card, 'r' to view a random card, or 'q' to return to the main menu.")
                print(f"Current card index: {curr_card}")
                curr_title = titles[curr_card]
                print(curr_title)
                print(cards[curr_title].replace("\n", "\n\n"))
                command = input("> ").lower()
                if command == 'q':
                    view_cards = False
                    print("Enter 'cards' to view your cards one at a time, 'titles' to see a list of all your card titles, 'json' to output to JSON, or 'quit' to quit.")
        elif command == "titles":
            print(list(cards.keys()))
        elif command == "dev":
            import pdb; pdb.set_trace()
        elif command == "json":
            print("Placeholder for conversion to json")
        elif command == "quit":
            run == False
        else:
            print("Command not recognized.")
            print("Enter 'cards' to view your cards one at a time, 'titles' to see a list of all your card titles, 'json' to output to JSON, or 'quit' to quit.")

    S.close()
