import os
import json

# Define the path to the OCR.txt file
docs_folder = "Docs"
file_name = "OCR.txt"
file_path = os.path.join(docs_folder, file_name)
#print(file_path)

# Check if the file exists
if os.path.exists(file_path):
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
        #print(data)

    # Attempt to parse the content into JSON
    try:
        parsed_data = json.loads(data)
    except json.JSONDecodeError as e:
        print("The file does not contain valid JSON.")
        parsed_data = {}
    # Comment out the print statements
    # Print the JSON data in key-value format
    # for key, value in parsed_data.items():
    #     print(f"{key}: {value}")
else:
    print(f"The file {file_name} does not exist in the {docs_folder} folder.")

