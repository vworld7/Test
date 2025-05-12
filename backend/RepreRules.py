import os
import pandas as pd
import json
import urllib.request

def read_specific_excel_file(file_path):
    """
    Reads all sheets from the specified Excel file and returns data as a dictionary.
    """
    try:
        data = pd.ExcelFile(file_path)
        file_data = {}
        for sheet_name in data.sheet_names:
            sheet_data = pd.read_excel(file_path, sheet_name=sheet_name)
            file_data[sheet_name] = sheet_data.to_dict(orient="records")  # Convert DataFrame to dict
        return file_data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return {}

def process_representment_rules(repre_data_dict):
    """
    Takes the sheet data dictionary and sends it to the API for processing notes.
    """
    prompt = (
        f"You are given the following decision table extracted from Excel:\n\n{repre_data_dict}\n\n"
        "Instructions:\n"
        "1. The table contains 16 unique scenarios. Each scenario may have up to 4 possible outputs or decision outcomes.\n"
        "2. Carefully analyze and group the rows based on each unique scenario.\n"
        "3. For each scenario, extract the associated inputs/conditions and all the possible outputs exactly as written in the table.\n"
        "4. Do NOT assume or infer any values that are not explicitly listed in the table.\n"
        "5. Structure the final output strictly in a JSON format as follows:\n\n"
        "{\n"
        "  \"Scenario 1\": {\n"
        "    \"Conditions\": { ... },\n"
        "    \"Possible Outputs\": [\"...\", \"...\", \"...\", \"...\"]\n"
        "  },\n"
        "  \"Scenario 2\": {\n"
        "    ...\n"
        "  },\n"
        "  ...\n"
        "  \"Scenario 16\": {\n"
        "    ...\n"
        "  }\n"
        "}\n\n"
        "6. Only return the JSON object. Do not include any commentary or explanation.\n"
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
file_path = "./Docs/Repre Decision Grid.xlsx"  # Specific file path
excel_data = read_specific_excel_file(file_path)
repre_decision = process_representment_rules(excel_data)
#print(repre_decision)
