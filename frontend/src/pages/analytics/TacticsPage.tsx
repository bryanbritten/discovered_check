import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../../services/api";
import type { TacticsResponse, TacticType } from "../../types";
import LoadingSpinner from "../../components/common/LoadingSpinner";

type MissedFilter = "all" | "missed" | "found";

const TACTIC_TYPE_OPTIONS: { label: string; value: TacticType | "" }[] = [
  { label: "All", value: "" },
  { label: "Fork", value: "fork" },
  { label: "Pin", value: "pin" },
  { label: "Skewer", value: "skewer" },
];

const TACTIC_ICONS: Record<TacticType, string> = {
  fork: "⑂",
  pin: "📌",
  skewer: "⚡",
};

const MISSED_OPTIONS: { label: string; value: MissedFilter }[] = [
  { label: "All", value: "all" },
  { label: "Missed", value: "missed" },
  { label: "Found", value: "found" },
];

function SummaryCard({
  label,
  total,
  missed,
}: {
  label: string;
  total: number;
  missed: number;
}) {
  const rate = total ? Math.round(((total - missed) / total) * 100) : 0;
  return (
    <div className="rounded-xl border border-white/10 bg-chess-darker p-5">
      <p className="text-sm text-gray-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-white">{total}</p>
      <div className="mt-2 flex items-center justify-between text-xs">
        <span className="text-red-400">{missed} missed</span>
        <span className="text-green-400">{rate}% found</span>
      </div>
      <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
        <div className="h-full rounded-full bg-green-400" style={{ width: `${rate}%` }} />
      </div>
    </div>
  );
}

export default function TacticsPage() {
  const [tacticType, setTacticType] = useState<TacticType | "">("");
  const [missedFilter, setMissedFilter] = useState<MissedFilter>("all");
  const [page, setPage] = useState(1);

  const params: Record<string, string | number> = { page };
  if (tacticType) params.tactic_type = tacticType;
  if (missedFilter === "missed") params.missed = "true";
  if (missedFilter === "found") params.missed = "false";

  const { data, isLoading } = useQuery<TacticsResponse>({
    queryKey: ["tactics", tacticType, missedFilter, page],
    queryFn: () => api.get("/analytics/tactics/", { params }).then((r) => r.data),
  });

  const summary = data?.summary;
  const totalPages = data ? Math.ceil(data.count / 20) : 1;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Missed Tactics</h1>
        <p className="mt-1 text-sm text-gray-400">
          Positions where a fork, pin, or skewer was available
        </p>
      </div>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <SummaryCard label="All Tactics" total={summary.total} missed={summary.missed_total} />
          <SummaryCard label="Forks" total={summary.forks} missed={summary.forks_missed} />
          <SummaryCard label="Pins" total={summary.pins} missed={summary.pins_missed} />
          <SummaryCard label="Skewers" total={summary.skewers} missed={summary.skewers_missed} />
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1 rounded-lg border border-white/10 bg-chess-darker p-1">
          {TACTIC_TYPE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => { setTacticType(opt.value); setPage(1); }}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                tacticType === opt.value
                  ? "bg-chess-accent text-chess-dark"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1 rounded-lg border border-white/10 bg-chess-darker p-1">
          {MISSED_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => { setMissedFilter(opt.value); setPage(1); }}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                missedFilter === opt.value
                  ? "bg-chess-accent text-chess-dark"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      {isLoading ? (
        <LoadingSpinner />
      ) : data?.results.length === 0 ? (
        <div className="rounded-xl border border-white/10 bg-chess-darker p-12 text-center">
          <p className="text-gray-500">No tactics found for these filters.</p>
          <p className="mt-2 text-xs text-gray-600">
            Import or sync games to start seeing tactics opportunities.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {data?.results.map((t) => (
            <div
              key={t.id}
              className="flex items-start gap-4 rounded-xl border border-white/10 bg-chess-darker px-5 py-4"
            >
              {/* Tactic type badge */}
              <div className="flex-shrink-0">
                <span
                  className={`inline-flex h-9 w-9 items-center justify-center rounded-lg text-lg ${
                    t.missed ? "bg-red-500/20 text-red-400" : "bg-green-500/20 text-green-400"
                  }`}
                >
                  {TACTIC_ICONS[t.tactic_type]}
                </span>
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="rounded bg-white/10 px-2 py-0.5 text-xs font-medium capitalize text-gray-300">
                    {t.tactic_type}
                  </span>
                  <span
                    className={`text-xs font-medium ${t.missed ? "text-red-400" : "text-green-400"}`}
                  >
                    {t.missed ? "Missed" : "Found"}
                  </span>
                  <span className="text-xs text-gray-600">
                    Move {t.move_number} ({t.move_color})
                  </span>
                </div>
                <p className="mt-1 text-sm text-gray-300">{t.description}</p>
              </div>

              <div className="flex-shrink-0 text-right">
                <p className="text-xs text-gray-600">
                  {new Date(t.played_at).toLocaleDateString()}
                </p>
                {t.lichess_game_id && (
                  <a
                    href={`https://lichess.org/${t.lichess_game_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-1 block text-xs text-chess-accent hover:underline"
                  >
                    View on Lichess →
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="rounded-lg border border-white/10 px-4 py-2 text-sm text-gray-400 hover:text-white disabled:opacity-30"
          >
            Previous
          </button>
          <span className="text-sm text-gray-500">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="rounded-lg border border-white/10 px-4 py-2 text-sm text-gray-400 hover:text-white disabled:opacity-30"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
