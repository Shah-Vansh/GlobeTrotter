/**
 * store/slices/authSlice.js
 * Owns the logged-in user's profile + JWT lifecycle (login/register/logout,
 * "who am I" hydration on app load). Tokens themselves live in
 * localStorage (see configs/api.js::tokenStorage); this slice only keeps
 * the in-memory user object and loading/error flags for the UI.
 */
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api, { tokenStorage } from "../../configs/api";
import { getErrorMessage } from "../../lib/formatters";

/** POST /api/auth/login -> { user, access_token, refresh_token } */
export const loginUser = createAsyncThunk(
  "auth/login",
  async ({ username, password }, { rejectWithValue }) => {
    try {
      const { data } = await api.post("/api/auth/login", { username, password });
      tokenStorage.setTokens(data.data.access_token, data.data.refresh_token);
      return data.data.user;
    } catch (err) {
      return rejectWithValue(getErrorMessage(err, "Invalid username or password."));
    }
  }
);

/** POST /api/auth/register -> { user, access_token, refresh_token } */
export const registerUser = createAsyncThunk(
  "auth/register",
  async (formPayload, { rejectWithValue }) => {
    try {
      const { data } = await api.post("/api/auth/register", formPayload);
      tokenStorage.setTokens(data.data.access_token, data.data.refresh_token);
      return data.data.user;
    } catch (err) {
      return rejectWithValue(getErrorMessage(err, "Registration failed."));
    }
  }
);

/** GET /api/auth/me - used on app load to restore the session from a stored token. */
export const fetchCurrentUser = createAsyncThunk(
  "auth/me",
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await api.get("/api/auth/me");
      return data.data;
    } catch (err) {
      return rejectWithValue(getErrorMessage(err));
    }
  }
);

const initialState = {
  user: null,
  status: "idle", // idle | loading | succeeded | failed
  bootstrapped: false, // has the initial "restore session" check finished?
  error: null,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout(state) {
      tokenStorage.clearTokens();
      state.user = null;
      state.status = "idle";
      state.error = null;
    },
    setUser(state, action) {
      state.user = action.payload;
    },
    /** Called when there is no stored token at all, so ProtectedRoute
     * doesn't spin forever waiting for a session-restore call that will
     * never happen (see App.jsx). */
    bootstrapDone(state) {
      state.bootstrapped = true;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })
      .addCase(registerUser.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })
      .addCase(fetchCurrentUser.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload;
        state.bootstrapped = true;
      })
      .addCase(fetchCurrentUser.rejected, (state) => {
        state.status = "idle";
        state.user = null;
        state.bootstrapped = true;
      });
  },
});

export const { logout, setUser, bootstrapDone } = authSlice.actions;
export default authSlice.reducer;
