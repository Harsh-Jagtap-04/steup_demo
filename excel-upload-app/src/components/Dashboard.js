import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './dashboardtable.css';

const Dashboard = () => {
    const [data, setData] = useState(null);

    useEffect(() => {
        axios.get('http://localhost:5000/dashboard')
            .then(response => {
                setData(response.data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }, []);

    if (!data) {
        return <div>Loading...</div>;
    }

    const renderTableHeader = () => {
        return (
            <tr>
                <th>Batch</th>
                {Object.keys(data.table_data).map(level => (
                    <th key={level} colSpan="4">{level}</th>
                ))}
            </tr>
        );
    };

    const renderSubHeader = () => {
        return (
            <tr>
                <th></th>
                {Object.keys(data.table_data).map(level => (
                    <>
                        <th key={`${level}-inv`}>Inv</th>
                        <th key={`${level}-c`}>C</th>
                        <th key={`${level}-inpro`}>In-Pro</th>
                        <th key={`${level}-f`}>F</th>
                    </>
                ))}
            </tr>
        );
    };

    const renderTableData = () => {
        return data.batches.map(batch => (
            <tr key={batch}>
                <td>{batch}</td>
                {Object.keys(data.table_data).map(level => (
                    <>
                        <td key={`${batch}-${level}-inv`}>{data.table_data[level][batch].invites}</td>
                        <td key={`${batch}-${level}-c`}>{data.table_data[level][batch].cleared}</td>
                        <td key={`${batch}-${level}-inpro`}>{data.table_data[level][batch].in_progress}</td>
                        <td key={`${batch}-${level}-f`}>{data.table_data[level][batch].failed}</td>
                    </>
                ))}
            </tr>
        ));
    };

    return (
        <div>
            <table border="1">
                <thead>
                    {renderTableHeader()}
                    {renderSubHeader()}
                </thead>
                <tbody>
                    {renderTableData()}
                </tbody>
            </table>
        </div>
    );
};

export default Dashboard;