import json
import os
import tempfile
from urllib.parse import urlparse

import pdfkit
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@login_required
def pdf_generator_page(request):
    """PDF生成ページを表示"""
    return render(request, 'pdf_generator/pdf_generator.html')

@csrf_exempt
@login_required
def generate_pdf_from_url(request):
    """URLからPDFを生成するAPI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url', '').strip()

            if not url:
                return JsonResponse({'error': 'URLが入力されていません'}, status=400)

            # URLの形式をチェック
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # 内部URL（同じドメイン）の場合は特別処理
            from django.http import HttpRequest
            current_domain = request.get_host()
            parsed_url = urlparse(url)

            if parsed_url.netloc == current_domain:
                # 内部URLの場合はURLチェックをスキップ（認証が必要なため）
                print(f"内部URLを処理中: {url}")
            else:
                # 外部URLの場合は通常のチェック
                try:
                    response = requests.head(url, timeout=10, allow_redirects=True)
                    if response.status_code not in [200, 301, 302]:
                        return JsonResponse({'error': f'URLにアクセスできません（ステータスコード: {response.status_code}）'}, status=400)
                except requests.RequestException as e:
                    return JsonResponse({'error': f'URLにアクセスできません: {str(e)}'}, status=400)

            # PDF生成オプション
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }

            # カスタムオプションがあれば追加
            if data.get('page_size'):
                options['page-size'] = data.get('page_size')
            if data.get('orientation'):
                options['orientation'] = data.get('orientation')

            # 一時ファイルにPDFを保存
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                pdf_path = tmp_file.name

            try:
                # PDF生成
                pdfkit.from_url(url, pdf_path, options=options)

                # PDFファイルを読み込み
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()

                # ファイル名を生成
                parsed_url = urlparse(url)
                filename = f"{parsed_url.netloc.replace('.', '_')}.pdf"

                # レスポンスを作成
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'

                return response

            except Exception as e:
                return JsonResponse({'error': f'PDF生成エラー: {str(e)}'}, status=500)
            finally:
                # 一時ファイルを削除
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)

        except json.JSONDecodeError:
            return JsonResponse({'error': '無効なJSONデータです'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'エラーが発生しました: {str(e)}'}, status=500)

    return JsonResponse({'error': 'POSTメソッドのみサポート'}, status=405)

@csrf_exempt
@login_required
def generate_pdf_from_html(request):
    """HTMLからPDFを生成するAPI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            html_content = data.get('html_content', '').strip()
            title = data.get('title', 'generated_document')

            if not html_content:
                return JsonResponse({'error': 'HTMLコンテンツが入力されていません'}, status=400)

            # PDF生成オプション
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }

            # カスタムオプションがあれば追加
            if data.get('page_size'):
                options['page-size'] = data.get('page_size')
            if data.get('orientation'):
                options['orientation'] = data.get('orientation')

            # 一時ファイルにPDFを保存
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                pdf_path = tmp_file.name

            try:
                # PDF生成
                pdfkit.from_string(html_content, pdf_path, options=options)

                # PDFファイルを読み込み
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()

                # レスポンスを作成
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{title}.pdf"'

                return response

            except Exception as e:
                return JsonResponse({'error': f'PDF生成エラー: {str(e)}'}, status=500)
            finally:
                # 一時ファイルを削除
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)

        except json.JSONDecodeError:
            return JsonResponse({'error': '無効なJSONデータです'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'エラーが発生しました: {str(e)}'}, status=500)

    return JsonResponse({'error': 'POSTメソッドのみサポート'}, status=405)

@login_required
def check_wkhtmltopdf(request):
    """wkhtmltopdfのインストール状況をチェック"""
    try:
        # wkhtmltopdfのバージョンを確認
        import subprocess
        result = subprocess.run(['wkhtmltopdf', '--version'],
                              capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            return JsonResponse({
                'installed': True,
                'version': result.stdout.strip(),
                'message': 'wkhtmltopdfが正常にインストールされています'
            })
        else:
            return JsonResponse({
                'installed': False,
                'error': result.stderr.strip(),
                'message': 'wkhtmltopdfの実行に失敗しました'
            })
    except FileNotFoundError:
        return JsonResponse({
            'installed': False,
            'message': 'wkhtmltopdfがインストールされていません。インストールしてください。'
        })
    except Exception as e:
        return JsonResponse({
            'installed': False,
            'error': str(e),
            'message': 'wkhtmltopdfの確認中にエラーが発生しました'
        })
