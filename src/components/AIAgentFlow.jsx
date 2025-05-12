import React, { useState } from "react";

const agents = [
  { id: 1, name: "Intake Agent" },
  { id: 2, name: "Validator Agent" },
  { id: 3, name: "Compliance Agent" },
  { id: 4, name: "Summary Generator Agent" },
];

export default function AIAgentFlow({ selectedClaim }) {
  const [results, setResults] = useState({});
  const [activeTab, setActiveTab] = useState("Overview");
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(
    agents.reduce((acc, agent) => {
      acc[agent.name] = 0; // Initialize progress for agents at 0
      return acc;
    }, {})
  );

  // Function to simulate the entire agent workflow
  const triggerAgents = async () => {
    if (!selectedClaim) {
      alert("Please select a claim from the table first!");
      return;
    }

    setIsProcessing(true);
    let data = `Claim ID ${selectedClaim}`; // Initial input data
    const agentResults = {};

    // Process agents sequentially
    for (const agent of agents) {
      await simulateProgress(agent.name); // Ensure progress completes before moving to the next
      data = `${data}, processed by ${agent.name}`; // Simulate the agent's data transformation
      agentResults[agent.name] = data; // Store the result for the agent
    }

    setResults(agentResults); // Set final results
    setIsProcessing(false); // Stop processing state
    setActiveTab("Overview"); // Switch to overview tab
  };

  // Function to simulate the progress of an individual agent
  const simulateProgress = (agentName) => {
    return new Promise((resolve) => {
      let progressValue = 0;
      const interval = setInterval(() => {
        progressValue += 10; // Increase progress by 10% every 200ms
        setProgress((prev) => ({ ...prev, [agentName]: progressValue })); // Update progress state

        if (progressValue >= 100) {
          clearInterval(interval); // Stop progress interval
          resolve(); // Resolve promise when progress completes
        }
      }, 200); // Update progress every 200ms
    });
  };

  return (
    <div className="p-4 bg-gray-100 rounded shadow">
      {/* Trigger Button */}
      <button
        className={`bg-blue-600 text-white px-4 py-2 rounded ${
          isProcessing ? "opacity-50 cursor-not-allowed" : "hover:bg-blue-700"
        }`}
        onClick={triggerAgents}
        disabled={isProcessing}
      >
        {isProcessing ? "Processing Agents..." : "Trigger AI Agent"}
      </button>

      {/* Progress Bars */}
      <div className="mt-6">
        {agents.map((agent) => (
          <div key={agent.id} className="mb-4">
            <p className="mb-1 text-sm font-medium">{agent.name}</p>
            <div className="w-full bg-gray-200 rounded h-4 shadow-inner">
              <div
                className="h-4 bg-green-500 rounded"
                style={{ width: `${progress[agent.name]}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs for Results */}
      {Object.keys(results).length > 0 && (
        <div className="mt-4">
          <div className="flex border-b border-gray-200">
            {/* Overview Tab */}
            <button
              onClick={() => setActiveTab("Overview")}
              className={`px-4 py-2 ${
                activeTab === "Overview" ? "bg-gray-200 font-bold" : "hover:bg-gray-100"
              }`}
            >
              Overview
            </button>
            {/* Individual Agent Tabs */}
            {Object.keys(results).map((agentName) => (
              <button
                key={agentName}
                onClick={() => setActiveTab(agentName)}
                className={`px-4 py-2 ${
                  activeTab === agentName ? "bg-gray-200 font-bold" : "hover:bg-gray-100"
                }`}
              >
                {agentName}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-4 border mt-2 bg-white rounded shadow-inner">
            {activeTab === "Overview" ? (
              <div>
                <h2 className="text-lg font-bold mb-2">Overview</h2>
                <ul className="list-disc list-inside">
                  {Object.entries(results).map(([key, value]) => (
                    <li key={key}>
                      <strong>{key}:</strong> {value}
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div>
                <h2 className="text-lg font-bold mb-2">{activeTab} Output</h2>
                <p>{results[activeTab]}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}