/**
 * store/store.js
 * Redux Toolkit store root. Combines every feature slice - add new slices
 * here as the app grows (e.g. tripsSlice, communitySlice) if a page needs
 * cross-component shared state beyond simple local component fetches.
 */
import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./slices/authSlice";
import themeReducer from "./slices/themeSlice";
import uiReducer from "./slices/uiSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    theme: themeReducer,
    ui: uiReducer,
  },
});
