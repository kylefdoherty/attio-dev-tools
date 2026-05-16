import { getSession } from "@/lib/session";
import { ConnectButton } from "@/components/connect-button";
import { Sidebar } from "@/components/sidebar";
import { Topbar } from "@/components/topbar";

export default async function Home() {
  const session = await getSession();
  const connected = !!session.accessToken;

  if (!connected) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold tracking-tight">My Attio App</h1>
          <p className="mt-2 text-muted-foreground">
            Connect your Attio workspace to get started.
          </p>
        </div>
        <ConnectButton connected={false} />
      </div>
    );
  }

  return (
    <div className="flex h-screen">
      <Sidebar workspaceName={session.workspaceName} />
      <div className="flex flex-1 flex-col">
        <Topbar connected={connected} />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-4xl">
            <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
            <p className="mt-2 text-muted-foreground">
              Your Attio app is connected and ready. Start building!
            </p>

            <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div className="rounded-lg border border-border bg-card p-6">
                <h3 className="font-semibold">Records</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Query records from your Attio workspace using the SDK.
                </p>
              </div>
              <div className="rounded-lg border border-border bg-card p-6">
                <h3 className="font-semibold">Lists</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Read and manage list entries in your CRM.
                </p>
              </div>
              <div className="rounded-lg border border-border bg-card p-6">
                <h3 className="font-semibold">Webhooks</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  React to real-time events from Attio.
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
