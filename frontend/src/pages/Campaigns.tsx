import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { CampaignItem, campaignStatusLabels, channelLabels } from "../types";
import { CampaignModal } from "../components/CampaignModal";

const statusBadgeClass: Record<string, string> = {
  active: "",
  draft: "neutral",
  paused: "neutral",
  completed: "neutral",
};

export function Campaigns() {
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [addCampaign, setAddCampaign] = useState(false);

  const load = () => {
    apiFetch("/campaigns")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setCampaigns)
      .catch(() => undefined);
  };

  useEffect(load, []);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const name = String(data.get("name") || "").trim();
    if (!name) return;
    const response = await apiFetch("/campaigns", {
      method: "POST",
      body: JSON.stringify({
        name,
        channel: data.get("channel"),
        status: data.get("status"),
        budget: Number(data.get("budget") || 0),
        spend: Number(data.get("spend") || 0),
      }),
    });
    if (!response.ok) {
      alert("Kampanja nije sačuvana.");
      return;
    }
    setAddCampaign(false);
    load();
  };

  return (
    <>
      <div className="contact-toolbar">
        <p className="subtitle">Praćenje reklamnih kampanja i njihove efikasnosti po leadu.</p>
        <button onClick={() => setAddCampaign(true)}>Nova kampanja</button>
      </div>
      <section className="card table campaigns-table">
        {campaigns.map((campaign) => (
          <div className="row campaign-row" key={campaign.id}>
            <div>
              <strong>{campaign.name}</strong>
              <span className="muted-line">{channelLabels[campaign.channel] || campaign.channel}</span>
            </div>
            <span className={`badge ${statusBadgeClass[campaign.status] ?? "neutral"}`}>{campaignStatusLabels[campaign.status]}</span>
            <span>{campaign.spend.toLocaleString("sr-RS")} / {campaign.budget.toLocaleString("sr-RS")} RSD</span>
            <span>{campaign.leads_count} leadova</span>
            <span>{campaign.cost_per_lead !== null ? `${campaign.cost_per_lead} RSD/lead` : "—"}</span>
            <span>{campaign.conversion_rate !== null ? `${campaign.conversion_rate}% konverzija` : "—"}</span>
          </div>
        ))}
        {!campaigns.length && <div className="row"><span>Još uvek nema kreiranih kampanja.</span></div>}
      </section>
      {addCampaign && <CampaignModal onClose={() => setAddCampaign(false)} onSubmit={submit} />}
    </>
  );
}
