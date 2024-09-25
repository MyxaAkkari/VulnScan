import './App.css';
import { Routes, Route, Navigate } from 'react-router-dom';
import Home from './components/Home';
import LoginRegister from './components/auth/LoginRegister';
import { RootState } from './main';
import { useSelector } from 'react-redux';
import { ConfigProvider, theme } from 'antd';


function App() {
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn || !!localStorage.getItem('token')); // Check for token
  const darkTheme = useSelector((state: RootState) => state.scanner.theme);
  return (
    <ConfigProvider
    theme={{
      algorithm: darkTheme ? theme.darkAlgorithm : theme.defaultAlgorithm,
    }}
  >
    <Routes>
      <Route path='/login-register' element={isLoggedIn ? <Navigate to="/" /> : <LoginRegister />} />
      <Route path='*' element={isLoggedIn ? <Home /> : <Navigate to="/login-register" />} />
    </Routes>
    </ConfigProvider>
  );
}

export default App;
