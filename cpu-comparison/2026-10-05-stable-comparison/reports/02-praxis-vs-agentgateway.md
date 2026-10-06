# Praxis versus agentgateway v1.6.0

Core v0.5.2, core nightly-20261002, AI v0.5.0 and the October 2 AI nightly are separate treatments. Common forwarding uses matching transport responsibilities. Native AI exercises configured functionality with different routing/accounting implementations; do not interpret native ratios as equal-work efficiency.

Every fixed-rate, capacity and streaming case appears in the full matrices: [common HTTP](matrices/common-http.md), [common AI transport](matrices/common-ai.md), [native AI](matrices/native-ai.md), [Kubernetes HTTP](matrices/kubernetes-http.md).

## Unlimited-rate Fortio cases

The ratio is agentgateway mean successful RPS divided by Praxis mean successful RPS. Greater than 1 favors agentgateway for this case; less than 1 favors Praxis. It is not an overall score. No best-run selection is used.

| Profile | Case | Praxis image | Agentgateway successful RPS | Praxis successful RPS | Agentgateway / Praxis |
| --- | --- | --- | ---: | ---: | ---: |
| Standalone common forwarding | openai / 1024 B content, 32 connections, unlimited | Praxis core nightly-20261002 | 22,646 [22,423–22,998] | 20,780 [20,487–21,182] | 1.090× |
| Standalone common forwarding | openai / 16384 B content, 32 connections, unlimited | Praxis core nightly-20261002 | 10,207 [9,910–10,508] | 9,430 [9,409–9,462] | 1.082× |
| Standalone common forwarding | anthropic / 1024 B content, 32 connections, unlimited | Praxis core nightly-20261002 | 22,506 [21,949–23,208] | 21,948 [21,603–22,284] | 1.025× |
| Standalone common forwarding | anthropic / 16384 B content, 32 connections, unlimited | Praxis core nightly-20261002 | 10,414 [10,170–10,698] | 9,641 [9,565–9,715] | 1.080× |
| Standalone common forwarding | openai / 1024 B content, 512 connections, unlimited | Praxis core nightly-20261002 | 19,291 [18,758–19,701] | 17,339 [16,674–17,684] | 1.113× |
| Standalone common forwarding | openai / 16384 B content, 512 connections, unlimited | Praxis core nightly-20261002 | 11,654 [11,488–11,934] | 10,433 [10,174–10,582] | 1.117× |
| Standalone common forwarding | 0 B content, 1 connections, unlimited | Praxis core nightly-20261002 | 2,782 [2,596–2,910] | 2,963 [2,774–3,145] | 0.939× |
| Standalone common forwarding | 0 B content, 16 connections, unlimited | Praxis core nightly-20261002 | 23,817 [22,720–25,351] | 27,490 [27,252–27,663] | 0.866× |
| Standalone common forwarding | 0 B content, 512 connections, unlimited | Praxis core nightly-20261002 | 21,798 [21,205–22,135] | 22,832 [22,356–23,113] | 0.955× |
| Standalone common forwarding | 16384 B content, 1 connections, unlimited | Praxis core nightly-20261002 | 1,926 [1,832–2,053] | 1,988 [1,915–2,047] | 0.969× |
| Standalone common forwarding | 16384 B content, 16 connections, unlimited | Praxis core nightly-20261002 | 17,014 [16,437–18,126] | 16,604 [16,529–16,684] | 1.025× |
| Standalone common forwarding | 16384 B content, 512 connections, unlimited | Praxis core nightly-20261002 | 15,640 [15,263–15,837] | 15,379 [14,957–15,806] | 1.017× |
| Standalone common forwarding | openai / 1024 B content, 32 connections, unlimited | Praxis core v0.5.2 | 22,646 [22,423–22,998] | 27,450 [27,151–27,667] | 0.825× |
| Standalone common forwarding | openai / 16384 B content, 32 connections, unlimited | Praxis core v0.5.2 | 10,207 [9,910–10,508] | 9,411 [9,336–9,457] | 1.085× |
| Standalone common forwarding | anthropic / 1024 B content, 32 connections, unlimited | Praxis core v0.5.2 | 22,506 [21,949–23,208] | 28,881 [28,311–29,823] | 0.779× |
| Standalone common forwarding | anthropic / 16384 B content, 32 connections, unlimited | Praxis core v0.5.2 | 10,414 [10,170–10,698] | 9,577 [9,442–9,683] | 1.087× |
| Standalone common forwarding | openai / 1024 B content, 512 connections, unlimited | Praxis core v0.5.2 | 19,291 [18,758–19,701] | 22,263 [21,916–22,503] | 0.866× |
| Standalone common forwarding | openai / 16384 B content, 512 connections, unlimited | Praxis core v0.5.2 | 11,654 [11,488–11,934] | 8,857 [8,720–8,931] | 1.316× |
| Standalone common forwarding | 0 B content, 1 connections, unlimited | Praxis core v0.5.2 | 2,782 [2,596–2,910] | 3,334 [3,122–3,484] | 0.834× |
| Standalone common forwarding | 0 B content, 16 connections, unlimited | Praxis core v0.5.2 | 23,817 [22,720–25,351] | 37,779 [36,728–39,142] | 0.630× |
| Standalone common forwarding | 0 B content, 512 connections, unlimited | Praxis core v0.5.2 | 21,798 [21,205–22,135] | 33,682 [32,123–34,563] | 0.647× |
| Standalone common forwarding | 16384 B content, 1 connections, unlimited | Praxis core v0.5.2 | 1,926 [1,832–2,053] | 2,090 [2,051–2,122] | 0.922× |
| Standalone common forwarding | 16384 B content, 16 connections, unlimited | Praxis core v0.5.2 | 17,014 [16,437–18,126] | 21,336 [19,856–22,132] | 0.797× |
| Standalone common forwarding | 16384 B content, 512 connections, unlimited | Praxis core v0.5.2 | 15,640 [15,263–15,837] | 20,637 [20,271–20,973] | 0.758× |
| Standalone native AI | openai / 1024 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 14,041 [13,871–14,211] | 13,398 [13,074–13,967] | 1.048× |
| Standalone native AI | openai / 16384 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 7,399 [7,321–7,488] | 2,838 [2,811–2,859] | 2.608× |
| Standalone native AI | anthropic / 1024 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 14,158 [13,781–14,467] | 12,075 [11,979–12,220] | 1.173× |
| Standalone native AI | anthropic / 16384 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 7,347 [7,214–7,438] | 2,700 [2,640–2,755] | 2.721× |
| Standalone native AI | translation / 1024 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 12,822 [12,503–13,295] | 7,118 [7,063–7,218] | 1.801× |
| Standalone native AI | translation / 16384 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 7,172 [7,116–7,226] | 1,507 [1,497–1,519] | 4.758× |
| Standalone native AI | openai / 1024 B content, 512 connections, unlimited | Praxis AI v0.5.0 | 12,205 [12,014–12,361] | 11,106 [11,075–11,150] | 1.099× |
| Standalone native AI | openai / 16384 B content, 512 connections, unlimited | Praxis AI v0.5.0 | 6,810 [6,718–6,872] | 2,693 [2,682–2,701] | 2.528× |
| Standalone native AI | openai / 1024 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 14,041 [13,871–14,211] | 12,985 [12,897–13,115] | 1.081× |
| Standalone native AI | openai / 16384 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 7,399 [7,321–7,488] | 2,714 [2,682–2,731] | 2.726× |
| Standalone native AI | anthropic / 1024 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 14,158 [13,781–14,467] | 12,108 [11,705–12,340] | 1.169× |
| Standalone native AI | anthropic / 16384 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 7,347 [7,214–7,438] | 2,654 [2,628–2,677] | 2.769× |
| Standalone native AI | translation / 1024 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 12,822 [12,503–13,295] | 7,025 [6,936–7,111] | 1.825× |
| Standalone native AI | translation / 16384 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 7,172 [7,116–7,226] | 1,460 [1,456–1,468] | 4.912× |
| Standalone native AI | openai / 1024 B content, 512 connections, unlimited | Praxis AI Oct 2 nightly | 12,205 [12,014–12,361] | 11,126 [10,969–11,258] | 1.097× |
| Standalone native AI | openai / 16384 B content, 512 connections, unlimited | Praxis AI Oct 2 nightly | 6,810 [6,718–6,872] | 2,626 [2,613–2,637] | 2.593× |
| Kubernetes HTTP | 0 B content, 1 connections, unlimited | Praxis core v0.5.2 | 572.873 [551.251–606.071] | 605.950 [571.020–639.645] | 0.945× |
| Kubernetes HTTP | 0 B content, 16 connections, unlimited | Praxis core v0.5.2 | 9,476 [9,177–9,654] | 9,734 [9,294–10,016] | 0.973× |
| Kubernetes HTTP | 0 B content, 512 connections, unlimited | Praxis core v0.5.2 | 24,892 [24,689–25,159] | 32,008 [31,969–32,077] | 0.778× |
| Kubernetes HTTP | 16384 B content, 1 connections, unlimited | Praxis core v0.5.2 | 534.786 [502.622–575.277] | 548.411 [535.891–572.182] | 0.975× |
| Kubernetes HTTP | 16384 B content, 16 connections, unlimited | Praxis core v0.5.2 | 8,514 [8,344–8,644] | 8,688 [8,671–8,699] | 0.980× |
| Kubernetes HTTP | 16384 B content, 512 connections, unlimited | Praxis core v0.5.2 | 16,196 [16,094–16,335] | 18,357 [18,284–18,432] | 0.882× |

## Compatibility and unavailable cells

The stock operator with the pinned core nightly rejects its generated cluster name. Kubernetes HTTP, scale and recovery for that pairing are not evaluated. Standalone nightly forwarding remains a separate, runnable treatment. The October 2 Praxis AI nightly is separately pinned from its successful scheduled build and retained SHA tag; there is no dated AI tag. The AI release is v0.5.0 and uses core libraries v0.7.2.

See [Gateway API evidence](03-gateway-api.md), [feature comparison](04-feature-comparison.md) and [methodology](05-methodology-and-validity.md). These results do not establish TLS/HTTP2 performance, policy/security equivalence, a universal routing limit or production availability.

Compare [sampled resource usage](08-resource-usage.md) beside achieved throughput. Native accounting work differs, and coarse resource samples do not establish exact CPU cycles per request.
