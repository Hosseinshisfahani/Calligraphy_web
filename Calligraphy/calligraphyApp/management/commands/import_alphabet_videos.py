import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from calligraphyApp.models import Part, Video, Course

class Command(BaseCommand):
    help = 'Import videos from the alphabet_videos directory into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--course-id',
            type=int,
            default=None,
            help='Course ID to link parts to'
        )
        parser.add_argument(
            '--create-parts',
            action='store_true',
            help='Create parts if they do not exist'
        )

    def handle(self, *args, **options):
        videos_dir = os.path.join('media', 'alphabet_videos')
        course_id = options['course_id']
        create_parts = options['create_parts']
        
        # Exit if no course ID provided and not creating parts
        if course_id is None and not create_parts:
            self.stdout.write(self.style.ERROR(
                'You must provide either a course ID (--course-id) or use --create-parts'
            ))
            return
        
        # Get course if ID provided
        course = None
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                self.stdout.write(self.style.SUCCESS(f'Using course: {course.title}'))
            except Course.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Course with ID {course_id} not found'))
                return
        
        # Create course if needed
        if course is None and create_parts:
            course = Course.objects.create(
                title='دوره خوشنویسی حروف الفبا',
                description='آموزش خوشنویسی حروف الفبای فارسی',
                price=0.00,  # Free course
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created new course: {course.title}'))
        
        # Map of folder names to their display titles
        folder_display_names = {
            'نقطه': 'نقطه گذاری',
            'الف': 'حرف الف',
            'ب': 'حرف ب',
            'ج': 'حرف ج، چ، ح، خ',
            'د': 'حرف د، ذ',
            'ر': 'حرف ر، ز، ژ',
            'س': 'حرف س، ش',
            'ص': 'حرف ص، ض',
            'ط': 'حرف ط، ظ',
            'ع': 'حرف ع، غ',
            'ف ق': 'حروف ف، ق',
            'ل': 'حرف ل',
            'م': 'حرف م',
            'ن': 'حرف ن',
            'ه': 'حرف ه',
            'و': 'حرف و',
            'ک': 'حرف ک، گ',
            'ی': 'حرف ی'
        }
        
        # Dictionary to store created parts
        parts_dict = {}
        
        # Get or create parts
        if create_parts:
            order = 1
            for folder_name, display_name in folder_display_names.items():
                part, created = Part.objects.get_or_create(
                    course=course,
                    title=display_name,
                    defaults={'order': order}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created part: {part.title}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Using existing part: {part.title}'))
                parts_dict[folder_name] = part
                order += 1
        else:
            # Get existing parts for the course
            parts = Part.objects.filter(course=course)
            for part in parts:
                # Try to match part title with folder names
                for folder_name, display_name in folder_display_names.items():
                    if display_name.lower() in part.title.lower() or folder_name in part.title:
                        parts_dict[folder_name] = part
                        self.stdout.write(self.style.SUCCESS(f'Mapped folder {folder_name} to part: {part.title}'))
        
        # Check if we have all folder mappings
        for folder_name in folder_display_names.keys():
            if folder_name not in parts_dict:
                self.stdout.write(self.style.WARNING(f'No part mapping found for folder: {folder_name}'))
        
        videos_imported = 0
        videos_skipped = 0
        
        # Process each folder
        for folder_name, part in parts_dict.items():
            folder_path = os.path.join(videos_dir, folder_name)
            
            if not os.path.exists(folder_path):
                self.stdout.write(self.style.WARNING(f'Folder not found: {folder_path}'))
                continue
            
            # Get list of video files in the folder
            try:
                video_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error listing directory {folder_path}: {str(e)}'))
                continue
            
            self.stdout.write(self.style.SUCCESS(f'Found {len(video_files)} videos in {folder_name}'))
            
            for order, video_file in enumerate(sorted(video_files), 1):
                # Clean up the title (remove .mp4 and clean up spaces)
                title = os.path.splitext(video_file)[0].strip()
                
                # Create relative path from media root
                relative_path = os.path.join('alphabet_videos', folder_name, video_file)
                
                # Check if video already exists
                if not Video.objects.filter(title=title, part=part).exists():
                    # Create video object
                    video = Video(
                        part=part,
                        title=title,
                        video_file=relative_path,
                        duration=timedelta(minutes=5),  # Default duration
                        order=order,
                        is_free=True  # Make all alphabet videos free
                    )
                    video.save()
                    
                    videos_imported += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Added video: {title} to part: {part.title}')
                    )
                else:
                    videos_skipped += 1
                    self.stdout.write(
                        self.style.WARNING(f'Video already exists: {title} in part: {part.title}')
                    )
        
        self.stdout.write(self.style.SUCCESS(
            f'Import completed: {videos_imported} videos imported, {videos_skipped} skipped'
        )) 