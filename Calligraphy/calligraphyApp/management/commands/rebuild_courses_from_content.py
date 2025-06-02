import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from calligraphyApp.models import Course, Part, Video, CourseEnrollment, Payment
import glob
from collections import defaultdict
from datetime import timedelta

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Rebuild all courses from scratch based on content directory structure'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be created without making changes')
        parser.add_argument('--clear-data', action='store_true', help='Clear existing course data before rebuilding')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        clear_data = options['clear_data']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in dry-run mode. No changes will be made.'))
        
        content_root = settings.MEDIA_ROOT
        self.stdout.write(f'Scanning content directory: {content_root}')
        
        # Clear existing data if requested
        if clear_data and not dry_run:
            self.stdout.write(self.style.WARNING('Clearing existing course data...'))
            with transaction.atomic():
                CourseEnrollment.objects.all().delete()
                Payment.objects.all().delete()
                Video.objects.all().delete()
                Part.objects.all().delete()
                Course.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))
        
        # Course structure based on directory analysis
        courses_to_create = []
        
        # 1. Alphabet Course (حروف الفبا)
        alphabet_path = os.path.join(content_root, 'حروف الفبا/New folder')
        if os.path.exists(alphabet_path):
            alphabet_course = {
                'title': 'آموزش خوشنویسی حروف فارسی',
                'description': 'آموزش کامل حروف الفبای فارسی به شیوه استاد حمید رضا توکلی',
                'price': 50000,
                'base_path': 'حروف الفبا/New folder',
                'parts': []
            }
            
            # Get all letter directories
            letter_dirs = [d for d in os.listdir(alphabet_path) if os.path.isdir(os.path.join(alphabet_path, d))]
            letter_order = ['نقطه', 'الف', 'ب', 'ج', 'د', 'ر', 'س', 'ص', 'ط', 'ع', 'ف ق', 'ل', 'م', 'ن', 'ه', 'و', 'ک', 'ی']
            
            for order, letter in enumerate(letter_order, 1):
                if letter in letter_dirs:
                    letter_path = os.path.join(alphabet_path, letter)
                    videos = [f for f in os.listdir(letter_path) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
                    if videos:
                        part_info = {
                            'title': f'{letter}',
                            'description': f'آموزش حرف {letter}',
                            'order': order,
                            'videos': []
                        }
                        
                        for video_order, video_file in enumerate(sorted(videos), 1):
                            video_path = f'حروف الفبا/New folder/{letter}/{video_file}'
                            part_info['videos'].append({
                                'title': video_file.replace('.mp4', ''),
                                'description': f'ویدیو {video_order} - {letter}',
                                'order': video_order,
                                'file_path': video_path,
                                'is_free': video_order == 1  # First video of each letter is free
                            })
                        
                        alphabet_course['parts'].append(part_info)
            
            courses_to_create.append(alphabet_course)
        
        # 2. Engineering Calligraphy Terms
        eng_path = os.path.join(content_root, 'آموزش نستعلیق به شیوه مهندسی خط')
        if os.path.exists(eng_path):
            terms = [d for d in os.listdir(eng_path) if os.path.isdir(os.path.join(eng_path, d))]
            term_order = ['ترم اول', 'ترم دو', 'ترم سه', 'ترم چهارم', 'ترم پنجم']
            term_prices = {
                'ترم اول': 100000,
                'ترم دو': 120000, 
                'ترم سه': 140000,
                'ترم چهارم': 160000,
                'ترم پنجم': 180000
            }
            
            for term in term_order:
                if term in terms:
                    term_path = os.path.join(eng_path, term)
                    course_info = {
                        'title': f'آموزش نستعلیق به شیوه مهندسی خط - {term}',
                        'description': f'آموزش {term} نستعلیق به شیوه مهندسی خط - استاد حمید رضا توکلی',
                        'price': term_prices.get(term, 150000),
                        'base_path': f'آموزش نستعلیق به شیوه مهندسی خط/{term}',
                        'parts': []
                    }
                    
                    # Get all session directories
                    sessions = [d for d in os.listdir(term_path) if os.path.isdir(os.path.join(term_path, d))]
                    
                    for session_order, session in enumerate(sorted(sessions), 1):
                        session_path = os.path.join(term_path, session)
                        videos = [f for f in os.listdir(session_path) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
                        
                        if videos:
                            part_info = {
                                'title': session,
                                'description': f'{session} - {term}',
                                'order': session_order,
                                'videos': []
                            }
                            
                            for video_order, video_file in enumerate(sorted(videos), 1):
                                video_path = f'آموزش نستعلیق به شیوه مهندسی خط/{term}/{session}/{video_file}'
                                part_info['videos'].append({
                                    'title': f'ویدیو {video_order} - {session}',
                                    'description': f'ویدیو {video_order} از {session}',
                                    'order': video_order,
                                    'file_path': video_path,
                                    'is_free': video_order == 1 and session_order == 1  # First video of first session is free
                                })
                            
                            course_info['parts'].append(part_info)
                    
                    courses_to_create.append(course_info)
        
        # Create courses
        self.stdout.write(f'\nFound {len(courses_to_create)} courses to create:')
        
        total_courses = 0
        total_parts = 0 
        total_videos = 0
        
        for course_data in courses_to_create:
            self.stdout.write(f'\n📚 Course: {course_data["title"]}')
            self.stdout.write(f'   Price: {course_data["price"]:,} تومان')
            self.stdout.write(f'   Parts: {len(course_data["parts"])}')
            
            if not dry_run:
                with transaction.atomic():
                    # Create course
                    course = Course.objects.create(
                        title=course_data['title'],
                        description=course_data['description'],
                        price=course_data['price']
                    )
                    total_courses += 1
                    
                    # Create parts and videos
                    for part_data in course_data['parts']:
                        part = Part.objects.create(
                            course=course,
                            title=part_data['title'],
                            order=part_data['order']
                        )
                        total_parts += 1
                        
                        part_video_count = 0
                        part_free_count = 0
                        
                        for video_data in part_data['videos']:
                            # Verify file exists
                            full_path = os.path.join(content_root, video_data['file_path'])
                            if os.path.exists(full_path):
                                Video.objects.create(
                                    part=part,
                                    title=video_data['title'],
                                    description=video_data['description'],
                                    video_file=video_data['file_path'],
                                    duration=timedelta(seconds=300),  # Default 5 minutes
                                    order=video_data['order'],
                                    is_free=video_data['is_free']
                                )
                                total_videos += 1
                                part_video_count += 1
                                if video_data['is_free']:
                                    part_free_count += 1
                        
                        self.stdout.write(f'   📁 {part_data["title"]}: {part_video_count} videos ({part_free_count} free)')
            else:
                # Dry run - just count
                total_courses += 1
                for part_data in course_data['parts']:
                    total_parts += 1
                    part_video_count = 0
                    part_free_count = 0
                    
                    for video_data in part_data['videos']:
                        full_path = os.path.join(content_root, video_data['file_path'])
                        if os.path.exists(full_path):
                            total_videos += 1
                            part_video_count += 1
                            if video_data['is_free']:
                                part_free_count += 1
                    
                    self.stdout.write(f'   📁 {part_data["title"]}: {part_video_count} videos ({part_free_count} free)')
        
        # Summary
        self.stdout.write(f'\n' + '='*50)
        self.stdout.write(f'SUMMARY:')
        self.stdout.write(f'📚 Courses: {total_courses}')
        self.stdout.write(f'📁 Parts: {total_parts}')
        self.stdout.write(f'🎬 Videos: {total_videos}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a dry run. Use --clear-data to actually rebuild the courses.'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Courses rebuilt successfully from content directory!')) 