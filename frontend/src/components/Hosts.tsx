import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Table, Button, Card, Space, ConfigProvider, Modal, Form, Input, notification, Select } from "antd";
import { RootState } from "../main";
import { getHostsThunk, deleteHostThunk, createTargetThunk, getPortlistsThunk } from "../features/scannerSlice";
import { ColumnsType } from "antd/es/table";
import { DeleteColumnOutlined, DeleteOutlined, PlusCircleOutlined } from "@ant-design/icons";


interface Host {
  id: string;
  hostname?: string;
  ip: string;
  OS: string;
  MAC?: string;
  "ssh-key"?: string;
}

const Hosts: React.FC = () => {
  const dispatch = useDispatch();
  const { hosts, status, error, portlists } = useSelector((state: RootState) => state.scanner);

  const [selectedHost, setSelectedHost] = useState<Host | null>(null);
  const [isDetailsVisible, setIsDetailsVisible] = useState(false);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]); // Track selected rows
  const [form] = Form.useForm();
  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const getHosts = async () => {
    try {
      const result = await dispatch(getHostsThunk());
      if (result.error) {
        console.log(result.error);
      }
    } catch (error) {
      console.error("Error fetching hosts:", error);
    }
  };

  const getPortlists = async () => {
    try {
      const result = await dispatch(getPortlistsThunk());
      if (result.error) {
        console.log(result.error);
      }
    } catch (error) {
      console.error("Error fetching port lists:", error);
    }
  };

  const fetchData = async () => {
    try {
      await getHosts();
      await getPortlists();
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [dispatch]);

  const handleDeleteHost = async (id: string) => {
    try {
      const result = await dispatch(deleteHostThunk(id));
      if (result.error) {
        notification.error({
          message: "Failed to Delete Host",
          description: result.error.message || "An error occurred while deleting the host.",
        });
      } else {
        notification.success({
          message: "Host Deleted",
          description: "The host was deleted successfully.",
        });
        setSelectedRowKeys([]); // Reset selected rows after deletion
        fetchData(); // Refresh hosts data after deletion
      }
    } catch (error) {
      console.error("Error deleting host:", error);
    }
  };

  const handleDeleteSelectedHosts = async () => {
    for (const key of selectedRowKeys) {
      await handleDeleteHost(String(key)); // Wait for each deletion to complete
      await delay(1000); // Delay of 500ms (you can adjust this value as needed)
    }
    setSelectedRowKeys([]); // Reset selected rows after deletion
  };

  const showDetails = (host: Host) => {
    setSelectedHost(host);
    setIsDetailsVisible(true);
  };

  const handleCreateTargetFromHost = (host: Host) => {
    form.setFieldsValue({
      name: host.hostname || host.ip,
      hosts: host.ip,
      comment: `MAC: ${host.MAC || 'N/A'}, OS: ${host.OS || 'N/A'}, SSH Key: ${host["ssh-key"] || 'N/A'}`,
    });
    setSelectedHost(host);
    setIsFormVisible(true);
  };

  const handleCreateTargetsFromSelected = async () => {
    for (const key of selectedRowKeys) {
      const host = hosts.find(h => h.id === key);
      if (host) {
        await handleCreateTargetFromHost(host);
      }
    }
    setSelectedRowKeys([]); // Reset selected rows after creating targets
  };

  const handleFormSubmit = async (values: any) => {
    const { name, hosts, port_range, port_list_id, comment } = values;
    const result = await dispatch(createTargetThunk({ name, hosts, port_range, port_list_id, comment }));
    if (result.error) {
      notification.error({
        message: "Failed to Create Target",
        description: result.error.message || "An error occurred while creating the target.",
      });
    } else {
      notification.success({
        message: "Target Created",
        description: "The target was created successfully.",
      });
    }
    setIsFormVisible(false);
    form.resetFields();
    setSelectedHost(null); // Reset selected host after operation
  };

  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    setSelectedRowKeys(newSelectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
  };

  const columns: ColumnsType<Host> = [
    {
      title: "Hostname",
      dataIndex: "hostname",
      key: "hostname",
      render: (text: string) => text || "N/A",
      sorter: (a: Host, b: Host) => {
        if (!a.hostname) return -1;
        if (!b.hostname) return 1;
        return a.hostname.localeCompare(b.hostname);
      },
      sortDirections: ["ascend", "descend"],
    },
    {
      title: "IP Address",
      dataIndex: "ip",
      key: "ip",
    },
    {
      title: "Operating System",
      dataIndex: "OS",
      key: "OS",
    },
  ];

  return (
    <ConfigProvider componentSize="small">
      <Card
        title="Hosts"
        extra={
          <Space>
            <Button
              danger
              icon={<DeleteOutlined/>}
              onClick={handleDeleteSelectedHosts}
              disabled={selectedRowKeys.length === 0}
            >
              Delete
            </Button>
            <Button
              type="primary"
              icon={<PlusCircleOutlined/>}
              onClick={handleCreateTargetsFromSelected}
              disabled={selectedRowKeys.length === 0}
            >
              Create Target
            </Button>
          </Space>
        }
      >
        {status === "loading" && <p>Loading...</p>}
        {status === "failed" && <p>Error: {error}</p>}
        {status === "succeeded" && (
          <Table
            columns={columns}
            dataSource={hosts}
            rowKey="id"
            pagination={{ pageSize: 13 }}
            rowSelection={rowSelection} // Enable row selection
            onRow={(record) => ({
              onClick: () => showDetails(record), // Open details modal when clicking on a row
            })}
          />
        )}

        {selectedHost && (
          <Modal
            title="Host Details"
            open={isDetailsVisible}
            onCancel={() => setIsDetailsVisible(false)}
            footer={[
              <Button key="back" onClick={() => setIsDetailsVisible(false)}>
                Close
              </Button>,
            ]}
          >
            <p><strong>ID:</strong> {selectedHost.id}</p>
            <p><strong>Hostname:</strong> {selectedHost.hostname || "N/A"}</p>
            <p><strong>IP Address:</strong> {selectedHost.ip}</p>
            <p><strong>Operating System:</strong> {selectedHost.OS || "N/A"}</p>
            {selectedHost.MAC && <p><strong>MAC Address:</strong> {selectedHost.MAC}</p>}
            {selectedHost["ssh-key"] && <p><strong>SSH Key:</strong> {selectedHost["ssh-key"]}</p>}
          </Modal>
        )}

        <Modal
          title="Create Target from Host"
          open={isFormVisible}
          onCancel={() => {
            setIsFormVisible(false);
            form.resetFields();
            setSelectedHost(null); // Reset selected host on cancel
          }}
          footer={null}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleFormSubmit}
          >
            <Form.Item
              name="name"
              label="Target Name"
              rules={[{ required: true, message: "Please input the target name!" }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="hosts"
              label="Hosts"
              rules={[{ required: true, message: "Please input the hosts!" }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="port_range"
              label="Port Range"
            >
              <Input placeholder="e.g., 1-1024" />
            </Form.Item>
            <Form.Item
              name="port_list_id"
              label="Port List"
            >
              <Select>
                {portlists.map((portlist: any) => (
                  <Select.Option key={portlist.id} value={portlist.id}>
                    {portlist.name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="comment"
              label="Comment"
            >
              <Input.TextArea />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit">
                Create Target
              </Button>
            </Form.Item>
          </Form>
        </Modal>
      </Card>
    </ConfigProvider>
  );
};

export default Hosts;
