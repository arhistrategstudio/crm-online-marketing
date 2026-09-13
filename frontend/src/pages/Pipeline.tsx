import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { LeadItem, stageKeys, stageLabels, stages } from "../types";

export function Pipeline() {
  const [leads, setLeads] = useState<LeadItem[]>([]);

  const load = () => {
    apiFetch("/leads")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setLeads)
      .catch(() => undefined);
  };

  useEffect(load, []);

  const changeStage = async (lead: LeadItem, nextLabel: string) => {
    const nextStage = stageKeys[nextLabel as keyof typeof stageKeys];
    setLeads((current) => current.map((l) => (l.id === lead.id ? { ...l, stage: nextStage } : l)));
    const response = await apiFetch(`/leads/${lead.id}`, {
      method: "PUT",
      body: JSON.stringify({ stage: nextStage, campaign_id: lead.campaign_id, value: lead.value }),
    });
    if (!response.ok) {
      alert("Faza leada nije sačuvana.");
      load();
    }
  };

  return (
    <div className="pipeline-board">
      {stages.map((stageLabel) => {
        const stageKey = stageKeys[stageLabel];
        const stageLeads = leads.filter((lead) => lead.stage === stageKey);
        return (
          <div className="pipeline-column" key={stageLabel}>
            <div className="pipeline-column-header">
              <strong>{stageLabel}</strong>
              <span className="badge">{stageLeads.length}</span>
            </div>
            {!stageLeads.length && <p className="muted-line">Nema leadova.</p>}
            {stageLeads.map((lead) => (
              <div className="lead-card" key={lead.id}>
                <strong>{lead.contact_name}</strong>
                <span>{lead.value !== null ? `${lead.value.toLocaleString("sr-RS")} RSD` : "Bez vrednosti"}</span>
                <select value={stageLabels[lead.stage] || stages[0]} onChange={(e) => changeStage(lead, e.target.value)}>
                  {stages.map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}
