#!/usr/bin/env python3
"""
Sitarc - Консольный сканер сайтов
Простой инструмент для поиска API, админ-панелей и скрытых директорий
"""

import requests
import sys
import time
from urllib.parse import urljoin
import os

# ASCII-арт логотип
ASCII_ART = """
  _____ _     _____           _    
 / ____(_)   |  __ \         | |   
| (___  _ ___| |__) |   _ ___| |__ 
 \___ \| / __|  _  / | | / __| '_ \\
 ____) | \__ \ | \ \ |_| \__ \ | | |
|_____/|_|___/_|  \_\__,_|___/_| |_|
                                    
      Website Security Scanner
      Version 1.1 | Made in Python
"""

class SiteArcScanner:
    def __init__(self):
        # Цвета для консоли
        self.COLORS = {
            'RED': '\033[91m',
            'GREEN': '\033[92m',
            'YELLOW': '\033[93m',
            'BLUE': '\033[94m',
            'MAGENTA': '\033[95m',
            'CYAN': '\033[96m',
            'RESET': '\033[0m',
            'BOLD': '\033[1m'
        }
        
        # Базовые словари для поиска
        self.wordlists = {
            'API и эндпоинты': [
                '/api/', '/api/v1/', '/api/v2/', '/graphql', '/rest/', '/soap/',
                '/swagger/', '/swagger-ui/', '/api-docs/', '/wp-json/', '/json/',
                '/oauth/', '/auth/', '/login/', '/logout/', '/register/', '/signup/'
            ],
            'Админ-панели': [
                '/admin/', '/administrator/', '/wp-admin/', '/admin/login/',
                '/admincp/', '/admin123/', '/adminpanel/', '/adminarea/',
                '/dashboard/', '/control/', '/backend/', '/manager/', '/moderator/',
                '/phpmyadmin/', '/mysql/', '/pma/', '/dbadmin/', '/sql/', '/admin.php'
            ],
            'Файлы и конфиги': [
                '/robots.txt', '/sitemap.xml', '/.env', '/.git/config',
                '/config.php', '/web.config', '/.htaccess', '/phpinfo.php',
                '/info.php', '/test.php', '/backup.zip', '/dump.sql'
            ],
            'Директории': [
                '/uploads/', '/images/', '/img/', '/css/', '/js/', '/assets/',
                '/static/', '/media/', '/files/', '/downloads/', '/backup/',
                '/tmp/', '/temp/', '/cache/', '/logs/', '/config/', '/includes/',
                '/src/', '/lib/', '/vendor/', '/node_modules/', '/storage/'
            ],
            'Разное': [
                '/', '/index.php', '/home/', '/main/', '/portal/', '/welcome/',
                '/internal/', '/intranet/', '/private/', '/secret/', '/hidden/'
            ]
        }
    
    def color_print(self, text, color):
        """Цветной вывод в консоль"""
        color_code = self.COLORS.get(color, self.COLORS['RESET'])
        print(f"{color_code}{text}{self.COLORS['RESET']}")
    
    def print_banner(self):
        """Вывод баннера"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.COLORS['CYAN'] + ASCII_ART + self.COLORS['RESET'])
        print("=" * 60)
    
    def create_session(self):
        """Создание новой сессии для каждого сканирования"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        return session
    
    def check_url(self, session, base_url, path):
        """Проверка существования URL"""
        url = urljoin(base_url, path)
        
        try:
            response = session.get(url, timeout=5, allow_redirects=True)
            
            if response.status_code < 400:
                return {
                    'url': url,
                    'status': response.status_code,
                    'path': path,
                    'category': self.get_category(path),
                    'size': len(response.content)
                }
                
        except requests.exceptions.RequestException:
            pass
        except Exception:
            pass
        
        return None
    
    def get_category(self, path):
        """Определение категории пути"""
        path_lower = path.lower()
        
        if 'api' in path_lower or 'rest' in path_lower or 'graphql' in path_lower:
            return 'API'
        elif 'admin' in path_lower or 'panel' in path_lower or 'manage' in path_lower:
            return 'Admin'
        elif '.' in path_lower or any(ext in path_lower for ext in ['.txt', '.xml', '.json', '.php']):
            return 'File'
        elif '/' in path_lower and not '.' in path_lower:
            return 'Directory'
        else:
            return 'Other'
    
    def scan_category(self, session, base_url, category_name, paths):
        """Сканирование одной категории"""
        self.color_print(f"[*] Проверяю {category_name}...", "CYAN")
        
        found_in_category = []
        total = len(paths)
        
        for i, path in enumerate(paths, 1):
            result = self.check_url(session, base_url, path)
            
            if result:
                found_in_category.append(result)
                status = result['status']
                color = "GREEN" if status == 200 else "YELLOW"
                self.color_print(f"  [{status}] {result['url']}", color)
            
            # Прогресс
            if i % 5 == 0 or i == total:
                sys.stdout.write(f"\r  Прогресс: {i}/{total}")
                sys.stdout.flush()
        
        print()  # Новая строка после прогресса
        return found_in_category
    
    def full_scan(self, url):
        """Полное сканирование сайта"""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        self.print_banner()
        print(f"{self.COLORS['GREEN']}[+] Цель сканирования: {url}")
        print(f"[+] Время начала: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + self.COLORS['RESET'])
        
        session = self.create_session()
        all_found = []
        
        print("\n[*] Начинаю полное сканирование...")
        start_time = time.time()
        
        # Сканирование всех категорий
        for category_name, paths in self.wordlists.items():
            found = self.scan_category(session, url, category_name, paths)
            all_found.extend(found)
        
        # Проверка robots.txt
        self.color_print("\n[*] Анализирую robots.txt...", "CYAN")
        robots_url = urljoin(url, '/robots.txt')
        try:
            resp = session.get(robots_url, timeout=5)
            if resp.status_code == 200:
                self.color_print(f"  [200] {robots_url} (найден)", "GREEN")
                all_found.append({
                    'url': robots_url,
                    'status': 200,
                    'path': '/robots.txt',
                    'category': 'Robots',
                    'size': len(resp.content)
                })
        except:
            pass
        
        end_time = time.time()
        
        # Анализ результатов
        self.analyze_results(all_found)
        
        print(f"\n{self.COLORS['GREEN']}[+] Сканирование заняло: {end_time - start_time:.2f} секунд")
        
        return all_found
    
    def quick_scan(self, url):
        """Быстрое сканирование только критических путей"""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        self.print_banner()
        print(f"{self.COLORS['GREEN']}[+] Быстрое сканирование: {url}")
        print("=" * 60 + self.COLORS['RESET'])
        
        session = self.create_session()
        
        critical_paths = [
            '/admin/', '/administrator/', '/wp-admin/', '/admin.php',
            '/api/', '/api/v1/', '/config.php', '/.env', '/.git/config',
            '/phpinfo.php', '/robots.txt', '/sitemap.xml', '/.htaccess'
        ]
        
        print("\n[*] Проверяю критические пути...")
        found = []
        
        for path in critical_paths:
            result = self.check_url(session, url, path)
            if result:
                found.append(result)
                status_color = "GREEN" if result['status'] == 200 else "YELLOW"
                self.color_print(f"  [{result['status']}] {result['url']}", status_color)
            else:
                print(f"  [--] {urljoin(url, path)} (не найден)")
        
        if found:
            print(f"\n{self.COLORS['GREEN']}[+] Найдено критических путей: {len(found)}")
            critical_found = [r for r in found if r['category'] == 'Admin' and r['status'] == 200]
            if critical_found:
                print(f"{self.COLORS['RED']}[!] ВНИМАНИЕ: Найдены доступные админ-панели!")
                for r in critical_found:
                    print(f"  !!! {r['url']}")
        else:
            self.color_print("\n[-] Критические пути не найдены", "YELLOW")
        
        return found
    
    def custom_scan(self, url):
        """Сканирование пользовательских путей"""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        self.print_banner()
        print(f"{self.COLORS['GREEN']}[+] Пользовательское сканирование: {url}")
        print("=" * 60 + self.COLORS['RESET'])
        
        print("\nВведите пути для проверки.")
        print("Пример: /admin/, /api/, /test.php")
        print("Для завершения ввода введите 'done'")
        print("-" * 40)
        
        custom_paths = []
        while True:
            path = input("Введите путь (или 'done' для начала): ").strip()
            if path.lower() == 'done':
                break
            if path:
                if not path.startswith('/'):
                    path = '/' + path
                custom_paths.append(path)
        
        if not custom_paths:
            self.color_print("[-] Не указаны пути для сканирования", "YELLOW")
            return []
        
        session = self.create_session()
        found = []
        
        print(f"\n[*] Проверяю {len(custom_paths)} пользовательских путей...")
        
        for path in custom_paths:
            result = self.check_url(session, url, path)
            if result:
                found.append(result)
                status_color = "GREEN" if result['status'] == 200 else "YELLOW"
                self.color_print(f"  [{result['status']}] {result['url']}", status_color)
            else:
                print(f"  [--] {urljoin(url, path)} (не найден)")
        
        return found
    
    def analyze_results(self, results):
        """Анализ и вывод результатов"""
        if not results:
            self.color_print("\n[-] Ничего не найдено", "YELLOW")
            return
        
        print(f"\n{self.COLORS['GREEN']}{'='*60}")
        print("РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ")
        print("="*60 + self.COLORS['RESET'])
        
        # Группировка по категориям
        categories = {}
        for result in results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        # Вывод по категориям
        category_colors = {
            'API': 'MAGENTA',
            'Admin': 'RED',
            'File': 'YELLOW',
            'Directory': 'BLUE',
            'Other': 'CYAN',
            'Robots': 'GREEN'
        }
        
        total_found = 0
        
        for cat, items in categories.items():
            color = category_colors.get(cat, 'RESET')
            self.color_print(f"\n[+] {cat} ({len(items)} найдено):", color)
            
            for item in items:
                status_color = "GREEN" if item['status'] == 200 else "YELLOW"
                self.color_print(f"  [{item['status']}] {item['url']} ({item['size']} байт)", status_color)
                total_found += 1
        
        # Статистика
        print(f"\n{self.COLORS['GREEN']}{'='*60}")
        self.color_print(f"[+] Всего найдено: {total_found} объектов", "GREEN")
        
        # Критические находки
        critical = [r for r in results if r['category'] == 'Admin' and r['status'] == 200]
        if critical:
            print(f"\n{self.COLORS['RED']}[!] КРИТИЧЕСКИЕ НАХОДКИ:")
            for item in critical:
                self.color_print(f"  !!! АДМИН-ПАНЕЛЬ: {item['url']}", "RED")
    
    def save_results(self, results, base_url, filename=None):
        """Сохранение результатов в файл"""
        if not results:
            self.color_print("[-] Нет результатов для сохранения", "YELLOW")
            return False
        
        if filename is None:
            domain = base_url.replace('http://', '').replace('https://', '').split('/')[0]
            filename = f"scan_{domain}_{int(time.time())}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Результаты сканирования: {base_url}\n")
                f.write(f"Время: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Всего найдено: {len(results)} объектов\n")
                f.write("="*60 + "\n\n")
                
                # Группировка по категориям
                categories = {}
                for result in results:
                    cat = result['category']
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(result)
                
                for cat, items in categories.items():
                    f.write(f"\n[{cat}] ({len(items)} найдено):\n")
                    for item in items:
                        f.write(f"  [{item['status']}] {item['url']}\n")
                        f.write(f"      Размер: {item['size']} байт\n")
            
            self.color_print(f"[+] Результаты сохранены в: {filename}", "GREEN")
            return True
        except Exception as e:
            self.color_print(f"[-] Ошибка сохранения: {e}", "RED")
            return False

def main_menu():
    """Главное меню программы"""
    scanner = SiteArcScanner()
    scanner.print_banner()
    
    while True:
        print("\n" + "="*60)
        print("ГЛАВНОЕ МЕНЮ SITARC")
        print("="*60)
        print("1. Полное сканирование сайта")
        print("2. Быстрое сканирование (критические пути)")
        print("3. Сканировать пользовательские пути")
        print("4. Показать справку")
        print("5. Выход")
        print("="*60)
        
        choice = input("\nВыберите действие (1-5): ").strip()
        
        if choice == '1':
            url = input("\nВведите URL сайта: ").strip()
            if not url:
                scanner.color_print("[-] URL не может быть пустым", "RED")
                continue
            
            try:
                results = scanner.full_scan(url)
                
                # Предложение сохранить результаты
                save = input("\nСохранить результаты в файл? (y/n): ").lower()
                if save == 'y':
                    custom_name = input("Имя файла (Enter для автоимени): ").strip()
                    if custom_name:
                        scanner.save_results(results, url, custom_name)
                    else:
                        scanner.save_results(results, url)
                
                input("\nНажмите Enter для продолжения...")
                
            except Exception as e:
                scanner.color_print(f"[-] Ошибка при сканировании: {e}", "RED")
                input("\nНажмите Enter для продолжения...")
        
        elif choice == '2':
            url = input("\nВведите URL сайта: ").strip()
            if not url:
                scanner.color_print("[-] URL не может быть пустым", "RED")
                continue
            
            try:
                results = scanner.quick_scan(url)
                
                if results:
                    save = input("\nСохранить результаты в файл? (y/n): ").lower()
                    if save == 'y':
                        scanner.save_results(results, url)
                
                input("\nНажмите Enter для продолжения...")
                
            except Exception as e:
                scanner.color_print(f"[-] Ошибка при сканировании: {e}", "RED")
                input("\nНажмите Enter для продолжения...")
        
        elif choice == '3':
            url = input("\nВведите URL сайта: ").strip()
            if not url:
                scanner.color_print("[-] URL не может быть пустым", "RED")
                continue
            
            try:
                results = scanner.custom_scan(url)
                
                if results:
                    save = input("\nСохранить результаты в файл? (y/n): ").lower()
                    if save == 'y':
                        scanner.save_results(results, url)
                
                input("\nНажмите Enter для продолжения...")
                
            except Exception as e:
                scanner.color_print(f"[-] Ошибка при сканировании: {e}", "RED")
                input("\nНажмите Enter для продолжения...")
        
        elif choice == '4':
            print("\n" + "="*60)
            print("СПРАВКА ПО SITARC")
            print("="*60)
            print("Sitarc - инструмент для поиска скрытых директорий,")
            print("API эндпоинтов и админ-панелей на веб-сайтах.")
            print("\nВозможности:")
            print("  1. Полное сканирование - проверка всех стандартных путей")
            print("  2. Быстрое сканирование - только критические пути")
            print("  3. Пользовательское - проверка указанных вами путей")
            print("  4. Сохранение результатов в текстовый файл")
            print("\nСловари поиска включают:")
            print("  • API эндпоинты (/api/, /rest/, /graphql/)")
            print("  • Админ-панели (/admin/, /wp-admin/, /phpmyadmin/)")
            print("  • Конфигурационные файлы (robots.txt, .env, config.php)")
            print("  • Стандартные директории (/uploads/, /images/, /css/)")
            print("\nПримечание:")
            print("  • Используйте только для тестирования своих сайтов")
            print("  • Не нарушайте законы вашей страны")
            print("  • Всегда получайте разрешение перед сканированием")
            print("="*60)
            input("\nНажмите Enter для продолжения...")
        
        elif choice == '5':
            scanner.color_print("\n[+] Выход из программы...", "GREEN")
            break
        
        else:
            scanner.color_print("\n[-] Неверный выбор. Попробуйте снова.", "YELLOW")
            time.sleep(1)
        
        # Очистка экрана и вывод баннера перед следующим выбором
        scanner.print_banner()

def main():
    """Точка входа в программу"""
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n" + "\033[91m[!] Программа прервана пользователем\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[91m[!] Критическая ошибка: {e}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    # Проверка наличия requests
    try:
        import requests
    except ImportError:
        print("\033[91m[!] Ошибка: библиотека requests не установлена\033[0m")
        print("\033[93m[+] Установите её командой: pip install requests\033[0m")
        sys.exit(1)
    
    main()