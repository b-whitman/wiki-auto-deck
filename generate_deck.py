import requests
from retrieve_definition import retrieve_definition, text_wrangle
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from classes import ApiSession


def get_params_size(search_string):
    """API parameters for the article lengths, watchers and visiting watchers for entered term(s)"""
    params = {
        "action": "query",
        "prop": "info",
        "inprop": "watchers|visitingwatchers",
        "titles": search_string,
        "redirect": True,
        "format": "json",
    }
    return params

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


def generate_deck(S, term, deck_size):
    """Function to generate a set of extracts from a single user-entered term using the Wikipedia API"""
    article_links = S.get_links(term)
    # if the term entered doesn't return any articles, suggest a different term
    if len(article_links) < 2:
        return S.open_search(term)
    # Get list of dictionaries
    articles = batch_search(article_links, attribute="size")
    # Flatten the list of dictionaries and sort by value[0]
    # TODO: I bet there's a better way I could be getting this info where I wouldn't have to flatten the dict
    flat_dict = {}
    for my_dict in articles:
        for key in my_dict.keys():
            flat_dict[key] = my_dict[key]
    articles = flat_dict
    articles = {k: v for k, v in sorted(articles.items(), key=lambda item: item[1][0], reverse=1)}
    # Transfer titles of longest articles to list
    longest_articles = []
    p = 0
    article_titles = articles.keys()
    article_titles = list(article_titles)
    while (len(longest_articles) < int(deck_size)*10) and (len(longest_articles) < len(article_titles)):
        title = article_titles[p]
        longest_articles.append(title)
        p += 1
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


def batch_search(terms_list, batch_size=50, attribute=None):
    """Function to break longer sets of related terms into groups of 50, the max allowed by the Wikipedia API call"""
    articles = []
    print(f"Total terms: {len(terms_list)}")
    if len(terms_list) > batch_size:
        while len(terms_list) > batch_size:
            print(f"{len(terms_list)} more articles to search...")
            search_string = get_search_string(terms_list, batch_size)
            if attribute == "size":
                articles.append(get_article_size(search_string))
            else:
                print("attribute not recognized!")
            terms_list = terms_list[batch_size:]
    if len(terms_list) < batch_size:
        print(f"Last batch! {len(terms_list)} more articles to search...")
        search_string = get_search_string(terms_list, batch_size)
        if attribute == "size":
            articles.append(get_article_size(search_string))
        else:
            print("attribute not recognized!")

    return articles
    
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


def get_article_size(search_string):
    """Function to get info about each article connected to the initial search term"""
    S = requests.Session()

    URL = "https://en.wikipedia.org/w/api.php"  # this is the base API URL for Wikipedia
    params = get_params_size(search_string)
    response = S.get(url=URL, params=params)
    data = response.json()
    pages = data["query"]["pages"]
    articles = {}
    for page in pages.keys():
        if page != "-1":
            # a -1 page_id means that the page does not exist
            title = pages[page]["title"]
            b_size = pages[page]["length"]
            if "watchers" in pages[page].keys():
                watchers = pages[page]["watchers"]
            else:
                watchers = None
            if "visitingwatchers" in pages[page].keys():
                visitingwatchers = pages[page]["visitingwatchers"]
            else:
                visitingwatchers = None
            articles[title] = (b_size, watchers, visitingwatchers)

    return articles


def get_search_string(terms_list, batch_size=50):
    """Function to create a search string from the list of related terms"""
    search_string = ""
    for item in terms_list[:batch_size]:
        search_string = search_string + "|" + item
    search_string = search_string[1:]
    # creates string of titles separated by pipeline character in order to send through API
    return search_string

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
