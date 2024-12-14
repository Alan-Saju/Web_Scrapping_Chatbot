import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import re

class WebsiteChatbot:
    def __init__(self, url, api_key):
       

        load_dotenv()
        
        
        if not url:
            raise ValueError("URL cannot be empty")
        if not api_key:
            raise ValueError("API key cannot be empty")
        
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.0-pro')
        
        
        self.url = self._validate_url(url)
        self.content = self._scrape_website()
    
    def _validate_url(self, url):
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Basic URL validation using regex
        url_pattern = re.compile(
            r'^https?://'  
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  
            r'localhost|'  
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  

            r'(?::\d+)?'  
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            raise ValueError(f"Invalid URL format: {url}")
        
        return url
    
    def _scrape_website(self):
        
        try:
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            
            for script in soup(["script", "style", "nav", "header", "footer", "iframe", "form"]):
                script.decompose()
            
            
            text = soup.get_text(separator=' ', strip=True)
            
            
            text = re.sub(r'\s+', ' ', text)  
            text = text.replace('\n', ' ')
            
            
            return text[:10000]
        
        except requests.RequestException as e:
            print(f"Error fetching website: {e}")
            return f"Unable to fetch website content. Error: {e}"
        except Exception as e:
            print(f"Unexpected error during scraping: {e}")
            return f"An unexpected error occurred: {e}"
    
    def generate_response(self, query):
        
        try:
        
            if not query or len(query.strip()) == 0:
                return "Please enter a valid query."
            
        
            prompt = f"""
            Context: The following text is from a website: {self.content}
            
            User Query: {query}
            
            Instructions:
            - Use the website context to provide a relevant and helpful response
            - If the context is insufficient, acknowledge that
            - Provide the best possible answer based on available information
            - Be concise and clear in your explanation
            """
            
            
            generation_config = {
                'max_output_tokens': 500,  # Limit response length
                'temperature': 0.7,  # Control randomness
                'top_p': 0.9  # Control diversity of response
            }
            
            response = self.model.generate_content(
                prompt, 
                generation_config=generation_config
            )
            
            return response.text
        
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I couldn't generate a response at the moment."

def main():
   
    print("\n=== Gemini Website Chatbot ===")
    print("Explore website content through conversational AI")
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        print("Please set up your Gemini API key in the .env file")
        return
    
    try:
       
        url = input("Enter the website URL to analyze: ").strip()
        
        
        chatbot = WebsiteChatbot(url, api_key)
        
        
        print("\nWebsite content loaded successfully!")
        print("Type 'exit' to end the conversation")
        
        while True:
            query = input("\nYou: ").strip()
            
            if query.lower() == 'exit':
                print("Goodbye! Thank you for using the Website Chatbot.")
                break
            
            
            response = chatbot.generate_response(query)
            print("\nChatbot:", response)
    
    except ValueError as ve:
        print(f"Input Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()