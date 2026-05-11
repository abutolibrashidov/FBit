import axios from 'axios';

const api = axios.create({
    baseURL: '/admin'
});

export const setAuthToken = (token) => {
    if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        localStorage.setItem('adminToken', token);
    } else {
        delete api.defaults.headers.common['Authorization'];
        localStorage.removeItem('adminToken');
    }
};

export const logout = () => {
    setAuthToken(null);
};

const token = localStorage.getItem('adminToken');
if (token) {
    setAuthToken(token);
}

export default api;
