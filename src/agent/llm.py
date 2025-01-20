import os

# Third-party imports
from ollama import chat, ChatResponse, AsyncClient
import openai


# Setup OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", None)
OPENAI_AVAILABLE = openai.api_key is not None
if not OPENAI_AVAILABLE:
    print("OpenAI API key not found. Only Ollama will be used.")


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    provider: str = "ollama",
    ollama_model: str = "mistral",
    openai_model: str = "gpt-4o-mini",
) -> str:
    """
    Generic LLM caller that can use either Ollama or OpenAI based on `provider`.

    Args:
        system_prompt (str): The system-level prompt (instructions, context).
        user_prompt (str): The user-level prompt (main content).
        provider (str): "ollama" or "openai".
        ollama_model (str): Name of the Ollama model to use (if provider=ollama).
        openai_model (str): Name of the OpenAI model to use (if provider=openai).

    Returns:
        str: The raw text response from the LLM.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if provider.lower() == "openai":
        if not OPENAI_AVAILABLE:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
            )

        try:
            response = openai.chat.completions.create(
                model=openai_model,
                messages=messages,
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"[OpenAI Error] {e}")
            return f"Error: {str(e)}"

    elif provider.lower() == "ollama":
        response: ChatResponse = await AsyncClient().chat(
            model=ollama_model,
            messages=messages,
        )
        return response["message"]["content"]

    else:
        raise ValueError(
            f"Unknown provider '{provider}'. Must be 'ollama' or 'openai'."
        )


async def main():
    resume_text = """
    Toghrul Tahirov Leader in AI Development & Researcher
	Austin, TX, USA ● linkedin.com/toghrul-tahirov ● toghrultahirov@gmail.com
	github.com/DataMonarch ● kaggle.com/toghrultahirov SKILLS ● Machine Learning: TensorFlow, Keras, PyTorch, Scikit-learn, Hugging Face Transformers, LlamaCPP, Transfer Learning, Time Series Forecasting, Computer Vision, NLP, Model Explainability, Small-Scale LLMs ● Cloud & Big Data: GCP, AWS, Azure, Hadoop, PySpark, SQL, PostgreSQL, Data Pipelines, Azure Functions, AWS EMRs ● Software Development: Python, Rust, Docker, Kubernetes, Nix, MLflow, Weights and Biases, Git/GitHub, Jupyter Notebooks, Linux ● Soft skills: Leadership, Strategic Planning, Product Management, Mentorship, Communication, Collaboration, Time Management

	Work EXPERIENCE:

	- Head of AI & Tech Lead | AI Architect & Lead Developer 12/2023 – present PolygrafAI | Remote - Austin, Texas, USA Led the technical vision and execution of Polygraf AI, driving the development of industry-leading AI and Data Governance solutions as both a leader and hands-on developer. ● Spearheaded AI model development, employing cutting-edge NLP (token classification, sequence classification, fine-tuning LLMs) and Computer Vision (document processing, object detection) techniques. ● Architected and implemented highly optimized model deployment pipelines, leveraging Rust for efficient inference, file processing and all resource intensive software components, Docker and Kubernetes for on-prem solutions, and Google Cloud and AWS (VPCs) for scalable cloud deployments. ● Managed the full AI product lifecycle, from conception to deployment, ensuring seamless integration with backend, frontend, and desktop components. ● Key achievements: o Leading the technical team of 28 to deliver innovative AI-powered solutions, resulting in widespread adoption across 500+ enterprise customers through strategic partnerships. o Successfully launched and scaled two groundbreaking products in the AI and Data Governance space. o Secured adoption of Polygraf's AI Content Detection tool by two Ivy League universities, replacing Turnitin for plagiarism and AI detection. o Top AI & Data Governance Product at the 2024 Product Awards (Products That Count) o Established Startups of the Year 2024 Top 10 (SXSW) o AI Trailblazers Top 5 (SXSW)
	- Lead AI/ML Engineer – Time Series Forecasting 03/2023 – 11/2023 BitsOrchestra & Eudaimonia Inc | Remote – Wisconsin, USA Cryptocurrency/Forex Market Forecasting initiative aimed at developing predictive algorithms for real-time trading decisions ● Conducted thorough research-based feature engineering, exploring and testing over 25 features to enhance model performance. ● Designed and implemented diverse LSTM and hybrid CNN-LSTM architectures to capture temporal patterns in the cryptocurrency market data. ● Developed a versatile data preprocessing, feature engineering and model training pipeline. The modular design ensured high maintainability, efficient GPU utilization, and flexibility to experiment with different processing techniques and model architectures. ● Centralized configuration management: Crafted a comprehensive ecosystem to control model architecture, data preprocessing, and feature engineering parameters, enabling seamless experiments and adjustments.
	● Leveraged Weights and Biases: Integrated the WandB platform to enable real-time experiment tracking through an intuitive dashboard, enhancing collaboration and model insights. ● Automated Model Selection: Engineered automatic model evaluation and selection webhooks using Weights and Biases, streamlining the decision-making process. ● Azure Function Integration: Employed Azure Functions to create efficient HTTP Trigger Functions, acting as middleware between data APIs and Google's Vertex AI, streamlining data processing/prediction process for production stage deployment. ● End-to-End Ownership: Undertook full project ownership, conceptualizing, designing, and implementing the entire data processing/model training system single-handedly, ensuring a comprehensive and well-executed solution.
	Deep Learning Researcher - Computer Vision 03/2022 – 12/2022 ADA University | Baku, Azerbaijan Sign Language Recognition and Processing for Azerbaijani Language to make life more accessible ● Developed 3D CNNs and Sequential Models (Attention and LSTM) for successful extraction of crucial spatial features and translation of spatial data into temporal domain, achieving over 80% accuracy across over 200 experiments ● Designed NLP algorithm for context aware sentence completion in Azerbaijani language ● Demonstrated expertise in deep learning and computer vision through successful completion of 4 complex projects
	● Published a paper demonstrating the 1st stage results of the research Speech Communication Journal, Elsevier
	- Chief Data Officer 10/2022 – 04/2023 DigData Startup | Delaware, USA Directing a team of 15 developers and data scientists tasked in delivering real-time insights and big data analytics for blockchain. ● Lead the development and implementation of a Blockchain Analytics webpage as CDO, resulting in a professional and attractive web interface ● Ensuring high availability and reliability of the system to enable traders and investors to easily analyze current and historical trends in crypto, resulting in informed investment decisions and improved success in the market ● Leveraged Apache Spark (PySpark) on AWS EMR to implement highly scalable and efficient Big Data processing pipelines (processing over 1 PB of data per day) ● Committed to driving innovation and growth for the company and passionate about revolutionizing the analysis and use of blockchain data ● Actively engaging with investors and presenting the company's offerings and capabilities
	- Senior Data Scientist - Blockchain 05/2022 – 09/2022 DigData Startup | Baku, Azerbaijan Senior Data Scientist tasked with leading a team of 8 to analyze and uncover the trends in Decentralized Finance and Exchanges, and cryptocurrency ● Developed a variety of user, wallet and contract labelling metrics and models on over 200 DEXes, and crypto analysis dashboards to aid DeFI investors in decision making ● Designed Clustering Algorithms to perform behavior analysis on anonymous on-chain data ● Trained and mentored junior data scientists, fostering a culture of growth and learning ● Stayed current on industry trends and developments, incorporating new techniques and tools as appropriate
	- Machine Learning Instructor / Product Owner 10/2021 – 09/2022 Galactech School | Baku, Azerbaijan Contributed to future job market by: ● Taught future innovators industrial level applications of classical Machine Learning and Deep Learning: have instructed over 80 students by now ● Designed and supervised a series of educational products on Data and AI in the EdTech ecosystem: 2 products currently being marketed at high value
	- Computer Vision Engineer 08/2021 – 12/2021
	- Crowthink | Remote Intelligent Solutions startup where I: ● Coded a Facial Recognition system to perform as an additional application-level security protocol ● Implemented a Recommendation Systems
	- Well Integrity Intern 07/2021 – 09/2021 bp | Baku, Azerbaijan ● Accelerated Well Integrity Testing and improve the testing procedures by devising a Prediction Model to determine when certain pressure levels might endanger production of Hydrocarbon Gas: lowered Non Productive Time by 6% ● Integrated the developed models into Palantir Web Service ● Developed highly functional near real-time analytical dashboards

	PUBLICATIONS

	Comprehensive Analysis and Implementation of Small-Scale LLMs For Human-Like Machine Causal Reasoning MSc Thesis
	Explored the capabilities of small-scale Large Language Models (LLMs) for causal reasoning, enhancing the CRASS and Tübingen datasets with GPT-4 to expand cause-effect and counterfactual reasoning examples. Spearheaded dataset augmentation including Azerbaijani language integration via mBERT, significantly enriching resources for underrepresented languages in AI research. Uncovered unique LLM behavior in multi-choice question processing, leading to insights on model biases and attention mechanisms. Our research underlines the potential of fine-tuned small LLMs to rival larger counterparts in specialized tasks, offering a scalable and efficient solution for AI-driven reasoning in resource-constrained applications.
	Development of a hybrid word recognition system and
	dataset for the Azerbaijani Sign Language dactyl alphabet Published - 09/2023
	Authored a groundbreaking paper on real-time fingerspelling-to-text translation systems for Azerbaijani Sign Language, presenting a hybrid word recognition approach using statistical and probabilistic models. Developed and publicly shared a comprehensive AzSL dataset with over 13,000 samples, significantly advancing sign language recognition technology. Demonstrated high-accuracy outcomes, achieving 94% accuracy in tests, and successfully showcased at TeknoFest 2022, earning first place in social-oriented technologies.
	EDUCATION
	George Washington University & ADA University | Master of Computer Science and Data Analytics 07/2022 – 07/2024 Washington, DC, USA MSc in Computer Science and Data Analytics ● Conducting research into the Causal Reasoning capabilities of Large Language Models (LLMs) under the supervision of a highly esteemed professor who is a Staff Software Engineer for Machine Learning applications at Google ● Acquired AWS Cloud Architect and Cloud Practitioner badges ● Carried out research into development of a highly scalable/parallelized data processing and modelling pipeline for Cryptocurrency Price Forecasting ● Program Structure: Advanced Software Engineering, Big Data, Applied Data Analytics, Artificial Intelligence and Machine Learning, Cloud Environments for HPC, Computer Systems Architecture, Computational Linear Algebra
	ABB Tech Academy | Machine Learning Professional Degree 12/2020 – 06/2021 ● GPA: 96/100 ● Program Structure: Exploratory Data Analysis, Regression, Classification, PCA & Dimensionality Reduction, Clustering, Deep Learning, Natural Language Processing, Computer Vision

	"""
    system_prompt = """You are a highly specialized assistant with a single task:
	- Employment history, in other words the WORK EXPERIENCE from resume related to all job positions held. On a new line, provide the information in the following format:
	  * [job_position1] - [start_date1] - [end_date1]
	  * [job_position2] - [start_date2] - [end_date2]
	"""
    user_prompt = """
	<Resume Text>
		{}  	
	<Instructions>
		As a specialized assistant, you are tasked with extracting the following information from the resume:
		- employment history, in other words the WORK EXPERIENCE from resume related to all job positions held. On a new line, provide the information in the following format. Start with the most recent job position which is at the top of the resume:
		* [job_position1] - [start_date1] - [end_date1]
		* [job_position2] - [start_date2] - [end_date2]

		As a hint, company names and job positions are usually next to each other. Also, there might be on going positions.
	
	"""
    # *You shall NOT OUTPUT any additional information or explanation beyond the requested information! And DO NOT MISS ANY JOB POSITION!*
    summarizer_system_prompt = """You are a highly specialized assistant with a single task:
	- Summarize resume and CV content in a concise manner. Provide a summary of every single job position held in the resume and every single academic performance.
	"""
    summarizer_user_prompt = f"""
	<Resume Text>
		{resume_text}

	<Instructions>
		As a specialized assistant, you are tasked with summarizing the resume and CV content in a concise manner. Provide a summary of every single job position held in the resume and every single academic performance.
	
		As a hint, summarize the job positions and academic performances in a few sentences each.
	"""
    date_extractor_system_prompt = """You are a highly specialized assistant with a single task:
	- Extract the dates related to all job positions held in the resume.
	"""
    date_extractor_user_prompt = f"""
	<Resume Text>
		{resume_text}

	<Instructions>
		As a specialized assistant, you are tasked with extracting the dates related to all job positions held in the resume.

		As a hint, look for the start and end dates of each job position.

	"""
    summary = await call_llm(
        summarizer_system_prompt,
        summarizer_user_prompt,
        provider="ollama",
        ollama_model="llama3.2",
    )
    print("#" * 20 + "\nSUMMARY\n" + "#" * 20)
    print(summary)
    print("_" * 100)
    user_prompt = user_prompt.format(resume_text)
    response = await call_llm(
        system_prompt, user_prompt, provider="ollama", ollama_model="llama3.2"
    )

    print("#" * 20 + "\WORK EXPERIENCE\n" + "#" * 20)
    print(response)

    date_response = await call_llm(
        date_extractor_system_prompt,
        date_extractor_user_prompt,
        provider="ollama",
        ollama_model="llama3.2",
    )

    print("#" * 20 + "\DATES\n" + "#" * 20)
    print(date_response)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
