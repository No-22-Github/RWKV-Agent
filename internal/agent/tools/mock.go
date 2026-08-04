package tools

import (
	"context"
	_ "embed"
	"encoding/json"
	"fmt"
	"strings"
)

//go:embed mockdata/facts.json
var defaultMockFactsJSON []byte

type MockFacts struct {
	Weather map[string]WeatherFact `json:"weather"`
	Transit map[string]TransitFact `json:"transit"`
	Hours   map[string]HoursFact   `json:"hours"`
	Rates   map[string]RateFact    `json:"rates"`
}

type MockProvider struct {
	Facts       MockFacts
	Unavailable map[string]bool
}

func DefaultMockProvider() (*MockProvider, error) {
	var facts MockFacts
	if err := json.Unmarshal(defaultMockFactsJSON, &facts); err != nil {
		return nil, fmt.Errorf("decode assistant mock facts: %w", err)
	}
	return &MockProvider{Facts: facts, Unavailable: make(map[string]bool)}, nil
}

func (p *MockProvider) Weather(_ context.Context, city string) (WeatherFact, error) {
	if p == nil || p.Unavailable["weather"] {
		return WeatherFact{}, ErrProviderUnavailable
	}
	fact, ok := p.Facts.Weather[city]
	if !ok {
		return WeatherFact{}, fmt.Errorf("weather fixture not found for %q", city)
	}
	return fact, nil
}

func (p *MockProvider) NearestTransit(_ context.Context, kind string) (TransitFact, error) {
	if p == nil || p.Unavailable["nearest_transit"] {
		return TransitFact{}, ErrProviderUnavailable
	}
	fact, ok := p.Facts.Transit[strings.ToLower(kind)]
	if !ok {
		return TransitFact{}, fmt.Errorf("transit fixture not found for %q", kind)
	}
	return fact, nil
}

func (p *MockProvider) TransitHours(_ context.Context, station string) (HoursFact, error) {
	if p == nil || p.Unavailable["transit_hours"] {
		return HoursFact{}, ErrProviderUnavailable
	}
	fact, ok := p.Facts.Hours[station]
	if !ok {
		return HoursFact{}, fmt.Errorf("hours fixture not found for %q", station)
	}
	return fact, nil
}

func (p *MockProvider) FXRate(_ context.Context, from string, to string) (RateFact, error) {
	if p == nil || p.Unavailable["fx"] || p.Unavailable["fx_convert"] {
		return RateFact{}, ErrProviderUnavailable
	}
	key := strings.ToUpper(from) + "/" + strings.ToUpper(to)
	fact, ok := p.Facts.Rates[key]
	if !ok {
		return RateFact{}, fmt.Errorf("rate fixture not found for %q", key)
	}
	return fact, nil
}

var _ Provider = (*MockProvider)(nil)
