import React from 'react';
import ReactDOM from 'react-dom/client';
import {BrowserRouter} from 'react-router-dom';
import {ApolloProvider} from '@apollo/client/react';
import {Toaster} from 'sonner';
import App from './App';
import './index.css';
import {AuthProvider} from './context/AuthContext';
import {HotelProvider} from './context/HotelContext';
import {apolloClient} from './services/apollo';

ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><ApolloProvider client={apolloClient}><BrowserRouter><HotelProvider><AuthProvider><App/><Toaster richColors position="top-right"/></AuthProvider></HotelProvider></BrowserRouter></ApolloProvider></React.StrictMode>);
