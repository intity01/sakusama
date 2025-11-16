# AI VTuber Avatar Engine

ระบบจัดการและแสดงผล Avatar สำหรับ AI VTuber Desktop Companion รองรับทั้ง Live2D และ VRM

## โครงสร้างโปรเจกต์

```
ai-vtuber-avatar-engine/
├── src/
│   ├── live2d/        # Live2D Cubism SDK integration
│   ├── vrm/           # VRM renderer (Three.js based)
│   ├── animation/     # Animation controller
│   └── expression/    # Expression mapper
├── assets/            # Sample avatars and animations
├── tests/             # Tests
├── docs/              # Documentation
└── examples/          # Example configurations
```

## คุณสมบัติหลัก

- **Multi-Format Support:** รองรับทั้ง Live2D (.moc3) และ VRM (.vrm)
- **Emotion Mapping:** แปลง emotion tag จาก AI เป็น animation อัตโนมัติ
- **Smooth Transitions:** การเปลี่ยนอารมณ์และ animation แบบ smooth
- **Customizable:** ปรับแต่ง emotion mapping และ animation ได้
- **Performance Optimized:** ใช้ WebGL สำหรับการ render ที่รวดเร็ว

## Emotion Mapping

ระบบใช้ไฟล์ JSON ในการกำหนดว่า emotion แต่ละอย่างจะแสดงผลอย่างไร ดูตัวอย่างที่ [examples/emotion_mapping.json](./examples/emotion_mapping.json)

## การติดตั้ง

(จะอัปเดตเมื่อมีเวอร์ชันแรก)

## License

MIT
