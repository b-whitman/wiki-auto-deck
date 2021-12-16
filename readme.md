# Wikipedia Flashcards

Scrapes pages related to a subject and, using TF-IDF as a similarity metric, creates a set of pages that are most similar.

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
