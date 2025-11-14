import re
import asyncio
import random
from typing import Dict, Any, Tuple, List
from datetime import datetime
from PyPDF2 import PdfReader
import json


class PipelineStages:
    
    CLASSIFICATION_MODEL = "v1.2-comprehend-classifier"
    EXTRACTION_MODEL = "textract-analyze-v3.0"
    VALIDATION_VERSION = "v2.1-business-rules"
    
    @staticmethod
    async def classify_document(file_path: str) -> Tuple[str, Dict[str, Any], float]:
        await asyncio.sleep(0.5)
        
        keywords = {
            "INVOICE": ["invoice", "bill", "amount due", "total", "vendor", "payment"],
            "NATIONAL_ID": ["national id", "identity card", "id number", "date of birth", "nationality"],
            "BANK_STATEMENT": ["bank statement", "account", "balance", "transaction", "deposit", "withdrawal"],
            "PAYSLIP": ["payslip", "salary", "earnings", "deductions", "net pay", "gross pay"],
            "UTILITY_BILL": ["utility", "electricity", "water", "gas", "meter reading"]
        }
        
        try:
            text = PipelineStages._extract_text_from_pdf(file_path).lower()
            
            scores = {}
            for doc_type, keywords_list in keywords.items():
                score = sum(1 for keyword in keywords_list if keyword in text)
                scores[doc_type] = score
            
            if max(scores.values()) == 0:
                doc_type = "UNKNOWN"
                confidence = 0.3
            else:
                doc_type = max(scores, key=scores.get)
                confidence = min(0.95, 0.6 + (scores[doc_type] * 0.07))
            
            output = {
                "document_type": doc_type,
                "confidence": confidence,
                "scores": scores,
                "model_version": PipelineStages.CLASSIFICATION_MODEL
            }
            
            return doc_type, output, confidence
            
        except Exception as e:
            return "UNKNOWN", {"error": str(e)}, 0.0
    
    @staticmethod
    async def extract_data(file_path: str, document_type: str) -> Tuple[Dict[str, Any], float]:
        await asyncio.sleep(0.8)
        
        text = PipelineStages._extract_text_from_pdf(file_path)
        
        if document_type == "INVOICE":
            extracted = PipelineStages._extract_invoice_data(text)
        elif document_type == "NATIONAL_ID":
            extracted = PipelineStages._extract_id_data(text)
        elif document_type == "BANK_STATEMENT":
            extracted = PipelineStages._extract_bank_statement_data(text)
        elif document_type == "PAYSLIP":
            extracted = PipelineStages._extract_payslip_data(text)
        else:
            extracted = {"raw_text": text[:500], "extracted_fields": {}}
        
        confidence = 0.85 + random.uniform(-0.1, 0.1)
        extracted["model_version"] = PipelineStages.EXTRACTION_MODEL
        extracted["extraction_timestamp"] = datetime.utcnow().isoformat()
        
        return extracted, confidence
    
    @staticmethod
    async def detect_and_redact_pii(data: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.3)
        
        pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+966|00966|0)?[5]\d{8}\b',
            "national_id": r'\b[12]\d{9}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            "iban": r'\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b'
        }
        
        redacted_data = json.loads(json.dumps(data))
        pii_detected = []
        
        def redact_recursive(obj, parent=None, key=None, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    redact_recursive(v, obj, k, f"{path}.{k}" if path else k)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    redact_recursive(item, obj, i, f"{path}[{i}]")
            elif isinstance(obj, str):
                redacted_value = obj
                for pii_type, pattern in pii_patterns.items():
                    matches = re.findall(pattern, redacted_value)
                    if matches:
                        for match in matches:
                            pii_detected.append({
                                "type": pii_type,
                                "location": path,
                                "redacted": True
                            })
                        redacted_value = re.sub(pattern, f"[REDACTED-{pii_type.upper()}]", redacted_value)
                
                if redacted_value != obj and parent is not None and key is not None:
                    parent[key] = redacted_value
        
        redact_recursive(redacted_data)
        
        return {
            "redacted_data": redacted_data,
            "pii_detected": pii_detected,
            "pii_detection_model": "aws-comprehend-pii-v2.0",
            "redaction_timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def validate_data(data: Dict[str, Any], document_type: str) -> Tuple[bool, List[str], List[str]]:
        await asyncio.sleep(0.4)
        
        passed_rules = []
        failed_rules = []
        
        if document_type == "INVOICE":
            if data.get("total_amount") and isinstance(data.get("total_amount"), (int, float)):
                passed_rules.append("total_amount_present")
            else:
                failed_rules.append("total_amount_missing_or_invalid")
            
            if data.get("vendor_name"):
                passed_rules.append("vendor_name_present")
            else:
                failed_rules.append("vendor_name_missing")
            
            if data.get("invoice_number"):
                passed_rules.append("invoice_number_present")
            else:
                failed_rules.append("invoice_number_missing")
                
        elif document_type == "NATIONAL_ID":
            if data.get("id_number"):
                passed_rules.append("id_number_present")
            else:
                failed_rules.append("id_number_missing")
            
            if data.get("name"):
                passed_rules.append("name_present")
            else:
                failed_rules.append("name_missing")
                
        elif document_type == "BANK_STATEMENT":
            if data.get("account_number"):
                passed_rules.append("account_number_present")
            else:
                failed_rules.append("account_number_missing")
        
        if not failed_rules:
            passed_rules.append("all_mandatory_fields_present")
        
        is_valid = len(failed_rules) == 0
        
        return is_valid, passed_rules, failed_rules
    
    @staticmethod
    def _extract_text_from_pdf(file_path: str) -> str:
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    @staticmethod
    def _extract_invoice_data(text: str) -> Dict[str, Any]:
        invoice_data = {
            "vendor_name": None,
            "invoice_number": None,
            "invoice_date": None,
            "due_date": None,
            "total_amount": None,
            "currency": "SAR",
            "line_items": []
        }
        
        invoice_match = re.search(r'invoice\s*(?:#|number|no\.?)?\s*:?\s*([A-Z0-9-]+)', text, re.IGNORECASE)
        if invoice_match:
            invoice_data["invoice_number"] = invoice_match.group(1)
        
        amount_match = re.search(r'(?:total|amount due|grand total)\s*:?\s*(?:SAR|SR|$)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if amount_match:
            invoice_data["total_amount"] = float(amount_match.group(1).replace(',', ''))
        
        vendor_match = re.search(r'(?:from|vendor|seller|company)\s*:?\s*([A-Za-z\s&]+)', text, re.IGNORECASE)
        if vendor_match:
            invoice_data["vendor_name"] = vendor_match.group(1).strip()
        
        return invoice_data
    
    @staticmethod
    def _extract_id_data(text: str) -> Dict[str, Any]:
        id_data = {
            "id_number": None,
            "name": None,
            "date_of_birth": None,
            "nationality": "Saudi Arabia",
            "gender": None
        }
        
        id_match = re.search(r'(?:id|identity)\s*(?:number|no\.?)?\s*:?\s*(\d{10})', text, re.IGNORECASE)
        if id_match:
            id_data["id_number"] = id_match.group(1)
        
        name_match = re.search(r'name\s*:?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
        if name_match:
            id_data["name"] = name_match.group(1).strip()
        
        return id_data
    
    @staticmethod
    def _extract_bank_statement_data(text: str) -> Dict[str, Any]:
        statement_data = {
            "account_number": None,
            "account_holder": None,
            "statement_period": None,
            "opening_balance": None,
            "closing_balance": None,
            "transactions": []
        }
        
        account_match = re.search(r'account\s*(?:number|no\.?)?\s*:?\s*([A-Z0-9]+)', text, re.IGNORECASE)
        if account_match:
            statement_data["account_number"] = account_match.group(1)
        
        balance_match = re.search(r'(?:closing|final)\s*balance\s*:?\s*(?:SAR|SR|$)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if balance_match:
            statement_data["closing_balance"] = float(balance_match.group(1).replace(',', ''))
        
        return statement_data
    
    @staticmethod
    def _extract_payslip_data(text: str) -> Dict[str, Any]:
        payslip_data = {
            "employee_name": None,
            "employee_id": None,
            "pay_period": None,
            "gross_salary": None,
            "net_salary": None,
            "deductions": []
        }
        
        salary_match = re.search(r'(?:net pay|net salary)\s*:?\s*(?:SAR|SR|$)?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        if salary_match:
            payslip_data["net_salary"] = float(salary_match.group(1).replace(',', ''))
        
        return payslip_data
