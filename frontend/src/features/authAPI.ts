import axios from "axios";

const MY_SERVER = "http://192.168.14.109:5000/auth";

// Instance of axios
const apiClient = axios.create();

// Add a request interceptor to attach the token to every request
apiClient.interceptors.request.use((config) => {
  // Get the token from localStorage or any other storage mechanism you're using
  const token = localStorage.getItem("token");

  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// API Calls
export const login = (email: string, password: string) => {
  return axios.post(MY_SERVER + "/signin", { email, password });
};

export const register = (email: string, username: string, password: string) => {
  return axios.post(MY_SERVER + "/signup", { email, username, password });
};

export const registerAdmin = (
  email: string,
  username: string,
  password: string
) => {
  return apiClient.post(MY_SERVER + "/create_admin", {
    email,
    username,
    password,
  });
};

export const modifyUser = (
  id: number,
  email?: string,
  username?: string,
  password?: string
) => {
  const payload: { [key: string]: string } = {};

  if (email) payload.email = email;
  if (username) payload.username = username;
  if (password) payload.password = password;

  return apiClient.put(MY_SERVER + `/modify_user/${id}`, payload);
};

export const deleteUser = (id: number) => {
  return apiClient.delete(MY_SERVER + `/delete_user/${id}`);
};

export const getUsers = () => {
  return apiClient.get(MY_SERVER + "/get_users");
};

export const getUser = () => {
  return apiClient.get(MY_SERVER + `/get_user`);
};
