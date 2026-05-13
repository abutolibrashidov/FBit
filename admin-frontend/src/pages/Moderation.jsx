import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function Moderation() {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = () => {
        setLoading(true);
        api.get('/admin/reports')
           .then(res => setReports(res.data))
           .catch(console.error)
           .finally(() => setLoading(false));
    };

    const handleAction = async (reportId, action) => {
        try {
            await api.post(`/admin/moderation?report_id=${reportId}&action=${action}`);
            fetchReports();
        } catch (e) {
            console.error(e);
            alert("Action failed to apply");
        }
    };

    return (
        <div>
            <h1 className="page-title">Moderation Queue</h1>
            <div className="glass-panel table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Report ID</th>
                            <th>Receiver ID</th>
                            <th>Violation Reason</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? <tr><td colSpan="5">Loading...</td></tr> : 
                        reports.map(r => (
                            <tr key={r.id}>
                                <td><small>{r.id.split('-')[0]}...</small></td>
                                <td>{r.receiver_id}</td>
                                <td>{r.report_reason}</td>
                                <td><span className="badge badge-warn" style={{background:'rgba(245, 158, 11, 0.1)', color:'#f59e0b', border:'1px solid rgba(245, 158, 11, 0.2)'}}>{r.status}</span></td>
                                <td>
                                    <div style={{display:'flex', gap:'8px'}}>
                                        <button onClick={() => handleAction(r.id, 'ignore')} className="btn btn-sm" style={{background:'rgba(255,255,255,0.1)'}}>Ignore</button>
                                        <button onClick={() => handleAction(r.id, 'mute')} className="btn btn-sm btn-warn">Mute</button>
                                        <button onClick={() => handleAction(r.id, 'ban')} className="btn btn-sm btn-danger">Ban</button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
