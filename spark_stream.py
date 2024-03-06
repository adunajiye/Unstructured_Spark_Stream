from __future__ import annotations
import logging
import os
from datetime import datetime
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
cluster_manager  = "local[*]"

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
        'extract_requirment_udf':udf(extract_requirement,StringType()),
        'extract_notes_udf':udf(extract_notes,StringType()),
        'extract_duties_udf':udf(extract_duties,StringType()),
        'extract_selection_udf':udf(extract_selection,StringType()),
        'extract_experince_length_udf':udf(extract_experince_length,StringType()),
        'extract_education_length_udf':udf(extract_education_length,StringType()),
        'extract_application_udf':udf(extract_duties,StringType()),
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
    .appName("Read Unstructured_Data") \
    .config("spark.executor.memory", "4g") \
    .config("spark.executor.cores", 2) \
    .config("spark.cores.max", 10) \
    .config("spark.dynamicAllocation.enabled", "false") \
    .config("spark.driver.memory", "100g") \
    .config('spark.jars.packages',jars)\
    .config('spark.master',cluster_manager)\
    .config("spark.hadoop.fs.s3a.access.key",config.get('AWS_KEY')) \
    .config("spark.hadoop.fs.s3a.secret.key", config.get('AWS_SECRET')) \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

    # Get app id
    app_id = spark.conf.get("spark.app.id")

    logging.info(f"SparkSession started successfully for app: {app_id}")

    return spark
spark = get_session()

csv_input_dir = "C:/Users/user/Desktop/Spark_Streaming_Unstructured/input/input_csv"
images_input_dir = "C:/Users/user/Desktop/Spark_Streaming_Unstructured/input/input_images"
json_input_dir = "C:/Users/user/Desktop/Spark_Streaming_Unstructured/input/input_json"
pdf_input_dir = "C:/Users/user/Desktop/Spark_Streaming_Unstructured/input/input_pdf"
text_input_dir = "C:/Users/user/Desktop/Spark_Streaming_Unstructured/input/input_text"
video_input_dir = "C:/Users/user/Desktop/Spark_Streaming_Unstructured/input/input_video"


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
                           StructField('education_lenght',StringType(), True),
                           StructField('school_type',StringType(), True),
                           StructField('application_location',StringType(), True),                         
                           
])

udfs = define_udf()

job_df = (spark.readStream
          .format('text')
          .option('wholetext','true')
          .load(text_input_dir)
          )
job_df = job_df.withColumn('file_name',regexp_replace(udfs['extract_file_name_udf']('value'),'\r',' '))
job_df = job_df.withColumn('value',regexp_replace('value',r'\n',' '))
job_df = job_df.withColumn('position',udfs['extract_position_udf']('value'))
job_df = job_df.withColumn('salary_start',udfs['extract_salary_udf']('value').getField('salary_start'))
job_df = job_df.withColumn('salary_end',udfs['extract_salary_udf']('value').getField('salary_end'))

job_df = job_df.withColumn('start_date',udfs['extract_startdate_udf']('value'))
job_df = job_df.withColumn('end_date',udfs['extract_enddate_udf']('value'))

jdf = job_df.select("file_name","start_date","end_date")

query =( jdf
.writeStream \
.outputMode('append')
.format('console')
.option('checkpointLocation', 'C:/Users/user/AppData/Local/Temp/')
.start()
)

query.awaitTermination()