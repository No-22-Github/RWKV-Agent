//go:build darwin

package netproxy

import (
	"bufio"
	"bytes"
	"fmt"
	"net"
	"net/http"
	"net/url"
	"os/exec"
	"strconv"
	"strings"
)

type proxySettings struct {
	httpURL                *url.URL
	httpsURL               *url.URL
	socksURL               *url.URL
	exceptions             []string
	excludeSimpleHostnames bool
}

func loadSystemProxy() (func(*http.Request) (*url.URL, error), error) {
	output, err := exec.Command("/usr/sbin/scutil", "--proxy").Output()
	if err != nil {
		return nil, err
	}
	settings, err := parseProxySettings(output)
	if err != nil {
		return nil, err
	}
	if settings.httpURL == nil && settings.httpsURL == nil && settings.socksURL == nil {
		return nil, nil
	}
	return func(request *http.Request) (*url.URL, error) {
		if settings.bypasses(request.URL.Hostname()) {
			return nil, nil
		}
		switch strings.ToLower(request.URL.Scheme) {
		case "http":
			if settings.httpURL != nil {
				return settings.httpURL, nil
			}
		case "https":
			if settings.httpsURL != nil {
				return settings.httpsURL, nil
			}
			if settings.httpURL != nil {
				return settings.httpURL, nil
			}
		}
		if settings.socksURL != nil {
			return settings.socksURL, nil
		}
		return nil, nil
	}, nil
}

func parseProxySettings(output []byte) (proxySettings, error) {
	values := make(map[string]string)
	exceptions := make([]string, 0)
	inExceptions := false
	scanner := bufio.NewScanner(bytes.NewReader(output))
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if strings.HasPrefix(line, "ExceptionsList : <array>") {
			inExceptions = true
			continue
		}
		if inExceptions && line == "}" {
			inExceptions = false
			continue
		}
		name, value, ok := strings.Cut(line, ":")
		if !ok {
			continue
		}
		if inExceptions {
			exceptions = append(exceptions, strings.TrimSpace(value))
			continue
		}
		values[strings.TrimSpace(name)] = strings.TrimSpace(value)
	}
	if err := scanner.Err(); err != nil {
		return proxySettings{}, err
	}

	settings := proxySettings{
		exceptions:             exceptions,
		excludeSimpleHostnames: values["ExcludeSimpleHostnames"] == "1",
	}
	var err error
	if values["HTTPEnable"] == "1" {
		settings.httpURL, err = proxyURL("http", values["HTTPProxy"], values["HTTPPort"])
		if err != nil {
			return proxySettings{}, fmt.Errorf("parse HTTP proxy: %w", err)
		}
	}
	if values["HTTPSEnable"] == "1" {
		settings.httpsURL, err = proxyURL("http", values["HTTPSProxy"], values["HTTPSPort"])
		if err != nil {
			return proxySettings{}, fmt.Errorf("parse HTTPS proxy: %w", err)
		}
	}
	if values["SOCKSEnable"] == "1" {
		settings.socksURL, err = proxyURL("socks5", values["SOCKSProxy"], values["SOCKSPort"])
		if err != nil {
			return proxySettings{}, fmt.Errorf("parse SOCKS proxy: %w", err)
		}
	}
	return settings, nil
}

func (settings proxySettings) bypasses(host string) bool {
	host = strings.Trim(strings.ToLower(strings.TrimSpace(host)), "[]")
	if host == "" || host == "localhost" || strings.HasSuffix(host, ".localhost") {
		return true
	}
	if address := net.ParseIP(host); address != nil && address.IsLoopback() {
		return true
	}
	if settings.excludeSimpleHostnames && !strings.Contains(host, ".") {
		return true
	}
	for _, exception := range settings.exceptions {
		if matchesException(host, exception) {
			return true
		}
	}
	return false
}

func matchesException(host, exception string) bool {
	exception = strings.Trim(strings.ToLower(strings.TrimSpace(exception)), "[]")
	if exception == "" {
		return false
	}
	if strings.HasPrefix(exception, "*.") {
		return strings.HasSuffix(host, exception[1:])
	}
	if _, network, err := parseExceptionCIDR(exception); err == nil {
		address := net.ParseIP(host)
		return address != nil && network.Contains(address)
	}
	return host == exception
}

func parseExceptionCIDR(value string) (net.IP, *net.IPNet, error) {
	if _, network, err := net.ParseCIDR(value); err == nil {
		return network.IP, network, nil
	}
	parts := strings.SplitN(value, "/", 2)
	if len(parts) != 2 {
		return nil, nil, fmt.Errorf("invalid CIDR %q", value)
	}
	octets := strings.Split(parts[0], ".")
	for len(octets) < 4 {
		octets = append(octets, "0")
	}
	if len(octets) != 4 {
		return nil, nil, fmt.Errorf("invalid CIDR %q", value)
	}
	return net.ParseCIDR(strings.Join(octets, ".") + "/" + parts[1])
}

func proxyURL(scheme, host, portText string) (*url.URL, error) {
	host = strings.TrimSpace(host)
	portText = strings.TrimSpace(portText)
	if host == "" || portText == "" {
		return nil, fmt.Errorf("host and port are required")
	}
	port, err := strconv.Atoi(portText)
	if err != nil || port < 1 || port > 65535 {
		return nil, fmt.Errorf("invalid port %q", portText)
	}
	if _, _, splitErr := net.SplitHostPort(host); splitErr != nil {
		host = net.JoinHostPort(host, strconv.Itoa(port))
	}
	return &url.URL{Scheme: scheme, Host: host}, nil
}
