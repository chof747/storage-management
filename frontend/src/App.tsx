import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HardwareItemPage from './pages/HardwareItemPage';
import Dashboard from './pages/Dashboard';
import Layout from './components/layout/Layout';
import StorageElementPage from './pages/StorageElementPage';
import StorageElementManagerPage from './pages/StorageElementManagerPage';
import AppRoutes from './Routes';

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
