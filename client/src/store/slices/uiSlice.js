/**
 * store/slices/uiSlice.js
 * Small pieces of shared UI state that don't warrant their own slice:
 * the current breadcrumb trail and whether the sidebar is collapsed
 * (persisted as a "saved preference", per the feature list).
 */
import { createSlice } from "@reduxjs/toolkit";

const SIDEBAR_KEY = "gt_sidebar_collapsed";

const uiSlice = createSlice({
  name: "ui",
  initialState: {
    breadcrumbs: [], // [{ label, path }]
    sidebarCollapsed: localStorage.getItem(SIDEBAR_KEY) === "true",
  },
  reducers: {
    setBreadcrumbs(state, action) {
      state.breadcrumbs = action.payload;
    },
    toggleSidebar(state) {
      state.sidebarCollapsed = !state.sidebarCollapsed;
      localStorage.setItem(SIDEBAR_KEY, String(state.sidebarCollapsed));
    },
  },
});

export const { setBreadcrumbs, toggleSidebar } = uiSlice.actions;
export default uiSlice.reducer;
