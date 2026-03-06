#!/usr/bin/env python3
"""
Test AWS Bedrock Model Access
This script checks which Claude models are available in your AWS account.
"""

import boto3
import json
from botocore.exceptions import ClientError
import os

# Load credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "your_aws_access_key_here")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "your_aws_secret_key_here")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

print("=" * 80)
print("AWS BEDROCK MODEL ACCESS TEST")
print("=" * 80)

# Initialize Bedrock client
try:
    bedrock = boto3.client(
        'bedrock',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    print(f"✅ Bedrock client initialized (region: {AWS_REGION})")
except Exception as e:
    print(f"❌ Failed to initialize Bedrock client: {e}")
    exit(1)

# List all foundation models
print("\n" + "=" * 80)
print("AVAILABLE ANTHROPIC CLAUDE MODELS")
print("=" * 80)

try:
    response = bedrock.list_foundation_models(byProvider='Anthropic')
    models = response.get('modelSummaries', [])
    
    if not models:
        print("⚠️  No Anthropic models found")
    else:
        for model in models:
            model_id = model.get('modelId')
            model_name = model.get('modelName', 'N/A')
            status = model.get('modelLifecycle', {}).get('status', 'UNKNOWN')
            print(f"\n📦 {model_name}")
            print(f"   ID: {model_id}")
            print(f"   Status: {status}")
            
except ClientError as e:
    print(f"❌ Error listing models: {e}")
    print(f"   Error Code: {e.response['Error']['Code']}")
    print(f"   Error Message: {e.response['Error']['Message']}")

# Test model invocation with a simple prompt
print("\n" + "=" * 80)
print("TESTING MODEL INVOCATION")
print("=" * 80)

# Try different model IDs (using inference profiles)
test_models = [
    "us.anthropic.claude-sonnet-4-20250514-v1:0",      # Sonnet 4 (recommended)
    "us.anthropic.claude-3-7-sonnet-20250219-v1:0",    # Sonnet 3.7
    "us.anthropic.claude-haiku-4-5-20251001-v1:0",     # Haiku 4.5 (fastest/cheapest)
    "anthropic.claude-3-haiku-20240307-v1:0"           # Legacy Haiku 3
]

bedrock_runtime = boto3.client(
    'bedrock-runtime',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

for model_id in test_models:
    print(f"\n🧪 Testing: {model_id}")
    
    try:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": "Say 'test successful' if you can read this."}],
            "max_tokens": 50,
            "temperature": 0.1
        })
        
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body
        )
        
        result = json.loads(response['body'].read())
        answer = result['content'][0]['text']
        
        print(f"   ✅ SUCCESS! Model is accessible")
        print(f"   Response: {answer}")
        print(f"   👉 USE THIS MODEL ID: {model_id}")
        break
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"   ❌ FAILED: {error_code}")
        print(f"   Message: {error_msg[:100]}...")
    except Exception as e:
        print(f"   ❌ FAILED: {type(e).__name__}: {str(e)[:100]}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\n💡 Next Steps:")
print("1. If all models failed, go to AWS Console → Bedrock → Model Access")
print("2. Click 'Manage model access' and enable Claude models")
print("3. Wait 2-5 minutes for approval")
print("4. Re-run this script to find working model ID")
print("5. Update BEDROCK_MODEL_ID in backend/.env with working model ID")
