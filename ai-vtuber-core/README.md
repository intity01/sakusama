# AI VTuber Core

ส่วนแกนหลักของระบบ AI VTuber Desktop Companion ที่รับผิดชอบการประมวลผล AI, การจัดการเสียง, และระบบความจำ

## โครงสร้างโปรเจกต์

```
ai-vtuber-core/
├── src/
│   ├── llm/           # โมดูล Large Language Model
│   ├── tts/           # โมดูล Text-to-Speech
│   ├── stt/           # โมดูล Speech-to-Text
│   ├── memory/        # ระบบความจำและ Vector Database
│   ├── events/        # Event Bus และ Event Handlers
│   └── plugins/       # Plugin Interface สำหรับ Core
├── tests/             # Unit tests และ Integration tests
├── docs/              # เอกสารเฉพาะโมดูล
├── examples/          # ตัวอย่างการใช้งาน
└── config/            # Configuration templates
```

## คุณสมบัติหลัก

- **Modular LLM Support:** รองรับหลาย LLM provider (OpenAI, Ollama, LangChain)
- **Flexible TTS/STT:** เปลี่ยน engine ได้ตามต้องการ
- **Vector Memory:** จัดเก็บและค้นหา context ด้วย Vector Database
- **Event-Driven:** สื่อสารผ่าน Event Bus เพื่อความยืดหยุ่น
- **Plugin-Ready:** รองรับการเชื่อมต่อกับปลั๊กอินภายนอก

## การติดตั้ง

(จะอัปเดตเมื่อมีเวอร์ชันแรก)

## การใช้งานเบื้องต้น

(จะอัปเดตเมื่อมีเวอร์ชันแรก)

## API Documentation

ดูเอกสาร API ที่ [docs/API.md](./docs/API.md)

## License

Apache 2.0 / MIT
