import whisper
from openai import OpenAI
import ffmpeg
import os
import logging
import asyncio

# ロギング設定: エラーとプロセスの進行状況を追跡する
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s: %(levelname)s: %(message)s"
)


class VideoProcessor:
    """
    VideoProcessorクラスは、ビデオファイルから音声を抽出し、それをテキストに変換し、
    さらにそのテキストを要約する処理を行う。

    Attributes:
        input_video_path (str): 入力ビデオファイルのパス。
        output_audio_path (str): 出力オーディオファイルのパス。
        api_key (str): OpenAI APIのキー。
        client (OpenAI): OpenAI APIのクライアント。
    """

    def __init__(self, input_video_path, output_audio_path):
        """
        コンストラクタ。入力ビデオパス、出力オーディオパスを受け取り、
        OpenAI APIのクライアントを初期化する。

        Args:
            input_video_path (str): 入力ビデオファイルのパス。
            output_audio_path (str): 出力オーディオファイルのパス。
        """
        self.input_video_path = input_video_path
        self.output_audio_path = output_audio_path
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if self.api_key is None:
            raise EnvironmentError("OPENAI_API_KEYが環境変数に設定されていません。")
        self.client = OpenAI(api_key=self.api_key)

    def check_file_exists(self, file_path):
        """
        指定されたファイルが存在するかチェックする。

        Args:
            file_path (str): チェックするファイルのパス。

        Raises:
            FileNotFoundError: 指定されたファイルが存在しない場合に発生。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"指定されたファイル {file_path} が見つかりません。")

    # ビデオから音声を抽出
    def extract_audio(self):
        """
        ffmpegを使用してビデオファイルから音声を抽出する。

        Raises:
            Exception: 音声抽出中にエラーが発生した場合に発生。
        """
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
        """
        Whisperモデルを使用して音声ファイルをテキストに変換する。

        Returns:
            dict: 変換結果を含む辞書。

        Raises:
            Exception: テキスト変換中にエラーが発生した場合に発生。
        """
        self.check_file_exists(self.output_audio_path)
        try:
            model = whisper.load_model("medium")
            result = model.transcribe(
                self.output_audio_path, verbose=True, language="ja"
            )
            logging.info("音声のテキスト変換が完了しました。")
            return result
        except Exception as e:
            logging.error(f"音声のテキスト変換中にエラーが発生しました: {e}")
            raise

    # 動画を要約する
    async def summarize_video(self, text):
        """
        OpenAI APIを使用して提供されたテキスト（動画の文字起こし）を要約する。

        Args:
            text (str): 要約するテキスト。

        Returns:
            str: 要約されたテキスト。

        Raises:
            Exception: 要約中にエラーが発生した場合に発生。
        """
        try:
            video_summary = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはSummarizer Proです。Summarizer Proは、提供された動画の文字起こしを確認し、会話のすべての重要な側面をカバーします。主なトピック、決定事項、アクションアイテムの要約に焦点を当てます。全会一致の決定事項や重要な問題を強調します。要約は、簡潔でありながら議論の本質をとらえ、包括的でなければなりません。箇条書きにするか、番号の付いたリストにすると分かりやすい。フォローアップ・アクションのセクションを設け、タスク、期限、責任者を列挙する。会議の目的と出席者を概説する導入部から始める。重要なことを聞き逃さないよう、すべての内容を徹底的に説明する。",
                    },
                    {
                        "role": "user",
                        "content": f"""以下の(#動画の文字起こし)をもとに、(#出力形式)のフォーマットに合わせて議事録を作成してください。限界を超えてください。
                                      (#出力形式)
                                      [#会議での重要なトピックと決定事項]
                                      -
                                      -

                                      [#フォローアップ・アクション]
                                      -
                                      -

                                      (#動画の文字起こし)
                                      {text}""",
                    },
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
    """
    メイン関数。ビデオ処理の全体的な流れを管理する。

    以下のステップを実行する:
    1. VideoProcessorクラスのインスタンスを作成する。
    2. ビデオから音声を抽出する。
    3. 音声をテキストに変換する。
    4. テキストを要約する。
    """
    input_video_path = "video/Harvest&Forecast.mp4"
    output_audio_path = "video/Harvest&Forecast.mp3"
    processor = VideoProcessor(input_video_path, output_audio_path)
    processor.extract_audio()
    transcription_result = await processor.transcribe_audio()
    summary = await processor.summarize_video(transcription_result["text"])
    print(summary)

if __name__ == "__main__":
    asyncio.run(main())
