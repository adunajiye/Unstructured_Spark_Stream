from __future__ import annotations
import logging
import os
from datetime import datetime
from tabnanny import check
from networkx import union
import numpy as np
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import mean, stddev, max, udf
from pyspark.sql.functions import regexp_replace,regexp_extract_all
from pyspark.sql.types import ArrayType, DoubleType
from tables import Column
from pyspark.sql.types import StringType,IntegerType,StructType,StructField,DataType,DateType
import configparser
from udf_utils import *
from configuration.config import config
# Configure logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

# config = configparser.ConfigParser()
cluster_manager  = "spark://164.92.85.68:7077"

def define_udf():
    return {
        'extract_file_name_udf':udf(extract_file_name,StringType()),
        'extract_position_udf':udf(extract_postion,StringType()),
        'extract_salary_udf':udf(extract_salary,StructType([
            StructField('salary_start',DoubleType(),True),
            StructField('salary_end',DoubleType(),True)
            ])),
        'extract_startdate_udf':udf(extract_start_date,StringType()),
        'extract_enddate_udf':udf(extract_end_date,StringType()),
        'extract_classcode_udf':udf(extract_classcode,StringType()),
        'extract_requirement_udf':udf(extract_requirement,StringType()),
        'extract_notes_udf':udf(extract_notes,StringType()),
        'extract_duties_udf':udf(extract_duties,StringType()),
        'extract_selection_udf':udf(extract_selection,StringType()),
        'extract_experience_length_udf':udf(extract_experience_length,StringType()),
        'extract_education_length_udf':udf(extract_education_length,StringType()),
        'extract_application_loc_udf':udf(extract_application_location,StringType()),
        }
packages = [ "org.apache.hadoop:hadoop-common:3.3.6",
             "com.fasterxml.jackson.core:jackson-databind:2.15.3",
                    "com.amazonaws:aws-java-sdk:1.11.469"
]
jars = ",".join(packages) 


def get_session() -> SparkSession:
    """Create a spark session for the Spark application.

    Returns:
        SparkSession.
    """
    # Configure Spark
    spark = SparkSession.builder \
    .appName("Stream_Unstructured_Data") \
    .config("spark.executor.memory", "12g") \
    .config("spark.executor.cores", 4) \
    .config("spark.cores.max", 80) \
    .config("spark.dynamicAllocation.enabled", "true") \
    .config("spark.driver.memory", "1000g") \
    .config('spark.jars.packages',jars)\
    .config('spark.master',cluster_manager)\
    .config("spark.eventLog.gcMetrics.youngGenerationGarbageCollectors", "G1 Concurrent GC") \
    .config("spark.eventLog.gcMetrics.oldGenerationGarbageCollectors", "G1 Concurrent GC") \
    .config("spark.eventLog.gcMetrics.youngGenerationGarbageCollectors", "G1 Young Generation") \
    .config("spark.eventLog.gcMetrics.oldGenerationGarbageCollectors", "G1 Old Generation") \
    .config("spark.hadoop.fs.s3a.access.key",config.get('AWS_KEY')) \
    .config("spark.hadoop.fs.s3a.secret.key", config.get('AWS_SECRET')) \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

    # Get app id
    app_id = spark.conf.get("spark.app.id")

    logging.info(f"SparkSession started successfully for app: {app_id}")
    
    return spark
spark = get_session()

csv_input_dir = ""
images_input_dir = ""
json_input_dir = "file:///C:/Users/user/Desktop/SparkStreamingUnstructured/input/input_json"
pdf_input_dir = ""
text_input_dir = "file:///C:/Users/user/Desktop/SparkStreamingUnstructured/input/input_text"
video_input_dir = ""


Data_Schema =  StructType([StructField('file_name',StringType(), True),
                           StructField('position',StringType(), True),
                           StructField('classcode',StringType(), True),
                           StructField('salary_start',DoubleType(), True),
                           StructField('salary_end',DoubleType(), True),
                           StructField('start_date',DateType(), True),
                           StructField('end_date',DateType(), True),
                           StructField('req',StringType(), True),
                           StructField('notes',StringType(), True),
                           StructField('duties',StringType(), True),
                           StructField('selection',StringType(), True),
                           StructField('experience_length',StringType(), True),
                           StructField('job_type',StringType(), True),
                           StructField('education_length',StringType(), True),
                           StructField('school_type',StringType(), True),
                           StructField('application_location',StringType(), True),                         
                           
])
checkpointLocation = "file:///C:/Users/user/Desktop/SparkStreamingUnstructured/checkpoint"


udfs = define_udf()
# Read the input files of the data
job_df = (spark.readStream
          .format('text')
          .option('wholetext','true')
          .load(text_input_dir)
          )
json_df = (
    spark.readStream \
           .json(json_input_dir,
                 schema = Data_Schema,
                 multiLine=True)
           )
# json_df.show()


job_df = job_df.withColumn('file_name',regexp_replace(udfs['extract_file_name_udf']('value'),'\r',' '))
job_df = job_df.withColumn('value',regexp_replace('value',r'\n',' '))
job_df = job_df.withColumn('position',udfs['extract_position_udf']('value'))
job_df = job_df.withColumn('salary_start',udfs['extract_salary_udf']('value').getField('salary_start'))
job_df = job_df.withColumn('salary_end',udfs['extract_salary_udf']('value').getField('salary_end'))
job_df = job_df.withColumn('start_date',udfs['extract_startdate_udf']('value'))
job_df = job_df.withColumn('end_date',udfs['extract_enddate_udf']('value'))
job_df = job_df.withColumn('classcode',udfs['extract_classcode_udf']('value'))
job_df = job_df.withColumn('req',udfs['extract_requirement_udf']('value'))
job_df = job_df.withColumn('notes',udfs['extract_notes_udf']('value'))
job_df = job_df.withColumn('duties',udfs['extract_duties_udf']('value'))
job_df = job_df.withColumn('selection',udfs['extract_selection_udf']('value'))
job_df = job_df.withColumn('experience_length',udfs['extract_experience_length_udf']('value'))
job_df = job_df.withColumn('education_length',udfs['extract_education_length_udf']('value'))
job_df = job_df.withColumn('application_location',udfs['extract_application_loc_udf']('value'))





jdf = job_df.select("file_name","start_date","end_date","salary_start","salary_end","classcode","req","notes","duties","selection","experience_length","education_length","application_location")
# Read Json format data 


# json_df = json_df.select("file_name","start_date","end_date","salary_start","salary_end","classcode","req","notes","duties","selection","experience_length","education_length","application_location")
# Combine two df using Union function 

# union_df = jdf.union(json_df)

# Stream Data to s3 Buckets 
# def StreamWriter(input:DataFrame,checkpointFolder,Output):
#     return (input.writeStream.format('parquet')
#             .option('checkpointLocation',checkpointFolder)
#             .option('path',Output)
#             .trigger(processingTime='3 Seconds')
#             .start()
#             )
# bucket_name = ""

# query = StreamWriter(union_df,
#                      f's3a://{bucket_name}/checkpoint',
#                      f's3a://{bucket_name}/data/spark_unstructured'
#                      )


query =( jdf
.writeStream \
.outputMode('append')
.format('console')
.option('truncate', False)
.option('checkpointLocation', checkpointLocation)
.start()
)

query.awaitTermination()
spark.stop()

