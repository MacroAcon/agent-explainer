import React from 'react';
import { BaseEdge, EdgeProps, getBezierPath } from 'reactflow';

const CustomEdge: React.FC<EdgeProps> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  markerEnd,
  data,
}) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      <BaseEdge
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          ...style,
          strokeWidth: 2,
          stroke: '#b1b1b7',
        }}
      />
      {data?.label && (
        <foreignObject
          x={labelX - 20}
          y={labelY - 10}
          width={40}
          height={20}
          className="edge-label"
        >
          <div style={{ textAlign: 'center' }}>{data.label}</div>
        </foreignObject>
      )}
    </>
  );
};

export default CustomEdge; 