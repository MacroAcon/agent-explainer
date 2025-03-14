import React from 'react';
import { initialNodes, initialEdges } from '../data/healthServiceData';
import AgentGraphTemplate from './AgentGraphTemplate';

const HealthAgentGraph = () => {
  return <AgentGraphTemplate nodes={initialNodes} edges={initialEdges} />;
};

export default HealthAgentGraph; 