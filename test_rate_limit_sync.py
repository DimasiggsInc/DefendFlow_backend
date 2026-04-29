import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_rate_limit_sync(url: str, total_requests: int, max_workers: int = 50):
    results = []
    
    def fetch(i: int):
        try:
            t = time.time()
            resp = requests.get(url, timeout=10)
            return (t, resp.status_code, None)
        except Exception as e:
            return (time.time(), "error", str(e))
    
    print(f"🧪 Отправляю {total_requests} запросов (workers={max_workers})...")
    t_start = time.time()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch, i) for i in range(total_requests)]
        for future in as_completed(futures):
            results.append(future.result())
    
    t_end = time.time()
    duration = t_end - t_start
    
    # Статистика
    ok = sum(1 for _, s, _ in results if s == 200)
    limited = sum(1 for _, s, _ in results if s == 429)
    errors = sum(1 for _, s, _ in results if s == "error")
    
    print("\n📊 Итоги:")
    print(f"⏱️  Длительность: {duration:.2f} сек")
    print(f"🚀 Темп: {total_requests / duration:.1f} req/s")
    print(f"✅ 200 OK: {ok}")
    print(f"🚫 429 Too Many Requests: {limited}")
    print(f"❌ Ошибки: {errors}")
    
    # Распределение по секундам
    print("\n📈 По секундам:")
    for sec in range(int(duration) + 1):
        sec_start = t_start + sec
        sec_end = sec_start + 1
        ok_s = sum(1 for t,s,_ in results if sec_start <= t < sec_end and s == 200)
        lim_s = sum(1 for t,s,_ in results if sec_start <= t < sec_end and s == 429)
        if ok_s + lim_s > 0:
            print(f"Сек {sec+1:2d}: {ok_s:3d} OK | {lim_s:3d} 429")

if __name__ == "__main__":
    TARGET_URL = "http://localhost:8000/"  # ← ваш рабочий URL
    TOTAL = 101
    WORKERS = 100  # concurrency
    test_rate_limit_sync(TARGET_URL, TOTAL, WORKERS)
