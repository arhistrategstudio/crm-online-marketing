import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

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

export function Dashboard() {
  const [summary, setSummary] = useState<Summary>(emptySummary);

  useEffect(() => {
    apiFetch("/dashboard/summary")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setSummary)
      .catch(() => undefined);
  }, []);

  const cards: [string, string | number][] = [
    ["Novi upiti", summary.new_inquiries],
    ["Aktivni leadovi", summary.active_leads],
    ["Poslate ponude", summary.offers_sent],
    ["Zakazano / Plaćeno", summary.scheduled_paid],
    ["Aktivne kampanje", summary.campaigns_active],
    ["Cena po leadu", summary.avg_cost_per_lead !== null ? `${summary.avg_cost_per_lead} RSD` : "—"],
  ];

  return (
    <>
      <div className="kpis">
        {cards.map(([label, value]) => (
          <div className="card" key={label}>
            <small>{label}</small>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      <section className="card">
        <h2>Pregled prodaje</h2>
        <div className="chart">▁▃▂▅▄▆▇</div>
      </section>
    </>
  );
}
