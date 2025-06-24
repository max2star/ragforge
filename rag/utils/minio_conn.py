#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import os
# Only set SSL_CERT_FILE if the certificate file exists (for production environment)
if os.path.exists('/etc/nginx/public.crt'):
    os.environ['SSL_CERT_FILE']='/etc/nginx/public.crt'
import logging
import time
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from rag import settings
from rag.utils import singleton
from minio.commonconfig import CopySource
from minio.commonconfig import ENABLED
from minio.versioningconfig import VersioningConfig
from minio.error import S3Error
import subprocess
from minio.sseconfig import Rule, SSEConfig


@singleton
class RAGFlowMinio:
    def __init__(self):
        self.secure = True
        self.conn = None
        self.remote_conn = None
        self.remote_flag = False
        self.bucket_encryption = True
        self.__open__()
    def __open__(self):
        try:
            if self.conn or self.remote_conn:
                self.__close__()
        except Exception:
            pass

        try:
            logging.info("cluster {},backup clutser {}".format(settings.MINIO,settings.MINIO_BACKUP))
            
            # Use HTTP for localhost/development environment, HTTPS for production
            is_localhost = settings.MINIO["host"].startswith("localhost") or settings.MINIO["host"].startswith("127.0.0.1")
            secure_connection = not is_localhost
            self.secure = secure_connection  # Update the instance variable
            
            self.conn = Minio(settings.MINIO["host"],
                              access_key=settings.MINIO["user"],
                              secret_key=settings.MINIO["password"],
                              secure=secure_connection
                              )
            self.bucket_encryption = settings.MINIO.get("bucket_encryption", True)
            if type(settings.MINIO['bucket_encryption']) == str:
                logging.info(f"settings.MINIO['bucket_encryption'] {settings.MINIO['bucket_encryption']} type {type(settings.MINIO['bucket_encryption'])}")
                self.bucket_encryption = settings.MINIO['bucket_encryption'].lower() == "true"
            logging.info(f"self.bucket_encryption {self.bucket_encryption} type {type(self.bucket_encryption)}")
            if settings.MINIO_BACKUP.get("host",None):
                logging.info(f"enable minio backup cluster")
                backup_is_localhost = settings.MINIO_BACKUP["host"].startswith("localhost") or settings.MINIO_BACKUP["host"].startswith("127.0.0.1")
                backup_secure = not backup_is_localhost
                self.remote_conn =  Minio(settings.MINIO_BACKUP["host"],
                                  access_key=settings.MINIO_BACKUP["user"],
                                  secret_key=settings.MINIO_BACKUP["password"],
                                  secure=backup_secure
                                  )
                self.remote_flag = True
                self.config_alias(src_cluster_alias=None,dest_cluster_alias=None)
            else:
                logging.info(f"not enable minio backup cluster")
        except Exception:
            logging.exception(
                "Fail to connect {} or {}".format(settings.MINIO["host"],settings.MINIO_BACKUP["host"]))

    def config_alias(self,src_cluster_alias,dest_cluster_alias):
        if not self.remote_flag:
            return
        src_cluster_alias = "minio-cluster-1"
        dest_cluster_alias = "minio-cluster-2"
        if self.secure:
            prefix_ = "https://"
        else:
            prefix_ = "http://"

        cmd1 = [
            'mc',
            'alias',
            'set',f'{src_cluster_alias}',f'{prefix_}{settings.MINIO["host"]}',f'{settings.MINIO["user"]}',f'{settings.MINIO["password"]}',
            '--insecure'
        ]
        cmd2 = [
            'mc',
            'alias',
            'set',f'{dest_cluster_alias}',f'{prefix_}{settings.MINIO_BACKUP["host"]}',f'{settings.MINIO_BACKUP["user"]}',f'{settings.MINIO_BACKUP["password"]}',
            '--insecure'
        ]

        try:
            process = subprocess.run(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.returncode != 0:
                logging.warning(f"mc command failed: {process.stderr.decode()}")
                return
            logging.info(f"config_alias {cmd1} excuted,result {process.returncode}")

            process = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.returncode != 0:
                logging.warning(f"mc command failed: {process.stderr.decode()}")
                return
            logging.info(f"config_alias {cmd2} excuted,result {process.returncode}")
        except FileNotFoundError:
            logging.warning("MinIO client (mc) not found. Skipping alias configuration. This is normal for development environments.")
        except Exception as e:
            logging.warning(f"Failed to configure MinIO aliases: {str(e)}")

    def config_backup_policy(self,src_cluster_alias,source_bucket, dest_cluster_alias,dest_bucket):
        if not self.remote_flag:
            return
        src_cluster_alias = "minio-cluster-1"
        dest_cluster_alias = "minio-cluster-2"
        if not dest_bucket:
            dest_bucket=source_bucket
        cmd = [
            'mc',
            'replicate',
            'add',
            '--priority', '10',
            '--remote-bucket', f"{dest_cluster_alias}/{dest_bucket}",
            '--limit-upload','1000Mi',
            #'--sync',
            f"{src_cluster_alias}/{source_bucket}"
        ]
        logging.info(f"config_backup_policy {cmd}")
        try:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if process.returncode != 0:
                logging.warning(f"mc command failed: {process.stderr.decode()}")
                return
            logging.info(f"config_backup_policy {cmd} excuted,result {process.returncode}")
        except FileNotFoundError:
            logging.warning("MinIO client (mc) not found. Skipping backup policy configuration. This is normal for development environments.")
        except Exception as e:
            logging.warning(f"Failed to configure backup policy: {str(e)}")

    def __close__(self):
        del self.conn
        self.conn = None
        if self.remote_conn:
            del self.remote_conn
            self.remote_conn=None

    def health(self):
        bucket, fnm, binary = "txtxtxtxt1", "txtxtxtxt1", b"_t@@@1"
        if not self.conn.bucket_exists(bucket):
            self.conn.make_bucket(bucket)
        r = self.conn.put_object(bucket, fnm,
                                 BytesIO(binary),
                                 len(binary)
                                 )
        return r

    def put(self, bucket, fnm, binary):
        for _ in range(3):
            try:
                if not self.conn.bucket_exists(bucket):
                    self.conn.make_bucket(bucket)
                    config = VersioningConfig(ENABLED)
                    self.conn.set_bucket_versioning(bucket, config)
                    encryption_rule = Rule(
                        sse_algorithm="aws:kms",  # 指定使用 KMS 加密
                        kms_master_key_id='my-key-1'# 指定 KMS 密钥 ID
                    )
                    sse_config = SSEConfig(rule=encryption_rule)
                    if self.bucket_encryption:
                        self.conn.set_bucket_encryption(
                            bucket, sse_config)

                    if self.remote_flag:
                        self.remote_conn.make_bucket(bucket)
                        self.remote_conn.set_bucket_versioning(bucket, config)
                        self.config_backup_policy(src_cluster_alias=None,source_bucket=bucket,dest_cluster_alias=None,dest_bucket=bucket)
                    if self.bucket_encryption:
                        self.remote_conn.set_bucket_encryption(bucket, sse_config)

                r = self.conn.put_object(bucket, fnm,
                                         BytesIO(binary),
                                         len(binary)
                                         )
                # 验证文件是否成功上传
                if self.obj_exist(bucket, fnm):
                    return r
                else:
                    logging.error(f"File {fnm} upload verification failed in bucket {bucket}")
                    continue
            except Exception as e:
                logging.exception(f"Fail to put {bucket}/{fnm}: {str(e)}")
                self.__open__()
                time.sleep(1)
            return None
        return None

    def list_objs(self,bucket,prefix,recursive):
        if not prefix.endswith("/"): prefix += "/"
        return self.conn.list_objects(bucket, prefix=prefix, recursive=recursive)

    def rm(self, bucket, fnm):
        try:
            self.conn.remove_object(bucket, fnm)
        except Exception:
            logging.exception(f"Fail to remove {bucket}/{fnm}:")

    def get(self, bucket, filename):
        max_retries = 3
        for retry in range(max_retries):
            try:
                if not self.conn.bucket_exists(bucket):
                    logging.error(f"Bucket {bucket} does not exist")
                    return None
                try:
                    r = self.conn.get_object(bucket, filename)
                    return r.read()
                except S3Error as e:
                    if e.code == "NoSuchKey":
                        logging.error(f"File {filename} does not exist in bucket {bucket}")
                    else:
                        logging.error(f"S3Error when getting {bucket}/{filename}: {str(e)}")
                    if retry < max_retries - 1:
                        time.sleep(1)
                        continue
                    return None
            except Exception as e:
                logging.exception(f"Fail to get {bucket}/{filename}: {str(e)}")
                import traceback
                traceback.print_exc()
                logging.error("Exception {} ,info is {}".format(e,traceback.format_exc()))
                self.__open__()
                if retry < max_retries - 1:
                    time.sleep(1)
                    continue
                return None
        return None

    def obj_exist(self, bucket, filename):
        try:
            if not self.conn.bucket_exists(bucket):
                return False
            if self.conn.stat_object(bucket, filename):
                return True
            else:
                return False
        except S3Error as e:
            if e.code in ["NoSuchKey", "NoSuchBucket", "ResourceNotFound"]:
                return False
        except Exception:
            logging.exception(f"obj_exist {bucket}/{filename} got exception")
            return False

    def get_presigned_url(self, bucket, fnm, expires):
        for _ in range(10):
            try:
                return self.conn.get_presigned_url("GET", bucket, fnm, expires)
            except Exception:
                logging.exception(f"Fail to get_presigned {bucket}/{fnm}:")
                self.__open__()
                time.sleep(1)
        return


    def mv(self, bucket,filename,dest_bucket):
        for _ in range(1):
            try:
                if not self.conn.bucket_exists(dest_bucket):
                    self.conn.make_bucket(dest_bucket)
                copy_s = CopySource(bucket, filename)
                copy_result = self.conn.copy_object(
                     dest_bucket,
                     filename,
                     copy_s
                     #f"/{bucket}/{filename}",
                 )
                self.conn.remove_object(bucket, filename)
            except Exception as e:
                logging.exception(f"Fail to mv {bucket}/{filename}")
                import traceback
                traceback.print_exc()
                logging.error("Exception {} ,info is {}".format(e,traceback.format_exc()))
                self.__open__()
                time.sleep(1)
        return
