run_celery_dev:
	echo "starting celery dev";\
	rabbitmq-server -detached;\
	celery worker --app=tasks -c1 -l info;\

run_celery:
	echo "starting celery";\
	rabbitmq-server -detached;\
	celery worker --app=tasks --autoscale=12,6  -l info;\
