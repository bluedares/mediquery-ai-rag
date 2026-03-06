# AWS Support Request Template

## Issue: Unable to Access Bedrock Models - Payment Instrument Error

### Problem Description
I am unable to use AWS Bedrock Claude models despite having a verified and default payment method configured. All API calls to Bedrock return the following error:

```
AccessDeniedException: Model access is denied due to INVALID_PAYMENT_INSTRUMENT:
A valid payment instrument must be provided. Your AWS Marketplace subscription 
for this model cannot be completed at this time.
```

### Account Details
- **AWS Account ID**: [Your account ID from AWS Console]
- **Region**: us-east-1
- **Service**: Amazon Bedrock
- **Models Attempted**: 
  - anthropic.claude-3-haiku-20240307-v1:0
  - anthropic.claude-3-sonnet-20240229-v1:0
  - anthropic.claude-3-5-sonnet-20241022-v2:0

### Payment Method Status
- ✅ Payment method added: American Express ending in 1003
- ✅ Set as **Default** payment method
- ✅ Shows as active in Billing Console
- ✅ Billing address configured

### Steps Already Taken
1. Added valid payment method (American Express)
2. Set as default payment method
3. Waited 2+ hours for validation
4. Verified payment method shows as "Default" in console
5. Tested multiple Bedrock model IDs
6. Checked for email verification requests (none received)

### Request
Please manually validate my payment method for AWS Bedrock service access, or advise on any additional steps needed to resolve this issue. I need to use Bedrock Claude models for a production application.

### Error Logs
```
🧪 Testing: anthropic.claude-3-haiku-20240307-v1:0
   ❌ FAILED: AccessDeniedException
   Message: Model access is denied due to INVALID_PAYMENT_INSTRUMENT:
   A valid payment instrument must be provided.
```

### Urgency
High - This is blocking production deployment.

### Contact Preference
Email: [Your email from billing console]
Phone: [Your phone if urgent]

---

## How to Submit This Request

1. Go to: https://console.aws.amazon.com/support/home#/case/create
2. Select **"Account and billing support"**
3. Category: **"Billing"**
4. Subject: **"Unable to use Bedrock - Invalid payment instrument error"**
5. Copy the content above into the description
6. Submit

**Expected Response Time**: 15 minutes - 1 hour for billing issues
