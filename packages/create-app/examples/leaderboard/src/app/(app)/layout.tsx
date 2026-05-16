import { redirect } from "next/navigation";
import { getSession } from "@/lib/session";
import { Sidebar } from "@/components/sidebar";
import { Topbar } from "@/components/topbar";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getSession();

  if (!session.accessToken) {
    redirect("/");
  }

  return (
    <div className="flex h-screen">
      <Sidebar workspaceName={session.workspaceName} />
      <div className="flex flex-1 flex-col">
        <Topbar connected={true} />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
