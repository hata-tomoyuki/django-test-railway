import base64
import io
import json
import os

import cv2
import numpy as np
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

# OCRライブラリのインポート（オプション）
try:
    import pyocr
    import pyocr.builders
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

@login_required
def handwriting_page(request):
    """手書き文字認識ページを表示"""
    return render(request, 'handwriting_ocr/handwriting.html')

@csrf_exempt
@login_required
def recognize_handwriting(request):
    """手書き文字を認識するAPI"""
    if request.method == 'POST':
        try:
                        # フロントエンドから送信された画像データを取得
            data = json.loads(request.body)
            image_data = data.get('image')
            language = data.get('language', 'jpn')  # デフォルトは日本語

            if not image_data:
                return JsonResponse({'error': '画像データがありません'}, status=400)

            # Base64データから画像を復元
            image_data = image_data.split(',')[1]  # "data:image/png;base64," の部分を除去
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # 画像をOpenCV形式に変換
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                                    # 画像の前処理
            processed_image = preprocess_image(cv_image)

            # デバッグ用に画像を保存
            cv2.imwrite('debug_original.png', cv_image)
            cv2.imwrite('debug_processed.png', processed_image)
            print("Debug images saved: debug_original.png, debug_processed.png")

            # OCR実行（Tesseractが利用可能な場合）
            if OCR_AVAILABLE:
                recognized_text = perform_ocr(processed_image, language)
            else:
                # モック実装（Tesseractが利用できない場合）
                recognized_text = "OCR機能は利用できません。Tesseractをインストールしてください。"

            return JsonResponse({
                'success': True,
                'recognized_text': recognized_text
            })

        except Exception as e:
            return JsonResponse({
                'error': f'エラーが発生しました: {str(e)}'
            }, status=500)

    return JsonResponse({'error': 'POSTメソッドのみサポート'}, status=405)

def preprocess_image(image):
    """画像の前処理を行う"""
    # グレースケール変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 画像のサイズを確認
    print(f"Original image shape: {image.shape}")
    print(f"Gray image shape: {gray.shape}")

    # 画像を拡大（Tesseractの精度向上のため）
    scale_factor = 3
    enlarged = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)

    # ガウシアンフィルタでノイズ除去
    blurred = cv2.GaussianBlur(enlarged, (3, 3), 0)

    # アダプティブ閾値処理（手書き文字に適している）
    adaptive_thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # モルフォロジー処理でノイズ除去
    kernel = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)

    # 境界を白で囲む（Tesseractの精度向上のため）
    bordered = cv2.copyMakeBorder(cleaned, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=255)

    # 画像を反転（黒背景に白文字）
    final_image = cv2.bitwise_not(bordered)

    return final_image

def perform_ocr(image, language='jpn'):
    """OCRを実行する"""
    try:
        # Tesseractのパスを設定（macOSの場合）
        tesseract_path = '/usr/local/bin/tesseract'
        if os.path.exists(tesseract_path):
            pyocr.tesseract.TESSERACT_CMD = tesseract_path

        # 利用可能なツールを取得
        tools = pyocr.get_available_tools()
        if not tools:
            return "Tesseractが見つかりません"

        tool = tools[0]

        # PIL Imageに変換
        pil_image = Image.fromarray(image)

        # OCR実行（デバッグ用にログを追加）
        print(f"Tesseract path: {pyocr.tesseract.TESSERACT_CMD}")
        print(f"Available tools: {tools}")
        print(f"Image size: {pil_image.size}")
        print(f"Language: {language}")

                # 手書き文字認識に適した設定（参考記事の設定を参考）
        text = tool.image_to_string(
            pil_image,
            lang=language,  # フロントエンドから送信された言語
            builder=pyocr.builders.TextBuilder(tesseract_layout=6)  # 統一されたブロックのテキスト
        )

        print(f"OCR result: {text}")

        return text.strip() if text else "文字が認識できませんでした"

    except Exception as e:
        print(f"OCR error: {str(e)}")
        return f"OCRエラー: {str(e)}"
