# Static-site publication boundary

This baseline describes the implemented publication design, not an ADR or a claim
of prior human security signoff. No authenticated backend, dataset service or
maturity certification is asserted. SIM keeps its upstream application controls.

- PUB-001: Read only fixed public SUaDtL/SIM GitHub metadata and its Pages preview.
  Require successful main Pages and exact-source main push CI. Validate bounded
  HTML, clean compiled identity and standalone offline CSP before staging bytes.
- PUB-002: Build/PR jobs have repository read permissions. Bounded consumers of
  the ephemeral GitHub token are the fixed metadata query through GH_TOKEN,
  the pinned Jekyll action's GitHub-metadata token input, and standard platform
  checkout/upload inputs. Checkout must not persist Git credentials. Never log
  the token, put it in URLs or send it to the public SIM website. No PAT or
  cross-repository writer is required. Pages/OIDC permissions stay in deploy.
- PUB-003: Only main deploys. The isolated deploy job has pages:write and
  id-token:write and checks out/runs no repository or upstream code. PRs only build
  previews. Failure before deployment leaves the last good site live.
- PUB-004: Copy upstream HTML unchanged after Jekyll, without executing it on the
  runner, rendering it as Liquid or adding an iframe/backend. Preserve SIM's
  connect-src 'none'. Website publication and dataset-file trust are separate.
- PUB-005: Retain platform TLS certificate verification. Python standard-library
  hashlib SHA-256 is approved for byte checksums; it is not a publisher signature.
  No keys or custom crypto are needed. MD5, SHA-1, obsolete ciphers, home-rolled
  primitives and disabled certificate verification are prohibited.
- PUB-006: Preserve news, archives, RSS, assets and CNAME in the complete artifact.
  Check rendered news before upload and receive exact live SIM bytes and news
  after deployment. Keep local tests, CI, merge, publication and receiving distinct.
