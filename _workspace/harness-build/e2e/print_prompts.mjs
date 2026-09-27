import fs from 'fs'
const src = fs.readFileSync('.claude/skills/varco-game-studio/scripts/asset_production.workflow.js','utf8').replace(/export const meta = \{[\s\S]*?\n\}/,'')
const body = src.slice(0, src.indexOf("log(`에셋 ${items.length}"))
const args = {slug:'tiny', mode:'dry-run', budget:1000, allowUnknownPrice:false, paths:{runMeta:'_workspace/harness-build/e2e/_ws/run_meta.json', manifest:'_workspace/harness-build/e2e/games/tiny/manifest.json', ledger:'_workspace/harness-build/e2e/_ws/varco_ledger.jsonl', gameDir:'_workspace/harness-build/e2e/games/tiny', workspace:'_workspace/harness-build/e2e/_ws'}, items:[{id:'sfx_coin_pickup',owner:'sound-designer',category:'sfx',priority:'P0'}]}
const f = new Function('args','log', `${body}; return {p: producePrompt(items[0], null), q: qaPrompt(items[0], {status:'__STATUS__', outputs:['__OUTPUTS__'], notes:'__NOTES__'}, 1)}`)
const r = f(args, ()=>{})
fs.writeFileSync('_workspace/harness-build/e2e/produce_prompt.txt', r.p); fs.writeFileSync('_workspace/harness-build/e2e/qa_prompt.txt', r.q)
