start-rabbit:
    docker run -d -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management

#run formater on given location
format WHAT:
    poetry run yapf -i --recursive {{WHAT}}

#used to basic start of rest_api
startapi:
    poetry run uvicorn test_service.main:app --reload
