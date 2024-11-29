import requests
import json
import boto3
from web import get_all_news


def txt_to_text(file_path):
    with open(file_path, "r") as f:
        text = f.read()
    return text


def bedrock_chatbot(text):
    response = boto3.client("bedrock-runtime").invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": text}],
                "max_tokens": 8192,
                "temperature": 0,
                "system": "최종 답변은 반드시 한국어로 해야 해. 주어진 뉴스와 질문을 바탕으로 참/거짓을 판단해 줘. 응답의 첫째 줄에는 '참' 또는 '거짓'을 적어 주고, 그 이후에는 자유롭게 답변을 작성해 주면 돼."
                + txt_to_text("claude-o1.txt"),
            }
        ),
        accept="application/json",
        contentType="application/json",
    )
    return json.loads(response.get("body").read())["content"][0]["text"]


def load_keyward(text):
    response = boto3.client("bedrock-runtime").invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": text}],
                "max_tokens": 8192,
                "temperature": 0,
                "system": "근거자료 탐색을 위한 쿼리로 적절한 한 단어를 출력해 봐, 한 단어만 반환해야 해. 다른 문장은 붙이지 마. 띄어쓰기 단위로 단어를 구성해 줘.",
            }
        ),
        accept="application/json",
        contentType="application/json",
    )
    return json.loads(response.get("body").read())["content"][0]["text"]


def lambda_handler(event, context):
    text_input = event["text_input"]
    callback_url = event["callback_url"]

    keyward = load_keyward(text_input)
    print(keyward)

    try:
        news = get_all_news(f"{keyward}")

        result = bedrock_chatbot(f"질의문: {text_input}, 뉴스: {news}")

        # https://kakaobusiness.gitbook.io/main/tool/chatbot/skill_guide/ai_chatbot_callback_guide#skillresponse
        requests.post(
            callback_url,
            json={
                "version": "2.0",
                "useCallback": False,
                "template": {"outputs": [{"simpleText": {"text": f"{result}"}}]},
            },
        )
        return True
    except:
        requests.post(
            callback_url,
            json={
                "version": "2.0",
                "useCallback": False,
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "근거자료를 찾을 수 없습니다. 다른 키워드를 입력해 주세요."
                            }
                        }
                    ]
                },
            },
        )
        return False
