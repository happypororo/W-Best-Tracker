#!/usr/bin/env python3
"""
W Concept 크롤링 스케줄러
매 시간 20분에 자동으로 크롤링 실행 (Fly.io 프로덕션)
"""

import asyncio
import subprocess
from datetime import datetime, timedelta
import time

def get_next_run_time():
    """다음 실행 시간 계산 (매 시간 20분)"""
    now = datetime.now()
    target_minute = 20
    
    if now.minute < target_minute:
        # 이번 시간 20분
        next_run = now.replace(minute=target_minute, second=0, microsecond=0)
    else:
        # 다음 시간 20분
        next_run = (now + timedelta(hours=1)).replace(minute=target_minute, second=0, microsecond=0)
    
    return next_run

def run_crawl():
    """크롤링 실행"""
    import os
    
    print("\n" + "=" * 80)
    print(f"🚀 자동 크롤링 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # 현재 스크립트의 디렉토리를 기준으로 경로 설정
        current_dir = os.path.dirname(os.path.abspath(__file__))
        auto_crawl_path = os.path.join(current_dir, 'auto_crawl.py')
        
        result = subprocess.run(
            ['python3', auto_crawl_path],
            cwd=current_dir,
            capture_output=True,
            text=True,
            timeout=1200  # 20분 타임아웃 (8개 카테고리 크롤링 대응)
        )
        
        print(result.stdout)
        if result.stderr:
            print("오류:", result.stderr)
        
        if result.returncode == 0:
            print("✅ 크롤링 성공!")
        else:
            print(f"❌ 크롤링 실패 (코드: {result.returncode})")
    
    except subprocess.TimeoutExpired:
        print("❌ 크롤링 타임아웃 (10분 초과)")
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    
    print("=" * 80 + "\n")

def main():
    """메인 스케줄러 루프"""
    print("🔔 W Concept 크롤링 스케줄러 시작 (Fly.io 프로덕션)")
    print("⏰ 실행 시간: 매 시간 20분 (W컨셉 업데이트 :15 + 5분 버퍼)")
    print("✅ DB는 Fly.io 디스크에 직접 저장되어 즉시 반영됨")
    print("=" * 80 + "\n")
    
    while True:
        next_run = get_next_run_time()
        now = datetime.now()
        wait_seconds = (next_run - now).total_seconds()
        
        print(f"⏰ 다음 실행 예정: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   (약 {int(wait_seconds/60)}분 후)\n")
        
        # 다음 실행 시간까지 대기
        time.sleep(wait_seconds)
        
        # 크롤링 실행
        run_crawl()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  스케줄러 종료")
