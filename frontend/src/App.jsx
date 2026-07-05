import { useCallback, useEffect, useRef, useState } from 'react'
import { marked } from 'marked'
import ForceGraph2D from 'react-force-graph-2d'

const API = '/api'

// fetch wrapper: every failure surfaces as a readable error, never a hang
async function api(path, opts = {}) {
  let res
  try {
    res = await fetch(`${API}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...opts,
    })
  } catch {
    throw new Error('Cannot reach the Legacy backend — is it running on :8400?')
  }
  let body
  try {
    body = await res.json()
  } catch {
    throw new Error(`Backend returned an unreadable response (HTTP ${res.status}).`)
  }
  if (!res.ok) throw new Error(body.detail || `HTTP ${res.status}`)
  if (body && typeof body === 'object' && body.error) throw new Error(body.error)
  return body
}

const NODE_STYLES = {
  GOAL: 'bg-emerald-950/60 text-emerald-300 border-emerald-800',
  ACTION: 'bg-indigo-950/60 text-indigo-300 border-indigo-800',
  CLAIM: 'bg-amber-950/60 text-amber-300 border-amber-800',
  EVIDENCE: 'bg-teal-950/60 text-teal-300 border-teal-800',
  CONTRADICTION: 'bg-rose-950/60 text-rose-300 border-rose-800',
  PROJECT: 'bg-sky-950/60 text-sky-300 border-sky-800',
}

function Markdown({ text }) {
  if (!text) return null
  return <div className="md text-sm text-[#b8b4ab]" dangerouslySetInnerHTML={{ __html: marked.parse(text) }} />
}

function ErrorNote({ error, onRetry }) {
  if (!error) return null
  return (
    <div className="border border-rose-900 bg-rose-950/40 rounded-lg px-4 py-3 text-sm text-rose-300 flex items-center justify-between gap-3">
      <span>{String(error.message || error)}</span>
      {onRetry && (
        <button onClick={onRetry} className="text-xs underline shrink-0 hover:text-white">retry</button>
      )}
    </div>
  )
}

function Skeleton({ lines = 4 }) {
  return (
    <div className="space-y-2 animate-pulse">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="h-3 rounded bg-[#1e2028]" style={{ width: `${90 - i * 12}%` }} />
      ))}
    </div>
  )
}

function Section({ title, kicker, children }) {
  return (
    <section className="border border-[#23252d] rounded-xl bg-[#121318] p-5">
      <div className="text-[11px] uppercase tracking-[0.18em] text-[#6b6f80] mb-1">{kicker}</div>
      <h2 className="text-[#f0ede6] font-serif text-lg mb-2">{title}</h2>
      {children}
    </section>
  )
}

/* ----------------------------- evidence sources ---------------------------- */

function SourceRow({ id, label, hint, cfg, onChange, onSync, busy }) {
  return (
    <div className="flex flex-wrap items-center gap-3 py-2">
      <button
        onClick={() => onChange({ ...cfg, enabled: !cfg.enabled }, true)}
        className={`relative w-9 h-5 rounded-full transition shrink-0 ${cfg.enabled ? 'bg-emerald-600' : 'bg-[#2a2c34]'}`}
        title={cfg.enabled ? 'on — Legacy may sync this source' : 'off — Legacy will not touch this source'}
      >
        <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${cfg.enabled ? 'left-[18px]' : 'left-0.5'}`} />
      </button>
      <span className="text-sm text-[#d7d3cb] w-20">{label}</span>
      <input
        value={cfg.username}
        onChange={(e) => onChange({ ...cfg, username: e.target.value }, false)}
        onBlur={() => onChange(cfg, true)}
        placeholder={hint}
        className="flex-1 min-w-40 bg-[#0d0e12] border border-[#2a2c34] rounded-md px-3 py-1.5 text-xs text-[#d7d3cb] placeholder-[#565a68] focus:outline-none"
      />
      <button
        onClick={() => onSync(id)}
        disabled={!cfg.enabled || !cfg.username || busy}
        className="px-3 py-1.5 rounded-md border border-[#2a2c34] text-xs text-[#d7d3cb] hover:border-[#4a4e5e] hover:bg-[#1a1c22] disabled:opacity-30 transition"
      >
        {busy ? 'syncing…' : 'Sync'}
      </button>
    </div>
  )
}

function SourcesPanel() {
  const [settings, setSettings] = useState(null)
  const [busy, setBusy] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api('/sources').then(setSettings).catch(setError)
  }, [])

  const save = async (source, cfg, persist = true) => {
    setError(null)
    const next = { ...settings, [source]: { ...settings[source], ...cfg } }
    setSettings(next)
    if (!persist) return  // typing updates locally; commit on blur/toggle
    try {
      await api('/sources', { method: 'POST', body: JSON.stringify({ [source]: next[source] }) })
    } catch (e) { setError(e) }
  }

  const sync = async (source) => {
    setBusy(source); setResult(null); setError(null)
    try {
      const r = await api(`/sources/${source}/sync`, { method: 'POST' })
      setResult({ source, ...r })
    } catch (e) { setError(e) }
    setBusy(null)
  }

  if (!settings?.github || !settings?.leetcode) return error ? <Section kicker="zero-trust · opt-in" title="Evidence Sources"><ErrorNote error={error} /></Section> : null
  return (
    <Section kicker="zero-trust · opt-in" title="Evidence Sources">
      <p className="text-xs text-[#6b6f80] mb-2">
        Claims are cheap. When a source is on, Legacy pulls your real public activity
        as verified evidence (confidence 0.9). Off means off — nothing is read.
      </p>
      <SourceRow id="github" label="GitHub" hint="github username" cfg={settings.github}
        onChange={(cfg, persist) => save('github', cfg, persist)} onSync={sync} busy={busy === 'github'} />
      <SourceRow id="leetcode" label="LeetCode" hint="leetcode username" cfg={settings.leetcode}
        onChange={(cfg, persist) => save('leetcode', cfg, persist)} onSync={sync} busy={busy === 'leetcode'} />
      <ErrorNote error={error} />
      {result && (
        <div className="mt-2 border border-teal-900 bg-teal-950/30 rounded-lg px-3 py-2">
          <div className="text-xs text-teal-300 mb-1">
            {result.synced} verified evidence node(s) synced from {result.source}
            {result.synced === 0 && ' — nothing new since last sync'}
          </div>
          {(result.evidence || []).map((s, i) => (
            <div key={i} className="text-[11px] font-mono text-[#8b8fa3] truncate">{s}</div>
          ))}
        </div>
      )}
    </Section>
  )
}

/* -------------------------------- hypotheses ------------------------------- */

function HypothesisCard({ hyp }) {
  const [context, setContext] = useState('')
  const [busy, setBusy] = useState(false)
  const [done, setDone] = useState(null)
  const [error, setError] = useState(null)

  const respond = async (response) => {
    setBusy(true); setError(null)
    try {
      setDone(await api('/hypothesis/respond', {
        method: 'POST',
        body: JSON.stringify({ id: hyp.id, response, context }),
      }))
    } catch (e) { setError(e) }
    setBusy(false)
  }

  if (done) {
    return (
      <div className="border border-emerald-900 bg-emerald-950/40 rounded-lg p-4 text-sm">
        <div className="text-emerald-300 font-medium mb-1">Graph recalibrated — {done.status}</div>
        <div className="text-[#8b8fa3] text-xs">
          Confidence {hyp.confidence}% → {done.confidence}%. Your correction is now part of the memory.
        </div>
      </div>
    )
  }

  return (
    <div className="border border-[#2a2c34] rounded-lg p-4 space-y-3">
      <div className="flex items-baseline gap-3">
        <span className="font-mono text-xs text-amber-400">{hyp.confidence}% confidence</span>
        <span className="font-mono text-xs text-[#6b6f80]">{hyp.supporting_nodes} supporting nodes</span>
      </div>
      <p className="text-sm text-[#d7d3cb]">{hyp.hypothesis}</p>
      <p className="text-xs text-[#8b8fa3]">Pattern: {hyp.pattern}</p>
      <input
        value={context}
        onChange={(e) => setContext(e.target.value)}
        placeholder="Add missing context (optional) — Legacy will remember it"
        className="w-full bg-[#0d0e12] border border-[#2a2c34] rounded-md px-3 py-2 text-xs text-[#d7d3cb] placeholder-[#565a68] focus:outline-none"
      />
      <div className="flex gap-2">
        {[['accurate', 'Accurate'], ['partial', 'Partially'], ['inaccurate', 'Missing context']].map(([v, label]) => (
          <button
            key={v}
            disabled={busy}
            onClick={() => respond(v)}
            className="px-3 py-1.5 rounded-md border border-[#2a2c34] text-xs text-[#d7d3cb] hover:border-[#4a4e5e] hover:bg-[#1a1c22] disabled:opacity-40 transition"
          >
            {busy ? '…' : label}
          </button>
        ))}
      </div>
      <ErrorNote error={error} />
    </div>
  )
}

/* ---------------------------------- report --------------------------------- */

function CloseGoal() {
  const [goal, setGoal] = useState('')
  const [reason, setReason] = useState('')
  const [done, setDone] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const close = async () => {
    if (!goal.trim() || busy) return
    setBusy(true); setError(null)
    try {
      await api('/goal/close', { method: 'POST', body: JSON.stringify({ goal, reason }) })
      setDone(true)
    } catch (e) { setError(e) }
    setBusy(false)
  }

  if (done) {
    return <p className="text-sm text-[#8b8fa3]">Recorded. The graph remembers that you moved on — and why.</p>
  }
  return (
    <div className="space-y-2">
      <p className="text-xs text-[#6b6f80]">
        Abandoning a goal on purpose is not failure — it's data. cognee.forget() records the closure instead of pretending it never existed.
      </p>
      <div className="flex flex-wrap gap-2">
        <input value={goal} onChange={(e) => setGoal(e.target.value)} placeholder="goal to close"
          className="flex-1 min-w-40 bg-[#0d0e12] border border-[#2a2c34] rounded-md px-3 py-2 text-xs text-[#d7d3cb] placeholder-[#565a68] focus:outline-none" />
        <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="why you're letting it go"
          className="flex-[2] min-w-52 bg-[#0d0e12] border border-[#2a2c34] rounded-md px-3 py-2 text-xs text-[#d7d3cb] placeholder-[#565a68] focus:outline-none" />
        <button onClick={close} disabled={busy} className="px-3 py-2 rounded-md border border-[#2a2c34] text-xs text-[#d7d3cb] hover:border-[#4a4e5e] disabled:opacity-40 transition">
          {busy ? 'closing…' : 'Close goal'}
        </button>
      </div>
      <ErrorNote error={error} />
    </div>
  )
}

function ReportScreen() {
  const [report, setReport] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const generate = async () => {
    setBusy(true); setError(null)
    try {
      setReport(await api('/report'))
    } catch (e) { setError(e) }
    setBusy(false)
  }

  const newHypothesis = async () => {
    setBusy(true); setError(null)
    try {
      await api('/hypothesis/generate', { method: 'POST' })
      setReport(await api('/report'))
    } catch (e) { setError(e) }
    setBusy(false)
  }

  if (busy && !report) {
    return (
      <div className="space-y-5">
        <p className="text-center text-xs text-[#6b6f80] font-mono pt-4">four engines are traversing your knowledge graph (~30s)…</p>
        {['engine 2 · consistency', 'engine 1 · contradictions', 'engine 3 · inference', 'engine 4 · projection'].map((k) => (
          <Section key={k} kicker={k} title=" "><Skeleton /></Section>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-5">
      {!report && (
        <div className="text-center py-16">
          <p className="text-[#8b8fa3] text-sm mb-5">
            Storage remembers. A real memory <em>notices</em>. Four engines traverse your
            graph and tell you, honestly,
            <br />whether you are becoming who you said you wanted to be.
          </p>
          <button
            onClick={generate}
            disabled={busy}
            className="px-6 py-2.5 rounded-lg bg-[#f0ede6] text-[#0d0e12] text-sm font-medium hover:bg-white disabled:opacity-40 transition"
          >
            Generate 30-Day Report
          </button>
          <div className="max-w-md mx-auto mt-4"><ErrorNote error={error} onRetry={generate} /></div>
        </div>
      )}

      {report && (
        <>
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#6b6f80] font-mono">generated {report.generated}</span>
            <button onClick={generate} disabled={busy} className="text-xs text-[#8b8fa3] hover:text-white transition">
              {busy ? 'refreshing…' : '↻ regenerate'}
            </button>
          </div>

          {report.alignment && (
            <section className="border border-[#23252d] rounded-xl bg-[#121318] p-6 flex items-center gap-6">
              <div className="text-center shrink-0">
                <div className={`font-serif text-6xl leading-none ${
                  report.alignment.score > 75 ? 'text-emerald-300'
                  : report.alignment.score >= 40 ? 'text-amber-300' : 'text-rose-300'
                }`}>{report.alignment.score}</div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-[#6b6f80] mt-1">alignment</div>
              </div>
              <div>
                <div className={`text-sm font-medium mb-1 ${
                  report.alignment.score > 75 ? 'text-emerald-300'
                  : report.alignment.score >= 40 ? 'text-amber-300' : 'text-rose-300'
                }`}>{report.alignment.verdict}</div>
                <p className="text-xs text-[#8b8fa3] leading-relaxed">
                  How closely your verified behavior matches who you said you want to become.
                  {' '}{report.alignment.explanation} Deterministic — recompute it yourself.
                </p>
              </div>
            </section>
          )}
          <ErrorNote error={error} onRetry={generate} />

          <Section kicker="engine 2 · deterministic ledger arithmetic" title="Goal Consistency">
            {busy ? <Skeleton /> : <Markdown text={report.consistency} />}
          </Section>

          <Section kicker="engine 1 · multi-hop graph traversal" title="Unverified Claims & Contradictions">
            {busy ? <Skeleton /> : <Markdown text={report.contradictions} />}
          </Section>

          <Section kicker="engine 3 · behavioral inference — asks, never tells" title="Hypotheses Awaiting Your Response">
            {(report.hypotheses || []).length === 0 ? (
              <div className="text-sm text-[#8b8fa3]">
                No pending hypotheses.{' '}
                <button onClick={newHypothesis} className="underline hover:text-white">Run the inference engine</button>
              </div>
            ) : (
              <div className="space-y-3">
                {(report.hypotheses || []).map((h) => <HypothesisCard key={h.id} hyp={h} />)}
              </div>
            )}
          </Section>

          <Section kicker="engine 4 · trajectory projection" title="Your Next Year, At This Pace">
            {busy ? <Skeleton /> : <Markdown text={report.projection} />}
          </Section>

          <Section kicker="legacy asks" title="The Question You're Avoiding">
            <p className="font-serif italic text-[#e8e4da] text-base leading-relaxed">
              {report.open_question}
            </p>
          </Section>

        </>
      )}
    </div>
  )
}

/* ---------------------------------- graph ---------------------------------- */

const GRAPH_COLORS = {
  Entity: '#34d399',
  EntityType: '#818cf8',
  TextSummary: '#565a68',
  DocumentChunk: '#3f424e',
  TextDocument: '#8b6f47',
  NodeSet: '#f59e0b',
}

function GraphScreen() {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState(null)
  const ref = useRef()

  useEffect(() => {
    api('/graph')
      .then((g) => {
        const nodes = g.nodes.map((n) => ({
          id: n.id,
          type: n.type,
          name: (n.properties?.text || n.properties?.name || n.label || '').slice(0, 180),
        }))
        const ids = new Set(nodes.map((n) => n.id))
        const links = g.edges
          .filter((e) => ids.has(e.source) && ids.has(e.target))
          .map((e) => ({ source: e.source, target: e.target, label: e.label }))
        setData({ nodes, links })
        setStats({ nodes: nodes.length, links: links.length })
      })
      .catch(setError)
  }, [])

  const paint = useCallback((node, ctx, scale) => {
    const color = GRAPH_COLORS[node.type] || '#d7d3cb'
    const r = node.type === 'Entity' ? 4 : 2.5
    ctx.beginPath()
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI)
    ctx.fillStyle = color
    ctx.fill()
    if (scale > 2.2 && node.type === 'Entity') {
      ctx.font = `${10 / scale * 2}px monospace`
      ctx.fillStyle = '#8b8fa3'
      ctx.fillText(node.name.slice(0, 28), node.x + 5, node.y + 2)
    }
  }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-[#8b8fa3]">
          Your memory is not a chat log. This is the actual Cognee knowledge graph of who you're becoming.
        </p>
        {stats && <span className="text-xs font-mono text-[#6b6f80] shrink-0 ml-3">{stats.nodes} nodes · {stats.links} edges</span>}
      </div>
      <div className="flex gap-4 text-[11px] font-mono text-[#6b6f80]">
        <span><span style={{ color: GRAPH_COLORS.Entity }}>●</span> entity</span>
        <span><span style={{ color: GRAPH_COLORS.EntityType }}>●</span> type</span>
        <span><span style={{ color: GRAPH_COLORS.TextSummary }}>●</span> summary</span>
        <span><span style={{ color: GRAPH_COLORS.TextDocument }}>●</span> memory string</span>
      </div>
      <ErrorNote error={error} />
      <div className="border border-[#23252d] rounded-xl overflow-hidden bg-[#0a0b0e]" style={{ height: 560 }}>
        {!data && !error && <div className="p-5"><Skeleton lines={6} /></div>}
        {data && (
          <ForceGraph2D
            ref={ref}
            graphData={data}
            width={Math.min(928, window.innerWidth - 60)}
            height={560}
            backgroundColor="#0a0b0e"
            nodeCanvasObject={paint}
            nodePointerAreaPaint={(node, color, ctx) => {
              ctx.beginPath(); ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI)
              ctx.fillStyle = color; ctx.fill()
            }}
            nodeLabel={(n) => { const esc = String(n.name).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); return `<div style="max-width:340px;font-size:11px">${n.type}: ${esc}</div>` }}
            linkColor={() => 'rgba(120,125,145,0.18)'}
            linkWidth={0.5}
            cooldownTicks={120}
            onEngineStop={() => ref.current?.zoomToFit(400, 40)}
          />
        )}
      </div>
      <p className="text-xs text-[#6b6f80]">
        Zoom in to read entity names. Green entities are the people, goals, problems and projects
        Cognee extracted; every reflection you write grows this graph.
      </p>
    </div>
  )
}

/* ----------------------------------- chat ---------------------------------- */

function ChatScreen() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, busy])

  const send = async () => {
    const text = input.trim()
    if (!text || busy) return
    setInput(''); setError(null)
    const next = [...messages, { role: 'user', content: text }]
    setMessages(next); setBusy(true)
    try {
      const r = await api('/chat', { method: 'POST', body: JSON.stringify({ messages: next.slice(-24) }) })
      if (!r.reply) throw new Error('Legacy returned an empty reply — try again.')
      setMessages([...next, { role: 'assistant', content: r.reply }])
    } catch (e) {
      setError(e); setMessages(next)
    }
    setBusy(false)
  }

  return (
    <div className="flex flex-col" style={{ minHeight: '58vh' }}>
      {messages.length === 0 && (
        <div className="text-center py-14">
          <p className="font-serif italic text-[#e8e4da] text-lg">Talk to the AI that actually knows you.</p>
          <p className="text-xs text-[#6b6f80] mt-2 max-w-md mx-auto">
            Analysis, advice, anything — like ChatGPT, except Legacy still remembers this
            conversation next month. Try: "what's my favourite bike?" or "what did I build in June?"
          </p>
        </div>
      )}

      <div className="flex-1 space-y-4">
        {messages.map((m, i) => (
          m.role === 'user' ? (
            <div key={i} className="flex justify-end">
              <div className="max-w-[85%] bg-[#1e2028] border border-[#2a2c34] rounded-2xl rounded-br-sm px-4 py-2.5 text-sm text-[#e8e4da]">
                {m.content}
              </div>
            </div>
          ) : (
            <div key={i} className="flex">
              <div className="max-w-[92%] border border-[#23252d] bg-[#121318] rounded-2xl rounded-bl-sm px-4 py-3">
                <div className="text-[10px] uppercase tracking-[0.2em] text-[#565a68] mb-1">legacy</div>
                <Markdown text={m.content} />
              </div>
            </div>
          )
        ))}
        {busy && (
          <div className="flex">
            <div className="border border-[#23252d] bg-[#121318] rounded-2xl rounded-bl-sm px-4 py-3 text-sm text-[#6b6f80] animate-pulse">
              thinking — checking memory if it needs to…
            </div>
          </div>
        )}
        <ErrorNote error={error} />
        <div ref={endRef} />
      </div>

      <div className="mt-5 flex gap-2 sticky bottom-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder="say anything — Legacy remembers what matters…"
          className="flex-1 bg-[#0d0e12] border border-[#2a2c34] rounded-xl px-4 py-3 text-sm text-[#d7d3cb] placeholder-[#565a68] focus:outline-none focus:border-[#4a4e5e]"
        />
        <button
          onClick={send}
          disabled={busy || !input.trim()}
          className="px-5 py-3 rounded-xl bg-[#f0ede6] text-[#0d0e12] text-sm font-medium hover:bg-white disabled:opacity-30 transition"
        >
          Send
        </button>
      </div>
      {messages.length > 0 && (
        <p className="text-[10px] text-[#3f424e] font-mono text-center mt-2">
          ◆ the durable parts of this conversation are being remembered — close the tab, Legacy still knows
        </p>
      )}
    </div>
  )
}

/* ---------------------------------- profile -------------------------------- */

const TYPE_LABELS = {
  GOAL: 'goals', ACTION: 'actions', CLAIM: 'claims', EVIDENCE: 'verified evidence',
  CONTRADICTION: 'contradictions', PREFERENCE: 'preferences', FACT: 'facts',
  PROJECT: 'project knowledge', CALIBRATION: 'calibrations',
}

let _profileCache = null

function ProfileScreen() {
  const [profile, setProfile] = useState(_profileCache)
  const [error, setError] = useState(null)

  const load = (force = false) => {
    if (_profileCache && !force) return
    setError(null)
    if (force) setProfile(null)
    api('/profile').then((p) => { _profileCache = p; setProfile(p) }).catch(setError)
  }
  useEffect(() => { load() }, [])

  return (
    <div className="space-y-5">
      <Section kicker="from the graph, nothing else" title="What Legacy Knows About You">
        {profile && (
          <button onClick={() => load(true)} className="float-right text-xs text-[#6b6f80] hover:text-white transition -mt-8">↻ refresh</button>
        )}
        {error && <ErrorNote error={error} onRetry={() => load(true)} />}
        {!profile && !error && <Skeleton lines={8} />}
        {profile && (
          <>
            <Markdown text={profile.narrative} />
            {profile.memory_stats && (
            <div className="flex flex-wrap gap-2 mt-4 pt-3 border-t border-[#23252d]">
              <span className="text-[11px] font-mono text-[#6b6f80] px-2 py-1">
                {profile.memory_stats.total_nodes} memories since {profile.memory_stats.since}
              </span>
              {Object.entries(profile.memory_stats.by_type || {}).map(([t, n]) => (
                <span key={t} className={`text-[11px] font-mono px-2 py-1 rounded-md border ${NODE_STYLES[t] || 'border-[#2a2c34] text-[#8b8fa3]'}`}>
                  {n} {TYPE_LABELS[t] || t.toLowerCase()}
                </span>
              ))}
            </div>
            )}
          </>
        )}
      </Section>

      <SourcesPanel />

      <Section kicker="cognee.forget() · your memory, your rules" title="Let a Goal Go">
        <CloseGoal />
      </Section>
    </div>
  )
}

/* ---------------------------------- quests --------------------------------- */

function JourneyChart({ journey }) {
  const [hover, setHover] = useState(null)
  if (!journey || journey.length < 2) return null
  const W = 860, H = 130, PAD = 8
  const xs = journey.map((_, i) => PAD + (i * (W - 2 * PAD)) / (journey.length - 1))
  const maxXp = Math.max(...journey.map((d) => d.xp), 1)
  const ys = journey.map((d) => H - PAD - (d.xp / maxXp) * (H - 2 * PAD))
  const line = xs.map((x, i) => `${i ? 'L' : 'M'}${x},${ys[i]}`).join(' ')
  const area = `${line} L${xs[xs.length - 1]},${H} L${xs[0]},${H} Z`
  const approxLen = 1200

  return (
    <div className="relative">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: 130 }}
           onMouseLeave={() => setHover(null)}>
        <path d={area} fill="rgba(52,211,153,0.10)" className="journey-area" />
        <path d={line} fill="none" stroke="#34d399" strokeWidth="2"
              strokeLinecap="round" className="journey-line"
              strokeDasharray={approxLen} style={{ '--len': approxLen }} />
        {journey.map((d, i) => (
          <g key={d.date} className="journey-dot" style={{ animationDelay: `${0.2 + i * 0.06}s` }}>
            <circle cx={xs[i]} cy={ys[i]} r="3" fill="#34d399" />
            <circle cx={xs[i]} cy={ys[i]} r="11" fill="transparent"
                    onMouseEnter={() => setHover({ ...d, x: xs[i], y: ys[i] })} />
          </g>
        ))}
        {hover && <line x1={hover.x} y1={PAD} x2={hover.x} y2={H - PAD}
                        stroke="rgba(139,143,163,0.35)" strokeWidth="1" />}
      </svg>
      {hover && (
        <div className="absolute pointer-events-none bg-[#1a1c22] border border-[#2a2c34] rounded-md px-2.5 py-1.5 text-[11px] font-mono text-[#d7d3cb]"
             style={{ left: `${(hover.x / W) * 100}%`, top: 0, transform: 'translateX(-50%)' }}>
          {hover.date} · {hover.xp} xp <span className="text-emerald-400">+{hover.gained}</span>
        </div>
      )}
      <div className="flex justify-between text-[10px] font-mono text-[#565a68] mt-1">
        <span>{journey[0].date}</span>
        <span className="text-[#8b8fa3]">{maxXp} xp earned — every point is a verified day</span>
        <span>{journey[journey.length - 1].date}</span>
      </div>
    </div>
  )
}

const VERIFY_LABEL = { github: 'proven by commit', leetcode: 'proven by solve', chat: 'proven in chat' }

function QuestCard({ quest, onVerified }) {
  const [busy, setBusy] = useState(false)
  const [verdict, setVerdict] = useState(null)
  const [error, setError] = useState(null)

  const prove = async () => {
    setBusy(true); setError(null)
    try {
      const r = await api(`/quests/${quest.id}/verify`, { method: 'POST' })
      if (r.verdict) setVerdict(r.verdict)
      else if (r.message) setVerdict({ done: r.quest?.status === 'DONE', proof: r.message })
      if (r.quest?.status === 'DONE') onVerified?.()
    } catch (e) { setError(e) }
    setBusy(false)
  }

  const done = quest.status === 'DONE' || verdict?.done
  const justDone = verdict?.done
  return (
    <div className={`relative border rounded-xl p-4 space-y-2 ${done ? 'border-emerald-900 bg-emerald-950/30' : 'border-[#2a2c34] bg-[#121318]'} ${justDone ? 'quest-glow' : ''}`}>
      {justDone && <span className="xp-pop right-4 top-2 font-mono text-emerald-300 text-sm">+{quest.xp} xp</span>}
      <div className="flex items-start justify-between gap-3">
        <div className="text-sm text-[#e8e4da] font-medium">{done ? '✓ ' : ''}{quest.title}</div>
        <span className="font-mono text-xs text-amber-300 shrink-0">+{quest.xp} xp</span>
      </div>
      <p className="text-xs text-[#8b8fa3]">{quest.why}</p>
      <div className="flex items-center justify-between gap-3">
        <span className="text-[10px] uppercase tracking-[0.15em] font-mono text-[#565a68]">{VERIFY_LABEL[quest.verify]}</span>
        {!done && (
          <button onClick={prove} disabled={busy}
            className="px-3 py-1.5 rounded-md border border-[#2a2c34] text-xs text-[#d7d3cb] hover:border-[#4a4e5e] hover:bg-[#1a1c22] disabled:opacity-40 transition">
            {busy ? 'checking receipts…' : 'Prove it'}
          </button>
        )}
      </div>
      {verdict && !verdict.done && (
        <p className="text-xs text-amber-400/90">Not proven: {verdict.proof}</p>
      )}
      {done && (quest.proof || verdict?.proof) && (
        <p className="text-xs text-emerald-400/80">{quest.proof || verdict.proof}</p>
      )}
      <ErrorNote error={error} />
    </div>
  )
}

function QuestsScreen() {
  const [board, setBoard] = useState(null)
  const [error, setError] = useState(null)

  const load = () => api('/quests').then(setBoard).catch(setError)
  useEffect(() => { load() }, [])

  return (
    <div className="space-y-5">
      <Section kicker="deterministic — verified evidence is worth more" title="Character Sheet">
        {!board && !error && <Skeleton lines={5} />}
        {board && (
          <div className="space-y-2.5">
            {(board.levels || []).map((l) => (
              <div key={l.domain} className="flex items-center gap-3">
                <span className="font-mono text-xs text-amber-300 w-12 shrink-0">Lv {l.level}</span>
                <span className="text-sm text-[#d7d3cb] w-56 shrink-0 truncate">{l.domain}</span>
                <div className="flex-1 h-2 rounded-full bg-[#1a1c22] overflow-hidden">
                  <div className="h-full rounded-full bg-gradient-to-r from-emerald-700 to-emerald-400"
                       style={{ width: `${Math.round(l.progress * 100)}%` }} />
                </div>
                <span className="font-mono text-[10px] text-[#565a68] w-24 text-right shrink-0">{l.xp}/{l.next_level_xp} xp</span>
              </div>
            ))}
          </div>
        )}
      </Section>

      <Section kicker="cumulative verified xp · hover any day" title="Your Journey">
        {!board && !error && <Skeleton lines={3} />}
        {board && <JourneyChart journey={board.journey} />}
      </Section>

      <Section kicker="generated from your graph · no checkboxes, only receipts" title="Today's Quests">
        <ErrorNote error={error} onRetry={load} />
        {!board && !error && <Skeleton lines={6} />}
        {board && (
          <div className="space-y-3">
            {(board.quests || []).map((q) => <QuestCard key={q.id} quest={q} onVerified={load} />)}
          </div>
        )}
        <p className="text-[11px] text-[#565a68] mt-3">
          You don't tick these — you prove them. Legacy checks your synced evidence and
          conversation memory; a completed quest becomes a verified action in the graph
          and moves your real scores.
        </p>
      </Section>
    </div>
  )
}

/* ----------------------------------- app ----------------------------------- */

export default function App() {
  const [tab, setTab] = useState('chat')
  const [visited, setVisited] = useState({ chat: true })
  const go = (id) => { setVisited((v) => ({ ...v, [id]: true })); setTab(id) }

  return (
    <div className="max-w-3xl mx-auto px-5 py-10">
      <header className="mb-8">
        <div className="flex items-baseline justify-between">
          <h1 className="font-serif text-3xl tracking-tight text-[#f0ede6]">
            Legacy<span className="text-emerald-400">.</span>
          </h1>
          <span className="font-mono text-[11px] text-[#565a68]">memory by cognee</span>
        </div>
        <p className="text-sm text-[#8b8fa3] mt-1 italic font-serif">
          The AI that actually knows you.
        </p>
        <nav className="flex gap-1 mt-6 border-b border-[#23252d]">
          {[['chat', 'Chat'], ['profile', 'Profile'], ['quests', 'Quests'], ['report', 'Insights'], ['graph', 'Memory Graph']].map(([id, label]) => (
            <button
              key={id}
              onClick={() => go(id)}
              className={`px-4 py-2 text-sm transition border-b-2 -mb-px ${
                tab === id
                  ? 'border-[#f0ede6] text-[#f0ede6]'
                  : 'border-transparent text-[#6b6f80] hover:text-[#b8b4ab]'
              }`}
            >
              {label}
            </button>
          ))}
        </nav>
      </header>

      <div className={tab === 'chat' ? '' : 'hidden'}><ChatScreen /></div>
      {visited.profile && <div className={tab === 'profile' ? '' : 'hidden'}><ProfileScreen /></div>}
      {visited.quests && <div className={tab === 'quests' ? '' : 'hidden'}><QuestsScreen /></div>}
      {visited.report && <div className={tab === 'report' ? '' : 'hidden'}><ReportScreen /></div>}
      {visited.graph && <div className={tab === 'graph' ? '' : 'hidden'}><GraphScreen /></div>}

      <footer className="mt-14 text-center text-[11px] text-[#3f424e] font-mono">
        the house always remembers · built on cognee remember / recall / forget
      </footer>
    </div>
  )
}
