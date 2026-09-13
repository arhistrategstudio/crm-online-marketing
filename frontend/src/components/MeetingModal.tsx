import { FormEvent } from "react";

export type MeetingContactOption = { id: number; name: string };

export function MeetingModal({
  contacts,
  onClose,
  onSubmit,
}: {
  contacts: MeetingContactOption[];
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="modal" onClick={onClose}>
      <form className="command-menu contact-modal" onClick={(e) => e.stopPropagation()} onSubmit={onSubmit}>
        <h2>Novi sastanak</h2>
        <label>
          Naziv
          <input name="title" required autoFocus placeholder="Sastanak sa..." />
        </label>
        <label>
          Kontakt (opciono)
          <select name="contact_id" defaultValue="">
            <option value="">Bez kontakta</option>
            {contacts.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </label>
        <label>
          Datum
          <input name="date" type="date" required />
        </label>
        <label>
          Od
          <input name="start_time" type="time" required />
        </label>
        <label>
          Do
          <input name="end_time" type="time" required />
        </label>
        <div className="form-actions">
          <button type="button" onClick={onClose}>Otkaži</button>
          <button type="submit">Sačuvaj sastanak</button>
        </div>
      </form>
    </div>
  );
}
