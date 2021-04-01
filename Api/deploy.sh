docker build -f Dockerfile -t api:latest .

docker tag api 711442408216.dkr.ecr.us-east-2.amazonaws.com/api

docker push 711442408216.dkr.ecr.us-east-2.amazonaws.com/api