@echo off
set PYSPARK_PYTHON=python
set SPARK_HOME= C:\Users\user\Downloads\spark-3.5.0-bin-hadoop3\spark-3.5.0-bin-hadoop3\spark-3.5.0-bin-hadoop3
set PYTHONPATH=%SPARK_HOME%\python;%SPARK_HOME%\python\lib\py4j-0.10.9-src.zip
%SPARK_HOME%\bin\spark-submit --packages org.apache.hadoop:hadoop-common:3.3.6,com.amazonaws:aws-java-sdk:1.11.469,com.fasterxml.jackson.core:jackson-databind:2.15.3 --master local[*] --executor-memory 2g --py-files C:\Users\user\Desktop\Spark_Streaming_Unstructured\spark_stream.py C:\Users\user\Desktop\Spark_Streaming_Unstructured\spark_stream.py
