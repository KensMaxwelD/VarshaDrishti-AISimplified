# VarshaDrishti AI

## AI-Assisted Flood & Weather Risk Monitoring Dashboard

VarshaDrishti AI is a prototype dashboard designed to monitor weather conditions across selected regions of India and present them in a simple, visual interface.

The project combines live weather data with a rule-based risk assessment system to help visualize areas that may require closer attention during periods of heavy rainfall or adverse weather.

## Features

- 🌦️ Live weather data
- 🌧️ Rainfall and precipitation monitoring
- 🌡️ Temperature and humidity information
- ⚠️ Weather-based risk assessment
- 🗺️ Interactive regional weather map
- 📍 Monitoring of multiple locations across India
- 🔄 Manual weather-data refresh
- 📊 Dashboard-style visualization
- ☁️ Current weather condition descriptions

## Monitored Locations

The prototype currently includes locations such as:

- Alappuzha / Kuttanad, Kerala
- Majuli, Assam
- Darbhanga, Bihar
- Mumbai, Maharashtra
- Chennai, Tamil Nadu
- Srinagar, Jammu & Kashmir

Additional weather points are displayed on the map for regional visualization.

## How It Works

VarshaDrishti AI uses geographical coordinates for each monitored location and retrieves current weather information from the Open-Meteo Weather API.

The application requests weather variables including:

- Temperature
- Relative humidity
- Precipitation
- Rain
- Showers
- Snowfall
- Weather condition code

Open-Meteo's current-weather data is based on frequently updated weather-model data, and its API supports multiple weather variables and geographical coordinates.

The retrieved information is then displayed in the dashboard and passed through the prototype's risk-assessment logic.

### Risk Assessment

The current prototype uses client-side rules to classify weather conditions into different risk levels.

The risk calculation is intended for **demonstration and visualization purposes**. It should not be treated as an official flood-warning or emergency-response system.

## Technology

### Frontend

- HTML
- CSS
- JavaScript
- SVG-based map visualization

### Weather Data

- Open-Meteo Weather API

Open-Meteo provides a JSON-based weather API and does not require an API key for its standard public usage.

### Deployment

The project can be deployed using Vercel.

The frontend communicates with a small serverless endpoint:

```text
/api/weather
```

This endpoint retrieves weather data from Open-Meteo and returns the relevant information to the dashboard.

## Project Structure

```text
VarshaDrishti-AISimplified/
│
├── index.html
├── api/
│   └── weather.js
├── .env.example
├── .gitignore
└── README.md
```

## Running Locally

Clone the repository:

```bash
git clone https://github.com/KensMaxwelD/VarshaDrishti-AISimplified.git
```

Enter the project directory:

```bash
cd VarshaDrishti-AISimplified
```

Then open `index.html` in a browser, or run the project through a local development server.

No Open-Meteo API key is required for the standard API configuration used by this project.

## Deployment

The project is structured so that it can be deployed to Vercel.

After connecting the GitHub repository to Vercel, the `/api/weather` serverless function handles weather-data requests.

No weather API secret needs to be placed inside the frontend code.

## Important Note

VarshaDrishti AI is currently a **prototype**.

Its risk indicators are intended to demonstrate how weather information could be presented and analyzed. They are not a replacement for official weather warnings, government disaster-management systems, or emergency services.

Weather conditions can change rapidly, and users should rely on official authorities for real-world safety decisions.

## Data Attribution

Weather data is provided by **Open-Meteo**.

Open-Meteo's data is provided under its applicable licensing terms, including CC BY 4.0 for the relevant open data.

## Future Improvements

Potential future versions could include:

- More Indian locations
- Historical rainfall analysis
- 24-hour and 7-day rainfall trends
- Improved flood-risk calculations
- River and water-level data
- Satellite imagery
- Weather alerts
- Automated notifications
- More detailed geographic maps
- Machine-learning-based risk prediction
- Integration with official disaster-management datasets

## Project Goal

The goal of VarshaDrishti AI is to explore how real-time weather information can be transformed into a clear and accessible dashboard for understanding rainfall and potential weather-related risks.

---

**VarshaDrishti AI — Prototype Console**

Built as an experimental weather and flood-risk visualization project.