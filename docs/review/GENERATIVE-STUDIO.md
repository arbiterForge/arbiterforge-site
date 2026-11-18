# Generative Studio: implementation and review

## Scope
The first step in the requested sequence is a procedural playground, before project showcases. It adds `/lab/` and enhances the existing cinematic hero. News editorial data, archives, RSS, SIM receiving and publishing workflows, and project destinations remain unchanged.

## Design and behavior
- The homepage retains its original generated imagery as atmosphere and no-JavaScript fallback. A new procedural geometry layer forms revolving ribbon structures, cores, filaments and moving satellites behind the stationary text.
- `/lab/` provides a standalone visual environment. Four modes, Foundry, Filaments, Bloom and Orbit, change the topology and motion.
- The 32-bit seed is deterministic. Mode and seed are written to the URL; speed and complexity are local controls. Regenerate, pulse, pause, still-image PNG export and link copy are provided.
- Real-time geometry is computed and projected in dependency-free Canvas2D. This is an artistic model, not a WebGL/CAD simulation. It has no network calls or remote assets beyond the site's own files.
- Existing global motion controls, system reduced-motion, Save-Data, hidden-document and offscreen checks govern animation. Canvas pixels and frame rate are bounded; a static scene is still drawn when animation is disabled.

## Pre-PR local verification
The prototype was applied to the prior real Pages output from PR #36 using the source changes proposed here. Chromium browser checks used the compiled HTML with local CSS/JS embedded because page navigation is restricted in the review environment.
- Lab widths **320, 375, 390, 768, 1024, and 1440px**: no horizontal overflow or page exceptions.
- Home widths **320, 390, and 1440px**: the header, hero, procedural Canvas and new Lab links rendered without page exceptions.
- Changing from Foundry to Bloom updates the pressed state and sculpture.
- Pause held the frame stable; resume restarted changes; regenerating updated the seed.
- Keyboard space toggled pause while Canvas was focused.
- Native reduced-motion emulation disabled the pause button and stopped animation.
- `node --check assets/generative-studio.js` passed.
- The local implementation packet includes a one-command source patch, screenshots and four regression contracts.

## Post-PR checks required
The GitHub Pages PR build must pass all source and rendered-site checks. Review the actual preview and verify `/lab/` from home, News, and essay navigation in a browser, then test on a physical mobile device for thermals, battery drain and sustained frame time before merge.

The full Project Showcase pages for codeArbiter, SIM and singedTerra are intentionally out of scope for this PR. They are the next phase.
