PROCESSED_RESUMES_PATH = r"/home/martin/tpp/resume-parsing/Data/Processed/Resumes"
PROCESSED_JOB_DESCRIPTIONS_PATH = r"/home/martin/tpp/resume-parsing/Data/Processed/JobDescription"

RESUMES_PATH = r"/home/martin/tpp/resume-parsing/Data/Resumes"
JD_PATH = r"/home/martin/tpp/resume-parsing/Data/JobDescription"

REGEX_PATTERNS = {
    "email_pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "phone_pattern": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
    "link_pattern": r"\b(?:https?://|www\.)\S+\b",
}

RESUME_SECTIONS = [
    "contact information",
    "objective",
    "summary",
    "education",
    "experience",
    "skills",
    "skill",
    "project",
    "projects",
    "certifications",
    "certification",
    "licenses",
    "license",
    "awards",
    "award",
    "honors",
    "honor",
    "publications",
    "publication",
    "references",
    "reference",
    "technical skills",
    "computer skills",
    "programming languages",
    "software skills",
    "soft skills",
    "language skills",
    "languages",
    "professional skills",
    "sransferable skills",
    "hard skills",
    "work experience",
    "professional experience",
    "employment history",
    "internship experience",
    "volunteer experience",
    "leadership experience",
    "research experience",
    "teaching experience",
]

DEGREE_PATTERNS = {
    "BACHELOR": [
        r'\b(Bachelor\'s (of )?Science|Bachelor of Science in)\b.*?(?=,|$)',
        r"\bBachelor's degree in\b\s+([a-zA-Z\s]+)"
    ],
    "MASTER": [
        r'\b(Master\'s (of )?Science|Master of Science in)\b.*?(?=,|$)',
        r'\bmaster\'s\b',
        r'\bmaster\b'
    ], 
    "PHD": [
        r'\b(Ph\.?D\.?|Doctorate|Doctor of Philosophy in)\b.*?(?=,|$)',
        r'\b(Doctor of Science in)\b.*?(?=,|$)',
        r'\bph\.?d\.?\b',
        r'\bdoctorate\b',
        r'\bphd\b'
    ]
}

EDUCATION = [
    'BE', 'B.E.', 'B.E', 'BS', 'B.S',
    'ME', 'M.E', 'M.E.', 'M.B.A', 'MBA', 'MS', 'M.S',
    'BTECH', 'B.TECH', 'M.TECH', 'MTECH',
    'SSLC', 'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
]