import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

class WebsiteChatbot:
    def __init__(self, url, api_key):
        """
        Initialize the chatbot with a website URL and Gemini API key
        
        Args:
            url (str): The website URL to scrape
            api_key (str): Google Gemini API key
        """
        load_dotenv()
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Website scraping
        self.url = url
        self.content = self._scrape_website()
    
    def _scrape_website(self):
        """
        Scrape website content and extract text
        
        Returns:
            str: Cleaned and processed website text
        """
        try:
            # Fetch website content
            response = requests.get(self.url)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, and navigation elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Extract text and clean
            text = soup.get_text(separator=' ', strip=True)
            
            # Limit text to first 10000 characters to avoid API limits
            return text[:10000]
        
        except requests.RequestException as e:
            print(f"Error fetching website: {e}")
            return "Unable to fetch website content."
    
    def generate_response(self, query):
        """
        Generate a response using Gemini based on website content and user query
        
        Args:
            query (str): User's input query
        
        Returns:
            str: Generated response from Gemini
        """
        try:
            # Construct prompt with website context
            prompt = f"""
            Context: The following text is from a website: {self.content}
            
            User Query: {query}
            
            Use the website context to provide a relevant and helpful response.
            If the context is insufficient, acknowledge that and provide the best possible answer.
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Sorry, I couldn't generate a response at the moment."

def main():
    # Load API key from environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        return
    
    # Specify the URL you want to chat about
    url = input("Enter the website URL to analyze: ")
    
    # Create chatbot instance
    chatbot = WebsiteChatbot(url, api_key)
    
    # Interactive chat loop
    print("\n=== Website Chatbot ===")
    print("Type 'exit' to end the conversation")
    
    while True:
        query = input("\nYou: ")
        
        if query.lower() == 'exit':
            print("Goodbye!")
            break
        
        response = chatbot.generate_response(query)
        print("\nChatbot:", response)

if __name__ == "__main__":
    main()