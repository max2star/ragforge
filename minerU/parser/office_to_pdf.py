#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
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
import sys
sys.path.append("/var/lib/gpustack/ragflow/ragflow/")
sys.path.append("/usr/local/lib/python3.10/dist-packages/")
import os
import subprocess
from pathlib import Path
import boto3
from io import BytesIO
import subprocess
import tempfile
import logging
from botocore.exceptions import ClientError
import uuid
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod
from magic_pdf.data.data_reader_writer import *
from magic_pdf.data.data_reader_writer import MultiBucketS3DataReader
from magic_pdf.data.schemas import S3Config
from magic_pdf.data.data_reader_writer import S3DataReader, S3DataWriter
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
import logging
from rag import settings


def get_uuid():
    return uuid.uuid1().hex

class SecureDocConverter:
    def __init__(self, s3_config,bucket,file_name,kb_id,doc_id):
        self.mem_tmp_dir = '/dev/shm'  # Linux内存盘路径
        if s3_config:
            self.s3_config = s3_config
        else:
            self.s3_config = settings.S3
        self.ak = self.s3_config.get('access_key', None)
        self.sk = self.s3_config.get('secret_key', None)
        self.endpoint_url = self.s3_config.get('endpoint_url', None)
        self.bucket_name =  bucket
        self.file_name = file_name
        self.name_without_suff = file_name.split(".")[0]
        self.reader = S3DataReader('/', self.bucket_name, self.ak, self.sk, self.endpoint_url)
        self.writer = S3DataWriter(f'minerU/{doc_id}',kb_id, self.ak, self.sk, self.endpoint_url)
        #print(self.ak,self.sk,self.endpoint_url)
    
    def _convert_in_memory(self, input_data: bytes) -> bytes:
        env = os.environ.copy()
        libreoffice_path = "/usr/lib/libreoffice/program"
        env["LD_LIBRARY_PATH"] = f"{libreoffice_path}:{env.get('LD_LIBRARY_PATH', '')}"
        try:
            with tempfile.TemporaryDirectory(dir=self.mem_tmp_dir) as tmp_dir:
                # 生成随机文件名
                uuid_ = get_uuid()
                input_name = os.path.join(tmp_dir,uuid_+".docx") 
                output_name = os.path.join(tmp_dir,uuid_+'.pdf')

                # 内存写入（不落盘）
                with open(input_name, 'wb') as f:
                    f.write(input_data)
                # 执行转换（内存操作）
                #cmd = [
                #    'libreoffice', '--headless', '--norestore', '--nofirststartwizard',
                #    '--convert-to', 'pdf:writer_pdf_Export',
                #    '--outdir', tmp_dir,
                #    input_name
                #]
                cmd = [
                    'soffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', str(tmp_dir),
                    str(input_name)
                ]
                result = subprocess.run(
                    cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )

                # 验证输出
                if not os.path.exists(output_name):
                    logging.error(f"转换失败: {result.stderr.decode()}")
                    raise RuntimeError("PDF文件未生成")

                # 读取PDF到内存
                with open(output_name, 'rb') as f:
                    return f.read()

        except subprocess.CalledProcessError as e:
            logging.error(f"转换进程错误: {e.stderr.decode()}")
            raise
        except Exception as e:
            logging.error(f"转换异常: {str(e)}")
            raise

    def convert_file_to_pdf(self,input_path, output_dir):
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"The input file {input_path} does not exist.")
    
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            'soffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', str(output_dir),
            str(input_path)
        ]
        
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(output_dir)   
        if process.returncode != 0:
            raise ConvertToPdfError(process.stderr.decode())

    def process_s3_object(self):
        """处理S3文档转换"""
        try:
            # 下载到内存
            file_data = self.reader.read(self.file_name)
            # 执行转换
            pdf_data = self._convert_in_memory(file_data)
            # 上传结果
            self.writer.write(self.name_without_suff+'.pdf', pdf_data)
            return
        
        except ClientError as e:
            logging.error(f"S3操作失败: {e.response['Error']['Message']}")
            raise
        except Exception as e:
            logging.error(f"处理失败: {str(e)}")
            raise

# 使用示例
if __name__ == "__main__":
    bucket_name = "maxiao"
    file_name =  '场景应用系统模块测试.docx'
    #file_name = "场景应用系统模块测试_001.docx"
    kb_id = bucket_name
    doc_id = "test_convert"
    s3_config = {
            'access_key':'D6Mdnsb3HvpyEVLQmmOX',
            'secret_key':'kUkrVtKBCwdRycKbobHygRI7QBdw0no38gW8Gqef',
            'endpoint_url':'https://101.52.216.178:19000/'
    }

    s= SecureDocConverter(s3_config,bucket_name,file_name,kb_id,doc_id)
    s.process_s3_object()
    #endpoint_url = "https://101.52.216.178:19000/"
    #reader = S3DataReader('/', bucket_name, ak, sk, endpoint_url)
    #writer = S3DataWriter('tmp/', bucket_name, ak, sk, endpoint_url)
    ##读取文件
    #pdf_file_name = '场景应用系统模块测试.docx'
    #file_data = reader.read(pdf_file_name)

    #converter = SecureDocConverter(None)
    #converted_data = converter._convert_in_memory(file_data)
    #file_dst = pdf_file_name+'.pdf' 
    #writer.write(file_dst, converted_data)
