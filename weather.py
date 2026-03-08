import requests

def get_weather_simple(city):
    """
    Упрощенная версия получения погоды
    """
    try:
        # Используем бесплатный API (может иметь ограничения)
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        current_condition = data['current_condition'][0]
        return {
            'город': city,
            'температура': current_condition['temp_C'],
            'описание': current_condition['weatherDesc'][0]['value'],
            'влажность': current_condition['humidity'],
            'ветер': current_condition['windspeedKmph']
        }
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


if __name__ == "__main__":
    # Использование
    city = input("Введите город: ")
    weather = get_weather_simple(city)

    if weather:
        print(f"\nПогода в {weather['город']}:")
        print(f"🌡️ Температура: {weather['температура']}°C")
        print(f"📝 Описание: {weather['описание']}")
        print(f"💧 Влажность: {weather['влажность']}%")
        print(f"💨 Ветер: {weather['ветер']} км/ч")
