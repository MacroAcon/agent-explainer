import React from 'react';
import { render, screen } from '@testing-library/react';
import AgentGraph from '../../src/components/AgentGraph';
import AgentGraphTemplate from '../../src/components/AgentGraphTemplate';

// Mock the AgentGraphTemplate component
jest.mock('../../src/components/AgentGraphTemplate', () => {
  return jest.fn(() => <div data-testid="agent-graph-template">Mocked Agent Graph Template</div>);
});

// Mock the data
jest.mock('../../src/data/retailData', () => ({
  initialNodes: [{ id: 'test-node', data: { label: 'Test Node' } }],
  initialEdges: [{ id: 'test-edge', source: 'node1', target: 'node2' }],
}));

describe('AgentGraph Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });
  
  it('renders with the correct data from retailData', () => {
    // Render the component
    render(<AgentGraph />);
    
    // Check if AgentGraphTemplate is rendered
    expect(screen.getByTestId('agent-graph-template')).toBeInTheDocument();
    
    // Check if AgentGraphTemplate was called with the correct props
    const { initialNodes, initialEdges } = require('../../src/data/retailData');
    expect(AgentGraphTemplate).toHaveBeenCalledWith(
      { nodes: initialNodes, edges: initialEdges },
      expect.anything()
    );
  });
}); 