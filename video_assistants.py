from openai import OpenAI
import os
import time

# OpenAI APIキーの存在をチェック
api_key = os.environ.get("OPENAI_API_KEY")
if api_key is None:
    raise EnvironmentError("OPENAI_API_KEYが環境変数に設定されていません。")

client = OpenAI(api_key=api_key)

file = client.files.create(
    file=open(
        "Transcript File",
        "rb",
    ),
    purpose="assistants",
)

assistant = client.beta.assistants.create(
  name="Transcript Assistant",
  instructions="Transcript Assistantは会話形式で対話するように設計されており、トランスクリプトファイルに基づいてクエリに応答するように最適化されています。ユーザーの質問が漠然としていたり不明確な場合、チャットボットは説明を求めるようにプログラムされています。これにより、提供される回答が可能な限り正確で適切なものになります。ユーザーの意図を理解することを優先し、トランスクリプトから正確な情報を提供することで、明確で適切なコミュニケーションを確保し、ユーザーエクスペリエンスを向上させます。",
  model="gpt-4-1106-preview",
  tools=[{"type": "retrieval"}],
  file_ids=[file.id]
)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="会議目的は何ですか？"
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

while True:
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(run.status)
    if run.status == "completed":
        break
    time.sleep(1)

messages = client.beta.threads.messages.list(
  thread_id=thread.id
)

for message in messages:
    print(message.content)
