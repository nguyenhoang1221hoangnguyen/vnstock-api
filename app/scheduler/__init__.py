"""
APScheduler setup for background jobs
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

from .stock_updater import run_daily_update, run_hourly_update

# Create scheduler instance
scheduler = BackgroundScheduler()


def init_scheduler():
    """Initialize and start the scheduler"""

    # Add jobs
    # Daily update: Chạy lúc 7:00 sáng mỗi ngày (sau giờ đóng cửa thị trường)
    scheduler.add_job(
        func=run_daily_update,
        trigger=CronTrigger(hour=7, minute=0),
        id='daily_update',
        name='Update all stale stocks daily',
        replace_existing=True
    )

    # Hourly update: Chạy mỗi 2 giờ trong giờ giao dịch (9h-15h)
    scheduler.add_job(
        func=run_hourly_update,
        trigger=CronTrigger(hour='9-15/2', minute=30),
        id='hourly_update',
        name='Update top stocks every 2 hours',
        replace_existing=True
    )

    # Start scheduler
    scheduler.start()
    print("✓ Background scheduler started")
    print("  - Daily update: 7:00 AM")
    print("  - Hourly update: Every 2 hours (9:30, 11:30, 13:30)")

    # Shut down scheduler when app exits
    atexit.register(lambda: scheduler.shutdown())


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("✓ Background scheduler stopped")


def get_scheduler_status():
    """Get current scheduler status"""
    jobs = scheduler.get_jobs()
    return {
        'running': scheduler.running,
        'jobs': [
            {
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in jobs
        ]
    }
