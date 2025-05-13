import json
import urllib.request
import logging
import os
from functools import wraps
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("representment_flow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RepresentmentFlow")

# Import data from other modules
try:
    from pdf_reader import parsed_data as v_pdf_data
    from csv_reader import response_from_api as v_csv_data
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    raise

# Constants
API_URL = "https://innovate-openai-api-mgt.azure-api.net/innovate-tracked/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-01"
API_KEY = os.environ.get("AZURE_OPENAI_API_KEY", "5002951037784ef8b91050d692a62318")  # Better to use environment variable

# Decorator for API calls to reduce code duplication
def api_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            prompt = func(*args, **kwargs)
            
            headers = {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-cache',
                'api-key': API_KEY,
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{
                    "role": "user",
                    "content": prompt
                }]
            }
            
            req = urllib.request.Request(
                API_URL, 
                headers=headers, 
                data=json.dumps(payload).encode("utf-8")
            )
            req.get_method = lambda: 'POST'
            
            logger.info(f"Calling API for {func.__name__}")
            response = urllib.request.urlopen(req)
            response_data = response.read().decode('utf-8')
            response_json = json.loads(response_data)
            
            return response_json['choices'][0]['message']['content']
            
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return json.dumps({"error": f"An error occurred in {func.__name__}: {e}"})
    
    return wrapper

@api_call
def claimvalidation_agent():
    """Generates prompt for claim validation against PDF and CSV data"""
    return f"""
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

@api_call
def regulatory_agent(response_data):
    """Processes the JSON response from ClaimValidationAgent and analyzes applicable Visa rules"""
    return f"""
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

@api_call
def cbvalidationdisplay_agent(response_data):
    """Processes response for user display purposes"""
    return f"""
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

@api_call
def decision_agent(response_data, message_content):
    """Makes decision recommendation based on validation and regulatory analysis"""
    return f"""
    You are a DecisionAgent with 30 years of chargeback domain expertise.
    You must analyze the following structured output from the claimvalidation_agent:{response_data} and output from the regulatory_agent:{message_content}
    
    1. Remember PDF_data is Merchant's response in the information from claimvalidation_agent
    2. "information_considered": "Bullet point summary of facts taken from input"
    3. Provide the Final Decision recommendation as **Send for Cardholder's review/Rebuttal letter** or **Deny Representment, pursue Pre-Arb** or **Accept Representment, close txn as CH Responsibility** or **Accept Representment, close txn as Merchant Issued Credit**
    4. justification": "Explain clearly and concisely why this decision was made, referencing scenario logic and input data only"
    """

@api_call
def validator_agent(decision_content):
    """Validates the decision against guardrails and compliance requirements"""
    return f"""
    Based on the following output from the DecisionAgent:
    {decision_content}

    Check the guardrails and review the output from the DecisionAgent. Provide a summary that includes:
    1. Guardrails Check: Confirm if all the guardrails and compliance requirements are met. Specifically, check for:
       - Accuracy: Ensure all data points and information used in the decision are accurate and correctly interpreted.
       - Compliance: Verify that the decision adheres to relevant laws, regulations, and policies.
       - Consistency: Confirm that the decision is consistent with previous similar decisions.
       - Risk Management: Assess any potential risks associated with the decision.
       - Transparency: Verify that the decision-making process is transparent and well-documented.
       - Ethical Considerations: Ensure the decision is ethically sound.
       - Alignment with Objectives: Check that the decision aligns with the organization's goals and objectives.
    2. Review Summary: Summarize the decision and the information considered.
    3. Recommendations: Provide any recommendations or actions needed based on the review.

    Provide the information in the following format:
    {{
      'Guardrails Check': 'Pass/Fail',
      'Review Summary': 'Summary of the decision and information considered',
      'Recommendations': 'Any recommendations or actions needed'
    }}
    """

@api_call
def summarizer_agent(decision_content):
    """Creates a user-friendly summary with emoji indicators for clarity"""
    return f"""
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

def save_results_to_file(flow_name, results):
    """Save all results to a JSON file for audit and reference"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"flow_results_{flow_name}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {filename}")
    return filename

def run_flow():
    """Main function to coordinate the workflow"""
    # Execution metadata
    flow_name = "RepresentmentFlow"
    flow_id = "8b65250b-75cf-458f-9311-edb9785fa27a"
    timestamp_start = datetime.now()
    
    # Result collection for audit
    results = {
        "flow_metadata": {
            "name": flow_name,
            "id": flow_id,
            "started_at": timestamp_start.isoformat(),
        },
        "agent_results": {}
    }
    
    # Boxed Header for Starting Flow
    print_boxed_message(
        "Flow Execution",
        f"Starting Flow Execution\n\nName: {flow_name}\nID: {flow_id}"
    )

    # Step 1: Generate the claim validation response
    logger.info(f"Starting Flow: {flow_name} with ID: {flow_id}")
    print("\n🌊 Flow: " + flow_name)
    print(f"    ID: {flow_id}")
    print("└── 🧠 Starting Flow...\n")

    # Call first function and display output
    print("Running: `Validating input data...`")
    try:
        claimvalidation_response = claimvalidation_agent()
        results["agent_results"]["claimvalidation_agent"] = claimvalidation_response
        print_boxed_message("ClaimValidationAgent Response", claimvalidation_response)
    except Exception as e:
        logger.error(f"Error in ClaimValidationAgent: {e}")
        print_boxed_message("ERROR", f"ClaimValidationAgent failed: {e}")
        return

    # Step 2: Process response in RegulatoryAgent
    print("\n🌊 Flow: RegulatoryAgent")
    print("└── 🔄 Running: Processing Dispute Reason...\n")
    try:
        regulatory_response = regulatory_agent(claimvalidation_response)
        results["agent_results"]["regulatory_agent"] = regulatory_response
        print_boxed_message("RegulatoryAgent Response", regulatory_response)
    except Exception as e:
        logger.error(f"Error in RegulatoryAgent: {e}")
        print_boxed_message("ERROR", f"RegulatoryAgent failed: {e}")
        return

    try:
        cbvalidation_display = cbvalidationdisplay_agent(claimvalidation_response)
        results["agent_results"]["cbvalidationdisplay_agent"] = cbvalidation_display
        logger.info("CB Display Agent completed successfully")
    except Exception as e:
        logger.error(f"Error in CBValidationDisplayAgent: {e}")
    
    # Step 3: Use in DecisionAgent
    print("\n🌊 Flow: DecisionAgent")
    print("└── 🔄 Running: Making Final Decision...\n")
    try:
        decision_response = decision_agent(claimvalidation_response, regulatory_response)
        results["agent_results"]["decision_agent"] = decision_response
        print_boxed_message("DecisionAgent Response", decision_response)
    except Exception as e:
        logger.error(f"Error in DecisionAgent: {e}")
        print_boxed_message("ERROR", f"DecisionAgent failed: {e}")
        return

    # Step 4: Validate with ValidatorAgent
    print("\n🌊 Flow: ValidatorAgent")
    print("└── 🔄 Running: Validating Decision...\n")
    try:
        validator_response = validator_agent(decision_response)
        results["agent_results"]["validator_agent"] = validator_response
        print_boxed_message("ValidatorAgent Response", validator_response)
    except Exception as e:
        logger.error(f"Error in ValidatorAgent: {e}")
        print_boxed_message("ERROR", f"ValidatorAgent failed: {e}")
        return

    # Step 5: Summarize with SummarizerAgent
    print("\n🌊 Flow: SummarizerAgent")
    print("└── 🔄 Running: Summarizing Decision...\n")
    try:
        summarizer_response = summarizer_agent(decision_response)
        results["agent_results"]["summarizer_agent"] = summarizer_response
        print_boxed_message("SummarizerAgent Response", summarizer_response)
    except Exception as e:
        logger.error(f"Error in SummarizerAgent: {e}")
        print_boxed_message("ERROR", f"SummarizerAgent failed: {e}")
        return

    # Finalize execution
    timestamp_end = datetime.now()
    results["flow_metadata"]["ended_at"] = timestamp_end.isoformat()
    results["flow_metadata"]["duration_seconds"] = (timestamp_end - timestamp_start).total_seconds()
    
    # Save results to file
    output_file = save_results_to_file(flow_name, results)
    
    print(f"\n✅ Flow Finished: {flow_name}")
    print_boxed_message(
        "Flow Completion",
        f"Flow Execution Completed\n\nName: {flow_name}\nID: {flow_id}\nResults saved to: {output_file}"
    )

if __name__ == "__main__":
    run_flow()
