from datetime import datetime
from collections import defaultdict
from config import register_runner
from utils.logging import Log
from utils.renderers import render_html, save_file
from .config import SaaConfig
from .fetch import fetch_weather_forecast, fetch_sunrise_sunset
from .transform import parse_weather_xml


@register_runner("saa", SaaConfig, "Generate weather forecast page for Salo")
def run_saa(config: SaaConfig):
    """
    Run the weather forecast ETL pipeline.
    Fetches FMI weather data, transforms it, and renders to HTML.
    """
    Log.info(f"Starting weather forecast generation for {config.place}")

    # Fetch weather data from FMI API
    xml_data = fetch_weather_forecast(config)
    if not xml_data:
        Log.error("Failed to fetch weather data - aborting")
        return

    # Transform XML data to structured format
    weather_result = parse_weather_xml(xml_data)
    forecast_data = weather_result["data"]
    station_info = weather_result["station_info"]

    if not forecast_data:
        Log.error("No forecast data available - aborting")
        return

    Log.info(f"Processing {len(forecast_data)} forecast points")

    # Group forecast data by day
    forecast_by_day = defaultdict(list)
    unique_dates = set()

    for point in forecast_data:
        try:
            # Parse the raw time to get the date
            dt = datetime.fromisoformat(point["raw_time"].replace("Z", "+00:00"))
            date_key = dt.strftime("%Y-%m-%d")
            day_name = dt.strftime("%A")  # Full day name
            date_display = dt.strftime("%d.%m.")

            point["date_key"] = date_key
            point["day_name"] = day_name
            point["date_display"] = date_display

            forecast_by_day[date_key].append(point)
            unique_dates.add(date_key)
        except Exception as e:
            Log.warning(f"Failed to parse date for point: {e}")
            continue

    # Sort days chronologically
    sorted_days = sorted(unique_dates)

    # Get sunrise/sunset for each unique day
    sunrise_sunset_data = {}
    for date_str in sorted_days:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            solar_data = fetch_sunrise_sunset(config.place, date_obj)
            if solar_data:
                sunrise_sunset_data[date_str] = solar_data
        except Exception as e:
            Log.warning(f"Failed to get sunrise/sunset for {date_str}: {e}")

    # Organize forecast by day with additional info
    daily_forecasts = []
    for date_key in sorted_days:
        day_points = forecast_by_day[date_key]
        if day_points:
            solar_info = sunrise_sunset_data.get(date_key, {})
            daily_forecasts.append(
                {
                    "date": date_key,
                    "day_name": day_points[0]["day_name"],
                    "date_display": day_points[0]["date_display"],
                    "points": day_points,
                    "sunrise": solar_info.get("sunrise"),
                    "sunset": solar_info.get("sunset"),
                    "day_length": solar_info.get("day_length_formatted"),
                }
            )

    # Prepare template context
    title = f"Säätiedot - {config.place.capitalize()}"
    if station_info and station_info.get("name"):
        title = f"Säätiedot - {station_info['name']}"

    context = {
        "title": title,
        "requested_location": config.place.capitalize(),
        "forecast_data": forecast_data,  # Keep original for compatibility
        "daily_forecasts": daily_forecasts,  # New organized data
        "station_info": station_info,
        "updated_timestamp": datetime.now().strftime("%d.%m.%Y klo %H:%M"),
        "forecast_hours": config.future_hours,
        "total_days": len(daily_forecasts),
    }

    # Render template to file
    template_path = "saa/template.html"
    output_path = f"{config.output_dir}/index.html"

    html_content = render_html(context, template_path)
    save_file(output_path, html_content)

    Log.info(f"Weather forecast generated successfully at {output_path}")
    Log.info(f"Forecast covers {len(forecast_data)} time points over {config.future_hours} hours")
