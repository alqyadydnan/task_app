[app]

title = My Tasks
package.name = mytasks
package.domain = org.myapp

requirements = python3,kivy==2.1.0,kivymd==1.1.1

version = 1.0
orientation = portrait

# 🔥 الأهم: لا تضع أي إعدادات لـ android.api أو build-tools هنا
# دع Buildozer يستخدم الإعدادات الافتراضية

source.dir = .
source.include_exts = py

# اسمح بالتحذيرات
ignore_gradle_warning = True
