// scannerAPI.ts
import axios from 'axios';

// Base URL for API
const MY_SERVER = "http://192.168.14.109:5000/scanner";

// Function to set up axios interceptors
const setupAxiosInterceptors = () => {
  axios.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers["Authorization"] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
};

// Call this function in your app initialization
setupAxiosInterceptors();

// API Calls
export const authenticate = () => axios.post(MY_SERVER + '/authenticate');
export const getRoles = () => axios.get(MY_SERVER + '/get_roles');
export const getUsers = () => axios.get(MY_SERVER + '/get_users');
export const getUser = (userId: string) => axios.get(MY_SERVER + `/get_user/${userId}`);
export const createUser = (userData: any) => axios.post(MY_SERVER + '/create_user', userData);
export const modifyUser = (userId: string, userData: any) => axios.put(MY_SERVER + `/modify_user/${userId}`, userData);
export const deleteUser = (userId: string) => axios.delete(MY_SERVER + `/delete_user/${userId}`);
export const cloneUser = (userId: string, userData: any) => axios.post(MY_SERVER + `/clone_user/${userId}`, userData);
export const getScanners = () => axios.get(MY_SERVER + '/get_scanners');
export const getConfigs = () => axios.get(MY_SERVER + '/get_configs');
export const getPortlists = () => axios.get(MY_SERVER + '/get_portlists');
export const getHosts = () => axios.get(MY_SERVER + '/get_hosts');
export const deleteHost = (hostId: string) => axios.delete(MY_SERVER + `/delete_host/${hostId}`);
export const convertHostsToTargets = (data: any) => axios.post(MY_SERVER + '/convert_hosts_to_targets', data);
export const getTargets = () => axios.get(MY_SERVER + '/get_targets');
export const createTarget = (data: any) => axios.post(MY_SERVER + '/create_target', data);
export const deleteTarget = (targetId: string) => axios.delete(MY_SERVER + `/delete_target/${targetId}`);
export const modifyTarget = (targetId: string, data: any) => axios.post(MY_SERVER + `/modify_target/${targetId}`, data);
export const createTask = (data: any) => axios.post(MY_SERVER + '/create_task', data);
export const startTask = (taskId: string) => axios.post(MY_SERVER + `/start_task/${taskId}`);
export const stopTask = (taskId: string) => axios.post(MY_SERVER + `/stop_task/${taskId}`);
export const resumeTask = (taskId: string) => axios.post(MY_SERVER + `/resume_task/${taskId}`);
export const deleteTask = (taskId: string) => axios.delete(MY_SERVER + `/delete_task/${taskId}`);
export const modifyTask = (taskId: string, data: any) => axios.put(MY_SERVER + `/modify_task/${taskId}`, data);
export const getTask = (taskId: string) => axios.get(MY_SERVER + `/get_task/${taskId}`);
export const getTaskStatus = (taskId: string) => axios.get(MY_SERVER + `/get_task_status/${taskId}`);
export const getTasks = () => axios.get(MY_SERVER + '/get_tasks');
export const getResults = (taskId: string) => axios.post(MY_SERVER + '/get_results', { task_id: taskId });
export const getReports = () => axios.get(MY_SERVER + '/get_reports_with_tasks');
export const getReport = (reportId: string) => axios.get(MY_SERVER + `/get_report/${reportId}`);
export const deleteReport = (reportId: string) => axios.delete(MY_SERVER + `/delete_report/${reportId}`);
export const exportReport = (reportId: string, format: string) => axios.get(MY_SERVER + `/export_report/${reportId}/${format}`, { responseType: 'blob' });
export const getSchedules = () => axios.get(MY_SERVER + '/get_schedules');
export const createSchedule = (data: any) => axios.post(MY_SERVER + '/create_schedule', data);
export const modifySchedule = (data: any) => axios.post(MY_SERVER + '/modify_schedule', data);
export const deleteSchedule = (scheduleId: string) => axios.delete(MY_SERVER + `/delete_schedule/${scheduleId}`);
export const createAlert = (data: any) => axios.post(MY_SERVER + '/create_alert', data);
export const getAlerts = () => axios.get(MY_SERVER + '/get_alerts');
export const analyze_report = (data: any) => axios.post('http://192.168.14.109:5000/ai/analyze_cve', data);
