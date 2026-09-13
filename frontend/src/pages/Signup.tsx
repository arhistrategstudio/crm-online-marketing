import { FormEvent, useState } from "react";
import { useAuth } from "../lib/auth";
import { GoogleButton } from "../components/GoogleButton";

export function Signup({ onSwitchToLogin }: { onSwitchToLogin: () => void }) {
  const { signup, loginWithGoogle, error, clearError } = useAuth();
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setSubmitting(true);
    try {
      await signup(
        String(data.get("name") || ""),
        String(data.get("email") || ""),
        String(data.get("password") || ""),
      );
    } catch {
      // error je već postavljen u AuthProvider-u
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-shell">
      <section className="auth-card">
        <p className="brand">CRM<span>+</span></p>
        <p className="subtitle">Napravite novi nalog</p>
        {error && <p className="auth-error">{error}</p>}
        <form onSubmit={submit}>
          <label>
            Ime i prezime
            <input name="name" required autoFocus onChange={clearError} />
          </label>
          <label>
            Email
            <input name="email" type="email" required onChange={clearError} />
          </label>
          <label>
            Lozinka
            <input name="password" type="password" minLength={8} required onChange={clearError} />
          </label>
          <button type="submit" disabled={submitting}>Napravi nalog</button>
        </form>
        <div className="auth-divider">ili</div>
        <GoogleButton onCredential={(idToken) => loginWithGoogle(idToken).catch(() => undefined)} />
        <p className="auth-switch">
          Već imate nalog? <button type="button" onClick={onSwitchToLogin}>Prijavite se</button>
        </p>
      </section>
    </main>
  );
}
