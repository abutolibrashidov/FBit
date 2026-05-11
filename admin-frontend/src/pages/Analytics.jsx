import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function Analytics() {
    const [data, setData] = useState(null);

    useEffect(() => {
        api.get('/analytics').then(res => setData(res.data)).catch(console.error);
    }, []);

    if (!data) return <div className="page-title">Loading...</div>;

    return (
        <div>
            <h1 className="page-title">System Analytics</h1>
            <div className="glass-panel table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Metric Name</th>
                            <th>Current Realtime Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Platform Wide Total Users</td><td><strong>{data.total_users}</strong></td></tr>
                        <tr><td>Active Users (Last 24h)</td><td><strong>{data.active_users_today}</strong></td></tr>
                        <tr><td>New Users (Last 24h)</td><td><strong>{data.new_users_today}</strong></td></tr>
                        <tr><td>Total Banned Assets</td><td style={{color:'var(--danger)'}}><strong>{data.banned_users}</strong></td></tr>
                        <tr><td>Open Toxic Reports</td><td><strong>{data.reports_today}</strong></td></tr>
                        <tr><td>Anonymous Msgs Today</td><td><strong>{data.anonymous_messages_today}</strong></td></tr>
                        <tr><td>Friendship Tests Today</td><td><strong>{data.friendship_tests_today}</strong></td></tr>
                        <tr><td>Poll Votes Today</td><td><strong>{data.poll_votes_today}</strong></td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
}
