package eval

import (
	"context"
	"fmt"
	"strings"

	tools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

// WeatherFixtureEntry is one canned get_weather answer. Location and Aliases
// match the requested place case-insensitively, either as the whole name or
// as a substring of it ("杭州市" matches "杭州").
type WeatherFixtureEntry struct {
	Location string              `json:"location"`
	Aliases  []string            `json:"aliases,omitempty"`
	Report   tools.WeatherReport `json:"report"`
}

type weatherFixtureProvider struct {
	entries []WeatherFixtureEntry
}

func (p weatherFixtureProvider) Forecast(_ context.Context, request tools.WeatherRequest) (tools.WeatherReport, error) {
	asked := strings.ToLower(strings.TrimSpace(request.Location))
	for _, entry := range p.entries {
		for _, name := range append([]string{entry.Location}, entry.Aliases...) {
			name = strings.ToLower(strings.TrimSpace(name))
			if name != "" && strings.Contains(asked, name) {
				report := entry.Report
				report.Daily = append([]tools.WeatherDay(nil), report.Daily...)
				if request.Days > 0 && len(report.Daily) > request.Days {
					report.Daily = report.Daily[:request.Days]
				}
				return report, nil
			}
		}
	}
	return tools.WeatherReport{}, fmt.Errorf("%w: %s", tools.ErrWeatherLocationNotFound, request.Location)
}
