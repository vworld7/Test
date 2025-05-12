import pandas as pd
import json
import urllib.request

def read_excel_sheets(input_directory):
    """
    Reads all sheets from the specified Excel file and returns data as a dictionary.
    """
    try:
        data = pd.ExcelFile(input_directory)
        all_excel_data = {}
        for sheet_name in data.sheet_names:
            sheet_data = pd.read_excel(input_directory, sheet_name=sheet_name)
            all_excel_data[sheet_name] = sheet_data.to_dict(orient="records")  # Convert DataFrame to dict
        return all_excel_data
    except Exception as e:
        print(f"Error reading {input_directory}: {e}")
        return {}

def process_notes_with_api(sheet_data_dict):
    """
    Takes the sheet data dictionary and sends it to the API for processing notes.
    """
    prompt = (
        f"""Based on the following data extracted from excel:\n{sheet_data_dict}\n\n"
        "1. Focus on extracting all information explicitly present in the ### Txn Data and ### Notes Data sections.\n"
        "2. In particular, analyze the **"FLDNoteText"** section, as it contains important information provided by the human agent regarding representment or chargeback. Extract all available details, such as:\n"
        "   - Amounts\n"
        "   - Dates\n"
        "   - References\n"
        "   - Customer details (names, accounts, transaction IDs, etc.)\n"
        "   - Actions taken (e.g., investigation, escalation, approval, etc.)\n"
        "   - Decisions made (e.g., dispute status, reason for chargeback/representment)\n"
        "   - Any other relevant details or context provided in the notes.\n"
        "3. Do NOT assume, infer, or fabricate any data. Only extract information that is explicitly mentioned in the notes or transaction data.\n"
        "4. Merge the extracted information from both Txn Data and Notes Data sections where applicable to provide a comprehensive view.\n"
        "5. Organize the final output strictly in a structured JSON format, ensuring it includes all fields. Do not provide any other explanations, suggestions, or comments. Only return the JSON.\n"
        "6. Clean the data to ensure there are no unnecessary duplicates, and all fields are formatted appropriately.\n"
        """
    )

    # API URL and headers
    url = "https://innovate-openai-api-mgt.azure-api.net/innovate-tracked/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-01"
    headers = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'api-key': '5002951037784ef8b91050d692a62318',  # Replace with your actual API key
    }

    # Data payload for the API
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }

    try:
        # Send the API request
        req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
        req.get_method = lambda: 'POST'
        response = urllib.request.urlopen(req)
        response_data = response.read().decode('utf-8')
        response_json = json.loads(response_data)
        response_data = response_json['choices'][0]['message']['content']
        return response_data

    except Exception as e:
        return json.dumps({"error": f"An error occurred: {e}"})

# Process data and expose it for external use
input_dir = "./docs/D1111111261.xlsx"  # Directory with Excel files
excel_data = read_excel_sheets(input_dir)
response_from_api = process_notes_with_api(excel_data)
#print(response_from_api)

