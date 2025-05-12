import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import DisputeTable from "./components/DisputeTable";
import disputeResponsePDF from "./Docs/DisputeResponse.pdf";
import FeedbackTable from "./components/FeedbackTable";
import DynamicTable from "./components/DynamicTable";
import { FaThumbsUp, FaThumbsDown } from "react-icons/fa"; // Importing icons


export default function App() {
  const [selectedClaim, setSelectedClaim] = useState(null); // Track selected claim
  const [activeTab, setActiveTab] = useState("Dashboard"); // Track current main tab
  const [activeExecutionSubTab, setActiveExecutionSubTab] = useState("Transaction Details"); // Default Execution sub-tab
  const [isExecutionEnabled, setIsExecutionEnabled] = useState(false); // Disable tabs initially
  const [isFeedbackEnabled, setIsFeedbackEnabled] = useState(false); // Disable feedback tab initially
  const [agents] = useState(["Claim Validation Agent", "Regulatory Agent", "Decision Agent", "Validator Agent"]); // Agent names
  const [progressStates, setProgressStates] = useState(agents.map(() => 0)); // Agent progress
  const [isProcessing, setIsProcessing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [claimvalidationResponse, setClaimvalidationResponse] = useState(null);
  const [regulatoryAgentResponse, setRegulatoryAgentResponse] = useState(null); // To store RegulatoryAgent response
  const [cbvalidationdisplayResponse, setCBValidationDisplayResponse] = useState(null); // To store RegulatoryAgent response
  const [decisionResponse, setDecisionResponse] = useState(null);
  const [validatorResponse, setValidatorResponse] = useState(null);
  const [summarizerResponse, setSummarizerResponse] = useState(null);
  const [feedback, setFeedback] = useState(Array(10).fill(null));

  const handleFeedback = (index, value) => {
    const updatedFeedback = [...feedback];
    updatedFeedback[index] = value;
    setFeedback(updatedFeedback);
  };

  const handleSubmit = () => {
    console.log("Submitted feedback:", feedback);
    alert("Feedback submitted!");
  };

  const handleCancel = () => {
    setFeedback(Array(10).fill(null));
  };


  // Check if all progress bars are 100% and enable tabs
  useEffect(() => {
    const allBarsCompleted = progressStates.every((progress) => progress === 100);
    setIsExecutionEnabled(allBarsCompleted); // Enable Execution tab
    setIsFeedbackEnabled(allBarsCompleted); // Enable Feedback tab
  }, [progressStates]);


  // Simulate agent progress sequentially
const triggerAgentSimulation = async () => {
  if (!selectedClaim) {
    alert("Please select a claim to trigger the AI Agent.");
    return;
  }

  // Reset states before starting
  setProgressStates(agents.map(() => 0));
  setIsProcessing(true);
  setLoading(true);
  setError(null);

  try {
    // Simulate progress while calling the backend API
    simulateSequentialProgress(agents);

    // Backend API call
    const response = await fetch("http://localhost:5000/api/validate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        pdf_data: { field: "Example PDF Data" }, // Replace with actual data
        csv_data: { field: "Example CSV Data", ClaimID: selectedClaim }, // Replace with actual data
      }),
    });

    if (!response.ok) {
      throw new Error("API call failed");
    }

    const data = await response.json();
    if (data.success) {
      setClaimvalidationResponse(data.result.ClaimValidationAgent);
      setRegulatoryAgentResponse(data.result.RegulatoryAgent);
      setCBValidationDisplayResponse(data.result.CBValidationDisplayAgent);
      setDecisionResponse(data.result.DecisionAgent);
      setValidatorResponse(data.result.ValidatorAgent);
      setSummarizerResponse(data.result.SummarizerAgent)
      // Store the RegulatoryAgent response
    } else {
      throw new Error(data.error || "Unknown error from API");
    }
  } catch (err) {
    console.error(err);
    setError(err.message || "An error occurred while fetching data.");
  } finally {
    setIsProcessing(false);
    setLoading(false);
  }
};

  const simulateSequentialProgress = (agentIds) => {
    let agentIndex = 0;

    const processAgent = () => {
      if (agentIndex >= agentIds.length) {
        setIsProcessing(false); // Stop processing when all agents complete
        return;
      }

      const currentAgentIndex = agentIndex;
      let progressValue = 0;

      const simulateProgress = async () => {
        while (progressValue < 100) {
          const randomDelay = Math.random() * 800 + 200; // 200ms to 1000ms delay
          await new Promise((resolve) => setTimeout(resolve, randomDelay));

          const increment = Math.floor(Math.random() * 10 + 5); // Increment progress randomly (5%-15%)
          progressValue = Math.min(progressValue + increment, 100); // Max value is 100%

          // Update state for progress
          setProgressStates((prev) => {
            const newProgress = [...prev];
            newProgress[currentAgentIndex] = progressValue;
            return newProgress;
          });
        }
        agentIndex++;
        processAgent(); // Move to the next agent
      };

      simulateProgress();
    };

    processAgent();
  };

  // Render content for the Main Page tab
  const renderContentForMainPage = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Dispute Claims</h1>
      <DisputeTable selectedClaim={selectedClaim} setSelectedClaim={setSelectedClaim} />
      <div className="mt-4">
        {selectedClaim ? (
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="mt-4 px-4 py-2 rounded"
              style={{
                backgroundColor: "#808080", // Gray
                color: selectedClaim && !isProcessing ? "#FFF" : "#BBB",
                cursor: !selectedClaim || isProcessing ? "not-allowed" : "pointer",
              }}
              onMouseEnter={(e) => {
                if (selectedClaim && !isProcessing) {
                  e.target.style.backgroundColor = "#E6F2E6"; // Light green on hover
                  e.target.style.color = "#000"; // Black text on hover
                }
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = "#808080"; // Reset to Gray
                e.target.style.color = "#FFF"; // Reset to original text color
              }}
              disabled={!selectedClaim || isProcessing}
              onClick={triggerAgentSimulation}
            >
              {isProcessing ? "Processing..." : "Initiate Review Process"}
            </button>
          </div>
        ) : (
          <p className="text-gray-500">Please select a claim to process.</p>
        )}
      </div>
      <div className="flex mt-6 space-x-4">
        {agents.map((agent, index) => (
          <div key={agent} className="w-1/4">
            <h3 className="font-bold text-center mb-2">{agent}</h3>
            <div className="relative bg-gray-200 h-4 w-full rounded">
              <div
                className="absolute bg-green-500 h-4 rounded"
                style={{ width: `${progressStates[index]}%` }}
              ></div>
            </div>
            <p className="text-center mt-2">{progressStates[index]}%</p>
          </div>
        ))}
      </div>
    </div>
  );
};


  // Render content for the Execution tab
  const renderContentForExecutionTab = () => {
    const executionTabs = ["Transaction Details", "Notes", "Document Interpretation" , "CB Validation", "Compelling Evidence", "Rebuttal Letter Preview", "Agents Playground"];
    const renderExecutionContent = () => {
      switch (activeExecutionSubTab) {
        case "Transaction Details":
          return (
  <div className="text-gray-700">
    <table style={{ borderCollapse: 'collapse', width: '70%' }}>
      <thead>
        <tr>
          <th style={{ border: '1px solid black', textAlign: 'left', padding: '8px' }}>Field</th>
          <th style={{ border: '1px solid black', textAlign: 'left', padding: '8px' }}>Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Txn ID</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>222222292</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Notification Date</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>03/13/25</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Disputed Amount</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>$ 25.45</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Network</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>007 (Visa)</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>CB Date</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>03/15/25</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>CB Reason code</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>13.1 (Merchandise/Service not received)</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>MCC</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>5699</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Merchant Name</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>TODAY SHOPS</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Survey ID</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>1252523</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Reason for dispute</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Merchandise not received</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Is merchandise or services</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>M</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Detailed description of what was purchased and an explanation of dispute</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Cardholder purchased SMART E-GADGETS Over-Ear Bluetooth Earbuds, black in color SKU #723466588287, Order #TSD002343866. Cardholder attempted to resolve via phone and was told that they did not have an order under her name.</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>CH address (for RC 13.1)</td>
          <td style={{ border: '1px solid black', padding: '8px', color: 'blue' }}>236, 1st Ave, Dreamland, PO Box 1245, NJ, US</td>
        </tr>
      </tbody>
    </table>
  </div>
);

        case "Document Interpretation":
  return (
    <div className="text-gray-700">
      <table style={{ borderCollapse: "collapse", width: "70%" }}>
        <thead>
          <tr>
            <th
              style={{
                border: "1px solid black",
                textAlign: "left",
                padding: "8px",
              }}
            >
              Field
            </th>
            <th
              style={{
                border: "1px solid black",
                textAlign: "left",
                padding: "8px",
              }}
            >
              Value
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style={{ border: "1px solid black", padding: "8px" }}>Document Link</td>
            <td style={{ border: "1px solid black", padding: "8px" }}>
              <a
                href={disputeResponsePDF} // Link to the PDF file
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 underline hover:text-blue-800"
              >
                DisputeResponse.PDF
              </a>
            </td>
          </tr>

        </tbody>
      </table>
    </div>
  );
        case "Notes":
        return (
  <div className="text-gray-700">
    <table style={{ borderCollapse: 'collapse', width: '70%' }}>
      <thead>
        <tr>
          <th style={{ border: '1px solid black', textAlign: 'left', padding: '8px' }}>Field</th>
          <th style={{ border: '1px solid black', textAlign: 'left', padding: '8px' }}>Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Notes date</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>03/13/25</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Dispute Reason</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Merchandise Not Received</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Disputed Amount</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>No mention</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Detailed Description</td>
          <td style={{ border: '1px solid black', padding: '8px', color: 'blue'}}>SMART E-GADGETS Over-Ear Bluetooth Earbuds, black in color SKU #723466588287</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Expected Delivery</td>
          <td style={{ border: '1px solid black', padding: '8px', color: 'blue'}}>02/25/25</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px', color: 'blue'}}>Attempt to resolve</td>
          <td style={{ border: '1px solid black', padding: '8px', color: 'blue'}}>Yes, no date</td>
        </tr>
      </tbody>
    </table>
            {/* New Table */}
      <div className="mt-8">
        <table style={{ borderCollapse: "collapse", width: "70%" }}>
          <thead>
            <tr>
              <th
                style={{
                  border: "1px solid black",
                  textAlign: "left",
                  padding: "8px",
                }}
              >
                FLD Created Date
              </th>
              <th
                style={{
                  border: "1px solid black",
                  textAlign: "left",
                  padding: "8px",
                }}
              >
                FLD Note Text
              </th>
              <th
                style={{
                  border: "1px solid black",
                  textAlign: "left",
                  padding: "8px",
                }}
              >
                FLD TXN ID
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ border: "1px solid black", padding: "8px" }}>
                3/13/2025
              </td>
              <td style={{ border: "1px solid black", padding: "8px" }}>
                IVR True: CH called to create a new dispute claim for this charge
                as Merchandise Not Received. Provided FGF info. Read Claim
                Creation script. Auto matched transaction. Provided claim #.
                Card status open prior to claim creation. Completed dispute
                survey. Detailed notes (below). SYS Release Claim.
                <br />
                Order: TSD002343866
                <br />
                Tracking #/Provider: None provided
                <br />
                Expected Delivery: 02/25/2025
                <br />
                TOS/CXL Policy: None provided
                <br />
                Item Description: CH paid/purchased SMART E-GADGETS Over-Ear
                Bluetooth Earbuds, black in color SKU #723466588287<br />
                Have you attempted to resolve with the merchant? When and how:
                CH ATR and was told that they did not have an order under her
                name.
                <br />
                Cardholder purchased SMART E-GADGETS Over-Ear Bluetooth Earbuds,
                black in color SKU #723466588287, Order #TSD002343866.
                Cardholder attempted to resolve via phone and was told that they
                did not have an order under her name.
              </td>
              <td style={{ border: "1px solid black", padding: "8px" }}>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
);
        case "Compelling Evidence":
        return (
  <div className="text-gray-700">
    <table style={{ borderCollapse: 'collapse', width: '70%' }}>
      <thead>
        <tr>
          <th style={{ border: '1px solid black', textAlign: 'left', padding: '8px' }}>Field</th>
          <th style={{ border: '1px solid black', textAlign: 'left', padding: '8px' }}>Value</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Represented timely</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Yes</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Compelling evidence addresses the reason for chargeback</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Yes</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Compelling evidence addresses the Amount of chargeback</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Yes</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Merchant Issued Credit</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Not found</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Valid Charge Identification</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Not found</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Summary</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Delivery details match. Date of delivery is after Expected date, send the merchant received information to Cardholder for review</td>
        </tr>
        <tr>
          <td style={{ border: '1px solid black', padding: '8px' }}>Recommendation</td>
          <td style={{ border: '1px solid black', padding: '8px' }}>Rebuttal letter to Cardholder, attach Merchant response received</td>
        </tr>
      </tbody>
    </table>
  </div>
);
        case "Rebuttal Letter Preview":
  return (
    <div className="p-6 text-gray-800 border rounded-lg bg-white shadow">
      <p className="text-right">04/29/2025</p>
      <br />
      <p>Dear Jason Jones:</p>
      <br />
      <p className="leading-relaxed">
        Thank you for your recent inquiry regarding the transaction(s) noted on the last page of this letter.
      </p>
      <br />
      <p className="leading-relaxed">
        You received provisional credit for this transaction in the amount of <strong>$25.54</strong>.
      </p>
      <br />
      <p className="leading-relaxed text-blue-500">
        The merchant has provided information concerning your claim: Merchant has responded to your dispute and is
        stating that the merchandise was delivered. Please review the merchant’s documentation. However, if the merchandise
        was received and returned, please state the specific reason for the return. In order to intercede on your behalf,
        card regulations require proof of return (return receipt and tracking number, proof that merchant has signed for
        returned items) and proof the merchandise was received by the merchant. If you have been in contact with the
        merchant, please provide the dates of contact and response from merchant.
      </p>
      <br />
      <ol className="list-decimal pl-5">
        <li className="leading-relaxed">
          Please notify us if you have concerns with the information provided by the merchant. If you have additional
          documentation that supports your claim, please provide it with your response. You may contact us at the phone
          number listed above or notify us in writing by mail or fax. Please use a copy of this letter as your coversheet
          if notifying by mail or fax.
        </li>
        <br />
        <li className="leading-relaxed">
          If you agree that this is a valid charge, please notify our office referencing your claim number by{" "}
          <strong>05/09/2025</strong>, at <strong>(800) 600-5249</strong> to confirm the charge.
        </li>
      </ol>
      <br />
      <p className="leading-relaxed">
        If a response is not received by <strong>05/09/2025</strong>, we will conclude our investigation and make a
        decision on your claim based on the information that we currently have available.
      </p>
      <br />
      <p className="leading-relaxed">
        Please retain a copy of this letter and all documentation relative to your claim for your records. If you have any
        additional questions, please contact us and reference your claim number. We appreciate the opportunity to be of
        service.
      </p>
      <br />
      <p>Sincerely,</p>
      <p>Chargeback Services</p>
      <br />
      <h4 className="font-bold">Transaction Details:</h4>
      <table className="border-collapse border border-gray-300 w-full text-left mt-4">
        <thead>
          <tr>
            <th className="border border-gray-300 px-2 py-1">Txn Date</th>
            <th className="border border-gray-300 px-2 py-1">Merchant Name</th>
            <th className="border border-gray-300 px-2 py-1">Txn Amount</th>
            <th className="border border-gray-300 px-2 py-1">Txn ID</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="border border-gray-300 px-2 py-1">02/20/2025</td>
            <td className="border border-gray-300 px-2 py-1">TODAY SHOPS</td>
            <td className="border border-gray-300 px-2 py-1">$25.54</td>
            <td className="border border-gray-300 px-2 py-1">222222292</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
        case "CB Validation":
  if (loading) {
    return <p className="text-blue-500">Loading AI Assistance...</p>;
  }
  if (error) {
    return <p className="text-red-500">Error: {error}</p>;
  }

  let parsedResponse = null;
  let cleaned = cbvalidationdisplayResponse;

  if (typeof cleaned === "string") {
    cleaned = cleaned.trim();
    if (cleaned.startsWith("```")) {
      cleaned = cleaned.replace(/```json|```/g, "").trim();
    }

    try {
      parsedResponse = JSON.parse(cleaned);
    } catch (e) {
      return (
        <p className="text-red-500">
          Invalid JSON format: {e.message}
        </p>
      );
    }
  } else {
    parsedResponse = cleaned;
  }

  const renderKeyValue = (obj) =>
    Object.entries(obj).map(([key, value], index) => (
      <div key={index} className="grid grid-cols-1 gap-4 border-b py-2 text-sm">
        <div className="font-medium text-gray-700">{key}</div>
        <div className="col-span-2 text-gray-900">
          {Array.isArray(value)
? value.map((item, i) => <div key={i}>- {item}</div>)
            : typeof value === "object" && value !== null
            ? renderKeyValue(value)
            : value?.toString()}
        </div>
      </div>
    ));

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6 text-gray-500">CB Validation</h1>
      <div className="bg-white shadow rounded-lg p-4 space-y-2">
        {parsedResponse ? (
          Object.entries(parsedResponse).map(([section, content], index) => (
            <div key={index}>
              <h2 className="text-lg font-semibold text-gray-800 mb-2 capitalize">
                {section.replace(/_/g, " ")}
              </h2>
              <div className="bg-gray-50 border rounded-md p-3">
                {typeof content === "object"
                  ? renderKeyValue(
                      Array.isArray(content)
                        ? Object.fromEntries(
content.map((val) => [val])
                          )
                        : content
                    )
                  : content.toString()}
              </div>
            </div>
          ))
        ) : (
          <p className="text-gray-500">
            AI is validating the final results. Please wait...
          </p>
        )}
      </div>
    </div>
  );

  // All agent responses
  case "Agents Playground":
  if (loading) {
    return <p className="text-blue-500">Loading AI Assistance...</p>;
  }
  if (error) {
    return <p className="text-red-500">Error: {error}</p>;
  }

  // All agent responses
  //const agentResponses = {
    //ClaimValidationAgent: claimvalidationResponse,
    //RegulatoryAgent: regulatoryAgentResponse,
    //DecisionAgent: decisionResponse,
    //ValidatorAgent: validatorResponse,
  //};

  return (
  <div>
    <h1 className="text-2xl font-bold mb-6 text-gray-800">Agent Responses</h1>

    {[
      { title: "ClaimValidationAgent Response", data: claimvalidationResponse },
      { title: "RegulatoryAgent Response", data: regulatoryAgentResponse },
      { title: "DecisionAgent Response", data: decisionResponse },
      { title: "ValidatorAgent Response", data: validatorResponse },
      { title: "SummarizerAgent Response", data: summarizerResponse },
    ].map(({ title, data }, index) => (
      <div key={index} className="mb-6 p-4 bg-gray-100 rounded-md shadow-md">
        {/* Agent Title */}
        <h2 className="text-lg font-bold mb-2">{title}:</h2>

        {/* Render Agent Data */}
        {data ? (
          Array.isArray(data) || typeof data === "object" ? (
            <pre className="bg-white p-4 rounded-md overflow-auto border border-gray-300">
              {JSON.stringify(data, null, 2)}
            </pre>
          ) : (
            <pre
              className="bg-white p-4 rounded-md overflow-auto border border-gray-300 whitespace-pre-line"
            >
              {data}
            </pre>
          )
        ) : (
          <p className="text-gray-500">No data available.</p>
        )}
      </div>
    ))}
  </div>
);
        default:
          return null;
      }
    };

    return (
      <div>
        <h1 className="text-2xl font-bold mb-4">AI Summary</h1>
      {summarizerResponse ? (
        <pre className="bg-gray-100 p-4 rounded-md overflow-auto">
          {summarizerResponse}
        </pre>
      ) : (
        <p className="text-gray-500">AI is validating the final results. Please wait...</p>
      )}

        <div className="flex border-b-2 border-gray-300 mb-4">
          {executionTabs.map((tab) => (
            <button
              key={tab}
            onClick={() => setActiveExecutionSubTab(tab)} // Update active tab
            style={{
              backgroundColor: activeExecutionSubTab === tab ? "#d4edda" : "#f8f9fa", // Active tab: #d4edda; Inactive tab: #f8f9fa (light gray)
              color: activeExecutionSubTab === tab ? "#155724" : "#333", // Active: Dark green text; Inactive: Default text
              borderRadius: "4px 4px 0 0", // Rounded top corners
              padding: "8px 12px",
              marginRight: "8px",
              transition: "background-color 0.2s ease",
              border: "1px solid #ced4da",
            }}

          >
            {tab}
          </button>
          ))}
        </div>
        <div className="mt-4">{renderExecutionContent()}</div>
      </div>
    );
  };

  // Render content for the Feedback tab
  const renderContentForFeedbackTab = () => {

  return (
    <div>
      <FeedbackTable />
    </div>
  );
};


  // Render content based on the active tab
  const renderAppContent = () => {
    switch (activeTab) {
      case "Dashboard":
        return renderContentForMainPage();
      case "Execution":
        return renderContentForExecutionTab();
      case "Feedback":
        return renderContentForFeedbackTab();
      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 p-6">
        <div className="tabs border-b-2 mb-4">
          <button
            className={`mr-4 px-4 py-2 ${
              activeTab === "Dashboard" ? "border-b-2 font-bold text-gray-500" : "text-gray-500"
            }`}
            onClick={() => setActiveTab("Dashboard")}
          >
            Dashboard
          </button>
          <button
            className={`mr-4 px-4 py-2 ${
              activeTab === "Execution" && isExecutionEnabled
                ? "border-b-2 font-bold text-gray-500"
                : "text-gray-500"
            }`}
            disabled={!isExecutionEnabled}
            title={
         !isExecutionEnabled
           ? "Complete all agent progress before accessing this tab."
           : "Go to Dashboard tab."
            }

            onClick={() => setActiveTab("Execution")}
          >
            Execution
          </button>
          <button
            className={`mr-4 px-4 py-2 ${
              activeTab === "Feedback" && isFeedbackEnabled
                ? "border-b-2 font-bold text-gray-500"
                : "text-gray-500"
            }`}
            disabled={!isFeedbackEnabled}
            title={
         !isExecutionEnabled
           ? "Complete all agent progress before accessing this tab."
           : "Go to Dashboard tab."
            }
            onClick={() => setActiveTab("Feedback")}
          >
            Feedback
          </button>
        </div>
        {renderAppContent()}
      </div>
    </div>
  );
}