import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { TrendingUp, MoreHorizontal, ChevronsLeft, ChevronsRight } from "lucide-react";

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

const demoContacts = [
  { name: "Sarah Johnson", sub: "IRA 100k", date: "2 Oct", status: "Qualified", statusClass: "status-qualified" },
  { name: "Michael Chen", sub: "IRA 75k", date: "1 Oct", status: "Hot", statusClass: "status-hot" },
  { name: "Emma Wilson", sub: "IRA 50k", date: "30 Sep", status: "Qualified", statusClass: "status-qualified" },
  { name: "James Brown", sub: "IRA 25k", date: "29 Sep", status: "Qualified", statusClass: "status-yellow-green" },
];

export function Dashboard() {
  const [summary, setSummary] = useState<Summary>(emptySummary);

  useEffect(() => {
    apiFetch("/dashboard/summary")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setSummary)
      .catch(() => undefined);
  }, []);

  const metrics = [
    { label: "Total Revenue", value: "$2,445,744", trend: "+8.2% ↑", trendClass: "trend-green" },
    { label: "Avg Deal Size", value: "$489,149", trend: null, trendClass: "" },
    { label: "Total Clients", value: "5", trend: "+20% ↑", trendClass: "trend-green" },
    { label: "Total Invoices", value: "31", trend: "+8.2% ↑", trendClass: "trend-pink" },
  ];

  return (
    <>
      <div className="demo-banner">
        <strong>Demo režim:</strong> Ovo je razvojno okruženje sa test podacima.
      </div>
      <div className="metrics-grid">
        {metrics.map((m) => (
          <div className="metric-card" key={m.label}>
            <span className="metric-label">{m.label}</span>
            <span className="metric-value">{m.value}</span>
            {m.trend && (
              <span className={`metric-trend ${m.trendClass}`}>
                <TrendingUp size={14} /> {m.trend}
              </span>
            )}
          </div>
        ))}
      </div>
      <div className="bottom-row-wide">
        <div className="card">
          <h2>Prospects to Watch</h2>
          <div className="contact-list">
            {demoContacts.map((c) => (
              <div className="contact-row" key={c.name}>
                <div>
                  <div className="contact-name">{c.name}</div>
                  <div className="contact-sub">
                    <span>📌</span> {c.sub}
                  </div>
                </div>
                <span className="contact-date">{c.date}</span>
                <span className={`contact-status ${c.statusClass}`}>{c.status}</span>
                <span className="contact-actions"><MoreHorizontal size={16} /></span>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <div className="calendar-header">
            <h2>Upcoming Meetings</h2>
            <div className="calendar-nav">
              <button><ChevronsLeft size={16} /></button>
              <span className="calendar-month">November 2025</span>
              <button><ChevronsRight size={16} /></button>
            </div>
          </div>
          <div className="date-strip">
            {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((d) => (
              <div className="day" key={d}>{d === 'Thu' ? '9' : ''}</div>
            ))}
          </div>
          <div className="meetings-list">
            <div className="meeting-card yellow">
              <div className="meeting-info">
                <div className="meeting-name">Meeting With John Doe</div>
                <div className="meeting-time">10:00 - 11:00 AM</div>
              </div>
              <span className="meeting-dots"><MoreHorizontal size={16} /></span>
            </div>
            <div className="meeting-card pink">
              <div className="meeting-info">
                <div className="meeting-name">Meeting With Michelle</div>
                <div className="meeting-time">12:00 - 01:00 PM</div>
              </div>
              <span className="meeting-dots"><MoreHorizontal size={16} /></span>
            </div>
          </div>
          <div className="calendar-footer">Fri, Nov 19</div>
        </div>
      </div>
      <div className="bookmark-card">
        <div>
          <div className="bookmark-title">Bookmarked Prospects</div>
          <div className="bookmark-subtitle">You have 39 prospects bookmarked</div>
        </div>
        <span className="bookmark-count">39</span>
      </div>
    </>
  );
}
