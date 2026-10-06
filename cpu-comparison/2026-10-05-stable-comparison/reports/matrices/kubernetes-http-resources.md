# Sampled resources: kubernetes http

Cells show the arithmetic mean of three per-run values followed by [minimum–maximum]. CPU is the mean over each sampled tool-execution window; memory is each window’s maximum sampled cgroup charge. These include client startup/warmup and are not exact measurement-only CPU cycles or RSS. See [resource interpretation](../08-resource-usage.md).

| Tool / case | Treatment | CPU, % of two-CPU quota | Maximum sampled memory, MiB | Maximum sampled descriptors |
| --- | --- | ---: | ---: | ---: |
| fortio: 0 B, 1 connections, unlimited | Agentgateway v1.6.0 | 3.30 [3.17–3.51] | 9.06 [8.91–9.35] | 24.00 [24.00–24.00] |
| fortio: 0 B, 1 connections, unlimited | Praxis core v0.5.2 | 3.00 [2.88–3.12] | 7.35 [7.23–7.43] | 28.00 [28.00–28.00] |
| fortio: 0 B, 1 connections, 1000 RPS | Agentgateway v1.6.0 | 2.15 [2.09–2.20] | 9.09 [8.68–9.41] | 24.00 [24.00–24.00] |
| fortio: 0 B, 1 connections, 1000 RPS | Praxis core v0.5.2 | 1.94 [1.86–2.00] | 6.40 [5.95–6.94] | 28.00 [28.00–28.00] |
| fortio: 0 B, 16 connections, unlimited | Agentgateway v1.6.0 | 41.40 [39.96–42.36] | 12.36 [11.98–12.57] | 54.00 [54.00–54.00] |
| fortio: 0 B, 16 connections, unlimited | Praxis core v0.5.2 | 33.76 [32.33–34.54] | 29.47 [28.70–29.86] | 58.00 [58.00–58.00] |
| fortio: 0 B, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 5.38 [5.28–5.52] | 11.40 [11.36–11.43] | 54.00 [54.00–54.00] |
| fortio: 0 B, 16 connections, 1000 RPS | Praxis core v0.5.2 | 4.77 [4.75–4.79] | 10.96 [10.75–11.30] | 58.00 [58.00–58.00] |
| fortio: 0 B, 512 connections, unlimited | Agentgateway v1.6.0 | 97.48 [96.33–99.66] | 76.15 [74.58–77.00] | 931.67 [925.00–935.00] |
| fortio: 0 B, 512 connections, unlimited | Praxis core v0.5.2 | 99.58 [99.50–99.64] | 163.47 [160.50–167.42] | 924.33 [910.00–939.00] |
| fortio: 0 B, 512 connections, 1000 RPS | Agentgateway v1.6.0 | 5.41 [5.35–5.47] | 57.21 [55.30–59.49] | 808.33 [738.00–908.00] |
| fortio: 0 B, 512 connections, 1000 RPS | Praxis core v0.5.2 | 4.92 [4.85–4.98] | 85.55 [84.89–86.33] | 662.00 [661.00–663.00] |
| fortio: 16384 B, 1 connections, unlimited | Agentgateway v1.6.0 | 5.60 [5.16–5.93] | 28.52 [28.33–28.84] | 419.33 [414.00–423.00] |
| fortio: 16384 B, 1 connections, unlimited | Praxis core v0.5.2 | 4.74 [4.67–4.88] | 107.09 [105.62–107.85] | 145.67 [145.00–146.00] |
| fortio: 16384 B, 1 connections, 1000 RPS | Agentgateway v1.6.0 | 3.62 [3.59–3.65] | 64.27 [63.21–66.10] | 419.33 [414.00–423.00] |
| fortio: 16384 B, 1 connections, 1000 RPS | Praxis core v0.5.2 | 3.08 [3.01–3.13] | 151.91 [136.67–162.25] | 145.67 [145.00–146.00] |
| fortio: 16384 B, 16 connections, unlimited | Agentgateway v1.6.0 | 63.24 [61.74–64.06] | 24.79 [24.77–24.80] | 54.00 [54.00–54.00] |
| fortio: 16384 B, 16 connections, unlimited | Praxis core v0.5.2 | 55.86 [55.54–56.21] | 123.10 [122.06–124.48] | 58.00 [58.00–58.00] |
| fortio: 16384 B, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 9.60 [9.47–9.68] | 28.64 [28.44–28.96] | 361.00 [358.00–363.00] |
| fortio: 16384 B, 16 connections, 1000 RPS | Praxis core v0.5.2 | 7.97 [7.94–8.00] | 105.51 [104.08–106.25] | 160.67 [160.00–161.00] |
| fortio: 16384 B, 512 connections, unlimited | Agentgateway v1.6.0 | 99.48 [99.40–99.52] | 96.73 [93.77–99.79] | 963.67 [939.00–1008.00] |
| fortio: 16384 B, 512 connections, unlimited | Praxis core v0.5.2 | 99.80 [99.61–100.01] | 231.13 [229.20–233.55] | 918.33 [912.00–923.00] |
| fortio: 16384 B, 512 connections, 1000 RPS | Agentgateway v1.6.0 | 9.50 [9.43–9.61] | 68.93 [66.82–70.66] | 966.00 [889.00–1028.00] |
| fortio: 16384 B, 512 connections, 1000 RPS | Praxis core v0.5.2 | 8.21 [8.14–8.31] | 178.80 [177.69–180.85] | 660.67 [656.00–666.00] |
| nighthawk: 0 B, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 5.09 [4.98–5.24] | 69.28 [62.46–80.96] | 455.67 [431.00–500.00] |
| nighthawk: 0 B, 16 connections, 1000 RPS | Praxis core v0.5.2 | 4.63 [4.58–4.73] | 212.02 [202.07–217.52] | 147.33 [146.00–149.00] |
| nighthawk: 16384 B, 16 connections, 1000 RPS | Agentgateway v1.6.0 | 9.42 [9.32–9.61] | 40.50 [39.30–42.39] | 443.33 [431.00–463.00] |
| nighthawk: 16384 B, 16 connections, 1000 RPS | Praxis core v0.5.2 | 7.65 [7.52–7.74] | 168.97 [168.03–169.54] | 147.00 [145.00–149.00] |
