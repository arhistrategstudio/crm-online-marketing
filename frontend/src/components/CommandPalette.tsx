import { Page } from "../types";
import { nav } from "./Shell";

export function CommandPalette({ onSelect, onClose }: { onSelect: (page: Page) => void; onClose: () => void }) {
  return (
    <div className="modal" onClick={onClose}>
      <div className="command-menu" onClick={(e) => e.stopPropagation()}>
        <h2>Brza navigacija</h2>
        {nav.map(([name]) => (
          <button key={name} onClick={() => onSelect(name)}>{name}</button>
        ))}
      </div>
    </div>
  );
}
