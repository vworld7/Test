import React from 'react';

const DynamicTable = ({ data }) => {
  const renderRow = (key, value) => {
    if (Array.isArray(value)) {
      return (
        <tr key={key}>
          <td className="border px-4 py-2 font-bold">{key}</td>
          <td className="border px-4 py-2">
            <ul className="list-disc pl-5">
{value.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </td>
        </tr>
      );
    } else if (typeof value === 'object' && value !== null) {
      return (
        <tr key={key}>
          <td className="border px-4 py-2 font-bold">{key}</td>
          <td className="border px-4 py-2">
            <DynamicTable data={value} />
          </td>
        </tr>
      );
    } else {
      return (
        <tr key={key}>
          <td className="border px-4 py-2 font-bold">{key}</td>
          <td className="border px-4 py-2">{value}</td>
        </tr>
      );
    }
  };

  return (
    <div className="dynamic-table">
      <h2 className="text-lg font-bold mb-4">Response Data</h2>
      <table className="min-w-full bg-white">
        <tbody>
          {Object.entries(data).map(([key, value]) => renderRow(key, value))}
        </tbody>
      </table>
    </div>
  );
};

export default DynamicTable;