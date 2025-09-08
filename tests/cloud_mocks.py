"""
Mock cloud service modules for testing
"""


class MockAWSService:
    @staticmethod
    def upload_file_to_s3(*args, **kwargs):
        return True

    @staticmethod
    def start_transcription_job(*args, **kwargs):
        return {"TranscriptionJob": {"JobName": "test-job"}}

    @staticmethod
    def wait_for_job_completion(*args, **kwargs):
        return {"TranscriptionJob": {"Transcript": {"TranscriptFileUri": "https://s3.amazonaws.com/test"}}}

    @staticmethod
    def download_transcription_result(*args, **kwargs):
        return {"results": []}

    @staticmethod
    def delete_file_from_s3(*args, **kwargs):
        return True


class MockAzureService:
    pass


class MockGCPService:
    pass


class MockTranscription:
    pass
