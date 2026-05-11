import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Users, ShieldAlert, BarChart3, LogOut } from 'lucide-react';
import { setAuthToken } from '../services/api';

export default function Sidebar() {
    const navigate = useNavigate();

    const handleLogout = () => {
        setAuthToken(null);
        navigate('/login');
    };

    return (
        <div className="sidebar">
            <div className="logo">
                <span>⚡</span> FBit Admin
            </div>
            <div className="nav-links">
                <NavLink to="/" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
                    <LayoutDashboard size={20}/> Dashboard
                </NavLink>
                <NavLink to="/users" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
                    <Users size={20}/> Users
                </NavLink>
                <NavLink to="/moderation" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
                    <ShieldAlert size={20}/> Moderation
                </NavLink>
                <NavLink to="/analytics" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
                    <BarChart3 size={20}/> Analytics
                </NavLink>
            </div>
            
            <button onClick={handleLogout} className="btn" style={{marginTop: 'auto', background: 'transparent', color: 'var(--text-muted)'}}>
                <LogOut size={20} /> Logout
            </button>
        </div>
    );
}
