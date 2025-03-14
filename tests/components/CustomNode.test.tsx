import React from 'react';
import { render, screen } from '@testing-library/react';
import CustomNode from '../../src/components/CustomNode';
import { NodeData } from '../../src/types/agent';

// Mock the react-flow dependencies
jest.mock('reactflow', () => ({
  Handle: jest.fn(({ type, position, id }) => (
    <div data-testid={`handle-${type}-${position}-${id || 'default'}`} />
  )),
  Position: {
    Top: 'top',
    Right: 'right',
    Bottom: 'bottom',
    Left: 'left'
  }
}));

describe('CustomNode Component', () => {
  const renderNodeWithType = (type: NodeData['type']) => {
    const mockData: NodeData = {
      label: 'Test Node',
      description: 'Test Description',
      type: type,
      channels: ['channel1', 'channel2'],
      tools: ['tool1', 'tool2']
    };
    
    return render(<CustomNode data={mockData} />);
  };
  
  it('renders coordinator node with correct styling', () => {
    renderNodeWithType('coordinator');
    
    // Check if basic elements are present
    expect(screen.getByText('Test Node')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    
    // Check if channels are rendered
    expect(screen.getByText('channel1')).toBeInTheDocument();
    expect(screen.getByText('channel2')).toBeInTheDocument();
    
    // Check if tools are rendered
    expect(screen.getByText('tool1')).toBeInTheDocument();
    expect(screen.getByText('tool2')).toBeInTheDocument();
    
    // Check for handles
    expect(screen.getByTestId('handle-target-top-default')).toBeInTheDocument();
    expect(screen.getByTestId('handle-source-bottom-default')).toBeInTheDocument();
  });
  
  it('renders operations node with correct styling', () => {
    renderNodeWithType('operations');
    
    // Basic checks
    expect(screen.getByText('Test Node')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });
  
  it('renders swarm_agent node with correct styling', () => {
    renderNodeWithType('swarm_agent');
    
    // Basic checks
    expect(screen.getByText('Test Node')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });
  
  it('renders default node when unknown type is provided', () => {
    const mockData: NodeData = {
      label: 'Test Node',
      description: 'Test Description',
      type: 'default',
      channels: ['channel1'],
      tools: ['tool1']
    };
    
    render(<CustomNode data={mockData} />);
    
    expect(screen.getByText('Test Node')).toBeInTheDocument();
  });
}); 