import os
import subprocess
import unicodedata
import re
import ctypes
from pathlib import Path
from tkinter import Tk, Label, Entry, Button, Checkbutton, IntVar, StringVar, filedialog, messagebox
from tkinter import ttk

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

class PermissionTool:
    def __init__(self, root):
        self.root = root
        self.root.title("PM reset permission - AnTin Solution")
        self.root.geometry("620x420")
        self.root.resizable(False, False)

        self.target_type = StringVar(value="Thư mục/ổ đĩa")
        self.target_path = StringVar()

        self.rename_target_type = StringVar(value="File")
        self.rename_target_path = StringVar()
        self.rename_target_name = StringVar()
        self.rename_recursive = IntVar(value=0)
        self.status_text = StringVar(value="Sẵn sàng.")

        self.build_ui()

        if os.name == "nt" and not is_admin():
            messagebox.showwarning(
                "Cảnh báo",
                "Nên chạy chương trình bằng quyền Administrator để thay đổi ACL."
            )

    def build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.place(x=10, y=10, width=600, height=400)

        permission_frame = ttk.Frame(notebook)
        rename_frame = ttk.Frame(notebook)

        notebook.add(permission_frame, text="Set Permissions")
        notebook.add(rename_frame, text="Đổi tên không dấu")

        self.build_permission_tab(permission_frame)
        self.build_rename_tab(rename_frame)

    def build_permission_tab(self, frame):
        Label(frame, text="Chọn file hoặc thư mục/ổ đĩa:").place(x=20, y=20)
        ttk.OptionMenu(frame, self.target_type, self.target_type.get(), "Thư mục/ổ đĩa", "File").place(x=220, y=15)
        Button(frame, text="Chọn target", width=18, command=self.choose_target).place(x=420, y=15)
        Entry(frame, textvariable=self.target_path, width=60, state="readonly").place(x=20, y=60)

        Label(frame, text="Fix permission- dev by: AnTin Solution").place(x=20, y=100)
        Label(frame, text="Chuyên: viết PM theo yêu cầu - Sửa máy tính - camera - máy in").place(x=20, y=130)
        Label(frame, text="Zalo: 0344 53 68 62").place(x=20, y=160)

        Button(frame, text="Áp dụng", width=22, command=self.apply_permissions).place(x=140, y=280)
        Button(frame, text="Thoát", width=22, command=self.root.quit).place(x=340, y=280)
        Label(frame, textvariable=self.status_text, foreground="blue").place(x=20, y=340)

    def build_rename_tab(self, frame):
        Label(frame, text="Chọn loại target:").place(x=20, y=20)
        ttk.OptionMenu(frame, self.rename_target_type, self.rename_target_type.get(), "Thư mục", "File").place(x=160, y=15)
        Button(frame, text="Chọn Ổ đĩa/thư mục/file", width=16, command=self.choose_rename_target).place(x=420, y=15)
        Entry(frame, textvariable=self.rename_target_path, width=60, state="readonly").place(x=20, y=60)

        Label(frame, text="Tên mới không dấu:").place(x=20, y=110)
        Entry(frame, textvariable=self.rename_target_name, width=60).place(x=20, y=140)

        Checkbutton(frame, text="Đổi tên đệ quy cho tất cả file/thư mục con",
                    variable=self.rename_recursive).place(x=20, y=180)

        Button(frame, text="Đổi tên", width=22, command=self.apply_rename).place(x=340, y=220)

    def choose_target(self):
        if self.target_type.get() == "File":
            path = filedialog.askopenfilename(title="Chọn file")
        else:
            path = filedialog.askdirectory(title="Chọn thư mục hoặc ổ đĩa")
        if path:
            self.target_path.set(path)

    def choose_rename_target(self):
        if self.rename_target_type.get() == "File":
            path = filedialog.askopenfilename(title="Chọn file")
        else:
            path = filedialog.askdirectory(title="Chọn thư mục")
        if path:
            self.rename_target_path.set(path)
            self.fill_normalized_name()

    def normalize_text(self, text):
        text = unicodedata.normalize("NFKD", text)
        text = ''.join(ch for ch in text if not unicodedata.combining(ch))
        text = text.replace('đ', 'd').replace('Đ', 'D')
        text = re.sub(r'[<>:"/\\\\|?*]', '_', text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def fill_normalized_name(self):
        path = Path(self.rename_target_path.get())
        self.rename_target_name.set(self.normalize_text(path.name))

    def apply_windows_everyone_full_control(self, path: Path):
        cmd = [
            "icacls",
            str(path),
            "/inheritance:r",
            "/grant:r",
            "Everyone:(OI)(CI)F",
            "/T",
            "/C"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise OSError(result.stderr.strip() or result.stdout.strip() or "ICACLS failed")

    def apply_permissions(self):
        path_text = self.target_path.get().strip()
        if not path_text:
            messagebox.showwarning("Lỗi", "Vui lòng chọn target.")
            return

        path = Path(path_text)
        if not path.exists():
            messagebox.showerror("Lỗi", f"Target không tồn tại: {path}")
            return

        try:
            self.apply_windows_everyone_full_control(path)
            self.status_text.set(f"Đã áp dụng quyền cho {path}")
            messagebox.showinfo("Thành công", f"Đã áp dụng quyền cho {path}")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def apply_recursive_rename(self, root: Path):
        if root.parent == root:
            raise OSError("Không thể đổi tên ổ đĩa.")

        items = sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True)

        for item in items:
            new_name = self.normalize_text(item.name)
            if new_name and new_name != item.name:
                target = item.with_name(new_name)
                if target.exists():
                    raise OSError(f"Tên đã tồn tại: {target}")
                item.rename(target)

        return root

    def apply_rename(self):
        path = Path(self.rename_target_path.get().strip())
        new_name = self.rename_target_name.get().strip()

        if not path.exists():
            messagebox.showerror("Lỗi", "Target không tồn tại.")
            return

        try:
            if self.rename_recursive.get() and path.is_dir():
                self.apply_recursive_rename(path)

            if path.parent == path:
                raise OSError("Không thể đổi tên ổ đĩa.")

            new_path = path.with_name(new_name)

            if new_path.exists() and new_path != path:
                raise OSError("Tên mới đã tồn tại.")

            path.rename(new_path)

            self.rename_target_path.set(str(new_path))
            self.rename_target_name.set(new_path.name)

            messagebox.showinfo("Thành công", f"Đã đổi tên thành:\n{new_path}")

        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

if __name__ == "__main__":
    root = Tk()
    PermissionTool(root)
    root.mainloop()
