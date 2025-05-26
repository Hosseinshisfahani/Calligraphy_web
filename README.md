# Caligraphy_web
This project is created for uploading calligraphy courses and instructional videos.

## Project Structure

- **Calligraphy/** - Main Django project
  - **calligraphyApp/** - Main application
  - **media/** - Media files
    - **alphabet_videos/** - Organized Persian alphabet instructional videos
    - **course_thumbnails/** - Thumbnails for courses
    - **videos/** - Other video content

## Video Organization

The Persian alphabet instructional videos are now organized in a structured directory:

```
media/alphabet_videos/
├── README.md         - Information about video content
├── الف/              - Alef letter videos
├── ب/                - Be letter videos
├── ج/                - Jim letter videos (including چ, ح, خ)
...and other Persian letters
```

## Management Commands

Several management commands are available to help manage video content:

- `python manage.py update_video_paths` - Updates database references to use the new organized path structure
- `python manage.py import_alphabet_videos` - Imports videos from the alphabet_videos directory
  - Options:
    - `--course-id ID` - Link videos to an existing course
    - `--create-parts` - Create a new course with parts for each letter group

## Setup Instructions

1. Clone the repository
2. Install dependencies from requirements.txt
3. Configure the database
4. Run migrations
5. Start the development server

## Video Files

The original video files are stored in the `حروف الفبا` directory and have been organized into the proper media structure.  
