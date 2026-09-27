// src/main.js
import Phaser from 'phaser';
import { initDebug } from './debug.js';
import { loadBalance, loadStrings, t } from './data.js';
import { loadManifest } from './assets.js';

const g = initDebug();                                       // URL 파라미터·window.__game
const schema = await (await fetch('../data/balance/_schema.json')).json();
g.data = { enemies: await loadBalance('enemies', schema) }; // 표마다
await loadStrings(g.lang); await loadManifest();

class Title extends Phaser.Scene {
  constructor() { super('scr_title'); }
  create() {
    g.setScene('scr_title');
    const btn = g.dom.button('btn_start', t('ui.title.start'), () => this.scene.start('scr_game'));
    this.events.once('shutdown', () => btn.remove());
  }
}
new Phaser.Game({ type: Phaser.AUTO, parent: 'game', width: 1280, height: 720, scene: [Title /*, Game … */],
                  seed: [String(g.seed)] });
g.ready = true;
