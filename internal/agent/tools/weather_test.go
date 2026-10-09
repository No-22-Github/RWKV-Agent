package tools

import (
	"context"
	"encoding/json"
	"testing"
)

type fakeWeatherProvider struct{ got WeatherRequest }

func (p *fakeWeatherProvider) Forecast(_ context.Context, request WeatherRequest) (WeatherReport, error) {
	p.got = request
	return WeatherReport{Location: request.Location, Daily: []WeatherDay{
		{Date: "2026-10-09"}, {Date: "2026-10-10"}, {Date: "2026-10-11"}, {Date: "2026-10-12"},
	}}, nil
}

func TestGetWeatherFloorsDaysAndLabelsRows(t *testing.T) {
	provider := &fakeWeatherProvider{}
	out, err := WeatherTools(provider)[0].Execute(context.Background(), json.RawMessage(`{"location":"杭州","days":1}`))
	if err != nil {
		t.Fatal(err)
	}
	if provider.got.Days != minWeatherForecastDays {
		t.Fatalf("days = %d, want floor %d", provider.got.Days, minWeatherForecastDays)
	}
	daily := out.(WeatherReport).Daily
	want := []string{"今天 周五", "明天 周六", "后天 周日", "周一"}
	for i, label := range want {
		if daily[i].Day != label {
			t.Fatalf("day %d label = %q, want %q", i, daily[i].Day, label)
		}
	}
}

func TestGetWeatherRejectsOutOfRangeDays(t *testing.T) {
	_, err := WeatherTools(&fakeWeatherProvider{})[0].Execute(context.Background(), json.RawMessage(`{"location":"杭州","days":8}`))
	if err == nil {
		t.Fatal("days=8 accepted")
	}
}

func TestWeatherConditionTables(t *testing.T) {
	if wmoCondition(0) != "晴" || wmoCondition(95) != "雷阵雨" || wmoCondition(12345) != "未知" {
		t.Fatal("WMO table drifted")
	}
	if wwoCondition("113") != "晴" || wwoCondition("389") != "雷阵雨" || wwoCondition("x") != "未知" {
		t.Fatal("WWO table drifted")
	}
}
