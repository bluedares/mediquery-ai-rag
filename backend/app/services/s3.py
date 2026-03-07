"""
S3 Service - Document Storage
"""

import boto3
from typing import Optional, BinaryIO
from botocore.exceptions import ClientError
import io

from ..config import settings
from ..utils.logger import logger


class S3Service:
    """
    S3 service for document storage
    
    Features:
    - Upload documents
    - Download documents
    - Delete documents
    - List documents
    - Presigned URLs
    """
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize S3 service
        
        Args:
            bucket_name: S3 bucket name (defaults to settings)
        """
        self.bucket_name = bucket_name or settings.s3_bucket
        
        try:
            # Initialize boto3 client with credentials
            self.client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            
            logger.info(
                "✅ S3 client initialized",
                bucket=self.bucket_name,
                region=settings.aws_region
            )
        except Exception as e:
            logger.error(
                "❌ Failed to initialize S3 client",
                error=str(e),
                bucket=self.bucket_name
            )
            raise
    
    async def upload_file(
        self,
        file_obj: BinaryIO,
        key: str,
        content_type: str = 'application/pdf',
        metadata: Optional[dict] = None
    ) -> str:
        """
        Upload file to S3
        
        Args:
            file_obj: File object to upload
            key: S3 object key
            content_type: MIME type
            metadata: Optional metadata
            
        Returns:
            S3 URI
        """
        try:
            # Upload file
            extra_args = {
                'ContentType': content_type,
                'ServerSideEncryption': 'AES256'
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            s3_uri = f"s3://{self.bucket_name}/{key}"
            
            logger.info(
                "✅ File uploaded to S3",
                key=key,
                bucket=self.bucket_name,
                uri=s3_uri
            )
            
            return s3_uri
            
        except ClientError as e:
            logger.error(
                "❌ Error uploading to S3",
                error=str(e),
                key=key
            )
            raise
    
    async def download_file(self, key: str) -> bytes:
        """
        Download file from S3
        
        Args:
            key: S3 object key
            
        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            content = response['Body'].read()
            
            logger.debug(
                "✅ File downloaded from S3",
                key=key,
                size_bytes=len(content)
            )
            
            return content
            
        except ClientError as e:
            logger.error(
                "❌ Error downloading from S3",
                error=str(e),
                key=key
            )
            raise
    
    async def delete_file(self, key: str) -> bool:
        """
        Delete file from S3
        
        Args:
            key: S3 object key
            
        Returns:
            True if successful
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            
            logger.info(
                "🗑️  File deleted from S3",
                key=key
            )
            
            return True
            
        except ClientError as e:
            logger.error(
                "❌ Error deleting from S3",
                error=str(e),
                key=key
            )
            raise
    
    async def list_files(self, prefix: str = "") -> list:
        """
        List files in S3 bucket
        
        Args:
            prefix: Key prefix to filter
            
        Returns:
            List of file keys
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
            
            logger.debug(
                "📋 Listed S3 files",
                count=len(files),
                prefix=prefix
            )
            
            return files
            
        except ClientError as e:
            logger.error(
                "❌ Error listing S3 files",
                error=str(e),
                prefix=prefix
            )
            raise
    
    async def get_presigned_url(
        self,
        key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate presigned URL for file access
        
        Args:
            key: S3 object key
            expiration: URL expiration in seconds
            
        Returns:
            Presigned URL
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            
            logger.debug(
                "🔗 Generated presigned URL",
                key=key,
                expiration=expiration
            )
            
            return url
            
        except ClientError as e:
            logger.error(
                "❌ Error generating presigned URL",
                error=str(e),
                key=key
            )
            raise
    
    async def health_check(self) -> bool:
        """
        Check if S3 bucket is accessible
        
        Returns:
            True if service is healthy
        """
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except Exception as e:
            logger.warning(
                "⚠️  S3 health check failed",
                error=str(e),
                bucket=self.bucket_name
            )
            return False


# Global service instance
# Commented out to prevent initialization on import - instantiate when needed
# s3_service = S3Service()
