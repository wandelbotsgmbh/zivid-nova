# Zivid-Nova

[Zivid](https://www.zivid.com/de/) integration for Wandelbots Nova.

This app allows to access Zivid SDK functionalties via [OpenAPI Interface](openapi.json).

## Prerequisite

* You need a setup with a physical Zivid camera connected to your IPC.
* The Ethernet interface needs to be in the IP range to access the camera under its default IP address `172.28.60.5/24`.
* The IPC must be equipped with an Intel GPU (integrated graphics of the CPU will also work).
    * The support for other GPUs is in progress.

## Install

* Requirement: [nova cli](https://github.com/wandelbotsgmbh/wabocli)

```bash
# Currently only machines with intel gpu (integrated gpu will also work) are supported with Nova.
# Nvidia GPU support is in preparation.
$ nova catalog install zivid-intel
```

## API

The first draft of the spec can be seen here [openapi.json](openapi.json).

## Development

### Formatting

* `poetry run black zivid_nova`
* `poetry run isort zivid_nova tests`

### YAML linting

[prebuild image](https://hub.docker.com/r/cytopia/yamllint) is used for [yamllint](https://github.com/adrienverge/yamllint)

```bash
docker run --rm -it -v $(pwd):/data cytopia/yamllint -d .yamllint .
```

### Running Locally

* Make sure [Zivid SDK](https://support.zivid.com/en/latest/index.html) is installed on your machine.
* Install project dependencies `poetry install`.
* Run the project with `poetry run serve`.
    * If you are using vscode you can press F5.
* Visit `127.0.0.1:8080` to access the [api docs](openapi.json).

### Building & Pushing & Installing

```bash
$ nova app install
```

### Building Docker

```bash
$ docker buildx build --platform linux/amd64 -t registry.code.wabo.run/ai/zivid-nova/zivid-nova --push .
```


