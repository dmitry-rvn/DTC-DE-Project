# [DataTalksClub Data Engineering Zoomcamp 2023](https://github.com/DataTalksClub/data-engineering-zoomcamp) - Final project

---

## Project description

We will collect crypto trading data from [finnhub.io](https://finnhub.io/) API
with **Kafka**, store it on **Google Cloud Storage**, 
create DWH in **BigQuery** and data models with **dbt**,
and finally build and publish a dashboard in Looker, 
that shows trading volumes by day and trading symbol.

---

## Prerequisites (to reproduce):

 * Google Cloud Platform account - to collect and store data, create data warehouse, create a dashboard
 * [dbt Cloud](https://www.getdbt.com/) account - to transform "raw" data into nice tables in GCP BiqQuery (dbt Cloud is free to have one project)
 * [finnhub.io](https://finnhub.io/) account - to pull data from API (registration is free)

---

## Project file structure

```
├── assets  # images for README.md files with instructions
│   ├── bigquery
│   │   └── *.png
│   ├── dbt
│   │   └── *.png
│   ├── kafka
│   │   └── *.png
│   ├── terraform
│   │   └── *.png
|   └── dashboard.pdf
├── data 
│   └── .gitkeep
├── src  # source code
│   ├── bigquery
│   │   ├── *.sql
│   │   └── README.md  # instructions for BigQuery
│   ├── dbt
│   │   ├── models  # tables definition
│   │   |   └── core
│   │   |       ├── *.sql
│   │   |       └── schema.yml
│   │   ├── seeds  # files with manual data
│   │   |   └── *.csv
│   │   ├── .gitignore
│   │   ├── dbt_project.yml
│   │   ├── packages.yml
│   │   └── README.md  # instructions for dbt
│   ├── kafka
│   │   ├── docker
│   │   |   └── docker-compose.yml
│   │   ├── schemas  # Avro schemas
│   │   |   ├── crypto_record_key.avsc
│   │   |   └── crypto_record_value.avsc
│   │   ├── *.py
│   │   └── README.md  # instructions for Kafka
│   └── terraform
│       ├── .terraform-version
│       ├── main.tf
│       └── README.md  # instructions for Terraform
│       └── variables.tf
├── .gitignore
├── README.md
└── requirements.txt  # python dependencies
```

---

## Project steps

### 1. Create GCP infrastructure with Terraform

We will create Cloud Storage bucket and BigQuery dataset.

See instructions and the result here: [src/terraform/README.md](src/terraform/README.md)

### 2. Collect data with Kafka and save on Cloud Storage

We will:
 * launch Kafka server
 * run Kafka producer to collect data from API
 * run Kafka consumer to collect data from Kafka and save to Cloud Storage as Avro files

See instructions and the result here: [src/kafka/README.md](src/kafka/README.md)

Note: I've chosen *stream processing* instead of *batch processing* 
because I have experience with Apache Airflow and Prefect,
and on the contrary I haven't dealt with stream and wanted to explore Kafka.
I understand that my Kafka setup isn't ideal: e.g. I think, 
I should use three VMs (server, producer, consumer) instead of just one, but I've encountered some difficulties with this.
Also, as fas as I understand, GCP doesn't allow to append data to files on Cloud Storage,
so I in consumer I write data to VM volume, and then move all the data from VM to Cloud Storage.
<br>So any advice on stream/Kafka would be appreciated.

### 3. Create BigQuery table from Cloud Storage data

We will create partitioned external table from Avro files from Cloud Storage bucket.

See instructions and the result here: [src/bigquery/README.md](src/bigquery/README.md)

### 4. Build data models with dbt

We will create number of data models (tables), and deploy it as a scheduled job.

See instructions and the result here: [src/dbt/README.md](src/dbt/README.md)

### 5. Dashboard

Dashboard is built in Looker and has:
 * slicer for crypto-symbols
 * scorecard with total volume
 * donut chart of trade volume by symbols
 * stacked column chart of trade volume by days (horizontal axis) and symbols (bar breakdown)

Dashboard is accessible with link: https://lookerstudio.google.com/reporting/28fd64cf-51c9-46b0-af76-a0cf42763fa8/page/tEnnC

Also it is saved as a static PDF here: [assets/dashboard.pdf](assets/dashboard.pdf)

Dashboard is based on following SQL:

```sql
SELECT
    symbol_description AS Symbol,
    dt AS Date,
    volume AS Volume
FROM dtc_crypto_data.agg_symbol_daily_volumes
```

---

## Self-assessment:

* Problem description
    * Criteria:
      * 0 points: Problem is not described
      * 1 point: Problem is described but shortly or not clearly 
      * 2 points: Problem is well described and it's clear what the problem the project solves
    * **My assessment: 1 point** *(I believe that the description is clear but maybe not very detailed)*
* Cloud
    * Criteria:
      * 0 points: Cloud is not used, things run only locally
      * 2 points: The project is developed in the cloud
      * 4 points: The project is developed in the cloud and IaC tools are used
    * **My assessment: 4 points** *(Terraform is used as IaC tool; all development performed in cloud: dbt Cloud and Google Cloud Platform)*
* Data ingestion
    * Criteria (Stream)
      * 0 points: No streaming system (like Kafka, Pulsar, etc)
      * 2 points: A simple pipeline with one consumer and one producer
      * 4 points: Using consumer/producers and streaming technologies (like Kafka streaming, Spark streaming, Flink, etc)
    * **My assessment: 2 points** *(Kafka with 1 producer and 1 consumer is used, but it's not very clear for me whether it's 2 or 4 points, but I guess it's closer to 2 point rather than 4)*
* Data warehouse
    * Criteria:
      * 0 points: No DWH is used
      * 2 points: Tables are created in DWH, but not optimized
      * 4 points: Tables are partitioned and clustered in a way that makes sense for the upstream queries (with explanation)
    * **My assessment: 4 points** *(Table `ext_trade_data` has source data partitioning (based on date of data); table `fact_trade_data_hourly` has clustering by crypto-symbol)*
* Transformations (dbt, spark, etc)
    * Criteria:
      * 0 points: No tranformations
      * 2 points: Simple SQL transformation (no dbt or similar tools)
      * 4 points: Tranformations are defined with dbt, Spark or similar technologies
    * **My assessment: 4 points** *(Cloud dbt (with deployment and scheduling) is used)*
* Dashboard
    * Criteria:
      * 0 points: No dashboard
      * 2 points: A dashboard with 1 tile
      * 4 points: A dashboard with 2 tiles
    * **My assessment: 4 points** *(dashboard has 2 tiles)*
* Reproducibility
    * Criteria:
      * 0 points: No instructions how to run code at all
      * 2 points: Some instructions are there, but they are not complete
      * 4 points: Instructions are clear, it's easy to run the code, and the code works
    * **My assessment: 4 points** *(all project parts have `README.md` with instructions, and I believe they are quite clear and reproducible)*

**Total: 23** (from 26 points)
