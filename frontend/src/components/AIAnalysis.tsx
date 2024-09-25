import React, { useEffect, useState } from "react";
import { Table, notification, Spin, Typography } from "antd";
import { useDispatch, useSelector } from "react-redux";
import { analyzeReportThunk } from "../features/scannerSlice";

interface AIAnalysisProps {
  report: any; // The selected report passed from the parent component
}

const { Title, Paragraph, Link } = Typography;

const AIAnalysis: React.FC<AIAnalysisProps> = ({ report }) => {
  const dispatch = useDispatch();
  const analysisResults = useSelector((state) => state.scanner.analysisResults);
  const error = useSelector((state) => state.scanner.error);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (report) {
      setLoading(true);
      dispatch(analyzeReportThunk(report)).finally(() => {
        setLoading(false);
      });
    }
  }, [dispatch, report]);

  useEffect(() => {
    if (error) {
      notification.error({
        message: "Analysis Error",
        description: error,
      });
    }
  }, [error]);

  const columns = [
    {
      title: "CVE Number",
      dataIndex: "cve",
      key: "cve",
    },
    {
      title: "Analysis",
      dataIndex: "answer",
      key: "answer",
      render: (text: string) => (
        <div>
          {text.split('\n').map((line, index) => {
            const isLink = line.startsWith('http');
            return (
              <Paragraph key={index}>
                {isLink ? <Link href={line} target="_blank">{line}</Link> : line}
              </Paragraph>
            );
          })}
        </div>
      ),
    },
  ];

  return (
    <div style={{ marginTop: 20 }}>
      <Title level={4}>AI Analysis Results</Title>
      {loading ? (
        <Spin size="large" />
      ) : (
        <Table
          columns={columns}
          dataSource={analysisResults}
          rowKey="cve"
          pagination={false}
        />
      )}
    </div>
  );
};

export default AIAnalysis;
