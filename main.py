"""Chainlit"""
import chainlit as cl

"""OpenAI"""
from langchain_openai import AzureChatOpenAI

"""Langchain"""
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

"""Yaml"""
import yaml

"""Subprocess"""
import subprocess

@cl.on_chat_start
async def main():    
    model = AzureChatOpenAI(
        azure_deployment="gpt-4o-august-sandbox",
        temperature=0.5,
        streaming=True,
        api_version="2023-06-01-preview"
    )

    hotel_booking_yaml = open("HotelBooking.yml", "r").read()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                  """
                  You are very knowledgable on Domain Driven Design and Event Modeling. 
                  I will ask you to generate a yaml file to describe an event model.
                  You are already given an example of such a file, that being a Hotel Booking System described in HotelBooking.yml
                  Here's the content of HotelBooking.yml for reference:
                  {hotel_booking_yaml}
                  """.format(hotel_booking_yaml = hotel_booking_yaml)
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)
    

@cl.on_message
async def main(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    max_attempts = 30
    for attempt in range(max_attempts):
        print('attempt no:', attempt)
        generated_content = ""
        async for chunk in runnable.astream(
            {"question": message.content if attempt == 0 else f"Fix the following YAML errors and regenerate the YAML: {error_message}"},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            generated_content += chunk

        try:
            # Extract and validate YAML content
            yaml_start = generated_content.find("```yaml")
            yaml_end = generated_content.rfind("```")
            
            if yaml_start != -1 and yaml_end != -1:
                yaml_content = generated_content[yaml_start+7:yaml_end].strip()
            else:
                yaml_content = generated_content

            # Validate YAML
            yaml.safe_load(yaml_content)

            # Save the validated YAML to a file
            with open("generated_model.yml", "w") as file:
                file.write(yaml_content)

            # Run the visualize.py script with the generated YAML as input
            result = subprocess.run(["python", "visualize.py", "generated_model.yml"], capture_output=True, text=True, check=True)
            
            # If we reach here, the script ran successfully
            await cl.Message(content="YAML generated and visualization complete. Check the output file.").send()
            
            # If visualize.py produces any output, send it to the user
            if result.stdout:
                await cl.Message(content=f"Visualization output:\n```\n{result.stdout}\n```").send()
            
            # Exit the loop if successful
            break

        except (yaml.YAMLError, subprocess.CalledProcessError) as e:
            error_message = str(e)
            if attempt == max_attempts - 1:
                await cl.Message(content=f"Failed to generate valid YAML after {max_attempts} attempts. Last error:\n```\n{error_message}\n```").send()
            else:
                await cl.Message(content=f"Attempt {attempt + 1} failed. Retrying...").send()