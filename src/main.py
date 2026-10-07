import tkinter as tk
from tkinter import scrolledtext
import argparse
import os

class Emulator:
    def __init__(self, root, vfs_path, script_path):
        self.root = root
        self.root.title("VFS")
        self.root.geometry("800x600")
        
        self.current_directory = "~"
        self.username = "user"
        self.hostname = "localhost"
        self.command_history = []
        self.history_index = 0
        self.vfs_path = vfs_path
        self.script_path = script_path
        
        self.setup_ui()
        self.show_welcome_message()
        self.show_debug()
        self.show_prompt()

        if self.script_path:
            self.root.after(100, self.run_script)

    def show_debug(self):
        """Отладочный вывод параметров конфигурации при запуске."""
        debug_info = (
            f"[DEBUG CONFIGURATION]\n"
            f"VFS Physical Path: {self.vfs_path}\n"
            f"Startup Script Path: {self.script_path if self.script_path else 'None'}\n"
            f"----------------------------------------\n\n"
        )
        self.append_output(debug_info)
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="black")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        """Текстовое поле для вывода"""
        self.output_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            bg="black",
            fg="#00ff00",
            font=("Courier New", 11),
            insertbackground="#00ff00",
            selectbackground="#333333",
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        """Фрейм для ввода команды"""
        input_frame = tk.Frame(main_frame, bg="black")
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        """Метка с приглашением"""
        self.prompt_label = tk.Label(input_frame,
            text="",
            bg="black",
            fg="#00ff00",
            font=("Courier New", 11)
        )
        self.prompt_label.pack(side=tk.LEFT)
        """Поле ввода команды"""
        self.command_entry = tk.Entry(input_frame,
            bg="black",
            fg="#00ff00",
            font=("Courier New", 11),
            insertbackground="#00ff00",
            relief=tk.FLAT,
            bd=0
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, 
                                expand=True, padx=(5, 0))

        self.command_entry.bind("<Return>", self.on_enter_pressed)
        self.command_entry.bind("<Up>", self.on_arrow_up)
        self.command_entry.bind("<Down>", self.on_arrow_down)
    
    def show_welcome_message(self):
        welcome = """Welcome to UNIX Shell Emulator v1.0
Type 'help' for available commands.

"""
        self.append_output(welcome)
    
    def show_prompt(self):
        """приглашение командной строки"""
        prompt = f"{self.username}@{self.hostname}:{self.current_directory}$ "
        self.prompt_label.config(text=prompt)
    
    def append_output(self, text):
        """Добавить текст в выходное поле"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def on_enter_pressed(self, event):
        command = self.command_entry.get().strip() #Обработка нажатия Enter
        
        """Выводим команду с приглашением"""
        prompt = f"{self.username}@{self.hostname}:{self.current_directory}$ "
        self.append_output(prompt + command + "\n")
        
        self.command_entry.delete(0, tk.END)
        
        if command:
            """Добавляем в историю"""
            self.command_history.append(command)
            self.history_index = len(self.command_history)

            self.process_command(command)
        
        self.show_prompt() # Обновляем приглашение
    
    def process_command(self, command):
        command_ = command.split()[0]
        options = []
        args = []
        for el in command.split()[1::]:
            if el[0] == "-":
                options.append(el)
            else:
                args.append(el)
        if command_ == "clear":
            self.clear_command(options.copy(), args.copy())
        elif command_ == "exit":
            self.exit_command(options.copy(), args.copy())
        elif command_ == "ls":
            self.ls_command(options.copy(), args.copy())
        elif command_ == "cd":
            self.cd_command(options.copy(), args.copy())
        else:
            self.append_output(f"{command}: command not found\n")
    
    def on_arrow_up(self, event):
        """Навигация по истории команд вверх"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, 
                                      self.command_history[self.history_index])
        return "break"
    
    def on_arrow_down(self, event):
        """Навигация по истории команд вниз"""
        if self.command_history and \
            self.history_index < len(self.command_history) - 1:

            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, 
                                      self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.command_entry.delete(0, tk.END)
        return "break"
    
    def clear_screen(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.show_prompt()

    def exit_command(self, options, args):
        if len(options) > 0:
            self.append_output(f"{options[0]}: invalid option\n")
        elif len(args) > 0:
            self.append_output(f"exit has no arguments\n")
        else:
            self.root.destroy()

    def ls_command(self, options, args):
        self.append_output(f"   List directory contents.\n")

    def clear_command(self, options, args):
        if len(options) > 0:
            self.append_output(f"{options[0]}: invalid option\n")
        elif len(args) > 0:
            self.append_output(f"clear has no arguments\n")
        else:
            self.clear_screen()

    def cd_command(self, options, args):
        self.append_output("    Change the shell working directory.\n")

    def run_script(self):
        """Выполнение скрипта"""
        if not os.path.exists(self.script_path):
            self.append_output(f"Error: Startup script '{self.script_path}' not found.\n")
            return
        
        with open(self.script_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                
                # Игнорируем пустые строки и комментарии (начинаются с #)
                if not line or line.startswith("#"):
                    continue
                
                prompt = f"{self.username}@{self.hostname}:{self.current_directory}$ "
                self.append_output(prompt + line + "\n")
                
                self.process_command(line)
        self.show_prompt()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vfs", type=str, required=True, help="Path to VFS zip archive")
    parser.add_argument("--script", type=str, default=None, help="Path to startup script")
    args = parser.parse_args()

    root = tk.Tk()
    app = Emulator(root, vfs_path=args.vfs, script_path=args.script)
    root.mainloop()

if __name__ == "__main__":
    main()