import { FormEvent } from "react";
import { leadSources } from "../types";

export function ContactModal({
  onClose,
  onSubmit,
}: {
  onClose: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <div className="modal" onClick={onClose}>
      <form className="command-menu contact-modal" onClick={(e) => e.stopPropagation()} onSubmit={onSubmit}>
        <h2>Novi kontakt</h2>
        <label>
          Ime i prezime
          <input name="name" required autoFocus />
        </label>
        <label>
          Telefon
          <input name="phone" placeholder="064 123 4567" />
        </label>
        <label>
          Email
          <input name="email" type="email" placeholder="ime@primer.rs" />
        </label>
        <label>
          Izvor upita
          <select name="source" defaultValue="manual">
            {leadSources.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>
        <label>
          Odgovorna osoba
          <input name="owner" placeholder="Ime prodavca" />
        </label>
        <label>
          Kratka beleška
          <textarea name="notes" rows={2} placeholder="Beleška o klijentu..." />
        </label>
        <div className="form-actions">
          <button type="button" onClick={onClose}>Otkaži</button>
          <button type="submit">Sačuvaj kontakt</button>
        </div>
      </form>
    </div>
  );
}
