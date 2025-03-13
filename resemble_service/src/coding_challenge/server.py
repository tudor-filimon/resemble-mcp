# server.py
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
from resemble import Resemble
import httpx

# Create an MCP server
# project id 49a55388
# voice id 55592656

mcp = FastMCP("Demo")

load_dotenv()

RESEMBLE_KEY = os.getenv('RESEMBLE_API_KEY')


@mcp.tool()
def list_voices(page: int, page_size: int) -> str:
    """
    Purpose: Get a list of all available voice models from Resemble AI.

    Args:
        page: The page number to fetch (starts from 1)
        page_size: Number of items per page (10 to 1000)

    Returns:
        A JSON structure containing model data. We need to only extract names from items.
    """
    try:
        # Ensure API key is loaded
        if not RESEMBLE_KEY:
            raise Exception("Error loading API key.")

        # Make sure page is at least 1
        if page < 1:
            raise Exception("Page number must be at least")


        # Make sure page_size is reasonable
        if page_size < 10 or page_size > 1000:
            raise Exception("Page size must be between 10 and 1000 (inclusive).")


        # Initialize Resemble client
        if not RESEMBLE_KEY:
            raise Exception("No Resemble API Key provided!")


        Resemble.api_key(RESEMBLE_KEY)
        # Get voices
        response = Resemble.v2.voices.all(page, page_size)

        if not response:
            raise Exception("Failed to retrieve voices or no voices found from Resemble models.")


        # Extract names from response using the items key
        voices = response['items']

        # Format the response to only output the name
        formatted_voices = []
        for voice in voices:
            voice_model_name = voice['name']
            voice_model_id = voice['uuid']
            voice_type = voice['voice_type']

            voice_info = f"""
    Voice Model Name: {voice_model_name}
    Voice Model ID: {voice_model_id}
    Voice Type: {voice_type}
                """
            formatted_voices.append(voice_info)

        if not formatted_voices:
            raise Exception("No formatted voices found for the given parameters")


        # format the result
        result = "\n\n----------\n\n".join(formatted_voices)

        # Return formatted models if it works
        return result

    except Exception as e:
        return f"Error occurred while fetching voices: {str(e)}"


@mcp.tool()
def text_to_speech(voice_uuid: int, data: str, sample_rate: int, accept_encoding: str) -> str:
    """
    Purpose: Given an input text, this will return a wav base64 encoding with a text-to-speech response with a specified voice uuid.

    Args:
        voice_uuid: id of the voice agent to use
        data: the text that will be converted in text-to-speech
        sample_rate: 8000, 16000, 22050, 32000, or 44100
        accept_encoding: part of the request header, and it is either gzip, deflate, br

    Returns:
        Audio content in Base64
    """

    try:
        # Ensure API key is loaded
        if not RESEMBLE_KEY:
            raise Exception("Error loading API key.")

        validated_uuid = str(voice_uuid).strip()

        # Ensure data is not greater than 3000 characters
        if len(data) > 3000:
            raise Exception("Error: Text length exceeds 3000 characters limit")


        #Ensure sample rate is valid
        valid_sample_rates = [8000, 16000, 22050, 32000, 44100, 48000]
        if int(sample_rate) not in valid_sample_rates:
            raise Exception(f"Error: Invalid sample rate. Must be one of {valid_sample_rates}")


        # Check encoding
        valid_encoding = ["gzip", "deflate", "br"]
        if accept_encoding not in valid_encoding:
            raise Exception(f"Error: Invalid encoding. Must be one of {valid_encoding}")

        #HTTP REQUEST
        url_endpoint = "https://f.cluster.resemble.ai/synthesize"

        headers = {
            "Authorization": f"Bearer {RESEMBLE_KEY}",
            "Content-Type": "application/json",
            "Accept-Encoding": f"{accept_encoding}"
        }

        body = {
            "voice_uuid": f"{validated_uuid}",
            "project_uuid": "49a55388",
            "data": data,
            "sample_rate": int(sample_rate),
            "output_format": "wav"
        }

        # Perform Post request for tts service
        try:
            response = httpx.post(url_endpoint, headers=headers, json=body)
            data = response.json()

            # Error trap for response
            if response.status_code != 200:
                raise Exception("Text to speech request failed.")


            # Extract output data
            audio_title = data.get("title", "Unknown Title")
            audio_duration = data.get("duration")

            # Base64 data is not extracted as it is too large to print
            # The user is informed that they can find their audio in Resemble's projects
            result = f"""
    The title of this recording was {audio_title} and it ran for {audio_duration} seconds. 
    Check your projects section in Resemble to see the recording!
            """

            return result

        except Exception as e:
            raise Exception(f"Error making post request to Resemble: {str(e)}")

    except Exception as e:
        return f"Error occurred during text-to-speech synthesis: {str(e)}"


def main():
    """Main function to start the MCP server."""
    print("Starting MCP Server...")

    try:
        mcp.run()
    except KeyboardInterrupt:
        print("Server shutting down.")

if __name__ == "__main__":
    main()
