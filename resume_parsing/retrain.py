# Import libraries
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')


def preprocess_text(text):
    # Convert the text to lowercase
    text = text.lower()

    # Remove punctuation from the text
    text = re.sub('[^a-z]', ' ', text)

    # Remove numerical values from the text
    #text = re.sub(r'\d+', '', text)

    # Remove extra whitespaces
    text = ' '.join(text.split())

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = text.split()
    words = [word for word in words if word not in stop_words]

    # Lemmatize words
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    text = ' '.join(words)
    return text


def retrain():

    df = pd.read_csv('./resume_parsing/Data/dice_com-job_us_sample.csv')

    relevant_columns = ['jobtitle','jobdescription', 'skills']
    df = df[relevant_columns]

    df['data'] = df[relevant_columns].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)

    df.drop(relevant_columns, axis=1, inplace=True)

    new_lines = []
    with open("./resume_parsing/Data/newJobDesc.csv") as file:
        for line in file:
            new_lines.append(line.strip())

    new_df = pd.DataFrame(new_lines, columns=['data'])

    df = pd.concat([df, new_df], ignore_index=True)

    data = list(df['data'])
    tagged_data = [TaggedDocument(words = word_tokenize(preprocess_text(_d)), tags = [str(i)]) for i, _d in enumerate(data)]

    #Model initialization
    model = Doc2Vec(vector_size = 10,
        window = 3,
        min_count = 5,
        epochs = 50,
        workers = 4
    )

    model.build_vocab(tagged_data)

    model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)

    model.save('./models/cv_job_maching_vector_size_10_min_count_5_window_3_epochs_50.model')

    return model







