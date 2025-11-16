# Getting Started with AI VTuber Desktop Companion

ยินดีต้อนรับสู่ AI VTuber Desktop Companion! คู่มือนี้จะช่วยให้คุณเริ่มต้นใช้งานได้อย่างรวดเร็ว

## ความต้องการของระบบ

ก่อนเริ่มต้น โปรดตรวจสอบว่าเครื่องของคุณมีสเปคตามที่กำหนด

**ระบบปฏิบัติการ**
- Windows 10 หรือใหม่กว่า
- macOS 12 (Monterey) หรือใหม่กว่า
- Ubuntu 20.04 LTS หรือใหม่กว่า

**ฮาร์ดแวร์**
- CPU: Intel Core i5 หรือเทียบเท่า (แนะนำ i7 ขึ้นไป)
- RAM: 8 GB ขึ้นไป (แนะนำ 16 GB)
- GPU: การ์ดจอที่รองรับ WebGL 2.0
- พื้นที่ว่าง: 2 GB ขึ้นไป

**ซอฟต์แวร์**
- Python 3.9 ขึ้นไป
- Node.js 18 ขึ้นไป
- Git

## การติดตั้ง

(ส่วนนี้จะอัปเดตเมื่อมีเวอร์ชันแรกออกมา)

### ขั้นตอนที่ 1: ดาวน์โหลด

### ขั้นตอนที่ 2: ติดตั้ง Dependencies

### ขั้นตอนที่ 3: ตั้งค่า Configuration

### ขั้นตอนที่ 4: เริ่มต้นใช้งาน

## การตั้งค่าเบื้องต้น

### การเลือก LLM Provider

คุณสามารถเลือกใช้ LLM provider ได้หลายแบบ

**OpenAI** - ใช้งานง่าย คุณภาพสูง แต่มีค่าใช้จ่าย
- ต้องการ API key จาก OpenAI
- รองรับ GPT-4, GPT-3.5

**Ollama** - ใช้งานฟรี รันบนเครื่องของคุณเอง
- ต้องติดตั้ง Ollama บนเครื่อง
- รองรับหลายโมเดล เช่น Llama 2, Mistral

**LangChain** - ยืดหยุ่นสูง รองรับหลาย provider
- สามารถสลับ provider ได้ง่าย
- รองรับ custom model

### การเลือก Avatar

ระบบรองรับ avatar 2 ประเภท

**Live2D** - เหมาะสำหรับ 2D anime-style character
- ต้องการไฟล์ .moc3
- animation ลื่นไหลและสวยงาม

**VRM** - เหมาะสำหรับ 3D character
- ต้องการไฟล์ .vrm
- รองรับ standard VRM

## ตัวอย่างการใช้งาน

(จะอัปเดตในภายหลัง)

## ปัญหาที่พบบ่อย

ดูที่ [Troubleshooting Guide](../troubleshooting/README.md)

## ขั้นตอนถัดไป

- อ่าน [Architecture Documentation](../architecture/README.md) เพื่อเข้าใจโครงสร้างของระบบ
- ดู [Plugin Development Guide](../guides/plugin-development.md) เพื่อสร้างปลั๊กอินของคุณเอง
- เข้าร่วม [Community](https://github.com/your-org/ai-vtuber-community) เพื่อแบ่งปันประสบการณ์
