import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ToastProvider } from './context/ToastContext';
import Navbar from './components/Navbar';
import RequireAuth from './components/RequireAuth';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import ProblemList from './pages/ProblemList';
import ProblemDetail from './pages/ProblemDetail';
import Results from './pages/Results';
import History from './pages/History';
import Forum from './pages/Forum';
import UploadProblem from './pages/UploadProblem';
import ForgotPassword from './pages/ForgotPass';
import VerifyOtp from './pages/VerifyOtp';
import ResetPassword from './pages/ResetPassword';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <Navbar />
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/forum" element={<Forum />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgotpassword" element={<Navigate to="/forgetpassword" replace />} />
            <Route path="/forgetpassword" element={<ForgotPassword />} />
            <Route path="/verify-otp" element={<VerifyOtp />} />
            <Route path="/reset-password" element={<ResetPassword />} />

            {/* Auth-gated routes — redirect to /login, preserve destination */}
            <Route path="/problems" element={<RequireAuth><ProblemList /></RequireAuth>} />
            <Route path="/problems/:id" element={<RequireAuth><ProblemDetail /></RequireAuth>} />
            <Route path="/uploadproblem" element={<RequireAuth><UploadProblem /></RequireAuth>} />
            <Route path="/results/:id" element={<RequireAuth><Results /></RequireAuth>} />
            <Route path="/history" element={<RequireAuth><History /></RequireAuth>} />
            <Route path="/history/:userId" element={<RequireAuth><History /></RequireAuth>} />


            {/* 404 Catch-all route */}
            <Route path="/404" element={<NotFound />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}

