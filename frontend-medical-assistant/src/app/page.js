'use client';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import Dashboard from "@/components/dashboard/dashboard"

export default function Home() {
  const { user, logout } = useAuth();

  return (
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  );
}
