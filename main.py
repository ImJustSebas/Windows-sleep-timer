import time
import os
import sys
import threading
import platform
from typing import Optional, Tuple, List, Dict, Callable
import datetime
import json

# Detección dinámica del módulo según el sistema operativo
if platform.system() == 'Windows':
    import msvcrt
    import ctypes
elif platform.system() == 'Linux' or platform.system() == 'Darwin':
    import select
    import termios
    import tty

class TerminalUI:
    """Clase para manejar la interfaz de usuario en terminal con estilos avanzados"""
    
    STYLES = {
        'reset': '\033[0m', 'bold': '\033[1m', 'italic': '\033[3m',
        'underline': '\033[4m', 'blink': '\033[5m', 'black': '\033[30m',
        'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m',
        'blue': '\033[94m', 'magenta': '\033[95m', 'cyan': '\033[96m',
        'white': '\033[97m', 'bg_black': '\033[40m', 'bg_red': '\033[41m',
        'bg_green': '\033[42m', 'bg_yellow': '\033[43m', 'bg_blue': '\033[44m',
        'bg_magenta': '\033[45m', 'bg_cyan': '\033[46m', 'bg_white': '\033[47m',
    }
    
    BOX_CHARS = {
        'simple': {'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘', 'h': '─', 'v': '│', 'title_l': '┤', 'title_r': '├'},
        'double': {'tl': '╔', 'tr': '╗', 'bl': '╚', 'br': '╝', 'h': '═', 'v': '║', 'title_l': '╡', 'title_r': '╞'},
        'rounded': {'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯', 'h': '─', 'v': '│', 'title_l': '┤', 'title_r': '├'}
    }
    
    def __init__(self):
        self.box_style = 'rounded'
        self.terminal_width, self.terminal_height = self._get_terminal_size()
        self.config = self._load_config()
        self._setup_terminal()
        self.is_raw_mode = False
        
    def _setup_terminal(self) -> None:
        if platform.system() == 'Windows':
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            os.system('title PowerTimer - Temporizador de Apagado')
        else:
            sys.stdout.write('\33]0;PowerTimer - Temporizador de Apagado\a')
            sys.stdout.flush()
    
    def _get_terminal_size(self) -> Tuple[int, int]:
        return os.get_terminal_size().columns, os.get_terminal_size().lines
    
    def _load_config(self) -> Dict:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'powertimer_config.json')
        default_config = {
            'theme': 'dark', 'box_style': self.box_style, 'accent_color': 'cyan',
            'text_color': 'white', 'error_color': 'red', 'warning_color': 'yellow',
            'success_color': 'green', 'last_used_times': [30, 60, 120]
        }
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            else:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception:
            return default_config
            
    def save_config(self) -> None:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'powertimer_config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass
    
    def update_last_used_times(self, minutes: int) -> None:
        if minutes in self.config['last_used_times']:
            self.config['last_used_times'].remove(minutes)
        self.config['last_used_times'].insert(0, minutes)
        self.config['last_used_times'] = self.config['last_used_times'][:5]
        self.save_config()
        
    def clear_screen(self) -> None:
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        
    def style_text(self, text: str, *styles: str) -> str:
        styled = text
        for style in styles:
            if style in self.STYLES:
                styled = f"{self.STYLES[style]}{styled}{self.STYLES['reset']}"
        return styled
    
    def get_theme_color(self, color_type: str) -> str:
        return self.config.get(color_type, self.config['accent_color'])
        
    def print_centered(self, text: str, *styles: str) -> None:
        self.terminal_width = self._get_terminal_size()[0]
        styled_text = self.style_text(text.center(self.terminal_width), *styles)
        print(styled_text)
        
    def draw_box(self, content: List[str], title: str = None, width: int = None, 
                 style: str = None, color: str = None) -> None:
        self.terminal_width = self._get_terminal_size()[0]
        box_style = style or self.config['box_style']
        chars = self.BOX_CHARS.get(box_style, self.BOX_CHARS['rounded'])
        color = color or self.config['accent_color']
        width = min(width or self.terminal_width - 4, 60)
        content_width = max((len(line) for line in content), default=0)
        width = max(width, content_width + 4)
        width = min(width, self.terminal_width - 2)
        left_margin = (self.terminal_width - width) // 2
        margin = ' ' * left_margin
        
        if title:
            title_space = width - 4
            title = title[:title_space-3] + "..." if len(title) > title_space else title
            left_part = chars['tl'] + chars['h'] * ((width - len(title) - 2) // 2)
            right_part = chars['h'] * (width - len(title) - 2 - len(left_part) + 1) + chars['tr']
            print(margin + self.style_text(left_part + ' ' + title + ' ' + right_part, color))
        else:
            print(margin + self.style_text(chars['tl'] + chars['h'] * (width - 2) + chars['tr'], color))
        
        for line in content:
            if len(line) < width - 4:
                padding = (width - 4 - len(line)) // 2
                line = ' ' * padding + line + ' ' * (width - 4 - len(line) - padding)
            elif len(line) > width - 4:
                line = line[:width-7] + "..."
            print(margin + self.style_text(chars['v'] + ' ' + line.ljust(width - 4) + ' ' + chars['v'], color))
        
        print(margin + self.style_text(chars['bl'] + chars['h'] * (width - 2) + chars['br'], color))
        
    def draw_progress_bar(self, current: float, total: float, width: int = 40, 
                         color: str = None, empty_char: str = '░', fill_char: str = '█') -> None:
        color = color or self.config['accent_color']
        progress = max(0, min(current / total, 1.0))
        filled_width = int(width * progress)
        bar = fill_char * filled_width + empty_char * (width - filled_width)
        percentage = f"{int(progress * 100)}%"
        self.terminal_width = self._get_terminal_size()[0]
        left_margin = (self.terminal_width - width - 7) // 2
        margin = ' ' * left_margin
        print(margin + self.style_text(bar, color) + f" {percentage}")
        
    def draw_menu(self, title: str, options: List[Tuple[str, str]], 
                 footer: str = None, selected: int = None) -> None:
        menu_content = [f"→ [{key}] {desc}" if selected is not None and i == selected 
                       else f"  [{key}] {desc}" for i, (key, desc) in enumerate(options)]
        if footer:
            menu_content.extend(["", footer])
        self.draw_box(menu_content, title, color=self.config['accent_color'])

    def draw_clock(self, remaining_seconds: int) -> None:
        hours, remainder = divmod(remaining_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
        time_desc = "horas  minutos  segundos" if hours > 0 else "minutos  segundos"
        clock_content = ["", time_str, time_desc, ""]
        self.draw_box(clock_content, "TIEMPO RESTANTE", color=self.config['accent_color'])
        self.draw_progress_bar(60 - (remaining_seconds % 60), 60)

    def get_keypress(self) -> Optional[str]:
        if platform.system() == 'Windows':
            if msvcrt.kbhit():
                return msvcrt.getch().decode('utf-8').lower()
        else:
            if not self.is_raw_mode:
                self.old_settings = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())
                self.is_raw_mode = True
            if select.select([sys.stdin], [], [], 0.1)[0]:
                return sys.stdin.read(1).lower()
        return None

    def restore_terminal(self) -> None:
        if platform.system() != 'Windows' and self.is_raw_mode:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            self.is_raw_mode = False

class PowerTimer:
    """Clase principal para el temporizador de apagado"""
    
    def __init__(self):
        self.ui = TerminalUI()
        self.cancel_event = threading.Event()
        
    def shutdown_system(self, minutes: int) -> None:
        self.cancel_event.clear()
        end_time = time.time() + (minutes * 60)
        
        def countdown():
            while time.time() < end_time and not self.cancel_event.is_set():
                remaining = int(end_time - time.time())
                self.ui.clear_screen()
                self.ui.draw_clock(remaining)
                self.ui.print_centered("Presiona 'C' para cancelar", self.ui.get_theme_color('warning_color'))
                time.sleep(1)
            if not self.cancel_event.is_set():
                os.system("shutdown /s /t 0" if platform.system() == 'Windows' else "shutdown -h now")
        
        timer_thread = threading.Thread(target=countdown)
        timer_thread.start()
        
        while timer_thread.is_alive() and not self.cancel_event.is_set():
            if self.ui.get_keypress() == 'c':
                self.cancel_event.set()
                timer_thread.join()
                self.ui.clear_screen()
                self.ui.draw_box(["Apagado cancelado"], "AVISO", color=self.ui.get_theme_color('success_color'))
                time.sleep(2)
                break
    
    def run(self) -> None:
        options = [
            ("1", "30 minutos"), ("2", "1 hora"), ("3", "2 horas"),
            ("4", "Personalizado"), ("5", "Salir")
        ]
        
        try:
            while True:
                self.ui.clear_screen()
                self.ui.draw_menu("PowerTimer", options, "Selecciona una opción con el número")
                choice = input("\nOpción: ").strip()
                
                if choice == '1':
                    self.ui.update_last_used_times(30)
                    self.shutdown_system(30)
                elif choice == '2':
                    self.ui.update_last_used_times(60)
                    self.shutdown_system(60)
                elif choice == '3':
                    self.ui.update_last_used_times(120)
                    self.shutdown_system(120)
                elif choice == '4':
                    try:
                        minutes = int(input("Tiempo en minutos: "))
                        if minutes <= 0:
                            raise ValueError("Debe ser mayor a 0")
                        self.ui.update_last_used_times(minutes)
                        self.shutdown_system(minutes)
                    except ValueError as e:
                        self.ui.clear_screen()
                        self.ui.draw_box([f"Error: {str(e)}"], "ERROR", color=self.ui.get_theme_color('error_color'))
                        time.sleep(2)
                elif choice == '5':
                    self.ui.clear_screen()
                    self.ui.draw_box(["¡Hasta pronto!"], "DESPEDIDA", color=self.ui.get_theme_color('success_color'))
                    time.sleep(1)
                    break
                else:
                    self.ui.clear_screen()
                    self.ui.draw_box(["Opción inválida"], "ERROR", color=self.ui.get_theme_color('error_color'))
                    time.sleep(2)
        finally:
            self.ui.restore_terminal()

if __name__ == "__main__":
    try:
        PowerTimer().run()
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        TerminalUI().restore_terminal()