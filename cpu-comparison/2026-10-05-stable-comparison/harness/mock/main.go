// Deterministic synthetic AI backend. No model inference takes place.
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync/atomic"
	"time"
)

var active, started, completed, canceled atomic.Int64

func event(w http.ResponseWriter, name string, value any) {
	b, _ := json.Marshal(value)
	if name != "" {
		fmt.Fprintf(w, "event: %s\n", name)
	}
	fmt.Fprintf(w, "data: %s\n\n", b)
	w.(http.Flusher).Flush()
}
func serve(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path == "/metrics" {
		json.NewEncoder(w).Encode(map[string]int64{"active": active.Load(), "started": started.Load(), "completed": completed.Load(), "canceled": canceled.Load()})
		return
	}
	if r.URL.Path == "/plain" {
		n, _ := strconv.Atoi(r.URL.Query().Get("bytes"))
		if n < 0 || n > 65536 {
			n = 0
		}
		w.Header().Set("Content-Length", strconv.Itoa(n))
		io.WriteString(w, strings.Repeat("x", n))
		return
	}
	if r.URL.Path == "/healthz" {
		io.WriteString(w, "ok")
		return
	}
	if r.URL.Path != "/v1/chat/completions" && r.URL.Path != "/v1/messages" {
		http.NotFound(w, r)
		return
	}
	var req struct {
		Model               string `json:"model"`
		Stream              bool   `json:"stream"`
		MaxTokens           int    `json:"max_tokens"`
		MaxCompletionTokens int    `json:"max_completion_tokens"`
	}
	if err := json.NewDecoder(http.MaxBytesReader(w, r.Body, 2<<20)).Decode(&req); err != nil {
		http.Error(w, "invalid JSON", 400)
		return
	}
	if r.Header.Get("x-bench-error") == "true" {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(429)
		io.WriteString(w, `{"error":{"type":"rate_limit_error","message":"synthetic rate limit"}}`)
		return
	}
	n, _ := strconv.Atoi(r.Header.Get("x-bench-output-bytes"))
	if n <= 0 {
		n = 1024
	}
	if n > 65536 {
		n = 65536
	}
	content := strings.Repeat("x", n)
	chunkSize := 64
	outputTokens := 64
	if req.Stream {
		outputTokens = req.MaxTokens
		if outputTokens <= 0 {
			outputTokens = req.MaxCompletionTokens
		}
		if outputTokens <= 0 {
			outputTokens = 64
		}
		if outputTokens > 1024 {
			outputTokens = 1024
		}
		content = strings.Repeat(" hello", outputTokens)
		chunkSize = 6
		started.Add(1)
		active.Add(1)
		defer active.Add(-1)
		select {
		case <-r.Context().Done():
			canceled.Add(1)
			return
		case <-time.After(25 * time.Millisecond):
		}
	}
	anthropic := r.URL.Path == "/v1/messages"
	if !req.Stream {
		w.Header().Set("Content-Type", "application/json")
		var out any
		if anthropic {
			out = map[string]any{"id": "msg_bench", "type": "message", "role": "assistant", "model": req.Model, "content": []any{map[string]any{"type": "text", "text": content}}, "stop_reason": "end_turn", "stop_sequence": nil, "usage": map[string]int{"input_tokens": 128, "output_tokens": outputTokens}}
		} else {
			out = map[string]any{"id": "chatcmpl-bench", "object": "chat.completion", "created": 1, "model": req.Model, "choices": []any{map[string]any{"index": 0, "message": map[string]string{"role": "assistant", "content": content}, "finish_reason": "stop"}}, "usage": map[string]int{"prompt_tokens": 128, "completion_tokens": outputTokens, "total_tokens": 128 + outputTokens}}
		}
		json.NewEncoder(w).Encode(out)
		return
	}
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	if anthropic {
		event(w, "message_start", map[string]any{"type": "message_start", "message": map[string]any{"id": "msg_bench", "type": "message", "role": "assistant", "model": req.Model, "content": []any{}, "stop_reason": nil, "stop_sequence": nil, "usage": map[string]int{"input_tokens": 128, "output_tokens": 0}}})
		event(w, "content_block_start", map[string]any{"type": "content_block_start", "index": 0, "content_block": map[string]string{"type": "text", "text": ""}})
	}
	for i := 0; i < len(content); i += chunkSize {
		end := i + chunkSize
		if end > len(content) {
			end = len(content)
		}
		if anthropic {
			event(w, "content_block_delta", map[string]any{"type": "content_block_delta", "index": 0, "delta": map[string]string{"type": "text_delta", "text": content[i:end]}})
		} else {
			event(w, "", map[string]any{"id": "chatcmpl-bench", "object": "chat.completion.chunk", "created": 1, "model": req.Model, "choices": []any{map[string]any{"index": 0, "delta": map[string]string{"role": "assistant", "content": content[i:end]}, "finish_reason": nil}}})
		}
		select {
		case <-r.Context().Done():
			canceled.Add(1)
			return
		case <-time.After(5 * time.Millisecond):
		}
	}
	if anthropic {
		event(w, "content_block_stop", map[string]any{"type": "content_block_stop", "index": 0})
		event(w, "message_delta", map[string]any{"type": "message_delta", "delta": map[string]any{"stop_reason": "end_turn", "stop_sequence": nil}, "usage": map[string]int{"output_tokens": outputTokens}})
		event(w, "message_stop", map[string]string{"type": "message_stop"})
	} else {
		event(w, "", map[string]any{"id": "chatcmpl-bench", "object": "chat.completion.chunk", "created": 1, "model": req.Model, "choices": []any{map[string]any{"index": 0, "delta": map[string]any{}, "finish_reason": "stop"}}, "usage": map[string]int{"prompt_tokens": 128, "completion_tokens": outputTokens, "total_tokens": 128 + outputTokens}})
		fmt.Fprint(w, "data: [DONE]\n\n")
		w.(http.Flusher).Flush()
	}
	completed.Add(1)
}
func main() {
	addr := os.Getenv("LISTEN_ADDR")
	if addr == "" {
		addr = ":8081"
	}
	s := &http.Server{Addr: addr, Handler: http.HandlerFunc(serve), ReadHeaderTimeout: 5 * time.Second, IdleTimeout: 90 * time.Second}
	log.Fatal(s.ListenAndServe())
}
