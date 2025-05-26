# Calligraphy Web

A web application for showcasing and learning calligraphy.

## Features

- Gallery of calligraphy works
- Tutorials and learning resources
- User profiles
- Community interaction

## Setup

1. Clone the repository
2. Install dependencies
3. Run the application

## Technologies

- Python
- Django
- HTML/CSS
- JavaScript

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

## Video Files

The original video files are stored in the `حروف الفبا` directory and have been organized into the proper media structure.  
