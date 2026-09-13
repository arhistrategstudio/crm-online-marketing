import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { ContactItem } from "../types";
import { ContactModal } from "../components/ContactModal";

export function Contacts() {
  const [contacts, setContacts] = useState<ContactItem[]>([]);
  const [query, setQuery] = useState("");
  const [addContact, setAddContact] = useState(false);

  const load = (search: string) => {
    const suffix = search.trim() ? `?search=${encodeURIComponent(search.trim())}` : "";
    apiFetch(`/contacts${suffix}`)
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((items: { id: number; name: string; source: string; phone: string | null; status: string }[]) => {
        setContacts(
          items.map((c) => ({ id: c.id, name: c.name, source: c.source, phone: c.phone || "Nije unet", status: c.status })),
        );
      })
      .catch(() => undefined);
  };

  useEffect(() => {
    const timeout = setTimeout(() => load(query), 300);
    return () => clearTimeout(timeout);
  }, [query]);

  const submitContact = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const name = String(data.get("name") || "").trim();
    if (!name) return;
    const response = await apiFetch("/contacts", {
      method: "POST",
      body: JSON.stringify({
        name,
        phone: String(data.get("phone") || "").trim() || null,
        email: String(data.get("email") || "").trim() || null,
        source: "manual",
      }),
    });
    if (!response.ok) {
      alert("Kontakt nije sačuvan. Proverite podatke i backend.");
      return;
    }
    setAddContact(false);
    load(query);
  };

  return (
    <>
      <div className="contact-toolbar">
        <input className="search" placeholder="Pretraži kontakte" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button onClick={() => setAddContact(true)}>Dodaj kontakt</button>
      </div>
      <section className="card table">
        {contacts.map((c) => (
          <div className="row" key={c.id}>
            <strong>{c.name}</strong>
            <span>{c.phone}</span>
            <span>{c.source}</span>
            <span className="badge">{c.status}</span>
          </div>
        ))}
        {!contacts.length && (
          <div className="row">
            <span>{query.trim() ? "Nema kontakata za ovu pretragu." : "Još uvek nema kontakata."}</span>
          </div>
        )}
      </section>
      {addContact && <ContactModal onClose={() => setAddContact(false)} onSubmit={submitContact} />}
    </>
  );
}
