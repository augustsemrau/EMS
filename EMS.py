"""Main file for Event Modeling System (EMS), as a prototype for using LLM assistance in Event Modelling."""


# Langchain imports
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain

## Local imports
from utils import init_llm_langsmith




class EMS:
    """Event Modeling System (EMS)."""

    def __init__(self,
                 llm_model,

                 student_name: str = "August",
                 course: str = "IntroToMachineLearning",
                 subject: str = "Linear Regression",
                 learning_prefs: str = "Prefers visual representations of the subject",
                 student_id=None,
                 ltm_query="",
                 ):
        """Initialize the EMS."""
        self.llm_model = llm_model
        self.course = course
        self.student_id = student_id # If student_id is None, the TAS will not use long-term memory
        self.student_name = student_name

        # Init short term memory
        self.short_term_memory = ConversationBufferMemory(memory_key="chat_history",
                                                          return_messages=False,
                                                          ai_prefix="Assistant",
                                                          human_prefix="User")

        self.prompt = self.build_prompt(student_name=student_name,
                                                course_name=course,
                                                subject_name=subject,
                                                learning_preferences=learning_prefs,
                                                ltm_query=ltm_query)
        
        # Build the executor
        # self.executor = self.build_tas()
        # self.output_tag = "output"
        self.executor = self.build_nonagenic_baseline()
        self.output_tag = "response"


    def build_nonagenic_baseline(self):
        """Baseline LLM Chain Teaching System."""
        prompt = {
            "chat_history": {},
            "input": input,
            "system_message": ".",
        }
        prompt_template = """You are a teaching assistant. You are responsible for answering questions and inquiries that the student might have.
Here is the student's query, which you MUST respond to:
{input}
This is the conversation so far:
{chat_history}"""
        prompt = PromptTemplate.from_template(template=prompt_template)
        baseline_chain = ConversationChain(llm=self.llm_model,
                                prompt=prompt,
                                memory=self.short_term_memory,
                                #output_parser=BaseLLMOutputParser(),
                                verbose=False,)
        return baseline_chain


    def build_prompt(self, student_name, course_name, subject_name, learning_preferences, ltm_query):
        """Build the agent prompt."""
        facts = "No prior conversations for this user."
        if self.student_id is not None and ltm_query != "":
            facts = self.long_term_memory_class.predict(query=ltm_query)
        prompt_hub_template = hub.pull("augustsemrau/react-tas-prompt-3").template
        prompt_template = PromptTemplate.from_template(template=prompt_hub_template)
        prompt = prompt_template.partial(student_name=student_name,
                                         course_name=course_name,
                                         subject_name=subject_name,
                                         learning_preferences=learning_preferences,
                                         ltm_facts=facts,
                                        )
        return prompt

    def build_tas(self):
        """Build the Teaching Agent System (TAS)."""
        tool_class = ToolClass()
        tools = [tool_class.build_search_tool(),
                 tool_class.build_retrieval_tool(course_name=self.course),
                #  tool_class.build_coding_tool(),
                ]

        tas_agent = create_react_agent(llm=self.llm_model,
                                       tools=tools,
                                       prompt=self.tas_prompt,
                                       output_parser=None)
        tas_agent_executor = AgentExecutor(agent=tas_agent,
                                           tools=tools,
                                           memory=self.short_term_memory,
                                           verbose=True,
                                           handle_parsing_errors=True)
        return tas_agent_executor



    def predict(self, query):
        """Invoke the Teaching Agent System."""
        print("\n\nUser Query:\n", query)
        response = self.executor.invoke({"input": query})[self.output_tag]
        print("\n\nResponse:\n", response)
        return response











if __name__ == '__main__':

    ls_name = "EMS_InitialTesting"
    llm_model = init_llm_langsmith(llm_key=3, temp=0.5, langsmith_name=ls_name)


    ems = EMS(llm_model=llm_model,)

    res = ems.predict(query="Hello")
    # res = ems.predict(query="I'm not sure I understand the subject from this explanation. Can you explain it in a different way?")
    # res = ems.predict(query="Thank you for the help, have a nice day!")


