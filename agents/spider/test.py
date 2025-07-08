import os
import pandas as pd
from dotenv import load_dotenv
import asyncio # Import asyncio for running async functions

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.runners import Runner, types
from google.adk.sessions import InMemorySessionService

# Load .env if needed
load_dotenv()

# Constants
APP_NAME = "movie_description_app"
USER_ID = "user1"
SESSION_ID = "session1"
                    

# Create the agent
root_agent = Agent(
    name="movie_search_agent",
    model="gemini-2.0-flash-exp",
    instruction=(
        "You are a smart assistant that receives a movie name as input and returns its description.\n"
        "Use the `Google Search` tool to search for '[movie name] movie description'.\n"
        "Extract the most relevant and concise description of the movie from the top results.\n"
        "Please provide the answer within the character limit specified in the input. If the description is longer, summarize or truncate it gracefully.\n" # Improved instruction
        "Respond with only the final description — do not mention the search process or list URLs."
    ),
    tools=[google_search],
)


# Function to call the agent (now asynchronous)
async def get_movie_description(runner_instance, movie_name, user_id, session_id, char_limit=1500):
    try:
        prompt = f"{movie_name} movie description. Character limit: {char_limit}"
        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        print(0)

        # The crucial change: Use async for with runner.run()
        events = runner_instance.run(user_id=user_id, session_id=session_id, new_message=content)
        print(1)


        for event in events:
            # print(event)
            print(2)
            if event.is_final_response():
                print(2.1)
                parts = event.content.parts
                return parts[0].text if parts else "No description found."
        return "No final response received from agent."
    except Exception as e:
        return f"Error retrieving description for {movie_name}: {e}"

# Main loop (now asynchronous)
async def main(): # Corrected: async def main()
    session_service = InMemorySessionService()

    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    print(f"Session created: {session.id}") # Confirm session ID

    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    movie_data = []
    print("Enter movie names one by one. Type 'done' when finished.")

    while True:
        movie_name = input("Movie name (or 'done'): ").strip()
        if movie_name.lower() == 'done':
            break
        if not movie_name:
            print("Movie name cannot be empty. Please try again.")
            continue

        print(f"Fetching description for '{movie_name}'...")
        # Corrected: await the get_movie_description call
        description = await get_movie_description(runner, movie_name, USER_ID, SESSION_ID)
        movie_data.append({"Movie Name": movie_name, "Description": description})
        print(f"Added: '{movie_name}' - '{description[:70]}...'")

    if movie_data:
        df = pd.DataFrame(movie_data)
        output_file = "movie_descriptions.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\nMovie descriptions saved to '{output_file}'")
        print(df)
    else:
        print("No data entered.")

if __name__ == "__main__":
    asyncio.run(main()) # Corrected: Run the main async function