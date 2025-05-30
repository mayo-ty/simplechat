# lambda/index.py
import json
import os
#import boto3
import re  # 正規表現モジュールをインポート
#from botocore.exceptions import ClientError
import urllib.request

# Lambda コンテキストからリージョンを抽出する関数
#def extract_region_from_arn(arn):
    # ARN 形式: arn:aws:lambda:region:account-id:function:function-name
#    match = re.search('arn:aws:lambda:([^:]+):', arn)
#    if match:
#        return match.group(1)
#    return "us-east-1"  # デフォルト値

# グローバル変数としてクライアントを初期化（初期値）
#bedrock_client = None

# モデルID
#MODEL_ID = os.environ.get("MODEL_ID", "us.amazon.nova-lite-v1:0")
FASTAPI_ENDPOINT = os.environ.get("FASTAPI_ENDPOINT", "https://dffd-34-142-207-39.ngrok-free.app/generate")
def lambda_handler(event, context):
    try:
        
        print("Received event:", json.dumps(event))
        # Cognitoで認証されたユーザー情報を取得
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])
        
        print("Processing message:", message)
        
        
       # FastAPIに送るペイロードを構築
        payload = {
                "prompt": message,
                "max_new_tokens": 128,
                "do_sample": True,
                "temperature": 0.7,
                "top_p": 0.9
        }
        messages = conversation_history.copy()

       # FastAPI に送るペイロード


       # FastAPIにリクエスト送信
        req = urllib.request.Request(
        FASTAPI_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
        )
        with urllib.request.urlopen(req) as res:
            response_body = json.loads(res.read().decode("utf-8"))

        print("FastAPI response:", json.dumps(response_body))

        assistant_response = response_body["generated_text"]
        messages.append({
            "role": "assistant",
            "content": assistant_response
            })

        # 成功レスポンスの返却
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }
        
    except Exception as error:
        print("Error:", str(error))
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
