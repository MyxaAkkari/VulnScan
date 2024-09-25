import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "bootstrap/dist/css/bootstrap.css";
import { configureStore } from "@reduxjs/toolkit";
import { Provider } from "react-redux";
import authReducer from "./features/authSlice.ts";
import scannerReducer from "./features/scannerSlice.ts";
import './index.css'
import { BrowserRouter } from "react-router-dom";
const store = configureStore({
  reducer: {
    auth: authReducer,
    scanner : scannerReducer
  },
});
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Provider store={store}>
      <BrowserRouter>
      <App />
      </BrowserRouter>
    </Provider>
  </StrictMode>
);
export type RootState = ReturnType<typeof store.getState>;