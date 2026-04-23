

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import DailyIframe from "@daily-co/daily-js";
import type { DailyCall, DailyParticipant } from "@daily-co/daily-js";

const ROOM_URL =
  process.env.NEXT_PUBLIC_DAILY_ROOM_URL ??
  "https://spell-bee-bot.daily.co/KNFdxnUOQBxAB3ai0ORO";

const API_BASE = "http://localhost:8000/api";

const GAME_STATS_WS_URL =
  process.env.NEXT_PUBLIC_GAME_STATS_WS_URL ??
  `${(process.env.NEXT_PUBLIC_API_WS ?? "ws://localhost:8000").replace(/\/$/, "")}/api/game-stats/ws`;

const pickRemoteMicTrack = (participant: DailyParticipant): MediaStreamTrack | null => {
  const audio = participant.tracks?.audio;
  if (!audio) return null;
  if (audio.state === "playable" && audio.track) return audio.track;
  if (audio.persistentTrack) return audio.persistentTrack;
  return null;
};

const syncBotAudioToElement = (callObject: DailyCall, audioEl: HTMLAudioElement | null) => {
  if (!audioEl) return;

  const remotes = Object.entries(callObject.participants())
    .filter(([key]) => key !== "local")
    .map(([, p]) => p);

  for (const p of remotes) {
    const track = pickRemoteMicTrack(p);
    if (!track) continue;

    const stream = new MediaStream([track]);
    audioEl.srcObject = stream;
    audioEl.play().catch(() => {});
    return;
  }
};

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const [score, setScore] = useState(0);
  const [round, setRound] = useState(0);

  const callRef = useRef<DailyCall | null>(null);
  const remoteAudioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    let isMounted = true;
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    const applyStatsPayload = (raw: unknown) => {
      if (!isMounted || typeof raw !== "object" || raw === null) return;
      const data = raw as { rounds?: number; score?: number };
      setScore(typeof data.score === "number" ? data.score : 0);
      setRound(typeof data.rounds === "number" ? data.rounds : 0);
    };

    const connect = () => {
      if (!isMounted) return;
      socket = new WebSocket(GAME_STATS_WS_URL);

      socket.onopen = () => {
        if (reconnectTimer) {
          clearTimeout(reconnectTimer);
          reconnectTimer = null;
        }
      };

      socket.onmessage = (event) => {
        try {
          applyStatsPayload(JSON.parse(event.data as string));
        } catch {
          // ignore malformed payloads
        }
      };

      socket.onerror = () => {
        socket?.close();
      };

      socket.onclose = () => {
        if (!isMounted) return;
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectTimer = setTimeout(connect, 2000);
      };
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);

  const handleStartSession = useCallback(async () => {
    if (loading) return;

    setLoading(true);

    try {
      await fetch(`${API_BASE}/new-session`, { method: "POST" });

      if (callRef.current) {
        await callRef.current.destroy();
        callRef.current = null;
      }

      const callObject = DailyIframe.createCallObject({
        subscribeToTracksAutomatically: true,
        startVideoOff: true,
      });

      callRef.current = callObject;

      const onMediaUpdate = () => {
        syncBotAudioToElement(callObject, remoteAudioRef.current);
      };

      callObject.on("joined-meeting", onMediaUpdate);
      callObject.on("participant-joined", onMediaUpdate);
      callObject.on("participant-updated", onMediaUpdate);
      callObject.on("track-started", onMediaUpdate);

      await callObject.join({
        url: ROOM_URL,
        userName: "Player",
        startVideoOff: true,
      });

      syncBotAudioToElement(callObject, remoteAudioRef.current);

      setMessage("Connected to game");
    } catch {
      setMessage("Failed to start session");
    } finally {
      setLoading(false);
    }
  }, [loading]);

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex items-center justify-center px-4">
      <audio ref={remoteAudioRef} className="hidden" autoPlay playsInline />

      <div className="w-full max-w-md bg-zinc-900 rounded-2xl shadow-xl p-6 space-y-6 border border-zinc-800">

        <div className="text-center space-y-2">
          <h1 className="text-2xl font-semibold">🎤 Spell Bee Voice Bot</h1>
          <p className="text-zinc-400 text-sm">
            Listen → Spell → Get Feedback
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-zinc-800 p-4 rounded-xl text-center">
            <p className="text-sm text-zinc-400">Score</p>
            <p className="text-xl font-bold text-green-400">{score}</p>
          </div>

          <div className="bg-zinc-800 p-4 rounded-xl text-center">
            <p className="text-sm text-zinc-400">Rounds done</p>
            <p className="text-xl font-bold">{round}</p>
          </div>
        </div>

        <button
          onClick={handleStartSession}
          disabled={loading}
          className="w-full bg-white text-black font-medium py-3 rounded-xl hover:bg-zinc-200 transition disabled:opacity-50"
        >
          {loading ? "Starting..." : "Start Game"}
        </button>

        {message && (
          <div className="text-center text-sm text-zinc-400">{message}</div>
        )}
      </div>
    </div>
  );
}