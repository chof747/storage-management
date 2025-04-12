import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HardwareItemPage from './pages/HardwareItemPage';
import Dashboard from './pages/Dashboard';
import Layout from './components/layout/Layout';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/hardware" element={<HardwareItemPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
