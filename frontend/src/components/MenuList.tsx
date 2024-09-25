// src/components/MenuList.tsx
import {
  BarsOutlined,
  ContactsOutlined,
  DashboardOutlined,
  FieldTimeOutlined,
  FileSearchOutlined,
  LogoutOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import { Menu, Switch } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../main";
import { setTheme } from "../features/scannerSlice";
import { logout } from "../features/authSlice";
import { HiOutlineMoon, HiOutlineSun } from "react-icons/hi";
import { BiHelpCircle } from "react-icons/bi";

const MenuList = ({ setSelectedComponent }: { setSelectedComponent: (component: string) => void }) => {
  const darkTheme = useSelector((state: RootState) => state.scanner.theme);
  const dispatch = useDispatch();
  const themeIcon = darkTheme ? <HiOutlineSun /> : <HiOutlineMoon />;

  const handleThemeChange = () => {
    dispatch(setTheme());
  };
  
  const handleMenuClick = (e: any) => {
    setSelectedComponent(e.key); // Update the selected component
  };

  // Define the items for the Menu  
  const items = [
    {
      key: "dashboard",
      icon: <DashboardOutlined />,
      label: "Dashboard",
    },
    {
      key: "reports",
      icon: <FileSearchOutlined />,
      label: "Reports",
    },
    {
      key: "tasks",
      icon: <BarsOutlined />,
      label: "Tasks",
    },
    {
      key: "schedules",
      icon: <FieldTimeOutlined />,
      label: "Schedules",
    },
    {
      key: "targets", 
      icon: <TeamOutlined />,
      label: "Targets",
    },
    {
      key: "hosts", 
      icon: <ContactsOutlined />,
      label: "Hosts",
    },
    {
      type: "divider",
    },
    {
      key: "help",
      icon: <BiHelpCircle />,
      label: "Help",
      onClick: () => window.open("https://github.com/MyxaAkkari/VulnScan.git", "_blank"),
    },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: "Logout",
      onClick: () => dispatch(logout()),
    },
    {
      key: "theme",
      icon: themeIcon,
      label: <Switch checked={darkTheme} onChange={handleThemeChange} />,
    },
  ];

  return (
    <Menu
      theme={darkTheme ? "dark" : "light"}
      mode="inline"
      className="menu-bar"
      items={items}
      onClick={handleMenuClick}
    />
  );
};

export default MenuList;
