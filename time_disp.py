import pygame
import datetime

# Initialize pygame font system (add this near your pygame.init())
pygame.font.init()

def read_images_from_file():
    images = []
    for i in range(8):  # Varsayılan olarak 8 resim okuyor
        try:
            image_path = f"images/{i}.jpg"
            image = pygame.image.load(image_path)
            images.append(image)
        except Exception as e:
            print(f"Error loading image from file {image_path}: {e}")
    return images
    
def display_current_time(screen):
    current_time = datetime.datetime.now().strftime("%H:%M")
    font = pygame.font.SysFont('Arial', 30) 
    
    text_surface = font.render(current_time, True, (255, 0, 0))  # Red color
    
    text_rect = text_surface.get_rect()
    
    text_rect.topright = (screen.get_width() - 10, 10) 
    
    screen.blit(text_surface, text_rect)

def add_timestamp_to_surface(surface):
    """Modifies the given surface by adding a timestamp in the top right corner"""
    # Get current time
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    # Create a font object
    font = pygame.font.SysFont('Arial', 30)
    
    # Render the text in red with a slight black outline for better visibility
    text_color = (255, 0, 0)  # Red
    outline_color = (0, 0, 0)  # Black
    
    # Create outline by rendering text in black with small offsets
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        outline = font.render(current_time, True, outline_color)
        outline_rect = outline.get_rect(topright=(surface.get_width() - 10 + dx, 10 + dy))
        surface.blit(outline, outline_rect)
    
    # Render main text
    text_surface = font.render(current_time, True, text_color)
    text_rect = text_surface.get_rect(topright=(surface.get_width() - 10, 10))
    surface.blit(text_surface, text_rect)
    
    return surface
# Your modified main loop would look like this:
def main():
    pygame.init()
    screen = pygame.display.set_mode((480, 480))
    pygame.display.set_caption("NASA EPIC Images")
    clock = pygame.time.Clock()
    running = True
    index = 0
    
    # Load your images
    images = read_images_from_file()
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        current_minute = datetime.datetime.now().minute
        
        # Check if minute has changed (to update timestamp)
        img = add_timestamp_to_surface(images[index].copy())
        
        screen.blit(img, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()