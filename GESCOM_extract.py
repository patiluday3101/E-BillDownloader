import fitz  # PyMuPDF
import json
import re

def extract_bill_details(pdf_path, output_json):
    doc = fitz.open(pdf_path)

    bill_details = {
        "Bill Number": "Not Found",
        "Bill Date": "Not Found",
        "Due Date": "Not Found",
        "Amount": "Not Found",
        "Power Factor": "0"  # Default to 0 if not found
    }

    for page in doc:
        text_instances = []
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_instances.append({
                            "text": span["text"].strip(),
                            "x": span["bbox"][0],  # X-coordinate
                            "y": span["bbox"][1]   # Y-coordinate (top of the text)
                        })

        # Identify header positions
        header_positions = {}
        for item in text_instances:
            if "Bill No" in item["text"]:
                header_positions["Bill Number"] = item
            elif "Billing Period" in item["text"]:
                header_positions["Billing Period"] = item
            elif "Due Date" in item["text"]:
                header_positions["Due Date"] = item
            elif "Current Bill Amount" in item["text"]:  
                header_positions["Amount"] = item
            elif "Power Factor" in item["text"] or "PF" in item["text"]:
                header_positions["Power Factor"] = item

        # Extract values below headers
        for key, header in header_positions.items():
            for item in text_instances:
                if item["y"] > header["y"] and abs(item["x"] - header["x"]) < 50:
                    bill_details[key] = item["text"]
                    break

        # Extract Bill Date (First date from Billing Period)
        if "Billing Period" in bill_details and bill_details["Billing Period"] != "Not Found":
            date_match = re.findall(r'\d{2}-\d{2}-\d{4}', bill_details["Billing Period"])
            if date_match:
                bill_details["Bill Date"] = date_match[0]  # First date as Bill Date

        # Extract Net Payable Amount (if found)
        for item in text_instances:
            if "Net Payable Amount" in item["text"]:
                amount_index = text_instances.index(item) + 1  # Get next item
                if amount_index < len(text_instances):
                    bill_details["Amount"] = text_instances[amount_index]["text"].replace(",", "").strip()
                    break

        # Extract Power Factor (correctly)
        if "Power Factor" in header_positions:
            pf_y = header_positions["Power Factor"]["y"]  # Y-coordinate of Power Factor label
            pf_candidates = []
            
            for item in text_instances:
                if item["y"] >= pf_y and abs(item["x"] - header_positions["Power Factor"]["x"]) < 80:
                    pf_match = re.findall(r'\b\d+\.\d+\b', item["text"])  # Find decimal values
                    if pf_match:
                        pf_candidates.extend(pf_match)

            # Choose the most relevant PF value (first one after the PF label)
            if pf_candidates:
                bill_details["Power Factor"] = pf_candidates[0]  # Pick first valid PF value
            else:
                bill_details["Power Factor"] = "0"  # Default to 0 if not found

        # Ensure Power Factor is a valid numeric value (avoid text like "Disconnection")
        if not re.match(r'^\d+\.\d+$', bill_details["Power Factor"]):
            bill_details["Power Factor"] = "0"

    # Remove "Billing Period" from the output since it's not needed
    bill_details.pop("Billing Period", None)

    # Save the extracted details
    with open(output_json, 'w') as json_file:
        json.dump(bill_details, json_file, indent=4)

    print("Extracted details saved to", output_json)
    return bill_details

# Example Usage
pdf_path = "7252862173.pdf"  # Replace with your actual file path
output_json = "bill_details.json"
result = extract_bill_details(pdf_path, output_json)
print(result)
