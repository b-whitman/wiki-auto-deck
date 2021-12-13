Long-term TODO:
Try different article comparison methods.
- What could I use that might be better than TF-IDF?
- Compare similarity of lists of links?
Multiple topic inputs.
- E.g. "New York City + history," "New York City + geography" 
- This could boost relevance of returned pages.
Clean Wikipedia extracts.
- Examine what exactly TFIDFVectorizer is doing and remove confounding characters


U:
I want to be able to submit a string term and an integer x and have the script return a list of length x of terms with brief descriptions drawn from wikipedia entries linked to the entry for that term.
The script should select only up to the x most important terms, as measured by article length and number of links.
Actually, let's consider that a sub-problem. What is the best way to determine importance?
We could explore generating a corpus of Wikipedia pages and extracting meaningful connections through a TF-IDF analysis of the corpus.
Would TF-IDF still be useful if I can glean information on importance from a combination of each article's length and its ratio of visiting watchers to all watchers?
P:

(*) One limitation: pages contain some direct links to pages and other redirecting links.
For example, "Buddhism" contains a link to Zen, which is the title of the page,
but a separate link to "Zen buddhism," which redirects to Zen. Still gets counted
in the initial count, though!
So that's something to keep in mind and possibly check on later, though I don't think it's vital for the moment.

Testing different thresholds of length for importance 

5x corpus
('Thomas Pynchon', nan)
('The New York Times', 0.0894749789548582)
('Cornell University', 0.08133830870920249)
('Isaac Asimov', 0.06616721439205846)
('United States', 0.06578640389874849)
('The Simpsons', 0.0647673772237135)
('Alan Moore', 0.0624794157535362)
('Joseph Conrad', 0.06103777383833202)
('Manhattan', 0.060570516182166294)
('George Orwell', 0.05853856481235498)

10x corpus
('Thomas Pynchon', nan)
('Salman Rushdie', 0.09931276282558665)
('Don DeLillo', 0.09310827484148812)
('Philip K. Dick', 0.08625334152781523)
('The New York Times', 0.08461214073467582)
('William Gibson', 0.08346218520010198)
('Cornell University', 0.08047937387457493)
('The Satanic Verses controversy', 0.0788773010175385)
('Nineteen Eighty-Four', 0.07734109485036485)
('Paul Thomas Anderson', 0.07574908402176497)

15x corpus
('Thomas Pynchon', nan)
('Thomas Pynchon bibliography', 0.5689501398523077)
("Gravity's Rainbow", 0.41924569699037917)
('Mason & Dixon', 0.20274138070707648)
('Postmodern literature', 0.1733005531985886)
('Inherent Vice (film)', 0.16093212634569998)
('National Book Award for Fiction', 0.12121313729994466)
('Don DeLillo', 0.10965357456508495)
('Salman Rushdie', 0.10924315124134587)
('Vladimir Nabokov', 0.10318055469678858)

So what can we conclude? Despite it being the longest part of the process, building a large corpus results in different results than when a smaller corpus is used.
Are these results better? I suppose it depends on what your purpose is.
It probably also depends on the nature of the subject you're deckbuilding for.
