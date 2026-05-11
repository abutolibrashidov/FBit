import React, { useEffect, useState } from 'react';
import api from '../services/api';

export default function Users() {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = () => {
        setLoading(true);
        api.get('/users?limit=100')
           .then(res => setUsers(res.data))
           .catch(console.error)
           .finally(() => setLoading(false));
    };

    const handleBan = async (userId, isBanned) => {
        setActionLoading(userId + '-ban');
        try {
            if (isBanned) {
                await api.post(`/users/${userId}/unban`);
            } else {
                await api.post(`/users/${userId}/ban`);
            }
            fetchUsers();
        } catch (e) {
            console.error(e);
            alert('Action failed');
        } finally {
            setActionLoading(null);
        }
    };

    const handleMute = async (userId) => {
        setActionLoading(userId + '-mute');
        try {
            await api.post(`/users/${userId}/mute?hours=24`);
            fetchUsers();
        } catch (e) {
            console.error(e);
            alert('Action failed');
        } finally {
            setActionLoading(null);
        }
    };

    return (
        <div>
            <h1 className="page-title">User Management</h1>
            <div className="glass-panel table-container">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Status</th>
                            <th>Risk Score</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? <tr><td colSpan="5">Loading...</td></tr> :
                        users.map(u => (
                            <tr key={u.id}>
                                <td><small>{u.id}</small></td>
                                <td>
                                    @{u.username || 'unknown'} <br/>
                                    <small style={{color:'var(--text-muted)'}}>{u.full_name}</small>
                                </td>
                                <td>
                                    {u.is_banned
                                        ? <span className="badge badge-danger" style={{padding:'4px 8px', fontSize:'10px'}}>Banned</span>
                                        : u.is_muted
                                            ? <span className="badge badge-warn" style={{padding:'4px 8px', fontSize:'10px', background:'rgba(245,158,11,.1)', color:'#f59e0b', border:'1px solid rgba(245,158,11,.2)'}}>Muted</span>
                                            : <span className="badge badge-success" style={{padding:'4px 8px', fontSize:'10px'}}>Active</span>
                                    }
                                </td>
                                <td style={{color: u.risk_score > 50 ? 'var(--danger)' : 'var(--success)'}}>
                                    <strong>{u.risk_score}</strong>
                                </td>
                                <td>
                                    <div style={{display:'flex', gap:'8px'}}>
                                        <button
                                            className="btn btn-sm btn-warn"
                                            onClick={() => handleMute(u.id)}
                                            disabled={actionLoading === u.id + '-mute'}
                                        >
                                            {actionLoading === u.id + '-mute' ? '...' : 'Mute 24h'}
                                        </button>
                                        <button
                                            className={`btn btn-sm ${u.is_banned ? '' : 'btn-danger'}`}
                                            style={u.is_banned ? {background:'rgba(255,255,255,0.1)'} : {}}
                                            onClick={() => handleBan(u.id, u.is_banned)}
                                            disabled={actionLoading === u.id + '-ban'}
                                        >
                                            {actionLoading === u.id + '-ban' ? '...' : u.is_banned ? 'Unban' : 'Ban'}
                                        </button>
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
