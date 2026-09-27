// 워크플로 스크립트 모의 실행기: agent/pipeline/parallel/phase/log 를 흉내 내 제어 흐름만 검증한다.
import fs from 'fs'
const src = fs.readFileSync(process.argv[2], 'utf8')
if (/Date\.now\(|Math\.random\(|new Date\(\)/.test(src)) { console.error('금지 API 사용'); process.exit(1) }
const metaMatch = src.match(/export const meta = (\{[\s\S]*?\n\})/)
const meta = eval('(' + metaMatch[1] + ')')
const body = src.replace(/export const meta = \{[\s\S]*?\n\}/, '')
const phasesUsed = new Set([...body.matchAll(/phase: '([^']+)'/g)].map(m => m[1]))
const metaTitles = new Set(meta.phases.map(p => p.title))
for (const p of phasesUsed) if (!metaTitles.has(p)) { console.error('meta.phases 에 없는 phase:', p); process.exit(1) }

const calls = []
const scenario = JSON.parse(process.argv[3])
const qaRound = {}
const sleep = ms => new Promise(r => setTimeout(r, ms))
async function agent(prompt, opts) {
  calls.push(opts.label)
  const id = opts.label.split(':')[1]
  const s = scenario[id] || {}
  await sleep(s.delay || 10)
  if (opts.agentType === 'asset-qa') {
    qaRound[id] = (qaRound[id] || 0) + 1
    const v = (s.qa || ['pass'])[qaRound[id] - 1] || 'pass'
    return { id, verdict: v, checks: [{ name: 'x', result: v === 'pass' ? 'pass' : 'fail' }], issues: v === 'pass' ? [] : ['문제'], retryable: s.retryable !== false }
  }
  if (s.produce === 'null') return null
  return { id, status: s.produce || 'generated', outputs: ['a.wav'], calls: 1, notes: '' }
}
let active = 0; const CAP = 2; const waiters = []
async function slot(fn) { while (active >= CAP) await new Promise(r => waiters.push(r)); active++; try { return await fn() } finally { active--; waiters.shift()?.() } }
async function pipeline(items, ...stages) {
  return Promise.all(items.map((it, i) => slot(async () => {
    let v = it
    try { for (const st of stages) v = await st(v, it, i) ; return v } catch (e) { console.error('stage error', e); return null }
  })))
}
async function parallel(thunks) { return Promise.all(thunks.map(t => t().catch(() => null))) }
const logs = []
const fn = new Function('args', 'agent', 'pipeline', 'parallel', 'phase', 'log', 'budget', `return (async () => {${body}})()`)
const args = JSON.parse(process.argv[4])
const out = await fn(args, agent, pipeline, parallel, () => {}, m => logs.push(m), { total: null, spent: () => 0, remaining: () => Infinity })
console.log(JSON.stringify({ summary: out.summary, halted: out.halted, finals: out.results.map(r => [r.id, r.final, r.reworks]), calls, logs }, null, 1))
