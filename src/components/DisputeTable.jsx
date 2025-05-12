import React, { useState } from "react";

const mockData = [
  {
    claimNumber: "D1111111261",
    txnid: "222222292",
    txndate: "2/20/2025",
    postdate: "2/20/2025",
    txnamount: "$25.45",
    repredate: "4/1/2025",
  },
    {
    claimNumber: "D2223050817",
    txnid: "987653210",
    txndate: "3/15/2025",
    postdate: "3/16/2025",
    txnamount: "$50.00",
    repredate: "4/5/2025",
  },
  {
    claimNumber: "D2724050867",
    txnid: "876543209",
    txndate: "4/10/2025",
    postdate: "4/11/2025",
    txnamount: "$120.85",
    repredate: "5/2/2025",
  },
  {
    claimNumber: "D2860818901",
    txnid: "765432109",
    txndate: "5/1/2025",
    postdate: "5/2/2025",
    txnamount: "$75.60",
    repredate: "6/1/2025",
  },
  {
    claimNumber: "D2023050821",
    txnid: "674010987",
    txndate: "6/15/2025",
    postdate: "6/16/2025",
    txnamount: "$98.45",
    repredate: "7/5/2025",
  },
];

export default function DisputeTable({ selectedClaim, setSelectedClaim }) {
  const [checkedStates, setCheckedStates] = useState(
    mockData.reduce((acc, item) => {
      acc[item.claimNumber] = false;
      return acc;
    }, {})
  );

  const handleCheckboxChange = (claimNumber) => {
    const resetCheckedStates = Object.keys(checkedStates).reduce(
      (acc, key) => {
        acc[key] = false;
        return acc;
      },
      {}
    );

    setCheckedStates({
      ...resetCheckedStates,
      [claimNumber]: true,
    });

    setSelectedClaim(claimNumber);
  };

  return (
    <div className="overflow-x-auto">
      <table className="table-auto w-full bg-white rounded-lg shadow">
        {/* Table header */}
        <thead>
          <tr
            style={{
              backgroundColor: "#D3d3d3", // Light green header
              color: "#333", // Text color for headers
              textAlign: "center", // Center-align text
            }}
          >
            <th className="p-3 border border-white">Select</th>
            <th className="p-3 border border-white">Claim ID</th>
            <th className="p-3 border border-white">TXN ID</th>
            <th className="p-3 border border-white">TXN Date</th>
            <th className="p-3 border border-white">Post Date</th>
            <th className="p-3 border border-white">TXN Amount</th>
            <th className="p-3 border border-white">Repre Date</th>
          </tr>
        </thead>

        {/* Table body */}
        <tbody>
          {mockData.map((item, index) => (
            <tr
              key={item.claimNumber}
              className={`text-sm ${
                index % 2 === 0 ? "bg-gray-100" : "bg-white"
              }`}
              style={{ textAlign: "center" }}
            >
              <td className="p-3 border border-white">
                <input
                  type="checkbox"
                  name="selectedClaim"
                  value={item.claimNumber}
                  checked={checkedStates[item.claimNumber]}
                  onChange={() => handleCheckboxChange(item.claimNumber)}
                  className="cursor-pointer"
                />
              </td>
              <td className="p-3 border border-white">{item.claimNumber}</td>
              <td className="p-3 border border-white">{item.txnid}</td>
              <td className="p-3 border border-white">{item.txndate}</td>
              <td className="p-3 border border-white">{item.postdate}</td>
              <td className="p-3 border border-white">{item.txnamount}</td>
              <td className="p-3 border border-white">{item.repredate}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}