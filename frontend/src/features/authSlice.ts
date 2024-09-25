import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import {
  login,
  register,
  registerAdmin,
  getUser,
  getUsers,
  modifyUser,
  deleteUser,
} from "./authAPI";

// Define types for User and State
interface User {
  id: number;
  email?: string;
  username?: string;
  // Include other user properties as needed
}

interface AuthState {
  isLoggedIn: boolean
  user: User | null;
  users: User[];
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}

// Handling errors because TypeScript doesn't like setting error type to "any"
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.response.data.error;
  return String(error);
}

const reportError = ({ message }: { message: string }) => {
  console.log(message);
};

// Async Thunks for each API call
// Login
export const loginUser = createAsyncThunk(
  "auth/login",
  async ({ email, password }: { email: string; password: string }, thunkAPI) => {
    try {
      const response = await login(email, password);
      return response.data; // Assuming the response contains user data and token
    } catch (error) {
      reportError({ message: getErrorMessage(error) });
      return thunkAPI.rejectWithValue(getErrorMessage(error));
    }
  }
);

// Register
export const registerUser = createAsyncThunk(
  "auth/register",
  async ({ email, username, password }: { email: string; username: string; password: string }, thunkAPI) => {
    try {
      const response = await register(email, username, password);
      return response.data;
    } catch (error) {
      reportError({ message: getErrorMessage(error) });
      return thunkAPI.rejectWithValue(getErrorMessage(error));
    }
  }
);

// Register Admin
export const registerAdminUser = createAsyncThunk(
  "auth/registerAdmin",
  async ({ email, username, password }: { email: string; username: string; password: string }, thunkAPI) => {
    try {
      const response = await registerAdmin(email, username, password);
      return response.data;
    } catch (error) {
      reportError({ message: getErrorMessage(error) });
      return thunkAPI.rejectWithValue(getErrorMessage(error));
    }
  }
);

// Get a single user
export const fetchUser = createAsyncThunk(
  "auth/getUser",
  async (_ , thunkAPI) => {
    try {
      const response = await getUser();
      return response.data;
    } catch (error) {
      reportError({ message: getErrorMessage(error) });
      return thunkAPI.rejectWithValue(getErrorMessage(error));
    }
  }
);

// Get all users
export const fetchUsers = createAsyncThunk(
  "auth/getUsers",
  async (_, thunkAPI) => {
    try {
      const response = await getUsers();
      return response.data;
    } catch (error) {
      reportError({ message: getErrorMessage(error) });
      return thunkAPI.rejectWithValue(getErrorMessage(error));
    }
  }
);

// Modify user
export const updateUser = createAsyncThunk(
  "auth/modifyUser",
  async (
    { id, email, username, password }: { id: number; email?: string; username?: string; password?: string },
    thunkAPI
  ) => {
    try {
      const response = await modifyUser(id, email, username, password);
      return response.data;
    } catch (error) {
      reportError({ message: getErrorMessage(error) });
      return thunkAPI.rejectWithValue(getErrorMessage(error));
    }
  }
);

// Delete user
export const removeUser = createAsyncThunk(
  "auth/deleteUser",
  async (id: number, thunkAPI) => {
    try {
      const response = await deleteUser(id);
      return { response, id }; // Return an object containing the id of the deleted user
    } catch (error) {
      reportError({ message: getErrorMessage(error) });
      return thunkAPI.rejectWithValue(getErrorMessage(error));
    }
  }
);

// Initial state
const initialState: AuthState = {
  user: null,
  users: [],
  status: 'idle',
  error: null,
  isLoggedIn: false
};

// Slice
export const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout: (state) => { 
      state.user = null;
      localStorage.removeItem("token"); 
      state.isLoggedIn = false
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.status = "loading";
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload.user;
        localStorage.setItem("token", action.payload.access_token); 
        state.isLoggedIn = true
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      })

      // Register
      .addCase(registerUser.pending, (state) => {
        state.status = "loading";
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      })

      // Register Admin
      .addCase(registerAdminUser.pending, (state) => {
        state.status = "loading";
      })
      .addCase(registerAdminUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload;
      })
      .addCase(registerAdminUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      })

      // Fetch single user
      .addCase(fetchUser.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      })

      // Fetch all users
      .addCase(fetchUsers.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.users = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      })

      // Modify user
      .addCase(updateUser.pending, (state) => {
        state.status = "loading";
      })
      .addCase(updateUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload;
      })
      .addCase(updateUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      })

      // Delete user
      .addCase(removeUser.pending, (state) => {
        state.status = "loading";
      })
      .addCase(removeUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.users = state.users.filter((user) => user.id !== action.payload.id);
      })
      .addCase(removeUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload as string;
      });
  },
});

export const { logout } = authSlice.actions;

export default authSlice.reducer;
