from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView


@method_decorator(login_required(login_url='accounts:login'), name='dispatch')
class DashboardView(TemplateView):
    """ 認証が必要なダッシュボードビュー """
    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        # 親クラスのコンテキストを取得
        context = super().get_context_data(**kwargs)

        # ユーザー情報を追加
        context['user'] = self.request.user

        # 現在の日時を追加
        context['current_time'] = datetime.now()

        # ユーザーの登録からの経過日数を計算
        if self.request.user.created_at:
            days_since_joined = (datetime.now().date() - self.request.user.created_at.date()).days
            context['days_since_joined'] = days_since_joined

        # ダッシュボードの統計情報（例）
        context['stats'] = {
            'total_users': 100,  # 実際はデータベースから取得
            'active_users': 75,
            'new_users_today': 5
        }

        return context


@method_decorator(login_required(login_url='accounts:login'), name='dispatch')
class ProfileView(TemplateView):
    """ 認証が必要なプロフィールビュー """
    template_name = "dashboard/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        # プロフィール専用のデータ
        context['profile_complete'] = all([
            self.request.user.first_name,
            self.request.user.last_name,
            self.request.user.email
        ])

        return context
