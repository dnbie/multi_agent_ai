import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useGoogleLogin, GoogleLogin } from '@react-oauth/google';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  User, 
  Zap, 
  Shield, 
  Sparkles,
  Bot
} from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const { login, googleLogin } = useAuth();
  
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    rememberMe: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.username || !formData.password) {
      toast.error('Please enter both username and password');
      return;
    }

    setLoading(true);
    const result = await login(formData.username, formData.password);
    setLoading(false);

    if (result.success) {
      toast.success('Welcome back!');
      navigate('/dashboard');
    } else {
      toast.error(result.error);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    setLoading(true);
    const result = await googleLogin(credentialResponse);
    setLoading(false);

    if (result.success) {
      toast.success('Welcome! Signed in with Google');
      navigate('/dashboard');
    } else {
      toast.error(result.error);
    }
  };

  const handleGoogleError = () => {
    toast.error('Google sign-in failed. Please try again.');
  };

  return (
    <div className="auth-page">
      {/* Left Side - Login Form */}
      <motion.div 
        className="auth-left"
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="auth-card">
          <div className="auth-logo">
            <div className="auth-logo-icon">
              <Bot size={24} />
            </div>
            <span>Agent X</span>
          </div>

          <h2>Welcome Back</h2>
          <p className="subtitle">Sign in to continue to your dashboard</p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Username</label>
              <div className="input-with-icon">
                <User className="input-icon" size={18} />
                <input
                  type="text"
                  name="username"
                  className="form-input"
                  placeholder="Enter your username"
                  value={formData.username}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <div className="input-with-icon">
                <Lock className="input-icon" size={18} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  className="form-input"
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div className="form-extras">
              <label className="checkbox-wrapper">
                <input
                  type="checkbox"
                  name="rememberMe"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                />
                <span>Remember me</span>
              </label>
              <Link to="/forgot-password" className="forgot-link">
                Forgot password?
              </Link>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-full"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="loading-spinner" style={{ width: 20, height: 20, borderWidth: 2 }}></div>
                  Signing in...
                </>
              ) : (
                <>
                  Sign In
                  <Zap size={18} />
                </>
              )}
            </button>
          </form>

          <div className="divider">
            <span>or continue with</span>
          </div>

          {/* Google Login Button */}
          <div className="google-auth-wrapper">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              useOneTap
              theme="filled_black"
              shape="rectangular"
              size="large"
              width="100%"
              text="signin_with"
            />
          </div>

          <div className="auth-footer">
            <p>
              Don't have an account? <Link to="/signup">Create account</Link>
            </p>
          </div>
        </div>
      </motion.div>

      {/* Right Side - Branding */}
      <motion.div 
        className="auth-right"
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <div className="auth-branding">
          <h1>Agent X</h1>
          <p>Your AI-powered task automation system. Automate emails, manage flights, organize files, and more.</p>
        </div>

        <motion.div 
          className="auth-features"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div className="auth-feature">
            <div className="auth-feature-icon">
              <Zap size={22} />
            </div>
            <span>11+ Specialized AI Agents</span>
          </div>
          <div className="auth-feature">
            <div className="auth-feature-icon">
              <Sparkles size={22} />
            </div>
            <span>Smart Task Automation</span>
          </div>
          <div className="auth-feature">
            <div className="auth-feature-icon">
              <Shield size={22} />
            </div>
            <span>Secure & Private</span>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Login;
