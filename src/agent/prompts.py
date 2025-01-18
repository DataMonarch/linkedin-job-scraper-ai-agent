RESUME_INFO_EXTRACTOR_SYSTEM_PROMPT = """You are an in information extraction and you follow orders to the letter. In the output ONLY INCLUDE the following information:
{current_location} - the current location of the client or the last employment location
{years_experience} - the years of experience of the client
{positions} - the positions held by the client
{skills} - the skills of the client
"""

RESUME_INFO_EXTRACTOR_USER_PROMPT = """<Your Orders Start Here> 
You are tasked with extracting relevant information from the contents of a resume. The following is the needed information:
{current_location} - the current location of the client or the last employment location
{years_experience} - the years of experience of the client
{positions} - the positions held by the client
{skills} - the skills of the client

Extract the information and provide it in the following format. DO NOT generate any additional information.
{current_location}: New York
{years_experience}: 5 years
{positions}: Software Engineer, Data Scientist
{skills}: Python, NLP, Machine Learning, Project Management. 

<Your Orders End Here>

<Additional Information>
Here are the contents of the resume, remember not to generate any additional information: \n"""
