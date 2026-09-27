<<<<<<< HEAD
// Vercel Serverless Function: Open-Meteo weather proxy
// No API key is required for Open-Meteo's non-commercial API.
// Keeping the request behind /api/weather also gives us one place to add
// caching/rate limiting later if the prototype becomes public.

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

function num(v, fallback = 0) {
  return Number.isFinite(Number(v)) ? Number(v) : fallback;
}

export default async function handler(req, res) {
  try {
    const url = new URL(req.url, `https://${req.headers.host || "localhost"}`);
    const lat = Number(url.searchParams.get("lat"));
    const lon = Number(url.searchParams.get("lon"));

    if (!Number.isFinite(lat) || !Number.isFinite(lon) ||
        lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      return res.status(400).json({ error: "Valid lat and lon are required." });
    }

    const apiUrl = new URL("https://api.open-meteo.com/v1/forecast");
    apiUrl.searchParams.set("latitude", String(lat));
    apiUrl.searchParams.set("longitude", String(lon));
    apiUrl.searchParams.set(
      "current",
      "temperature_2m,relative_humidity_2m,precipitation,rain,showers,snowfall,weather_code"
    );
    apiUrl.searchParams.set("hourly", "precipitation");
    apiUrl.searchParams.set("past_hours", "3");
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

    const precip3h = precipSeries.reduce((sum, value) => sum + num(value), 0);
    const currentPrecip = num(current.precipitation);
    const phrase = WEATHER_CODE_PHRASES[current.weather_code] || "Unknown conditions";

    return res.status(200).json({
      tempC: num(current.temperature_2m, null),
      humidity: num(current.relative_humidity_2m, null),
      precip24h: precip3h,
      precip3h,
      phrase,
      alert: null,
      fetchedAt: new Date().toISOString(),
      source: "Open-Meteo",
      weatherCode: current.weather_code ?? null,
      currentPrecipitation: currentPrecip,
      timezone: data.timezone || null
    });
  } catch (error) {
    console.error(error);
    return res.status(500).json({ error: "Weather service unavailable." });
=======
export default async function handler(req, res) {
  const { lat, lon } = req.query;
  const apiKey = process.env.ACCUWEATHER_API_KEY;

  if (!apiKey) {
    return res.status(500).json({ error: "ACCUWEATHER_API_KEY is not configured on Vercel." });
  }

  const latitude = Number(lat);
  const longitude = Number(lon);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    return res.status(400).json({ error: "lat and lon are required numeric parameters." });
  }

  try {
    const headers = {
      Authorization: `Bearer ${apiKey}`,
      Accept: "application/json",
      "Accept-Encoding": "gzip,deflate"
    };

    const locationUrl = new URL("https://dataservice.accuweather.com/locations/v1/cities/geoposition/search");
    locationUrl.searchParams.set("q", `${latitude},${longitude}`);
    locationUrl.searchParams.set("language", "en-us");
    locationUrl.searchParams.set("details", "false");

    const locationRes = await fetch(locationUrl, { headers });
    if (!locationRes.ok) {
      const text = await locationRes.text();
      return res.status(locationRes.status).json({ error: `AccuWeather location lookup failed (${locationRes.status})`, details: text.slice(0, 500) });
    }
    const location = await locationRes.json();
    const locationKey = location?.Key;
    if (!locationKey) {
      return res.status(404).json({ error: "AccuWeather returned no location key." });
    }

    const currentUrl = new URL(`https://dataservice.accuweather.com/currentconditions/v1/${encodeURIComponent(locationKey)}`);
    currentUrl.searchParams.set("language", "en-us");
    currentUrl.searchParams.set("details", "true");

    const currentRes = await fetch(currentUrl, { headers });
    if (!currentRes.ok) {
      const text = await currentRes.text();
      return res.status(currentRes.status).json({ error: `AccuWeather current conditions failed (${currentRes.status})`, details: text.slice(0, 500) });
    }
    const data = await currentRes.json();
    const c = data?.[0];
    if (!c) return res.status(502).json({ error: "AccuWeather returned no current conditions." });

    const json = {
      tempC: c.Temperature?.Metric?.Value ?? null,
      humidity: c.RelativeHumidity ?? null,
      precip3h: c.PrecipitationSummary?.Past3Hours?.Metric?.Value ?? 0,
      precip24h: c.PrecipitationSummary?.Past24Hours?.Metric?.Value ?? 0,
      phrase: c.WeatherText ?? "Unknown",
      alert: c.HasPrecipitation ? (c.PrecipitationType || "Precipitation") : null
    };

    res.setHeader("Cache-Control", "s-maxage=300, stale-while-revalidate=600");
    return res.status(200).json(json);
  } catch (error) {
    console.error(error);
    return res.status(500).json({ error: "Weather service request failed." });
>>>>>>> 62cd7e2e23b56d71483d7086cca9b91cda064602
  }
}
