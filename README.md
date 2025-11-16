!# AI VTuber Desktop Companion

> [!NOTE]
> โครงการนี้เป็นโครงการโอเพนซอร์สที่มุ่งสร้าง "เพื่อนคุย" แบบ AI VTuber บนเดสก์ท็อปที่สามารถปรับแต่งและขยายความสามารถได้

**AI VTuber Desktop Companion** คือเพื่อนคู่ใจบนเดสก์ท็อปของคุณที่ขับเคลื่อนด้วย AI, สามารถพูดคุย, แสดงอารมณ์, และโต้ตอบกับคุณได้แบบเรียลไทม์ โปรเจกต์นี้ถูกออกแบบมาให้เป็นแบบ **modular** และ **customizable** ทำให้คุณสามารถเปลี่ยนโมเดลภาษา (LLM), ระบบเสียง (TTS/STT), และแม้กระทั่งตัวละคร VTuber ได้อย่างอิสระ

## คุณสมบัติหลัก

- **Transparent Overlay:** ตัวละคร VTuber จะแสดงผลอยู่บนเดสก์ท็อปของคุณโดยไม่บดบังหน้าต่างอื่น
- **Interactive Conversation:** พูดคุยกับ AI ได้อย่างเป็นธรรมชาติผ่านเสียงหรือข้อความ
- **Emotional Expression:** Avatar สามารถแสดงอารมณ์ได้สอดคล้องกับบทสนทนา
- **Plugin System:** ขยายความสามารถได้ไม่จำกัดด้วยระบบปลั๊กอิน เช่น เครื่องมือช่วยทำงาน, มินิเกม, หรือการเชื่อมต่อกับแอปอื่น
- **Customizable:** เปลี่ยนได้ทั้งโมเดล AI, เสียง, และตัวละคร VTuber
- **Privacy-Focused:** ออกแบบโดยคำนึงถึงความเป็นส่วนตัวของผู้ใช้เป็นอันดับแรก

## Roadmap

ดูแผนงานการพัฒนาทั้งหมดได้ที่ [Roadmap & แผนงานการสร้าง AI VTuber Desktop Companion](https://www.notion.so/Roadmap-AI-VTuber-Desktop-Companion-ฉบับพร้อมเริ่ม-e5a1b1c7b5a84f6b9a7d8e2f3c4d5e6f)

## การติดตั้งและเริ่มต้นใช้งาน

(ส่วนนี้จะถูกอัปเดตเมื่อมีเวอร์ชันแรกออกมา)

## การมีส่วนร่วม

เรายินดีต้อนรับผู้ร่วมพัฒนาทุกคน! ไม่ว่าคุณจะเป็นโปรแกรมเมอร์, ศิลปิน, หรือผู้ใช้งานทั่วไป คุณก็สามารถมีส่วนร่วมกับโปรเจกต์นี้ได้ อ่านรายละเอียดเพิ่มเติมได้ที่ [CONTRIBUTING.md](./CONTRIBUTING.md)

## Repository

โปรเจกต์นี้แบ่งออกเป็น 7 repository หลัก:

| Repository | คำอธิบาย | ภาษาหลัก |
|---|---|---|
| `ai-vtuber-core` | ส่วนแกนหลักของ AI, LLM, TTS/STT, และระบบจัดการอีเวนต์ | Python/Node.js |
| `ai-vtuber-desktop-client` | แอปพลิเคชันบนเดสก์ท็อป (Electron) และ UI | TypeScript/Electron |
| `ai-vtuber-avatar-engine` | ระบบจัดการและแสดงผล Avatar (Live2D/VRM) | TypeScript/C++ |
| `ai-vtuber-plugins` | เทมเพลตและ API สำหรับสร้างปลั๊กอิน | TypeScript/Python |
| `ai-vtuber-docs` | เอกสารทั้งหมดของโปรเจกต์ | Markdown/MDX |
| `ai-vtuber-models` | โมเดล Avatar และ Animation ตัวอย่าง | JSON/Asset |
| `ai-vtuber-community` | พื้นที่สำหรับพูดคุย, แจ้งปัญหา, และแสดงผลงาน | Markdown |

## License

โปรเจกต์นี้ใช้สัญญาอนุญาตแบบ Apache 2.0 และ MIT สำหรับโค้ด และ Creative Commons (CC BY 4.0) สำหรับโมเดลและเนื้อหาอื่นๆ ดูรายละเอียดที่ไฟล์ [LICENSE](./LICENSE)
