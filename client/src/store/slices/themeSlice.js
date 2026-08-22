/**
 * store/slices/themeSlice.js
 * Light / dark mode state. Persisted to localStorage immediately (so a
 * refresh never flashes the wrong theme) and, when the user is logged in,
 * synced to the backend via PUT /api/users/me/theme so the preference
 * follows them across devices.
 */
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../../configs/api";

const STORAGE_KEY = "gt_theme";

function getInitialTheme() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark") return stored;
  // Fall back to the user's OS preference on first visit.
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  return prefersDark ? "dark" : "light";
}

/** Best-effort sync to the backend; failures shouldn't block the UI toggle. */
export const syncThemeToServer = createAsyncThunk(
  "theme/syncToServer",
  async (theme, { rejectWithValue }) => {
    try {
      await api.put("/api/users/me/theme", { theme });
      return theme;
    } catch (err) {
      // Not logged in yet, or offline - that's fine, localStorage still has it.
      return rejectWithValue(err?.response?.data?.message);
    }
  }
);

const themeSlice = createSlice({
  name: "theme",
  initialState: {
    mode: getInitialTheme(), // "light" | "dark"
  },
  reducers: {
    setTheme(state, action) {
      state.mode = action.payload;
      localStorage.setItem(STORAGE_KEY, state.mode);
    },
    toggleTheme(state) {
      state.mode = state.mode === "dark" ? "light" : "dark";
      localStorage.setItem(STORAGE_KEY, state.mode);
    },
  },
});

export const { setTheme, toggleTheme } = themeSlice.actions;
export default themeSlice.reducer;
