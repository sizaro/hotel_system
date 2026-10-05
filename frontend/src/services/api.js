import axios from 'axios';
const baseURL=import.meta.env.VITE_API_BASE_URL||'http://127.0.0.1:8000/api';
export const tokenStore={get:()=>sessionStorage.getItem('hotel_access'),set:v=>sessionStorage.setItem('hotel_access',v),clear:()=>{sessionStorage.removeItem('hotel_access');sessionStorage.removeItem('hotel_refresh')}};
export const api=axios.create({baseURL,timeout:30000});
api.interceptors.request.use(config=>{const token=tokenStore.get();if(token)config.headers.Authorization=`Bearer ${token}`;return config});
api.interceptors.response.use(response=>response,error=>{if(error.response?.status===401)tokenStore.clear();return Promise.reject(error)});
