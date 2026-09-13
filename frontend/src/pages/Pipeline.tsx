import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { stageKeys, stageLabels, stages } from "../types";

export function Pipeline() {
  const [lead, setLead] = useState<string>(stages[0]);
  const [leadId, setLeadId] = useState<number | null>(null);

  useEffect(() => {
    apiFetch("/leads")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((items) => {
        if (items.length) {
          setLeadId(items[0].id);
          setLead(stageLabels[items[0].stage] || stages[0]);
        }
      })
      .catch(() => undefined);
  }, []);

  const changeStage = async (next: string) => {
    setLead(next);
    if (!leadId) return;
    const response = await apiFetch(`/leads/${leadId}`, {
      method: "PUT",
      body: JSON.stringify({ stage: stageKeys[next as keyof typeof stageKeys] }),
    });
    if (!response.ok) alert("Faza leada nije sačuvana.");
  };

  return (
    <section className="card pipeline-card">
      <h2>Ana Jovanović</h2>
      <p>Promeni fazu leada:</p>
      <select value={lead} onChange={(e) => changeStage(e.target.value)}>
        {stages.map((stage) => <option key={stage}>{stage}</option>)}
      </select>
      <p className="badge pipeline-stage">{lead}</p>
    </section>
  );
}
