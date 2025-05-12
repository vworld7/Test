import json
import urllib.request
from pdf_reader import parsed_data as v_pdf_data  # Import parsed data from pdf_reader
from csv_reader import response_from_api as v_csv_data  # Import the sheet data from csv_reader
#from RepreRules import repre_decision as v_repre_decision

# Function to generate the ClaimValidationAgent response
def claimvalidation_agent():
    #print(json.dumps(v_pdf_data, indent=2))
    #print(json.dumps(v_csv_data, default=str, indent=2))
    """
    Sends PDF and Excel data to Azure OpenAI GPT-4O API and retrieves insights.
    """

    # Prepare the prompt with necessary instructions
    prompt = (
        f"""
    You are an AI assistant for the Chargeback Representment process.

    You are provided two data sources:
    - **PDF Data**: {v_pdf_data}
    - **DRC Data**: {v_csv_data}

    Instructions:
    1. Extract and convert both sources to structured JSON format.
    2. Only use the data explicitly available in the inputs. Do NOT assume, infer, or fabricate any missing information.
    3. Perform a field-by-field comparison. While comparing:
       - Normalize date formats (e.g., DD/MM/YYYY vs MM-DD-YYYY) before comparing.
       - Normalize casing and remove extra spaces or symbols when comparing strings.
       - Use semantic similarity to align fields with different names (e.g., "Transaction Date" ≈ "Txn Date").
       - If a value appears in multiple fields, prioritize the most contextually relevant or detailed one.

    4. While extracting fields:
       - Scan the full text, including nested paragraphs or blocks, to ensure **no key-value pair is missed** explicitly **"FLDNoteText"**.
       - Use intelligent logic (e.g., regex-style pattern recognition) to parse semi-structured or unstructured data.
       - If unsure whether a piece of data is a field or value, include it with field name and value but no information should be missed.
    5. If a field is present in one source but not the other, use `"null"` for the missing side. Strictly follow it for all information explicitly present in the data source.
    6. Clean the data to ensure there are no unnecessary duplicates, and all fields are formatted appropriately.
    7. Organize the final output strictly in a structured JSON format. Do not provide any other explanations, suggestions, or comments. Only return the JSON.
    
    Guidelines:
    - Do NOT assume, infer, or fabricate any data.
    - Be strictly factual. Do not guess or assume missing data.
    - Use `null` for missing values and avoid generating fake field values.
    - If no matching or mismatching data is found, return an empty list for those sections.
    """
    )

    # API URL and headers
    url = "https://innovate-openai-api-mgt.azure-api.net/innovate-tracked/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-01"
    headers = {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        'api-key': '5002951037784ef8b91050d692a62318',  # Replace it with your actual API key
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


# Function to extract the dispute reason from ClaimValidationAgent response
def regulatory_agent(response_data):
    """
    Processes the JSON response from ClaimValidationAgent and extracts the dispute reason.
    """

    try:
        # Parse the JSON response from the ClaimValidationAgent
        prompt = (
            f"""
        You are a RegulatoryValidationAgent with 30 years of chargeback domain expertise.

        Your task is to identify the applicable Visa rules based on the Dispute Category/Condition/Reason mentioned in the input and verify if all required information is present for the dispute reason.

        Input:
        {response_data}

        Instructions:
        1. Based on the dispute reason in the input, determine the Dispute Reason & Visa requirements.
        2. Do NOT add or assume any information not explicitly present in the input.
        3. Evaluate whether all required fields and evidence for the identified dispute reason are present.
        4. Respond strictly based on the input provided.

        Output format (JSON):
        {{
          "dispute_reason": "Dispute reason extracted from the input",
          "identified_visa_rules": "Summarized Visa requirements based on dispute reason",
          "required_information": [
            "List of expected supporting documents or data for this dispute reason"
          ],
          "available_information": [
            "List of information actually found in the input"
          ],
          "missing_information": [
            "List of required items not found in the input"
          ],
          "justification": "Reasoning based only on comparison of required vs available data. Do not fabricate or assume."
        }}
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

        # Send the API request
        req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
        req.get_method = lambda: 'POST'
        response = urllib.request.urlopen(req)
        response_data = response.read().decode('utf-8')

        # Extract and return the summarized dispute reason from the response
        response_json = json.loads(response_data)
        message_content = response_json['choices'][0]['message']['content']

        return message_content
    except Exception as e:
        return json.dumps({"error": f"An error occurred while extracting the dispute reason: {e}"})

def cbvalidationdisplay_agent(response_data):
    """
    Processes the JSON response from ClaimValidationAgent and extracts the dispute reason.
    """

    try:
        # Parse the JSON response from the ClaimValidationAgent
        prompt = (
            f"""
                You are a RegulatoryValidationAgent with 30 years of chargeback domain expertise.
                 
                Your task is to identify the applicable Visa rules based on the Dispute Category/Condition/Reason mentioned in the input and verify if all required information is present.
                 
                Input:
                {response_data}
                 
                Instructions:
                1. Identify the Dispute Reason & Visa requirements based strictly on input.
                2. Do NOT assume or add any information not present.
                3. Compare required data vs available data.
                4. Return output in JSON format:
                 
                {{
                  "dispute_reason": "<Extracted reason>",
                  "identified_visa_rules": "<Visa rules based on dispute reason>",
                  "required_information": ["<Item1>", "<Item2>", "..."],
                  "available_information": ["<Item1>", "<Item2>", "..."],
                  "missing_information": ["<Item1>", "<Item2>", "..."],
                  "justification": "<Only based on comparison of required vs all available input data. Do not fabricate.>"
                }}
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

        # Send the API request
        req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
        req.get_method = lambda: 'POST'
        response = urllib.request.urlopen(req)
        response_data = response.read().decode('utf-8')

        # Extract and return the summarized dispute reason from the response
        response_json = json.loads(response_data)
        cbvalidation_display = response_json['choices'][0]['message']['content']

        return cbvalidation_display
    except Exception as e:
        return json.dumps({"error": f"An error occurred while extracting the dispute reason: {e}"})




def decision_agent(response_data, message_content):
    """
    Processes the JSON response from ClaimValidationAgent and extracts the dispute reason.
    """
    #print("repre",v_repre_decision)
    try:
        # Parse the JSON response from the DecisionAgent
        prompt = (
        f"""
        You are a DecisionAgent with 30 years of chargeback domain expertise.
        You must analyze the following structured output from the claimvalidation_agent:{response_data} and output from the regulatory_agent:{message_content}
        "1. Remember PDF_data is Merchant's response in the information from claimvalidation_agent
        "2. "information_considered": "Bullet point summary of facts taken from input"
        "3. Provide the Final Decision recommendation as **Send for Cardholder's review/Rebuttal letter** or **Deny Representment, pursue Pre-Arb** or **Accept Representment, close txn as CH Responsibility** or **Accept Representment, close txn as Merchant Issued Credit**
        "4. justification": "Explain clearly and concisely why this decision was made, referencing scenario logic and input data only"
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

        # Send the API request
        req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
        req.get_method = lambda: 'POST'
        response = urllib.request.urlopen(req)
        response_data = response.read().decode('utf-8')

        # Extract and return the summarized dispute reason from the response
        response_json = json.loads(response_data)
        decision_content = response_json['choices'][0]['message']['content']

        return decision_content
    except Exception as e:
        return json.dumps({"error": f"An error occurred while extracting the dispute reason: {e}"})

def validator_agent(decision_content):
    """
    Processes the JSON response from ClaimValidationAgent and extracts the dispute reason.
    """
    try:
        # Parse the JSON response from the ClaimValidationAgent
        prompt = (
            f"Based on the following output from the DecisionAgent:\n{decision_content}\n\n"
            "Check the guardrails and review the output from the DecisionAgent. Provide a summary that includes:\n"
            "1. Guardrails Check: Confirm if all the guardrails and compliance requirements are met. Specifically, check for:\n"
            "   - Accuracy: Ensure all data points and information used in the decision are accurate and correctly interpreted.\n"
            "   - Compliance: Verify that the decision adheres to relevant laws, regulations, and policies.\n"
            "   - Consistency: Confirm that the decision is consistent with previous similar decisions.\n"
            "   - Risk Management: Assess any potential risks associated with the decision.\n"
            "   - Transparency: Verify that the decision-making process is transparent and well-documented.\n"
            "   - Ethical Considerations: Ensure the decision is ethically sound.\n"
            "   - Alignment with Objectives: Check that the decision aligns with the organization's goals and objectives.\n"
            "2. Review Summary: Summarize the decision and the information considered.\n"
            "3. Recommendations: Provide any recommendations or actions needed based on the review.\n\n"
            "Provide the information in the following format:\n"
            "{\n"
            "  'Guardrails Check': 'Pass/Fail',\n"
            "  'Review Summary': 'Summary of the decision and information considered',\n"
            "  'Recommendations': 'Any recommendations or actions needed'\n"
            "}\n"
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

        # Send the API request
        req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
        req.get_method = lambda: 'POST'
        response = urllib.request.urlopen(req)
        response_data = response.read().decode('utf-8')

        # Extract and return the summarized dispute reason from the response
        response_json = json.loads(response_data)
        decision_content = response_json['choices'][0]['message']['content']

        return decision_content
    except Exception as e:
        return json.dumps({"error": f"An error occurred while extracting the dispute reason: {e}"})

def summarizer_agent(decision_content):
    """
    Processes the JSON response from ClaimValidationAgent and extracts the dispute reason.
    """
    try:
        # Parse the JSON response from the summarizer_agent
        prompt = (
            f"""
                You are an AI Summarizer Agent for the Chargeback Representment process.

                You are provided with the output from a decision_agent. Your task is to summarize this content into a clean, human-readable Markdown format with emoji icons for better clarity.

                ### Input:
                {decision_content}

                Instructions:
                1. Do not alter or fabricate content. Summarize based solely on the input provided and use step-by-step thinking.
                2. ONLY use facts available in the inputs. Do NOT assume, hallucinate, or fabricate any missing information.
                3. Identify whether the dispute is represented timely using step-by-step thinking, 
                4. If compelling evidence is provided use step-by-step thinking to identify reason and amount of dispute or chargeback.
                5. Identify if merchant issued credit or valid charge ID is found.
                6. Normalize date formats (e.g., DD/MM/YYYY vs MM-DD-YYYY) before comparing.
                7. Normalize casing and remove extra spaces or symbols when comparing strings.
                8. Use semantic similarity to align fields with different names (e.g., "Transaction Date" ≈ "Txn Date").
                9. Check Address of delivery same as billing address and Cardholder's address
                10. Check Date of delivery - available or not
                11. Track details for delivery available or not
                12. If all three point# 9,10,11 are available, consider it as Representment addresses the chargeback
                13. If there is no note in DRC indicating that Cardholder has reviewed and accepted merchant's representment response, propose "rebuttal letter to cardholder" as recommendation
                14. Provide a Markdown-formatted summary using the emoji icons below based on the decision:
                   - ✅ for "Yes"
                   - ❌ for "No"
                   - 🔍 for "Missing" or "None"
                   - ✉️ for recommendations
                   - ⏱️ for time-related entries
                   - 📦 for dispute-related findings
                   - 📨 for communication guidance


                Your response must strictly follow this Markdown format:

                ### Summary:
                - ⏱️ Represented timely: ✅Yes/❌No
                - 📄 Compelling evidence addresses the reason for chargeback: ✅Yes/❌No
                - 💵 Compelling evidence addresses the amount of chargeback: ✅Yes/❌No

                Merchant Issued Credit:
                - 🔍 Credit issued: actual value(MIC/Merchant Issued Credit) or None found

                Valid Charge Identification:
                - 🔍 Charge ID: actual value or None found

                Dispute Evaluation:
                - 📦 Highlight key findings based on comparison
                - 📨 Suggest an appropriate action for issuer/cardholder

                Recommendation:
                - ✉️ Final recommendation or rebuttal instruction
                ---

                Keep your entire response in this Markdown format and do not include raw JSON or code.
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

        # Send the API request
        req = urllib.request.Request(url, headers=headers, data=json.dumps(payload).encode("utf-8"))
        req.get_method = lambda: 'POST'
        response = urllib.request.urlopen(req)
        response_data = response.read().decode('utf-8')

        # Extract and return the summarized dispute reason from the response
        response_json = json.loads(response_data)
        summarizer_content = response_json['choices'][0]['message']['content']

        return summarizer_content
    except Exception as e:
        return json.dumps({"error": f"An error occurred while extracting the dispute reason: {e}"})



def print_boxed_message(title, content):
    """
    Print a boxed message for visual organization in the terminal.
    """
    box_width = max(len(title), len(max(content.splitlines(), key=len))) + 4
    print("┌" + "─" * box_width + "┐")
    print(f"│  {title.ljust(box_width - 2)}  │")
    print("├" + "─" * box_width + "┤")
    for line in content.split("\n"):
        print(f"│  {line.ljust(box_width - 2)}  │")
    print("└" + "─" * box_width + "┘")



# Main function to coordinate the workflow
if __name__ == "__main__":
    # Boxed Header for Starting Flow
    flow_name = "RepresentmentFlow"
    flow_id = "8b65250b-75cf-458f-9311-edb9785fa27a"
    print_boxed_message(
        "Flow Execution",
        f"Starting Flow Execution\n\nName: {flow_name}\nID: {flow_id}"
    )

    # Step 1: Generate the claim validation response
    print("\n🌊 Flow: " + flow_name)
    print(f"    ID: {flow_id}")
    print("└── 🧠 Starting Flow...\n")

    # Call first function and display output
    print("Running: `Validating input data...`")
    claimvalidation_agent_response = claimvalidation_agent()
    print_boxed_message(
        "ClaimValidationAgent Response",
        claimvalidation_agent_response
    )

    # Step 2: Process response in RegulatoryAgent
    print("\n🌊 Flow: RegulatoryAgent")
    print("└── 🔄 Running: Processing Dispute Reason...\n")
    extracted_dispute_reason = regulatory_agent(claimvalidation_agent_response)
    print_boxed_message(
        "RegulatoryAgent Response",
        extracted_dispute_reason
    )

    cbvalidationdisplay_agent_response = cbvalidationdisplay_agent(claimvalidation_agent_response)
    print("CB Display",cbvalidationdisplay_agent)
    # Step 3: Use in DecisionAgent
    print("\n🌊 Flow: DecisionAgent")
    print("└── 🔄 Running: Making Final Decision...\n")
    decision_response = decision_agent(claimvalidation_agent_response, extracted_dispute_reason)
    print_boxed_message(
        "DecisionAgent Response",
        decision_response
    )

    # Step 4: Validate with ValidatorAgent
    print("\n🌊 Flow: ValidatorAgent")
    print("└── 🔄 Running: Validating Decision...\n")
    validator_response = validator_agent(decision_response)
    print_boxed_message(
        "ValidatorAgent Response",
        validator_response
    )

    # Step 5: Summarize with Decision Agent
    print("\n🌊 Flow: SummarizerAgent")
    print("└── 🔄 Running: Summarizing Decision...\n")
    summarizer_response = summarizer_agent(decision_response)
    print_boxed_message(
        "SummarizerAgent Response",
        summarizer_response
    )

    print("\n✅ Flow Finished: " + flow_name)
    print_boxed_message(
        "Flow Completion",
        f"Flow Execution Completed\n\nName: {flow_name}\nID: {flow_id}"
    )