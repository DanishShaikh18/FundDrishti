import React, { createContext, useContext, useState } from "react";

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [filters, setFilters] = useState({
    patternType: null,
    status: null,
    minScore: 0,
    maxScore: 100,
  });

  const updateFilters = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const value = {
    selectedAlert,
    setSelectedAlert,
    filters,
    updateFilters,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useAppContext must be used within AppProvider");
  }
  return context;
};
