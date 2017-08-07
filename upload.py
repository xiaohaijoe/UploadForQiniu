#!/user/bin/python3
# -*- coding:utf-8 -*-
'''
Creat a simple window
'''
__author__ = 'Hijac Wu'

from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config

class Upload:
    #需要填写你的 Access Key 和 Secret Key
    access_key = ''
    secret_key = ''
    # 构建鉴权对象
    auth = 0
    #要上传的空间
    bucketName = ''

    def __init__(self):
        self.auth = Auth(self.access_key, self.secret_key)

    def setBucketName(self, bucketName):
        self.bucketName = bucketName

    # 上传单个文件
    # orginPath: 源路径, 要上传的文件路径
    # destPath: 目标路径, 上传到七牛后保存的文件名
    def putFile(self, originPath, destPath):
        # 生成上传 Token，可以指定过期时间
        token = self.auth.upload_token(self.bucketName, destPath, 3600)
        ret, info = put_file(token, destPath, originPath)
        return ret, info


