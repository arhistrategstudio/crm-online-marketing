import { FormEvent, useState } from "react";
import { useAuth } from "../lib/auth";

export function Settings() {
  const { user, changePassword } = useAuth();
  const [status, setStatus] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!user) return null;
  const hasPassword = user.has_password;

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const newPassword = String(data.get("new_password") || "");
    const confirmPassword = String(data.get("confirm_password") || "");
    if (newPassword !== confirmPassword) {
      setStatus({ type: "error", text: "Nova lozinka i potvrda se ne poklapaju." });
      return;
    }
    setSubmitting(true);
    setStatus(null);
    try {
      const currentPassword = hasPassword ? String(data.get("current_password") || "") : null;
      await changePassword(currentPassword, newPassword);
      setStatus({ type: "success", text: "Lozinka je uspešno sačuvana." });
      form.reset();
    } catch (err) {
      setStatus({ type: "error", text: (err as Error).message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <section className="card">
        <h2>Moj profil</h2>
        <div className="row">
          <strong>{user.name}</strong>
          <span>{user.email}</span>
          <span>{user.auth_provider === "google" ? "Google nalog" : "Lokalni nalog"}</span>
          <span className="badge">{user.role}</span>
        </div>
      </section>
      <section className="card contact-modal">
        <h2>{hasPassword ? "Promeni lozinku" : "Postavi lozinku"}</h2>
        {status && <p className={status.type === "error" ? "auth-error" : "badge"}>{status.text}</p>}
        <form onSubmit={submit}>
          {hasPassword && (
            <label>
              Trenutna lozinka
              <input name="current_password" type="password" required />
            </label>
          )}
          <label>
            Nova lozinka
            <input name="new_password" type="password" minLength={8} required />
          </label>
          <label>
            Potvrdi novu lozinku
            <input name="confirm_password" type="password" minLength={8} required />
          </label>
          <div className="form-actions">
            <button type="submit" disabled={submitting}>Sačuvaj</button>
          </div>
        </form>
      </section>
    </>
  );
}
