"""
Voice calls module for the Briq API — Phase 6.
All routes under /v1/voice/
"""


class VoiceAPI:
    """
    Voice API for Briq.

    Provides methods for initiating voice calls using a URL, file upload, or TTS.
    """

    def __init__(self, client):
        self.client = client

    def call_audio(self, receiver_number, audio_url):
        """
        POST /v1/voice/calls/audio — initiate a voice call that plays audio from a URL.

        Args:
            receiver_number (str): E.164 or national number to call (e.g. "255788344348")
            audio_url (str): Public URL of the audio file (MP3 or WAV)

        Returns:
            dict: Response data
        """
        return self.client.post("voice/calls/audio", data={
            "receiver_number": receiver_number,
            "audio_url": audio_url,
        })

    def call_audio_upload(self, receiver_number, file):
        """
        POST /v1/voice/calls/audio/upload — upload a local audio file and initiate a call.

        Args:
            receiver_number (str): E.164 or national number to call
            file: File-like object (open binary stream) for the audio file (MP3 or WAV)

        Returns:
            dict: Response data
        """
        return self.client.post(
            "voice/calls/audio/upload",
            files={"file": file},
            data={"receiver_number": receiver_number},
        )

    def call_tts(self, receiver_number, text):
        """
        POST /v1/voice/calls/tts — initiate a voice call that speaks text (TTS).

        Args:
            receiver_number (str): E.164 or national number to call
            text (str): Text to be spoken to the recipient

        Returns:
            dict: Response data
        """
        return self.client.post("voice/calls/tts", data={
            "receiver_number": receiver_number,
            "text": text,
        })
