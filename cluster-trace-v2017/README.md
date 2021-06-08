**Below is for cluster trace released in 2017. There will be no more updates for this file.**

# Overview

The trace data, ClusterData201708,  contains cluster information of a production cluster in 12 hours period (see note below), and contains about 1.3k machines that run both online service and batch jobs.

*note for 12 hours period:  although the data for server and batch spans about 24hours, data for containers is refined to 12 hours. We will release another version in near future.*

# Trace data 
The format of trace data is described in the [schema description](trace_201708.md), and defined in the specification file [schema.csv](schema.csv) in the repository.

# Downloading the trace
The data is stored in Alibaba Cloud Object Storage Service. You do not need to have an Alibaba account or sign up for Object Storage Service to download the data.

Downloading information can be found (after a short survey) in [this link](https://goo.gl/forms/eOoe6DwZQpd2H5n53). We use the contact information to keep in touch with you, and announce goodies such as new traces.
Included with the trace is a [SHA256SUM](SHA256SUM) file, which can be used to verify the integrity of a download, using the sha256sum command from GNU coreutils using a command like

```
sha256sum --check SHA256SUM
```




