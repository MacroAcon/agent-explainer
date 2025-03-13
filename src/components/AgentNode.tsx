'use client';

import { memo } from 'react';
import { Handle, Position } from 'reactflow';

interface AgentNodeData {
  label: string;
  description: string;
  tools: string[];
}

interface AgentNodeProps {
  data: AgentNodeData;
  isConnectable: boolean;
}

function AgentNode({ data, isConnectable }: AgentNodeProps) {
  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-white border-2 border-gray-200 min-w-[200px]">
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="w-2 h-2"
      />
      
      <div className="flex flex-col">
        <div className="flex items-center">
          <div className="ml-2">
            <div className="text-lg font-bold text-gray-900">{data.label}</div>
            <div className="text-gray-500 text-sm">{data.description}</div>
          </div>
        </div>
        
        <div className="mt-2">
          <div className="text-sm font-semibold text-gray-700">Tools:</div>
          <div className="flex flex-wrap gap-1 mt-1">
            {data.tools.map((tool) => (
              <span
                key={tool}
                className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
              >
                {tool}
              </span>
            ))}
          </div>
        </div>
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        className="w-2 h-2"
      />
    </div>
  );
}

export default memo(AgentNode); 