import mimetypes
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from app.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_REGION_NAME, AWS_STORAGE_BUCKET_NAME, \
    AWS_S3_CUSTOM_DOMAIN

class AWSBucket:

    @staticmethod
    def get_instance():
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_S3_REGION_NAME
        )


    @staticmethod
    def upload_to_s3(file_path: str, file_key: str) -> str:
        """
        Uploads a file via file path to an S3 bucket.

        :param file_path: The file path to upload.
        :param file_key: The desired file name in the bucket.
        :return: S3 file URL
        """

        if not isinstance(file_path, str):
            raise Exception("The file_path should be a string, not a file object!")

        s3_client = AWSBucket.get_instance()

        # Get the content type based on the file extension
        content_type, _ = mimetypes.guess_type(file_path)

        if content_type is None:
            # Default fallback
            content_type = "application/octet-stream"

        try:
            # Upload file to S3
            s3_client.upload_file(
                Filename=file_path,
                Bucket=AWS_STORAGE_BUCKET_NAME,
                Key=file_key,
                ExtraArgs={
                    "ContentType": content_type,
                }
            )

            # Generate the S3 file URL.
            file_url = f"https://{AWS_S3_CUSTOM_DOMAIN}/{file_key}"

        except NoCredentialsError:
            raise Exception("AWS credentials not found.")

        except PartialCredentialsError:
            raise Exception("Incomplete AWS credentials.")

        return file_url


    @staticmethod
    def upload_file_object_to_s3(file, file_key: str) -> str:
        """
        Uploads a file object to an S3 bucket.

        :param file: The file object to upload.
        :param file_key: The desired file name in the bucket.
        :return: S3 file URL
        """

        if isinstance(file, str):
            raise Exception("The file should be a file object, not a string!")

        s3_client = AWSBucket.get_instance()

        try:
            # Upload file to S3
            s3_client.upload_fileobj(
                Fileobj=file,
                Bucket=AWS_STORAGE_BUCKET_NAME,
                Key=file_key,
                ExtraArgs={
                    "ContentType": file.content_type,
                }
            )

            # Generate the S3 file URL.
            file_url = f"https://{AWS_S3_CUSTOM_DOMAIN}/{file_key}"

        except NoCredentialsError:
            raise Exception("AWS credentials not found.")

        except PartialCredentialsError:
            raise Exception("Incomplete AWS credentials.")

        return file_url
