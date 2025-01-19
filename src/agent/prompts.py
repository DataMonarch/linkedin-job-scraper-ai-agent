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
