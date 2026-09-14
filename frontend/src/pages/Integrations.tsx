import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { channelLabels, IntegrationItem } from "../types";

export function Integrations() {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>([]);

  useEffect(() => {
    apiFetch("/integrations")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((items) => {
        if (items.length) setIntegrations(items.map((i: { channel: string; status: string }) => ({ channel: i.channel, status: i.status })));
      })
      .catch(() => undefined);
  }, []);

  const toggle = async (item: IntegrationItem) => {
    const nextStatus = item.status === "Povezano" ? "Nije povezano" : "Povezano";
    const response = await apiFetch(`/integrations/${item.channel}`, {
      method: "PUT",
      body: JSON.stringify({ status: nextStatus, configuration: null }),
    });
    if (!response.ok) {
      alert("Status integracije nije sačuvan.");
      return;
    }
    const saved = await response.json();
    setIntegrations(integrations.map((i) => (i.channel === item.channel ? { channel: saved.channel, status: saved.status } : i)));
  };

  return (
    <>
      <div className="kpis integrations-grid">
        {integrations.map((item) => (
          <section className="card" key={item.channel}>
            <h2>{channelLabels[item.channel] || item.channel}</h2>
            <span className={`badge ${item.status === "Povezano" ? "" : item.status === "Greška" ? "danger" : "neutral"}`}>{item.status}</span>
            <p className="muted-line">Status se čuva u aplikaciji. Stvarno povezivanje kanala (Meta/Viber) zahteva API token — uputstva u docs/production-v1.md</p>
            <button className="configure-button" onClick={() => toggle(item)}>
              {item.status === "Povezano" ? "Isključi" : "Poveži"}
            </button>
          </section>
        ))}
      </div>
    </>
  );
}
