# JOEFLOW v1.1.0 personal installation verification

Date: 2026-10-13 (Asia/Seoul)

## Installed identity

- Source commit: `e3be5d11fe0e8f5b79c42e35a0bcb157f5bdda4a`
- Source tree: `29f7b4207ccec790581630a763c59441cad86be1`
- Program version: `1.1.0`
- Runtime skill ID: `joewrks-product-definition`
- Personal install: `C:/Users/tjdwo/.codex/skills/joewrks-product-definition`
- Backup: `C:/Users/tjdwo/.codex/skills-backups/joewrks-product-definition-before-v1.1.0-t040-20261013T221648-KST`

The installed skill directory intentionally has no root `VERSION` file. Its version is confirmed by the exact source commit and root `VERSION`, the tracked source blob manifest, the declared preserved overlays, and the installation receipt.

## Backup and delta

- Installed before: 201 files
- Backup: 201 files, exact path/hash parity with the old installation
- Installed after: 201 files
- Changed: `agents/openai.yaml`
- Created: 0
- Deleted: 0
- Old manifest SHA-256: `2f1656a793c79e22c610ebe23ef80d4f4b17dce3ca614f17aeeb4d087473ab5c`
- New manifest SHA-256: `d40e5c9a01cee3d7a74b633d3ec9830ee0cd0fe2e3a4058748abb0a35f1cbf28`
- Source manifest SHA-256: `b663ac3c95b17e4206a36134b0ff5b7dbd48d59aa428284ae8962ae3a38dbe6c`

Two pre-existing personal Figma handoff documents were preserved byte-for-byte as approved local overlays:

- `references/figma-make-handoff.md`
- `templates/figma-make-handoff.md`

The 29 pre-existing `__pycache__` files were also preserved. The complete old, source and new manifests are in [personal-install-receipt.json](personal-install-receipt.json), SHA-256 `883fd2f5f6235395cfad02e2f415cb602da5102a48f98808866f7a9302d37138` before this Markdown record was committed.

## Verification

- Native State 0.2.0 validator: PASS
- Legacy State 0.1.2.1 validator: PASS
- Frozen `authority_binding_v2.py` blob: `03704ea991aa72d20c2dd8c251ea22cbda8640ce`
- Other personal JOE skills changed by this owner: 0
- Global settings changed: 0
- Git tag created in this step: NO
- GitHub Release created in this step: NO

The cross-product installation check, tag and GitHub Release publication remain centrally owned after all three product installations are verified.
