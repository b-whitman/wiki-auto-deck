import requests
from retrieve_definition import retrieve_definition, text_wrangle
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from classes import ApiSession

def get_params_extract(search_string):
    """API parameters for entire text of Wikipedia entry for term(s)."""
    params = {
        "action": "query",
        "prop": "extracts",
        "exlimit": 1,
        "titles": search_string,
        "explaintext": 1,
        "formatversion": 2,
        "redirect": True,
        "format": "json"
    }
    return params


def generate_deck(S: ApiSession, term, deck_size):
    """Function to generate a set of extracts from a single user-entered term using the Wikipedia API"""
    deck_size = int(deck_size)
    article_links = S.get_links(term)
    # Get list of dictionaries
    longest_articles = S.get_longest_articles(article_links, deck_size)
    # For each article title, pull the page contents from Wikipedia API
    extracts = {term:get_article_extract(term)}
    for article in longest_articles:
        extract = get_article_extract(article)
        extracts[article] = extract
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
    for page in similars[1:int(deck_size)+1]:
        print(page)
    cards = {}
    return cards
    
def get_article_extract(article_title):
    """Get Wikipedia extracts for all pages in search_string."""
    print(f"retrieving extract for {article_title}")
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"  # this is the base API URL for Wikipedia
    params = get_params_extract(article_title)
    response = S.get(url=URL, params=params)
    data = response.json()
    extract = data["query"]["pages"][0]["extract"]
    return extract

if __name__ == "__main__":
    S = ApiSession()
    article_title = None
    while article_title == None:
        term = input("Enter page to scan: ")
        # Check to see if the term has a corresponding wiki article
        article_title = S.validate_term(term)
    deck_size = input("Enter number of cards to generate: ")
    cards = generate_deck(S, article_title, deck_size)
    print(cards)
    S.close()
