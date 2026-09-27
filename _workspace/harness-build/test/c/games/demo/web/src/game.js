import { loadCsv } from './data.js';
const enemies = await loadCsv('../data/balance/enemies.csv');
export function spawn(id) { const e = enemies[id]; return { hp: e.hp, atk: e.attack, speed: e.move_speed_px_s }; }
export function bossHp() { return 1200; }            // 하드코딩
export const T = { start: t('ui.menu.start'), gold: t('ui.hud.gold'), bad: t('ui.menu.quit') };
playLine('ch1_intro_001'); playLine('ch1_intro_009');
const cd = row['dash_cooldwn_s'];
// 'ui.menu.fake' 는 주석이라 무시
