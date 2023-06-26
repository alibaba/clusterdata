#!/bin/bash  
  
url='http://aliopentrace.oss-cn-beijing.aliyuncs.com/v2021MicroservicesTraces'

mkdir data
cd data

mkdir Node
mkdir MSResource
mkdir MSRTQps
mkdir MSCallGraph

cd Node

command="wget -c --retry-connrefused --tries=0 --timeout=50 ${url}/node/Node_0.tar.gz"
${command}

cd ../MSRTQps
for((i=0;i<=24;i++));  
do   
	command="wget -c --retry-connrefused --tries=0 --timeout=50 ${url}/MSRTQps/MSRTQps_${i}.tar.gz"
	${command}
done 

cd ../MSCallGraph
for((i=0;i<=144;i++));  
do   
	command="wget -c --retry-connrefused --tries=0 --timeout=50 ${url}/MSCallGraph/MSCallGraph_${i}.tar.gz"
	${command}
done 

cd ../MSResource
for((i=0;i<=11;i++));  
do   
	command="wget -c --retry-connrefused --tries=0 --timeout=50 ${url}/MSResource/MSResource_${i}.tar.gz"
	${command}
done 