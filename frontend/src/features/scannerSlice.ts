// scannerSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import {
  authenticate,
  getRoles,
  getUsers,
  getUser,
  createUser,
  modifyUser,
  deleteUser,
  cloneUser,
  getScanners,
  getConfigs,
  getPortlists,
  getHosts,
  deleteHost,
  convertHostsToTargets,
  getTargets,
  createTarget,
  deleteTarget,
  modifyTarget,
  createTask,
  startTask,
  deleteTask,
  modifyTask,
  getTask,
  getTaskStatus,
  getTasks,
  getResults,
  getReports,
  getReport,
  deleteReport,
  exportReport,
  getSchedules,
  createSchedule,
  modifySchedule,
  deleteSchedule,
  createAlert,
  getAlerts,
  stopTask,
  resumeTask,
  analyze_report
} from './scannerAPI';

// Define the types for state
interface ScannerState {
  roles: any[];
  users: any[];
  user: any;
  scanners: any[];
  configs: any[];
  portlists: any[];
  hosts: any[];
  targets: any[];
  tasks: any[];
  reports: any[];
  selectedReport: any; 
  schedules: any[];
  alerts: any[];
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  analysisResults: any[]
  error: string | null;
  theme : boolean
  isCollapsed: boolean
}

// Initial state
const initialState: ScannerState = {
  roles: [],
  users: [],
  user: null,
  scanners: [],
  configs: [],
  portlists: [],
  hosts: [],
  targets: [],
  tasks: [],
  reports: [],
  selectedReport: null,
  schedules: [],
  alerts: [],
  analysisResults: [],
  status: 'idle',
  error: null,
  theme : true,
  isCollapsed: false,
};

// Thunks for async actions
export const authenticateThunk = createAsyncThunk('scanner/authenticate', async () => {
  const response = await authenticate();
  return response.data;
});

export const getRolesThunk = createAsyncThunk('scanner/getRoles', async () => {
  const response = await getRoles();
  return response.data;
});

export const getUsersThunk = createAsyncThunk('scanner/getUsers', async () => {
  const response = await getUsers();
  return response.data;
});

export const getUserThunk = createAsyncThunk('scanner/getUser', async (userId: string) => {
  const response = await getUser(userId);
  return response.data;
});

export const createUserThunk = createAsyncThunk('scanner/createUser', async (userData: any) => {
  const response = await createUser(userData);
  return response.data;
});

export const modifyUserThunk = createAsyncThunk('scanner/modifyUser', async ({ userId, userData }: { userId: string, userData: any }) => {
  const response = await modifyUser(userId, userData);
  return response.data;
});

export const deleteUserThunk = createAsyncThunk('scanner/deleteUser', async (userId: string) => {
  await deleteUser(userId);
  return userId;
});

export const cloneUserThunk = createAsyncThunk('scanner/cloneUser', async ({ userId, userData }: { userId: string, userData: any }) => {
  const response = await cloneUser(userId, userData);
  return response.data;
});

export const getScannersThunk = createAsyncThunk('scanner/getScanners', async () => {
  const response = await getScanners();
  return response.data;
});

export const getConfigsThunk = createAsyncThunk('scanner/getConfigs', async () => {
  const response = await getConfigs();
  return response.data;
});

export const getPortlistsThunk = createAsyncThunk('scanner/getPortlists', async () => {
  const response = await getPortlists();
  return response.data.portlists;
});

export const getHostsThunk = createAsyncThunk('scanner/getHosts', async () => {
  const response = await getHosts();
  return response.data.hosts;
});

export const deleteHostThunk = createAsyncThunk('scanner/deleteHost', async (hostId: string) => {
    await deleteHost(hostId);
    return hostId;
  });

export const convertHostsToTargetsThunk = createAsyncThunk('scanner/convertHostsToTargets', async (data: any) => {
  const response = await convertHostsToTargets(data);
  return response.data;
});

export const getTargetsThunk = createAsyncThunk('scanner/getTargets', async () => {
  const response = await getTargets();  
  return response.data;
});

export const createTargetThunk = createAsyncThunk('scanner/createTarget', async (data: any) => {
  const response = await createTarget(data);
  return response.data;
});

export const deleteTargetThunk = createAsyncThunk('scanner/deleteTarget', async (targetId: string) => {
  await deleteTarget(targetId);
  return targetId;
});

export const modifyTargetThunk = createAsyncThunk('scanner/modifyTarget', async ({ targetId, data }: { targetId: string, data: any }) => {
  const response = await modifyTarget(targetId, data);
  return response.data;
});

export const createTaskThunk = createAsyncThunk('scanner/createTask', async (data: any) => {
  const response = await createTask(data);
  return response.data;
});

export const startTaskThunk = createAsyncThunk('scanner/startTask', async (taskId: string) => {
  const response = await startTask(taskId);
  return response.data;
});

export const stopTaskThunk = createAsyncThunk('scanner/stopTask', async (taskId: string) => {
    const response = await stopTask(taskId);
    return response.data;
  });

  export const resumeTaskThunk = createAsyncThunk('scanner/resumeTask', async (taskId: string) => {
    const response = await resumeTask(taskId);
    return response.data;
  });

export const deleteTaskThunk = createAsyncThunk('scanner/deleteTask', async (taskId: string) => {
  await deleteTask(taskId);
  return taskId;
});

export const modifyTaskThunk = createAsyncThunk('scanner/modifyTask', async ({ taskId, data }: { taskId: string, data: any }) => {
  const response = await modifyTask(taskId, data);
  return response.data;
});

export const getTaskThunk = createAsyncThunk('scanner/getTask', async (taskId: string) => {
  const response = await getTask(taskId);
  return response.data;
});

export const getTaskStatusThunk = createAsyncThunk('scanner/getTaskStatus', async (taskId: string) => {
  const response = await getTaskStatus(taskId);
  return response.data;
});

export const getTasksThunk = createAsyncThunk('scanner/getTasks', async () => {
  const response = await getTasks();
  return response.data.tasks;
});

export const getResultsThunk = createAsyncThunk('scanner/getResults', async (taskId: string) => {
  const response = await getResults(taskId);
  return response.data;
});

export const getReportsThunk = createAsyncThunk('scanner/getReports', async () => {
  const response = await getReports();
  return response.data.reports;
});

export const getReportThunk = createAsyncThunk('scanner/getReport', async (reportId: string) => {
  const response = await getReport(reportId);
  return response.data;
});

export const deleteReportThunk = createAsyncThunk('scanner/deleteReport', async (reportId: string) => {
  await deleteReport(reportId);
  return reportId;
});

export const exportReportThunk = createAsyncThunk('scanner/exportReport', async ({ reportId, format }: { reportId: string, format: string }) => {
  const response = await exportReport(reportId, format);
  return response;
});

export const getSchedulesThunk = createAsyncThunk('scanner/getSchedules', async () => {
  const response = await getSchedules();
  return response.data.schedules;
});

export const createScheduleThunk = createAsyncThunk('scanner/createSchedule', async (data: any) => {
  const response = await createSchedule(data);
  return response.data;
});

export const modifyScheduleThunk = createAsyncThunk('scanner/modifySchedule', async (data: any) => {
  const response = await modifySchedule(data);
  return response.data;
});

export const deleteScheduleThunk = createAsyncThunk('scanner/deleteSchedule', async (scheduleId: string) => {
  await deleteSchedule(scheduleId);
  return scheduleId;
});

export const createAlertThunk = createAsyncThunk('scanner/createAlert', async (data: any) => {
  const response = await createAlert(data);
  return response.data;
});

export const getAlertsThunk = createAsyncThunk('scanner/getAlerts', async () => {
  const response = await getAlerts();
  return response.data;
});

export const analyzeReportThunk = createAsyncThunk('scanner/analyzeReport', async (data: any) => {
    const response = await analyze_report(data);
    return response.data
});

// Create slice
const scannerSlice = createSlice({
  name: 'scanner',
  initialState,
  reducers: {
    clearAnalysisResults: (state) => {
        state.analysisResults = [];
        state.error = null;
      },
      setTheme: (state) => {
        state.theme = !state.theme;
      }, setSidebarCollapsed: (state, action) => {
        state.isCollapsed = action.payload; 
      },
  
  },
  extraReducers: (builder) => {
    builder
      .addCase(authenticateThunk.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(authenticateThunk.fulfilled, (state) => {
        state.status = 'succeeded';
      })
      .addCase(authenticateThunk.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to authenticate';
      })
      .addCase(getRolesThunk.fulfilled, (state, action) => {
        state.roles = action.payload;
        state.status = 'succeeded';
      })
      .addCase(getUsersThunk.fulfilled, (state, action) => {
        state.users = action.payload;
        state.status = 'succeeded';
      })
      .addCase(getUserThunk.fulfilled, (state, action) => {
        state.user = action.payload;
        state.status = 'succeeded';
      })
      .addCase(getScannersThunk.fulfilled, (state, action) => {
        state.scanners = action.payload;
        state.status = 'succeeded';
      })
      .addCase(getConfigsThunk.fulfilled, (state, action) => {
        state.configs = action.payload;
        state.status = 'succeeded';
      })
      .addCase(getPortlistsThunk.fulfilled, (state, action) => {
        state.portlists = action.payload;
        state.status = 'succeeded';
      })
      .addCase(getHostsThunk.fulfilled, (state, action) => {
        state.hosts = action.payload;
        state.status = 'succeeded';
      })
      .addCase(deleteHostThunk.fulfilled, (state, action) => {
        state.hosts = state.hosts.filter(host => host.id !== action.payload);
        state.status = 'succeeded';
      })
      .addCase(convertHostsToTargetsThunk.fulfilled, (state, action) => {
        state.targets = action.payload;
        state.status = 'succeeded';
      })
      .addCase(getTargetsThunk.fulfilled, (state, action) => {
        state.targets = action.payload;
        state.status = 'succeeded';
      })
      .addCase(createTargetThunk.fulfilled, (state, action) => {
        state.targets.push(action.payload);
        state.status = 'succeeded';
      })
      .addCase(deleteTargetThunk.fulfilled, (state, action) => {
        state.targets = state.targets.filter(target => target.id !== action.payload);
        state.status = 'succeeded';
      })
      .addCase(modifyTargetThunk.fulfilled, (state, action) => {
        state.targets = state.targets.map(target =>
          target.id === action.payload.id ? action.payload : target
        );
        state.status = 'succeeded';
      })
      .addCase(createTaskThunk.fulfilled, (state, action) => {
        state.tasks.push(action.payload);
        state.status = 'succeeded';
      })
      .addCase(startTaskThunk.fulfilled, (state, action) => {
        const updatedTask = state.tasks.find(task => task.id === action.payload.id);
        if (updatedTask) {
          Object.assign(updatedTask, action.payload);
        }
        state.status = 'succeeded';
      })
      .addCase(stopTaskThunk.fulfilled, (state, action) => {
        const updatedTask = state.tasks.find(task => task.id === action.payload.id);
        if (updatedTask) {
          Object.assign(updatedTask, action.payload);
        }
        state.status = 'succeeded';
      })
      .addCase(resumeTaskThunk.fulfilled, (state, action) => {
        const updatedTask = state.tasks.find(task => task.id === action.payload.id);
        if (updatedTask) {
          Object.assign(updatedTask, action.payload);
        }
        state.status = 'succeeded';
      })
      .addCase(deleteTaskThunk.fulfilled, (state, action) => {
        state.tasks = state.tasks.filter(task => task.id !== action.payload);
        state.status = 'succeeded';
      })
      .addCase(modifyTaskThunk.fulfilled, (state, action) => {
        state.tasks = state.tasks.map(task =>
          task.id === action.payload.id ? action.payload : task
        );
        state.status = 'succeeded';
      })
      .addCase(getTaskThunk.fulfilled, (state, action) => {
        const updatedTask = state.tasks.find(task => task.id === action.payload.id);
        if (updatedTask) {
          Object.assign(updatedTask, action.payload);
        }
        state.status = 'succeeded';
      })
      .addCase(getTaskStatusThunk.fulfilled, (state, action) => {
        const task = state.tasks.find(task => task.id === action.payload.id);
        if (task) {
          task.status = action.payload.status;
        }
        state.status = 'succeeded';
      })
      .addCase(getTasksThunk.fulfilled, (state, action) => {
        state.tasks = action.payload;
        state.status = 'succeeded';
      })
      .addCase(getResultsThunk.fulfilled, (state, action) => {
        // Implement handling for results here if needed
        state.status = 'succeeded';
      })
      .addCase(getReportsThunk.fulfilled, (state, action) => {
        state.reports = action.payload;        
        state.status = 'succeeded';
      })
      .addCase(getReportThunk.fulfilled, (state, action) => {
        state.selectedReport = action.payload; // Set the selected report
        state.status = 'succeeded';
      })
      .addCase(deleteReportThunk.fulfilled, (state, action) => {
        state.reports = state.reports.filter(report => report.id !== action.payload);
        if (state.selectedReport?.id === action.payload) {
          state.selectedReport = null; // Clear selected report if deleted
        }
        state.status = 'succeeded';
      })
      .addCase(exportReportThunk.fulfilled, (state, action) => {
        state.status = 'succeeded';
      })
      .addCase(getSchedulesThunk.fulfilled, (state, action) => {
        state.schedules = action.payload;
        state.status = 'succeeded';
      })
      .addCase(createScheduleThunk.fulfilled, (state, action) => {
        state.schedules.push(action.payload);
        state.status = 'succeeded';
      })
      .addCase(modifyScheduleThunk.fulfilled, (state, action) => {
        state.schedules = state.schedules.map(schedule =>
          schedule.id === action.payload.id ? action.payload : schedule
        );
        state.status = 'succeeded';
      })
      .addCase(deleteScheduleThunk.fulfilled, (state, action) => {
        state.schedules = state.schedules.filter(schedule => schedule.id !== action.payload);
        state.status = 'succeeded';
      })
      .addCase(createAlertThunk.fulfilled, (state, action) => {
        state.alerts.push(action.payload);
        state.status = 'succeeded';
      })
      .addCase(getAlertsThunk.fulfilled, (state, action) => {
        state.alerts = action.payload;
        state.status = 'succeeded';
      })
      .addCase(analyzeReportThunk.fulfilled, (state, action) => {
        state.analysisResults = action.payload; 
        state.status = 'succeeded';
      })
      // Add additional cases for other thunks here
      .addMatcher(
        (action) => action.type.endsWith('/rejected'),
        (state, action) => {
          state.status = 'failed';
          state.error = action.error.message || 'Request failed';
        }
      );
  },
});

export const { clearAnalysisResults, setSidebarCollapsed } = scannerSlice.actions;
export const { setTheme } = scannerSlice.actions;
export default scannerSlice.reducer;
