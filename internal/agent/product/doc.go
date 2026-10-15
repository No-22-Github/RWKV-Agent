// Package product is the single assembly point for what the user's App session
// and the product evaluation (agent-eval --harness app) hand to the Runner:
// the tool directory (Tools) and the harness Options (HarnessOptions).
//
// Both callers describe the same session in the same terms and differ only in
// the backends behind it. The App passes real providers, a real clock and its
// staged workspace; the evaluation passes fixture providers, a fixed clock and
// the same kind of staged view. Because the prompt a model sees is a function
// of (tool specs, tool order, harness options, task control), keeping one
// implementation of each makes "the eval ran what the App runs" a property of
// the code instead of a promise in a document.
//
// The package must not import the api package: api converts its Config into
// the plain structs defined here.
package product
