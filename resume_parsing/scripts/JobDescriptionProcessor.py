from .parsers import ParseJobDesc



class JobDescriptionProcessor:
    def __init__(self, data):
        self.data = data

    def process(self) -> bool:
        try:
            jd_dict = self._read_job_desc()
            return jd_dict
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return {"error": str(e)}

    def _read_job_desc(self) -> dict:
        output = ParseJobDesc(self.data).get_JSON()
        return output
