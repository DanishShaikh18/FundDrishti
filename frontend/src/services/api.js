import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.message);
    return Promise.reject(error);
  },
);

// API Endpoints

/**
 * Fetch all active fraud alerts
 * @returns {Promise<Array>} Array of alert objects
 */
export const fetchAlerts = async () => {
  try {
    const response = await apiClient.get("/alerts");
    return response.data;
  } catch (error) {
    console.error("Failed to fetch alerts:", error);
    throw error;
  }
};

/**
 * Fetch detailed case information
 * @param {string} caseId - The case ID
 * @returns {Promise<Object>} Case detail object
 */
export const fetchCaseDetail = async (caseId) => {
  try {
    const response = await apiClient.get(`/cases/${caseId}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch case ${caseId}:`, error);
    throw error;
  }
};

/**
 * Update case status
 * @param {string} caseId - The case ID
 * @param {string} status - New status (Open, Investigating, Closed)
 * @param {string} investigatorNotes - Optional notes
 * @returns {Promise<Object>} Updated case object
 */
export const updateCaseStatus = async (
  caseId,
  status,
  investigatorNotes = "",
) => {
  try {
    const response = await apiClient.put(`/cases/${caseId}/status`, {
      status,
      investigator_notes: investigatorNotes,
    });
    return response.data;
  } catch (error) {
    console.error(`Failed to update case status for ${caseId}:`, error);
    throw error;
  }
};

export default apiClient;
