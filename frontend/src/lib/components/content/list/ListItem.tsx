export default function ListItem({ children }: { children: React.ReactNode }) {
  return (
    <li
      className="
        inline-block pl-3 pr-4 py-4
        card border-l-[6px] text-xl w-full"
    >
      {children}
    </li>
  );
}
