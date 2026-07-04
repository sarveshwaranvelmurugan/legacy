import { useState } from 'react'
import { marked } from 'marked'

const API = '/api'

const NODE_STYLES = {
  GOAL: 'bg-emerald-950/60 text-emerald-300 border-emerald-800',
  ACTION: 'bg-indigo-950/60 text-indigo-300 border-indigo-800',
  CLAIM: 'bg-amber-950/60 text-amber-300 border-amber-800',
  EVIDENCE: 'bg-teal-950/60 text-teal-300 border-teal-800',
  CONTRADICTION: 'bg-rose-950/60 text-rose-300 border-rose-800',
}

function Markdown({ text }) {
  if (!text) return null
  return <div className="md text-sm text-[#b8b4ab]" dangerouslySetInnerHTML={{ __html: marked.parse(text) }} />
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

function ReflectScreen() {
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)

  const submit = async () => {
    if (!text.trim()) return
    setBusy(true)
    setResult(null)
    const res = await fetch(`${API}/reflect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
    setResult(await res.json())
    setBusy(false)
  }

  return (
    <div className="space-y-5">
      <Section kicker="daily reflection" title="What did you actually do today?">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={5}
          placeholder="Two minutes of honesty. Legacy distills it into typed memory before Cognee ever sees it…"
          className="w-full bg-[#0d0e12] border border-[#2a2c34] rounded-lg p-3 text-sm text-[#d7d3cb] placeholder-[#565a68] focus:outline-none focus:border-[#4a4e5e] resize-none"
        />
        <button
          onClick={submit}
          disabled={busy}
          className="mt-3 px-5 py-2 rounded-lg bg-[#f0ede6] text-[#0d0e12] text-sm font-medium hover:bg-white disabled:opacity-40 transition"
        >
          {busy ? 'Distilling…' : 'Remember this'}
        </button>
      </Section>

      {result && (
        <Section kicker="compact memory engine" title={`${result.nodes.length} node(s) extracted — noise discarded`}>
          {result.nodes.length === 0 && <p className="text-sm text-[#8b8fa3]">{result.message}</p>}
          <div className="space-y-2">
            {result.nodes.map((n, i) => (
              <div key={i} className={`border rounded-lg px-3 py-2 text-sm ${NODE_STYLES[n.type] || ''}`}>
                <span className="font-mono text-[11px] mr-2 opacity-80">[{n.type}]</span>
                {n.text}
                <span className="font-mono text-[11px] ml-2 opacity-60">conf {n.confidence}</span>
              </div>
            ))}
          </div>
          {result.nodes.length > 0 && (
            <p className="text-xs text-[#6b6f80] mt-3">
              Ingested via cognee.remember() — the graph is rebuilding in the background.
              {result.agent_will_ask && (
                <span className="block mt-1 text-amber-400/80">
                  Legacy noticed a pattern forming — a new hypothesis will be waiting in your report.
                </span>
              )}
            </p>
          )}
        </Section>
      )}
    </div>
  )
}

function HypothesisCard({ hyp, onResponded }) {
  const [context, setContext] = useState('')
  const [busy, setBusy] = useState(false)
  const [done, setDone] = useState(null)

  const respond = async (response) => {
    setBusy(true)
    const res = await fetch(`${API}/hypothesis/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: hyp.id, response, context }),
    })
    const updated = await res.json()
    setDone(updated)
    setBusy(false)
    onResponded?.(updated)
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
    </div>
  )
}

function ReportScreen() {
  const [report, setReport] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const generate = async () => {
    setBusy(true)
    setError(null)
    try {
      const res = await fetch(`${API}/report`)
      if (!res.ok) throw new Error(await res.text())
      setReport(await res.json())
    } catch (e) {
      setError(String(e))
    }
    setBusy(false)
  }

  const newHypothesis = async () => {
    setBusy(true)
    await fetch(`${API}/hypothesis/generate`, { method: 'POST' })
    await generate()
  }

  return (
    <div className="space-y-5">
      {!report && (
        <div className="text-center py-16">
          <p className="text-[#8b8fa3] text-sm mb-5">
            Four reasoning engines traverse your knowledge graph and tell you, honestly,
            <br />whether you are becoming who you said you wanted to be.
          </p>
          <button
            onClick={generate}
            disabled={busy}
            className="px-6 py-2.5 rounded-lg bg-[#f0ede6] text-[#0d0e12] text-sm font-medium hover:bg-white disabled:opacity-40 transition"
          >
            {busy ? 'Traversing the graph… (30–60s)' : 'Generate 30-Day Report'}
          </button>
          {error && <p className="text-rose-400 text-xs mt-4">{error}</p>}
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

          <Section kicker="engine 2 · recall() + arithmetic" title="Goal Consistency">
            <Markdown text={report.consistency} />
          </Section>

          <Section kicker="engine 1 · multi-hop graph traversal" title="Unverified Claims & Contradictions">
            <Markdown text={report.contradictions} />
          </Section>

          <Section kicker="engine 3 · behavioral inference — asks, never tells" title="Hypotheses Awaiting Your Response">
            {report.hypotheses.length === 0 ? (
              <div className="text-sm text-[#8b8fa3]">
                No pending hypotheses.{' '}
                <button onClick={newHypothesis} className="underline hover:text-white">Run the inference engine</button>
              </div>
            ) : (
              <div className="space-y-3">
                {report.hypotheses.map((h) => (
                  <HypothesisCard key={h.id} hyp={h} />
                ))}
              </div>
            )}
          </Section>

          <Section kicker="engine 4 · trajectory projection" title="Your Next Year, At This Pace">
            <Markdown text={report.projection} />
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

export default function App() {
  const [tab, setTab] = useState('reflect')

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
          Are you becoming who you said you wanted to be?
        </p>
        <nav className="flex gap-1 mt-6 border-b border-[#23252d]">
          {[['reflect', 'Reflect'], ['report', '30-Day Report']].map(([id, label]) => (
            <button
              key={id}
              onClick={() => setTab(id)}
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

      {tab === 'reflect' ? <ReflectScreen /> : <ReportScreen />}

      <footer className="mt-14 text-center text-[11px] text-[#3f424e] font-mono">
        the house always remembers · built on cognee remember / recall / forget
      </footer>
    </div>
  )
}
