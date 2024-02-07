import React, { useState } from 'react';
import axios from 'axios';

function FileUpload() {
    const [file, setFile] = useState(null);
    const [tableData, setTableData] = useState([]);
    const [uploadStatus, setUploadStatus] = useState(''); // State should be defined at the top level of the component

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/upload-csv/', formData);
            setTableData(response.data.data); // Assuming 'data' is the key in the JSON response
            setUploadStatus('File uploaded successfully.');
        } catch (error) {
            console.error('Error uploading file:', error);
            setUploadStatus(`Error uploading file: ${error.message}`);
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input type="file" onChange={handleFileChange} accept=".csv" />
                <button type="submit">Upload</button>
            </form>
            <p>{uploadStatus}</p> {/* Display the upload status */}
            {tableData.length > 0 && (
                <table>
                    <thead>
                    <tr>
                        <th>Country</th>
                        <th>Probability of Default (Pd)</th>
                    </tr>
                    </thead>
                    <tbody>
                    {tableData.map((row, index) => (
                        <tr key={index}>
                            <td>{row.country}</td>
                            <td>{row.Pd}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

export default FileUpload;
