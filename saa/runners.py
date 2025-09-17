from datetime import datetime
from config import register_runner
from utils.logging import Log
from utils.renderers import render_html, save_file
from .config import SaaConfig
from .fetch import fetch_weather_forecast, fetch_sunrise_sunset
from .transform import (
    parse_weather_xml,
    group_forecast_by_day,
    add_solar_data_to_forecast,
    prepare_weather_context,
)


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
    daily_forecasts = group_forecast_by_day(forecast_data)

    # Fetch sunrise/sunset data for each day
    sunrise_sunset_data = _fetch_solar_data_for_days(daily_forecasts)

    # Add solar data to daily forecasts
    daily_forecasts = add_solar_data_to_forecast(daily_forecasts, sunrise_sunset_data)

    # Calculate future hours for context
    from .api import FMIWeatherAPI

    api = FMIWeatherAPI()
    future_hours = api.calculate_future_hours(config.future_days)

    # Prepare and render template
    context = prepare_weather_context(future_hours, forecast_data, daily_forecasts, station_info)
    _render_weather_template(context, config)

    Log.info(f"Weather forecast generated successfully at {config.output_dir}/index.html")
    Log.info(
        f"Forecast covers {len(forecast_data)} time points over {future_hours} hours ({config.future_days} days)"
    )


def _fetch_solar_data_for_days(daily_forecasts):
    """Fetch sunrise/sunset data for all forecast days."""
    if not daily_forecasts:
        return {}

    sunrise_sunset_data = {}

    for day_forecast in daily_forecasts:
        date_str = day_forecast["date"]
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            solar_data = fetch_sunrise_sunset(date_obj)
            if solar_data:
                sunrise_sunset_data[date_str] = solar_data
        except Exception as e:
            Log.warning(f"Failed to get sunrise/sunset for {date_str}: {e}")

    return sunrise_sunset_data


def _render_weather_template(context, config):
    """Render and save the weather template."""
    template_path = "saa/template.html"
    output_path = f"{config.output_dir}/index.html"

    html_content = render_html(context, template_path)
    save_file(output_path, html_content)
