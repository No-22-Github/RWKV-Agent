package tools

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// Live weather backends that need no API key. Open-Meteo resolves the place
// name through its own geocoder first (two requests); wttr.in takes the place
// name directly but only forecasts three days and answers in English names.
const (
	WeatherBackendOpenMeteo = "open-meteo"
	WeatherBackendWttr      = "wttr"

	defaultOpenMeteoGeocodeEndpoint  = "https://geocoding-api.open-meteo.com/v1/search"
	defaultOpenMeteoForecastEndpoint = "https://api.open-meteo.com/v1/forecast"
	defaultWttrEndpoint              = "https://wttr.in"
	maxWeatherForecastDays           = 7
	// minWeatherForecastDays is the floor on returned days. Live probes
	// (2026-10-09) showed the model passing days=1 for "明天" and days=2 for
	// "后天", then reading today's row as the asked-for day; always covering
	// today..后天 removes that off-by-one at the cost of two short rows.
	minWeatherForecastDays = 3
)

type WeatherRequest struct {
	Location string
	Days     int
}

type WeatherDay struct {
	Day        string `json:"day"`
	Date       string `json:"date"`
	Condition  string `json:"condition"`
	TempC      string `json:"temp_c"`
	RainChance string `json:"rain_chance,omitempty"`
}

type WeatherReport struct {
	Location   string       `json:"location"`
	ObservedAt string       `json:"observed_at,omitempty"`
	Current    string       `json:"current"`
	Daily      []WeatherDay `json:"daily"`
	Source     string       `json:"source"`
}

type WeatherProvider interface {
	Forecast(context.Context, WeatherRequest) (WeatherReport, error)
}

// ErrWeatherLocationNotFound marks a place name the backend cannot resolve;
// the tool reports it as an ordinary failure so the model can retry with a
// different spelling instead of treating the provider as down.
var ErrWeatherLocationNotFound = errors.New("location not found")

func NewWeatherProvider(backend string) (WeatherProvider, error) {
	client := &http.Client{Timeout: 20 * time.Second}
	switch strings.TrimSpace(backend) {
	case WeatherBackendOpenMeteo:
		return &OpenMeteoProvider{
			geocodeEndpoint: defaultOpenMeteoGeocodeEndpoint, forecastEndpoint: defaultOpenMeteoForecastEndpoint,
			httpClient: client, retry: defaultProviderRetryPolicy(), gate: newProviderRequestGate(),
		}, nil
	case WeatherBackendWttr:
		return &WttrProvider{
			endpoint: defaultWttrEndpoint, httpClient: client,
			retry: defaultProviderRetryPolicy(), gate: newProviderRequestGate(),
		}, nil
	}
	return nil, fmt.Errorf("unknown weather backend %q; use %s or %s", backend, WeatherBackendOpenMeteo, WeatherBackendWttr)
}

func WeatherTools(provider WeatherProvider) []agent.Tool {
	return []agent.Tool{&getWeatherTool{provider: provider}}
}

type getWeatherTool struct{ provider WeatherProvider }

func (*getWeatherTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "get_weather",
		Description: "Get the current weather and the daily forecast (today, tomorrow, ...) for a city. Pass the city name, not a landmark.",
		Arguments:   `{"location":"city name","days":"integer 1..7"}`,
		Parameters:  json.RawMessage(`{"type":"object","properties":{"location":{"type":"string","minLength":1,"maxLength":100},"days":{"type":["integer","null"],"minimum":1,"maximum":7}},"required":["location","days"],"additionalProperties":false}`),
		Strict:      true,
		Permission:  agent.PermissionNetworkRead,
	}
}

func (t *getWeatherTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Location string `json:"location"`
		Days     int    `json:"days"`
	}
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	args.Location = strings.TrimSpace(args.Location)
	if args.Location == "" {
		return nil, invalidArguments("location is required")
	}
	if args.Days == 0 {
		args.Days = 3
	}
	if args.Days < 1 || args.Days > maxWeatherForecastDays {
		return nil, invalidArguments("days must be between 1 and %d", maxWeatherForecastDays)
	}
	if t.provider == nil {
		return nil, agent.ErrProviderUnavailable
	}
	report, err := t.provider.Forecast(ctx, WeatherRequest{Location: args.Location, Days: max(args.Days, minWeatherForecastDays)})
	if err != nil {
		return nil, err
	}
	labelWeatherDays(report.Daily)
	return report, nil
}

// labelWeatherDays names each row relative to the first one, which both
// backends report as the location's local today.
func labelWeatherDays(days []WeatherDay) {
	relative := []string{"今天", "明天", "后天"}
	weekdays := []string{"周日", "周一", "周二", "周三", "周四", "周五", "周六"}
	for i := range days {
		date, err := time.Parse("2006-01-02", days[i].Date)
		if err != nil {
			continue
		}
		label := weekdays[date.Weekday()]
		if i < len(relative) {
			label = relative[i] + " " + label
		}
		days[i].Day = label
	}
}

type OpenMeteoProvider struct {
	geocodeEndpoint  string
	forecastEndpoint string
	httpClient       *http.Client
	retry            providerRetryPolicy
	gate             *providerRequestGate
}

func (p *OpenMeteoProvider) Forecast(ctx context.Context, request WeatherRequest) (WeatherReport, error) {
	geocode, _ := url.Parse(p.geocodeEndpoint)
	query := geocode.Query()
	query.Set("name", request.Location)
	query.Set("count", "1")
	query.Set("language", "zh")
	geocode.RawQuery = query.Encode()
	var places struct {
		Results []struct {
			Name      string  `json:"name"`
			Latitude  float64 `json:"latitude"`
			Longitude float64 `json:"longitude"`
			Country   string  `json:"country"`
			Admin1    string  `json:"admin1"`
		} `json:"results"`
	}
	if err := p.getJSON(ctx, "Open-Meteo geocoding", geocode.String(), &places); err != nil {
		return WeatherReport{}, err
	}
	if len(places.Results) == 0 {
		return WeatherReport{}, fmt.Errorf("%w: %q", ErrWeatherLocationNotFound, request.Location)
	}
	place := places.Results[0]

	forecast, _ := url.Parse(p.forecastEndpoint)
	query = forecast.Query()
	query.Set("latitude", strconv.FormatFloat(place.Latitude, 'f', 4, 64))
	query.Set("longitude", strconv.FormatFloat(place.Longitude, 'f', 4, 64))
	query.Set("current", "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m")
	query.Set("daily", "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max")
	query.Set("timezone", "auto")
	query.Set("forecast_days", strconv.Itoa(request.Days))
	forecast.RawQuery = query.Encode()
	var payload struct {
		Current struct {
			Time        string  `json:"time"`
			Temperature float64 `json:"temperature_2m"`
			FeelsLike   float64 `json:"apparent_temperature"`
			Humidity    float64 `json:"relative_humidity_2m"`
			Code        int     `json:"weather_code"`
			Wind        float64 `json:"wind_speed_10m"`
		} `json:"current"`
		Daily struct {
			Time       []string   `json:"time"`
			Code       []int      `json:"weather_code"`
			Max        []float64  `json:"temperature_2m_max"`
			Min        []float64  `json:"temperature_2m_min"`
			RainChance []*float64 `json:"precipitation_probability_max"`
		} `json:"daily"`
	}
	if err := p.getJSON(ctx, "Open-Meteo forecast", forecast.String(), &payload); err != nil {
		return WeatherReport{}, err
	}
	current := payload.Current
	report := WeatherReport{
		Location:   joinNonEmpty("，", place.Name, place.Admin1, place.Country),
		ObservedAt: current.Time,
		Current: fmt.Sprintf("%s %.0f°C 体感 %.0f°C 湿度 %.0f%% 风速 %.0f km/h",
			wmoCondition(current.Code), current.Temperature, current.FeelsLike, current.Humidity, current.Wind),
		Source: "open-meteo.com",
	}
	daily := payload.Daily
	for i := range daily.Time {
		if i >= len(daily.Code) || i >= len(daily.Max) || i >= len(daily.Min) {
			break
		}
		day := WeatherDay{
			Date:      daily.Time[i],
			Condition: wmoCondition(daily.Code[i]),
			TempC:     fmt.Sprintf("%.0f~%.0f", daily.Min[i], daily.Max[i]),
		}
		if i < len(daily.RainChance) && daily.RainChance[i] != nil {
			day.RainChance = fmt.Sprintf("%.0f%%", *daily.RainChance[i])
		}
		report.Daily = append(report.Daily, day)
	}
	return report, nil
}

func (p *OpenMeteoProvider) getJSON(ctx context.Context, label string, endpoint string, target any) error {
	return getProviderJSON(ctx, p.httpClient, p.retry, p.gate, label, endpoint, target)
}

type WttrProvider struct {
	endpoint   string
	httpClient *http.Client
	retry      providerRetryPolicy
	gate       *providerRequestGate
}

func (p *WttrProvider) Forecast(ctx context.Context, request WeatherRequest) (WeatherReport, error) {
	endpoint := strings.TrimRight(p.endpoint, "/") + "/" + url.PathEscape(request.Location) + "?format=j1"
	type value []struct {
		Value string `json:"value"`
	}
	var payload struct {
		CurrentCondition []struct {
			TempC      string `json:"temp_C"`
			FeelsLikeC string `json:"FeelsLikeC"`
			Humidity   string `json:"humidity"`
			WindKmph   string `json:"windspeedKmph"`
			Code       string `json:"weatherCode"`
		} `json:"current_condition"`
		NearestArea []struct {
			AreaName value `json:"areaName"`
			Region   value `json:"region"`
			Country  value `json:"country"`
		} `json:"nearest_area"`
		Weather []struct {
			Date    string `json:"date"`
			MaxTemp string `json:"maxtempC"`
			MinTemp string `json:"mintempC"`
			Hourly  []struct {
				Code       string `json:"weatherCode"`
				RainChance string `json:"chanceofrain"`
			} `json:"hourly"`
		} `json:"weather"`
	}
	if err := getProviderJSON(ctx, p.httpClient, p.retry, p.gate, "wttr.in", endpoint, &payload); err != nil {
		return WeatherReport{}, err
	}
	if len(payload.CurrentCondition) == 0 {
		return WeatherReport{}, fmt.Errorf("%w: %q", ErrWeatherLocationNotFound, request.Location)
	}
	first := func(v value) string {
		if len(v) == 0 {
			return ""
		}
		return v[0].Value
	}
	current := payload.CurrentCondition[0]
	report := WeatherReport{
		Location: request.Location,
		Current: fmt.Sprintf("%s %s°C 体感 %s°C 湿度 %s%% 风速 %s km/h",
			wwoCondition(current.Code), current.TempC, current.FeelsLikeC, current.Humidity, current.WindKmph),
		Source: "wttr.in",
	}
	if len(payload.NearestArea) > 0 {
		area := payload.NearestArea[0]
		report.Location = joinNonEmpty("，", request.Location, first(area.Region), first(area.Country))
	}
	for i, day := range payload.Weather {
		if i >= request.Days {
			break
		}
		entry := WeatherDay{Date: day.Date, TempC: day.MinTemp + "~" + day.MaxTemp}
		// Daily rows carry no condition of their own; midday (index 4 of the
		// eight three-hour slots) is the representative one, and the rain
		// chance is the day's maximum.
		if len(day.Hourly) > 0 {
			entry.Condition = wwoCondition(day.Hourly[min(4, len(day.Hourly)-1)].Code)
			best := -1
			for _, hour := range day.Hourly {
				if chance, err := strconv.Atoi(hour.RainChance); err == nil && chance > best {
					best = chance
				}
			}
			if best >= 0 {
				entry.RainChance = strconv.Itoa(best) + "%"
			}
		}
		report.Daily = append(report.Daily, entry)
	}
	return report, nil
}

func getProviderJSON(
	ctx context.Context, client *http.Client, policy providerRetryPolicy, gate *providerRequestGate,
	label string, endpoint string, target any,
) error {
	response, attempts, err := doProviderRequest(ctx, "get_weather", client, policy, gate, func() (*http.Request, error) {
		request, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
		if err != nil {
			return nil, fmt.Errorf("build %s request: %w", label, err)
		}
		request.Header.Set("Accept", "application/json")
		// wttr.in serves a terminal-art page to curl-like agents; a plain
		// identifying UA with Accept JSON keeps both backends on their API path.
		request.Header.Set("User-Agent", "RWKV-Agent/1.0")
		return request, nil
	})
	if err != nil {
		var exhausted providerRetryExhaustedError
		if errors.As(err, &exhausted) {
			return providerUnavailableError{message: fmt.Sprintf(
				"%s request failed after %d attempts: %v", label, exhausted.attempts, exhausted.cause,
			)}
		}
		return fmt.Errorf("%s request: %w", label, err)
	}
	defer response.Body.Close()
	if response.StatusCode == http.StatusNotFound {
		return ErrWeatherLocationNotFound
	}
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return providerHTTPError(label, response.Status, attempts)
	}
	if err := decodeLimitedJSON(response.Body, target); err != nil {
		return fmt.Errorf("decode %s response: %w", label, err)
	}
	return nil
}

func joinNonEmpty(separator string, parts ...string) string {
	kept := make([]string, 0, len(parts))
	for _, part := range parts {
		part = strings.TrimSpace(part)
		if part != "" && (len(kept) == 0 || kept[len(kept)-1] != part) {
			kept = append(kept, part)
		}
	}
	return strings.Join(kept, separator)
}

// wmoCondition maps WMO weather interpretation codes (Open-Meteo).
func wmoCondition(code int) string {
	switch code {
	case 0:
		return "晴"
	case 1:
		return "大部晴朗"
	case 2:
		return "多云"
	case 3:
		return "阴"
	case 45, 48:
		return "雾"
	case 51, 53, 55:
		return "毛毛雨"
	case 56, 57:
		return "冻毛毛雨"
	case 61:
		return "小雨"
	case 63:
		return "中雨"
	case 65:
		return "大雨"
	case 66, 67:
		return "冻雨"
	case 71:
		return "小雪"
	case 73:
		return "中雪"
	case 75:
		return "大雪"
	case 77:
		return "米雪"
	case 80, 81:
		return "阵雨"
	case 82:
		return "强阵雨"
	case 85, 86:
		return "阵雪"
	case 95:
		return "雷阵雨"
	case 96, 99:
		return "雷阵雨伴冰雹"
	}
	return "未知"
}

// wwoCondition maps WorldWeatherOnline condition codes (wttr.in).
func wwoCondition(code string) string {
	switch code {
	case "113":
		return "晴"
	case "116":
		return "多云"
	case "119":
		return "阴"
	case "122":
		return "阴天"
	case "143", "248", "260":
		return "雾"
	case "149":
		return "霾"
	case "176", "263", "266", "293", "296", "353":
		return "小雨"
	case "299", "302", "356":
		return "中雨"
	case "305", "308", "359":
		return "大雨"
	case "179", "323", "326", "368":
		return "小雪"
	case "227", "329", "332", "371":
		return "中雪"
	case "230", "335", "338", "395":
		return "大雪"
	case "182", "185", "281", "284", "311", "314", "317", "320", "350", "362", "365", "374", "377":
		return "雨夹雪"
	case "200", "386", "389", "392":
		return "雷阵雨"
	}
	return "未知"
}
