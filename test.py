#!/user/bin/python3
# -*- coding:utf-8 -*-
'''
test
'''
__author__ = 'Hijac Wu'

from upload import Upload

x = Upload()
x.setBucketName("kingmahjong-test")
originPath = './sync/bbb.png'
destPath = 'my-python-logo1.png'
x.putFile(originPath, destPath)