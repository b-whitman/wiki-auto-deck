import requests
from retrieve_definition import retrieve_definition, open_search, text_wrangle
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


"""
U:
I want to be able to submit a string term and an integer x and have the script return a list of length x of terms with brief descriptions drawn from wikipedia entries linked to the entry for that term.
The script should select only up to the x most important terms, as measured by article length and number of links.
Actually, let's consider that a sub-problem. What is the best way to determine importance?
We could explore generating a corpus of Wikipedia pages and extracting meaningful connections through a TF-IDF analysis of the corpus.
Would TF-IDF still be useful if I can glean information on importance from a combination of each article's length and its ratio of visiting watchers to all watchers?
P:
I think I'm going to need to refactor this.
Some of it, anyway.
Mostly autogenerate().
So let's just imagine it from the top.
First we establish a connection to the wikipedia API using requests.
We normalize the search term to play nice with Wikipedia.
Query the API with a get request.
Get the json out of the returned response.
If the API returned an error, get opensearch results and prompt the user: "Did you mean [x],[y],[z],[N]one?"
    If one of those terms better fits what they're looking for, great! If not, return to main menu
Once the user has landed on a term corresponding to an actual wiki entry, get the list of all links from the page.
Retrieve lengths of all linked pages, and store as {name of page: length}

(*) One limitation: pages contain some direct links to pages and other redirecting links.
For example, "Buddhism" contains a link to Zen, which is the title of the page,
but a separate link to "Zen buddhism," which redirects to Zen. Still gets counted
in the initial count, though!
So that's something to keep in mind and possibly check on later, though I don't think it's vital for the moment.

Alright, here's an idea.
Filter the results down. Just because wahhabism is a widely-watched and long article
linked to from Buddhism doesn't mean wahhabism is important within buddhism.
But downloading all 1808 articles linked to from Buddhism as a corpus seems like it might be a waste of time and bandwidth.
So maybe we first filter down to some manageable number of documents if the corpus is too large.
If the corpus is already only a reasonable size, let's leave it as it is and move straight to relevance checks.
And of course if the corpus is large but the user wants a flashcard deck that large, we can leave things as they are.
We could choose corpus size dynamically depending on the ratio of deck size to number of links.
For example, Buddhism has 1808 links. (ostensibly- see above (*))
If the user wants only 50 cards, not all the top 50 longest articles will be most relevant.
But we can assume that there exists a number of documents less than all 1808 that will contain all the most relevant articles.
So what do we need to make sure we'll get all of the most relevant results?
5x as many documents as deck_size? 10x?
Once we have our corpus, we'll vectorize the documents using TF-IDF and calculate 
pairwise similarity
"""


def get_params_links(term):
    """API parameters for set of links on Wikipedia entry for term"""
    params = {
        "action": "parse",
        "prop": "links",
        "page": term,
        "format": "json",
    }
    return params


def get_params_size(search_string):
    """API parameters for the article lengths, watchers and visiting watchers for entered term(s)"""
    params = {
        "action": "query",
        "prop": "info",
        "inprop": "watchers|visitingwatchers",
        "titles": search_string,
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
        "format": "json"
    }
    return params


def generate_deck(term, deck_size):
    """Function to generate a set of extracts from a single user-entered term using the Wikipedia API"""
    S = requests.Session()
    # Accessing the MediaWiki Action API. What would the pros/cons be of switching to one of Wikipedia's other APIs?
    URL = "https://en.wikipedia.org/w/api.php"  # this is the base API URL for Wikipedia
    params = get_params_links(term)
    response = S.get(url=URL, params=params)
    data = response.json()
    # if the term does not match a Wikipedia entry, the open_search function runs and suggests a different term
    if "error" in data.keys():
        return open_search(term)
    # getting the list of links from the JSON object returned from the API call
    links = data['parse']['links']
    article_links = []
    # includes only titles that are namespace: 0 (articles only), exist,
    # and don't contain the listed exclusion phrases
    exclude_types = ["List of", "History of", "Timeline of", "Glossary of"]
    for item in links:
        if (item['ns'] == 0) & ("exists" in item.keys()) & ~ any(excluded in item["*"] for excluded in exclude_types):
            article_links.append(item["*"])
    # if the term entered doesn't return any articles, suggest a different term
    if len(article_links) < 2:
        return open_search(term)
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
    while (len(longest_articles) < int(deck_size)*5) and (len(longest_articles) < len(article_titles)):
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
    for page in similars[:int(deck_size)]:
        print(page)
    import pdb; pdb.set_trace()
    cards = {}
    S.close()
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
    S.close()
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
    term = input("Enter page to scan: ").title()
    deck_size = input("Enter number of cards to generate: ")
    cards = autogenerate(term, deck_size)
    print(cards)