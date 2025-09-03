import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './pages/Auth/Login';
import Dashboard from './pages/Dashboard/Dashboard';
import Parts from './pages/Parts/Parts';
import PartsForm from './pages/Parts/PartsForm';
import Orders from './pages/Orders/Orders';
import OrdersForm from './pages/Orders/OrdersForm';
import Contacts from './pages/Contacts/Contacts';
import ContactsForm from './pages/Contacts/ContactsForm';
import Schedule from './pages/Schedule/Schedule';
import ScheduleForm from './pages/Schedule/ScheduleForm';
import Inventory from './pages/Inventory/Inventory';
import Shipping from './pages/Shipping/Shipping';
import LoadingSpinner from './components/UI/LoadingSpinner';

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/parts" element={<Parts />} />
        <Route path="/parts/new" element={<PartsForm />} />
        <Route path="/parts/:id/edit" element={<PartsForm />} />
        <Route path="/orders" element={<Orders />} />
        <Route path="/orders/new" element={<OrdersForm />} />
        <Route path="/orders/:id/edit" element={<OrdersForm />} />
        <Route path="/contacts" element={<Contacts />} />
        <Route path="/contacts/new" element={<ContactsForm />} />
        <Route path="/contacts/:id/edit" element={<ContactsForm />} />
        <Route path="/schedule" element={<Schedule />} />
        <Route path="/schedule/new" element={<ScheduleForm />} />
        <Route path="/schedule/:id/edit" element={<ScheduleForm />} />
        <Route path="/inventory" element={<Inventory />} />
        <Route path="/shipping" element={<Shipping />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Layout>
  );
}

export default App;
