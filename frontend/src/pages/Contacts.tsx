import { FormEvent, useEffect, useState } from "react";
import { apiFetch } from "../lib/api";
import { ContactItem } from "../types";
import { ContactModal } from "../components/ContactModal";

const demoContacts: ContactItem[] = [
  { id: 0, name: "Ana Jovanović", source: "Instagram", phone: "064 123 4567" },
  { id: 0, name: "Marko Petrović", source: "Facebook", phone: "065 222 111" },
  { id: 0, name: "Jelena Ilić", source: "Email", phone: "063 345 678" },
];

export function Contacts() {
  const [contacts, setContacts] = useState<ContactItem[]>(demoContacts);
  const [query, setQuery] = useState("");
  const [addContact, setAddContact] = useState(false);

  useEffect(() => {
    apiFetch("/contacts")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((items) => {
        if (items.length) {
          setContacts(items.map((c: { id: number; name: string; source: string; phone: string | null }) => ({
            id: c.id,
            name: c.name,
            source: c.source,
            phone: c.phone || "Nije unet",
          })));
        }
      })
      .catch(() => undefined);
  }, []);

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
    const contact = await response.json();
    setContacts([...contacts, { id: contact.id, name: contact.name, source: "Ručno", phone: contact.phone || "Nije unet" }]);
    setAddContact(false);
  };

  return (
    <>
      <div className="contact-toolbar">
        <input className="search" placeholder="Pretraži kontakte" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button onClick={() => setAddContact(true)}>Dodaj kontakt</button>
      </div>
      <section className="card table">
        {contacts
          .filter((c) => c.name.toLowerCase().includes(query.toLowerCase()))
          .map((c) => (
            <div className="row" key={`${c.name}-${c.phone}`}>
              <strong>{c.name}</strong>
              <span>{c.phone}</span>
              <span>{c.source}</span>
              <span className="badge">Aktivan</span>
            </div>
          ))}
      </section>
      {addContact && <ContactModal onClose={() => setAddContact(false)} onSubmit={submitContact} />}
    </>
  );
}
