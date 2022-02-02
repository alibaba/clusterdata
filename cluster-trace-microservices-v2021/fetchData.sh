#!/bin/bash  
  
url='http://alitrip.oss-cn-zhangjiakou.aliyuncs.com/TraceData'

mkdir data
cd data

mkdir Node
mkdir MSResource
mkdir MSRTQps
mkdir MSCallGraph

cd Node
command="curl ${url}/node/Node.tar.gz -o Node.tar.gz"
${command}

cd ../MSRTQps
for((i=0;i<=24;i++));  
do   
	command="curl ${url}/MSRTQps/MSRTQps_${i}.tar.gz -o MSRTQps_${i}.tar.gz"
	${command}
done 

cd ../MSCallGraph
for((i=0;i<=144;i++));  
do   
	command="curl ${url}/MSCallGraph/MSCallGraph_${i}.tar.gz -o MSCallGraph_${i}.tar.gz"
	${command}
done 

cd ../MSResource
for((i=0;i<=11;i++));  
do   
	command="curl ${url}/MSResource/MSResource_${i}.tar.gz -o MSResource_${i}.tar.gz"
	${command}
done 