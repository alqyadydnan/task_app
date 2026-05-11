# main.py
import sqlite3
from datetime import datetime
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.picker import MDDatePicker

# تصميم الواجهة (KV Language)
KV = '''
ScreenManager:
    MainScreen:
    AddTaskScreen:

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'مدير المهام'
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            right_action_items: [['plus', lambda x: root.go_to_add_task()]]

        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(10)
            spacing: dp(10)

            MDLabel:
                text: 'مهامي اليومية'
                font_style: 'H5'
                halign: 'center'
                size_hint_y: None
                height: self.texture_size[1] + dp(20)

            ScrollView:
                MDList:
                    id: task_list
                    spacing: dp(5)

        MDRectangleFlatButton:
            text: 'حذف جميع المهام'
            pos_hint: {'center_x': 0.5}
            size_hint: (0.8, None)
            height: dp(50)
            md_bg_color: 0.8, 0.2, 0.2, 1
            text_color: 1, 1, 1, 1
            on_release: root.delete_all_tasks()

<AddTaskScreen>:
    name: 'add_task'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'إضافة مهمة جديدة'
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [['arrow-left', lambda x: root.go_back()]]

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(15)
                size_hint_y: None
                height: self.minimum_height

                MDTextField:
                    id: task_title
                    hint_text: 'عنوان المهمة'
                    required: True
                    mode: 'rectangle'
                    size_hint_x: 1

                MDTextField:
                    id: task_desc
                    hint_text: 'وصف المهمة (اختياري)'
                    mode: 'rectangle'
                    multiline: True
                    size_hint_y: None
                    height: dp(100)

                MDBoxLayout:
                    orientation: 'horizontal'
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(50)

                    MDLabel:
                        text: 'تاريخ الاستحقاق:'
                        size_hint_x: 0.4

                    MDLabel:
                        id: selected_date
                        text: 'لم يتم الاختيار'
                        size_hint_x: 0.6

                    MDRaisedButton:
                        text: 'اختر التاريخ'
                        size_hint_x: 1
                        on_release: root.show_date_picker()

                MDRaisedButton:
                    text: 'إضافة المهمة'
                    md_bg_color: app.theme_cls.primary_color
                    size_hint_x: 1
                    size_hint_y: None
                    height: dp(50)
                    on_release: root.add_task()
'''

# إنشاء كلاس لعنصر القائمة
class TaskItem(OneLineListItem):
    def __init__(self, task_id, title, completed, **kwargs):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.text = title
        self.completed = completed

        # إضافة checkbox
        self.check = Checkbox()
        self.check.active = bool(completed)
        self.check.bind(active=self.on_checkbox_toggle)

        # زر الحذف
        self.delete_btn = Button(text='X', size_hint=(None, None), size=(dp(40), dp(40)))
        self.delete_btn.bind(on_release=self.delete_task)

        layout = BoxLayout(orientation='horizontal', spacing=dp(10))
        layout.add_widget(self.check)
        layout.add_widget(Label(text=title))
        layout.add_widget(self.delete_btn)
        self.add_widget(layout)

    def on_checkbox_toggle(self, checkbox, value):
        app = MDApp.get_running_app()
        app.update_task_status(self.task_id, value)

    def delete_task(self, instance):
        app = MDApp.get_running_app()
        app.delete_task(self.task_id)

# الشاشة الرئيسية
class MainScreen(Screen):
    def on_enter(self):
        app = MDApp.get_running_app()
        app.load_tasks()

    def go_to_add_task(self):
        self.manager.current = 'add_task'

    def delete_all_tasks(self):
        dialog = MDDialog(
            title='تأكيد الحذف',
            text='هل أنت متأكد من حذف جميع المهام؟',
            buttons=[
                MDFlatButton(text='إلغاء', on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text='حذف', on_release=lambda x: self.confirm_delete_all(dialog))
            ]
        )
        dialog.open()

    def confirm_delete_all(self, dialog):
        app = MDApp.get_running_app()
        app.delete_all_tasks()
        dialog.dismiss()

# شاشة إضافة مهمة جديدة
class AddTaskScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_date = None

    def go_back(self):
        self.manager.current = 'main'
        self.clear_fields()

    def show_date_picker(self):
        date_dialog = MDDatePicker(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.selected_date = value
        self.ids.selected_date.text = value.strftime('%Y-%m-%d')

    def add_task(self):
        title = self.ids.task_title.text.strip()
        desc = self.ids.task_desc.text.strip()

        if not title:
            dialog = MDDialog(title='خطأ', text='يرجى إدخال عنوان المهمة')
            dialog.open()
            return

        app = MDApp.get_running_app()
        app.add_task_to_db(title, desc, self.selected_date)
        self.go_back()

    def clear_fields(self):
        self.ids.task_title.text = ''
        self.ids.task_desc.text = ''
        self.ids.selected_date.text = 'لم يتم الاختيار'
        self.selected_date = None

# التطبيق الرئيسي
class TaskManagerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = 'Orange'
        self.theme_cls.theme_style = 'Light'

    def build(self):
        self.init_database()
        return Builder.load_string(KV)

    def init_database(self):
        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT
            )
        ''')
        self.conn.commit()

    def add_task_to_db(self, title, description, due_date):
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        due_date_str = due_date.strftime('%Y-%m-%d') if due_date else None

        self.cursor.execute(
            'INSERT INTO tasks (title, description, due_date, completed, created_at) VALUES (?, ?, ?, ?, ?)',
            (title, description, due_date_str, 0, created_at)
        )
        self.conn.commit()

    def load_tasks(self):
        self.cursor.execute('SELECT id, title, completed, due_date FROM tasks ORDER BY completed ASC, created_at DESC')
        tasks = self.cursor.fetchall()

        task_list = self.root.get_screen('main').ids.task_list
        task_list.clear_widgets()

        styles = {
            'active': '[color=#4CAF50][b]{}[/b][/color]',
            'inactive': '[color=#FF5722][b]{}[/b][/color]',
            'completed': '[color=#999999][s][b]{}[/b][/s][/color]'
        }

        for task_id, title, completed, due_date in tasks:
            if completed:
                text_line = f'{title} ✅'
                secondary_text = f'📅 {due_date}' if due_date else ''
                icon = 'checkbox-marked-circle-outline'
                icon_color = (0.6, 0.6, 0.6, 1)
            else:
                text_line = title
                secondary_text = f'⏰ {due_date}' if due_date else ''
                icon = 'checkbox-blank-circle-outline'
                icon_color = (1, 0.5, 0, 1)

            item = OneLineIconListItem(IconLeftWidget(icon=icon, theme_text_color='Custom', text_color=icon_color))
            item.text = text_line
            item.secondary_text = secondary_text
            item.bind(on_release=lambda x, tid=task_id, comp=completed: self.toggle_task(tid, comp))
            task_list.add_widget(item)

    def toggle_task(self, task_id, current_status):
        new_status = 0 if current_status else 1
        self.cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new_status, task_id))
        self.conn.commit()
        self.load_tasks()

    def delete_task(self, task_id):
        self.cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        self.load_tasks()

    def update_task_status(self, task_id, status):
        self.cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (1 if status else 0, task_id))
        self.conn.commit()
        self.load_tasks()

    def delete_all_tasks(self):
        self.cursor.execute('DELETE FROM tasks')
        self.conn.commit()
        self.load_tasks()

if __name__ == '__main__':
    TaskManagerApp().run()