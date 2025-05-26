import os
from django.core.management.base import BaseCommand
from calligraphyApp.models import Video

class Command(BaseCommand):
    help = 'Update video file paths to use the new alphabet_videos directory structure'

    def handle(self, *args, **options):
        # Get all videos from the database
        videos = Video.objects.filter(video_file__contains='videos/New folder')
        
        video_count = videos.count()
        updated_count = 0
        skipped_count = 0
        
        self.stdout.write(self.style.SUCCESS(f'Found {video_count} videos to update'))
        
        for video in videos:
            # Get the current path
            current_path = video.video_file.name
            
            # Skip if already updated
            if 'alphabet_videos' in current_path:
                skipped_count += 1
                continue
                
            try:
                # Transform path from 'videos/New folder/الف/4 الف.mp4' 
                # to 'alphabet_videos/الف/4 الف.mp4'
                parts = current_path.split('/')
                if len(parts) >= 3 and parts[0] == 'videos' and parts[1] == 'New folder':
                    letter_dir = parts[2]
                    filename = parts[3] if len(parts) > 3 else ''
                    
                    # Create the new path
                    new_path = f'alphabet_videos/{letter_dir}/{filename}'
                    
                    # Update the video file path
                    video.video_file = new_path
                    video.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated path: {current_path} → {new_path}')
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping unexpected path format: {current_path}')
                    )
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error updating {current_path}: {str(e)}')
                )
                skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Completed: {updated_count} videos updated, {skipped_count} skipped out of {video_count} total'
        )) 