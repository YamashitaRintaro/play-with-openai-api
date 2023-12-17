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
        "transcript.txt",
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

# 会話の状態を保持
thread = client.beta.threads.create()

# 新しいメッセージをスレッドに追加
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=input() 
)

# アシスタントに対してスレッド内のメッセージを確認し、行動を取るよう指示
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
)

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

run = wait_on_run(run, thread)

messages = client.beta.threads.messages.list(
  thread_id=thread.id, order="asc", after=message.id
)

for message in messages:
    print(message.content)
