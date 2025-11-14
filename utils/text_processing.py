import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# Download necessary NLTK data (Railway-friendly)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        print("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
    except Exception as e:
        print(f'WARNING: NLTK download failed: {e}')
        # Continue anyway, functions will handle missing data

def process_text(text):
    """
    Process text by tokenizing, removing stop words, and stemming.
    """
    if not text:
        return []
        
    # Tokenize
    tokens = word_tokenize(text.lower())
    
    # Remove stop words and non-alphabetic characters
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    
    # Stemming
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    
    return stemmed_tokens
