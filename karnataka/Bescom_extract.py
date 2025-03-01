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
        "Power Factor": "0"
    }

    for page in doc:
        text_instances = []
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_instances.append({
                            "text": span["text"],
                            "x": span["bbox"][0],  # X-coordinate
                            "y": span["bbox"][1]   # Y-coordinate (top of the text)
                        })

        # Identify header positions
        header_positions = {}
        for item in text_instances:
            if "Bill No" in item["text"]:
                header_positions["Bill Number"] = item
            elif "Bill Date" in item["text"]:
                header_positions["Bill Date"] = item
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

        for item in text_instances:
            if "Net Payable Amount" in item["text"]:
                amount_index = text_instances.index(item) + 1  # Get next item
                if amount_index < len(text_instances):
                    bill_details["Amount"] = text_instances[amount_index]["text"].replace(",", "")
                    break



        # Extract Power Factor (if found)
        if "Power Factor" in header_positions:
            for item in text_instances:
                if item["y"] >= header_positions["Power Factor"]["y"] and abs(item["x"] - header_positions["Power Factor"]["x"]) < 80:
                    pf_match = re.search(r'\d+\.\d+', item["text"])
                    if pf_match:
                        bill_details["Power Factor"] = pf_match.group()
                    break

    # Save the extracted details
    with open(output_json, 'w') as json_file:
        json.dump(bill_details, json_file, indent=4)

    print("Extracted details saved to", output_json)
    return bill_details

# Example Usage
pdf_path = "3914302000.pdf"  # Replace with your actual file path
output_json = "bill_details.json"
result = extract_bill_details(pdf_path, output_json)
print(result)

