#!/usr/bin/env python3
import os
import subprocess
import unicodedata
import re
from pathlib import Path
from tkinter import Tk, Label, Entry, Button, Checkbutton, IntVar, StringVar, filedialog, messagebox
from tkinter import ttk


class PermissionTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Permission Tool")
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

        Label(frame, text="Đặt Everyone FullControl và loại bỏ ACL khác.").place(x=20, y=100)
        Label(frame, text="AnTin Solution - Zalo: 0344 53 68 62").place(x=20, y=130)

        Button(frame, text="Áp dụng", width=22, command=self.apply_permissions).place(x=140, y=280)
        Button(frame, text="Thoát", width=22, command=self.root.quit).place(x=340, y=280)
        Label(frame, textvariable=self.status_text, foreground="blue").place(x=20, y=340)

    def build_rename_tab(self, frame):
        Label(frame, text="Chọn loại target:").place(x=20, y=20)
        ttk.OptionMenu(frame, self.rename_target_type, self.rename_target_type.get(), "Thư mục", "File").place(x=160, y=15)
        Button(frame, text="Chọn Ổ đĩa/thư mục/file", width=16, command=self.choose_rename_target).place(x=420, y=15)
        Entry(frame, textvariable=self.rename_target_path, width=60, state="readonly").place(x=20, y=60)

        Label(frame, text="Tên mới không dấu (tự động tạo khi chọn target):").place(x=20, y=110)
        Entry(frame, textvariable=self.rename_target_name, width=60).place(x=20, y=140)

        self.create_checkbox(frame, "Đổi tên đệ quy cho tất cả file/thư mục con", self.rename_recursive, 20, 180)

        Button(frame, text="Đổi tên", width=22, command=self.apply_rename).place(x=340, y=220)

        Label(frame, text="Ví dụ: Nguyễn Văn A -> Nguyen Van A").place(x=20, y=270)

    def create_checkbox(self, frame, text, variable, x, y):
        Checkbutton(frame, text=text, variable=variable).place(x=x, y=y)

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
        text = re.sub(r'[<>:"/\\|?*]', '_', text)
        return text.strip()

    def fill_normalized_name(self):
        target_text = self.rename_target_path.get().strip()
        if not target_text:
            messagebox.showwarning("Lỗi", "Vui lòng chọn target để tạo tên không dấu.")
            return
        path = Path(target_text)
        self.rename_target_name.set(self.normalize_text(path.name))

    def apply_windows_everyone_full_control(self, path: Path):
        powershell_script = r"""
$target = Get-Item -LiteralPath $args[0]
$acl = if ($target.PSIsContainer) { New-Object System.Security.AccessControl.DirectorySecurity } else { New-Object System.Security.AccessControl.FileSecurity }
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone","FullControl","ContainerInherit, ObjectInherit","None","Allow")
$acl.SetAccessRuleProtection($true,$false)
$acl.SetAccessRule($rule)
Set-Acl -Path $target.FullName -AclObject $acl
"""
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", powershell_script, str(path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise OSError(result.stderr.strip() or result.stdout.strip())

    def apply_permissions(self):
        path_text = self.target_path.get().strip()
        if not path_text:
            messagebox.showwarning("Lỗi", "Vui lòng chọn target trước khi áp dụng quyền.")
            return

        path = Path(path_text)
        if not path.exists():
            messagebox.showerror("Lỗi", f"Target không tồn tại: {path}")
            return

        try:
            if os.name != "nt":
                raise OSError("Chỉ chạy trên Windows. Tool này không hỗ trợ hệ điều hành khác.")
            self.apply_windows_everyone_full_control(path)
        except PermissionError:
            messagebox.showerror("Lỗi", "Không đủ quyền để thay đổi quyền truy cập. Hãy chạy với quyền quản trị nếu cần.")
            return
        except OSError as err:
            messagebox.showerror("Lỗi", f"Lỗi khi thay đổi quyền: {err}")
            return

        status_message = f"Đã áp dụng quyền cho {path}"
        self.status_text.set(status_message)
        messagebox.showinfo("Thành công", status_message)

    def apply_recursive_rename(self, root: Path):
        items = sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True)
        for item in items:
            normalized = self.normalize_text(item.name)
            if normalized and normalized != item.name:
                target = item.with_name(normalized)
                if target.exists() and not target.samefile(item):
                    raise OSError(f"Tên đã tồn tại khi đổi tên đệ quy: {target}")
                item.rename(target)

        normalized_root = self.normalize_text(root.name)
        if normalized_root and normalized_root != root.name:
            new_root = root.with_name(normalized_root)
            if new_root.exists() and not new_root.samefile(root):
                raise OSError(f"Tên thư mục mới đã tồn tại: {new_root}")
            root.rename(new_root)
            return new_root
        return root

    def apply_rename(self):
        path_text = self.rename_target_path.get().strip()
        new_name = self.rename_target_name.get().strip()
        if not path_text:
            messagebox.showwarning("Lỗi", "Vui lòng chọn target để đổi tên.")
            return
        if not new_name:
            messagebox.showwarning("Lỗi", "Vui lòng tạo tên mới không dấu trước khi đổi tên.")
            return

        path = Path(path_text)
        if not path.exists():
            messagebox.showerror("Lỗi", f"Target không tồn tại: {path}")
            return

        try:
            if self.rename_target_type.get() == "Thư mục" and self.rename_recursive.get() and path.is_dir():
                final_path = self.apply_recursive_rename(path)
                messagebox.showinfo("Thành công", f"Đã đổi tên đệ quy thư mục và nội dung: {final_path}")
                self.rename_target_path.set(str(final_path))
                self.rename_target_name.set(final_path.name)
            else:
                new_path = path.with_name(new_name)
                if new_path.exists() and not new_path.samefile(path):
                    messagebox.showerror("Lỗi", f"Tên mới đã tồn tại: {new_path}")
                    return
                path.rename(new_path)
                messagebox.showinfo("Thành công", f"Đã đổi tên thành: {new_path}")
                self.rename_target_path.set(str(new_path))
                self.rename_target_name.set(new_path.name)
        except OSError as err:
            messagebox.showerror("Lỗi", f"Không thể đổi tên: {err}")
            return


if __name__ == "__main__":
    root = Tk()
    PermissionTool(root)
    root.mainloop()
