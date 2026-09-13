import { FormEvent } from "react";
import { apiFetch } from "../lib/api";
import { ProposalItem } from "../types";

export function proposalToPdf(proposal: ProposalItem, contactName: string, contactEmail: string | null): void {
  const win = window.open("", "_blank", "width=800,height=1000");
  if (!win) {
    alert("Pregledač je blokirao otvaranje PDF prikaza. Dozvolite iskačuće prozore.");
    return;
  }
  const sentAt = proposal.sent_at ? new Date(proposal.sent_at).toLocaleDateString("sr-RS") : "-";
  win.document.write(`<!doctype html><html lang="sr"><head><meta charset="utf-8" />
    <title>Ponuda ${proposal.title}</title>
    <style>
      body { font-family: Arial, sans-serif; color: #111; padding: 48px; }
      h1 { font-size: 28px; margin-bottom: 4px; }
      .muted { color: #666; font-size: 13px; }
      table { width: 100%; border-collapse: collapse; margin-top: 32px; }
      th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }
      .total { font-size: 20px; font-weight: bold; text-align: right; margin-top: 24px; }
      .box { background: #f4f4f2; border-radius: 10px; padding: 16px; margin-top: 24px; }
      .note { white-space: pre-wrap; }
    </style></head><body>
    <h1>Ponuda</h1>
    <p class="muted">Datum slanja: ${sentAt}</p>
    <div class="box">
      <strong>Klijent:</strong> ${contactName}<br />
      ${contactEmail ? `<strong>Email:</strong> ${contactEmail}` : ""}
    </div>
    <h2>${proposal.title}</h2>
    <table>
      <tr><th>Opis / usluga</th><th>Iznos</th></tr>
      <tr><td class="note">${proposal.items || proposal.title}</td><td>${proposal.amount.toLocaleString("sr-RS")} ${proposal.currency}</td></tr>
    </table>
    <p class="total">Ukupno: ${proposal.amount.toLocaleString("sr-RS")} ${proposal.currency}</p>
    ${proposal.notes ? `<div class="box"><strong>Napomena:</strong><p class="note">${proposal.notes}</p></div>` : ""}
    </body></html>`);
  win.document.close();
  win.focus();
  win.print();
}

export function ProposalModal({
  leadId,
  contactName,
  onClose,
  onSaved,
}: {
  leadId: number;
  contactName: string;
  onClose: () => void;
  onSaved: (proposal: ProposalItem) => void;
}) {
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const response = await apiFetch(`/leads/${leadId}/proposals`, {
      method: "POST",
      body: JSON.stringify({
        title: String(data.get("title") || "").trim(),
        amount: Number(data.get("amount") || 0),
        currency: String(data.get("currency") || "RSD"),
        items: String(data.get("items") || "").trim() || null,
        notes: String(data.get("notes") || "").trim() || null,
      }),
    });
    if (!response.ok) {
      alert("Ponuda nije sačuvana. Proverite podatke.");
      return;
    }
    onSaved(await response.json());
  };

  return (
    <div className="modal" onClick={onClose}>
      <form className="command-menu contact-modal" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <h2>Kreiraj ponudu — {contactName}</h2>
        <label>
          Naziv usluge / ponude
          <input name="title" required autoFocus placeholder="npr. SEO paket - 6 meseci" />
        </label>
        <label>
          Cena / iznos
          <input name="amount" type="number" min="0" step="1" required placeholder="35000" />
        </label>
        <label>
          Valuta
          <select name="currency" defaultValue="RSD">
            <option>RSD</option>
            <option>EUR</option>
            <option>USD</option>
          </select>
        </label>
        <label>
          Opis / stavke (opciono)
          <textarea name="items" rows={3} placeholder="Kratak opis usluge, obim posla..." />
        </label>
        <label>
          Napomena (opciono)
          <textarea name="notes" rows={2} placeholder="Uslovi, rok, način plaćanja..." />
        </label>
        <div className="form-actions">
          <button type="button" onClick={onClose}>Otkaži</button>
          <button type="submit">Sačuvaj i generiši PDF</button>
        </div>
      </form>
    </div>
  );
}
