# 🤖 AI VTuber Core

**AI VTuber Core** คือส่วนหัวใจหลักของ AI VTuber Desktop Companion ที่รวมระบบ AI, LLM Integration, Memory System, Persona Engine, และ TTS/STT เข้าด้วยกัน

โปรเจกต์นี้เป็นส่วนหนึ่งของ [sakusama](https://github.com/intity01/sakusama) - AI VTuber Desktop Companion ที่เป็น Open Source

---

## ✨ คุณสมบัติหลัก

-   **🧠 LLM Integration:** รองรับ OpenAI, Google Gemini, และ Ollama (Local LLM)
-   **💾 Memory System:** จัดเก็บบทสนทนาด้วยการเข้ารหัส AES-256
-   **🎭 Persona Engine:** ระบบบุคลิกที่ปรับแต่งได้ (Luna, Sage, Saku)
-   **🔊 TTS (Text-to-Speech):** รองรับ pyttsx3 (Offline) และ Edge TTS (Cloud)
-   **📡 Event Bus System:** สถาปัตยกรรมแบบ Event-Driven
-   **🛡️ Error Handling:** ระบบจัดการข้อผิดพลาดที่แข็งแกร่ง

---

## 🚀 เริ่มต้นใช้งาน

### 1. ติดตั้ง

```bash
# Clone repository
git clone https://github.com/intity01/sakusama.git
cd sakusama/ai-vtuber-core

# สร้าง Virtual Environment
python -m venv venv

# เปิดใช้งาน Virtual Environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# ติดตั้ง Dependencies
pip install -r requirements.txt
```

### 2. ตั้งค่า

```bash
# คัดลอกไฟล์ Config ตัวอย่าง
copy config\config.example.json config\config.json

# แก้ไข config.json (ใส่ API Keys, เลือก LLM Provider, ตั้งค่า TTS)
notepad config\config.json
```

### 3. รัน Demo

```bash
python demo_cli.py
```

---

## 📚 เอกสาร

-   **[INSTALLATION.md](docs/INSTALLATION.md)** - คู่มือการติดตั้งแบบละเอียด
-   **[TTS_GUIDE.md](docs/TTS_GUIDE.md)** - คู่มือการใช้งานและแก้ไขปัญหา TTS
-   **[ARCHITECTURE.md](../ARCHITECTURE.md)** - สถาปัตยกรรมของระบบ
-   **[CONTRIBUTING.md](../CONTRIBUTING.md)** - แนวทางการมีส่วนร่วม

---

## 🎤 การหา Voice Index สำหรับ TTS

ถ้าคุณใช้ `pyttsx3` และต้องการเปลี่ยนเสียงพูด (เช่น เป็นภาษาไทย) ให้รันสคริปต์นี้:

```bash
python find_voices.py
```

สคริปต์จะแสดงรายการเสียงทั้งหมดที่มีในเครื่องของคุณ พร้อมเลข `Index` ที่คุณสามารถนำไปใส่ใน `config.json` ได้

---

## 🗂️ โครงสร้างโปรเจกต์

```
ai-vtuber-core/
├── config/                 # ไฟล์ Config
│   ├── config.example.json # ตัวอย่าง Config
│   └── config.json         # Config จริง (ไม่ถูก commit)
├── data/                   # ข้อมูลและ Cache
│   ├── memory/             # ข้อมูล Memory ที่เข้ารหัส
│   └── tts_cache/          # Cache ไฟล์เสียง TTS
├── docs/                   # เอกสาร
├── personas/               # ไฟล์ Persona (YAML)
│   ├── luna.yaml
│   ├── sage.yaml
│   └── saku.yaml
├── src/                    # Source Code
│   ├── events/             # Event Bus System
│   ├── error/              # Error Handler
│   ├── llm/                # LLM Integration
│   ├── memory/             # Memory System
│   ├── persona/            # Persona Engine
│   └── tts/                # TTS Module
├── demo_cli.py             # CLI Demo Application
├── find_voices.py          # สคริปต์หา Voice Index
└── requirements.txt        # Python Dependencies
```

---

## 🤝 การมีส่วนร่วม

เรายินดีต้อนรับผู้ร่วมพัฒนาทุกคน! อ่านรายละเอียดได้ที่ [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## ⚖️ สัญญาอนุญาต

โปรเจกต์นี้ใช้สัญญาอนุญาตแบบ Apache 2.0 และ MIT - ดูรายละเอียดที่ [LICENSE](../LICENSE)

---

## 🔗 ลิงก์ที่เกี่ยวข้อง

-   **Repository หลัก:** [sakusama](https://github.com/intity01/sakusama)
-   **เอกสารหลัก:** [ai-vtuber-docs](https://github.com/intity01/sakusama/tree/master/ai-vtuber-docs)
-   **Community:** [ai-vtuber-community](https://github.com/intity01/sakusama/tree/master/ai-vtuber-community)
