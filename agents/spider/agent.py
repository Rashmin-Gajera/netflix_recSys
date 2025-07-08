import os
from google.adk import Agent
from google.adk.agents import LlmAgent, ParallelAgent
from google.adk.tools import google_search
from dotenv import load_dotenv
load_dotenv()

# root_agent = Agent(
#     name="spider",
#     model = "gemini-2.0-flash",
#     description = "Spider is AI Agent, who is responsible to find the movie desecription using the google Serach",
#     instruction = "You are a helpful AI assistant that can use following tools: - google_serach",
#     tools = [google_search]
# )



root_agent = LlmAgent(
    name="spider",
    model="gemini-2.0-flash",
    description="Spider is a movie assistant that retrieves information like movie descriptions using Google search.",
    instruction=(
        "You are a smart assistant that receives a movie name as input and returns its description.\n"
        "Use the `google_search` tool to search for '[movie name] movie description'.\n"
        "Extract the most relevant and concise description of the movie from the top results.\n"
        "Please take the character limit from the input and give answer on that limits.\n"
        "Respond with only the final description — do not mention the search process or list URLs."
    ),
    tools=[google_search]
)