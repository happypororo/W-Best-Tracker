#!/usr/bin/env python3
"""
APScheduler 기반 자동화 스케줄러
정해진 시간마다 W컨셉 베스트 상품 크롤링 및 DB 저장
"""

import asyncio
import sys
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import time
import signal

from wconcept_scraper_v2 import WConceptScraper, scrape_all_categories
from database import Database

class WConceptScheduler:
    """W컨셉 크롤링 스케줄러"""
    
    def __init__(self, scrape_all=True):
        """
        Args:
            scrape_all: True면 모든 카테고리 크롤링, False면 아우터만
        """
        self.scheduler = BackgroundScheduler(
            timezone='Asia/Seoul',
            job_defaults={
                'coalesce': True,  # 누락된 작업 실행 방지
                'max_instances': 1  # 동시 실행 방지
            }
        )
        self.db = Database()
        self.scrape_all = scrape_all
        if not scrape_all:
            self.scraper = WConceptScraper(category_key='outer')
        self.is_running = False
    
    def scheduled_scraping_job(self):
        """스케줄된 크롤링 작업"""
        
        job_start_time = datetime.now()
        
        print("\n" + "=" * 70)
        print(f"🤖 자동 크롤링 작업 시작: {job_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        try:
            # 1. 크롤링 실행
            print("\n📡 크롤링 시작...")
            
            if self.scrape_all:
                # 모든 카테고리 크롤링
                products = asyncio.run(scrape_all_categories(max_products=200))
            else:
                # 단일 카테고리만 크롤링
                products = asyncio.run(self.scraper.scrape(max_products=200))
            
            if not products:
                raise Exception("수집된 상품이 없습니다.")
            
            print(f"✅ {len(products)}개 상품 수집 완료")
            
            # 2. 데이터베이스에 저장
            print("\n💾 데이터베이스 저장 중...")
            saved_count = self.db.save_products(products)
            
            # 3. 실행 시간 계산
            job_end_time = datetime.now()
            execution_time = int((job_end_time - job_start_time).total_seconds())
            
            # 4. 로그 저장
            self.db.log_scraping_job(
                started_at=job_start_time,
                status='success',
                products_collected=saved_count,
                execution_time=execution_time
            )
            
            print(f"\n✅ 작업 완료! ({execution_time}초 소요)")
            print(f"   저장된 상품: {saved_count}개")
            print(f"   다음 실행: {self._get_next_run_time()}")
            
        except Exception as e:
            # 실패 로그 저장
            job_end_time = datetime.now()
            execution_time = int((job_end_time - job_start_time).total_seconds())
            
            self.db.log_scraping_job(
                started_at=job_start_time,
                status='failed',
                products_collected=0,
                error_message=str(e),
                execution_time=execution_time
            )
            
            print(f"\n❌ 작업 실패: {str(e)}")
            print(f"   다음 실행: {self._get_next_run_time()}")
    
    def _get_next_run_time(self):
        """다음 실행 시간 조회"""
        jobs = self.scheduler.get_jobs()
        if jobs:
            next_run = jobs[0].next_run_time
            if next_run:
                return next_run.strftime('%Y-%m-%d %H:%M:%S')
        return "예정 없음"
    
    def add_hourly_job(self, hours: int = 1):
        """매 N시간마다 실행하는 작업 추가"""
        self.scheduler.add_job(
            self.scheduled_scraping_job,
            trigger=IntervalTrigger(hours=hours),
            id='hourly_scraping',
            name=f'매 {hours}시간마다 크롤링',
            replace_existing=True
        )
        print(f"✅ 스케줄 추가: 매 {hours}시간마다 실행")
    
    def add_cron_job(self, hours_str: str = '9,12,18,21'):
        """특정 시간에 실행하는 작업 추가 (Cron)"""
        self.scheduler.add_job(
            self.scheduled_scraping_job,
            trigger=CronTrigger(hour=hours_str, timezone='Asia/Seoul'),
            id='cron_scraping',
            name=f'매일 {hours_str}시에 크롤링',
            replace_existing=True
        )
        print(f"✅ 스케줄 추가: 매일 {hours_str}시에 실행")
    
    def start(self, mode: str = 'hourly', hours: int = 1, cron_hours: str = '9,12,18,21'):
        """스케줄러 시작"""
        
        print("\n" + "=" * 70)
        print("W컨셉 자동 크롤링 스케줄러")
        print("=" * 70)
        print()
        
        # 스케줄 설정
        if mode == 'hourly':
            self.add_hourly_job(hours)
        elif mode == 'cron':
            self.add_cron_job(cron_hours)
        elif mode == 'both':
            self.add_hourly_job(hours)
            self.add_cron_job(cron_hours)
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'hourly', 'cron', or 'both'")
        
        # 스케줄러 시작
        self.scheduler.start()
        self.is_running = True
        
        print(f"\n🚀 스케줄러 시작됨!")
        print(f"   다음 실행: {self._get_next_run_time()}")
        print(f"   데이터베이스: {self.db.db_path}")
        print()
        print("종료하려면 Ctrl+C를 누르세요.")
        print()
        
        # 즉시 한 번 실행할지 선택 (옵션)
        # self.scheduled_scraping_job()
    
    def stop(self):
        """스케줄러 중지"""
        if self.is_running:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            print("\n✅ 스케줄러 중지됨")
    
    def show_jobs(self):
        """등록된 작업 목록 표시"""
        print("\n📋 등록된 스케줄 작업:")
        jobs = self.scheduler.get_jobs()
        
        if not jobs:
            print("   (등록된 작업 없음)")
            return
        
        for job in jobs:
            print(f"\n   작업 ID: {job.id}")
            print(f"   이름: {job.name}")
            print(f"   다음 실행: {job.next_run_time}")
            print(f"   트리거: {job.trigger}")
    
    def show_stats(self):
        """데이터베이스 통계 표시"""
        stats = self.db.get_database_stats()
        
        print("\n📊 데이터베이스 통계:")
        print(f"   총 제품 수: {stats['total_products']}")
        print(f"   총 브랜드 수: {stats['total_brands']}")
        print(f"   총 데이터 포인트: {stats['total_data_points']}")
        print(f"   첫 수집: {stats['first_collection']}")
        print(f"   최근 수집: {stats['last_collection']}")
        print(f"   총 작업 수: {stats['total_scraping_jobs']}")
        print(f"   성공한 작업: {stats['successful_jobs']}")


def signal_handler(sig, frame):
    """Ctrl+C 처리"""
    print("\n\n종료 중...")
    sys.exit(0)


def main():
    """메인 함수"""
    
    # Ctrl+C 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    
    # 명령행 인자 처리
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = 'hourly'  # 기본값
    
    # 스케줄러 생성 및 시작 (기본: 모든 카테고리 크롤링)
    scheduler = WConceptScheduler(scrape_all=True)
    
    # 모드별 설정
    if mode == 'hourly':
        # 매 1시간마다 실행
        scheduler.start(mode='hourly', hours=1)
    elif mode == 'hourly-2':
        # 매 2시간마다 실행
        scheduler.start(mode='hourly', hours=2)
    elif mode == 'cron':
        # 매일 9시, 12시, 18시, 21시에 실행
        scheduler.start(mode='cron', cron_hours='9,12,18,21')
    elif mode == 'test':
        # 테스트: 매 1분마다 실행
        print("⚠️  테스트 모드: 매 1분마다 실행")
        scheduler.scheduler.add_job(
            scheduler.scheduled_scraping_job,
            trigger=IntervalTrigger(minutes=1),
            id='test_scraping',
            name='테스트 크롤링 (1분마다)',
            replace_existing=True
        )
        scheduler.scheduler.start()
        scheduler.is_running = True
        print(f"\n🚀 스케줄러 시작됨 (테스트 모드)")
        print(f"   다음 실행: {scheduler._get_next_run_time()}")
        print("\n종료하려면 Ctrl+C를 누르세요.\n")
    elif mode == 'now':
        # 즉시 한 번만 실행
        print("🚀 즉시 크롤링 실행...")
        scheduler.scheduled_scraping_job()
        print("\n✅ 작업 완료!")
        scheduler.show_stats()
        return
    elif mode == 'stats':
        # 통계만 표시
        scheduler.show_stats()
        return
    else:
        print(f"❌ 알 수 없는 모드: {mode}")
        print("\n사용법:")
        print("  python scheduler.py              # 매 1시간마다 실행")
        print("  python scheduler.py hourly-2     # 매 2시간마다 실행")
        print("  python scheduler.py cron         # 매일 9, 12, 18, 21시에 실행")
        print("  python scheduler.py test         # 테스트 모드 (매 1분)")
        print("  python scheduler.py now          # 즉시 한 번 실행")
        print("  python scheduler.py stats        # 통계만 표시")
        return
    
    # 스케줄 작업 표시
    scheduler.show_jobs()
    scheduler.show_stats()
    
    # 스케줄러 계속 실행
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()


if __name__ == "__main__":
    main()
