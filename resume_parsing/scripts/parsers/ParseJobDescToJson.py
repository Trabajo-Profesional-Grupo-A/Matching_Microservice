from resume_parsing.scripts.Extractor import DataExtractor
from resume_parsing.scripts.KeytermsExtraction import KeytermExtractor
from resume_parsing.scripts.TextCleaner import CountFrequency, TextCleaner
from resume_parsing.scripts.utils.Utils import generate_unique_id


class ParseJobDesc:

    def __init__(self, job_desc: str):
        self.job_desc_data = job_desc
        self.clean_data = TextCleaner(self.job_desc_data).clean_text()
        self.entities = DataExtractor(self.job_desc_data).extract_entities()
        self.qualifications = DataExtractor(self.job_desc_data).extract_qualifications()
        self.key_words = DataExtractor(self.job_desc_data).extract_particular_words()
        self.job_title = DataExtractor(self.clean_data).extract_designition()
        self.pos_frequencies = CountFrequency(self.clean_data).count_frequency()
        self.keyterms = KeytermExtractor(self.clean_data).get_keyterms_based_on_sgrank()
        self.bi_grams = KeytermExtractor(self.clean_data).bi_gramchunker()
        self.tri_grams = KeytermExtractor(self.clean_data).tri_gramchunker()
        self.model_data = DataExtractor(self.clean_data).extract_model_data()

    def get_JSON(self) -> dict:
        """
        Returns a dictionary of job description data.
        """
        job_desc_dictionary = {
            "unique_id": generate_unique_id(),
            "job_desc_data": self.job_desc_data,
            "clean_data": self.clean_data,
            "entities": self.entities,
            "qualifications": self.qualifications,
            "extracted_keywords": self.key_words,
            "job_title": self.job_title,
            "keyterms": self.keyterms,
            "bi_grams": str(self.bi_grams),
            "tri_grams": str(self.tri_grams),
            "pos_frequencies": self.pos_frequencies,
            "model_data": self.model_data,
        }

        return job_desc_dictionary
