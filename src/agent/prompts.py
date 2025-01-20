RESUME_INFO_EXTRACTOR_SYSTEM_PROMPT = """You are a highly specialized assistant with two tasks:

1) Extract these specific resume fields in a strict format:
{current_location}: ...
{years_experience}: ...
{positions}: ...
{skills}: ...

2) Generate exactly K sets of keyword combinations for job searching. Each set should contain multiple relevant job titles, technologies, and skills extrapolated to the job market base on the resume. Each set should be a comma-separated list of related terms.

Output Format (no extra text, no disclaimers):

{current_location}: [some location or blank if not found]
{years_experience}: [some integer or text, e.g. "5 years"]
{positions}: [comma-separated job titles]
{skills}: [comma-separated skill list]

<Keywords>
1) ...
2) ...
...
K) ...
<\\Keywords>

Do not include commentary or additional information beyond these fields and the K lines of keyword sets.

"""

RESUME_INFO_EXTRACTOR_USER_PROMPT = """<Instructions>
You will be given:
1. The number K (the exact number of keyword sets to generate).
2. The full resume text.

First, extract the following fields from the resume:
- {{current_location}}
- {{years_experience}}
- {{positions}}
- {{skills}}

Next, produce exactly {k} sets of keyword combinations focusing on job titles, skills, and relevant technologies from the resume. Each set should be on its own line, numbered from 1 to K. Use a comma to separate terms within a single set.

Do not generate additional text or commentary. Follow the format strictly.

<Resume Text>
{resume_text}"""


KEYWORD_GEN_SYSTEM_PROMPT = (
    "You are a helpful assistant that specializes in job search optimization. "
    "You will receive a resume text and must generate exactly {} sets of keyword combinations. "
    "Each set should be relevant for LinkedIn job searches, focusing on job titles, skills, technologies, etc. Main focus should be o the job titles."
    "Return them as a numbered list, with one combination per line. Do not add extra commentary."
)

KEYWORD_GEN_USER_PROMPT = (
    "<Resume Contents>\n{}\n\n"
    "<Instructions>\nPlease produce 20 distinct keyword combinations for LinkedIn job searches "
    "most likely to yield relevant job results, based on the above resume."
)


SMALL_EXTRACTOR_SYSTEM_PROPMPT = """You are a specialized text-parsing assistant. 
    Your sole task is to parse a provided resume and extract requested data. 
    You must output only the requested information, with no extra commentary or explanations.
	"""
SMALL_EXTRACTOR_USER_PROPMPT = """
    <RESUME TEXT START>
    {}
    <RESUME TEXT END>

    <INSTRUCTIONS START>
    1. Read the entire resume text above. 
    2. Extract the **employment history** (job positions, start dates, end dates).
    3. Present the results in reverse-chronological order (most recent job first).
    4. For each position, use the exact output format below:
        * [job_position] - [start_date] - [end_date]
    5. If an end date is ongoing or missing, use "Present". If any date is not found, use "N/A".
    6. Provide **no other text** besides these bullet points (no commentary, no disclaimers).
    <INSTRUCTIONS END>

    """

SMALL_SUMMARIZER_SYSTEM_PROMPT = """You are a highly specialized assistant with a single task:
    - Summarize resume and CV content in a concise manner. Provide a summary of every single job position held in the resume and every single academic performance.
    """
SMALL_SUMMARIZER_USER_PROMPT = """
    <Resume Text>
        {}

    <Instructions>
        As a specialized assistant, you are tasked with summarizing the resume and CV content in a concise manner. Provide a summary of every single job position held in the resume and every single academic performance.

        As a hint, summarize the job positions and academic performances in a few sentences each.
    """

SMALL_DATE_EXTRACTOR_SYSTEM_PROMPT = """You are a highly specialized assistant with a single task:
- Extract the dates related to all job positions held in the resume.
"""
SMALL_DATE_EXTRACTOR_USER_PROMPT = """
    <Resume Text>
        {}

    <Instructions>
        As a specialized assistant, you are tasked with extracting the dates related to all job positions held in the resume.

        As a hint, look for the start and end dates of each job position.

    """

SMALL_INFO_EXTRACTOR_SYSTEM_PROMPT = """You are an expert resume parser. Your task is to extract only the company and job position names from the WORK EXPERIENCE or EXPERIENCE sections of the provided resume text. Return the extracted job position related information in a JSON array formatted as follows:
    ```json
    {{
    "company_names": {{
        "Company Name 1": {{
        "Positions": ["Job Position 1", "Job Position 2"],
        "Start Date": "Month Year",
        "End Date": "Month Year"
        "Relevant Skills": ["Skill 1", "Skill 2"]
        }},
        "Company Name 2": {{
        "Positions": ["Job Position 1"],
        "Start Date": "Month Year",
        "End Date": "Month Year"
        "Relevant Skills": ["Skill 1", "Skill 2"]
        }},
        ...
    }}
    }}
    ```

Ensure the following:
- Extract only job position related information associated with the company.
- If no company names are found, return an empty array.
- Do not include any additional information or details.

"""
SMALL_INFO_EXTRACTOR_USER_PROMPT = """
    <Resume Text>
    {}
    </Resume Text>

    <Instructions>
    1. Analyze the resume text above and extract the WORK EXPERIENCE section.
    2. For each company, extract:
    - Company Name
    - Positions held at the company (as a list)
    - Start Date (in "Month Year" format)
    - End Date (in "Month Year" format, or "Present" if the position is ongoing)
    3. Format the extracted information as a JSON object, structured as follows:
    ```json
    {{
    "company_names": {{
        "Company Name 1": {{
        "Positions": ["Job Position 1", "Job Position 2"],
        "Start Date": "Month Year",
        "End Date": "Month Year"
        "Relevant Skills": ["Skill 1", "Skill 2"]
        }},
        "Company Name 2": {{
        "Positions": ["Job Position 1"],
        "Start Date": "Month Year",
        "End Date": "Month Year"
        "Relevant Skills": ["Skill 1", "Skill 2"]
        }},
        ...
    }}
    }}
    ```
    4. Start with the most recent job position and group multiple positions under the same company name if applicable.
    5. If dates are missing, leave them as empty strings ("").
    6. Do not include any additional information beyond the specified format.
    </Instructions>
    """


SMALL_LOCATION_EXTRACTOR_SYSTEM_PROMPT = """You are an expert resume parser. Your task is to analyze the first 300 words of a resume and extract the current location of the resume owner. The location should include the city, state, and/or country, depending on what is available.

Return the extracted location in the following JSON format:
```json
    {
    "current_location": "City, State, Country"
    }
```
Ensure the following:
- Extract the most recent or relevant location mentioned (e.g., under contact information, address, or recent work experience).
- If no location is found, return "None".
- Do not include any additional information beyond the specified format.
"""

SMALL_LOCATION_EXTRACTOR_USER_PROMPT = """
<Resume Text>
{}
</Resume Text>

<Instructions>
1. The location should include the city, state, and/or country, depending on what is available.
2. Return the extracted location in the following JSON format:
    ```json
        {
        "current_location": "City, State, Country"
        }
    ```
3. If no location is found, return:
    ```json
        {
        "current_location": "None"
        }
    ```
4. Focus on the most recent or relevant location mentioned (e.g., under contact information, address, or recent work experience).
5. Do not include any additional information beyond the specified format.

Example Output:
{
  "current_location": "San Francisco, California, USA"
}
</Instructions>
"""
