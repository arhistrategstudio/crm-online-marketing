import { FormEvent } from "react";

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
        <div className="form-actions">
          <button type="button" onClick={onClose}>Otkaži</button>
          <button type="submit">Sačuvaj kontakt</button>
        </div>
      </form>
    </div>
  );
}
