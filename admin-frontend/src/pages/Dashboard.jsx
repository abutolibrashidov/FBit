import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Users, Activity, ShieldAlert, BarChart } from 'lucide-react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function Dashboard() {
    const [data, setData] = useState(null);

    useEffect(() => {
        api.get('/analytics').then(res => setData(res.data)).catch(console.error);
    }, []);

    if (!data) return <div className="page-title">Loading...</div>;

    const chartData = {
        labels: ['Active Users Today', 'New Users Today'],
        datasets: [{
            data: [data.active_users_today, data.new_users_today],
            backgroundColor: ['#6366f1', '#10b981'],
            borderColor: ['#0f0f13', '#0f0f13'],
        }]
    };

    return (
        <div>
            <h1 className="page-title">Platform Overview</h1>
            <div className="grid-cards">
                <div className="glass-panel metric-card">
                    <div className="metric-header">
                        <div className="metric-icon"><Users size={20}/></div>
                        <div className="metric-title">Total Users</div>
                    </div>
                    <div className="metric-value">{data.total_users}</div>
                </div>
                <div className="glass-panel metric-card">
                    <div className="metric-header">
                        <div className="metric-icon"><Activity size={20}/></div>
                        <div className="metric-title">Active Today</div>
                    </div>
                    <div className="metric-value">{data.active_users_today}</div>
                </div>
                <div className="glass-panel metric-card">
                    <div className="metric-header">
                        <div className="metric-icon"><ShieldAlert size={20}/></div>
                        <div className="metric-title">Banned Users</div>
                    </div>
                    <div className="metric-value">{data.banned_users}</div>
                </div>
                <div className="glass-panel metric-card">
                    <div className="metric-header">
                        <div className="metric-icon"><BarChart size={20}/></div>
                        <div className="metric-title">Reports Today</div>
                    </div>
                    <div className="metric-value">{data.reports_today}</div>
                </div>
            </div>
            
            <div className="grid-cards">
                <div className="glass-panel" style={{padding: '24px', width: '340px'}}>
                   <h3 style={{marginBottom: '20px', fontSize: '16px', color: 'var(--text-muted)'}}>User Activity Metrics</h3>
                   <Doughnut data={chartData} options={{cutout: '75%'}}/>
                </div>
            </div>
        </div>
    );
}
