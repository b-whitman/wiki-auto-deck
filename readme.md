# Wikipedia Flashcards

Scrapes pages related to a subject and, using TF-IDF as a similarity metric, creates a set of pages that are most similar.

demo.ipynb contains a quick overview of this script's capabilities and a peek behind the curtain at the raw TF-IDF results.

Adapted from work by Amer Mahyoub, Cai Nowicki, and myself during Lambda Labs. https://github.com/b-whitman/Studium-ds

# Further reading

Wikipedia has a similar function already, "Related Pages." It's only deployed on mobile Wikipedia, and I don't think it's been updated since 2016. 
It appears it's no longer being worked on. From what I can see, it seems to get its results from Elasticsearch's "more like this" query.

Main project page: https://www.mediawiki.org/wiki/Reading/Web/Projects/Related_pages
Feature Request for Comment: https://en.wikipedia.org/wiki/Wikipedia_talk:Related_Pages_extension/RfC

Those pages contain some great discussion about the ins and outs of an algorithm like this. When the WMF was considering adding this as a feature, they naturally had to decide what to do when improper results were served. They also had to think about how this feature would be accessed by their users, how to measure its success, and how to scale it across all Wikipedia articles. As I've implemented it, there are significant unanswered questions about how it would scale up. The "Related Pages" feature uses functionality already built into Wikipedia, while my implementation uses a different TF-IDF-based pipeline.


## Long-term TODO:

Display URL of wiki article with each card

Handle disambiguation of homonyms when validating article title.

Store term and term description as "{term} [root term] : description" in cards

Try different article comparison methods.

- What could I use that might be better than TF-IDF?
- Compare similarity of lists of links?

Multiple topic inputs.

- E.g. "New York City + history," "New York City + geography" 
- This could boost relevance of returned pages.

Clean Wikipedia extracts.

- Make data more readable for the CountVectorizer's tokenizer

Allow user to view full list of similars and add article extracts to a deck.
