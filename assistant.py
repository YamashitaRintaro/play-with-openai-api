from openai import OpenAI
import os
import time
import json

def show_json(obj):
    display(json.loads(obj.model_dump_json()))

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# filename = "./image/20230725_resources_ai_outline.pdf"

# files = client.files.create(
#   file=open(filename, "rb"),
#   purpose="assistants"
# )

# Step 1: Create an Assistant
assistant = client.beta.assistants.create(
  name="Math Tutor",
  
  # how the Assistant and model should behave or respond
  instructions="You are a personal math tutor. Write and run code to answer math questions.",
  
  # the API supports Code Interpreter and Retrieval that are built and hosted by OpenAI.
  tools=[{"type": "code_interpreter"}],
  
  model="gpt-4-1106-preview"
)

# Step 2: Create a Thread
thread = client.beta.threads.create()
show_json(assistant)

# Step 3: Add a Message to a Thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)

# Step 4: Run the Assistant
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as Jane Doe. The user has a premium account."
)

# Step 5: Check the Run status
run = client.beta.threads.runs.retrieve(
  thread_id=thread.id,
  run_id=run.id
)

print(run)

# Step 6: Display the Assistant's Response
messages = client.beta.threads.messages.list(
  thread_id=thread.id
)

print(messages)
