import { ReactFlow } from 'reactflow';
import 'reactflow/dist/style.css';
import AgentGraph from '@/components/AgentGraph';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-gray-900 text-white">
      <div className="z-10 w-full max-w-7xl">
        <h1 className="text-4xl font-bold mb-8 text-center">Calhoun Business Agent Network</h1>
        <div style={{ width: '100%', height: '80vh' }} className="border border-gray-700 rounded-lg overflow-hidden">
          <AgentGraph />
        </div>
      </div>
    </main>
  );
}
