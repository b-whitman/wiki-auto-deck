from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from classes import ApiSession

def generate_deck(S: ApiSession, term, deck_size, desc_length):
    """Function to generate a set of extracts from a single user-entered term using the Wikipedia API"""
    deck_size = int(deck_size)
    article_links = S.get_links(term)
    longest_articles = S.get_longest_articles(article_links, deck_size)

    # For each article title, pull the page contents from Wikipedia API
    # I wonder if I need to land these in a dict, or if I can just land them directly into the corpus?
    extracts = {term:S.get_article_extract(term)}
    for article in longest_articles:
        title = article[0]
        extract = S.get_article_extract(title)
        extracts[title] = extract
    # Perform TF-IDF comparisons
    corpus = []
    titles = []
    for key in extracts:
        titles.append(key)
        corpus.append(extracts[key])
    vect = TfidfVectorizer(min_df=1, stop_words="english")
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
        if desc_length > 0:
            description = extracts[title][:desc_length]
        else: 
            intro_end = extracts[title].find("\n\n\n")
            description = extracts[title][:intro_end]
        cards[title] = description
    import pdb; pdb.set_trace()
    return cards

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
    print(cards)
    S.close()
