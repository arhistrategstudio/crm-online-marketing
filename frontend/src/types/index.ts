export type Page = "Dashboard" | "Inbox" | "Kontakti" | "Prodajni levak" | "Kampanje" | "Integracije" | "Podešavanja";

export type ContactItem = {
  id: number;
  name: string;
  source: string;
  phone: string;
  email: string | null;
  owner: string | null;
  notes: string | null;
  status: string;
};

export type ConversationItem = {
  id: number;
  contact_id: number;
  contact_name: string;
  channel: string;
  unread_count: number;
  last_message: string | null;
  created_at: string;
};

export type LeadItem = {
  id: number;
  contact_id: number;
  contact_name: string;
  contact_phone: string | null;
  contact_email: string | null;
  contact_source: string;
  contact_owner: string | null;
  contact_notes: string | null;
  campaign_id: number | null;
  stage: string;
  value: number | null;
  lost_reason: string | null;
  next_activity: string | null;
  next_activity_at: string | null;
  followup_due: boolean;
  proposals_count: number;
  last_proposal_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ProposalItem = {
  id: number;
  lead_id: number;
  contact_id: number;
  title: string;
  amount: number;
  currency: string;
  items: string | null;
  notes: string | null;
  status: string;
  sent_at: string | null;
  created_at: string;
};

export type TimelineItem = {
  kind: string;
  title: string;
  detail: string | null;
  channel: string | null;
  created_at: string;
};

export type DashboardSummary = {
  new_inquiries: number;
  contacted: number;
  active_leads: number;
  potential_value: number;
  closed_this_month_value: number;
  offers_sent: number;
  proposals_sent: number;
  won: number;
  lost: number;
  win_rate: number | null;
  avg_time_to_sale_days: number | null;
  scheduled_paid: number;
  campaigns_active: number;
  avg_cost_per_lead: number | null;
  lost_reasons: { reason: string; count: number }[];
};

export type IntegrationItem = { channel: string; status: string };

export type CampaignChannel = "facebook" | "instagram" | "viber" | "email" | "manual" | "google" | "referral" | "phone" | "website";

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

export const stages = [
  "Novi upit",
  "Kontaktiran",
  "Poslata ponuda",
  "Pregovori",
  "Čekamo odgovor",
  "Dobijen posao",
  "Zakazano",
  "Plaćeno",
  "Izgubljen posao",
] as const;

export const stageKeys: Record<string, string> = {
  "Novi upit": "new_inquiry",
  Kontaktiran: "contacted",
  "Poslata ponuda": "offer_sent",
  Pregovori: "negotiation",
  "Čekamo odgovor": "waiting_response",
  "Dobijen posao": "deal_won",
  Zakazano: "scheduled",
  "Plaćeno": "paid",
  "Izgubljen posao": "deal_lost",
};

export const stageLabels: Record<string, string> = {
  new_inquiry: "Novi upit",
  contacted: "Kontaktiran",
  offer_sent: "Poslata ponuda",
  negotiation: "Pregovori",
  waiting_response: "Čekamo odgovor",
  deal_won: "Dobijen posao",
  scheduled: "Zakazano",
  paid: "Plaćeno",
  deal_lost: "Izgubljen posao",
  scheduled_paid: "Zakazano / Plaćeno",
};

export const leadSources = [
  { value: "instagram", label: "Instagram" },
  { value: "facebook", label: "Facebook Ads" },
  { value: "google", label: "Google" },
  { value: "referral", label: "Preporuka" },
  { value: "phone", label: "Telefon" },
  { value: "website", label: "Sajt" },
  { value: "viber", label: "Viber" },
  { value: "email", label: "Email" },
  { value: "manual", label: "Ručno" },
] as const;

export const channelLabels: Record<string, string> = {
  facebook: "Facebook",
  instagram: "Instagram",
  viber: "Viber",
  email: "Email",
  manual: "Ručno",
  google: "Google",
  referral: "Preporuka",
  phone: "Telefon",
  website: "Sajt",
};

export const campaignStatusLabels: Record<CampaignStatus, string> = {
  draft: "Priprema",
  active: "Aktivna",
  paused: "Pauzirana",
  completed: "Završena",
};
