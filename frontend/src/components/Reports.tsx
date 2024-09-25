import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  Card,
  Table,
  Button,
  Space,
  notification,
  Modal,
  Select,
  ConfigProvider,
} from "antd";
import {
  getReportsThunk,
  getReportThunk,
  deleteReportThunk,
  exportReportThunk,
} from "../features/scannerSlice";
import { RootState } from "../main";
import ReportDetails from "./ReportDetails";
import { DeleteOutlined, DownloadOutlined } from "@ant-design/icons";

const { Option } = Select;

const Reports: React.FC = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [detailsVisible, setDetailsVisible] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);
  const [exportVisible, setExportVisible] = useState(false);
  const [exportFormat, setExportFormat] = useState<string | null>(null);
  const reports = useSelector((state: RootState) => state.scanner.reports);

  const fetchReportsAndTasks = async () => {
    setLoading(true);
    try {
      const result = await dispatch(getReportsThunk());
      if (result.error) {
        throw new Error("Failed to fetch reports");
      }
    } catch (error) {
      notification.error({
        message: "Error Fetching Reports",
        description: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReportsAndTasks();
  }, [dispatch]);

  const handleViewDetails = async (reportId: string) => {
    const result = await dispatch(getReportThunk(reportId));
    if (result.error) {
      notification.error({
        message: "Failed to Fetch Report Details",
        description:
          result.error.message ||
          "An error occurred while fetching report details.",
      });
    } else {
      const selected = reports.find((report: any) => report.id === reportId);
      if (selected) {
        setSelectedReport({
          id: reportId,
          creation_time: selected.creation_time,
          task_name: selected.task_name,
          highest_severity: selected.highest_severity,
          results: result.payload.results,
          vulns_count: result.payload.vulns_count,
        });
        setDetailsVisible(true);
      }
    }
  };

  const handleDeleteReports = async () => {
    for (const reportId of selectedRowKeys) {
      const result = await dispatch(deleteReportThunk(reportId));
      if (result.error) {
        notification.error({
          message: "Failed to Delete Report",
          description:
            result.error.message ||
            "An error occurred while deleting the report.",
        });
      } else {
        notification.success({
          message: "Report Deleted",
          description: "Report has been successfully deleted.",
        });
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    setSelectedRowKeys([]);
    fetchReportsAndTasks();
  };

  const handleDownloadReports = async () => {
    if (!exportFormat) {
      notification.warning({ message: "Please select a format!" });
      return;
    }

    for (const reportId of selectedRowKeys) {
      const result = await dispatch(
        exportReportThunk({ reportId, format: exportFormat })
      );
      if (result.error) {
        notification.error({
          message: "Export Failed",
          description:
            result.error.message ||
            "An error occurred while exporting the report.",
        });
      } else {
        const { data, headers } = result.payload;
        const blob = new Blob([data], { type: headers["content-type"] });
        const downloadUrl = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = downloadUrl;
        link.setAttribute("download", `report_${reportId}.${exportFormat}`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        URL.revokeObjectURL(downloadUrl);
        notification.success({
          message: "Export Successful",
          description: `Report ${reportId} exported successfully.`,
        });
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    setSelectedRowKeys([]);
    setExportVisible(false);
  };

  const closeReportDetails = () => {
    setSelectedReport(null);
    setDetailsVisible(false);
  };

  const columns = [
    {
      title: "Date",
      dataIndex: "creation_time",
      key: "creation_time",
      render: (text: string) => text || "N/A",
      sorter: (a: any, b: any) =>
        new Date(a.creation_time).getTime() -
        new Date(b.creation_time).getTime(),
    },
    {
      title: "Task Name",
      dataIndex: "task_name",
      key: "task",
      render: (text: string) => text || "N/A",
      sorter: (a: any, b: any) => a.task_name.localeCompare(b.task_name),
    },
    {
      title: "Severity",
      dataIndex: "highest_severity",
      key: "severity",
      render: (text: string) => text || "Log",
      sorter: (a: any, b: any) => a.highest_severity - b.highest_severity,
    },
  ];

  return (
    <ConfigProvider componentSize="small">
      <Card
        title="Reports"
        loading={loading}
        
        extra={
          <Space>
            <Button
              type="primary"
              danger
              icon={<DeleteOutlined/>}
              onClick={handleDeleteReports}
              disabled={selectedRowKeys.length === 0}
            >
              Delete
            </Button>
            <Button
              type="default"
              icon={<DownloadOutlined/>}
              onClick={() => setExportVisible(true)}
              disabled={selectedRowKeys.length === 0}
            >
              Download
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={reports}
          rowKey="id"
          pagination={{ pageSize: 13 }}
          rowSelection={{
            selectedRowKeys,
            onChange: (selectedKeys: string[]) =>
              setSelectedRowKeys(selectedKeys),
          }}
          onRow={(record) => ({
            onClick: (event) => {
              // Prevent opening details when clicking the checkbox
              if ((event.target as HTMLElement).tagName !== "INPUT") {
                handleViewDetails(record.id);
              }
            },
          })}
        />

        {selectedReport && (
          <ReportDetails
            report={selectedReport}
            visible={detailsVisible}
            onClose={closeReportDetails}
          />
        )}

        <Modal
          title="Select Export Format"
          open={exportVisible}
          onCancel={() => setExportVisible(false)}
          onOk={handleDownloadReports}
        >
          <Select
            placeholder="Select format"
            onChange={(value) => setExportFormat(value)}
            style={{ width: "100%" }}
          >
            <Option value="csv">CSV</Option>
            <Option value="xlsx">XLSX</Option>
            <Option value="pdf">PDF</Option>
          </Select>
        </Modal>
      </Card>
    </ConfigProvider>
  );
};

export default Reports;
