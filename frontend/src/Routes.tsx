import React from 'react';
import { useRoutes } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import HardwareItemPage from './pages/HardwareItemPage';
import StorageElementPage from './pages/StorageElementPage';
import StorageTypePage from './pages/StorageTypePage';
import StorageElementManagerPage from './pages/StorageElementManagerPage';


export default function AppRoutes() {
  const EmptyPage = () => null;

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
    {
      path: '/storage_type',
      element: (
        <Layout>
          <StorageTypePage />
        </Layout>
      )
    },
    {
      path: '/label-printing',
      element: (
        <Layout>
          <EmptyPage />
        </Layout>
      )
    },
  ]);

  return routes;
}
