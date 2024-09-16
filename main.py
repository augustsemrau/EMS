import chainlit as cl
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@cl.on_chat_start
async def main():
    try:
        model = AzureChatOpenAI(
            azure_deployment="gpt-4o-august-sandbox",
            temperature=0.5,
            streaming=True,
            api_version="2023-06-01-preview"
        )

        instructions = open("EMS_prompt.md", "r").read()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", instructions),
                ("human", "{question}"),
            ]
        )
        runnable = prompt | model | StrOutputParser()
        cl.user_session.set("runnable", runnable)
        logger.info("Chat session initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing chat session: {str(e)}")
        raise

@cl.on_message
async def on_message(message: cl.Message):
    try:
        runnable = cl.user_session.get("runnable")  # type: Runnable
        if not runnable:
            raise ValueError("Runnable not found in user session")

        logger.info(f"Received message: {message.content}")

        msg = cl.Message(content="")
        async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await msg.stream_token(chunk)

        await msg.send()
        logger.info("Response sent successfully")
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await cl.Message(content=f"An error occurred: {str(e)}").send()


# import chainlit as cl
# from langchain_openai import AzureChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema import StrOutputParser
# from langchain.schema.runnable import Runnable
# from langchain.schema.runnable.config import RunnableConfig
# import subprocess
# import multiprocessing

# @cl.on_chat_start
# async def main():
#     model = AzureChatOpenAI(
#         azure_deployment="gpt-4o-august-sandbox",
#         temperature=0.5,
#         streaming=True,
#         api_version="2023-06-01-preview"
#     )

#     instructions = open("EMS_prompt.md", "r").read()

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", instructions),
#             ("human", "{question}"),
#         ]
#     )
#     runnable = prompt | model | StrOutputParser()
#     cl.user_session.set("runnable", runnable)

# async def visualize_model():
#     await cl.Message(content="Start visualization").send()
#     subprocess.run(["python", "visualize.py", "generated_model.yml"], capture_output=True, text=True, check=True)
#     await cl.Message(content="Visualization complete").send()

# @cl.on_message
# async def on_message(message: cl.Message):
#         runnable = cl.user_session.get("runnable")  # type: Runnable
        
#         content = cl.Message(content="")
#         async for chunk in runnable.astream(
#             {"question": message.content},
#             config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
#         ):
#             await content.stream_token(chunk)
#             content += chunk

#         await content.send()
#         # Extract and validate YAML content
#         yaml_start = content.find("```yaml")
#         yaml_end = content.rfind("```")
        
#         if yaml_start != -1 and yaml_end != -1:
#             yaml_content = content[yaml_start+7:yaml_end].strip()
#         else:
#             yaml_content = content

#         await cl.Message(content="Writing YAML file").send()

#         with open("generated_model.yml", "w") as file:
#             file.write(yaml_content)
        
#         await cl.Message(content="Done writing YAML file - starting visualization").send()

#         multiprocessing.Process(target=visualize_model, args=("generated_model.yml",)).start()


        

        