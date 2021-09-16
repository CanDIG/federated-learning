# federated-learning
For the development of differentially private federated machine learning on the CanDIG data services

## Quick Start

1. **Configure docker-compose.** The docker-compose.yaml file expects a .env file in root folder, so that it can configure the Katsu database with some secrets such as the password. For a generic configuration, you can run the following to copy and use the default configuration: `cp .default.env .env`
2. **Spin up Katsu.** Run `docker-compose up katsu`
3. **Browse Katsu.** Navigate your browser to `localhost:8000`

## Development

To run more existing services alongside Katsu, add the services to the `docker-compose.yaml` file and add their default configuration variables to `.default.env`.

You can also contribute code pertaining to federated learning to this repository. Please organize new files into subdirectories. The root folder should only contain the README, configuration files, and subdirectories.