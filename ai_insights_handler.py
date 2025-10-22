import google.generativeai as genai
import PIL.Image

class AIInsights:
    def __init__(self,api_key):
        self.api_key=api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name = "gemini-2.0-flash")
        
    def get_ai_insights(self,image_path,stock):  

        image = PIL.Image.open(image_path)
        prompt = f"This is an image of stock performance of stock : '{stock}' for the last 100 days on the market. On the basis of volume traded, closing prices and 7, 20 day moving averages, provide some analysis and suggestion about this stock, including if the stock should be purchased or not."
        response = self.model.generate_content([prompt, image])
        return response

