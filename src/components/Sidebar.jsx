import React from "react";
import logo from "./Logo/FISlogo.jpg"; // Import the logo

export default function Sidebar() {
  return (
    <div
      className="w-80 p-4"
      style={{
        backgroundColor: "#FFFFFF", // Background color for sidebar
        color: "#333",
        fontFamily: "Arial, sans-serif", // Use Arial font
        height: "100vh", // Full height for sidebar
      }}
    >
      {/* Logo Section */}
      <div className="logo mb-4">
        <img
          src={logo}
          alt="Company Logo"
          style={{
            width: "150px", // Adjust width as needed
            height: "auto", // Maintain aspect ratio
          }}
        />
      </div>

      {/* Menu Section */}
      <div className="menu-item">
        <div className="text-xl font-bold mb-4">Home (Vivek KUMAR)</div>

        <div className="menu-item">
          <div>My Work</div>
          <div className="submenu-item ml-4">
            <div>Processes</div>
            <div className="submenu-item ml-4">
              <div>Dispute Management</div>
              <div className="ml-4">Claim Creation</div>
              <div className="ml-4">PPC14 Claim Investigation</div>
              <div className="ml-4">T4 First Chargeback</div>
              <div
                className="ml-4"
                style={{ backgroundColor: "#d4edda", padding: "5px" }} // Light green background
              >
                T5 Representment
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
