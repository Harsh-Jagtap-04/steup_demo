import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import FileUpload from "./components/FileUpload";
import Dashboard from "./components/Dashboard";

const App = () => {
  return (
    <Router>
      <nav>
        <ul>
          <li><Link to="/">File Upload</Link></li>
          <li><Link to="/dashboard">Dashboard</Link></li>
        </ul>
      </nav>
      <Routes>
        <Route path="/" element={<FileUpload />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  );
};

export default App;
