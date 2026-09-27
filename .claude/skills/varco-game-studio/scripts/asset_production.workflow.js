export const meta = {
  name: 'varco-asset-production',
  description: '승인된 에셋 매니페스트를 VARCO API로 제작하고, 에셋마다 QA 검증과 한 번의 재작업을 거친다',
  whenToUse: 'varco-game-studio 오케스트레이터의 3단계(에셋 제작)에서만 호출한다',
  phases: [
    { title: '제작', detail: '에셋 담당 에이전트가 VARCO API로 생성한다. 드라이런이면 요청 명세만 만든다' },
    { title: '검증', detail: 'asset-qa가 매니페스트의 acceptance 기준으로 검사한다' },
    { title: '재작업', detail: '고칠 수 있는 실패만 QA 피드백을 반영해 다시 만들고 재검증한다' },
  ],
}

// args 형식 (오케스트레이터가 채운다)
// {
//   slug, mode: 'live'|'dry-run', budget: 숫자, maxRework: 1, allowUnknownPrice: bool,
//   paths: { runMeta, manifest, ledger, gameDir, workspace },
//   items: [{ id, owner, category, priority, manual: bool }]   // 우선순위 순으로 정렬해서 넘긴다
// }

const PRODUCE = {
  type: 'object',
  required: ['id', 'status', 'outputs', 'calls', 'notes'],
  properties: {
    id: { type: 'string' },
    status: { type: 'string', enum: ['generated', 'dry-run', 'failed', 'budget_blocked', 'auth_failed', 'credit_exhausted'] },
    outputs: { type: 'array', items: { type: 'string' } },
    calls: { type: 'integer' },
    est_credits_spent: { type: 'number' },
    notes: { type: 'string' },
    error: { type: 'string' },
  },
}

const QA = {
  type: 'object',
  required: ['id', 'verdict', 'checks', 'issues', 'retryable'],
  properties: {
    id: { type: 'string' },
    verdict: { type: 'string', enum: ['pass', 'fail', 'cannot_verify'] },
    checks: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'result'],
        properties: {
          name: { type: 'string' },
          result: { type: 'string', enum: ['pass', 'fail', 'skip'] },
          detail: { type: 'string' },
        },
      },
    },
    issues: { type: 'array', items: { type: 'string' } },
    retryable: { type: 'boolean' },
    fix_hint: { type: 'string' },
  },
}

const A = args || {}
const P = A.paths || {}
const items = Array.isArray(A.items) ? A.items : []
const mode = A.mode === 'live' ? 'live' : 'dry-run'
const maxRework = Number.isInteger(A.maxRework) ? A.maxRework : 1
const SHORT = {
  'sound-designer': 'sound', 'voice-director': 'voice', 'visual-artist': 'visual',
  'localization-specialist': 'l10n', 'marketing-artist': 'marketing',
}
// 다시 시도해도 결과가 같은 실패. 하나라도 나오면 남은 에셋은 호출하지 않는다(남은 크레딧·한도를 지키기 위해).
const FATAL = ['auth_failed', 'credit_exhausted']
let halt = null

if (!items.length) {
  log('제작할 에셋이 없습니다.')
  return { results: [], summary: { total: 0 }, halted: null }
}

const context = [
  `게임: ${A.slug}`,
  `실행 설정: ${P.runMeta}`,
  `승인된 매니페스트: ${P.manifest}`,
  `확정 폴더: ${P.gameDir}  작업 폴더: ${P.workspace}`,
  `크레딧 장부: ${P.ledger}`,
  mode === 'live'
    ? `모드: live. varco_client.py call 에 --ledger ${P.ledger} --budget ${A.budget} --asset-id <id> 를 반드시 붙인다.`
    : `모드: dry-run. varco_client.py call 에 --dry-run --ledger ${P.ledger} --asset-id <id> 를 붙인다. 실제 호출은 하지 않는다.`,
  mode === 'live' && A.allowUnknownPrice
    ? '단가 미공개 API(번역·Voice-to-Face·VC Acting) 호출을 사용자가 승인했다. 이 API 에는 --allow-unknown-price 를 붙인다.'
    : '단가 미공개 API 에는 --allow-unknown-price 를 붙이지 않는다. 막히면 budget_blocked 로 반환한다.',
].join('\n')

function producePrompt(item, qa) {
  const lines = [
    `매니페스트에서 id 가 "${item.id}" 인 에셋 하나를 제작하라.`,
    context,
    '매니페스트는 읽기만 한다. 상태 갱신은 리더가 한다.',
    `결과 파일은 에셋의 output 위치(확정 폴더 기준)에 저장하고, 작업 기록은 ${P.workspace}/03_${SHORT[item.owner] || 'asset'}_${item.id}.json 에 남긴다.`,
    'varco_client.py 종료 코드가 3(예산 초과)이면 status=budget_blocked, 10(인증)이면 auth_failed, 11(크레딧·권한)이면 credit_exhausted 로 즉시 끝낸다. 이 세 경우는 재시도하지 않는다.',
    '최종 응답은 사용자에게 보내는 글이 아니라 스키마에 맞춘 반환 데이터다.',
  ]
  if (qa) {
    lines.push(
      '이번은 재작업이다. 아래 QA 결과의 실패 항목만 고친다. 통과한 결과물은 건드리지 않는다.',
      `QA 결과: ${JSON.stringify({ verdict: qa.verdict, issues: qa.issues, fix_hint: qa.fix_hint, failed: (qa.checks || []).filter(c => c.result === 'fail') })}`,
    )
  }
  return lines.join('\n')
}

function qaPrompt(item, prod, round) {
  return [
    `에셋 "${item.id}"(${item.category}, 담당 ${item.owner})을 검증하라. 검증 ${round}회차다.`,
    context,
    `제작 결과: ${JSON.stringify({ status: prod.status, outputs: prod.outputs, notes: prod.notes })}`,
    mode === 'live'
      ? '실제 파일을 스크립트로 검사한다. 파일이 있는지만 보지 말고 acceptance 기준 값을 측정해 대조한다.'
      : '드라이런이다. {파일}.dryrun.json 요청 명세를 varco_client.py validate 로 검사하고, 출력 경로·개수·파라미터가 매니페스트와 맞는지 대조한다.',
    `검사 결과를 ${P.workspace}/03_assetqa_${item.id}${round > 1 ? `_r${round}` : ''}.json 에 저장한다.`,
    'retryable 은 제작 담당이 파라미터나 프롬프트를 바꿔 고칠 수 있을 때만 true 다. 원본 입력 누락처럼 담당이 고칠 수 없는 문제는 false 다.',
    '최종 응답은 스키마에 맞춘 반환 데이터다.',
  ].join('\n')
}

function finalStatus(prod, qa) {
  if (prod.status === 'manual_pending') return 'manual_pending'
  if (prod.status === 'halted' || FATAL.includes(prod.status)) return 'halted'
  if (prod.status === 'budget_blocked') return 'budget_blocked'
  if (prod.status === 'failed') return 'failed'
  if (!qa || qa.verdict !== 'pass') return 'qa_failed'
  return mode === 'live' ? 'qa_passed' : 'dry-run'
}

function noteHalt(item, prod) {
  if (!halt && FATAL.includes(prod.status)) {
    halt = `${item.id}: ${prod.status}${prod.error ? ' — ' + prod.error : ''}`
    log(`중단 사유 발생(${halt}). 아직 시작하지 않은 에셋은 호출하지 않습니다.`)
  }
}

log(`에셋 ${items.length}건 제작을 시작합니다. 모드: ${mode}${mode === 'live' ? `, 예산 ${A.budget} 크레딧` : ''}`)

const results = await pipeline(
  items,
  // 1) 제작
  async (item) => {
    if (item.manual) {
      return { item, prod: { id: item.id, status: 'manual_pending', outputs: [], calls: 0, notes: '공개 API 없음 — 사람이 제작' } }
    }
    if (halt) {
      return { item, prod: { id: item.id, status: 'halted', outputs: [], calls: 0, notes: `앞선 치명적 실패로 호출하지 않음: ${halt}` } }
    }
    const prod = await agent(producePrompt(item, null), {
      agentType: item.owner, schema: PRODUCE, phase: '제작', label: `제작:${item.id}`,
    })
    if (!prod) {
      return { item, prod: { id: item.id, status: 'failed', outputs: [], calls: 0, notes: '제작 에이전트가 결과 없이 종료됨' } }
    }
    noteHalt(item, prod)
    return { item, prod }
  },
  // 2) 검증
  async (r) => {
    const { item, prod } = r
    if (!['generated', 'dry-run'].includes(prod.status)) return { ...r, qa: null }
    const qa = await agent(qaPrompt(item, prod, 1), {
      agentType: 'asset-qa', schema: QA, phase: '검증', label: `검증:${item.id}`,
    })
    return { ...r, qa }
  },
  // 3) 재작업: 고칠 수 있는 실패만, 최대 maxRework 회
  async (r) => {
    let { item, prod, qa } = r
    let reworks = 0
    while (qa && qa.verdict === 'fail' && qa.retryable && reworks < maxRework && !halt) {
      reworks++
      const again = await agent(producePrompt(item, qa), {
        agentType: item.owner, schema: PRODUCE, phase: '재작업', label: `재작업:${item.id}`,
      })
      if (!again) break
      prod = again
      noteHalt(item, again)
      if (!['generated', 'dry-run'].includes(again.status)) break
      qa = await agent(qaPrompt(item, again, reworks + 1), {
        agentType: 'asset-qa', schema: QA, phase: '재작업', label: `재검증:${item.id}`,
      })
    }
    return {
      id: item.id, owner: item.owner, category: item.category, priority: item.priority,
      final: finalStatus(prod, qa), reworks, prod, qa,
    }
  },
)

const done = results.filter(Boolean)
const dropped = items.length - done.length
if (dropped) log(`결과를 받지 못한 에셋 ${dropped}건이 있습니다. 보고서에 누락으로 적습니다.`)
const byFinal = {}
for (const r of done) byFinal[r.final] = (byFinal[r.final] || 0) + 1
const missing = items.filter(it => !done.some(d => d.id === it.id)).map(it => it.id)
log(`완료: ${Object.entries(byFinal).map(([k, v]) => `${k} ${v}건`).join(', ') || '없음'}`)

return {
  results: done,
  summary: { total: items.length, byFinal, dropped, missing },
  halted: halt,
}
