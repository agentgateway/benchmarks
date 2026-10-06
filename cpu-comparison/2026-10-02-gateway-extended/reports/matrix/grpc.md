# gRPC — per-test evidence

Each cell gives repetitions 1 / 2 / 3: **P** pass, **F** assertion failure, **S** skipped, **N/E** not executed, **pending** no result yet. N/E is not a feature failure. Source links identify the exact pinned upstream test.

| Test | Provisional | Agentgateway v1.6.0 / release comparison | Praxis v0.5.2 | Agentgateway v1.6.0 / nightly comparison | Praxis nightly-20261002 |
| --- | --- | --- | --- | --- | --- |
| [GRPCExactMethodMatching](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/grpcroute-exact-method-matching.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [GRPCRouteHeaderMatching](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/grpcroute-header-matching.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [GRPCRouteListenerHostnameMatching](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/grpcroute-listener-hostname-matching.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [GRPCRouteNamedRule](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/grpcroute-named-rule.go) | yes | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [GRPCRouteWeight](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/grpcroute-weight.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |

Two tests use experimental features: HTTPRouteInvalidParentRefNotMatchingListenerPort and TLSRouteMixedTerminationSameNamespace. All other selected cases use standard-channel feature labels.
