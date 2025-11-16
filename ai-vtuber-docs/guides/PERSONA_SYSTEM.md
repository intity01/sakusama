# Persona System Guide

เอกสารนี้อธิบายการทำงานของระบบ Persona ซึ่งช่วยให้ AI VTuber สามารถมีบุคลิกและรูปแบบการตอบสนองที่หลากหลายได้

## ภาพรวม

Persona Engine เป็นโมดูลที่ทำหน้าที่ปรับเปลี่ยนพฤติกรรมของ LLM ตามโปรไฟล์ที่ผู้ใช้เลือก ทำให้ผู้ใช้สามารถเปลี่ยน AI จาก "ผู้ช่วยส่วนตัว" เป็น "เพื่อนสนิท" หรือ "ตัวละครในเกม" ได้อย่างง่ายดาย

## ส่วนประกอบหลัก

### Persona Engine

เป็นโมดูลหลักที่รับผิดชอบการโหลด, จัดการ, และปรับใช้ Persona

### Persona Profiles

เป็นไฟล์ JSON หรือ YAML ที่กำหนดคุณลักษณะของแต่ละ Persona โดยมีโครงสร้างดังนี้:

```yaml
name: "Luna the Playful Friend"
version: "1.0"
description: "A cheerful and playful friend who loves to joke around."
author: "Community User"

# LLM Configuration
llm_config:
  system_prompt: >
    You are Luna, a cheerful and playful VTuber. 
    You love to use emojis and make jokes. 
    You are always supportive and try to make the user smile.
  temperature: 0.85
  top_p: 0.9
  response_length: "short"

# Voice Configuration
tts_config:
  voice: "luna_voice_model"
  pitch: 1.2
  speed: 1.1

# Behavior Rules
behavior:
  greeting: ["Hey there!", "What's up?", "Hiii!"]
  farewell: ["See ya!", "Bye bye!", "Catch you later!"]
  use_emojis: true
  joke_frequency: 0.3 # 30% chance to tell a joke

# Emotion Mapping Override
emotion_map:
  happy: "excited_jump"
  sad: "pout"
```

### การทำงาน

1.  **Loading:** เมื่อผู้ใช้เลือก Persona, `Persona Engine` จะโหลดไฟล์โปรไฟล์ที่เกี่ยวข้อง
2.  **Applying:**
    *   `system_prompt` และ `llm_config` จะถูกส่งไปอัปเดต `LLM Module`
    *   `tts_config` จะถูกส่งไปอัปเดต `TTS Module`
    *   `behavior` จะถูกใช้โดย `Context Manager` เพื่อปรับแต่งการตอบสนอง (เช่น การสุ่มคำทักทาย)
    *   `emotion_map` จะ override การตั้งค่าเริ่มต้นใน `Expression Mapper`
3.  **Real-time Switching:** การเปลี่ยน Persona สามารถทำได้แบบเรียลไทม์ ทำให้ผู้ใช้สามารถสลับบุคลิกของ AI ได้ทันที

## การสร้าง Persona ของคุณเอง

1.  สร้างไฟล์ `.yaml` หรือ `.json` ตามโครงสร้างด้านบน
2.  นำไฟล์ไปไว้ในไดเรกทอรี `ai-vtuber-models/personas/`
3.  โปรแกรมจะตรวจจับและแสดง Persona ใหม่ในเมนูให้เลือกโดยอัตโนมัติ

## การพัฒนาในอนาคต

- **Persona Training:** ระบบจะเรียนรู้จากสไตล์การคุยของผู้ใช้เพื่อปรับ Persona ให้เข้ากันมากยิ่งขึ้น
- **Persona Marketplace:** ผู้ใช้สามารถแชร์และดาวน์โหลด Persona ที่สร้างโดย community ได้
