"""Utility functions for the thesis project."""

import os
from dotenv import load_dotenv
from getpass import getpass
import time
from langchain_openai import AzureChatOpenAI

def init_llm_langsmith(llm_key = 3, temp = 0.5, langsmith_name: str = ""):
    """Initialize the LLM model and LangSmith tracing.

    Args:
    ----
    llm_key (int): The LLM model designation.
    temp (float): The temperature to use in the LLM model.
    langsmith_name (str): The name of the LangSmith project.

    Returns:
    -------
    ChatOpenAI: LLM model.

    """
    # Set environment variables
    load_dotenv()
    def _set_if_undefined(var: str):
        if not os.environ.get(var):
            # print(f"{var} is not set. Prompting for value...")
            os.environ[var] = getpass(f"Please provide your {var}")
        else:
            pass
            # print(f"{var} is already set.")# to: {os.environ[var]}")
    _set_if_undefined('LANGCHAIN_API_KEY')
    _set_if_undefined('AZURE_OPENAI_ENDPOINT')
    _set_if_undefined('AZURE_OPENAI_API_KEY')

    if llm_key == 3:
        llm_ver, azure_depl = "gpt-3.5-turbo-0125", "gpt-35-turbo-august-sandbox"
    elif llm_key == 4:
        llm_ver = "gpt-4-turbo-2024-04-09"
    elif llm_key == 40:
        llm_ver, azure_depl = "gpt-4o-2024-05-13", "gpt-4o-august-sandbox"


    if langsmith_name is not None:
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        time_now = time.strftime("%Y.%m.%d-%H.%M.")
        os.environ["LANGCHAIN_PROJECT"] = langsmith_name + "_LLM:" + llm_ver + "_Timestamp:" + time_now + "_Temp: " + str(temp)

    # llm_model = ChatOpenAI(model_name=llm_ver, temperature=temp)
    llm_model = AzureChatOpenAI(
        azure_deployment=azure_depl,
        api_version="2023-06-01-preview",
        temperature=temp,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        )

    return llm_model

