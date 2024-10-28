# Blender Commands Enhanced Search Application

import json
from rapidfuzz import process, fuzz
from colorama import init, Fore, Back, Style
import textwrap

# Initialize colorama for cross-platform colored output
init()

cheat_sheet_path = r'F:\exo-cortex\device\designs\cheat_sheet.json'

def load_cheat_sheet(filepath=cheat_sheet_path):
    """
    Loads the cheat sheet from a JSON file.
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
        return data["cheat_sheet"]

def search_commands(query, cheat_sheet, limit=3, score_threshold=45):
    """
    Enhanced search for commands using fuzzy matching and multiple search criteria.
    
    Args:
        query (str): The natural language query.
        cheat_sheet (list): The cheat sheet data.
        limit (int): Maximum number of results to return.
        score_threshold (int): Minimum score for a match to be considered.

    Returns:
        list: A list of matching command dictionaries with scores.
    """
    results = []
    query = query.lower()
    
    # Split query into words for better matching
    query_words = set(query.split())
    
    for idx, item in enumerate(cheat_sheet):
        # Create searchable text combining description and keywords
        description = item["description"].lower()
        keywords = " ".join(item.get("keywords", [])).lower()
        category = item["category"].lower()
        
        # Calculate different types of matches
        desc_score = fuzz.WRatio(query, description)
        keyword_score = fuzz.WRatio(query, keywords)
        category_score = fuzz.WRatio(query, category)
        
        # Calculate word match score
        word_matches = sum(1 for word in query_words if word in description or word in keywords)
        word_score = (word_matches / len(query_words)) * 100 if query_words else 0
        
        # Calculate weighted final score
        final_score = (
            desc_score * 0.4 +      # Description match weight
            keyword_score * 0.4 +    # Keyword match weight
            category_score * 0.1 +   # Category match weight
            word_score * 0.1         # Word match weight
        )
        
        if final_score >= score_threshold:
            results.append({
                **item,
                "score": final_score,
                "match_details": {
                    "description_score": desc_score,
                    "keyword_score": keyword_score,
                    "category_score": category_score,
                    "word_score": word_score
                }
            })
    
    # Sort results by score in descending order
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

def wrap_text(text, width=80):
    """Wrap text to specified width while preserving newlines in code."""
    if '\n' in text:  # If text contains newlines (like code), preserve them
        return '\n'.join(line for line in text.split('\n'))
    return '\n'.join(textwrap.wrap(text, width=width))

def display_results(results):
    """
    Displays the search results in a formatted and colored manner.

    Args:
        results (list): List of matching command dictionaries.
    """
    if not results:
        print(f"\n{Fore.RED}No matching commands found.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Tip: Try using different terms or check the available keywords for this command.{Style.RESET_ALL}\n")
        return

    print(f"\n{Fore.GREEN}Found {len(results)} matching command(s):{Style.RESET_ALL}\n")
    
    for idx, match in enumerate(results, 1):
        # Print separator
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        # Print result header with score
        print(f"{Fore.YELLOW}Result {idx} {Style.BRIGHT}(Score: {match['score']:.1f}){Style.RESET_ALL}")
        
        # Print category
        print(f"{Fore.MAGENTA}Category: {Style.RESET_ALL}{match['category']}")
        
        # Print description
        print(f"{Fore.MAGENTA}Description: {Style.RESET_ALL}{wrap_text(match['description'])}")
        
        # Print keywords if available
        if "keywords" in match:
            print(f"{Fore.MAGENTA}Related terms: {Style.RESET_ALL}{wrap_text(', '.join(match['keywords']))}")
        
        # Print command with special formatting
        print(f"\n{Fore.GREEN}Command:{Style.RESET_ALL}")
        print(f"{Back.BLACK}{Fore.WHITE}{wrap_text(match['command'])}{Style.RESET_ALL}")
        
        # Print match details
        if "match_details" in match:
            print(f"\n{Fore.BLUE}Match Details:{Style.RESET_ALL}")
            for key, value in match["match_details"].items():
                print(f"  {key}: {value:.1f}")
        
        print()  # Add spacing between results

def main():
    cheat_sheet = load_cheat_sheet()

    # Print header with styling
    print(f"\n{Back.BLUE}{Fore.WHITE} Blender Python Commands Enhanced Search {Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Enter a description of what you want to do, or type 'exit' to quit.{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Tip: Use natural language or keywords to describe what you want to achieve.{Style.RESET_ALL}\n")

    while True:
        try:
            user_input = input(f"{Fore.CYAN}Search Query{Fore.WHITE} > {Style.RESET_ALL}").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print(f"\n{Fore.GREEN}Exiting the search application.{Style.RESET_ALL}")
                break
            elif not user_input:
                print(f"{Fore.YELLOW}Please enter a valid query.{Style.RESET_ALL}")
                continue

            matches = search_commands(user_input, cheat_sheet)
            display_results(matches)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Search interrupted. Press Ctrl+C again to exit.{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()




