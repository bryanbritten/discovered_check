import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import api from "../../services/api";
import type { TimeAnalysis, TimeControlCategory } from "../../types";
import LoadingSpinner from "../../components/common/LoadingSpinner";

const TC_OPTIONS: { label: string; value: TimeControlCategory | "" }[] = [
  { label: "All", value: "" },
  { label: "Bullet", value: "bullet" },
  { label: "Blitz", value: "blitz" },
  { label: "Rapid", value: "rapid" },
  { label: "Classical", value: "classical" },
];

const TIME_CATEGORY_LABELS: Record<string, string> = {
  instant: "Instant (<2s)",
  quick: "Quick (2–10s)",
  normal: "Normal (10–30s)",
  considered: "Considered (30–60s)",
  long_think: "Long Think (>60s)",
};

const TIME_CATEGORY_COLORS: Record<string, string> = {
  instant: "#6366f1",
  quick: "#22d3ee",
  normal: "#4ade80",
  considered: "#facc15",
  long_think: "#f87171",
};

const RESULT_COLORS: Record<string, string> = {
  win: "#4ade80",
  loss: "#f87171",
  draw: "#94a3b8",
};

function fmt(seconds: number | null | undefined): string {
  if (seconds == null) return "—";
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  return `${(seconds / 60).toFixed(1)}m`;
}

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="mb-4 border-b border-white/10 pb-2 text-lg font-semibold text-white">
      {children}
    </h2>
  );
}

export default function TimeAnalysisPage() {
  const [tcFilter, setTcFilter] = useState<TimeControlCategory | "">("");

  const params = tcFilter ? { time_control_category: tcFilter } : {};
  const { data, isLoading } = useQuery<TimeAnalysis>({
    queryKey: ["time-analysis", tcFilter],
    queryFn: () => api.get("/analytics/time/", { params }).then((r) => r.data),
  });

  if (isLoading) return <LoadingSpinner />;
  if (!data) return null;

  const categoryData = data.time_category_distribution.map((c) => ({
    name: TIME_CATEGORY_LABELS[c.category] ?? c.category,
    count: c.count,
    fill: TIME_CATEGORY_COLORS[c.category] ?? "#e2b96f",
    key: c.category,
  }));

  const resultData = data.time_by_result.map((r) => ({
    name: r.result.charAt(0).toUpperCase() + r.result.slice(1),
    "Avg Time (s)": r.avg_time_per_move ?? 0,
    fill: RESULT_COLORS[r.result] ?? "#e2b96f",
  }));

  const tcData = data.by_time_control.map((t) => ({
    name: t.category,
    "Avg Time (s)": t.avg_time_per_move ?? 0,
  }));

  const lt = data.long_think_correlation;
  const ltDiff =
    lt.games_with_long_think.total > 0 && lt.games_without_long_think.total > 0
      ? lt.games_with_long_think.win_rate - lt.games_without_long_think.win_rate
      : null;

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Time Analysis</h1>
          <p className="mt-1 text-sm text-gray-400">
            How you spend your clock — and whether it matters
          </p>
        </div>

        <div className="flex items-center gap-1 rounded-lg border border-white/10 bg-chess-darker p-1">
          {TC_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setTcFilter(opt.value)}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                tcFilter === opt.value
                  ? "bg-chess-accent text-chess-dark"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-white/10 bg-chess-darker p-5">
          <p className="text-sm text-gray-400">Avg Time per Move</p>
          <p className="mt-1 text-3xl font-bold text-white">
            {fmt(data.overall.avg_time_per_move)}
          </p>
          <p className="mt-1 text-xs text-gray-600">
            across {data.overall.total_moves_analyzed.toLocaleString()} moves
          </p>
        </div>

        {/* Long-think correlation */}
        <div className="col-span-2 rounded-xl border border-white/10 bg-chess-darker p-5">
          <p className="mb-3 text-sm text-gray-400">Long Think Correlation</p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500">Games WITH a long think</p>
              <p className="mt-1 text-2xl font-bold text-white">
                {lt.games_with_long_think.win_rate}%
              </p>
              <p className="text-xs text-gray-600">
                win rate · {lt.games_with_long_think.total} games
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Games WITHOUT a long think</p>
              <p className="mt-1 text-2xl font-bold text-white">
                {lt.games_without_long_think.win_rate}%
              </p>
              <p className="text-xs text-gray-600">
                win rate · {lt.games_without_long_think.total} games
              </p>
            </div>
          </div>
          {ltDiff !== null && (
            <p
              className={`mt-3 text-sm font-medium ${
                ltDiff > 0 ? "text-green-400" : ltDiff < 0 ? "text-red-400" : "text-gray-400"
              }`}
            >
              {ltDiff > 0
                ? `+${ltDiff.toFixed(1)}% win rate when you think longer`
                : ltDiff < 0
                ? `${ltDiff.toFixed(1)}% win rate when you think longer`
                : "No difference in win rate"}
            </p>
          )}
        </div>
      </div>

      {/* Time category distribution */}
      {categoryData.length > 0 && (
        <div className="rounded-xl border border-white/10 bg-chess-darker p-5">
          <SectionHeading>How Long Do You Think?</SectionHeading>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={categoryData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} />
              <YAxis
                type="category"
                dataKey="name"
                width={140}
                tick={{ fontSize: 11, fill: "#94a3b8" }}
              />
              <Tooltip
                contentStyle={{
                  background: "#16213e",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 8,
                }}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]} name="Moves">
                {categoryData.map((entry) => (
                  <Cell key={entry.key} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Avg time per move by result */}
      {resultData.length > 0 && (
        <div className="rounded-xl border border-white/10 bg-chess-darker p-5">
          <SectionHeading>Avg Time per Move by Game Result</SectionHeading>
          <p className="mb-4 text-xs text-gray-500">
            Do you take more time in games you win, lose, or draw?
          </p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={resultData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} unit="s" />
              <Tooltip
                contentStyle={{
                  background: "#16213e",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 8,
                }}
                formatter={(v: number) => [`${v.toFixed(1)}s`, "Avg Time"]}
              />
              <Bar dataKey="Avg Time (s)" radius={[4, 4, 0, 0]}>
                {resultData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Avg time by time control */}
      {tcData.length > 1 && !tcFilter && (
        <div className="rounded-xl border border-white/10 bg-chess-darker p-5">
          <SectionHeading>Avg Time per Move by Time Control</SectionHeading>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={tcData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} unit="s" />
              <Tooltip
                contentStyle={{
                  background: "#16213e",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 8,
                }}
                formatter={(v: number) => [`${v.toFixed(1)}s`, "Avg Time"]}
              />
              <Bar dataKey="Avg Time (s)" fill="#e2b96f" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
