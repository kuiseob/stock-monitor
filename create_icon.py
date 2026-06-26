#!/usr/bin/env python3
"""
Stock Monitor용 Windows 아이콘 생성 스크립트

이 스크립트는 Pillow를 사용하여 간단한 아이콘을 생성합니다.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Stock Monitor 아이콘 생성"""

    # 아이콘 크기
    size = 256

    # 새 이미지 생성 (흰색 배경)
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)

    # 배경 그라디언트 효과 (파란색)
    for i in range(size):
        color = (int(102 + (153-102) * i / size),
                int(178 + (229-178) * i / size),
                int(255))
        draw.line([(0, i), (size, i)], fill=color)

    # 텍스트 추가
    try:
        # 큰 폰트 찾기 (Windows 기본 폰트)
        font_size = 80
        font_paths = [
            "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\Arial.ttf",
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Linux
        ]

        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break

        if font is None:
            font = ImageFont.load_default()
    except Exception as e:
        print(f"[Warning] 폰트 로드 실패: {e}")
        font = ImageFont.load_default()

    # 📈 차트 아이콘 그리기
    # Y축
    draw.line([(40, 200), (40, 60)], fill='white', width=3)
    # X축
    draw.line([(40, 200), (240, 200)], fill='white', width=3)

    # 차트 라인 (상승)
    points = [
        (60, 170),
        (100, 140),
        (140, 110),
        (180, 80),
        (220, 50)
    ]
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill='#00FF00', width=3)

    # 점 표시
    for point in points:
        draw.ellipse([point[0]-5, point[1]-5, point[0]+5, point[1]+5],
                    fill='#00FF00')

    # 텍스트 "SM" (Stock Monitor)
    text = "SM"
    try:
        # 텍스트 위치 계산
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = size - text_height - 20

        draw.text((x, y), text, fill='white', font=font)
    except:
        pass

    # ICO 파일로 저장
    ico_path = "stock-monitor.ico"
    img.save(ico_path, 'ICO', sizes=[(256, 256)])

    print(f"[SUCCESS] 아이콘 생성 완료: {ico_path}")
    print(f"파일 크기: {os.path.getsize(ico_path)} bytes")

    return True

if __name__ == "__main__":
    try:
        create_icon()
    except Exception as e:
        print(f"[ERROR] 아이콘 생성 실패: {e}")
        print("\n[INFO] Pillow 설치 중...")
        import subprocess
        subprocess.run("pip install pillow", shell=True)
        create_icon()
