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
  notification,
  Modal,
  Select,
} from "antd";
import {
  DeleteOutlined,
  PlusOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  StopOutlined,
  EditOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import { RootState } from "../main";
import {
  getTasksThunk,
  startTaskThunk,
  stopTaskThunk,
  resumeTaskThunk,
  createTaskThunk,
  modifyTaskThunk,
  deleteTaskThunk,
  getTargetsThunk,
  getConfigsThunk,
  getScannersThunk,
  getSchedulesThunk,
  getTaskThunk,
} from "../features/scannerSlice";

const Tasks = () => {
  const dispatch = useDispatch();
  const [form] = Form.useForm();
  const { tasks, status, error, targets, configs, scanners, schedules } =
    useSelector((state: RootState) => state.scanner);
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [currentTask, setCurrentTask] = useState<any>(null);
  const [isDetailVisible, setIsDetailVisible] = useState(false);
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

  const getTasks = async () => {
    try {
      const result = await dispatch(getTasksThunk());
      if (result.error) {
        console.log(result.error);
      }
      return result;
    } catch (error) {
      console.error("Error fetching tasks:", error);
    }
  };

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

  const getConfigs = async () => {
    try {
      const result = await dispatch(getConfigsThunk());
      if (result.error) {
        console.log(result.error);
      }
      return result;
    } catch (error) {
      console.error("Error fetching configs:", error);
    }
  };

  const getScanners = async () => {
    try {
      const result = await dispatch(getScannersThunk());
      if (result.error) {
        console.log(result.error);
      }
      return result;
    } catch (error) {
      console.error("Error fetching scanners:", error);
    }
  };

  const getSchedules = async () => {
    try {
      const result = await dispatch(getSchedulesThunk());
      if (result.error) {
        console.log(result.error);
      }
      return result;
    } catch (error) {
      console.error("Error fetching schedules:", error);
    }
  };

  const fetchData = async () => {
    try {
      await getTasks();
      await getTargets();
      await getConfigs();
      await getScanners();
      await getSchedules();
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [dispatch]);

  const handleAddOrModifyTask = async (values: any) => {
    const { name, target_id, config_id, scanner_id, schedule_id } = values;

    if (currentTask) {
      // Modify existing task
      const result = await dispatch(
        modifyTaskThunk({
          taskId: currentTask.id,
          data: { name, target_id, config_id, scanner_id, schedule_id },
        })
      );
      if (result.error) {
        notification.error({
          message: "Failed to Modify Task",
          description:
            result.error.message ||
            "An error occurred while modifying the task.",
        });
      } else {
        notification.success({
          message: "Task Modified",
          description: "The task was modified successfully.",
        });
      }
    } else {
      // Create new task
      const result = await dispatch(
        createTaskThunk({
          name,
          target_id,
          config_id,
          scanner_id,
          schedule_id: schedule_id || null,
        })
      );
      if (result.error) {
        notification.error({
          message: "Failed to Create Task",
          description:
            result.error.message ||
            "An error occurred while creating the task.",
        });
      } else {
        notification.success({
          message: "Task Created",
          description: "The task was created successfully.",
        });
      }
    }
    setIsFormVisible(false);
    form.resetFields();
    setCurrentTask(null);
    getTargets();
  };

  const handleStartTask = async (id: string) => {
    try {
      const result = await dispatch(startTaskThunk(id));
      if (result.error) {
        notification.error({
          message: "Failed to Start Task",
          description:
            result.error.message ||
            "An error occurred while starting the task.",
        });
      } else {
        notification.success({
          message: "Task Started",
          description: "The task was started successfully.",
        });
      }
      await fetchData();
    } catch (error) {
      console.error("Error starting task:", error);
    }
  };

  const handleStopTask = async (id: string) => {
    try {
      const result = await dispatch(stopTaskThunk(id));
      if (result.error) {
        notification.error({
          message: "Failed to Stop Task",
          description:
            result.error.message ||
            "An error occurred while stopping the task.",
        });
      } else {
        notification.success({
          message: "Task Stopped",
          description: "The task was stopped successfully.",
        });
      }
      await fetchData();
    } catch (error) {
      console.error("Error stopping task:", error);
    }
  };

  const handleResumeTask = async (id: string) => {
    try {
      const result = await dispatch(resumeTaskThunk(id));
      if (result.error) {
        notification.error({
          message: "Failed to Resume Task",
          description:
            result.error.message ||
            "An error occurred while resuming the task.",
        });
      } else {
        notification.success({
          message: "Task Resumed",
          description: "The task was resumed successfully.",
        });
      }
      await fetchData();
    } catch (error) {
      console.error("Error resuming task:", error);
    }
  };

  const handleDeleteTask = async (id: string) => {
    try {
      const result = await dispatch(deleteTaskThunk(id));
      if (result.error) {
        notification.error({
          message: "Failed to Delete Task",
          description:
            result.error.message ||
            "An error occurred while deleting the task.",
        });
      } else {
        notification.success({
          message: "Task Deleted",
          description: "The task was deleted successfully.",
        });
        await fetchData();
      }
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  const modifyTask = (task: any) => {
    form.setFieldsValue({
      name: task.name,
    });
    setCurrentTask(task);
    setIsFormVisible(true);
  };

  // Function to view task details
  const viewTaskDetails = async (task: any) => {
    try {
      // Fetch complete task details
      const result = await dispatch(getTaskThunk(task.id));
      if (result.error) {
        console.error("Error fetching task details:", result.error);
        return;
      }

      // Update selectedTask with fetched task details
      const fetchedTask = result.payload; // Assuming the task data is returned in payload
      console.log(fetchedTask);

      setSelectedTask(fetchedTask);

      // Open the modal with the updated task details
      setIsDetailVisible(true);
    } catch (error) {
      console.error("Error fetching task details:", error);
    }
  };

  const handleBatchStart = async () => {
    for (const id of selectedRowKeys) {
      await handleStartTask(id);
      await new Promise((resolve) => setTimeout(resolve, 1000)); // 1-second delay
    }
    setSelectedRowKeys([]); // Clear selection
  };

  const handleBatchDelete = async () => {
    for (const id of selectedRowKeys) {
      await handleDeleteTask(id);
      await new Promise((resolve) => setTimeout(resolve, 1000)); // 1-second delay
    }
    setSelectedRowKeys([]); // Clear selection
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
    },
    {
      title: "Actions",
      key: "actions",
      render: (text, record) => (
        <Space size="middle">
          {/* Conditionally render the buttons based on the task's status */}
          {(record.status === "New" || record.status === "Done") && (
            <Button type="default" onClick={() => handleStartTask(record.id)}>
              <PlayCircleOutlined />
            </Button>
          )}
          {(record.status === "Running" ||
            record.status === "Requested" ||
            record.status === "Queued") && (
            <Button type="default" onClick={() => handleStopTask(record.id)}>
              <StopOutlined />
            </Button>
          )}
          {(record.status === "Stopped" || record.status === "Interrupted") && (
            <Button type="default" onClick={() => handleResumeTask(record.id)}>
              <PauseCircleOutlined />
            </Button>
          )}
          <Button type="primary" onClick={() => modifyTask(record)}>
            <EditOutlined />
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <ConfigProvider componentSize="small">
      <Card
        title="Tasks"
        extra={
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsFormVisible(true)}
            >
              Add Task
            </Button>
            <Button
              type="default"
              icon={<PlayCircleOutlined/>}
              onClick={handleBatchStart}
              disabled={selectedRowKeys.length === 0}
            >
              Start
            </Button>
            <Button
              danger
              icon={<DeleteOutlined/>}
              onClick={handleBatchDelete}
              disabled={selectedRowKeys.length === 0}
            >
              Delete
            </Button>
          </Space>
        }
      >
        <Modal
          title={currentTask ? "Edit Task" : "Add Task"}
          open={isFormVisible}
          onCancel={() => {
            setIsFormVisible(false);
            form.resetFields();
            setCurrentTask(null);
          }}
          footer={null}
        >
          <Form form={form} layout="vertical" onFinish={handleAddOrModifyTask}>
          <Form.Item
              name="name"
              label="Task Name"
              rules={[
                { required: true, message: "Please input the task name!" },
              ]}
            >
              <Input />
            </Form.Item>
            <Form.Item
                name="target_id"
                label="Target"
                rules={[
                    { required: true },
                  ]}
              >
                <Select placeholder="Select a target">
                  {(Array.isArray(targets) ? targets : []).map(target => (
                    <Select.Option key={target.id} value={target.id}>
                      {target.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                name="config_id"
                label="Scan type"
                rules={[
                    { required: true },
                  ]}
              >
                <Select placeholder="Select a scan type">
                  {(Array.isArray(configs) ? configs : []).map(config => (
                    <Select.Option key={config.config_id} value={config.config_id}>
                      {config.config_name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                name="scanner_id"
                label="Scanner"
                rules={[
                    { required: true },
                  ]}
              >
                <Select placeholder="Select scanner">
                  {(Array.isArray(scanners) ? scanners : []).map(scanner => (
                    <Select.Option key={scanner.id} value={scanner.id}>
                      {scanner.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                name="schedule_id"
                label="Schedule (Optional)"
              >
                <Select placeholder="Select schedule">
                  {(Array.isArray(schedules) ? schedules : []).map(schedule => (
                    <Select.Option key={schedule.id} value={schedule.id}>
                      {schedule.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            <Form.Item></Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit">
                {currentTask ? "Update" : "Submit"}
              </Button>
              <Button
                onClick={() => {
                  setIsFormVisible(false);
                  form.resetFields();
                  setCurrentTask(null);
                }}
                style={{ marginTop: 10 }}
              >
                Cancel
              </Button>
            </Form.Item>
          </Form>
        </Modal>

        {status === "loading" && <p>Loading...</p>}
        {status === "failed" && <p>Error: {error}</p>}
        {status === "succeeded" && (
          <Table
            rowSelection={{
              selectedRowKeys,
              onChange: setSelectedRowKeys,
            }}
            columns={columns}
            dataSource={tasks}
            rowKey="id"
            pagination={{ pageSize: 13}}
            onRow={(record) => ({
              onClick: () => viewTaskDetails(record),
            })}
          />
        )}
      </Card>

      <Modal
        title="Task Details"
        open={isDetailVisible}
        onCancel={() => setIsDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setIsDetailVisible(false)}>
            Close
          </Button>,
        ]}
      >
        {selectedTask && (
          <div>
            <p>
              <strong>ID:</strong> {selectedTask.id}
            </p>
            <p>
              <strong>Last Report ID:</strong> {selectedTask.last_report.id}
            </p>
            <p>
              <strong>Name:</strong> {selectedTask.name}
            </p>
            <p>
              <strong>Status:</strong> {selectedTask.status}
            </p>
            <p>
              <strong>Owner:</strong> {selectedTask.owner}
            </p>
            <p>
              <strong>Start Time:</strong> {selectedTask.last_report.scan_start}
            </p>
            <p>
              <strong>Finish Time:</strong> {selectedTask.last_report.scan_end}
            </p>
            <p>
              <strong>Comment:</strong> {selectedTask.comment}
            </p>
            {/* Add more fields if needed */}
          </div>
        )}
      </Modal>
    </ConfigProvider>
  );
};

export default Tasks;
