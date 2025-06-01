import os
import re
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from calligraphyApp.models import Course, Part, Video
from django.core.files import File
from datetime import timedelta
import datetime

class Command(BaseCommand):
    help = 'Creates a new Nastaliq calligraphy course from the content directory'

    def add_arguments(self, parser):
        parser.add_argument('--source_dir', type=str, default='/home/projects/content khat/آموزش نستعلیق به شیوه مهندسی خط', 
                            help='Source directory containing course content')
        parser.add_argument('--create', action='store_true', help='Actually create the course (otherwise just prints what would be created)')
        parser.add_argument('--first_free', action='store_true', help='Make the first video of each part free')

    def handle(self, *args, **options):
        source_dir = options['source_dir']
        create_mode = options['create']
        first_free = options['first_free']
        
        # Course pricing structure as specified
        pricing = {
            'ترم اول': Decimal('7800000'),   # 780,000 تومان
            'ترم دوم': Decimal('9800000'),   # 980,000 تومان
            'ترم سه': Decimal('9800000'),    # 980,000 تومان
            'ترم چهارم': Decimal('12800000'), # 1,280,000 تومان
            'ترم پنجم': Decimal('15800000')  # 1,580,000 تومان
        }
        
        # Course main data
        course_data = {
            'title': 'آموزش نستعلیق به شیوه مهندسی خط',
            'description': """
دوره جامع آموزش خط نستعلیق به شیوه مهندسی خط

این دوره آموزشی شامل ۵ ترم است که از مبتدی تا پیشرفته را پوشش می‌دهد:

ترم اول: مبانی و اصول اولیه خط نستعلیق (۷۸۰,۰۰۰ تومان)
ترم دوم: آموزش متوسط خط نستعلیق (۹۸۰,۰۰۰ تومان)
ترم سوم: تکنیک‌های پیشرفته خط نستعلیق (۹۸۰,۰۰۰ تومان)
ترم چهارم: هنر ترکیب‌بندی در خط نستعلیق (۱,۲۸۰,۰۰۰ تومان)
ترم پنجم: اصول استادی و خلق آثار هنری (۱,۵۸۰,۰۰۰ تومان)

هر ترم شامل چندین جلسه آموزشی با ویدیوهای کاربردی است که توسط استاد با تجربه تدریس می‌شود.
            """,
        }
        
        if not os.path.isdir(source_dir):
            self.stdout.write(self.style.ERROR(f'Source directory not found: {source_dir}'))
            return
            
        if create_mode:
            # Create the main course
            self.stdout.write(self.style.SUCCESS(f'Creating course: {course_data["title"]}'))
            course = Course.objects.create(
                title=course_data['title'],
                description=course_data['description'],
                # We'll keep price at 0 for the main course since we'll charge per term
                price=0,
                is_active=True
            )
        else:
            self.stdout.write(self.style.SUCCESS(f'Would create course: {course_data["title"]}'))
            course = None
            
        # Scan the directory for terms
        terms = sorted([d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))])
        
        for term_idx, term_name in enumerate(terms, 1):
            term_path = os.path.join(source_dir, term_name)
            term_price = pricing.get(term_name, Decimal('0'))
            
            # Create a course for each term
            term_title = f"{course_data['title']} - {term_name}"
            term_desc = f"بخش {term_name} از دوره آموزش نستعلیق به شیوه مهندسی خط"
            
            if create_mode:
                self.stdout.write(self.style.SUCCESS(f'Creating term course: {term_title} with price {term_price}'))
                term_course = Course.objects.create(
                    title=term_title,
                    description=term_desc,
                    price=term_price,
                    is_active=True
                )
            else:
                self.stdout.write(self.style.SUCCESS(f'Would create term course: {term_title} with price {term_price}'))
                term_course = None
            
            # Scan for sessions in each term
            sessions = sorted([d for d in os.listdir(term_path) if os.path.isdir(os.path.join(term_path, d))])
            
            for session_idx, session_name in enumerate(sessions, 1):
                session_path = os.path.join(term_path, session_name)
                
                if create_mode:
                    self.stdout.write(self.style.SUCCESS(f'Creating part: {session_name} for {term_title}'))
                    part = Part.objects.create(
                        course=term_course,
                        title=session_name,
                        order=session_idx
                    )
                else:
                    self.stdout.write(self.style.SUCCESS(f'Would create part: {session_name} for {term_title}'))
                    part = None
                
                # Find videos in each session
                videos = [f for f in os.listdir(session_path) if f.endswith('.mp4')]
                
                # Sort videos by part number
                def extract_part_number(filename):
                    match = re.search(r'Part\s*(\d+)', filename, re.IGNORECASE)
                    if match:
                        return int(match.group(1))
                    return 999  # Default high number for files without part number
                
                videos.sort(key=extract_part_number)
                
                for video_idx, video_file in enumerate(videos, 1):
                    video_path = os.path.join(session_path, video_file)
                    match = re.search(r'Part\s*(\d+)', video_file, re.IGNORECASE)
                    if match:
                        part_number = match.group(1)
                        video_title = f"بخش {part_number} - {session_name}"
                    else:
                        video_title = f"ویدیو {video_idx} - {session_name}"
                    
                    # Set first video as free if requested
                    is_free = first_free and video_idx == 1
                    
                    if create_mode:
                        self.stdout.write(self.style.SUCCESS(f'Processing video: {video_file} -> {video_title}'))
                        # Get file size for an estimate of duration (1MB ≈ 10 seconds as a rough estimate)
                        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                        estimated_duration = timedelta(seconds=int(file_size_mb * 10))
                        
                        # Create video object without file first (we'll add it later if needed)
                        video = Video.objects.create(
                            part=part,
                            title=video_title,
                            description=f"ویدیوی آموزشی {video_title} از دوره {term_title}",
                            duration=estimated_duration,
                            order=video_idx,
                            is_free=is_free
                        )
                        
                        self.stdout.write(f'Video created: {video.title} (Free: {is_free})')
                        # Note: Uploading the actual video files would require copying them
                        # to the media directory, which may be resource-intensive
                        self.stdout.write(f'Video file path: {video_path}')
                        # Uncommment below to actually copy the video files (may be slow for large files)
                        # with open(video_path, 'rb') as f:
                        #    video.video_file.save(os.path.basename(video_path), File(f), save=True)
                    else:
                        self.stdout.write(self.style.SUCCESS(
                            f'Would create video: {video_title} from {video_path} (Free: {is_free})'
                        ))
        
        if create_mode:
            self.stdout.write(self.style.SUCCESS('Course creation completed successfully!'))
            self.stdout.write(self.style.WARNING('Note: Video files were not uploaded to save resources.'))
            self.stdout.write(self.style.WARNING('You may need to manually add the video files later.'))
        else:
            self.stdout.write(self.style.SUCCESS('Dry run completed. Use --create to actually create the course.')) 