import whisper
from openai import OpenAI
import ffmpeg
import os
import logging
import asyncio

# ロギング設定: エラーとプロセスの進行状況を追跡する
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

class VideoProcessor:
    def __init__(self, input_video_path, output_audio_path):
        self.input_video_path = input_video_path
        self.output_audio_path = output_audio_path
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if self.api_key is None:
            raise EnvironmentError("OPENAI_API_KEYが環境変数に設定されていません。")
        self.client = OpenAI(api_key=self.api_key)

    def check_file_exists(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定されたファイル {file_path} が見つかりません。")

    # ビデオから音声を抽出
    def extract_audio(self):
        self.check_file_exists(self.input_video_path)
        try:
            stream = ffmpeg.input(self.input_video_path)
            stream = ffmpeg.output(stream, self.output_audio_path)
            ffmpeg.run(stream)
            logging.info("音声の抽出が完了しました。")
        except Exception as e:
            logging.error(f"音声抽出中にエラーが発生しました: {e}")
            raise

    # 音声を文字起こし
    async def transcribe_audio(self):
        self.check_file_exists(self.output_audio_path)
        try:
            model = whisper.load_model("medium")
            result = model.transcribe(self.output_audio_path, verbose=True, language="ja")
            logging.info("音声のテキスト変換が完了しました。")
            return result
        except Exception as e:
            logging.error(f"音声のテキスト変換中にエラーが発生しました: {e}")
            raise

    # 動画を要約する
    async def summarize_video(self, text):
        try:
            video_summary = self.client.chat.completions.create(
            messages=[
              {"role": "system", "content": "あなたはSummarizer Proです。Summarizer Proは、提供された動画の文字起こしを確認し、会話のすべての重要な側面をカバーします。主なトピック、決定事項、アクションアイテムの要約に焦点を当てます。全会一致の決定事項や重要な問題を強調します。要約は、簡潔でありながら議論の本質をとらえ、包括的でなければなりません。箇条書きにするか、番号の付いたリストにすると分かりやすい。フォローアップ・アクションのセクションを設け、タスク、期限、責任者を列挙する。会議の目的と出席者を概説する導入部から始める。重要なことを聞き逃さないよう、すべての内容を徹底的に説明する。"},
              {"role": "user", "content": f"動画の文字起こしを要約し、動画の内容を詳細に解説してください。限界を超えてください。### 動画の文字起こし: {result['text']} ###"},
            ],
                model="gpt-4-1106-preview",
            )
            logging.info("動画の要約が完了しました。")
            return video_summary.choices[0].message.content
        except Exception as e:
            logging.error(f"動画の要約中にエラーが発生しました: {e}")
            raise

# メイン関数: ビデオ処理の流れを管理する
async def main():
    input_video_path = "video/Harvest&Forecast.mp4"
    output_audio_path = "video/Harvest&Forecast.mp3"
    processor = VideoProcessor(input_video_path, output_audio_path)
    processor.extract_audio()
    transcription_result = await processor.transcribe_audio()
    summary = await processor.summarize_video(transcription_result['text'])
    print(summary)

if __name__ == "__main__":
    asyncio.run(main())
