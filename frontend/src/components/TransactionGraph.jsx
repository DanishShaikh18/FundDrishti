import CytoscapeComponentModule from "react-cytoscapejs";
import { CYTOSCAPE_CONFIG } from "../utils/constants";
import "../styles/TransactionGraph.css";

const CytoscapeComponent = CytoscapeComponentModule.default || CytoscapeComponentModule;

function TransactionGraph({ nodes, edges }) {
  if (!nodes || nodes.length === 0) {
    return (
      <div className="transaction-graph empty">
        <p>No transaction data available</p>
      </div>
    );
  }

  // Transform data to cytoscape format
  const elements = [
    ...nodes.map((node) => ({
      data: {
        id: node.id,
        label: node.label,
        role: node.role,
      },
    })),
    ...(edges || []).map((edge) => ({
      data: {
        source: edge.source,
        target: edge.target,
        weight: edge.amount,
        label: `$${edge.amount.toLocaleString()}`,
      },
    })),
  ];

  return (
    <div className="transaction-graph" style={{ width: "100%", height: "100%" }}>
      <CytoscapeComponent
        key={JSON.stringify(elements)}
        elements={elements}
        style={{ width: "100%", height: "100%" }}
        stylesheet={CYTOSCAPE_CONFIG.style}
        layout={CYTOSCAPE_CONFIG.layout}
        wheelSensitivity={0.1}
      />
    </div>
  );
}

export default TransactionGraph;
