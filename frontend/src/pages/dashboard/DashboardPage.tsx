import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../../services/api";
import type { LichessSync, OverviewStats, PGNImport } from "../../types";
import LoadingSpinner from "../../components/common/LoadingSpinner";

function StatCard({
  label,
  value,
  sub,
  to,
}: {
  label: string;
  value: string | number;
  sub?: string;
  to?: string;
}) {
  const inner = (
    <div className="rounded-xl border border-white/10 bg-chess-darker p-5 transition-colors hover:border-chess-accent/30">
      <p className="text-sm text-gray-400">{label}</p>
      <p className="mt-1 text-3xl font-bold text-white">{value}</p>
      {sub && <p className="mt-1 text-xs text-gray-500">{sub}</p>}
    </div>
  );
  return to ? <Link to={to}>{inner}</Link> : inner;
}

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const { data: stats, isLoading } = useQuery<OverviewStats>({
    queryKey: ["overview"],
    queryFn: () => api.get("/analytics/overview/").then((r) => r.data),
  });

  const { data: syncStatus } = useQuery<LichessSync>({
    queryKey: ["lichess-sync"],
    queryFn: () => api.get("/imports/lichess/sync/status/").then((r) => r.data),
    refetchInterval: (query) =>
      query.state.data?.status === "syncing" ? 3000 : false,
  });

  const syncMutation = useMutation({
    mutationFn: () => api.post("/imports/lichess/sync/"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lichess-sync"] });
      queryClient.invalidateQueries({ queryKey: ["overview"] });
    },
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadStatus("Uploading…");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const { data } = await api.post<PGNImport>("/imports/pgn/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadStatus(
        `Imported ${data.processed_games} game${data.processed_games !== 1 ? "s" : ""} from ${data.filename}`
      );
      queryClient.invalidateQueries({ queryKey: ["overview"] });
    } catch {
      setUploadStatus("Upload failed. Please try again.");
    }

    if (fileInput.current) fileInput.current.value = "";
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-400">Your chess at a glance</p>
        </div>

        {/* Data controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => syncMutation.mutate()}
            disabled={syncStatus?.status === "syncing" || syncMutation.isPending}
            className="flex items-center gap-2 rounded-lg border border-chess-accent/40 px-4 py-2 text-sm text-chess-accent transition-colors hover:bg-chess-accent/10 disabled:opacity-50"
          >
            {syncStatus?.status === "syncing" ? (
              <>
                <LoadingSpinner size="sm" />
                Syncing…
              </>
            ) : (
              "Sync Lichess"
            )}
          </button>

          <label className="cursor-pointer rounded-lg border border-white/10 px-4 py-2 text-sm text-gray-300 transition-colors hover:border-white/20 hover:text-white">
            Import PGN
            <input
              ref={fileInput}
              type="file"
              accept=".pgn"
              className="hidden"
              onChange={handleFileUpload}
            />
          </label>
        </div>
      </div>

      {uploadStatus && (
        <div className="rounded-lg border border-chess-accent/30 bg-chess-accent/10 px-4 py-3 text-sm text-chess-accent">
          {uploadStatus}
        </div>
      )}

      {syncStatus?.status === "failed" && syncStatus.error_message && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          Sync failed: {syncStatus.error_message}
        </div>
      )}

      {/* Key stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard
          label="Total Games"
          value={stats?.total_games ?? 0}
          to="/analytics/overview"
        />
        <StatCard
          label="Win Rate"
          value={stats ? `${stats.win_rate}%` : "—"}
          sub={stats ? `${stats.wins}W / ${stats.losses}L / ${stats.draws}D` : undefined}
          to="/analytics/overview"
        />
        <StatCard
          label="As White"
          value={stats ? `${stats.as_white.win_rate}%` : "—"}
          sub={`${stats?.as_white.total ?? 0} games`}
          to="/analytics/overview"
        />
        <StatCard
          label="As Black"
          value={stats ? `${stats.as_black.win_rate}%` : "—"}
          sub={`${stats?.as_black.total ?? 0} games`}
          to="/analytics/overview"
        />
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Link
          to="/analytics/overview"
          className="group rounded-xl border border-white/10 bg-chess-darker p-6 hover:border-chess-accent/30 transition-colors"
        >
          <div className="text-3xl">📊</div>
          <h2 className="mt-3 font-semibold text-white group-hover:text-chess-accent">
            Overall Statistics
          </h2>
          <p className="mt-1 text-sm text-gray-400">
            Win rates by color, time control, opening, and more
          </p>
        </Link>

        <Link
          to="/analytics/tactics"
          className="group rounded-xl border border-white/10 bg-chess-darker p-6 hover:border-chess-accent/30 transition-colors"
        >
          <div className="text-3xl">🎯</div>
          <h2 className="mt-3 font-semibold text-white group-hover:text-chess-accent">
            Missed Tactics
          </h2>
          <p className="mt-1 text-sm text-gray-400">
            Forks, pins, and skewers you didn't play
          </p>
        </Link>

        <Link
          to="/analytics/time"
          className="group rounded-xl border border-white/10 bg-chess-darker p-6 hover:border-chess-accent/30 transition-colors"
        >
          <div className="text-3xl">⏱</div>
          <h2 className="mt-3 font-semibold text-white group-hover:text-chess-accent">
            Time Analysis
          </h2>
          <p className="mt-1 text-sm text-gray-400">
            Does thinking longer make your moves better?
          </p>
        </Link>
      </div>

      {/* Sync info */}
      {syncStatus?.last_synced_at && (
        <p className="text-xs text-gray-600">
          Last Lichess sync:{" "}
          {new Date(syncStatus.last_synced_at).toLocaleString()} ·{" "}
          {syncStatus.games_synced} games synced total
        </p>
      )}
    </div>
  );
}
