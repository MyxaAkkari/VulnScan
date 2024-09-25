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
  DatePicker,
} from "antd";
import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { RootState } from "../main";
import {
  getSchedulesThunk,
  createScheduleThunk,
  modifyScheduleThunk,
  deleteScheduleThunk,
} from "../features/scannerSlice";
import dayjs from "dayjs";

const Schedules = () => {
  const dispatch = useDispatch();
  const [form] = Form.useForm();
  const { schedules, status, error } = useSelector(
    (state: RootState) => state.scanner
  );
  const [isFormVisible, setIsFormVisible] = useState(false);
  const [currentSchedule, setCurrentSchedule] = useState<any>(null);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]); // Selected row keys
  const delay = (ms: number) =>
    new Promise((resolve) => setTimeout(resolve, ms));

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

  useEffect(() => {
    getSchedules();
  }, [dispatch]);

  const handleAddOrModifySchedule = async (values: any) => {
    const { name, dtstart, timezone, comment, frequency, interval, count } =
      values;
    // Format the dtstart value to the correct format expected by the backend
    const formattedDtstart = formatDate(dtstart);

    if (currentSchedule) {
      // Modify existing schedule
      const result = await dispatch(
        modifyScheduleThunk({
          schedule_id: currentSchedule.id,
          name,
          dtstart: formattedDtstart,
          timezone,
          comment,
          frequency,
          interval,
          count,
        })
      );
      if (result.error) {
        notification.error({
          message: "Failed to Modify Schedule",
          description:
            result.error.message ||
            "An error occurred while modifying the schedule.",
        });
      } else {
        notification.success({
          message: "Schedule Modified",
          description: "The schedule was modified successfully.",
        });
      }
    } else {
      // Create new schedule
      const result = await dispatch(
        createScheduleThunk({
          name,
          dtstart: formattedDtstart,
          timezone,
          comment,
          frequency,
          interval,
          count,
        })
      );
      if (result.error) {
        notification.error({
          message: "Failed to Create Schedule",
          description:
            result.error.message ||
            "An error occurred while creating the schedule.",
        });
      } else {
        notification.success({
          message: "Schedule Created",
          description: "The schedule was created successfully.",
        });
      }
    }
    setIsFormVisible(false);
    form.resetFields();
    setCurrentSchedule(null);
    getSchedules();
  };

  // Utility function to format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toISOString().split(".")[0]; // Format to 'YYYY-MM-DDTHH:MM:SS'
  };

  const modifySchedule = (schedule: any) => {
    form.setFieldsValue({
      name: schedule.name,
      dtstart: dayjs(schedule.dtstart),
      timezone: schedule.timezone,
      comment: schedule.comment,
      frequency: schedule.frequency,
      interval: schedule.interval,
      count: schedule.count,
    });
    setCurrentSchedule(schedule);
    setIsFormVisible(true);
  };

  const handleDeleteSchedule = async (id: string) => {
    try {
      const result = await dispatch(deleteScheduleThunk(id));
      if (result.error) {
        notification.error({
          message: "Failed to Delete Schedule",
          description:
            result.error.message ||
            "An error occurred while deleting the schedule.",
        });
      } else {
        notification.success({
          message: "Schedule Deleted",
          description: "The schedule was deleted successfully.",
        });
        await delay(1000);
      }
      setSelectedRowKeys([]);
      await getSchedules();
    } catch (error) {
      console.error("Error deleting schedule:", error);
    }
  };

  // Batch delete selected schedules
  const handleBatchDelete = async () => {
    for (const id of selectedRowKeys) {
      await handleDeleteSchedule(id);
    }
    setSelectedRowKeys([]);
  };

  // Open modal with the first selected schedule's details for batch modification
  const handleBatchModify = () => {
    if (selectedRowKeys.length > 0) {
      const firstSelected = schedules.find(
        (schedule: any) => schedule.id === selectedRowKeys[0]
      );
      if (firstSelected) {
        modifySchedule(firstSelected);
      }
    }
  };

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "Frequency",
      dataIndex: "period",
      key: "period",
      render: (text: string) => <span>{text ? text : "One-Time"}</span>,
    },
    {
      title: "Comment",
      dataIndex: "comment",
      key: "comment",
    },
  ];

  return (
    <ConfigProvider componentSize="small">
      <Card
        title="Schedules"
        extra={
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsFormVisible(true)}
            >
              Add Schedule
            </Button>
            <Button
            icon={<EditOutlined/>}
              onClick={handleBatchModify}
              disabled={selectedRowKeys.length === 0}
            >
              Modify
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
          title={currentSchedule ? "Edit Schedule" : "Add Schedule"}
          open={isFormVisible}
          onCancel={() => {
            setIsFormVisible(false);
            form.resetFields();
            setCurrentSchedule(null);
          }}
          footer={null}
        >
          <Form
            form={form}
            layout="vertical"
            onFinish={handleAddOrModifySchedule}
          >
            <Form.Item
              name="name"
              label="Schedule Name"
              rules={[
                { required: true, message: "Please input the schedule name!" },
              ]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="dtstart"
              label="Start Date and Time"
              rules={[
                { required: true, message: "Please select date and time!" },
              ]}
            >
              <DatePicker showTime />
            </Form.Item>
            <Form.Item
              name="timezone"
              label="Timezone"
              rules={[{ required: true, message: "Please select timezone!" }]}
            >
              <Select>
                <Select.Option value="UTC">UTC</Select.Option>
                {/* Add more timezones as needed */}
              </Select>
            </Form.Item>
            <Form.Item name="comment" label="Comment">
              <Input.TextArea />
            </Form.Item>
            <Form.Item
              name="frequency"
              label="Frequency"
              rules={[{ required: true, message: "Please select frequency!" }]}
            >
              <Select placeholder="Select frequency">
                <Select.Option value="daily">Daily</Select.Option>
                <Select.Option value="weekly">Weekly</Select.Option>
                <Select.Option value="monthly">Monthly</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item
              name="interval"
              label="Interval"
              rules={[{ required: true, message: "Please input interval!" }]}
            >
              <Input type="number" min={1} />
            </Form.Item>
            <Form.Item
              name="count"
              label="Occurrences"
              rules={[{ required: true, message: "Please input occurrences!" }]}
            >
              <Input type="number" min={1} />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit">
                {currentSchedule ? "Update" : "Submit"}
              </Button>
              <Button
                onClick={() => {
                  setIsFormVisible(false);
                  form.resetFields();
                  setCurrentSchedule(null);
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
            rowKey="id"
            rowSelection={{
              selectedRowKeys,
              onChange: setSelectedRowKeys,
            }}
            columns={columns}
            dataSource={schedules}
            pagination={{ pageSize: 13 }}
          />
        )}
      </Card>
    </ConfigProvider>
  );
};

export default Schedules;
