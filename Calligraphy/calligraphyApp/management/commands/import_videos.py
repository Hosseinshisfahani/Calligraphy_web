import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.files import File
from calligraphyApp.models import Part, Video

class Command(BaseCommand):
    help = 'Import videos from media directory into database'

    def handle(self, *args, **options):
        videos_dir = '/root/Caligraphy_web/Calligraphy/media/videos/New folder'
        
        # Map of folder names to part IDs (based on your created parts)
        folder_to_part = {
            'نقطه': 1,
            'الف': 2,
            'ب': 3,
            'ج': 4,
            'د': 5,
            'ر': 6,
            'س': 7,
            'ص': 8,
            'ط': 9,
            'ع': 10,
            'ف ق': 11,
            'ل': 12,
            'م': 13,
            'ن': 14,
            'ه': 15,
            'و': 16,
            'ک': 17,
            'ی': 18,
        }

        for folder_name, part_id in folder_to_part.items():
            folder_path = os.path.join(videos_dir, folder_name)
            if not os.path.exists(folder_path):
                self.stdout.write(self.style.WARNING(f'Folder not found: {folder_path}'))
                continue

            part = Part.objects.get(id=part_id)
            
            # Get list of video files in the folder
            video_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
            
            for order, video_file in enumerate(sorted(video_files), 1):
                video_path = os.path.join(folder_path, video_file)
                
                # Clean up the title (remove .mp4 and clean up spaces)
                title = os.path.splitext(video_file)[0].strip()
                
                # Check if video already exists
                if not Video.objects.filter(title=title, part=part).exists():
                    # Create relative path from media root
                    relative_path = os.path.join('videos/New folder', folder_name, video_file)
                    
                    # Create video object
                    video = Video(
                        part=part,
                        title=title,
                        video_file=relative_path,
                        duration=timedelta(minutes=5),  # Default duration
                        order=order
                    )
                    video.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully added video: {title} to part: {part.title}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Video already exists: {title} in part: {part.title}')
                    ) 