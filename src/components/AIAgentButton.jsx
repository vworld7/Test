import React from "react";
import AIAgentFlow from "./AIAgentFlow";

const AIAgentButton = ({ selectedId }) => {
  return (
    <div className="p-4">
      <AIAgentFlow selectedId={selectedId} />
    </div>
  );
};

export default AIAgentButton;