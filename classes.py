import requests
from tqdm import tqdm

class ApiSession():

    def __init__(self):
        self.S = requests.Session()
        self.URL = "https://en.wikipedia.org/w/api.php"
    
    def close(self):
        # Could I just inherit this method (and all Session() methods) from requests.Session at initialization?
        self.S.close()

    def get_links(self, term):
        """
        Given a term matching a Wikipedia article, returns a list of all links 
        in that article.
        """
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
        """
        Given a term, search for a matching Wikipedia page. If one exists, or if 
        Wikipedia redirects to a page when given that term, return the name of 
        the Wiki article.
        
        If no matching page exists or is redirected to, perform a search of 
        Wikipedia and allow the user to choose the best match for their intent.
        """
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
            article_title = pages[page_id[0]]["title"]
            print(f"{term} matches the page {article_title} on Wikipedia!")
            

        return article_title

    def get_longest_articles(self, article_links, deck_size):
        """
        Gets lengths, watchers, and visiting watchers of all article links, to
        rank pages by importance.

        Currently article length is used as a direct proxy for importance, but 
        one possible extension would be to incorporate information from watchers
        and visiting watchers to make that a more robust measure.

        (Watchers are Wikipedia users who have chosen to be notified when a 
        given page is edited;
        Visiting watchers are the watchers of a given page who have visited
        recent edits to that page.)
        """
        num_articles = deck_size*10
        search_strings = []
        # Wikipedia API can query info from up to 50 pages at a time, so here we
        # distribute our article titles into search strings of 50 titles each
        while len(article_links) > 0:
            search_string = ""
            for title in article_links[:50]:
                search_string = search_string + "|" + title
            # Remove initial pipe
            search_string = search_string[1:]
            search_strings.append(search_string)
            if len(article_links) > 50:
                article_links = article_links[50:]
            else:
                break

        articles_info = []
        print("Pulling article lengths...")
        for s in tqdm(search_strings):
            params = {
            "action": "query",
            "prop": "info",
            "inprop": "watchers|visitingwatchers|url",
            "titles": s,
            "redirect": True,
            "format": "json",
            }
            response = self.S.get(url=self.URL, params=params)
            data=response.json()
            pages = data["query"]["pages"]
            # We'll get watchers and visiting watchers to potentially use in a 
            # more robust page importance algorithm, but we don't actually use
            # them yet.
            for page in pages.keys():
                if page != "-1":
                    # a -1 page_id means that the page does not exist
                    title = pages[page]["title"]
                    b_size = pages[page]["length"]
                    url = pages[page]["fullurl"]
                    if "watchers" in pages[page].keys():
                        watchers = pages[page]["watchers"]
                    else:
                        watchers = None
                    if "visitingwatchers" in pages[page].keys():
                        visitingwatchers = pages[page]["visitingwatchers"]
                    else:
                        visitingwatchers = None
                    articles_info.append((title, b_size, watchers, visitingwatchers, url))

        articles_info.sort(key=lambda tup: tup[1], reverse=True)
        if len(articles_info) > num_articles:
            longest_articles = articles_info[:num_articles]
        else:
            longest_articles = articles_info
        return longest_articles

    def get_article_extract(self, article_title):
        """
        Given the title of a Wikipedia article, returns the full text of the 
        article.
        """
        params = {
        "action": "query",
        "prop": "extracts",
        "exlimit": 1,
        "titles": article_title,
        "explaintext": 1,
        "formatversion": 2,
        "redirect": True,
        "format": "json"
        }
        response = self.S.get(url=self.URL, params=params)
        data = response.json()
        extract = data["query"]["pages"][0]["extract"]
        return extract
            
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

