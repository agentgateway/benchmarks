# Sampled resources: common http

Cells show the arithmetic mean of three per-run values followed by [minimum–maximum]. CPU is the mean over each sampled tool-execution window; memory is each window’s maximum sampled cgroup charge. These include client startup/warmup and are not exact measurement-only CPU cycles or RSS. See [resource interpretation](../08-resource-usage.md).

| Tool / case | Treatment | CPU, % of two-CPU quota | Maximum sampled memory, MiB | Maximum sampled descriptors |
| --- | --- | ---: | ---: | ---: |
| fortio: 0 B, 1 connections, unlimited | Agentgateway v1.6.0 | 12.85 [12.18–13.46] | 8.31 [8.14–8.39] | 22.00 [22.00–22.00] |
| fortio: 0 B, 1 connections, unlimited | Praxis core v0.5.2 | 10.55 [10.23–10.72] | 4.77 [4.47–4.99] | 23.00 [23.00–23.00] |
| fortio: 0 B, 1 connections, unlimited | Praxis core nightly-20261002 | 13.66 [13.11–14.38] | 11.32 [11.17–11.45] | 27.00 [27.00–27.00] |
| fortio: 0 B, 1 connections, 1000 RPS | Agentgateway v1.6.0 | 4.58 [4.19–5.17] | 9.28 [9.04–9.42] | 22.00 [22.00–22.00] |
| fortio: 0 B, 1 connections, 1000 RPS | Praxis core v0.5.2 | 3.74 [3.52–3.98] | 5.57 [5.41–5.77] | 23.00 [23.00–23.00] |
| fortio: 0 B, 1 connections, 1000 RPS | Praxis core nightly-20261002 | 5.18 [5.10–5.25] | 12.23 [11.89–12.72] | 27.00 [27.00–27.00] |
| fortio: 0 B, 16 connections, unlimited | Agentgateway v1.6.0 | 97.92 [97.81–98.08] | 11.97 [11.64–12.23] | 52.00 [52.00–52.00] |
| fortio: 0 B, 16 connections, unlimited | Praxis core v0.5.2 | 93.12 [92.19–93.67] | 7.61 [7.36–7.85] | 53.00 [53.00–53.00] |
| fortio: 0 B, 16 connections, unlimited | Praxis core nightly-20261002 | 97.26 [96.99–97.42] | 14.20 [13.71–14.50] | 57.00 [57.00–57.00] |
| fortio: 0 B, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 6.73 [6.28–7.28] | 10.56 [10.46–10.73] | 51.00 [51.00–51.00] |
| fortio: 0 B, 16 connections, 1000 RPS | Praxis core v0.5.2 | 5.26 [5.08–5.47] | 6.74 [6.70–6.82] | 51.33 [51.00–52.00] |
| fortio: 0 B, 16 connections, 1000 RPS | Praxis core nightly-20261002 | 7.45 [7.21–7.78] | 13.30 [13.12–13.56] | 56.00 [56.00–56.00] |
| fortio: 0 B, 512 connections, unlimited | Agentgateway v1.6.0 | 98.84 [97.14–99.72] | 72.93 [71.52–74.27] | 924.00 [899.00–941.00] |
| fortio: 0 B, 512 connections, unlimited | Praxis core v0.5.2 | 99.53 [99.50–99.58] | 78.35 [77.46–80.09] | 931.00 [929.00–933.00] |
| fortio: 0 B, 512 connections, unlimited | Praxis core nightly-20261002 | 99.62 [99.58–99.65] | 85.17 [84.10–86.59] | 930.67 [918.00–955.00] |
| fortio: 0 B, 512 connections, 1000 RPS | Agentgateway v1.6.0 | 6.57 [6.42–6.87] | 56.14 [52.84–60.35] | 839.00 [726.00–927.00] |
| fortio: 0 B, 512 connections, 1000 RPS | Praxis core v0.5.2 | 5.34 [5.16–5.68] | 60.91 [59.50–62.28] | 651.33 [646.00–655.00] |
| fortio: 0 B, 512 connections, 1000 RPS | Praxis core nightly-20261002 | 7.58 [7.40–7.76] | 69.74 [68.05–71.75] | 660.67 [657.00–664.00] |
| fortio: 16384 B, 1 connections, unlimited | Agentgateway v1.6.0 | 17.30 [16.70–17.74] | 27.51 [26.79–28.18] | 412.67 [388.00–430.00] |
| fortio: 16384 B, 1 connections, unlimited | Praxis core v0.5.2 | 13.15 [12.47–14.16] | 14.15 [13.92–14.38] | 144.33 [140.00–150.00] |
| fortio: 16384 B, 1 connections, unlimited | Praxis core nightly-20261002 | 16.19 [15.89–16.67] | 19.83 [19.64–20.13] | 144.33 [141.00–147.00] |
| fortio: 16384 B, 1 connections, 1000 RPS | Agentgateway v1.6.0 | 6.02 [5.85–6.17] | 59.53 [55.29–65.42] | 412.67 [388.00–430.00] |
| fortio: 16384 B, 1 connections, 1000 RPS | Praxis core v0.5.2 | 4.71 [4.59–4.80] | 68.02 [66.42–69.21] | 144.33 [140.00–150.00] |
| fortio: 16384 B, 1 connections, 1000 RPS | Praxis core nightly-20261002 | 6.27 [6.22–6.34] | 71.68 [65.91–78.04] | 144.33 [141.00–147.00] |
| fortio: 16384 B, 16 connections, unlimited | Agentgateway v1.6.0 | 98.46 [98.26–98.75] | 23.62 [21.67–24.61] | 52.00 [52.00–52.00] |
| fortio: 16384 B, 16 connections, unlimited | Praxis core v0.5.2 | 96.21 [95.13–97.44] | 11.14 [10.91–11.27] | 53.00 [53.00–53.00] |
| fortio: 16384 B, 16 connections, unlimited | Praxis core nightly-20261002 | 98.79 [98.65–98.92] | 18.29 [18.28–18.30] | 57.00 [57.00–57.00] |
| fortio: 16384 B, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 9.91 [9.61–10.43] | 27.51 [26.46–28.20] | 348.33 [344.00–351.00] |
| fortio: 16384 B, 16 connections, 1000 RPS | Praxis core v0.5.2 | 7.38 [7.02–7.68] | 9.89 [9.41–10.14] | 159.33 [155.00–165.00] |
| fortio: 16384 B, 16 connections, 1000 RPS | Praxis core nightly-20261002 | 9.81 [9.55–9.98] | 17.08 [17.01–17.18] | 159.33 [156.00–162.00] |
| fortio: 16384 B, 512 connections, unlimited | Agentgateway v1.6.0 | 99.71 [99.68–99.73] | 95.01 [92.75–96.39] | 943.00 [929.00–963.00] |
| fortio: 16384 B, 512 connections, unlimited | Praxis core v0.5.2 | 99.63 [99.61–99.66] | 84.23 [84.12–84.34] | 915.00 [890.00–937.00] |
| fortio: 16384 B, 512 connections, unlimited | Praxis core nightly-20261002 | 99.62 [99.59–99.67] | 92.47 [92.02–92.75] | 911.33 [891.00–929.00] |
| fortio: 16384 B, 512 connections, 1000 RPS | Agentgateway v1.6.0 | 9.83 [9.43–10.21] | 66.41 [63.34–68.01] | 915.33 [846.00–954.00] |
| fortio: 16384 B, 512 connections, 1000 RPS | Praxis core v0.5.2 | 7.36 [7.20–7.47] | 64.31 [63.05–65.24] | 653.67 [649.00–659.00] |
| fortio: 16384 B, 512 connections, 1000 RPS | Praxis core nightly-20261002 | 9.80 [9.42–10.08] | 73.53 [71.19–75.10] | 659.00 [652.00–664.00] |
| nighthawk: 0 B, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 5.99 [5.80–6.19] | 74.20 [69.74–80.74] | 433.00 [419.00–453.00] |
| nighthawk: 0 B, 16 connections, 1000 RPS | Praxis core v0.5.2 | 4.59 [4.31–4.88] | 71.13 [68.91–73.27] | 149.67 [147.00–152.00] |
| nighthawk: 0 B, 16 connections, 1000 RPS | Praxis core nightly-20261002 | 6.67 [6.52–6.97] | 69.98 [66.55–76.11] | 147.67 [145.00–151.00] |
| nighthawk: 16384 B, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 9.08 [8.15–9.76] | 38.19 [34.70–41.77] | 407.33 [341.00–454.00] |
| nighthawk: 16384 B, 16 connections, 1000 RPS | Praxis core v0.5.2 | 6.64 [6.20–7.43] | 19.58 [12.43–33.61] | 149.00 [148.00–150.00] |
| nighthawk: 16384 B, 16 connections, 1000 RPS | Praxis core nightly-20261002 | 9.24 [8.72–9.56] | 19.15 [18.86–19.41] | 147.00 [144.00–150.00] |
