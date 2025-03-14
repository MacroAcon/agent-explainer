import React from 'react';
import { initialNodes, initialEdges } from '../data/retailData';
import AgentGraphTemplate from './AgentGraphTemplate';

const AgentGraph = () => {
  return <AgentGraphTemplate nodes={initialNodes} edges={initialEdges} />;
};

export default AgentGraph; 