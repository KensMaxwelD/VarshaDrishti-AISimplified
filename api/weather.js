// Vercel Serverless Function: Open-Meteo weather proxy
// No API key is required for the standard Open-Meteo API.
//
// This endpoint keeps the weather request behind /api/weather,
// giving us one place to add caching or rate limiting later.

const WEATHER_CODE_PHRASES = {
  0: "Clear sky",
  1: "Mainly clear",
  2: "Partly cloudy",
  3: "Overcast",
  45: "Fog",
  48: "Depositing rime fog",
  51: "Light drizzle",
  53: "Moderate drizzle",
  55: "Dense drizzle",
  56: "Light freezing drizzle",
  57: "Dense freezing drizzle",
  61: "Slight rain",
  63: "Moderate rain",
  65: "Heavy rain",
  66: "Light freezing rain",
  67: "Heavy freezing rain",
  71: "Slight snow",
  73: "Moderate snow",
  75: "Heavy snow",
  77: "Snow grains",
  80: "Slight rain showers",
  81: "Moderate rain showers",
  82: "Violent rain showers",
  85: "Slight snow showers",
  86: "Heavy snow showers",
  95: "Thunderstorm",
  96: "Thunderstorm with slight hail",
  99: "Thunderstorm with heavy hail"
};

function num(value, fallback = 0) {
  return Number.isFinite(Number(value))
    ? Number(value)
    : fallback;
}

export default async function handler(req, res) {
  try {
    const url = new URL(
      req.url,
      `https://${req.headers.host || "localhost"}`
    );

    const lat = Number(url.searchParams.get("lat"));
    const lon = Number(url.searchParams.get("lon"));

    // Validate coordinates.
    if (
      !Number.isFinite(lat) ||
      !Number.isFinite(lon) ||
      lat < -90 ||
      lat > 90 ||
      lon < -180 ||
      lon > 180
    ) {
      return res.status(400).json({
        error: "Valid lat and lon are required."
      });
    }

    // Open-Meteo request.
    const apiUrl = new URL(
      "https://api.open-meteo.com/v1/forecast"
    );

    apiUrl.searchParams.set("latitude", String(lat));
    apiUrl.searchParams.set("longitude", String(lon));

    // Current weather conditions.
    apiUrl.searchParams.set(
      "current",
      [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "rain",
        "showers",
        "snowfall",
        "weather_code"
      ].join(",")
    );

    // Request the previous 24 hours of precipitation.
    apiUrl.searchParams.set(
      "hourly",
      "precipitation"
    );

    apiUrl.searchParams.set("past_hours", "24");
    apiUrl.searchParams.set("timezone", "auto");
    apiUrl.searchParams.set("temperature_unit", "celsius");
    apiUrl.searchParams.set("precipitation_unit", "mm");

    const response = await fetch(apiUrl);

    if (!response.ok) {
      return res.status(response.status).json({
        error: `Open-Meteo HTTP ${response.status}`
      });
    }

    const data = await response.json();

    const current = data.current || {};
    const hourly = data.hourly || {};

    const precipSeries = Array.isArray(hourly.precipitation)
      ? hourly.precipitation
      : [];

    // Total precipitation over the requested 24-hour period.
    const precip24h = precipSeries.reduce(
      (sum, value) => sum + num(value),
      0
    );

    // Last 3 hourly precipitation values.
    const last3Hours = precipSeries.slice(-3);

    const precip3h = last3Hours.reduce(
      (sum, value) => sum + num(value),
      0
    );

    const currentPrecip = num(
      current.precipitation
    );

    const weatherCode = current.weather_code ?? null;

    const phrase =
      WEATHER_CODE_PHRASES[weatherCode] ||
      "Unknown conditions";

    return res.status(200).json({
      tempC: num(current.temperature_2m, null),

      humidity: num(
        current.relative_humidity_2m,
        null
      ),

      // Correct 24-hour precipitation total.
      precip24h,

      // Correct 3-hour precipitation total.
      precip3h,

      phrase,

      // Open-Meteo does not provide the same
      // alert field as AccuWeather.
      alert: null,

      fetchedAt: new Date().toISOString(),

      source: "Open-Meteo",

      weatherCode,

      currentPrecipitation: currentPrecip,

      timezone: data.timezone || null
    });
  } catch (error) {
    console.error(error);

    return res.status(500).json({
      error: "Weather service unavailable."
    });
  }
}