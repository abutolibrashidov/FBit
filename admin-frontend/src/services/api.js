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
    window.location.href = '/login';
};

const token = localStorage.getItem('adminToken');
if (token) {
    setAuthToken(token);
}

api.interceptors.response.use(
    response => response,
    error => {
        if (error.response && (error.response.status === 401 || error.response.status === 403)) {
            logout();
        }
        return Promise.reject(error);
    }
);

export default api;
