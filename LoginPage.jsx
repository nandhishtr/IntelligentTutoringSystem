import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
//import { login, register } from '../api'; // Add register API function

const LoginPage = () => {
  const [isRegister, setIsRegister] = useState(false); // Toggle between login and register
  const [credentials, setCredentials] = useState({ username: '', password: '', email: '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // const handleSubmit = async (e) => {
  //   e.preventDefault();
  //   try {
  //     if (isRegister) {
  //       // Register user
  //       await register({ username: credentials.username, password: credentials.password, email: credentials.email });
  //       setMessage('Registration successful! You can now log in.');
  //       setIsRegister(false); // Switch back to login form
  //     } else {
  //       // Log in user
  //       const data = await login({ username: credentials.username, password: credentials.password });
  //       localStorage.setItem('accessToken', data.access);
  //       localStorage.setItem('refreshToken', data.refresh);
  //       navigate('/upload'); // Redirect to upload page
  //     }
  //   } catch (err) {
  //     setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
  //   }
  // };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>{isRegister ? 'Register' : 'Login'}</h1>
        <label>
          Username:
          <input
            type="text"
            value={credentials.username}
            onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
            required
          />
        </label>
        {isRegister && (
          <label>
            Email:
            <input
              type="email"
              value={credentials.email}
              onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
              required
            />
          </label>
        )}
        <label>
          Password:
          <input
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
            required
          />
        </label>
        <button type="submit">{isRegister ? 'Register' : 'Login'}</button>
        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}
        <p>
          {isRegister ? (
            <>
              Already have an account? <span onClick={() => setIsRegister(false)}>Login</span>
            </>
          ) : (
            <>
              Don’t have an account? <span onClick={() => setIsRegister(true)}>Register</span>
            </>
          )}
        </p>
      </form>
    </div>
  );
};

export default LoginPage;