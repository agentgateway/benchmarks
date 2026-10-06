# Sampled resources: common ai

Cells show the arithmetic mean of three per-run values followed by [minimum–maximum]. CPU is the mean over each sampled tool-execution window; memory is each window’s maximum sampled cgroup charge. These include client startup/warmup and are not exact measurement-only CPU cycles or RSS. See [resource interpretation](../08-resource-usage.md).

| Tool / case | Treatment | CPU, % of two-CPU quota | Maximum sampled memory, MiB | Maximum sampled descriptors |
| --- | --- | ---: | ---: | ---: |
| aiperf: anthropic, 16 streams | Agentgateway v1.6.0 | 4.18 [3.66–4.76] | 57.51 [47.68–63.41] | 169.00 [169.00–169.00] |
| aiperf: anthropic, 16 streams | Praxis core v0.5.2 | 4.42 [4.06–5.03] | 39.17 [31.58–43.50] | 166.67 [166.00–167.00] |
| aiperf: anthropic, 16 streams | Praxis core nightly-20261002 | 4.79 [4.50–5.22] | 25.88 [20.99–28.91] | 168.67 [158.00–174.00] |
| aiperf: anthropic, 128 streams | Agentgateway v1.6.0 | 19.87 [18.04–22.08] | 35.19 [34.82–35.52] | 279.00 [279.00–279.00] |
| aiperf: anthropic, 128 streams | Praxis core v0.5.2 | 18.04 [17.83–18.43] | 43.98 [43.68–44.34] | 278.33 [278.00–279.00] |
| aiperf: anthropic, 128 streams | Praxis core nightly-20261002 | 21.18 [19.55–23.26] | 29.56 [29.19–29.91] | 284.00 [284.00–284.00] |
| aiperf: openai, 16 streams | Agentgateway v1.6.0 | 3.97 [3.51–4.46] | 108.41 [87.94–119.60] | 666.33 [658.00–673.00] |
| aiperf: openai, 16 streams | Praxis core v0.5.2 | 4.64 [4.37–4.96] | 71.88 [37.90–107.03] | 162.67 [161.00–164.00] |
| aiperf: openai, 16 streams | Praxis core nightly-20261002 | 4.58 [4.14–4.99] | 100.92 [98.97–102.25] | 170.00 [168.00–173.00] |
| aiperf: openai, 128 streams | Agentgateway v1.6.0 | 18.37 [17.42–20.21] | 69.02 [68.74–69.40] | 776.33 [768.00–783.00] |
| aiperf: openai, 128 streams | Praxis core v0.5.2 | 20.68 [19.75–22.29] | 45.58 [44.96–45.90] | 278.33 [278.00–279.00] |
| aiperf: openai, 128 streams | Praxis core nightly-20261002 | 19.97 [18.26–21.23] | 29.91 [29.60–30.12] | 284.33 [284.00–285.00] |
| fortio: anthropic / 1024 B, 32 connections, unlimited | Agentgateway v1.6.0 | 99.13 [99.06–99.26] | 17.51 [17.25–17.68] | 86.67 [85.00–89.00] |
| fortio: anthropic / 1024 B, 32 connections, unlimited | Praxis core v0.5.2 | 97.14 [96.76–97.74] | 13.88 [13.76–14.10] | 85.00 [85.00–85.00] |
| fortio: anthropic / 1024 B, 32 connections, unlimited | Praxis core nightly-20261002 | 99.23 [99.15–99.35] | 19.38 [19.04–19.73] | 89.00 [89.00–89.00] |
| fortio: anthropic / 1024 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 6.95 [6.58–7.55] | 22.08 [21.76–22.36] | 86.67 [85.00–89.00] |
| fortio: anthropic / 1024 B, 32 connections, 1000 RPS | Praxis core v0.5.2 | 6.97 [6.53–7.36] | 14.87 [14.36–15.25] | 85.00 [85.00–85.00] |
| fortio: anthropic / 1024 B, 32 connections, 1000 RPS | Praxis core nightly-20261002 | 8.18 [7.92–8.59] | 23.35 [23.30–23.39] | 89.00 [89.00–89.00] |
| fortio: anthropic / 1024 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 17.13 [16.19–18.13] | 17.85 [17.75–18.00] | 86.67 [85.00–89.00] |
| fortio: anthropic / 1024 B, 32 connections, 3000 RPS | Praxis core v0.5.2 | 15.24 [13.75–16.30] | 12.30 [12.21–12.36] | 85.00 [85.00–85.00] |
| fortio: anthropic / 1024 B, 32 connections, 3000 RPS | Praxis core nightly-20261002 | 18.78 [18.14–19.81] | 19.06 [18.51–19.71] | 89.00 [89.00–89.00] |
| fortio: anthropic / 16384 B, 32 connections, unlimited | Agentgateway v1.6.0 | 86.17 [82.70–89.24] | 22.97 [22.74–23.25] | 86.33 [84.00–89.00] |
| fortio: anthropic / 16384 B, 32 connections, unlimited | Praxis core v0.5.2 | 97.27 [96.83–97.74] | 21.14 [20.79–21.71] | 82.67 [81.00–84.00] |
| fortio: anthropic / 16384 B, 32 connections, unlimited | Praxis core nightly-20261002 | 86.54 [83.81–89.27] | 24.56 [24.09–25.15] | 89.33 [89.00–90.00] |
| fortio: anthropic / 16384 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 12.05 [11.29–12.77] | 19.92 [19.59–20.11] | 84.00 [84.00–84.00] |
| fortio: anthropic / 16384 B, 32 connections, 1000 RPS | Praxis core v0.5.2 | 13.91 [13.09–14.79] | 11.91 [11.77–12.04] | 54.33 [54.00–55.00] |
| fortio: anthropic / 16384 B, 32 connections, 1000 RPS | Praxis core nightly-20261002 | 12.73 [12.12–13.90] | 20.06 [19.90–20.24] | 89.00 [89.00–89.00] |
| fortio: anthropic / 16384 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 31.26 [29.35–32.28] | 19.82 [19.47–20.02] | 84.00 [84.00–84.00] |
| fortio: anthropic / 16384 B, 32 connections, 3000 RPS | Praxis core v0.5.2 | 38.15 [37.28–38.91] | 13.36 [13.12–13.71] | 57.00 [56.00–58.00] |
| fortio: anthropic / 16384 B, 32 connections, 3000 RPS | Praxis core nightly-20261002 | 32.63 [31.34–33.57] | 21.45 [21.01–21.80] | 89.00 [89.00–89.00] |
| fortio: openai / 1024 B, 32 connections, unlimited | Agentgateway v1.6.0 | 99.11 [98.93–99.27] | 18.91 [16.83–22.75] | 84.00 [84.00–84.00] |
| fortio: openai / 1024 B, 32 connections, unlimited | Praxis core v0.5.2 | 98.05 [97.93–98.14] | 13.46 [13.21–13.72] | 85.00 [85.00–85.00] |
| fortio: openai / 1024 B, 32 connections, unlimited | Praxis core nightly-20261002 | 99.39 [99.35–99.45] | 19.15 [19.05–19.21] | 89.00 [89.00–89.00] |
| fortio: openai / 1024 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 7.42 [6.99–8.25] | 36.61 [35.95–37.22] | 361.33 [357.00–367.00] |
| fortio: openai / 1024 B, 32 connections, 1000 RPS | Praxis core v0.5.2 | 6.07 [5.66–6.38] | 11.60 [11.27–11.98] | 177.67 [175.00–180.00] |
| fortio: openai / 1024 B, 32 connections, 1000 RPS | Praxis core nightly-20261002 | 8.31 [8.12–8.67] | 18.84 [18.71–19.03] | 176.00 [173.00–180.00] |
| fortio: openai / 1024 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 17.11 [16.57–18.08] | 20.37 [16.01–22.66] | 77.67 [76.00–81.00] |
| fortio: openai / 1024 B, 32 connections, 3000 RPS | Praxis core v0.5.2 | 14.25 [13.14–15.16] | 10.97 [10.80–11.11] | 80.00 [76.00–84.00] |
| fortio: openai / 1024 B, 32 connections, 3000 RPS | Praxis core nightly-20261002 | 19.18 [18.03–19.80] | 18.13 [18.04–18.27] | 83.33 [81.00–86.00] |
| fortio: openai / 1024 B, 512 connections, unlimited | Agentgateway v1.6.0 | 98.64 [96.42–99.75] | 75.03 [73.46–76.77] | 973.00 [930.00–998.00] |
| fortio: openai / 1024 B, 512 connections, unlimited | Praxis core v0.5.2 | 99.64 [99.58–99.69] | 96.79 [94.61–99.22] | 925.67 [896.00–953.00] |
| fortio: openai / 1024 B, 512 connections, unlimited | Praxis core nightly-20261002 | 99.61 [99.49–99.76] | 88.40 [88.00–89.03] | 925.67 [899.00–952.00] |
| fortio: openai / 16384 B, 32 connections, unlimited | Agentgateway v1.6.0 | 85.71 [83.18–88.18] | 22.79 [22.60–23.10] | 86.67 [85.00–89.00] |
| fortio: openai / 16384 B, 32 connections, unlimited | Praxis core v0.5.2 | 96.33 [95.81–96.87] | 21.08 [20.96–21.33] | 83.67 [83.00–85.00] |
| fortio: openai / 16384 B, 32 connections, unlimited | Praxis core nightly-20261002 | 85.02 [81.75–86.76] | 24.89 [24.75–25.00] | 89.00 [89.00–89.00] |
| fortio: openai / 16384 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 12.03 [11.68–12.72] | 19.97 [19.32–21.00] | 84.00 [84.00–84.00] |
| fortio: openai / 16384 B, 32 connections, 1000 RPS | Praxis core v0.5.2 | 13.57 [13.07–14.09] | 10.91 [10.42–11.38] | 54.67 [54.00–55.00] |
| fortio: openai / 16384 B, 32 connections, 1000 RPS | Praxis core nightly-20261002 | 12.74 [12.54–13.06] | 19.73 [19.71–19.76] | 89.00 [89.00–89.00] |
| fortio: openai / 16384 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 31.29 [31.00–31.74] | 20.02 [19.66–20.43] | 84.00 [84.00–84.00] |
| fortio: openai / 16384 B, 32 connections, 3000 RPS | Praxis core v0.5.2 | 36.99 [36.64–37.60] | 13.47 [13.33–13.57] | 56.33 [56.00–57.00] |
| fortio: openai / 16384 B, 32 connections, 3000 RPS | Praxis core nightly-20261002 | 32.70 [30.69–34.26] | 21.42 [21.23–21.73] | 89.00 [89.00–89.00] |
| fortio: openai / 16384 B, 512 connections, unlimited | Agentgateway v1.6.0 | 98.62 [96.45–99.72] | 140.14 [138.04–141.35] | 1157.67 [1149.00–1165.00] |
| fortio: openai / 16384 B, 512 connections, unlimited | Praxis core v0.5.2 | 99.47 [99.41–99.55] | 140.07 [136.82–142.64] | 841.33 [819.00–874.00] |
| fortio: openai / 16384 B, 512 connections, unlimited | Praxis core nightly-20261002 | 99.63 [99.54–99.70] | 124.89 [122.69–126.50] | 905.00 [897.00–919.00] |
