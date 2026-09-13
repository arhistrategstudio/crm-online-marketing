export type Page = "Dashboard" | "Inbox" | "Kontakti" | "Prodajni levak" | "Kampanje" | "Integracije" | "Podešavanja";

export type ContactItem = { id: number; name: string; source: string; phone: string };

export type IntegrationItem = { channel: string; status: string };

export type CampaignChannel = "facebook" | "instagram" | "viber" | "email" | "manual";

export type CampaignStatus = "draft" | "active" | "paused" | "completed";

export type CampaignItem = {
  id: number;
  name: string;
  channel: CampaignChannel;
  status: CampaignStatus;
  budget: number;
  spend: number;
  leads_count: number;
  cost_per_lead: number | null;
  conversion_rate: number | null;
};

export type AuthUser = {
  id: number;
  name: string;
  email: string;
  role: string;
  status: string;
  auth_provider: string;
  has_password: boolean;
  created_at: string;
};

export const stages = ["Stigao upit", "Poslata ponuda", "Čekamo odgovor", "Zakazano / Plaćeno"] as const;

export const stageKeys = {
  "Stigao upit": "new_inquiry",
  "Poslata ponuda": "offer_sent",
  "Čekamo odgovor": "waiting_response",
  "Zakazano / Plaćeno": "scheduled_paid",
} as const;

export const stageLabels: Record<string, string> = Object.fromEntries(
  Object.entries(stageKeys).map(([label, key]) => [key, label]),
);

export const channelLabels: Record<string, string> = {
  facebook: "Facebook",
  instagram: "Instagram",
  viber: "Viber",
  email: "Email",
  manual: "Ručno",
};

export const campaignStatusLabels: Record<CampaignStatus, string> = {
  draft: "Priprema",
  active: "Aktivna",
  paused: "Pauzirana",
  completed: "Završena",
};
