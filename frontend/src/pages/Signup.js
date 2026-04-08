import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  User, 
  UserPlus,
  Zap, 
  Shield, 
  Sparkles,
  Bot,
  CheckCircle
} from 'lucide-react';

const Signup = () => {
  const navigate = useNavigate();
  const { signup, googleLogin } = useAuth();
  
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const validateForm = () => {
    if (!formData.username || !formData.password) {
      toast.error('Username and password are required');
      return false;
    }
    
    if (formData.username.length < 3) {
      toast.error('Username must be at least 3 characters');
      return false;
    }
    
    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return false;
    }
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return false;
    }
    
    if (!formData.agreeTerms) {
      toast.error('Please agree to the terms and conditions');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    const result = await signup({
      full_name: formData.fullName,
      email: formData.email,
      username: formData.username,
      password: formData.password
    });
    setLoading(false);

    if (result.success) {
      toast.success('Account created! Please sign in.');
      navigate('/login');
    } else {
      toast.error(result.error);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    setLoading(true);
    const result = await googleLogin(credentialResponse);
    setLoading(false);

    if (result.success) {
      toast.success('Welcome! Account created with Google');
      navigate('/dashboard');
    } else {
      toast.error(result.error);
    }
  };

  const handleGoogleError = () => {
    toast.error('Google sign-up failed. Please try again.');
  };

  const passwordStrength = () => {
    const password = formData.password;
    if (!password) return 0;
    let strength = 0;
    if (password.length >= 6) strength++;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const strengthColors = ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#10b981'];
  const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];

  return (
    <div className="auth-page">
      {/* Left Side - Signup Form */}
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

          <h2>Create Account</h2>
          <p className="subtitle">Start your automation journey today</p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <div className="input-with-icon">
                <User className="input-icon" size={18} />
                <input
                  type="text"
                  name="fullName"
                  className="form-input"
                  placeholder="Enter your full name"
                  value={formData.fullName}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Email</label>
              <div className="input-with-icon">
                <Mail className="input-icon" size={18} />
                <input
                  type="email"
                  name="email"
                  className="form-input"
                  placeholder="Enter your email"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Username</label>
              <div className="input-with-icon">
                <User className="input-icon" size={18} />
                <input
                  type="text"
                  name="username"
                  className="form-input"
                  placeholder="Choose a username"
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
                  placeholder="Create a password"
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
              {formData.password && (
                <div style={{ marginTop: '0.5rem' }}>
                  <div style={{ display: 'flex', gap: '4px', marginBottom: '4px' }}>
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        style={{
                          flex: 1,
                          height: '4px',
                          borderRadius: '2px',
                          background: i < passwordStrength() 
                            ? strengthColors[passwordStrength() - 1] 
                            : 'rgba(255,255,255,0.1)'
                        }}
                      />
                    ))}
                  </div>
                  <span style={{ 
                    fontSize: '0.75rem', 
                    color: strengthColors[passwordStrength() - 1] || '#71717a' 
                  }}>
                    {passwordStrength() > 0 ? strengthLabels[passwordStrength() - 1] : 'Enter password'}
                  </span>
                </div>
              )}
            </div>

            <div className="form-group">
              <label className="form-label">Confirm Password</label>
              <div className="input-with-icon">
                <Lock className="input-icon" size={18} />
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  name="confirmPassword"
                  className="form-input"
                  placeholder="Confirm your password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {formData.confirmPassword && formData.password === formData.confirmPassword && (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.25rem', 
                  marginTop: '0.5rem',
                  color: '#10b981',
                  fontSize: '0.75rem'
                }}>
                  <CheckCircle size={14} />
                  <span>Passwords match</span>
                </div>
              )}
            </div>

            <div className="form-group">
              <label className="checkbox-wrapper">
                <input
                  type="checkbox"
                  name="agreeTerms"
                  checked={formData.agreeTerms}
                  onChange={handleChange}
                />
                <span>I agree to the <Link to="/terms" style={{ color: 'var(--accent-primary)' }}>Terms of Service</Link> and <Link to="/privacy" style={{ color: 'var(--accent-primary)' }}>Privacy Policy</Link></span>
              </label>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary btn-full"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="loading-spinner" style={{ width: 20, height: 20, borderWidth: 2 }}></div>
                  Creating account...
                </>
              ) : (
                <>
                  Create Account
                  <UserPlus size={18} />
                </>
              )}
            </button>
          </form>

          <div className="divider">
            <span>or sign up with</span>
          </div>

          {/* Google Signup Button */}
          <div className="google-auth-wrapper">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              theme="filled_black"
              shape="rectangular"
              size="large"
              width="100%"
              text="signup_with"
            />
          </div>

          <div className="auth-footer">
            <p>
              Already have an account? <Link to="/login">Sign in</Link>
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
          <h1>Join Agent X</h1>
          <p>Unlock the power of AI automation. Create your free account and start automating tasks in minutes.</p>
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
            <span>Free to get started</span>
          </div>
          <div className="auth-feature">
            <div className="auth-feature-icon">
              <Sparkles size={22} />
            </div>
            <span>No credit card required</span>
          </div>
          <div className="auth-feature">
            <div className="auth-feature-icon">
              <Shield size={22} />
            </div>
            <span>Enterprise-grade security</span>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Signup;
