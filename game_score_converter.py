def convert_string_to_int(mining_score):
    """Convert string mining score to integer"""
    if not isinstance(mining_score, str) or not mining_score.isdigit():
        raise ValueError("Score must be a string containing only digits")
    return int(mining_score)

def convert_float_to_int(combat_score):
    """Convert float combat score to integer"""
    if not isinstance(combat_score, float):
        raise ValueError("Score must be a float")
    if combat_score < 0:
        raise ValueError("Score must be non-negative")
    return int(combat_score)

def convert_hex_to_int(achievement_hex):
    """Convert hexadecimal achievement score to integer"""
    if not isinstance(achievement_hex, str) or not all(c in '0123456789ABCDEFabcdef' for c in achievement_hex):
        raise ValueError("Input must be a valid hexadecimal string")
    return int(achievement_hex, 16)

def convert_score_to_string(total_score):
    """Convert total score to string for display"""
    if not isinstance(total_score, (int, float)):
        raise ValueError("Score must be a number")
    return str(total_score)

def create_player_list(player_name, total_score):
    """Create a list containing player name and score"""
    if not isinstance(player_name, str) or not player_name:
        raise ValueError("Player name must be a non-empty string")
    return [player_name, total_score]

if __name__ == "__main__":
    print("Minecraft Score Calculator")
    print("=" * 30)
    print("Welcome to the new Minecraft scoring system!")
    print("-" * 30)
    
    # Get mining score (string format)
    mining_score = input("Enter your mining points (e.g., '100'): ")
    mining_points = convert_string_to_int(mining_score)
    print(f"Mining points: {mining_points}")
    
    # Get combat score (float format)
    combat_score = float(input("Enter your combat accuracy (e.g., 98.7): "))
    combat_points = convert_float_to_int(combat_score)
    print(f"Combat points: {combat_points}")
    
    # Get achievement bonus (hex format)
    achievement_hex = input("Enter achievement bonus in hex (e.g., 'A' or '1F'): ")
    achievement_bonus = convert_hex_to_int(achievement_hex)
    print(f"Achievement bonus: {achievement_bonus}")
    
    # Calculate total score
    total_score = mining_points + combat_points + achievement_bonus
    score_display = convert_score_to_string(total_score)
    
    # Create player record
    player_name = input("\nEnter your Minecraft username: ")
    player_stats = create_player_list(player_name, total_score)
    
    print("\n" + "=" * 30)
    print(f"Final Stats for {player_name}:")
    print(f"Mining Points: {mining_points}")
    print(f"Combat Points: {combat_points}")
    print(f"Achievement Bonus: {achievement_bonus}")
    print(f"Total Score: {score_display}")
    print("=" * 30)