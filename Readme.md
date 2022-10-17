# Beat Scheduler
A Django based application with pre-configured settings to work with Celery task queue and Celery Beat 
using the dynamic database scheduler.

The current application was made to serve as a generic code base for further development. Hence, it requires some refinements to work with your business logic.

## Technologies Used

- Python 3.8
- MySQL 8.0
- Redis
- RabbitMQ
- REST API
- Django
- Celery
- Celery Beat
- Ngnix

## Minimum Server Requirements

* OS: Ubuntu 18.04 (bionic)
* Memory: 6GB
* Storage: 64GB
* Processor: 4v Cores

## Building Project
### Cloning Repository
```bash
git clone https://github.com/Nitro963/beat-scheduler.git
cd beat-scheduler
```

### Install Docker Engine
```bash 
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```
Verify that Docker Engine is installed correctly by running the `hello-world` image.
```bash
sudo docker run hello-world
```
This command downloads a test image and runs it in a container. When the container runs, it prints a message and exits.

### Compile Yourself

After you have installed docker-engine and docker-compose run the following commands

```bash
cp .env.example .env
sudo docker compose build
sudo docker compose -f "docker-compose-pytest.yml" build
```

### Unit Tests
We have created an environment to run the unit tests and configured Pytest framework to work with Celery and Django 
using the official plugins.

After you have compiled the images run the following commands:
```bash
sudo docker compose -f "docker-compose-pytest.yml" up -d
sudo docker exec ${DOCKER_PROJECT}-testing-server pytest
sudo docker compose -f "docker-compose-pytest.yml" down
```
You can configure the testing session using pytest.ini and conftest.py files.

### Running Services

After you have compiled the images and ensured that you have correct environment i.e. successfull testing session.
Run the following command
#### Development Environment
```bash
sudo docker compose up
```
Now you can access the API [documentation](http://localhost:7075/api/v1/docs/) in your browser.

#### Production Environment
TODO

## System Monitoring
We have provided multiple administration tools for our services.

1. **The RabbitMQ Management** a plugin provides an HTTP-based API for management and monitoring of RabbitMQ nodes and clusters, along with a browser-based UI and a command line tool, rabbitmqadmin. You can access it through *port 7071*.
2. **RedisInsight** is a desktop manager that provides an intuitive and efficient GUI for Redis, allowing you to interact with your databases, monitor, and manage your data. You can access it through *port 7072*.
3. **PhpMyAdmin** is a web based tool for administrating MySQL databases. You can access it through *port 7073*.
4. **Flower** is a web based tool for monitoring and administrating Celery clusters. You can access it through *port 7074*.

> Note that we have used Nginx reverse proxy with basic Http auth to forward the requests to RedisInsight container as it lack any user authentication schema after it have been connected to a Redis database.

### Django Admin Dashboard
We have integerated the premade django-admin with the cool and modern theme of [Baton](https://github.com/otto-torino/django-baton).<br>
You can refer to the [documentation](https://django-baton.readthedocs.io/en/latest/) for more details about theme customization.

## Fixtures And Seeding
Database seeding is the initial seeding of a database with data. Seeding process usually automated that is executed 
upon the initial setup of an application. The data can be dummy data or necessary data.
### Static Data
The django container entrypoint script is configured to load any fixture named `inital_data` regardless of it's format (XML, JSON)
You can refer to django [documentation](https://docs.djangoproject.com/en/4.1/howto/initial-data/) for more details about the command.
### Dummy Seeding
Heavily inspired by [Laravel](https://laravel.com/) seed command we have created a reusable application to seed the 
database with random data using [FactoryBoy](https://factoryboy.readthedocs.io/) along with [Faker](https://github.com/joke2k/faker/) libraries.

In order to create a new seeder for your django app create a `seeder.py` script and inherit from `SeederBase` class 
then write your seed methods. You can refer to profiles_app to get a hands-on example.

For more details about command options run the following
```bash
sudo docker exec ${DOCKER_PROJECT}-web python manage.py seed --help
```
> Note that you MUST name your class Seeder in order to be discovered. Also, you must follow the naming convention `seed_$table_name` for each method you want to run.
