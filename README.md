<h1 align="center">Agent Ip2Geo</h1>

<p align="center">
<img src="https://img.shields.io/badge/License-Apache_2.0-brightgreen.svg">
<img src="https://img.shields.io/github/languages/top/ostorlab/agent_tsunami">
<img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg">
</p>

_Ip2Geo agent is part of the auto-discovery agents, responsible for detecting the geolocation details of an IP address._

<p align="center">
<img src="https://github.com/Ostorlab/agent_ip2geo/blob/main/images/logo.png" alt="agent-ip2geo" />
</p>

This repository is an implementation of [Ostorlab Agent](https://pypi.org/project/ostorlab/). 

## Getting Started
The Ip2Geo Agent works collectively with other agents. Its job; Find all geolocation details of an IP address and emit back these findings.

To perform your first scan, simply run the following command:

```shell
ostorlab scan run --install --agent agent/ostorlab/ip2geo \
							--agent agent/ostorlab/subfinder \
							--agent agent/ostorlab/autodiscovery_persist_graph \
							ip 8.8.8.8
```

This command will download and install the agents :`ip2geo`, `subfinder` and `autodiscovery_persist_graph` and target the IP address `8.8.8.8`.

For more information, please refer to the [Ostorlab Documentation](https://github.com/Ostorlab/ostorlab/blob/main/README.md)


## Usage

Agent Ip2Geo can be installed directly from the ostorlab agent store or built from this repository.

 ### Install directly from ostorlab agent store

 ```shell
 ostorlab agent install agent/ostorlab/ip2geo
 ```

### Build directly from the repository

 1. To build the Ip2Geo agent you need to have [ostorlab](https://pypi.org/project/ostorlab/) installed in your machine. If you have already installed ostorlab, you can skip this step.

```shell
pip3 install ostorlab
```

 2. Clone this repository.

```shell
git clone https://github.com/Ostorlab/agent_ip2geo.git && cd agent_ip2geo
```

 3. Build the agent image using ostorlab cli.

 ```shell
 ostortlab agent build --file=ostorlab.yaml
 ```
 You can pass the optional flag `--organization` to specify your organisation. The organization is empty by default.

 4. Run the agent using one of the following commands:
	 * If you did not specify an organization when building the image:
	  ```shell
	  ostorlab scan run --agent agent//ip2geo --agent agent//autodiscovery_persist_graph ip 8.8.8.8
	  ```
	 * If you specified an organization when building the image:
	  ```shell
	  ostorlab scan run --agent agent/[ORGANIZATION]/ip2geo --agent agent/[ORGANIZATION]/autodiscovery_persist_graph ip 8.8.8.8


## License
[Apache](./LICENSE)

