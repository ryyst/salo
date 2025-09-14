from datetime import datetime
from config import register_runner
from utils.logging import Log
from utils.renderers import render_html, save_file
from .config import SaaConfig
from .fetch import fetch_weather_forecast
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

    # Prepare template context
    title = f"Säätiedot - {config.place.capitalize()}"
    if station_info and station_info.get("name"):
        title = f"Säätiedot - {station_info['name']}"

    context = {
        "title": title,
        "requested_location": config.place.capitalize(),
        "forecast_data": forecast_data,
        "station_info": station_info,
        "updated_timestamp": datetime.now().strftime("%d.%m.%Y klo %H:%M"),
        "forecast_hours": config.future_hours,
    }

    # Render template to file
    template_path = "saa/template.html"
    output_path = f"{config.output_dir}/index.html"

    html_content = render_html(context, template_path)
    save_file(output_path, html_content)

    Log.info(f"Weather forecast generated successfully at {output_path}")
    Log.info(f"Forecast covers {len(forecast_data)} time points over {config.future_hours} hours")
