#import libraries
import pandas as pd
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import nltk
from langdetect import detect
import re, string, unicodedata
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer


def remove_non_ascii(words):

    """Remove non-ASCII characters from list of tokenized words"""

    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)

    return new_words


def remove_punctuation(words):

    """Remove punctuation from list of tokenized words"""

    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words




def remove_stopwords(doc):

    """Remove stop words from list of tokenized words"""
    stop_words = stopwords.words('english')

    for word in stop_words:
        doc = doc.replace(" "+word+" ", ' ')
        
    return doc


def lemmatize_verbs(words):

    """Lemmatize verbs in list of tokenized words"""

    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)

    return lemmas


def isLatin(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

    
def clean_data(content):
	"""
	Preprocess the text
	"""
	
	content_str = str(content)   #convert content from object type to string
	words = word_tokenize(content_str)

	#remove digits, lowercase words
	words = [''.join([i.lower() for i in w if not i.isdigit()]) for w in words]

	#remove punctuation
	words = remove_punctuation(words)
	
	#remove empty strings
	while '' in words:
		words.remove('')
    
	#remove non ascii
	words = remove_non_ascii(words)

	#lemmatization
	words = lemmatize_verbs(words)
	
	doc = " ".join(w for w in words)

	#remove stop words
	doc = remove_stopwords(doc)
	#remove special characters
	doc = re.sub('[^A-Za-z0-9]+', ' ', doc)
	
	return doc

