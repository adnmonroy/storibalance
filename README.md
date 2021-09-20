# Stori Balance Function Demo (SBFD)

SBFD is an AWS Lambda Function programmed in Python to process CSV Balance files in PostgreSQL database.

## Installation
Installation must be in 3 parts:
* [S3 bucket](#s3-bucket)
* [RDS database (PostgreSQL 12.7)](#rds-database-(postgreSQL-12.7))
* [Lambda function (Python 3.6)](#lambda-function-(Python-3.6))

### S3 Bucket
1. Create a bucket named balancestori.
2. Create a file named transaction.csv.
3. Perform AWS connection rules and apply access policies.

### RDS database (PostgreSQL 12.7)
1. Create new RDS PostgreSQL database in your AWS Account.
2. Create a table using including balance.sql file.
3. Perform AWS connection rules and apply access policies.

### Lambda function (Python 3.6)
1. Create new Lambda Function in your AWS Account.
2. Edit the lambda-function.py file with your e-mail account and RDS access settings.
3. Compress the saved lamda_function.py file and psycopg2 folder in a new .zip file.
4. Upload the content of .zip file on Labda function.
5. Perform AWS connection rules and apply access policies.

## Live Demo
* You can see live demo and upload your own .csv file in demo Google Sites page: [https://sites.google.com/view/stori-file-balance-upload-demo/main](https://sites.google.com/view/stori-file-balance-upload-demo/main).

* The demo only works with email account configured in lambda function.

## Contributing
This is only a demo. Not upgrades or changes are planned.

## License
[MIT](https://choosealicense.com/licenses/mit/)
