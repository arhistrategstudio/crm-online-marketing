import { FormEvent } from "react";
import { campaignStatusLabels, channelLabels } from "../types";

const adChannels = ["facebook", "instagram", "viber"] as const;

export function CampaignModal({
  onClose,
  onSubmit,
}: {
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="modal" onClick={onClose}>
      <form className="command-menu contact-modal" onClick={(e) => e.stopPropagation()} onSubmit={onSubmit}>
        <h2>Nova kampanja</h2>
        <label>
          Naziv kampanje
          <input name="name" required autoFocus placeholder="npr. Prolećna akcija - Instagram" />
        </label>
        <label>
          Kanal
          <select name="channel" defaultValue="instagram">
            {adChannels.map((channel) => <option key={channel} value={channel}>{channelLabels[channel]}</option>)}
          </select>
        </label>
        <label>
          Status
          <select name="status" defaultValue="draft">
            {Object.entries(campaignStatusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </label>
        <label>
          Budžet (RSD)
          <input name="budget" type="number" min={0} defaultValue={0} />
        </label>
        <label>
          Potrošeno (RSD)
          <input name="spend" type="number" min={0} defaultValue={0} />
        </label>
        <div className="form-actions">
          <button type="button" onClick={onClose}>Otkaži</button>
          <button type="submit">Sačuvaj kampanju</button>
        </div>
      </form>
    </div>
  );
}
