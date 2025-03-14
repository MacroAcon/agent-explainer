// Configure Jest DOM extensions
import '@testing-library/jest-dom';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '',
      query: {},
      asPath: '',
      push: jest.fn(),
      replace: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn(),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
    };
  },
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // Deprecated
    removeListener: jest.fn(), // Deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Suppress React Flow warnings
jest.mock('reactflow', () => {
  const originalModule = jest.requireActual('reactflow');
  return {
    __esModule: true,
    ...originalModule,
    ReactFlow: jest.fn(() => null),
    Background: jest.fn(() => null),
    Controls: jest.fn(() => null),
    MiniMap: jest.fn(() => null),
    useNodesState: jest.fn(() => [[], jest.fn()]),
    useEdgesState: jest.fn(() => [[], jest.fn()]),
    useReactFlow: jest.fn(() => ({
      project: jest.fn(),
      getNodes: jest.fn(() => []),
      getEdges: jest.fn(() => []),
      getNode: jest.fn(),
      getEdge: jest.fn(),
      setNodes: jest.fn(),
      setEdges: jest.fn(),
      addNodes: jest.fn(),
      addEdges: jest.fn(),
      fitView: jest.fn(),
      zoomIn: jest.fn(),
      zoomOut: jest.fn(),
    })),
  };
}); 