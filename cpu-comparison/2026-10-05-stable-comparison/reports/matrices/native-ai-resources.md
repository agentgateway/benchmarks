# Sampled resources: native ai

Cells show the arithmetic mean of three per-run values followed by [minimum–maximum]. CPU is the mean over each sampled tool-execution window; memory is each window’s maximum sampled cgroup charge. These include client startup/warmup and are not exact measurement-only CPU cycles or RSS. See [resource interpretation](../08-resource-usage.md).

| Tool / case | Treatment | CPU, % of two-CPU quota | Maximum sampled memory, MiB | Maximum sampled descriptors |
| --- | --- | ---: | ---: | ---: |
| aiperf: anthropic, 16 streams | Agentgateway v1.6.0 | 5.09 [4.90–5.27] | 60.19 [57.86–62.75] | 318.00 [168.00–618.00] |
| aiperf: anthropic, 16 streams | Praxis AI v0.5.0 | 5.40 [4.97–6.01] | 47.75 [43.36–52.91] | 204.00 [204.00–204.00] |
| aiperf: anthropic, 16 streams | Praxis AI Oct 2 nightly | 5.64 [5.17–6.15] | 46.69 [45.75–47.95] | 204.00 [204.00–204.00] |
| aiperf: anthropic, 128 streams | Agentgateway v1.6.0 | 25.21 [24.47–26.22] | 42.28 [41.99–42.45] | 278.00 [278.00–278.00] |
| aiperf: anthropic, 128 streams | Praxis AI v0.5.0 | 25.82 [24.19–28.54] | 58.84 [55.63–60.88] | 426.00 [426.00–426.00] |
| aiperf: anthropic, 128 streams | Praxis AI Oct 2 nightly | 24.86 [24.57–25.07] | 56.31 [55.58–57.29] | 426.00 [426.00–426.00] |
| aiperf: openai, 16 streams | Agentgateway v1.6.0 | 4.92 [4.67–5.21] | 85.52 [71.04–101.24] | 655.67 [653.00–660.00] |
| aiperf: openai, 16 streams | Praxis AI v0.5.0 | 5.25 [5.10–5.41] | 108.19 [92.28–118.96] | 208.33 [206.00–210.00] |
| aiperf: openai, 16 streams | Praxis AI Oct 2 nightly | 5.52 [5.34–5.61] | 112.14 [99.46–123.75] | 214.00 [210.00–217.00] |
| aiperf: openai, 128 streams | Agentgateway v1.6.0 | 25.46 [24.35–26.92] | 64.97 [64.72–65.30] | 765.67 [763.00–770.00] |
| aiperf: openai, 128 streams | Praxis AI v0.5.0 | 23.87 [23.70–24.14] | 49.31 [44.81–54.21] | 298.33 [298.00–299.00] |
| aiperf: openai, 128 streams | Praxis AI Oct 2 nightly | 24.59 [23.35–26.74] | 48.11 [47.22–49.70] | 298.00 [298.00–298.00] |
| aiperf: translation, 16 streams | Agentgateway v1.6.0 | 6.01 [5.81–6.19] | 31.84 [30.86–32.64] | 168.00 [168.00–168.00] |
| aiperf: translation, 16 streams | Praxis AI v0.5.0 | 6.82 [6.64–7.12] | 53.53 [46.36–58.05] | 203.00 [203.00–203.00] |
| aiperf: translation, 16 streams | Praxis AI Oct 2 nightly | 6.86 [6.83–6.88] | 51.27 [44.46–55.68] | 203.33 [203.00–204.00] |
| aiperf: translation, 128 streams | Agentgateway v1.6.0 | 29.00 [28.29–30.32] | 33.68 [33.56–33.79] | 278.00 [278.00–278.00] |
| aiperf: translation, 128 streams | Praxis AI v0.5.0 | 33.01 [31.53–33.85] | 60.17 [58.52–63.03] | 425.33 [425.00–426.00] |
| aiperf: translation, 128 streams | Praxis AI Oct 2 nightly | 32.24 [30.84–35.04] | 60.94 [57.41–64.59] | 425.33 [425.00–426.00] |
| fortio: anthropic / 1024 B, 32 connections, unlimited | Agentgateway v1.6.0 | 99.58 [99.55–99.62] | 15.82 [15.79–15.85] | 87.33 [87.00–88.00] |
| fortio: anthropic / 1024 B, 32 connections, unlimited | Praxis AI v0.5.0 | 99.64 [99.61–99.66] | 27.72 [26.61–29.94] | 133.00 [132.00–134.00] |
| fortio: anthropic / 1024 B, 32 connections, unlimited | Praxis AI Oct 2 nightly | 99.61 [99.58–99.64] | 29.81 [28.84–30.37] | 132.67 [132.00–133.00] |
| fortio: anthropic / 1024 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 11.85 [11.66–12.05] | 20.63 [20.27–20.97] | 88.33 [88.00–89.00] |
| fortio: anthropic / 1024 B, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 12.14 [11.75–12.75] | 28.83 [28.02–29.41] | 133.33 [131.00–135.00] |
| fortio: anthropic / 1024 B, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 11.91 [11.39–12.22] | 29.35 [29.17–29.58] | 133.67 [132.00–135.00] |
| fortio: anthropic / 1024 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 28.95 [28.71–29.14] | 15.53 [15.44–15.61] | 88.33 [88.00–89.00] |
| fortio: anthropic / 1024 B, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 30.27 [29.34–31.26] | 26.69 [25.38–28.64] | 133.33 [131.00–135.00] |
| fortio: anthropic / 1024 B, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 30.40 [30.28–30.63] | 28.83 [27.88–29.53] | 133.67 [132.00–135.00] |
| fortio: anthropic / 16384 B, 32 connections, unlimited | Agentgateway v1.6.0 | 99.63 [99.61–99.65] | 21.83 [21.59–22.16] | 88.00 [87.00–89.00] |
| fortio: anthropic / 16384 B, 32 connections, unlimited | Praxis AI v0.5.0 | 99.74 [99.70–99.76] | 34.30 [31.48–37.30] | 103.33 [103.00–104.00] |
| fortio: anthropic / 16384 B, 32 connections, unlimited | Praxis AI Oct 2 nightly | 99.71 [99.67–99.77] | 36.26 [35.08–36.97] | 102.67 [102.00–103.00] |
| fortio: anthropic / 16384 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 19.05 [18.73–19.65] | 19.46 [18.76–19.89] | 83.33 [82.00–84.00] |
| fortio: anthropic / 16384 B, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 40.16 [39.68–40.83] | 30.26 [27.71–33.25] | 102.33 [102.00–103.00] |
| fortio: anthropic / 16384 B, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 40.83 [40.75–40.94] | 32.92 [32.02–33.40] | 102.33 [102.00–103.00] |
| fortio: anthropic / 16384 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 49.47 [48.70–50.03] | 19.01 [18.62–19.26] | 83.33 [82.00–84.00] |
| fortio: anthropic / 16384 B, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 99.74 [99.71–99.75] | 33.28 [30.66–36.11] | 102.33 [102.00–103.00] |
| fortio: anthropic / 16384 B, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 99.71 [99.68–99.74] | 35.67 [34.33–36.37] | 102.33 [102.00–103.00] |
| fortio: openai / 1024 B, 32 connections, unlimited | Agentgateway v1.6.0 | 99.59 [99.53–99.62] | 14.36 [14.20–14.46] | 83.67 [83.00–84.00] |
| fortio: openai / 1024 B, 32 connections, unlimited | Praxis AI v0.5.0 | 99.62 [99.57–99.66] | 21.11 [20.80–21.45] | 103.00 [103.00–103.00] |
| fortio: openai / 1024 B, 32 connections, unlimited | Praxis AI Oct 2 nightly | 99.47 [99.17–99.65] | 20.77 [20.27–21.16] | 103.00 [103.00–103.00] |
| fortio: openai / 1024 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 12.10 [11.80–12.32] | 12.93 [12.67–13.30] | 84.00 [84.00–84.00] |
| fortio: openai / 1024 B, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 11.29 [10.97–11.45] | 19.29 [19.08–19.59] | 102.67 [102.00–103.00] |
| fortio: openai / 1024 B, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 10.93 [10.56–11.20] | 19.47 [18.95–19.89] | 102.33 [101.00–103.00] |
| fortio: openai / 1024 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 29.71 [28.63–30.46] | 13.04 [12.84–13.38] | 83.67 [83.00–84.00] |
| fortio: openai / 1024 B, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 27.87 [27.15–28.24] | 19.92 [19.56–20.18] | 102.67 [102.00–103.00] |
| fortio: openai / 1024 B, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 27.62 [27.22–27.91] | 19.95 [19.89–20.06] | 102.33 [101.00–103.00] |
| fortio: openai / 1024 B, 512 connections, unlimited | Agentgateway v1.6.0 | 99.68 [99.55–99.78] | 79.61 [77.88–81.40] | 981.00 [945.00–1002.00] |
| fortio: openai / 1024 B, 512 connections, unlimited | Praxis AI v0.5.0 | 99.68 [99.60–99.78] | 106.74 [104.30–110.57] | 954.67 [936.00–967.00] |
| fortio: openai / 1024 B, 512 connections, unlimited | Praxis AI Oct 2 nightly | 99.71 [99.69–99.75] | 105.61 [104.95–106.19] | 957.00 [938.00–969.00] |
| fortio: openai / 16384 B, 32 connections, unlimited | Agentgateway v1.6.0 | 99.65 [99.62–99.68] | 21.69 [21.66–21.73] | 88.00 [87.00–89.00] |
| fortio: openai / 16384 B, 32 connections, unlimited | Praxis AI v0.5.0 | 99.72 [99.68–99.76] | 26.92 [26.74–27.04] | 103.00 [103.00–103.00] |
| fortio: openai / 16384 B, 32 connections, unlimited | Praxis AI Oct 2 nightly | 99.71 [99.67–99.73] | 26.58 [26.38–26.71] | 103.00 [103.00–103.00] |
| fortio: openai / 16384 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 19.03 [18.56–19.56] | 18.63 [18.50–18.85] | 83.00 [81.00–84.00] |
| fortio: openai / 16384 B, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 39.21 [38.62–39.74] | 23.62 [23.18–24.02] | 102.67 [102.00–103.00] |
| fortio: openai / 16384 B, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 39.96 [39.71–40.39] | 23.20 [22.99–23.34] | 103.00 [103.00–103.00] |
| fortio: openai / 16384 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 48.68 [48.64–48.73] | 18.85 [18.69–19.16] | 83.00 [81.00–84.00] |
| fortio: openai / 16384 B, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 99.72 [99.69–99.74] | 25.99 [25.71–26.34] | 102.67 [102.00–103.00] |
| fortio: openai / 16384 B, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 99.72 [99.70–99.75] | 26.12 [25.99–26.20] | 102.67 [102.00–103.00] |
| fortio: openai / 16384 B, 512 connections, unlimited | Agentgateway v1.6.0 | 98.72 [96.94–99.71] | 149.04 [146.19–150.64] | 1147.67 [1145.00–1152.00] |
| fortio: openai / 16384 B, 512 connections, unlimited | Praxis AI v0.5.0 | 99.64 [99.60–99.66] | 149.57 [139.27–155.37] | 947.67 [937.00–954.00] |
| fortio: openai / 16384 B, 512 connections, unlimited | Praxis AI Oct 2 nightly | 99.64 [99.63–99.65] | 145.95 [142.30–148.55] | 958.33 [942.00–969.00] |
| fortio: translation / 1024 B, 32 connections, unlimited | Agentgateway v1.6.0 | 99.60 [99.54–99.64] | 15.82 [15.65–16.01] | 88.00 [88.00–88.00] |
| fortio: translation / 1024 B, 32 connections, unlimited | Praxis AI v0.5.0 | 99.57 [99.55–99.59] | 38.68 [34.81–43.18] | 132.00 [132.00–132.00] |
| fortio: translation / 1024 B, 32 connections, unlimited | Praxis AI Oct 2 nightly | 99.58 [99.54–99.60] | 39.66 [37.93–41.23] | 129.67 [129.00–130.00] |
| fortio: translation / 1024 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 12.12 [11.69–12.39] | 20.78 [20.23–21.48] | 88.33 [88.00–89.00] |
| fortio: translation / 1024 B, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 15.92 [15.58–16.41] | 33.28 [30.97–36.41] | 103.33 [101.00–105.00] |
| fortio: translation / 1024 B, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 16.18 [15.62–16.51] | 36.27 [35.42–37.07] | 100.33 [95.00–104.00] |
| fortio: translation / 1024 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 30.86 [30.43–31.24] | 15.78 [15.46–16.03] | 88.33 [88.00–89.00] |
| fortio: translation / 1024 B, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 44.55 [44.42–44.75] | 32.75 [28.51–37.12] | 104.67 [103.00–106.00] |
| fortio: translation / 1024 B, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 45.47 [45.19–45.73] | 34.66 [31.62–37.34] | 102.67 [101.00–104.00] |
| fortio: translation / 16384 B, 32 connections, unlimited | Agentgateway v1.6.0 | 99.65 [99.61–99.68] | 21.85 [21.81–21.92] | 88.67 [88.00–89.00] |
| fortio: translation / 16384 B, 32 connections, unlimited | Praxis AI v0.5.0 | 99.79 [99.76–99.83] | 41.04 [35.91–48.13] | 103.00 [103.00–103.00] |
| fortio: translation / 16384 B, 32 connections, unlimited | Praxis AI Oct 2 nightly | 99.79 [99.76–99.81] | 44.23 [43.09–44.93] | 103.33 [103.00–104.00] |
| fortio: translation / 16384 B, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 19.42 [18.98–19.70] | 18.86 [18.67–19.02] | 82.33 [82.00–83.00] |
| fortio: translation / 16384 B, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 68.50 [68.23–68.94] | 38.65 [35.21–43.60] | 103.00 [103.00–103.00] |
| fortio: translation / 16384 B, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 70.14 [69.57–70.67] | 39.68 [37.62–41.32] | 103.33 [103.00–104.00] |
| fortio: translation / 16384 B, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 50.84 [50.67–51.15] | 19.02 [18.54–19.39] | 82.33 [82.00–83.00] |
| fortio: translation / 16384 B, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 99.77 [99.74–99.80] | 42.85 [39.79–47.07] | 103.00 [103.00–103.00] |
| fortio: translation / 16384 B, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 99.78 [99.76–99.81] | 44.27 [41.93–46.23] | 103.33 [103.00–104.00] |
