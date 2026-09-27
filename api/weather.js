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
  }
}
