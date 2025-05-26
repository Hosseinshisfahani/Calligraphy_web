from django.core.management.base import BaseCommand
from calligraphyApp.models import Part, Video

class Command(BaseCommand):
    help = 'Fix video part assignments'

    def handle(self, *args, **options):
        # Clear all videos first
        Video.objects.all().delete()
        
        # Correct folder to part mapping
        folder_to_part = {
            'نقطه': 'نقطه (Dots)',
            'الف': 'الف (Alef)',
            'ب': 'ب (Be)',
            'ج': 'ج (Jim)',
            'د': 'دال (daal)',
            'ر': 'ر (re)',
            'س': 'سین (sin)',
            'ص': 'صاد (saad)',
            'ط': 'طاء (taa)',
            'ع': 'عین (ain)',
            'ف ق': 'ف ق (fe and ghaf)',
            'ل': 'لام (laam)',
            'م': 'میم (mym)',
            'ن': 'نون (noon)',
            'ه': 'ه (he)',
            'و': 'واو (waav)',
            'ک': 'کاف (kaf)',
            'ی': 'ی (ye)',
        }
        
        # Get part objects
        parts = {part.title: part for part in Part.objects.all()}
        
        # Import videos with correct part assignments
        import os
        from datetime import timedelta
        
        videos_dir = '/root/Caligraphy_web/Calligraphy/media/videos/New folder'
        
        for folder_name, part_title in folder_to_part.items():
            folder_path = os.path.join(videos_dir, folder_name)
            if not os.path.exists(folder_path):
                self.stdout.write(self.style.WARNING(f'Folder not found: {folder_path}'))
                continue
            
            part = parts.get(part_title)
            if not part:
                self.stdout.write(self.style.ERROR(f'Part not found: {part_title}'))
                continue
            
            video_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
            
            for order, video_file in enumerate(sorted(video_files), 1):
                title = os.path.splitext(video_file)[0].strip()
                relative_path = os.path.join('videos/New folder', folder_name, video_file)
                
                video = Video(
                    part=part,
                    title=title,
                    video_file=relative_path,
                    duration=timedelta(minutes=5),
                    order=order
                )
                video.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully added video: {title} to part: {part.title}')
                ) 