import pygame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import math
import random
import threading
import time
from weather import get_weather_simple
import os
import io

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Глобальные переменные
current_weather = 'christmas'
current_city = 'Могилев'
current_temperature = '0'
current_humidity = '0'
current_wind = '0'
update_tree = False
stop_program = False
current_music = None

# Размеры окна
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("🎄 Новогодняя Ёлка с Погодой 🎄")

WEATHER_TRANSLATIONS = {
    'clear': 'ясно',
    'sunny': 'солнечно', 
    'clouds': 'облачно',
    'partly cloudy': 'переменная облачность',
    'rain': 'дождь',
    'drizzle': 'морось',
    'snow': 'снег',
    'thunderstorm': 'гроза',
    'mist': 'туман',
    'fog': 'туман',
    'haze': 'дымка',
    'christmas': 'рождество'
}

# Цвета фона для разных погодных условий
WEATHER_BG_COLORS = {
    'clear': (135, 206, 235),       # солнечно - голубое небо
    'sunny': (135, 206, 235),       # солнечно
    'clouds': (140, 160, 190),      # облачно
    'partly cloudy': (140, 160, 190), # переменная облачность
    'rain': (70, 85, 120),          # дождь
    'drizzle': (70, 85, 120),       # морось
    'snow': (180, 200, 230),        # снег
    'thunderstorm': (50, 50, 80),   # гроза
    'mist': (160, 160, 160),        # туман
    'fog': (160, 160, 160),         # туман
    'haze': (180, 180, 180),        # дымка
    'christmas': (10, 15, 40)       # рождество
}

# Цвета ёлки для разных погодных условий
TREE_COLORS = {
    'clear': '#32B432',      # зеленая
    'sunny': '#32B432',      # зеленая
    'clouds': '#32B432',     # зеленая
    'partly cloudy': '#32B432', # зеленая
    'rain': '#327832',       # темно-зеленая (дождь)
    'drizzle': '#327832',    # темно-зеленая
    'snow': '#C8DCF0',       # снежно-голубая (снег)
    'thunderstorm': '#32B432', # зеленая
    'mist': '#32B432',       # зеленая
    'fog': '#32B432',        # зеленая
    'haze': '#32B432',       # зеленая
    'christmas': '#32B432'   # зеленая
}

# Шрифты
font_large = pygame.font.SysFont('Arial', 28, bold=True)
font_medium = pygame.font.SysFont('Arial', 24, bold=True)

# Переменные для эффектов погоды
snowflakes = []
raindrops = []
clouds = []
lightning_timer = 0
lightning_active = False
lightning_alpha = 0
lightning_flash = 0
lightning_flash_duration = 0

# Функция для воспроизведения музыки
def play_weather_music(weather_type):
    global current_music
    
    if current_music:
        pygame.mixer.music.stop()
    
    weather_type = weather_type.strip().lower()
    
    # Соответствие погоды музыкальным файлам
    music_mapping = {
        'clear': "sunny_christmas.mp3",
        'sunny': "sunny_christmas.mp3", 
        'clouds': "cloudy_christmas.mp3",
        'partly cloudy': "cloudy_christmas.mp3",
        'rain': "rainy_christmas.mp3",
        'drizzle': "rainy_christmas.mp3",
        'snow': "snowy_christmas.mp3",
        'thunderstorm': "rainy_christmas.mp3",
        'mist': "cloudy_christmas.mp3",
        'fog': "cloudy_christmas.mp3",
        'haze': "cloudy_christmas.mp3",
        'christmas': "christmas.mp3"
    }
    
    music_file = os.path.join("music", music_mapping.get(weather_type, "christmas.mp3"))
    
    if os.path.exists(music_file):
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)
            current_music = music_file
            print(f"Воспроизводится: {music_file}")
        except Exception as e:
            print(f"Ошибка воспроизведения музыки: {e}")
    else:
        print(f"Музыкальный файл не найден: {music_file}")

# Функция создания снежинок (правильная реализация)
def create_snowflakes(count):
    global snowflakes
    snowflakes = []
    for _ in range(count):
        snowflakes.append({
            'x': random.randint(-400, 400),
            'y': random.randint(-400, 400),
            'z': random.randint(0, 100),
            'size': random.randint(2, 4)
        })

# Функция создания капель дождя (правильная реализация)
def create_raindrops(count):
    global raindrops
    raindrops = []
    for _ in range(count):
        raindrops.append({
            'x': random.randint(-400, 400),
            'y': random.randint(-400, 400),
            'z': random.randint(0, 200),
            'length': random.randint(8, 15)
        })

# Функция создания облаков (теперь спавнятся справа и летят налево)
def create_clouds(count, cloud_type="normal"):
    global clouds
    clouds = []
    
    if cloud_type == "partly":
        count = max(3, count // 2)  # Меньше облаков для переменной облачности
    
    for _ in range(count):
        size = random.randint(100, 200)
        if cloud_type == "partly":
            size = random.randint(70, 150)  # Меньшие облака для переменной облачности
            
        clouds.append({
            'x': WIDTH + random.randint(50, 200),  # Спавним справа за пределами экрана
            'y': random.randint(50, HEIGHT // 3),
            'speed': random.uniform(1.5, 3.0),  # Увеличена скорость движения
            'size': size,
            'density': random.uniform(0.6, 0.9)
        })

# Функция обновления эффектов погоды
def update_weather_effects():
    global snowflakes, raindrops, clouds, lightning_timer, lightning_active, lightning_alpha, lightning_flash, lightning_flash_duration
    
    weather_key = current_weather.strip().lower()
    
    # Обновляем снежинки (правильная реализация)
    if weather_key in ['snow']:
        for snowflake in snowflakes:
            # Снежинки остаются на своих местах, они пересоздаются каждый кадр
            pass
    
    # Обновляем капли дождя (правильная реализация)
    if weather_key in ['rain', 'drizzle', 'thunderstorm']:
        for raindrop in raindrops:
            # Капли остаются на своих местах, они пересоздаются каждый кадр
            pass
    
    # Обновляем облака (движение справа налево)
    if weather_key in ['clouds', 'partly cloudy']:
        for cloud in clouds:
            cloud['x'] -= cloud['speed']  # Движение влево
            if cloud['x'] < -300:
                cloud['x'] = WIDTH + random.randint(50, 200)
                cloud['y'] = random.randint(50, HEIGHT // 3)
    
    # Обновляем молнию и вспышку
    if weather_key in ['thunderstorm']:
        if lightning_flash_duration > 0:
            lightning_flash_duration -= 1
            if lightning_flash_duration <= 0:
                lightning_flash = 0
        
        if lightning_active:
            lightning_alpha -= 15
            if lightning_alpha <= 0:
                lightning_active = False
                lightning_timer = random.randint(90, 240)  # 1.5-4 секунды (90-240 кадров при 60 FPS)
        else:
            lightning_timer -= 1
            if lightning_timer <= 0:
                lightning_active = True
                lightning_alpha = 200
                lightning_flash = 255
                lightning_flash_duration = 5  # Вспышка на 5 кадров

# Функция отрисовки эффектов погоды
def draw_weather_effects(surface):
    weather_key = current_weather.strip().lower()
    
    # Рисуем солнце для ясной погоды (в 2 раза меньше)
    if weather_key in ['clear', 'sunny']:
        pygame.draw.circle(surface, (255, 255, 0), (WIDTH - 100, 100), 25)
        for i in range(8):
            angle = i * math.pi / 4
            start_x = WIDTH - 100 + 30 * math.cos(angle)
            start_y = 100 + 30 * math.sin(angle)
            end_x = WIDTH - 100 + 40 * math.cos(angle)
            end_y = 100 + 40 * math.sin(angle)
            pygame.draw.line(surface, (255, 255, 0), (start_x, start_y), (end_x, end_y), 3)
    
    # Рисуем облака
    if weather_key in ['clouds', 'partly cloudy']:
        for cloud in clouds:
            draw_cloud(surface, cloud['x'], cloud['y'], cloud['size'], cloud['density'])
    
    # Рисуем снег (правильная реализация)
    if weather_key in ['snow']:
        # Пересоздаем снежинки каждый кадр для случайного распределения
        create_snowflakes(20)
        for snowflake in snowflakes:
            # Преобразуем 3D координаты в 2D экранные координаты
            screen_x = WIDTH // 2 + snowflake['x'] * 0.8
            screen_y = HEIGHT // 2 - snowflake['y'] * 0.8 - snowflake['z'] * 0.5
            if 0 <= screen_x <= WIDTH and 0 <= screen_y <= HEIGHT:
                pygame.draw.circle(surface, (255, 255, 255), 
                                  (int(screen_x), int(screen_y)), 
                                  snowflake['size'])
    
    # Рисуем дождь (правильная реализация)
    if weather_key in ['rain', 'drizzle', 'thunderstorm']:
        # Пересоздаем капли каждый кадр для случайного распределения
        create_raindrops(30)
        for raindrop in raindrops:
            # Преобразуем 3D координаты в 2D экранные координаты
            screen_x = WIDTH // 2 + raindrop['x'] * 0.8
            screen_y = HEIGHT // 2 - raindrop['y'] * 0.8 - raindrop['z'] * 0.5
            
            # Рисуем вертикальную линию для капли дождя
            if 0 <= screen_x <= WIDTH and 0 <= screen_y <= HEIGHT:
                pygame.draw.line(surface, (100, 150, 255),
                                (int(screen_x), int(screen_y)),
                                (int(screen_x), int(screen_y + raindrop['length'])), 2)
    
    # Рисуем молнию
    if weather_key in ['thunderstorm'] and lightning_active:
        # Рисуем зигзаг молнии
        points = []
        start_x = random.randint(100, WIDTH - 100)
        points.append((start_x, 0))
        
        for i in range(1, 8):
            x = points[i-1][0] + random.randint(-50, 50)
            y = i * (HEIGHT // 7)
            points.append((x, y))
        
        if len(points) > 1:
            pygame.draw.lines(surface, (255, 255, 200), False, points, 3)
    
    # Рисуем вспышку молнии (белый экран)
    if lightning_flash > 0:
        flash_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash_surface.fill((255, 255, 255, lightning_flash))
        surface.blit(flash_surface, (0, 0))

# Функция рисования облака
def draw_cloud(surface, x, y, size, density):
    cloud_color = (255, 255, 255, int(200 * density))
    
    circles = [
        (x, y, size * 0.5),
        (x + size * 0.3, y - size * 0.1, size * 0.4),
        (x + size * 0.6, y, size * 0.5),
        (x + size * 0.3, y + size * 0.1, size * 0.4),
        (x - size * 0.2, y, size * 0.4)
    ]
    
    for cx, cy, radius in circles:
        pygame.draw.circle(surface, cloud_color, (int(cx), int(cy)), int(radius))

# Предварительно создаем ёлку для анимации (в 1.5 раза больше)
def create_tree_animation_frames():
    """Создаем несколько кадров анимации ёлки заранее (в 1.5 раза больше)"""
    frames = []
    for frame in range(60):
        fig = plt.figure(figsize=(12, 12), facecolor='none', dpi=100)
        ax = fig.add_subplot(111, projection="3d")
        
        ax.set_axis_off()
        ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
        ax.set_facecolor('none')
        fig.patch.set_alpha(0.0)
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        
        k = 350
        x_tree = [math.cos(i / 5 + frame / 10) * (k - i) * 0.8 for i in range(k)]
        y_tree = [math.sin(i / 5 + frame / 10) * (k - i) * 0.8 for i in range(k)]
        z_tree = [i for i in range(k)]
        
        weather_key = current_weather.strip().lower()
        if weather_key == 'snow':
            tree_color = '#C8DCF0'
        elif weather_key in ['rain', 'drizzle', 'thunderstorm']:
            tree_color = '#327832'
        else:
            tree_color = '#32B432'
        
        ax.scatter(x_tree, y_tree, z_tree, color=tree_color, marker="^", s=38, alpha=0.8)
        
        step = 4
        z_garland = [i for i in range(20, k-20, step)]
        x_garland = [math.cos(i / 5 + 2 + frame / 8) * (k - i + 15) * 0.8 for i in range(20, k-20, step)]
        y_garland = [math.sin(i / 5 + 2 + frame / 8) * (k - i + 15) * 0.8 for i in range(20, k-20, step)]
        
        garland_colors = []
        for i in range(len(z_garland)):
            if weather_key in ['rain', 'drizzle', 'thunderstorm']:
                garland_colors.append('#6496FF')
            elif weather_key == 'snow':
                garland_colors.append('#FFFAC8')
            else:
                colors = ['#FF6E6E', '#FF8C42', '#FFDA66', '#9AFF6E', '#6EBAFF', '#B46EFF']
                garland_colors.append(random.choice(colors))
        
        ax.scatter(x_garland, y_garland, z_garland, c=garland_colors, marker="o", s=53, alpha=0.9)
        ax.scatter([0], [0], [k+15], c='gold', marker="*", s=525, alpha=0.9)
        
        ax.set_xlim(-500, 500)
        ax.set_ylim(-500, 500)
        ax.set_zlim(0, k+50)
        ax.set_box_aspect([1, 1, 1])
        
        canvas = FigureCanvasAgg(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        tree_surface = pygame.image.load(buf).convert_alpha()
        
        plt.close(fig)
        frames.append(tree_surface)
    
    return frames

# Создаем анимационные кадры заранее
tree_frames = create_tree_animation_frames()

# Функция отрисовки информации о погоде
def draw_weather_info(surface):
    info_rect = pygame.Rect(430, 230, WIDTH * 0.35, 220)
    s = pygame.Surface((info_rect.width, info_rect.height), pygame.SRCALPHA)
    s.fill((0, 0, 0, 135))
    surface.blit(s, info_rect)
    pygame.draw.rect(surface, (255, 255, 255, 200), info_rect, 2, border_radius=12)
    
    weather_ru = WEATHER_TRANSLATIONS.get(current_weather.lower(), current_weather)
    
    texts = [
        f"Погода в {current_city.title()}е:",
        f"Температура: {current_temperature}°C",
        f"Погода: {weather_ru}",
        f"Влажность: {current_humidity}%",
        f"Ветер: {current_wind} км/ч"
    ]
    
    fonts = [font_large, font_medium, font_medium, font_medium, font_medium]
    
    for i, (text, font) in enumerate(zip(texts, fonts)):
        text_surface = font.render(text, True, (255, 255, 255))
        surface.blit(text_surface, (50, 50 + i * 40))

# Функция для получения реальной погоды
def weather_input_handler():
    global current_city, current_temperature, current_weather, current_humidity, current_wind, update_tree, stop_program
    
    print("🎄 Интерактивная Новогодняя Ёлка 🎄")
    print("Данные о погоде обновляются автоматически...")
    
    create_snowflakes(20)
    create_raindrops(30)
    create_clouds(5)
    
    while not stop_program:
        try:
            weather = get_weather_simple("могилев")
            
            if weather and 'описание' in weather:
                current_city = weather.get('город', 'Могилев')
                current_temperature = weather.get('температура', '0')
                current_weather = weather.get('описание', 'christmas')
                current_humidity = weather.get('влажность', '0')
                current_wind = weather.get('ветер', '0')
                
                print(f"Текущая погода: {current_weather}, {current_temperature}°C")
                
                weather_key = current_weather.strip().lower()
                
                if weather_key in ['clouds']:
                    create_clouds(8, "normal")
                elif weather_key in ['partly cloudy']:
                    create_clouds(4, "partly")
                elif weather_key in ['rain', 'drizzle', 'thunderstorm']:
                    create_raindrops(30)
                elif weather_key in ['snow']:
                    create_snowflakes(20)
                
                play_weather_music(current_weather)
                
        except Exception as e:
            print(f"Ошибка при получении погоды: {e}")
            current_weather = 'christmas'
            current_temperature = '0'
        
        time.sleep(300)

# Функция для применения эффекта тумана к ёлке
def apply_fog_effect(tree_surface, intensity):
    fog_surface = pygame.Surface(tree_surface.get_size(), pygame.SRCALPHA)
    fog_surface.fill((200, 200, 200, intensity))
    tree_surface.blit(fog_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tree_surface

# Функция для применения снежного эффекта к ёлке
def apply_snow_effect(tree_surface, intensity):
    snow_surface = pygame.Surface(tree_surface.get_size(), pygame.SRCALPHA)
    snow_surface.fill((255, 255, 255, intensity))
    tree_surface.blit(snow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tree_surface

# Основная функция
def main():
    global WIDTH, HEIGHT, screen, stop_program, tree_frames
    
    clock = pygame.time.Clock()
    frame = 0
    
    input_thread = threading.Thread(target=weather_input_handler)
    input_thread.daemon = True
    input_thread.start()
    
    print("Окно с ёлкой запущено...")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                stop_program = True
            elif event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.size
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                create_snowflakes(20)
                create_raindrops(30)
                create_clouds(5)
        
        weather_key = current_weather.strip().lower()
        bg_color = WEATHER_BG_COLORS.get(weather_key, (10, 15, 40))
        screen.fill(bg_color)
        
        update_weather_effects()
        
        # Пересоздаем кадры ёлки при изменении погоды
        if frame % 300 == 0:  # Пересоздаем каждые 5 секунд (при 60 FPS)
            tree_frames = create_tree_animation_frames()
        
        current_frame = frame % len(tree_frames)
        tree_surface = tree_frames[current_frame].copy()
        
        if weather_key in ['mist', 'fog']:
            tree_surface = apply_fog_effect(tree_surface, 100)
        elif weather_key in ['snow']:
            tree_surface = apply_snow_effect(tree_surface, 40)
        
        if tree_surface:
            tree_rect = tree_surface.get_rect(center=(WIDTH * 0.65, HEIGHT * 0.55))
            screen.blit(tree_surface, tree_rect)
        
        draw_weather_effects(screen)
        draw_weather_info(screen)
        
        pygame.display.flip()
        frame += 1
        clock.tick(60)
    
    pygame.quit()
    print("Программа завершена.")

if __name__ == "__main__":
    main()
