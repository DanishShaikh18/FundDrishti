import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import "../styles/BehavioralRadar.css";

function BehavioralRadar({ behavioralProfile }) {
  if (!behavioralProfile) {
    return (
      <div className="behavioral-radar empty">No behavioral data available</div>
    );
  }

  // Transform data for radar chart
  const radarData = [
    {
      axis: "Account Age",
      victim: behavioralProfile.victim?.account_age_days || 0,
      suspect: behavioralProfile.suspect?.account_age_days || 0,
      baseline: behavioralProfile.baseline?.account_age_days || 0,
    },
    {
      axis: "Avg Transaction Size",
      victim: (behavioralProfile.victim?.avg_transaction_size || 0) / 1000,
      suspect: (behavioralProfile.suspect?.avg_transaction_size || 0) / 1000,
      baseline: (behavioralProfile.baseline?.avg_transaction_size || 0) / 1000,
    },
    {
      axis: "Transaction Frequency",
      victim: behavioralProfile.victim?.transaction_frequency || 0,
      suspect: behavioralProfile.suspect?.transaction_frequency || 0,
      baseline: behavioralProfile.baseline?.transaction_frequency || 0,
    },
    {
      axis: "Dormancy Days",
      victim: behavioralProfile.victim?.dormancy_days || 0,
      suspect: behavioralProfile.suspect?.dormancy_days || 0,
      baseline: behavioralProfile.baseline?.dormancy_days || 0,
    },
    {
      axis: "Geographic Variance",
      victim: behavioralProfile.victim?.geographic_variance || 0,
      suspect: behavioralProfile.suspect?.geographic_variance || 0,
      baseline: behavioralProfile.baseline?.geographic_variance || 0,
    },
    {
      axis: "Network Centrality",
      victim: behavioralProfile.victim?.network_centrality || 0,
      suspect: behavioralProfile.suspect?.network_centrality || 0,
      baseline: behavioralProfile.baseline?.network_centrality || 0,
    },
    {
      axis: "Risk Indicator",
      victim: behavioralProfile.victim?.risk_indicator || 0,
      suspect: behavioralProfile.suspect?.risk_indicator || 0,
      baseline: behavioralProfile.baseline?.risk_indicator || 0,
    },
  ];

  return (
    <div className="behavioral-radar">
      <h3>Behavioral Profile Comparison</h3>
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart key={JSON.stringify(radarData)} data={radarData}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis
            dataKey="axis"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "#94a3b8" }}
          />
          <Radar
            name="Victim"
            dataKey="victim"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.3}
          />
          <Radar
            name="Suspect"
            dataKey="suspect"
            stroke="#ef4444"
            fill="#ef4444"
            fillOpacity={0.3}
          />
          <Radar
            name="Baseline"
            dataKey="baseline"
            stroke="#10b981"
            fill="#10b981"
            fillOpacity={0.3}
          />
          <Legend wrapperStyle={{ color: "#e2e8f0" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #334155",
              borderRadius: "4px",
              color: "#e2e8f0",
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BehavioralRadar;
