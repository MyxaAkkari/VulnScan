import { FaShieldAlt } from "react-icons/fa";
import { useSelector } from "react-redux";
import { RootState } from "../main";

const Logo = () => {
  const isCollapsed = useSelector((state: RootState) => state.scanner.isCollapsed);
  const darkTheme = useSelector((state: RootState) => state.scanner.theme);
  return (
    <div className="logo">
      <div className="logo-icon">
        <FaShieldAlt />
      </div>
      {!isCollapsed && <span className="logo-text" style={{ color: darkTheme ? "#fff" : "#000" }}>VulnScan</span>}
    </div>
  );
};

export default Logo;
