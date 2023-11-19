from openai import OpenAI
import os

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# (method) def generate(
#     *,
#     prompt: str,
#     model: str | NotGiven | None = NOT_GIVEN,
#     n: int | NotGiven | None = NOT_GIVEN,
#     quality: NotGiven | Literal['standard', 'hd'] = NOT_GIVEN,
#     response_format: NotGiven | Literal['url', 'b64_json'] | None = NOT_GIVEN,
#     size: NotGiven | Literal['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792'] | None = NOT_GIVEN,
#     style: NotGiven | Literal['vivid', 'natural'] | None = NOT_GIVEN,
#     user: str | NotGiven = NOT_GIVEN,
#     extra_headers: Headers | None = None,
#     extra_query: Query | None = None,
#     extra_body: Body | None = None,
#     timeout: float | Timeout | NotGiven | None = NOT_GIVEN
# ) -> ImagesResponse

response = client.images.generate(
  model="dall-e-3",
  prompt="Incredible and spectacular views",
  size="1024x1024",
  quality="standard",
  n=1,
)

image_url = response.data[0].url
print(image_url)