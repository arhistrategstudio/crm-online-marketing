import { useEffect, useState } from "react";
import { AlertTriangle, CalendarClock, User } from "lucide-react";
import { apiFetch } from "../lib/api";
import { DashboardSummary, LeadItem, channelLabels, stageKeys, stages } from "../types";
import { LeadDrawer } from "../components/LeadDrawer";

const emptySummary: DashboardSummary = {
  new_inquiries: 0,
  contacted: 0,
  active_leads: 0,
  potential_value: 0,
  closed_this_month_value: 0,
  offers_sent: 0,
  proposals_sent: 0,
  won: 0,
  lost: 0,
  win_rate: null,
  avg_time_to_sale_days: null,
  scheduled_paid: 0,
  campaigns_active: 0,
  avg_cost_per_lead: null,
  lost_reasons: [],
};

function money(value: number): string {
  return `${value.toLocaleString("sr-RS")} RSD`;
}

function formatReminder(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleString("sr-RS", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export function Pipeline() {
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [summary, setSummary] = useState<DashboardSummary>(emptySummary);
  const [openLead, setOpenLead] = useState<number | null>(null);
  const [dragging, setDragging] = useState<number | null>(null);
  const [dragOver, setDragOver] = useState<string | null>(null);

  const load = () => {
    apiFetch("/leads")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setLeads)
      .catch(() => undefined);
    apiFetch("/dashboard/summary")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setSummary)
      .catch(() => undefined);
  };

  useEffect(load, []);

  const changeStage = async (leadId: number, stageKey: string) => {
    const lead = leads.find((l) => l.id === leadId);
    if (!lead || lead.stage === stageKey) return;
    setLeads((current) => current.map((l) => (l.id === leadId ? { ...l, stage: stageKey } : l)));
    const response = await apiFetch(`/leads/${leadId}`, {
      method: "PUT",
      body: JSON.stringify({ stage: stageKey }),
    });
    if (!response.ok) {
      alert("Faza leada nije sačuvana.");
      load();
      return;
    }
    load();
  };

  const followupCount = leads.filter((l) => l.followup_due).length;

  return (
    <>
      <div className="funnel-summary card">
        <div className="funnel-metric">
          <span className="metric-label">Aktivni leadovi</span>
          <span className="metric-value">{summary.active_leads}</span>
        </div>
        <div className="funnel-metric">
          <span className="metric-label">Potencijalna vrednost</span>
          <span className="metric-value">{money(summary.potential_value)}</span>
        </div>
        <div className="funnel-metric">
          <span className="metric-label">Zatvoreno ovog meseca</span>
          <span className="metric-value">{money(summary.closed_this_month_value)}</span>
        </div>
        {followupCount > 0 && (
          <div className="funnel-metric funnel-alert">
            <span className="metric-label">Follow-up potreban</span>
            <span className="metric-value">{followupCount}</span>
          </div>
        )}
      </div>

      <div className="kanban-scroll">
        <div className="kanban-board">
          {stages.map((label) => {
            const stageKey = stageKeys[label];
            const stageLeads = leads.filter((lead) => lead.stage === stageKey);
            const stageValue = stageLeads.reduce((sum, lead) => sum + (lead.value || 0), 0);
            return (
              <div
                className={`kanban-column${dragOver === stageKey ? " drag-over" : ""}`}
                key={label}
                onDragOver={(e) => {
                  e.preventDefault();
                  setDragOver(stageKey);
                }}
                onDragLeave={() => setDragOver((current) => (current === stageKey ? null : current))}
                onDrop={(e) => {
                  e.preventDefault();
                  setDragOver(null);
                  const id = Number(e.dataTransfer.getData("text/plain"));
                  if (id) changeStage(id, stageKey);
                }}
              >
                <div className="kanban-column-header">
                  <strong>{label}</strong>
                  <span className="badge">{stageLeads.length}</span>
                </div>
                <span className="kanban-column-value">{money(stageValue)}</span>
                <div className="kanban-cards">
                  {stageLeads.map((lead) => (
                    <div
                      className={`lead-card${dragging === lead.id ? " dragging" : ""}`}
                      key={lead.id}
                      draggable
                      onDragStart={(e) => {
                        e.dataTransfer.setData("text/plain", String(lead.id));
                        setDragging(lead.id);
                      }}
                      onDragEnd={() => setDragging(null)}
                      onClick={() => setOpenLead(lead.id)}
                    >
                      <div className="lead-card-top">
                        <strong>{lead.contact_name}</strong>
                        <span className="lead-card-value">{lead.value != null ? money(lead.value) : "Bez vrednosti"}</span>
                      </div>
                      <div className="lead-card-meta">
                        <span>{channelLabels[lead.contact_source] || lead.contact_source}</span>
                        {lead.contact_owner && <span><User size={12} /> {lead.contact_owner}</span>}
                      </div>
                      {lead.next_activity && (
                        <div className="lead-card-reminder">
                          <CalendarClock size={13} />
                          <span>
                            {lead.next_activity}
                            {lead.next_activity_at ? ` · ${formatReminder(lead.next_activity_at)}` : ""}
                          </span>
                        </div>
                      )}
                      {lead.followup_due && (
                        <div className="lead-card-followup">
                          <AlertTriangle size={13} /> Follow-up bez odgovora
                        </div>
                      )}
                    </div>
                  ))}
                  {!stageLeads.length && <p className="muted-line">Nema leadova.</p>}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {openLead !== null && (
        <LeadDrawer leadId={openLead} onClose={() => setOpenLead(null)} onChanged={load} />
      )}
    </>
  );
}
