"""
Management command to scrape an exam from examenredes.com.

Usage:
    python manage.py scrape_exam https://examenredes.com/ccna-1-examen-final-itnv7-preguntas-y-respuestas/
    python manage.py scrape_exam URL --wait 20
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Scrape an exam from examenredes.com and save to DB"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="Full URL of the exam page")
        parser.add_argument(
            "--wait",
            type=int,
            default=15,
            help="Seconds to wait for page load (default: 15)",
        )

    def handle(self, *args, **options):
        url = options["url"]
        wait = options["wait"]

        self.stdout.write(f"🕷️  Scraping: {url}")
        self.stdout.write(f"⏱️  Wait time: {wait}s")

        try:
            from ciscoapp.scraper_service import scrape_exam

            stats = scrape_exam(url, wait_seconds=wait)
        except Exception as exc:
            raise CommandError(f"Scraping failed: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone: {stats['exam_title']}\n"
                f"   Created:    {stats['created']}\n"
                f"   Skipped:    {stats['skipped']}\n"
                f"   Image-only: {stats['image_only']}"
            )
        )
