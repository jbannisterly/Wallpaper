import openmeteo_requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 50,
	"longitude": 0,
	"minutely_15": ["is_day", "rain", "weather_code"],
	"forecast_days": 1,
	"forecast_minutely_15": 96,
}

client = openmeteo_requests.Client()

responses = client.weather_api(url, params = params)
response = responses[0]

print(response.Minutely15().Variables(2).ValuesAsNumpy())