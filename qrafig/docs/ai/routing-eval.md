# Routing evaluation set

96 realistic QRAFIG prompts with the routing each one should produce. Use it to check `qrafig-router`
after any change to the router or to a skill's `description`.

**How to run it.** For a sample of rows, give the prompt to a fresh session and compare the skills it
loads and the files it opens against the expectations here. A row **fails** if a listed skill is
missing, a listed gate is skipped, or a skill from the *negative* section is loaded. Extra reading is
not a failure; extra *skills* usually is — the goal is the minimally sufficient context.

Abbreviations: skills are named without the `qrafig-` prefix. **LIVE** = a live `QRAFIG.exe` smoke is
mandatory. **CONC** = a concurrency test with independent clients. **MIG** = migration gates
(`has-pending-model-changes`, fresh **and** populated database). **TEN** = a cross-tenant negative test.

Every row also implies: `router` → `repo-state` first, and `verification` before reporting. They are
omitted below for brevity.

---

## A. Open-ended and continuation

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 1 | "Продолжи разработку QRAFIG с текущего состояния" | repo-state, then whatever the handoff's next task routes to | status ledger § Session handoff; § Completion criteria | as routed |
| 2 | "Разберись сам, что здесь сломано, и исправь" | diagnostics + the suspected layer's skill | handoff; the failing command; logs | reproduction first, then as routed |
| 3 | "Что вообще уже сделано в проекте?" | repo-state | § Phase status; § Completion criteria; § Session handoff | none — it is a question |
| 4 | "Какой модуль делать следующим?" | repo-state | handoff *Next concrete task*; *Planned next Desktop slice* | none |
| 5 | "Проверь весь модуль перед production" | verification + the module's skill + tenancy + appsec + performance | the module's ADRs and tests | all four suites, MIG if persistence, LIVE if Desktop, TEN |
| 6 | "Сделай ревью моих последних изменений" | architecture + the touched lanes' skills | the diff; the nearest neighbour code | build + the affected suites |
| 7 | "Обнови документацию по факту" | repo-state | the ledger sections your evidence covers | the evidence must exist first |
| 8 | "Заверши Phase 19" | repo-state (it is deliberately partial), outbox-jobs, observability, appsec | Phase 19 section; handoff's warning not to start a backend phase | ask before starting — the handoff says not to |

## B. Backend API and contracts

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 9 | "Добавь endpoint для списка смен" | api-endpoints, tenancy, authorization, pos-domain | `PosSalesEndpoints.cs`; `ShiftService`; ADR-0017, 0021, 0022 | integration incl. 403/404/TEN; `OpenApiTests` |
| 10 | "Добавь новый error code" | api-endpoints, architecture | `ErrorCodes.cs`; ADR-0009; the client mirror | `MirroredContractTests` |
| 11 | "Верни больше полей в ответе товара" | api-endpoints, inventory (cost confidentiality), tenancy | `CatalogEndpoints.cs`; ADR-0033, 0073, 0143, 0169 | integration + a cost-withholding assertion |
| 12 | "Почини валидацию на форме поставщика" | api-endpoints, purchasing | `ApiContractValidators.cs`; ADR-0168 | integration validation cases |
| 13 | "Сделай пагинацию по продажам" | api-endpoints, postgres, reporting | `Paging.cs`; ADR-0016, 0055, 0075, 0200 | integration; index present in the same migration |
| 14 | "Добавь Idempotency-Key на новый command endpoint" | api-endpoints, concurrency | `IdempotencyFilter.cs`; ADR-0011, 0141 | `IdempotencyTests`; a replay case |
| 15 | "Поменяй порядок middleware" | api-endpoints | ADR-0020 | `RateLimitAndHeaderTests`, `IdempotencyTests` |
| 16 | "Добавь rate limit на новый маршрут" | api-endpoints, appsec | `RateLimitingSetup.cs`; ADR-0020 | `RateLimitAndHeaderTests` |
| 17 | "Сделай OpenAPI чище" | api-endpoints | `EndpointConventions.cs`, `OpenApiSetup.cs` | `OpenApiTests` |
| 18 | "Добавь health check для нового зависимого сервиса" | observability, api-endpoints | `HealthSetup.cs`, `ConnectivityHealthChecks.cs` | `HealthTests` |

## C. Persistence

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 19 | "Сделай новую migration" | efcore-migrations, postgres | `## Migration history`; the module's `*Configurations.cs` | MIG, incl. populated-database proof |
| 20 | "Добавь индекс, поиск тормозит" | postgres, performance, efcore-migrations | the query; the existing indexes | plan before/after; MIG |
| 21 | "Добавь уникальность на код клиента" | efcore-migrations, concurrency, postgres | ADR-0171; `ux_*` examples | MIG + CONC (two simultaneous inserts) |
| 22 | "Почини pending model changes" | efcore-migrations | the model vs the snapshot | `has-pending-model-changes` — **never** hand-edit the snapshot |
| 23 | "Мигрируй существующие данные под новое правило" | efcore-migrations | the refuse-rather-than-repair precedents in `## Migration history` | MIG on a populated database with the ambiguous rows seeded |
| 24 | "Оптимизируй PostgreSQL запрос" | performance, postgres | the generated SQL | `EXPLAIN (ANALYZE, BUFFERS)` before/after |
| 25 | "Почини deadlock" | concurrency, postgres | `FinanceLocks.cs`; ADR-0037, 0196 | CONC: opposite operations queue instead of erroring |
| 26 | "Добавь таблицу для нового справочника" | efcore-migrations, architecture, tenancy | the nearest configuration; delete-behaviour precedents | MIG + TEN |
| 27 | "Перенеси схему локальной базы на новую версию" | sqlite-local | `LocalDatabase.cs`, `LocalMigrations` | fresh, upgrade, and **newer-schema-refused** cases |

## D. Concurrency and correctness

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 28 | "Найди race conditions" | concurrency, postgres + the module's skill | the module's service; the existing `*ConcurrencyTests` | a reproduction that fails before the fix |
| 29 | "Два менеджера сохраняют одну карточку, второй затирает первого" | concurrency, authorization | ADR-0008, 0164, 0170, 0197, 0205 | CONC → `409 CONCURRENCY_CONFLICT` |
| 30 | "Иногда приходит 500 при создании роли" | concurrency, authorization, diagnostics | the unique index; `IsUniqueViolation` | CONC reproducing the 500 |
| 31 | "Два кассира закрывают смену одновременно" | concurrency, pos-domain, postgres | ADR-0128 | CONC: exactly one close |
| 32 | "План на 10 сотрудников держит 11" | concurrency, authorization, money | ADR-0206, 0085 | CONC: simultaneous hires |
| 33 | "Одна операция применилась дважды" | offline-sync, concurrency | ADR-0047, 0129 | duplicate push settles as `duplicate`, not 500 |

## E. Money and finance

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 34 | "Переделай finance reconciliation" | money-finance, concurrency, reporting | ADR-0065, 0194, 0199, 0200; `FinanceLedger` | CONC + invariant tests + LIVE if the workspace changed |
| 35 | "Покажи общий итог по всем счетам" | money-finance, reporting | ADR-0193 | **refuse**: currencies are not summed. Say so, return per-currency |
| 36 | "Добавь расход с приложенным чеком" | money-finance, storage, appsec | ADR-0067, 0097–0099 | integration + storage tests + TEN |
| 37 | "Сделай перевод между счетами в разных валютах" | money-finance, concurrency | ADR-0068, 0196 | CONC: opposite transfers queue |
| 38 | "Посчитай чистую прибыль" | money-finance, reporting | ADR-0069, 0193 | net profit is **not** computed — say so before building |
| 39 | "Баланс счёта разошёлся с проводками" | diagnostics, money-finance | `LEDGER_OUT_OF_BALANCE`; ADR-0065 | reproduce; it is a defect, not a counting error |
| 40 | "Добавь курс валют" | money-finance, architecture | ADR-0068, 0193 | a rate table is a product decision — raise it, do not invent one |

## F. POS, offline and sync

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 41 | "Добавь возвраты" | pos-domain, money-finance, authorization, offline-sync, inventory, desktop-workspace, desktop-wpf | ADR-0057–0061, 0120, 0123 | all four suites + LIVE + CONC on approval |
| 42 | "Добавь кнопку refund на кассе" | as row 41 | plus `PosReturnView.xaml`, `PosReturnViewModel` | LIVE mandatory |
| 43 | "Почини offline sync" | offline-sync, sqlite-local, pos-domain, concurrency, diagnostics | ADR-0047, 0048, 0054, 0113, 0118, 0129 | disconnect, retry, duplicate, crash, reconnect, reconcile |
| 44 | "Касса не видит изменение цены" | offline-sync, diagnostics | ADR-0048, 0119, 0122 | change-feed test: a late commit is still returned |
| 45 | "Сделай оффлайн-режим для склада" | offline-sync, inventory, sqlite-local | **ADR-0142** — Warehouse is read-only offline by decision | do not add a queue; explain and stop |
| 46 | "Отложенный чек пропадает" | pos-domain, offline-sync, concurrency | ADR-0052, 0134, 0186 | CONC: two tills claim one cart |
| 47 | "Сделай X и Z отчёты по-новому" | pos-domain, reporting, money-finance | ADR-0135, 0136, 0137 | `PosShiftReportTests` + LIVE |
| 48 | "Уволенный кассир не может провести старую продажу" | authorization, offline-sync, pos-domain | ADR-0056, 0126 | **that is the designed behaviour** — the sale must still land |
| 49 | "Смена не закрывается, если сеть упала" | pos-domain, offline-sync, diagnostics | ADR-0127, 0137 | no Z until QRAFIG has the close |
| 50 | "Добавь новый тип оплаты" | pos-domain, money-finance, desktop-workspace | ADR-0060, 0187, 0189 | integration + Desktop + LIVE |
| 51 | "Продажа синхронизировалась с другой суммой" | offline-sync, diagnostics, pos-domain | ADR-0118 | both figures recorded; nothing overwritten |
| 52 | "Касса потеряла очередь после замены устройства" | offline-sync, sqlite-local | ADR-0113 | stranded work is surfaced, never deleted |

## G. Inventory and purchasing

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 53 | "Сделай нормальный inventory transfer" | inventory, concurrency, authorization, desktop-workspace | ADR-0035, 0038, 0143–0149 | integration + CONC + LIVE |
| 54 | "Остаток ушёл в минус" | inventory, diagnostics, concurrency | ADR-0006, 0037 | sum the movements; CONC on the path |
| 55 | "Добавь инвентаризацию по категории" | inventory | ADR-0151, 0150 | integration + LIVE |
| 56 | "Себестоимость видна кассиру" | inventory, authorization, tenancy | ADR-0033, 0073, 0143 | assertion on every route carrying cost |
| 57 | "Приёмка товара с браком" | purchasing, inventory | ADR-0039, 0041 | damaged quantity never reaches sellable stock |
| 58 | "Landed cost пересчитывается после приёмки" | purchasing, diagnostics | ADR-0161, 0166 | it must be refused after a receipt |
| 59 | "Долг поставщику неверный" | purchasing, money-finance, diagnostics | ADR-0040 | it is derived — recompute from documents |
| 60 | "Добавь возврат поставщику" | purchasing, inventory, money-finance | ADR-0163, 0167 | integration + CONC + LIVE |

## H. Customers, privacy, security, tenancy

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 61 | "Проведи security audit авторизации" | authorization, appsec, tenancy, testing | ADR-0021, 0022, 0024, 0126; `OrganizationContext` | positive, negative, cross-tenant **and stale-authority** cases |
| 62 | "Может ли одна организация увидеть данные другой?" | tenancy | `OrganizationContextResolver`; ADR-0021 | TEN on every route in scope |
| 63 | "Удали клиента по требованию" | customers-privacy, appsec | ADR-0063, 0183 | anonymization, not deletion; refused while money is owed |
| 64 | "Сделай выгрузку данных клиента" | customers-privacy, appsec, storage, tenancy | ADR-0192; `CustomerExportTests` | bounded by refusal; no credentials; no neighbour's rows |
| 65 | "Добавь бонусные баллы" | customers-privacy, money-finance, pos-domain | ADR-0060, 0179–0181 | integration + Desktop + LIVE |
| 66 | "Проверь, не течёт ли PII в логи" | appsec, observability, customers-privacy | the redaction rules | grep the log call sites; outbox fault path |
| 67 | "Добавь API key для интеграции" | appsec, api-endpoints, tenancy | ADR-0088 | hashed, prefix-identified, shown once |
| 68 | "Проверь webhook подпись" | appsec, outbox-jobs | ADR-0084, 0089 | signature verified; replay is a no-op |
| 69 | "Обнови уязвимую зависимость" | appsec | `Directory.Packages.props`; the `SSH.NET` precedent | `dotnet list package --vulnerable --include-transitive` |
| 70 | "Сделай сотрудника неактивным, он всё ещё работает на кассе" | authorization, pos-domain, offline-sync | ADR-0126 | current authority re-read; historical attribution untouched |

## I. Desktop and WPF

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 71 | "Исправь эту WPF страницу" | desktop-wpf, desktop-live-smoke | the view; `EmployeesView.xaml` as the corrected reference | `xaml_audit.py` + Desktop tests + **LIVE** |
| 72 | "Исправь XAML clipping" | desktop-wpf, desktop-live-smoke | the `Grid` column definitions | LIVE at 150% and 1280×720. **No migration, no database skill** |
| 73 | "Кнопка не нажимается" | desktop-wpf | ADR-0190; the view model's command wiring | LIVE — no test can see this |
| 74 | "Все секции показываются сразу" | desktop-wpf | the `DataContext` overrides; ADR-0191 | `xaml_audit.py` + LIVE |
| 75 | "Вкладка не подсвечивается" | desktop-wpf | `Trigger Property="Tag"`; `EmployeesView.xaml`'s `DataTrigger` | `xaml_audit.py` + LIVE |
| 76 | "Добавь новый workspace" | desktop-workspace, desktop-wpf, desktop-live-smoke + the domain skill | `NavigationModel.cs`; `ClientContext`; the nearest workspace | Desktop + E2E + **LIVE** |
| 77 | "Экран пустой при обрыве связи" | desktop-workspace, offline-sync, diagnostics | ADR-0204; the shell's lock host | LIVE: drop the connection **inside** the workspace |
| 78 | "Список тормозит на 20 000 строк" | performance, desktop-wpf | virtualization; the item template | LIVE at realistic row counts, measured |
| 79 | "Исправь проблему, которая появляется только при запуске QRAFIG.exe" | diagnostics, desktop-wpf, desktop-live-smoke | the client log; the three defect classes | reproduce in the live run first |
| 80 | "Сделай тёмную тему для нового контрола" | desktop-wpf | `Tokens.Light.xaml` **and** `Tokens.Dark.xaml`; `Controls.xaml` | both palettes; LIVE in both themes |
| 81 | "Клавиатурная работа на кассе сломана" | desktop-wpf, pos-domain | focus and tab order | LIVE, mouse unplugged |
| 82 | "Добавь колонку в таблицу товаров" | desktop-wpf, desktop-workspace | the `DataGrid` widths | LIVE at the narrow layout |
| 83 | "Приложение долго стартует" | performance, desktop-workspace, diagnostics | `ShellViewModel.StartAsync`; ADR-0110 | measured, before and after |

## J. Reporting, jobs, storage, observability

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 84 | "Сделай Reports" | reporting, money-finance, authorization, tenancy, desktop-workspace, desktop-wpf, performance | the handoff (Reports is the next slice, feature-gated, outside the trial); ADR-0069–0076 | all four suites + **LIVE**, starting with the locked-module state |
| 85 | "Добавь график выручки на дашборд" | reporting, desktop-wpf | ADR-0076 — the dashboard composes the reports | LIVE |
| 86 | "Отчёт показывает противоречивые цифры" | reporting, postgres, diagnostics | ADR-0136 | one `REPEATABLE READ` snapshot; a concurrent-commit test |
| 87 | "Отчёт падает на большом периоде" | reporting, performance, api-endpoints | ADR-0074 | bounded refusal, measured |
| 88 | "Добавь новую фоновую задачу" | outbox-jobs, observability, tenancy | ADR-0094, 0095, 0096 | advisory lock; `job_runs`; same service as the endpoint |
| 89 | "Событие не дошло до интеграции" | outbox-jobs, diagnostics, observability | the Control outbox routes | attempts, lease, classification |
| 90 | "Добавь загрузку фото товара" | storage, appsec, tenancy, desktop-workspace | ADR-0097–0099 | reserve → upload → finalize; expiring link; TEN |
| 91 | "Добавь метрику" | observability | the `Qrafig.Outbox` meter as the model | low cardinality; no ids in dimensions |
| 92 | "Настрой OpenTelemetry на прод" | observability, appsec | `ObservabilitySetup.cs` | the exporter must not fail closed |

## K. Site (isolated)

| # | Prompt | Skills | Read first | Gates |
| --- | --- | --- | --- | --- |
| 93 | "Добавь новую страницу на сайте" | **site only** | `src/app/[locale]/`; `src/lib/site.ts`; the dictionaries | `tsc --noEmit`, `eslint`, `check-content.mjs`, `next build` |
| 94 | "Исправь metadata на сайте" | **site only** | the page's `generateMetadata`; `NEXT_PUBLIC_SITE_URL` | typecheck, lint, build |
| 95 | "Обнови цены на сайте" | site only | `src/content/pricing.ts`; the platform's `PlanService`; SITE-SYNC FACTS | `check-content.mjs` (yearly = ten monthly) |
| 96 | "Отметь модуль как готовый на сайте" | site + repo-state (to read the platform ledger) | `## Completion criteria`; `SITE-SYNC FACTS` | never ahead of the ledger |

---

## Negative routing — these must **not** load

| Prompt | Must not load |
| --- | --- |
| "Исправь metadata на сайте" | pos-domain, money-finance, sqlite-local, efcore-migrations, postgres, desktop-* |
| "Почини PostgreSQL deadlock" | site, desktop-wpf, desktop-live-smoke, reporting |
| "Исправь XAML clipping" | efcore-migrations, postgres, money-finance, outbox-jobs — and **no migration is generated** |
| "Поменяй favicon" | everything except the file itself (site or `Assets/`) |
| "Добавь индекс в PostgreSQL" | site, desktop-*, pos-domain, customers-privacy |
| "Обнови текст на странице тарифов" | any platform skill |
| "Переименуй переменную в SaleService" | desktop-*, site, storage, observability |
| "Добавь unit-тест на MoneyArithmetic" | desktop-*, site, postgres, outbox-jobs (unit suite, no Docker) |
| "Обнови README" | every domain skill — read, do not route |
| Any site prompt | **every** platform skill except `repo-state`, and that only to read the ledger for a factual claim |

## Behaviours the set also checks

| Expectation | Rows |
| --- | --- |
| Refuses to invent a product rule and says so | 38, 40 |
| Refuses a request that contradicts an ADR, with the reason | 35, 45, 48 |
| Does not reopen a closed claim | 1, 5, 8 |
| Does not start a phase the handoff says not to start | 8 |
| Reproduces before fixing | 2, 28, 30, 39, 54, 79, 86 |
| Requires the live smoke where it is owed | 41, 42, 47, 50, 53, 71–84 |
| Requires independent-client concurrency proof | 21, 28–33, 37, 46, 53, 60 |
| Requires a populated-database migration proof | 19, 23, 26 |
| Requires a cross-tenant negative test | 9, 26, 36, 62, 64, 90 |
| Keeps the site isolated | 93–96 and the whole negative table |
