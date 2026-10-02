# Common core HTTP conformance

Both implementations passed **33 tests, with zero failures and zero core skips**, against Gateway API v1.5.1 source/CRDs `e7677b70ae75d14a4448fba94870e7deea6cf0ad`.

| Implementation | Core passed | Core failed | Core skipped |
| --- | ---: | ---: | ---: |
| agentgateway controller/proxy v1.5.0 | 33 | 0 | 0 |
| Praxis operator fb8beaa + documented core 0.5.2 | 33 | 0 | 0 |

The selected profile was `GATEWAY-HTTP`, with explicit `--supported-features=Gateway,HTTPRoute,ReferenceGrant`, no arbitrary skips and no CRD mismatch override. Extended tests outside that shared set appear as excluded/skipped in the full logs; they are not passing capabilities. This is a Solo.io-executed observation, not third-party certification or proof of complete feature parity.

The primary evidence directories are `conformance-agentgateway-core` and `conformance-praxis-core-clean` in the raw bundle. Each contains full logs, YAML report, start/end times, exit code and cluster snapshots. The actual classes retain their advertised feature declarations in campaign snapshots. The conformance runner uses the same resource-normalized class parameters as the other tests.

## Earlier attempts, retained separately

- `conformance-agentgateway`: leaving supported features empty caused automatic inference of the GatewayClass's advertised extensions. Core passed 33/33. The extended report lists 53 passes and one failure, `GatewayStaticAddresses`; its log shows zero usable and unusable address fixtures were supplied, while the test expected three total addresses. This preliminary setup does not establish a static-address implementation defect or a comparable extension score.
- `conformance-praxis-core`: the first sequential launch collided with deletion of the preceding suite's namespace and failed in setup before executing cases. The runner now waits for namespace deletion. This is a harness teardown error, not a Praxis conformance failure. The clean run is retained separately rather than overwriting it.

## Operator/core compatibility

Praxis operator `fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c` with core 0.7.2 generated an empty router for a Gateway with no HTTPRoutes. That core exited with `router: 'routes' is empty; every request would fail with 404`. The empty Gateway did not become ready. Agentgateway's empty Gateway became ready.

Changing only the Praxis proxy image to the operator's documented default core 0.5.2 made the empty Gateway ready. The primary comparison therefore uses 0.5.2, with both failed and successful qualification configurations/logs retained. This is a tested incompatibility of the specified operator/newer-core combination, not a throughput score, a claim that Praxis lacks Gateway API support, or a prediction about other revisions.
