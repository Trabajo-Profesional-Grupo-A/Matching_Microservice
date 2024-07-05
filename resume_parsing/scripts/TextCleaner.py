import string
import re
import spacy
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.corpus import wordnet
from collections import Counter

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')


class TextCleaner:
    """
    A class for cleaning a text by removing specific patterns.
    """

    def __init__(self, raw_text):
        self.stopwords_set = set(stopwords.words("english") + list(string.punctuation))
        self.lemmatizer = WordNetLemmatizer()
        self.raw_input_text = raw_text

    def clean_text(self) -> str:
        text_to_lower = self.raw_input_text.lower()
        pattern = r"\.js|\W+"
        text_without_special_characters = re.sub(pattern, lambda x: x.group(0) if x.group(0) == ".js" else " ", text_to_lower)
        text_without_extra_spaces = " ".join(text_without_special_characters.split())
        tokens = word_tokenize(text_without_extra_spaces)
        pos_tags = pos_tag(tokens)
        allowed_tags = {'NN', 'NNP', 'NNPS', 'NNS', 'JJ', 'JJR', 'JJS', 'CD'}
        filtered_words = [word for word, tag in pos_tags if tag in allowed_tags]
        filtered_words = [token for token in filtered_words if token not in self.stopwords_set]
        lemmatized_words = [self.lemmatizer.lemmatize(token, self._get_wordnet_pos(tag)) for token, tag in pos_tag(filtered_words)]
        cleaned_text = " ".join(lemmatized_words)
        return cleaned_text
    
    def _get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN
        

# Load the English model
nlp = spacy.load("en_core_web_md")

class CountFrequency:
    def __init__(self, text):
        self.text = text
        self.doc = nlp(text)

    def count_frequency(self):
        """
        Count the frequency of words in the input text and return the top 10 most frequent words.

        Returns:
            dict: A dictionary with the top 10 most frequent words as keys and their frequency as values.
        """
        word_freq = Counter()

        for token in self.doc:
                word_freq[token.text.lower()] += 1

        top_10_words = dict(word_freq.most_common(10))
        return top_10_words