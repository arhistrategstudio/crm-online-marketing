import { FormEvent, useState } from "react";
import { useAuth } from "../lib/auth";
import { GoogleButton } from "../components/GoogleButton";

export function Login({ onSwitchToSignup }: { onSwitchToSignup: () => void }) {
  const { login, loginWithGoogle, error, clearError } = useAuth();
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setSubmitting(true);
    try {
      await login(String(data.get("email") || ""), String(data.get("password") || ""));
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
        <p className="subtitle">Prijavite se na svoj nalog</p>
        {error && <p className="auth-error">{error}</p>}
        <form onSubmit={submit}>
          <label>
            Email
            <input name="email" type="email" required autoFocus onChange={clearError} />
          </label>
          <label>
            Lozinka
            <input name="password" type="password" required onChange={clearError} />
          </label>
          <button type="submit" disabled={submitting}>Prijavi se</button>
        </form>
        <div className="auth-divider">ili</div>
        <GoogleButton onCredential={(idToken) => loginWithGoogle(idToken).catch(() => undefined)} />
        <p className="auth-switch">
          Nemate nalog? <button type="button" onClick={onSwitchToSignup}>Napravite nalog</button>
        </p>
      </section>
    </main>
  );
}
