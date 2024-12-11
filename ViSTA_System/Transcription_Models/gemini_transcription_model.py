from .transcription_model import TranscriptionModel
from .transcription import Transcription
import google.generativeai as genai
import os


class GeminiTranscriptionModel(TranscriptionModel):

    def __init__(self,raw_transcription_prompt_file,detail_extraction_prompt_file,token_tracker):
        super().__init__(raw_transcription_prompt_file,detail_extraction_prompt_file,token_tracker)
        goog_key = os.environ.get("GOOG_KEY")
        genai.configure(api_key=goog_key)
        generation_config = genai.GenerationConfig(temperature=0)
        self.__model = genai.GenerativeModel("gemini-1.5-pro", generation_config=generation_config)


    def generate_transcription(self,image_file):
        """
        Generates a raw transcription of the text from the given image_file
        Inputs:
            - None
        Outputs:
            - returns a Transcription object from the response generated by the model
            - self.token_tracker is initialized with the number of tokens used in the request
        """
        #Make request to transcribe the raw text off of the image
        response = self.__model.generate_content(contents=[self.raw_transcription_prompt, image_file])
        token_data = response.usage_metadata
        self.token_tracker.update_token_tracker(token_data) #Update token tracker with new token counts
        raw_transcription = response.text

        #Make request to extract photographer name and dates from the given transcription
        detail_extraction_prompt = f"{self.detail_extraction_prompt}{raw_transcription}"
        detail_extraction = self.__model.generate_content(contents=[detail_extraction_prompt]).text
        token_data = response.usage_metadata
        self.token_tracker.update_token_tracker(token_data) #Update token tracker with new token counts

        transcription = Transcription(raw_transcription,detail_extraction)
        return transcription


