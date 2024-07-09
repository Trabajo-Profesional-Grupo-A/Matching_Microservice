import re
import urllib.request
import pandas as pd

import spacy
import csv
from resume_parsing.constants import DEGREE_PATTERNS, EDUCATION, RESUME_SECTIONS
from resume_parsing.scripts.TextCleaner import TextCleaner
from transformers import BartTokenizer, BartForConditionalGeneration



# Load the English model
nlp = spacy.load("en_core_web_sm")
matcher = spacy.matcher.Matcher(nlp.vocab)
designitionmatcher = spacy.matcher.PhraseMatcher(nlp.vocab)

# Load the tokenizer and model
tokenizer = BartTokenizer.from_pretrained('ilsilfverskiold/tech-keywords-extractor')
model = BartForConditionalGeneration.from_pretrained('ilsilfverskiold/tech-keywords-extractor')



class DataExtractor:
    """
    A class for extracting various types of data from text.
    """

    def __init__(self, raw_text: str, resume_dict_OCR = None):
        """
        Initialize the DataExtractor object.

        Args:
            raw_text (str): The raw input text.
        """
        self.resume_dict_OCR = resume_dict_OCR
        self.text = raw_text
        self.clean_text = TextCleaner(self.text).clean_text()
        self.doc = nlp(self.text)
        self.doc_clean = nlp(self.clean_text)

    def extract_links(self):
        """
        Find links of any type in a given string.

        Args:
            text (str): The string to search for links.

        Returns:
            list: A list containing all the found links.
        """
        link_pattern = r"\b(?:https?://|www\.)\S+\b"
        links = re.findall(link_pattern, self.text)
        return links

    def extract_links_extended(self):
        """
        Extract links of all kinds (HTTP, HTTPS, FTP, email, www.linkedin.com,
          and github.com/user_name) from a webpage.

        Args:
            url (str): The URL of the webpage.

        Returns:
            list: A list containing all the extracted links.
        """
        links = []
        try:
            response = urllib.request.urlopen(self.text)
            html_content = response.read().decode("utf-8")
            pattern = r'href=[\'"]?([^\'" >]+)'
            raw_links = re.findall(pattern, html_content)
            for link in raw_links:
                if link.startswith(
                    (
                        "http://",
                        "https://",
                        "ftp://",
                        "mailto:",
                        "www.linkedin.com",
                        "github.com/",
                        "twitter.com",
                    )
                ):
                    links.append(link)
        except Exception as e:
            print(f"Error extracting links: {str(e)}")
        return links

    def extract_names(self):
        """Extracts and returns a list of names from the given
        text using spaCy's named entity recognition.

        Args:
            text (str): The text to extract names from.

        Returns:
            list: A list of strings representing the names extracted from the text.
        """
        # First name and Last name are always Proper Nouns
        pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        
        matcher.add('NAME', [pattern])
        matches = matcher(self.doc)
        
        # Extract names using Matcher
        matcher_names = [self.doc[start:end].text for match_id, start, end in matches]

        
        # Extract names using NER
        ner_names = [ent.text for ent in self.doc.ents if ent.label_ == "PERSON"]

        
        # Combine results and remove duplicates
        all_names = list(set(matcher_names + ner_names))
        
        return all_names
    

    def extract_emails(self):
        """
        Extract email addresses from a given string.

        Args:
            text (str): The string from which to extract email addresses.

        Returns:
            list: A list containing all the extracted email addresses.
        """
        # First method using spaCy matcher
        matcher = spacy.matcher.Matcher(nlp.vocab)
        email_pattern = [{'LIKE_EMAIL': True}]
        matcher.add('EMAIL', [email_pattern])
        
        matches = matcher(self.doc)
        spacy_emails = set()  # Use a set to store unique emails from spaCy
        for match_id, start, end in matches:
            if match_id == nlp.vocab.strings['EMAIL']:
                spacy_emails.add(self.doc[start:end].text)

        # Second method using regular expression
        email_pattern_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        regex_emails = set(re.findall(email_pattern_regex, self.text))  # Use a set to store unique emails from regex

        # Combine both sets of emails
        unique_emails = spacy_emails.union(regex_emails)

        # Return the list of unique emails
        return list(unique_emails)

    def extract_phone_numbers(self):
        """
        Extract phone numbers from a given string.

        Args:
            text (str): The string from which to extract phone numbers.

        Returns:
            list: A list containing all the extracted phone numbers.
        """
        phone_number_patterns = [
        r"^(\+\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$",  # General format
        r"\(\d{3}\) \d{3}-\d{4}",  # Alternate format: (123) 456-7890
        r"(?:\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"  # Other common formats
    ]

        # Try each pattern and return the first match found
        for pattern in phone_number_patterns:
            match = re.search(pattern, self.text)
            if match:
                return match.group(0)

        return None  # Return None if no phone number is found

    def extract_experience(self):
        """
        Extract experience from a given string. It does so by using the Spacy module.

        Args:
            text (str): The string from which to extract experience.

        Returns:
            str: A string containing all the extracted experience.
        """

        return self.resume_dict_OCR.get("Work Experience")
    
    def extract_education(self):
        """
        Extract education from a given string. It does so by using the Spacy module.

        Args:
            text (str): The string from which to extract education.

        Returns:
            str: A string containing all the extracted education.
        """

        return self.resume_dict_OCR.get("Education")
    
    def extract_personal_info(self):
        """
        Extract personal information from a given string. It does so by using the Spacy module.

        Args:
            text (str): The string from which to extract personal information.

        Returns:
            str: A string containing all the extracted personal information.
        """
        return self.resume_dict_OCR.get("Personal Info")
    
    def extract_extra_info(self):
        """
        Extract extra information from a given string. It does so by using the Spacy module.

        Args:
            text (str): The string from which to extract extra information.

        Returns:
            str: A string containing all the extracted extra information.
        """
        return self.resume_dict_OCR.get("Extra")
    
    def extract_education_title(self):
        """
        Extract education title from a given string. It does so by using the Spacy module.

        Args:
            text (str): The string from which to extract education title.

        Returns:
            list: A list containing the extracted education titles.
        """
        # Sentence Tokenizer
        nlp_text = [sent.text.strip() for sent in self.doc.sents]

        education_titles = []

        # Extract education degree
        for text in nlp_text:
            for word in text.split():
                # Replace all special symbols
                word_clean = re.sub(r'[?|$|.|!|,]', r'', word)
                if word_clean.upper() in EDUCATION or word_clean.upper() in DEGREE_PATTERNS.keys():
                    # Append the entire sentence if the word is found in EDUCATION
                    education_titles.append(text)
                    break  # Stop after finding the first match in the sentence

        

        # Post-process to extract only the relevant part of the sentence
        processed_titles = []
        for title in education_titles:
            match = re.search(r'(' + '|'.join(EDUCATION) + r')\s*.*?,\s*.*?(?=,|$)', title, re.IGNORECASE)
            if match:
                processed_titles.append(match.group(0).strip())
            for _, patterns in DEGREE_PATTERNS.items():
                pattern = '|'.join(patterns)
                match_qual = re.search(pattern, title, re.IGNORECASE)
                if match_qual:
                    processed_titles.append(match_qual.group(0).strip())

        return processed_titles 
    
    def extract_qualifications(self):
        """
        Extract qualifications from a given string. It does so by using the Spacy module.

        Args:
            text (str): The string from which to extract qualifications.

        Returns:
            str: A string containing all the extracted qualifications.
        """
    
        # Sentence Tokenizer
        nlp_text = [sent.text.strip() for sent in self.doc.sents]

        qualifications = []
        

        # Extract education degree
        for text in nlp_text:
            for word in text.split():
                # Replace all special symbols
                word_clean = re.sub(r'[?|$|.|!|,]', r'', word)
                if  word_clean.upper() in DEGREE_PATTERNS.keys():
                    # Append the entire sentence if the word is found in EDUCATION
                    qualifications.append(text)
                    break  # Stop after finding the first match in the sentence

        # Post-process to extract only the relevant part of the sentence
        processed_titles = []
        for title in qualifications:
            for _, patterns in DEGREE_PATTERNS.items():
                pattern = '|'.join(patterns)
                match_qual = re.search(pattern, title, re.IGNORECASE)
                if match_qual:
                    processed_titles.append(match_qual.group(0).strip())

        return processed_titles 
    
    def extract_universities(self):
        """
        Extract university from a given string. It does so by using the Spacy module.

        Args:
            text (str): The string from which to extract university.

        Returns:
            str: A string containing all the extracted university.
        """
    
        # Method 1: Using spaCy NER
        universities_spacy = set()  # Use a set to avoid duplicates
        for entity in self.doc.ents:
            if entity.label_ == "ORG" and ("university" in entity.text.lower() or "college" in entity.text.lower() or "institute" in entity.text.lower()):
                universities_spacy.add(entity.text)

        # Method 2: Using a list of known universities from a CSV file
        file = r'./resume_parsing/Data/world-universities.csv'
        df = pd.read_csv(file, header=None)
        known_universities = [i.lower() for i in df[1]]
        universities_csv = set()  # Use a set to avoid duplicates

        for uni in known_universities:
            if re.search(r'\b' + re.escape(uni) + r'\b', self.clean_text):
                universities_csv.add(uni)

        # Combine results from both methods and convert to list
        all_universities = list(universities_spacy.union(universities_csv))

        return all_universities
    
    def _extract_skills_from_BERT(self):
        # Tokenize the input text
        inputs = tokenizer(self.clean_text, return_tensors='pt')

        # Generate keywords
        outputs = model.generate(**inputs, max_new_tokens=40)

        # Decode the generated keywords
        keywords = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return keywords.split(", ")
    
    def _load_keywords(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            return set(row[0] for row in reader)
        
    def _csv_skills(self):
        skills_keywords = self._load_keywords(r'./resume_parsing/Data/newSkills.csv')
        skills = set()

        for keyword in skills_keywords:
            if keyword.lower() in self.doc.text.lower():
                skills.add(keyword)

        return skills

    def extract_skills(self):
        skills_csv = self._csv_skills()
        skills_BERT = self._extract_skills_from_BERT()
        skills_OCR_text = self.resume_dict_OCR.get("Skills").lower()
        skills_OCR = set(skills_OCR_text.split(", "))
         
        combined_skills = skills_csv.union(skills_BERT)  # Combine filtered skills without duplicates
        all_skills = combined_skills.union(skills_OCR)
        
        return list(all_skills)  # Return combined filtered skills as a list
    

    def extract_model_data(self):
        """
        Extract model data from a given string. It does so by using the Spacy module.

        Args:
            text (str): The string from which to extract model data.

        Returns:
            str: A string containing all the extracted model data.
        """

        # personal_info = self.extract_personal_info()
        # cleaned_personal_text = TextCleaner(personal_info).clean_text()

        # print("personal info", personal_info)
        # print("cleaned personal info", cleaned_personal_text)

        # job_titles = self.extract_designition()

        # for title in job_titles:
        #     if title in cleaned_personal_text:
        #         cleaned_personal_text = cleaned_personal_text.replace(title, "")

        # print("cleaned personal info 2", cleaned_personal_text)

        # words_to_remove = set(cleaned_personal_text.split())

        # print("words to remove", words_to_remove)

        # cleaned_text = ' '.join([word for word in self.text.split() if word not in words_to_remove])

        pattern_numbers = r"\b\d+\b"
        model_text = re.sub(pattern_numbers, "", self.text)
            
        return model_text



    def extract_particular_words(self):
        """
        Extract nouns and proper nouns from the given text.

        Args:
            text (str): The input text to extract nouns from.

        Returns:
            list: A list of extracted nouns.
        """
        pos_tags = ["NOUN", "PROPN"]
        nouns = [token.text for token in self.doc if token.pos_ in pos_tags]
        return nouns

    def extract_entities(self):
        """
        Extract named entities of types 'GPE' (geopolitical entity) and 'ORG' (organization) from the given text.

        Args:
            text (str): The input text to extract entities from.

        Returns:
            list: A list of extracted entities.
        """
        entity_labels = ["GPE", "ORG"]
        entities = [
            token.text for token in self.doc.ents if token.label_ in entity_labels
        ]
        return list(set(entities))
    

    def extract_designition(self):
        """
        Extract designition from a given string.

        Args:
            text (str): The string from which to extract designition.

        Returns:
            str: A string containing the extracted designition.
        """
        file = r'./resume_parsing/Data/titles_combined.txt'
        with open(file, "r", encoding='utf-8') as f:
            designation = [line.strip().lower() for line in f]
        
        patterns = [nlp.make_doc(text) for text in designation if len(nlp.make_doc(text)) < 10]
        designitionmatcher.add("Job title", None, *patterns)
        
        job_titles = set()
        matches = designitionmatcher(self.doc_clean)
        
        for match_id, start, end in matches:
            span = self.doc_clean[start:end]
            job_titles.add(span.text)
        
        return list(job_titles)
