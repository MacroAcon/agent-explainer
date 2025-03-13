import { ReactFlow } from 'reactflow';
import 'reactflow/dist/style.css';
import AgentGraph from '@/components/AgentGraph';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-gray-900 text-white">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8 text-center">Calhoun Business Agent Network</h1>
        <div className="h-[600px] w-full border border-gray-700 rounded-lg overflow-hidden">
          <AgentGraph />
        </div>
      </div>
    </main>
  );
}
