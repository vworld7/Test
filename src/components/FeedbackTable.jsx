import React, { useState } from "react";
import "./FeedbackTable.css"; // External CSS for styling
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faThumbsUp, faThumbsDown } from "@fortawesome/free-solid-svg-icons";

const questions = [
  { question: "Is this an unauthorized dispute? Y/N", response: "Y" },
  { question: "Card Disposition MOTO/Fraud Use", response: "MOTO" },
  { question: "Is cardholder notification date(s) correct on DRC for the disputed Txn(s)? Y/N", response: "Y" },
  { question: "Did you make adjustment in the notification date? Y/N", response: "N" },
  { question: "Did the issuer make the decision to approve or deny the claim? Y/N", response: "N" },
  { question: "Did the merchant issue credit to any of the contested transaction? Y/N", response: "N" },
  { question: "What is the oldest date for the time period that the transaction history was reviewed for?", response: "4/8/2023" },
  { question: "What is the newest date for the time period that the transaction history was reviewed for?", response: "4/8/2023" },
  { question: "Does the card/account have at least 60 days of activity? Y/N", response: "Y" }
];

export default function FeedbackTable() {
  const [feedback, setFeedback] = useState({});
  const [message, setMessage] = useState("");

  const handleThumbClick = (index, type) => {
    setFeedback((prev) => ({
      ...prev,
      [index]: prev[index] === type ? null : type
    }));
  };

  const handleSubmit = () => {
    setMessage("Thank you for your response, we have registered your feedback.");
  };

  return (
    <div className="feedback-container">
      <h2>Feedback for AI Agent</h2>
      <table>
        <colgroup>
          <col style={{ width: "55%" }} />
          <col style={{ width: "25%" }} />
          <col style={{ width: "20%" }} />
        </colgroup>
        <thead>
          <tr>
            <th>Question</th>
            <th className="center">Response</th>
            <th className="center">Feedback</th>
          </tr>
        </thead>
        <tbody>
          {questions.map((item, idx) => (
            <tr key={idx}>
              <td>{item.question}</td>
              <td className="center">{item.response}</td>
              <td className="center">
                <FontAwesomeIcon
                  icon={faThumbsUp}
                  className={`thumb ${feedback[idx] === "up" ? "selected-up" : ""}`}
                  onClick={() => handleThumbClick(idx, "up")}
                />
                <FontAwesomeIcon
                  icon={faThumbsDown}
                  className={`thumb ${feedback[idx] === "down" ? "selected-down" : ""}`}
                  onClick={() => handleThumbClick(idx, "down")}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="buttons">
        <button className="submit-btn" onClick={handleSubmit}>Submit</button>
        <button className="cancel-btn" onClick={handleSubmit}>Cancel</button>
      </div>

      {message && <div className="message">{message}</div>}
    </div>
  );
}