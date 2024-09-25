import React, { useState } from "react";
import {
  Modal,
  Table,
  Descriptions,
  Typography,
  Button,
  Select,
  notification,
  Space,
  ConfigProvider,
} from "antd";
import { AntDesignOutlined, DownloadOutlined } from "@ant-design/icons";
import { useDispatch } from "react-redux";
import { exportReportThunk, clearAnalysisResults } from "../features/scannerSlice";
import AIAnalysis from "./AIAnalysis";
import { createStyles } from "antd-style";

const useStyle = createStyles(({ prefixCls, css }) => ({
  linearGradientButton: css`
    &.${prefixCls}-btn-primary:not([disabled]):not(.${prefixCls}-btn-dangerous) {
      border-width: 0;

      > span {
        position: relative;
      }

      &::before {
        content: '';
        background: linear-gradient(135deg, #6253e1, #04befe);
        position: absolute;
        inset: 0;
        opacity: 1;
        transition: all 0.3s;
        border-radius: inherit;
      }

      &:hover::before {
        opacity: 0;
      }
    }
  `,
}));

interface ReportDetailsProps {
  visible: boolean;
  onClose: () => void;
  report: any;
}

const ReportDetails: React.FC<ReportDetailsProps> = ({
  visible,
  onClose,
  report,
}) => {
  if (!report) {
    return <div>No report available</div>;
}

  const dispatch = useDispatch();
  const [exportVisible, setExportVisible] = useState(false);
  const [exportFormat, setExportFormat] = useState<string | null>(null);
  const [showAIAnalysis, setShowAIAnalysis] = useState(false);
  const { styles } = useStyle(); // Get the styles for the gradient button

  const handleClose = () => {
    dispatch(clearAnalysisResults());
    onClose();
  };

  const handleExport = async () => {
    if (!exportFormat) {
      notification.warning({ message: "Please select a format!" });
      return;
    }

    const result = await dispatch(
      exportReportThunk({ reportId: report.id, format: exportFormat })
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
      link.setAttribute("download", `report.${exportFormat}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(downloadUrl);

      notification.success({
        message: "Export Successful",
        description: `Report exported in ${exportFormat.toUpperCase()} format.`,
      });
    }
    setExportVisible(false);
  };

  const columns = [
    {
      title: "CVE Number",
      dataIndex: "cve_numbers",
      key: "cve_numbers",
      render: (cve_numbers: string[]) => cve_numbers.join(", ") || "N/A",
    },
    {
      title: "Port",
      dataIndex: "port",
      key: "port",
      render: (text: string) => text || "N/A",
    },
    {
      title: "Severity",
      dataIndex: "severity",
      key: "severity",
      render: (text: string) => text || "Log",
      sorter: (a: any, b: any) => a.severity - b.severity,
      sortDirections: ["ascend", "descend"],
      defaultSortOrder: "descend",
    },
    {
      title: "Threat",
      dataIndex: "threat",
      key: "threat",
      render: (text: string) => text || "N/A",
    },
    {
      title: "Description",
      dataIndex: "description",
      key: "description",
      render: (text: string) => text || "N/A",
    },
  ];

  return (
    <Modal
      open={visible}
      title={`Report Details - ${report.task_name} | ${report.creation_time}`}
      onCancel={handleClose}
      width="80%"
      footer
    >
      <Descriptions bordered>
        <Descriptions.Item label="Report Date">
          {report.creation_time || "N/A"}
        </Descriptions.Item>
        <Descriptions.Item label="Task Name">
          {report.task_name || "N/A"}
        </Descriptions.Item>
        <Descriptions.Item label="Highest Severity">
          {report.highest_severity || "N/A"}
        </Descriptions.Item>
        <Descriptions.Item label="Host IP">
          {report.results.length > 0 ? report.results[0].host : "N/A"}
        </Descriptions.Item>
        <Descriptions.Item label="Total Vulnerabilities">
          {report.vulns_count || "N/A"}
        </Descriptions.Item>
      </Descriptions>
      <Space style={{marginTop: 16}}><Button
          type="primary"
          icon={<DownloadOutlined />}
          onClick={() => setExportVisible(true)}
        >
          Download Report
        </Button></Space>
      <Typography.Title level={4} style={{ marginTop: 16 }}>
        Vulnerability Details
      </Typography.Title>
      <Table
        columns={columns}
        dataSource={report.results}
        rowKey="id"
        pagination={{ pageSize: 5 }}
      />

      {/* Gradient AI Analysis Button */}
      <ConfigProvider
        button={{
          className: styles.linearGradientButton,
        }}
      >
        <Space style={{ marginTop: 16 }}>
          <Button
            type="primary"
            size="large"
            onClick={() => setShowAIAnalysis(true)}
            icon={<AntDesignOutlined />}
          >
            AI Analysis
          </Button>
        </Space>
      </ConfigProvider>

      {/* Conditionally render AIAnalysis component */}
      {showAIAnalysis && <AIAnalysis report={report} />}

      {/* Export Format Selection Modal */}
      <Modal
        title="Select Export Format"
        open={exportVisible}
        onCancel={() => setExportVisible(false)}
        onOk={handleExport}
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
    </Modal>
  );
};

export default ReportDetails;
