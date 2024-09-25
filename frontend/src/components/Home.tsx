// src/components/Home.tsx
import { Layout } from "antd";
import Logo from "./Logo";
import MenuList from "./MenuList";
import { Content } from "antd/es/layout/layout";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "../main";
import Targets from "./Targets";
import Hosts from "./Hosts";
import Tasks from "./Tasks";
import Schedules from "./Schedules";
import Reports from "./Reports";
import Dashboard from "./Dashboard";
import { setSidebarCollapsed } from "../features/scannerSlice"; 
import { useState } from "react";

const { Sider } = Layout;

const Home = () => {
  const darkTheme = useSelector((state: RootState) => state.scanner.theme);
  const [collapsed, setCollapsed] = useState(false);
  const [selectedComponent, setSelectedComponent] = useState("dashboard"); // Default component
  const dispatch = useDispatch();

  const onCollapse = (collapsed: boolean) => {
    setCollapsed(collapsed);
    dispatch(setSidebarCollapsed(collapsed)); 
  };

  // Function to render the selected component
  const renderComponent = () => {
    switch (selectedComponent) {
      case "targets":
        return <Targets />;
      case "hosts":
        return <Hosts />;
      case "tasks":
        return <Tasks />;
      case "schedules":
        return <Schedules />;
      case "reports":
        return <Reports />;
      case "dashboard":
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        width={210}
        collapsible
        collapsed={collapsed}
        onCollapse={onCollapse}
        collapsedWidth="70"
        className="sidebar"
        style={{
          position: "fixed",
          height: "100vh",
          overflow: "auto",
          zIndex: 100,
        }}
        theme={darkTheme ? "dark" : "light"}
      >
        <Logo />
        <MenuList setSelectedComponent={setSelectedComponent} />
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 70 : 210 }}>
        <Content
          className="content"
          style={{ padding: "10px", overflowY: "auto", height: "100vh" }}
        >
          {renderComponent()} 
        </Content>
      </Layout>
    </Layout>
  );
};

export default Home;
