# Standalone native AI: AI matrix

Values are arithmetic means of three runs followed by [minimum–maximum].
Latency p99 is the mean of each run's p99, **not a pooled p99**. RPS counts successful
responses. Fortio latency includes all response statuses. Do not compare different
workloads, traffic rates, APIs or deployment profiles as if they were equal work.
Every individual pass and raw artifact path is in [load-rows.json](../data/load-rows.json).

Praxis AI response usage extraction and agentgateway LLM processing are distinct implementations. Translation has an OpenAI direct baseline and Anthropic gateway clients. These ratios do not isolate equal accounting work.

## fortio

| Case | Treatment | Successful RPS | Mean latency ms | p99 latency ms | Error evidence |
| --- | --- | ---: | ---: | ---: | --- |
| anthropic / 1024 B content, 32 connections, unlimited | Direct service | 60,099 [59,160–60,756] | 0.532 [0.526–0.540] | 1.983 [1.980–1.988] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 14,158 [13,781–14,467] | 2.261 [2.211–2.321] | 3.737 [3.639–3.845] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 12,075 [11,979–12,220] | 2.650 [2.618–2.671] | 3.979 [3.973–3.983] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 12,108 [11,705–12,340] | 2.644 [2.593–2.733] | 3.978 [3.968–3.994] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 1000 RPS | Direct service | 998.951 [998.942–998.956] | 0.314 [0.304–0.332] | 0.481 [0.439–0.556] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.923 [998.917–998.930] | 0.639 [0.609–0.660] | 0.868 [0.805–0.917] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 998.930 [998.918–998.943] | 0.630 [0.605–0.660] | 0.871 [0.833–0.948] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 998.920 [998.919–998.920] | 0.621 [0.614–0.631] | 0.854 [0.832–0.874] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.307 [0.293–0.326] | 0.572 [0.555–0.591] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 0.568 [0.552–0.579] | 0.825 [0.786–0.856] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 2,999 [2,999–2,999] | 0.575 [0.550–0.601] | 0.831 [0.793–0.888] | 0.000 [0.000–0.000] errors/run |
| anthropic / 1024 B content, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 2,999 [2,999–2,999] | 0.582 [0.568–0.596] | 0.850 [0.819–0.897] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, unlimited | Direct service | 10,267 [10,215–10,334] | 3.116 [3.096–3.132] | 15.160 [14.889–15.339] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 7,347 [7,214–7,438] | 4.355 [4.302–4.435] | 7.400 [7.390–7.414] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 2,700 [2,640–2,755] | 11.851 [11.612–12.118] | 19.880 [19.872–19.891] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 2,654 [2,628–2,677] | 12.056 [11.950–12.175] | 19.887 [19.883–19.891] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 1000 RPS | Direct service | 998.939 [998.935–998.943] | 0.645 [0.602–0.728] | 1.556 [1.342–1.691] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.920 [998.903–998.930] | 1.048 [1.027–1.063] | 1.984 [1.981–1.985] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 998.909 [998.896–998.921] | 1.451 [1.423–1.491] | 2.556 [2.421–2.732] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 998.904 [998.902–998.906] | 1.466 [1.462–1.473] | 2.627 [2.586–2.658] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.626 [0.597–0.682] | 1.629 [1.502–1.791] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 1.104 [1.074–1.121] | 1.987 [1.985–1.989] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 2,739 [2,687–2,766] | 8.159 [8.080–8.311] | 16.487 [15.837–17.381] | 0.000 [0.000–0.000] errors/run |
| anthropic / 16384 B content, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 2,680 [2,650–2,711] | 8.329 [8.237–8.407] | 17.252 [16.028–19.486] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, unlimited | Direct service | 58,425 [57,827–58,983] | 0.547 [0.542–0.553] | 1.992 [1.988–1.996] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 14,041 [13,871–14,211] | 2.279 [2.251–2.306] | 3.784 [3.738–3.825] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 13,398 [13,074–13,967] | 2.390 [2.290–2.447] | 3.905 [3.849–3.934] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 12,985 [12,897–13,115] | 2.464 [2.439–2.481] | 3.938 [3.932–3.943] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 1000 RPS | Direct service | 998.934 [998.923–998.950] | 0.315 [0.302–0.328] | 0.487 [0.442–0.545] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.922 [998.914–998.929] | 0.659 [0.635–0.695] | 0.913 [0.870–0.981] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 998.926 [998.916–998.945] | 0.618 [0.615–0.621] | 0.860 [0.836–0.891] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 998.937 [998.923–998.949] | 0.600 [0.588–0.615] | 0.816 [0.799–0.851] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.312 [0.303–0.323] | 0.586 [0.575–0.600] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 0.587 [0.567–0.621] | 0.853 [0.815–0.919] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 2,999 [2,999–2,999] | 0.556 [0.548–0.565] | 0.817 [0.795–0.846] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 2,999 [2,999–2,999] | 0.548 [0.528–0.567] | 0.803 [0.773–0.844] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 512 connections, unlimited | Direct service | 70,812 [69,812–71,367] | 7.229 [7.172–7.332] | 25.219 [24.780–25.611] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 512 connections, unlimited | Agentgateway v1.6.0 | 12,205 [12,014–12,361] | 41.938 [41.402–42.600] | 74.381 [74.335–74.446] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 512 connections, unlimited | Praxis AI v0.5.0 | 11,106 [11,075–11,150] | 46.070 [45.892–46.200] | 79.255 [77.341–81.614] | 0.000 [0.000–0.000] errors/run |
| openai / 1024 B content, 512 connections, unlimited | Praxis AI Oct 2 nightly | 11,126 [10,969–11,258] | 45.990 [45.445–46.648] | 79.968 [77.456–83.939] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, unlimited | Direct service | 10,031 [9,976–10,060] | 3.189 [3.180–3.207] | 15.800 [15.689–15.913] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 7,399 [7,321–7,488] | 4.324 [4.273–4.370] | 7.395 [7.382–7.406] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 2,838 [2,811–2,859] | 11.275 [11.188–11.382] | 19.863 [19.861–19.867] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 2,714 [2,682–2,731] | 11.788 [11.716–11.931] | 19.881 [19.878–19.885] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 1000 RPS | Direct service | 998.912 [998.908–998.918] | 0.625 [0.608–0.651] | 1.543 [1.406–1.758] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.926 [998.922–998.930] | 1.064 [1.035–1.082] | 1.979 [1.964–1.987] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 998.909 [998.899–998.920] | 1.402 [1.371–1.429] | 2.380 [2.117–2.565] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 998.899 [998.890–998.907] | 1.418 [1.403–1.433] | 2.501 [2.449–2.600] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.612 [0.603–0.629] | 1.582 [1.448–1.703] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 1.118 [1.084–1.141] | 1.988 [1.986–1.990] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 2,791 [2,774–2,813] | 7.999 [7.894–8.059] | 16.076 [15.644–16.448] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 2,740 [2,735–2,748] | 8.165 [8.132–8.189] | 16.776 [16.484–17.038] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 512 connections, unlimited | Direct service | 14,377 [14,244–14,477] | 35.577 [35.330–35.909] | 1,080 [1,028–1,128] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 512 connections, unlimited | Agentgateway v1.6.0 | 6,810 [6,718–6,872] | 75.132 [74.440–76.153] | 215.877 [207.574–226.081] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 512 connections, unlimited | Praxis AI v0.5.0 | 2,693 [2,682–2,701] | 189.542 [188.959–190.344] | 448.226 [412.424–507.585] | 0.000 [0.000–0.000] errors/run |
| openai / 16384 B content, 512 connections, unlimited | Praxis AI Oct 2 nightly | 2,626 [2,613–2,637] | 194.386 [193.603–195.327] | 459.309 [437.526–474.129] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, unlimited | Direct service | 58,358 [57,366–59,208] | 0.548 [0.540–0.557] | 1.992 [1.982–2.003] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 12,822 [12,503–13,295] | 2.497 [2.406–2.559] | 3.939 [3.911–3.957] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 7,118 [7,063–7,218] | 4.495 [4.433–4.530] | 7.411 [7.401–7.416] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 7,025 [6,936–7,111] | 4.554 [4.499–4.613] | 7.419 [7.411–7.428] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, 1000 RPS | Direct service | 998.939 [998.924–998.957] | 0.335 [0.303–0.384] | 0.502 [0.441–0.598] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.935 [998.916–998.947] | 0.626 [0.594–0.648] | 0.854 [0.805–0.899] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 998.936 [998.934–998.939] | 0.884 [0.851–0.917] | 1.801 [1.606–1.951] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 998.926 [998.908–998.939] | 0.900 [0.869–0.940] | 1.921 [1.879–1.960] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.313 [0.298–0.328] | 0.584 [0.567–0.598] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 0.566 [0.559–0.573] | 0.834 [0.803–0.859] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 2,999 [2,999–2,999] | 0.828 [0.810–0.849] | 1.865 [1.830–1.911] | 0.000 [0.000–0.000] errors/run |
| translation / 1024 B content, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 2,999 [2,999–2,999] | 0.841 [0.836–0.849] | 1.884 [1.877–1.894] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, unlimited | Direct service | 10,081 [10,064–10,101] | 3.173 [3.167–3.179] | 15.656 [15.538–15.758] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, unlimited | Agentgateway v1.6.0 | 7,172 [7,116–7,226] | 4.461 [4.427–4.496] | 7.419 [7.415–7.424] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, unlimited | Praxis AI v0.5.0 | 1,507 [1,497–1,519] | 21.222 [21.060–21.368] | 36.271 [36.061–36.376] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, unlimited | Praxis AI Oct 2 nightly | 1,460 [1,456–1,468] | 21.907 [21.792–21.975] | 37.507 [37.407–37.609] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, 1000 RPS | Direct service | 998.933 [998.928–998.940] | 0.659 [0.641–0.689] | 1.673 [1.598–1.720] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, 1000 RPS | Agentgateway v1.6.0 | 998.909 [998.903–998.922] | 1.061 [1.048–1.073] | 1.985 [1.984–1.987] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, 1000 RPS | Praxis AI v0.5.0 | 998.880 [998.865–998.892] | 2.098 [2.061–2.144] | 2.994 [2.990–2.999] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, 1000 RPS | Praxis AI Oct 2 nightly | 998.894 [998.890–998.898] | 2.119 [2.102–2.138] | 2.996 [2.995–2.999] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, 3000 RPS | Direct service | 2,999 [2,999–2,999] | 0.625 [0.612–0.645] | 1.603 [1.441–1.739] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, 3000 RPS | Agentgateway v1.6.0 | 2,999 [2,999–2,999] | 1.151 [1.121–1.173] | 1.991 [1.990–1.992] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, 3000 RPS | Praxis AI v0.5.0 | 1,494 [1,482–1,501] | 15.794 [15.686–15.975] | 29.199 [29.070–29.449] | 0.000 [0.000–0.000] errors/run |
| translation / 16384 B content, 32 connections, 3000 RPS | Praxis AI Oct 2 nightly | 1,477 [1,470–1,488] | 16.144 [15.919–16.287] | 29.278 [29.184–29.337] | 0.000 [0.000–0.000] errors/run |

## aiperf

| Case | Treatment | Successful RPS | Mean TTFT ms | p99 TTFT ms | Mean ITL ms | Errors per run |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| anthropic, 16 streams | Direct service | 41.344 [41.285–41.415] | 26.442 [26.434–26.456] | 28.276 [28.193–28.334] | 5.572 [5.561–5.581] | 0.000 [0.000–0.000] |
| anthropic, 16 streams | Agentgateway v1.6.0 | 41.212 [41.111–41.298] | 27.157 [27.080–27.210] | 29.213 [28.992–29.415] | 5.577 [5.565–5.593] | 0.000 [0.000–0.000] |
| anthropic, 16 streams | Praxis AI v0.5.0 | 41.284 [41.232–41.366] | 26.820 [26.808–26.826] | 28.823 [28.705–28.888] | 5.575 [5.563–5.583] | 0.000 [0.000–0.000] |
| anthropic, 16 streams | Praxis AI Oct 2 nightly | 41.346 [41.177–41.459] | 26.804 [26.779–26.842] | 28.823 [28.612–29.108] | 5.566 [5.549–5.592] | 0.000 [0.000–0.000] |
| anthropic, 128 streams | Direct service | 323.859 [323.725–324.083] | 27.205 [27.147–27.235] | 36.991 [36.130–37.529] | 5.609 [5.608–5.610] | 0.000 [0.000–0.000] |
| anthropic, 128 streams | Agentgateway v1.6.0 | 323.691 [323.199–324.086] | 27.760 [27.672–27.851] | 36.264 [35.655–37.201] | 5.603 [5.600–5.606] | 0.000 [0.000–0.000] |
| anthropic, 128 streams | Praxis AI v0.5.0 | 322.788 [321.967–323.381] | 27.550 [27.451–27.641] | 37.844 [35.982–39.571] | 5.624 [5.618–5.632] | 0.000 [0.000–0.000] |
| anthropic, 128 streams | Praxis AI Oct 2 nightly | 323.360 [323.223–323.521] | 27.513 [27.501–27.532] | 36.046 [35.766–36.507] | 5.618 [5.617–5.620] | 0.000 [0.000–0.000] |
| openai, 16 streams | Direct service | 41.351 [41.240–41.482] | 26.328 [26.306–26.363] | 27.230 [27.137–27.374] | 5.589 [5.570–5.608] | 0.000 [0.000–0.000] |
| openai, 16 streams | Agentgateway v1.6.0 | 41.307 [41.265–41.354] | 26.715 [26.674–26.746] | 27.937 [27.686–28.107] | 5.584 [5.580–5.589] | 0.000 [0.000–0.000] |
| openai, 16 streams | Praxis AI v0.5.0 | 41.368 [41.293–41.426] | 26.600 [26.559–26.624] | 27.742 [27.420–28.012] | 5.573 [5.552–5.594] | 0.000 [0.000–0.000] |
| openai, 16 streams | Praxis AI Oct 2 nightly | 41.480 [41.453–41.534] | 26.621 [26.614–26.626] | 27.861 [27.647–28.010] | 5.558 [5.546–5.570] | 0.000 [0.000–0.000] |
| openai, 128 streams | Direct service | 323.419 [322.856–323.772] | 26.817 [26.802–26.835] | 32.595 [32.035–33.159] | 5.666 [5.661–5.670] | 0.000 [0.000–0.000] |
| openai, 128 streams | Agentgateway v1.6.0 | 320.680 [320.366–321.046] | 27.257 [27.237–27.275] | 33.812 [32.744–34.403] | 5.703 [5.695–5.710] | 0.000 [0.000–0.000] |
| openai, 128 streams | Praxis AI v0.5.0 | 321.392 [321.306–321.555] | 27.170 [27.166–27.174] | 34.331 [33.364–35.209] | 5.690 [5.688–5.692] | 0.000 [0.000–0.000] |
| openai, 128 streams | Praxis AI Oct 2 nightly | 321.827 [320.844–322.552] | 27.127 [27.085–27.200] | 33.547 [33.266–33.997] | 5.685 [5.676–5.699] | 0.000 [0.000–0.000] |
| translation, 16 streams | Direct service | 41.322 [41.253–41.380] | 26.323 [26.290–26.371] | 27.527 [27.096–27.968] | 5.594 [5.585–5.608] | 0.000 [0.000–0.000] |
| translation, 16 streams | Agentgateway v1.6.0 | 41.205 [41.135–41.269] | 26.763 [26.712–26.797] | 28.421 [27.740–28.969] | 5.570 [5.544–5.587] | 0.000 [0.000–0.000] |
| translation, 16 streams | Praxis AI v0.5.0 | 41.214 [41.124–41.271] | 26.730 [26.688–26.755] | 28.256 [28.005–28.434] | 5.585 [5.575–5.598] | 0.000 [0.000–0.000] |
| translation, 16 streams | Praxis AI Oct 2 nightly | 41.277 [41.154–41.471] | 26.779 [26.761–26.801] | 28.770 [28.682–28.868] | 5.577 [5.549–5.594] | 0.000 [0.000–0.000] |
| translation, 128 streams | Direct service | 322.991 [322.943–323.053] | 26.879 [26.851–26.916] | 34.401 [32.948–35.546] | 5.670 [5.667–5.675] | 0.000 [0.000–0.000] |
| translation, 128 streams | Agentgateway v1.6.0 | 324.062 [323.755–324.222] | 27.513 [27.452–27.576] | 36.967 [36.315–37.562] | 5.603 [5.596–5.611] | 0.000 [0.000–0.000] |
| translation, 128 streams | Praxis AI v0.5.0 | 323.074 [322.695–323.812] | 27.554 [27.488–27.589] | 37.030 [36.417–37.824] | 5.617 [5.613–5.622] | 0.000 [0.000–0.000] |
| translation, 128 streams | Praxis AI Oct 2 nightly | 324.034 [323.707–324.555] | 27.551 [27.477–27.591] | 36.799 [35.226–38.337] | 5.605 [5.604–5.606] | 0.000 [0.000–0.000] |
