
all: build-docker

build-docker:
	docker build -t pudo/libsanctions .

push: build-docker
	docker push pudo/libsanctions

env:
	docker run -ti un-sc-sanctions /bin/bash
