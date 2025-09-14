import SideNavbar from "@/lib/components/SideNavbar";

export default function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex flex-row h-dvh">
      <header className="w-1/5 bg-off-background">
        <SideNavbar />
      </header>
      <main className="w-4/5 shadow-[0_0_8px_rgba(0,0,0,0.25)] ">
        {children}
      </main>
    </div>
  );
}
