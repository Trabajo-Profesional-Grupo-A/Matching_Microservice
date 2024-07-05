from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize 
import collections
from nltk import tokenize
import math
from operator import itemgetter

stop_words = set(stopwords.words('english'))

def do_tfidf(token):
    tfidf = TfidfVectorizer(max_df=0.05, min_df=0.002)
    words = tfidf.fit_transform(token)
    sentence = " ".join(tfidf.get_feature_names())
    
    return sentence


def get_tf_idf(doc, n):

    # Step 1 : Find total words in the document
    total_words = doc.split()
    total_word_length = len(total_words)

    # Step 2 : Find total number of sentences
    total_sentences = tokenize.sent_tokenize(doc)
    total_sent_len = len(total_sentences)

    # Step 3: Calculate TF for each word
    tf_score = {}
    for each_word in total_words:
        each_word = each_word.replace('.','')
        if each_word not in stop_words and each_word.isalpha() and len(each_word) >= 3:
            if each_word in tf_score:
                tf_score[each_word] += 1
            else:
                tf_score[each_word] = 1


    # Dividing by total_word_length for each dictionary element
    tf_score.update((x, y/int(total_word_length)) for x, y in tf_score.items())


    # Check if a word is there in sentence list
    def check_sent(word, sentences): 
        final = [all([w in x for w in word]) for x in sentences] 
        sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
        return int(len(sent_len))


    # Step 4: Calculate IDF for each word
    idf_score = {}
    for each_word in total_words:
        each_word = each_word.replace('.','')
        if each_word not in stop_words:
            if each_word in idf_score:
                idf_score[each_word] = check_sent(each_word, total_sentences)
            else:
                idf_score[each_word] = 1

    # Performing a log and divide
    idf_score.update((x, math.log(int(total_sent_len)/y)) for x, y in idf_score.items())

    # Step 5: Calculating TF*IDF
    tf_idf_score = {key: tf_score[key] * idf_score.get(key, 0) for key in tf_score.keys()} 

   
    result = dict(sorted(tf_idf_score.items(), key = itemgetter(1), reverse = True)[:n]) 
    return result

def extract_keywords(text, top_n=10):
    vectorizer = TfidfVectorizer(max_features=top_n)
    vectors = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    dense = vectors.todense()
    denselist = dense.tolist()
    tfidf_scores = dict(zip(feature_names, denselist[0]))
    return tfidf_scores