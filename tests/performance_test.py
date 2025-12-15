"""
パフォーマンステストスクリプト

API応答時間を測定し、パフォーマンス基準を満たしているか確認します。

使用方法:
    pytest tests/performance_test.py -v -s
"""

import time
import statistics
import pytest


def measure_endpoint_performance(client, method, endpoint, data=None, iterations=100):
    """エンドポイントのパフォーマンス測定"""
    response_times = []
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        
        if method == 'GET':
            response = client.get(endpoint)
        elif method == 'POST':
            response = client.post(endpoint, json=data)
        elif method == 'DELETE':
            response = client.delete(endpoint, json=data)
        
        end_time = time.perf_counter()
        
        # 正常なレスポンスの場合のみ測定
        if 200 <= response.status_code < 300:
            response_times.append((end_time - start_time) * 1000)  # ミリ秒に変換
    
    if not response_times:
        return None
    
    return {
        'mean': statistics.mean(response_times),
        'median': statistics.median(response_times),
        'min': min(response_times),
        'max': max(response_times),
        'stdev': statistics.stdev(response_times) if len(response_times) > 1 else 0,
        'successful_requests': len(response_times),
        'total_requests': iterations
    }


def print_results(results):
    """結果の表示"""
    if results is None:
        print("  ❌ 測定失敗（レスポンスエラー）")
        return
    
    print(f"  平均応答時間: {results['mean']:.2f}ms")
    print(f"  中央値:       {results['median']:.2f}ms")
    print(f"  最小値:       {results['min']:.2f}ms")
    print(f"  最大値:       {results['max']:.2f}ms")
    print(f"  標準偏差:     {results['stdev']:.2f}ms")
    print(f"  成功リクエスト: {results['successful_requests']}/{results['total_requests']}")


def check_performance(results, threshold):
    """パフォーマンス基準のチェック"""
    if results is None:
        print(f"  ⚠️  パフォーマンスチェック: 失敗")
        return False
    
    if results['mean'] <= threshold:
        print(f"  ✅ パフォーマンス基準: 合格 (平均 {results['mean']:.2f}ms <= {threshold}ms)")
        return True
    else:
        print(f"  ⚠️  パフォーマンス基準: 要改善 (平均 {results['mean']:.2f}ms > {threshold}ms)")
        return False


class TestPerformance:
    """パフォーマンステスト"""
    
    def test_get_index_performance(self, client):
        """GET / のパフォーマンステスト"""
        print("\n📊 Test: GET / (メインページ)")
        results = measure_endpoint_performance(client, 'GET', '/')
        print_results(results)
        assert check_performance(results, threshold=50), "メインページのレスポンスが遅すぎます"
    
    def test_post_session_start_performance(self, client):
        """POST /api/session/start のパフォーマンステスト"""
        print("\n📊 Test: POST /api/session/start (セッション開始)")
        results = measure_endpoint_performance(
            client, 
            'POST', 
            '/api/session/start', 
            data={'type': 'work'}
        )
        print_results(results)
        assert check_performance(results, threshold=10), "セッション開始のレスポンスが遅すぎます"
    
    def test_get_stats_today_performance(self, client):
        """GET /api/stats/today のパフォーマンステスト"""
        print("\n📊 Test: GET /api/stats/today (統計取得)")
        results = measure_endpoint_performance(client, 'GET', '/api/stats/today')
        print_results(results)
        assert check_performance(results, threshold=10), "統計取得のレスポンスが遅すぎます"
    
    def test_post_session_complete_performance(self, client):
        """POST /api/session/complete のパフォーマンステスト"""
        print("\n📊 Test: POST /api/session/complete (セッション完了)")
        # セッションを作成
        response = client.post('/api/session/start', json={'type': 'work'})
        session_id = response.json['id']
        
        # パフォーマンス測定
        results = measure_endpoint_performance(
            client,
            'POST',
            '/api/session/complete',
            data={'id': session_id},
            iterations=1
        )
        print_results(results)
        assert check_performance(results, threshold=10), "セッション完了のレスポンスが遅すぎます"
    
    def test_delete_session_reset_performance(self, client):
        """DELETE /api/session/reset のパフォーマンステスト"""
        print("\n📊 Test: DELETE /api/session/reset (セッションリセット)")
        # セッションを作成
        response = client.post('/api/session/start', json={'type': 'work'})
        session_id = response.json['id']
        
        # パフォーマンス測定
        results = measure_endpoint_performance(
            client,
            'DELETE',
            '/api/session/reset',
            data={'id': session_id},
            iterations=1
        )
        print_results(results)
        assert check_performance(results, threshold=10), "セッションリセットのレスポンスが遅すぎます"


if __name__ == '__main__':
    print("=" * 70)
    print("パフォーマンステスト実行")
    print("=" * 70)
    print("\n使用方法: pytest tests/performance_test.py -v -s")
    print("=" * 70)
