package tools

import (
	"context"
	"errors"
	"testing"
)

type Suite struct {
	NewProvider func(*testing.T) Provider
	ExactValues bool
}

func Run(t *testing.T, suite Suite) {
	t.Helper()
	if suite.NewProvider == nil {
		t.Fatal("provider contract requires NewProvider")
	}
	provider := suite.NewProvider(t)
	if provider == nil {
		t.Fatal("NewProvider returned nil")
	}
	ctx := context.Background()
	weather, err := provider.Weather(ctx, "上海")
	if err != nil {
		t.Fatalf("Weather: %v", err)
	}
	if weather.City == "" || weather.Condition == "" || weather.ObservedAt.IsZero() {
		t.Fatalf("Weather returned incomplete fields: %+v", weather)
	}
	transit, err := provider.NearestTransit(ctx, "subway")
	if err != nil {
		t.Fatalf("NearestTransit: %v", err)
	}
	if transit.Name == "" || transit.DistanceM < 0 || transit.Lines == nil {
		t.Fatalf("NearestTransit returned incomplete fields: %+v", transit)
	}
	hours, err := provider.TransitHours(ctx, transit.Name)
	if err != nil {
		t.Fatalf("TransitHours: %v", err)
	}
	if hours.Station == "" || hours.Open == "" || hours.Close == "" || hours.Weekday == "" {
		t.Fatalf("TransitHours returned incomplete fields: %+v", hours)
	}
	rate, err := provider.FXRate(ctx, "CNY", "USD")
	if err != nil {
		t.Fatalf("FXRate: %v", err)
	}
	if rate.Rate <= 0 || rate.QuotedAt.IsZero() {
		t.Fatalf("FXRate returned incomplete fields: %+v", rate)
	}
	if suite.ExactValues {
		if weather.Condition != "多云" || transit.Name != "世纪大道站" || rate.Rate != 0.14 {
			t.Fatalf("exact mock values changed: weather=%+v transit=%+v rate=%+v", weather, transit, rate)
		}
	}
	if unavailable, ok := provider.(*MockProvider); ok {
		unavailable.Unavailable["fx"] = true
		_, err = unavailable.FXRate(ctx, "CNY", "USD")
		if !errors.Is(err, ErrProviderUnavailable) {
			t.Fatalf("unavailable error = %v, want ErrProviderUnavailable", err)
		}
	}
}
