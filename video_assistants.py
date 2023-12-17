from openai import OpenAI
import os
import time

# OpenAI APIキーの存在をチェック
api_key = os.environ.get("OPENAI_API_KEY")
if api_key is None:
    raise EnvironmentError("OPENAI_API_KEYが環境変数に設定されていません。")

client = OpenAI(api_key=api_key)

file = client.files.create(
    file=open("transcript.txt", "rb"),
    purpose="assistants"
)

assistant = client.beta.assistants.create(
  name="Transcript Assistant",
  instructions="Transcript Assistantはトランスクリプトファイルに基づいてユーザーの質問に対して簡潔に回答するチャットボットです。ユーザーの質問が漠然としていたり不明確な場合、チャットボットは説明を求めるようにプログラムされています。これにより、提供される回答が可能な限り正確で適切なものになります。",
  model="gpt-4-1106-preview",
  tools=[{"type": "retrieval"}],
  file_ids=[file.id]
)

def submit_message(assistant_id, thread, user_message):
    # 新しいメッセージをスレッドに追加
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    
    # アシスタントに対してスレッド内のメッセージを確認し、行動を取るよう指示
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def get_assistant_responses(thread):
    responses = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
    assistant_responses = [msg.content[0].text.value for msg in responses.data if msg.role == 'assistant']
    return assistant_responses
  
def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(assistant.id, thread, user_input)
    return thread, run

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

thread1, run1 = create_thread_and_run("アップロードしたファイルを参照して、フォローアップ・アクションを教えてください。")
run1 = wait_on_run(run1, thread1)

for response in get_assistant_responses(thread1):
    print(response)