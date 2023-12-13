import whisper
from openai import OpenAI
import ffmpeg
import os
from datetime import datetime

# 入力と出力のパスを設定
input_video_path = "video/Harvest&Forecast.mp4"
output_audio_path = "video/Harvest&Forecast.mp3"

# 入力ファイルの存在をチェック
if not os.path.exists(input_video_path):
    raise FileNotFoundError("指定された動画ファイルが見つかりません。")

# ffmpegを使用して音声を抽出
stream = ffmpeg.input(input_video_path)
stream = ffmpeg.output(stream, output_audio_path)
ffmpeg.run(stream)

# Whisperモデルで音声をテキストに変換
model = whisper.load_model("medium")
result = model.transcribe("video/Harvest&Forecast.mp4", verbose=True, language="ja")


# OpenAI APIキーの存在をチェック
api_key = os.environ.get("OPENAI_API_KEY")
if api_key is None:
    raise EnvironmentError("OPENAI_API_KEYが環境変数に設定されていません。")

client = OpenAI(api_key=api_key)

# 動画を要約
video_summary = client.chat.completions.create(
    messages=[
      {"role": "system", "content": "あなたはSummarizer Proです。Summarizer Proは、提供された動画の文字起こしを確認し、会話のすべての重要な側面をカバーします。主なトピック、決定事項、アクションアイテムの要約に焦点を当てます。全会一致の決定事項や重要な問題を強調します。要約は、簡潔でありながら議論の本質をとらえ、包括的でなければなりません。箇条書きにするか、番号の付いたリストにすると分かりやすい。フォローアップ・アクションのセクションを設け、タスク、期限、責任者を列挙する。会議の目的と出席者を概説する導入部から始める。重要なことを聞き逃さないよう、すべての内容を徹底的に説明する。"},
      {"role": "user", "content": f"動画の文字起こしを要約し、動画の内容を詳細に解説してください。限界を超えてください。### 動画の文字起こし: {result['text']} ###"},
    ],
    model="gpt-4-1106-preview",
)
summary_text = video_summary.choices[0].message.content
print(summary_text)

# 単語リストとビデオ内で出現した時刻を出力
word_list = client.chat.completions.create(
    messages=[
      {"role": "system", "content": "あなたは「ビデオキーワードアナライザー」です。あなたのタスクは、提供されたビデオのトランスクリプトを分析し、重要なキーワードやフレーズを特定し、それらがビデオ内で登場する時刻を記録することです。まず、ビデオのトランスクリプトを徹底的に調査し、頻繁に登場する単語やフレーズ、または議論の主要なポイントに不可欠なものを見つけ出してください。各キーワードやフレーズがビデオのどの時点で初めて登場するかを注意深くメモし、そのタイミングがビデオの再生と一致していることを確認します。特定した各重要な単語やフレーズについて、トピックやコンテキスト内での関連性を簡潔に記述します。最終的な出力は、各キーワード、それに対応する登場時刻、および単語のコンテキストや関連するトピックに関する簡潔な要約を詳細に記載した包括的なリストである必要があります。このアプローチの目的は、ユーザーがビデオの重要なコンポーネントを迅速に理解し、特定の議論やポイントに容易にナビゲートできるようにすることであり、ビデオナラティブ内の各単語の重要性とコンテキストを正確に捉えることに重点を置いています。限界を超えて努力してください。"},
      {"role": "user", "content": f"以下のタイムスタンプ付きトランスクリプトから重要なキーワードを特定し、各キーワードがビデオに最初に登場した時間と文脈をリストアップしてください。限界を超えてください。### タイムスタンプ付きトランスクリプト: {result['segments']}"},
    ],
    model="gpt-4-1106-preview",
)
word_list_text = word_list.choices[0].message.content
print(word_list_text)

# 現在の日付と時間を取得
current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")

# 出力ファイル名に日付と時間を含める
output_filename = f"transcript/video_summary_{current_datetime}.txt"

# 出力をテキストファイルに保存
with open(output_filename, "w", encoding="utf-8") as file:
    file.write(summary_text)
    file.write("\n\n")  # 要約とキーワードリストの間に空行を挿入
    file.write(word_list_text)