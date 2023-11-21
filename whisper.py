import whisper
from openai import OpenAI

model = whisper.load_model("large")
result = model.transcribe("", verbose=True, language="ja")
print(result["text"])

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="",
)

chat_completion = client.chat.completions.create(
    messages=[
      {"role": "system", "content": "You are one of the best in the world at making minutes. Review the minutes provided and prepare a summary in Japanese. Focus on the main topics discussed, decisions made, and action items agreed upon. Pay special attention to unanimous decisions or significant issues that arose. Present your summary in a clear and structured format, preferably using bullet points or a numbered list. Include a section for follow-up actions, listing any tasks assigned, along with their deadlines and the responsible parties. Begin with a short introduction detailing the meeting’s purpose and the list of attendees."},
      {"role": "user", "content": f"Summarize the submitted minutes. Minutes: {result['text']}"},
    ],
    model="gpt-4-1106-preview",
)

print(chat_completion['choices'][0]['message']['content'])