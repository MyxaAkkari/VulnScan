import { useDispatch, useSelector } from "react-redux";
import { useEffect, useState } from "react";
import {
  Table,
  Button,
  Card,
  Space,
  ConfigProvider,
  Form,
  Input,
  Select,
  notification,
  Modal,
} from "antd";
import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { RootState } from "../main";
import {
  getTargetsThunk,
  getPortlistsThunk,
  createTargetThunk,
  deleteTargetThunk,
  modifyTargetThunk,
} from "../features/scannerSlice";

const Targets = () => {
  const dispatch = useDispatch();
  const { targets, portlists, status, error } = useSelector(
    (state: RootState) => state.scanner
  );

  const [form] = Form.useForm();
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [isDetailsVisible, setIsDetailsVisible] = useState(false);
  const [currentTarget, setCurrentTarget] = useState<any>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const delay = (ms: number) =>
    new Promise((resolve) => setTimeout(resolve, ms));

  const getTargets = async () => {
    try {
      const result = await dispatch(getTargetsThunk());
      if (result.error) {
        console.log(result.error);
      }
      return result;
    } catch (error) {
      console.error("Error fetching targets:", error);
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
      await getTargets();
      await getPortlists();
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [dispatch]);

  const handleAddOrModifyTarget = async (values: any) => {
    const { name, hosts, port_range, port_list_id, comment } = values;

    if (currentTarget) {
      // Modify existing target
      const result = await dispatch(
        modifyTargetThunk({
          targetId: currentTarget.id,
          data: { name, hosts, port_range, port_list_id, comment },
        })
      );
      if (result.error) {
        notification.error({
          message: "Failed to Modify Target",
          description:
            result.error.message ||
            "An error occurred while modifying the target.",
        });
      } else {
        notification.success({
          message: "Target Modified",
          description: "The target was modified successfully.",
        });
      }
    } else {
      // Create new target
      const result = await dispatch(
        createTargetThunk({ name, hosts, port_range, port_list_id, comment })
      );
      if (result.error) {
        notification.error({
          message: "Failed to Create Target",
          description:
            result.error.message ||
            "An error occurred while creating the target.",
        });
      } else {
        notification.success({
          message: "Target Created",
          description: "The target was created successfully.",
        });
      }
    }

    setIsFormVisible(false);
    form.resetFields();
    setCurrentTarget(null); // Reset current target after operation
    getTargets(); // Refresh targets list
  };

  const handleDeleteSelected = async () => {
    try {
      for (const id of selectedRowKeys) {
        const result = await dispatch(deleteTargetThunk(id));
        if (result.error) {
          notification.error({
            message: "Failed to Delete Target",
            description:
              result.error.message ||
              "An error occurred while deleting the target.",
          });
        } else {
          notification.success({
            message: "Target Deleted",
            description: "The target was deleted successfully.",
          });
          await delay(1000); // Delay of 500ms (you can adjust this value as needed)
        }
      }
      setSelectedRowKeys([]);
      getTargets(); // Refresh targets list after deletion
    } catch (error) {
      console.error("Error deleting target:", error);
    }
  };

  const handleModifySelected = () => {
    if (selectedRowKeys.length === 1) {
      const target = targets.find((t) => t.id === selectedRowKeys[0]);
      if (target) {
        modifyTarget(target);
      }
    } else {
      notification.warning({
        message: "Select a Single Target",
        description: "Please select only one target to modify.",
      });
    }
  };

  const showDetails = (target: any) => {
    setCurrentTarget(target);
    setIsDetailsVisible(true);
  };

  const modifyTarget = (target: any) => {
    form.setFieldsValue({
      name: target.name,
      hosts: target.hosts,
      port_range: target.port_range,
      port_list_id: target.port_list_id,
      comment: target.comment,
    });
    setCurrentTarget(target);
    setIsFormVisible(true);
  };

  const columns = [
    {
      title: "Target Name",
      dataIndex: "name",
      key: "name",
      sorter: (a: any, b: any) => a.name.localeCompare(b.name),
      sortDirections: ["ascend", "descend"],
    },
    {
      title: "IP",
      dataIndex: "hosts",
      key: "hosts",
    },
    {
      title: "Portlist Name",
      dataIndex: "port_list",
      key: "port_list",
    },
  ];

  return (
    <ConfigProvider componentSize="small">
      <Card
        title="Targets"
        extra={
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsFormVisible(true)}
            >
              Add Target
            </Button>
            <Button
              type="primary"
              icon={<EditOutlined />}
              onClick={handleModifySelected}
              disabled={selectedRowKeys.length !== 1}
            >
              Modify
            </Button>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleDeleteSelected}
              disabled={selectedRowKeys.length === 0}
            >
              Delete
            </Button>
          </Space>
        }
      >
        <Modal
          title={currentTarget ? "Edit Target" : "Add Target"}
          open={isFormVisible}
          onCancel={() => {
            setIsFormVisible(false);
            form.resetFields();
            setCurrentTarget(null);
          }}
          footer={null}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleAddOrModifyTarget}
          >
            <Form.Item
              name="name"
              label="Target Name"
              rules={[
                { required: true, message: "Please input the target name!" },
              ]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="hosts"
              label="Hosts IP (Comma separated)"
              rules={[{ required: true, message: "Please input the hosts!" }]}
            >
              <Input />
            </Form.Item>
            <Form.Item name="port_range" label="Port Range">
              <Input placeholder="e.g., 1-1024" />
            </Form.Item>
            <Form.Item name="port_list_id" label="Port List">
              <Select placeholder="Select a port list">
                {(Array.isArray(portlists) ? portlists : []).map((portlist) => (
                  <Select.Option key={portlist.id} value={portlist.id}>
                    {portlist.name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="comment" label="Comment">
              <Input placeholder="Optional" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit">
                {currentTarget ? "Update" : "Submit"}
              </Button>
              <Button
                onClick={() => {
                  setIsFormVisible(false);
                  form.resetFields();
                  setCurrentTarget(null);
                }}
                style={{ marginTop: 10 }}
              >
                Cancel
              </Button>
            </Form.Item>
          </Form>
        </Modal>
        <Modal
          title="Target Details"
          open={isDetailsVisible}
          onCancel={() => setIsDetailsVisible(false)}
          footer={null}
        >
          {currentTarget && (
            <div>
              <p>
                <strong>Name:</strong> {currentTarget.name}
              </p>
              <p>
                <strong>Hosts:</strong> {currentTarget.hosts}
              </p>
              <p>
                <strong>Port List:</strong> {currentTarget.port_list}
              </p>
              <p>
                <strong>Creation Time:</strong> {currentTarget.creation_time}
              </p>
              <p>
                <strong>Modification Time:</strong>{" "}
                {currentTarget.modification_time}
              </p>
              <p>
                <strong>Comment:</strong> {currentTarget.comment}
              </p>
            </div>
          )}
        </Modal>
        <Table
          rowSelection={{
            selectedRowKeys,
            onChange: setSelectedRowKeys,
          }}
          onRow={(record) => ({
            onClick: () => showDetails(record),
          })}
          columns={columns}
          dataSource={Array.isArray(targets) ? targets : []}
          rowKey="id"
          loading={status === "loading"}
          pagination={{ pageSize: 13 }}
        />
      </Card>
    </ConfigProvider>
  );
};

export default Targets;
