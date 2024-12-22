import os
import customtkinter as ctk
from PIL import Image, UnidentifiedImageError
import subprocess
import json
import sys

# Constants
APPS_DIR = os.path.join(os.path.expanduser("~"), "ROSHUB", "apps")
DEFAULT_LOGO = "images/default_logo.png"
REPO_LIST = "repo_list.json"
GIT_PORTABLE_PATH = os.path.join(os.getcwd(), "Git", "bin", "git.exe")  # Ruta a Git Portable
RHCA_UPDATER = os.path.join(os.getcwd(), "rhcaupdater.py")  # Ruta al archivo rhcaupdater.py

# Ensure Git Portable is available
def ensure_git():
    if not os.path.isfile(GIT_PORTABLE_PATH):
        print("Git Portable is not available. Please include it in the application folder.")
        exit(1)

# Main Application
class RHCA(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RosHub Central App")
        self.geometry("1200x800")
        self.configure(bg="#1e1e1e")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.nav_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")

        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        self.setup_navbar()
        self.show_home()

    def setup_navbar(self):
        # Home Button
        self.home_button = ctk.CTkButton(self.nav_frame, text="Home", command=self.show_home)
        self.home_button.pack(pady=10, padx=20, fill="x")

        # RH Apps Button
        self.rh_apps_button = ctk.CTkButton(self.nav_frame, text="RH Apps", command=self.show_rh_apps)
        self.rh_apps_button.pack(pady=10, padx=20, fill="x")

        # Update RHCA Button
        self.update_button = ctk.CTkButton(self.nav_frame, text="Update RHCA", command=self.run_updater, fg_color="orange")
        self.update_button.pack(pady=10, padx=20, fill="x")

        # Exit Button at the bottom
        self.nav_frame.pack_propagate(False)
        self.exit_button = ctk.CTkButton(self.nav_frame, text="Exit", command=self.quit, fg_color="red", text_color="white")
        self.exit_button.pack(side="bottom", pady=10, padx=20, fill="x")

    def show_home(self):
        self.clear_main_frame()
        apps_label = ctk.CTkLabel(self.main_frame, text="Applications", font=ctk.CTkFont(size=24, weight="bold"))
        apps_label.pack(pady=20)

        apps_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        apps_container.pack(pady=10, padx=20, fill="both", expand=True)

        if not os.path.exists(APPS_DIR):
            os.makedirs(APPS_DIR, exist_ok=True)

        apps = [d for d in os.listdir(APPS_DIR) if os.path.isdir(os.path.join(APPS_DIR, d))]
        if not apps:
            ctk.CTkLabel(apps_container, text="No applications found.", font=ctk.CTkFont(size=16)).pack(pady=20)
        else:
            for app in apps:
                app_path = os.path.join(APPS_DIR, app)
                main_py_path = os.path.join(app_path, "main.py")
                logo_path = os.path.join(app_path, "images", "logo.png")

                if not os.path.isfile(main_py_path):
                    continue

                try:
                    app_logo = ctk.CTkImage(Image.open(logo_path), size=(50, 50))
                except (FileNotFoundError, UnidentifiedImageError):
                    app_logo = ctk.CTkImage(Image.open(DEFAULT_LOGO), size=(50, 50))

                app_frame = ctk.CTkFrame(apps_container, fg_color="#3e3e3e", corner_radius=10)
                app_frame.pack(pady=10, padx=10, fill="x")

                logo_label = ctk.CTkLabel(app_frame, image=app_logo, text="")
                logo_label.pack(side="left", padx=10, pady=10)

                app_label = ctk.CTkLabel(app_frame, text=app, font=ctk.CTkFont(size=16))
                app_label.pack(side="left", padx=10)

                open_button = ctk.CTkButton(app_frame, text="Open", command=lambda path=app_path: self.launch_app(path))
                open_button.pack(side="right", padx=10, pady=10)

    def show_rh_apps(self):
        self.clear_main_frame()
        repos_label = ctk.CTkLabel(self.main_frame, text="RH Applications", font=ctk.CTkFont(size=24, weight="bold"))
        repos_label.pack(pady=20)

        repos_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        repos_container.pack(pady=10, padx=20, fill="both", expand=True)

        if not os.path.exists(REPO_LIST):
            with open(REPO_LIST, "w") as f:
                json.dump([], f)

        with open(REPO_LIST, "r") as f:
            repos = json.load(f)

        if not repos:
            ctk.CTkLabel(repos_container, text="No repositories available.", font=ctk.CTkFont(size=16)).pack(pady=20)
        else:
            for repo in repos:
                repo_name = os.path.basename(repo).replace(".git", "")
                app_path = os.path.join(APPS_DIR, repo_name)
                is_installed = os.path.exists(app_path)

                repo_frame = ctk.CTkFrame(repos_container, fg_color="#3e3e3e", corner_radius=10)
                repo_frame.pack(pady=10, padx=10, fill="x")

                repo_label = ctk.CTkLabel(repo_frame, text=repo_name, font=ctk.CTkFont(size=16))
                repo_label.pack(side="left", padx=10)

                if is_installed:
                    update_button = ctk.CTkButton(repo_frame, text="Update", command=lambda r=repo: self.update_repo(r))
                    update_button.pack(side="right", padx=10, pady=10)
                else:
                    install_button = ctk.CTkButton(repo_frame, text="Install", command=lambda r=repo: self.install_repo(r))
                    install_button.pack(side="right", padx=10, pady=10)

    def run_updater(self):
        if os.path.isfile(RHCA_UPDATER):
            subprocess.Popen(["python", RHCA_UPDATER])
            self.quit()
        else:
            ctk.CTkLabel(self.main_frame, text="Updater not found!", text_color="red").pack(pady=10)

    def install_repo(self, repo_url):
        repo_name = os.path.basename(repo_url).replace(".git", "")
        repo_path = os.path.join(APPS_DIR, repo_name)
        if not os.path.exists(repo_path):
            try:
                subprocess.run([GIT_PORTABLE_PATH, "clone", repo_url, repo_path], check=True)
                ctk.CTkLabel(self.main_frame, text=f"Installed {repo_name} successfully.", text_color="green").pack(pady=10)
            except subprocess.CalledProcessError:
                ctk.CTkLabel(self.main_frame, text=f"Failed to install {repo_name}.", text_color="red").pack(pady=10)

    def update_repo(self, repo_url):
        repo_name = os.path.basename(repo_url).replace(".git", "")
        repo_path = os.path.join(APPS_DIR, repo_name)
        if os.path.exists(repo_path):
            try:
                subprocess.run([GIT_PORTABLE_PATH, "-C", repo_path, "pull"], check=True)
                ctk.CTkLabel(self.main_frame, text=f"Updated {repo_name} successfully.", text_color="green").pack(pady=10)
            except subprocess.CalledProcessError:
                ctk.CTkLabel(self.main_frame, text=f"Failed to update {repo_name}.", text_color="red").pack(pady=10)

    def launch_app(self, app_path):
        main_py_path = os.path.join(app_path, "main.py")
        if os.path.isfile(main_py_path):
            original_cwd = os.getcwd()
            try:
                os.chdir(app_path)
                os.system(f'python "main.py"')
            finally:
                os.chdir(original_cwd)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    ensure_git()
    app = RHCA()
    app.mainloop()
