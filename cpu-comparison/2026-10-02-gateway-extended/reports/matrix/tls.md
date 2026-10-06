# TLS-dependent tests (including route-kind validation) — per-test evidence

Each cell gives repetitions 1 / 2 / 3: **P** pass, **F** assertion failure, **S** skipped, **N/E** not executed, **pending** no result yet. N/E is not a feature failure. Source links identify the exact pinned upstream test.

| Test | Provisional | Agentgateway v1.6.0 / release comparison | Praxis v0.5.2 | Agentgateway v1.6.0 / nightly comparison | Praxis nightly-20261002 |
| --- | --- | --- | --- | --- | --- |
| [HTTPRouteDisallowedKind](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/httproute-disallowed-kind.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [ListenerSetAllowedRoutesSupportedKinds](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/listenerset-allowed-routes-supported-kinds.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteHostnameIntersection](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-hostname-intersection.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteInvalidBackendRefNonexistent](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-invalid-backendref-nonexistent.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteInvalidBackendRefUnknownKind](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-invalid-backendref-unknown-kind.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteInvalidNoMatchingListener](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-invalid-no-matching-listener.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteInvalidNoMatchingListenerHostname](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-invalid-no-matching-listener-hostname.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteInvalidReferenceGrant](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-invalid-reference-grant.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteListenerMixedTerminationNotSupported](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-listener-mixed-termination-not-supported.go) | no | P / P / P | P / P / P | P / P / P | N/E / N/E / N/E |
| [TLSRouteListenerPassthroughSupportedKinds](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-listener-passthrough-supported-kinds.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteListenerTerminateNotSupported](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-listener-terminate-not-supported.go) | no | P / P / P | P / P / P | P / P / P | N/E / N/E / N/E |
| [TLSRouteListenerTerminateSupportedKinds](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-listener-terminate-supported-kinds.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteMixedTerminationSameNamespace](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-mixed-termination-same-namespace.go) | yes | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteSimpleSameNamespace](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-simple-same-namespace.go) | no | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |
| [TLSRouteTerminateSimpleSameNamespace](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/conformance/tests/tlsroute-terminate-simple-same-namespace.go) | yes | P / P / P | F / F / F | P / P / P | N/E / N/E / N/E |

Two tests use experimental features: HTTPRouteInvalidParentRefNotMatchingListenerPort and TLSRouteMixedTerminationSameNamespace. All other selected cases use standard-channel feature labels.
