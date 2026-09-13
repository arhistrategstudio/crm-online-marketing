import { FormEvent, useEffect, useState } from "react";
import { X } from "lucide-react";
import { apiFetch } from "../lib/api";
import { LeadItem, ProposalItem, TimelineItem, channelLabels, stageKeys, stageLabels, stages } from "../types";
import { ProposalModal, proposalToPdf } from "./ProposalModal";

function toInputDateTime(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("sr-RS", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

function money(value: number | null): string {
  return value != null ? `${value.toLocaleString("sr-RS")} RSD` : "—";
}

const timelineKindLabel: Record<string, string> = {
  message: "Poruka",
  activity: "Aktivnost",
  proposal: "Ponuda",
  note: "Beleška",
  call: "Poziv",
  email: "Email",
  stage_change: "Promena faze",
};

export function LeadDrawer({
  leadId,
  onClose,
  onChanged,
}: {
  leadId: number;
  onClose: () => void;
  onChanged: () => void;
}) {
  const [lead, setLead] = useState<LeadItem | null>(null);
  const [history, setHistory] = useState<TimelineItem[]>([]);
  const [proposals, setProposals] = useState<ProposalItem[]>([]);
  const [showProposal, setShowProposal] = useState(false);

  const load = () => {
    apiFetch(`/leads/${leadId}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setLead)
      .catch(() => undefined);
    apiFetch(`/leads/${leadId}/history`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setHistory)
      .catch(() => undefined);
    apiFetch(`/leads/${leadId}/proposals`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setProposals)
      .catch(() => undefined);
  };

  useEffect(load, [leadId]);

  const saveEdits = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const nextAt = String(data.get("next_activity_at") || "");
    const response = await apiFetch(`/leads/${leadId}`, {
      method: "PUT",
      body: JSON.stringify({
        stage: String(data.get("stage")),
        value: data.get("value") ? Number(data.get("value")) : null,
        next_activity: String(data.get("next_activity") || "").trim() || null,
        next_activity_at: nextAt ? `${nextAt}:00` : null,
        lost_reason: String(data.get("lost_reason") || "").trim() || null,
        contact_owner: String(data.get("contact_owner") || "").trim() || null,
        contact_notes: String(data.get("contact_notes") || "").trim() || null,
      }),
    });
    if (!response.ok) {
      alert("Izmene nisu sačuvane.");
      return;
    }
    setLead(await response.json());
    load();
    onChanged();
  };

  const addActivity = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const description = String(data.get("description") || "").trim();
    if (!description) return;
    const response = await apiFetch(`/leads/${leadId}/activities`, {
      method: "POST",
      body: JSON.stringify({ type: String(data.get("type") || "note"), description }),
    });
    if (!response.ok) {
      alert("Aktivnost nije sačuvana.");
      return;
    }
    form.reset();
    load();
    onChanged();
  };

  const prepareFollowup = async () => {
    if (!lead) return;
    const message = `Zdravo ${lead.contact_name}, javljam se u vezi poslate ponude${
      lead.last_proposal_at ? ` (${formatDateTime(lead.last_proposal_at)})` : ""
    }. Da li imate pitanja ili vam treba dodatna informacija kako bismo nastavili saradnju?`;
    try {
      await navigator.clipboard.writeText(message);
      alert(`Predlog follow-up poruke je kopiran:\n\n${message}`);
    } catch {
      alert(`Predlog follow-up poruke:\n\n${message}`);
    }
  };

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div>
            <h2>{lead?.contact_name || "Učitavanje..."}</h2>
            <p className="muted-line">
              {lead ? `${stageLabels[lead.stage] || lead.stage} · ${money(lead.value)}` : ""}
            </p>
          </div>
          <button className="icon-btn" onClick={onClose} aria-label="Zatvori"><X size={18} /></button>
        </div>

        {lead && (
          <>
            <div className="drawer-contact">
              <div><span>Telefon</span><strong>{lead.contact_phone || "Nije unet"}</strong></div>
              <div><span>Mejl</span><strong>{lead.contact_email || "Nije unet"}</strong></div>
              <div><span>Izvor</span><strong>{channelLabels[lead.contact_source] || lead.contact_source}</strong></div>
              <div><span>Odgovorna osoba</span><strong>{lead.contact_owner || "Nije dodeljena"}</strong></div>
            </div>

            {lead.followup_due && (
              <div className="followup-alert">
                <strong>Follow-up potreban:</strong> ponuda je poslata, a nema odgovora već više dana.
                <button type="button" onClick={prepareFollowup}>Pripremi poruku</button>
              </div>
            )}

            <form className="drawer-form" onSubmit={saveEdits} key={`${lead.id}-${lead.updated_at}`}>
              <div className="drawer-grid">
                <label>
                  Faza
                  <select name="stage" defaultValue={lead.stage}>
                    {stages.map((label) => (
                      <option key={label} value={stageKeys[label]}>{label}</option>
                    ))}
                    {lead.stage === "scheduled_paid" && <option value="scheduled_paid">Zakazano / Plaćeno</option>}
                  </select>
                </label>
                <label>
                  Vrednost (RSD)
                  <input name="value" type="number" min="0" defaultValue={lead.value ?? ""} placeholder="0" />
                </label>
                <label>
                  Sledeća aktivnost
                  <input name="next_activity" defaultValue={lead.next_activity ?? ""} placeholder="npr. Pozvati klijenta" />
                </label>
                <label>
                  Podsetnik
                  <input name="next_activity_at" type="datetime-local" defaultValue={toInputDateTime(lead.next_activity_at)} />
                </label>
                <label>
                  Odgovorna osoba
                  <input name="contact_owner" defaultValue={lead.contact_owner ?? ""} placeholder="Ime prodavca" />
                </label>
                <label>
                  Razlog gubitka
                  <input name="lost_reason" defaultValue={lead.lost_reason ?? ""} placeholder="npr. Preskupo" />
                </label>
              </div>
              <label className="full">
                Kratka beleška
                <textarea name="contact_notes" rows={2} defaultValue={lead.contact_notes ?? ""} placeholder="Beleška o klijentu..." />
              </label>
              <div className="form-actions">
                <button type="submit">Sačuvaj izmene</button>
              </div>
            </form>

            <div className="drawer-section-head">
              <h3>Ponude ({proposals.length})</h3>
              <button type="button" className="accent-btn" onClick={() => setShowProposal(true)}>Kreiraj ponudu</button>
            </div>
            <div className="proposal-list">
              {!proposals.length && <p className="muted-line">Još uvek nema ponuda.</p>}
              {proposals.map((p) => (
                <div className="proposal-row" key={p.id}>
                  <div>
                    <strong>{p.title}</strong>
                    <span className="muted-line">
                      {p.amount.toLocaleString("sr-RS")} {p.currency} · poslata {p.sent_at ? formatDateTime(p.sent_at) : "—"}
                    </span>
                  </div>
                  <button type="button" onClick={() => lead && proposalToPdf(p, lead.contact_name, lead.contact_email)}>
                    PDF
                  </button>
                </div>
              ))}
            </div>

            <div className="drawer-section-head">
              <h3>Nova aktivnost</h3>
            </div>
            <form className="drawer-form inline" onSubmit={addActivity}>
              <select name="type" defaultValue="note">
                <option value="note">Beleška</option>
                <option value="call">Poziv</option>
                <option value="email">Email</option>
                <option value="meeting">Sastanak</option>
              </select>
              <input name="description" placeholder="Šta je urađeno / sledeći korak" />
              <button type="submit">Dodaj</button>
            </form>

            <div className="drawer-section-head">
              <h3>Istorija komunikacije</h3>
            </div>
            <div className="timeline">
              {!history.length && <p className="muted-line">Nema zabeležene komunikacije.</p>}
              {history.map((item, i) => (
                <div className={`timeline-item kind-${item.kind}`} key={i}>
                  <div className="timeline-dot" />
                  <div className="timeline-body">
                    <strong>
                      {item.kind === "message" ? (item.title || "Poruka") : (timelineKindLabel[item.kind] || item.kind)}
                      {item.channel ? ` · ${channelLabels[item.channel] || item.channel}` : ""}
                    </strong>
                    {item.detail && <p>{item.detail}</p>}
                    <span className="muted-line">{formatDateTime(item.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
      {showProposal && lead && (
        <ProposalModal
          leadId={lead.id}
          contactName={lead.contact_name}
          onClose={() => setShowProposal(false)}
          onSaved={(proposal) => {
            setShowProposal(false);
            load();
            onChanged();
            proposalToPdf(proposal, lead.contact_name, lead.contact_email);
          }}
        />
      )}
    </div>
  );
}
