# AI VTuber Plugins

ระบบปลั๊กอินสำหรับ AI VTuber Desktop Companion ที่ช่วยให้คุณขยายความสามารถของระบบได้อย่างอิสระ

## โครงสร้างโปรเจกต์

```
ai-vtuber-plugins/
├── templates/         # เทมเพลตปลั๊กอินสำหรับเริ่มต้น
│   ├── basic/         # ปลั๊กอินพื้นฐาน
│   ├── assistant/     # ปลั๊กอินช่วยทำงาน
│   ├── game-helper/   # ปลั๊กอินช่วยเล่นเกม
│   └── mini-app/      # มินิแอปพลิเคชัน
├── src/               # ซอร์สโค้ดของระบบปลั๊กอิน
│   ├── loader/        # Plugin Loader
│   ├── api/           # Plugin API
│   └── manager/       # Plugin Manager
├── examples/          # ตัวอย่างปลั๊กอิน
└── docs/              # เอกสาร
```

## การสร้างปลั๊กอินของคุณเอง

### 1. คัดลอกเทมเพลต

```bash
cp -r templates/basic my-plugin
cd my-plugin
```

### 2. แก้ไข plugin.json

```json
{
  "name": "MyAwesomePlugin",
  "version": "1.0.0",
  "description": "My awesome plugin description",
  "author": "Your Name",
  "entry_point": "plugin.py",
  "dependencies": [],
  "permissions": [
    "read_messages",
    "send_messages"
  ],
  "events": {
    "subscribe": [
      "user_message"
    ]
  }
}
```

### 3. เขียนโค้ดปลั๊กอินของคุณ

แก้ไขไฟล์ `plugin.py` ตามตัวอย่างในเทมเพลต

### 4. ทดสอบปลั๊กอิน

(วิธีการทดสอบจะอัปเดตในภายหลัง)

## Plugin API

ดูเอกสาร API ที่ [docs/PLUGIN_API.md](./docs/PLUGIN_API.md)

## ตัวอย่างปลั๊กอิน

- **Weather Plugin:** แสดงสภาพอากาศเมื่อผู้ใช้ถาม
- **Reminder Plugin:** ตั้งเตือนและแจ้งเตือนผู้ใช้
- **Game Helper:** ช่วยเหลือในเกมต่างๆ

## License

MIT
