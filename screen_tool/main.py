from .capture import capture_fullscreen, capture_region
from .analyze import analyze_image

def analyze_screen(command: str, use_region: bool = False, use_context: bool = True) -> dict:
    """
    Main entrypoint for the Screen Insight Tool.
    
    Args:
        command: The prompt for the Jarvis AI (e.g., "Analyze my screen")
        use_region: If True, opens a UI to select a specific screen region.
        use_context: Whether to maintain and use conversation history.
        
    Returns:
        A dictionary containing the structured model response.
    """
    try:
        # Step 1: Capture Screen
        if use_region:
            img_path = capture_region()
        else:
            img_path = capture_fullscreen()
            
        # Step 2: Analyze using Vision Model
        result = analyze_image(img_path, command, use_context=use_context)
        return result
        
    except Exception as e:
        return {"error": str(e)}
