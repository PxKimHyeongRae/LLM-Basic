from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

completion = client.chat.completions.create(
  extra_body={},
  model="tngtech/deepseek-r1t2-chimera:free",
  messages=[
    {
      "role": "user",
      "content": "어제의 평균온도는 18도고 오늘의 평균온도는 24도야. 이런 경우에 공원을 방문하는 고객들에게 적절하게 전달해줄 전광판 메시지를 작성해줘 (100자 이내)"
    }
  ]
)
print(completion.choices[0].message.content)