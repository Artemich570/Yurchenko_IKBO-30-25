import tkinter as tk
from tkinter import scrolledtext
import argparse
import os
import zipfile

class Emulator:
    def __init__(self, root, vfs_path, script_path):
        self.vfs = {}
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

        self.load_vfs()

    def load_vfs(self):
        """Загрузка VFS из ZIP-архива в оперативную память."""
        self.vfs = {
            "/": {"type": "directory"}
        }
        if not os.path.exists(self.vfs_path):
            self.append_output(f"ZIP file '{self.vfs_path}' not found.\n")
            return
        with zipfile.ZipFile(self.vfs_path, 'r') as f:
            for info in f.infolist():
                path = "/" + info.filename.rstrip("/")
                if info.is_dir():
                    self.vfs[path] = {"type": "directory"}
                else:
                    with f.open(info) as f2:
                        self.vfs[path] = {"type": "file", "content": f2.read()}
        self.append_output("VFS successfully loaded into memory.\n"
                           "----------------------------------------\n\n")


    def show_debug(self):
        """Отладочный вывод параметров конфигурации при запуске."""
        debug_info = (
            "[DEBUG CONFIGURATION]\n"
            f"VFS Physical Path: {self.vfs_path}\n"
            f"Startup Script Path: {self.script_path if self.script_path\
                                     else 'None'}\n"
            "----------------------------------------\n\n"
        )
        self.append_output(debug_info)
    
    def setup_ui(self):
        """Настройка UI"""
        main_frame = tk.Frame(self.root, bg="black")
        main_frame.pack(fill=tk.BOTH, expand=True)
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

        input_frame = tk.Frame(main_frame, bg="black")
        input_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        self.prompt_label = tk.Label(input_frame,
            text="",
            bg="black",
            fg="#00ff00",
            font=("Courier New", 11)
        )
        self.prompt_label.pack(side=tk.LEFT)

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
        """Обработка нажатия enter"""
        command = self.command_entry.get().strip()
        
        prompt = f"{self.username}@{self.hostname}:{self.current_directory}$ "
        self.append_output(prompt + command + "\n")
        
        self.command_entry.delete(0, tk.END)
        
        if command:
            self.command_history.append(command)
            self.history_index = len(self.command_history)

            self.process_command(command)
        
        self.show_prompt()
    
    def process_command(self, command):
        """Обработка команды"""
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
        elif command_ == "vfs-save":
            self.vfs_save(options.copy(), args.copy())
        elif command_ == "vfs-init":
            self.vfs_init(options.copy(), args.copy())
        else:
            self.append_output(f"{command_}: command not found\n")

    def vfs_save(self, options, args):
        """Сохранение текущего состояния VFS."""
        if len(args) != 1:
            self.append_output("Usage: vfs-save <dest_zip_path>\n")
            return
            
        dest_path = args[0]
        with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for path, data in self.vfs.items():
                if path == "/":
                    continue
                zip_name = path.lstrip('/')
                
                if data["type"] == "directory":
                    z.writestr(zip_name + "/", "")
                elif data["type"] == "file":
                    z.writestr(zip_name, data["content"])
                    
        self.append_output(f"VFS state successfully saved to '{dest_path}'.\n")

    def vfs_init(self, options, args):
        """Сброс VFS к состоянию по умолчанию."""
        zip_folder("vfs", "vfs.zip")
                
        self.append_output("VFS has been re-initialized to default.\n")
    
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
        """Команда exit"""
        if len(options) > 0:
            self.append_output(f"{options[0]}: invalid option\n")
        elif len(args) > 0:
            self.append_output(f"exit has no arguments\n")
        else:
            self.root.destroy()

    def ls_command(self, options, args):
        """Команда ls"""
        self.append_output(f"   List directory contents.\n")

    def clear_command(self, options, args):
        """Команда clear"""
        if len(options) > 0:
            self.append_output(f"{options[0]}: invalid option\n")
        elif len(args) > 0:
            self.append_output(f"clear has no arguments\n")
        else:
            self.clear_screen()

    def cd_command(self, options, args):
        """Команда cd"""
        self.append_output("    Change the shell working directory.\n")

    def run_script(self):
        """Выполнение скрипта"""
        if not os.path.exists(self.script_path):
            self.append_output(f"Error: Startup script \
                               '{self.script_path}' not found.\n")
            return
        
        with open(self.script_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                prompt = \
                f"{self.username}@{self.hostname}:{self.current_directory}$ "
                self.append_output(prompt + line + "\n")
                
                self.process_command(line)
        self.show_prompt()

def zip_folder(folder_path, output_path):
        """Создание архива"""
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    full = os.path.join(root, file)
                    zf.write(full, os.path.relpath(full, folder_path))

                for d in dirs:
                    full_dir = os.path.join(root, d)
                    if not os.listdir(full_dir):
                        arcname = os.path.relpath(full_dir, folder_path) + "/"
                        zf.writestr(arcname, "")

def main():
    if not os.path.exists("vfs.zip"):
        zip_folder("vfs", "vfs.zip")

    parser = argparse.ArgumentParser()
    parser.add_argument("--vfs", type=str, 
                        required=True, help="Path to VFS zip archive")
    parser.add_argument("--script", type=str, 
                        default=None, help="Path to startup script")
    args = parser.parse_args()

    root = tk.Tk()
    app = Emulator(root, vfs_path=args.vfs, script_path=args.script)
    root.mainloop()

if __name__ == "__main__":
    main()