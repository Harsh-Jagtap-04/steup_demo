import React, { useState } from "react";
import axios from "axios";

const FileUpload = () => {
  const [files, setFiles] = useState({
    invitesTable: null,
    testTable: null,
    consolidatedTable: null,
    batchInformation: null,
  });

  const handleFileChange = (e, table) => {
    setFiles({ ...files, [table]: e.target.files[0] });
  };

  const handleUpload = async (table) => {
    const formData = new FormData();
    formData.append("file", files[table]);
    formData.append("table", table);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData);
      alert(`Upload successful for ${table}`);
    } catch (error) {
      alert(`Error uploading ${table}: ${error.message}`);
    }
  };

  return (
    <div>
      <h1>File Upload</h1>
      {["invitesTable", "testTable", "consolidatedTable", "batchInformation"].map((table) => (
        <div key={table}>
          <h3>Upload {table}</h3>
          <input type="file" onChange={(e) => handleFileChange(e, table)} />
          <button onClick={() => handleUpload(table)}>Upload</button>
        </div>
      ))}
    </div>
  );
};

export default FileUpload;
