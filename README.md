---
Title: GPU Services
---


# Usage

* Set up client parameters included [Accesskey and Accesskey secret](https://usercenter.console.aliyun.com/#/manage/ak), [Regions ID](https://www.alibabacloud.com/help/doc-detail/40654.htm)

* Check [Images ID](https://api.alibabacloud.com/?spm=a2c63.p38356.879954.7.2be5426brpiPMO#/?product=Ecs&version=2014-05-26&api=DescribeImages&params={%22RegionId%22:%22eu-central-1%22,%22Status%22:%22Available%22,%22OSType%22:%22Linux%22}&tab=DOC&lang=PYTHON) by using DescribeImages() with RegionId, Status = Available, OSType= Linux.

* Instance type can be find in [Instance created process](https://ecs-buy-eu-central-1.aliyun.com/wizard?spm=5176.13329450.home-res.buy.37617d33njrB32#/prepay/eu-central-1) and also can use DescribeInstanceTypes() function.

* Secure group must be set [VPC network](https://vpcnext.console.aliyun.com/vpc/eu-central-1/switches?VpcId=vpc-gw8fwbo016k2kg2hfpt15). Remember VpcId and Vswitchid.
For more details to check: [DOC](https://www.alibabacloud.com/help/doc-detail/54095.htm?spm=a2c63.p38356.b99.14.6b6358a7FctoCn)

* Find [secure group id](https://api.alibabacloud.com/?spm=a2c63.p38356.879954.7.2be5426brpiPMO#/?product=Ecs&version=2014-05-26&api=CreateSecurityGroup&tab=DOC&lang=PYTHON) by using CreateSecurityGroup() with VpcId showed above process.