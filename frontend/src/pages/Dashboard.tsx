import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { ChevronsLeft, ChevronsRight, Plus } from "lucide-react";
import { DashboardSummary, stageLabels } from "../types";
import { MeetingModal, MeetingContactOption } from "../components/MeetingModal";

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

type Prospect = {
  lead_id: number;
  contact_id: number;
  name: string;
  stage: string;
  value: number | null;
  updated_at: string;
};

type Meeting = {
  id: number;
  contact_id: number | null;
  contact_name: string | null;
  title: string;
  start_at: string;
  end_at: string;
};

type SetupStep = { key: string; title: string; done: boolean };
type SetupStatus = { configured: boolean; steps: SetupStep[] };

const monthNames = [
  "Januar", "Februar", "Mart", "April", "Maj", "Jun",
  "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar",
];
const dayLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

const stageStatusClass: Record<string, string> = {
  new_inquiry: "status-hot",
  contacted: "status-qualified",
  offer_sent: "status-qualified",
  negotiation: "status-yellow-green",
  waiting_response: "status-yellow-green",
  deal_won: "status-scheduled",
  scheduled: "status-scheduled",
  paid: "status-scheduled",
  deal_lost: "status-lost",
  scheduled_paid: "status-scheduled",
};

function startOfWeek(date: Date): Date {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  return d;
}

function addDays(date: Date, amount: number): Date {
  const d = new Date(date);
  d.setDate(d.getDate() + amount);
  return d;
}

function sameDate(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

function pad(n: number): string {
  return n.toString().padStart(2, "0");
}

function toLocalIso(date: Date, hours = 0, minutes = 0): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(hours)}:${pad(minutes)}:00`;
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return `${d.getDate()} ${monthNames[d.getMonth()].slice(0, 3)}`;
}

export function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary>(emptySummary);
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [weekStart, setWeekStart] = useState(() => startOfWeek(new Date()));
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [contacts, setContacts] = useState<MeetingContactOption[]>([]);
  const [addMeeting, setAddMeeting] = useState(false);
  const [setup, setSetup] = useState<SetupStatus>({ configured: true, steps: [] });

  useEffect(() => {
    apiFetch("/dashboard/summary")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setSummary)
      .catch(() => undefined);
    apiFetch("/dashboard/prospects?limit=5")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setProspects)
      .catch(() => undefined);
    apiFetch("/contacts")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((items: { id: number; name: string }[]) => setContacts(items.map((c) => ({ id: c.id, name: c.name }))))
      .catch(() => undefined);
    apiFetch("/dashboard/setup")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setSetup)
      .catch(() => undefined);
  }, []);

  const loadMeetings = () => {
    const weekEnd = addDays(weekStart, 7);
    apiFetch(`/meetings?start=${toLocalIso(weekStart)}&end=${toLocalIso(weekEnd)}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setMeetings)
      .catch(() => undefined);
  };

  useEffect(loadMeetings, [weekStart]);

  const submitMeeting = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const date = String(data.get("date"));
    const startTime = String(data.get("start_time"));
    const endTime = String(data.get("end_time"));
    const contactId = String(data.get("contact_id") || "");
    const response = await apiFetch("/meetings", {
      method: "POST",
      body: JSON.stringify({
        title: String(data.get("title") || "").trim(),
        contact_id: contactId ? Number(contactId) : null,
        start_at: `${date}T${startTime}:00`,
        end_at: `${date}T${endTime}:00`,
      }),
    });
    if (!response.ok) {
      alert("Sastanak nije sačuvan. Provera: vreme završetka mora biti posle početka.");
      return;
    }
    setAddMeeting(false);
    loadMeetings();
  };

  const metrics = [
    { label: "Novi upiti", value: summary.new_inquiries },
    { label: "Aktivni leadovi", value: summary.active_leads },
    { label: "Ponude poslate", value: summary.proposals_sent },
    { label: "Dobijeni poslovi", value: summary.won },
  ];

  const today = new Date();
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  const meetingCardColors = ["yellow", "pink"];

  return (
    <>
      {!setup.configured && (
        <div className="card setup-card">
          <h2>Aktivacija aplikacije</h2>
          <p className="card-subtitle">Koraci za prvi dan rada sa CRM-om — detaljna uputstva u <code>docs/production-v1.md</code></p>
          <ul className="setup-list">
            {setup.steps.map((step) => (
              <li key={step.key} className={step.done ? "done" : undefined}>
                <span className={`setup-check ${step.done ? "done" : ""}`}>{step.done ? "✓" : "·"}</span>
                {step.title}
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="funnel-summary card">
        <div className="funnel-metric">
          <span className="metric-label">Aktivni leadovi</span>
          <span className="metric-value">{summary.active_leads}</span>
        </div>
        <div className="funnel-metric">
          <span className="metric-label">Potencijalna vrednost</span>
          <span className="metric-value">{summary.potential_value.toLocaleString("sr-RS")} RSD</span>
        </div>
        <div className="funnel-metric">
          <span className="metric-label">Zatvoreno ovog meseca</span>
          <span className="metric-value">{summary.closed_this_month_value.toLocaleString("sr-RS")} RSD</span>
        </div>
      </div>
      <div className="card metrics-card">
        <div className="metrics-card-header">
          <h2>Pregled prodajnog levka</h2>
          <p className="card-subtitle">{today.getDate()} {monthNames[today.getMonth()]} {today.getFullYear()}</p>
        </div>
        <div className="metrics-row">
          {metrics.map((m) => (
            <div className="metric-col" key={m.label}>
              <span className="metric-label">{m.label}</span>
              <div className="metric-value-row">
                <span className="metric-value">{m.value}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="card stats-card">
        <h2>Statistika prodaje</h2>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="metric-label">Procenat zatvorenih poslova</span>
            <span className="stat-value">{summary.win_rate != null ? `${summary.win_rate}%` : "—"}</span>
          </div>
          <div className="stat-item">
            <span className="metric-label">Prosečno vreme do prodaje</span>
            <span className="stat-value">
              {summary.avg_time_to_sale_days != null ? `${summary.avg_time_to_sale_days} dana` : "—"}
            </span>
          </div>
          <div className="stat-item">
            <span className="metric-label">Izgubljeni poslovi</span>
            <span className="stat-value">{summary.lost}</span>
          </div>
          <div className="stat-item stat-reasons">
            <span className="metric-label">Razlozi gubitka</span>
            {summary.lost_reasons.length === 0 && <span className="muted-line">Nema zabeleženih gubitaka.</span>}
            {summary.lost_reasons.map((r) => (
              <span className="stat-reason" key={r.reason}>
                {r.reason} <strong>{r.count}</strong>
              </span>
            ))}
          </div>
        </div>
      </div>
      <div className="bottom-row-wide">
        <div className="card">
          <h2>Prospects to Watch</h2>
          <p className="card-subtitle contact-list-subtitle">Najnovije aktivnosti u levku</p>
          <div className="contact-list">
            {prospects.length === 0 && <p className="dropdown-empty">Nema aktivnih leadova.</p>}
            {prospects.map((p) => (
              <div className="contact-row" key={p.lead_id}>
                <div className="contact-main">
                  <div className="contact-name">{p.name}</div>
                  <div className="contact-sub">
                    {p.value != null ? `Vrednost: ${p.value.toLocaleString("sr-RS")} RSD` : "Bez unete vrednosti"}
                  </div>
                </div>
                <div className="contact-field">
                  <span className="contact-field-label">Poslednja izmena</span>
                  <span className="contact-date">{formatDate(p.updated_at)}</span>
                </div>
                <div className="contact-field">
                  <span className="contact-field-label">Status</span>
                  <span className={`contact-status ${stageStatusClass[p.stage] || "status-qualified"}`}>
                    {stageLabels[p.stage] || p.stage}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="calendar-header">
            <h2>Upcoming Meetings</h2>
            <div className="calendar-nav">
              <button type="button" onClick={() => setWeekStart((d) => addDays(d, -7))}>
                <ChevronsLeft size={16} />
              </button>
              <span className="calendar-month">{monthNames[weekStart.getMonth()]} {weekStart.getFullYear()}</span>
              <button type="button" onClick={() => setWeekStart((d) => addDays(d, 7))}>
                <ChevronsRight size={16} />
              </button>
              <button type="button" onClick={() => setAddMeeting(true)} aria-label="Dodaj sastanak">
                <Plus size={16} />
              </button>
            </div>
          </div>
          <div className="date-strip">
            {weekDays.map((d, i) => (
              <div className="date-col" key={i}>
                <span className="date-col-label">{dayLabels[i]}</span>
                <div className={`day ${sameDate(d, today) ? "active" : ""}`}>{d.getDate()}</div>
              </div>
            ))}
          </div>
          <p className="calendar-today-label">
            {weekDays.some((d) => sameDate(d, today)) ? "Ova nedelja" : "Izabrana nedelja"}
          </p>
          <div className="meetings-list">
            {meetings.length === 0 && <p className="dropdown-empty">Nema zakazanih sastanaka.</p>}
            {meetings.map((m, i) => (
              <div className={`meeting-card ${meetingCardColors[i % meetingCardColors.length]}`} key={m.id}>
                <div className="meeting-info">
                  <div className="meeting-name">{m.title}{m.contact_name ? ` — ${m.contact_name}` : ""}</div>
                  <div className="meeting-time">{formatTime(m.start_at)} - {formatTime(m.end_at)}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="calendar-footer">
            {meetings.length > 0 ? `${meetings.length} sastanak(a) ove nedelje` : "Nema zakazanih sastanaka ove nedelje"}
          </div>
        </div>
      </div>
      {addMeeting && (
        <MeetingModal contacts={contacts} onClose={() => setAddMeeting(false)} onSubmit={submitMeeting} />
      )}
    </>
  );
}
