# U:
# I want to make a class for the connection to Wikipedia API.
# At initialization, this would open a requests Session object.
# It could then be the intermediary for all the interactions with the Wikipedia API involved in this program.

import requests
from sklearn.feature_extraction.text import TfidfVectorizer

class ApiSession():

    def __init__(self):
        self.S = requests.Session()
        self.URL = "https://en.wikipedia.org/w/api.php"
    
    def close(self):
        # Could I just inherit this method (and all Session() methods) from requests.Session at initialization?
        self.S.close()

    def get_links(self, term):
        params = {
        "action": "parse",
        "prop": "links",
        "page": term,
        "redirects": True,
        "format": "json",
        }
        response = self.S.get(url=self.URL, params=params)
        data = response.json()
        if "error" in data.keys():
            return self.open_search(term)
        else:
            links = data['parse']['links']
        article_links = []
        # includes only titles that are namespace: 0 (articles only), exist,
        # and don't contain the listed exclusion phrases
        exclude_types = ["List of", "History of", "Timeline of", "Glossary of"]
        for item in links:
            if (item['ns'] == 0) & ("exists" in item.keys()) & ~ any(excluded in item["*"] for excluded in exclude_types):
                article_links.append(item["*"])
        
        return article_links

    def validate_term(self, term):
        # U:
        # Right now the way the validated term is acquired and stored is sort of all over the place.
        # If there is a wiki article with the given term as its title, continue on.
        # But if there is no such article, prompt the user to choose one of the suggestions.
        params = {
            "action": "query",
            "titles": term,
            "prop": "info",
            "inprop": "url",
            "redirects": True,
            "format": "json"
        }
        response = self.S.get(url=self.URL, params=params)
        data=response.json()
        pages = data["query"]["pages"]
        page_id = [x for x in pages.keys()]
        if page_id[0] == '-1':
            print(f"{term} doesn't match a page on Wikipedia.")
            suggestions = self.open_search(term)
            if len(suggestions) > 0:
                print("Term not recognized. Please select a suggestion:")
                for i,s in enumerate(suggestions):
                    print(i+1,s)
                selection = int(input("Enter number of term: "))-1
                article_title = suggestions[selection]
            else:
                print(f"That doesn't look close to any pages we can find...")
                article_title = None

        else:
            print(f"{term} matches a page on Wikipedia!")
            article_title = term

        return article_title

            
    def open_search(self, term):
        """
        function to use opensearch on Wikipedia API and return most likely related articles for a given term. opensearch
        is a Wikimedia API feature which returns similarly-titled articles within the wiki.
        """
        params = {
            "action": "opensearch",
            "search": term,
            "redirects": "resolve",
            "format": "json"
        }
        R = self.S.get(url=self.URL, params=params)
        data = R.json()
        suggests = data[1]

        return suggests

