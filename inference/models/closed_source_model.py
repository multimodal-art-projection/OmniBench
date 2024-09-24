import torch
import base64
from PIL import Image
from abc import ABC, abstractmethod
from openai import OpenAI
import base64
from PIL import Image
import io
import google.generativeai as genai
from PIL import Image
from reka import ChatMessage
from reka.client import Reka



class APIInferencer(ABC):
    @abstractmethod
    def infer(self, prompt: str, image_path: str) -> str:
        pass

    def load_client(self):
        return OpenAI(
            api_key='xxx',
            base_url="your_base_url",
        )

    def cleanup(self):
        if hasattr(self, 'client'):
            del self.client

    def encode_image_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def get_correct_response(
                            self, 
                            model_name: str, 
                            system_prompt: str, 
                            user_prompt: str, 
                            image_path: str, 
                            temperature: float
                            ) -> str:
        response = self.model_chat(model_name, system_prompt, user_prompt, image_path, temperature)
        return response
    

    def model_chat(self, model_name: str, system_prompt: str, user_prompt: str, image_path: str, temperature: float) -> str:
        client = self.load_client()
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            } if system_prompt else {},
            {
                "role": "user",
                "content": self.build_message_content(user_prompt, image_path)
            }
        ]
        messages = [msg for msg in messages if msg]
        
        max_attempts = 20
        for attempt in range(max_attempts):
            try:
                completion = client.chat.completions.create(model=model_name, messages=messages, temperature=temperature)
                return completion.choices[0].message.content
            except Exception as e:
                print(f"Error occurred on attempt {attempt + 1}: {e}")
                if attempt == max_attempts - 1:
                    print("Max attempts reached. Exiting.")
                    return ""  # Or raise an error, depending on your preference
            
    def build_message_content(self, prompt: str, image_path: str):
        if image_path == "Null":
            return prompt
        base64_image = self.encode_image_to_base64(image_path)
        return [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                },
            },
        ]

class BaseInferencer(APIInferencer):
    def __init__(self, model_name: str):
        self.model_name = model_name

    def infer(self, system_prompt: str, prompt: str, image_path: str, temperature: float) -> str:
        response = self.get_correct_response(self.model_name, system_prompt, prompt, image_path, temperature)
        return response

class GPT4oInferencer(BaseInferencer):
    def __init__(self):
        super().__init__('gpt-4o-0513')

class GPT4o_0806_Inferencer(BaseInferencer):
    def __init__(self):
        super().__init__('gpt-4o-0806')

class Claude35Inferencer(BaseInferencer):
    def __init__(self):
        super().__init__('claude35_sonnet')

class GPT4VInference(BaseInferencer):
    def __init__(self):
        super().__init__('gpt-4-vision-preview')

class Gemini15ProInference(BaseInferencer):
    def __init__(self):
        super().__init__('gemini-1.5-pro')

class GPT4TurboInference(BaseInferencer):
    def __init__(self):
        super().__init__('gpt-4-turbo-128k')

class GPT4TurboVisionInference(BaseInferencer):
    def __init__(self):
        super().__init__('gpt-4-0409')

class GPT35turboInference(BaseInferencer):
    def __init__(self):
        super().__init__('gpt-3.5-turbo')

class GPT4oMiniInference(BaseInferencer):
    def __init__(self):
        super().__init__('gpt-4o-mini-0718')



class Gemini15ProInference(APIInferencer):
    MAX_RETRIES = 10

    def load_model(self):
        """Load the model with the given API key."""
        genai.configure(api_key="xxx")
    
    def infer(self, prompt: str, image_path: str = None, audio_file_path: str = None, temperature: float = 0.0) -> str:
        """Infer response using the model, with optional image and audio input."""
        input_list = [prompt]
        
        # Upload the image if provided
        if image_path:
            image_file = genai.upload_file(path=image_path)
            input_list.append(image_file)
        
        # Upload the audio if provided
        if audio_file_path:
            audio_file = genai.upload_file(path=audio_file_path)
            input_list.append(audio_file)

        for attempt in range(self.MAX_RETRIES):
            try:
                response = genai.GenerativeModel(model_name="gemini-1.5-pro").generate_content(
                    input_list,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                    ),
                ).text
                
                if response:
                    return response
            
            except Exception as e:
                print(f"Error occurred: {e}")
        
        # If all attempts fail, return an empty string
        return ""
        

    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode the specified image to a base64 string."""
        with Image.open(image_path) as img:
            # Resize the image to not exceed 1024x1024
            max_size = (1024, 1024)
            img.thumbnail(max_size)

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='png', quality=85)  # Use PNG with specified quality
            img_byte_arr = img_byte_arr.getvalue()
            return base64.b64encode(img_byte_arr).decode('utf-8')



class RekaInferencer(APIInferencer):
    MAX_RETRIES = 3
    def load_model(self, api_key: str = 'xxx'):
        self.api_key = api_key
        self.client = Reka(api_key=self.api_key)
        
    def infer(self, system_prompt: str, user_prompt: str, image_path: str = None, audio_path: str = None, temperature: float = 0.0) -> str:
        """Infer response using the Reka API, with optional system prompt and multimodal input."""
        response = self.get_correct_response(system_prompt, user_prompt, image_path, audio_path, temperature)
        return response

    def get_correct_response(self, system_prompt: str, user_prompt: str, image_path: str = None, audio_path: str = None, temperature: float = 0.0) -> str:
        # Prepare the message content
        content = []
        
        if image_path:
            content.append({"type": "image_url", "image_url": image_path})
        
        if audio_path:
            content.append({"type": "audio_url", "audio_url": audio_path})
        
        if user_prompt:
            content.append({"type": "text", "text": user_prompt})
        
        # Create the message list with roles
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        if content:
            messages.append(ChatMessage(content=content, role="user"))

        # Retry mechanism
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.client.chat.create(
                    messages=messages,
                    model="reka-core-20240501"
                )
                return response.responses[0].message.content
            
            except Exception as e:
                print(f"Error occurred on attempt {attempt + 1}: {e}")
                
                if attempt == self.MAX_RETRIES - 1:  # If it's the last attempt
                    return ""

    def build_message_content(self, prompt: str, image_path: str):
        # This method is no longer used separately and can be removed.
        pass

    def cleanup(self):
        """Cleanup the client if necessary."""
        if self.client:
            del self.client
