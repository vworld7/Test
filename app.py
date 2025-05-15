from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os, json
import pandas as pd
import PyPDF2
from RegulatoryAgent import claimvalidation_agent, regulatory_agent, cbvalidationdisplay_agent, decision_agent, \
    validator_agent, summarizer_agent

# Setup logging
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
CORS(app)

DATA_DIR = r"D:\Agentic AI\backend\Docs"


'''### 🔸 Your Existing Functions for Reading Excel & PDF Data ###
def read_excel_data(claim_id):
    file_path = f"{DATA_DIR}/{claim_id}.xlsx"
    print("excel file path :", file_path)
    if not os.path.exists(file_path):
        print("Error: File %s does not exist.", file_path)
        return None
    df = pd.read_excel(file_path)
    print("df :", df)
    return df.to_dict()


def read_pdf_data(claim_id):
    pdf_file_path = f"{DATA_DIR}/{claim_id}.txt"
    print("pdf file path :", pdf_file_path)
    if not os.path.exists(pdf_file_path):
        return None
    with open(pdf_file_path, 'r', encoding='utf-8') as pdf_file:
        pdf_reader = pdf_file.read()
    try:
        text = json.loads(pdf_reader)
    except json.JSONDecodeError as e:
        print("The file does not contain valid JSON.")
        text = {}
    print("pdf_reader :", pdf_reader)
    return text'''


### 🔹 Your Existing API for Validation ###
@app.route('/api/validate', methods=['POST'])
def validate_dispute_reason():
    try:
        claim_id = request.json.get("claim_id")
        print("claim_id :", claim_id)
        if not claim_id:
            return jsonify({"success": False, "error": "Claim ID not provided"}), 400
        '''excel_data = read_excel_data(claim_id)
        print("excel_data :", excel_data)
        pdf_data = read_pdf_data(claim_id)
        print("pdf_data :", pdf_data)

        if excel_data is None or pdf_data is None:
            return jsonify({"success": False, "error": "Files for given claim ID not found"}), 404'''

        claimvalidation_response = claimvalidation_agent()
        regulatory_response = regulatory_agent(claimvalidation_response)
        cbvalidationdisplay_response = cbvalidationdisplay_agent(claimvalidation_response)
        decision_response = decision_agent(claimvalidation_response, regulatory_response)
        validator_response = validator_agent(decision_response)
        summarizer_response = summarizer_agent(decision_response)

        result = {
            "ClaimValidationAgent": claimvalidation_response,
            "RegulatoryAgent": regulatory_response,
            "CBValidationDisplayAgent": cbvalidationdisplay_response,
            "DecisionAgent": decision_response,
            "ValidatorAgent": validator_response,
            "SummarizerAgent": summarizer_response,
        }

        return jsonify({"success": True, "result": result})
    except Exception as e:
        app.logger.error("Error occurred: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


### 🔹 Added API for Fetching Claims Data (From `server.js`) ###
def preserve_date_format(value, key):
    date_fields = {"FLD TXN Date", "FLD Post Date", "Repre Date"}

    if key in date_fields and isinstance(value, (int, float)) and value > 30000:
        excel_epoch_start = pd.Timestamp("1899-12-30")
        formatted_date = excel_epoch_start + pd.to_timedelta(value, unit="D")
        return formatted_date.strftime("%Y-%m-%d")

    return value


@app.route("/api/getClaims", methods=["GET"])
def get_claims():
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]
        claims_data = []

        for file in files:
            file_path = os.path.join(DATA_DIR, file)
            sheets = pd.ExcelFile(file_path).sheet_names

            for sheet_name in sheets:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                df = df.fillna("")
                formatted_data = df.apply(lambda row: {k: preserve_date_format(v, k) for k, v in row.items()}, axis=1)

                claims_data.extend(formatted_data.to_dict(orient="records"))

        return jsonify(claims_data)

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500


### ✅ Keep Everything Running on Port 5000 ###
if __name__ == "__main__":
    app.run(debug=True, port=5000)