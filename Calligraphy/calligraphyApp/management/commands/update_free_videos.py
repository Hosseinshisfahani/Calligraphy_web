from django.core.management.base import BaseCommand
from calligraphyApp.models import Course

class Command(BaseCommand):
    help = 'Update all courses to have exactly one free video (first video of first part)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        courses = Course.objects.all()
        
        if not courses:
            self.stdout.write(self.style.WARNING('No courses found'))
            return
            
        total_courses = courses.count()
        updated_courses = 0
        
        self.stdout.write(f'Processing {total_courses} courses...\n')
        
        for course in courses:
            self.stdout.write(f'Processing course: {course.title}')
            
            # Get current free videos count
            current_free_count = course.get_free_videos().count()
            
            if dry_run:
                self.stdout.write(f'  Current free videos: {current_free_count}')
                if current_free_count != 1:
                    self.stdout.write(f'  Would update to have exactly 1 free video')
                else:
                    self.stdout.write(f'  Already has exactly 1 free video')
            else:
                # Update the course to have exactly one free video
                free_video = course.ensure_one_free_video()
                
                if free_video:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Set free video: {free_video.title}')
                    )
                    updated_courses += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'  ✗ No videos found in course')
                    )
        
        if dry_run:
            self.stdout.write(f'\nDRY RUN COMPLETE - {total_courses} courses analyzed')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nUPDATE COMPLETE - {updated_courses} courses updated')
            ) 