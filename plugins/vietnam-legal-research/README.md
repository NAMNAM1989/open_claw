# vietnam-legal-research (OpenClaw plugin)

PoC hỗ trợ tra cứu pháp lý Việt Nam cho OpenClaw.

**Trạng thái:** `APPROVED_FOR_LIMITED_POC` — mặc định `link-only`, **không** scrape Thư Viện Pháp Luật.

## Tính năng

- Tool `vietnam_legal_research`: phân loại câu hỏi, tạo URL TVPL + nguồn chính phủ
- Citation builder + disclaimer + prompt-injection filter
- Rate limiter / cache TTL (URL + metadata)
- Browser/API adapters ở trạng thái stub/blocked theo source policy

## Dev

```bash
cd plugins/vietnam-legal-research
npm install
npm run typecheck
npm test
npm run build
```

## Env

Xem root `.env.example` (`TVPL_*`, `RUN_TVPL_LIVE_TESTS`).

## Docs

`docs/integrations/thuvienphapluat/`
