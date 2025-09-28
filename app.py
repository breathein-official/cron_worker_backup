import os
import random
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_audioclips
import textwrap
import openai
from dotenv import load_dotenv
from token_tracker import track_usage

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configuration
IMAGE_SIZE = (1080, 1920)
TORCH_PATH = "icons/torch.png"
CAMERA_PATH = "icons/camera.png"
LOGO_PATH = "icons/cronWorker.png"

def ai_function():
    """Generate a short BlockScroll-style motivational notification about scrolling."""
    prompt = (
        "Write a single short push-notification text mocking endless scrolling. "
        "Style: achievement unlocked / streak / gaming reward tone. "
        "It should highlight wasted hours scrolling with a clever, realistic twist "
        "about regret, lost time, or missed success. But motivating and realistic do not say you could have written a novel and all "
        "Examples: 'Elon Musk made millions while you scrolled 2h — unlocked: regret!'. "
        "Keep it under 100 characters. "
        "Do not use any emojis in the output. "
        "Do not explain, list, or say 'here are options'. "
        "Output only one notification text, nothing else."
    )
    
    # Fallback text if AI fails
    fallback_text = "2 hours lost scrolling. Elon Musk made millions. You unlocked: regret."
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        # Track token usage
        track_usage(response.usage, "Notification Generation", "gpt-3.5-turbo")
        
        # Extract the message safely
        response_text = response.choices[0].message.content.strip()
        
        # Remove filler like "Here are some options:" if it appears
        if response_text.lower().startswith("here are"):
            response_text = response_text.split(":", 1)[-1].strip()
        
        # If multiple lines or options come back, take just the first
        if "\n" in response_text:
            response_text = response_text.split("\n")[0].strip()
        
        # Remove quotes if they wrap the entire response
        if response_text.startswith('"') and response_text.endswith('"'):
            response_text = response_text[1:-1]
        
        # Remove any emojis that might have slipped through
        import re
        response_text = re.sub(r'[^\w\s\.,!?\-:;()]', '', response_text)
        
        # If response is empty or too short, use fallback
        if not response_text or len(response_text) < 10:
            response_text = fallback_text
            
        print(f"Generated notification: {response_text}")
        return response_text
        
    except Exception as e:
        print(f"AI generation failed: {e}, using fallback")
        return fallback_text

def wrap_text_words(text, words_per_line=4):
    """Wrap text to specified number of words per line"""
    words = text.split()
    return [
        " ".join(words[i : i + words_per_line])
        for i in range(0, len(words), words_per_line)
    ]

def calculate_text_block_size(text, font):
    """Calculate text height with word-based wrapping"""
    wrapped_lines = wrap_text_words(text)
    line_height = font.getbbox("A")[3] - font.getbbox("A")[1] + 25
    return wrapped_lines, len(wrapped_lines) * line_height

def process_logo():
    """Create logo with rounded corners"""
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo = logo.resize((100, 100), Image.LANCZOS)

        # Create rounded mask
        mask = Image.new("L", (100, 100), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, 100, 100], radius=20, fill=255)

        logo.putalpha(mask)
        return logo
    except Exception as e:
        print(f"Error loading logo: {e}")
        # Create a placeholder logo
        logo = Image.new('RGBA', (100, 100), (100, 100, 255, 255))
        draw = ImageDraw.Draw(logo)
        draw.text((25, 35), "BS", fill="white", font=ImageFont.load_default())
        return logo

def get_font(font_path, size):
    """Try to load a font, fallback to default if not available."""
    try:
        return ImageFont.truetype(font_path, size)
    except:
        try:
            # Try common Windows fonts
            return ImageFont.truetype("arial.ttf", size)
        except:
            # Use default font with approximate sizing
            return ImageFont.load_default()

def create_fade_clip(image_path, duration, fade_duration):
    """Create a clip with smooth opacity fade-in and fade-out effects."""
    from moviepy import ImageSequenceClip
    import numpy as np
    from PIL import Image
    
    # Create multiple frames with different opacity levels
    fps = 30  # Higher FPS for smoother transitions
    total_frames = int(duration * fps)
    fade_frames = int(fade_duration * fps)
    
    frames = []
    base_image = Image.open(image_path).convert("RGBA")
    
    for frame_num in range(total_frames):
        t = frame_num / fps
        
        # Calculate opacity with smoother curve
        if t <= fade_duration:
            # Fade in: 0 to 1 with smooth curve
            progress = t / fade_duration
            opacity = progress * progress  # Quadratic curve for smoother fade
        elif t >= duration - fade_duration:
            # Fade out: 1 to 0 with smooth curve
            progress = (duration - t) / fade_duration
            opacity = progress * progress  # Quadratic curve for smoother fade
        else:
            # Full opacity in middle
            opacity = 1.0
        
        # Create frame with opacity
        frame = base_image.copy()
        if opacity < 1.0:
            # Apply opacity to alpha channel
            frame_array = np.array(frame)
            frame_array[:, :, 3] = (frame_array[:, :, 3] * opacity).astype(np.uint8)
            frame = Image.fromarray(frame_array, 'RGBA')
        
        # Convert to RGB for MoviePy
        frame_rgb = Image.new('RGB', frame.size, (255, 255, 255))
        frame_rgb.paste(frame, mask=frame.split()[-1])
        frames.append(np.array(frame_rgb))
    
    # Create clip from frames
    clip = ImageSequenceClip(frames, fps=fps)
    print(f"Created fade clip with {len(frames)} frames at {fps} fps")
    return clip

def draw_bold_text(draw, xy, text, font, fill, weight=0):
    """Draw text with adjustable boldness using stroke; falls back to multi-draw.

    - weight: integer pixels of thickness. 0 = normal, 1-4 recommended.
    """
    if weight is None or weight <= 0:
        draw.text(xy, text, fill=fill, font=font)
        return
    try:
        draw.text(xy, text, fill=fill, font=font, stroke_width=weight, stroke_fill=fill)
    except TypeError:
        x, y = xy
        for dx in range(-weight, weight + 1):
            for dy in range(-weight, weight + 1):
                if dx == 0 and dy == 0:
                    continue
                draw.text((x + dx, y + dy), text, fill=fill, font=font)
        draw.text(xy, text, fill=fill, font=font)

def create_lockscreen_frame(bg_path, notif_msg):
    """Create a lockscreen frame using the proven layout approach."""
    try:
        # Load background
        background = Image.open(bg_path).convert("RGB")

        # Grayscale conversion with enhancement
        gray = cv2.cvtColor(np.array(background), cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        background = Image.fromarray(clahe.apply(gray)).convert("RGB")

        # POV text options - randomly select one
        pov_texts = [
            "POV: A notification changes your entire life trajectory",
            "POV: Duolingo has finally a worthy opponent", 
            "POV: You were scrolling hopelessly and then your phone hits you"
        ]
        selected_pov = random.choice(pov_texts)

        # POV Section calculation
        pov_font = get_font("arial.ttf", 72)
        pov_lines, pov_height = calculate_text_block_size(selected_pov, pov_font)
        WHITE_BOX_HEIGHT = pov_height + 240

        # Background processing to fit properly
        bg_aspect = background.width / background.height
        target_aspect = IMAGE_SIZE[0] / (IMAGE_SIZE[1] - WHITE_BOX_HEIGHT)

        if bg_aspect > target_aspect:
            new_height = IMAGE_SIZE[1] - WHITE_BOX_HEIGHT
            new_width = int(new_height * bg_aspect)
        else:
            new_width = IMAGE_SIZE[0]
            new_height = int(new_width / bg_aspect)

        background = background.resize((new_width, new_height), Image.LANCZOS)
        background = background.crop(
            (
                (new_width - IMAGE_SIZE[0]) // 2,
                (new_height - (IMAGE_SIZE[1] - WHITE_BOX_HEIGHT)) // 2,
                (new_width + IMAGE_SIZE[0]) // 2,
                (new_height + (IMAGE_SIZE[1] - WHITE_BOX_HEIGHT)) // 2,
            )
        )

        # Create canvas
        canvas = Image.new("RGB", IMAGE_SIZE, "white")
        canvas.paste(background, (0, WHITE_BOX_HEIGHT))
        draw = ImageDraw.Draw(canvas)

        # Draw POV section
        draw.rectangle([0, 0, IMAGE_SIZE[0], WHITE_BOX_HEIGHT], fill="white")
        y_pos = (WHITE_BOX_HEIGHT - pov_height) // 2
        pov_weight = 1  # Set >0 to increase boldness (e.g., 1 or 2)
        pov_margin_x = 80  # Horizontal margin for POV text
        for line in pov_lines:
            text_width = draw.textbbox((0, 0), line, font=pov_font)[2]
            # Center text within available width (full width minus margins)
            available_width = IMAGE_SIZE[0] - (2 * pov_margin_x)
            text_x = pov_margin_x + (available_width - text_width) // 2
            draw_bold_text(
                draw,
                (text_x, y_pos),
                line,
                pov_font,
                "black",
                weight=pov_weight,
            )
            y_pos += pov_font.getbbox("A")[3] - pov_font.getbbox("A")[1] + 25

        # Add "why not you?" overlay shifted up
        canvas = canvas.convert("RGBA")
        overlay = Image.new("RGBA", IMAGE_SIZE, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_font = get_font("arial.ttf", 150)

        text = "why not you?"
        text_bbox = overlay_draw.textbbox((0, 0), text, font=overlay_font)
        text_y = (
            IMAGE_SIZE[1] - (text_bbox[3] - text_bbox[1])
        ) // 2 - 50  # Shifted up 50px

        # Semi-bold effect with shadow
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            overlay_draw.text(
                (
                    text_bbox[0] + (IMAGE_SIZE[0] - text_bbox[2]) // 2 + offset[0],
                    text_y + offset[1],
                ),
                text,
                fill=(255, 255, 255, 100),
                font=overlay_font,
            )
        overlay_draw.text(
            (text_bbox[0] + (IMAGE_SIZE[0] - text_bbox[2]) // 2, text_y),
            text,
            fill=(255, 255, 255, 220),
            font=overlay_font,
        )
        canvas = Image.alpha_composite(canvas, overlay)

        # Notification box with proper positioning
        NOTIF_WIDTH = 1000
        notif_font = get_font("arial.ttf", 50)
        notif_lines = textwrap.wrap(notif_msg, width=32)
        text_height = len(notif_lines) * (
            notif_font.getbbox("A")[3] - notif_font.getbbox("A")[1] + 30
        )
        NOTIF_HEIGHT = max(220, 150 + text_height)

        # Create notification box
        notif_box = Image.new("RGBA", (NOTIF_WIDTH, NOTIF_HEIGHT), (0, 0, 0, 0))
        notif_draw = ImageDraw.Draw(notif_box)
        notif_draw.rounded_rectangle(
            [0, 0, NOTIF_WIDTH, NOTIF_HEIGHT], radius=25, fill=(45, 45, 45, 200)
        )

        # Prepare fonts for alignment calculations
        app_name_font = get_font("arial.ttf", 50)

        # Compute vertical center of the notification text block (title + message)
        title_top = 40
        title_height = app_name_font.getbbox("A")[3] - app_name_font.getbbox("A")[1]
        title_bottom = title_top + title_height
        message_top = 120
        message_bottom = message_top + text_height
        text_block_top = title_top
        text_block_bottom = max(title_bottom, message_bottom)
        text_block_center_y = (text_block_top + text_block_bottom) // 2

        # Add logo aligned to the vertical center of the text block
        if os.path.exists(LOGO_PATH):
            logo = process_logo()
            logo_height = 100
            logo_y = int(text_block_center_y - (logo_height // 2))
            # Clamp within notification box just in case
            logo_y = max(0, min(NOTIF_HEIGHT - logo_height, logo_y))
            notif_box.paste(logo, (40, logo_y), logo)

        # Notification text elements
        title_weight = 1.5  # Set >0 to increase boldness (e.g., 1 or 2)
        draw_bold_text(
            notif_draw,
            (160, 40),
            "BlockScroll",
            app_name_font,
            "white",
            weight=title_weight,
        )
        notif_draw.text(
            (NOTIF_WIDTH - 180, 40),
            "now",
            fill="white",
            font=get_font("arial.ttf", 40),
        )

        # Notification message
        y_pos = 120
        for line in notif_lines:
            notif_draw.text((160, y_pos), line, fill="white", font=notif_font)
            y_pos += notif_font.getbbox("A")[3] - notif_font.getbbox("A")[1] + 30

        # Position notification box closer to main text
        canvas.paste(
            notif_box,
            (
                (IMAGE_SIZE[0] - NOTIF_WIDTH) // 2,
                int(text_y + (text_bbox[3] - text_bbox[1]) + 60),
            ),
            notif_box,
        )

        # Add torch and camera icons at bottom
        icon_size = 70
        bg_size = 140
        bottom_padding = 250
        icon_spacing = 250

        # Common positions
        base_y = IMAGE_SIZE[1] - bottom_padding
        
        # Process torch (left side)
        if os.path.exists(TORCH_PATH):
            try:
                # Left side background
                left_bg = Image.new("RGBA", (bg_size, bg_size), (0, 0, 0, 0))
                draw_left = ImageDraw.Draw(left_bg)
                draw_left.ellipse((0, 0, bg_size, bg_size), fill=(45, 45, 45, 180))
                
                # Process torch icon
                torch = Image.open(TORCH_PATH).convert("RGBA")
                torch = torch.resize((icon_size, icon_size), Image.LANCZOS)
                
                # Convert to white while preserving alpha
                white_torch = Image.new("RGBA", torch.size, (0, 0, 0, 0))
                torch_data = torch.getdata()
                white_data = []
                for pixel in torch_data:
                    if len(pixel) == 4:  # RGBA
                        white_data.append((255, 255, 255, pixel[3]))
                    else:  # RGB
                        white_data.append((255, 255, 255, 255))
                white_torch.putdata(white_data)
                
                # Position left (center X - spacing)
                left_x = (IMAGE_SIZE[0] // 2) - icon_spacing - bg_size//2
                canvas.paste(left_bg, (left_x, base_y - bg_size//2), left_bg)
                canvas.paste(white_torch, 
                           (left_x + (bg_size-icon_size)//2, 
                            base_y - icon_size//2), 
                           white_torch)

            except Exception as e:
                print(f"Error processing torch: {str(e)}")

        # Process camera (right side)
        if os.path.exists(CAMERA_PATH):
            try:
                # Right side background
                right_bg = Image.new("RGBA", (bg_size, bg_size), (0, 0, 0, 0))
                draw_right = ImageDraw.Draw(right_bg)
                draw_right.ellipse((0, 0, bg_size, bg_size), fill=(45, 45, 45, 180))
                
                # Process camera icon
                camera = Image.open(CAMERA_PATH).convert("RGBA")
                camera = camera.resize((icon_size, icon_size), Image.LANCZOS)
                
                # Convert to white while preserving alpha
                white_camera = Image.new("RGBA", camera.size, (0, 0, 0, 0))
                camera_data = camera.getdata()
                white_data = []
                for pixel in camera_data:
                    if len(pixel) == 4:  # RGBA
                        white_data.append((255, 255, 255, pixel[3]))
                    else:  # RGB
                        white_data.append((255, 255, 255, 255))
                white_camera.putdata(white_data)
                
                # Position right (center X + spacing)
                right_x = (IMAGE_SIZE[0] // 2) + icon_spacing - bg_size//2
                canvas.paste(right_bg, (right_x, base_y - bg_size//2), right_bg)
                canvas.paste(white_camera, 
                           (right_x + (bg_size-icon_size)//2, 
                            base_y - icon_size//2), 
                           white_camera)

            except Exception as e:
                print(f"Error processing camera: {str(e)}")

        # Convert back to RGB for video export
        final_frame = canvas.convert("RGB")
        return np.array(final_frame)

    except Exception as e:
        print(f"Error creating lockscreen frame: {str(e)}")
        return None

def generate_video():
    """Generate a complete lockscreen video with random background and music."""
    print("Starting video generation...")
    
    # Ensure required directories exist
    required_dirs = ["bg_images", "music", "icons"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"Warning: Directory '{dir_name}' not found!")
            return
    
    # Pick random background
    bg_files = [f for f in os.listdir("bg_images") if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    if not bg_files:
        print("Error: No background images found in bg_images/")
        return
    
    bg_path = os.path.join("bg_images", random.choice(bg_files))
    print(f"Using background: {bg_path}")
    
    # Pick random music
    music_files = [f for f in os.listdir("music") if f.lower().endswith('.mp3')]
    if not music_files:
        print("Warning: No music files found in music/")
        music_path = None
    else:
        music_path = os.path.join("music", random.choice(music_files))
        print(f"Using music: {music_path}")
    
    # Generate AI notification text
    print("Generating notification text...")
    notif_msg = ai_function()
    
    # Create lockscreen frame
    print("Creating lockscreen frame...")
    frame = create_lockscreen_frame(bg_path, notif_msg)
    if frame is None:
        print("Error: Could not create lockscreen frame")
        return
    
    # Save temporary frame
    temp_frame_path = "temp_lockscreen_frame.png"
    cv2.imwrite(temp_frame_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    # Create video clip with fade-in effect
    print("Creating video clip...")
    video_duration = 6  # 6 seconds to match audio
    fade_duration = 1.0  # 1 second fade-in
    
    # Create video clip with smooth fade-in and fade-out effects
    try:
        clip = create_fade_clip(temp_frame_path, video_duration, fade_duration)
        print("Added custom fade-in and fade-out effects")
    except Exception as e:
        print(f"Error with fade effect: {e}")
        clip = ImageClip(temp_frame_path).with_duration(video_duration)
    
    # Add audio if available
    audio = None
    if music_path and os.path.exists(music_path):
        try:
            print(f"Loading audio from: {music_path}")
            audio = AudioFileClip(music_path)
            print(f"Audio duration: {audio.duration} seconds")
            
            # Keep audio running continuously without looping or trimming
            # Audio will play at its natural duration (6.11 seconds)
            print(f"Using audio at natural duration: {audio.duration} seconds")
            
            clip = clip.with_audio(audio)
            print("Audio added successfully to clip")
        except Exception as e:
            print(f"Warning: Could not add audio: {e}")
            import traceback
            traceback.print_exc()
    
    # Create output directory
    os.makedirs("outputVideos", exist_ok=True)
    
    # Generate unique filename
    output_filename = f"lockscreen_{random.randint(1000, 9999)}.mp4"
    output_path = os.path.join("outputVideos", output_filename)
    
    # Export video
    print(f"Exporting video to {output_path}...")
    try:
        clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio=True,
            audio_codec='aac'
        )
        print(f"✅ Video saved successfully: {output_path}")
        
        # Clean up temporary frame
        if os.path.exists(temp_frame_path):
            os.remove(temp_frame_path)
            
    except Exception as e:
        print(f"Error exporting video: {e}")
    
    # Close clips to free memory
    clip.close()
    if 'audio' in locals() and audio is not None:
        try:
            audio.close()
        except:
            pass

def batch_generate_videos(count=1):
    """Generate multiple videos in batch."""
    for i in range(count):
        print(f"\n--- Generating video {i+1}/{count} ---")
        generate_video()
        print(f"Completed {i+1}/{count}")

if __name__ == "__main__":
    # Generate a single video
    generate_video()
    
    # Or generate multiple videos:
    # batch_generate_videos(3)