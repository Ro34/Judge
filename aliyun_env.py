from Judge.AliyunCredentialsProvider2 import AliyunCredentialsProvider
from Judge.env import *

provider = AliyunCredentialsProvider(
    AliyunAccessKey, AccessSecret, ResourceOwnerId)

MQUsername = provider.get_username()
MQPassword = provider.get_password()
