# game_score_converter.py

"""
Required Variable Names:
- mining_score (string input like "100")
- mining_points (converted to integer)
- combat_score (decimal like 98.7)
- combat_points (converted to integer)
- achievement_hex (hex string like "1F")
- achievement_bonus (converted to integer)
- total_score (sum of all points)
- score_display (total score as string)
- player_stats (list with name and score)
"""

def convert_string_to_int(mining_score):
    """Convert string mining score to integer"""
    # Input validation (DON'T CHANGE THIS)
    if not isinstance(mining_score, str) or not mining_score.isdigit():
        raise ValueError("Score must be a string containing only digits")
    
    # TODO: Convert mining_score to integer
    # Hint: Use the int() function to convert string to integer
    # Example: "100" should become 100
    return None  # Replace None with your code

def convert_float_to_int(combat_score):
    """Convert float combat score to integer"""
    # Input validation (DON'T CHANGE THIS)
    if not isinstance(combat_score, float):
        raise ValueError("Score must be a float")
    if combat_score < 0:
        raise ValueError("Score must be non-negative")
    
    # TODO: Convert combat_score to integer
    # Hint: Use int() to remove decimal part
    # Example: 98.7 should become 98
    return None  # Replace None with your code

def convert_hex_to_int(achievement_hex):
    """Convert hexadecimal achievement score to integer"""
    # Input validation (DON'T CHANGE THIS)
    if not isinstance(achievement_hex, str) or not all(c in '0123456789ABCDEFabcdef' for c in achievement_hex):
        raise ValueError("Input must be a valid hexadecimal string")
    
    # TODO: Convert achievement_hex to integer
    # Hint: Use int(achievement_hex, 16) to convert hex to integer
    # Example: "1F" should become 31
    return None  # Replace None with your code

def convert_score_to_string(total_score):
    """Convert total score to string for display"""
    # Input validation (DON'T CHANGE THIS)
    if not isinstance(total_score, (int, float)):
        raise ValueError("Score must be a number")
    
    # TODO: Convert total_score to string
    # Hint: Use str() to convert number to string
    # Example: 150 should become "150"
    return None  # Replace None with your code

def create_player_list(player_name, total_score):
    """Create a list containing player name and score"""
    # Input validation (DON'T CHANGE THIS)
    if not isinstance(player_name, str) or not player_name:
        raise ValueError("Player name must be a non-empty string")
    
    # TODO: Create and return a list with player_name and total_score
    # Hint: Return them as [player_name, total_score]
    # Example: Input "Steve", 100 should return ["Steve", 100]
    return None  # Replace None with your code

if __name__ == "__main__":
    print("Minecraft Score Calculator")
    print("=" * 30)
    print("Welcome to the new Minecraft scoring system!")
    print("-" * 30)
    
    # TODO: Add your code here. Use these variable names:
    # 1. Ask user for mining_score and convert to mining_points
    # Hint: mining_score = input("Enter your mining points: ")
    
    # 2. Ask user for combat_score and convert to combat_points
    # Hint: Remember to convert input to float first
    
    # 3. Ask user for achievement_hex and convert to achievement_bonus
    # Hint: User will type something like "1F"
    
    # 4. Calculate total_score (add all points together)
    # Hint: total_score = mining_points + combat_points + achievement_bonus
    
    # 5. Convert total_score to score_display
    
    # 6. Get player_name and create player_stats list
    
    # 7. Display all results nicely formatted
    # Hint: Use print(f"Mining Points: {mining_points}")