# sk-mastan — SDE / ML / AI Engineer · Systems / Backend

SDE + ML/AI + Systems. I build reliable backends and ML systems that ship. Go, Java, Python, TypeScript. Focus: agent orchestration, distributed systems, payment ledgers, and ML for systems.

[![Focus: Agents](https://img.shields.io/badge/focus-agents%20%26%20evals-6366f1)](https://github.com/mastaan66/foreman)
[![Focus: Systems](https://img.shields.io/badge/focus-distributed%20systems-0ea5e9)](https://github.com/mastaan66/Distributed-API-Rate-Limiter)
[![Focus: Backend](https://img.shields.io/badge/focus-payments%20%26%20ACID-10b981)](https://github.com/mastaan66/Fault-Tolerant-Payment-Ledger)

> **Hiring signal 2026:** LLMs 63%, evals 56%, agents 50% of AI-engineer JDs now outrank PyTorch 33% [Dexity 390 JDs, July 2026]. Distributed systems averages $268k, top paid tag [aidevboard 8,967 roles]. My pinned 6 map directly to that.

## Flagship — pick one and go deep

### 1. foreman — multi-model orchestration engine for AI coding agents [FLAGSHIP]

Director writes tickets, tiered workforce executes via opencode under hard budgets and gates. Zero dependencies, Node >=22.

```
director -> lead (premium: plan, review, gates)
           -> coder / tester (standard: implement)
           -> drone / librarian (economy: chores, retrieval)
```

- Tickets, not prompts. Verify gates run by engine, not by worker claims
- Budgets: steps, tokens, context, USD, minutes — SIGTERM and escalation on breach
- Live dashboard `foreman` with STREAM / ORG / TASKS / COST

```bash
npm i -g @mastaan66/foreman
foreman doctor
foreman init --name my-project
foreman ticket hello --title "Add hello test"
foreman run T001 --verify
```

**Links:** [Repo](https://github.com/mastaan66/foreman) · [npm](https://www.npmjs.com/package/@mastaan66/foreman) · [Releases](https://github.com/mastaan66/foreman/releases) · [Docs](https://mastaan66.github.io/foreman/) · `v0.4.0`

---

### 2. Distributed-API-Rate-Limiter — exact sliding window in Go + Redis + Lua

Redis-backed, one atomic Lua per decision. Redis server time avoids clock skew, no fixed-window spikes, rejected requests do not consume capacity.

```bash
docker compose up --build
for i in 1 2 3 4 5 6 7; do curl -i http://localhost:8080/ping; done
```

```go
limiter, _ := ratelimit.NewRedisLimiter(redisClient)
guard, _ := ginlimit.New(limiter, ginlimit.Options{
  Policy: ratelimit.Policy{Limit: 100, Window: time.Minute},
})
```

**Links:** [Repo](https://github.com/mastaan66/Distributed-API-Rate-Limiter) · [Go pkg](https://pkg.go.dev/github.com/mastaan66/Distributed-API-Rate-Limiter) · `Go 1.25` · `MIT`

### 3. Fault-Tolerant-Payment-Ledger — ACID ledger in Java 21 + Spring Boot

Transfers, balance changes, audit record, and idempotency commit in one transaction. Optimistic locking, lexical account ordering to reduce deadlocks, `409 Conflict` on idempotency misuse.

```bash
./mvnw spring-boot:run
curl --request POST http://localhost:8081/api/ledger/transfers \
  --header 'Content-Type: application/json' \
  --header 'Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000' \
  --data '{"from":"AC100","to":"AC200","amount":"100.00"}'
```

**Links:** [Repo](https://github.com/mastaan66/Fault-Tolerant-Payment-Ledger) · `Java 21` · `Spring Boot 4.0` · `MIT`

---

## ML / AI — systems + evaluation

### 4. data-highway — ML query runtime optimization [rebuilding]

ML + indexing to cut query execution time 40%. Query parsing, index recommendation via scikit-learn, execution plan analysis, LRU caching. Postgres/MySQL, Flask/FastAPI.

```bash
pip install -r requirements.txt
python -m src.optimizer "SELECT * FROM users WHERE age > 30"
```

> Rebuild in progress: converting `.docx` report to `docs/`, adding `pyproject.toml`, proper `src/`, eval split and statistical tests [ANOVA, Tukey HSD]. See [Repo](https://github.com/mastaan66/data-highway)

### 5. margin-notes-for-pdf — browser extension, per-page notes + stylus

PDFs dock left/right, free space is a notebook. One note per page, autosave by PDF fingerprint, Markdown, handwriting with pressure, virtualized rendering tested on 1971 pages.

```bash
npm run build   # build/chrome + build/firefox
```

**Links:** [Repo](https://github.com/mastaan66/margin-notes-for-pdf) · `MV3` · `pdf.js 6.x`

### 6. smart-attendance — geo-fenced attendance evidence service

Next.js + Prisma + Postgres + Redis. Attendance is evidence, not verdict. Idempotent writes, rotating session codes, enrollment scoped by tenant.

```bash
cp .env.example .env
docker compose up --build
npx prisma migrate deploy
npm test
```

**Links:** [Repo](https://github.com/mastaan66/smart-attendance) · `Next.js 16` · Roadmap in `docs/ROADMAP.md`

---

## How I build

```text
tickets, not prompts
verify gates, not claims
budgets and evals over vibes
one atomic Lua, one ACID transaction, one fingerprint at a time
```

- Clean code, typed, linted, tested, reviewed. Deletion over addition.
- Releases with semantic versioning and `CHANGELOG.md`. No `node_modules` in git.
- CI on every push, branch protection, CodeQL, Dependabot — reward when green, penalty when red.

## Stack

```
Languages:  Go · Java · Python · TypeScript · JavaScript
Systems:    Redis · PostgreSQL · Docker · GitHub Actions · Spring Boot
ML/AI:      scikit-learn · Pandas · NumPy · agents · RAG · evals
```

## Proof

- `foreman` — 0 dependencies, `npm i -g @mastaan66/foreman`, CI passing, 3 releases
- `Distributed-API-Rate-Limiter` — integration + race tests, Docker demo
- `Fault-Tolerant-Payment-Ledger` — concurrency tests, `application/problem+json`
- All repos: `LICENSE` MIT, `CONTRIBUTING.md`, `SECURITY.md`

## Contact

- GitHub: [@mastaan66](https://github.com/mastaan66)
- Email: `mastaanshaik37@gmail.com` [from foreman package.json]
- Portfolio: add Vercel link here
- Resume: add PDF link here

---

<details>
<summary>Archived and private repos</summary>

Tutorial and experiment repos are archived to keep signal high. DSA and notes are private. Forks are not pinned. See [all repos](https://github.com/mastaan66?tab=repositories) for full history.

</details>
