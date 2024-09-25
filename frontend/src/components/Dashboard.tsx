import React, { useEffect, useState } from "react";
import {
  Row,
  Col,
  Card,
  Statistic,
  Table,
  Button,
  notification,
  Spin,
  ConfigProvider,
} from "antd";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
} from "recharts"; 
import { useSelector, useDispatch } from "react-redux";
import {
  getReportsThunk,
  getTasksThunk,
  getReportThunk,
} from "../features/scannerSlice";
import ReportDetails from "./ReportDetails";

const Dashboard: React.FC = () => {
  const dispatch = useDispatch();

  const reports = useSelector((state: any) => state.scanner.reports);
  const tasks = useSelector((state: any) => state.scanner.tasks);

  const [loading, setLoading] = useState<boolean>(true);
  const [loadingChart, setLoadingChart] = useState<boolean>(true);
  const [tableData, setTableData] = useState<any[]>([]);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [detailsVisible, setDetailsVisible] = useState(false);

  const [metrics, setMetrics] = useState({
    totalScans: 0,
    criticalVulnerabilities: 0,
    openTasks: 0,
    resolvedIssues: 0,
  });

  const [vulnerabilitiesCount, setVulnerabilitiesCount] = useState([
    { severity: "Critical", count: 0 },
    { severity: "High", count: 0 },
    { severity: "Medium", count: 0 },
    { severity: "Log", count: 0 },
  ]);

  const [scanFrequencyData, setScanFrequencyData] = useState<any[]>([]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setLoadingChart(true);
      try {
        // Fetch reports and tasks sequentially and wait for both to complete
        const fetchedReports = await dispatch(getReportsThunk()).unwrap();
        const fetchedTasks = await dispatch(getTasksThunk()).unwrap();
  
        // Calculate total scans, open tasks, and resolved issues
        const totalScans = fetchedReports.length;
        const openTasks = fetchedTasks.filter((task: any) => task.status !== "Done").length;
        const resolvedIssues = fetchedTasks.filter((task: any) => task.status === "Done").length;
  
        // Initialize vulnerability counts
        const vulnerabilityCountTemp = [
          { severity: "Critical", count: 0 },
          { severity: "High", count: 0 },
          { severity: "Medium", count: 0 },
          { severity: "Log", count: 0 },
        ];
  
        // Process vulnerability data for each report
        for (const report of fetchedReports) {
          const result = await dispatch(getReportThunk(report.id)).unwrap();
          const { results } = result;
          results.forEach((vuln: any) => {
            if (vuln.severity >= 7.0) vulnerabilityCountTemp[0].count++;
            else if (vuln.severity >= 4.0) vulnerabilityCountTemp[1].count++;
            else if (vuln.severity >= 2.0) vulnerabilityCountTemp[2].count++;
            else vulnerabilityCountTemp[3].count++;
          });
        }
  
        setVulnerabilitiesCount(vulnerabilityCountTemp);
        const criticalVulnerabilities = vulnerabilityCountTemp[0].count;
  
        // Update the metrics state
        setMetrics({
          totalScans,
          criticalVulnerabilities,
          openTasks,
          resolvedIssues,
        });
  
        // Calculate scan frequency data
        const now = new Date();
        const oneWeekAgo = new Date(now);
        oneWeekAgo.setDate(now.getDate() - 7);
        const oneMonthAgo = new Date(now);
        oneMonthAgo.setMonth(now.getMonth() - 1);
        const oneYearAgo = new Date(now);
        oneYearAgo.setFullYear(now.getFullYear() - 1);
  
        const scanFrequency = {
          lastWeek: 0,
          lastMonth: 0,
          lastYear: 0,
        };
  
        fetchedReports.forEach((report: any) => {
          const creationDate = new Date(report.creation_time);
          if (creationDate >= oneWeekAgo) scanFrequency.lastWeek++;
          if (creationDate >= oneMonthAgo) scanFrequency.lastMonth++;
          if (creationDate >= oneYearAgo) scanFrequency.lastYear++;
        });
  
        setScanFrequencyData([
          { timeFrame: "Last Week", scans: scanFrequency.lastWeek },
          { timeFrame: "Last Month", scans: scanFrequency.lastMonth },
          { timeFrame: "Last Year", scans: scanFrequency.lastYear },
        ]);
  
        // Format task data for the table
        const formattedTasks = fetchedTasks.map((task: any) => {
          const relatedReport = fetchedReports.find((report: any) => report.task_id === task.id);
          return {
            id: task.id,
            task: task.name,
            date: relatedReport?.creation_time || "N/A",
            status: task.status,
          };
        });
  
        setTableData(formattedTasks);
  
      } catch (error) {
        notification.error({
          message: "Error Fetching Dashboard Data",
          description: error.message || "Something went wrong!",
        });
      } finally {
        setLoading(false);
        setLoadingChart(false);
      }
    };
  
    fetchDashboardData();
  }, [dispatch]);
  

  const handleViewReport = async (taskId: string) => {
    const relatedReport = reports.find(
      (report: any) => report.task_id === taskId
    );
    if (relatedReport) {
      const result = await dispatch(getReportThunk(relatedReport.id)).unwrap();
      setSelectedReport({
        id: relatedReport.id,
        creation_time: relatedReport.creation_time,
        task_name: relatedReport.task_name,
        highest_severity: relatedReport.highest_severity,
        results: result.results,
        vulns_count: result.vulns_count,
      });
      setDetailsVisible(true);
    } else {
      notification.warning({
        message: "No Report Found",
        description: "This task has no associated report.",
      });
    }
  };

  const closeReportDetails = () => {
    setSelectedReport(null);
    setDetailsVisible(false);
  };

  const columns = [
    { title: "Task", dataIndex: "task", key: "task" },
    { title: "Date", dataIndex: "date", key: "date" },
    { title: "Status", dataIndex: "status", key: "status" },
    {
      title: "Action",
      key: "action",
      render: (text: string, record: any) => (
        <Button type="link" onClick={() => handleViewReport(record.id)}>
          View Report
        </Button>
      ),
    },
  ];


  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col span={6}>
          <Card>
            <Statistic title="Total Scans" value={metrics.totalScans} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Critical Vulnerabilities"
              value={metrics.criticalVulnerabilities}
              valueStyle={{ color: "#cf1322" }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Open Tasks" value={metrics.openTasks} />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic title="Completed Tasks" value={metrics.resolvedIssues} />
          </Card>
        </Col>
      </Row>

      <div style={{ marginTop: "30px" }}>
        <ConfigProvider componentSize="small">
        <Card title="Recent Activity">
          <Table
            columns={columns}
            dataSource={tableData}
            loading={loading}
            rowKey="id"
            pagination={{ pageSize: 5 }}
          />
        </Card>
        </ConfigProvider>
      </div>

      <div style={{ marginTop: "30px", display: "flex", justifyContent: "space-between" }}>
        <Card title="Vulnerabilities Count by Severity" style={{ flex: 1, marginRight: "20px" }}>
          {loadingChart ? (
            <Spin />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={vulnerabilitiesCount}
                  dataKey="count"
                  nameKey="severity"
                  cx="50%"
                  cy="50%"
                  outerRadius="80%"
                  fill="#8884d8"
                  label
                >
                  <Cell fill="#cf1322" /> {/* Critical */}
                  <Cell fill="#faad14" /> {/* High */}
                  <Cell fill="#3f8600" /> {/* Medium */}
                  <Cell fill="#808080" /> {/* Log */}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
        </Card>

        <Card title="Scan Frequency" style={{ flex: 1 }}>
          {loadingChart ? (
            <Spin />
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={scanFrequencyData}>
                <XAxis dataKey="timeFrame" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="scans" fill="#4caf50" />
                <Tooltip />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>
      </div>

      {selectedReport && (
          <ReportDetails
            report={selectedReport}
            visible={detailsVisible}
            onClose={closeReportDetails}
          />
        )}
    </div>
  );
};

export default Dashboard;
