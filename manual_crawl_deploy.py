#!/usr/bin/env python3
"""
수동 크롤링 + Git Push + 재배포 통합 스크립트
Option 1: Full Integration - 자동 크롤링과 완전히 동일한 흐름
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """명령어 실행 헬퍼"""
    print(f"🔄 실행 중: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result

def main():
    """메인 실행 함수"""
    start_time = time.time()
    base_dir = Path(__file__).parent
    
    print("=" * 60)
    print("🚀 수동 크롤링 + 배포 시작")
    print("=" * 60)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')}")
    print()
    
    # Step 1: 크롤링 실행 (약 3분)
    print("📡 Step 1/5: 크롤링 실행 중...")
    crawl_start = time.time()
    
    try:
        crawl_script = base_dir / "auto_crawl.py"
        result = run_command(
            ["python3", str(crawl_script)],
            cwd=base_dir
        )
        
        crawl_time = time.time() - crawl_start
        print(f"✅ 크롤링 완료 ({crawl_time:.1f}초)")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 크롤링 실패: {e}")
        sys.exit(1)
    
    # Step 2: Git 상태 확인
    print("📝 Step 2/5: Git 상태 확인...")
    
    try:
        # DB 파일 추가
        run_command(["git", "add", "wconcept_tracking.db"], cwd=base_dir)
        
        # 변경사항 확인
        result = run_command(
            ["git", "diff", "--staged", "--quiet"],
            cwd=base_dir,
            check=False
        )
        
        if result.returncode == 0:
            print("ℹ️  변경사항 없음 - 배포 불필요")
            total_time = time.time() - start_time
            print()
            print("=" * 60)
            print(f"⏱️  총 소요 시간: {total_time:.1f}초")
            print("=" * 60)
            return
        
        print("✅ 변경사항 감지됨")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 상태 확인 실패: {e}")
        sys.exit(1)
    
    # Step 3: Git Commit
    print("💾 Step 3/5: Git 커밋 생성...")
    commit_start = time.time()
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S KST')
        commit_msg = f"chore: Manual crawl update - {timestamp}"
        
        run_command(
            ["git", "commit", "-m", commit_msg],
            cwd=base_dir
        )
        
        commit_time = time.time() - commit_start
        print(f"✅ 커밋 완료 ({commit_time:.1f}초)")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 커밋 실패: {e}")
        sys.exit(1)
    
    # Step 4: Git Push
    print("🚀 Step 4/5: GitHub에 Push 중...")
    push_start = time.time()
    
    try:
        run_command(["git", "push"], cwd=base_dir)
        
        push_time = time.time() - push_start
        print(f"✅ Push 완료 ({push_time:.1f}초)")
        print()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Push 실패: {e}")
        sys.exit(1)
    
    # Step 5: 완료
    total_time = time.time() - start_time
    
    print("=" * 60)
    print("✨ 수동 크롤링 + 배포 완료!")
    print("=" * 60)
    print(f"⏱️  총 소요 시간: {total_time:.1f}초")
    print(f"   - 크롤링: {crawl_time:.1f}초")
    print(f"   - Git 작업: {commit_time + push_time:.1f}초")
    print()
    print("📌 Fly.io가 자동으로 재배포를 시작합니다 (1-2분 소요)")
    print("=" * 60)

if __name__ == "__main__":
    main()
