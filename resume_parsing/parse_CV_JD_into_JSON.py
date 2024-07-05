import logging
from scripts import JobDescriptionProcessor, ResumeProcessor
from scripts.utils import  init_logging_config
from constants import RESUMES_PATH, JD_PATH
from scripts.utils.Utils import get_filenames_from_dir

init_logging_config()

def parse_CV():

    logging.info("Started to read from Data\Resumes")
    try:
  
        file_names = get_filenames_from_dir(RESUMES_PATH)
        print(f"Archivos encontrados: {file_names}")
        logging.info("Reading from Data\Resumes is now complete.")
    except:
        # Exit the program if there are no resumes.
        logging.error("There are no resumes present in the specified folder.")
        logging.error("Exiting from the program.")
        logging.error("Please add resumes in the Data\Resumes folder and try again.")
        exit(1)

    # Now after getting the file_names parse the resumes into a JSON Format.
    logging.info("Started parsing the resumes.")
    for file in file_names:
        processor = ResumeProcessor(file)
        processor.process()
    logging.info("Parsing of the resumes is now complete.")

def parse_JD():

    logging.info("Started to read from Data\JobDescription")
    try:
        file_names = get_filenames_from_dir(JD_PATH)
        logging.info("Reading from Data/JobDescription is now complete.")
    except:
        # Exit the program if there are no resumes.
        logging.error("There are no job-description present in the specified folder.")
        logging.error("Exiting from the program.")
        logging.error("Please add resumes in the Data\JobDescription folder and try again.")
        exit(1)

    logging.info("Started parsing the Job Descriptions.")
    for file in file_names:
        processor = JobDescriptionProcessor(file)
        processor.process()
    logging.info("Parsing of the Job Descriptions is now complete.")
        


if __name__ == "__main__":
    parse_CV()
    parse_JD()


