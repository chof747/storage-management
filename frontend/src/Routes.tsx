import React from 'react';
import { useRoutes } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import HardwareItemPage from './pages/HardwareItemPage';
import StorageElementPage from './pages/StorageElementPage';
import StorageElementManagerPage from './pages/StorageElementManagerPage';

export default function AppRoutes() {
  const routes = useRoutes([
    {
      path: '/',
      element: (
        <Layout>
          <Dashboard />
        </Layout>
      ),
    },
    {
      path: '/hardware',
      element: (
        <Layout>
          <HardwareItemPage />
        </Layout>
      ),
    },
    {
      path: '/storage',
      element: (
        <Layout>
          <StorageElementPage />
        </Layout>
      ),
    },
    {
      path: '/storage/manage',
      element: (
        StorageElementManagerPage()
      ),
    },
  ]);

  return routes;
}
