import asyncio
from pipeline_stages import PipelineStages

async def test_pii_redaction():
    test_data = {
        "name": "Ahmed Mohammed",
        "email": "ahmed@example.com",
        "phone": "0501234567",
        "id_number": "1234567890",
        "account": "SA1234567890123456789012",
        "nested": {
            "contact_email": "contact@company.sa",
            "mobile": "+966501234567"
        },
        "list_items": [
            "Call 0509876543 for details",
            "Email: info@test.com"
        ]
    }
    
    print("Original Data:")
    print(test_data)
    print("\n" + "="*60 + "\n")
    
    result = await PipelineStages.detect_and_redact_pii(test_data)
    
    print("Redacted Data:")
    print(result["redacted_data"])
    print("\n" + "="*60 + "\n")
    
    print("PII Detected:")
    for pii in result["pii_detected"]:
        print(f"  - {pii['type']} found at {pii['location']}")
    
    print("\n" + "="*60 + "\n")
    
    print("Verification:")
    redacted = result["redacted_data"]
    
    if "ahmed@example.com" in str(redacted):
        print("❌ FAILED: Email not redacted!")
    else:
        print("✓ Email successfully redacted")
    
    if "0501234567" in str(redacted):
        print("❌ FAILED: Phone not redacted!")
    else:
        print("✓ Phone successfully redacted")
    
    if "1234567890" in str(redacted):
        print("❌ FAILED: National ID not redacted!")
    else:
        print("✓ National ID successfully redacted")
    
    if "SA1234567890123456789012" in str(redacted):
        print("❌ FAILED: IBAN not redacted!")
    else:
        print("✓ IBAN successfully redacted")
    
    if "contact@company.sa" in str(redacted):
        print("❌ FAILED: Nested email not redacted!")
    else:
        print("✓ Nested email successfully redacted")
    
    if "info@test.com" in str(redacted):
        print("❌ FAILED: List item email not redacted!")
    else:
        print("✓ List item email successfully redacted")
    
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(test_pii_redaction())
