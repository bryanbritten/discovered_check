import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import api from "../../services/api";
import type { OverviewStats, TimeControlCategory } from "../../types";
import LoadingSpinner from "../../components/common/LoadingSpinner";

const TC_OPTIONS: { label: string; value: TimeControlCategory | "" }[] = [
  { label: "All", value: "" },
  { label: "Bullet", value: "bullet" },
  { label: "Blitz", value: "blitz" },
  { label: "Rapid", value: "rapid" },
  { label: "Classical", value: "classical" },
];

const COLORS = { win: "#4ade80", loss: "#f87171", draw: "#94a3b8" };
function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="mb-4 text-lg font-semibold text-white border-b border-white/10 pb-2">
      {children}
    </h2>
  );
}

function ColorCompare({ stats }: { stats: OverviewStats }) {
  const data = [
    {
      label: "White",
      wins: stats.as_white.wins,
      losses: stats.as_white.losses,
      draws: stats.as_white.draws,
      wr: stats.as_white.win_rate,
    },
    {
      label: "Black",
      wins: stats.as_black.wins,
      losses: stats.as_black.losses,
      draws: stats.as_black.draws,
      wr: stats.as_black.win_rate,
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4">
      {data.map((d) => (
        <div key={d.label} className="rounded-xl border border-white/10 bg-chess-darker p-5">
          <p className="text-sm font-medium text-gray-400">As {d.label}</p>
          <p className="mt-1 text-3xl font-bold text-white">{d.wr}%</p>
          <div className="mt-3 flex gap-3 text-xs text-gray-500">
            <span className="text-green-400">{d.wins}W</span>
            <span className="text-red-400">{d.losses}L</span>
            <span className="text-gray-400">{d.draws}D</span>
          </div>
          <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
            <div
              className="h-full rounded-full bg-green-400"
              style={{ width: `${d.wr}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function OverallStatsPage() {
  const [tcFilter, setTcFilter] = useState<TimeControlCategory | "">("");

  const params = tcFilter ? { time_control_category: tcFilter } : {};
  const { data: stats, isLoading } = useQuery<OverviewStats>({
    queryKey: ["overview", tcFilter],
    queryFn: () => api.get("/analytics/overview/", { params }).then((r) => r.data),
  });

  if (isLoading) return <LoadingSpinner />;
  if (!stats) return null;

  const resultPie = [
    { name: "Wins", value: stats.wins },
    { name: "Losses", value: stats.losses },
    { name: "Draws", value: stats.draws },
  ];
  const pieColors = [COLORS.win, COLORS.loss, COLORS.draw];

  const tcBar = stats.by_time_control.map((tc) => ({
    name: tc.category,
    "Win %": tc.win_rate,
    Total: tc.total,
  }));

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Overall Statistics</h1>
          <p className="mt-1 text-sm text-gray-400">
            {stats.total_games} game{stats.total_games !== 1 ? "s" : ""} analyzed
          </p>
        </div>

        {/* Time control filter */}
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

      {/* Summary numbers */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Win Rate", value: `${stats.win_rate}%` },
          { label: "Wins", value: stats.wins },
          { label: "Losses", value: stats.losses },
          { label: "Draws", value: stats.draws },
        ].map((s) => (
          <div
            key={s.label}
            className="rounded-xl border border-white/10 bg-chess-darker p-5"
          >
            <p className="text-sm text-gray-400">{s.label}</p>
            <p className="mt-1 text-3xl font-bold text-white">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Color comparison */}
      <div>
        <SectionHeading>By Color</SectionHeading>
        <ColorCompare stats={stats} />
      </div>

      {/* Result pie + monthly trend */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-white/10 bg-chess-darker p-5">
          <SectionHeading>Result Breakdown</SectionHeading>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={resultPie}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={3}
                dataKey="value"
              >
                {resultPie.map((_, i) => (
                  <Cell key={i} fill={pieColors[i]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: "#16213e", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }}
                labelStyle={{ color: "#fff" }}
              />
              <Legend
                formatter={(value) => (
                  <span className="text-xs text-gray-400">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl border border-white/10 bg-chess-darker p-5">
          <SectionHeading>Monthly Win Rate</SectionHeading>
          {stats.monthly_trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={stats.monthly_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: "#94a3b8" }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#94a3b8" }} unit="%" />
                <Tooltip
                  contentStyle={{ background: "#16213e", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }}
                  labelStyle={{ color: "#fff" }}
                />
                <Line
                  type="monotone"
                  dataKey="win_rate"
                  stroke="#e2b96f"
                  strokeWidth={2}
                  dot={{ r: 3, fill: "#e2b96f" }}
                  name="Win %"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="mt-4 text-sm text-gray-500">No data yet.</p>
          )}
        </div>
      </div>

      {/* By time control */}
      {tcBar.length > 0 && (
        <div className="rounded-xl border border-white/10 bg-chess-darker p-5">
          <SectionHeading>Win Rate by Time Control</SectionHeading>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={tcBar}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#94a3b8" }} unit="%" />
              <Tooltip
                contentStyle={{ background: "#16213e", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8 }}
              />
              <Bar dataKey="Win %" fill="#e2b96f" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Top openings */}
      {stats.top_openings.length > 0 && (
        <div className="rounded-xl border border-white/10 bg-chess-darker p-5">
          <SectionHeading>Top Openings</SectionHeading>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-left text-xs text-gray-500">
                  <th className="pb-2 pr-4">Opening</th>
                  <th className="pb-2 pr-4 text-right">Games</th>
                  <th className="pb-2 pr-4 text-right">W</th>
                  <th className="pb-2 pr-4 text-right">L</th>
                  <th className="pb-2 text-right">Win %</th>
                </tr>
              </thead>
              <tbody>
                {stats.top_openings.map((o) => {
                  const wr = o.total ? Math.round((o.wins / o.total) * 100) : 0;
                  return (
                    <tr
                      key={o.opening_name}
                      className="border-b border-white/5 last:border-0"
                    >
                      <td className="py-2 pr-4 text-gray-300">
                        {o.opening_eco && (
                          <span className="mr-2 rounded bg-white/10 px-1.5 py-0.5 text-xs text-gray-500">
                            {o.opening_eco}
                          </span>
                        )}
                        {o.opening_name}
                      </td>
                      <td className="py-2 pr-4 text-right text-gray-400">{o.total}</td>
                      <td className="py-2 pr-4 text-right text-green-400">{o.wins}</td>
                      <td className="py-2 pr-4 text-right text-red-400">{o.losses}</td>
                      <td className="py-2 text-right font-medium text-chess-accent">
                        {wr}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
