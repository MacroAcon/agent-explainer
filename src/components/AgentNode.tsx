'use client';

import { memo } from 'react';
import { Handle, Position } from 'reactflow';

interface AgentNodeData {
  label: string;
  description: string;
  tools: string[];
  memorySystems?: string[];
  channels?: string[];
}

interface AgentNodeProps {
  data: AgentNodeData;
  isConnectable: boolean;
}

function AgentNode({ data, isConnectable }: AgentNodeProps) {
  return (
    <div className="px-4 py-2 shadow-md rounded-md bg-gray-800 border-2 border-gray-600 min-w-[250px]">
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="w-2 h-2 !bg-blue-500"
      />
      
      <div className="flex flex-col">
        <div className="flex items-center">
          <div className="ml-2">
            <div className="text-lg font-bold text-white">{data.label}</div>
            <div className="text-gray-300 text-sm">{data.description}</div>
          </div>
        </div>
        
        {data.memorySystems && (
          <div className="mt-2">
            <div className="text-sm font-semibold text-gray-300">Memory Systems:</div>
            <div className="flex flex-wrap gap-1 mt-1">
              {data.memorySystems.map((memory) => (
                <span
                  key={memory}
                  className="px-2 py-1 text-xs bg-purple-900 text-purple-100 rounded-full"
                >
                  {memory}
                </span>
              ))}
            </div>
          </div>
        )}

        {data.channels && (
          <div className="mt-2">
            <div className="text-sm font-semibold text-gray-300">Channels:</div>
            <div className="flex flex-wrap gap-1 mt-1">
              {data.channels.map((channel) => (
                <span
                  key={channel}
                  className="px-2 py-1 text-xs bg-green-900 text-green-100 rounded-full"
                >
                  {channel}
                </span>
              ))}
            </div>
          </div>
        )}
        
        <div className="mt-2">
          <div className="text-sm font-semibold text-gray-300">Tools:</div>
          <div className="flex flex-wrap gap-1 mt-1">
            {data.tools.map((tool) => (
              <span
                key={tool}
                className="px-2 py-1 text-xs bg-blue-900 text-blue-100 rounded-full"
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
        className="w-2 h-2 !bg-blue-500"
      />
    </div>
  );
}

export default memo(AgentNode); 