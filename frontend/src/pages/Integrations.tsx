import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { channelLabels, IntegrationItem } from "../types";

const demoIntegrations: IntegrationItem[] = Object.keys(channelLabels)
  .filter((channel) => channel !== "manual")
  .map((channel) => ({ channel, status: "Nije povezano" }));

export function Integrations() {
  const [integrations, setIntegrations] = useState<IntegrationItem[]>(demoIntegrations);

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
    if (nextStatus === "Povezano") {
      const confirmed = window.confirm(
        `Ovo je demo simulacija: status kanala „${channelLabels[item.channel] || item.channel}" će biti promenjen u „Povezano", ali se time NE uspostavlja prava konekcija (OAuth/API) sa tim nalogom.\n\nDa li želite da nastavite?`
      );
      if (!confirmed) return;
    }
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
      <div className="integration-demo-banner">
        <strong>Demo režim:</strong> status kanala ispod je simulacija. Dugme „Podesi"/„Isključi" samo menja zapis u bazi i ne
        uspostavlja pravu konekciju (OAuth/API) sa Facebook, Instagram, Viber ili Email nalogom.
      </div>
      <div className="kpis integrations-grid">
        {integrations.map((item) => (
          <section className="card" key={item.channel}>
            <h2>{channelLabels[item.channel] || item.channel}</h2>
            <span className={`badge ${item.status === "Povezano" ? "" : item.status === "Greška" ? "danger" : "neutral"}`}>{item.status}</span>
            <p className="muted-line">Simulirani status — bez prave konekcije</p>
            <button className="configure-button" onClick={() => toggle(item)}>
              {item.status === "Povezano" ? "Isključi" : "Podesi"}
            </button>
          </section>
        ))}
      </div>
    </>
  );
}
