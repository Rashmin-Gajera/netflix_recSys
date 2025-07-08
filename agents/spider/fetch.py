import os
import pandas as pd
from dotenv import load_dotenv
import asyncio
import time
import random
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import Runner, types
from google.adk.sessions import InMemorySessionService

# Load environment variables
load_dotenv()

# Constants
APP_NAME = "movie_description_app"
USER_ID = "user2"
INPUT_FILE = "movie_descriptions.csv"
OUTPUT_FILE = "movie_descriptions.csv"

# Create the agent
root_agent = Agent(
    name="movie_search_agent",
    model="gemini-1.5-flash",
    instruction=(
        "You are a smart assistant that receives a movie/webseries name as input and returns its description.\n"
        "Use the `Google Search` tool to search for '[movie name] movie/webseries description'.\n"
        "Extract the most relevant and concise description of the movie/webseries from the top results.\n"
        "Please provide the answer within the character limit specified in the input. If the description is longer, summarize or truncate it gracefully.\n"
        "Respond with only the final description — do not mention the search process or list URLs."
    ),
    tools=[google_search],
)

# Async function to get movie description
async def get_movie_description(runner_instance, movie_name, user_id, session_id, char_limit=1800):
    try:
        prompt = f"{movie_name} - a netflix movie/webseries description. Character limit: {char_limit}. You should return only description."
        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        print(f"Fetching description for movie: '{movie_name}'")

        events = runner_instance.run(user_id=user_id, session_id=session_id, new_message=content)

        for event in events:
            if event.is_final_response():
                parts = event.content.parts
                time.sleep(2)
                return parts[0].text if parts else "No description found."

        return "No final response received from agent."
    except Exception as e:
        time.sleep(20)
        return f"Error retrieving description for {movie_name}: {e}"

# Main async logic
async def main():
    session_service = InMemorySessionService()
    df = pd.read_csv(INPUT_FILE)
    processed_rows=0

    # Ensure 'fetched_description' column exists
    if 'fetched_description' not in df.columns:
        df['fetched_description'] = ""

    # Initialize the runner outside the loop to avoid frequent reinitialization
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    # Iterate and fetch descriptions where missing
    for index, row in df.iterrows():
        if pd.notna(row['fetched_description']) and str(row['fetched_description']).strip() != "":
            print(f"Skipping '{row['title']}' - already has description. Index: {index}")
            continue
        
        if processed_rows % 50 == 0:  # Create a new session every 100 rows
            session_id = f"session_{processed_rows // 50}"
            session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
            print(f"Session created: {session.id}")
            runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

        description = await get_movie_description(runner, row['title'], USER_ID, session_id)
        processed_rows+=1

        if description == "No final response received from agent.":
            break

        df.at[index, 'fetched_description'] = description
        print(f"Index: {index} , Fetched: {description}")

        # Save after every 10 rows 
        if processed_rows % 10 == 0:
            df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

        # Add random sleep time to respect rate limits
        time.sleep(random.uniform(1, 2))

    # Final save after loop
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"\nAll movie descriptions updated in '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    asyncio.run(main())
