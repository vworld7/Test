from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from RegulatoryAgent import claimvalidation_agent, regulatory_agent, cbvalidationdisplay_agent , decision_agent, validator_agent, summarizer_agent

# Setup logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

@app.route('/api/validate', methods=['POST'])
def validate_dispute_reason():
    try:
        '''        # Get PDF and CSV data from the request
        pdf_data = request.json.get("pdf_data", {})
        print("Show PDF DATA", pdf_data)
        csv_data = request.json.get("csv_data", {})
        print("Show csv DATA",csv_data)

        app.logger.info("Received PDF Data: %s", pdf_data)
        app.logger.info("Received CSV Data: %s", csv_data)'''

        # Step 1: Run ClaimValidationAgent
        app.logger.info("Processing ClaimValidationAgent...")
        claimvalidation_response = claimvalidation_agent()
        app.logger.debug("ClaimValidationAgent Response: %s", claimvalidation_response)

        # Step 2: Run RegulatoryAgent
        app.logger.info("Processing RegulatoryAgent...")
        regulatory_response = regulatory_agent(claimvalidation_response)
        app.logger.debug("RegulatoryAgent Response: %s", regulatory_response)

        # Step 2: Run cbvalidationdisplay_agent
        app.logger.info("Processing CBValidationDisplayAgent...")
        cbvalidationdisplay_response = cbvalidationdisplay_agent(claimvalidation_response)
        app.logger.debug("CBValidationDisplayAgent Response: %s", cbvalidationdisplay_response)

        # Step 3: Run DecisionAgent
        app.logger.info("Processing DecisionAgent...")
        decision_response = decision_agent(claimvalidation_response, regulatory_response)
        app.logger.debug("DecisionAgent Response: %s", decision_response)

        # Step 4: Run ValidatorAgent
        app.logger.info("Processing ValidatorAgent...")
        validator_response = validator_agent(decision_response)
        app.logger.debug("ValidatorAgent Response: %s", validator_response)

        # Step 5: Run SummarizerAgent
        app.logger.info("Processing SummarizerAgent...")
        summarizer_response = summarizer_agent(decision_response)
        app.logger.debug("ValidatorAgent Response: %s", validator_response)

        # Maintains the order of the responses (ensures desired sequence)
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


if __name__ == "__main__":
    app.run(debug=True, port=5000)