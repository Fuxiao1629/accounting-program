import tkinter as tk #导入tkinter 库来创建图形用户界面（GUI）
import datetime #引入datetime 模块来处理日期时间
from tkinter import messagebox #从 tkinter 中导入 messagebox，来弹出提示框
import os #导入os模块来操作文件夹和文件
import glob #导入glob进行文件路径通配符匹配


class AccountingGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("记账程序")
        
        # 先初始化月度预算、支出记录等属性
        self.monthly_budget = 0
        self.expenses = {}
        self.current_month = datetime.date.today().month
        self.last_record_date = ""  # 用于记录当月最近一次账单日期

        # 检查并获取存储文件夹路径，优先从配置文件读取
        self.folder_path = self.get_jizhang_folder_path_from_config()
        if not self.folder_path:
            # 若配置文件中无记录，进行创建或获取文件夹路径的常规流程
            self.folder_path = self.get_jizhang_folder_path()
            self.save_folder_path_to_config(self.folder_path)
        self.create_widgets()
        self.check_and_update_budget_on_first()
        self.load_data_and_update_budget_balance()
        

    def get_jizhang_folder_path_from_config(self):
        config_file_path = "config.txt"
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r') as f:
                folder_path = f.read().strip()
                if os.path.exists(folder_path):
                    return folder_path
        return ""

    def save_folder_path_to_config(self, folder_path):
        config_file_path = "config.txt"
        with open(config_file_path, 'w') as f:
            f.write(folder_path)

    def get_jizhang_folder_path(self):
        default_folder_path = "D:/jizhang"
        if os.path.exists(default_folder_path):
            # 若默认文件夹已存在，让用户输入新文件夹名
            new_folder_name = self.get_user_folder_name()
            folder_path = os.path.join("D:/", new_folder_name)
            os.makedirs(folder_path)
            # 弹出新窗口提示用户保存路径
            self.show_folder_path_popup(folder_path)
            return folder_path
        else:
            # 若默认文件夹不存在，创建默认文件夹
            os.makedirs(default_folder_path)
            # 弹出新窗口提示用户保存路径
            self.show_folder_path_popup(default_folder_path)
            return default_folder_path

    def get_user_folder_name(self):
        # 创建一个临时窗口用于获取用户输入的文件夹名
        input_window = tk.Toplevel()
        input_window.title("输入文件夹名")
        tk.Label(input_window, text="请输入存储数据的文件夹名：").pack()
        folder_name_entry = tk.Entry(input_window)
        folder_name_entry.pack()
        def confirm_folder_name():
            folder_path = os.path.join("D:/", folder_name_entry.get())
            if os.path.exists(folder_path):
                messagebox.showerror("错误", "该文件夹已存在，请重新输入！")
                return
            input_window.destroy()
            return folder_path
        tk.Button(input_window, text="确定", command=confirm_folder_name).pack()
        # 等待用户输入并关闭临时窗口
        self.root.wait_window(input_window)
        return confirm_folder_name()

    def show_folder_path_popup(self, folder_path):
        # 创建新窗口用于显示文件夹路径b
        popup_window = tk.Toplevel()
        popup_window.title("文件夹路径提示")

        tk.Label(popup_window, text=f"记账数据将保存至：{folder_path}").pack()

        def close_popup():
            popup_window.destroy()

        tk.Button(popup_window, text="确定", command=close_popup).pack()

        # 等待用户关闭新窗口
        self.root.wait_window(popup_window)

    def create_widgets(self):
        # 月度预算显示
        self.budget_label = tk.Label(self.root, text=f"月度总预算: {self.monthly_budget}", font=("Helvetica", 16))
        self.budget_label.pack(pady=10)

        # 余额显示
        self.balance_label = tk.Label(self.root, text="当月余额: ", font=("Helvetica", 16))
        self.balance_label.pack(pady=10)

        # 最近一次记账日期显示
        self.last_record_date_label = tk.Label(self.root, text="当月最近一次账单日期: ", font=("Helvetica", 16))
        self.last_record_date_label.pack(pady=10)

        # 新增月度预算输入框及设置按钮
        tk.Label(self.root, text="设置月度预算:", font=("Helvetica", 12)).pack()
        self.budget_entry = tk.Entry(self.root)
        self.budget_entry.pack()
        tk.Button(self.root, text="更新预算", font=("Helvetica", 12), command=self.update_budget).pack()

        # 记账输入框和按钮
        tk.Label(self.root, text="记账日期(YYYY-MM-DD):", font=("Helvetica", 12)).pack()
        self.date_entry = tk.Entry(self.root)
        self.date_entry.pack()

        tk.Label(self.root, text="支出金额:", font=("Helvetica", 12)).pack()
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack()

        tk.Label(self.root, text="支出描述:", font=("Helvetica", 12)).pack()
        self.description_entry = tk.Entry(self.root)
        self.description_entry.pack()

        self.record_button = tk.Button(self.root, text="记账", font=("Helvetica", 12), command=self.record_expense)
        self.record_button.pack(pady=10)

        # 查找账单输入框和按钮
        tk.Label(self.root, text="查找账单日期(YYYY-MM-DD):", font=("Helvetica", 12)).pack()
        self.search_date_entry = tk.Entry(self.root)
        self.search_date_entry.pack()

        self.search_button = tk.Button(self.root, text="查找账单", font=("Helvetica", 12), command=self.search_bill)
        self.search_button.pack(pady=10)

    def check_and_update_budget_on_first(self):
        today = datetime.date.today()
        if today.day == 1:
            self.current_month = today.month
            self.balance_label.config(text=f"当月余额: {self.monthly_budget}")

    def load_data_and_update_budget_balance(self):
    # 获取数据文件夹中所有的txt文件
        txt_files = glob.glob(os.path.join(self.folder_path, "*.txt"))
        if txt_files:
        # 按文件名（日期）排序，获取最新的记账文件
            latest_file = max(txt_files, key=os.path.getctime)
            with open(latest_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > 1:  # 确保至少有一行数据（不算标题行）
                    last_data_line = lines[-1].strip()  # 获取最后一行数据（去除首尾空白字符）
                    data_parts = last_data_line.split("\t")
                    if len(data_parts) >= 4:  # 确保分割后的数据部分至少有4个元素（对应需要的列）
                        self.monthly_budget = float(data_parts[3])
                        self.balance = float(data_parts[4])
                        self.budget_label.config(text=f"月度总预算: {self.monthly_budget}")
                        self.balance_label.config(text=f"当月余额: {self.balance}")
                        # 更新最近一次记账日期
                        self.last_record_date = data_parts[0]
                        self.last_record_date_label.config(text=f"当月最近一次账单日期: {self.last_record_date}")


    def update_budget(self):
        try:
            new_budget = float(self.budget_entry.get())
            if new_budget > 0:
                # 获取当月已有账单总支出（通过最近一次记账数据计算）
                total_expense_this_month = self.get_total_expense_this_month()
                # 更新月度预算
                self.monthly_budget = new_budget
                # 根据新预算和已有支出重新计算余额
                self.balance = self.monthly_budget - total_expense_this_month
                self.budget_label.config(text=f"月度总预算: {self.monthly_budget}")
                self.balance_label.config(text=f"当月余额: {self.balance}")
                # 同时更新所有已记录账单文件中的预算和余额信息（遍历文件夹内所有文件进行更新）
                self.update_all_bills_budget_and_balance()
            else:
                messagebox.showerror("错误", "预算金额必须大于0")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字作为预算金额")

    def get_total_expense_this_month(self):
        """
        通过读取最近一次记账数据文件的最后一笔账单记录来计算当月已有账单总支出
        """
        txt_files = glob.glob(os.path.join(self.folder_path, "*.txt"))
        if txt_files:
            latest_file = max(txt_files, key=os.path.getctime)
            with open(latest_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > 1:
                    last_data_line = lines[-1].strip()
                    data_parts = last_data_line.split("\t")
                    if len(data_parts) >= 4:
                        return float(data_parts[3]) - float(data_parts[4])
        return 0

    def update_balance(self):
        today = datetime.date.today()
        total_expense = 0
        for date, date_expenses in self.expenses.items():
            if date.month == today.month and date.year == today.year:
                for expense in date_expenses:
                    total_expense += expense[0]
        self.balance = self.monthly_budget - total_expense
        self.balance_label.config(text=f"当月余额: {self.balance}")

    def record_expense(self):
        date_str = self.date_entry.get()
        try:
            date = datetime.date.fromisoformat(date_str)
            today = datetime.date.today()
            if date.month == today.month and date.year == today.year:
                if date.month!= self.current_month:
                    self.expenses = {}
                    self.current_month = date.month
                amount = float(self.amount_entry.get())
                description = self.description_entry.get()
                if date not in self.expenses:
                    self.expenses[date] = []
                self.expenses[date].append((amount, description))

                file_path = os.path.join(self.folder_path, date_str + ".txt")
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write("记账日期\t金额\t描述\t月度总预算\t当月余额\n")
                with open(file_path, "a", encoding="utf-8") as f:
                    # 记录月度总预算和计算后的余额，使用更新后的预算和余额来记录
                    new_balance = self.balance - amount
                    f.write(f"{date_str}\t{amount}\t{description}\t{self.monthly_budget}\t{new_balance}\n")

                # 更新最近一次记账日期
                self.last_record_date = date_str
                self.last_record_date_label.config(text=f"当月最近一次记账日期: {self.last_record_date}")

                # 更新余额，确保按照当前预算和支出情况准确更新余额
                self.update_balance()
            else:
                # 不是同年同月，仅记录账单信息
                amount = float(self.amount_entry.get())
                description = self.description_entry.get()
                if date not in self.expenses:
                    self.expenses[date] = []
                self.expenses[date].append((amount, description))

                file_path = os.path.join(self.folder_path, date_str + ".txt")
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write("记账日期\t金额\t描述\n")
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(f"{date_str}\t{amount}\t{description}\n")

            self.clear_entries()
        except ValueError:
            messagebox.showerror("错误","记账日期格式应为 YYYY-MM-DD，支出金额应为数字")


    def clear_entries(self):
        self.date_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)

    def search_bill(self):
        date_str = self.search_date_entry.get()
        try:
            date = datetime.date.fromisoformat(date_str)
            file_path = os.path.join(self.folder_path, date_str + ".txt")
            if os.path.exists(file_path):
                bill_info = []
                with open(file_path, "r", encoding="utf-8") as f:
                    # 跳过标题行
                    next(f)
                    for line in f:
                        parts = line.strip().split("\t")
                        amount = float(parts[1])
                        description = parts[2]
                        if len(parts) >= 5:
                            budget = float(parts[3])
                            balance = float(parts[4])
                            bill_info.append(f"金额: {amount}, 描述: {description}, 当月月度总预算: {budget}, 实时余额: {balance}")
                        else:
                            bill_info.append(f"金额: {amount}, 描述: {description}")
                messagebox.showinfo("账单详情", "\n".join(bill_info))
            else:
                messagebox.showinfo("账单详情", "该日无支出记录")
        except ValueError:
            messagebox.showerror("错误", "查找账单日期格式应为 YYYY-MM-DD")

    def run(self):
        self.check_and_update_budget_on_first()  # 启动时先检查一次
        self.root.after(86400000, self.check_daily)  # 每隔一天（86400000毫秒）检查一次是否是1号更新余额
        self.root.mainloop()

    def check_daily(self):
        self.check_and_update_budget_on_first()
        self.root.after(86400000, self.check_daily)  # 继续循环检查


if __name__ == "__main__":
    accounting_gui = AccountingGUI()
    accounting_gui.run()