import re

def extract_invoice_number(text: str) -> str | None:
    # Handles spaces, alternative words, and loose spacing from OCR noise
    pattern = (
        r"(?:Invoice|Inv|Bill)\s*(?:Number|No|#|Ref)?\s*[:#\.-]?\s*([A-Z0-9-/]+)"
    )
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_customer_name(text: str) -> str | None:
    # Uses \s* to support names appearing on the next line or across line breaks
    pattern = (
        r"(?:Customer|Client|Bill To|Sold To)\s*(?:Name)?\s*[:#\.-]?\s*\n?([A-Za-z][A-Za-z \.-]+)"
    )
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_date(text: str) -> str | None:
    # Supports YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, and dots as dividers
    pattern = (
        r"(?:Date|Inv\s*Date|Issued)\s*[:#\.-]?\s*(\d{2,4}[-/\.]\d{2}[-/\.]\d{2,4})"
    )
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_total_amount(text: str) -> float | None:
    # Uses re.findall to grab the LAST numeric match near total words,
    # avoiding table sub-totals or tax lines sitting above the final number.
    pattern = (
        r"(?:Total|Total\s*Amount|Grand\s*Total|Due|Balance)\s*[:#\.-]?\s*(?:[\d,]+\.\d{2})"
    )
    matches = re.findall(pattern, text, re.IGNORECASE)
    if not matches:
        return None
    
    # Grab the final amount statement block found at the bottom of the page
    last_match = matches[-1]
    amount_digits = re.search(r"([\d,]+\.\d{2})", last_match)
    if amount_digits:
        return float(amount_digits.group(1).replace(",", ""))
    return None


def extract_structured_data(text: str) -> dict:
    return {
        "invoice_number": extract_invoice_number(text),
        "customer_name": extract_customer_name(text),
        "invoice_date": extract_date(text),
        "total_amount": extract_total_amount(text),
    }
