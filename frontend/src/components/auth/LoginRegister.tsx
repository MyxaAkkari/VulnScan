import { useEffect, useState } from "react";
import "./LoginRegister.css";
import { FaEnvelope, FaLock, FaUser } from "react-icons/fa";
import { loginUser, registerUser } from "../../features/authSlice";
import { useDispatch } from "react-redux";
import CustomAlert from "../CustomAlert";
import { useNavigate } from "react-router-dom";

const LoginRegister = () => {
  const [action, setAction] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [userName, setUserName] = useState("");
  const [error, setError] = useState(null);
  const [rememberMe, setRememberMe] = useState(false);
  const [termsChecked, setTermsChecked] = useState(false);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState("");
  const dispatch = useDispatch();
  const navigate = useNavigate(); 

  const registerLink = () => {
    setAction("active-register");
  };

  const loginLink = () => {
    setAction("");
  };

  const forgotPasswordLink = () => {
    setAction("active-forgot");
  };

  const triggerAlert = (message: string) => {
    setAlertMessage(message);
    setShowAlert(true);
  };

  const closeAlert = () => {
    setShowAlert(false);
  };

  const handleForgotPassword = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle password reset link logic here (e.g., API call)
    triggerAlert(`Reset link sent to ${email}`);
  };

  useEffect(() => {
    const savedEmail = localStorage.getItem("email");
    if (savedEmail) {
      setEmail(savedEmail);
      setRememberMe(true);
    }
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const result = await dispatch(loginUser({ email, password }));
    if (result.error) {
      setError(result.payload);
    } else {
      localStorage.setItem("token", result.payload.access_token);
      setEmail("");
      setPassword("");
      navigate("/");
    }
    // Save email if "Remember me" is checked
    if (rememberMe) {
      localStorage.setItem("email", email);
    } else {
      localStorage.removeItem("email");
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!termsChecked) {
      setError("You must agree to the terms and conditions.");
      return;
    }
    setError(null);
    const result = await dispatch(
      registerUser({ email, username: userName, password })
    );
    if (result.error) {
      setError(result.payload);
    } else {
      setEmail("");
      setPassword("");
      setUserName("");
    }
  };

  return (
    <>
      {showAlert && <CustomAlert message={alertMessage} onClose={closeAlert} />}
      <div className="login-register-wrapper">
      <div className={`wrapper ${action}`}>
        <div className="form-box login">
          <form onSubmit={handleLogin}>
            <h1>Login</h1>
            <div className="input-box">
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <FaEnvelope className="icon" />
            </div>
            <div className="input-box">
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <FaLock className="icon" />
              {error && (
                <div className="error-message">
                  <label>{error}</label>
                </div>
              )}
            </div>
            <div className="remember-forgot">
              <label>
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                Remember me
              </label>

              <a href="#" onClick={forgotPasswordLink}>
                Forgot password?
              </a>
            </div>
            <button type="submit">Login</button>
            <div className="register-link">
              <p>
                Don't have an account?{" "}
                <a href="#" onClick={registerLink}>
                  Register
                </a>
              </p>
            </div>
          </form>
        </div>

        {/* Register Form */}
        <div className="form-box register">
          <form onSubmit={handleRegister}>
            <h1>Registration</h1>
            <div className="input-box">
              <input
                type="text"
                placeholder="Username"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                required
              />
              <FaUser className="icon" />
            </div>
            <div className="input-box">
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <FaEnvelope className="icon" />
            </div>
            <div className="input-box">
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <FaLock className="icon" />
              {error && (
                <div className="error-message">
                  <label>{error}</label>
                </div>
              )}
            </div>
            <div className="remember-forgot">
              <label>
                <input
                  type="checkbox"
                  checked={termsChecked}
                  onChange={(e) => setTermsChecked(e.target.checked)}
                />
                I agree to the terms & conditions
              </label>
            </div>
            <button type="submit">Register</button>

            <div className="register-link">
              <p>
                Already have an account?{" "}
                <a href="#" onClick={loginLink}>
                  Login
                </a>
              </p>
            </div>
          </form>
        </div>
        <div className="form-box forgot">
          <form onSubmit={handleForgotPassword}>
            <h1>Forgot Password</h1>
            <div className="input-box">
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <FaEnvelope className="icon" />
            </div>
            <button type="submit">Send Reset Link</button>
            <div className="register-link">
              <p>
                Remember your password?{" "}
                <a href="#" onClick={loginLink}>
                  Login
                </a>
              </p>
            </div>
          </form>
        </div>
      </div>
      </div>
    </>
  );
};
export default LoginRegister;
