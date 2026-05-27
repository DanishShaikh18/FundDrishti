import { useState, useEffect } from "react";
import { fetchAlerts } from "../services/api";

/**
 * Hook to fetch and manage alerts
 * @returns {Object} { alerts, loading, error, refetch }
 */
export const useAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = async () => {
    setLoading(true);
    try {
      const data = await fetchAlerts();
      setAlerts(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refetch();
    // Auto-refresh alerts every 30 seconds
    const interval = setInterval(refetch, 30000);
    return () => clearInterval(interval);
  }, []);

  return { alerts, loading, error, refetch };
};
