# Cinematic atelier

## Direction

The approved November 17, 2026 mockup combines smoked glass, dark metal,
olive ceramic, clay, and fine luminous filaments. The implementation brings
those materials to the homepage, project cards, News, archive, and essay.
Body text stays on quiet editorial surfaces. The independently published SIM
application and external game keep their own interfaces.

## What is actually animated

The machine is an optimized still artwork, not a fully rigged 3D model.
A transparent Canvas draws gently drifting braided paths and moving light
signals over it. Small pointer-responsive depth and a slow light wash add
atmosphere. All typography, links, buttons, and controls remain real HTML.
There is no video download, WebGL dependency, tracking, or new remote service.

The drawing loop stops when paused, offscreen, or in a hidden document, and
when reduced motion or Save-Data is enabled. The desktop rasterization limit
is 1.5 device pixels per CSS pixel (1.25 on smaller layouts), with a 30 fps
visual update budget. These are safeguards, not measured battery-life claims.
The existing shared motion preference controls both the hero and footer.
Without JavaScript or Canvas, the still artwork and every link remain usable.

## Artwork provenance

`assets/atelier-machine.avif` is a 796 by 618 crop of the image generated in
this conversation and approved by the site owner. The crop excludes the
mockup's baked-in navigation, headline, buttons, and Projects section.
It is decorative artwork, not a screenshot of any product. The 24,504-byte
file is reused for the hero, project material studies, and News mastheads.
The existing `hero-forge.webp` illustrates the essay and notebook card.
The actual singedTerra screenshot is retained.

## Scope and preservation

Project data, destinations, editorial data, editions, historical records,
coverage history, feeds, and publication workflows are unchanged. Existing
SIM bytes are not edited. A shared CSS layer applies to both current and
historical pages that already include `theme-head.html`.

## Local verification

- Four new Python tests pass, including a dependency-free Node lifecycle test.
- JavaScript syntax validation passes.
- Home, News, archive, and essay have no horizontal overflow at 320, 390, 768,
  1024, and 1440 CSS pixels. Images loaded and no page JavaScript exceptions
  occurred in these 20 cases.
- Browser checks confirmed changing Canvas frames, pause/freeze, resume,
  synchronized controls, offscreen suspension, and resumption on re-entry.
- Browser emulation confirmed dynamic system reduced-motion behavior and
  disabled motion controls. Dark appearance was checked.
- With JavaScript disabled, the homepage retains its artwork and all three
  project cards; News retains all four topic sections.
- Node lifecycle checks cover hidden-document and Save-Data suspension,
  pagehide/pageshow, duplicate-loop prevention, and absent Canvas/hero fallback.

Browser checks used actual existing Pages output plus the edited templates,
with local resources inlined into the document because browser navigation in
this environment is restricted. This validates layout and behavior, not live
network delivery. Cross-navigation storage persistence and physical mobile
GPU/battery performance were not measured. Existing preference-storage logic
is unchanged. The pull request's normal Pages workflow is the authoritative
full Jekyll/build-contract validation; do not merge unless those checks pass.

Screenshots of the rendered desktop, mobile, dark, and reading layouts are
provided in the conversation. There is no merge or deployment in this change.
