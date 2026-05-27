import { useState, useEffect } from "react";
import { fetchCaseDetail } from "../services/api";

/**
 * Hook to fetch and manage case details
 * @param {string} caseId - The case ID to fetch
 * @returns {Object} { caseData, loading, error, refetch }
 */
export const useCaseDetail = (caseId) => {
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = async () => {
    if (!caseId) return;

    setLoading(true);
    try {
      const data = await fetchCaseDetail(caseId);
      setCaseData(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      setCaseData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refetch();
  }, [caseId]);

  return { caseData, loading, error, refetch };
};
