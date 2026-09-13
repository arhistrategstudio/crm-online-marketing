import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { ChevronsLeft, ChevronsRight, Plus } from "lucide-react";
import { stageLabels } from "../types";
import { MeetingModal, MeetingContactOption } from "../components/MeetingModal";

type Summary = {
  new_inquiries: number;
  active_leads: number;
  offers_sent: number;
  scheduled_paid: number;
  campaigns_active: number;
  avg_cost_per_lead: number | null;
};

const emptySummary: Summary = {
  new_inquiries: 0,
  active_leads: 0,
  offers_sent: 0,
  scheduled_paid: 0,
  campaigns_active: 0,
  avg_cost_per_lead: null,
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

const monthNames = [
  "Januar", "Februar", "Mart", "April", "Maj", "Jun",
  "Jul", "Avgust", "Septembar", "Oktobar", "Novembar", "Decembar",
];
const dayLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

const stageStatusClass: Record<string, string> = {
  new_inquiry: "status-hot",
  offer_sent: "status-qualified",
  waiting_response: "status-yellow-green",
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
  const [summary, setSummary] = useState<Summary>(emptySummary);
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [weekStart, setWeekStart] = useState(() => startOfWeek(new Date()));
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [contacts, setContacts] = useState<MeetingContactOption[]>([]);
  const [addMeeting, setAddMeeting] = useState(false);

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
    { label: "Ponude poslate", value: summary.offers_sent },
    { label: "Zakazano / Plaćeno", value: summary.scheduled_paid },
  ];

  const today = new Date();
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  const meetingCardColors = ["yellow", "pink"];

  return (
    <>
      <div className="demo-banner">
        <strong>Demo režim:</strong> Ovo je razvojno okruženje sa test podacima.
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
